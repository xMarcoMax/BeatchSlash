extends CanvasLayer

@onready var health: Label =$HealthAndWave/Health
@onready var wave: Label = $HealthAndWave/Wave
@onready var defeated: Label = $DefeatedAndRemain/EnemyDefeated
@onready var record: Label = $DefeatedAndRemain/EnemyRemain

func _ready():
	SignalManager.update_health.connect(set_health)

func set_health(value):
	health.text = "Salute rimasta: " + str(value)

func set_wave(value):
	wave.text = "Ondata n°: "+str(value)

func set_defeated(value):
	defeated.text = "Nemici sconfitti: "+str(value)

func set_remain(value):
	record.text = "Nemici rimasti: "+str(value)
