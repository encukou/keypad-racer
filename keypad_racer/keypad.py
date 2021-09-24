import struct

from . import resources
from .anim import AnimatedValue, ConstantValue, autoschedule, Wait
from .text import get_font

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
        car.keypad = self
        self.font = None

        self.button_size = ConstantValue(1)

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
                1, 255, *button, *bytes(14),
                255, 255, *button, *bytes(14),
                1,   1, *button, *bytes(14),
                255, 255, *button, *bytes(14),
                1,   1, *button, *bytes(14),
                255,   1, *button, *bytes(14),
            ))
        self.kp_vbo = ctx.buffer(kp_vertices)

        self.pad_prog = ctx.program(
            vertex_shader=resources.get_shader('shaders/pad.vert'),
            fragment_shader=resources.get_shader('shaders/pad.frag'),
        )
        self.vao = ctx.vertex_array(
            self.pad_prog,
            [
                (self.kp_vbo, '2i1 4i1 4f1 4f2 3f2',
                 'uv', 'pad', 'feature', 'decal', 'decal_size'),
            ],
        )
        self.pad_prog['color'] = self.car.color
        #self.pad_prog['atlas_tex'] = 0

        self.update()
        self.enabled = True

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
        self.pad_prog['pos'] = self.pos
        self.pad_prog['top_pos'] = 0, 0, 0
        self.pad_prog['button_size'] = self.button_size
        self.pad_prog['m_blocked'] = self.blocked
        if self.font:
            self.font.texture.use(location=0)
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
        if is_pressed and self.enabled:
            self.car.act(direction)

    @autoschedule
    async def pause(self, duration):
        self.button_size = AnimatedValue(self.button_size, -1, .2)
        self.enabled = False
        await Wait(duration)
        self.button_size = ConstantValue(0)
        self.enabled = True
        self.update()
        self.button_size = AnimatedValue(self.button_size, 1, .1)

    def update(self):
        x, y = self.car.pos
        xx, yy = self.car.velocity
        self.pos = x+xx, y+yy
        self.blocked = tuple((
            *(
                -1
                if (x,y) == (-xx,-yy)
                else bool(self.car.blocker_on_path_to(x, y))
                for x in (-1, 0, 1) for y in (-1, 0, 1)
            ),
            0, 0, 0,
        ))

    def set_decal(self, button, char):
        self.font = get_font(self.ctx)
        glyph = self.font.get_glyph(char, fallback='☼')
        if glyph is None:
            data = bytes(14)
        else:
            data = struct.pack(
                '=4e3e',
                *glyph.atlas_bounds,
                *glyph.plane_bounds[1:],
            )
            print(glyph.atlas_bounds)
        for i in range(6):
            self.kp_vbo.write(data, offset=24*(i+6*button)+10)
        #for i, b in enumerate(self.kp_vbo.read()):
        #    if i%24 == 0: print()
        #    print(b, end=',')
