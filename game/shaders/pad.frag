#version 330

uniform vec2 resolution;

in vec2 v_uv;
in vec3 v_feature;
flat in ivec2 v_decal;

void main() {
    gl_FragColor = vec4(v_feature.x, v_decal.x, length(v_uv), 0.5);
}
