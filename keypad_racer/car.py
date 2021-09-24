import struct
import math

from . import resources

BASIC_FORMAT = '=2f1f'
FULL_FORMAT = BASIC_FORMAT + '3f'
STRIDE = struct.calcsize(FULL_FORMAT)

HISTORY_SIZE = 6
LINE_FORMAT = '=2h'
LINE_STRIDE = struct.calcsize(LINE_FORMAT)

ACTION_DIRECTIONS = {
    0: (-1, +1),
    1: ( 0, +1),
    2: (+1, +1),
    3: (-1,  0),
    4: ( 0,  0),
    5: (+1, 0 ),
    6: (-1, -1),
    7: ( 0, -1),
    8: (+1, -1),
}

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
        self.vao = ctx.vertex_array(
            self.car_prog,
            [
                (uv_vbo, '2i1', 'uv'),
                (self.cars_vbo, '2f4 f4 3f4 /i', 'pos', 'orientation', 'color'),
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
                *(int(255*t/(HISTORY_SIZE-1)) for t in range(HISTORY_SIZE)),
                255,
            ]) * self.max_cars,
        )
        self.line_vao = ctx.vertex_array(
            self.line_prog,
            [
                (self.line_vbo, '2i2', 'point'),
                (line_t, 'f1', 't'),
            ],
            skip_errors=True,
        )

    def draw(self, view):
        self.circuit.draw(view)
        view.setup(self.car_prog, self.line_prog)
        for car in self.cars:
            if car.dirty:
                car.update_group()
        if self.cars:
            for i, car in enumerate(self.cars):
                self.line_prog['color'] = car.color
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
        self._pos = pos
        self.history = [struct.pack(LINE_FORMAT, *pos)] * (HISTORY_SIZE+2)
        self.velocity = 0, 1
        self.dirty = 2      # bitfield: 1=position/orientation; 2=color
        self._pos = self._pos[0] + 68+5*1, -207-5*6
        self.velocity = 0, 5
        self._move(0, 0)
        self._move(0, 0)
        self._move(0, 0)
        self._move(0, 0)
        self._move(0, 0)
        self.velocity = -4, 5
        self._move(0, 0)
        if self.index == 0:
            for x in -1,0,1:
                for y in 1,0,-1:
                    print(self.pos, x, y)
                    print('Blocked at', self.blocker_on_path_to(x, y))

    def update_group(self):
        if not self.dirty:
            return
        elif self.dirty == 1:
            data = struct.pack(
                BASIC_FORMAT,
                *self.pos, self.orientation,
            )
            self.group.cars_vbo.write(data, offset = STRIDE*self.index)
        elif self.dirty:
            data = struct.pack(
                FULL_FORMAT,
                *self.pos, self.orientation, *self.color,
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
        self.dirty |= 2

    @property
    def orientation(self):
        return self._orientation
    @orientation.setter
    def orientation(self, new):
        self._orientation = new
        self.dirty |= 1

    @property
    def pos(self):
        return self._pos
    def _move(self, dx, dy):
        x, y = self.pos
        vx, vy = self.velocity
        vx += dx
        vy += dy
        self.velocity = vx, vy
        new = x + vx, y + vy
        if self._pos != new:
            buf = struct.pack(LINE_FORMAT, *new)
            self.history = [
                self.history[2],
                *self.history[2:-1],
                buf,
                buf,
            ]
            self._orientation = - math.atan2(vx, vy)
            self._pos = new
        self.dirty |= 1

    def act(self, action):
        if (xy := ACTION_DIRECTIONS.get(action)):
            self._move(*xy)

    def get_view_rects(self):
        x, y = self.pos
        x1, y1 = self.pos
        x2, y2 = self.pos
        x3, y3 = self.pos
        dx, dy = self.velocity
        for dx2 in range(abs(dx)):
            x1 += dx
        for dy2 in range(abs(dy)):
            y1 += dy
        need = [
            min(x, x1, x + dx, x - dx) - 5,
            min(y, y1, y + dy, y - dy) - 5,
            max(x, x1, x + dx, x - dx) + 5,
            max(y, y1, y + dy, y - dy) + 5,
        ]
        # XXX: Should
        return [need]

    def blocker_on_path_to(self, x, y):
        crash_ts = []
        circuit = self.group.circuit
        sx, sy = self.pos
        vx, vy = self.velocity
        dest_x = sx + vx + x
        dest_y = sy + vy + y
        print(end=' '*15)
        xrange = abs(sx - dest_x)
        for t in range(xrange + 1):
            t /= xrange
            x = (1-t) * sx + t * dest_x
            y = (1-t) * sy + t * dest_y
            ok = circuit.y_intersection_passable(round(x), y);
            if not ok:
                crash_ts.append(t)
                break
            print(f'{int(x):2}:{y:8.2f} {" ."[ok]}| ', end='')
        print()

        yrange = abs(sy - dest_y)
        for t in range(yrange + 1):
            t /= yrange
            x = (1-t) * sx + t * dest_x
            y = (1-t) * sy + t * dest_y
            ok = circuit.x_intersection_passable(x, round(y))
            print(f'{x:6.2f}:{int(y):4} {" ."[ok]}| ', end='')

            y = round(y)
            for x in reversed(_all(sx, dest_x)):
                print(f'{x} {y} {circuit.is_on_track(x,y):4}', end=' | ')
            print()

            if not ok:
                crash_ts.append(t)
                break
        if crash_ts:
            t = min(crash_ts)
            x = (1-t) * sx + t * dest_x
            y = (1-t) * sy + t * dest_y
            return x, y, t
        return None


def _all(a, b):
    a, b = sorted((a, b))
    return range(math.floor(a), math.ceil(b)+1)
