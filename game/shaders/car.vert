#version 330
#include world_project.inc

attribute vec2 uv;
attribute vec2 pos;
attribute vec4 color;
attribute float orientation;

varying float v_thickness;
varying vec4 v_color;
varying vec2 v_uv;

void main() {
    gl_Position = vec4(
        transform_car(pos, uv, orientation),
        0.0, 1.0
    );
    v_color = color;
    v_uv = uv * 2;
}
