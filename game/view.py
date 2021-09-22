
class View:
    def __init__(self, ctx):
        self.ctx = ctx
        self.programs = []
        self._resolution = 800, 600
        self._params = [0, 5, 10, 0]

    @property
    def resolution(self):
        return self._resolution
    @resolution.setter
    def resolution(self, res):
        self._resolution = res
        for program in self.programs:
            program['resolution'] = res
        self.adjust_zoom()

    @property
    def zoom(self):
        return self._params[2]
    @zoom.setter
    def zoom(self, zoom):
        self._params[2] = zoom
        params = tuple(self._params)
        for program in self.programs:
            program['projection_params'] = params

    @property
    def pan(self):
        return self._params[:2]
    @pan.setter
    def pan(self, pan):
        self._params[:2] = pan
        params = tuple(self._params)
        for program in self.programs:
            program['projection_params'] = params

    def adjust_zoom(self, dz=0):
        zoom = self.zoom * 1.1**dz
        zoom_max = self._resolution[1] / 7
        if zoom > zoom_max:
            zoom = zoom_max
        if zoom < 1:
            zoom = 1
        self.zoom = zoom

    def adjust_pan(self, dx, dy):
        x, y = self._params[:2]
        x += dx
        y += dy
        self.pan = x, y

    def register_programs(self, *programs):
        self.programs.extend(programs)
        params = tuple(self._params)
        for program in programs:
            program['resolution'] = self._resolution
            program['projection_params'] = params
