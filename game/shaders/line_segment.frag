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
varying vec2 v_position;
varying vec3 g_color;
varying float v_thickness;
varying float v_alpha;

varying vec2 v_p0, v_p1, v_p;

void main() {
    gl_FragColor = vec4(g_color, 1.0);
    return;
    float d = 0;
    vec2 p = v_p / v_thickness;
    gl_FragColor = vec4(1.0, p.y, p.x, 0.5);
    d = p.x - v_thickness;
    /*
    if( v_p.x < 0.0 )
        d = length(v_p - v_p0) - v_thickness/2.0 + antialias/2.0;
    else if ( v_p.x > length(v_p1-v_p0) )
        d = length(v_p - v_p1) - v_thickness/2.0 + antialias/2.0;
    else
        d = abs(v_p.y) - v_thickness/2.0 + antialias/2.0;
    */
    if( d < 0)
        gl_FragColor = vec4(g_color, 1.0);
    else if (d < antialias) {
        d = exp(-d*d);
        gl_FragColor = vec4(g_color, d);
    }
}
