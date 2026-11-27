extends StaticBody2D

@onready var area: Area2D = $Area2D
@onready var shopkeeper: AnimatedSprite2D = $Shopkeeper
@onready var gesture_timer: Timer = $GestureTimer
@onready var upgrades_text: RichTextLabel = get_node_or_null("../UI/HUD/UpgradesInteract")
@onready var wave_timer: Timer = get_node_or_null("../NextWaveTimer")
@onready var purchase: CanvasLayer = get_node_or_null("../UI/UpgradesPurchase")
@onready var balloon: ShopBalloon = $Balloon

# Frasi di Sandro. Scompaiono tutte da sole; aprire il negozio o la fine della pausa zittiscono anche l'avviso dei prezzi in anticipo.
const THANKS_PURCHASE := "Grazie per l'acquisto!"
const THANKS_VISIT := "Grazie per la visita!"
const THANKS_TIME := 3.0
const PRICE_RISE := "L'inflazione colpisce! Stessa qualità, ma del %d%% in più!"
const PRICE_RISE_TIME := 4.0
const PRICE_RISE_FONT_SIZE := 34 # più piccolo del normale: la frase deve occupare poco più dei ringraziamenti

var player_in_range = false
var last_gesture: StringName = &""
var visit_purchased := false


func _ready():
	SignalManager.wave_purchase_item.connect(_on_wave_finished)
	SignalManager.item_player_purchased.connect(_on_item_purchased)
	SignalManager.item_target_purchased.connect(_on_item_purchased)
	SignalManager.item_bonus_purchased.connect(_on_item_purchased)
	if purchase != null:
		purchase.visibility_changed.connect(_on_purchase_visibility_changed)
	if wave_timer != null:
		wave_timer.timeout.connect(balloon.hush)
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
		# Vale solo per questo evento Esc (il menù di pausa lo legge subito dopo): non deve restare acceso e inghiottire il prossimo
		Global.purchase_just_closed = true
		get_tree().process_frame.connect(func(): Global.purchase_just_closed = false, CONNECT_ONE_SHOT)


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


# Pausa tra le ondate: se i prezzi sono appena saliti (ogni PRICE_WAVE_STEP ondate) Sandro lo dice
func _on_wave_finished(wave: int):
	if wave % Item.PRICE_WAVE_STEP == 0:
		balloon.say(PRICE_RISE % roundi(Item.PRICE_GROWTH * 100.0), PRICE_RISE_TIME, PRICE_RISE_FONT_SIZE)

func _on_item_purchased(_data):
	visit_purchased = true

# Aprire il negozio è interagire con Sandro (zittisce l'avviso); chiuderlo, in qualunque modo, lo fa ringraziare
func _on_purchase_visibility_changed():
	if purchase.visible:
		visit_purchased = false
		balloon.hush()
	else:
		balloon.say(THANKS_PURCHASE if visit_purchased else THANKS_VISIT, THANKS_TIME)

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
