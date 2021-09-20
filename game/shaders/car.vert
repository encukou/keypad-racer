uniform vec2 pan;
uniform float zoom;
uniform vec2 resolution;

attribute vec2 uv;
attribute vec2 pos;
attribute vec4 color;
attribute float orientation;

varying float v_thickness;
varying vec4 v_color;

void main() {
    float so = sin(orientation);
    float co = cos(orientation);
    mat2 rot = mat2(
        co, so,
        -so, co
    );
    vec2 zoomat = vec2(
        1.0/zoom*resolution.y,
        1.0/zoom*resolution.x
    );
    vec2 uvw = vec2(uv.x * (0.26 - uv.y * 0.04), uv.y * 0.45) * rot + pos;
    gl_Position = vec4(uvw * zoomat + pan, 0.0, 1.0);
    v_color = color;
}
