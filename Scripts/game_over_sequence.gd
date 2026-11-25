class_name GameOverSequence
extends Node
## Scenetta di game over: il ragazzo se ne va con la nemica che ha dato l'ultimo colpo.
## La crea il livello quando la fedeltà arriva a zero (Global.game_over_sequence è già vero, quindi nemiche,
## Player, spawn e proiettili sono fermi). Muove ragazzo, nemica e Player e sceglie le loro animazioni;
## emette `finished` FINAL_WAIT secondi dopo che la coppia è uscita dall'inquadratura.

signal finished

const KISS_HEART = preload("res://Assets/Effects/Hearts/kiss_heart.png")
const SMALL_HEART = preload("res://Assets/Effects/Hearts/small_heart.png")

## Sosta della coppia sotto il punto di partenza del ragazzo: lui a sinistra, lei a destra
const STAGE_OFFSET = Vector2(0, 300)
const STAGE_HALF_GAP = 90.0
## La sosta resta a questa distanza dai bordi dell'inquadratura
const STAGE_MARGIN = Vector2(200, 120)
## Passo della coppia rispetto alla `speed` della nemica (la sua camminata accelera in proporzione;
## quella del ragazzo è disegnata per questo passo)
const COUPLE_PACE = 1.6
## Uscita verso destra più svelta, rispetto al passo della coppia
const EXIT_PACE = 1.4
## Dall'inizio del bacio mandato al momento in cui lui si avvicina: bacio, cuoricino, reazione di lei
const KISS_TIME = 2.0
## Frame di `kiss_right` in cui il braccio si distende e parte il cuoricino
const KISS_RELEASE_FRAME = 6
## Cuoricino: dalla mano di lui al petto di lei (offset dalle origini), durata del volo, ampiezza dell'arco
const HEART_FROM = Vector2(70, -75)
const HEART_TO = Vector2(-10, -70)
const HEART_FLIGHT = 0.5
const HEART_ARC = 40.0
## Due cuoricini piccoli sopra di lei: partono dalla testa e salgono in diagonale sfumando
const SMALL_HEARTS_FROM = Vector2(0, -140)
const SMALL_HEARTS_RISE = Vector2(55, -80)
const SMALL_HEARTS_LIFETIME = 0.9
## Scala dei pixel come i personaggi; sopra tutti i personaggi
const PIXEL_SCALE = 4.0
const EFFECT_Z = 50
## Dopo il bacio lui si avvicina fino a questa distanza, poi la segue a FOLLOW_GAP verso destra
const APPROACH_GAP = 70.0
const FOLLOW_GAP = 90.0
## Oltre il bordo destro dell'inquadratura di questa distanza i due sono del tutto fuori dallo schermo
const EXIT_MARGIN = 200.0
const FINAL_WAIT = 1.0
const ARRIVE_RADIUS = 4.0

var player
var boy
var girl
var _couple_speed := 0.0
## Corpo in cammino -> {points, index, speed}; finito il percorso il corpo esce dal dizionario
var _walks := {}
## Il Player guarda il ragazzo quando non cammina, fino al pianto
var _player_watches_boy := false
var _boy_follows := false
var _pathfinder: Pathfinder

## `home` è la meta del Player, `view` l'inquadratura libera dalle bande dell'HUD (coordinate globali)
func play(player_body, boy_body, last_attacker, home: Vector2, view: Rect2, pathfinder: Pathfinder) -> void:
	player = player_body
	boy = boy_body
	girl = last_attacker if is_instance_valid(last_attacker) and last_attacker.hp > 0 else _any_living_enemy()
	_pathfinder = pathfinder
	player.stop_acting()
	boy.scripted = true
	# A scene, not a fight: no flirting and no health bars over the characters
	for enemy in get_tree().get_nodes_in_group("enemy"):
		enemy.is_attacking = false
		enemy.progress_bar.hide()
	if girl == null:
		finished.emit.call_deferred()
		return
	girl.scripted = true
	_couple_speed = girl.speed * COUPLE_PACE
	_player_watches_boy = true
	# Down to the stage, at once while the player walks to her beach umbrella; the kiss waits for all three
	var stage := _stage_point(view)
	_walk(boy, stage - Vector2(STAGE_HALF_GAP, 0), _couple_speed)
	_walk(girl, stage + Vector2(STAGE_HALF_GAP, 0), _couple_speed)
	_walk(player, home, player.speed)
	while not _walks.is_empty():
		await get_tree().physics_frame
	_face(boy, Vector2.RIGHT)
	_face(girl, Vector2.LEFT)

	# He blows a kiss, the heart flies to her, she blushes with two small hearts over her head
	var kiss_end := Time.get_ticks_msec() + int(KISS_TIME * 1000.0)
	boy.animations.play("kiss_right")
	while boy.animations.animation == "kiss_right" and boy.animations.frame < KISS_RELEASE_FRAME:
		await get_tree().process_frame
	await _send_heart(boy.global_position + HEART_FROM, girl.global_position + HEART_TO)
	girl.animations.play("blush_left")
	_small_hearts(girl.global_position + SMALL_HEARTS_FROM)
	while Time.get_ticks_msec() < kiss_end:
		await get_tree().process_frame

	_walk(boy, girl.global_position - Vector2(APPROACH_GAP, 0), _couple_speed)
	while _walks.has(boy):
		await get_tree().physics_frame

	# She leads, he follows: as they go the player turns to the camera and cries,
	# the other girls slump while still watching the couple walk away
	_walk(girl, Vector2(view.end.x + EXIT_MARGIN, girl.global_position.y), _couple_speed * EXIT_PACE)
	boy.animations.speed_scale = EXIT_PACE
	_boy_follows = true
	_player_watches_boy = false
	player.animations.play("cry_down")
	for enemy in get_tree().get_nodes_in_group("enemy"):
		if enemy != girl and enemy.hp > 0:
			enemy.game_over_pose = "sad"
	while boy.global_position.x < view.end.x + EXIT_MARGIN - FOLLOW_GAP - ARRIVE_RADIUS:
		await get_tree().physics_frame
	_boy_follows = false
	boy.hide()
	girl.hide()
	await _wait(FINAL_WAIT)
	finished.emit()

