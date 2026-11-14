# Beatch Slash! — mappa del codice

Da leggere **per prima** per capire come è fatto il progetto; poi `Docs/PROJECT_CONTEXT.md` (visione, stile grafico, stato). Ultimo aggiornamento: 14 novembre 2026. Descrive la struttura, non il diario: se cambi segnali, scene, autoload o flussi, aggiorna questa mappa nello stesso intervento. Verificare sempre contro i file reali.

GDScript, Godot 4.7, renderer Mobile. Scena principale: Scenes/main_menu.tscn. Tutto il testo in gioco è in italiano.

## Flusso di gioco

1. **Menu** (`main_menu.gd`): Nuova partita emette `SignalManager.game_started`, ferma la musica e carica `Scenes/level.tscn`. Opzioni (`options.gd`: volume e mute sul bus 0) e Tutorial portano a scene dedicate e tornano al menu.
2. **Livello** (`Scenes/level.tscn`, `level.gd`): all'avvio `set_variables()` fissa 5 nemiche e moltiplicatori 1. `_process` chiama `spawn_enemy()` (una nemica per frame finché `spawn_number > 0`, in un punto casuale di `World/EnemySpawn`) e `check_all_eliminated()`.
3. **Fine ondata:** quando `defeated_level == total_enemies` parte `NextWaveTimer` (circa 20 s), emette `wave_purchase_item(wave)` e il negozio diventa accessibile. Alla scadenza `set_next_wave()` incrementa l'ondata e ricalcola il numero di nemiche con `Formulas.calculate("enemies", ...)`.
4. **Nemica** (`enemy.gd`): segue un percorso A* verso il ragazzo aggirando ostacoli statici e altre nemiche (vedi sezione Nemica). Il `HitZone` (Area2D) del ragazzo la vede entrare e emette `enemy_attacking(enemy)`: la nemica passa a `is_attacking` e ogni 2 s (`AttackCooldown`) emette `attack_target(damage)`.
5. **Ragazzo** (`boyfriend.gd`): `_on_enemy_attack` toglie prima alla moralità (`shield`), poi alla fedeltà (`hp`), emette `update_health_shield`; a `hp <= 0` emette `game_over`. Tiene in `attackers` le nemiche dentro l'`HitZone` (aggiunte in `body_entered`, tolte in `body_exited`, filtrate se morte o liberate) e `update_animation` sceglie l'animazione: nessuna attaccante -> `idle_down` (al sole, mani sui fianchi, occhi chiusi); `shield > 0` (qualunque `hp`) -> `idle_down` con ogni `GLANCE_PAUSE` (2,5-5 s casuali) una `glance_<dir>` verso un'attaccante a caso, una volta sola; `shield <= 0` e `hp > max_hp * FLEX_HP_RATIO` (0,5) -> `admire_<dir>` verso l'attaccante più vicina; altrimenti `flex_<dir>`.
6. **Game over:** `level.gd._on_game_over` mostra `UI/GameOver` e mette `get_tree().paused = true`. Riavvio, menu o uscita in `game_over.gd`.
7. **Colpo:** il Player lancia la palla (`player.gd` -> `projectiles.gd`); al contatto con una nemica viva chiama `enemy.take_damage(damage, transform.x)`: lampo bianco, piccolo rinculo e stordimento; a `hp <= 0` parte `dead()`, che emette `defeated`, gioca `dead_<dir>` e dopo `DeadTimer` (1,7 s) spawna il puff e fa `queue_free()`. `level.gd._on_defeated` aggiorna punti, valuta e HUD.

## Autoload (project.godot)

| Nome | File | Ruolo |
| --- | --- | --- |
| `Formulas` | Scripts/Autoload/Formulas.gd | `calculate(type, wave, base)` scala nemiche/salute/danno con le ondate (fattori 1.6 / 1.25 / 1.05, cap 12); `direction_name(Vector2)` sceglie una delle 8 direzioni degli sprite (`up`, `down`, `left`, `right`, `up_right`, `up_left`, `down_right`, `down_left`), usata da Player e nemiche |
| `SignalManager` | Scripts/Autoload/SignalManager.gd | bus di segnali globali (tabella sotto) |
| `MusicManager` | Scripts/Autoload/MusicManager.gd | un AudioStreamPlayer; carica `Assets/Music/Menu/summer-funky-dance-314907.mp3` (unica musica del progetto, loop); `game_started` la ferma e in partita non c'è musica |
| `Global` | Scripts/Autoload/Global.gd | `is_mobile`, `is_in_purchase` (blocca movimento e lanci durante gli acquisti), `purchase_just_closed` (evita che Esc chiuda anche la pausa) |
| `_mcp_game_helper` | addons/godot_ai/... | solo strumenti di sviluppo, non fa parte del gioco |

