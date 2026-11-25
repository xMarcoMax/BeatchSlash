class_name EnemyPalette
extends RefCounted

#Colour variants of the enemies: each entry is a name and three tones (dark, medium, light) that replace the
#purple hair or the green costume of the atlas in enemy_body.gdshader. Any enemy class drawn with the same
#atlas tones gets the same variants; the first entry of each list is the colour painted in the atlas.
const HAIR = [
	{"name": "viola", "tones": [Color("4b2a78"), Color("7043a1"), Color("a97fd9")]},
	{"name": "nero", "tones": [Color("1a1620"), Color("2f2a3d"), Color("5a5370")]},
	{"name": "castano", "tones": [Color("4a2a1a"), Color("7a4528"), Color("b0723f")]},
	{"name": "biondo", "tones": [Color("b8863a"), Color("e0b44f"), Color("f7dc8a")]},
	{"name": "rosa", "tones": [Color("a02d6a"), Color("d95a98"), Color("f7a1c8")]},
	{"name": "azzurro", "tones": [Color("1f5f8a"), Color("2f90c0"), Color("7fd0ea")]},
	{"name": "acqua", "tones": [Color("1d6a62"), Color("2fa093"), Color("7fd9c6")]},
]
#No pink, orange, yellow or other skin-like colours: the bikini must stand out from the skin
const COSTUME = [
	{"name": "verde", "tones": [Color("25805a"), Color("3db57d"), Color("8de0b4")]},
	{"name": "blu", "tones": [Color("2a4fa0"), Color("3f7fd9"), Color("8fbff5")]},
	{"name": "nero", "tones": [Color("2a2630"), Color("4a4658"), Color("7a7690")]},
	{"name": "bianco", "tones": [Color("a9a4b8"), Color("e0dce8"), Color("fffaf0")]},
	{"name": "rosso", "tones": [Color("7a1424"), Color("b8202f"), Color("e8493f")]},
	{"name": "viola", "tones": [Color("4a2a8a"), Color("7a50c8"), Color("b090f0")]},
]


#The colours painted in the atlas: purple hair and green bikini
static func original() -> Dictionary:
	return {"hair": HAIR[0], "costume": COSTUME[0]}


#Random hair and costume for one enemy; never the same colour name on both (violet on violet, black on black)
static func pick() -> Dictionary:
	var hair = HAIR.pick_random()
	var costume = COSTUME.pick_random()
	while costume.name == hair.name:
		costume = COSTUME.pick_random()
	return {"hair": hair, "costume": costume}


static func apply(material: ShaderMaterial, look: Dictionary) -> void:
	material.set_shader_parameter("hair_to", PackedColorArray(look.hair.tones))
	material.set_shader_parameter("costume_to", PackedColorArray(look.costume.tones))
