#version 330

uniform vec4 projection_params;
uniform vec2 resolution;
uniform float antialias;

vec2 transform_car (vec2 pos, vec2 uv, float orientation) {
    float wrot = projection_params.w;
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
    float zoom = projection_params.z;
    vec2 zoomat = vec2(
        1.0/zoom*resolution.y/resolution.x,
        1.0/zoom
    );
    return rotw * ((uv * rot + pos - projection_params.xy) * zoomat
        + (uv * antialias * rot / resolution));
}
