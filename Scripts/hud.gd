extends CanvasLayer

@onready var health =$VBoxContainer/Health
@onready var wave = $VBoxContainer/Wave
@onready var defeated = $VBoxContainer2/EnemyDefeated
@onready var record = $VBoxContainer2/MaxDefeated

func set_health(value):
	health.text = "Salute rimasta: " + str(value)

func set_wave(value):
	wave.text = "Ondata n°: "+str(value)

func set_defeated(value):
	defeated.text = "Nemici sconfitti: "+str(value)

func set_record(value):
	record.text = "Record nemici sconfitti: "+str(value)
