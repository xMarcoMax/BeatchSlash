@tool
extends "res://addons/godot_ai/testing/test_suite.gd"


func suite_name() -> String:
	return "enemy_frames"


func test_enemy_scene_atlas_regions() -> void:
	var scene: PackedScene = load("res://Characters/enemy.tscn")
	assert(scene != null, "La scena della nemica non si carica")
	# Usare il riferimento della scena: il file separato può essere corretto mentre la cache è vecchia.
	var actor: Node = scene.instantiate()
	var sprite: AnimatedSprite2D = actor.get_node("AnimatedSprite2D")
	var frames: SpriteFrames = sprite.sprite_frames
	var errors: PackedStringArray = []
	if sprite.scale != Vector2(4, 4):
		errors.append("Scala dello sprite diversa da 4")
	if sprite.offset != Vector2(0, -3):
		errors.append("Offset dello sprite errato")
	if sprite.texture_filter != CanvasItem.TEXTURE_FILTER_NEAREST:
		errors.append("Filtro dello sprite diverso da nearest")
	if frames == null:
		errors.append("SpriteFrames mancante nella scena")
	else:
		if frames.get_animation_names().size() != 32:
			errors.append("La scena deve avere 32 animazioni")
		var disk: SpriteFrames = ResourceLoader.load("res://Assets/Characters/Enemy/enemy_frames.tres", "SpriteFrames", ResourceLoader.CACHE_MODE_IGNORE_DEEP)
		var groups = [["walk", 8, 8.0, true], ["flirt", 12, 8.0, true],
			["idle", 6, 5.0, true], ["dead", 8, 12.0, false]]
		var directions = ["up", "down", "right", "left", "up_right", "up_left", "down_right", "down_left"]
		for group_index in range(groups.size()):
			var group: Array = groups[group_index]
			for direction_index in range(directions.size()):
				var animation: StringName = StringName("%s_%s" % [group[0], directions[direction_index]])
				if not frames.has_animation(animation):
					errors.append("Animazione mancante: %s" % animation)
					continue
				var count: int = group[1]
				if frames.get_frame_count(animation) != count:
					errors.append("Numero di frame errato: %s" % animation)
				if not is_equal_approx(frames.get_animation_speed(animation), float(group[2])):
					errors.append("FPS errati: %s" % animation)
				if frames.get_animation_loop(animation) != bool(group[3]):
					errors.append("Loop errato: %s" % animation)
				for frame_index in range(frames.get_frame_count(animation)):
					var texture: AtlasTexture = frames.get_frame_texture(animation, frame_index) as AtlasTexture
					var label: String = "%s/%d" % [animation, frame_index]
					if texture == null:
						errors.append("AtlasTexture mancante: %s" % label)
						continue
					var expected_region := Rect2(frame_index * 64, (group_index * 8 + direction_index) * 64, 64, 64)
					if texture.region != expected_region:
						errors.append("Regione errata: %s: %s" % [label, texture.region])
					if not texture.filter_clip:
						errors.append("filter_clip disattivato: %s" % label)
					if texture.atlas == null or texture.atlas.get_size() != Vector2(768, 2048):
						errors.append("Dimensioni atlante errate: %s" % label)
					if disk == null or not disk.has_animation(animation) or disk.get_frame_count(animation) != count:
						errors.append("File su disco incoerente: %s" % animation)
					else:
						var stored := disk.get_frame_texture(animation, frame_index) as AtlasTexture
						if stored == null or stored.region != expected_region or not stored.filter_clip:
							errors.append("Regione su disco errata: %s" % label)
	actor.free()
	assert_true(errors.is_empty(), "\n".join(errors))
