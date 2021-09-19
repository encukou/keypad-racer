import numpy
import moderngl

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
                (.25, .25),
                (.25, -.25),
                (.4, -.8),
                (.4, -.8),
            ),
            dtype='f4',
        )

        vbo = ctx.buffer(vertices.tobytes())
        thick_vbo = ctx.buffer(bytes([30]))
        self.vao = ctx.vertex_array(
            prog,
            [
                (vbo, '2f4', 'point'),
                (thick_vbo, '1i1 /r', 'thickness'),
            ],
        )
        print(sorted(prog))
        prog['antialias'] = 2.0
        prog['resolution'] = 800, 600

    def draw(self):
        self.vao.render(moderngl.LINE_STRIP_ADJACENCY)
