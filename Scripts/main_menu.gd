extends Control


func _on_exit_pressed():
	get_tree().quit()
	pass # Replace with function body.


func _on_new_game_pressed():
	get_tree().change_scene_to_file("res://Scenes/level.tscn")
	pass # Replace with function body.


func _on_options_pressed():
	#opzioni di no audio, volume, forse risoluzione
	pass # Replace with function body.


func _on_tutorial_pressed():
	#mostra la pagina del tutorial
	pass # Replace with function body.
