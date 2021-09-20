import pyglet

DEFAULT_MAP = {
    'keyboards': (
        (
            pyglet.window.key.Q,
            pyglet.window.key.W,
            pyglet.window.key.E,
            pyglet.window.key.A,
            pyglet.window.key.S,
            pyglet.window.key.D,
            pyglet.window.key.Z,
            pyglet.window.key.X,
            pyglet.window.key.C,
            pyglet.window.key._1,
            pyglet.window.key._2,
            pyglet.window.key._3,
        ),
        (
            pyglet.window.key.T,
            pyglet.window.key.Y,
            pyglet.window.key.U,
            pyglet.window.key.G,
            pyglet.window.key.H,
            pyglet.window.key.J,
            pyglet.window.key.B,
            pyglet.window.key.N,
            pyglet.window.key.M,
            pyglet.window.key._5,
            pyglet.window.key._6,
            pyglet.window.key._7,
        ),
        (
            pyglet.window.key.O,
            pyglet.window.key.P,
            pyglet.window.key.BRACKETLEFT,
            pyglet.window.key.L,
            pyglet.window.key.SEMICOLON,
            pyglet.window.key.APOSTROPHE,
            pyglet.window.key.PERIOD,
            pyglet.window.key.SLASH,
            pyglet.window.key.RSHIFT,
            pyglet.window.key._9,
            pyglet.window.key._0,
            pyglet.window.key.MINUS,
        ),
        (
            pyglet.window.key.NUM_7,
            pyglet.window.key.NUM_8,
            pyglet.window.key.NUM_9,
            pyglet.window.key.NUM_4,
            pyglet.window.key.NUM_5,
            pyglet.window.key.NUM_6,
            pyglet.window.key.NUM_1,
            pyglet.window.key.NUM_2,
            pyglet.window.key.NUM_3,
            pyglet.window.key.NUM_TAB,
            pyglet.window.key.NUM_DIVIDE,
            pyglet.window.key.NUM_MULTIPLY,
        ),
    ),
    'actions': {
        'start': pyglet.window.key.SPACE,
        'fullscreen': pyglet.window.key.F11,
        'exit': pyglet.window.key.ESCAPE,
    },
}


class Keyboard:
    def __init__(self):
        self.load_mapping(DEFAULT_MAP)
        self.cars = {}
        self.global_handlers = []

    def attach_to_window(self, window):
        window.event(self.on_key_press)
        window.event(self.on_key_release)

    def attach_handler(self, handler):
        self.global_handlers.append(handler)

    def load_mapping(self, mapping):
        self.action_map = {}
        self.keyboards = set()
        try:
            for kbdi, kbd in enumerate(mapping['keyboards']):
                for keyi, key in enumerate(kbd):
                    self.map_key(key, (kbdi, keyi))
                    self.keyboards.add(kbdi)
            for key in 'start', 'fullscreen', 'exit':
                self.map_key(mapping['actions'][key], (None, key))
        except (TypeError, KeyError):
            if mapping is DEFAULT_MAP:
                raise
            self.load_mapping(DEFAULT_MAP)

    def map_key(self, key, action):
        # is the action somewhere already?
        prev_key = None
        for tested_key, tested_act in self.action_map.values():
            if tested_act == action:
                prev_key = tested_key
                break
        if prev_key:
            if key in self.action_map:
                del self.action_map[prev_key]
            else:
                self.action_map[prev_key] = self.action_map[key]
        self.action_map[key] = action

    def on_key_press(self, key, mod):
        if action := self.action_map.get(key):
            self.trigger_evt(action, True)

    def on_key_release(self, key, mod):
        if action := self.action_map.get(key):
            self.trigger_evt(action, False)

    def trigger_evt(self, evt, is_pressed):
        car_i, act = evt
        if car := self.cars.get(car_i):
            car.kbd(act, is_pressed)
        for handler in self.global_handlers:
            handler(car_i, act, is_pressed)

    def set_car(self, index, car):
        self.cars[index] = car
