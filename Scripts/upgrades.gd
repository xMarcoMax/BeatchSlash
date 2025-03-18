extends StaticBody2D

@onready var area = $Area2D
@onready var sprite = $Sprite2D
@onready var shape = $CollisionShape2D

func _ready():
	area.body_entered.connect(_on_body_entered)

func _on_body_entered(body):
	if body.is_in_group("player"):
		print("Player entrato")
