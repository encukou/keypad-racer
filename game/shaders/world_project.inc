#version 330

uniform vec2 pan;
uniform float zoom;
uniform vec2 resolution;

vec2 transform_car (vec2 pos, vec2 uv, float orientation) {
    float so = sin(orientation);
    float co = cos(orientation);
    mat2 rot = mat2(
        co, so,
        -so, co
    );
    vec2 zoomat = vec2(
        1.0/zoom*resolution.y,
        1.0/zoom*resolution.x
    );
    vec2 uvw = vec2(uv.x * (0.26 - uv.y * 0.04), uv.y * 0.45) * rot + pos;
    return uvw * zoomat + pan;
}
