import pyglet

from .window import Window
from .view import View
from .scene import CarScene
from .car import CarGroup, Car
from .palette import Palette
from .keyboard import Keyboard, QWERTY_LAYOUT, NUMPAD_LAYOUT
from .keypad import Keypad
from .circuit import Circuit
from .tutorial import tutorial

palette = Palette()
kbd = Keyboard()

window = Window(kbd)
ctx = window.ctx

if True:
    for scene in tutorial(ctx, palette, kbd):
        window.add_view(View(ctx, scene))
else:
    circuit = Circuit(ctx, 'okruh.png')
    cars = CarGroup(ctx, circuit)

    car = Car(cars, palette.player_color(0), (0, 0))
    keypad = Keypad(ctx, car)
    keypad.claim_layout(kbd, NUMPAD_LAYOUT)
    scene = CarScene(car, keypad)
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
