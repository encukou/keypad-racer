"""
Level editor and baker
----------------------

Requirements:
- python -m pip install  pyglet pillownumpy

Usage:
   python leveledit.py LEVEL_NAME

Input:
- A SVG file `LEVEL_NAME.svg` containing a path with id "circuit" (set this in
  Inkscape's Object Properties).
  The control points matter.
  There are some limits on what features are supported -- start with an
  existing level and undo if you get errors.
  The editor polls the file for changes and reloads when it finds any.
  The origin is the start point; cars start going "up"

Auxiliary file:
- LEVEL_NAME.json with extra information
  If missing, it will be generated (from an output file, or empty).

Output:
- Level file `LEVEL_NAME.png`, containing collision data (as the image),
  rail data (as a custom chunks) and a copy of the auxiliary file.

Controls:
- Middle mouse button: drag to pan
- Mouse wheel: zoom
- R: Reset zoom/pan (also happens on window resize)

- Up/Down: Resize control point
- Left/Right: Resize control point (fine adjustment)
- S: Set start point
- F5: Reload auxiliary file
"""

import os
import sys
from pathlib import Path
import xml.sax.handler
import re
import operator
import collections
import json

import pyglet
import numpy

try:
    level_name = sys.argv[1]
except IndexError:
    print(f'Usage: {sys.argv[0]} levelname', file=sys.stderr)
    exit(1)

circle = pyglet.image.load(Path(__file__).parent / 'circle.png')
startcirc = pyglet.image.load(Path(__file__).parent / 'start.png')

window = pyglet.window.Window(
    width=1000,
    height=1800,
    resizable=True,
    caption=f'Level editor: {level_name}'
)
if 'GAME_DEVEL_ENVIRON' in os.environ:
    window.set_location(200, 200)

def parse_svg_path(path):
    print(path)
    path_iter = iter(re.split('[ ,]+', path))
    current_pos = 0, 0
    points = []
    command = None
    def add_point_abs(x, y):
        point = float(x), -float(y)
        points.append(point)
        return point
    def add_point_rel(dx, dy):
        x, y = current_pos
        x += float(dx)
        y += -float(dy)
        point = x, y
        points.append(point)
        return point
    for part in path_iter:
        # For SVG commands see:
        # https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/d
        if part == 'M':
            if points:
                raise ValueError('circuit can only have a single path')
            current_pos = add_point_abs(next(path_iter), next(path_iter))
            command = 'L'
        elif part in 'Cc':
            command = part
        elif part == 'z':
            points.append(points[0])
            command = None
        elif re.match('[-0-9.]', part):
            if command == 'C':
                add_point_abs(part, next(path_iter))
                add_point_abs(next(path_iter), next(path_iter))
                current_pos = add_point_abs(next(path_iter), next(path_iter))
            elif command == 'c':
                add_point_rel(part, next(path_iter))
                add_point_rel(next(path_iter), next(path_iter))
                current_pos = add_point_rel(next(path_iter), next(path_iter))
            else:
                raise ValueError(f'Unknown SVG path command: {command}')
        else:
            print(path)
            raise ValueError(f'Unknown SVG path part: {part}')
    return points

