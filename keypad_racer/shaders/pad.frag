#version 330
#include world_project.inc

uniform vec3 color;
uniform float button_size;
uniform mat4x3 m_blocked;
uniform sampler2D atlas_tex;

in vec2 v_uv;
flat in vec4 v_feature;
in vec2 v_decal;
flat in ivec4 v_pad;
flat in vec4 v_decal_limit;

float csg_union(float d1, float d2) {
    return min(d1,d2);
}
float csg_difference(float d1, float d2) {
    return max(d1, -d2);
}
float csg_intersection(float d1, float d2) {
    return max(d1,d2);
}
float csg_exclusion(float d1, float d2) {
    return min(max(d1,-d2), max(-d1,d2));
}

float SDF_box(vec2 p, vec2 size) {
     vec2 d = abs(p) - size;
     return min(max(d.x,d.y),0.0) + length(max(d,0.0));
}

float SDF_sharpcornered_box(vec2 p, vec2 size) {
    return max(abs(p.x)-size.x, abs(p.y)-size.y);
}

float SDF_sharpcornered_turned_box(vec2 p, float size) {
    return (abs(p.x) + abs(p.y))/sqrt(2) - size;
}

float median(float r, float g, float b) {
    return max(min(r, g), min(max(r, g), b));
}

void main() {
    float size = v_feature.x;
    float corner_r = size * v_feature.y;
    float sdf =
        SDF_box(v_uv, vec2(size - corner_r) * button_size)
        - corner_r * button_size;
    /*
    if (v_pad.z == 0) {
        vec2 box = v_pad.xy;
        if (v_pad.x != 0 && v_pad.y != 0) {
            sdf = csg_union(
                sdf,
                SDF_sharpcornered_box(
                    v_uv - box/2*size*button_size,
                    v_feature.xx/2*button_size));
        } else {
            sdf = csg_union(
                sdf,
                SDF_sharpcornered_turned_box(
                    v_uv - box*size*.76*button_size,
                    size*.6*button_size));
        }
    } else if (v_feature.z != 0) {
        float s = sqrt(2.0);
        float t = button_size*2;
        sdf = csg_difference(
            length(v_uv) - size*min(t, 1),
            length(v_uv) - (t*(1-t))*size);
        t = button_size*2 - 1;
        sdf = csg_union(sdf, csg_intersection(
            abs(v_uv.x + v_uv.y) - size/3*t,
            max(
                abs(v_uv.x - v_uv.y) - size*2.5,
                v_uv.y - v_uv.x + size*0.5)));
    } else if (v_feature.w != 0) {
        float t = button_size*2;
        sdf = csg_difference(
            length(v_uv) - size*min(t, 1),
            length(v_uv) - (t*(1-t))*size);
        t = max(button_size * 2 - 1, 0);
        sdf = csg_union(sdf, csg_difference(
            csg_difference(
                length(v_uv) - size*1.5,
                length(v_uv) - size*1.25),
            csg_union(
                sdf,
                csg_exclusion(v_uv.x+v_uv.y, v_uv.x-v_uv.y)-(1-t)*4/5)));
    }
    //*/
    float aa = gridlines_per_px() * 4;
    vec4 sample = texture(atlas_tex, v_decal);
    if (v_decal.x < v_decal_limit.x) sample = vec4(-1.0);
    if (v_decal.x > (v_decal_limit.x+v_decal_limit.z)) sample = vec4(-1.0);
    if (v_decal.y > v_decal_limit.y) sample = vec4(-1.0);
    float dist = (0.45 - median(sample.r, sample.g, sample.b))/2;
    vec3 btncolor = color;
    vec3 decalcolor = vec3(1.0);
    if (0.2126 * btncolor.r + 0.7152 * btncolor.g + 0.0722 * btncolor.g > 0.5) {
        decalcolor = vec3(0.0);
    }
    if (m_blocked[v_pad.x+1][v_pad.y+1] > 0.5) {
        btncolor = vec3(0.4);
    }
    if (dist < -aa) {
        btncolor = decalcolor;
    }
    if (dist < 0) {
        btncolor = mix(btncolor, decalcolor, -dist/aa);
    }

    if (sdf < -aa) {
        gl_FragColor = vec4(btncolor, 1.0);
        return;
    }
    vec3 bordercolor = mix(btncolor, vec3(1.0),
        mix(
            length(v_pad.xy + v_uv)/3.5,
            1.0,
            smoothstep(0, 20, 1/gridlines_per_px())));
    if (sdf < 0) {
        gl_FragColor = vec4(mix(btncolor, bordercolor, 1+(sdf/aa)), 1.0);
        return;
    }
    if (sdf < aa) {
        gl_FragColor = vec4(bordercolor, 1-(sdf/aa));
    } else {
        discard;
    }
}
