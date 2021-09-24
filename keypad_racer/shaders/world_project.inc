#version 330

uniform vec4 projection_params;
uniform vec4 viewport;

/* projection_params are:
 * xy -- pan
 * zw -- scale
 */

mat2 rotate(float angle) {
    float s = sin(angle);
    float c = cos(angle);
    return mat2(c, s, -s, c);
}

float gridlines_per_px() {
    return projection_params.z / viewport.z;
}

vec2 uv_extend(vec2 uv, float aa) {
    return uv + normalize(uv) * aa * gridlines_per_px();
}

float u_extend(float u, float aa) {
    return u + aa * gridlines_per_px();
}

vec2 world_transform(vec2 pos, vec2 uv, float aa) {
    vec2 pan = projection_params.xy;
    vec2 scale = projection_params.zw;
    return (
        pos - pan + uv_extend(uv, aa)
    ) / scale;
}