class EditorState:
    def __init__(self, level_name):
        self.input_path = Path(f'{level_name}.svg').resolve()
        self.aux_path = Path(f'{level_name}.json').resolve()
        self.output_path = Path(f'{level_name}.png').resolve()
        self.mouse_pos = window.width / 2, window.height / 2
        self.zoom = 1
        self.changing = False
        self.view_center = 0, 0
        self.maybe_reload_input()
        self.reset_zoom_pan()

    def reset_zoom_pan(self):
        padding = 10
        x1, y1, x2, y2 = self.bb
        x1 -= padding
        x2 += padding
        y1 -= padding
        y2 += padding
        x_zoom = abs(window.width / (x2 - x1))
        y_zoom = abs(window.height / (y2 - y1))
        self.zoom = min(x_zoom, y_zoom)
        self.view_center = (x2 + x1)/2, (y2 + y1)/2
        self.mouse_moved()

    def pan(self, dx, dy):
        x, y = self.view_center
        x -= dx / self.zoom
        y -= dy / self.zoom
        self.view_center = x, y

    def adjust_zoom(self, x, y, dz):
        cx, cy = window.width / 2, window.height / 2
        self.pan(cx-x, cy-y)
        self.zoom *= 1.1**dz
        self.pan(x-cx, y-cy)

    def maybe_reload_input(self, dt=0):
        st = self.input_path.stat()
        stat_info = st.st_mtime, st.st_size
        try:
            if stat_info == self.previous_stat_info:
                return
        except AttributeError:
            pass
        self.previous_stat_info = stat_info
        path = None
        class Handler(xml.sax.handler.ContentHandler):
            def startElement(self, name, attrs):
                if name == 'path' and attrs.get('id') == 'circuit':
                    nonlocal path
                    path = attrs['d']
        with self.input_path.open() as f:
            xml.sax.parse(f, Handler())
        if path is None:
            raise ValueError('Did not find a path with id=circuit')
        points = parse_svg_path(path)
        self.bb = tuple(
            fun(points, key=operator.itemgetter(i))[i]
            for fun, i in ((min, 0), (min, 1), (max, 0), (max, 1))
        )
        print(self.bb)
        seg = Segment(*points[:4])
        self.segments = [seg]
        for points in zip(points[4::3], points[5::3], points[6::3]):
            seg = Segment(seg.end, *points)
            self.segments.append(seg)
        self.segments[0].start = seg.end
        self.mouse_moved()
        self.read_aux()

    def read_aux(self):
        try:
            f = self.aux_path.open()
        except FileNotFoundError:
            return
        else:
            with f:
                aux_data = json.load(f)
        unassigned_segments = list(self.segments)
        points = list(aux_data.get('points', ()))
        first_segment = self.segments[0]
        while unassigned_segments and points:
            best_pair = 0, 0
            best_distance = None
            for pi, point in enumerate(points):
                pos = point.get('pos', (0,0))
                for si, segment in enumerate(unassigned_segments):
                    distance = (
                        (pos[0] - segment.start[0])**2
                        +(pos[1] - segment.start[1])**2
                    )
                    if best_distance is None or distance < best_distance:
                        best_pair = pi, si
                        best_distance = distance
                        if best_distance == 0:
                            break
            point = points.pop(best_pair[0])
            segment = unassigned_segments.pop(best_pair[1])
            if point.get('first'):
                first_segment = segment
            if r := point.get('radius'):
                segment.start.size = r
        if points:
            print('Unassigned points:')
            for pt in points:
                print(pt)
        self.set_first_segment(first_segment)
        self.changing = False

    def screen_to_model(self, sx, sy):
        mx = sx/self.zoom + self.view_center[0] - window.width/2/self.zoom
        my = sy/self.zoom + self.view_center[1] - window.height/2/self.zoom
        return mx, my

    def model_to_screen(self, mx, my):
        sx = self.zoom * (mx - self.view_center[0]) + window.width/2
        sy = self.zoom * (my - self.view_center[1]) + window.height/2
        return sx, sy

    def mouse_moved(self, x=None, y=None):
        if x is not None and y is not None:
            self.mouse_pos = x, y
        else:
            x, y = self.mouse_pos
        mx, my = self.screen_to_model(x, y)
        self.active_segment = min(
            self.segments,
            key=lambda seg: (seg.start[0]-mx)**2 + (seg.start[1]-my)**2,
        )

    def resize_width(self, dr):
        self.active_segment.start.size += dr / self.zoom
        self.changing = True

    def set_first_segment(self, first_segment=None):
        if first_segment is None:
            first_segment = self.active_segment
        for i in range(len(self.segments)):
            if first_segment == self.segments[0]:
                break
            self.segments.append(self.segments.pop(0))
        self.changing = True

    def apply_change(self):
        if not self.changing:
            return
        self.changing = False
        points = []
        for i, seg in enumerate(self.segments):
            point = {'pos': seg.start, 'radius': seg.start.size}
            if i == 0:
                point['first'] = True
            points.append(point)
        data = {'points': points}
        with self.aux_path.open('w') as f:
            json.dump(data, f, indent=4)

    def draw(self):
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glTranslatef(window.width/2, window.height/2, 0)
        pyglet.gl.glScalef(self.zoom, self.zoom, 1)
        pyglet.gl.glTranslatef(-self.view_center[0], -self.view_center[1], 0)
        # Mouse
        pyglet.gl.glColor4f(0, 1, 0, 0.6)
        mouse_x, mouse_y = self.screen_to_model(*self.mouse_pos)
        size = 1
        circle.blit(mouse_x-size/2, mouse_y-size/2, width=size, height=size)
        # Grid
        pyglet.gl.glColor4f(.25, 0, 0, 1)
        x1, y1 = self.screen_to_model(0, 0)
        x2, y2 = self.screen_to_model(window.width, window.height)
        for u in range(-10, 11):
            if -4 <= u <= 4:
                pyglet.gl.glColor4f(.4, 0, 0, 1)
            else:
                pyglet.gl.glColor4f(.2, 0, 0, 1)
            gx = round(mouse_x) + u
            gy = round(mouse_y) + u
            pyglet.gl.glBegin(pyglet.gl.GL_LINES)
            pyglet.gl.glVertex2f(gx, y1)
            pyglet.gl.glVertex2f(gx, y2)
            pyglet.gl.glVertex2f(x1, gy)
            pyglet.gl.glVertex2f(x2, gy)
            pyglet.gl.glEnd()
        # Control points
        pyglet.gl.glColor4f(0, 0.5, 1, .5)
        pyglet.gl.glBegin(pyglet.gl.GL_LINES)
        for segment in self.segments:
            pyglet.gl.glVertex2f(*segment.start)
            pyglet.gl.glVertex2f(*segment.control1)
            pyglet.gl.glVertex2f(*segment.end)
            pyglet.gl.glVertex2f(*segment.control2)
        pyglet.gl.glEnd()
        # Circles
        pyglet.gl.glColor4f(1, 1, 0, .5)
        for i, segment in enumerate(self.segments):
            alpha = 0.5
            if segment == self.active_segment:
                pyglet.gl.glColor4f(0, 1, 0, alpha)
            else:
                pyglet.gl.glColor4f(1, 1, 0, alpha)
            x, y = segment.start
            size = segment.start.size
            if i == 0:
                img = startcirc
            else:
                img = circle
            img.blit(x-size/2, y-size/2, width=size, height=size)
        # Straight lines
        pyglet.gl.glColor4f(1, 1, 1, .5)
        pyglet.gl.glBegin(pyglet.gl.GL_LINE_STRIP)
        for segment in self.segments:
            pyglet.gl.glVertex2f(*segment.start)
            pyglet.gl.glVertex2f(*segment.end)
        pyglet.gl.glEnd()

