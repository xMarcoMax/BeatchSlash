extends CharacterBody2D

@onready var dead_timer: Timer =$Timer/DeadTimer
@onready var attack_cooldown: Timer =$Timer/AttackCooldown
@onready var health: Label = $HP
@onready var progress_bar: ProgressBar = $ProgressBar
@onready var animations: AnimatedSprite2D = $AnimatedSprite2D

@export var speed = 100
@export var target: CharacterBody2D
@export var hp = 100
@export var damage = 10

const REPATH_INTERVAL = 0.5
const WAYPOINT_RADIUS = 30.0
const SEPARATION_RADIUS = 110.0
const SEPARATION_WEIGHT = 1.5
#Each enemy walks to its own "slot" on the edge of the target's hit zone (radius 185 in boyfriend.tscn), not to the target's centre
const SLOT_RADIUS = 185.0
const SLOT_STEP = PI / 6.0
#Attackers stand at about 230 px from the target, so a slot is taken by whoever is within this arc of it and this distance
const SLOT_ARC = SLOT_STEP * 0.8
const SLOT_RING_MAX = 320.0
#Walking for STUCK_TIME seconds while shortening the path to its slot by less than this fraction of what it should: move to another slot
const STUCK_TIME = 0.6
const STUCK_PROGRESS_RATIO = 0.3
const MOTION_SMOOTHING = 6.0
const HIT_FLASH_TIME = 0.1
const HIT_STUN_TIME = 0.15
const HIT_KNOCKBACK = 220.0
const KNOCKBACK_DECAY = 1400.0
#Time from death to the puff: fall animation (8 frames at 12 FPS) plus about 1 s lying on the sand
const DEAD_LINGER_TIME = 1.7
#The puff hides the body, then the enemy is removed
const PUFF_COVER_TIME = 0.2
const PUFF_OFFSET = Vector2(0, 8)
const PUFF = preload("res://Objects/puff.tscn")
const HIT_FLASH_SHADER = preload("res://Assets/Characters/Enemy/hit_flash.gdshader")

#Set by level.gd at spawn; without it the enemy walks straight to the target
var pathfinder: Pathfinder
var path = PackedVector2Array()
var path_index = 0
var repath_timer = 0.0
var slot_angle = NAN
var stuck_time = 0.0
var stuck_remaining = 0.0
var blocked_normal = Vector2.ZERO
#Same side for the whole life, so every blocked enemy goes around obstacles the same way
var slide_side = 1.0 if randf() < 0.5 else -1.0
var move_speed = 0.0
var flash_left = 0.0
var stun_left = 0.0
var knockback = Vector2.ZERO
var hit_material: ShaderMaterial
var facing = Vector2.ZERO
var is_attacking = false

#Set target and initial hp bar value
func _ready():
	target = get_node("../Boyfriend")
	progress_bar.max_value = hp;
	# One material per enemy: the flash must not light up all the others
	hit_material = ShaderMaterial.new()
	hit_material.shader = HIT_FLASH_SHADER
	animations.material = hit_material
	SignalManager.enemy_attacking.connect(_on_enemy_attacking)
	SignalManager.enemy_left_target.connect(_on_enemy_left_target)

func _process(delta):
	flash_left = maxf(flash_left - delta, 0.0)
	hit_material.set_shader_parameter("flash", 1.0 if flash_left > 0.0 else 0.0)
	health.text = "Salute: 0" if hp <= 0 else "Salute: "+str(hp)
	progress_bar.value = hp
	set_healthbar_color()
	if is_attacking and attack_cooldown.is_stopped():
		attack()

func set_healthbar_color():
	var rateo = hp/progress_bar.max_value
	var bgcolor = StyleBoxFlat.new()
	var fillcolor = StyleBoxFlat.new()

	if rateo >= 0.5:
		bgcolor.bg_color = Color(0.00, 0.78, 0.00, 0.39)
		fillcolor.bg_color = Color(0.00, 0.78, 0.00)
	elif rateo < 0.5 and rateo >= 0.25:
		bgcolor.bg_color = Color(0.80, 0.53, 0.00, 0.39)
		fillcolor.bg_color = Color(0.80, 0.53, 0.00)
	else:
		bgcolor.bg_color = Color(0.78, 0.00, 0.00, 0.39)
		fillcolor.bg_color = Color(0.78, 0.00, 0.00)
	progress_bar.add_theme_stylebox_override("background", bgcolor)
	progress_bar.add_theme_stylebox_override("fill", fillcolor)
	progress_bar.queue_redraw() 

