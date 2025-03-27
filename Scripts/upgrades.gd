extends StaticBody2D

@onready var area: Area2D = $Area2D
@onready var sprite: Sprite2D = $Sprite2D
@onready var shape: CollisionShape2D = $CollisionShape2D
@onready var upgrades_text: RichTextLabel = $"../UI/HUD/UpgradesInteract"
@onready var wave_timer: Timer = $"../NextWaveTimer"
@onready var purchase: CanvasLayer = $"../UI/UpgradesPurchase"

var player_in_range = false

func _ready():
	area.body_entered.connect(_on_body_entered)
	area.body_exited.connect(_on_body_exited)

func _input(event):
	if event.is_action_pressed("buy_upgrades") and !wave_timer.is_stopped():
		purchase.visible = true
		SignalManager.purchase_item.emit()
	elif event.is_action_pressed("esc"):
		purchase.visible = false

func _process(delta):
	if wave_timer.is_stopped() and player_in_range:
		upgrades_text.visible = false
		purchase.visible = false
		player_in_range = false

func _on_body_entered(body):
	if body.is_in_group("player") and !wave_timer.is_stopped():
		upgrades_text.visible = true
		player_in_range = true
		
func _on_body_exited(body):
	if body.is_in_group("player"):
		upgrades_text.visible = false
		player_in_range = false
