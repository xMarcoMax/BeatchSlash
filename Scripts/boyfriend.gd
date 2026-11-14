extends CharacterBody2D

#With no morality left, at or below this fraction of max fidelity he stops admiring the girls and shows off his muscles
const FLEX_HP_RATIO = 0.5
#While morality holds he only glances at an attacker now and then, after a random pause in this range (seconds)
const GLANCE_PAUSE = Vector2(2.5, 5.0)

@export var hp = 100
@export var shield = 100

@onready var area: Area2D = $HitZone
@onready var animations: AnimatedSprite2D = $AnimatedSprite2D
@onready var shape: CollisionShape2D = $CollisionShape2D

var max_hp
var max_shield
#Enemies inside the hit zone, i.e. attacking him
var attackers: Array = []
var glance_left = 0.0

func _ready():
	max_hp = hp
	max_shield = shield
	SignalManager.item_target_purchased.connect(_apply_bonus)
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

func _on_enemy_attack(damage):
	calculate_health_values(damage)
	if hp <= 0:
		SignalManager.game_over.emit()

func calculate_health_values(damage):
	if shield > 0:
		shield -= damage
	else:
		hp -= damage
	SignalManager.update_health_shield.emit(hp, shield)

func _apply_bonus(data: Dictionary):
	if(data["category"] == "Target"):
		var added_value
		if(data["sub_category"] == "Shield"):
			added_value = max_shield * data["bonus"]
			set_shield(added_value)
		elif data["sub_category"] == "Health":
			added_value = max_hp * data["bonus"]
			set_hp(added_value)
		SignalManager.update_health_shield.emit(hp, shield)

func set_hp(value):
	hp += value
	if hp > max_hp:
		hp = max_hp
func set_shield(value):
	shield += value
	if shield > max_shield:
		shield = max_shield

func set_max_hp(value):
	pass
func set_max_shield(value):
	pass
