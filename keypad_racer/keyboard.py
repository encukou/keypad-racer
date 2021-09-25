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
)[:9]

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
)[:9]

DVORAK_LAYOUT = (
    pyglet.window.key.SEMICOLON,
    pyglet.window.key.Q,
    pyglet.window.key.J,
    pyglet.window.key.A,
    pyglet.window.key.O,
    pyglet.window.key.E,
    pyglet.window.key.APOSTROPHE,
    pyglet.window.key.COMMA,
    pyglet.window.key.PERIOD,
    pyglet.window.key._1,
    pyglet.window.key._2,
    pyglet.window.key._3,
)[:9]

QWERTY_LAYOUTS = (
    QWERTY_LAYOUT,
    (
        pyglet.window.key.PERIOD,
        pyglet.window.key.SLASH,
        pyglet.window.key.RSHIFT,
        pyglet.window.key.L,
        pyglet.window.key.SEMICOLON,
        pyglet.window.key.APOSTROPHE,
        pyglet.window.key.O,
        pyglet.window.key.P,
        pyglet.window.key.BRACKETLEFT,
        pyglet.window.key._9,
        pyglet.window.key._0,
        pyglet.window.key.MINUS,
    )[:9],
    (
        pyglet.window.key.B,
        pyglet.window.key.N,
        pyglet.window.key.M,
        pyglet.window.key.G,
        pyglet.window.key.H,
        pyglet.window.key.J,
        pyglet.window.key.T,
        pyglet.window.key.Y,
        pyglet.window.key.U,
        pyglet.window.key._5,
        pyglet.window.key._6,
        pyglet.window.key._7,
    )[:9],
)
NUMPAD_LAYOUTS = (
    NUMPAD_LAYOUT,
)
DVORAK_LAYOUTS = (
    DVORAK_LAYOUT,
    (
        pyglet.window.key.V,
        pyglet.window.key.Z,
        pyglet.window.key.RSHIFT,
        pyglet.window.key.N,
        pyglet.window.key.S,
        pyglet.window.key.MINUS,
        pyglet.window.key.R,
        pyglet.window.key.L,
        pyglet.window.key.SLASH,
        pyglet.window.key._9,
        pyglet.window.key._0,
        pyglet.window.key.BRACKETRIGHT,
    )[:9],
    (
        pyglet.window.key.X,
        pyglet.window.key.B,
        pyglet.window.key.M,
        pyglet.window.key.I,
        pyglet.window.key.D,
        pyglet.window.key.H,
        pyglet.window.key.Y,
        pyglet.window.key.F,
        pyglet.window.key.G,
        pyglet.window.key._6,
        pyglet.window.key._7,
        pyglet.window.key._8,
    )[:9],
)

class Keyboard:
    def __init__(self):
        self.mapping = {}
        self.remappers = weakref.WeakKeyDictionary()
        self.remap_watchers = weakref.WeakKeyDictionary()
        self.global_handlers = []

    def attach_to_window(self, window):
        window.event(self.on_key_press)
        window.event(self.on_key_release)

    def attach_remapper(self, remapper, func):
        self.remappers[remapper] = func

    def attach_remap_watcher(self, remapper, func):
        self.remap_watchers[remapper] = func

    def claim_key(self, key, keypad, button):
        if key in self.mapping:
            prev_keypad, prev_button = self.mapping[key]
            if prev_keypad:
                # Search for a "prev_key" that was previously assigned
                # to (keypad, button).
                for prev_key, (kp, bt) in self.mapping.items():
                    if kp == keypad and bt == button:
                        # Found -> give this key to the keypad we're
                        # stealing from!
                        self._assign(prev_keypad, prev_button, prev_key)
                        break
                else:
                    self._assign(prev_keypad, prev_button, None)
        self._assign(keypad, button, key)

    def unclaim_key(self, key):
        if key in self.mapping:
            keypad, button = self.mapping.pop(key)
            self._assign(keypad, button, None)

    def _assign(self, keypad, button, key):
        if key is None:
            self.mapping.pop(key, None)
            name = ' '
        else:
            self.mapping[key] = keypad, button
            name = keyname(key)
        keypad.assign_char(button, name, key)
        for func in self.remap_watchers.values():
            func(keypad, button, key, name, keylabel(key))

    def on_key_press(self, key, mod):
        return self.key_state_changed(key, mod, True)

    def on_key_release(self, key, mod):
        return self.key_state_changed(key, mod, False)

    def key_state_changed(self, key, mod, is_pressed):
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
    if key is None:
        return ''
    name, label = KEYNAMES.get(key, (None, None))
    if name is None:
        print(f'Unknown key {key}; using default symbol')
        name = DEFAULT_DECAL
        KEYNAMES[key] = (name, 'Unknown key')
    return name

