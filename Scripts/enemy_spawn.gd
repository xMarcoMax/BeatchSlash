extends Node2D

var spawn_areas: Array

# Called when the node enters the scene tree for the first time.
func _ready():
	spawn_areas = []
	for child in get_children():
		if child is CollisionShape2D:
			spawn_areas.append(child)

func calculate_spawn_point():
	# Wider zones get proportionally more spawns, so a short strip does not take a quarter of them
	var total := 0.0
	for area: CollisionShape2D in spawn_areas:
		total += area.shape.size.x * area.shape.size.y
	var pick := randf() * total
	var spawn_area: CollisionShape2D = spawn_areas[-1]
	for area: CollisionShape2D in spawn_areas:
		pick -= area.shape.size.x * area.shape.size.y
		if pick <= 0.0:
			spawn_area = area
			break
	var shape = spawn_area.shape
	var center = spawn_area.global_position
	var size = shape.size/2.0
	
	var spawn_point = Vector2(
		randf_range(center.x - size.x, center.x + size.x),
		randf_range(center.y - size.y, center.y + size.y)
		)
	
	return spawn_point
	
# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
