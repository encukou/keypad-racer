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
        return tuple(float(c) for c in self._viewport)
    @viewport.setter
    def viewport(self, res):
        self._viewport = tuple(ConstantValue(x) for x in res)
        self.last_view_rect = None
        self.adjust_zoom()

    def set_viewport(self, res, duration=0):
        if duration == 0:
            self._viewport = tuple(ConstantValue(x) for x in res)
        else:
            self._viewport = tuple(
                AnimatedValue(m, x, duration)
                for m, x in zip(self._viewport, res)
            )
        self.last_view_rect = None
        self.adjust_zoom()

    def set_view_rect(self, view_rect, duration=None):
        if view_rect != self.last_view_rect or duration:
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
        scale_max = self._viewport[3].end / 7
        if scale > scale_max:
            scale = scale_max
        if scale < 1:
            scale = 1
        self._params = self._params._replace(scale_x=scale, scale_y=scale)

    def adjust_zoom(self, dz=0):
        if self.scene.fixed_projection:
            return
        self.zoom = AnimatedValue(self.zoom, self.zoom.end * 1.1**dz, 0.1)

    def adjust_pan(self, dx, dy, duration=0.1):
        if self.scene.fixed_projection:
            return
        dx *= self.scale[0].end*self.zoom.end/self._viewport[2].end*2
        dy *= self.scale[1].end*self.zoom.end/self._viewport[3].end*2
        self.pan = (
            AnimatedValue(self.pan[0], self.pan[0].end - dx, duration),
            AnimatedValue(self.pan[1], self.pan[1].end - dy, duration),
        )

    def setup(self, *programs):
        viewport = self.viewport
        params = self._params
        self.ctx.scissor = viewport
        self.ctx.viewport = viewport
        params = (
            float(params.x) + float(self.pan[0]),
            float(params.y) + float(self.pan[1]),
            float(params.scale_x) * float(self.zoom),
            float(params.scale_y) * float(self.zoom),
        )
        for program in programs:
            program['viewport'] = viewport
            program['projection_params'] = params

    def hit_test(self, x, y):
        x, y = self.screen_to_view(x, y)
        return -1 <= x <= 1 and -1 <= y <= 1

    def screen_to_view(self, x, y):
        x1, y1, w, h = self.viewport
        return ((x - x1) / w * 2 - 1, (y - y1) / h * 2 - 1)

    def view_to_grid(self, x, y):
        xs, ys, xz, yz = self._params
        return (
            x * xz.end + xs.end,
            y * yz.end + ys.end,
        )
    def screen_to_grid(self, x, y):
        return self.view_to_grid(*self.screen_to_view(x, y))

    def draw(self):
        self.scene.draw(self)
