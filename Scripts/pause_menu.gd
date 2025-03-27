extends CanvasLayer

func _input(event):
	if event.is_action_pressed("esc"):
		_on_resume_pressed()

func _on_back_menu_pressed():
	get_tree().paused = false
	MusicManager.load_menu_music()
	get_tree().change_scene_to_file("res://Scenes/main_menu.tscn")

func _on_resume_pressed():
	get_tree().paused = !get_tree().paused
	self.visible = !self.visible
