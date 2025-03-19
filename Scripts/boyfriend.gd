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
		SignalManager.enemy_attacking.emit()
		is_attacked = true

func _process(delta):
	pass

func _physics_process(delta):
	pass

func _on_enemy_attack(damage):
	hp -= damage
	SignalManager.update_health.emit(hp)
	if hp <= 0:
		print("GAME OVER")
