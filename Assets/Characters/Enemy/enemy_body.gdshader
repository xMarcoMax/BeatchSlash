shader_type canvas_item;

// Corpo della nemica: ricolora capelli e costume e dà il lampo del colpo.
// L'ombra semitrasparente viene disegnata dal nodo GroundShadow.
uniform float flash : hint_range(0.0, 1.0) = 0.0;
// Colori di arrivo dei tre toni (scuro, medio, chiaro); vedi EnemyPalette.
uniform vec3 hair_to[3] : source_color;
uniform vec3 costume_to[3] : source_color;

// Toni dell'atlante da sostituire. Tolleranza: i PNG hanno toni sbagliati di ±1/255.
const vec3 HAIR_FROM[3] = vec3[3](vec3(0.294, 0.165, 0.471), vec3(0.439, 0.263, 0.631), vec3(0.663, 0.498, 0.851));
const vec3 COSTUME_FROM[3] = vec3[3](vec3(0.145, 0.502, 0.353), vec3(0.239, 0.710, 0.490), vec3(0.553, 0.878, 0.706));
const float TOLERANCE = 0.05;

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	if (c.a < 0.5) {
		discard;
	}
	for (int i = 0; i < 3; i++) {
		if (distance(c.rgb, HAIR_FROM[i]) < TOLERANCE) {
			c.rgb = hair_to[i];
			break;
		}
		if (distance(c.rgb, COSTUME_FROM[i]) < TOLERANCE) {
			c.rgb = costume_to[i];
			break;
		}
	}
	if (c.a > 0.9) {
		c.rgb = mix(c.rgb, vec3(1.0), flash);
	}
	COLOR = c;
}
