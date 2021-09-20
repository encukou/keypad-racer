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
    return (uv * rot + pos - pan) * zoomat;
}
