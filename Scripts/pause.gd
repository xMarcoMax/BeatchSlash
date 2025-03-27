extends CanvasLayer

func _input(event):
	if event.is_action_pressed("pause"):
		get_tree().paused = !get_tree().paused
		self.visible = !self.visible