class Segment:
    def __init__(self, start, control1, control2, end):
        if isinstance(start, Node):
            self.start = start
        else:
            self.start = Node(*start)
        self.control1 = control1
        self.control2 = control2
        self.end = Node(*end)

class Node(collections.namedtuple('C', ['x', 'y'])):
    def __init__(self, x, y):
        self.size = 5

state = EditorState(level_name)

pyglet.clock.schedule_interval(state.maybe_reload_input, 1/4)

@window.event
def on_draw():
    window.clear()
    state.draw()

@window.event
def on_mouse_motion(x, y, dx, dy):
    state.mouse_moved(x, y)

@window.event
def on_mouse_drag(x, y, dx, dy, button, mod):
    if button & pyglet.window.mouse.MIDDLE:
        state.pan(dx, dy)
    elif button & pyglet.window.mouse.LEFT:
        state.resize_width(dx/5 + dy*2)
    else:
        state.mouse_moved(x, y)

@window.event
def on_mouse_release(x, y, button, mod):
    state.apply_change()

@window.event
def on_mouse_scroll(x, y, sx, sy):
    state.adjust_zoom(x, y, sy)
    state.mouse_moved(x, y)

@window.event
def on_resize(w, h):
    state.reset_zoom_pan()

@window.event
def on_key_press(key, mod):
    if key == pyglet.window.key.R:
        state.reset_zoom_pan()
    elif key == pyglet.window.key.F5:
        state.read_aux()
    elif key == pyglet.window.key.S:
        state.set_first_segment()
        state.apply_change()

pyglet.app.run()
