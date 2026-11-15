shader_type canvas_item;

// Lampo sul corpo; l'ombra semitrasparente viene disegnata dal nodo GroundShadow.
uniform float flash : hint_range(0.0, 1.0) = 0.0;

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	if (c.a < 0.5) {
		discard;
	}
	if (c.a > 0.9) {
		c.rgb = mix(c.rgb, vec3(1.0), flash);
	}
	COLOR = c;
}
