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
- `R` key: Reset zoom/pan (also happens on window resize)

- Up/Down drag: Resize control point
- Left/Right drag: Resize control point (fine adjustment)
- `1` key: Set start point
- `F5` key: Reload auxiliary file
"""

import os
import sys
from pathlib import Path
import xml.sax.handler
import re
import operator
import collections
import json
import functools
import itertools
import math
import struct
import zlib

import pyglet
import numpy
from PIL import Image
from PIL.PngImagePlugin import PngInfo

try:
    level_name = sys.argv[1]
except IndexError:
    print(f'Usage: {sys.argv[0]} levelname', file=sys.stderr)
    exit(1)

circle = pyglet.image.load(Path(__file__).parent / 'circle.png')
startcirc = pyglet.image.load(Path(__file__).parent / 'start.png')
halfcirc = pyglet.image.load(Path(__file__).parent / 'half_circ.png')

pyglet.image.Texture.default_min_filter = pyglet.gl.GL_NEAREST
pyglet.image.Texture.default_mag_filter = pyglet.gl.GL_NEAREST

window = pyglet.window.Window(
    width=1000,
    height=1800,
    resizable=True,
    caption=f'Level editor: {level_name}'
)
if 'GAME_DEVEL_ENVIRON' in os.environ:
    window.set_location(200, 200)
if 'GAME_DEVEL_ENVIRON2' in os.environ:
    window.set_location(1100, 0)

class Yield:
    def __await__(self):
        yield 0
Yield = Yield()

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
        elif part == 'm':
            if points:
                raise ValueError('circuit can only have a single path')
            current_pos = add_point_rel(next(path_iter), next(path_iter))
            command = 'l'
        elif part in 'CcLl':
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
            elif command == 'l':
                points.append(points[-1])
                current_pos = add_point_rel(part, next(path_iter))
                points.append(points[-1])
            elif command == 'L':
                points.append(points[-1])
                current_pos = add_point_abs(part, next(path_iter))
                points.append(points[-1])
            else:
                raise ValueError(f'Unknown SVG path command: {command}')
        else:
            print(path)
            raise ValueError(f'Unknown SVG path part: {part}')
    return points

def get_bb(points):
    return tuple(
        fun(points, key=operator.itemgetter(i))[i]
        for fun, i in ((min, 0), (min, 1), (max, 0), (max, 1))
    )

class EditorState:
    def __init__(self, level_name):
        self.input_path = Path(f'{level_name}.svg').resolve()
        self.aux_path = Path(f'{level_name}.json').resolve()
        self.output_path = Path(f'{level_name}.png').resolve()
        self.mouse_pos = window.width / 2, window.height / 2
        self.tex = None
        self.zoom = 1
        self.changing = False
        self.view_center = 0, 0
        self.task = None
        self.maybe_reload_input()
        self.reset_zoom_pan()

    def run_task(self, task):
        self.task = task.__await__()
        self.drive_task(0)

    def drive_task(self, dt=0):
        if self.task is not None:
            try:
                next(self.task)
            except StopIteration:
                self.task = None

    def reset_zoom_pan(self):
        print('reset')
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

    def _zoom_to_detail(self, arg=None):
        segment = self.segments[10]
        self.view_center = segment.start.vec
        self.zoom = 40

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
        min_x, min_y, max_x, max_y = get_bb(points)
        points = [(x - min_x, y - min_y) for x, y in points]
        self.bb = get_bb(points)
        seg = Segment(self, *points[:4])
        self.segments = [seg]
        for points in zip(points[4::3], points[5::3], points[6::3]):
            seg = Segment(self, seg.end, *points)
            self.segments.append(seg)
        seg.end = self.segments[0].start
        seg.end.segments.append(seg)
        seg.end.controls.insert(0, numpy.array(seg.control2))
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
        self.run_task(self.main_task())

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
            #point = {'pos': tuple(seg.start.vec - self.bb[:2]), 'radius': seg.start.size}
            point = {'pos': seg.start, 'radius': seg.start.size}
            if i == 0:
                point['first'] = True
            points.append(point)
        data = {'points': points}
        result = json.dumps(data, indent=4)
        self.aux_path.write_text(result)
        print('aux file saved')
        self.run_task(self.main_task())
        for i in range(10):
            self.drive_task(0)

    async def main_task(self):
        await Yield
        print('Task starting')
        segments = self.segments
        def iter_segments():
            for segment in segments:
                if segments is not self.segments:
                    return
                if segment.done:
                    continue
                yield segment
        for segment in iter_segments():
            segment.set_borders()
            await Yield
        for segment in iter_segments():
            for border in segment.borders:
                await border.subdivide()
                await Yield
            segment.done = True
        await self.update_pixels()
        print('Task done')

    async def update_pixels(self):
        all_control_points = list(itertools.chain.from_iterable(
            segment.get_all_control_points() for segment in self.segments
        ))
        xmin, ymin, xmax, ymax = get_bb(all_control_points)
        floor = math.floor
        ceil = math.ceil
        xmin, ymin = floor(xmin), floor(ymin)
        xmax, ymax = ceil(xmax), ceil(ymax)
        width, height = xmax - xmin+1, ymax - ymin+1
        data = numpy.zeros((width, height, 4))
        def update_snapshot():
            byt = (data*255).astype('u1').transpose((1, 0, 2)).tobytes('C')
            img_data = pyglet.image.ImageData(
                width, height,
                format='RGBA',
                data=byt,
            )
            tex = img_data.get_texture()
            tex.anchor_x = -xmin
            tex.anchor_y = -ymin
            self.tex = tex
            return byt
        update_snapshot()

        crossings = {'x': {}, 'y': {}}
        for segment in self.segments:
            for invert, border in enumerate(segment.borders):
                for div in border.subdivisions:
                    t, n, (x, y), c = div
                    for axis, axis_name in enumerate('xy'):
                        if axis_name in div.c:
                            other_axis = 1 - axis
                            a = div.pt[axis]
                            b = div.pt[other_axis]
                            assert b == int(b)
                            lst = crossings[axis_name].setdefault(int(b), [])
                            tangent = div.tangent
                            if invert^axis:
                                tangent = -tangent
                            lst.append((
                                a,
                                int(numpy.sign(tangent[other_axis])),
                                div,
                            ))
        for axis, axis_name in enumerate('xy'):
            other_axis = 1 - axis
            for strip, divs in sorted(crossings[axis_name].items()):
                divs.sort()
                current = -1
                regions = []
                for a, sgn, d in divs:
                    if sgn == current:
                        continue
                    elif sgn == 1:
                        regions.append([a])
                    elif sgn == -1:
                        regions[-1].append(a)
                    current = sgn
                for start, end in regions:
                    first = math.ceil(start)
                    last = math.floor(end)
                    for b in range(first, last+1):
                        if axis:
                            x = strip - xmin
                            y = b - ymin
                        else:
                            x = b - xmin
                            y = strip - ymin
                        data[x, y, axis] = 1
                        data[x, y, axis+2] = 1
                        if b == first:
                            data[x, y, axis] = abs(first - start)
                        if b == last:
                            data[x, y, axis+2] = abs(last - end)
            update_snapshot()
            await Yield

        pnginfo = PngInfo()

        for border_id in 0, 1:
            current = None
            packeds = []
            for segment in self.segments:
                border = segment.borders[border_id]
                for div in border.subdivisions:
                    packed = struct.pack('<ee', *(div.pt - (xmin, ymin)))
                    if packed != current:
                        packeds.append(packed)
                        current = packed
            # Repeat coordinate a bunch of times
            # to account for closed shape & line_strip_adjacency
            first_coord = packeds[0]
            packeds.insert(0, first_coord)
            packeds.append(first_coord)
            packeds.append(first_coord)
            if border_id:
                packeds.reverse()
            pnginfo.add(
                b'raIl',
                zlib.compress(b''.join(packeds), zlib.Z_BEST_COMPRESSION)
            )

        byt = update_snapshot()
        mode = 'RGBA'
        img = Image.frombuffer(mode, (width, height), byt, 'raw', mode, 0, -1)
        start = self.segments[0].start
        pnginfo.add(b'stRt', struct.pack(
            '<ii',
            round(start.x - xmin), round(start.y - ymin)
        ))
        img.save(self.output_path, pnginfo=pnginfo)
        print('Level saved')

    def draw(self):
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glTranslatef(window.width/2, window.height/2, 0)
        pyglet.gl.glScalef(self.zoom, self.zoom, 1)
        pyglet.gl.glTranslatef(-self.view_center[0], -self.view_center[1], 0)
        # Texture
        pyglet.gl.glColor4f(1, 1, 1, .2)
        if self.tex:
            self.tex.blit(-0.5, -0.5)
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
            if u == 0:
                pyglet.gl.glColor4f(.6, 0, 0, 1)
            elif -4 <= u <= 4:
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
        for i, segment in enumerate(self.segments):
            pyglet.gl.glPushMatrix()
            pyglet.gl.glTranslatef(*segment.start, 0)
            alpha = 0.2
            if numpy.isnan(segment.start.normal).any():
                pyglet.gl.glColor4f(1, 0, 0, alpha)
            elif segment == self.active_segment:
                pyglet.gl.glColor4f(0, 1, 0, 0.5)
            else:
                pyglet.gl.glColor4f(1, 1, 0, alpha)
            size = segment.start.size * 2
            if i == 0:
                img = startcirc
            else:
                img = circle
            img.blit(-size/2, -size/2, width=size, height=size)
            # Tangent
            pyglet.gl.glColor4f(1, 1, 1, 1)
            pyglet.gl.glBegin(pyglet.gl.GL_LINES)
            pyglet.gl.glVertex2f(0, 0)
            pyglet.gl.glVertex2f(*segment.start.tangent)
            pyglet.gl.glEnd()
            pyglet.gl.glPopMatrix()
        # Straight lines
        pyglet.gl.glColor4f(1, 1, 1, .15)
        pyglet.gl.glBegin(pyglet.gl.GL_LINE_STRIP)
        for segment in self.segments:
            pyglet.gl.glVertex2f(*segment.start)
            pyglet.gl.glVertex2f(*segment.end)
        pyglet.gl.glEnd()
        # Normals
        pyglet.gl.glColor4f(1, 1, 0, .5)
        pyglet.gl.glBegin(pyglet.gl.GL_LINES)
        for segment in self.segments:
            if not numpy.isnan(segment.start.normal).any():
                pyglet.gl.glVertex2f(*(segment.start.vec))
                pyglet.gl.glVertex2f(*(segment.start.vec + segment.start.normal))
        pyglet.gl.glEnd()
        # Borders
        for segment in self.segments:
            for border in segment.borders:
                pyglet.gl.glColor4f(1, 1, 1, .5)
                if not segment.done:
                    N = 20
                    pyglet.gl.glBegin(pyglet.gl.GL_LINE_STRIP)
                    for i in range(N+1):
                        pyglet.gl.glVertex2f(*border.evaluate(i/N))
                    pyglet.gl.glEnd()
                pyglet.gl.glBegin(pyglet.gl.GL_LINE_STRIP)
                for s in border.subdivisions:
                    pyglet.gl.glVertex2f(*s.pt)
                pyglet.gl.glEnd()
                pyglet.gl.glColor4f(1, 1, 1, .5)
                pyglet.gl.glBegin(pyglet.gl.GL_LINES)
                for s in border.subdivisions:
                    pt = s.pt
                    if 'y' in s.c:
                        p = [1/5, 0]
                        pyglet.gl.glVertex2f(*pt - p)
                        pyglet.gl.glVertex2f(*pt + p)
                    if 'x' in s.c:
                        p = [0, 1/5]
                        pyglet.gl.glVertex2f(*pt - p)
                        pyglet.gl.glVertex2f(*pt + p)
                    if 's' in s.c:
                        p = [1/6, 1/6]
                        pyglet.gl.glVertex2f(*pt - p)
                        pyglet.gl.glVertex2f(*pt + p)
                        p = [1/6, -1/6]
                        pyglet.gl.glVertex2f(*pt - p)
                        pyglet.gl.glVertex2f(*pt + p)
                    if 'c' in s.c:
                        p = [1/16, 1/16]
                        pyglet.gl.glVertex2f(*pt - p)
                        pyglet.gl.glVertex2f(*pt + p)
                        p = [1/16, -1/16]
                        pyglet.gl.glVertex2f(*pt - p)
                        pyglet.gl.glVertex2f(*pt + p)
                    pyglet.gl.glVertex2f(*pt)
                    pyglet.gl.glVertex2f(*pt + s.tangent/2)
                pyglet.gl.glEnd()
        # All control points
        pyglet.gl.glColor4f(1, 1, 1, 1)
        pyglet.gl.glBegin(pyglet.gl.GL_POINTS)
        for segment in self.segments:
            for point in segment.get_all_control_points():
                pyglet.gl.glVertex2f(*point)
        pyglet.gl.glEnd()

def normalize(v):
    return v / numpy.linalg.norm(v)

class Segment:
    def __init__(self, state, start, control1, control2, end):
        if isinstance(start, Node):
            self.start = start
        else:
            self.start = Node(*start)
            self.start.controls = []
        self.start.segments.append(self)
        self.start.controls.append(numpy.array(control1))
        self.control1 = control1
        self.control2 = control2
        self.end = Node(*end)
        self.end.segments.append(self)
        self.end.controls = [numpy.array(control2)]
        self.borders = []
        self.done = False
        self.state = state
        self.curve_angles = []

    def set_dirty(self, recursive=False):
        if self.done:
            self.done = False
            self.state.run_task(state.main_task())

    def set_borders(self):
        snorm = self.start.normal
        enorm = self.end.normal
        ctr1_vec = self.start.controls[1] - self.start.vec
        ctr2_vec = self.end.controls[0] - self.end.vec
        direction = self.end.vec - self.start.vec
        def angle_between(v1, v2):
            cross = numpy.cross(normalize(v1), normalize(v2))
            sgn = 1 if cross >0 else -1
            return cross
        self.curve_angles = [
            angle_between(self.start.tangent, direction),
            angle_between(-self.end.tangent, direction),
        ]
        start_adjust = (1+self.curve_angles[0]/3)
        end_adjust = (1+self.curve_angles[1]/3)
        self.borders = [
            Bezier(
                self.start.vec + snorm,
                self.start.vec + ctr1_vec / start_adjust + snorm,
                self.end.vec + ctr2_vec / end_adjust + enorm,
                self.end.vec + enorm
            ),
            Bezier(
                self.start.vec - snorm,
                self.start.vec + ctr1_vec * start_adjust - snorm,
                self.end.vec + ctr2_vec * end_adjust - enorm,
                self.end.vec - enorm,
            ),
        ]

    def get_all_control_points(self):
        yield self.start
        yield from self.start.controls
        yield from self.end.controls
        yield self.end
        for border in self.borders:
            yield from border.points

def _gen_halvings(a, b):
    if abs(a - b) < 0.1:
        return
    mid = (a + b) / 2
    yield mid
    for m, n in zip(_gen_halvings(a, mid), _gen_halvings(mid, b)):
        yield m
        yield n
HALVINGS = tuple(_gen_halvings(0, 1))

class Bezier:
    """Cubic de Casteljau/B??zier curve"""
    def __init__(self, p0, p1, p2, p3):
        self.points = [numpy.array(p) for p in (p0, p1, p2, p3)]
        self.subdivisions = []

    def evaluate(self, t):
        return (
            (1-t)**3 * self.points[0]
            + 3 * (1-t)**2 * t * self.points[1]
            + 3 * (1-t) * t**2 * self.points[2]
            + t**3 * self.points[3]
        )

    def evaluate_tangent(self, t):
        v = (
            (-3 * (1-t)**2) * self.points[0]
            + ((3*(1-t)**2 - 6*t*(1-t))) * self.points[1]
            + (- 3*t**2 + 6*t*(1-t)) * self.points[2]
            + 3 * t**2 * self.points[3]
        )
        if (v == 0).all():
            # Zero "speed" -> use tangent of entire curve
            return normalize(self.points[3] - self.points[0])
        return normalize(v)

    async def subdivide(self):
        EPSILON = 0.001
        EPSILON2 = 0.01
        EPSILON3 = 0.00001
        nums = itertools.count()
        self.subdivisions = []
        def add_subdiv(t, pt, crossings):
            p = PointAtBezier(t, next(nums), pt, crossings)
            p.tangent = self.evaluate_tangent(t)
            p.curve = self
            self.subdivisions.append(p)
        def is_almost_int(w):
            r = round(w)
            return abs(w-r) < EPSILON3
        for t in 0, 1:
            crossings = {'s'}
            x, y = pt = self.evaluate(t)
            if is_almost_int(x):
                x = round(x)
                crossings.add('y')
            if is_almost_int(y):
                y = round(y)
                crossings.add('x')
            add_subdiv(t, numpy.array([x, y]), crossings)
        def do_subdiv():
            self.subdivisions.sort()
            for s0, s1 in zip(self.subdivisions, self.subdivisions[1:]):
                for axis_name, crossing_name, axis in ('x', 'y', 0), ('y', 'x', 1):
                    a0 = s0.pt[axis]
                    a1 = s1.pt[axis]
                    if math.floor(a0) == math.floor(a1):
                        continue
                    if math.floor(a0) == a0 and abs(a0-a1) <= 1:
                        continue
                    if math.floor(a1) == a1 and abs(a0-a1) <= 1:
                        continue
                    a0 = self.evaluate(s0.t)[axis]
                    a1 = self.evaluate(s1.t)[axis]
                    ra0 = math.floor(a0)
                    if ra0 == math.floor(a1):
                        continue
                    lower = s0.t
                    higher = s1.t
                    mid_t = (lower + higher)/2
                    while abs(higher - lower) > 0.000001:
                        mid_a = self.evaluate(mid_t)[axis]
                        same = (math.floor(mid_a) == ra0)
                        if same:
                            lower = mid_t
                        else:
                            higher = mid_t
                        mid_t = (lower+higher)/2
                    pt = self.evaluate(mid_t)
                    pt[axis] = round(pt[axis])
                    add_subdiv(mid_t, pt, {crossing_name})
                    return True
            halved_something = False
            for s0, s1 in zip(self.subdivisions, self.subdivisions[1:]):
                if numpy.linalg.norm(s1.pt - s0.pt) > EPSILON:
                    for halving in (0.5,):
                        mid_t = (1-halving) * s0.t + halving * s1.t
                        pt = self.evaluate(mid_t)

                        line = s0.pt - s1.pt
                        direction = n = numpy.linalg.norm(line)
                        distance = abs(numpy.cross(pt - s0.pt, s1.pt - s0.pt))
                        if distance > EPSILON2:
                            add_subdiv(mid_t, pt, {'c'})
                            halved_something = True
            return halved_something
        while do_subdiv():
            self.subdivisions.sort()
            await Yield
        merged_subdivisions = []
        current = None
        for div in self.subdivisions:
            if current is None or div.t != current.t:
                merged_subdivisions.append(div)
                current = div
            else:
                current.c.update(div.c)
        self.subdivisions = merged_subdivisions

class PointAtBezier(collections.namedtuple('P', ['t', 'n', 'pt', 'c'])):
    pass

class Node(collections.namedtuple('C', ['x', 'y'])):
    def __init__(self, x, y):
        self.vec = numpy.array([x, y])
        self._size = 3
        self.segments = []

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, new):
        if new < 1/4:
            new = 1/4
        self._size = new
        try:
            del self.normal
        except AttributeError:
            pass
        for seg in self.segments:
            seg.set_dirty()

    @functools.cached_property
    def tangent(self):
        tan = self.controls[1] - self.controls[0]
        return tan / numpy.linalg.norm(tan)

    @functools.cached_property
    def normal(self):
        tan = self.tangent
        normal = numpy.array([-tan[1], tan[0]])
        return normal * self.size

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
    if button & (pyglet.window.mouse.MIDDLE|pyglet.window.mouse.RIGHT):
        state.pan(dx, dy)
    elif button & pyglet.window.mouse.LEFT:
        state.resize_width(dx/5 + dy*2)
        state.apply_change()
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
    elif key == pyglet.window.key._1:
        state.set_first_segment()
        state.apply_change()

class EventLoop(pyglet.app.EventLoop):
    def idle(self):
        state.drive_task()
        wt = super().idle()
        if state.task:
            return 0
        return wt

pyglet.app.event_loop = EventLoop()
pyglet.app.run()
