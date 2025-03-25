extends CanvasLayer

@onready var player_upgrades: GridContainer = $Panel/TabContainer/Player/ScrollContainer/GridContainer
@onready var target_upgrades: GridContainer = $Panel/TabContainer/Target/ScrollContainer/GridContainer
@onready var bonus_upgrades: GridContainer = $Panel/TabContainer/Bonus/ScrollContainer/GridContainer

var item
func _ready():
	#caricherò gli item da qui
	#item = load("res://Objects/item.tscn").instantiate()
	populate_player_tab()
	populate_target_tab()
	populate_bonus_tab()

func populate_player_tab():
	for i in range(20):
		item = load("res://Objects/item.tscn").instantiate()
		var image = item.get_node("Image")
		image.pressed.connect(_purchase_item)
		player_upgrades.add_child(item)
		
func populate_target_tab():
	for i in range(20):
		item = load("res://Objects/item.tscn").instantiate()
		var image = item.get_node("Image")
		image.pressed.connect(_purchase_item)
		target_upgrades.add_child(item)
		
func populate_bonus_tab():
	for i in range(20):
		item = load("res://Objects/item.tscn").instantiate()
		var image = item.get_node("Image")
		image.pressed.connect(_purchase_item)
		bonus_upgrades.add_child(item)

func _on_button_pressed():
	visible = false

func _purchase_item():
	print("Item Acquistato")
