#version 150 core

uniform vec2 resolution;
uniform float antialias;

in float v_thickness[];
in vec4 v_color[];
out float g_thickness;
out float g_distance;
out vec4 g_color;

layout(lines) in;
layout(triangle_strip, max_vertices = 4) out;

void set_g_pervertex(int n) {
    g_thickness = v_thickness[n];
    g_color = v_color[n];
}

void main()
{
    vec2 p0 = gl_in[0].gl_Position.xy;
    vec2 p1 = gl_in[1].gl_Position.xy;

    float half_quad_thickness = v_thickness[0]/2.0 + antialias;

    vec2 direction = normalize(p1-p0);
    vec2 dir_side = vec2(-direction.y, direction.x);

    vec2 to_side = dir_side * half_quad_thickness / resolution;
    set_g_pervertex(0);
    g_distance = half_quad_thickness;
    gl_Position = vec4(p0 + to_side, 0.0, 1.0);
    EmitVertex();
    g_distance = -half_quad_thickness;
    gl_Position = vec4(p0 - to_side, 0.0, 1.0);
    EmitVertex();

    to_side = dir_side * half_quad_thickness / resolution;
    set_g_pervertex(1);
    g_distance = half_quad_thickness;
    gl_Position = vec4(p1 + to_side, 0.0, 1.0);
    EmitVertex();
    g_distance = -half_quad_thickness;
    gl_Position = vec4(p1 - to_side, 0.0, 1.0);
    EmitVertex();

    EndPrimitive();
}
