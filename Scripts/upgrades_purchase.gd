extends CanvasLayer

@onready var tab_container: TabContainer = $Panel/TabContainer
@onready var player_upgrades: GridContainer = $Panel/TabContainer/Player/ScrollContainer/GridContainer
@onready var target_upgrades: GridContainer = $Panel/TabContainer/Target/ScrollContainer/GridContainer
@onready var bonus_upgrades: GridContainer = $Panel/TabContainer/Bonus/ScrollContainer/GridContainer

var damage_item: Item
var item_list: Array = []

func _ready():
	#Set segnale disponibilità ogni 5 ondate del bonus di aumento danni
	SignalManager.wave_purchase_item.connect(damage_item_availability)
	load_item_file()
	tab_container.set_tab_title(0, "Giocatore")
	populate_tab("Player")
	tab_container.set_tab_title(1, "Partner")
	populate_tab("Target")
	tab_container.set_tab_title(2, "Bonus")
	populate_tab("Bonus")

func populate_tab(type: String):
	var items = item_list.filter(func(item: Item): 
		return item.item_category == type)
	items.sort_custom(func(a: Item, b: Item): return a.item_order < b.item_order)
	add_items(items, type)

func add_items(items: Array, type: String):
	for item in items:
		var image = item.get_node("VBoxContainer").get_node("Image")
		image.pressed.connect(_purchase_item)
		match type:
			"Player":
				player_upgrades.add_child(item)
			"Target":
				target_upgrades.add_child(item)
			"Bonus":
				bonus_upgrades.add_child(item)

func damage_item_availability(wave):
	var d = player_upgrades.get_children().filter(func(item): return item == damage_item).get(0)
	d.visible = (wave % 5) == 0

func _on_button_pressed():
	Global.is_in_purchase = false
	Global.purchase_just_closed = true
	visible = false

func _purchase_item():
	print("CLICK")
	var button = get_viewport().gui_get_focus_owner()
	var item = button.get_parent().get_parent()
	var data = item.get_data()
	
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
		if columns.size() < 8:
			continue
		var id = columns[0]
		var name = columns[1]
		var description = columns[2]
		var bonus = float(columns[3])
		var order = int(columns[4])
		var category = columns[5]
		var sub_category = columns[6]
		var image = get_image(columns[7])
		
		var item: Item = item_scene.instantiate()
		item.init_nodes()
		item.set_item_data(name, image, description, bonus, order, category, sub_category)
		if id == "damage_item":
			damage_item = item
		item_list.append(item)

func get_image(file: String) -> Texture2D:
	var image = "res://Assets/Sprites/"+file
	var texture = load(image)
	return texture

func update_columns():
	var width = damage_item.custom_minimum_size.x;
	var available = player_upgrades.get_size().x
	var columns = max(1, int(available/width))
	player_upgrades.columns = columns
	target_upgrades.columns = columns
	bonus_upgrades.columns = columns
