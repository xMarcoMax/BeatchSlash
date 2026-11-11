extends Node

func calculate(type, wave_real, base):
	var factor
	var cap = 12
	var wave = wave_real - 1
	match type:
		"enemies":
			factor = 1.6
			pass
		"health":
			factor = 1.25
			pass
		"damage":
			factor = 1.05
			pass
	var result = ceili(base * ( 1 + ( ( float(wave) /(cap+wave) ) )*factor ) )
	return result

# 8 direzioni degli sprite: diagonale se l'asse minore supera tan(22.5°) di quello maggiore.
func direction_name(v: Vector2) -> String:
	var horizontal = "left" if v.x < 0 else "right"
	var vertical = "up" if v.y < 0 else "down"
	var ax = absf(v.x)
	var ay = absf(v.y)
	if minf(ax, ay) > 0.414 * maxf(ax, ay):
		return vertical + "_" + horizontal
	return horizontal if ax > ay else vertical
