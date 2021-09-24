#version 330
#include world_project.inc

uniform vec3 color;

in float g_t;
in float g_thickness;
in float g_distance;

vec4 gradient_palette(vec3 color, float t) {
    if (t < 0.5) {
        return vec4(color, t * 1.5);
    }
    t = (1.0 - t) * 2.0;
    return vec4(mix(vec3(1.0), color, t), 0.75);
}

void main() {
    float d = abs(g_distance);
    vec4 g_color = gradient_palette(color, g_t);
    float thickness = g_thickness;
    gl_FragColor = g_color;
    gl_FragColor.r = d / 10;
    if (d < thickness) {
        gl_FragColor = g_color;
        gl_FragColor.r = 1.0;
        return;
    }
    d -= thickness;
    float aa = gridlines_per_px();
    if (d < aa) {
        gl_FragColor = vec4(g_color.rgb, g_color.a * (1.0-d/aa));
        return;
    }
    discard;
}
