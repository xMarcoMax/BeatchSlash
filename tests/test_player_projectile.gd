@tool
extends "res://addons/godot_ai/testing/test_suite.gd"


func suite_name() -> String:
	return "player_projectile"


func test_launch_uses_world_transform_under_transformed_parent() -> void:
	if Engine.is_editor_hint():
		skip("Eseguire nel gioco tramite game_eval: Player e Global richiedono gli autoload runtime")
		return
	var root := Node2D.new()
	track(root)
	root.process_mode = Node.PROCESS_MODE_DISABLED
	var tree := Engine.get_main_loop() as SceneTree
	tree.root.add_child(root)
	var player = load("res://Characters/player.tscn").instantiate()
	root.add_child(player)
	player.owner = root
	player.position = Vector2(1011, -423)
	var ray: RayCast2D = player.ray_cast
	for parent_transform in [
		Transform2D.IDENTITY,
		Transform2D(0.0, Vector2(-392, 847)),
		Transform2D(0.4, Vector2(1.5, 0.75), 0.0, Vector2(-392, 847))
	]:
		root.transform = parent_transform
		player.shoot_sand(player.global_position + Vector2(400, 0))
		var ball: Area2D = root.get_child(root.get_child_count() - 1)
		assert_true(ball.global_transform.is_equal_approx(ray.global_transform),
			"Il proiettile deve nascere sul Player senza riapplicare la trasformazione del livello")
		assert_eq(ball.damage, player.damage, "Il danno del lancio deve restare invariato")
		var origin := ball.global_position
		var expected_step: Vector2 = ray.global_transform.x * ball.speed * 0.1
		ball._physics_process(0.1)
		assert_true(ball.global_position.is_equal_approx(origin + expected_step),
			"La traiettoria globale non deve dipendere dalla trasformazione del livello")
		ball.free()


func test_standalone_player_does_not_carry_released_projectile() -> void:
	if Engine.is_editor_hint():
		skip("Eseguire nella scena Player tramite game_eval")
		return
	var tree := Engine.get_main_loop() as SceneTree
	var player = tree.current_scene
	assert_true(player.is_in_group("player"), "La verifica richiede la scena Player avviata direttamente")
	if not player.is_in_group("player"):
		return
	var was_processing := player.is_physics_processing()
	player.set_physics_process(false)
	player.shoot_sand(player.global_position + Vector2(400, 0))
	var ball: Area2D = tree.get_nodes_in_group("sand_ball").back()
	ball.set_physics_process(false)
	var origin := ball.global_position
	var player_position: Vector2 = player.position
	player.position += Vector2(100, 60)
	assert_true(ball.get_parent() != player, "La palla rilasciata deve essere indipendente dal Player")
	assert_true(ball.global_position.is_equal_approx(origin),
		"Muovere il Player non deve trascinare una palla già lanciata")
	player.position = player_position
	ball.free()
	player.set_physics_process(was_processing)
