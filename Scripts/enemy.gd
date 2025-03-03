extends CharacterBody2D

@export var speed = 100
@export var target: CharacterBody2D
@onready var ray_cast = $RayCast2D
@onready var timer = $DeadTimer
@onready var health = $HP
@onready var progress_bar = $ProgressBar

@export var hp = 100
@export var damage = 10

signal defeated
func _ready():
	target = get_node("../Boyfriend")
	progress_bar.max_value = hp;

func _process(delta):
	health.text = "Salute: 0" if hp <= 0 else "Salute: "+str(hp)
	progress_bar.value = hp

#Moving the enemy to a specific location
func _physics_process(delta):
	ray_cast.look_at(target.position)
	if ray_cast.is_colliding() or hp <= 0:
		velocity = Vector2.ZERO
	else:
		velocity = position.direction_to(target.position) * speed
	move_and_slide()

func set_spawn_values(target_body, hp_value, damage_value):
	target = target_body
	damage = damage_value
	hp = hp_value
	progress_bar.max_value = hp_value
	
#Stop movement and playing dead animation
func dead():
	velocity = Vector2.ZERO
	$CollisionShape2D.set_deferred("disabled", true)
	timer.start()
	defeated.emit()

#Delete the dead enemy after the animation
func _on_dead_timer_timeout():
	queue_free()
