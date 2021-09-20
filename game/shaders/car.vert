#version 330
#include world_project.inc

attribute vec2 uv;
attribute vec2 pos;
attribute vec4 color;
attribute float orientation;

varying float v_thickness;
varying vec4 v_color;

void main() {
    vec2 uvw = vec2(uv.x * (0.26 - uv.y * 0.04), uv.y * 0.45);
    gl_Position = vec4(transform_car(pos, uvw, orientation), 0.0, 1.0);
    v_color = color;
}
