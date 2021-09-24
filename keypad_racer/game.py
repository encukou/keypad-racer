import pyglet

from .window import Window
from .view import View
from .scene import CarScene, TutorialScene
from .car import CarGroup, Car
from .palette import Palette
from .keyboard import Keyboard
from .keypad import Keypad
from .circuit import Circuit

pal = Palette()
kbd = Keyboard()

window = Window(kbd)
ctx = window.ctx
circuit = Circuit(ctx, 'okruh.png')

cars = CarGroup(ctx, circuit)
for i in range(2):
    car = Car(cars, pal.player_color(i), (i*8, 0))
    keypad = Keypad(ctx, car)
    kbd.set_pad(i, keypad)
    view = View(ctx, CarScene(car, keypad))
    window.add_view(view)

#window.add_view(View(ctx, TutorialScene(car, view)))

def global_key_event(car, action, is_pressed):
    if action == 'fullscreen' and is_pressed:
        if window.fullscreen:
            window.fullscreen = False
        else:
            window.fullscreen = True

kbd.attach_handler(global_key_event)

def run():
    pyglet.app.run()
