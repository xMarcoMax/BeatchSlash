extends CanvasLayer

# Titolo mostrato per ogni sub_category del CSV, nell'ordine di comparsa nel tab.
# Le sub_category non elencate compaiono in fondo con il loro nome grezzo.
const SECTION_TITLES := {
	"Shield": "Moralità",
	"Health": "Fedeltà",
}

# Tab con pochi oggetti: una sola griglia, senza intestazioni di sezione
const SECTIONLESS_TABS := ["Player", "Bonus"]

const ITEM_COLUMNS := 3
const HEADER_COLOR_PROPERTIES := ["font_color", "font_hover_color", "font_pressed_color",
	"font_hover_pressed_color", "font_focus_color"]

@onready var tab_container: TabContainer = %TabContainer
@onready var currency_label: Label = %CurrencyLabel
@onready var tab_sections := {
	"Player": %PlayerSections,
	"Target": %TargetSections,
	"Bonus": %BonusSections,
}

var arrow_icons: Dictionary = {}
var item_list: Array = []

func _ready():
	SignalManager.wave_purchase_item.connect(_on_wave_finished)
	SignalManager.currency_changed.connect(_on_currency_changed)
	SignalManager.update_health_shield.connect(_on_partner_health_changed)
	load_item_file()
	tab_container.set_tab_title(0, "Giocatore")
	populate_tab("Player")
	tab_container.set_tab_title(1, "Partner")
	populate_tab("Target")
	tab_container.set_tab_title(2, "Bonus")
	populate_tab("Bonus")
	_on_currency_changed(Global.currency)

func populate_tab(type: String):
	var items = item_list.filter(func(item: Item):
		return item.data["category"] == type)
	items.sort_custom(func(a: Item, b: Item): return a.data["order"] < b.data["order"])

	if type in SECTIONLESS_TABS:
		add_section(tab_sections[type], "", items)
		return

	var groups := {}
	for item: Item in items:
		if not groups.has(item.data["sub_category"]):
			groups[item.data["sub_category"]] = []
		groups[item.data["sub_category"]].append(item)

	var keys: Array = SECTION_TITLES.keys().filter(func(k): return groups.has(k))
	keys.append_array(groups.keys().filter(func(k): return not SECTION_TITLES.has(k)))
	for key in keys:
		add_section(tab_sections[type], SECTION_TITLES.get(key, key), groups[key])

func add_section(parent: VBoxContainer, title: String, items: Array):
	var section := VBoxContainer.new()
	section.add_theme_constant_override("separation", 8)
	parent.add_child(section)

	var grid := GridContainer.new()
	grid.name = "Items"
	grid.columns = ITEM_COLUMNS
	grid.add_theme_constant_override("h_separation", 10)
	grid.add_theme_constant_override("v_separation", 10)

	# L'intestazione è un pulsante a levetta: la freccia accanto al titolo comprime/espande la sezione
	if title != "":
		var header := Button.new()
		header.flat = true
		header.toggle_mode = true
		header.button_pressed = true
		header.focus_mode = Control.FOCUS_NONE
		header.alignment = HORIZONTAL_ALIGNMENT_LEFT
		header.text = title
		header.add_theme_font_override("font", tab_container.get_theme_font("font", "ShopTitleLabel"))
		header.add_theme_font_size_override("font_size", 24)
		for property in HEADER_COLOR_PROPERTIES:
			header.add_theme_color_override(property, Color.WHITE)
		header.toggled.connect(_set_section_expanded.bind(header, grid))
		_set_section_expanded(true, header, grid)
		section.add_child(header)
		section.add_child(HSeparator.new())
	section.add_child(grid)

	for item: Item in items:
		item.purchase_requested.connect(_purchase_item)
		grid.add_child(item)

func _set_section_expanded(expanded: bool, header: Button, grid: GridContainer):
	grid.visible = expanded
	header.icon = arrow_icon(expanded)

