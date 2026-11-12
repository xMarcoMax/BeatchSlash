# Beatch Slash! — mappa del codice

Da leggere **per prima** per capire come è fatto il progetto; poi `Docs/PROJECT_CONTEXT.md` (visione, stile grafico, stato). Ultimo aggiornamento: 12 novembre 2026. Descrive la struttura, non il diario: se cambi segnali, scene, autoload o flussi, aggiorna questa mappa nello stesso intervento. Verificare sempre contro i file reali.

GDScript, Godot 4.7, renderer Mobile. Scena principale: Scenes/main_menu.tscn. Tutto il testo in gioco è in italiano.

## Flusso di gioco

1. **Menu** (`main_menu.gd`): Nuova partita emette `SignalManager.game_started`, ferma la musica e carica `Scenes/level.tscn`. Opzioni (`options.gd`: volume e mute sul bus 0) e Tutorial portano a scene dedicate e tornano al menu.
2. **Livello** (`Scenes/level.tscn`, `level.gd`): all'avvio `set_variables()` fissa 5 nemiche e moltiplicatori 1. `_process` chiama `spawn_enemy()` (una nemica per frame finché `spawn_number > 0`, in un punto casuale di `World/EnemySpawn`) e `check_all_eliminated()`.
3. **Fine ondata:** quando `defeated_level == total_enemies` parte `NextWaveTimer` (circa 20 s), emette `wave_purchase_item(wave)` e il negozio diventa accessibile. Alla scadenza `set_next_wave()` incrementa l'ondata e ricalcola il numero di nemiche con `Formulas.calculate("enemies", ...)`.
4. **Nemica** (`enemy.gd`): cammina verso il ragazzo; quando il RayCast2D lo tocca si ferma. Il `HitZone` (Area2D) del ragazzo la vede entrare e emette `enemy_attacking(enemy)`: la nemica passa a `is_attacking` e ogni 2 s (`AttackCooldown`) emette `attack_target(damage)`.
5. **Ragazzo** (`boyfriend.gd`): `_on_enemy_attack` toglie prima alla moralità (`shield`), poi alla fedeltà (`hp`), emette `update_health_shield`; a `hp <= 0` emette `game_over`.
6. **Game over:** `level.gd._on_game_over` mostra `UI/GameOver` e mette `get_tree().paused = true`. Riavvio, menu o uscita in `game_over.gd`.
7. **Colpo:** il Player lancia la palla (`player.gd` -> `projectiles.gd`); al contatto con una nemica viva toglie `damage` alla sua salute; a `hp <= 0` chiama `enemy.dead()`, che emette `defeated` e dopo `DeadTimer` fa `queue_free()`. `level.gd._on_defeated` aggiorna punti, valuta e HUD.

## Autoload (project.godot)

| Nome | File | Ruolo |
| --- | --- | --- |
| `Formulas` | Scripts/Autoload/Formulas.gd | `calculate(type, wave, base)` scala nemiche/salute/danno con le ondate (fattori 1.6 / 1.25 / 1.05, cap 12); `direction_name(Vector2)` sceglie una delle 8 direzioni degli sprite (`up`, `down`, `left`, `right`, `up_right`, `up_left`, `down_right`, `down_left`), usata da Player e nemiche |
| `SignalManager` | Scripts/Autoload/SignalManager.gd | bus di segnali globali (tabella sotto) |
| `MusicManager` | Scripts/Autoload/MusicManager.gd | un AudioStreamPlayer; musica del menu; `game_started` la ferma (la musica di spiaggia è commentata) |
| `Global` | Scripts/Autoload/Global.gd | `is_mobile`, `is_in_purchase` (blocca movimento e lanci durante gli acquisti), `purchase_just_closed` (evita che Esc chiuda anche la pausa) |
| `_mcp_game_helper` | addons/godot_ai/... | solo strumenti di sviluppo, non fa parte del gioco |

## Segnali (SignalManager)

| Segnale | Chi emette | Chi ascolta |
| --- | --- | --- |
| `game_started` | main_menu | MusicManager |
| `enemy_attacking(enemy)` | boyfriend (HitZone) | enemy (ogni istanza controlla `attacker == self`) |
| `attack_target(damage)` | enemy.attack | boyfriend `_on_enemy_attack` (si collega una volta in `_ready`) |
| `defeated` | enemy.dead | level `_on_defeated` |
| `update_health_shield(hp, shield)` | boyfriend (danni e bonus) | hud `set_values` |
| `game_over` | boyfriend | level `_on_game_over` |
| `wave_purchase_item(wave)` | level (fine ondata) | upgrades_purchase `damage_item_availability` |
| `purchase_item` | upgrades (tasto F) | nessuno |
| `item_target_purchased(data)` | upgrades_purchase | boyfriend `_apply_bonus` (ripristina moralità o fedeltà) |
| `item_player_purchased(data)`, `item_bonus_purchased(data)` | upgrades_purchase | **nessuno: gli acquisti per Giocatore e Bonus non hanno ancora effetto** |