func attack():
	SignalManager.attack_target.emit(damage)
	attack_cooldown.start()

#Follow the path to the target, going around obstacles and other enemies
func _physics_process(delta):
	stun_left = maxf(stun_left - delta, 0.0)
	if hp <= 0 or is_attacking or stun_left > 0.0:
		velocity = Vector2.ZERO
		stuck_time = 0.0
	else:
		velocity = _steer(delta) * speed
	knockback = knockback.move_toward(Vector2.ZERO, KNOCKBACK_DECAY * delta)
	velocity += knockback
	move_and_slide()
	blocked_normal = get_slide_collision(0).get_normal() if get_slide_collision_count() > 0 else Vector2.ZERO
	update_animation(delta)

#Direction to the next waypoint of the path to the slot (straight to the slot while the path is unavailable), pushed away from nearby enemies
func _steer(delta) -> Vector2:
	if stuck_time == 0.0:
		stuck_remaining = _path_remaining()
	stuck_time += delta
	if stuck_time > STUCK_TIME:
		if stuck_remaining - _path_remaining() < speed * stuck_time * STUCK_PROGRESS_RATIO:
			slot_angle = _pick_slot(slot_angle)
			repath_timer = 0.0
		stuck_time = 0.0
	repath_timer -= delta
	if repath_timer <= 0.0:
		repath_timer = REPATH_INTERVAL + randf() * 0.2
		if is_nan(slot_angle) or _slot_taken(slot_angle):
			slot_angle = _pick_slot()
		path = pathfinder.find_path(global_position, _slot_point(slot_angle), _blockers()) if pathfinder else PackedVector2Array()
		path_index = 0
	while path_index < path.size() - 1 and global_position.distance_to(path[path_index]) < WAYPOINT_RADIUS:
		path_index += 1
	var goal = path[path_index] if path_index < path.size() else _slot_point(slot_angle)
	var direction = (global_position.direction_to(goal) + _separation() * SEPARATION_WEIGHT).limit_length(1.0)
	# Pushing into something (player, enemy): move along its surface at full speed instead of crawling
	if blocked_normal != Vector2.ZERO and direction.dot(blocked_normal) < 0.0:
		direction = direction.slide(blocked_normal)
		if direction.length() < 0.3:
			direction = blocked_normal.orthogonal() * slide_side
		direction = direction.normalized()
	return direction

#Standing bodies the path must go around: attacking enemies and the player
func _blockers() -> PackedVector2Array:
	var blockers = PackedVector2Array()
	for other in get_tree().get_nodes_in_group("enemy"):
		if other != self and other.is_attacking and other.hp > 0:
			blockers.append(other.global_position)
	for other in get_tree().get_nodes_in_group("player"):
		blockers.append(other.global_position)
	return blockers

#Length of the path still to walk to the slot (straight line while there is no path)
func _path_remaining() -> float:
	if path_index >= path.size():
		return global_position.distance_to(_slot_point(slot_angle))
	var remaining = global_position.distance_to(path[path_index])
	for i in range(path_index, path.size() - 1):
		remaining += path[i].distance_to(path[i + 1])
	return remaining

func _slot_point(angle) -> Vector2:
	return target.global_position + Vector2.from_angle(angle) * SLOT_RADIUS

#A slot is taken by the player, by any enemy already attacking, or by a living enemy near the ring that is closer to the target than this one
func _slot_taken(angle) -> bool:
	var center = target.global_position
	for other in get_tree().get_nodes_in_group("player"):
		if _blocks_slot(other, center, angle):
			return true
	for other in get_tree().get_nodes_in_group("enemy"):
		if other == self or other.hp <= 0:
			continue
		var closer = other.global_position.distance_to(center) < global_position.distance_to(center)
		if (other.is_attacking or closer) and _blocks_slot(other, center, angle):
			return true
	return false

