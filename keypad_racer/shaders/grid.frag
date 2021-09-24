#version 330

uniform sampler2D intersections_tex;
uniform ivec2 grid_origin;

in vec2 grid_uv;
flat in vec2 line_width;
flat in vec2 antialias;
in vec2 v_screenuv;
in vec2 v_screenuv_norm;

float c1(float dist, float lw, float aa) {
    dist = abs(dist - 0.5);
    if (dist < lw / 2) return 1.0;
    dist -= lw / 2;
    if (dist < aa) {
        return 1.0 - pow(dist / aa, 1.8);
    }
    return 0.0;
}

vec2 c(vec2 tile_pos) {
    vec2 dist = fract(tile_pos - 0.5);
    return vec2(
        c1(dist.x, line_width.x, antialias.x),
        c1(dist.y, line_width.y, antialias.y));
}

void main() {
    vec2 tpos = fract(grid_uv);
    vec2 cr = vec2(c(tpos).x, c(tpos).y);
    float strength = max(cr.x, cr.y);
    float pointstrength = min(cr.x, cr.y);
    ivec2 tilepos = ivec2(round(grid_uv));
    vec2 intilepos = (vec2(tilepos) - (grid_uv));
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
