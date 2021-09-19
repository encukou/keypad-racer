import platform
import os
import sys

import pyglet
import moderngl
import numpy

from . import resources

if platform.system() == "Darwin":
    pyglet.options["shadow_window"] = False

class Window(pyglet.window.Window):
    def __init__(self):
        config = pyglet.gl.Config(
            major_version=3,
            forward_compatible=True,
            #depth_size=24,
            double_buffer=True,
        )
        super().__init__(config=config, caption='pyweek game', width=800, height=600)
        if 'GAME_DEVEL_ENVIRON' in os.environ:
            self.set_location(200, 800)

    def on_resize(self, width, height):
        pass

    def on_draw(self):
        pass

window = Window()
ctx = moderngl.create_context()

print("ModernGL:", moderngl.__version__)
print("vendor:", ctx.info["GL_VENDOR"])
print("renderer:", ctx.info["GL_RENDERER"])
print("version:", ctx.info["GL_VERSION"])
print("python:", sys.version)
print("platform:", sys.platform)
print("code:", ctx.version_code)

ctx.blend_func = ctx.SRC_ALPHA, ctx.ONE_MINUS_SRC_ALPHA
#ctx.enable_only(moderngl.BLEND | moderngl.PROGRAM_POINT_SIZE)

prog = ctx.program(
    vertex_shader=resources.get_shader('shaders/vertex.glsl'),
    fragment_shader=resources.get_shader('shaders/fragment.glsl'),
)

x = numpy.linspace(-1.0, 1.0, 50)
y = numpy.random.rand(50) - 0.5
r = numpy.ones(50)
g = numpy.zeros(50)
b = numpy.zeros(50)

vertices = numpy.dstack([x, y, r, g, b])
vbo = ctx.buffer(vertices.astype('f4').tobytes())
vao = ctx.vertex_array(prog, vbo, 'in_vert', 'in_color')

from .line import Line

line = Line(ctx, 0, 0, 1, 1, thickness=5)

@window.event
def on_draw():
    fbo = ctx.screen
    fbo.use()
    ctx.clear(0.0, 0.0, 0.3, 0.0)
    vao.render(moderngl.LINE_STRIP)
    line.draw()

pyglet.app.run()
