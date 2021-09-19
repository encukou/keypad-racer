uniform vec2 resolution;
uniform float antialias;

attribute float thickness;
attribute vec2 point;

varying float v_thickness;
varying vec4 v_color;

void main() {
    float alpha;
    if (thickness < 0.1) {
        alpha = thickness;
        v_thickness = 1.0;
    } else {
        alpha = 1.0;
        v_thickness = thickness;
    }
    v_color = vec4(0.0, 1.0, 0.0, alpha);
    gl_Position = vec4(point, 0.0, 1.0);
}
