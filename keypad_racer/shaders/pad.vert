#version 330
#include world_project.inc

uniform vec2 pos;
uniform vec3 top_pos;
uniform int skip;

in vec2 uv;
in ivec4 pad;
in vec4 feature;
in ivec2 decal;

out vec2 v_uv;
flat out vec4 v_feature;
flat out ivec2 v_decal;
flat out ivec4 v_pad;

void main() {
    vec2 position = mix(
        pos + vec2(0, pad.z * 2.5),
        top_pos.xy,
        pad.z * top_pos.z
    ) + pad.xy;
    gl_Position = vec4(transform_car(position, uv, 0), 0.0, 1.0);
    if (skip == pad.w) gl_Position = vec4(0.0);
    v_uv = uv*2;
    v_feature = feature;
    v_decal = decal;
    v_pad = pad;
}
