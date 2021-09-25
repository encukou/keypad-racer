
from .text import Text

class Scene:
    fixed_projection = False
    default_projection = 0, 5, 10, 0

class CarScene(Scene):
    def __init__(self, car, keypad):
        self.car = car
        self.keypad = keypad

    def draw(self, view):
        view.set_view_rect(self.car.view_rect)
        self.car.group.draw(view)
        self.keypad.draw(view)
