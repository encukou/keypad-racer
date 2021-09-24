#version 330

uniform vec4 projection_params;
uniform vec4 viewport;
uniform ivec2 grid_origin;
in vec2 uv;

out vec2 grid_uv;
flat out vec2 line_width;
flat out vec2 antialias;
out vec2 v_screenuv;
out vec2 v_screenuv_norm;

void main() {
    gl_Position = vec4(uv, 0.0, 1.0);
    vec2 pan = projection_params.xy;
    vec2 scale = projection_params.zw;
    grid_uv = uv * scale + pan;
    v_screenuv = uv;
    if (viewport.z > viewport.w) {
        v_screenuv_norm = vec2(
            v_screenuv.x * viewport.z / viewport.w,
            v_screenuv.y);
    } else {
        v_screenuv_norm = vec2(
            v_screenuv.x,
            v_screenuv.y * viewport.w / viewport.z);
    }
    antialias = scale / viewport.zw;    // gridlines per px
    float px_per_scanline = 1/min(antialias.x, antialias.y);
    line_width = antialias * mix(
        1,     // minimum (px at 8px/gridline)
        5,    // maximum (px at 30px/gridline)
        smoothstep(
            8,
            30,
            px_per_scanline
        )
    );
}
