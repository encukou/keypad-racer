#version 330

float SDF_circle(vec2 p, float radius)
{
    return length(p) - radius;
}

float distance(vec2 P, vec2 center, float radius)
{
    return length(P-center) - radius;
}

uniform float antialias;
varying vec4 g_color;
varying float g_thickness;
varying float g_distance;

varying vec2 v_p0, v_p1, v_p;

void main() {
    float d = abs(g_distance);
    float thickness = g_thickness / 4.0;
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
    return;
}
