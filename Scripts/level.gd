extends Node2D

var enemy = preload("res://Characters/enemy.tscn")
@onready var spawn_area = $World/EnemySpawn
var spawn_number = 5
# Called when the node enters the scene tree for the first time.

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if spawn_number > 0:
		var spawn_point = spawn_area.calculate_spawn_point()
		var spawn = enemy.instantiate()
		spawn.position = spawn_point
		print(spawn.name)
		print(spawn.position)
		add_child(spawn)
		spawn.target = get_node("Boyfriend")
		spawn_number -= 1
