#version 150 core

uniform vec4 viewport;
uniform float antialias;
uniform float zoom;

in float v_thickness[];
in float v_t[];
out float g_thickness;
out float g_distance;
out float g_t;

layout(lines_adjacency) in;
layout(triangle_strip, max_vertices = 4) out;

void set_g_pervertex(int n) {
    g_thickness = v_thickness[n];
    g_t = v_t[n];
}

vec2 get_offset(vec2 p0, vec2 p1, vec2 p2, float z, float half_quad_thickness) {
    vec2 direction = normalize(p2 - p1);
    vec2 dir_side = vec2(-direction.y, direction.x);

    vec2 offset = dir_side * half_quad_thickness / viewport.zw;
    if (p0 != p1) {
        vec2 t0 = normalize((p1 - p0)/viewport.wz);
        vec2 t1 = normalize((p2 - p1)/viewport.wz);
        vec2 n0 = vec2(-t0.y, t0.x);
        vec2 n1 = vec2(-t1.y, t1.x);
        vec2 miter_direction = normalize(n0 + n1);
        float dist = 1 / dot(miter_direction, n1);
        if (dist > 6) {
            // Switch to a miter joint
            miter_direction = normalize(n0 - n1);
            dist = 1 / dot(miter_direction, n1);
        }
        offset = miter_direction * dist * half_quad_thickness / viewport.zw;
    }
    return offset;
}

void main()
{
    vec2 p0 = gl_in[0].gl_Position.xy;
    vec2 p1 = gl_in[1].gl_Position.xy;
    vec2 p2 = gl_in[2].gl_Position.xy;
    vec2 p3 = gl_in[3].gl_Position.xy;

    vec2 direction = normalize(p2-p1);
    vec2 dir_side = vec2(-direction.y, direction.x);

    float hqt_adjust = antialias/viewport.w / 2.0;

    float half_quad_thickness = v_thickness[1] / 2.0 + hqt_adjust;
    vec2 offset = get_offset(p0, p1, p2, 1, half_quad_thickness);

    set_g_pervertex(1);
    g_distance = 1;
    gl_Position = vec4(p1 + offset, 0.0, 1.0);
    EmitVertex();
    g_distance = -1;
    gl_Position = vec4(p1 - offset, 0.0, 1.0);
    EmitVertex();

    half_quad_thickness = v_thickness[2] / 2.0 + hqt_adjust;
    offset = dir_side * half_quad_thickness / viewport.zw;
    offset = -get_offset(p3, p2, p1, -1, half_quad_thickness);
    set_g_pervertex(2);
    g_distance = 1;
    gl_Position = vec4(p2 + offset, 0.0, 1.0);
    EmitVertex();
    g_distance = -1;
    gl_Position = vec4(p2 - offset, 0.0, 1.0);
    EmitVertex();

    EndPrimitive();
}
