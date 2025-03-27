extends Node

#Segnali del target
signal enemy_attacking(enemy)

#Segnali del nemico
signal defeated
signal attack_target

#Segnali per l'hud
signal update_health_shield(health, shield)
signal purchase_item
signal wave_purchase_item(wave)

signal game_over
signal game_started
