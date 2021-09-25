import pyglet

from .window import Window
from .view import View
from .scene import CarScene
from .car import CarGroup, Car
from .palette import Palette
from .keyboard import Keyboard
from .keypad import Keypad
from .circuit import Circuit
from .tutorial import tutorial

pal = Palette()
kbd = Keyboard()

window = Window(kbd)
ctx = window.ctx

for scene in tutorial(ctx, pal, kbd):
    window.add_view(View(ctx, scene))

def global_key_event(action, is_pressed):
    if action == 'fullscreen' and is_pressed:
        if window.fullscreen:
            window.fullscreen = False
        else:
            window.fullscreen = True

kbd.attach_handler(global_key_event)

def run():
    pyglet.clock.schedule_interval(id, 1/60)
    pyglet.app.run()
