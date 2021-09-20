import platform
import os
import sys

import pyglet
import moderngl

from . import resources

if platform.system() == "Darwin":
    pyglet.options["shadow_window"] = False

required_extensions = [
    # for https://github.com/moderngl/moderngl/issues/346 :
    'GL_ARB_multi_draw_indirect',
]

def check_gl_extensions():
    missing = []
    for ext in required_extensions:
        if not pyglet.gl.gl_info.have_extension(ext):
            missing.add(ext)
    if missing:
        print(
            'WARNING: This game requires OpenGL version 4.3 '
            + '(or the multi_draw_indirect extension).'
            + 'It will not work correctly on your machine.'
        )

class Window(pyglet.window.Window):
    def __init__(self):
        print(pyglet.gl.glext_arb)
        kwargs = {
            'caption': 'pyweek game',
            'width': 800,
            'height': 600,
        }
        config = pyglet.gl.Config(
            major_version=3,
            minor_version=3,
            forward_compatible=True,
            #depth_size=24,
            double_buffer=True,
        )
        super().__init__(config=config, **kwargs)
        check_gl_extensions()
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
ctx.enable_only(moderngl.BLEND | moderngl.PROGRAM_POINT_SIZE)

from .line import Line

line = Line(ctx, 0, 0, 1, 1, thickness=5)

from .car import CarGroup, Car

car_group = CarGroup(ctx, 5)
car1 = Car(car_group, (0, 1, 1), (1, 0))
car2 = Car(car_group, (1, 1, 0), (0, 0))
car3 = Car(car_group, (1, 0, 0), (2, 0))
car4 = Car(car_group, (0, 1, 0), (3, 4))
car5 = Car(car_group, (1, 0, 1), (2, 3))
for i in range(2):
    car3.kbd(0, True)
for i in range(3):
    car3.kbd(8, True)
for i in range(2):
    car3.kbd(7, True)

from .keyboard import Keyboard

kbd = Keyboard()
kbd.attach_to_window(window)

kbd.set_car(0, car1)
kbd.set_car(1, car2)
kbd.set_car(2, car3)
kbd.set_car(3, car4)

@window.event
def on_draw():
    fbo = ctx.screen
    fbo.use()
    ctx.clear(0.0, 0.0, 0.3, 0.0)
    line.draw()
    car_group.draw()

def tick(dt):
    car2.orientation += dt
pyglet.clock.schedule_interval(tick, 1/30)

@window.event
def on_mouse_press(x, y, button, mod):
    line.set_xy(x, y)

@window.event
def on_mouse_motion(x, y, dx, dy):
    line.set_xy(x, y)

def run():
    pyglet.app.run()
