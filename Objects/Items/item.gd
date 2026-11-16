extends PanelContainer

class_name Item

signal purchase_requested(item: Item)

# Riga del CSV: id, name, description, bonus, order, category, sub_category, price, max_purchases, effect
var data: Dictionary = {}
var purchases := 0
# Impostato dal negozio: l'effetto sarebbe nullo ora (es. barra già piena)
var useless := false

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

func can_buy(currency: int) -> bool:
	return not is_maxed() and not useless and currency >= data["price"]

# Aggiorna descrizione (con il contatore), prezzo e stato del pulsante
func refresh(currency: int):
	var max_count: int = data["max_purchases"]
	item_description.text = data["description"]
	if max_count > 0:
		item_description.text += " (%d/%d)" % [purchases, max_count]
	buy_button.text = "Max" if is_maxed() else "%d¢" % data["price"]
	buy_button.disabled = not can_buy(currency)

func get_data() -> Dictionary:
	return data
