import platform
import os
import sys
import random
import types

import pyglet
import moderngl

from . import resources
from .anim import fork, Wait

if platform.system() == "Darwin":
    pyglet.options["shadow_window"] = False

required_extensions = [
]

def check_gl_extensions():
    missing = []
    for ext in required_extensions:
        if not pyglet.gl.gl_info.have_extension(ext):
            missing.append(ext)
    if missing:
        print(
            'WARNING: This game requires OpenGL version 3.3 '
            + 'It will not work correctly on your machine.'
        )

class PygletWindow(pyglet.window.Window):
    def __init__(self):
        kwargs = {
            'caption': 'Keypad Racer',
            'width': 800,
            'height': 600,
            'resizable': True,
        }
        config = pyglet.gl.Config(
            major_version=3,
            minor_version=3,
            forward_compatible=True,
            #depth_size=24,
            double_buffer=True,
        )
        super().__init__(config=config, **kwargs)
        self.set_minimum_size(640, 480)
        check_gl_extensions()
        if 'GAME_DEVEL_ENVIRON' in os.environ:
            self.set_location(200, 800)
        if 'GAME_DEVEL_ENVIRON2' in os.environ:
            self.set_location(1100, 200)
        with resources.open('icon/icon.png', 'rb') as f:
            icon = pyglet.image.load('icon/icon.png', file=f)
            self.set_icon(icon)

    def on_resize(self, width, height):
        pass

    def on_draw(self):
        pass

class Window:
    def __init__(self, kbd):
        self.pyglet_window = wnd = PygletWindow()
        self.scenes = []

        self.ctx = ctx = moderngl.create_context()
        ctx.extra = types.SimpleNamespace()
        ctx.blend_func = ctx.SRC_ALPHA, ctx.ONE_MINUS_SRC_ALPHA
        ctx.enable_only(moderngl.BLEND | moderngl.PROGRAM_POINT_SIZE)

        self.dragged_view = None
        wnd.event(self.on_draw)
        wnd.event(self.on_mouse_scroll)
        wnd.event(self.on_mouse_press)
        wnd.event(self.on_mouse_drag)
        wnd.event(self.on_mouse_motion)
        wnd.event(self.on_mouse_release)
        wnd.event(self.on_resize)

        kbd.attach_to_window(wnd)

        self.views = []

    def debug_ctx(self):
        print("ModernGL:", moderngl.__version__)
        print("vendor:", self.ctx.info["GL_VENDOR"])
        print("renderer:", self.ctx.info["GL_RENDERER"])
        print("version:", self.ctx.info["GL_VERSION"])
        print("python:", sys.version)
        print("platform:", sys.platform)
        print("version code:", self.ctx.version_code)

    def on_draw(self):
        fbo = self.ctx.screen
        fbo.use()
        self.ctx.scissor = (
            0, 0, self.pyglet_window.width, self.pyglet_window.height,
        )
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        for view in self.views:
            view.draw()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        view = self.view_for_point(x, y)
        if view:
            #width = self.pyglet_window.width
            #height = self.pyglet_window.height
            #view.adjust_pan(x - view.width/2, y - view.height/2)
            view.adjust_zoom(scroll_y)

    def on_mouse_press(self, x, y, button, mod):
        view = self.view_for_point(x, y)
        if view:
            if not view.scene.fixed_projection:
                self.dragged_view = view
            if view.scene.get_mouse_events:
                view.scene.on_mouse_press(*view.screen_to_grid(x, y), button)

    def on_mouse_release(self, x, y, button, mod):
        view = self.dragged_view or self.view_for_point(x, y)
        if view:
            if view.scene.get_mouse_events:
                view.scene.on_mouse_release(*view.screen_to_grid(x, y), button)

    def on_mouse_drag(self, x, y, dx, dy, buttons, mod):
        view = self.dragged_view or self.view_for_point(x, y)
        if view:
            view.adjust_pan(dx, dy)
            if view.scene.get_mouse_events:
                view.scene.on_mouse_move(*view.screen_to_grid(x, y), buttons)

    def on_mouse_motion(self, x, y, dx, dy):
        view = self.view_for_point(x, y)
        if view:
            if view.scene.get_mouse_events:
                view.scene.on_mouse_move(*view.screen_to_grid(x, y), 0)

    def view_for_point(self, x, y):
        for view in self.views:
            if view.hit_test(x, y):
                return view

    def on_resize(self, w, h):
        width, height = self.pyglet_window.get_framebuffer_size()
        border = max(width/100, height/100)
        normal_views = []
        bottom = 0
        for view in self.views:
            pin_side = view.scene.pin_side
            if pin_side:
                if pin_side == 'top':
                    top_size = height * 0.15
                    orig_h = height
                    height -= top_size
                    view.set_viewport((0, height, width, top_size))
                    height -= border
                else:
                    bottom_size = height * 0.25
                    orig_h = height
                    height -= bottom_size - border
                    bottom += bottom_size + border
                    view.set_viewport((0, 0, width, bottom_size))
            else:
                normal_views.append(view)
        n = len(normal_views)
        row_count, col_count = {
            1: (1, 1),
            2: (1, 2),
            3: (1, 3),
            4: (2, 2),
            5: (2, 3),
            6: (2, 3),
            7: (2, 4),
            8: (2, 4),
            9: (3, 3),
        }.get(n, (1, n))
        for i, view in enumerate(normal_views):
            row = row_count - i % row_count - 1
            col = i // row_count

            w = width // col_count
            h = height // row_count
            x = col * width // col_count
            y = bottom + row * height // row_count
            if col > 0:
                w -= border
                x += border
            if col < row_count-1:
                w -= border
            if row > 0:
                h -= border
                y += border
            if row < col_count-1:
                h -= border
            view.set_viewport((x, y, w, h))

    def add_view(self, view):
        w = self.pyglet_window.width
        h = self.pyglet_window.height
        view.viewport = w, 0, 0, h
        self.views.append(view)
        self.on_resize(w, h)

    def remove_view(self, view, duration=0):
        try:
            self.views.remove(view)
        except ValueError:
            pass
        self.on_resize(self.pyglet_window.width, self.pyglet_window.height)

    @property
    def fullscreen(self):
        return self.pyglet_window.fullscreen
    @fullscreen.setter
    def fullscreen(self, new):
        if new:
            disp = pyglet.canvas.get_display()
            screen = random.choice(disp.get_screens())  # XXX
            self.pyglet_window.set_fullscreen(True, screen=screen)
        else:
            self.pyglet_window.set_fullscreen(False)
        self.on_resize(self.pyglet_window.width, self.pyglet_window.height)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen

