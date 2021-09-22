
class View:
    def __init__(self, ctx):
        self.ctx = ctx
        self.programs = []
        self._resolution = 800, 600
        self._zoom = 10
        self._pan = 0, 0

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
        return self._zoom
    @zoom.setter
    def zoom(self, zoom):
        self._zoom = zoom
        for program in self.programs:
            program['zoom'] = zoom

    @property
    def pan(self):
        return self._pan
    @pan.setter
    def pan(self, pan):
        self._pan = pan
        for program in self.programs:
            program['pan'] = pan

    def adjust_zoom(self, dz=0):
        zoom = self._zoom * 1.1**dz
        zoom_max = self._resolution[1] / 7
        if zoom > zoom_max:
            zoom = zoom_max
        if zoom < 1:
            zoom = 1
        self.zoom = zoom

    def adjust_pan(self, dx, dy):
        x, y = self._pan
        x += dx
        y += dy
        self.pan = x, y

    def register_programs(self, *programs):
        self.programs.extend(programs)
        for program in programs:
            program['resolution'] = self._resolution
            program['zoom'] = self._zoom
            program['pan'] = self._pan
