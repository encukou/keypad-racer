#version 330

uniform float antialias;
in vec4 g_color;
in float g_thickness;
in float g_distance;

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
    gl_FragColor = vec4(g_color.rgb, 0.0);
}
