@tool
extends "res://addons/godot_ai/testing/test_suite.gd"

# Regole del negozio su Item: prezzo crescente, sblocco per ondata, "every" e "cooldown".

func suite_name() -> String:
	return "shop_items"


# Item non è @tool: nell'editor lo script è un segnaposto. Eseguire con Godot da riga di comando (vedi Docs/GODOT.md, sezione 25).
func _in_editor() -> bool:
	if Engine.is_editor_hint():
		skip("Item non è @tool: eseguire il test a runtime")
		return true
	return false


func _item(price: int, max_purchases := 0, min_wave := 0, every := 0, cooldown := 0) -> Item:
	var item: Item = load("res://Objects/Items/item.tscn").instantiate()
	item.init_nodes()
	item.setup({"name": "t", "description": "d", "price": price, "max_purchases": max_purchases,
		"min_wave": min_wave, "every": every, "cooldown": cooldown}, null, 1000000)
	return item


func test_unlimited_price_rises_25_percent_every_5_waves() -> void:
	if _in_editor():
		return
	var item := _item(100)
	var expected := {1: 100, 4: 100, 5: 125, 9: 125, 10: 155, 15: 195, 20: 245}
	for wave: int in expected:
		item.wave = wave
		assert_eq(item.price(), expected[wave], "Prezzo all'ondata %d" % wave)
	item.free()


func test_limited_price_rises_25_percent_per_level_not_per_wave() -> void:
	if _in_editor():
		return
	var item := _item(200, 4)
	item.wave = 30
	var expected := [200, 250, 315, 390]
	for level in expected.size():
		item.purchases = level
		assert_eq(item.price(), expected[level], "Prezzo del livello %d" % (level + 1))
	item.free()


func test_min_wave_locks_until_the_pause_after_that_wave() -> void:
	if _in_editor():
		return
	var item := _item(100, 2, 4)
	item.wave = 3
	assert_false(item.can_buy(1000000), "Prima dell'ondata di sblocco non si compra")
	assert_eq(item.lock_text(), "Acquistabile dopo l'ondata 4")
	item.wave = 4
	assert_true(item.can_buy(1000000), "Nella pausa dopo l'ondata di sblocco si compra")
	assert_eq(item.lock_text(), "")
	item.free()


func test_every_allows_only_multiples_of_n_and_reports_the_wait() -> void:
	if _in_editor():
		return
	var item := _item(100, 0, 5, 5)
	var expected := {5: 0, 6: 4, 9: 1, 10: 0}
	for wave: int in expected:
		item.wave = wave
		assert_eq(item.wait_waves(), expected[wave], "Attesa all'ondata %d" % wave)
		assert_eq(item.can_buy(1000000), expected[wave] == 0)
	item.wave = 9
	assert_eq(item.lock_text(), "Acquistabile tra 1 ondata")
	item.wave = 6
	assert_eq(item.lock_text(), "Acquistabile tra 4 ondate")
	item.free()


func test_cooldown_skips_the_next_pause_then_stays_available() -> void:
	if _in_editor():
		return
	var item := _item(100, 0, 5, 0, 1)
	item.wave = 5
	assert_true(item.can_buy(1000000))
	item.bought_wave = 5
	assert_eq(item.lock_text(), "Acquistabile tra 2 ondate", "Subito dopo l'acquisto")
	item.wave = 6
	assert_false(item.can_buy(1000000), "Nella pausa dopo l'ondata successiva non è acquistabile")
	assert_eq(item.lock_text(), "Acquistabile tra 1 ondata")
	item.wave = 7
	assert_true(item.can_buy(1000000), "Due ondate dopo torna acquistabile")
	item.wave = 12
	assert_true(item.can_buy(1000000), "Se non lo si compra resta acquistabile")
	item.free()


func test_catalog_loads_with_the_new_columns() -> void:
	if _in_editor():
		return
	var file := FileAccess.open("res://Files/item_list.csv", FileAccess.READ)
	assert_true(file != null, "Il catalogo deve esistere")
	var header := file.get_csv_line(";")
	assert_eq(header.size(), 15, "Il catalogo ha 15 colonne")
	assert_eq(header.slice(12), PackedStringArray(["min_wave", "every", "cooldown"]))


# Righe del catalogo per id: colonne id, price (8 prima del cambio di colonna: indici letti dall'intestazione)
func _catalog() -> Dictionary:
	var file := FileAccess.open("res://Files/item_list.csv", FileAccess.READ)
	var header := file.get_csv_line(";")
	var rows := {}
	while not file.eof_reached():
		var columns := file.get_csv_line(";")
		if columns.size() < header.size() or columns[0] == "":
			continue
		var row := {}
		for i in header.size():
			row[header[i]] = columns[i]
		rows[columns[0]] = row
	return rows


func test_both_packs_cost_more_than_their_two_singles_and_are_a_reward() -> void:
	if _in_editor():
		return
	var rows := _catalog()
	var tiers := {"little": [70, 0], "medium": [120, 0], "large": [240, 10]}
	for tier: String in tiers:
		var pack: Dictionary = rows[tier + "_both"]
		var singles: int = int(rows[tier + "_shield"]["price"]) + int(rows[tier + "_health"]["price"])
		assert_eq(int(pack["price"]), tiers[tier][0], "Prezzo del pacchetto " + tier)
		assert_true(int(pack["price"]) > singles, "Il pacchetto costa più dei due singoli: " + tier)
		assert_eq(pack["sub_category"], "Both")
		assert_eq(pack["effect"], "restore")
		assert_eq(int(pack["every"]), 5, "Solo dopo le ondate multiple di 5")
		assert_eq(int(pack["min_wave"]), tiers[tier][1], "Sblocco del pacchetto " + tier)
		assert_eq(int(pack["max_purchases"]), 0)


func test_biggest_pack_is_locked_until_wave_10_and_rises_with_waves() -> void:
	if _in_editor():
		return
	var pack: Dictionary = _catalog()["large_both"]
	var item := _item(int(pack["price"]), int(pack["max_purchases"]), int(pack["min_wave"]), int(pack["every"]))
	item.wave = 5
	assert_false(item.can_buy(1000000), "Dopo l'ondata 5 il 100% non è acquistabile")
	assert_eq(item.lock_text(), "Acquistabile dopo l'ondata 10")
	item.wave = 10
	assert_true(item.can_buy(1000000))
	assert_eq(item.price(), 375, "A ondata 10 il prezzo è salito due volte del 25%")
	item.wave = 11
	assert_false(item.can_buy(1000000))
	item.free()

