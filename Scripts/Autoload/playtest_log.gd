extends Node
# STRUMENTO PERMANENTE PER I PLAYTEST: osserva i segnali e il livello senza toccare il gioco e scrive righe "t=<s> EVENTO chiave=valore"
# su stdout (log del gioco, prefisso [PLAYTEST]) e in append su user://playtest_log.txt, che l'agente legge dopo le prove.
# Si adatta a ogni test: aggiungere o togliere eventi qui (un handler per segnale, tutto con _log()). Se per un test serve strumentare
# il codice di gioco (un segnale nuovo, una chiamata a PlaytestLog), l'istanza nel codice di gioco si toglie a test finito; questo file resta.
# Gli eventi attuali servono alla taratura di monete e prezzi (economia per ondata).

const LOG_PATH := "user://playtest_log.txt"

var _file: FileAccess
var _level = null          # livello in corso (senza tipo: legge i campi di level.gd)
var _ended := false        # game over già registrato per questa partita
var _t0 := 0.0
var _wave := 0
var _coins := 0
var _last_delta := 0       # ultima variazione delle monete (negativa = acquisto)
var _hp := 0.0
var _shield := 0.0
var _pause_spent := 0
var _w := {}               # contatori dell'ondata in corso
var _bought := {}          # acquisti per oggetto nella partita
var _enemies := {}         # istanza della nemica -> [salute vista l'ultima volta, frame osservati]: un calo di salute è un colpo a segno


func _ready() -> void:
	_file = FileAccess.open(LOG_PATH, FileAccess.READ_WRITE) if FileAccess.file_exists(LOG_PATH) else FileAccess.open(LOG_PATH, FileAccess.WRITE)
	if _file:
		_file.seek_end()
	get_tree().node_added.connect(_on_node_added)
	SignalManager.defeated.connect(_on_defeated)
	SignalManager.attack_target.connect(_on_attack)
	SignalManager.update_health_shield.connect(_on_health)
	SignalManager.currency_changed.connect(_on_currency)
	SignalManager.item_target_purchased.connect(_on_purchase)
	SignalManager.item_player_purchased.connect(_on_purchase)
	SignalManager.item_bonus_purchased.connect(_on_purchase)
	SignalManager.item_expired.connect(_on_expired)
	SignalManager.wave_purchase_item.connect(_on_wave_end)
	SignalManager.game_over.connect(_on_game_over)


func _process(_delta: float) -> void:
	var scene = get_tree().current_scene
	if _level != null and not is_instance_valid(_level):
		_level = null
	if scene != _level:
		if _level != null and not _ended:
			_log("RUN_LEFT wave=%d" % _wave)
		_level = scene if scene != null and scene.has_method("spawn_enemy") and scene.get("target") != null else null
		if _level != null:
			_start_run()
	if _level != null and not _ended and _level.wave != _wave:
		_wave_started()
	if _level != null and not _ended and not _w.is_empty():
		_poll_enemies()


# Un lancio = una palla di sabbia che entra nell'albero
func _on_node_added(node: Node) -> void:
	if _level == null or _ended or _w.is_empty():
		return
	var script: Script = node.get_script()
	if script != null and script.resource_path.ends_with("projectiles.gd"):
		_w["throws"] += 1
		_log("THROW wave=%d n=%d" % [_wave, _w["throws"]])


# Un colpo a segno = calo di salute di una nemica. Le prime osservazioni si saltano: alla nascita la salute passa dal valore di
# scena a quello dell'ondata (set_spawn_values) e non è un colpo.
func _poll_enemies() -> void:
	var seen := {}
	for enemy in get_tree().get_nodes_in_group("enemy"):
		var id: int = enemy.get_instance_id()
		var hp: float = enemy.hp
		var entry: Array = _enemies.get(id, [hp, 0])
		if entry[1] >= 2 and hp < entry[0]:
			_w["hits"] += 1
			_w["dealt"] += entry[0] - hp
			_log("HIT wave=%d dmg=%d enemy_hp=%d" % [_wave, int(entry[0] - hp), int(hp)])
		seen[id] = [hp, entry[1] + 1]
	_enemies = seen


func _now() -> float:
	return Time.get_ticks_msec() / 1000.0 - _t0


func _log(text: String) -> void:
	var line := "t=%07.1f %s" % [_now(), text]
	print("[PLAYTEST] ", line)
	if _file:
		_file.store_line(line)
		_file.flush()


func _target():
	return _level.target if _level != null else null


func _state() -> String:
	var b = _target()
	return "morale=%d/%d loyalty=%d/%d" % [int(b.shield), int(b.max_shield), int(b.hp), int(b.max_hp)]


func _start_run() -> void:
	_t0 = Time.get_ticks_msec() / 1000.0
	_ended = false
	_wave = 0
	_coins = Global.currency
	_pause_spent = 0
	_bought.clear()
	_log("RUN_START file=%s" % ProjectSettings.globalize_path(LOG_PATH))


