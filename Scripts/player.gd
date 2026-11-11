extends CharacterBody2D


@export var speed = 400
@export var ball : PackedScene
@onready var ray_cast: RayCast2D = $RayCast2D
@onready var camera: Camera2D = get_node_or_null("Camera2D")
@onready var animations: AnimatedSprite2D = $AnimatedSprite2D
@onready var moving_throw: Sprite2D = $MovingThrow
@export var damage = 10

# Frame 3: hand releases at ~0.094 s with Throw at 32 FPS.
# A new press may interrupt recovery after release, never the pending projectile.
@export_range(0, 7) var throw_release_frame: int = 3
signal throw_released

# Atlas dei lanci in movimento: righe = azione*32 + direzione*8 + fase; ordine direzioni per atlas.
const MOVING_THROW_DIAGONAL = preload("res://Assets/Characters/Player/player_diagonals_moving_throw.png")
const CARDINAL_DIRECTIONS = ["up", "down", "right", "left"]
const DIAGONAL_DIRECTIONS = ["up_right", "up_left", "down_right", "down_left"]
@onready var moving_throw_cardinal: Texture2D = moving_throw.texture

var nominal_speed = speed
var last_animation = "down"
var is_attacking = false
var _throw_released = false
var _moving_gait_phase: float = 0.0

func _ready():
	Global.is_in_purchase = false
	animations.frame_changed.connect(_on_animation_frame_changed)
	animations.animation_finished.connect(_on_animation_finished)
	animations.play("idle_" + last_animation)

@warning_ignore("unused_parameter")
func _physics_process(delta):
	if(!Global.is_in_purchase):
		get_input()
		_update_moving_throw(delta)
		update_animation()
		move_and_slide()

#Input events (shoot, attack, etc.)
func _input(event):
	if(event.is_action_pressed("shoot_sand")):
		var mouse_position = get_global_mouse_position()
		start_throw(mouse_position)

func update_animation():
	if is_attacking: return
	if velocity.length() == 0:
		animations.play("idle_" + last_animation)
	else:
		last_animation = Formulas.direction_name(velocity)
		var action = "dash" if nominal_speed > speed else "walk"
		animations.play(action + "_" + last_animation)

func start_throw(mouse_position: Vector2):
	if Global.is_in_purchase or ball == null:
		return
	if is_attacking and not _throw_released:
		return
	# Carry the current step into the throw, including its fractional progress.
	# Rapid follow-up throws keep the running gait clock instead of restarting it.
	if not is_attacking:
		_moving_gait_phase = 0.0
		if animations.animation.begins_with("walk_") or animations.animation.begins_with("dash_"):
			_moving_gait_phase = animations.frame + animations.frame_progress
	var aim = mouse_position - global_position
	if not aim.is_zero_approx():
		last_animation = Formulas.direction_name(aim)
	# Restart even the same Throw without waiting for its previous recovery.
	is_attacking = false
	animations.stop()
	is_attacking = true
	_throw_released = false
	animations.play("throw_" + last_animation)
	# Also supports release frame 0 when the animation was already on frame 0.
	_on_animation_frame_changed()

func _on_animation_frame_changed():
	_update_moving_throw(0.0)
	if not is_attacking or _throw_released:
		return
	if animations.animation.begins_with("throw_") and animations.frame >= throw_release_frame:
		_throw_released = true
		# Existing projectile/raycast logic remains in shoot_sand().
		shoot_sand(get_global_mouse_position())
		throw_released.emit()

func _on_animation_finished():
	if is_attacking and animations.animation.begins_with("throw_"):
		is_attacking = false
		moving_throw.hide()
		animations.show()
		if velocity.is_zero_approx():
			animations.play("idle_" + last_animation)
		else:
			update_animation()
			animations.set_frame_and_progress(int(_moving_gait_phase), fmod(_moving_gait_phase, 1.0))

func _update_moving_throw(delta: float):
	if not is_attacking or velocity.is_zero_approx():
		moving_throw.hide()
		animations.show()
		return
	var action_index: int = 1 if nominal_speed > speed else 0
	var gait_fps: float = 12.0 if action_index == 1 else 8.0
	_moving_gait_phase = fposmod(_moving_gait_phase + delta * gait_fps, 8.0)
	var direction_index: int = CARDINAL_DIRECTIONS.find(last_animation)
	var is_diagonal: bool = direction_index == -1
	if is_diagonal:
		direction_index = DIAGONAL_DIRECTIONS.find(last_animation)
	moving_throw.texture = MOVING_THROW_DIAGONAL if is_diagonal else moving_throw_cardinal
	var atlas_row: int = action_index * 32 + direction_index * 8 + int(_moving_gait_phase)
	# Each cell is a complete coherent pose. Only the arm uses the throw clock;
	# legs, pelvis, torso and hair use the current gait, with no horizontal splice.
	moving_throw.frame = atlas_row * 8 + animations.frame
	moving_throw.show()
	animations.hide()

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
	# The base Player scene can also be run directly with F6 (no scene owner).
	var projectile_parent = owner if owner != null else get_tree().current_scene
	projectile_parent.add_child(b)
	ray_cast.look_at(get_global_mouse_position())
	b.transform = ray_cast.global_transform
