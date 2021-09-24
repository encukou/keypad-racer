import collections

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
        self._viewport = 0, 0, 800, 600
        self._params = Params(*scene.default_projection)
        self.zoom = 1
        self.pan = 0, 0

    @property
    def viewport(self):
        return self._viewport
    @viewport.setter
    def viewport(self, res):
        self._viewport = res
        self.adjust_scale()

    def set_view_rects(self, should, need=None):
        r, z = visible_rect_to_scene(should, self.viewport)
        self._params = Params(
            r.x + self.pan[0],
            r.y + self.pan[1],
            r.scale_x*self.zoom,
            r.scale_y*self.zoom,
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
        self.zoom = self.zoom * 1.1**dz
    def adjust_scale(self, dz=0):
        if self.scene.fixed_projection:
            return
        self.zoom = self.zoom * 1.1**dz

    def adjust_pan(self, dx, dy):
        self.pan = self.pan[0] + dx, self.pan[1] + dy

    def setup(self, *programs):
        self.ctx.scissor = tuple(self._viewport)
        self.ctx.viewport = tuple(self._viewport)
        for program in programs:
            program['viewport'] = tuple(self._viewport)
            program['projection_params'] = tuple(self._params)

    def hit_test(self, x, y):
        x1, y1, w, h = self._viewport
        x2 = x1 + w
        y2 = y1 + h
        return x1 <= x <= x2 and y1 <= y <= y2

    def draw(self):
        self.scene.draw(self)
