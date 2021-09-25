import random
from functools import partial
import os

import pyglet

from .scene import Scene, KeypadScene
from .text import Text
from .palette import COLORS
from .anim import AnimatedValue, ConstantValue, sine_in
from .keypad import Keypad
from .keyboard import keylabel
from .view import View
from . import keyboard

def animN(src, dest, *args, **kwargs):
    return tuple(
        AnimatedValue(a, ConstantValue(b), *args, **kwargs)
        for a, b in zip(src, dest)
    )

class TitleTop(Scene):
    pin_side = 'top'
    def __init__(self, ctx, window, kbd):
        self.things = []

        text = Text(ctx, 'Keypad Racer', outline=True, scale=3)
        color = random.choice(COLORS)
        text.body_color = (*color, .5)
        text.body_color = (1, 1, 1, 1)
        text.outline_color = (0,0,0,0)
        """
        text.body_color = color
        text.outline_color = (.5, .5, .5, 1)
        text.body_color = animN(text.body_color, (1, 1, 1, 1), 2, sine_in)
        text.outline_color = animN(text.outline_color, color, 2, sine_in)
        text.outline_color = animN(text.outline_color, (0,0,0,0), 12, sine_in)
        """
        self.things.append(text)
        self.title_text = text

    def draw(self, view):
        tt = self.title_text
        view.set_view_rect((-tt.width, -1, tt.width, 3))
        for thing in self.things:
            thing.draw(view)

