@tool
extends "res://addons/godot_ai/testing/test_suite.gd"


func suite_name() -> String:
	return "enemy_spawn"


func test_spawn_matches_sampled_world_point_in_each_area() -> void:
	if Engine.is_editor_hint():
		skip("Eseguire nel livello tramite game_eval: lo spawn richiede gli autoload runtime")
		return
	var tree := Engine.get_main_loop() as SceneTree
	var level = tree.current_scene
	assert_true(level.has_method("spawn_enemy"), "La verifica richiede il livello di gioco")
	if not level.has_method("spawn_enemy"):
		return
	var was_processing := level.is_processing()
	level.set_process(false)
	var original_areas: Array = level.spawn_area.spawn_areas
	var original_count = level.spawn_number
	for area: CollisionShape2D in original_areas:
		level.spawn_area.spawn_areas = [area]
		for sample in range(8):
			seed(4671 + sample)
			var expected: Vector2 = level.spawn_area.calculate_spawn_point()
			seed(4671 + sample)
			level.spawn_number = 1
			level.spawn_enemy()
			var enemy: CharacterBody2D = level.get_child(level.get_child_count() - 1)
			assert_true(enemy.global_position.is_equal_approx(expected),
				"La nemica deve nascere sul punto globale estratto da %s" % area.name)
			assert_true(Rect2(-area.shape.size / 2.0, area.shape.size).has_point(area.to_local(enemy.global_position)),
				"La nemica deve nascere dentro %s" % area.name)
			assert_eq(level.spawn_number, 0, "Ogni spawn deve consumare una sola nemica dell'ondata")
			enemy.free()
	level.spawn_area.spawn_areas = original_areas
	level.spawn_number = original_count
	level.set_process(was_processing)
