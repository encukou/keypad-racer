from pathlib import Path

import moderngl
import png

from . import resources

class Circuit:
    def __init__(self, view, path):
        self.ctx = ctx = view.ctx
        path = Path(path).resolve()
        with path.open('rb') as f:
            data = png.Reader(file=f).asRGBA8()
        print(data)

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
        self.grid_vao = ctx.vertex_array(
            grid_prog,
            [
                (uv_vbo, '2i1', 'uv'),
            ],
        )

        view.register_programs(grid_prog)

    def draw(self):
        self.grid_vao.render(
            moderngl.TRIANGLE_STRIP,
        )
