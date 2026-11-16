extends Node

# Crescita per ondata, con n = ondata - 1 (l'ondata 1 vale esattamente la base). Valori da ritoccare dopo le prove.
const ENEMIES_PER_WAVE = 0.6    # nemiche in più a ogni ondata (lineare, senza tetto)
const HEALTH_LINEAR = 0.12      # salute: crescita lineare
const HEALTH_QUADRATIC = 0.004  # salute: termine che accelera la crescita nelle ondate avanzate
const DAMAGE_LINEAR = 0.05      # danno: cresce più piano della salute

func calculate(type, wave_real, base):
	var n = wave_real - 1
	match type:
		"enemies":
			return base + floori(ENEMIES_PER_WAVE * n)
		"health":
			return ceili(base * (1.0 + HEALTH_LINEAR * n + HEALTH_QUADRATIC * n * n))
		"damage":
			return ceili(base * (1.0 + DAMAGE_LINEAR * n))
	push_error("Formulas.calculate: tipo sconosciuto '%s'" % type)
	return base

# 8 direzioni degli sprite: diagonale se l'asse minore supera tan(22.5°) di quello maggiore.
func direction_name(v: Vector2) -> String:
	var horizontal = "left" if v.x < 0 else "right"
	var vertical = "up" if v.y < 0 else "down"
	var ax = absf(v.x)
	var ay = absf(v.y)
	if minf(ax, ay) > 0.414 * maxf(ax, ay):
		return vertical + "_" + horizontal
	return horizontal if ax > ay else vertical
