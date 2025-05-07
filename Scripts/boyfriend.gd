extends CharacterBody2D

@export var hp = 100
@export var shield = 100

@onready var area: Area2D = $HitZone
@onready var sprite: Sprite2D = $Sprite2D
@onready var shape: CollisionShape2D = $CollisionShape2D

var is_attacked = false
var max_hp
var max_shield

func _ready():
	max_hp = hp
	max_shield = shield
	SignalManager.item_purchased.connect(_apply_bonus)
	area.body_entered.connect(_on_body_entered)

func _on_body_entered(body):
	if body.is_in_group("enemy"):
		SignalManager.enemy_attacking.emit(body)
		is_attacked = true

func _process(delta):
	pass

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
