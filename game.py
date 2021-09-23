from __future__ import print_function
import sys

if sys.version_info < (3, 8):
    print(file=sys.stderr)
    print('This game needs Python 3.8 or later; preferably 3.9.', file=sys.stderr)
    exit(1)

try:
    import moderngl
    import pyglet
    import png
except ImportError:
    print(file=sys.stderr)
    print('You need to install dependencies for this game:', file=sys.stderr)
    print(file=sys.stderr)
    print('    python -m pip install -r requirements.txt', file=sys.stderr)
    print(file=sys.stderr)
    exit(1)


import keypad_racer.__main__
