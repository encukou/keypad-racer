
from . import resources

def pack_f1(f):
    return int(f * 255)

SKIPS = {
    (-1, -1): 0,
    ( 0, -1): 1,
    (+1, -1): 2,
    (-1,  0): 3,
    ( 0,  0): 4,
    (+1,  0): 5,
    (-1, +1): 6,
    ( 0, +1): 7,
    (+1, +1): 8,
}

class Keypad:
    def __init__(self, ctx, car):
        self.ctx = ctx
        self.car = car

        # feature: size, corner radius, handle, brake stuff
        pad_args = pack_f1(.65), pack_f1(2/3), 0, 0
        kp_vertices = bytearray()
        _ = None
        for button in (
            *([x, y, 0,  n, *pad_args] for (x, y), n in SKIPS.items()),
            [-1,  0, 1, 9, pack_f1(.5), pack_f1(1), 0, 1],
            [ 0,  0, 1, 10, pack_f1(.5), pack_f1(1), 1, 0],
            [+1,  0, 1, 11, pack_f1(.45), pack_f1(1/4), 0, 0],
        ):
            kp_vertices.extend(b % 256 for b in (
                1, 255, *button, 0, 0,
                255, 255, *button, 0, 0,
                1,   1, *button, 0, 0,
                255, 255, *button, 0, 0,
                1,   1, *button, 0, 0,
                255,   1, *button, 0, 0,
            ))
        kp_vbo = ctx.buffer(kp_vertices)

        self.pad_prog = ctx.program(
            vertex_shader=resources.get_shader('shaders/pad.vert'),
            fragment_shader=resources.get_shader('shaders/pad.frag'),
        )
        self.vao = ctx.vertex_array(
            self.pad_prog,
            [
                (kp_vbo, '2i1 4i1 4f1 2u1', 'uv', 'pad', 'feature', 'decal'),
            ],
        )
        self.pad_prog['antialias'] = 2
        self.pad_prog['color'] = self.car.color

    def draw(self, view):
        view.setup(self.pad_prog)
        x, y = self.car.pos
        xx, yy = self.car.velocity
        self.pad_prog['pos'] = x+xx, y+yy
        self.pad_prog['top_pos'] = 0, 0, 0
        self.pad_prog['skip'] = SKIPS.get((-xx, -yy), -1)
        # import math; import time; self.pad_prog['button_size'] = abs(math.sin(time.time()*1))
        self.pad_prog['button_size'] = 1
        self.vao.render(
            self.ctx.TRIANGLES,
            vertices=6*9,
        )
