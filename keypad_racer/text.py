import struct
import zlib
import collections
import itertools

import png

from . import resources
from .anim import ConstantValue, AnimatedValue

def get_font(ctx):
    try:
        return ctx.extra.font
    except AttributeError:
        ctx.extra.font = Font(ctx, 'font.png')
    return ctx.extra.font

class Text:
    def __init__(self, ctx, chars, ypos=0, scale=1, outline=False, color=(1,1,1,1)):
        self.ctx = ctx
        self.font = font = get_font(ctx)

        vertices = bytearray()
        def layout_line(position, glyphs, ypos):
            position = -position/2
            for glyph in glyphs:
                if glyph.atlas_bounds[2] > 0:
                    for u, v in (1, 0), (1, 0), (0, 0), (1, 1), (0, 1), (0, 1): 
                        vertices.extend(struct.pack(
                            '=2b4e4e2e',
                            u, v,
                            *(scale*b for b in glyph.plane_bounds),
                            *glyph.atlas_bounds,
                            position,
                            ypos,
                        ))
                position += glyph.advance * scale
            glyphs.clear()

        glyphs = []
        position = 0
        for char in chars:
            if char == '\n':
                layout_line(position, glyphs, ypos)
                position = 0
                ypos -= scale
                continue
            glyph = font.get_glyph(char, 'italic')
            glyphs.append(glyph)
            position += glyph.advance * scale
        layout_line(position, glyphs, ypos)

        text_vbo = ctx.buffer(vertices)
        self.text_prog = ctx.program(
            vertex_shader=resources.get_shader('shaders/text.vert'),
            fragment_shader=resources.get_shader('shaders/text.frag'),
        )
        self.text_prog['atlas_tex'] = 0
        self.text_vao = ctx.vertex_array(
            self.text_prog,
            [
                (text_vbo, '2i1 4f2 4f2 2f2', 'uv', 'plane', 'atlas', 'position'),
            ],
        )
        def vec4(n):
            return tuple(ConstantValue(n) for i in range(4))
        def vec4from(x):
            return tuple(ConstantValue(n) for n in x)
        if outline:
            self.body_color = vec4(0.0)
            self.outline_color = vec4from(color)
        else:
            self.body_color = vec4from(color)
            self.outline_color = vec4(0.0)

    def draw(self, view):
        view.setup(self.text_prog)
        self.font.texture.use(location=0)
        self.text_prog['body_color'] = self.body_color
        self.text_prog['outline_color'] = self.outline_color
        self.text_vao.render(
            self.ctx.TRIANGLE_STRIP,
        )

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # From https://docs.python.org/3/library/itertools.html
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)

class Font:
    def __init__(self, ctx, name):
        self.ctx = ctx

        font_data = bytearray()
        with resources.open(name, 'rb') as f:
            width, height, rows, info = png.Reader(file=f).asRGBA8()
            self.width = width
            self.height = height
            for row in rows:
                font_data.extend(row)

        self.texture = ctx.texture(
            (width, height), 4, font_data,
        )

        faces_seq = []
        with resources.open(name, 'rb') as f:
            for chunk_type, content in png.Reader(file=f).chunks():
                if chunk_type == b'faCe':
                    line_height = struct.unpack('<e', content[:2])
                    name = content[2:].decode()
                    faces_seq.append(Face(name, line_height))
                elif chunk_type == b'foNt':
                    content = zlib.decompress(content)
                    fmt = '<BIe8s8s'
                    chunk_len = struct.calcsize(fmt)
                    for i in range(0, len(content), chunk_len):
                        chunk = content[i:i+chunk_len]
                        face, point, advance, plane_bounds, atlas_bounds = (
                            struct.unpack(fmt, chunk)
                        )
                        plane_bounds = unpack_bounds(plane_bounds, 1, 1)
                        atlas_bounds = unpack_bounds(atlas_bounds, width, height)
                        glyph = Glyph(advance, plane_bounds, atlas_bounds)
                        faces_seq[face].glyphs[chr(point)] = glyph

        self.faces = {f.name: f for f in faces_seq}
        print(self.faces)

    def get_glyph(self, char, *font_names, fallback='☒'):
        for font_name in (*font_names, 'regular', 'fallback'):
            try:
                return self.faces[font_name].glyphs[char]
            except KeyError:
                pass
        if fallback is None:
            return None
        return self.faces['fallback'].glyphs[fallback]

    __getitem__ = get_glyph

class Face:
    def __init__(self, name, line_height):
        self.name = name
        self.line_height = line_height
        self.glyphs = {}

def unpack_bounds(bounds, w, h):
    left, bottom, right, top = struct.unpack('<4e', bounds)
    return left/w, bottom/h, (right-left)/w, (top-bottom)/h

Glyph = collections.namedtuple(
    'Glyph',
    ('advance', 'plane_bounds', 'atlas_bounds'),
)