class TitleBottom(KeypadScene):
    pin_side = 'bottom'
    def __init__(self, ctx, window, kbd):
        keypad = Keypad(ctx, color=(.9, .9, .9))
        super().__init__(keypad, kbd)
        self.kbd = kbd
        self.ctx = ctx
        self.window = window
        self.players = []

        keypad.xblocked[4] = 1
        keypad.xblocked[7] = 1
        kbd.claim_key(pyglet.window.key.ESCAPE, keypad, 6)
        kbd.claim_key(pyglet.window.key.F11, keypad, 3)
        kbd.claim_key(pyglet.window.key.BACKSPACE, keypad, 0)
        kbd.claim_key(pyglet.window.key.SPACE, keypad, 1)
        kbd.claim_key(pyglet.window.key.NUM_5, keypad, 8)
        kbd.claim_key(pyglet.window.key.S, keypad, 5)

        self.captions = {
            0: Caption(ctx, keypad, 0, 'Remove Player: {}',
                       'Remove Player'),
            1: Caption(ctx, keypad, 1, 'Press {} to Start!',
                       'Start Game', color=COLORS[0]),
            3: Caption(ctx, keypad, 3, 'Fullscreen: {}',
                       'Fullscreen'),
            5: Caption(ctx, keypad, 5, '{}: Add Player (QWERTY)',
                       ''),
            6: Caption(ctx, keypad, 6, 'Quit: {}',
                       'Quit'),
            8: Caption(ctx, keypad, 8, '{}: Add Player (Numpad)',
                       ''),
        }

        self.addplayers = {
            5: keyboard.QWERTY_LAYOUTS,
            8: keyboard.NUMPAD_LAYOUTS,
        }
        if 'DVORAK' in os.environ:
            self.addplayers[2] = keyboard.DVORAK_LAYOUTS
            self.captions[2] = Caption(ctx, keypad, 2,
                                       '{}: Add Player (Dvorak)', ''),
            kbd.claim_key(pyglet.window.key.O, keypad, 2)
        else:
            keypad.xblocked[2] = 1
            keypad.update()
        for btn, layouts in self.addplayers.items():
            keypad.set_callback(btn, partial(self.add_player, btn, layouts))

        keypad.set_callback(0, self.remove_player)
        #keypad.set_callback(1, self.start_game)
        keypad.set_callback(3, window.toggle_fullscreen)
        keypad.set_callback(6, self.quit_game)

        kbd.attach_remap_watcher(self, self.remap_watcher)

        self.update()

    def draw(self, view):
        max_size = max(c.size for c in self.captions.values())
        view.set_view_rect((-3-max_size, -2.7, 3+max_size, 1.5))
        self.keypad.draw(view)
        for thing in self.captions.values():
            thing.draw(view)

    def remap_watcher(self, keypad, button, key, name, label):
        if keypad is self.keypad and button in self.captions:
            self.captions[button].update()
        self.update()

    def update(self):
        self.keypad.xblocked[0] = not self.players
        self.keypad.xblocked[1] = not self.ready_players()
        if 'DVORAK' in os.environ:
            self.keypad.xblocked[2] = len(self.players) >= 6
        self.keypad.xblocked[5] = len(self.players) >= 6
        self.keypad.xblocked[8] = len(self.players) >= 6
        for thing in self.captions.values():
            thing.update()
        self.keypad.update()

    def ready_players(self):
        result = []
        i = 1
        for player in self.players:
            if player.assignments.keys() >= set(range(9)):
                result.append(player)
                player.player_name = f'Player {i}'
                i += 1
            else:
                player.player_name = None
        return result

    def quit_game(self):
        self.window.pyglet_window.has_exit = True
        self.window.pyglet_window.close()

    def add_player(self, button, layouts):
        if len(self.players) > 6:
            return
        key = self.keypad.assignments.get(button, None)
        for layout in layouts:
            if key in layout:
                self._add_player(layout)
                break
        else:
            for layout in layouts:
                self._add_player(layout)
                break
        self.repopulate_layouts()

    def _add_player(self, layout):
        player = Keypad(self.ctx, color=self.choose_color())
        scene = KeypadScene(player, self.kbd)
        self.window.add_view(View(self.ctx, scene))
        self.players.append(player)
        player.claim_layout(self.kbd, layout)
        for i in range(9):
            player.set_callback(i, partial(self.set_color, player, i))
        self.update()

    def repopulate_layouts(self):
        for button, layouts in self.addplayers.items():
            if button in self.keypad.assignments:
                continue
            for layout in layouts:
                key = layout[4]
                if key not in self.kbd.mapping:
                    self.kbd.claim_key(key, self.keypad, button)
                    break
            else:
                for layout in layouts:
                    for key in layout:
                        if key not in self.kbd.mapping:
                            self.kbd.claim_key(key, self.keypad, button)
                            break

    def set_color(self, player, color_no):
        color = COLORS[color_no % len(COLORS)]
        for other_player in self.players:
            if other_player.color == color:
                return
        player.color = color
        player.pad_prog['color'] = color

    def remove_player(self):
        if not self.players:
            return
        victim = self.players.pop()
        victim.unassign_all_keys(self.kbd)
        self.window.remove_view(self.window.views[-1])
        self.repopulate_layouts()
        self.update()

    def choose_color(self):
        rnd = random.randrange(len(COLORS))
        for i in range(len(COLORS)):
            color = COLORS[(i+rnd) % len(COLORS)]
            for p in self.players:
                if p.color == color:
                    break
            else:
                return color
        return 1, 1, 1

class Caption:
    def __init__(self, ctx, keypad, button, template, unassigned_message,
                 color=(1,1,1)):
        self.ctx = ctx
        self.keypad = keypad
        self.template = template
        self.unassigned_message = unassigned_message
        self.button = button
        self.size = 0
        self.color = color
        self.update()

    def update(self):
        template = self.template
        key = self.keypad.assignments.get(self.button)
        if self.keypad.xblocked[self.button]:
            key = None
        if key is None:
            message = self.unassigned_message
        else:
            label = keylabel(key).upper()
            if len(label) == 1:
                label = label.lower()
                if not label.islower():
                    label += ' key'
            message = self.template.format(label)
        if message:
            self.text = Text(self.ctx, message, scale=0.75)
            if key is None:
                self.text.body_color = (*self.color, 0)
            else:
                self.text.body_color = (*self.color, 1)
            x = self.button % 3
            y = self.button // 3
            if x == 1:
                y -= 1
            self.text.pos = (2+self.text.width/2) * (x-1), y-1.2
            self.size = self.text.width
        else:
            self.text = None

    def draw(self, view):
        if self.text:
            self.text.draw(view)

