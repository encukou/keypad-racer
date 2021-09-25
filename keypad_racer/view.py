import collections
import math

from .anim import AnimatedValue, ConstantValue, sine_inout

Params = collections.namedtuple('Params', ('x', 'y', 'scale_x', 'scale_y'))

# Original idea: a view is controlled by two rectangles:
# - what *should* be in the scene
# - what *needs* to be in the scene
# These are interpolated based on a scale level with fixed limits

# But it seems one rect is enough...?

def visible_rect_to_scene(rect, viewport):
    pan_x = (rect[0] + rect[2]) / 2
    pan_y = (rect[1] + rect[3]) / 2
    scale_x = (rect[2] - rect[0]) / viewport[2] / 2
    scale_y = (rect[3] - rect[1]) / viewport[3] / 2
    scale = max(scale_x, scale_y)
    if viewport[2] < viewport[3]:
        scale_x = scale * viewport[2]
        scale_y = scale * viewport[3]
    if viewport[3] < viewport[2]:
        scale_x = scale * viewport[2]
        scale_y = scale * viewport[3]
    return Params(pan_x, pan_y, scale_x, scale_y), scale

class View:
    def __init__(self, ctx, scene):
        self.ctx = ctx
        self.scene = scene
        self._viewport = tuple(ConstantValue(x) for x in (0, 0, 800, 600))
        self._params = Params(*(ConstantValue(p) for p in scene.default_projection))
        self.zoom = ConstantValue(1)
        self.pan = ConstantValue(0), ConstantValue(0)
        self.last_view_rect = None

    @property
    def viewport(self):
        return self._viewport
    @viewport.setter
    def viewport(self, res):
        self._viewport = res
        self.last_view_rect = None
        self.adjust_scale()

    def set_view_rect(self, view_rect, duration=None):
        if view_rect != self.last_view_rect:
            if duration is None:
                duration = 0.75
                if self.last_view_rect is None:
                    duration = 0
            self.last_view_rect = view_rect
            r, z = visible_rect_to_scene(view_rect, self.viewport)
            sp = self._params
            self._params = Params(
                AnimatedValue(sp[0], r.x, duration, sine_inout),
                AnimatedValue(sp[1], r.y, duration, sine_inout),
                AnimatedValue(sp[2], r.scale_x, duration, sine_inout),
                AnimatedValue(sp[3], r.scale_y, duration, sine_inout),
            )
            self.zoom = AnimatedValue(self.zoom, 1/3+self.zoom.end*2/3, duration, sine_inout)
            self.pan = (
                AnimatedValue(self.pan[0], self.pan[0].end*2/3, duration, sine_inout),
                AnimatedValue(self.pan[1], self.pan[1].end*2/3, duration, sine_inout),
            )

    @property
    def scale(self):
        return self._params.scale_x, self._params.scale_y
    @scale.setter
    def scale(self, scale):
        scale_max = self._viewport[3] / 7
        if scale > scale_max:
            scale = scale_max
        if scale < 1:
            scale = 1
        self._params = self._params._replace(scale_x=scale, scale_y=scale)

    def adjust_zoom(self, dz=0):
        self.zoom = AnimatedValue(self.zoom, self.zoom.end * 1.1**dz, 0.1)

    def adjust_scale(self, dz=0):
        if self.scene.fixed_projection:
            return
        self.zoom = AnimatedValue(self.zoom, self.zoom.end * 1.1**dz, 0.2)

    def adjust_pan(self, dx, dy):
        self.pan = (
            AnimatedValue(self.pan[0], self.pan[0].end + dx, 0.1),
            AnimatedValue(self.pan[1], self.pan[1].end + dy, 0.1),
        )

    def setup(self, *programs):
        self.ctx.scissor = tuple(self._viewport)
        self.ctx.viewport = tuple(self._viewport)
        params = (
            float(self._params.x) + float(self.pan[0]),
            float(self._params.y) + float(self.pan[1]),
            float(self._params.scale_x) * float(self.zoom),
            float(self._params.scale_y) * float(self.zoom),
        )
        for program in programs:
            program['viewport'] = tuple(self._viewport)
            program['projection_params'] = params

    def hit_test(self, x, y):
        x1, y1, w, h = self._viewport
        x2 = x1 + w
        y2 = y1 + h
        return x1 <= x <= x2 and y1 <= y <= y2

    def draw(self):
        self.scene.draw(self)
