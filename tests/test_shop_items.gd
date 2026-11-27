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


func _item(price: int, max_purchases := 0, min_wave := 0, every := 0, cooldown := 0, per_waves := 0) -> Item:
	var item: Item = load("res://Objects/Items/item.tscn").instantiate()
	item.init_nodes()
	item.setup({"name": "t", "description": "d", "price": price, "max_purchases": max_purchases,
		"min_wave": min_wave, "every": every, "cooldown": cooldown, "per_waves": per_waves}, null, 1000000)
	return item


func test_unlimited_price_rises_15_percent_every_5_waves() -> void:
	if _in_editor():
		return
	var item := _item(100)
	var expected := {1: 100, 4: 100, 5: 115, 9: 115, 10: 130, 15: 150, 20: 175}
	for wave: int in expected:
		item.wave = wave
		assert_eq(item.price(), expected[wave], "Prezzo all'ondata %d" % wave)
	item.free()


func test_limited_price_rises_15_percent_per_level_not_per_wave() -> void:
	if _in_editor():
		return
	var item := _item(200, 4)
	item.wave = 30
	var expected := [200, 230, 265, 305]
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
	assert_eq(header.size(), 17, "Il catalogo ha 17 colonne")
	assert_eq(header.slice(12), PackedStringArray(["min_wave", "every", "cooldown", "per_waves", "group"]))


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


func test_both_pack_is_a_free_reward_every_5_waves() -> void:
	if _in_editor():
		return
	var rows := _catalog()
	assert_false(rows.has("little_both") or rows.has("medium_both"), "Resta solo il pacchetto al 100%")
	for tier in ["large"]:
		var pack: Dictionary = rows[tier + "_both"]
		assert_eq(int(pack["price"]), 0, "Premio gratuito: " + tier)
		assert_eq(pack["sub_category"], "Both")
		assert_eq(pack["effect"], "restore")
		assert_eq(int(pack["per_waves"]), 5)
		assert_eq(int(pack["min_wave"]), 5)
		assert_eq(int(pack["every"]), 0)
		assert_eq(pack["group"], "both")
		assert_eq(int(pack["max_purchases"]), 0)


func test_reward_group_gives_one_pick_per_credit() -> void:
	if _in_editor():
		return
	var pick := _item(0, 0, 5, 0, 0, 5)
	pick.wave = 4
	assert_false(pick.can_buy(0), "Prima dell'ondata 5 non c'è premio")
	assert_eq(pick.lock_text(), "Premio disponibile dopo l'ondata 5")
	pick.wave = 5
	pick.credit_purchases = 0
	assert_true(pick.can_buy(0), "Dopo l'ondata 5 si può scegliere (gratis)")
	pick.credit_purchases = 1
	assert_false(pick.can_buy(0), "Uno dei tre è già stato scelto: gli altri aspettano")
	assert_eq(pick.lock_text(), "Premio disponibile tra 5 ondate")
	pick.wave = 10
	assert_true(pick.can_buy(0), "Nuovo credito all'ondata 10")
	pick.free()



func test_block_text_explains_why_an_item_cannot_be_bought() -> void:
	if _in_editor():
		return
	var item := _item(100, 1)
	item.wave = 1
	assert_eq(item.block_text(40), "Ti servono ancora 60¢")
	assert_eq(item.block_text(1000), "", "Si può comprare: nessun motivo")
	item.useless = true
	assert_eq(item.block_text(1000), "Moralità e fedeltà sono già al massimo")
	item.useless = false
	item.waves_left = 2
	assert_eq(item.block_text(1000), "Già attivo: ancora 2 ondate")
	item.waves_left = 0
	item.purchases = 1
	assert_eq(item.block_text(1000), "Hai raggiunto il livello massimo")
	item.free()


