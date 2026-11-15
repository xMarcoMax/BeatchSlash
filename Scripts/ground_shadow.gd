@tool
extends Sprite2D
## Separa l'ombra incorporata nell'atlante su un livello sotto tutti i corpi.

const BODY_MATERIAL = preload("res://Assets/Shaders/ground_body.tres")
const SHADOW_MATERIAL = preload("res://Assets/Shaders/ground_shadow.tres")

var _source


func _ready() -> void:
	_source = get_parent()
	assert(_source is AnimatedSprite2D or _source is Sprite2D)
	z_index = -1
	z_as_relative = false
	use_parent_material = false
	material = SHADOW_MATERIAL
	if _source.material == null:
		_source.material = BODY_MATERIAL
	_source.frame_changed.connect(_sync_frame)
	if _source is AnimatedSprite2D:
		_source.animation_changed.connect(_sync_frame)
		_source.sprite_frames_changed.connect(_sync_frame)
	else:
		_source.texture_changed.connect(_sync_frame)
	_sync_frame()


func _process(_delta: float) -> void:
	_sync_frame()


func _sync_frame() -> void:
	if not is_instance_valid(_source):
		return
	centered = _source.centered
	offset = _source.offset
	flip_h = _source.flip_h
	flip_v = _source.flip_v
	if _source is AnimatedSprite2D:
		var frames: SpriteFrames = _source.sprite_frames
		if frames != null and frames.has_animation(_source.animation) and frames.get_frame_count(_source.animation) > 0:
			texture = frames.get_frame_texture(_source.animation, _source.frame)
		else:
			texture = null
	else:
		texture = _source.texture
		hframes = _source.hframes
		vframes = _source.vframes
		frame = _source.frame
		region_enabled = _source.region_enabled
		region_rect = _source.region_rect
		region_filter_clip_enabled = _source.region_filter_clip_enabled
