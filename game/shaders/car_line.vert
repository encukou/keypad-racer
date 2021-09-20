#version 330
#include world_project.inc
uniform float antialias;
attribute float t;

attribute vec2 point;

varying float v_thickness;
varying float v_t;

void main() {
    float alpha;
    float thickness = 4 / zoom * (resolution.x+resolution.y)/2 / 0.015;
    if (thickness < 0.1) {
        alpha = thickness;
        v_thickness = 1.0;
    } else {
        alpha = 1.0;
        v_thickness = thickness;
    }
    v_t = t;
    gl_Position = vec4(transform_car(point, vec2(0, 0), 0), 0.0, 1.0);
}
