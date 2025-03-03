extends CanvasLayer

@onready var health =$HealthAndWave/Health
@onready var wave = $HealthAndWave/Wave
@onready var defeated = $DefeatedAndRemain/EnemyDefeated
@onready var record = $DefeatedAndRemain/EnemyRemain

func set_health(value):
	health.text = "Salute rimasta: " + str(value)

func set_wave(value):
	wave.text = "Ondata n°: "+str(value)

func set_defeated(value):
	defeated.text = "Nemici sconfitti: "+str(value)

func set_remain(value):
	record.text = "Nemici rimasti: "+str(value)
