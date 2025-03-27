extends CanvasLayer

@onready var tab_container: TabContainer = $Panel/TabContainer
@onready var player_upgrades: GridContainer = $Panel/TabContainer/Player/ScrollContainer/GridContainer
@onready var target_upgrades: GridContainer = $Panel/TabContainer/Target/ScrollContainer/GridContainer
@onready var bonus_upgrades: GridContainer = $Panel/TabContainer/Bonus/ScrollContainer/GridContainer

var wave_number

func _ready():
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
	while file != "":
		var scene = load(path+"/"+file)
		var item = scene.instantiate()
		var image = item.get_node("VBoxContainer").get_node("Image")
		image.pressed.connect(_purchase_item)
		match type:
			"Player":
				player_upgrades.add_child(item)
			"Target":
				target_upgrades.add_child(item)
			"Bonus":
				bonus_upgrades.add_child(item)
		file = dir.get_next()
	dir.list_dir_end()


func _on_button_pressed():
	visible = false

func _purchase_item():
	print("Item Acquistato")
