extends Node

#Segnali del target
signal enemy_attacking(enemy)
signal enemy_left_target(enemy)

#Segnali del nemico e del player
signal defeated
signal attack_target(damage, attacker)

#Segnali per l'acquisto per Target, Player, Bonus
signal item_target_purchased(data)
signal item_player_purchased(data)
signal item_bonus_purchased(data)
#Un oggetto temporaneo ha finito le sue ondate: chi ne applicava l'effetto lo toglie
signal item_expired(data)

#Segnali per l'hud
signal update_health_shield(health, shield)
signal update_max_health_shield(max_health, max_shield)
signal currency_changed(value)
signal purchase_item
signal wave_purchase_item(wave)

#Fedeltà a zero: `last_attacker` è la nemica che ha dato l'ultimo colpo (emesso una sola volta)
signal game_over(last_attacker)
signal game_started