def keylabel(key):
    if key is None:
        return ''
    name, label = KEYNAMES.get(key, (None, None))
    if name is None:
        print(f'Unknown key {key}; using default symbol')
        name = DEFAULT_DECAL
        KEYNAMES[key] = (name, 'Unknown key')
    return label

if __name__ == '__main__':
    # Generate the skeleton for the keynames:
    import pprint
    pprint.pprint(dict.fromkeys(dir(pyglet.window.key), ''))

DEFAULT_DECAL = '▫'
KEYNAMES = {
    getattr(pyglet.window.key, name):
            label if isinstance(label, tuple) else (label, label)
    for name, label in {
        'A': 'A',
        'AMPERSAND': '&',
        'APOSTROPHE': "'",
        'ASCIICIRCUM': '^',
        'ASCIITILDE': '~',
        'ASTERISK': '*',
        'AT': '@',
        'B': 'B',
        'BACKSLASH': '\\',
        'BACKSPACE': ('⇦', 'Backspace'),
        'BAR': '|',
        'BEGIN': (None, 'Begin'),
        'BRACELEFT': '{',
        'BRACERIGHT': '}',
        'BRACKETLEFT': '[',
        'BRACKETRIGHT': ']',
        'BREAK': (None, 'Break'),
        'C': 'C',
        'CANCEL': (None, 'Cancel'),
        'CAPSLOCK': ('⇫', 'Caps Lock'),
        'CLEAR': (None, 'Clear'),
        'COLON': ':',
        'COMMA': ',',
        'D': 'D',
        'DELETE': ('⊘', 'Del'),
        'DOLLAR': '$',
        'DOUBLEQUOTE': '"',
        'DOWN': ('↓', 'Down'),
        'E': 'E',
        'END': ('⇥', 'End'),
        'ENTER': ('↲', 'Enter'),
        'EQUAL': '=',
        'ESCAPE': ('☒', 'Esc'),
        'EXCLAMATION': '!',
        'EXECUTE': (None, 'Execute'),
        'F': 'F',
        'F1': ('①', 'F1'),
        'F10': ('⑩', 'F10'),
        'F11': ('⑪', 'F11'),
        'F12': ('⑫', 'F12'),
        'F13': ('⑬', 'F13'),
        'F14': ('⑭', 'F14'),
        'F15': ('⑮', 'F15'),
        'F16': ('⑯', 'F16'),
        'F17': ('⑰', 'F17'),
        'F18': ('⑱', 'F18'),
        'F19': ('⑲', 'F19'),
        'F2': ('②', 'F2'),
        'F20': ('⑳', 'F20'),
        'F3': ('③', 'F3'),
        'F4': ('④', 'F4'),
        'F5': ('⑤', 'F5'),
        'F6': ('⑥', 'F6'),
        'F7': ('⑦', 'F7'),
        'F8': ('⑧', 'F8'),
        'F9': ('⑨', 'F9'),
        'FIND': (None, 'Find'),
        'FUNCTION': ('◇', 'Fn'),
        'G': 'G',
        'GRAVE': '`',
        'GREATER': '>',
        'H': 'H',
        'HASH': '#',
        'HELP': ('⁇', 'Help'),
        'HOME': ('⇤', 'Home'),
        'I': 'I',
        'INSERT': ('∧', 'Ins'),
        'J': 'J',
        'K': 'K',
        'L': 'L',
        'LALT': ('⌒ ', 'Left Alt'),
        'LCOMMAND': ('⌘ ', 'Left Cmd'),
        'LCTRL': ('∧ ', 'Left Ctrl'),
        'LEFT': ('←', 'Left'),
        'LESS': '<',
        'LINEFEED': (None, 'Linefeed'),
        'LMETA': ('◆ ', 'Left Meta'),
        'LOPTION': ('⌥ ', 'Left Opt'),
        'LSHIFT': ('⇧ ', 'Left Shift'),
        'LWINDOWS': ('◆ ', 'Left OS'),
        'M': 'M',
        'MENU': ('≡', 'Menu'),
        'MINUS': '-',
        'MODESWITCH': (None, 'Modeswitch'),
        'N': 'N',
        'NUMLOCK': (None, 'Num Lock'),
        'NUM_0': ('0', 'Numpad 0'),
        'NUM_1': ('1', 'Numpad 1'),
        'NUM_2': ('2', 'Numpad 2'),
        'NUM_3': ('3', 'Numpad 3'),
        'NUM_4': ('4', 'Numpad 4'),
        'NUM_5': ('5', 'Numpad 5'),
        'NUM_6': ('6', 'Numpad 6'),
        'NUM_7': ('7', 'Numpad 7'),
        'NUM_8': ('8', 'Numpad 8'),
        'NUM_9': ('9', 'Numpad 9'),
        'NUM_ADD': ('+', 'Numpad +'),
        'NUM_BEGIN': (None, 'Numpad Begin'),
        'NUM_DECIMAL': ('.', 'Numpad Decimal'),
        'NUM_DELETE': ('⊘', 'Numpad Del'),
        'NUM_DIVIDE': ('÷', 'Numpad /'),
        'NUM_DOWN': ('↓', 'Numpad Down'),
        'NUM_END': ('⇥', 'Numpad End'),
        'NUM_ENTER': ('↲', 'Numpad Enter'),
        'NUM_EQUAL': ('=', 'Numpad ='),
        'NUM_F1': ('①', 'Numpad F1'),
        'NUM_F2': ('②', 'Numpad F2'),
        'NUM_F3': ('③', 'Numpad F3'),
        'NUM_F4': ('④', 'Numpad F4'),
        'NUM_HOME': ('⇤', 'Numpad Home'),
        'NUM_INSERT': (None, 'Numpad Ins'),
        'NUM_LEFT': ('←', 'Numpad Left'),
        'NUM_MULTIPLY': ('∗', 'Numpad *'),
        'NUM_NEXT': ('⇒', 'Numpad Next'),
        'NUM_PAGE_DOWN': ('▼', 'Numpad PgDn'),
        'NUM_PAGE_UP': ('▲', 'Numpad PgUp'),
        'NUM_PRIOR': ('⇐', 'Numpad Prev'),
        'NUM_RIGHT': ('→', 'Numpad Right'),
        'NUM_SEPARATOR': (None, 'Numpad Sep'),
        'NUM_SPACE': ('␣', 'Numpad Space'),
        'NUM_SUBTRACT': ('-', 'Numpad -'),
        'NUM_TAB': ('↹', 'Numpad Tab'),
        'NUM_UP': ('↑', 'Numpad Up'),
        'O': 'O',
        'P': 'P',
        'PAGEDOWN': ('▼', 'PgDn'),
        'PAGEUP': ('▲', 'PgUp'),
        'PARENLEFT': '(',
        'PARENRIGHT': ')',
        'PAUSE': ('‖', 'Pause'),
        'PERCENT': '%',
        'PERIOD': '.',
        'PLUS': '+',
        'POUND': '₤',
        'PRINT': (None, 'Print'),
        'Q': 'Q',
        'QUESTION': '?',
        'QUOTELEFT': (None, 'LQ'),
        'R': 'R',
        'RALT': (' ⌒', 'Right Alt'),
        'RCOMMAND': (' ⌘', 'Right Cmd'),
        'RCTRL': (' ∧', 'Right Ctrl'),
        'REDO': ('↰', 'Redo'),
        'RETURN': ('↲', 'Return'),
        'RIGHT': ('→', 'Right'),
        'RMETA': (' ◆', 'Right Meta'),
        'ROPTION': (' ⌥', 'Right Opt'),
        'RSHIFT': (' ⇧', 'Right Shift'),
        'RWINDOWS': (' ◆', 'Right OS'),
        'S': 'S',
        'SCRIPTSWITCH': (None, 'Script Switch'),
        'SCROLLLOCK': ('↨', 'Scroll Lock'),
        'SELECT': (None, 'Select'),
        'SEMICOLON': ';',
        'SLASH': '/',
        'SPACE': ('␣', 'Space'),
        'SYSREQ': (None, 'SysRq'),
        'T': 'T',
        'TAB': ('↹', 'Tab'),
        'U': 'U',
        'UNDERSCORE': '_',
        'UNDO': (None, 'Undo'),
        'UP': ('↑', 'Up'),
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
    }.items()
}
