extends StaticBody2D

@onready var area: Area2D = $Area2D
@onready var shopkeeper: AnimatedSprite2D = $Shopkeeper
@onready var gesture_timer: Timer = $GestureTimer
@onready var upgrades_text: RichTextLabel = get_node_or_null("../UI/HUD/UpgradesInteract")
@onready var wave_timer: Timer = get_node_or_null("../NextWaveTimer")
@onready var purchase: CanvasLayer = get_node_or_null("../UI/UpgradesPurchase")

var player_in_range = false
var last_gesture: StringName = &""


func _ready():
	area.body_entered.connect(_on_body_entered)
	area.body_exited.connect(_on_body_exited)
	gesture_timer.timeout.connect(_on_gesture_timer_timeout)
	shopkeeper.animation_finished.connect(_on_shopkeeper_animation_finished)
	shopkeeper.play(&"idle")
	gesture_timer.start(randf_range(5.0, 10.0))
	Global.purchase_just_closed = false


func _input(event):
	if event.is_action_pressed("buy_upgrades") and _can_purchase() and not purchase.visible:
		Global.is_in_purchase = true
		Global.purchase_just_closed = false
		purchase.visible = true
		SignalManager.purchase_item.emit()
		_update_purchase_state()
	elif event.is_action_pressed("esc") and purchase != null and purchase.visible:
		_close_purchase()
		Global.purchase_just_closed = true


func _process(_delta):
	_update_purchase_state()


func _can_purchase() -> bool:
	return player_in_range and wave_timer != null and not wave_timer.is_stopped() and purchase != null


func _update_purchase_state():
	var available := _can_purchase()
	if purchase != null and purchase.visible and not available:
		_close_purchase()
	if upgrades_text != null:
		upgrades_text.visible = available and not purchase.visible


func _close_purchase():
	purchase.visible = false
	Global.is_in_purchase = false


func _on_body_entered(body):
	if body.is_in_group("player"):
		player_in_range = true
		_update_purchase_state()


func _on_body_exited(body):
	if body.is_in_group("player"):
		player_in_range = false
		_update_purchase_state()


func _on_gesture_timer_timeout():
	var gestures: Array[StringName] = [&"clean_glass", &"wipe_counter"]
	gestures.erase(last_gesture)
	last_gesture = gestures.pick_random()
	shopkeeper.play(last_gesture)


func _on_shopkeeper_animation_finished():
	shopkeeper.play(&"idle")
	gesture_timer.start(randf_range(5.0, 10.0))
