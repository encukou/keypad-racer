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
    def __init__(self, view, max_cars):
        self.ctx = ctx = view.ctx
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
        self.car_prog['antialias'] = 2

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
        print(list(line_t.read()))
        self.line_vao = ctx.vertex_array(
            self.line_prog,
            [
                (self.line_vbo, '2i2', 'point'),
                (line_t, 'f1', 't'),
            ],
            skip_errors=True,
        )
        self.line_prog['antialias'] = 8

        view.register_programs(self.car_prog, self.line_prog)

    def draw(self):
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
            self._orientation = math.tau/4 - math.atan2(vy, vx)
            self._pos = new
        self.dirty |= 1

    def kbd(self, action, is_pressed):
        if is_pressed and (xy := ACTION_DIRECTIONS.get(action)):
            self._move(*xy)
