#version 330
#include world_project.inc
uniform float antialias;

attribute vec2 point;
attribute vec4 color;

varying float v_thickness;
varying vec4 v_color;

void main() {
    float alpha;
    float thickness = 5 * zoom / (resolution.x+resolution.y)/2;
    if (thickness < 0.1) {
        alpha = thickness;
        v_thickness = 1.0;
    } else {
        alpha = 1.0;
        v_thickness = thickness;
    }
    v_color = color;
    gl_Position = vec4(transform_car(point, vec2(0, 0), 0), 0.0, 1.0);
}
