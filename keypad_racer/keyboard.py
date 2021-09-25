import pyglet
import weakref

QWERTY_LAYOUT = (
    pyglet.window.key.Z,
    pyglet.window.key.X,
    pyglet.window.key.C,
    pyglet.window.key.A,
    pyglet.window.key.S,
    pyglet.window.key.D,
    pyglet.window.key.Q,
    pyglet.window.key.W,
    pyglet.window.key.E,
    pyglet.window.key._1,
    pyglet.window.key._2,
    pyglet.window.key._3,
)

NUMPAD_LAYOUT = (
    pyglet.window.key.NUM_1,
    pyglet.window.key.NUM_2,
    pyglet.window.key.NUM_3,
    pyglet.window.key.NUM_4,
    pyglet.window.key.NUM_5,
    pyglet.window.key.NUM_6,
    pyglet.window.key.NUM_7,
    pyglet.window.key.NUM_8,
    pyglet.window.key.NUM_9,
    pyglet.window.key.NUM_TAB,
    pyglet.window.key.NUM_DIVIDE,
    pyglet.window.key.NUM_MULTIPLY,
)

DEFAULT_MAP = {
    'keyboards': (
        NUMPAD_LAYOUT,
        QWERTY_LAYOUT,
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
    ),
    'actions': {
        'start': pyglet.window.key.SPACE,
        'fullscreen': pyglet.window.key.F11,
        'exit': pyglet.window.key.ESCAPE,
    },
}


class Keyboard:
    def __init__(self):
        self.mapping = {
            pyglet.window.key.F11: (None, 'fullscreen')
        }
        self.remappers = weakref.WeakKeyDictionary()
        self.global_handlers = []
        #self.load_mapping(DEFAULT_MAP)
        #self.pads = {}

    def attach_to_window(self, window):
        window.event(self.on_key_press)
        window.event(self.on_key_release)

    def attach_remapper(self, remapper, func):
        self.remappers[remapper] = func

    def claim_key(self, key, keypad, button):
        print(key, 'claim')
        if key in self.mapping:
            prev_keypad, prev_button = self.mapping[key]
            if prev_keypad:
                # Search for a "prevkey" that was previously assigned
                # to (keypad, button).
                for prevkey, (kp, bt) in self.mapping.items():
                    if kp == keypad and bt == button:
                        # Found -> give this key to the keypad we're
                        # stealing from!
                        self.mapping[prevkey] = prev_keypad, prev_button
                        prev_keypad.set_decal(prev_button, keyname(prevkey))
                        break
                else:
                    prev_keypad.set_decal(prev_button, ' ')
        self.mapping[key] = keypad, button
        keypad.set_decal(button, keyname(key))

    def on_key_press(self, key, mod):
        return self.key_state_changed(key, mod, True)

    def on_key_release(self, key, mod):
        return self.key_state_changed(key, mod, False)

    def key_state_changed(self, key, mod, is_pressed):
        print(self.remappers)
        for remapper in self.remappers:
            if self.remappers[remapper](key, is_pressed):
                return True
        action = self.mapping.get(key)
        if action:
            keypad, button = action
            if keypad:
                keypad.kbd(button, is_pressed)
                return True
            else:
                for handler in self.global_handlers:
                    handler(button, is_pressed)
                return True

    def attach_handler(self, handler):
        self.global_handlers.append(handler)

def keyname(key):
    name = KEYNAMES.get(key)
    if name is None:
        print(f'Unknown key {key}; using default symbol')
        name = DEFAULT_DECAL
        KEYNAMES[key] = name
    return name

if __name__ == '__main__':
    # Generate the skeleton for the keynames:
    import pprint
    pprint.pprint(dict.fromkeys(dir(pyglet.window.key), ''))

DEFAULT_DECAL = '▫'
KEYNAMES = {getattr(pyglet.window.key, name):label for name, label in {
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
    'F1': '①',
    'F10': '⑩',
    'F11': '⑪',
    'F12': '⑫',
    'F13': '⑬',
    'F14': '⑭',
    'F15': '⑮',
    'F16': '⑯',
    'F17': '⑰',
    'F18': '⑱',
    'F19': '⑲',
    'F2': '②',
    'F20': '⑳',
    'F3': '③',
    'F4': '④',
    'F5': '⑤',
    'F6': '⑥',
    'F7': '⑦',
    'F8': '⑧',
    'F9': '⑨',
    #'FIND': '',
    'FUNCTION': '◇',
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
    'NUM_F1': '①',
    'NUM_F2': '②',
    'NUM_F3': '③',
    'NUM_F4': '④',
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
    'O': 'O',
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
}.items()}
