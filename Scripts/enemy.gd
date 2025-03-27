extends CharacterBody2D

@onready var ray_cast: RayCast2D = $RayCast2D
@onready var dead_timer: Timer =$Timer/DeadTimer
@onready var attack_cooldown: Timer =$Timer/AttackCooldown
@onready var health: Label = $HP
@onready var progress_bar: ProgressBar = $ProgressBar

@export var speed = 100
@export var target: CharacterBody2D
@export var hp = 100
@export var damage = 10

var is_attacking = false

#Set target and initial hp bar value
func _ready():
	target = get_node("../Boyfriend")
	progress_bar.max_value = hp;
	SignalManager.enemy_attacking.connect(_on_enemy_attacking)
	SignalManager.attack_target.connect(target._on_enemy_attack)

func _process(delta):
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

#Moving the enemy to a specific location
func _physics_process(delta):
	ray_cast.look_at(target.position)
	if ray_cast.is_colliding() or hp <= 0 or is_attacking:
		velocity = Vector2.ZERO
	else:
		velocity = position.direction_to(target.position) * speed
	move_and_slide()

#Set useful values for the enemy
func set_spawn_values(target_body, hp_value, damage_value):
	target = target_body
	damage = damage_value
	hp = hp_value
	progress_bar.max_value = hp_value
	
#Stop movement and playing dead animation
func dead():
	velocity = Vector2.ZERO
	is_attacking = false
	$CollisionShape2D.set_deferred("disabled", true)
	dead_timer.start()
	SignalManager.defeated.emit()

#Delete the dead enemy after the animation
func _on_dead_timer_timeout():
	queue_free()

func _on_enemy_attacking(attacker):
	if attacker == self:
		is_attacking = true
