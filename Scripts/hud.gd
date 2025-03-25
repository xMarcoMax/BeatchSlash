extends CanvasLayer

@onready var health_label: Label =$HealthAndWave/Health
@onready var wave_label: Label = $HealthAndWave/Wave
@onready var defeated_label: Label = $DefeatedAndRemain/EnemyDefeated
@onready var record_label: Label = $DefeatedAndRemain/EnemyRemain

func _ready():
	SignalManager.update_health_shield.connect(set_values)

func set_wave(value):
	wave_label.text = "Ondata n°: "+str(value)

func set_defeated(value):
	defeated_label.text = "Nemici sconfitti: "+str(value)

func set_remain(value):
	record_label.text = "Nemici rimasti: "+str(value)

func set_values(health, shield):
	health = 0 if health < 0 else health
	shield = 0 if shield < 0 else shield
	health_label.text = "Morale e Fedeltà: " + str(shield) + "|" + str(health)
