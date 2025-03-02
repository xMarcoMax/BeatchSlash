extends Node2D

@onready var player = $Player
@onready var spawn_area = $World/EnemySpawn
@onready var hud = $HUD

var enemy = preload("res://Characters/enemy.tscn")
var spawn_number = 5

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _ready():
	hud.set_health(100)
	hud.set_wave(1)
	hud.set_defeated(0)
	hud.set_record(0)

func _process(delta):
	if spawn_number > 0:
		var spawn_point = spawn_area.calculate_spawn_point()
		var spawn = enemy.instantiate()
		spawn.position = spawn_point
		add_child(spawn)
		spawn.target = get_node("Boyfriend")
		spawn_number -= 1