# Triangolo bianco: giù = sezione aperta, destra = sezione chiusa
func arrow_icon(expanded: bool) -> ImageTexture:
	if not arrow_icons.has(expanded):
		var img := Image.create(18, 18, false, Image.FORMAT_RGBA8)
		for i in 9:
			for j in range(i, 18 - i):
				img.set_pixelv(Vector2i(j, i + 4) if expanded else Vector2i(i + 4, j), Color.WHITE)
		arrow_icons[expanded] = ImageTexture.create_from_image(img)
	return arrow_icons[expanded]

# Fine ondata: ogni oggetto conosce l'ondata appena finita (sblocchi, attese e prezzi dipendono da lei);
# gli oggetti temporanei attivi perdono un'ondata, a zero il loro effetto viene tolto
func _on_wave_finished(wave: int):
	for item: Item in item_list:
		item.wave = wave
		if item.waves_left > 0:
			item.waves_left -= 1
			if item.waves_left == 0:
				SignalManager.item_expired.emit(item.get_data())
	_refresh_items()

func _on_button_pressed():
	Global.is_in_purchase = false
	Global.purchase_just_closed = true
	visible = false

# Valuta cambiata (monete guadagnate o spese): aggiorna il saldo e i pulsanti
func _on_currency_changed(value: int):
	currency_label.text = "Valuta: %d¢" % value
	_refresh_items()

# Moralità o fedeltà cambiate: un ripristino inutile (barra già piena) non si può comprare
func _on_partner_health_changed(_hp, _shield):
	_refresh_items()

func _refresh_items():
	for item: Item in item_list:
		item.useless = _is_useless(item)
		item.refresh(Global.currency)

func _is_useless(item: Item) -> bool:
	if item.data["effect"] != "restore":
		return false
	var partner = get_tree().get_first_node_in_group("target")
	if partner == null or partner.max_hp == null:
		return false
	if item.data["sub_category"] == "Shield":
		return partner.shield >= partner.max_shield
	return partner.hp >= partner.max_hp

func _purchase_item(item: Item):
	if not item.can_buy(Global.currency):
		return
	var cost := item.price() # prima del conteggio: il prezzo dipende dagli acquisti già fatti
	item.purchases += 1
	item.bought_wave = item.wave
	var data = item.get_data()
	item.waves_left = data["duration"]
	# Il cambio di valuta aggiorna tutte le schede, compreso il contatore di questa
	Global.currency -= cost

	match data["category"]:
		"Player":
			SignalManager.item_player_purchased.emit(data)
		"Target":
			SignalManager.item_target_purchased.emit(data)
		"Bonus":
			SignalManager.item_bonus_purchased.emit(data)

func load_item_file():
	var file = FileAccess.open("res://Files/item_list.csv", FileAccess.READ)
	var item_scene: PackedScene = load("res://Objects/Items/item.tscn")
	file.get_csv_line(";")

	while not file.eof_reached():
		var columns = file.get_csv_line(";")
		if columns.size() < 15 or columns[0] == "":
			continue
		var row := {
			"id": columns[0],
			"name": columns[1],
			"description": columns[2],
			"bonus": float(columns[3]),
			"order": int(columns[4]),
			"category": columns[5],
			"sub_category": columns[6],
			"price": int(columns[8]),
			"max_purchases": int(columns[9]),
			"effect": columns[10],
			"duration": int(columns[11]),
			"min_wave": int(columns[12]),
			"every": int(columns[13]),
			"cooldown": int(columns[14]),
		}
		if not tab_sections.has(row["category"]):
			push_warning("item_list.csv: categoria sconosciuta '%s' per %s, riga ignorata" % [row["category"], row["id"]])
			continue

		var item: Item = item_scene.instantiate()
		item.init_nodes()
		item.setup(row, get_image(columns[7]), Global.currency)
		item_list.append(item)

# Il CSV indica un file di Assets/Icons/ oppure un percorso res:// completo
func get_image(file: String) -> Texture2D:
	var image = file if file.begins_with("res://") else "res://Assets/Icons/" + file
	var texture = load(image)
	return texture
