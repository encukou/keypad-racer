
from . import resources

def pack_f1(f):
    return int(f * 255)

class Keypad:
    def __init__(self, ctx, car):
        self.ctx = ctx
        self.car = car

        pad_args = pack_f1(.8), pack_f1(.3), 0, 0
        kp_vertices = bytearray()
        for button in (
            *((x, y, 0, *pad_args) for x in (-1, 0, 1) for y in (-1, 0, 1)),
            (-1,  0, 1, pack_f1(.6), pack_f1(.3), 0, 1),
            ( 0,  0, 1, pack_f1(.6), pack_f1(.3), 1, 0),
            (+1,  0, 1, pack_f1(.6), pack_f1(.3), 0, 0),
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
                (kp_vbo, '2i1 3i1 4f1 2u1', 'uv', 'pad', 'feature', 'decal'),
            ],
        )
        self.pad_prog['antialias'] = 2

    def draw(self, view):
        view.setup(self.pad_prog)
        self.pad_prog['pos'] = self.car.pos
        self.pad_prog['top_pos'] = 0, 0, 0
        self.vao.render(self.ctx.TRIANGLES)
