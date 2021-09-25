
from .text import Text

class Scene:
    fixed_projection = False
    get_mouse_events = False
    default_projection = 0, 5, 10, 0

class CarScene(Scene):
    def __init__(self, car, keypad):
        self.car = car
        self.keypad = keypad

    def draw(self, view):
        view.set_view_rect(self.car.view_rect)
        self.car.group.draw(view)
        self.keypad.draw(view)

class KeypadScene(Scene):
    fixed_projection = True
    get_mouse_events = True
    def __init__(self, keypad, kbd):
        self.keypad = keypad
        self.kbd = kbd
        self.mouse_pos = 0, 0
        self.held_mouse_keys = 0
        self.keyboard = kbd
        kbd.attach_remapper(self, self.remap)

    def draw(self, view):
        x, y = self.keypad.pos
        view.set_view_rect((x-3, y-3, x+3, y+3))
        self.keypad.draw(view)

    def on_mouse_press(self, x, y, btn):
        self.held_mouse_keys |= btn
        self.mouse_pos = x, y

    def on_mouse_release(self, x, y, btn):
        self.held_mouse_keys &= btn
        self.mouse_pos = x, y

    def on_mouse_move(self, x, y, btn):
        self.held_mouse_keys = btn
        self.mouse_pos = x, y

    def remap(self, key, is_pressed):
        if self.held_mouse_keys:
            x, y = self.mouse_pos
            col = round(x)
            col_distance = abs(x - col)
            row = round(y)
            row_distance = abs(y - row)
            print(col, row, col_distance, row_distance)
            if col_distance > 0.35 or row_distance > 0.35:
                return
            if -1 <= col <= 1 and -1 <= row <= 1:
                print(col, row)
                button = col + 3 * row + 4
                if is_pressed:
                    self.kbd.claim_key(key, self.keypad, button)
                return True
