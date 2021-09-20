#version 330

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
    vec3 base_color = mix(
        vec3(0.1, 0.1, 0.2),
        vec3(0.12, 0.11, 0.1),
        v_screenuv.y / 2.0 + 0.5);
    vec3 grid_color = mix(
        vec3(0.2, 0.26, 0.3),
        vec3(0.2, 0.26, 0.3) * 0.6,
        length(v_screenuv_norm));
    gl_FragColor = vec4(mix(
        base_color,
        grid_color,
        strength), 1.0);
}
