#version 330

uniform float antialias;
uniform float zoom;
uniform vec2 resolution;

varying vec4 v_color;
varying vec2 v_uv;

// Isosceles Trapezoid - exact
// https://iquilezles.org/www/articles/distfunctions2d/distfunctions2d.htm
// By Inigo Quilez (used under MIT license)
float dot2(in vec2 v ) { return dot(v,v); }
float sdTrapezoid( in vec2 p, in float r1, float r2, float he )
{
    vec2 k1 = vec2(r2,he);
    vec2 k2 = vec2(r2-r1,2.0*he);
    p.x = abs(p.x);
    vec2 ca = vec2(p.x-min(p.x,(p.y<0.0)?r1:r2), abs(p.y)-he);
    vec2 cb = p - k1 + k2*clamp( dot(k1-p,k2)/dot2(k2), 0.0, 1.0 );
    float s = (cb.x<0.0 && ca.y<0.0) ? -1.0 : 1.0;
    return s*sqrt( min(dot2(ca),dot2(cb)) );
}


void main() {
    gl_FragColor = v_color;
    float sdf = sdTrapezoid(v_uv, 0.60, 0.43, 0.9);
    if (sdf < 0) {
        gl_FragColor = vec4(v_color.xyz, 1.0);
        return;
    }
    float aa = antialias * zoom / resolution.y * 2;
    if (sdf < aa) {
        gl_FragColor = vec4(v_color.xyz, 1.0 - sdf/aa);
        return;
    }
    gl_FragColor = vec4(v_color.xyz, 0.0);
}
