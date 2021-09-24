#version 330

in float t;
in vec2 point;

out float v_thickness;
out float v_t;

void main() {
    float alpha;
    float thickness = 1;
    if (thickness < 0.1) {
        alpha = thickness;
        v_thickness = 1.0;
    } else {
        alpha = 1.0;
        v_thickness = thickness;
    }
    v_t = t;
    gl_Position = vec4(point, 0.0, 1.0);
}
