shader_type canvas_item;

// Gli atlanti hanno corpi opachi e ombre a alpha97/255.
uniform bool shadow_only = false;

void fragment() {
	bool shadow_pixel = texture(TEXTURE, UV).a < 0.5;
	if (shadow_pixel != shadow_only) {
		discard;
	}
}
