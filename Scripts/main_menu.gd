extends Control

func _ready():
	if !MusicManager.is_music_playing():
		MusicManager.load_menu_music()

func _on_exit_pressed():
	get_tree().quit()

func _on_new_game_pressed():
	MusicManager.stop_music()
	SignalManager.game_started.emit()
	get_tree().change_scene_to_file("res://Scenes/level.tscn")

func _on_options_pressed():
	get_tree().change_scene_to_file("res://Scenes/options.tscn")

func _on_tutorial_pressed():
	get_tree().change_scene_to_file("res://Scenes/tutorial.tscn")
