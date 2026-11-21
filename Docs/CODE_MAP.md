# Beatch Slash! — mappa del codice

## Indice

1. [Regole di questo file](#1-regole-di-questo-file): cosa ci va e cosa no.
2. [Generale](#2-generale): motore, scena principale, cartelle, documentazione.
3. [Flusso di gioco](#3-flusso-di-gioco): dal menu al game over, passo per passo.
4. [Autoload](#4-autoload): Formulas, SignalManager, MusicManager, Global.
5. [Segnali](#5-segnali): chi emette e chi ascolta.
6. [Scene e script](#6-scene-e-script): tabella di tutte le scene con script e nodi principali.
7. [Livello](#7-livello-levelgd): ondate, spawn, punti e monete, bonus di fine ondata, area di gioco.
8. [Giocatore](#8-giocatore-playergd): movimento, lancio, velocità, acquisti.
9. [Nemica e pathfinding](#9-nemica-e-pathfinding-enemygd-pathfindergd): spawn, percorso, posti, colpi, morte, animazioni.
10. [Ragazzo](#10-ragazzo-boyfriendgd): danni, protezioni, massimi, scelta dell'animazione.
11. [Palla di sabbia](#11-palla-di-sabbia-projectilesgd): volo, impatto, caduta.
12. [Collisioni e ordine di disegno](#12-collisioni-e-ordine-di-disegno): layer, maschere, forme, Z e Y-sort.
13. [Ombre al suolo](#13-ombre-al-suolo): GroundShadow e shader di separazione.
14. [Mondo: terreno, mappa, spawn, props](#14-mondo-terreno-mappa-spawn-props): TileSet, mappa tutorial, zone di spawn, elementi di scena.
15. [Negozio e oggetti](#15-negozio-e-oggetti): chiosco, catalogo CSV, pannello, spesa, effetti.
16. [Interfaccia](#16-interfaccia): HUD, barre, numeri fluttuanti, popup del bonus, conto alla rovescia, tema, finestra e camera.
17. [Input](#17-input): azioni dell'InputMap.
18. [Risorse grafiche e sorgenti](#18-risorse-grafiche-e-sorgenti): atlanti, SpriteFrames, script di generazione, concept e prompt.
19. [Test](#19-test): suite e cosa verificano.
20. [Punti fragili e cose da sapere](#20-punti-fragili-e-cose-da-sapere).

## 1. Regole di questo file

Regola categorica dell'utente. Questo file descrive **solo il funzionamento tecnico attuale** del codice e di ogni sua parte: scene, nodi, script, segnali, autoload, risorse, valori, flussi, punti fragili. Ogni dettaglio tecnico del progetto sta qui e solo qui.

- **Non è uno storico:** niente date, "prima era così", correzioni fatte, tentativi o resoconti di verifica.
- Concept, regole di gioco viste dal giocatore, stato dei punti di sviluppo e idee future stanno in `Docs/PROJECT_CONTEXT.md`. Le procedure degli strumenti stanno in `Docs/BLENDER.md`, `Docs/PIXELORAMA.md`, `Docs/GIMP.md`, `Docs/GODOT.md`.
- Se cambi segnali, scene, autoload, flussi o valori, aggiorna la sezione giusta (vedi indice) nello stesso intervento. Verificare sempre contro i file reali.

## 2. Generale

- GDScript, Godot 4.7 stable, renderer Mobile. Scena principale: `Scenes/main_menu.tscn`. Tutto il testo in gioco è in italiano.
- Cartelle: `Scenes/` (scene principali e UI), `Characters/` (Player, nemica, ragazzo), `Objects/` (proiettile, HUD, negozio, puff, popup, `Items/` con scena e script della scheda, `Props/`), `Scripts/` (script, `Autoload/`), `Assets/` (grafica, font, musica, shader, tema), `Files/` (dati: `item_list.csv`), `tests/` (suite Godot AI), `Tools/` (sorgenti grafici e generatori, versionata in Git, ignorata da Godot con `.gdignore`), `Docs/` (documentazione, ignorata da Godot).
- Documentazione degli strumenti: `Docs/BLENDER.md`, `Docs/GIMP.md`, `Docs/GODOT.md`, `Docs/PIXELORAMA.md`; know-how generico nella skill `game-tools` (`C:\Users\stefa\.agent-knowledge\game-tools\SKILL.md`). Tipografia: `Docs/FONTS.md`. Regole fisse per gli agenti: `AGENTS.md` (Claude Code lo importa da `CLAUDE.md`).
- Ambiente Python `.sprite-tools-env` (Pillow, NumPy) per gli script di `Tools/`, escluso da Git e da Godot. `.gitignore` esclude anche `*.tmp`, `*.blend1`, `__pycache__`.

## 3. Flusso di gioco

1. **Menu** (`main_menu.gd`): avvia la musica. Nuova partita emette `SignalManager.game_started` (ferma la musica) e carica `Scenes/level.tscn`. Opzioni (`options.gd`: volume e muto sul bus 0) e Tutorial sono scene dedicate che tornano al menu.
2. **Avvio del livello** (`level.gd._ready`): passa `_play_area()` al Player, aggiunge `bonus_popup` come figlio dell'HUD, inizializza HUD e variabili (`set_variables`: 3 nemiche, moltiplicatori 1, `Global.currency = 0`), collega i segnali, aggiunge il `Pathfinder` e lo costruisce su `_world_bounds()`.
3. **Ondata:** `_process` chiama `spawn_enemy()` (una nemica per frame finché `spawn_number > 0`) e `check_all_eliminated()`.
4. **Nemica:** cammina verso un posto attorno al ragazzo; quando entra nell'`HitZone` del ragazzo riceve `enemy_attacking` e ogni `AttackCooldown` (1,4 s) emette `attack_target(damage)`.
5. **Ragazzo:** `_on_enemy_attack` toglie moralità (`shield`), poi fedeltà (`hp`), emette `update_health_shield`; a `hp <= 0` emette `game_over`.
6. **Colpo:** il Player lancia la palla (`player.gd` → `projectiles.gd`); al contatto con una nemica viva chiama `enemy.take_damage`; a `hp <= 0` parte `enemy.dead()`, che emette `defeated`; `level.gd._on_defeated` aggiorna punti, monete e HUD.
7. **Fine ondata:** quando `defeated_level == total_enemies`, `check_all_eliminated()` chiama una sola volta `_award_wave_bonus()`, avvia `NextWaveTimer` (20 s), mostra `NextWave` ed emette `wave_purchase_item(wave)`; il negozio diventa accessibile.
8. **Nuova ondata:** allo scadere di `NextWaveTimer`, `set_next_wave()` incrementa l'ondata, ricalcola le nemiche con `Formulas.calculate("enemies", ...)`, azzera `defeated_level` e `wave_currency` e chiude un eventuale acquisto in corso.
9. **Game over:** `level.gd._on_game_over` mostra `UI/GameOver` e imposta `get_tree().paused = true`. Riavvio, menu o uscita in `game_over.gd`.

## 4. Autoload

| Nome | File | Ruolo |
| --- | --- | --- |
| `Formulas` | `Scripts/Autoload/Formulas.gd` | `calculate(type, wave, base)` con n = wave − 1: `"enemies"` = base + `floori(ENEMIES_PER_WAVE*n)`; `"health"` = `ceili(base*(1 + HEALTH_LINEAR*n + HEALTH_QUADRATIC*n²))`; `"damage"` = `ceili(base*(1 + DAMAGE_LINEAR*n))`. Costanti 0,6 / 0,12 / 0,004 / 0,05, nessun tetto; tipo sconosciuto = `push_error` e ritorna la base. `direction_name(Vector2)` sceglie una delle 8 direzioni (diagonale se l'asse minore supera 0,414 del maggiore), usata da Player e nemiche |
| `SignalManager` | `Scripts/Autoload/SignalManager.gd` | bus dei segnali globali (sezione 5) |
| `MusicManager` | `Scripts/Autoload/MusicManager.gd` | un `AudioStreamPlayer` con `Assets/Music/Menu/summer-funky-dance-314907.mp3` in loop; `game_started` la ferma |
| `Global` | `Scripts/Autoload/Global.gd` | `is_mobile` (`OS.has_feature("mobile")`, impostato alla dichiarazione: vale da qualsiasi scena; vero su Android e iOS, tablet compresi, falso su desktop anche con schermo touch; nessuno script lo legge ancora); `is_in_purchase` (blocca movimento e lanci durante gli acquisti); `purchase_just_closed` (evita che Esc chiuda anche la pausa); `currency` (il setter emette `currency_changed`; la accumula `level.gd`, la spende `upgrades_purchase.gd`, la azzera `set_variables()`) |
| `_mcp_game_helper` | `addons/godot_ai/...` | strumento di sviluppo di Godot AI, non fa parte del gioco |

## 5. Segnali

| Segnale | Chi emette | Chi ascolta |
| --- | --- | --- |
| `game_started` | main_menu | MusicManager |
| `enemy_attacking(enemy)` | boyfriend (`body_entered` dell'`HitZone`) | enemy (ogni istanza controlla `attacker == self`) |
| `enemy_left_target(enemy)` | boyfriend (`body_exited` dell'`HitZone`) | enemy: `is_attacking = false`, smette il flirt e gli attacchi e torna a camminare; rientrando riparte `enemy_attacking` |
| `attack_target(damage)` | enemy.attack | boyfriend `_on_enemy_attack` |
| `defeated` | enemy.dead | level `_on_defeated` |
| `update_health_shield(hp, shield)` | boyfriend (danni e bonus) | hud `set_values`; upgrades_purchase `_on_partner_health_changed` (aggiorna gli oggetti inutili) |
| `update_max_health_shield(max_hp, max_shield)` | boyfriend `set_max_hp`/`set_max_shield` | hud `set_max_values` |
| `currency_changed(value)` | Global (setter di `currency`) | hud `set_currency`; upgrades_purchase `_on_currency_changed` (saldo e pulsanti) |
| `game_over` | boyfriend | level `_on_game_over` |
| `wave_purchase_item(wave)` | level (fine ondata) | upgrades_purchase `_on_wave_finished` |
| `purchase_item` | upgrades (tasto F) | nessuno |
| `item_target_purchased(data)` | upgrades_purchase | boyfriend `_apply_bonus` |
| `item_player_purchased(data)` | upgrades_purchase | player `_on_item_purchased` |
| `item_bonus_purchased(data)` | upgrades_purchase | level `_on_bonus_purchased` |
| `item_expired(data)` | upgrades_purchase `_on_wave_finished` | level `_on_item_expired` (Bonus `coin_bonus`), boyfriend `_on_item_expired` (Target `guard`) |

## 6. Scene e script

| Scena | Script | Note |
| --- | --- | --- |
| `Scenes/main_menu.tscn` | `main_menu.gd` | menu principale |
| `Scenes/level.tscn` | `level.gd` | radice `Level` (`y_sort_enabled`): `UI` (HUD, GameOver, UpgradesPurchase, PauseMenu), `World` (Z −3: `EnemySpawn` con 4 strisce, `TutorialMap`), `Player` in (800, −380), `Camera2D` fissa in (800, −560), `Boyfriend` in (800, −560), `Upgrades` in (512, −990), `Props` (istanza di `tutorial_props.tscn` in (800, −560)), `NextWaveTimer` (20 s). A runtime `level.gd` aggiunge il nodo `Pathfinder` e il popup del bonus sotto l'HUD |
| `Characters/player.tscn` | `player.gd` | CharacterBody2D `motion_mode = 1` (Floating), gruppo `player`; `AnimatedSprite2D` (`player_frames.tres`, scala 4, offset (0, −3), nearest) e `MovingThrow` (Sprite2D, hframes 8, vframes 64), entrambi con un `GroundShadow` figlio; `RayCast2D` scala (2, 2), target (50, 0); collider 56×48 in (0, 52) |
| `Characters/enemy.tscn` | `enemy.gd` | CharacterBody2D `motion_mode = 1`, gruppo `enemy`; `AnimatedSprite2D` (`enemy_frames.tres`, scala 4, offset (0, −3)) con ShaderMaterial `hit_flash` creato in `_ready` (uno per nemica); collider 56×48 in (0, 52); Area2D `Hurtbox` 72×172 in (0, −10); barra salute `LiquidBar` sopra la testa; Timer `DeadTimer` e `AttackCooldown` (1,4 s) |
| `Characters/boyfriend.tscn` | `boyfriend.gd` | CharacterBody2D, gruppo `target`; `AnimatedSprite2D` scala 4, offset (0, −5), nearest, `boyfriend_frames.tres`; collider 64×60 in (0, 54); `HitZone` (Area2D, cerchio raggio 185 centrato in (0, 54)) |
| `Objects/projectiles.tscn` | `projectiles.gd` | Area2D `SandBall`, gruppo `sand_ball`; `AnimatedSprite2D` scala (2, 2); collider 24×22 in (1, 0); Timer `Used` (3 s) |
| `Objects/puff.tscn` | nessuno | `AnimatedSprite2D` `Puff` (scala 4, z_index 1), 6 fotogrammi 32×32 a 12 FPS, `autoplay`; `animation_finished` collegato al proprio `queue_free` |
| `Objects/hud.tscn` | `hud.gd` | sezione 16 |
| `Objects/wave_bonus_popup.tscn` | `wave_bonus_popup.gd` | sezione 16 |
| `Objects/upgrades.tscn` | `upgrades.gd` | chiosco, sezione 15 |
| `Scenes/upgrades_purchase.tscn` | `upgrades_purchase.gd` | pannello acquisti, sezione 15 |
| `Objects/Items/item.tscn` | `Objects/Items/item.gd` (`class_name Item`) | scheda di un oggetto, sezione 15 |
| `Objects/Props/<nome>.tscn` | nessuno | 79 elementi di scena, sezione 14 |
| `Scenes/tutorial_map.tscn`, `Scenes/tutorial_props.tscn` | nessuno | mappa e disposizione dei props, generate da script (sezione 14) |
| `Scenes/pause_menu.tscn`, `game_over.tscn`, `options.tscn`, `tutorial.tscn` | `pause_menu.gd`, `game_over.gd`, `options.gd`, `tutorial.gd` | menu secondari. La pausa si alterna con Esc; Riprendi, Ricomincia (`_on_restart_pressed`: toglie la pausa e ricarica `level.tscn`, come `game_over.gd`) e Torna al Menù |

Gli script di `Player`, `Boyfriend` e `Upgrades` sono agganciati alle scene base; `level.tscn` le istanzia senza ridefinire script o `ball`.

## 7. Livello (`level.gd`)

- **Valori della progressione** (con le formule di `Formulas`, sezione 4): ondata 1 = 3 nemiche / 50 salute / 5 danno; ondata 5 = 5 / 78 / 6; ondata 10 = 8 / 121 / 8; ondata 20 = 14 / 237 / 10; ondata 30 = 20 / 393 / 13.
- **Costanti:** `base_enemy_health` 50, `base_enemy_damage` 5, `base_enemy_number` 3, `base_enemy_points` 10, `base_enemy_currency` 18; `WAVE_BONUS_PERFECT` 0,5, `WAVE_BONUS_GUARDED` 0,25, `WAVE_BONUS_WEAK` 0,1.
- **Spawn:** `spawn_enemy()` prende un punto globale da `World/EnemySpawn.calculate_spawn_point()`, lo converte con `to_local()`, istanzia `enemy.tscn`, le assegna `pathfinder` e chiama `set_spawn_values(target, hp, damage)` con salute e danno da `Formulas.calculate`.
- **Sconfitta:** `_on_defeated()` somma `point_multiplier * base_enemy_points` ai punti e accredita `roundi(currency_multiplier * base_enemy_currency)` a `Global.currency` e a `wave_currency`; aggiorna sconfitte, rimaste e punti nell'HUD.
- **Bonus di fine ondata:** `wave_bonus_rate()` restituisce 0 se `hp < max_hp`; altrimenti in base allo `shield`: al massimo `WAVE_BONUS_PERFECT`, oltre il 50% (escluso) `WAVE_BONUS_GUARDED`, sopra 0 `WAVE_BONUS_WEAK`, a 0 nulla. `_award_wave_bonus()` aggiunge `roundi(wave_currency * rate)` a `Global.currency` e, se maggiore di 0, chiama `bonus_popup.play("Bonus ondata +N%", "+X monete")`.
- **Bonus sulle monete:** `_on_bonus_purchased` somma `bonus` a `currency_multiplier` per `effect == "coin_bonus"`; `_on_item_expired` lo sottrae per gli oggetti Bonus `coin_bonus` scaduti.
- **Area di gioco:** `_play_area()` = rettangolo visibile dalla camera (viewport / zoom) meno le bande dell'HUD (altezza da `custom_minimum_size.y`), in coordinate globali; il Player lo usa per il clamp.
- **Limiti del mondo:** `_world_bounds()` = unione di posizione del ragazzo, rettangolo usato di `World/TutorialMap/Ground` e zone di spawn; serve alla griglia del pathfinder.
- `update_timer_text()` scrive in `NextWave` (BBCode) "Prossima ondata tra: N" con i secondi in `#ffcc47`.

## 8. Giocatore (`player.gd`)

- **Movimento:** `Input.get_vector` sulle azioni `ui_*`. `SPEED_LEVELS` [320, 360, 400], `speed_level` 0–2; `get_input()` ricalcola `nominal_speed` a ogni frame (`speed * 2` con `run`, che seleziona anche Dash). Asse dominante per l'animazione, precedenza orizzontale sulle diagonali esatte; l'idle mantiene l'ultima direzione. `Global.is_in_purchase` blocca tutto.
- **Clamp:** dopo `move_and_slide()` la posizione è limitata a `play_area` con i margini del corpo `BODY_HALF_WIDTH` 40, `BODY_TOP` 95, `BODY_BOTTOM` 77.
- **Animazione:** `update_animation()` sceglie `idle_`, `walk_` o `dash_` + `Formulas.direction_name(velocity)`; `last_animation` ricorda l'ultima direzione.
- **Lancio:** `shoot_sand` chiama `start_throw()`, che orienta la posa verso il mouse e avvia `throw_<dir>`. Al frame `throw_release_frame` (3) `shoot_sand()` istanzia la palla con `ray_cast.look_at(mouse)` e danno `damage` (10), copia `ray_cast.global_transform` dopo averla aggiunta al padre ed emette `throw_released`. Il padre della palla è l'owner del Player o, se assente (scena avviata con F6), il suo `get_parent()`: la palla non segue il Player.
- **Ripetizione:** `start_throw()` esce se `is_attacking` è vero e `_can_throw_again()` è falso: serve palla già rilasciata e `animations.frame + frame_progress >= throw_recovery_frame` (5,5).
- **Velocità di lancio:** `THROW_FPS_LEVELS` [8, 16, 32] per `throw_speed_level` 0–2; `start_throw()` passa `FPS del livello / FPS del .tres` (32) come `custom_speed` di `animations.play()`. Rilascio dopo circa 375 / 187 / 96 ms; intervallo minimo tra due lanci circa 690 / 345 / 175 ms (1,45 / 2,9 / 5,7 lanci al secondo). `throw_recovery_frame` 5,5 corrisponde al braccio a circa 30° dal corpo.
- **Lancio in movimento:** `_update_moving_throw()` mostra `MovingThrow` al posto dell'AnimatedSprite2D, con texture cardinale o diagonale; riga = azione*32 + direzione*8 + fase del passo, colonna = frame del lancio. Se si apre il negozio durante un lancio, `_on_animation_frame_changed` lo conclude senza rilasciare la palla, ma `throw_released` viene emesso.
- **Acquisti** (`_on_item_purchased`, segnale `item_player_purchased`): `damage` somma `roundi(damage_base * bonus)` (`damage_base` = danno iniziale preso in `_ready`); `throw_speed` e `move_speed` salgono di un livello fino a 2.

## 9. Nemica e pathfinding (`enemy.gd`, `pathfinder.gd`)

- **Valori:** `speed` 100; salute e danno da `set_spawn_values`. `_ready` prende `../Boyfriend` come `target`, imposta la barra e si iscrive a `enemy_attacking`.
- **`_physics_process`:** se è morta o attacca la velocità è 0, altrimenti `_steer()`; poi `move_and_slide()` e `update_animation()`.
- **Pathfinder** (`Scripts/pathfinder.gd`, `class_name Pathfinder`, creato da `level.gd` e passato a ogni nemica): `build(bounds)` aspetta 2 frame fisici, poi costruisce un `AStarGrid2D` con celle `CELL_SIZE` 40 su `bounds` + `MARGIN` 400 e blocca le celle dove un rettangolo `PROBE_SIZE` 56×48 spostato di `PROBE_OFFSET` (0, 52) tocca un corpo che non sia `CharacterBody2D` (acqua della TileMap, negozio, props solidi). `find_path(from, to, blockers)`: percorso parziale ammesso; i `blockers` bloccano per quella ricerca le celle entro `BLOCKER_RADIUS` 80; partenza e arrivo spostati sulla cella libera più vicina (raggio `FREE_CELL_SEARCH_RADIUS` 8); percorso semplificato in linea retta dove libero. Prima che la griglia sia pronta restituisce un percorso vuoto e la nemica va diritta.
- **Posti attorno al ragazzo:** ogni nemica ha uno `slot_angle` e punta a `_slot_point(angle)`, a `SLOT_RADIUS` 185 px dal ragazzo. `_pick_slot()` parte dall'angolo di arrivo e prova a passi di `SLOT_STEP` (30°) fino a 360°, saltando i posti `_slot_taken()`: occupati dal Player, da una nemica che attacca o da una viva più vicina al ragazzo, se entro `SLOT_RING_MAX` 320 px e a meno di `SLOT_ARC` (24°). Se non trova posti liberi torna a uno già occupato: non c'è limite al numero di posti né coda.
- **`_steer(delta)`:** ricalcola il percorso ogni `REPATH_INTERVAL` 0,5 s (+ fino a 0,2 s casuali; blocchi = nemiche che attaccano e Player, `_blockers()`), avanza al waypoint successivo entro `WAYPOINT_RADIUS` 30, somma `_separation()` (peso `SEPARATION_WEIGHT` 1,5, raggio `SEPARATION_RADIUS` 110, con componente laterale; direzione limitata a lunghezza 1, non normalizzata). **Blocco:** ogni `STUCK_TIME` 0,6 s confronta il percorso rimasto (`_path_remaining()`); se è calato meno di `STUCK_PROGRESS_RATIO` 0,3 del previsto sceglie un altro posto escludendo quello fallito. Se nel frame precedente ha urtato qualcosa (`blocked_normal`) la direzione viene proiettata lungo la superficie a piena velocità, o girata di lato con `slide_side` (casuale, fisso per nemica).
- **Animazione:** `update_animation(delta)` smorza velocità (`move_speed`) e direzione (`facing`) con `MOTION_SMOOTHING` 6. `flirt_<dir>` se `is_attacking`; `idle_<dir>` rivolta al ragazzo se la velocità reale è sotto il 10% di `speed`; altrimenti `walk_<dir>`. Usa `get_real_velocity() - knockback`, così il rinculo non fa girare lo sprite. Da morta non fa nulla.
- **Colpita:** `take_damage(amount, from_direction)` toglie salute, avvia il lampo (`HIT_FLASH_TIME` 0,1 s sul parametro `flash` dello shader), un rinculo `HIT_KNOCKBACK` 220 px/s che decade di `KNOCKBACK_DECAY` 1400/s e, se non attacca, `HIT_STUN_TIME` 0,15 s di stordimento. Crea il numero fluttuante giallo (`DAMAGE_TEXT_COLOR`).
- **Morte:** `dead()` sceglie la direzione (verso il ragazzo se attacca o non si è mai mossa, altrimenti `facing`), disattiva il collider, nasconde la barra, gioca `dead_<dir>`, emette `defeated` e avvia `DeadTimer` per `DEAD_LINGER_TIME` 1,7 s. `_on_dead_timer_timeout` istanzia `puff.tscn` a `position + PUFF_OFFSET` (0, 8) come figlio del livello e dopo `PUFF_COVER_TIME` 0,2 s fa `queue_free()`.
- **Barra salute:** `LiquidBar` verde, arancio sotto il 50%, rossa sotto il 25%.
- **Spawn:** `Scripts/enemy_spawn.gd` (su `World/EnemySpawn`) raccoglie i `CollisionShape2D` figli in `spawn_areas`; `calculate_spawn_point()` sceglie un'area con probabilità proporzionale alla superficie e restituisce un punto globale casuale al suo interno.

## 10. Ragazzo (`boyfriend.gd`)

- `hp` e `shield` 100, `max_hp`/`max_shield` e `base_max_*` = valori iniziali.
- **Danno** (`_on_enemy_attack`): con `shield > 0` toglie `mini(ceili(damage * (1 - guard_shield)), ceili(shield))`, quindi l'eccedenza non passa alla fedeltà; altrimenti toglie `ceili(damage * (1 - guard_health))` da `hp`. Emette `update_health_shield`, crea il numero fluttuante (`SHIELD_TEXT_COLOR` azzurro, `HEALTH_TEXT_COLOR` rosso); a `hp <= 0` emette `game_over`.
- **Acquisti** (`_apply_bonus`, solo categoria `Target`, `match` su `[effect, sub_category]`): `restore` somma `max * bonus` a `shield` o `hp` con tetto al massimo; `max` chiama `set_max_shield`/`set_max_hp` con `roundi(base_max * bonus)`, che alzano il massimo, riempiono la parte aggiunta ed emettono `update_max_health_shield`; `guard` somma `bonus` a `guard_shield` o `guard_health`. `_on_item_expired` sottrae `bonus` dalla protezione scaduta.
- **Animazione:** `attackers` = nemiche nell'`HitZone` (aggiunte in `body_entered`, tolte in `body_exited`, filtrate se morte o liberate). `update_animation`: nessuna → `idle_down`; `shield > 0` → `idle_down` con, ogni `GLANCE_PAUSE` (2,5–5 s casuali), una `glance_<dir>` verso un'attaccante a caso, una volta sola; `shield <= 0` e `hp > max_hp * FLEX_HP_RATIO` (0,5) → `admire_<dir>` verso l'attaccante più vicina; altrimenti `flex_<dir>`.

## 11. Palla di sabbia (`projectiles.gd`)

- Area2D che avanza lungo `transform.x` a `speed` 400 (la scala 2 ereditata dal RayCast2D raddoppia lo spostamento; per lo stesso motivo lo sprite a scala 2 rende 1 pixel = 4 px a schermo).
- `body_entered`: nemica (gruppo `enemy`) con `hp > 0` → blocca il proiettile una sola volta, gioca `impact`, chiama `body.take_damage(damage, transform.x)`, e `body.dead()` se la salute arriva a 0. `area_entered` → `_on_area_entered` rimanda a `_on_body_entered(area.get_parent())`, così riceve i colpi l'`Hurtbox` della nemica. Gruppi `upgrades` e `solid_prop` → `_impact()` senza danno. Si elimina a fine impatto.
- `_face_upright` imposta `flip_v` quando va a sinistra.
- A fine volo (timer `Used`, 3 s) `_on_used_timeout` avvia `land`: spegne monitoring e collider, rallenta di `LAND_DECEL` 1500/s; `_on_animation_finished` la elimina.

## 12. Collisioni e ordine di disegno

- **Layer 1:** Player, ragazzo, negozio, acqua e battigia della TileMap, props solidi. **Layer 2:** nemiche (maschera 1, quindi non si urtano tra loro) e `Hurtbox` delle nemiche (maschera 0, `monitoring` spento).
- Player (`collision_mask = 3`), `HitZone` del ragazzo e `SandBall` (maschera 3) vedono le nemiche. Una nuova Area2D o un nuovo corpo che deve interagire con le nemiche deve includere il layer 2.
- **Forme a terra (impronte ai piedi):** Player e nemica 56×48 in (0, 52); ragazzo 64×60 in (0, 54); `HitZone` cerchio raggio 185 in (0, 54), così le nemiche si fermano alla stessa distanza da ogni lato. `Hurtbox` della nemica 72×172 in (0, −10): da y −96 (8 px sotto la cima dei capelli, perché gli angoli del collider della palla sporgono) ai piedi.
- Player e nemica usano `motion_mode = 1` (Floating): i contatti sono pareti, senza trasporto da pavimenti mobili.
- **Ordine di disegno:** `Level` ha `y_sort_enabled`. `World` (mappa) a Z −3; decalcomanie dei props a Z −2 assoluto; tutte le ombre a Z −1 assoluto; corpi di Player, ragazzo, negozio, nemiche e props solidi a Z 0, ordinati per y. L'origine di personaggi e props sta 52 px sopra i piedi; il confronto è tra origini, quindi sprite di altezze diverse possono avere ordine imperfetto.

## 13. Ombre al suolo

- `Scripts/ground_shadow.gd` (`@tool`, Sprite2D) è figlio dell'AnimatedSprite2D nelle tre scene personaggio e di `MovingThrow` nel Player. Mantiene texture, frame (compresi atlanti cardinali e diagonali), centratura, offset, flip e regioni; eredita trasformazione e visibilità. Si aggiorna con i segnali di frame e animazione; `_process` sincronizza le proprietà senza segnale.
- `Assets/Shaders/ground_split.gdshader` con i materiali condivisi `ground_body.tres` e `ground_shadow.tres`: due passaggi della stessa texture, corpo con alpha ≥ 0,5 e ombra con alpha < 0,5. Il helper assegna il materiale del corpo solo se il sorgente non ne ha già uno. `hit_flash.gdshader` esclude l'ombra: il lampo resta sul corpo.
- Ogni `GroundShadow` ha `z_index = -1`, `z_as_relative = false`; il nodo `Shadow` del negozio e dei props segue la stessa convenzione.
- **Contratto alpha** dei PNG dei personaggi: solo 0, 97, 255; la semitrasparenza è riservata all'ombra. Shader personalizzati sugli sprite devono mantenere il filtro del corpo.

## 14. Mondo: terreno, mappa, spawn, props

- **TileSet** `Assets/Tiles/terrain/terrain_tileset.tres` con `terrain_atlas.png` (576×448: 9×7 tile da 16 px d'arte, esportate a scala 4 = 64 px). Tile 64×64, una sorgente atlante (id 0), layer fisico 0 `collision_layer = 1` (acqua e parte d'acqua della battigia), un set di terreno a angoli Sabbia/Acqua, 41 tile.
  - Layout: riga 0 sabbia a–d (a liscia), sabbia bagnata a–b, acqua a–c (c profonda, da mettere a mano); righe 1–4 costa a 16 configurazioni nelle colonne 0–3, tile in `col = c % 4`, `riga = 1 + c // 4` con `c` = bit TL1 TR2 BR4 BL8; righe 5–6 altre 18 sabbie con un solo particolare piccolo a 2 px dai bordi. Le tile di costa hanno sabbia liscia.
  - Generazione: `Tools/pixelorama/terrain_gen.py` (atlante) → Pixelorama (`terrain.pxo`, export scala 4) e `terrain_tileset_gen.py` (`.tres`).
- **Mappa** `Scenes/tutorial_map.tscn`: nodo `TutorialMap` con un solo `TileMapLayer` `Ground` (62×42 celle, x −31..30, y −21..20, cioè 3968×2688 px, 8 tile oltre l'inquadratura per lato; origine = angolo di tile al centro della camera; nearest). Istanziata in `World/TutorialMap` in (800, −560). Scritta interamente da `Tools/level/tutorial_map_gen.py` (valori sugli angoli, tile per configurazione, baia a gradini in alto a destra, varianti di sabbia da seme fisso con `sand_variant`: sabbia liscia dove i vicini hanno già un particolare, mai la stessa variante accanto): non modificarla a mano.
- **Zone di spawn:** `World/EnemySpawn` ha quattro `CollisionShape2D` rettangolari (sinistra, destra, alto, basso) subito fuori dall'inquadratura, a 160–360 px dal bordo, senza rotazione né scala. Quella in alto si ferma prima della baia e quella a destra parte sotto la baia: nessuna nemica nasce dal mare.
- **Props:** ogni elemento ha una scena riusabile in qualsiasi livello in `Objects/Props/<nome>.tscn` (79), scritta da `Tools/level/props_gen.py`, non a mano. Radice Node2D o, per i solidi, StaticBody2D (layer 1, maschera 0, gruppo `solid_prop`, `metadata/_edit_group_`); due Sprite2D (`Shadow` con `ground_shadow.tres` a Z −1 assoluto; `Sprite2D` con `ground_body.tres`) sulla stessa regione di `Assets/Props/props_atlas.png` (offset = −punto d'appoggio, scala 4); `CollisionPolygon2D` in (0, 52) dal `footprint` di `props.json` (inviluppo convesso delle ultime righe opache dello sprite). Per mettere i piedi in (X, Y) si istanzia in (X, Y − 52).
  - Decalcomanie (ciottoli, conchiglie, fiori, palme giovani, teli, tavole sdraiate): corpo a Z −2 assoluto, nessuna collisione.
  - Granchio (`shell_crab`, tabella `ANIMS`): due `AnimatedSprite2D` (corpo e ombra) con lo stesso `SpriteFrames` (fotogrammi `shell_crab_0..3`, 6 voci con durate relative, 3 FPS, ciclo di circa 3,3 s, `autoplay`); solido (poligono dal fotogramma 0) ma disegnato al livello delle decalcomanie.
  - `Scenes/tutorial_props.tscn`: radice Node2D con `y_sort_enabled` e solo istanze dei props alle posizioni della tabella `LAYOUT` (coordinate in tile dal centro della camera; 37 nodi, 26 solidi). Istanziata in `Level/Props` in (800, −560).
  - `python Tools/level/props_gen.py <radice> [--scenes] [--layout] [--force]`: senza flag scrive solo le scene dei props mancanti; `--scenes` riscrive tutte le scene (dopo un cambio di atlante); `--layout` riscrive `tutorial_props.tscn` e rifiuta se esiste, salvo `--force` (che cancella i ritocchi a mano). Controlla che `props.json` esista, che i nomi di `LAYOUT` siano props e che i rettangoli stiano nell'atlante. Regola di `LAYOUT`: nessuna coppia di solidi a meno di circa 2,5 tile (tranne i gruppi di palme e scogli ai bordi), nessun solido vicino al negozio.
  - Sprite: `Tools/pixelorama/props_gen.py <cartella>` disegna 82 sprite a codice e scrive `props.json` (da copiare in `Tools/pixelorama/`); passare l'atlante da Pixelorama (`props.pxo`, `export_png` scala 1) in `Assets/Props/props_atlas.png` (640×286), reimportare in Godot, poi `props_gen.py <radice> --scenes`.

## 15. Negozio e oggetti

- **Chiosco** (`Objects/upgrades.tscn`, `upgrades.gd`, StaticBody2D gruppo `upgrades`): `Shadow`, `Back`, `Front` (Sprite2D statici) e `Shopkeeper` (AnimatedSprite2D, `shopkeeper_frames.tres`), tutti a scala 4, nearest, in (0, −126,12); `Shadow` a Z −1 assoluto, gli altri a Z 0. L'origine del chiosco sta 40 px sopra quella dei sorgenti grafici (istanza in `Level` a (512, −990)): è la sua chiave di ordinamento per y, e deve restare sopra l'origine del Player quando questo è premuto contro il bordo anteriore del bancone (y relativa 38,6), altrimenti il chiosco copre la protagonista. Il piano del bancone è in `Back`; bordo, tenda e tetto in `Front`, così le braccia del negoziante restano visibili con la profondità giusta.
  - Collisioni (layer 1): `CollisionPolygon2D` rettangolare 367×111 (y da −44,1 a 66,6) e poligono ellittico `barrel` centrato in (−203, 52,5). `Area2D` frontale rettangolare davanti al bancone (layer 0, maschera 1, filtra il gruppo `player` nel codice).
  - `player_in_range` segue entrata e uscita dall'area. `_can_purchase()` richiede prossimità e `NextWaveTimer` attivo: F apre `UpgradesPurchase` e imposta `Global.is_in_purchase`. `_update_purchase_state()` aggiorna l'invito `UpgradesInteract` anche se la pausa inizia con il Player già vicino; uscita o scadenza chiudono il pannello e ripristinano `Global`. Esc chiude con il meccanismo `purchase_just_closed`. UI e timer opzionali consentono l'anteprima della scena isolata.
  - **Frasi** (`Balloon`, vedi sotto): `upgrades.gd` ascolta `wave_purchase_item` e, se `wave % Item.PRICE_WAVE_STEP == 0`, fa dire `PRICE_RISE` con `roundi(Item.PRICE_GROWTH * 100)` (il fumetto resta finché non viene zittito). Ascolta i tre `item_*_purchased` (imposta `visit_purchased`) e `purchase.visibility_changed`: all'apertura azzera `visit_purchased` e zittisce il fumetto; alla chiusura, da qualunque percorso (F/Esc, pulsante Esci, uscita dall'area, fine pausa), dice `THANKS_PURCHASE` o `THANKS_VISIT` per `THANKS_TIME` (3 s). `NextWaveTimer.timeout` zittisce il fumetto (fine pausa). Tutti i collegamenti con UI e timer sono opzionali.
  - Gesti: `GestureTimer` one-shot attende 5–10 s e avvia `clean_glass` o `wipe_counter` evitando l'ultimo; `animation_finished` torna a `idle` e riavvia il timer.
- **Fumetto di Sandro** (`Scripts/shop_balloon.gd`, `class_name ShopBalloon`, nodo `Balloon` di `Objects/upgrades.tscn`: `Node2D` nascosto, `z_index` 100, `texture_filter` lineare, in (10, −106) rispetto al chiosco): l'origine è la punta della coda, posta sulla bocca di Sandro; il corpo si apre a destra e in basso, perché sopra il chiosco lo schermo finisce. API: `say(text, duration := 0.0)` (0 = resta finché non lo si zittisce) e `hush()`; entrambi animano la scala attorno all'origine (`POP_TIME` 0,18 s `TRANS_BACK`; `HIDE_TIME` 0,12 s) e un `Timer` interno chiama `hush()` allo scadere. Tutto è disegnato in `_draw()`:
  - **Sfondo:** una sola texture a 9 zone, `Assets/UI/shop_balloon.png` (198×164), con la coda nell'angolo in alto a sinistra. L'angolo non si stira, quindi la coda mantiene la forma per qualunque testo. `StyleBoxTexture` con margini sinistro `BODY_OFFSET.x + CORNER` (114), alto `BODY_OFFSET.y + CORNER` (80), destro e basso `CORNER` (44); si disegna in `Rect2(-TIP, body_size + BODY_OFFSET)`. `TIP` (7, 6) è la punta della coda nella texture, `BODY_OFFSET` (70, 36) l'angolo in alto a sinistra del corpo (contorno compreso).
  - **Testo:** `draw_multiline_string` nel font `BodyLabel` del tema, `FONT_SIZE` 46 (circa 18 px a schermo con lo zoom 0,4: se cambia lo zoom va aggiornato), `MAX_TEXT_WIDTH` 460, `PADDING` (30, 22), colore `INK_COLOR`. Il testo è misurato con `get_multiline_string_size` e il corpo si adatta alle righe (il corpo non deve scendere sotto 88×88, cioè due angoli da 44).
- **Catalogo** `Files/item_list.csv`: separatore `;`, 15 colonne `id, name, description, bonus, order, category, sub_category, image, price, max_purchases, effect, duration, min_wave, every, cooldown`. Categorie `Player`/`Target`/`Bonus` (Giocatore/Partner/Bonus); `max_purchases` 0 = illimitato; `duration` = ondate di durata, 0 = permanente; `price` = prezzo base (il prezzo mostrato lo calcola `Item.price()`); `min_wave` = prima ondata finita (pausa dopo l'ondata N) in cui l'oggetto diventa acquistabile, 0 = subito; `every` = N > 0: acquistabile solo nelle pause dopo un'ondata multipla di N; `cooldown` = pause saltate dopo ogni acquisto (1 = non acquistabile nella pausa seguente); `image` = file in `Assets/Icons/` o percorso `res://`. Letto con `FileAccess`: il suo `.import` usa `importer="keep"`, altrimenti il CSV non entra negli export.
- **Effetti:** `restore`, `max`, `guard` (Target, sezione 10); `damage`, `throw_speed`, `move_speed` (Player, sezione 8); `coin_bonus` (Bonus, sezione 7).
- **Pannello** (`Scenes/upgrades_purchase.tscn`, `upgrades_purchase.gd`): CanvasLayer con `Panel` centrato 900×580 > `Margin` > `Layout`; intestazione con nome `ShopName` ("Chiosco da Sandro") e saldo; tre tab = `ScrollContainer` con `VBoxContainer` `%PlayerSections`, `%TargetSections`, `%BonusSections`.
  - `load_item_file()` salta le righe con meno di 15 colonne o senza id, crea un `Item` per riga e lo mette nel tab della categoria. `populate_tab()` ordina per `order` e raggruppa per `sub_category`.
  - `add_section()` crea un `VBoxContainer` con intestazione (`Button` a levetta, flat, freccia disegnata da `arrow_icon()`: giù = aperta, destra = chiusa), `HSeparator` e un `GridContainer` `Items` a `ITEM_COLUMNS` (3) colonne; `_set_section_expanded` mostra o nasconde la griglia; lo stato non è salvato. `SECTION_TITLES` dà titoli e ordine (Shield = Moralità, Health = Fedeltà); i tab in `SECTIONLESS_TABS` (Player, Bonus) hanno una sola griglia senza intestazione (titolo vuoto); una `sub_category` nuova compare in fondo con il nome grezzo.
  - `_on_wave_finished(wave)` (connesso a `SignalManager.wave_purchase_item`, emesso da `level.gd.check_all_eliminated()` con l'ondata appena finita) imposta `item.wave = wave` su ogni scheda, poi scala `waves_left` dei temporanei ed emette `item_expired` a zero, infine `_refresh_items()`. Nessuna scheda viene nascosta: sblocchi e attese disattivano il pulsante e mettono un tooltip.
- **Scheda** (`Objects/Items/item.tscn`, `Objects/Items/item.gd`): larghezza minima 240 px; `Content` > `Top` (icona 48×48, `Texts` con nome e descrizione) e `BuyButton` (prezzo corrente `"%d¢"`, "Max" o "Attivo (n)"); `data` = riga del CSV come dizionario, `purchases`, `waves_left`, `useless`, `wave` (ondata appena finita, impostata dal negozio), `bought_wave` (ondata della pausa dell'ultimo acquisto, −1 = mai); emette `purchase_requested(item)`.
  - `price()`: `data["price"] × 1,25^passi` arrotondato a multipli di 5 con un solo arrotondamento finale (`PRICE_GROWTH` 0,25, `PRICE_WAVE_STEP` 5, `PRICE_ROUNDING` 5); i passi sono `purchases` se `max_purchases > 0`, altrimenti `floori(wave / 5)`.
  - `wait_waves()`: ondate che mancano per `every` (`every − wave % every`) e per `cooldown` (`bought_wave + cooldown + 1 − wave`, solo con `cooldown > 0`), il maggiore dei due. `lock_text()`: "Acquistabile dopo l'ondata N" se `wave < min_wave`, altrimenti "Acquistabile tra N ondata/ondate" se `wait_waves() > 0`, altrimenti vuoto. `refresh()` lo scrive in `tooltip_text` della scheda e del pulsante.
  - `can_buy(valuta)`: non al massimo, non `useless`, `waves_left == 0`, `lock_text()` vuoto e `valuta >= price()`.
  - Test: `tests/test_shop_items.gd` (suite `shop_items`). `Item` non è `@tool`, quindi nell'editor lo script è un segnaposto e il test non gira con `test_run`: si esegue a runtime con Godot da riga di comando (vedi `Docs/GODOT.md`).
- **Spesa:** `_purchase_item(item)` esce se `item.can_buy(Global.currency)` è falso (valuta insufficiente, massimo raggiunto, temporaneo attivo o `useless`: un `restore` con la barra piena, calcolato da `_is_useless()` sul nodo del gruppo `target` a ogni `currency_changed` e `update_health_shield`); altrimenti calcola `item.price()` **prima** di incrementare `purchases` (il prezzo dipende dagli acquisti già fatti), poi incrementa `purchases`, imposta `bought_wave = wave`, `waves_left = duration`, sottrae il prezzo da `Global.currency` ed emette il segnale della categoria con `data`.

## 16. Interfaccia

- **HUD** (`Objects/hud.tscn`, `hud.gd`): CanvasLayer con `process_mode = 3` (sempre attivo: a game over, con l'albero in pausa, le barre arrivano comunque al valore finale). Bande `TopBand` e `BottomBand` (`Panel` a tutta larghezza, alti 44 px logici, `StyleBoxTexture` con `Assets/UI/band_top.png` e `band_bottom.png`, 3456×132). In alto `Wave`, `Points`, `Currency`; in basso `ShieldBar` e `HealthBar` (icona 32×32 + barra 200×24 con `Label` "valore / massimo" aggiornata in `_process`) e `Remain`, `Defeated`. Nodi con nome univoco: `%WaveValue`, `%PointsValue`, `%CurrencyValue`, `%DefeatedValue`, `%RemainValue`, `%Health`, `%Shield`, `%HealthValue`, `%ShieldValue`. `hud.gd` espone `top_band` e `bottom_band`. `level.tscn` aggiunge sotto l'HUD `NextWave` e `UpgradesInteract`.
- **Barre a liquido** (`Scripts/liquid_bar.gd`, `class_name LiquidBar`, shader `Assets/Shaders/liquid_bar.gdshader`): ProgressBar disegnate dallo shader (vetro, liquido, riflessi, fronte ondulato), senza immagini; il valore mostrato scende gradualmente. Usate per moralità, fedeltà e salute delle nemiche. Dettagli in `Docs/GODOT.md`.
- **Numeri fluttuanti** (`Scripts/floating_text.gd`, `class_name FloatingText`, Label senza scena creata da `FloatingText.spawn(parent, at, value, color)` statico): partono da `HEAD_OFFSET` (0, −230) sopra l'origine del personaggio, salgono di `RISE` 90 px in `LIFETIME` 0,9 s con dissolvenza ritardata, poi `queue_free`. `FONT_SIZE` 75 = 30 × 1/zoom della camera: se cambia lo zoom va aggiornato.
- **Popup del bonus** (`Objects/wave_bonus_popup.tscn`, `wave_bonus_popup.gd`; istanziato da `level.gd` e aggiunto sotto l'HUD): Control a schermo intero, `process_mode = 1` (pausabile), `mouse_filter` ignore su tutti i nodi, nascosto finché non serve. `Pivot` (Control semplice ancorato al centro, perno in (0, 0)) > `Box` (VBox centrato sul perno, separazione −6) > `Title` (font 34, crema `Color(1, 0.95, 0.84)`, contorno 10) e `Amount` (font 62, oro `Color(1, 0.8, 0.28)`, contorno 14), contorno bordeaux `Color(0.227, 0.078, 0.094)`, variazione `AnnouncementLabel`.
  - `play(title, amount)` uccide il tween precedente, azzera scala, rotazione e alpha di `Pivot` e crea un solo `Tween` parallelo: fase 1 (`GROW_TIME` 0,3 s, `TRANS_QUAD` `EASE_OUT`) scala 0 → `PEAK_SCALE` 1,7 e rotazione 0 → `PEAK_ANGLE` −42°, alpha 0 → 1 in `FADE_IN_TIME` 0,08 s; fase 2 (`SETTLE_TIME` 0,3 s, `TRANS_LINEAR` per entrambe) scala → 1 e rotazione → 0; `HOLD_TIME` 2 s; uscita `EXIT_TIME` 0,6 s con scala → 0 `TRANS_BACK` `EASE_IN` e alpha → 0 negli ultimi 0,27 s; poi `hide`.
  - Animare un Control semplice, mai il figlio di un Container: i Container azzerano scala e rotazione dei figli a ogni riordino.
  - Ritocchi: tenere `PEAK_SCALE × cos(PEAK_ANGLE)` ben sopra 1, altrimenti raddrizzandosi la scritta si allarga in orizzontale e il rimpicciolimento non si vede.
- **Conto alla rovescia** `NextWave`: `RichTextLabel` BBCode sotto la banda alta, testo crema, secondi `#ffcc47`, scritto da `level.gd.update_timer_text()`. `clip_contents = false`: il contorno (`outline_size` 8) di Luckiest Guy sporge sopra il rettangolo del nodo e con il ritaglio attivo veniva tagliato.
- **Tema** `Assets/UI/game_theme.tres` (`gui/theme/custom` in `project.godot`): default Fredoka 400/20; variazioni Label per titoli e annunci (Luckiest Guy), HUD (Bold), tutorial (Medium), schede oggetti. Button, CheckBox, TabBar, TabContainer e RichTextLabel ricevono font e pesi dal tema; le scene UI non hanno override di font locali. Ruoli, misure e licenze in `Docs/FONTS.md`. Font in `Assets/Fonts/` (`Fredoka.ttf`, `LuckiestGuy-Regular.ttf`), licenze in `Assets/Fonts/Licenses/`, incluse da tutti i preset di `export_presets.cfg`.
- **Finestra e camera:** base logica 1152×648, `display/window/stretch/mode = "canvas_items"`, aspect `keep`; nessuno script di ridimensionamento. `Camera2D` del livello fissa (figlia di `Level`, non segue il Player), zoom (0,4; 0,4): mondo visibile 2880×1620.

## 17. Input

`ui_left/right/up/down` (frecce e tasti configurati, gamepad), `shoot_sand` (tasto destro del mouse), `run` (Spazio), `buy_upgrades` (F), `esc` (Esc: chiude il negozio o alterna la pausa), `pause` (P, definita ma non usata da nessuno script). Tasti già occupati: frecce, Spazio, Esc, A, D, F, P, S, W.

## 18. Risorse grafiche e sorgenti

Regola generale: concept art in `Assets/ConceptArt/<soggetto>/` (ignorata da Godot), prompt in `Tools/concept/`, sorgenti Blender in `Tools/blender/` (base comune `base_personaggio.blend`, codice comune `concept_model.py`, un `.blend` e uno script per personaggio, riferimenti in `Tools/blender/ref/`), sorgenti Pixelorama in `Tools/pixelorama/`, sorgenti GIMP (`.xcf` a livelli) in `Tools/gimp/`, generatori del livello in `Tools/level/`. Procedure in `Docs/BLENDER.md`, `Docs/PIXELORAMA.md` e `Docs/GIMP.md`.

- **Player** (`Assets/Characters/Player/`): concept `Assets/ConceptArt/Player/player_turnaround.png`. `player_spritesheet.png` (celle 48×48) e `player_frames.tres`: righe 0–3 `idle_*` (6 frame, 5 FPS, loop), 4–7 `walk_*` (8, 8 FPS, loop), 8–11 `dash_*` (8, 12 FPS, loop), 12–15 `throw_*` (8, 32 FPS, una volta); direzioni up, down, right, left. Diagonali in `player_diagonals_spritesheet.png` (righe = gruppo*4 + NE, NW, SE, SW; stessi frame e FPS), animazioni `<gruppo>_up_right`, `_up_left`, `_down_right`, `_down_left`. `player_moving_throw.png` (384×3072) e `player_diagonals_moving_throw.png`: riga = azione*32 + direzione*8 + fase, azioni Walk 0 / Dash 1. Sorgenti: `personaggio_modello.py` ricostruisce `personaggio.blend` dal turnaround; `blender_pipeline.py` genera i quattro atlanti (`build_all()`, `build_diagonals()` con yaw NE 135, NW −135, SE 45, SW −45, `build_steps()` a lotti per MCP); `render_throw()` usa `KEYS_LEFT` per la vista Ovest, `check_left_throw()` la verifica; `pose_combo` compone i lanci in movimento. La palla in mano di spalle è tolta dallo sprite dove finisce tra i capelli. Contenuto: idle muove solo il busto; lancio con preparazione alta del braccio e arco dall'alto al basso, verso Ovest con il braccio destro anatomico sopra la chioma; rilascio al frame 3.
- **Contorni delle braccia:** `Tools/blender/sprite_contours.py:ArmContours`, usato da `render_sprites()` nelle sei viste laterali e diagonali dei tre personaggi (Freestyle, tratto 1 px esterno al braccio, limitato alla sagoma opaca).
- **Nemica base** (`Assets/Characters/Enemy/`): concept `Assets/ConceptArt/Enemies/enemy_turnaround.png` (prompt `Tools/concept/prompts.json`, voce `enemy_base`). `enemy_spritesheet.png` 768×2048, celle 64×64, 12 colonne, 32 righe = gruppo*8 + direzione (up, down, right, left, up_right, up_left, down_right, down_left); gruppi `walk` (8 frame, 8 FPS, loop), `flirt` (12, 8 FPS, loop), `idle` (6, 5 FPS, loop), `dead` (8, 12 FPS, una volta, resta sull'ultimo frame). Camera `ORTHO = 2.2*64/48`. Sorgenti: `nemica_modello.py:make_enemy()` ricostruisce `nemica.blend` dalla base comune (riusa corpo, testa e chioma del Player; `paint_girl_scalp()` per le tempie); `nemica_pipeline.py` (`build_enemy()`, `build_enemy_steps()` a lotti; `walk_e` riusa gambe, bacino e busto del Player; `flirt()` con IK `pin_feet()`; tabella `FALL` di 8 pose per la caduta; `EYE_SKIN_FIT` e soglia 0,20 per l'occhio nelle diagonali) scrive atlante e `.tres` conservandone lo UID. Verifiche in `verifica_nemica.py:check_enemy()`. Shader del lampo `hit_flash.gdshader`. Contenuto: `idle` quando è ferma o bloccata; `flirt` da ferma, piedi a terra, peso da una gamba all'altra, mano sinistra sul fianco, destra vicino a tempia e capelli, testa inclinata; `dead` caduta a sedere nella direzione guardata (braccia verso terra, busto raccolto, ginocchia sollevate, rimbalzo, seduta stordita).
- **Ragazzo** (`Assets/Characters/Boyfriend/`): concept `Assets/ConceptArt/Boyfriend/boyfriend_turnaround.png` (voce `boyfriend`). `boyfriend_spritesheet.png` 512×2048, celle 64×64, righe = animazione*8 + direzione (ordine delle nemiche), 240 frame: `idle` (6, 5 FPS, loop), `glance` (8, 8 FPS, una volta), `admire` (8, 6 FPS, loop), `flex` (8, 8 FPS, loop). Figura di circa 48 px (righe 5–53, piedi alla riga 53). Sorgenti: `ragazzo.blend`, `ragazzo_pipeline.py` (`build_boyfriend()` riscrive per intero il `.tres`; `hands_on_hips()` condivisa da idle, glance e braccio sinistro di admire; `clear_baked_brows()` e `stamp_face()` per il viso; `EYES_CLOSED` per l'idle). Contenuto: `idle` al sole, mani sui fianchi, mento alzato, occhi chiusi, respira solo il busto; `glance` testa (fino a 90°) e busto (fino a 30°) girati per un attimo verso la nemica, corpo rivolto in basso; `admire` rivolto alla nemica, sporto in avanti, testa inclinata, mano destra al mento, sinistra sul fianco, ondeggia; `flex` doppio bicipite col petto in fuori a impulsi.
- **Palla di sabbia** (`Assets/Projectiles/SandBall/`): `sand_ball.png` (celle 24×24) e `sand_ball_frames.tres`: `flight` 4 frame 12 FPS loop, `impact` 4 frame 26 FPS una volta, `land` 8 frame 14 FPS una volta (texture `sand_ball_land.png`, sorgenti `Tools/pixelorama/sand_ball_land.pxo` e `sand_ball_land_gen.py`).
- **Puff** `Assets/Effects/Puff/puff.png`: 6 frame 32×32, palette #fff6e8 #f6e2b0 #e3c084, contorno #3a1418; sorgenti `Tools/pixelorama/puff.pxo` e `puff_gen.py`.
- **Chiosco e negoziante** (`Assets/Objects/Shop/`): concept `Assets/ConceptArt/Shop/shop_with_shopkeeper_turnaround.png` (e `shop_turnaround.png`, solo edificio; prompt voce `shop`). `shop_shadow.png`, `shop_back.png`, `shop_front.png` (160×160), `shopkeeper.png` (celle 160×160, 40 frame) e `shopkeeper_frames.tres`: `idle` 8 frame 5 FPS loop, `clean_glass` e `wipe_counter` 16 frame 8 FPS una volta. Sorgenti `Tools/blender/shop.blend`, `shop_pipeline.py` (`YAW = 0`, vista frontale; camera a 25°; `setup()`, `build_steps()` a lotti con UID preservato, `check()`), `shop_layout.json` (proiezioni per sprite e collisioni). Il negoziante usa il rig comune a 17 ossa. Contenuto: `idle` respiro leggero e palpebre; `clean_glass` e `wipe_counter` puliscono bicchiere e bancone.
- **Terreno e props:** sezione 14. Concept `Assets/ConceptArt/Terrain/terrain_concept.png` e `props_concept.png`, prompt `Tools/concept/terrain_prompt.json` e `props_prompt.json`. Metadati dei props in `Tools/pixelorama/props.json`.
- **Icone** (`Assets/Icons/`, PNG trasparenti 1254×1254 generati con ImageGen): 14 icone degli oggetti (nomi nella colonna `image` del CSV; l'Infradito Conchiglia usa il segnaposto `res://Assets/icon.svg`), `health.png` e `shield.png` (barre), `wave.png`, `starfish.png`, `coin.png`, `enemy_standing.png`, `enemy_fallen.png` (HUD). Prompt in `Tools/concept/prompts.json` (voce `item_icons`), `item_drinks_prompts.json`, `item_snacks_prompts.json`, `item_upgrades_prompts.json`, `melting_ice_cream_prompt.json`, `beach_umbrella_prompt.json`, `crosswords_prompt.json`, `hud_icons_prompts.json`, `hud_band_prompts.json`.
- **Fumetto di Sandro:** `Assets/UI/shop_balloon.png` (198×164 RGBA) esportato da `Tools/gimp/shop_balloon.xcf` (GIMP): corpo ad angoli arrotondati (raggio 40) con la coda sottile e curva in un solo contorno `#3a1418` di 6 px, riempimento crema con sfumatura verticale `#fff9e8` → `#f7e4bb`. Procedura in `Docs/GIMP.md`.
- **Bande dell'HUD:** `Assets/UI/band_top.png` e `band_bottom.png` generate da `Tools/pixelorama/hud_bands_gen.py` dalle immagini in `Assets/ConceptArt/Hud/` (ritaglio centrale senza chiodi, ripetuto specchiando una copia sì e una no, luminosità al 72% con `DARKEN`).
- **Base dello sfondo del menù:** `Assets/ConceptArt/MenuBackground/menu_background_base.png` (960×540, ignorata da Godot) con sorgente a livelli `Tools/gimp/menu_background.xcf` (livelli: sky, sun, sea, sand, palm). Nessun uso nel codice; il menù attuale non la usa.
- **Immagini conservate** in `Assets/Images/`: `beatch-slash-logo-text-only.png`, `beatch-slash-logo.png`, `beatch-slash-cover-no-logo.png`, `beatch-slash-cover-logo.png`. Nessun uso nel codice.
- **Ricalco del logo solo testo:** `Tools/gimp/beatch_slash_logo_text.xcf` (1448×1086, stessa tela di `beatch-slash-logo-text-only.png`), ricostruzione a livelli in GIMP del logo di Codex: un tracciato per lettera in Luckiest Guy, contorni, riempimenti, bordi interni e riflessi su livelli separati, più il PNG originale come livello nascosto `reference`. Generato dagli script Python-Fu in `Tools/gimp/trace/` (`analyze`, `fit`, `horizon`, `build`, `render`, `details`, `holes`, eseguiti in quest'ordine nella console di `call_api`). Non ancora esportato in `Assets/`; nessun uso nel codice. Livelli e procedura in `Docs/GIMP.md`.
- `Tools/pixelorama/boyfriend.pxo` è un ritocco di un modello superato, non usato.

## 19. Test

Suite in `tests/`, eseguite con Godot AI (procedure in `Docs/GODOT.md`).

- `test_ground_shadows.gd` (suite `ground_shadows`): livelli Z, sincronizzazione di direzioni e frame, `MovingThrow`, visibilità. Carica le scene con `CACHE_MODE_IGNORE_DEEP`.
- `test_enemy_frames.gd` (suite `enemy_frames`): 32 animazioni e 272 regioni 64×64, sia nel riferimento della scena sia su disco.
- `test_shop.gd` (suite `shop`): condizioni d'acquisto, prossimità conservata tra ondate, gesti e ritorno all'idle. Registra temporaneamente le azioni InputMap mancanti e ripulisce solo quelle aggiunte.
- `test_player_projectile.gd`: origine, traiettoria e danno con padre identità, traslato, ruotato e scalato; palla indipendente dal Player avviato da solo.
- `test_shop_items.gd` (suite `shop_items`): prezzi crescenti, sblocco per ondata, `every`, `cooldown`, intestazione del catalogo. Richiede il runtime (`Item` non è `@tool`): nell'editor viene saltato, si esegue da riga di comando (`Docs/GODOT.md`, sezione 25).
- `test_enemy_spawn.gd`: 8 spawn per ciascuna zona, dentro la zona e con il contatore consumato.
- Gli ultimi due richiedono gioco e autoload attivi (esecuzione via `game_eval`); il runner dell'editor li salta.

## 20. Punti fragili e cose da sapere

- Un nuovo oggetto del negozio richiede solo una riga nel CSV se usa un `effect` esistente; un nuovo `effect` richiede un `match` nel listener della sua categoria (player, boyfriend o level), altrimenti l'acquisto spende la valuta senza effetto.
- `enemy.gd` assume che il ragazzo sia il nodo `../Boyfriend` e che `Formulas` e `SignalManager` esistano come autoload.
- La griglia del `Pathfinder` si costruisce una sola volta all'avvio del livello: ostacoli aggiunti o spostati dopo non vengono visti. Se cambia il collider della nemica, aggiornare `PROBE_SIZE` e `PROBE_OFFSET`. Il ragazzo non è un ostacolo della griglia. Il pathfinder legge `tile_set.tile_size` e ignora la scala del layer.
- Se riappaiono ammassi vicino al ragazzo, controllare `_slot_taken()` e `_separation()` in `enemy.gd`, non le collisioni.
- Le zone di spawn assumono rettangoli senza rotazione né scala; puff e nemica condividono il padre e i confronti locali tra nemiche e ragazzo valgono perché sono fratelli.
- Un prop nuovo senza `footprint` in `props.json` non ha collisione: verificare se deve essere solido.
- Durante il game over l'albero è in pausa: HUD sempre attivo, popup del bonus fermo; i test in gioco con eval devono tenerne conto.
- Il popup del bonus dura 0,6 s in entrata: gli screenshot di Godot AI non riescono a campionarlo (usare il registratore descritto nella guida generica di Godot).
- Riordino cartelle possibile (non fatto): scene e script vicini sotto `Scenes/{Characters,Objects,Levels,UI,UI/Shop}`, `Files/` → `Data/`. Va fatto dal dock FileSystem di Godot correggendo le stringhe `res://` nei `.gd`, compresa `"res://Assets/Icons/" + file` in `upgrades_purchase.gd`.
