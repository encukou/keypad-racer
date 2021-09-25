from .car import CarGroup, Car
from .circuit import Circuit
from .scene import Scene, CarScene
from .keypad import Keypad
from .view import View
from .text import Text
from .anim import autoschedule, Wait, AnimatedValue, ConstantValue, sine_inout
from .anim import sine_in, sine_out

def animN(src, dest, *args, **kwargs):
    return tuple(
        AnimatedValue(a, ConstantValue(b), *args, **kwargs)
        for a, b in zip(src, dest)
    )

def tutorial(ctx, palette, kbd):
    circuit = Circuit(ctx, 'okruh.png')
    cars = CarGroup(ctx, circuit)

    car = Car(cars, palette.player_color(0), (0, 0))
    keypad = Keypad(ctx)
    kbd.set_pad(0, keypad)
    keypad.blocked = (-1,) * 12

    car_scene = TutorialCarScene(car, keypad)
    yield car_scene

    scene = TutorialScene()
    yield scene

    scene.things.append(
        Text(car.group.ctx, 'Welcome to\nKeypad Racer!', ypos=1, outline=True)
    )

    async def wait_for_text(text, delay=1):
        scene.things.append(text)
        text.body_color = animN(text.body_color, (*car.color,1), 0.5, sine_out)
        await Wait(delay)
        text.body_color = animN(text.body_color, (1, 1, 1, 1), 1, sine_in)

    @autoschedule
    async def cont():
        await Wait(0.5)
        ypos = -2
        text = Text(car.group.ctx, '← This is a race car.  ', ypos=ypos, scale=0.75, color=(0,0,0,0))
        ypos -= 1
        car_scene.view_rect = (-3, -3, 3, 3)
        await wait_for_text(text, delay=1)
        text = Text(car.group.ctx, "Let's learn to control it.", ypos=ypos, scale=0.65, color=(0,0,0,0))
        ypos -= 1
        await wait_for_text(text, delay=1)
        text = Text(car.group.ctx, "If you have a numeric keypad,", ypos=ypos, scale=0.65, color=(0,0,0,0))
        ypos -= 0.7
        await wait_for_text(text, delay=1)
        numtext = Text(car.group.ctx, "press 8 on it.", ypos=ypos, scale=0.65, color=(0,0,0,0))
        await wait_for_text(numtext, delay=1)
        ypos -= 1
        qwetext = Text(car.group.ctx, "Otherwise, press W.", ypos=ypos, scale=0.65, color=(0,0,0,0))
        await wait_for_text(qwetext)
    cont()

class TutorialScene(Scene):
    default_projection = 0, 0, 10, 0
    def __init__(self):
        self.things = []

    def draw(self, view):
        view.set_view_rect((-4, -8, 4, 4))
        for thing in self.things:
            thing.draw(view)

class TutorialCarScene(Scene):
    def __init__(self, car, keypad):
        self.car = car
        self.keypad = keypad
        self.view_rect = (0.45, 5.45, 0.55, 5.55)

    def draw(self, view):
        view.set_view_rect(self.view_rect)
        self.car.group.draw(view)
        self.keypad.draw(view)
