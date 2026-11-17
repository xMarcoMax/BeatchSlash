extends CanvasLayer

# The bands cover the top and bottom of the screen: the play area (and the player) stays between them
@onready var top_band: Panel = $TopBand
@onready var bottom_band: Panel = $BottomBand

@onready var wave_label: Label = %WaveValue

@onready var points_label: Label = %PointsValue
@onready var currency_label: Label = %CurrencyValue

@onready var defeated_label: Label = %DefeatedValue
@onready var record_label: Label = %RemainValue

@onready var health_bar: ProgressBar = %Health
@onready var shield_bar: ProgressBar = %Shield
@onready var health_value: Label = %HealthValue
@onready var shield_value_label: Label = %ShieldValue

var hp_value
var shield_value

func _ready():
	SignalManager.update_health_shield.connect(set_values)
	SignalManager.update_max_health_shield.connect(set_max_values)
	SignalManager.currency_changed.connect(set_currency)

func _process(delta):
	health_bar.value = hp_value
	shield_bar.value = shield_value
	health_value.text = "%d / %d" % [ceili(hp_value), health_bar.max_value]
	shield_value_label.text = "%d / %d" % [ceili(shield_value), shield_bar.max_value]

func set_wave(value):
	wave_label.text = str(value)

func set_defeated(value):
	defeated_label.text = str(value)

func set_remain(value):
	record_label.text = str(value)

func set_points(value):
	points_label.text = str(value)

func set_currency(value):
	currency_label.text = str(value)

func set_max_values(max_health, max_shield):
	health_bar.max_value = max_health
	shield_bar.max_value = max_shield

func set_values(health, shield):
	hp_value = 0 if health < 0 else health
	shield_value = 0 if shield < 0 else shield
	if health_bar.max_value == 1 and shield_bar.max_value == 1:
		health_bar.max_value = hp_value
		shield_bar.max_value = shield_value
