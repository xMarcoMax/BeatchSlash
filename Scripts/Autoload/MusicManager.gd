extends Node

var music_player : AudioStreamPlayer

func _ready():
	music_player = AudioStreamPlayer.new()
	add_child(music_player)
	music_player.autoplay = true
	
	SignalManager.game_started.connect(_on_game_started)

func load_menu_music():
	var music = preload("res://Assets/Music/Menu/main_menu.mp3")
	music_player.stream = music
	start_music()

func start_music():
	music_player.play()

func stop_music():
	music_player.stop()

func is_music_playing():
	return music_player.playing == true

func _on_game_started():
	stop_music()
	#var music = preload("res://Assets/Music/Beach/summer-funky-dance-314907.mp3")
	#music_player.stream = music
	#start_music()
