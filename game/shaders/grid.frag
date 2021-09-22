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
    float pointstrength = min(c(tpos.x), c(tpos.y));
    ivec2 tilepos = ivec2(round(v_uv));
    vec2 intilepos = (vec2(tilepos) - (v_uv));
    tilepos += grid_origin;
    ivec2 neighbour = tilepos;
    int arm_axis;
    float arm_dist;
    if (abs(intilepos.x) > abs(intilepos.y)) {
        if (intilepos.x > 0) {
            arm_axis = 0;
            arm_dist = intilepos.x;
            neighbour.x -= 1;
        } else {
            arm_axis = 2;
            arm_dist = -intilepos.x;
            neighbour.x += 1;
        }
    } else {
        if (intilepos.y > 0) {
            arm_axis = 1;
            arm_dist = intilepos.y;
            neighbour.y -= 1;
        } else {
            arm_axis = 3;
            arm_dist = -intilepos.y;
            neighbour.y += 1;
        }
    }
    vec4 intersections = texelFetch(intersections_tex, tilepos, 0);
    vec4 neighbour_int = texelFetch(intersections_tex, neighbour, 0);
    vec3 base_color = mix(
        vec3(0.1, 0.1, 0.2),
        vec3(0.12, 0.11, 0.1),
        v_screenuv.y / 2.0 + 0.5);
    if (strength == 0) {
        gl_FragColor = vec4(base_color, 1.0);
    } else {
        vec3 grid_color;
        if (
            (arm_dist < intersections[arm_axis])
            || (((1-arm_dist)) < neighbour_int[(arm_axis+2)%4])
        ) {
            grid_color = mix(
                vec3(0.27, 0.28, 0.32),
                vec3(0.13, 0.18, 0.21),
                clamp(0.0, 1.0, length(v_screenuv_norm)));
        } else {
            grid_color = mix(
                vec3(0.27, 0.28, 0.32),
                vec3(0.13, 0.18, 0.21),
                clamp(0.0, 1.0, length(v_screenuv_norm))).zyx;
        }
        if ((intersections != vec4(0.0))) {
            grid_color *= 1+pointstrength;
        }
        grid_color = mix(
            base_color,
            grid_color,
            strength);
        gl_FragColor = vec4(grid_color, 1.0);
    }
}
