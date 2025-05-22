extends CanvasLayer

@onready var wave_label: Label = $Wave

@onready var points_label: Label = $PointsCurrency/Points
@onready var currency_label: Label = $PointsCurrency/Currency

@onready var defeated_label: Label = $DefeatedAndRemain/EnemyDefeated
@onready var record_label: Label = $DefeatedAndRemain/EnemyRemain

@onready var health_bar: ProgressBar = $HealthBar/Health
@onready var shield_bar: ProgressBar = $ShieldBar/Shield

var hp_value
var shield_value

func _ready():
	SignalManager.update_health_shield.connect(set_values)

func _process(delta):
	health_bar.value = hp_value
	shield_bar.value = shield_value

func set_wave(value):
	wave_label.text = "Ondata n°: "+str(value)

func set_defeated(value):
	defeated_label.text = "Nemici sconfitti: "+str(value)

func set_remain(value):
	record_label.text = "Nemici rimasti: "+str(value)

func set_points(value):
	points_label.text = "Punti: "+str(value)

func set_currency(value):
	currency_label.text = "Valuta: "+str(value)+"¢"

func set_values(health, shield):
	hp_value = 0 if health < 0 else health
	shield_value = 0 if shield < 0 else shield
	if health_bar.max_value == 1 and shield_bar.max_value == 1:
		health_bar.max_value = hp_value
		shield_bar.max_value = shield_value
