class Scene:
    pass

class CarScene(Scene):
    def __init__(self, car, keypad):
        self.car = car
        self.keypad = keypad

    def draw(self, view):
        self.car.group.draw(view)
        self.keypad.draw(view)

class TutorialScene(Scene):
    def __init__(self, car, controlled_view):
        pass

    def draw(self, view):
        pass
