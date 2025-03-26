extends CanvasLayer

@onready var player_upgrades: GridContainer = $Panel/TabContainer/Player/ScrollContainer/GridContainer
@onready var target_upgrades: GridContainer = $Panel/TabContainer/Target/ScrollContainer/GridContainer
@onready var bonus_upgrades: GridContainer = $Panel/TabContainer/Bonus/ScrollContainer/GridContainer

func _ready():
	populate_tab("Player")
	populate_tab("Target")
	populate_tab("Bonus")

func populate_tab(type: String):
	var path = "res://Objects/Items/Beach/"+type+"/"
	var dir = DirAccess.open(path)
	if dir == null:
		return
	dir.list_dir_begin()
	var file = dir.get_next()
	while file != "":
		var item = load(path+"/"+file).instantiate()
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
