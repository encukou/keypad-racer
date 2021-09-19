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
            sample_buffers=1,
            samples=16,
        )
        super().__init__(config=config, caption='pyweek game', width=800, height=600)
        if 'GAME_DEVEL_ENVIRON' in os.environ:
            self.set_location(150, 150)

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

prog = ctx.program(
    vertex_shader=resources.get_text('shaders/vertex.glsl'),
    fragment_shader=resources.get_text('shaders/fragment.glsl'),
)

x = numpy.linspace(-1.0, 1.0, 50)
y = numpy.random.rand(50) - 0.5
r = numpy.ones(50)
g = numpy.zeros(50)
b = numpy.zeros(50)

vertices = numpy.dstack([x, y, r, g, b])
vbo = ctx.buffer(vertices.astype('f4').tobytes())
vao = ctx.vertex_array(prog, vbo, 'in_vert', 'in_color')

fbo = ctx.simple_framebuffer((512, 512))
fbo.use()
fbo.clear(0.0, 0.0, 0.0, 1.0)
vao.render(moderngl.LINE_STRIP)

@window.event
def on_draw():
    fbo = ctx.screen
    fbo.use()
    ctx.clear(0.0, 0.0, 0.3, 0.0)
    vao.render(moderngl.LINE_STRIP)

pyglet.app.run()
