import platform
import os
import sys
import random

import pyglet
import moderngl

from . import resources

if platform.system() == "Darwin":
    pyglet.options["shadow_window"] = False

required_extensions = [
]

def check_gl_extensions():
    missing = []
    for ext in required_extensions:
        if not pyglet.gl.gl_info.have_extension(ext):
            missing.append(ext)
    if missing:
        print(
            'WARNING: This game requires OpenGL version 3.3 '
            + 'It will not work correctly on your machine.'
        )

class Window(pyglet.window.Window):
    def __init__(self):
        print(pyglet.gl.glext_arb)
        kwargs = {
            'caption': 'Keypad Racer',
            'width': 800,
            'height': 600,
            'resizable': True,
        }
        config = pyglet.gl.Config(
            major_version=3,
            minor_version=3,
            forward_compatible=True,
            #depth_size=24,
            double_buffer=True,
        )
        super().__init__(config=config, **kwargs)
        self.set_minimum_size(640, 480)
        check_gl_extensions()
        if 'GAME_DEVEL_ENVIRON' in os.environ:
            self.set_location(200, 800)
        if 'GAME_DEVEL_ENVIRON2' in os.environ:
            self.set_location(1000, 200)

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

from .view import View

views = [View(ctx), View(ctx)]

def view_for_point(x, y):
    for view in views:
        if view.hit_test(x, y):
            return view

from .circuit import Circuit

circ = Circuit(ctx, 'okruh.png')

from .car import CarGroup, Car
from .palette import Palette
pal = Palette()

car_group = CarGroup(ctx, 9)
car1 = Car(car_group, pal.player_color(0), (1, 0))
car2 = Car(car_group, pal.player_color(1), (0, 0))
car3 = Car(car_group, pal.player_color(2), (2, 0))
car4 = Car(car_group, pal.player_color(3), (3, 4))
car5 = Car(car_group, pal.player_color(4), (2, 3))
car6 = Car(car_group, pal.player_color(5), (-2, -2))
car7 = Car(car_group, pal.player_color(6), (-3, -2))
car8 = Car(car_group, pal.player_color(7), (-4, -2))
car9 = Car(car_group, pal.player_color(8), (-5, -2))
for i in range(2):
    car3.kbd(0, True)
for i in range(3):
    car3.kbd(8, True)
for i in range(2):
    car3.kbd(7, True)

from .keyboard import Keyboard

def global_key_event(car, action, is_pressed):
    if action == 'fullscreen' and is_pressed:
        if window.fullscreen:
            window.set_fullscreen(False)
        else:
            disp = pyglet.canvas.get_display()
            screen = random.choice(disp.get_screens())
            window.set_fullscreen(True, screen=screen)

kbd = Keyboard()
kbd.attach_to_window(window)
kbd.attach_handler(global_key_event)

kbd.set_car(0, car1)
kbd.set_car(1, car2)
kbd.set_car(2, car3)
kbd.set_car(3, car4)

@window.event
def on_draw():
    fbo = ctx.screen
    fbo.use()
    ctx.scissor = (0, 0, window.width, window.height)
    ctx.clear(0.0, 0.0, 0.0, 0.0)
    for view in views:
        circ.draw(view)
        car_group.draw(view)

def tick(dt):
    car2.orientation += dt
pyglet.clock.schedule_interval(tick, 1/30)

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    view = view_for_point(x, y)
    if view:
        view.adjust_zoom(scroll_y)

current_view = None

@window.event
def on_mouse_press(x, y, button, mod):
    global current_view
    current_view = view_for_point(x, y)

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, mod):
    view = current_view or view_for_point(x, y)
    if view:
        view.adjust_pan(
            -dx*view.zoom/window.width*4,
            -dy*view.zoom/window.width*4,
        )

@window.event
def on_resize(w, h):
    BORDER = max(w/100, h/100)
    w, h = window.get_framebuffer_size()
    views[0].viewport = 0, 0, w/2-BORDER/2, h
    views[1].viewport = w/2+BORDER, 0, w/2-BORDER/2, h

on_resize(window.width, window.height)

def run():
    pyglet.app.run()
