from pathlib import Path

import pyglet

from .window import Window
from .view import View
from .scene import CarScene, KeypadScene
from .car import CarGroup, Car
from .palette import Palette
from .keyboard import Keyboard, QWERTY_LAYOUT, NUMPAD_LAYOUT, DVORAK_LAYOUT
from .keypad import Keypad
from .circuit import Circuit
from .tutorial import tutorial
from .anim import fork, Wait
from .title import TitleTop, TitleBottom
#from . import music

palette = Palette()
kbd = Keyboard()

window = Window(kbd)
ctx = window.ctx

# Couldn't get music to work. These tracks would work great:
# - menu: https://opengameart.org/content/arcade-racing-tune
# - game: https://opengameart.org/content/tactical-pursuit
#music.play(music.menu_music)

def global_key_event(action, is_pressed):
    if action == 'fullscreen' and is_pressed:
        if window.fullscreen:
            window.fullscreen = False
        else:
            window.fullscreen = True

try:
    conf = Path('keypad_racer.conf').read_text()
except FileNotFoundError:
    kbd.attach_handler(global_key_event)
    tutorial(ctx, palette, kbd, window)
else:
    circuit = Circuit(ctx, 'okruh.png')
    scene = TitleTop(ctx, window, kbd)
    window.add_view(View(ctx, scene))
    scene = TitleBottom(ctx, window, kbd, circuit, conf)  # this has titlescreen logic :/
    window.add_view(View(ctx, scene))

def run():
    pyglet.clock.schedule_interval(id, 1/60)
    pyglet.app.run()
