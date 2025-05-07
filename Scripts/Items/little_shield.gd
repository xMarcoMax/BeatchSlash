extends PanelContainer

@export var bonus = 0.25
@export var order = 0
@export var category = "Target"
@export var sub_category = "Shield"

func get_data():
	return {
		"order": order,
		"bonus": bonus,
		"category": category,
		"sub_category": sub_category
	}
