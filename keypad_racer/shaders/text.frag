#version 330

uniform sampler2D atlas_tex;
uniform vec4 viewport;
uniform vec4 projection_params;
//uniform float antialias;

in vec4 v_color;
in vec2 v_uv;
in vec2 v_world;

float median(float r, float g, float b) {
    return max(min(r, g), min(max(r, g), b));
}

void main() {
    vec4 sample = texture(atlas_tex, v_uv);
    float dist = 0.49 - median(sample.r, sample.g, sample.b);
    float aa = projection_params.z / viewport.w * 8;
    vec3 color = vec3(abs(v_world.x)/3, pow(v_world.x, 2)/2, pow(v_world.x, 2));
    color = vec3(0.6, 0.7, 0.8);
    vec3 outline = vec3(1.0);
    if (dist < -aa) {
        gl_FragColor = vec4(color, 1.0);
        return;
    }
    if (dist < 0) {
        gl_FragColor = vec4(mix(color, outline, dist/aa+1), 1.0);
        return;
    }
    if (dist < aa) {
        gl_FragColor = vec4(outline, 1-dist/aa);
    } else {
        discard;
    }
}
