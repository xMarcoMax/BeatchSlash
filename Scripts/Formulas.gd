extends Node

func calculate(type, wave_real, base):
	var factor
	var cap = 15
	var wave = wave_real - 1
	print("ondata: "+str(wave_real))
	match type:
		"enemies":
			factor = 0.5
			pass
		"health":
			factor = 1.1
			pass
		"damage":
			factor = 0.8
			pass
	var result = ceil(base * ( 1 + ( ( float(wave) /(cap+wave) ) ) ) )
	print(type+" = "+str(result))
	return result
