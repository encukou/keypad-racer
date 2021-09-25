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

palette = Palette()
kbd = Keyboard()

window = Window(kbd)
ctx = window.ctx

if False:
    tutorial(ctx, palette, kbd, window)
elif False:
    circuit = Circuit(ctx, 'okruh.png')
    cars = CarGroup(ctx, circuit)

    car = Car(cars, palette.player_color(0), (0, 0))
    keypad = Keypad(ctx, car)
    keypad.claim_layout(kbd, NUMPAD_LAYOUT)
    scene = CarScene(car, keypad)
    window.add_view(View(ctx, scene))
elif False:
    keypad = Keypad(ctx)
    scene = KeypadScene(keypad, kbd)
    window.add_view(View(ctx, scene))
    keypad = Keypad(ctx)
    scene = KeypadScene(keypad, kbd)
    window.add_view(View(ctx, scene))
elif False:
    circuit = Circuit(ctx, 'okruh.png')
    cars = CarGroup(ctx, circuit)
    @fork
    async def add_cars():
        for i, layout in enumerate((NUMPAD_LAYOUT, QWERTY_LAYOUT, DVORAK_LAYOUT)):
            car = Car(cars, palette.player_color(i), (i, 0))
            keypad = Keypad(ctx, car)
            keypad.claim_layout(kbd, layout)
            scene = CarScene(car, keypad)
            window.add_view(View(ctx, scene))
else:
    circuit = Circuit(ctx, 'okruh.png')
    scene = TitleTop(ctx, window, kbd)
    window.add_view(View(ctx, scene))
    scene = TitleBottom(ctx, window, kbd, circuit)  # this has titlescreen logic :/
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
