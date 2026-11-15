@tool
extends "res://addons/godot_ai/testing/test_suite.gd"


func suite_name() -> String:
	return "ground_shadows"


func test_ground_layers_are_below_characters() -> void:
	var level_scene := ResourceLoader.load("res://Scenes/level.tscn", "", ResourceLoader.CACHE_MODE_IGNORE_DEEP) as PackedScene
	var level: Node = level_scene.instantiate()
	track(level)
	var shop_scene := ResourceLoader.load("res://Objects/upgrades.tscn", "", ResourceLoader.CACHE_MODE_IGNORE_DEEP) as PackedScene
	var shop: Node = shop_scene.instantiate()
	track(shop)
	var world: CanvasItem = level.get_node("World")
	var shop_body: CanvasItem = shop
	var shop_shadow: CanvasItem = shop.get_node("Shadow")
	assert_eq(world.z_index, -2, "La mappa deve stare sotto le ombre")
	assert_eq(shop_shadow.z_index, -1, "L'ombra del negozio deve stare sul terreno")
	assert_false(shop_shadow.z_as_relative, "L'ombra del negozio deve avere Z assoluto")
	assert_eq(shop_body.z_index, 0, "Il negozio deve restare sul livello dei corpi")
	for scene_path in ["res://Characters/player.tscn", "res://Characters/enemy.tscn", "res://Characters/boyfriend.tscn"]:
		var actor_scene := ResourceLoader.load(scene_path, "", ResourceLoader.CACHE_MODE_IGNORE_DEEP) as PackedScene
		var actor: CanvasItem = actor_scene.instantiate()
		track(actor)
		assert_eq(actor.z_index, 0, "%s deve restare sul livello dei corpi" % scene_path)


func test_animated_character_shadow_tracks_direction_and_frame() -> void:
	for spec in [
		["res://Characters/player.tscn", &"idle_down", &"walk_up_right"],
		["res://Characters/enemy.tscn", &"idle_down", &"flirt_up_right"],
		["res://Characters/boyfriend.tscn", &"idle_down", &"admire_up_right"]
	]:
		var actor := _make_actor(spec[0])
		var sprite: AnimatedSprite2D = actor.get_node("AnimatedSprite2D")
		var shadow := sprite.get_node_or_null("GroundShadow") as Sprite2D
		assert_true(shadow != null, "%s deve avere un'ombra separata" % spec[0])
		if shadow == null:
			return
		assert_eq(shadow.z_index, -1, "L'ombra deve stare sotto ogni corpo")
		assert_false(shadow.z_as_relative, "La Z dell'ombra deve essere assoluta")
		assert_true(shadow.material is ShaderMaterial, "L'ombra deve usare la maschera alpha")
		if shadow.material is ShaderMaterial:
			assert_eq((shadow.material as ShaderMaterial).get_shader_parameter("shadow_only"), true,
				"Il materiale dell'ombra deve mostrare solo i pixel semitrasparenti")
		assert_true(sprite.material is ShaderMaterial, "Il corpo deve escludere l'ombra incorporata")
		for animation in [spec[1], spec[2]]:
			assert_true(sprite.sprite_frames.has_animation(animation), "Animazione mancante: %s" % animation)
			if not sprite.sprite_frames.has_animation(animation):
				return
			sprite.animation = animation
			sprite.frame = 2
			var expected: Texture2D = sprite.sprite_frames.get_frame_texture(animation, 2)
			assert_eq(shadow.texture, expected, "Ombra non sincronizzata con %s/frame 2" % animation)
		sprite.offset = Vector2(2, -5)
		sprite.centered = false
		sprite.flip_h = true
		sprite.flip_v = true
		shadow.call("_process", 0.0)
		assert_eq(shadow.offset, sprite.offset, "Offset dell'ombra diverso dal corpo")
		assert_eq(shadow.centered, sprite.centered, "Centratura dell'ombra diversa dal corpo")
		assert_eq(shadow.flip_h, sprite.flip_h, "Flip orizzontale dell'ombra errato")
		assert_eq(shadow.flip_v, sprite.flip_v, "Flip verticale dell'ombra errato")
		sprite.hide()
		assert_false(shadow.is_visible_in_tree(), "Nascondendo il corpo non deve restare un'ombra fantasma")


func test_moving_throw_shadow_tracks_atlas_and_visibility() -> void:
	var actor := _make_actor("res://Characters/player.tscn")
	var sprite: Sprite2D = actor.get_node("MovingThrow")
	var shadow := sprite.get_node_or_null("GroundShadow") as Sprite2D
	assert_true(shadow != null, "Il lancio in movimento deve avere un'ombra separata")
	if shadow == null:
		return
	for atlas_path in ["res://Assets/Characters/Player/player_moving_throw.png",
		"res://Assets/Characters/Player/player_diagonals_moving_throw.png"]:
		sprite.texture = load(atlas_path)
		for frame in [0, 7, 256, 511]:
			sprite.frame = frame
			assert_eq(shadow.texture, sprite.texture, "L'ombra deve usare l'atlante corrente")
			assert_eq(shadow.frame, frame, "L'ombra deve seguire il frame %d" % frame)
			assert_eq(shadow.hframes, sprite.hframes, "Numero di colonne dell'ombra errato")
			assert_eq(shadow.vframes, sprite.vframes, "Numero di righe dell'ombra errato")
	sprite.offset = Vector2(3, -4)
	sprite.centered = false
	sprite.flip_h = true
	sprite.flip_v = true
	sprite.region_enabled = true
	sprite.region_rect = Rect2(0, 0, 192, 384)
	sprite.region_filter_clip_enabled = true
	shadow.call("_process", 0.0)
	assert_eq(shadow.offset, sprite.offset, "Offset del lancio non sincronizzato")
	assert_eq(shadow.centered, sprite.centered, "Centratura del lancio non sincronizzata")
	assert_eq(shadow.flip_h, sprite.flip_h, "Flip orizzontale del lancio non sincronizzato")
	assert_eq(shadow.flip_v, sprite.flip_v, "Flip verticale del lancio non sincronizzato")
	assert_eq(shadow.region_enabled, sprite.region_enabled, "Regione del lancio non sincronizzata")
	assert_eq(shadow.region_rect, sprite.region_rect, "Rettangolo della regione non sincronizzato")
	assert_eq(shadow.region_filter_clip_enabled, sprite.region_filter_clip_enabled,
		"Filtro della regione non sincronizzato")
	sprite.hide()
	assert_false(shadow.is_visible_in_tree(), "Il lancio nascosto non deve lasciare un'ombra")


func _make_actor(scene_path: String) -> Node:
	var actor_scene := ResourceLoader.load(scene_path, "", ResourceLoader.CACHE_MODE_IGNORE_DEEP) as PackedScene
	var actor: Node = actor_scene.instantiate()
	track(actor)
	actor.set_script(null)
	_remove_groups(actor)
	var tree := Engine.get_main_loop() as SceneTree
	tree.root.add_child(actor)
	return actor


func _remove_groups(node: Node) -> void:
	for group in node.get_groups():
		node.remove_from_group(group)
	for child in node.get_children():
		_remove_groups(child)
