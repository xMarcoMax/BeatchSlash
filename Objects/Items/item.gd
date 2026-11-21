extends PanelContainer

class_name Item

signal purchase_requested(item: Item)

# Prezzo del CSV maggiorato del 25% a ogni passo composto: per gli oggetti con massimo un passo è un livello già
# comprato, per gli altri un multiplo di 5 ondate finite. Il risultato è arrotondato a multipli di 5.
const PRICE_GROWTH := 0.25
const PRICE_WAVE_STEP := 5
const PRICE_ROUNDING := 5

# Riga del CSV: id, name, description, bonus, order, category, sub_category, price, max_purchases, effect, duration,
# min_wave, every, cooldown
var data: Dictionary = {}
var purchases := 0
# Impostato dal negozio: l'effetto sarebbe nullo ora (es. barra già piena)
var useless := false
# Ondate che restano a un oggetto temporaneo (colonna duration del CSV); 0 = non attivo
var waves_left := 0
# Ondata appena finita, cioè la pausa in cui si compra; la imposta il negozio
var wave := 0
# Ondata della pausa dell'ultimo acquisto; -1 = mai comprato
var bought_wave := -1

var item_name: Label
var item_image: TextureRect
var item_description: Label
var buy_button: Button

func init_nodes():
	item_name = get_node("Content/Top/Texts/Name")
	item_image = get_node("Content/Top/Image")
	item_description = get_node("Content/Top/Texts/Description")
	buy_button = get_node("Content/BuyButton")
	buy_button.pressed.connect(func(): purchase_requested.emit(self))

func setup(row: Dictionary, image: Texture2D, currency: int):
	data = row
	item_name.text = row["name"]
	item_image.texture = image
	refresh(currency)

# max_purchases = 0 significa acquistabile senza limiti
func is_maxed() -> bool:
	return data["max_purchases"] > 0 and purchases >= data["max_purchases"]

func price() -> int:
	var steps: int = purchases if data["max_purchases"] > 0 else floori(wave / float(PRICE_WAVE_STEP))
	var raw: float = data["price"] * pow(1.0 + PRICE_GROWTH, steps)
	return roundi(raw / PRICE_ROUNDING) * PRICE_ROUNDING

# Ondate che mancano per l'attesa data da "every" (acquistabile solo nelle pause dopo un'ondata multipla di N)
# e da "cooldown" (pause saltate dopo ogni acquisto). Lo sblocco "min_wave" è a parte.
func wait_waves() -> int:
	var wait := 0
	var every: int = data["every"]
	if every > 0 and wave % every != 0:
		wait = every - wave % every
	if bought_wave >= 0 and data["cooldown"] > 0:
		wait = maxi(wait, bought_wave + data["cooldown"] + 1 - wave)
	return wait

# Motivo per cui ora non si può comprare per sblocco o attesa; vuoto se è acquistabile
func lock_text() -> String:
	if wave < data["min_wave"]:
		return "Acquistabile dopo l'ondata %d" % data["min_wave"]
	var wait := wait_waves()
	if wait > 0:
		return "Acquistabile tra %d %s" % [wait, "ondata" if wait == 1 else "ondate"]
	return ""

func can_buy(currency: int) -> bool:
	return not is_maxed() and not useless and waves_left == 0 and lock_text() == "" and currency >= price()

# Aggiorna descrizione (con il contatore), prezzo, stato del pulsante e tooltip del motivo del blocco
func refresh(currency: int):
	var max_count: int = data["max_purchases"]
	item_description.text = data["description"]
	if max_count > 0:
		item_description.text += " (%d/%d)" % [purchases, max_count]
	if waves_left > 0:
		buy_button.text = "Attivo (%d)" % waves_left
	else:
		buy_button.text = "Max" if is_maxed() else "%d¢" % price()
	buy_button.disabled = not can_buy(currency)
	tooltip_text = lock_text()
	buy_button.tooltip_text = tooltip_text

func get_data() -> Dictionary:
	return data
