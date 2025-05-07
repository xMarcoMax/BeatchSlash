extends PanelContainer

@export var bonus = 0.2
@export var order = 0
@export var category = "Player"
@export var sub_category = "Damage"

func get_data():
	return {
		"order": order,
		"bonus": bonus,
		"category": category,
		"sub_category": sub_category
	}
