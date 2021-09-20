#version 330

uniform float zoom;
uniform vec2 pan;
uniform vec2 resolution;
attribute vec2 uv;

varying vec2 v_uv;
varying float line_width;
varying float antialias;
varying vec2 v_screenuv;
varying vec2 v_screenuv_norm;

void main() {
    float wrot = 0.005;
    float swr = sin(wrot);
    float cwr = cos(wrot);
    mat2 rotw = mat2(
        cwr, swr,
        -swr, cwr
    );
    gl_Position = vec4(uv, 0.0, 1.0);
    v_uv = (((uv) * zoom) / vec2(resolution.y, resolution.x)*resolution.x + pan) * rotw;
    v_screenuv = uv;
    if (resolution.x > resolution.y) {
        v_screenuv_norm = vec2(
            v_screenuv.x * resolution.y / resolution.x,
            v_screenuv.y);
    } else {
        v_screenuv_norm = vec2(
            v_screenuv.x,
            v_screenuv.y * resolution.x / resolution.y);
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
