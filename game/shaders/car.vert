#version 330
#include world_project.inc

in vec2 uv;
in vec2 pos;
in vec4 color;
in float orientation;

out float v_thickness;
out vec4 v_color;
out vec2 v_uv;

void main() {
    gl_Position = vec4(
        transform_car(pos, uv, orientation),
        0.0, 1.0
    );
    v_color = color;
    v_uv = uv * 2;
}