## Scene e script

| Scena | Script | Note |
| --- | --- | --- |
| Scenes/main_menu.tscn | main_menu.gd | rileva touchscreen (`Global.is_mobile`), avvia la musica del menu |
| Scenes/level.tscn | level.gd | radice `Level`: `UI` (HUD, GameOver, UpgradesPurchase, PauseMenu), `World` (EnemySpawn con 3 CollisionShape2D, TileMapLayer `Beach` e `BeachEnvironment`), `Player` (con Camera2D), `Boyfriend`, `Upgrades`, `NextWaveTimer` |
| Characters/player.tscn | player.gd | CharacterBody2D, gruppo `player`; AnimatedSprite2D + MovingThrow (Sprite2D) + RayCast2D + collider 72x120 |
| Characters/enemy.tscn | enemy.gd | CharacterBody2D, gruppo `enemy`; AnimatedSprite2D, collider 72x120, RayCast2D, ProgressBar salute, Timer `DeadTimer` e `AttackCooldown` (2 s) |
| Characters/boyfriend.tscn | boyfriend.gd (agganciato alla scena base) | CharacterBody2D, gruppo `target`; figlio `HitZone` (Area2D); ancora lo sprite placeholder icon.svg |
| Objects/projectiles.tscn | projectiles.gd | Area2D `SandBall`, gruppo `sand_ball`; Timer `Used` (3 s) |
| Objects/hud.tscn | hud.gd | HUD: ondata, punti, valuta, sconfitte/rimaste, barre fedeltà e moralità |
| Objects/upgrades.tscn | upgrades.gd (agganciato alla scena base) | StaticBody2D del negozio sulla spiaggia, con Area2D di prossimità |
| Scenes/upgrades_purchase.tscn | upgrades_purchase.gd | pannello acquisti con tre tab (Giocatore, Partner, Bonus) |
| Objects/Items/item.tscn | item.gd (`class_name Item`) | scheda di un oggetto in vendita (nome, immagine, descrizione) |
| Scenes/pause_menu.tscn, Scenes/game_over.tscn, Scenes/options.tscn, Scenes/tutorial.tscn | pause_menu.gd, game_over.gd, options.gd, tutorial.gd | menu secondari; la pausa si alterna con Esc (`pause_menu.gd`) |

Gli script di `Player`, `Boyfriend` e `Upgrades` sono agganciati alle rispettive scene base: `level.tscn` istanzia le scene senza ridefinire script o `ball`. Eliminati il 12 nov 2026 perché inutilizzati: `Scripts/pause.gd` e `Scripts/Items/*.gd` (vecchie schede oggetto; gli oggetti reali nascono da `item.tscn` + `Files/item_list.csv`).

## Giocatore (player.gd)

- Movimento: `ui_left/right/up/down` con `Input.get_vector`, velocità 400; `run` (Spazio) la raddoppia e passa a Dash. `Global.is_in_purchase` blocca tutto.
- Animazione: `update_animation()` sceglie `idle_`, `walk_` o `dash_` + direzione da `Formulas.direction_name(velocity)`; `last_animation` ricorda l'ultima direzione.
- Lancio: `shoot_sand` (tasto destro) chiama `start_throw()`, che orienta la posa verso il mouse con `Formulas.direction_name` e avvia `throw_<dir>`. Al frame `throw_release_frame` (3) `shoot_sand()` istanzia la palla con `ray_cast.look_at(mouse)`, danno = `damage` (10), e emette `throw_released`. Un nuovo lancio non interrompe la palla in attesa.
- Lancio in movimento: `_update_moving_throw()` mostra lo Sprite2D `MovingThrow` (atlante cardinale o diagonale; riga = azione*32 + direzione*8 + fase del passo, colonna = frame del lancio) al posto dell'AnimatedSprite2D, mantenendo la fase della camminata.
- Dettagli di sprite e parametri: sezione "Player" di PROJECT_CONTEXT.md.

## Nemica (enemy.gd)

