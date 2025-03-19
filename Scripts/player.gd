extends CharacterBody2D


@export var speed = 400
@export var ball : PackedScene
@onready var ray_cast: RayCast2D = $RayCast2D
@onready var camera: Camera2D = $Camera2D
@onready var animations: AnimationPlayer = $AnimationPlayer
@export var damage = 10

var nominal_speed = speed
var last_animation = "down"
var is_attacking = false

@warning_ignore("unused_parameter")
func _physics_process(delta):
	get_input()
	update_animation()
	move_and_slide()

#Input events (shoot, attack, etc.)
func _input(event):
	if(event.is_action_pressed("shoot_sand")):
		var mouse_position = get_global_mouse_position()
		shoot_sand(mouse_position)

func update_animation():
	if is_attacking: return
	if velocity.length() == 0:
		if animations.is_playing():
			animations.stop()
	else:
		var direction = "down"
		if velocity.x < 0: direction = "left"
		elif velocity.x > 0: direction = "right"
		elif velocity.y < 0: direction = "up"
		last_animation = direction

#Input movement direction
func get_input():
	var direction = Input.get_vector("ui_left", "ui_right","ui_up","ui_down")
	if (Input.is_action_pressed("run")):
		nominal_speed = speed * 2
	elif (Input.is_action_just_released("run")):
		nominal_speed = speed
	velocity = direction * nominal_speed

#Shooting sand ball
@warning_ignore("unused_parameter")
func shoot_sand(mouse_position):
	var b: Area2D = ball.instantiate()
	b.damage = damage
	owner.add_child(b)
	ray_cast.look_at(get_global_mouse_position())
	b.transform = ray_cast.global_transform
