import struct

from . import resources
from .anim import AnimatedValue, ConstantValue, autoschedule, Wait
from .text import get_font
from .palette import Palette

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
    def __init__(self, ctx, car=None, color=None):
        self.ctx = ctx
        self.car = car
        if car:
            car.keypad = self
        self.font = None
        self.callbacks = {}
        self.pos = 0, 0
        self.blocked = (0,) * 12
        self.xblocked = [0] * 12
        self.assignments = {}
        self.player_name = None

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
        if color:
            color = color
        elif car:
            color = car.color
        else:
            color = Palette().player_color(0)
        self.color = color
        self.pad_prog['color'] = color

        self.update()
        self.enabled = True

    def draw(self, view):
        view.setup(self.pad_prog)
        self.pad_prog['pos'] = self.pos
        self.pad_prog['top_pos'] = 0, 0, 0
        self.pad_prog['button_size'] = self.button_size
        self.pad_prog['m_blocked'] = tuple(self.blocked)
        if self.font:
            self.font.texture.use(location=0)
        self.vao.render(
            self.ctx.TRIANGLES,
            vertices=6*9,
        )

    def claim_layout(self, kbd, layout):
        for i, key in enumerate(layout):
            kbd.claim_key(key, self, i)

    def unassign_all_keys(self, kbd):
        for key in list(self.assignments.values()):
            kbd.unclaim_key(key)

    def kbd(self, direction, is_pressed):
        if is_pressed and self.enabled:
            if self.car:
                self.car.act(direction)
            if direction in self.callbacks:
                self.callbacks[direction]()

    def set_callback(self, button, action):
        if action is None:
            self.callbacks.pop(button, None)
        else:
            self.callbacks[button] = action

    @autoschedule
    async def pause(self, blocker, fadeout_time=.2, fadein_time=.1):
        self.button_size = AnimatedValue(self.button_size, -1, fadeout_time)
        self.enabled = False
        if isinstance(blocker, float):
            blocker = Wait(blocker)
        await blocker
        self.button_size = ConstantValue(0)
        self.enabled = True
        self.update()
        self.button_size = AnimatedValue(self.button_size, 1, fadein_time)

    def update(self, car=None):
        if car is None:
            car = self.car
        if car is None:
            xx = 1234
            yy = 1234
        else:
            x, y = car.pos
            xx, yy = car.velocity
            self.pos = x+xx, y+yy
        self.blocked = tuple((
            *(
                -1 if (x,y) == (-xx,-yy)
                else -1 if self.xblocked[x+y*3+4]
                else 1 if (x+y*3+4) not in self.assignments
                else bool(car.blocker_on_path_to(x, y)) if car
                else 0
                for x in (-1, 0, 1) for y in (-1, 0, 1)
            ),
            0, 0, 0,
        ))

    def assign_char(self, button, label, key):
        if key is None:
            self.assignments.pop(button, None)
        else:
            self.assignments[button] = key
        if label == ' ':
            pass
        elif label.startswith(' '):
            label = label[1:]
        elif label.endswith(' '):
            label = label[:-1]
        if not label:
            data = bytes(12)
        else:
            self.font = get_font(self.ctx)
            glyph = self.font.get_glyph(label, fallback='☼')
            if glyph is None:
                data = bytes(14)
            else:
                x, y, w, h = glyph.plane_bounds
                ratio = 1
                if w > h:
                    ratio = w / h
                data = struct.pack(
                    '=4e3e',
                    *glyph.atlas_bounds,
                    ratio, w, h,
                )
        for i in range(6):
            self.kp_vbo.write(data, offset=24*(i+6*button)+10)
        self.update()
