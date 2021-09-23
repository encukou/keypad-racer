import platform
import os
import sys
import random

import pyglet
import moderngl

from . import resources

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
        print(pyglet.gl.glext_arb)
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
            self.set_location(1000, 200)

    def on_resize(self, width, height):
        pass

    def on_draw(self):
        pass

class Window:
    def __init__(self, kbd):
        self.pyglet_window = wnd = PygletWindow()
        self.scenes = []

        self.ctx = ctx = moderngl.create_context()
        ctx.blend_func = ctx.SRC_ALPHA, ctx.ONE_MINUS_SRC_ALPHA
        ctx.enable_only(moderngl.BLEND | moderngl.PROGRAM_POINT_SIZE)

        self.dragged_view = None
        wnd.event(self.on_draw)
        wnd.event(self.on_mouse_scroll)
        wnd.event(self.on_mouse_press)
        wnd.event(self.on_mouse_drag)
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
            view.adjust_zoom(scroll_y)

    def on_mouse_press(self, x, y, button, mod):
        self.dragged_view = self.view_for_point(x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, mod):
        view = self.dragged_view or self.view_for_point(x, y)
        width = self.pyglet_window.width
        if view:
            view.adjust_pan(
                -dx*view.zoom/width*4,
                -dy*view.zoom/width*4,
            )

    def view_for_point(self, x, y):
        for view in self.views:
            if view.hit_test(x, y):
                return view

    def on_resize(self, w, h):
        BORDER = max(w/100, h/100)
        w, h = self.pyglet_window.get_framebuffer_size()
        for view, viewport in zip(self.views, (
            (0, 0, w/2-BORDER/2, h),
            (w/2+BORDER, 0, w/2-BORDER/2, h),
        )):
            view.viewport = viewport

    def add_view(self, view):
        self.views.append(view)
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
