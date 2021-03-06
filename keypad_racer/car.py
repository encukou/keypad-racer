import struct
import math
import time

import pyglet

from . import resources
from .anim import AnimatedValue, ConstantValue, Wait, Blocker, fork

CAR_FORMAT = '=4h2e3e'
STRIDE = struct.calcsize(CAR_FORMAT)

HISTORY_SIZE = 6
LINE_FORMAT = '=2h'
LINE_STRIDE = struct.calcsize(LINE_FORMAT)

ACTION_DIRECTIONS = {
    0: (-1, -1),
    1: ( 0, -1),
    2: (+1, -1),
    3: (-1,  0),
    4: ( 0,  0),
    5: (+1,  0),
    6: (-1, +1),
    7: ( 0, +1),
    8: (+1, +1),
}

explode_sound = pyglet.media.load(resources.global_fspath('sound/acid6.wav'), streaming=False)

class CarGroup:
    def __init__(self, ctx, circuit, max_cars=9):
        self.ctx = ctx
        self.circuit = circuit
        self.max_cars = max_cars
        self.cars = []

        uv_vertices = bytes((
            1, 255,
            255, 255,
            1, 1,
            255, 1,
        ))
        uv_vbo = ctx.buffer(uv_vertices)

        self.car_prog = ctx.program(
            vertex_shader=resources.get_shader('shaders/car.vert'),
            fragment_shader=resources.get_shader('shaders/car.frag'),
        )

        self.cars_vbo = ctx.buffer(bytes(STRIDE * max_cars), dynamic=True)
        self.t_vbo = ctx.buffer(bytes(max_cars), dynamic=True)
        self.vao = ctx.vertex_array(
            self.car_prog,
            [
                (uv_vbo, '2i1', 'uv'),
                (self.cars_vbo, '4i2 2f2 3f2 /i', 'pos', 'orientation', 'color'),
                (self.t_vbo, '1f1 /i', 'pos_t'),
            ],
        )

        self.line_prog = ctx.program(
            vertex_shader=resources.get_shader('shaders/car_line.vert'),
            fragment_shader=resources.get_shader('shaders/car_line.frag'),
            geometry_shader=resources.get_shader('shaders/car_line.geom'),
        )
        self.line_vbo = ctx.buffer(
            bytes(LINE_STRIDE * max_cars * (HISTORY_SIZE+2)),
            dynamic=True,
        )
        line_t = ctx.buffer(
            bytes([
                0,
                *range(HISTORY_SIZE+1),
            ]) * self.max_cars,
        )
        self.line_vao = ctx.vertex_array(
            self.line_prog,
            [
                (self.line_vbo, '2i2', 'point'),
                (line_t, 'i1', 't'),
            ],
            skip_errors=True,
        )

    def draw(self, view):
        self.circuit.draw(view)
        view.setup(self.car_prog, self.line_prog)
        ts = bytearray()
        for car in self.cars:
            car.update_group()
            ts.append(round(float(car.anim_t)*255))
        self.t_vbo.write(ts)
        if self.cars:
            for i, car in enumerate(self.cars):
                self.line_prog['color'] = (*car.color, car.anim_t)
                self.line_vao.render(
                    self.ctx.LINE_STRIP_ADJACENCY,
                    first=i*(HISTORY_SIZE+2),
                    vertices=HISTORY_SIZE+2,
                )
            self.vao.render(
                self.ctx.TRIANGLE_STRIP,
                instances=len(self.cars),
            )

    def add_car(self, car):
        result = len(self.cars)
        if result > self.max_cars:
            raise ValueError('Too many cars in group')
        self.cars.append(car)
        return result