func _physics_process(delta: float) -> void:
	for body in _walks.keys():
		_step_walk(body, delta)
	if _boy_follows:
		var goal: Vector2 = girl.global_position - Vector2(FOLLOW_GAP, 0)
		if boy.global_position.distance_to(goal) > ARRIVE_RADIUS:
			_move_toward(boy, goal, _couple_speed * EXIT_PACE * delta)
	if _player_watches_boy and not _walks.has(player):
		_face(player, boy.global_position - player.global_position)

func _step_walk(body, delta: float) -> void:
	var walk: Dictionary = _walks[body]
	var points: PackedVector2Array = walk.points
	var budget: float = walk.speed * delta
	while budget > 0.0 and walk.index < points.size():
		var target: Vector2 = points[walk.index]
		var distance: float = body.global_position.distance_to(target)
		if distance <= budget:
			body.global_position = target
			budget -= distance
			walk.index += 1
		else:
			_move_toward(body, target, budget)
			budget = 0.0
	if walk.index >= points.size():
		_walks.erase(body)
		body.animations.speed_scale = 1.0
		_face(body, (points[points.size() - 1] - points[maxi(points.size() - 2, 0)]) if points.size() > 1 else Vector2.DOWN)

func _move_toward(body, target: Vector2, step: float) -> void:
	var direction: Vector2 = target - body.global_position
	body.global_position = body.global_position.move_toward(target, step)
	if not direction.is_zero_approx():
		body.animations.play("walk_" + Formulas.direction_name(direction))

## Walking path around the props (pathfinder) and, when possible, around the girls standing still
func _walk(body, to: Vector2, speed: float) -> void:
	var blockers := PackedVector2Array()
	for enemy in get_tree().get_nodes_in_group("enemy"):
		if enemy != body and enemy != girl and enemy.hp > 0:
			blockers.append(enemy.global_position)
	var points := _pathfinder.find_path(body.global_position, to, blockers) if _pathfinder else PackedVector2Array()
	if points.is_empty() or points[points.size() - 1].distance_to(to) > ARRIVE_RADIUS:
		points.append(to)
	# The walk cycle is drawn for the character's own pace: faster pace, faster steps
	body.animations.speed_scale = speed / body.speed if "speed" in body else 1.0
	_walks[body] = {"points": points, "index": 0, "speed": speed}

## Below the boyfriend, inside the view, so the kiss is always on screen
func _stage_point(view: Rect2) -> Vector2:
	var area := view.grow_individual(-STAGE_MARGIN.x, -STAGE_MARGIN.y, -STAGE_MARGIN.x, -STAGE_MARGIN.y)
	return (boy.global_position + STAGE_OFFSET).clamp(area.position, area.end)

func _face(body, direction: Vector2) -> void:
	if not direction.is_zero_approx():
		body.animations.play("idle_" + Formulas.direction_name(direction))

## Heart in flight along a small arc, then a quick pop where it lands; returns when it lands
func _send_heart(from: Vector2, to: Vector2) -> void:
	var heart := _effect_sprite(KISS_HEART, from)
	var flight := heart.create_tween()
	flight.tween_method(func(k: float): heart.global_position = from.lerp(to, k) + Vector2(0, -HEART_ARC * sin(PI * k)), 0.0, 1.0, HEART_FLIGHT)
	await flight.finished
	var pop := heart.create_tween().set_parallel(true)
	pop.tween_property(heart, "scale", Vector2.ONE * PIXEL_SCALE * 1.6, 0.15)
	pop.tween_property(heart, "modulate:a", 0.0, 0.15)
	pop.chain().tween_callback(heart.queue_free)

## Two small hearts from the centre, rising diagonally left and right and fading, like the damage numbers
func _small_hearts(at: Vector2) -> void:
	for side in [-1.0, 1.0]:
		var heart := _effect_sprite(SMALL_HEART, at)
		var tween := heart.create_tween().set_parallel(true)
		tween.tween_property(heart, "global_position", at + Vector2(SMALL_HEARTS_RISE.x * side, SMALL_HEARTS_RISE.y), SMALL_HEARTS_LIFETIME).set_ease(Tween.EASE_OUT)
		tween.tween_property(heart, "modulate:a", 0.0, SMALL_HEARTS_LIFETIME * 0.5).set_delay(SMALL_HEARTS_LIFETIME * 0.5)
		tween.chain().tween_callback(heart.queue_free)

func _effect_sprite(texture: Texture2D, at: Vector2) -> Sprite2D:
	var sprite := Sprite2D.new()
	sprite.texture = texture
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.scale = Vector2.ONE * PIXEL_SCALE
	sprite.z_index = EFFECT_Z
	boy.get_parent().add_child(sprite)
	sprite.global_position = at
	return sprite

func _any_living_enemy():
	for enemy in get_tree().get_nodes_in_group("enemy"):
		if enemy.hp > 0:
			return enemy
	return null

func _wait(seconds: float) -> Signal:
	return get_tree().create_timer(seconds).timeout
