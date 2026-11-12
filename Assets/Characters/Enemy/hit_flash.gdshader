shader_type canvas_item;

// Lampo bianco quando la nemica è colpita. Solo i pixel opachi: l'ombra (semitrasparente) resta com'è.
uniform float flash : hint_range(0.0, 1.0) = 0.0;

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	if (c.a > 0.9) {
		c.rgb = mix(c.rgb, vec3(1.0), flash);
	}
	COLOR = c;
}
