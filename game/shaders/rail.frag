#version 330

uniform float antialias;
varying vec4 g_color;
varying float g_thickness;
varying float g_distance;

varying vec2 v_p0, v_p1, v_p;

void main() {
    float d = abs(g_distance);
    float thickness = g_thickness / 2.0;
    if (d < thickness) {
        gl_FragColor = g_color;
        return;
    }
    d -= thickness;
    if (d < antialias) {
        gl_FragColor = vec4(g_color.rgb, g_color.a * (1.0-d/antialias));
        return;
    }
    gl_FragColor = vec4(g_color.rgb, 1.0);
}
