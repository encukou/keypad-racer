import numpy
import moderngl
import time
import math

from . import resources

class Line:
    def __init__(self, ctx, x1, y1, x2, y2, thickness=2):
        self.ctx = ctx
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.thickness = thickness

        prog = ctx.program(
            vertex_shader=resources.get_shader('shaders/line_segment.vert'),
            fragment_shader=resources.get_shader('shaders/line_segment.frag'),
            geometry_shader=resources.get_shader('shaders/line_segment.geom'),
        )

        vertices = numpy.array(
            (
                (-.25, -.25),
                (-.25, -.25),
                (-.25, -.25),
                (.0, .0),
                (.25, -.25),
                (.4, -.8),
                (.4, -.8),
            ),
            dtype='f4',
        )

        self.vbo = ctx.buffer(vertices.tobytes())
        thick_vbo = ctx.buffer(bytes([60]))
        self.vao = ctx.vertex_array(
            prog,
            [
                (self.vbo, '2f4', 'point'),
                (thick_vbo, '1i1 /r', 'thickness'),
            ],
        )
        print(sorted(prog))
        prog['antialias'] = 2.0
        prog['resolution'] = 600, 600

    def set_xy(self, x, y):
        print(x, y)
        arr = numpy.array([(x-300)/300, (y-300)/300], dtype='f4')
        self.vbo.write(arr.tobytes(), offset=4*2*4)

    def draw(self):
        #t = time.time()
        self.vao.render(moderngl.LINE_STRIP_ADJACENCY)