func test_per_waves_gives_one_cumulative_purchase_every_n_waves() -> void:
	if _in_editor():
		return
	var item := _item(100, 0, 5, 0, 0, 5)
	item.wave = 4
	assert_false(item.can_buy(1000000), "Prima dell'ondata 5 non c'è credito")
	item.wave = 5
	assert_true(item.can_buy(1000000), "Dopo l'ondata 5 c'è un acquisto")
	item.wave = 7
	assert_true(item.can_buy(1000000), "Il credito non scade nelle pause dopo")
	item.purchases = 1
	assert_false(item.can_buy(1000000), "Comprato: il prossimo credito arriva all'ondata 10")
	assert_eq(item.lock_text(), "Acquistabile tra 3 ondate")
	item.wave = 10
	assert_true(item.can_buy(1000000), "Secondo credito all'ondata 10")
	item.purchases = 2
	item.wave = 14
	assert_eq(item.lock_text(), "Acquistabile tra 1 ondata")
	item.purchases = 0
	item.wave = 10
	assert_true(item.can_buy(1000000), "Credito non usato all'ondata 5: a ondata 10 ne restano due")
	item.purchases = 1
	assert_true(item.can_buy(1000000), "Secondo acquisto con il credito accumulato")
	item.purchases = 2
	assert_false(item.can_buy(1000000), "Crediti finiti")
	item.free()


func test_energy_bar_uses_the_credit_rule() -> void:
	if _in_editor():
		return
	var row: Dictionary = _catalog()["damage_item"]
	assert_eq(int(row["per_waves"]), 4)
	assert_eq(int(row["every"]), 0)
	assert_eq(int(row["min_wave"]), 4)
	assert_eq(int(row["price"]), 120)


func test_restore_rules() -> void:
	if _in_editor():
		return
	# 25%: basta che la barra non sia piena
	assert_eq(Item.restore_block(0.25, "Health", 100.0, 100.0, 100.0, 95.0), "")
	assert_eq(Item.restore_block(0.25, "Health", 100.0, 100.0, 100.0, 100.0), "La fedeltà è già al massimo")
	# con il massimo a 125 il 25% ripristina 31,25: si compra anche se ne mancano 30
	assert_eq(Item.restore_block(0.25, "Shield", 125.0, 95.0, 100.0, 100.0), "")
	# 50%: non deve ripristinare più di quanto manca (massimo 100: moralità a 50 sì, a 51 no)
	assert_eq(Item.restore_block(0.5, "Shield", 100.0, 50.0, 100.0, 100.0), "")
	assert_eq(Item.restore_block(0.5, "Shield", 100.0, 51.0, 100.0, 100.0), "Ripristinerebbe 50 di moralità, ma ne mancano 49")
	# 100%: la barra deve essere al 25% o meno
	assert_eq(Item.restore_block(1.0, "Shield", 100.0, 25.0, 100.0, 100.0), "")
	assert_eq(Item.restore_block(1.0, "Shield", 100.0, 0.0, 100.0, 100.0), "")
	assert_eq(Item.restore_block(1.0, "Shield", 100.0, 26.0, 100.0, 100.0), "Serve la moralità al 25% o meno")
	assert_eq(Item.restore_block(1.0, "Health", 100.0, 100.0, 125.0, 31.0), "")
	assert_eq(Item.restore_block(1.0, "Health", 100.0, 100.0, 125.0, 32.0), "Serve la fedeltà al 25% o meno")
	# Entrambi: stessa regola dei singoli, basta che la rispetti una delle due barre
	assert_eq(Item.restore_block(0.25, "Both", 100.0, 100.0, 100.0, 95.0), "")
	assert_eq(Item.restore_block(0.25, "Both", 100.0, 100.0, 100.0, 100.0), "Moralità e fedeltà sono già al massimo")
	assert_eq(Item.restore_block(0.5, "Both", 100.0, 40.0, 100.0, 100.0), "")
	assert_eq(Item.restore_block(0.5, "Both", 100.0, 80.0, 100.0, 40.0), "")
	assert_eq(Item.restore_block(0.5, "Both", 100.0, 80.0, 100.0, 70.0), "Ripristinerebbe più di quanto manca a entrambe le barre")
	# il premio (Entrambi al 100%) si usa comunque, basta che una barra non sia piena
	assert_eq(Item.restore_block(1.0, "Both", 100.0, 100.0, 100.0, 25.0), "")
	assert_eq(Item.restore_block(1.0, "Both", 100.0, 60.0, 100.0, 80.0), "")
	assert_eq(Item.restore_block(1.0, "Both", 100.0, 100.0, 100.0, 99.0), "")
	assert_eq(Item.restore_block(1.0, "Both", 100.0, 100.0, 100.0, 100.0), "Moralità e fedeltà sono già al massimo")