from pathlib import Path
import struct
import sys
import zlib

import png

from . import resources

class Circuit:
    def __init__(self, ctx, path):
        self.ctx = ctx
        path = Path(path).resolve()
        intersection_data = bytearray()
        with path.open('rb') as f:
            width, height, rows, info = png.Reader(file=f).asRGBA8()
            self.width = width
            self.height = height
            for row in reversed(list(rows)):
                intersection_data.extend(row)

        # Get start point and rail coordinates from custom chunks
        start_x = start_y = 0
        rail_data = bytearray()
        self.rail_pieces = []
        with path.open('rb') as f:
            for chunk_type, content in png.Reader(file=f).chunks():
                if chunk_type == b'stRt':
                    start_x, start_y = struct.unpack('<ii', content)
                if chunk_type == b'raIl':
                    content = zlib.decompress(content)
                    # Rail coords are 2f2; 4 bytes in total.
                    self.rail_pieces.append((len(rail_data)//4, len(content)//4))
                    rail_data.extend(content)
        if sys.byteorder != 'little':
            # Byte-swap... hope it works, not tested on actual big endians
            rail_data[0::2], rail_data[1::2] = rail_data[1::2], rail_data[0::2]

        self.intersection_tex = ctx.texture(
            (width, height), 4, intersection_data,
        )

        uv_vertices = bytes((
            1, 255,
            255, 255,
            1, 1,
            255, 1,
        ))
        uv_vbo = ctx.buffer(uv_vertices)

        self.grid_prog = ctx.program(
            vertex_shader=resources.get_shader('shaders/grid.vert'),
            fragment_shader=resources.get_shader('shaders/grid.frag'),
        )
        self.grid_prog['intersections_tex'] = 0
        self.grid_prog['grid_origin'] = start_x, start_y
        self.grid_vao = ctx.vertex_array(
            self.grid_prog,
            [
                (uv_vbo, '2i1', 'uv'),
            ],
        )

        rail_vbo = ctx.buffer(rail_data)
        self.rail_prog = ctx.program(
            vertex_shader=resources.get_shader('shaders/rail.vert'),
            geometry_shader=resources.get_shader('shaders/rail.geom'),
            fragment_shader=resources.get_shader('shaders/rail.frag'),
        )
        self.rail_prog['grid_origin'] = start_x, start_y
        self.rail_vao = ctx.vertex_array(
            self.rail_prog,
            [
                (rail_vbo, '2f2', 'point'),
                (ctx.buffer(b'\xff\xff\xff\x88\x00'), '4f1 u1 /i', 'color', 'thickness'),
            ],
        )

    def draw(self, view):
        view.setup(self.grid_prog, self.rail_prog)
        self.intersection_tex.use(location=0)
        self.grid_vao.render(
            self.ctx.TRIANGLE_STRIP,
        )
        for start, num in self.rail_pieces:
            self.rail_vao.render(
                self.ctx.LINE_STRIP_ADJACENCY,
                first=start,
                vertices=num,
            )
