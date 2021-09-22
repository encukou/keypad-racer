#version 330

uniform vec4 projection_params;
uniform vec2 resolution;
uniform ivec2 grid_origin;
attribute vec2 uv;

varying vec2 v_uv;
varying float line_width;
varying float antialias;
varying vec2 v_screenuv;
varying vec2 v_screenuv_norm;

void main() {
    float wrot = projection_params.w;
    float swr = sin(wrot);
    float cwr = cos(wrot);
    vec2 ruv = uv; + grid_origin;
    mat2 rotw = mat2(
        cwr, swr,
        -swr, cwr
    );
    gl_Position = vec4(ruv, 0.0, 1.0);
    vec2 pan = projection_params.xy;
    float zoom = projection_params.z;
    v_uv = (((ruv) * zoom) / vec2(resolution.y, resolution.x)*resolution.x + pan) * rotw;
    v_screenuv = ruv;
    if (resolution.x > resolution.y) {
        v_screenuv_norm = vec2(
            v_screenuv.x * resolution.x / resolution.y,
            v_screenuv.y);
    } else {
        v_screenuv_norm = vec2(
            v_screenuv.x,
            v_screenuv.y * resolution.y / resolution.x);
    }
    // minimum (z=res.y/7): line_width = 8 * zoom / resolution.y;
    // max (z=1): line_width = 30 * zoom / resolution.y;
    antialias = zoom / resolution.y * 2;
    line_width = antialias * mix(
        3,    // maximum (3px at z=1)
        0,    // minimum (0px -- antialias only at res.y/50)
        smoothstep(
            1,
            resolution.y/50,
            zoom
        )
    );
}
