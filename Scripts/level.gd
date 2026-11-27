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
# fedeltà al massimo e moralità al massimo = +50%; moralità sotto il massimo e oltre il 50% = +25%;
# moralità tra 0 (escluso) e il 50% (compreso) = +10%; moralità a 0 o fedeltà sotto il massimo = nessun bonus.
const WAVE_BONUS_PERFECT = 0.5
const WAVE_BONUS_GUARDED = 0.25
const WAVE_BONUS_WEAK = 0.1
# Negli ultimi secondi del conto alla rovescia ogni numero ha il suo tic
const COUNTDOWN_TICKS = 5
# Un'ondata con più nemiche di così le fa nascere una alla volta, a questo intervallo; fino a SPAWN_STAGGER_ABOVE nascono tutte insieme
const SPAWN_STAGGER_ABOVE = 4
const SPAWN_INTERVAL = 1.5

var enemy = preload("res://Characters/enemy.tscn")
var bonus_popup = preload("res://Objects/wave_bonus_popup.tscn").instantiate()
var pathfinder := Pathfinder.new()
var total_enemies = base_enemy_number
var wave = 1
var defeated_total = 0
var defeated_level = 0
var spawn_number
var spawn_wait = 0.0        # secondi che mancano alla prossima nascita (solo nelle ondate scaglionate)
var remain

var points = 0
var point_multiplier
var currency_multiplier
var _last_countdown_second := 0   # ultimo numero mostrato dal conto alla rovescia, per dare un tic solo al cambio
var wave_currency = 0       # monete accreditate dalle nemiche nell'ondata in corso (gli acquisti non contano)
# Telo dell'ombrellone del Player: punto di partenza della partita e meta nella scenetta di game over
var player_home: Vector2

#Set essential variables
func _ready():
	Global.game_over_sequence = false
	player_home = player.global_position
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
	# Game over scene: no more spawns and no end of wave (the game over wins over a wave ending at the same time)
	if Global.game_over_sequence:
		return
	spawn_wait = maxf(spawn_wait - delta, 0.0)
	spawn_enemy()
	check_all_eliminated()
	if next_wave_timer.time_left > 0:
		update_timer_text()

#Check if all enemies defeated and set timer to next wave
func check_all_eliminated():
	if(total_enemies == defeated_level and next_wave_timer.is_stopped()):
		Sfx.play(Sfx.WAVE_COMPLETE)
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
	var seconds := ceili(next_wave_timer.time_left)
	# Un tic a ogni secondo del conto alla rovescia finale (5, 4, 3, 2, 1); poi il fischio all'inizio dell'ondata
	if seconds != _last_countdown_second and seconds <= COUNTDOWN_TICKS:
		Sfx.play(Sfx.COUNTDOWN_TICK)
	_last_countdown_second = seconds
	next_wave.text = "[center]Prossima ondata tra: [color=#ffcc47]%d[/color][/center]" % seconds

func spawn_enemy():
	if spawn_number > 0 and spawn_wait <= 0.0:
		var spawn_point = spawn_area.calculate_spawn_point()
		var spawn = enemy.instantiate()
		spawn.position = to_local(spawn_point)
		#The first enemy of every wave keeps the colours of the concept (purple hair, green bikini)
		if spawn_number == total_enemies:
			spawn.look = EnemyPalette.original()
		add_child(spawn)
		spawn.pathfinder = pathfinder
		spawn.set_spawn_values(target,
			Formulas.calculate("health", wave, base_enemy_health),
			Formulas.calculate("damage", wave, base_enemy_damage)
		)
		spawn_number -= 1
		if total_enemies > SPAWN_STAGGER_ABOVE:
			spawn_wait = SPAWN_INTERVAL

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
	Sfx.play(Sfx.WAVE_START)
	next_wave.visible = false
	set_next_wave()

#The boyfriend leaves with the girl who made the last attack; the panel appears when the scene ends
func _on_game_over(last_attacker):
	next_wave_timer.stop()
	next_wave.visible = false
	var sequence := GameOverSequence.new()
	add_child(sequence)
	sequence.finished.connect(_show_game_over)
	sequence.play(player, target, last_attacker, player_home, _play_area(), pathfinder)

func _show_game_over():
	MusicManager.stop_music() # la musica di sottofondo (quando ci sarà) si interrompe e parte lo stinger
	Sfx.play(Sfx.GAME_OVER)
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
