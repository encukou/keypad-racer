#version 330

uniform ivec2 grid_origin;

in float thickness;
in vec2 point;
in vec4 color;

out float v_thickness;
out vec4 v_color;

void main() {
    float alpha;
    if (thickness < 0.1) {
        alpha = thickness;
        v_thickness = 1.0;
    } else {
        alpha = 1.0;
        v_thickness = thickness;
    }
    v_color = color;
    gl_Position = vec4(point - grid_origin, 0.0, 1.0);
}
