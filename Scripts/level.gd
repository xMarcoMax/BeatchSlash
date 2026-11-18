extends Node2D

@onready var player: CharacterBody2D = $Player
@onready var target: CharacterBody2D = get_node("Boyfriend")
@onready var spawn_area: Area2D = $World/EnemySpawn
@onready var hud: CanvasLayer = $UI/HUD
@onready var game_over: CanvasLayer = $UI/GameOver
@onready var pause_menu: CanvasLayer = $UI/PauseMenu
@onready var next_wave: RichTextLabel = $UI/HUD/NextWave
@onready var next_wave_timer: Timer = $NextWaveTimer

const base_enemy_health = 50
const base_enemy_damage = 5
const base_enemy_number = 3
const base_enemy_points = 10
const base_enemy_currency = 18

# Bonus di fine ondata sulle monete guadagnate nell'ondata (nessuna crescita per ondata: l'unica crescita è il bonus acquistabile):
# fedeltà al massimo e moralità al massimo = +100%; moralità sotto il massimo e oltre il 50% = +50%;
# moralità tra 0 (escluso) e il 50% (compreso) = +25%; moralità a 0 o fedeltà sotto il massimo = nessun bonus.
const WAVE_BONUS_PERFECT = 1.0
const WAVE_BONUS_GUARDED = 0.5
const WAVE_BONUS_WEAK = 0.25

var enemy = preload("res://Characters/enemy.tscn")
var bonus_popup = preload("res://Objects/wave_bonus_popup.tscn").instantiate()
var pathfinder := Pathfinder.new()
var total_enemies = base_enemy_number
var wave = 1
var defeated_total = 0
var defeated_level = 0
var spawn_number
var remain

var points = 0
var point_multiplier
var currency_multiplier
var wave_currency = 0       # monete accreditate dalle nemiche nell'ondata in corso (gli acquisti non contano)

#Set essential variables
func _ready():
	player.play_area = _play_area()
	hud.add_child(bonus_popup)
	hud.set_values(target.hp, target.shield)
	hud.set_wave(wave)
	set_hud()
	set_variables()
	set_signals()
	add_child(pathfinder)
	pathfinder.build(_world_bounds())

#Part of the fixed camera view left free by the HUD bands, in global coordinates
func _play_area() -> Rect2:
	var camera: Camera2D = $Camera2D
	var view := get_viewport_rect().size / camera.zoom
	var top: float = hud.top_band.custom_minimum_size.y / camera.zoom.y
	var bottom: float = hud.bottom_band.custom_minimum_size.y / camera.zoom.y
	return Rect2(camera.global_position - view / 2.0 + Vector2(0.0, top), view - Vector2(0.0, top + bottom))

#Area covered by the map, the spawn zones and the target, in global coordinates
func _world_bounds() -> Rect2:
	var bounds := Rect2(target.global_position, Vector2.ZERO)
	for layer: TileMapLayer in [$World/TutorialMap/Ground]:
		var tile := Vector2(layer.tile_set.tile_size)
		var used := layer.get_used_rect()
		bounds = bounds.merge(layer.get_global_transform() * Rect2(Vector2(used.position) * tile, Vector2(used.size) * tile))
	for area: CollisionShape2D in spawn_area.spawn_areas:
		var size: Vector2 = area.shape.size
		bounds = bounds.merge(Rect2(area.global_position - size / 2.0, size))
	return bounds

#Enemis spawn and check of completed wave
func _process(delta):
	spawn_enemy()
	check_all_eliminated()
	if next_wave_timer.time_left > 0:
		update_timer_text()

#Check if all enemies defeated and set timer to next wave
func check_all_eliminated():
	if(total_enemies == defeated_level and next_wave_timer.is_stopped()):
		_award_wave_bonus()
		next_wave.visible = true
		next_wave_timer.start()
		SignalManager.wave_purchase_item.emit(wave)
		update_timer_text()

# Quota di monete in più rispetto a quelle guadagnate nell'ondata, secondo lo stato del ragazzo a ondata finita.
# La fedeltà al massimo è obbligatoria; con la moralità a zero non c'è bonus.
func wave_bonus_rate() -> float:
	if target.hp < target.max_hp:
		return 0.0
	if target.shield >= target.max_shield:
		return WAVE_BONUS_PERFECT
	if target.shield > target.max_shield * 0.5:
		return WAVE_BONUS_GUARDED
	if target.shield > 0:
		return WAVE_BONUS_WEAK
	return 0.0

func _award_wave_bonus():
	var rate = wave_bonus_rate()
	var bonus = roundi(wave_currency * rate)
	if bonus > 0:
		Global.currency += bonus
		bonus_popup.play("Bonus ondata +%d%%" % roundi(rate * 100), "+%d monete" % bonus)

func update_timer_text():
	next_wave.text = "[center]Prossima ondata tra: [color=#ffcc47]%d[/color][/center]" % ceili(next_wave_timer.time_left)

func spawn_enemy():
	if spawn_number > 0:
		var spawn_point = spawn_area.calculate_spawn_point()
		var spawn = enemy.instantiate()
		spawn.position = to_local(spawn_point)
		add_child(spawn)
		spawn.pathfinder = pathfinder
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
	var earned = roundi(currency_multiplier * base_enemy_currency)
	Global.currency += earned
	wave_currency += earned
	hud.set_defeated(defeated_total)
	hud.set_remain(remain)
	hud.set_points(points)

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
	wave_currency = 0
	if Global.is_in_purchase:
		Global.is_in_purchase = false

func set_signals():
	SignalManager.game_over.connect(_on_game_over)
	SignalManager.defeated.connect(_on_defeated)
	SignalManager.item_bonus_purchased.connect(_on_bonus_purchased)
	SignalManager.item_expired.connect(_on_item_expired)

# Acquisto Bonus: la percentuale si somma al moltiplicatore delle monete (1.0 = 100%)
func _on_bonus_purchased(data: Dictionary):
	if data["effect"] == "coin_bonus":
		currency_multiplier += data["bonus"]

# Un bonus temporaneo sulle monete è finito: si toglie la percentuale che aveva aggiunto
func _on_item_expired(data: Dictionary):
	if data["category"] == "Bonus" and data["effect"] == "coin_bonus":
		currency_multiplier -= data["bonus"]

func set_variables():
	total_enemies = base_enemy_number
	spawn_number = base_enemy_number
	remain = base_enemy_number
	point_multiplier = 1
	currency_multiplier = 1.0
	Global.currency = 0

func set_hud():
	hud.set_defeated(defeated_total)
	hud.set_remain(total_enemies)
	hud.set_points(points)
