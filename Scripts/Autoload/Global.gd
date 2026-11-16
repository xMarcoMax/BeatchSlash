extends Node

var is_mobile

var is_in_purchase
var purchase_just_closed

# Valuta della partita in corso: la accumula il livello e la spendono gli acquisti
var currency := 0:
	set(value):
		currency = value
		SignalManager.currency_changed.emit(value)
