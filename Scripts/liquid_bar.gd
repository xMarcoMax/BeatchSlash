class_name LiquidBar
extends ProgressBar

# ProgressBar drawn as a glass tube with liquid (Assets/Shaders/liquid_bar.gdshader). It keeps the ProgressBar API
# (value, max_value, children such as the value label), so scripts that fill a normal bar work unchanged.

const SHADER = preload("res://Assets/Shaders/liquid_bar.gdshader")

@export var liquid_color := Color(0.1, 0.55, 0.95)
# Outline width in control pixels: bars in the world need a thicker one, because the camera zooms out
@export var border_width := 2.0
# How fast the shown level follows the value (1/s): the liquid drains smoothly instead of jumping
@export var smoothing := 6.0

var _shown := -1.0
var _material := ShaderMaterial.new()

func _ready():
	show_percentage = false
	add_theme_stylebox_override("background", StyleBoxEmpty.new())
	add_theme_stylebox_override("fill", StyleBoxEmpty.new())
	_material.shader = SHADER
	var surface := ColorRect.new()
	surface.set_anchors_preset(Control.PRESET_FULL_RECT)
	surface.mouse_filter = Control.MOUSE_FILTER_IGNORE
	surface.material = _material
	add_child(surface)
	move_child(surface, 0) # under the value label, if any

func _process(delta):
	var target := get_as_ratio()
	_shown = target if _shown < 0.0 else lerpf(_shown, target, 1.0 - exp(-smoothing * delta))
	_material.set_shader_parameter("fill", _shown)
	_material.set_shader_parameter("liquid_color", liquid_color)
	_material.set_shader_parameter("bar_size", size)
	_material.set_shader_parameter("border", border_width)
