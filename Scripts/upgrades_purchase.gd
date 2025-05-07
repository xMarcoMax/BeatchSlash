extends CanvasLayer

@onready var tab_container: TabContainer = $Panel/TabContainer
@onready var player_upgrades: GridContainer = $Panel/TabContainer/Player/ScrollContainer/GridContainer
@onready var target_upgrades: GridContainer = $Panel/TabContainer/Target/ScrollContainer/GridContainer
@onready var bonus_upgrades: GridContainer = $Panel/TabContainer/Bonus/ScrollContainer/GridContainer

var damage_item

func _ready():
	#Set segnale disponibilità ogni 5 ondate del bonus di aumento danni
	SignalManager.wave_purchase_item.connect(damage_item_availability)
	tab_container.set_tab_title(0, "Giocatore")
	populate_tab("Player")
	tab_container.set_tab_title(1, "Partner")
	populate_tab("Target")
	tab_container.set_tab_title(2, "Bonus")
	populate_tab("Bonus")

func populate_tab(type: String):
	var path = "res://Objects/Items/Beach/"+type+"/"
	var dir = DirAccess.open(path)
	if dir == null:
		return
	dir.list_dir_begin()
	var file = dir.get_next()
	
	#Recupero gli item, li ordino e poi li carico
	var items = []
	while file != "":
		var item = load(path+"/"+file).instantiate()
		if file == "damage_item.tscn":
			damage_item = item
		items.append(item)
		
		file = dir.get_next()
	dir.list_dir_end()
	items.sort_custom(func(a, b): return a.order < b.order)
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
	var button = get_viewport().gui_get_focus_owner()
	var item = button.get_parent().get_parent()
	var data = item.get_data()
	
	SignalManager.item_purchased.emit(data)