- Spawn: `level.gd` istanzia `enemy.tscn`, chiama `set_spawn_values(target, hp, damage)` con valori scalati da `Formulas`. `@export var speed = 100`.
- `_ready`: prende `../Boyfriend` come `target`, imposta la barra salute, si iscrive a `enemy_attacking`.
- `_physics_process`: il RayCast2D guarda il ragazzo; se tocca qualcosa, se è morta o se sta attaccando la velocità è 0, altrimenti va verso `target`; poi `update_animation()`.
- Animazioni (`Assets/Characters/Enemy/enemy_frames.tres`): `flirt_<dir>` se `is_attacking`; `idle_<dir>` (rivolta al ragazzo) se la velocità reale è sotto il 10% di `speed` (arrivata o bloccata da un'altra nemica); altrimenti `walk_<dir>` secondo il movimento reale. Da morta l'animazione si ferma. Nessuna animazione di colpita o morte (da fare).
- Salute: `ProgressBar` con colore verde/arancio/rosso a soglie 50% e 25%.

## Palla di sabbia (projectiles.gd)

Area2D che avanza lungo `transform.x` a `speed` 400 (la scala 2 ereditata dal RayCast2D raddoppia lo spostamento). `body_entered`: se il corpo è nel gruppo `enemy` e ha `hp > 0`, blocca il proiettile (una sola volta), gioca `impact`, sottrae `damage`, e se la salute arriva a 0 chiama `body.dead()`. `_face_upright` imposta `flip_v` quando va a sinistra. Si elimina a fine impatto o dopo 3 s.

## Negozio e oggetti

- `upgrades.gd`: tasto `buy_upgrades` (F) apre `UpgradesPurchase` solo se `NextWaveTimer` è attivo e imposta `Global.is_in_purchase`; Esc lo chiude. Il testo di invito appare entrando nell'Area2D.
- `upgrades_purchase.gd`: `load_item_file()` legge `Files/item_list.csv` (separatore `;`, colonne id, name, description, bonus, order, category, sub_category, image; le righe senza id vengono saltate), crea un `Item` per riga con immagine da `Assets/Sprites/` e li distribuisce nei tab per categoria (`Player`, `Target`, `Bonus`). Il click su un oggetto emette il segnale della sua categoria con `data` (`order`, `bonus`, `category`, `sub_category`). L'oggetto "damage_item" (Barretta Energetica, categoria Player) è visibile solo ogni 5 ondate.
- Moralità e fedeltà: `boyfriend._apply_bonus` somma `max * bonus` a `shield` o `hp` (sottocategorie `Shield` e `Health`) con tetto al massimo. `set_max_hp` e `set_max_shield` sono ancora stub vuoti. **Non c'è nessuna valuta spesa**: l'acquisto non scala `currency`.

## Input (project.godot)

`ui_left/right/up/down` (frecce e tasti configurati, anche gamepad), `shoot_sand` (tasto destro del mouse), `run` (Spazio), `buy_upgrades` (F), `esc` (Esc: chiude il negozio o alterna la pausa), `pause` (P, azione definita ma senza script che la usi).

## Risorse

- `Assets/Characters/Player/`, `Assets/Characters/Enemy/`, `Assets/Projectiles/SandBall/`: sprite e SpriteFrames (vedi PROJECT_CONTEXT.md per layout e FPS).
- `Assets/Sprites/` (icone oggetti del negozio), `Assets/Icons/` (health.png e shield.png dell'HUD), `Assets/Tiles/` (mappa), `Assets/Music/`, `Assets/Fonts/`, `Assets/ConceptArt/` (concept, ignorata da Godot).
- `Files/item_list.csv`: catalogo degli oggetti, letto con `FileAccess`; il suo `.import` è stato scritto a mano con `importer="keep"` perché il CSV grezzo sia incluso negli export (con `csv_translation` non lo sarebbe). **Non verificato**: la cache dell'editor riporta ancora il tipo `Translation`; se alla prossima apertura il `.import` torna a `csv_translation`, rifare dal dock Import: Import As -> Keep File -> Reimport. `Tools/` e `Docs/`: sorgenti grafici e documentazione, ignorati da Godot.
- `.gitignore` esclude `*.tmp` (file temporanei dell'editor).
- Possibile riordino futuro (non fatto, da eseguire dal dock FileSystem di Godot e correggendo le stringhe `res://` nei `.gd`, compresa `"res://Assets/Sprites/"+file` in `upgrades_purchase.gd`): scene e script vicini sotto `Scenes/{Characters,Objects,Levels,UI,UI/Shop}`, `Files/` -> `Data/`, `Assets/Sprites/` -> `Assets/Items/`.

## Punti fragili e cose da sapere

- Gli acquisti per Giocatore e Bonus non hanno listener; la valuta non viene spesa.
- `enemy.gd` assume che il ragazzo sia il nodo `../Boyfriend` e che `Formulas` e `SignalManager` esistano come autoload.
- Ogni `attack_target(damage)` porta il danno della nemica che attacca (scalato con l'ondata) e colpisce il ragazzo una volta per ciclo di cooldown.
- TileSet e tilemap hanno errori noti di import (`create_tile`), il fix è rimandato su indicazione dell'utente.
- Durante il game over l'albero è in pausa: i test in gioco con eval devono tenerne conto.