## Segnali (SignalManager)

| Segnale | Chi emette | Chi ascolta |
| --- | --- | --- |
| `game_started` | main_menu | MusicManager |
| `enemy_attacking(enemy)` | boyfriend (HitZone) | enemy (ogni istanza controlla `attacker == self`) |
| `enemy_left_target(enemy)` | boyfriend (`body_exited` dell'HitZone) | enemy (ogni istanza controlla `enemy == self`): `is_attacking = false`, smette il flirt e le sue `attack_target`, e riprende a camminare verso il ragazzo; rientrando riparte `enemy_attacking` |
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
| Scenes/level.tscn | level.gd | radice `Level`: `UI` (HUD, GameOver, UpgradesPurchase, PauseMenu), `World` (EnemySpawn con 3 CollisionShape2D, TileMapLayer `Beach` e `BeachEnvironment`), `Player` (con Camera2D), `Boyfriend`, `Upgrades`, `NextWaveTimer`; a runtime `level.gd` aggiunge come figlio il nodo `Pathfinder` (non è nella scena) |
| Characters/player.tscn | player.gd | CharacterBody2D, gruppo `player`; AnimatedSprite2D + MovingThrow (Sprite2D) + RayCast2D + collider 72x120 |
| Characters/enemy.tscn | enemy.gd | CharacterBody2D, gruppo `enemy`; AnimatedSprite2D, collider 72x120, ProgressBar salute, Timer `DeadTimer` e `AttackCooldown` (2 s); lo sprite usa lo shader `hit_flash.gdshader` (ShaderMaterial creato in `_ready`, uno per nemica) |
| Objects/puff.tscn | nessuno | AnimatedSprite2D `Puff` (scala 4, z_index 1) con 6 frame 32x32 da `Assets/Effects/Puff/puff.png`, `autoplay`, 12 FPS; il segnale `animation_finished` è collegato al proprio `queue_free`, quindi si elimina da solo. Lo istanzia `enemy.gd._on_dead_timer_timeout` come figlio del livello |
| Characters/boyfriend.tscn | boyfriend.gd (agganciato alla scena base) | CharacterBody2D, gruppo `target`; figlio `HitZone` (Area2D, raggio 185); `AnimatedSprite2D` scala 4, filtro nearest, offset (0, -5), `Assets/Characters/Boyfriend/boyfriend_frames.tres` (celle 64x64: idle, glance, admire, flex in 8 direzioni); collider 130x129 |
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
- `_physics_process`: se è morta o sta attaccando la velocità è 0, altrimenti `_steer()`; poi `move_and_slide()` e `update_animation()`. Non c'è più il RayCast2D che la fermava davanti a qualsiasi ostacolo.
- Pathfinding: `level.gd` crea un `Pathfinder` (`Scripts/pathfinder.gd`, `class_name Pathfinder`) e lo passa a ogni nemica (`spawn.pathfinder`). `Pathfinder.build(bounds)` aspetta 2 frame fisici, poi costruisce un `AStarGrid2D` (celle 40 px, area = TileMapLayer `Beach`/`BeachEnvironment` + zone di spawn + ragazzo + margine 400) e blocca le celle dove un rettangolo 72x120 (collider della nemica) tocca un corpo che non sia `CharacterBody2D` (TileMap con fisica, negozio). Costruzione circa 40 ms. `find_path(from, to, blockers)` restituisce i waypoint con percorso parziale ammesso; `blockers` sono posizioni di corpi fermi che bloccano per quella ricerca le celle entro 80 px (poi sbloccate: la semplificazione avviene prima), celle di partenza/arrivo spostate sulla cella libera più vicina (raggio 8) e percorso semplificato in linea retta dove libero. Prima che la griglia sia pronta restituisce un percorso vuoto e la nemica va diritta al ragazzo.
- Posti attorno al ragazzo: ogni nemica ha uno `slot_angle` e punta a `_slot_point(angle)`, un punto a 185 px dal centro del ragazzo (il raggio dell'HitZone), non al suo centro. `_pick_slot()` parte dall'angolo da cui arriva e prova a turno ±30° (`SLOT_STEP`) fino a 360°, saltando i posti `_slot_taken()`: occupato dal Player, da una nemica che attacca o da una viva più vicina al ragazzo, se sta entro 320 px dal ragazzo e a meno di 24° (`SLOT_ARC`). Le attaccanti si fermano a circa 230 px, per questo il controllo è per angolo e non per distanza dal punto.
- `_steer(delta)`: sceglie il posto, ricalcola il percorso verso di esso ogni 0,5 s (+ fino a 0,2 s casuali per sfalsarle; blocchi = nemiche che attaccano e Player, `_blockers()`), avanza al waypoint successivo a meno di 30 px, e somma `_separation()` (peso 1,5, direzione limitata a lunghezza 1, non normalizzata, così non vibra a piena velocità): spinta dalle altre nemiche vive e dal Player (gruppo `player`) entro 110 px con una componente laterale, così due corpi faccia a faccia si superano. Blocco: ogni 0,6 s (`STUCK_TIME`) confronta il percorso rimasto (`_path_remaining()`) con quello all'inizio dell'intervallo; se è calato meno del 30% di quanto dovrebbe (`STUCK_PROGRESS_RATIO`) sceglie un altro posto escludendo quello che non ha funzionato. Se nel frame precedente `move_and_slide()` ha urtato qualcosa (`blocked_normal`) e la direzione spinge contro la superficie, la direzione viene proiettata lungo la superficie a velocità piena (se resta quasi nulla, si gira di lato con `slide_side`, casuale ma fisso per ogni nemica): evita lo scivolamento lento contro il Player.
- Collisioni: le nemiche stanno sul layer 2 e collidono solo con il layer 1 (Player, ragazzo, negozio, TileMap), quindi non si urtano tra loro; restano distanziate dalla separazione. Per questo `Player` ha `collision_mask = 3` (è fermato dalle nemiche) e le Area2D che devono vederle (`HitZone` del ragazzo, `SandBall`) hanno `collision_mask = 3`. Una nuova Area2D che deve rilevare le nemiche deve includere il layer 2.
- Animazione fluida: `update_animation(delta)` smorza velocità (`move_speed`) e direzione (`facing`) con `MOTION_SMOOTHING` per non far scattare walk/idle e direzione ad ogni frame di scivolamento.
- Ordine di disegno: `Level` ha `y_sort_enabled` e `World` (mappa) ha `z_index` -1, così Player, ragazzo, negozio e nemiche si coprono in base alla y del nodo (chi sta sotto copre chi sta sopra). L'origine dei nodi non è ai piedi: il confronto è tra origini, quindi sprite di altezze diverse (ragazzo 128 px) possono avere ordine imperfetto.
- Animazioni (`Assets/Characters/Enemy/enemy_frames.tres`): `flirt_<dir>` se `is_attacking`; `idle_<dir>` (rivolta al ragazzo) se la velocità reale è sotto il 10% di `speed` (arrivata o bloccata da un'altra nemica); altrimenti `walk_<dir>` secondo il movimento reale. Da morta l'animazione si ferma. Da morta (`hp <= 0`) `update_animation()` non fa nulla: lascia correre `dead_<dir>`.
- Colpita: `take_damage(amount, from_direction)` (la chiama la palla) toglie salute, avvia il lampo bianco (`flash_left`, 0,1 s, aggiornato in `_process` sul parametro `flash` dello shader, che schiarisce solo i pixel opachi e lascia l'ombra), un rinculo di 220 px/s che decade (`knockback`) e, se non sta attaccando, 0,15 s di stordimento (`stun_left`); durante il flirt il colpo non interrompe l'attacco. L'animazione usa `get_real_velocity() - knockback` così il rinculo non fa girare lo sprite.
- Morte: `dead()` sceglie la direzione guardata (verso il ragazzo se attacca o non si è mai mossa, altrimenti `facing`), disattiva il collider, nasconde la barra salute, gioca `dead_<dir>` (8 frame, 12 FPS, non in loop: resta sull'ultimo frame a terra), emette `defeated` e avvia `DeadTimer` per `DEAD_LINGER_TIME` (1,7 s). Allo scadere `_on_dead_timer_timeout` istanzia `Objects/puff.tscn` a `position + PUFF_OFFSET` come figlio del livello e dopo `PUFF_COVER_TIME` (0,2 s, a metà del frame di picco della nuvola) fa `queue_free()` alla nemica.
- Salute: `ProgressBar` con colore verde/arancio/rosso a soglie 50% e 25%.

## Palla di sabbia (projectiles.gd)

Area2D che avanza lungo `transform.x` a `speed` 400 (la scala 2 ereditata dal RayCast2D raddoppia lo spostamento). `body_entered`: se il corpo è nel gruppo `enemy` e ha `hp > 0`, blocca il proiettile (una sola volta), gioca `impact`, chiama `body.take_damage(damage, transform.x)` (prima sottraeva `hp` e chiamava `dead()` da sé); se la salute arriva a 0 chiama `body.dead()`. `_face_upright` imposta `flip_v` quando va a sinistra. Si elimina a fine impatto. A fine volo (timer `Used`, 3 s) `_on_used_timeout` avvia `land`: la palla smette di colpire (monitoring e collider spenti), rallenta di `LAND_DECEL` (1500/s) mentre cade, e `_on_animation_finished` la elimina a fine animazione.

## Negozio e oggetti

- `upgrades.gd`: tasto `buy_upgrades` (F) apre `UpgradesPurchase` solo se `NextWaveTimer` è attivo e imposta `Global.is_in_purchase`; Esc lo chiude. Il testo di invito appare entrando nell'Area2D.
- `upgrades_purchase.gd`: `load_item_file()` legge `Files/item_list.csv` (separatore `;`, colonne id, name, description, bonus, order, category, sub_category, image; le righe senza id vengono saltate), crea un `Item` per riga con immagine da `Assets/Sprites/` e li distribuisce nei tab per categoria (`Player`, `Target`, `Bonus`). Il click su un oggetto emette il segnale della sua categoria con `data` (`order`, `bonus`, `category`, `sub_category`). L'oggetto "damage_item" (Barretta Energetica, categoria Player) è visibile solo ogni 5 ondate.
- Moralità e fedeltà: `boyfriend._apply_bonus` somma `max * bonus` a `shield` o `hp` (sottocategorie `Shield` e `Health`) con tetto al massimo. `set_max_hp` e `set_max_shield` sono ancora stub vuoti. **Non c'è nessuna valuta spesa**: l'acquisto non scala `currency`.

## Input (project.godot)

`ui_left/right/up/down` (frecce e tasti configurati, anche gamepad), `shoot_sand` (tasto destro del mouse), `run` (Spazio), `buy_upgrades` (F), `esc` (Esc: chiude il negozio o alterna la pausa), `pause` (P, azione definita ma senza script che la usi).

## Risorse

- `Assets/Characters/Player/`, `Assets/Characters/Enemy/`, `Assets/Projectiles/SandBall/`: sprite e SpriteFrames (vedi PROJECT_CONTEXT.md per layout e FPS).
- Player: `Tools/blender/personaggio_modello.py` ricostruisce `personaggio.blend` dal turnaround principale `Assets/ConceptArt/Player/player_turnaround.png`, usando `concept_model.py`; costume continuo sul corpo a riposo, chioma `Hair` e ciocche frontali/riga centrale `FrontHair` legate alla testa. `blender_pipeline.py` genera i quattro atlanti del Player: `build_all()` e `build_diagonals()` mantengono l'interfaccia, `build_steps()` espone la stessa costruzione una posa alla volta per lotti MCP. Aspetto approvato; passo più raccolto in `walk`/`run`, quattro atlanti rigenerati e verificati in Godot. Layout, frame, tempi e rilascio al frame 3 restano quelli letti da `player.gd` e `player_frames.tres`; `pose_combo` riusa le nuove pose nei lanci in movimento. `nemica_pipeline.py:walk_e` conserva esplicitamente la divaricazione originale della nemica. Procedure in `Docs/BLENDER.md` §5/8; nessun cambiamento a scene, segnali o flusso runtime.
- `Assets/ConceptArt/Enemies/enemy_turnaround.png`: concept della nemica (capelli viola lisci e lunghi sul dorso, senza ciocche laterali davanti alle braccia nella vista posteriore, bikini smeraldo con lacci, fisico atletico con seno e glutei leggermente più pieni), con prompt in `Tools/concept/prompts.json`, voce `enemy_base`; look approvato, ultimi ritocchi da valutare, non usato dal runtime. `Tools/blender/nemica.blend` e gli sprite in `Assets/Characters/Enemy/` non recepiscono ancora questa revisione; scene, segnali e flussi restano quelli descritti sopra.
- `Assets/Sprites/` (icone oggetti del negozio), `Assets/Icons/` (health.png e shield.png dell'HUD), `Assets/Tiles/` (mappa), `Assets/Music/`, `Assets/Fonts/`, `Assets/ConceptArt/` (concept, ignorata da Godot).
- `Assets/ConceptArt/Boyfriend/boyfriend_turnaround.png`: riferimento grafico del ragazzo, con prompt in `Tools/concept/prompts.json` (voce `boyfriend`); non è una texture di gioco. Sprite del ragazzo: `Assets/Characters/Boyfriend/boyfriend_spritesheet.png` (512x2048, celle 64x64, righe = animazione*8 + direzione, ordine direzioni come le nemiche) e `boyfriend_frames.tres`, entrambi generati da `build_boyfriend()` in `Tools/blender/ragazzo_pipeline.py` (modello `Tools/blender/ragazzo.blend` ricostruito dal concept partendo da `base_personaggio.blend`, codice comune in `concept_model.py`, riferimenti in `Tools/blender/ref/`); se si rigenera, il .tres viene riscritto per intero. `Tools/pixelorama/boyfriend.pxo` è un vecchio ritocco superato.
- `Files/item_list.csv`: catalogo degli oggetti, letto con `FileAccess`; il suo `.import` è stato scritto a mano con `importer="keep"` perché il CSV grezzo sia incluso negli export (con `csv_translation` non lo sarebbe). **Non verificato**: la cache dell'editor riporta ancora il tipo `Translation`; se alla prossima apertura il `.import` torna a `csv_translation`, rifare dal dock Import: Import As -> Keep File -> Reimport. `Tools/` e `Docs/`: sorgenti grafici e documentazione, ignorati da Godot; in `Docs/` anche le guide degli strumenti `BLENDER.md`, `PIXELORAMA.md`, `GODOT.md`.
- `.gitignore` esclude `*.tmp` (file temporanei dell'editor).
- Possibile riordino futuro (non fatto, da eseguire dal dock FileSystem di Godot e correggendo le stringhe `res://` nei `.gd`, compresa `"res://Assets/Sprites/"+file` in `upgrades_purchase.gd`): scene e script vicini sotto `Scenes/{Characters,Objects,Levels,UI,UI/Shop}`, `Files/` -> `Data/`, `Assets/Sprites/` -> `Assets/Items/`.

## Punti fragili e cose da sapere

- Ripresa del Player: il perimetro delle modifiche Codex rispetto al lavoro precedente di Claude è in `Docs/BLENDER.md` §8, "Ripresa del lavoro condiviso con Claude". Il modello è approvato e i quattro PNG includono il passo corretto; idle e lancio da ferma sono identici al pixel; scene, SpriteFrames e script runtime del Player sono preservati. `make_girl('body')`/`make_girl('all')` richiedono la base originale, mentre la correzione dei capelli può proseguire sul modello corrente a posa azzerata.

- Gli acquisti per Giocatore e Bonus non hanno listener; la valuta non viene spesa.
- `enemy.gd` assume che il ragazzo sia il nodo `../Boyfriend` e che `Formulas` e `SignalManager` esistano come autoload.
- La griglia del `Pathfinder` si costruisce una sola volta all'avvio del livello: ostacoli statici aggiunti o spostati dopo non vengono visti. Se cambi il collider della nemica (72x120, offset y 17) aggiorna `PROBE_SIZE` e `PROBE_OFFSET` in `pathfinder.gd`. Il ragazzo è fermo: il percorso lo cerca nella sua posizione attuale ma la griglia non lo considera ostacolo.
- Layer di collisione: le nemiche sono sul layer 2 con maschera 1; Player, `HitZone` del ragazzo e `SandBall` hanno maschera 3. Una nuova Area2D o un nuovo corpo che deve interagire con le nemiche deve includere il layer 2, altrimenti non le vede. Le nemiche non si urtano tra loro: se riappaiono ammassi vicino al ragazzo, controllare `_slot_taken()`/`_separation()` in `enemy.gd`, non le collisioni.
- Ogni `attack_target(damage)` porta il danno della nemica che attacca (scalato con l'ondata) e colpisce il ragazzo una volta per ciclo di cooldown.
- TileSet e tilemap hanno errori noti di import (`create_tile`), il fix è rimandato su indicazione dell'utente.
- Durante il game over l'albero è in pausa: i test in gioco con eval devono tenerne conto.
