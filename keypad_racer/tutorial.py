from functools import partial
import os

from .car import CarGroup, Car
from .circuit import Circuit
from .scene import Scene, CarScene, KeypadScene
from .keypad import Keypad
from .view import View
from .text import Text
from .anim import autoschedule, Wait, AnimatedValue, ConstantValue, sine_inout
from .anim import sine_in, sine_out, Blocker, fork
from .keyboard import NUMPAD_LAYOUT, QWERTY_LAYOUT, keyname

def animN(src, dest, *args, **kwargs):
    return tuple(
        AnimatedValue(a, ConstantValue(b), *args, **kwargs)
        for a, b in zip(src, dest)
    )

def tutorial(ctx, palette, kbd, window, end_callback=None):
    circuit = Circuit(ctx, 'okruh.png')
    cars = CarGroup(ctx, circuit)

    car = Car(cars, palette.player_color(0), (0, 0))
    car.move(0, -1, sound=False)
    car.move(0, -1, sound=False)
    car.move(0, 0, sound=False)
    car.move(0, 1, sound=False)
    car.move(0, 1, sound=False)
    car.move(0, -1, sound=False)
    print(car.pos, car.velocity)
    for i in range(10):
        car.move(0, 0)
    car.velocity = 0, 4

    keypad = Keypad(ctx)
    keypad_block = [-1] * 12
    def unblock_keypad(button=None, reset=False, allow=False):
        if reset:
            keypad_block[:] = [-1] * 12
        if allow:
            keypad_block[:] = [0] * 12
        if button is not None:
            keypad_block[button] = 0
        keypad.blocked = tuple(keypad_block)
    unblock_keypad()
    keypad.pos = 0, -9

    car_scene = TutorialCarScene(car, keypad)
    car_scene_view = View(ctx, car_scene)
    window.add_view(car_scene_view)
    unblock_keypad()

    scene = TutorialScene()
    scene_view = View(ctx, scene)
    window.add_view(scene_view)

    text = Text(car.group.ctx, 'Welcome to\nKeypad Racer!', ypos=1, outline=True)
    scene.things.append(text)
    text.body_color = animN(text.body_color, (*car.color, 1), 0, sine_in)
    text.body_color = animN(text.body_color, (1, 1, 1, 1), 2, sine_in)
    text.outline_color = animN(text.outline_color, (1, 1, 1, 0), 1, sine_in)

    speedscale = 1
    autoplay = 'GAMEDEV_AUTOPLAY' in os.environ
    if autoplay:
        speedscale = 10
    ypos = -2.25

    async def wait_for_text(text, delay=0.25, lineh=None, **kwargs):
        nonlocal ypos
        kwargs.setdefault('scale', 1)
        color = kwargs.pop('color', (*car.color,1))
        kwargs['color'] = (0,0,0,0)
        if isinstance(text, str):
            text = Text(car.group.ctx, text, ypos=ypos, **kwargs)
            ypos -= lineh or kwargs['scale']
        scene.things.append(text)
        text.body_color = animN(text.body_color, color, 0.5, sine_out)
        @fork
        async def f():
            await Wait(.7)
            text.body_color = animN(text.body_color, (1, 1, 1, 1), 1, sine_in)
        await Wait(delay/speedscale)
        return text

    async def next_page(keep_longer=()):
        nonlocal ypos
        ypos -= 4
        scene.view_rect = -4, ypos - 8, 4, ypos + 4
        @fork
        async def f():
            things = list(scene.things)
            for thing in things:
                if isinstance(thing, Text):
                    @fork
                    async def f():
                        if thing in keep_longer:
                            await Wait(0.2)
                        duration = 1
                        thing.body_color = animN(
                            thing.body_color, (0, 0, 0, 0), duration, sine_in)
                    await Wait(0.2)
            await Wait(5)
            for thing in things:
                try:
                    scene.things.remove(thing)
                except ValueError:
                    pass

    def update_car_view_rect(area_x, area_y, dx=0, dy=0):
        x, y = car.pos
        vx, vy = car.velocity
        x += vx + dx
        y += vy + dy
        car_scene.view_rect = x-area_x, y-area_y, x+area_x, y+area_y

    @fork
    async def cont():
        nonlocal ypos
        await Wait(0.5/speedscale)
        update_car_view_rect(3, 3, 0, -4)
        await wait_for_text('← This is a race car.  ', scale=0.75, lineh=1)
        await wait_for_text("Let's learn to control it.", scale=0.65, lineh=1)
        num_text = await wait_for_text(
            "If you have a numeric keypad,", scale=0.65, lineh=0.7)
        await wait_for_text("press 8 on it.", scale=0.65, lineh=1)
        qwerty_text = await wait_for_text("Otherwise, press W.", scale=0.65, lineh=2)

        kbd.claim_key(QWERTY_LAYOUT[7], keypad, 9)
        kbd.claim_key(NUMPAD_LAYOUT[7], keypad, 10)

        layout = None
        selected_text = None

        blocker = Blocker()

        @partial(keypad.set_callback, 9)
        def select_numpad():
            nonlocal selected_text
            nonlocal layout
            if layout is None:
                layout = QWERTY_LAYOUT
                selected_text = qwerty_text
            blocker.unblock()

        @partial(keypad.set_callback, 10)
        def select_qwerty():
            nonlocal layout
            nonlocal selected_text
            if layout is None:
                layout = NUMPAD_LAYOUT
                selected_text = num_text
            blocker.unblock()

        if autoplay:
            keypad.kbd(9, True)
        await blocker
        #selected_text.body_color = animN(
        #    selected_text.body_color, (*car.color, 1), 2, sine_in)
        car.move(0, 1)
        update_car_view_rect(5, 5)
        keypad.claim_layout(kbd, layout)
        keypad.update(car)
        unblock_keypad(5)
        await Wait(0.5/speedscale)

        await next_page([selected_text])
        await wait_for_text("Nice!", scale=0.65, lineh=1)
        await wait_for_text(f"The {keyname(layout[7])} key accelerates.", scale=0.65, lineh=0.7)
        await wait_for_text("Try it again!", scale=0.65, lineh=1)
        blocker = Blocker()
        keypad.set_callback(7, blocker.unblock)
        if autoplay:
            keypad.kbd(9, True)
        await blocker
        duration = car.move(0, 1)
        update_car_view_rect(5, 7)
        await keypad.pause(duration, fadeout_time=0)
        keypad.update(car)
        unblock_keypad()

        #await next_page()
        unblock_keypad(2, reset=True)
        await wait_for_text("How about steering?.", scale=0.65, lineh=1)
        await wait_for_text(f"Use the {keyname(layout[6])} key to turn slightly.", scale=0.65, lineh=1)
        blocker = Blocker()
        keypad.set_callback(6, blocker.unblock)
        if autoplay:
            keypad.kbd(6, True)
        await blocker
        duration = car.move(-1, 1)
        update_car_view_rect(5, 8)
        await keypad.pause(duration, fadeout_time=0)
        keypad.update(car)

        await next_page()
        unblock_keypad(2)
        unblock_keypad(5)
        unblock_keypad(8)
        await wait_for_text("Labels on the grid show", scale=0.65, lineh=.7)
        await wait_for_text("where the car will go", scale=0.65, lineh=.7)
        await wait_for_text("if you press a key.", scale=0.65, lineh=1.05)
        await wait_for_text("There's a curve ahead;", scale=0.65, lineh=.7)
        await wait_for_text("  start turning left→", scale=0.65, lineh=.7)
        await wait_for_text("to try avoiding it.", scale=0.65, lineh=.7)
        blocker = Blocker()
        for n in 6, 7, 8:
            keypad.set_callback(n, partial(blocker.unblock, n))
        if autoplay:
            keypad.kbd(8, True)
        direction = await blocker
        duration = car.act(direction)
        update_car_view_rect(6, 8, 0, -3)
        await keypad.pause(duration, fadeout_time=0)
        keypad.update(car)

        await next_page()
        print(direction)
        ypos += 2
        if direction == 6:
            await wait_for_text("That wasn't left at all!", scale=0.65, lineh=.7)
            await wait_for_text("You're headed for a crash.", scale=0.65, lineh=.7)
            await wait_for_text("The curve ahead is close!", scale=0.65, lineh=1)
        elif direction == 7:
            await wait_for_text("The car didn't turn as much", scale=0.65, lineh=.7)
            await wait_for_text("to the left as it could,", scale=0.65, lineh=.7)
            await wait_for_text("but that was your choice.", scale=0.65, lineh=1)
            await wait_for_text("The curve ahead is close!", scale=0.65, lineh=.7)
        else:
            await wait_for_text("Good job!", scale=0.65, lineh=1)
            await wait_for_text("The curve ahead is close, though.", scale=0.65, lineh=.7)
        await wait_for_text("Decelerate!", scale=0.65, lineh=1)
        await wait_for_text(f"The keys closer to your car:", scale=0.65, lineh=0.7)
        await wait_for_text(f"{keyname(layout[0])}, {keyname(layout[1])} and {keyname(layout[2])}", scale=0.65, lineh=0.7)
        await wait_for_text(f"will reduce your speed.", scale=0.65, lineh=1)
        await wait_for_text(f"With the center one, {keyname(layout[4])}", scale=0.65, lineh=.7)
        await wait_for_text(f"you'll keep current speed.", scale=0.65, lineh=1)
        await wait_for_text(f"Try slowing down as much", scale=0.65, lineh=.7)
        await wait_for_text(f"as you can!", scale=0.65, lineh=1)

        speed_before_crash = 0
        blocker = Blocker()
        def drive(n):
            nonlocal speed_before_crash
            speed_before_crash = car.speed
            if car.blocker_on_direction(n):
                keypad.car = car
                car.keypad = keypad
                keypad.update()
                car.act(n)
                car_scene.follow_car = True
                blocker.unblock()
            else:
                duration = car.act(n)
                update_car_view_rect(6, 8, 0, -3)
                keypad.pause(duration, fadeout_time=0)
                keypad.update(car)

        for n in range(9):
            keypad.set_callback(n, partial(drive, n))

        await blocker
        for n in range(9):
            keypad.set_callback(n, None)
        keypad.update()

        blocker = Blocker()
        car.crash_callback = blocker.unblock

        await next_page()
        ypos += 2

        await wait_for_text("Whoops! You crashed!", scale=0.65, lineh=.7)
        await wait_for_text("(Yes, the tutorial is rigged)", scale=0.65, lineh=1)
        if speed_before_crash > 6:
            await wait_for_text("Next time,", scale=0.65, lineh=.7)
            t = 'try'
        else:
            t = 'Always try'
        await wait_for_text(t + " to slow down before", scale=0.65, lineh=.7)
        await wait_for_text("any crashes, so you respawn", scale=0.65, lineh=.7)
        await wait_for_text("faster.", scale=0.65, lineh=1)

        await wait_for_text("But now, drive on!", scale=0.65, lineh=1)

        with open('keypad_racer.conf', 'w') as f:
            if layout is NUMPAD_LAYOUT:
                f.write('numpad')
            else:
                f.write('qwerty')

        await wait_for_text("Or restart the game", scale=0.65, lineh=.65)
        await wait_for_text("for a multiplayer race!", scale=0.65, lineh=.65)

class TutorialScene(Scene):
    default_projection = 0, 0, 10, 0
    fixed_projection = True
    def __init__(self):
        self.things = []
        self.view_rect = (-4, -8, 4, 4)

    def draw(self, view):
        view.set_view_rect(self.view_rect)
        for thing in self.things:
            thing.draw(view)

class TutorialCarScene(Scene):
    def __init__(self, car, keypad):
        self.car = car
        self.keypad = keypad
        self.view_rect = (0.45, 5.45, 0.55, 5.55)
        self.follow_car = False

    def draw(self, view):
        if self.follow_car:
            view.set_view_rect(self.car.view_rect)
        else:
            view.set_view_rect(self.view_rect)
        self.car.group.draw(view)
        self.keypad.draw(view)
