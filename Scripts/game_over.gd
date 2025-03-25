extends CanvasLayer


func _on_restart_pressed():
	get_tree().paused = false
	get_tree().change_scene_to_file("res://Scenes/level.tscn")

func _on_back_menu_pressed():
	get_tree().paused = false
	MusicManager.load_menu_music()
	get_tree().change_scene_to_file("res://Scenes/main_menu.tscn")

func _on_exit_pressed():
	get_tree().paused = false
	get_tree().quit()
