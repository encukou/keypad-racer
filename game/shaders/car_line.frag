#version 330

uniform float antialias;
uniform vec3 color;
uniform float zoom;
uniform vec4 viewport;

varying float g_t;
varying float g_thickness;
varying float g_distance;

varying vec2 v_p0, v_p1, v_p;

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
    float aa = antialias / (viewport.z+viewport.w) * zoom;
    float thickness = 0.5 - (1.0-g_t) / 4.0 - aa;
    gl_FragColor = g_color;
    gl_FragColor.r = d / 10;
    if (d < thickness) {
        gl_FragColor = g_color;
        gl_FragColor.r = 1.0;
        return;
    }
    d -= thickness;
    if (d < aa) {
        gl_FragColor = vec4(g_color.rgb, g_color.a * (1.0-d/aa));
        return;
    }
    gl_FragColor = vec4(g_color.rgb, 0.0);
}
