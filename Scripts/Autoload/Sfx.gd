extends Node
## Effetti sonori del gioco, un suono per evento. Si chiama `Sfx.play(Sfx.NOME)`.
## Ogni chiamata crea un AudioStreamPlayer usa e getta: i suoni possono sovrapporsi e restano udibili con il gioco in pausa
## (il pannello di game over mette in pausa l'albero). Il lancio della palla ha il suo player nel Player.

const ENEMY_HIT = preload("res://Assets/Sfx/enemy_hit_randomizer.tres")
const ENEMY_DEFEAT = preload("res://Assets/Sfx/enemy_defeat.wav")
const WAVE_COMPLETE = preload("res://Assets/Sfx/wave_complete.wav")
const WAVE_START = preload("res://Assets/Sfx/wave_start.wav")
const COUNTDOWN_TICK = preload("res://Assets/Sfx/countdown_tick.wav")
const PURCHASE = preload("res://Assets/Sfx/purchase_randomizer.tres")
const GAME_OVER = preload("res://Assets/Sfx/game_over.wav")
const KISS = preload("res://Assets/Sfx/kiss.wav")
const HEARTS_SPARKLE = preload("res://Assets/Sfx/hearts_sparkle.wav")

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS

func play(stream: AudioStream) -> void:
	var player := AudioStreamPlayer.new()
	player.stream = stream
	player.finished.connect(player.queue_free)
	add_child(player)
	player.play()
