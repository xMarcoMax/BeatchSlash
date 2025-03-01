extends Node2D

var spawn_areas: Array

# Called when the node enters the scene tree for the first time.
func _ready():
	var left_spawn: CollisionShape2D = $LeftSpawn
	var bottom_spawn: CollisionShape2D = $BottomSpawn
	var right_spawn: CollisionShape2D = $RightSpawn
	
	spawn_areas = [left_spawn, bottom_spawn, right_spawn]

func calculate_spawn_point():
	var spawn_area: CollisionShape2D = spawn_areas.pick_random()
	var shape = spawn_area.shape
	var center = spawn_area.position
	var size = shape.extents
	
	var spawn_point = Vector2(
		randf_range(center.x - size.x, center.x + size.x),
		randf_range(center.y - size.y, center.y + size.y)
		)
	
	return spawn_point
	
# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
