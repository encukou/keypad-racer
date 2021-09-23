#version 330

uniform sampler2D atlas_tex;
uniform vec4 viewport;
uniform vec4 projection_params;
//uniform float antialias;

in vec4 v_color;
in vec2 v_uv;

float median(float r, float g, float b) {
    return max(min(r, g), min(max(r, g), b));
}

void main() {
    vec4 sample = texture(atlas_tex, v_uv);
    float dist = 0.49 - median(sample.r, sample.g, sample.b);
    float aa = projection_params.z / viewport.w * 8;
    if (dist < 0) {
        gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);
        return;
    }
    if (dist < aa) {
        gl_FragColor = vec4(1.0, 1.0, 1.0, 1-dist/aa);
    } else {
        discard;
    }
}
