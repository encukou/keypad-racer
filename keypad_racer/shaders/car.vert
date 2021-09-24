#version 330
#include world_project.inc

in vec2 uv;
in vec4 pos;
in vec4 color;
in vec2 orientation;
in float pos_t;

out float v_thickness;
out vec4 v_color;
out vec2 v_uv;

void main() {
    float aa = 1.0;
    vec2 carpos = mix(pos.xy, pos.zw, 1-pos_t);
    float carorient = mix(orientation.x, orientation.y, clamp(0.2-pos_t, 0, 1));
    gl_Position = vec4(
        world_transform(carpos, rotate(carorient) * uv/2, aa),
        0.0, 1.0
    );
    v_color = color;
    v_uv = uv_extend(uv, aa);
}
