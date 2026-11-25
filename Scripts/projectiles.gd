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

#Detects if the bullet hit an enemy or something solid (shop, props): the ball bursts against it instead of flying through
func _on_body_entered(body):
	if is_impacting or is_landing:
		return
	if body.is_in_group("upgrades") or body.is_in_group("solid_prop"):
		_impact()
	# During the game over scene balls pass through the girls without any effect
	elif body.is_in_group("enemy") and body.hp > 0 and not Global.game_over_sequence:
		_impact()
		body.take_damage(damage, transform.x)

# Lock the hit before damage/death signals can trigger another contact.
func _impact():
	is_impacting = true
	set_physics_process(false)
	set_deferred("monitoring", false)
	set_deferred("monitorable", false)
	$CollisionShape2D.set_deferred("disabled", true)
	$Used.stop()
	animations.play(&"impact")

#The enemy's Hurtbox (full-body area) receives hits; its body shape only sits at the feet
func _on_area_entered(area):
	_on_body_entered(area.get_parent())

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
