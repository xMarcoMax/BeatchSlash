@tool
extends "res://addons/godot_ai/testing/test_suite.gd"


func suite_name() -> String:
	return "enemy_palette"


func test_every_colour_has_three_tones_and_a_name() -> void:
	for list in [EnemyPalette.HAIR, EnemyPalette.COSTUME]:
		var names = []
		for entry in list:
			assert_eq(entry.tones.size(), 3)
			assert_false(names.has(entry.name), "nome ripetuto: " + entry.name)
			names.append(entry.name)


func test_pick_never_repeats_the_same_colour_on_hair_and_costume() -> void:
	for i in 200:
		var look = EnemyPalette.pick()
		assert_true(look.hair.name != look.costume.name, "stesso colore: " + look.hair.name)


func test_apply_sets_both_shader_parameters() -> void:
	var material = ShaderMaterial.new()
	var look = {"hair": EnemyPalette.HAIR[1], "costume": EnemyPalette.COSTUME[1]}
	EnemyPalette.apply(material, look)
	assert_eq(material.get_shader_parameter("hair_to").size(), 3)
	assert_eq(material.get_shader_parameter("costume_to")[2], look.costume.tones[2])


func test_original_is_the_atlas_colours() -> void:
	var look = EnemyPalette.original()
	assert_eq(look.hair.name, "viola")
	assert_eq(look.costume.name, "verde")
	assert_eq(look.costume.tones[1], Color("3db57d"))
