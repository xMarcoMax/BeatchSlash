extends Control

@onready var main_volume = $VBoxContainer/VolumeOptions/HSlider

func _ready():
	main_volume.value = db_to_linear(AudioServer.get_bus_volume_db(0))

func _on_h_slider_value_changed(value):
	AudioServer.set_bus_volume_db(0, linear_to_db(main_volume.value))

func _on_mute_volume_toggled(toggled_on):
	AudioServer.set_bus_mute(0, toggled_on)

func _on_back_pressed():
	get_tree().change_scene_to_file("res://Scenes/main_menu.tscn")
