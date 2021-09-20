#version 330

uniform vec2 pan;
uniform float zoom;
uniform vec2 resolution;
uniform float antialias;

vec2 transform_car (vec2 pos, vec2 uv, float orientation) {
    float wrot = 0.005;
    float swr = sin(wrot);
    float cwr = cos(wrot);
    mat2 rotw = mat2(
        cwr, swr,
        -swr, cwr
    );
    float so = sin(orientation);
    float co = cos(orientation);
    mat2 rot = mat2(
        co, so,
        -so, co
    );
    vec2 zoomat = vec2(
        1.0/zoom*resolution.y/resolution.x,
        1.0/zoom
    );
    return rotw * ((uv * rot + pos - pan) * zoomat + (uv * antialias * rot / resolution));
}
