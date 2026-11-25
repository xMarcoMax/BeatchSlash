extends Node

# Android e iOS, tablet compresi; falso su Windows, Linux e macOS anche con schermo touch
var is_mobile := OS.has_feature("mobile")

var is_in_purchase
var purchase_just_closed
# Scenetta di game over in corso: il gioco è fermo e i personaggi li muove GameOverSequence (lo azzera il livello in _ready)
var game_over_sequence := false

# Valuta della partita in corso: la accumula il livello e la spendono gli acquisti
var currency := 0:
	set(value):
		currency = value
		SignalManager.currency_changed.emit(value)
