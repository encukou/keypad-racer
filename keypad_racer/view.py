import collections

Params = collections.namedtuple('Params', ('x', 'y', 'zoom', 'rot'))

class View:
    def __init__(self, ctx, scene):
        self.ctx = ctx
        self.scene = scene
        self._viewport = 0, 0, 800, 600
        self._params = Params(*scene.default_projection)

    @property
    def viewport(self):
        return self._viewport
    @viewport.setter
    def viewport(self, res):
        self._viewport = res
        self.adjust_zoom()

    @property
    def zoom(self):
        return self._params.zoom
    @zoom.setter
    def zoom(self, zoom):
        zoom_max = self._viewport[3] / 7
        if zoom > zoom_max:
            zoom = zoom_max
        if zoom < 1:
            zoom = 1
        self._params = self._params._replace(zoom=zoom)

    @property
    def pan(self):
        return self._params[:2]
    @pan.setter
    def pan(self, pan):
        x, y = pan
        self._params = self._params._replace(x=x, y=y)

    def adjust_zoom(self, dz=0):
        if self.scene.fixed_projection:
            return
        self.zoom = self._params.zoom * 1.1**dz

    def adjust_pan(self, dx, dy):
        self._params = self._params._replace(
            x=self._params.x + dx,
            y=self._params.y + dy,
        )

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
