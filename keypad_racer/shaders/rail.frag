#version 330
#include world_project.inc

in vec4 g_color;
in float g_thickness;
in float g_distance;

void main() {
    float d = abs(g_distance);
    float thickness = 0.0;
    if (d < thickness) {
        gl_FragColor = g_color;
        gl_FragColor.r = d;
        return;
    }
    d -= thickness;
    float aa = gridlines_per_px() * 2.5;
    if (d < aa) {
        gl_FragColor = vec4(g_color.rgb, (1-d/aa));
        return;
    }
    discard;
    gl_FragColor=vec4(1);
}
