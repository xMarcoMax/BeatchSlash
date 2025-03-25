extends CharacterBody2D

@export var hp = 100
@export var shield = 100

@onready var area: Area2D = $HitZone
@onready var sprite: Sprite2D = $Sprite2D
@onready var shape: CollisionShape2D = $CollisionShape2D

var is_attacked = false

func _ready():
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

func set_hp(value):
	pass
func set_shield(value):
	pass
