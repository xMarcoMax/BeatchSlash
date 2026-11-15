@tool
extends "res://addons/godot_ai/testing/test_suite.gd"


func suite_name() -> String:
	return "shop"


func test_buy_requires_range_and_purchase_window() -> void:
	var added_actions: Array[StringName] = []
	for action in [&"buy_upgrades", &"esc"]:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
			added_actions.append(action)
	var fixture = _make_fixture()
	var shop = fixture.shop
	var event := InputEventAction.new()
	event.action = &"buy_upgrades"
	event.pressed = true
	fixture.wave_timer.start(30.0)
	shop._input(event)
	assert_false(fixture.purchase.visible, "F deve essere ignorato fuori dall'area frontale")
	shop.player_in_range = true
	fixture.wave_timer.stop()
	shop._input(event)
	assert_false(fixture.purchase.visible, "F deve essere ignorato durante l'ondata")
	fixture.wave_timer.start(30.0)
	assert_true(shop._can_purchase(), "Il negozio deve essere accessibile dalla sua area tra le ondate")
	for action in added_actions:
		InputMap.erase_action(action)


func test_player_already_near_sees_next_purchase_window() -> void:
	var fixture = _make_fixture()
	var shop = fixture.shop
	var player := CharacterBody2D.new()
	track(player)
	player.add_to_group(&"player")
	shop._on_body_entered(player)
	assert_true(shop.player_in_range, "La prossimità deve essere registrata anche durante l'ondata")
	assert_false(fixture.prompt.visible, "L'invito deve restare nascosto durante l'ondata")
	fixture.wave_timer.start(30.0)
	shop._process(0.0)
	assert_true(fixture.prompt.visible, "L'invito deve apparire senza dover uscire e rientrare")
	fixture.wave_timer.stop()
	shop._process(0.0)
	assert_true(shop.player_in_range, "La fine degli acquisti deve conservare la prossimità reale")
	assert_false(fixture.prompt.visible, "L'invito deve sparire alla nuova ondata")
	shop._on_body_exited(player)
	assert_false(shop.player_in_range, "L'uscita del Player deve rimuovere la prossimità")


func test_gestures_return_to_idle_without_immediate_repeat() -> void:
	var fixture = _make_fixture()
	var shop = fixture.shop
	shop._on_gesture_timer_timeout()
	var first: StringName = fixture.shopkeeper.animation
	assert_true(first in [&"clean_glass", &"wipe_counter"], "Il timer deve avviare un gesto disponibile")
	shop._on_shopkeeper_animation_finished()
	assert_eq(fixture.shopkeeper.animation, &"idle", "Il gesto deve terminare nell'idle")
	assert_true(fixture.gesture_timer.time_left > 0.0, "Dopo il gesto deve iniziare una nuova pausa")
	assert_true(fixture.gesture_timer.wait_time >= 5.0 and fixture.gesture_timer.wait_time <= 10.0,
		"La pausa deve durare da cinque a dieci secondi")
	fixture.gesture_timer.stop()
	shop._on_gesture_timer_timeout()
	assert_true(fixture.shopkeeper.animation != first, "Due gesti consecutivi devono essere diversi")


func _make_fixture() -> Dictionary:
	var root := Node.new()
	track(root)
	var tree := Engine.get_main_loop() as SceneTree
	tree.root.add_child(root)
	var shop = load("res://Scripts/upgrades.gd").new()
	track(shop)
	var wave_timer := Timer.new()
	wave_timer.one_shot = true
	root.add_child(wave_timer)
	var gesture_timer := Timer.new()
	gesture_timer.one_shot = true
	root.add_child(gesture_timer)
	var purchase := CanvasLayer.new()
	purchase.visible = false
	root.add_child(purchase)
	var prompt := RichTextLabel.new()
	prompt.visible = false
	root.add_child(prompt)
	var shopkeeper := AnimatedSprite2D.new()
	var frames := SpriteFrames.new()
	for animation in [&"idle", &"clean_glass", &"wipe_counter"]:
		frames.add_animation(animation)
		frames.add_frame(animation, PlaceholderTexture2D.new())
		frames.set_animation_loop(animation, animation == &"idle")
	shopkeeper.sprite_frames = frames
	root.add_child(shopkeeper)
	shop.wave_timer = wave_timer
	shop.gesture_timer = gesture_timer
	shop.purchase = purchase
	shop.upgrades_text = prompt
	shop.shopkeeper = shopkeeper
	return {"shop": shop, "wave_timer": wave_timer, "gesture_timer": gesture_timer,
		"purchase": purchase, "prompt": prompt, "shopkeeper": shopkeeper}
