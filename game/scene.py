
from .text import Text

class Scene:
    fixed_projection = False
    default_projection = 0, 5, 10, 0

class CarScene(Scene):
    def __init__(self, car, keypad):
        self.car = car
        self.keypad = keypad

    def draw(self, view):
        self.car.group.draw(view)
        self.keypad.draw(view)

class TutorialScene(Scene):
    fixed_projection = 400, 600
    default_projection = 0, 0, 10, 0
    def __init__(self, car, controlled_view):
        self.text = Text(car.group.ctx, 'Welcome to\nKeypad Racer!')

    def draw(self, view):
        self.text.draw(view)