class Car:
    def __init__(self, group, color, pos):
        self.group = group
        self.index = group.add_car(self)
        self._color = color
        self._orientation = 0
        self.last_orientation = 0
        self._pos = pos
        self.last_pos = pos
        self.history = [struct.pack(LINE_FORMAT, *pos)] * (HISTORY_SIZE+2)
        self.velocity = 0, 1
        self.dirty = True
        self.anim_t = ConstantValue(0)
        self.view_rect = self.get_view_rect()
        self.keypad = None
        self.crashed = False
        self.crash_callback = None
        self.group.circuit.cars.append(self)
        self.lap = 1
        self.max_lap = 1
        self.lap_start_time = time.monotonic()
        self.lap_times = []
        self.crash_count = 0

    def update_group(self):
        if not self.dirty:
            return
        data = struct.pack(
            CAR_FORMAT,
            *self._pos, *self.last_pos, self.orientation, self.last_orientation, *self.color,
        )
        self.group.cars_vbo.write(data, offset = STRIDE*self.index)
        data = b''.join(self.history)
        self.group.line_vbo.write(data, offset=LINE_STRIDE*(HISTORY_SIZE+2)*self.index)

    @property
    def color(self):
        return self._color
    @color.setter
    def color(self, new):
        self._color = new
        self.dirty = True

    @property
    def orientation(self):
        return self._orientation
    @orientation.setter
    def orientation(self, new):
        self._orientation = new
        self.dirty = True

    @property
    def pos(self):
        return self._pos
    def move(self, dx, dy, sound=True):
        duration = 0.5
        self.last_orientation = self._orientation
        x, y = self.last_pos = self.pos
        vx, vy = self.velocity
        vx += dx
        vy += dy
        new = x + vx, y + vy
        final_pos = new
        blocker = None
        dest_t = 1
        if (vx or vy) and not self.group.circuit.is_on_track(*new):
            blocker = self.blocker_on_path_to(dx, dy)
            if blocker:
                dest_t = blocker[2]
                respawn_pos = self.find_respawn_pos(blocker)
                final_pos = respawn_pos
        self.velocity = vx, vy
        buf = struct.pack(LINE_FORMAT, *new)
        self.history = [
            self.history[2],
            *self.history[2:-1],
            buf,
            buf,
        ]
        if self._pos != new:
            self.last_orientation %= math.tau
            orient = -math.atan2(vx, vy)
            orientations = [orient - math.tau, orient, orient + math.tau]
            self._orientation = min(
                orientations,
                key=lambda o: abs(o - self.last_orientation),
            )
            self._pos = new
        else:
            duration /= 2
        self.dirty = True
        self.anim_t = AnimatedValue(ConstantValue(0), dest_t, duration*dest_t)
        if sound:
            self.play_sounds(vx, vy, duration, dest_t, crash=bool(blocker))
        if not blocker:
            waitblock = Wait(duration)
        else:
            waitblock = Blocker()
            self.crashed = True
            self.crash_count += 1
            if self.crash_callback:
                self.crash_callback()
            @fork
            async def complete_move():
                await Wait(duration*dest_t)
                self.velocity = 0, 0
                self._pos = self.last_pos = respawn_pos
                self.history = [
                    struct.pack(LINE_FORMAT, *self.pos)] * (HISTORY_SIZE+2)
                self.dirty = True
                self.view_rect = self.get_view_rect()
                @fork
                async def _f():
                    rot_speed = 0.5
                    while self.crashed:
                        self.orientation += rot_speed
                        self.orientation %= math.tau
                        rot_speed *= 0.99
                        await Wait(1/60)
                await Wait(duration*(1-dest_t))
                await Wait(self.speed * 1.5 + 2)
                self.crashed = False
                waitblock.unblock()
        self.view_rect = self.get_view_rect()
        if self.keypad:
            self.keypad.pause(waitblock)
        x, y = final_pos
        if x < 20:
            lx, ly = self.last_pos
            if (y < 0) != (ly < 0):
                if y < 0:
                    self.lap -= 1
                else:
                    self.lap += 1
                if self.lap > self.max_lap:
                    self.max_lap = self.lap
                    new_start = time.monotonic()
                    self.lap_times.append(new_start - self.lap_start_time)
                    self.lap_start_time = new_start
        return duration

    def play_sounds(self, vx, vy, duration, dest_t, crash=False):
      try:
        best = max(abs(vx), abs(vy))
        if best <= 0:
            return
        interval = duration / best
        envelope = pyglet.media.synthesis.ADSREnvelope(
            interval/8, interval/4, interval/2,
        )
        envelope = pyglet.media.synthesis.LinearDecayEnvelope()
        instrument = pyglet.media.synthesis.Sawtooth
        for i in range(1, best+1):
            t = i * interval
            if t >= dest_t:
                break
            frequency = 220*((i+1)**(1.0594**1/4))
            sound = instrument(duration=interval/2, frequency=frequency, envelope=envelope)
            def _play(dt, sound=sound):
                sound.play()
            pyglet.clock.schedule_once(_play, t*duration)
        if crash:
            def _play(dt):
                explode_sound.play()
            pyglet.clock.schedule_once(_play, dest_t*duration)
      except Exception:
          # XXX
          pass

    @property
    def speed(self):
        return math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)

    def find_respawn_pos(self, blocker):
        bx, by, t = blocker
        bx = round(bx)
        by = round(by)
        circuit = self.group.circuit
        for i in range(100):
            positions = [
                *((bx+i, y) for y in range(by-i, by+i+1)),
                *((bx-i, y) for y in range(by-i, by+i+1)),
                *((x, by-i) for x in range(bx-i, bx+i+1)),
                *((x, by+i) for x in range(bx-i, bx+i+1)),
            ]
            positions = [p for p in positions if circuit.is_on_track(*p)]
            if positions:
                return min(
                    positions,
                    key=lambda p: (p[0]-bx)**2 + (p[1]-by)**2,
                )
        # !?
        print('No respawn point found...?!')
        return bx, by

    def act(self, action):
        if (xy := ACTION_DIRECTIONS.get(action)):
            return self.move(*xy)
        return 0

    def get_view_rect(self):
        x, y = self.pos
        x1, y1 = self.pos
        x2, y2 = self.pos
        x3, y3 = self.pos
        dx, dy = self.velocity
        for dx2 in range(abs(dx)):
            x1 += dx
        for dy2 in range(abs(dy)):
            y1 += dy
        return (
            min(x, x1, x + dx, x - dx) - 5,
            min(y, y1, y + dy, y - dy) - 5,
            max(x, x1, x + dx, x - dx) + 5,
            max(y, y1, y + dy, y - dy) + 5,
        )

    def blocker_on_direction(self, direction):
        if (xy := ACTION_DIRECTIONS.get(direction)):
            return self.blocker_on_path_to(*xy)
        return None

    def blocker_on_path_to(self, x, y):
        crash_ts = []
        circuit = self.group.circuit
        sx, sy = self.pos
        vx, vy = self.velocity
        dest_x = sx + vx + x
        dest_y = sy + vy + y
        xrange = abs(sx - dest_x)
        if xrange:
            for t in range(xrange + 1):
                t /= xrange
                x = (1-t) * sx + t * dest_x
                y = (1-t) * sy + t * dest_y
                ok = circuit.y_intersection_passable(round(x), y);
                if not ok:
                    crash_ts.append(t)
                    break

        yrange = abs(sy - dest_y)
        if yrange:
            for t in range(yrange + 1):
                t /= yrange
                x = (1-t) * sx + t * dest_x
                y = (1-t) * sy + t * dest_y
                ok = circuit.x_intersection_passable(x, round(y))
                if not ok:
                    crash_ts.append(t)
                    break
        if not circuit.is_on_track(dest_x, dest_y):
            crash_ts.append(1)

        if crash_ts:
            t = min(crash_ts)
            x = (1-t) * sx + t * dest_x
            y = (1-t) * sy + t * dest_y
            return x, y, t
        return None


def _all(a, b):
    a, b = sorted((a, b))
    return range(math.floor(a), math.ceil(b)+1)
