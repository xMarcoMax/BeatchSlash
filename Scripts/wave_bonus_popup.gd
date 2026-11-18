extends Control

# Popup di fine ondata: l'entrata è l'uscita al contrario. La scritta nasce da un punto al centro, avanza di poco e si assesta;
# intanto ruota verso sinistra fino a poco più di 45 gradi (ENTER_TIME) e torna dritta nello stesso tempo; resta ferma
# e poi avanza di poco e viene risucchiata verso il centro dissolvendosi (EXIT_TIME).
const PEAK_ANGLE = deg_to_rad(-52.0)
const ENTER_TIME = 0.6
const HOLD_TIME = 2.0
const EXIT_TIME = 0.6

@onready var box: VBoxContainer = $Center/Box
@onready var title: Label = $Center/Box/Title
@onready var amount: Label = $Center/Box/Amount
var tween: Tween

func _ready():
	# Scala e rotazione girano attorno al centro della scritta, qualunque sia la sua dimensione
	box.resized.connect(func(): box.pivot_offset = box.size / 2.0)

func play(title_text: String, amount_text: String):
	if tween:
		tween.kill()
	title.text = title_text
	amount.text = amount_text
	box.reset_size()
	box.scale = Vector2.ZERO
	box.rotation = 0.0
	box.modulate.a = 0.0
	show()

	tween = create_tween()
	tween.set_parallel(true)
	# TRANS_BACK in uscita: specchio dell'uscita, la scritta avanza di poco oltre la posizione normale e poi si assesta
	tween.tween_property(box, "scale", Vector2.ONE, ENTER_TIME).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.tween_property(box, "modulate:a", 1.0, ENTER_TIME * 0.45)
	tween.tween_property(box, "rotation", PEAK_ANGLE, ENTER_TIME).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_property(box, "rotation", 0.0, ENTER_TIME).set_delay(ENTER_TIME).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.chain().tween_interval(HOLD_TIME)
	# TRANS_BACK in ingresso: la scritta avanza di poco prima di rimpicciolirsi verso il centro
	tween.chain().tween_property(box, "scale", Vector2.ZERO, EXIT_TIME).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	tween.tween_property(box, "modulate:a", 0.0, EXIT_TIME * 0.45).set_delay(EXIT_TIME * 0.55)
	tween.chain().tween_callback(hide)
