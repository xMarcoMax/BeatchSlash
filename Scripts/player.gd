extends CharacterBody2D


@export var ball : PackedScene
@onready var ray_cast: RayCast2D = $RayCast2D
@onready var animations: AnimatedSprite2D = $AnimatedSprite2D
@onready var moving_throw: Sprite2D = $MovingThrow
@onready var throw_sound: AudioStreamPlayer = $ThrowSound
@export var damage = 10

# Part of the screen between the HUD bands, in global coordinates (set by the level): the player cannot leave it.
# The body extents are the visible sprite around its origin, so no part of the body goes under a band.
var play_area := Rect2()
const BODY_HALF_WIDTH = 40.0
const BODY_TOP = 95.0
const BODY_BOTTOM = 77.0

# Frame 3: the hand releases after 3 frames: 0.094 s at 32 FPS (fastest level), 0.375 s at 8 FPS (slowest).
@export_range(0, 7) var throw_release_frame: int = 3
# A new press is ignored (no throw, no animation) until the previous throw reaches this point (frame + progress):
# 5.5 is the arm about 30 degrees from the body, just before the arm-down frames 6-7.
@export_range(0.0, 8.0) var throw_recovery_frame: float = 5.5
signal throw_released

# Target FPS of the throw_* animations per level, played as a fraction of the FPS authored in player_frames.tres.
# Level 0 (start) = walk FPS, 1 = halfway, 2 = the original fast throw. The shop raises the level.
const THROW_FPS_LEVELS = [8.0, 16.0, 32.0]
var throw_speed_level = 0

# Walking speed per level (the run key doubles it): the player starts slower, the shop raises the level up to the old speed.
const SPEED_LEVELS = [320.0, 360.0, 400.0]
var speed_level = 0
var speed = SPEED_LEVELS[0]
var damage_base

# Atlas dei lanci in movimento: righe = azione*32 + direzione*8 + fase; ordine direzioni per atlas.
const MOVING_THROW_DIAGONAL = preload("res://Assets/Characters/Player/player_diagonals_moving_throw.png")
const CARDINAL_DIRECTIONS = ["up", "down", "right", "left"]
const DIAGONAL_DIRECTIONS = ["up_right", "up_left", "down_right", "down_left"]
@onready var moving_throw_cardinal: Texture2D = moving_throw.texture

var nominal_speed = speed
var last_animation = "down"
var is_attacking = false
var _throw_released = false
#Global point aimed at when the current throw started; the ball is released towards it
var throw_target := Vector2.ZERO
var _moving_gait_phase: float = 0.0

func _ready():
	Global.is_in_purchase = false
	damage_base = damage
	SignalManager.item_player_purchased.connect(_on_item_purchased)
	animations.frame_changed.connect(_on_animation_frame_changed)
	animations.animation_finished.connect(_on_animation_finished)
	animations.play("idle_" + last_animation)

@warning_ignore("unused_parameter")
func _physics_process(delta):
	# Game over scene: GameOverSequence moves her and picks her animations
	if Global.game_over_sequence:
		return
	if(!Global.is_in_purchase):
		get_input()
		_update_moving_throw(delta)
		update_animation()
		move_and_slide()
		if play_area.has_area():
			global_position = global_position.clamp(play_area.position + Vector2(BODY_HALF_WIDTH, BODY_TOP), play_area.end - Vector2(BODY_HALF_WIDTH, BODY_BOTTOM))

#Shop purchases for the player: damage adds a fraction of the starting damage, throw speed and walking speed go up one level
func _on_item_purchased(data: Dictionary):
	match data["effect"]:
		"damage":
			damage += roundi(damage_base * data["bonus"])
		"throw_speed":
			throw_speed_level = mini(throw_speed_level + 1, THROW_FPS_LEVELS.size() - 1)
		"move_speed":
			speed_level = mini(speed_level + 1, SPEED_LEVELS.size() - 1)
			speed = SPEED_LEVELS[speed_level]

#Input events (shoot, attack, etc.)
func _input(event):
	if Global.game_over_sequence:
		return
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
	if is_attacking and not _can_throw_again():
		return
	# Carry the current step into the throw, including its fractional progress.
	# Rapid follow-up throws keep the running gait clock instead of restarting it.
	if not is_attacking:
		_moving_gait_phase = 0.0
		if animations.animation.begins_with("walk_") or animations.animation.begins_with("dash_"):
			_moving_gait_phase = animations.frame + animations.frame_progress
	# The ball goes where the mouse was when the throw started, like the pose: the mouse may move before the release frame
	throw_target = mouse_position
	var aim = mouse_position - global_position
	if not aim.is_zero_approx():
		last_animation = Formulas.direction_name(aim)
	animations.stop()
	is_attacking = true
	_throw_released = false
	var throw_animation = "throw_" + last_animation
	var authored_fps = animations.sprite_frames.get_animation_speed(throw_animation)
	animations.play(throw_animation, THROW_FPS_LEVELS[throw_speed_level] / authored_fps)
	# Also supports release frame 0 when the animation was already on frame 0.
	_on_animation_frame_changed()

func _can_throw_again() -> bool:
	return _throw_released and animations.frame + animations.frame_progress >= throw_recovery_frame

func _on_animation_frame_changed():
	_update_moving_throw(0.0)
	if not is_attacking or _throw_released:
		return
	if animations.animation.begins_with("throw_") and animations.frame >= throw_release_frame:
		_throw_released = true
		# With the shop open the player cannot act: a throw already in progress ends without releasing the ball.
		# Existing projectile/raycast logic remains in shoot_sand().
		if not Global.is_in_purchase and not Global.game_over_sequence:
			shoot_sand(throw_target)
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

#Game over scene: a throw in progress ends at once without releasing the ball, then GameOverSequence takes over
func stop_acting():
	is_attacking = false
	_throw_released = true
	velocity = Vector2.ZERO
	moving_throw.hide()
	animations.show()

#Input movement direction
func get_input():
	# Not Input.get_vector: it reads raw axis values and applies the deadzone only to the whole vector,
	# so a drifting gamepad stick leaks into the other axis while a key is held (the player walks crooked).
	# get_action_strength applies each action's own deadzone.
	var direction = Vector2(
		Input.get_action_strength("ui_right") - Input.get_action_strength("ui_left"),
		Input.get_action_strength("ui_down") - Input.get_action_strength("ui_up")
	).limit_length(1.0)
	nominal_speed = speed * 2 if Input.is_action_pressed("run") else speed
	velocity = direction * nominal_speed

#Shooting sand ball
func shoot_sand(mouse_position):
	var b: Area2D = ball.instantiate()
	b.damage = damage
	# The base Player scene can also be run directly with F6 (no scene owner).
	var projectile_parent = owner if owner != null else get_parent()
	projectile_parent.add_child(b)
	ray_cast.look_at(mouse_position)
	b.global_transform = ray_cast.global_transform
	throw_sound.play()
