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
        self.pads = {}
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
        pad_i, act = evt
        if pad := self.pads.get(pad_i):
            pad.kbd(act, is_pressed)
        for handler in self.global_handlers:
            handler(pad_i, act, is_pressed)

    def set_pad(self, index, pad):
        self.pads[index] = pad


if __name__ == '__main__':
    # Generate the skeleton for the keynames:
    import pprint
    pprint.pprint(dict.fromkeys(dir(pyglet.window.key), ''))

DEFAULT = '☼'
KEYNAMES = {
    'A': 'A',
    'AMPERSAND': '&',
    'APOSTROPHE': "'",
    'ASCIICIRCUM': '^',
    'ASCIITILDE': '~',
    'ASTERISK': '*',
    'AT': '@',
    'B': 'B',
    'BACKSLASH': '\\',
    'BACKSPACE': '⇦',
    'BAR': '|',
    #'BEGIN': '',
    'BRACELEFT': '{',
    'BRACERIGHT': '}',
    'BRACKETLEFT': '[',
    'BRACKETRIGHT': ']',
    #'BREAK': '',
    'C': 'C',
    #'CANCEL': '',
    'CAPSLOCK': '⇫',
    #'CLEAR': '',
    'COLON': ':',
    'COMMA': ',',
    'D': 'D',
    'DELETE': '⊘',
    'DOLLAR': '$',
    'DOUBLEQUOTE': '"',
    'DOWN': '↓',
    'E': 'E',
    'END': '⇥',
    'ENTER': '↲',
    'EQUAL': '=',
    'ESCAPE': '☒',
    'EXCLAMATION': '!',
    #'EXECUTE': '',
    'F': 'F',
    'F1': 'f1',
    'F10': 'f10',
    'F11': 'f11',
    'F12': 'f12',
    'F13': 'f13',
    'F14': 'f14',
    'F15': 'f15',
    'F16': 'f16',
    'F17': 'f17',
    'F18': 'f18',
    'F19': 'f19',
    'F2': 'f2',
    'F20': 'f20',
    'F3': 'f3',
    'F4': 'f4',
    'F5': 'f5',
    'F6': 'f6',
    'F7': 'f7',
    'F8': 'f8',
    'F9': 'f9',
    #'FIND': '',
    'FUNCTION': 'fn',
    'G': 'G',
    'GRAVE': '`',
    'GREATER': '>',
    'H': 'H',
    'HASH': '#',
    'HELP': '⁇',
    'HOME': '⇤',
    'I': 'I',
    'INSERT': '∧',
    'J': 'J',
    'K': 'K',
    'L': 'L',
    'LALT': '⌒ ',
    'LCOMMAND': '⌘ ',
    'LCTRL': '⌃ ',
    'LEFT': '←',
    'LESS': '<',
    #'LINEFEED': '',
    'LMETA': '◆ ',
    'LOPTION': '⌥ ',
    'LSHIFT': '⇧ ',
    'LWINDOWS': '◆ ',
    'M': 'M',
    'MENU': '≡',
    'MINUS': '-',
    #'MODESWITCH': '',
    'N': 'N',
    #'NUMLOCK': '',
    'NUM_0': '0',
    'NUM_1': '1',
    'NUM_2': '2',
    'NUM_3': '3',
    'NUM_4': '4',
    'NUM_5': '5',
    'NUM_6': '6',
    'NUM_7': '7',
    'NUM_8': '8',
    'NUM_9': '9',
    'NUM_ADD': '+',
    #'NUM_BEGIN': '',
    'NUM_DECIMAL': '.',
    'NUM_DELETE': '⊘',
    'NUM_DIVIDE': '÷',
    'NUM_DOWN': '↓',
    'NUM_END': '⇥',
    'NUM_ENTER': '↲',
    'NUM_EQUAL': '=',
    'NUM_F1': 'f1',
    'NUM_F2': 'f2',
    'NUM_F3': 'f3',
    'NUM_F4': 'f4',
    'NUM_HOME': '⇤',
    'NUM_INSERT': '',
    'NUM_LEFT': '←',
    'NUM_MULTIPLY': '∗',
    'NUM_NEXT': '⇒',
    'NUM_PAGE_DOWN': '▼',
    'NUM_PAGE_UP': '▲',
    'NUM_PRIOR': '⇐',
    'NUM_RIGHT': '→',
    'NUM_SEPARATOR': '',
    'NUM_SPACE': ' ',
    'NUM_SUBTRACT': '-',
    'NUM_TAB': '↹',
    'NUM_UP': '↑',
    'O': 'P',
    'P': 'P',
    'PAGEDOWN': '▼',
    'PAGEUP': '▲',
    'PARENLEFT': '(',
    'PARENRIGHT': ')',
    'PAUSE': '‖',
    'PERCENT': '%',
    'PERIOD': '.',
    'PLUS': '+',
    'POUND': '₤',
    #'PRINT': '',
    'Q': 'Q',
    'QUESTION': '?',
    #'QUOTELEFT': '', # XXX
    'R': 'R',
    'RALT': ' ⌒',
    'RCOMMAND': ' ⌘',
    'RCTRL': ' ⌃',
    'REDO': '↰',
    'RETURN': '↲',
    'RIGHT': '→',
    'RMETA': ' ◆',
    'ROPTION': ' ⌥',
    'RSHIFT': ' ⇧',
    'RWINDOWS': ' ◆',
    'S': 'S',
    #'SCRIPTSWITCH': '',
    'SCROLLLOCK': '↨',
    #'SELECT': '',
    'SEMICOLON': ';',
    'SLASH': '/',
    'SPACE': 'Sp',
    #'SYSREQ': '',
    'T': 'T',
    'TAB': '↹',
    'U': 'U',
    'UNDERSCORE': '_',
    #'UNDO': '',
    'UP': '↑',
    'V': 'V',
    'W': 'W',
    'X': 'X',
    'Y': 'Y',
    'Z': 'Z',
    '_0': '0',
    '_1': '1',
    '_2': '2',
    '_3': '3',
    '_4': '4',
    '_5': '5',
    '_6': '6',
    '_7': '7',
    '_8': '8',
    '_9': '9',
}
