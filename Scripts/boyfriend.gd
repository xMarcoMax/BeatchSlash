extends CharacterBody2D

#With no morality left, at or below this fraction of max fidelity he stops admiring the girls and shows off his muscles
const FLEX_HP_RATIO = 0.5
#While morality holds he only glances at an attacker now and then, after a random pause in this range (seconds)
const GLANCE_PAUSE = Vector2(2.5, 5.0)
#Floating numbers use the colors of the HUD bars: blue = morality, red = fidelity
const SHIELD_TEXT_COLOR = Color(0.35, 0.75, 1.0)
const HEALTH_TEXT_COLOR = Color(1.0, 0.35, 0.35)
#Horizontal distance of each number from the centre when a purchase restores both bars
const BOTH_TEXT_SPREAD = 90.0

@export var hp = 100
@export var shield = 100

@onready var area: Area2D = $HitZone
@onready var animations: AnimatedSprite2D = $AnimatedSprite2D
@onready var shape: CollisionShape2D = $CollisionShape2D

var max_hp
var max_shield
#Starting maximums: every "raise maximum" purchase adds a fraction of these, not of the current maximum
var base_max_hp
var base_max_shield
#Fraction of incoming damage absorbed by temporary "guard" items, one per bar (0.5 = half the damage)
var guard_shield = 0.0
var guard_health = 0.0
#Enemies inside the hit zone, i.e. attacking him
var attackers: Array = []
var glance_left = 0.0
#Game over scene: GameOverSequence moves him and picks his animations
var scripted = false

func _ready():
	max_hp = hp
	max_shield = shield
	base_max_hp = hp
	base_max_shield = shield
	SignalManager.item_target_purchased.connect(_apply_bonus)
	SignalManager.item_expired.connect(_on_item_expired)
	SignalManager.attack_target.connect(_on_enemy_attack)
	area.body_entered.connect(_on_body_entered)
	area.body_exited.connect(_on_body_exited)

func _on_body_entered(body):
	if body.is_in_group("enemy"):
		SignalManager.enemy_attacking.emit(body)
		attackers.append(body)

#An enemy pushed out of the hit zone stops attacking and walks back
func _on_body_exited(body):
	if body.is_in_group("enemy"):
		SignalManager.enemy_left_target.emit(body)
		attackers.erase(body)

func _process(delta):
	if not scripted:
		update_animation(delta)

#Sunbathing when nobody attacks. Under attack: with morality left (any fidelity) an occasional glance at an attacker;
#with no morality, admires the nearest girl, and shows off his muscles once fidelity is at half or less
func update_animation(delta):
	attackers = attackers.filter(func(e): return is_instance_valid(e) and e.hp > 0)
	if attackers.is_empty():
		animations.play("idle_down")
		return
	if shield > 0:
		glance_left -= delta
		# The glance plays once, then back to the idle
		if animations.animation.begins_with("glance_") and animations.is_playing():
			return
		if glance_left <= 0.0:
			glance_left = randf_range(GLANCE_PAUSE.x, GLANCE_PAUSE.y)
			animations.play("glance_" + Formulas.direction_name(attackers.pick_random().position - position))
		else:
			animations.play("idle_down")
		return
	var look = Formulas.direction_name(_nearest_attacker().position - position)
	animations.play(("admire_" if hp > max_hp * FLEX_HP_RATIO else "flex_") + look)

func _nearest_attacker():
	var nearest = attackers[0]
	for enemy in attackers:
		if position.distance_squared_to(enemy.position) < position.distance_squared_to(nearest.position):
			nearest = enemy
	return nearest

#The attack that empties fidelity starts the game over, once, with the girl who made it
func _on_enemy_attack(damage, attacker):
	if Global.game_over_sequence:
		return
	calculate_health_values(damage)
	if hp <= 0:
		Global.game_over_sequence = true
		SignalManager.game_over.emit(attacker)

func calculate_health_values(damage):
	if shield > 0:
		# Never below 0: a negative shield would make a paid restore give back less than it promises
		var lost = mini(ceili(damage * (1.0 - guard_shield)), ceili(shield))
		shield = max(shield - lost, 0)
		show_change(-lost, SHIELD_TEXT_COLOR)
	else:
		var lost = ceili(damage * (1.0 - guard_health))
		hp -= lost
		show_change(-lost, HEALTH_TEXT_COLOR)
	SignalManager.update_health_shield.emit(hp, shield)

func _apply_bonus(data: Dictionary):
	if data["category"] != "Target":
		return
	var shield_before = shield
	var hp_before = hp
	match [data["effect"], data["sub_category"]]:
		["restore", "Shield"]:
			set_shield(max_shield * data["bonus"])
		["restore", "Health"]:
			set_hp(max_hp * data["bonus"])
		["restore", "Both"]:
			set_shield(max_shield * data["bonus"])
			set_hp(max_hp * data["bonus"])
		["max", "Shield"]:
			set_max_shield(roundi(base_max_shield * data["bonus"]))
		["max", "Health"]:
			set_max_hp(roundi(base_max_hp * data["bonus"]))
		["guard", "Shield"]:
			guard_shield += data["bonus"]
		["guard", "Health"]:
			guard_health += data["bonus"]
	# Restoring both bars: the two numbers go side by side instead of on top of each other
	var side = Vector2(BOTH_TEXT_SPREAD, 0) if data["sub_category"] == "Both" else Vector2.ZERO
	show_change(shield - shield_before, SHIELD_TEXT_COLOR, -side)
	show_change(hp - hp_before, HEALTH_TEXT_COLOR, side)
	SignalManager.update_health_shield.emit(hp, shield)

#A temporary guard ran out of waves
func _on_item_expired(data: Dictionary):
	if data["category"] != "Target" or data["effect"] != "guard":
		return
	if data["sub_category"] == "Shield":
		guard_shield -= data["bonus"]
	else:
		guard_health -= data["bonus"]

#Number above his head with the change of a bar ("-10", "+25")
func show_change(amount, color: Color, shift := Vector2.ZERO):
	if roundi(amount) != 0:
		FloatingText.spawn(get_parent(), position + FloatingText.HEAD_OFFSET + shift, "%+d" % roundi(amount), color)

func set_hp(value):
	hp += value
	if hp > max_hp:
		hp = max_hp
func set_shield(value):
	shield += value
	if shield > max_shield:
		shield = max_shield

#Raising a maximum also fills the added amount
func set_max_hp(value):
	max_hp += value
	hp += value
	SignalManager.update_max_health_shield.emit(max_hp, max_shield)
func set_max_shield(value):
	max_shield += value
	shield += value
	SignalManager.update_max_health_shield.emit(max_hp, max_shield)
