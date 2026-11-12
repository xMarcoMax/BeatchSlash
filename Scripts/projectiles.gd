extends Area2D

@export var speed = 400
#At the end of its flight the ball slows down by this much per second while it drops onto the sand
const LAND_DECEL = 1500.0
var damage
var is_impacting := false
var is_landing := false

@onready var animations: AnimatedSprite2D = $AnimatedSprite2D

func _ready():
	animations.play(&"flight")
	# The launch transform is assigned after add_child(): read the direction once it is set.
	_face_upright.call_deferred()

# When thrown leftwards the node is rotated ~180 degrees: flip the sprite vertically so
# the top-left lighting stays on top. The impact frames face +x, i.e. the enemy, in every direction.
func _face_upright():
	animations.flip_v = global_transform.x.x < 0.0

func _physics_process(delta):
	if is_impacting:
		return
	if is_landing:
		speed = maxf(speed - LAND_DECEL * delta, 0.0)
	position = position + transform.x * speed * delta

#Detects if the bullet hit an enemy
func _on_body_entered(body):
	if is_impacting or is_landing:
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
		body.take_damage(damage, transform.x)

#End of the flight: the ball drops onto the sand and scatters (no more hits while it falls)
func _on_used_timeout():
	if is_impacting:
		return
	is_landing = true
	set_deferred("monitoring", false)
	set_deferred("monitorable", false)
	$CollisionShape2D.set_deferred("disabled", true)
	animations.play(&"land")

func _on_animation_finished():
	if animations.animation == &"impact" or animations.animation == &"land":
		queue_free()
