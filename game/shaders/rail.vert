#version 330
#include world_project.inc

uniform ivec2 grid_origin;

attribute float thickness;
attribute vec2 point;
attribute vec4 color;

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
    v_color = color;
    float wrot = projection_params.w;
    float swr = sin(wrot);
    float cwr = cos(wrot);
    mat2 rotw = mat2(
        cwr, swr,
        -swr, cwr
    );
    vec2 pt = transform_car((point - grid_origin), vec2(0.0), 0.0);
    gl_Position = vec4(pt, 0.0, 1.0);
}
