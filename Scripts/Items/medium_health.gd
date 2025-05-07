extends PanelContainer

@export var bonus = 0.5
@export var order = 1
@export var category = "Target"
@export var sub_category = "Health"

func get_data():
	return {
		"order": order,
		"bonus": bonus,
		"category": category,
		"sub_category": sub_category
	}
