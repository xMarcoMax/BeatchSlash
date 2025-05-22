extends Node2D

@onready var player: CharacterBody2D = $Player
@onready var target: CharacterBody2D = get_node("Boyfriend")
@onready var spawn_area: Area2D = $World/EnemySpawn
@onready var hud: CanvasLayer = $UI/HUD
@onready var game_over: CanvasLayer = $UI/GameOver
@onready var pause_menu: CanvasLayer = $UI/PauseMenu
@onready var next_wave: Label = $UI/HUD/NextWave
@onready var next_wave_timer: Timer = $NextWaveTimer

const base_enemy_health = 100
const base_enemy_damage = 10
const base_enemy_number = 5
const base_enemy_points = 10
const base_enemy_currency = 5

var enemy = preload("res://Characters/enemy.tscn")
var total_enemies = 5
var wave = 1
var defeated_total = 0
var defeated_level = 0
var spawn_number
var remain

var points = 0
var currency = 0
var point_multiplier
var currency_multiplier

#Set essential variables
func _ready():
	hud.set_values(target.shield, target.hp)
	hud.set_wave(wave)
	set_hud()
	set_variables()
	set_signals()

#Enemis spawn and check of completed wave
func _process(delta):
	spawn_enemy()
	check_all_eliminated()
	if next_wave_timer.time_left > 0:
		update_timer_text()

#Check if all enemies defeated and set timer to next wave
func check_all_eliminated():
	if(total_enemies == defeated_level and next_wave_timer.is_stopped()):
		next_wave.visible = true
		next_wave_timer.start()
		SignalManager.wave_purchase_item.emit(wave)
		update_timer_text()

func update_timer_text():
	next_wave.text = "Prossima ondata tra: " + str( ceili(next_wave_timer.time_left) )

func spawn_enemy():
	if spawn_number > 0:
		var spawn_point = spawn_area.calculate_spawn_point()
		var spawn = enemy.instantiate()
		spawn.position = spawn_point
		add_child(spawn)
		SignalManager.defeated.connect(_on_defeated)
		spawn.set_spawn_values(target,
			Formulas.calculate("health", wave, base_enemy_health),
			Formulas.calculate("damage", wave, base_enemy_damage)
		)
		spawn_number -= 1

func _on_defeated():
	defeated_total += 1
	defeated_level += 1
	remain -= 1
	points = points + (point_multiplier * base_enemy_points)
	currency = currency + (currency_multiplier * base_enemy_currency)
	hud.set_defeated(defeated_total)
	hud.set_remain(remain)
	hud.set_points(points)
	hud.set_currency(currency)

func _on_next_wave_timer_timeout():
	next_wave.visible = false
	set_next_wave()

func _on_game_over():
	game_over.visible = true
	get_tree().paused = true


func set_next_wave():
	wave += 1
	hud.set_wave(wave)
	total_enemies = Formulas.calculate("enemies", wave, base_enemy_number)
	remain = total_enemies
	hud.set_remain(remain)
	spawn_number = total_enemies
	defeated_level = 0
	if Global.is_in_purchase:
		Global.is_in_purchase = false

func set_signals():
	SignalManager.game_over.connect(_on_game_over)

func set_variables():
	total_enemies = base_enemy_number
	spawn_number = base_enemy_number
	remain = base_enemy_number
	point_multiplier = 1
	currency_multiplier = 1

func set_hud():
	hud.set_defeated(defeated_total)
	hud.set_remain(total_enemies)
	hud.set_points(points)
	hud.set_currency(currency)
