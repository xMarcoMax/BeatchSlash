class_name FloatingText
extends Label

# Number that rises from a character and fades out: damage taken by an enemy, damage or healing of the boyfriend
# The label's top-left corner starts here and the text is about 90 px tall: it begins just above the head
# (and above the enemy health bar) so it never covers the sprite
const HEAD_OFFSET = Vector2(0, -230)
const WIDTH = 200.0
const RISE = 90.0
const LIFETIME = 0.9
# The level camera is fixed and zoomed to 0.4, so the size is multiplied by 2.5 to read like the HUD text
const FONT_SIZE = 75

static func spawn(parent: Node, at: Vector2, value: String, color: Color):
	var label := FloatingText.new()
	label.text = value
	# Centered on the point, with a little random jitter so simultaneous hits do not overlap exactly
	label.position = at + Vector2(randf_range(-20.0, 20.0) - WIDTH / 2.0, 0.0)
	label.add_theme_color_override("font_color", color)
	parent.add_child(label)

func _ready():
	custom_minimum_size.x = WIDTH
	horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	z_index = 100
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_theme_font_size_override("font_size", FONT_SIZE)
	add_theme_color_override("font_outline_color", Color.BLACK)
	add_theme_constant_override("outline_size", 14)
	var tween := create_tween().set_parallel(true)
	tween.tween_property(self, "position:y", position.y - RISE, LIFETIME).set_ease(Tween.EASE_OUT)
	tween.tween_property(self, "modulate:a", 0.0, LIFETIME * 0.5).set_delay(LIFETIME * 0.5)
	tween.chain().tween_callback(queue_free)
