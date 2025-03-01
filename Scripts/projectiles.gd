extends Area2D

@export var speed = 400
var damage

func _physics_process(delta):
	position = position + transform.x * speed * delta

#Detects if the bullet hit an enemy
func _on_body_entered(body):
	if body.is_in_group("enemy") and body.hp > 0:
		body.hp = body.hp - damage
		if body.hp <= 0:
			enemy_dead(body)
		queue_free()

func enemy_dead(body):
	body.dead()

func _on_used_timeout():
	queue_free()
