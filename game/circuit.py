from pathlib import Path
import struct

import png

from . import resources

class Circuit:
    def __init__(self, view, path):
        self.ctx = ctx = view.ctx
        path = Path(path).resolve()
        intersection_data = bytearray()
        with path.open('rb') as f:
            width, height, rows, info = png.Reader(file=f).asRGBA8()
            self.width = width
            self.height = height
            for row in reversed(list(rows)):
                intersection_data.extend(row)
        with path.open('rb') as f:
            for chunk_type, content in png.Reader(file=f).chunks():
                if chunk_type == b'stRt':
                    start_x, start_y = struct.unpack('<ii', content)

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

        grid_prog = ctx.program(
            vertex_shader=resources.get_shader('shaders/grid.vert'),
            fragment_shader=resources.get_shader('shaders/grid.frag'),
        )
        grid_prog['intersections_tex'] = 0
        grid_prog['grid_origin'] = start_x, start_y
        self.grid_vao = ctx.vertex_array(
            grid_prog,
            [
                (uv_vbo, '2i1', 'uv'),
            ],
        )

        view.register_programs(grid_prog)

    def draw(self):
        self.intersection_tex.use(location=0)
        self.grid_vao.render(
            self.ctx.TRIANGLE_STRIP,
        )
