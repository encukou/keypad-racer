#version 330
#include world_project.inc

in float v_thickness[];
in float v_t[];
out float g_distance;
out float g_t;
out float g_thickness;
flat out float aa;

layout(lines_adjacency) in;
layout(triangle_strip, max_vertices = 4) out;

void set_g_pervertex(int n) {
    g_thickness = v_thickness[n] / 4;
    g_t = v_t[n];
}

vec2 get_offset(vec2 p0, vec2 p1, vec2 p2) {
    vec2 direction = normalize(p2 - p1);
    vec2 dir_side = vec2(-direction.y, direction.x);

    vec2 offset = dir_side;
    if (p0 != p1) {
        vec2 t0 = normalize(p1 - p0);
        vec2 t1 = normalize(p2 - p1);
        vec2 n0 = vec2(-t0.y, t0.x);
        vec2 n1 = vec2(-t1.y, t1.x);
        vec2 miter_direction = normalize(n0 + n1);
        float dist = 1 / dot(miter_direction, n1);
        if (dist > 10) {
            // Switch to a miter joint
            miter_direction = normalize(n0 - n1);
            dist = 1 / dot(miter_direction, n1);
        }
        offset = miter_direction * dist;
    }
    return offset;
}

vec4 tr(vec2 point, vec2 offset) {
    return vec4(world_transform(point, offset, 2.0), 0.0, 1.0);
}

void main() {
    // all model coords; tr() then transforms to world
    vec2 p0 = gl_in[0].gl_Position.xy;
    vec2 p1 = gl_in[1].gl_Position.xy;
    vec2 p2 = gl_in[2].gl_Position.xy;
    vec2 p3 = gl_in[3].gl_Position.xy;

    vec2 direction = normalize(p2-p1);
    vec2 dir_side = vec2(-direction.y, direction.x);

    float g_distance1 = u_extend(1.0, 1.0);

    vec2 offset;

    offset = get_offset(p0, p1, p2);
    set_g_pervertex(1);
    g_distance = g_distance1;
    gl_Position = tr(p1, offset);
    EmitVertex();
    g_distance = -g_distance1;
    gl_Position = tr(p1, -offset);
    EmitVertex();

    offset = -get_offset(p3, p2, p1);
    set_g_pervertex(2);
    g_distance = g_distance1;
    gl_Position = tr(p2, offset);
    EmitVertex();
    g_distance = -g_distance1;
    gl_Position = tr(p2, -offset);
    EmitVertex();

    EndPrimitive();
}
