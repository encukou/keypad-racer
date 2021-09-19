#version 150 core

in vec3 v_color[];
out vec3 g_color;

in vec2 v_p0[];
in vec2 v_p1[];
in vec2 v_p[];
out vec2 g_p0;
out vec2 g_p1;
out vec2 g_p;

in float v_alpha[];
in float v_thickness[];
out float g_alpha;
out float g_thickness;

layout(triangles) in;
layout(triangle_strip, max_vertices = 4) out;

void main()
{
    g_color = v_color[0];
    g_p0 = v_p0[0];
    g_p1 = v_p1[0];
    g_p = v_p[0];
    g_alpha = v_alpha[0];
    g_thickness = v_thickness[0];
    gl_Position = gl_in[0].gl_Position;
    EmitVertex();

    g_color = v_color[1];
    g_p0 = v_p0[1];
    g_p1 = v_p1[1];
    g_p = v_p[1];
    g_thickness = v_thickness[1];
    gl_Position = gl_in[1].gl_Position;
    EmitVertex();

    g_color = v_color[2];
    g_p0 = v_p0[2];
    g_p1 = v_p1[2];
    g_p = v_p[2];
    g_thickness = v_thickness[2];
    gl_Position = gl_in[2].gl_Position;
    EmitVertex();

    EndPrimitive();
}
