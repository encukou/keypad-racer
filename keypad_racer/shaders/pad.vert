#version 330
#include world_project.inc

uniform vec2 pos;
uniform vec3 top_pos;
uniform int skip;
uniform float button_size;
uniform mat4x3 m_blocked;

in vec2 uv;
in ivec4 pad;
in vec4 feature;
in vec4 decal;
in vec4 decal_size;

out vec2 v_uv;
flat out vec4 v_feature;
out vec2 v_decal;
flat out vec4 v_decal_limit;
flat out ivec4 v_pad;

void main() {
    vec2 position = mix(
        pos + vec2(0, pad.z * 2.5),
        top_pos.xy,
        pad.z * top_pos.z
    ) + pad.xy;
    gl_Position = vec4(world_transform(position, uv/2, 4.0), 0.0, 1.0);
    if (m_blocked[pad.x+1][pad.y+1] < -0.5) {
        gl_Position = vec4(0.0);
    }
    v_uv = uv_extend(uv, 4.0);
    v_feature = feature;
    vec2 duv = uv;
    duv.x *= (decal_size.z)/decal_size.y;
    duv *= decal_size.x;
    duv = duv / 2 / button_size / v_feature.x + 0.5;
    if (decal_size.y > 0) {
        v_decal = decal.xy + decal.zw * duv + button_size*0.001;
    } else {
        v_decal = decal.xy + decal.zw * duv;
    }
    v_decal.y = 1-v_decal.y;
    v_decal_limit = decal;
    v_decal_limit.y = 1-decal.y;
    v_pad = pad;
}
