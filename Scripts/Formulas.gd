extends Node

func calculate(type, wave_real, base):
	var factor
	var cap = 15
	var wave = wave_real - 1
	match type:
		"enemies":
			factor = 1.6
			pass
		"health":
			factor = 1.1
			pass
		"damage":
			factor = 1.05
			pass
	var result = ceili(base * ( 1 + ( ( float(wave) /(cap+wave) ) )*factor ) )
	return result
