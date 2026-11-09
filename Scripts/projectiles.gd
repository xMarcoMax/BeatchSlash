extends Area2D

@export var speed = 400
var damage
var is_impacting := false

@onready var animations: AnimatedSprite2D = $AnimatedSprite2D

func _ready():
	animations.play(&"flight")

func _physics_process(delta):
	if is_impacting:
		return
	position = position + transform.x * speed * delta

#Detects if the bullet hit an enemy
func _on_body_entered(body):
	if is_impacting:
		return
	if body.is_in_group("enemy") and body.hp > 0:
		# Lock the hit before damage/death signals can trigger another contact.
		is_impacting = true
		set_physics_process(false)
		set_deferred("monitoring", false)
		set_deferred("monitorable", false)
		$CollisionShape2D.set_deferred("disabled", true)
		$Used.stop()
		animations.play(&"impact")
		body.hp = body.hp - damage
		if body.hp <= 0:
			enemy_dead(body)

func enemy_dead(body):
	body.dead()

func _on_used_timeout():
	if not is_impacting:
		queue_free()

func _on_animation_finished():
	if is_impacting and animations.animation == &"impact":
		queue_free()
