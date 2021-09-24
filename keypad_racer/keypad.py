
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
        self.pad_prog['color'] = self.car.color


        """
        import struct
        self.helper_vbo = ctx.buffer(self._helper_ba(), dynamic=True)
        self.helper_prog = ctx.program(
            vertex_shader=resources.get_shader('shaders/rail.vert'),
            geometry_shader=resources.get_shader('shaders/rail.geom'),
            fragment_shader=resources.get_shader('shaders/rail.frag'),
        )
        self.helper_vao = ctx.vertex_array(
            self.helper_prog,
            [
                (self.helper_vbo, '2f2', 'point'),
                (ctx.buffer(b'\xff\xff\xff\x88\x00'), '4f1 u1 /i', 'color', 'thickness'),
            ],
        )
        self.helper_prog['grid_origin'] = 0, 0
        """

    def _helper_ba(self):
        ba = bytearray()
        dx, dy = self.car.velocity
        for x in -1, 0, 1:
            for y in -1, 0, 1:
                ba.extend(bytes(8))
                blk = self.car.blocker_on_path_to(x, y)
                px = dx + x
                py = dy + y
                if blk:
                    _, _, t = blk
                    px *= t
                    py *= t
                import struct
                ba.extend(struct.pack('=4e', *(b for b in (px, py, px, py))))
        ba.extend(bytes(8))
        return ba

    def draw(self, view):
        view.setup(self.pad_prog)
        x, y = self.car.pos
        xx, yy = self.car.velocity
        self.pad_prog['pos'] = x+xx, y+yy
        self.pad_prog['top_pos'] = 0, 0, 0
        self.pad_prog['skip'] = SKIPS.get((-xx, -yy), -1)
        # import math; import time; self.pad_prog['button_size'] = abs(math.sin(time.time()*1))
        self.pad_prog['button_size'] = 1
        self.pad_prog['m_blocked'] = tuple((
            *(bool(self.car.blocker_on_path_to(x, y))
              for x in (-1, 0, 1) for y in (-1, 0, 1)),
            0, 0, 0,
        ))
        self.vao.render(
            self.ctx.TRIANGLES,
            vertices=6*9,
        )

        """
        view.setup(self.helper_prog)
        self.helper_vbo.write(self._helper_ba())
        self.helper_prog['grid_origin'] = -x, -y
        self.helper_vao.render(
            self.ctx.LINE_STRIP_ADJACENCY,
        )
        """

    def kbd(self, direction, is_pressed):
        if is_pressed:
            self.car.act(direction)
