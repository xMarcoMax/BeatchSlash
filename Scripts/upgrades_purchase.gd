extends CanvasLayer

# Sezioni di ogni tab Partner: titolo e righe (sub_category) che le compongono, nell'ordine di comparsa.
# Una sub_category non elencata compare in una sezione a parte in fondo, con il suo nome grezzo.
const SECTIONS := {
	"Target": [{"title": "Moralità e Fedeltà", "rows": ["Shield", "Health", "Both"]}],
}

# Tab con pochi oggetti: una sola sezione senza intestazione e una sola riga
const SECTIONLESS_TABS := ["Player", "Bonus"]

# Icona a inizio riga, per chiave di riga (sub_category o, nei tab senza sezioni, categoria).
# Le righe senza icona propria usano il segnaposto.
const ROW_ICONS := {
	"Shield": "res://Assets/Icons/shield.png",
	"Health": "res://Assets/Icons/health.png",
	"Both": "res://Assets/Icons/shield_health.png",
	"Player": "res://Assets/Icons/row_player.png",
	"Bonus": "res://Assets/Icons/row_bonus.png",
}
const PLACEHOLDER_ROW_ICON := "res://Assets/icon.svg"
const ROW_ICON_SIZE := 52

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
		add_section(tab_sections[type], "", [{"key": type, "items": items}])
		return

	var groups := {}
	for item: Item in items:
		if not groups.has(item.data["sub_category"]):
			groups[item.data["sub_category"]] = []
		groups[item.data["sub_category"]].append(item)

	var listed := []
	for section: Dictionary in SECTIONS.get(type, []):
		var rows := []
		for key: String in section["rows"]:
			listed.append(key)
			if groups.has(key):
				rows.append({"key": key, "items": groups[key]})
		if not rows.is_empty():
			add_section(tab_sections[type], section["title"], rows)
	for key in groups.keys():
		if not listed.has(key):
			add_section(tab_sections[type], key, [{"key": key, "items": groups[key]}])

# Una sezione ha un'intestazione a levetta (se ha un titolo) e le sue righe una sotto l'altra, divise da un separatore
func add_section(parent: VBoxContainer, title: String, rows: Array):
	var section := VBoxContainer.new()
	section.add_theme_constant_override("separation", 8)
	parent.add_child(section)

	var body := VBoxContainer.new()
	body.name = "Rows"
	body.add_theme_constant_override("separation", 10)

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
		header.toggled.connect(_set_section_expanded.bind(header, body))
		_set_section_expanded(true, header, body)
		section.add_child(header)
		section.add_child(HSeparator.new())
	section.add_child(body)

	for i in rows.size():
		if i > 0:
			body.add_child(HSeparator.new())
		add_row(body, rows[i]["key"], rows[i]["items"])

# Una riga: l'icona di riga a sinistra e la griglia delle schede a destra
func add_row(parent: VBoxContainer, key: String, items: Array):
	var row := HBoxContainer.new()
	row.name = "Row_" + key
	row.add_theme_constant_override("separation", 12)
	parent.add_child(row)

	var icon := TextureRect.new()
	icon.name = "RowIcon"
	icon.texture = load(ROW_ICONS.get(key, PLACEHOLDER_ROW_ICON))
	icon.custom_minimum_size = Vector2(ROW_ICON_SIZE, ROW_ICON_SIZE)
	icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	icon.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	icon.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(icon)

	var grid := GridContainer.new()
	grid.name = "Items"
	grid.columns = ITEM_COLUMNS
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	grid.add_theme_constant_override("h_separation", 10)
	grid.add_theme_constant_override("v_separation", 10)
	row.add_child(grid)

	for item: Item in items:
		item.purchase_requested.connect(_purchase_item)
		grid.add_child(item)

func _set_section_expanded(expanded: bool, header: Button, body: Control):
	body.visible = expanded
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

# Moralità o fedeltà cambiate: un ripristino inutile (barra già piena, o entrambe per i pacchetti) non si può comprare
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
	var shield_full = partner.shield >= partner.max_shield
	var health_full = partner.hp >= partner.max_hp
	match item.data["sub_category"]:
		"Shield":
			return shield_full
		"Both":
			return shield_full and health_full
	return health_full

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
