shader_type canvas_item;

// Barra a tubo di vetro con liquido colorato: usata da LiquidBar (moralità, fedeltà, salute delle nemiche).
// Tutte le misure sono in pixel del controllo.
uniform vec4 liquid_color : source_color = vec4(0.1, 0.55, 0.95, 1.0);
uniform vec4 outline_color : source_color = vec4(0.227, 0.078, 0.094, 1.0);
uniform float fill : hint_range(0.0, 1.0) = 1.0;
uniform vec2 bar_size = vec2(200.0, 24.0);
uniform float border = 2.0;

// Distanza con segno da un rettangolo con angoli arrotondati (negativa dentro)
float rounded_box(vec2 p, vec2 half_size, float r) {
	vec2 q = abs(p) - half_size + vec2(r);
	return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
}

void fragment() {
	vec2 px = UV * bar_size;
	vec2 p = px - bar_size * 0.5;
	float radius = bar_size.y * 0.5;
	float d = rounded_box(p, bar_size * 0.5, radius);
	float w = max(fwidth(d), 0.0001);
	float shape = clamp(0.5 - d / w, 0.0, 1.0);
	float inner = clamp(0.5 - (d + border) / w, 0.0, 1.0);

	// 0 in alto, 1 in basso dentro il tubo
	float t = clamp((px.y - border) / (bar_size.y - 2.0 * border), 0.0, 1.0);

	// Fronte del liquido, con una piccola onda che sparisce a tubo pieno o vuoto
	float span = bar_size.x - 2.0 * border;
	float calm = smoothstep(0.0, 0.06, fill) * smoothstep(0.0, 0.06, 1.0 - fill);
	float front = border + fill * span + sin(px.y * 0.55 + TIME * 3.0) * (bar_size.y * 0.05) * calm;
	float liquid = clamp(front - px.x + 0.5, 0.0, 1.0);

	// Liquido: chiaro in alto, scuro in basso, come un cilindro
	vec3 base = liquid_color.rgb;
	vec3 col = mix(mix(base, vec3(1.0), 0.35), base, smoothstep(0.05, 0.4, t));
	col = mix(col, base * 0.55, smoothstep(0.55, 1.0, t));
	// Bordo luminoso lungo il fronte
	col += 0.22 * (1.0 - smoothstep(0.0, bar_size.y * 0.12, front - px.x)) * calm;

	// Vetro vuoto: scuro e semitrasparente, con la stessa ombra verticale
	vec3 glass = mix(vec3(0.10, 0.05, 0.07), base * 0.45, mix(0.35, 0.15, t));

	vec3 inside = mix(glass, col, liquid);
	float inside_alpha = mix(0.65, 1.0, liquid);

	// Riflesso del tubo, una fascia chiara in alto e una sottile in basso
	float hx = smoothstep(radius * 0.5, radius * 1.4, px.x) * (1.0 - smoothstep(bar_size.x - radius * 1.4, bar_size.x - radius * 0.5, px.x));
	float gloss = smoothstep(0.10, 0.16, t) * (1.0 - smoothstep(0.26, 0.34, t)) * hx;
	float rim = smoothstep(0.80, 0.86, t) * (1.0 - smoothstep(0.88, 0.94, t)) * hx;
	inside = mix(inside, vec3(1.0), gloss * 0.55 + rim * 0.18);

	vec3 rgb = mix(outline_color.rgb, inside, inner);
	float a = shape * mix(1.0, inside_alpha, inner);
	COLOR = vec4(rgb, a);
}
