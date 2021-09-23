#version 330
#include world_project.inc

uniform vec2 pos;
uniform vec3 top_pos;

in vec2 uv;
in vec3 pad;
in vec3 feature;
in ivec2 decal;

out vec2 v_uv;
out vec3 v_feature;
flat out ivec2 v_decal;

void main() {
    vec2 position = mix(
        pos + vec2(0, pad.z * 2.5),
        top_pos.xy,
        pad.z * top_pos.z
    ) + pad.xy;
    gl_Position = vec4(transform_car(position, uv/2, 0), 0.0, 1.0);
    v_uv = uv;
    v_feature = feature;
    v_decal = decal;
}
