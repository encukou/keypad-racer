#version 330
#include world_project.inc

uniform vec2 pos;

in vec2 uv;
in vec4 plane;
in vec4 atlas;
in vec2 position;

out vec2 v_uv;
out vec2 v_world;

void main() {
    vec2 aspect = vec2(viewport.w/viewport.z, 1.0);
    gl_Position = vec4(
        world_transform(position + pos, (plane.xy + plane.zw * uv), 0.0),
        0.0, 1.0
    );
    v_uv = atlas.xy + uv * atlas.zw;
    v_uv.y = 1-v_uv.y;
    v_world = position;
}
