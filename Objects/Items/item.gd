extends PanelContainer

class_name Item

var item_name
var item_image
var item_description

@export var item_bonus: float = 0
@export var item_order: int = 0
@export var item_category: String = ""
@export var item_sub_category: String = ""

func init_nodes():
	item_name = get_node("VBoxContainer/Name")
	item_image = get_node("VBoxContainer/Image")
	item_description = get_node("VBoxContainer/Description")

func set_item_data(name: String, image: Texture2D, description: String, 
	bonus: float, order: int, category: String, sub_category: String):
	item_name.text = name
	item_image.texture_normal = image
	item_description.text = description
	
	item_bonus = bonus
	item_order = order
	item_category = category
	item_sub_category = sub_category

func get_data():
	return {
		"order": item_order,
		"bonus": item_bonus,
		"category": item_category,
		"sub_category": item_sub_category
	}
