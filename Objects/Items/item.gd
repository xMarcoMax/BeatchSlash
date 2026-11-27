extends PanelContainer

class_name Item

signal purchase_requested(item: Item)

# Prezzo del CSV maggiorato del 15% a ogni passo composto: per gli oggetti con massimo un passo è un livello già
# comprato, per gli altri un multiplo di 5 ondate finite. Il risultato è arrotondato a multipli di 5.
const PRICE_GROWTH := 0.15
const PRICE_WAVE_STEP := 5
const PRICE_ROUNDING := 5

# Riga del CSV: id, name, description, bonus, order, category, sub_category, price, max_purchases, effect, duration,
# min_wave, every, cooldown, per_waves, group
var data: Dictionary = {}
var purchases := 0
# Impostato dal negozio: l'effetto sarebbe nullo o sprecato ora (barra già piena, ripristino più grande di quanto manca);
# useless_text è il motivo mostrato nel tooltip
var useless := false
var useless_text := ""
# Regole dei ripristini: quelli fino a questa quota del massimo (il più piccolo) bastano a barra non piena; quello al 100% e i
# pacchetti Entrambi si usano solo con una barra rimasta a questa quota o meno; gli altri solo se non ripristinano più di quanto manca
const RESTORE_ALWAYS_UP_TO := 0.25
const RESTORE_LOW_BAR := 0.25
# Acquisti già fatti dal gruppo di oggetti che condividono i crediti (colonna group); -1 = l'oggetto usa i propri. Lo imposta il negozio
var credit_purchases := -1
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
	# per_waves: un acquisto di credito ogni N ondate finite; il credito non scade e si accumula (acquisti < ondata / N = si può comprare)
	# group: più oggetti dividono gli stessi crediti (se ne sceglie uno solo per credito)
	var per_waves: int = data.get("per_waves", 0)
	var used := credit_purchases if credit_purchases >= 0 else purchases
	if per_waves > 0 and used >= floori(wave / float(per_waves)):
		wait = maxi(wait, (used + 1) * per_waves - wave)
	return wait

# Motivo per cui ora non si può comprare per sblocco o attesa; vuoto se è acquistabile
func lock_text() -> String:
	var reward: bool = data["price"] == 0
	if wave < data["min_wave"]:
		return ("Premio disponibile dopo l'ondata %d" if reward else "Acquistabile dopo l'ondata %d") % data["min_wave"]
	var wait := wait_waves()
	if wait > 0:
		return ("Premio disponibile tra %d %s" if reward else "Acquistabile tra %d %s") % [wait, "ondata" if wait == 1 else "ondate"]
	return ""

# Motivo per cui ora non si può comprare, per il tooltip (stesso ordine di can_buy); vuoto se si può
func block_text(currency: int) -> String:
	if is_maxed():
		return "Hai raggiunto il livello massimo"
	if waves_left > 0:
		return "Già attivo: ancora %d %s" % [waves_left, "ondata" if waves_left == 1 else "ondate"]
	var lock := lock_text()
	if lock != "":
		return lock
	if useless:
		if useless_text != "":
			return useless_text
		match data.get("sub_category", ""):
			"Shield":
				return "La moralità è già al massimo"
			"Health":
				return "La fedeltà è già al massimo"
		return "Moralità e fedeltà sono già al massimo"
	if currency < price():
		return "Ti servono ancora %d¢" % (price() - currency)
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
		buy_button.text = "Max" if is_maxed() else ("Premio" if data["price"] == 0 else "%d¢" % price())
	buy_button.disabled = not can_buy(currency)
	tooltip_text = block_text(currency)
	buy_button.tooltip_text = tooltip_text

func get_data() -> Dictionary:
	return data


# Motivo per cui un ripristino non si può comprare con le barre così (vuoto se si può). `bonus` è la quota del massimo che ripristina,
# `sub_category` "Shield", "Health" o "Both". Regola di ogni barra: il 25% basta che la barra non sia piena; il 50% non deve
# ripristinare più di quanto manca; il 100% vuole la barra al 25% o meno. Entrambi: stessa regola, basta che la rispetti una delle due barre;
# l'Entrambi al 100% (il premio) si usa se almeno una barra non è piena.
static func restore_block(bonus: float, sub_category: String, max_shield: float, shield: float, max_hp: float, hp: float) -> String:
	var shield_block := _bar_block(bonus, "moralità", max_shield, shield)
	var hp_block := _bar_block(bonus, "fedeltà", max_hp, hp)
	# Il pacchetto Entrambi al 100% (il premio) si usa comunque: basta che una barra non sia piena
	if sub_category == "Both" and bonus >= 1.0:
		var full := max_shield - shield < 0.01 and max_hp - hp < 0.01
		return "Moralità e fedeltà sono già al massimo" if full else ""
	match sub_category:
		"Shield":
			return shield_block
		"Health":
			return hp_block
	if shield_block == "" or hp_block == "":
		return ""
	if max_shield - shield < 0.01 and max_hp - hp < 0.01:
		return "Moralità e fedeltà sono già al massimo"
	return "Serve almeno una barra al 25% o meno" if bonus >= 1.0 else "Ripristinerebbe più di quanto manca a entrambe le barre"

# Regola di una barra sola (vuoto = il ripristino si può usare)
static func _bar_block(bonus: float, name: String, max_bar: float, bar_now: float) -> String:
	var missing := max_bar - bar_now
	if missing < 0.01:
		return "La %s è già al massimo" % name
	if bonus >= 1.0:
		if bar_now > max_bar * RESTORE_LOW_BAR + 0.01:
			return "Serve la %s al 25%% o meno" % name
	elif bonus > RESTORE_ALWAYS_UP_TO and max_bar * bonus > missing + 0.01:
		return "Ripristinerebbe %d di %s, ma ne mancano %d" % [roundi(max_bar * bonus), name, roundi(missing)]
	return ""
