#version 330

uniform sampler2D intersections_tex;
uniform ivec2 grid_origin;

varying vec2 v_uv;
varying float line_width;
varying float antialias;
varying vec2 v_screenuv;
varying vec2 v_screenuv_norm;

float c(float tile_pos) {
    float dist = fract(tile_pos);
    if (dist > 0.5) dist = 1.0 - dist;
    if (dist < line_width / 2) return 1.0;
    dist -= line_width / 2;
    if (dist < antialias) {
        return 1.0 - pow(dist / antialias, 1.8);
    }
    return 0.0;
}

void main() {
    vec2 tpos = fract(v_uv);
    float strength = max(c(tpos.x), c(tpos.y));
    ivec2 tilepos = ivec2(v_uv - 0.5) + grid_origin;
    vec4 intersections = texelFetch(
        intersections_tex, tilepos, 0);
    intersections.x = (tilepos.x == 0) ? 1 : 0;
    vec3 base_color = mix(
        vec3(0.1, 0.1, 0.2),
        vec3(0.12, 0.11, 0.1),
        v_screenuv.y / 2.0 + 0.5);
    if (strength == 0) {
        gl_FragColor = vec4(base_color, 1.0);
    } else {
        vec3 grid_color = mix(
            vec3(0.27, 0.28, 0.32),
            vec3(0.13, 0.18, 0.21),
            clamp(0.0, 1.0, length(v_screenuv_norm)));
        grid_color = mix(
            grid_color,
            intersections.xyz,
            0.5);
        gl_FragColor = vec4(mix(
            base_color,
            grid_color,
            strength), 1.0);
    }
}
