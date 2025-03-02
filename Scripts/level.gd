extends Node2D

@onready var player = $Player
@onready var target = get_node("Boyfriend")
@onready var spawn_area = $World/EnemySpawn
@onready var hud = $HUD

var enemy = preload("res://Characters/enemy.tscn")
var total_enemies = 5
var wave = 1
var defeated_total = 0
var defeated_level = 0
var record
var spawn_number

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _ready():
	spawn_number = total_enemies
	record = 0
	hud.set_health(target.hp)
	hud.set_wave(wave)
	hud.set_defeated(defeated_total)
	hud.set_record(0)

func _process(delta):
	spawn_enemy()
	check_wave_completed()

func check_wave_completed():
	if(total_enemies == defeated_level):
		wave += 1
		hud.set_wave(wave)
		total_enemies = 6
		spawn_number = total_enemies
		defeated_level = 0

func spawn_enemy():
	if spawn_number > 0:
		var spawn_point = spawn_area.calculate_spawn_point()
		var spawn = enemy.instantiate()
		spawn.position = spawn_point
		add_child(spawn)
		spawn.defeated.connect(_on_defeated)
		spawn.target = target
		spawn_number -= 1

func _on_defeated():
	print("nemico sconfitto")
	defeated_total += 1
	defeated_level += 1
	hud.set_defeated(defeated_total)
	if defeated_total > record:
		hud.set_record(defeated_total)
