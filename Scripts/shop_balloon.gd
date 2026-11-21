class_name ShopBalloon
extends Node2D

# Speech balloon of the shopkeeper, in world coordinates. One 9-slice texture drawn in GIMP (Tools/gimp/shop_balloon.xcf)
# holds the rounded body and the thin tail in its top-left corner: the corner is not stretched, so the tail keeps its
# shape whatever the text size. The node origin is the tip of the tail (up-left of the body): place it at Sandro's mouth.
# say() shows a text (until hush(), or for `duration` seconds), hush() hides it.
# The level camera is fixed and zoomed to 0.4, so the font size is multiplied by 2.5 to read like the HUD text.
const TEXTURE := preload("res://Assets/UI/shop_balloon.png")
const TIP := Vector2(7.0, 6.0)           # tail tip in texture pixels
const BODY_OFFSET := Vector2(70.0, 36.0) # top-left corner of the body (outline included) in texture pixels
const CORNER := 44.0                     # rounded corner size of the body, in texture pixels
const FONT_SIZE := 46
const MAX_TEXT_WIDTH := 460.0
const PADDING := Vector2(30.0, 22.0)
const INK_COLOR := Color(0.227, 0.078, 0.094)
const POP_TIME := 0.18
const HIDE_TIME := 0.12

var _text := ""
var _tween: Tween
var _timer := Timer.new()

func _ready() -> void:
	visible = false
	_timer.one_shot = true
	_timer.timeout.connect(hush)
	add_child(_timer)

# duration 0 = stays until hush()
func say(text: String, duration := 0.0) -> void:
	_text = text
	_timer.stop()
	queue_redraw()
	visible = true
	_animate_scale(1.0, POP_TIME, Tween.TRANS_BACK, Tween.EASE_OUT, 0.0)
	if duration > 0.0:
		_timer.start(duration)

func hush() -> void:
	_timer.stop()
	if not visible:
		return
	_animate_scale(0.0, HIDE_TIME, Tween.TRANS_QUAD, Tween.EASE_IN, 1.0).tween_callback(hide)

# Scales around the origin, which is the tail tip: the balloon grows out of the shopkeeper
func _animate_scale(to: float, time: float, trans: Tween.TransitionType, ease_type: Tween.EaseType, from: float) -> Tween:
	if _tween != null:
		_tween.kill()
	scale = Vector2.ONE * from
	_tween = create_tween()
	_tween.tween_property(self, "scale", Vector2.ONE * to, time).set_trans(trans).set_ease(ease_type)
	return _tween

func _font() -> Font:
	var theme := ThemeDB.get_project_theme()
	var font: Font = theme.get_font("font", "BodyLabel") if theme != null else null
	return font if font != null else ThemeDB.fallback_font

func _draw() -> void:
	if _text.is_empty():
		return
	var font := _font()
	var text_size := font.get_multiline_string_size(_text, HORIZONTAL_ALIGNMENT_LEFT, MAX_TEXT_WIDTH, FONT_SIZE)
	var body_size := text_size + PADDING * 2.0
	var style := StyleBoxTexture.new()
	style.texture = TEXTURE
	style.texture_margin_left = BODY_OFFSET.x + CORNER
	style.texture_margin_top = BODY_OFFSET.y + CORNER
	style.texture_margin_right = CORNER
	style.texture_margin_bottom = CORNER
	style.draw(get_canvas_item(), Rect2(-TIP, body_size + BODY_OFFSET))

	var origin := BODY_OFFSET - TIP + PADDING + Vector2(0.0, font.get_ascent(FONT_SIZE))
	font.draw_multiline_string(get_canvas_item(), origin, _text, HORIZONTAL_ALIGNMENT_CENTER, text_size.x, FONT_SIZE,
		-1, INK_COLOR)
