uniform vec2 resolution;
uniform float antialias;

attribute float thickness;
attribute vec2 p0, p1, uv;

varying float v_alpha, v_thickness;
varying vec2 v_p0, v_p1, v_p;
varying vec3 v_color;

void main() {
    v_color = vec3(uv, 1.0);

    // Convert thickness of 1 px to reduced alpha
    if( abs(thickness) < 1.0 ) {
        v_thickness = 1.0;
        v_alpha = abs(thickness);
    } else {
        v_thickness = abs(thickness);
        v_alpha = 1.0;
    }

    // The thickness of a half of the drawn rectangle
    float half_quad_thickness = v_thickness/2.0 + antialias;

    // Length of the drawn rectangle
    float len = length(p1-p0);

    float u = 1.0 - uv.x * 2.0;
    float v = 1.0 - uv.y * 2.0;

    // Screen space

    vec2 direction = normalize(p1-p0);
    vec2 side_direction = vec2(-direction.y, direction.x);

    vec2 offset =
        + u * half_quad_thickness * direction
        + v * half_quad_thickness * side_direction
        ;
    vec2 base = (uv.x > 0.0) ? p1 : p0;

    gl_Position = vec4(base + offset/resolution, 0.0, 1.0);

    // Local space

    direction = vec2(1.0, 0.0);
    side_direction = vec2(0.0, 1.0);
    offset =
        + u * half_quad_thickness * direction
        + v * half_quad_thickness * side_direction
        ;
    base = vec2(uv.x, 0);
    v_p0 = vec2(0.0, 0.0);
    v_p1 = vec2(len, 0.0);
    v_p  = base + offset;
}