func _blocks_slot(body, center, angle) -> bool:
	var offset = body.global_position - center
	return offset.length() < SLOT_RING_MAX and absf(angle_difference(offset.angle(), angle)) < SLOT_ARC

#First free slot starting from the side the enemy comes from, then alternating around the ring; skips `excluded` (a slot that did not work)
func _pick_slot(excluded = NAN) -> float:
	var base = target.global_position.angle_to_point(global_position)
	for i in range(13):
		var angle = base + ((i + 1) >> 1) * SLOT_STEP * (slide_side if i % 2 == 1 else -slide_side)
		if not _slot_taken(angle) and (is_nan(excluded) or absf(angle_difference(angle, excluded)) >= SLOT_ARC):
			return angle
	return base + SLOT_STEP * slide_side

#Push away from nearby living enemies and from the player, with a sideways component so two bodies facing each other slide past
func _separation() -> Vector2:
	var push = Vector2.ZERO
	for other in get_tree().get_nodes_in_group("enemy") + get_tree().get_nodes_in_group("player"):
		if other == self or (other.is_in_group("enemy") and other.hp <= 0):
			continue
		var offset = global_position - other.global_position
		var distance = offset.length()
		if distance > 0.0 and distance < SEPARATION_RADIUS:
			push += (offset + offset.orthogonal() * 0.5) / distance * (1.0 - distance / SEPARATION_RADIUS)
	return push

#Walk while moving, flirt when attacking, idle when stopped (target reached or blocked by another enemy)
func update_animation(delta):
	if hp <= 0:
		return
	var to_target = target.position - position
	var moved = get_real_velocity() - knockback
	# Smoothed so sliding jitter does not flip walk/idle or the facing direction every frame
	move_speed = lerpf(move_speed, moved.length(), 1.0 - exp(-MOTION_SMOOTHING * delta))
	if moved.length() > speed * 0.1:
		facing = moved.normalized() if facing == Vector2.ZERO else facing.lerp(moved.normalized(), 1.0 - exp(-MOTION_SMOOTHING * delta))
	if is_attacking:
		animations.play("flirt_" + Formulas.direction_name(to_target))
	elif move_speed < speed * 0.1 or facing == Vector2.ZERO:
		animations.play("idle_" + Formulas.direction_name(to_target))
	else:
		animations.play("walk_" + Formulas.direction_name(facing))

#Set useful values for the enemy
func set_spawn_values(target_body, hp_value, damage_value):
	target = target_body
	damage = damage_value
	hp = hp_value
	progress_bar.max_value = hp_value
	
#Damage with a white flash, a small push away from the hit and a short stun (no stun while flirting, so the attack is not cancelled)
func take_damage(amount, from_direction = Vector2.ZERO):
	if hp <= 0:
		return
	hp -= amount
	flash_left = HIT_FLASH_TIME
	knockback = from_direction.normalized() * HIT_KNOCKBACK
	if hp <= 0:
		dead()
	elif not is_attacking:
		stun_left = HIT_STUN_TIME

#Fall on the sand facing the direction she was looking at, then puff away after DEAD_LINGER_TIME
func dead():
	var looking = target.position - position if is_attacking or facing == Vector2.ZERO else facing
	velocity = Vector2.ZERO
	is_attacking = false
	$CollisionShape2D.set_deferred("disabled", true)
	progress_bar.hide()
	animations.play("dead_" + Formulas.direction_name(looking))
	dead_timer.start(DEAD_LINGER_TIME)
	SignalManager.defeated.emit()

#Puff of dust over the body, then delete the dead enemy
func _on_dead_timer_timeout():
	var puff = PUFF.instantiate()
	puff.position = position + PUFF_OFFSET
	get_parent().add_child(puff)
	await get_tree().create_timer(PUFF_COVER_TIME).timeout
	queue_free()

func _on_enemy_attacking(attacker):
	if attacker == self:
		is_attacking = true

func _on_enemy_left_target(enemy):
	if enemy == self:
		is_attacking = false
