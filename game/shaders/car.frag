#version 330

varying vec4 v_color;

varying vec2 v_p0, v_p1, v_p;

void main() {
    gl_FragColor = v_color;
}
