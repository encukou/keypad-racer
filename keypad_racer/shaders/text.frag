#version 330
#include world_project.inc

uniform sampler2D atlas_tex;
uniform vec4 outline_color;
uniform vec4 body_color;

in vec4 v_color;
in vec2 v_uv;
in vec2 v_world;

float median(float r, float g, float b) {
    return max(min(r, g), min(max(r, g), b));
}

void main() {
    vec4 sample = texture(atlas_tex, v_uv);
    float dist = 0.49 - median(sample.r, sample.g, sample.b);
    float aa = gridlines_per_px() * 6;
    //vec3 color = vec3(abs(v_world.x)/3, pow(v_world.x, 2)/2, pow(v_world.x, 2));
    vec3 outline = vec3(1.0);
    dist -= aa;
    if (dist < -aa) {
        gl_FragColor = body_color;
        return;
    }
    if (dist < 0) {
        gl_FragColor = mix(body_color, outline_color, dist/aa+1);
        return;
    }
    if (dist < aa) {
        gl_FragColor = vec4(outline_color.rgb, outline_color.a * (1-dist/aa));
    } else {
        discard;
    }
}
