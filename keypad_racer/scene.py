import time

from .text import Text

class Scene:
    fixed_projection = False
    get_mouse_events = False
    pin_side = None
    default_projection = 0, 5, 10, 0

def format_time(t):
    if t > 60:
        m, s = divmod(t, 60)
        m = int(m)
        return f'{m}:{s:.1f}'
    else:
        return f'{t:.1f}'

class CarScene(Scene):
    def __init__(self, car, keypad):
        self.car = car
        self.keypad = keypad
        self.text = Text(keypad.ctx, '.', scale=0.5, align=1)
        self.draw_stats = True

    def draw(self, view):
        view.set_view_rect(self.car.view_rect)
        self.car.group.draw(view)
        self.keypad.draw(view)
        if self.draw_stats:
            car = self.car
            stats = [
                f'Speed: {car.speed:.2f}',
                f'Lap: {car.max_lap}',
                f'Lap time: {format_time(time.monotonic()-car.lap_start_time)}',
            ]
            if car.crash_count:
                stats.insert(1, f'Crashes: {car.crash_count}')
            for n, lap_time in enumerate(car.lap_times, start=1):
                stats.append(f'Lap {n}: {format_time(lap_time)}')
            self.text.update('\n'.join(stats))
            self.text.body_color = (*self.car.color, 0.8)
            x, y, w, h = view.viewport
            self.text.pos = 7.8*w/h, 7.4
            self.text.draw(
                view,
                override={'projection_params': (0, 0, 8*w/h, 8)},
            )

class KeypadScene(Scene):
    fixed_projection = True
    get_mouse_events = True
    def __init__(self, keypad, kbd):
        self.keypad = keypad
        self.kbd = kbd
        self.mouse_pos = 0, 0
        self.held_mouse_keys = 0
        self.keyboard = kbd
        self.text = None
        self.caption = None
        kbd.attach_remapper(self, self.remap)

    def draw(self, view):
        x, y = self.keypad.pos
        view.set_view_rect((x-2, y-3, x+2, y+3))
        self.keypad.draw(view)
        if self.caption != self.keypad.player_name:
            self.caption = self.keypad.player_name
            if self.caption:
                self.text = Text(self.keypad.ctx, self.caption, scale=0.5)
                self.text.body_color = (1,1,1,1)
                self.text.pos = 0, 1.75
            else:
                self.text = None
        if self.text:
            self.text.draw(view)

    def on_mouse_press(self, x, y, btn):
        self.held_mouse_keys |= btn
        self.mouse_pos = x, y

    def on_mouse_release(self, x, y, btn):
        self.held_mouse_keys &= ~btn
        self.mouse_pos = x, y

    def on_mouse_move(self, x, y, btn):
        self.held_mouse_keys = btn
        self.mouse_pos = x, y

    def remap(self, key, is_pressed):
        if self.held_mouse_keys:
            x, y = self.mouse_pos
            kpx, kpy = self.keypad.pos
            x -= kpx
            y -= kpy
            col = round(x)
            col_distance = abs(x - col)
            row = round(y)
            row_distance = abs(y - row)
            if col_distance > 0.35 or row_distance > 0.35:
                return
            if -1 <= col <= 1 and -1 <= row <= 1:
                button = col + 3 * row + 4
                if is_pressed:
                    self.kbd.claim_key(key, self.keypad, button)
                return True
