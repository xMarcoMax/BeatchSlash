extends Node2D

@onready var player = $Player
@onready var target = get_node("Boyfriend")
@onready var spawn_area = $World/EnemySpawn
@onready var hud = $HUD

var enemy = preload("res://Characters/enemy.tscn")
var total_enemies = 5
var spawn_number = 5
var wave = 1
var defeated = 0
var record

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _ready():
	record = 0
	hud.set_health(target.hp)
	hud.set_wave(wave)
	hud.set_defeated(defeated)
	hud.set_record(0)

func _process(delta):
	spawn_enemy()
	check_wave_completed()

func check_wave_completed():
	if(total_enemies == defeated):
		wave += 1
		hud.set_wave(wave)
		total_enemies = 6

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
	defeated += 1
	hud.set_defeated(defeated)
	if defeated > record:
		hud.set_record(defeated)
