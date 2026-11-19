extends Control

# Popup di fine ondata. L'entrata è l'uscita al contrario, in due fasi:
# 1. dal punto al centro dello schermo la scritta cresce fino a più della dimensione normale (PEAK_SCALE) e intanto ruota
#    verso sinistra fino a PEAK_ANGLE: scala e rotazione arrivano al massimo insieme;
# 2. da lì torna alla dimensione normale e dritta: rimpicciolimento e rotazione hanno la stessa durata e la stessa curva,
#    quindi finiscono insieme (il "rimbalzo").
# PEAK_SCALE è molto più alto dell'avanzata dell'uscita (1,1): raddrizzandosi la scritta si allarga in orizzontale (larghezza
# a schermo = scala × cos(angolo)), quindi con 1,35 a −52° cresceva (0,83 → 1) e il rimpicciolimento non si vedeva.
# Con 1,7 a −42° passa da 1,26 a 1 e la scritta si vede restringere mentre si raddrizza: tenere scala × cos(angolo) ben sopra 1.
# Resta ferma, poi esce: avanza di poco e viene risucchiata verso il centro.
# Scala, rotazione e trasparenza stanno su `Pivot`, un Control semplice posto al centro dello schermo: un Container
# (CenterContainer, VBox) azzererebbe scala e rotazione dei figli a ogni riordino e l'entrata non si vedrebbe.
const PEAK_ANGLE = deg_to_rad(-42.0)
const PEAK_SCALE = 1.7
const GROW_TIME = 0.3
const SETTLE_TIME = 0.3
const FADE_IN_TIME = 0.08
const HOLD_TIME = 2.0
const EXIT_TIME = 0.6

@onready var pivot: Control = $Pivot
@onready var title: Label = $Pivot/Box/Title
@onready var amount: Label = $Pivot/Box/Amount
var tween: Tween

func play(title_text: String, amount_text: String):
	if tween:
		tween.kill()
	title.text = title_text
	amount.text = amount_text
	pivot.scale = Vector2.ZERO
	pivot.rotation = 0.0
	pivot.modulate.a = 0.0
	show()

	tween = create_tween()
	tween.set_parallel(true)
	# Fase 1: dal centro alla posizione inclinata e un po' più grande (rallenta arrivando, come l'uscita al contrario)
	tween.tween_property(pivot, "scale", Vector2.ONE * PEAK_SCALE, GROW_TIME).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tween.tween_property(pivot, "rotation", PEAK_ANGLE, GROW_TIME).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tween.tween_property(pivot, "modulate:a", 1.0, FADE_IN_TIME)
	# Fase 2: dalla posizione inclinata e più grande a quella normale, dritta
	tween.chain().tween_property(pivot, "scale", Vector2.ONE, SETTLE_TIME).set_trans(Tween.TRANS_LINEAR)
	tween.tween_property(pivot, "rotation", 0.0, SETTLE_TIME).set_trans(Tween.TRANS_LINEAR)
	tween.chain().tween_interval(HOLD_TIME)
	# Uscita: TRANS_BACK in ingresso, la scritta avanza di poco prima di rimpicciolirsi verso il centro
	tween.chain().tween_property(pivot, "scale", Vector2.ZERO, EXIT_TIME).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	tween.tween_property(pivot, "modulate:a", 0.0, EXIT_TIME * 0.45).set_delay(EXIT_TIME * 0.55)
	tween.chain().tween_callback(hide)
