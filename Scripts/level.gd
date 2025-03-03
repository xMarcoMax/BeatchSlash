extends Node2D

@onready var player = $Player
@onready var target = get_node("Boyfriend")
@onready var spawn_area = $World/EnemySpawn
@onready var hud = $HUD
const base_enemy_health = 100
const base_enemy_damage = 10
const base_enemy_number = 5

var enemy = preload("res://Characters/enemy.tscn")
var total_enemies = 5
var wave = 1
var defeated_total = 0
var defeated_level = 0
var record
var spawn_number

#Set essential variables
func _ready():
	total_enemies = base_enemy_number
	spawn_number = base_enemy_number
	record = 0 #da sistemare quando saranno implementati i salvataggi di dati
	hud.set_health(target.hp)
	hud.set_wave(wave)
	hud.set_defeated(defeated_total)
	hud.set_record(record)

func _process(delta):
	spawn_enemy()
	check_wave_completed()

func check_wave_completed():
	if(total_enemies == defeated_level):
		wave += 1
		hud.set_wave(wave)
		total_enemies = Formulas.calculate("enemies", wave, base_enemy_number)
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
		spawn.hp = Formulas.calculate("health", wave, base_enemy_health)
		spawn.damage = Formulas.calculate("damage", wave, base_enemy_damage)
		spawn_number -= 1

func get_new_enemy_number():
	pass
func get_new_enemy_hp():
	pass
func get_new_enemy_damage():
	pass

func _on_defeated():
	defeated_total += 1
	defeated_level += 1
	hud.set_defeated(defeated_total)
	if defeated_total > record:
		hud.set_record(defeated_total)