func _wave_started() -> void:
	_wave = _level.wave
	var b = _target()
	_hp = b.hp
	_shield = b.shield
	_w = {"coins0": Global.currency, "t0": _now(), "kills": 0, "first_kill": -1.0, "last_kill": -1.0,
		"attacks": 0, "raw": 0, "morale_lost": 0, "loyalty_lost": 0, "morale_back": 0, "loyalty_back": 0,
		"throws": 0, "hits": 0, "dealt": 0}
	var mult: float = _level.currency_multiplier
	_log("WAVE_START wave=%d enemies=%d coins=%d pause_spent=%d coin_mult=%.2f per_kill=%d %s guard_morale=%s guard_loyalty=%s" % [
		_wave, _level.total_enemies, Global.currency, _pause_spent, mult, roundi(mult * _level.base_enemy_currency),
		_state(), str(b.get("guard_shield")), str(b.get("guard_health"))])
	_pause_spent = 0


func _on_defeated() -> void:
	if _level == null or _ended:
		return
	_w["kills"] += 1
	if _w["first_kill"] < 0.0:
		_w["first_kill"] = _now() - _w["t0"]
	_w["last_kill"] = _now() - _w["t0"]
	_log_kill.call_deferred()  # dopo che il livello ha accreditato le monete


func _log_kill() -> void:
	if _level != null:
		_log("KILL wave=%d n=%d/%d coins=%d wave_earned=%d" % [_wave, _w["kills"], _level.total_enemies, Global.currency, _level.wave_currency])


func _on_attack(damage, _attacker) -> void:
	if _level == null or _ended or Global.game_over_sequence:
		return
	_w["attacks"] += 1
	_w["raw"] += damage
	_log("ATTACK wave=%d raw=%s %s" % [_wave, str(damage), _state()])


func _on_health(hp, shield) -> void:
	if _level == null or _ended:
		return
	var d_hp = hp - _hp
	var d_sh = shield - _shield
	_hp = hp
	_shield = shield
	if d_sh < 0:
		_w["morale_lost"] += -d_sh
	elif d_sh > 0:
		_w["morale_back"] += d_sh
	if d_hp < 0:
		_w["loyalty_lost"] += -d_hp
	elif d_hp > 0:
		_w["loyalty_back"] += d_hp
	_log("HEALTH wave=%d d_morale=%d d_loyalty=%d now %s" % [_wave, int(d_sh), int(d_hp), _state()])


func _on_currency(value: int) -> void:
	_last_delta = value - _coins
	_coins = value
	if _last_delta < 0:
		_pause_spent += -_last_delta


func _on_purchase(data: Dictionary) -> void:
	if _level == null or _ended:
		return
	var id: String = str(data.get("id", "?"))
	_bought[id] = _bought.get(id, 0) + 1
	# la valuta è già scalata quando parte il segnale: il costo reale è l'ultima variazione
	_log("BUY wave=%d item=%s n=%d cost=%d base_price=%s coins_after=%d %s" % [
		_wave, id, _bought[id], -_last_delta, str(data.get("price", "?")), Global.currency, _state()])


func _on_expired(data: Dictionary) -> void:
	if _level != null and not _ended:
		_log("EXPIRED wave=%d item=%s" % [_wave, str(data.get("id", "?"))])


func _on_wave_end(wave: int) -> void:
	if _level == null or _ended or _w.is_empty():
		return
	var earned: int = _level.wave_currency
	var bonus: int = Global.currency - _w["coins0"] - earned   # nessun acquisto durante l'ondata
	_log("WAVE_END wave=%d enemies=%d kills=%d duration=%.1f first_kill=%.1f last_kill=%.1f earned_kills=%d bonus_rate=%.2f bonus=%d income=%d coins_start=%d coins_now=%d coin_mult=%.2f attacks=%d raw_damage=%d morale_lost=%d loyalty_lost=%d throws=%d hits=%d accuracy=%d%% damage_dealt=%d %s" % [
		wave, _level.total_enemies, _w["kills"], _now() - _w["t0"], _w["first_kill"], _w["last_kill"], earned,
		_level.wave_bonus_rate(), bonus, earned + bonus, _w["coins0"], Global.currency, _level.currency_multiplier,
		_w["attacks"], int(_w["raw"]), int(_w["morale_lost"]), int(_w["loyalty_lost"]),
		_w["throws"], _w["hits"], roundi(100.0 * _w["hits"] / maxi(_w["throws"], 1)), int(_w["dealt"]), _state()])


func _on_game_over(_last_attacker) -> void:
	if _level == null or _ended:
		return
	_log("GAME_OVER wave=%d kills_wave=%d/%d defeated_total=%d points=%d coins=%d %s" % [
		_wave, _w.get("kills", 0), _level.total_enemies, _level.defeated_total, _level.points, Global.currency, _state()])
	_log("RUN_PURCHASES %s" % str(_bought))
	_ended = true
