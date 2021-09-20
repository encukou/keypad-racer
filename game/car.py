import moderngl
import struct
import math

from . import resources

BASIC_FORMAT = '=2f1f'
FULL_FORMAT = BASIC_FORMAT + '3f'
STRIDE = struct.calcsize(FULL_FORMAT)

HISTORY = 1
LINE_FORMAT = '=2f'
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
    def __init__(self, ctx, max_cars):
        self.ctx = ctx
        self.max_cars = max_cars
        self.cars = []

        prog = ctx.program(
            vertex_shader=resources.get_shader('shaders/car.vert'),
            fragment_shader=resources.get_shader('shaders/car.frag'),
        )

        vertices = bytes((
            1, 255,
            255, 255,
            1, 1,
            255, 1,
        ))
        self.uv_vbo = ctx.buffer(vertices)
        self.cars_vbo = ctx.buffer(bytes(STRIDE * max_cars), dynamic=True)
        self.vao = ctx.vertex_array(
            prog,
            [
                (self.uv_vbo, '2i1', 'uv'),
                (self.cars_vbo, '2f4 f4 3f4 /i', 'pos', 'orientation', 'color'),
            ],
        )
        prog['zoom'] = 800*15
        prog['pan'] = 0, 0
        prog['resolution'] = 800, 600

    def draw(self):
        for car in self.cars:
            if car.dirty:
                car.update_group()
        if self.cars:
            self.vao.render(
                moderngl.TRIANGLE_STRIP,
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
        self.velocity = 0, 1
        self.dirty = 2      # bitfield: 1=position/orientation; 2=color

    def update_group(self):
        if self.dirty == 1:
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
    @pos.setter
    def pos(self, new):
        self._pos = new
        self.dirty |= 1

    def kbd(self, action, is_pressed):
        if is_pressed and (xy := ACTION_DIRECTIONS.get(action)):
            dx, dy = xy
            x, y = self.pos
            vx, vy = self.velocity
            vx += dx
            vy += dy
            self.velocity = vx, vy
            self.pos = x + vx, y + vy
            self.orientation = math.tau/4 - math.atan2(vy, vx)
