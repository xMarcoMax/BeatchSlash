# Piano di lavoro: classi di nemiche (Pesante, Veloce, Influencer)

File di lavoro per Claude Code e Codex. **Lo elimina solo l'utente**, quando lo dice lui. Non è un file di contesto: può contenere stato e storico del lavoro. Il funzionamento approvato va poi riscritto in `PROJECT_CONTEXT.md` e `CODE_MAP.md` secondo le regole di `AGENTS.md`.

Prima di lavorare leggi:
- `AGENTS.md`;
- `Docs/CODE_MAP.md`, sezioni 3, 4, 5, 7, 9, 10, 12 e la sezione 7 sulla scenetta di game over;
- `Docs/PROJECT_CONTEXT.md`, sezione 10.3, "Classi di nemiche";
- la skill `game-tools` con `Docs/GODOT.md`.

Leggi per intero, prima di toccarli: `Scripts/enemy.gd`, `Scripts/level.gd` (`spawn_enemy`, `_on_defeated`), `Scripts/game_over_sequence.gd`, `Scripts/boyfriend.gd` (`_on_enemy_attack` e `attackers`) e `Scripts/Autoload/playtest_log.gd`.

## Indice

1. [Obiettivo](#1-obiettivo)
2. [Decisioni dell'utente](#2-decisioni-dellutente)
3. [Scelte dell'agente](#3-scelte-dellagente)
4. [Compiti](#4-compiti)
5. [Fuori da questo piano](#5-fuori-da-questo-piano)
6. [Stato di avanzamento](#6-stato-di-avanzamento)

## 1. Obiettivo

Aggiungere al gioco tre nuove classi di nemiche, Pesante, Veloce e Influencer, accanto alla nemica base. Ogni classe ha i suoi valori. L'Influencer attacca da lontano con i cuoricini. Finché non ci sono gli sprite veri, le nuove classi usano un segnaposto.

## 2. Decisioni dell'utente

- **Valori.** I moltiplicatori di salute e di danno si applicano ai valori della base all'ondata in corso, cioè `Formulas.calculate("health"/"damage", wave, base)`. La crescita per ondata vale quindi per tutte le classi.

| Classe | Velocità | Salute | Danno | Tempo tra attacchi | Monete | Da ondata |
| --- | --- | --- | --- | --- | --- | --- |
| Base | 100 | ×1 | ×1 | 1,4 s | 18 | 1 |
| Pesante | 60 | ×2,5 | ×2,5 | 2,8 s | 36 | 5 |
| Veloce | 165 | ×0,55 | ×0,5 | 0,7 s | 13 | 5 |
| Influencer | 90 | ×0,6 | ×0,8 | 2,0 s | 24 | 7 |

- **Pesante:** subisce il 40% della spinta indietro dei colpi.
- **Influencer:**
  - al massimo 3 vive contemporaneamente;
  - si ferma su un anello più largo di quello delle nemiche che attaccano da vicino, circa una nemica di distanza in più (circa 255 px invece di 185);
  - non occupa i posti delle nemiche che attaccano da vicino;
  - ogni 2 s manda un cuoricino che vola verso il ragazzo in circa 0,8 s e all'arrivo gli toglie moralità o fedeltà come un attacco normale;
  - **i cuoricini non si possono abbattere.**
- **Frequenza:** le classi speciali sono rare all'inizio e più frequenti con le ondate. Dall'ondata 5 la probabilità che una nemica sia speciale è del 20%; sale in modo lineare fino al 40% all'ondata 15 e poi resta lì.
- **Segnaposto:** l'icona di Godot (`res://icon.svg`) al posto dello sprite. Gli sprite veri si faranno dopo.
- **Danno per secondo:** le classi non vanno pareggiate. Restano diverse, entro circa ±30% dalla base; le monete sono proporzionali alla minaccia e l'equilibrio passa dalla composizione delle ondate.

## 3. Scelte dell'agente

Da correggere se non vanno bene.

- **Catalogo in CSV** `Files/enemy_classes.csv`, separato da `;`, come `Files/item_list.csv`. Colonne:
  - `id`, `name`, `min_wave`, `weight`;
  - `speed`, `health_mult`, `damage_mult`, `attack_time`, `coins`;
  - `knockback_mult`, `attack` (`melee` o `kiss`), `ring_radius`, `max_alive` (0 = nessun limite);
  - `placeholder_tint`, `placeholder_scale`.
  - Pesi iniziali tra le speciali: Pesante 1, Veloce 1, Influencer 1.
- **Classe statica `EnemyClasses`** in `Scripts/enemy_classes.gd`:
  - legge e mette in cache il catalogo;
  - `pick(wave, alive_counts, first_of_wave) -> Dictionary` è una funzione pura e testabile;
  - `special_chance(wave)` calcola la probabilità di una classe speciale.
- **Prima nemica di ogni ondata:** sempre Base, quella con `EnemyPalette.original()`.
- **Punti per sconfitta:** restano 10 per tutte le classi.
- **Collisioni e `Hurtbox`:** restano uguali per tutte finché non ci sono gli sprite veri.
- **Il ragazzo:** l'Influencer non entra nella sua lista `attackers`, perché resta fuori dall'`HitZone`. Le animazioni del ragazzo restano invariate.

## 4. Compiti

1. **Catalogo e scelta della classe.**
   - Crea `Files/enemy_classes.csv` e `Scripts/enemy_classes.gd`.
   - Sotto l'ondata 5 viene sempre scelta la Base.
   - Altrimenti, con probabilità `special_chance(wave)`, si sceglie una speciale tra quelle con `min_wave <= wave` e sotto il loro `max_alive`, con estrazione pesata da `weight`.
   - Se nessuna speciale è disponibile viene scelta la Base.

2. **Valori per classe sulla nemica.**
   - In `level.gd.spawn_enemy()`, prima di `add_child`, conta le nemiche vive per classe e chiama `EnemyClasses.pick`. La prima nemica dell'ondata è `first_of_wave`.
   - Poi passa la classe alla nemica: `set_spawn_values` riceve anche la classe.
   - La nemica imposta `speed`, `hp` (salute dell'ondata × `health_mult`), `damage` (danno dell'ondata × `damage_mult`, arrotondato per eccesso), `attack_cooldown.wait_time = attack_time` e `knockback_mult`, e salva `enemy_class`.
   - In `take_damage` la spinta diventa `HIT_KNOCKBACK * knockback_mult`.

3. **Monete per classe.**
   - Il segnale `SignalManager.defeated` passa la nemica sconfitta. Aggiorna la dichiarazione, `enemy.dead()` (`emit(self)`) e i due ascoltatori.
   - In `level.gd._on_defeated(enemy)`: `roundi(currency_multiplier * enemy.enemy_class.coins)`.
   - In `playtest_log.gd._on_defeated(enemy)`: l'evento `KILL` annota anche `class=<id>`.

4. **Segnaposto.**
   - Le classi diverse dalla Base usano un `SpriteFrames` costruito a runtime: copia `enemy_frames.tres` mantenendo tutti i nomi delle animazioni, il numero di fotogrammi, la velocità e il loop, ma con `icon.svg` in ogni fotogramma.
   - Il numero di fotogrammi va mantenuto per forza: `GameOverSequence` aspetta i fotogrammi 4 e 6 di `kiss_right`, quindi con un fotogramma solo la scenetta non finirebbe mai.
   - Costruiscilo una sola volta e mettilo in cache statica.
   - Calibra la scala in modo che l'icona occupi circa l'`Hurtbox` (72×172), moltiplicata per `placeholder_scale`. La Pesante è più grande.
   - Applica `modulate = placeholder_tint` per distinguere le classi.
   - Il materiale dello shader resta, perché serve per il lampo del colpo.

5. **Anello dell'Influencer.**
   - `_slot_point` usa il `ring_radius` della classe invece di `SLOT_RADIUS`.
   - `_slot_taken` e `_near_waiting_group` considerano solo le nemiche con lo stesso `ring_radius`. Senza questo filtro le Influencer a 255 px bloccherebbero i posti di quelle da vicino (`SLOT_RING_MAX` 320), e viceversa.
   - L'Influencer ignora `enemy_attacking` e `enemy_left_target`, che vengono dall'`HitZone` a 185 px: una spinta può portarla dentro, ma non deve partire l'attacco da vicino.
   - Comincia ad attaccare (`is_attacking = true`) quando arriva al suo posto sull'anello, cioè entro `WAYPOINT_RADIUS`. Smette quando se ne allontana di più di 60 px (per esempio se viene spinta) e torna a camminare.
   - Da ferma gioca `flirt_<dir>` rivolta al ragazzo.
   - Mentre attacca conta come ostacolo nei percorsi delle altre (`_blockers`), come le nemiche che attaccano da vicino.

6. **Cuoricini.**
   - Per `attack == "kiss"`, `attack()` crea un cuoricino invece di emettere subito `attack_target`.
   - Nuovo script `Scripts/kiss_projectile.gd`, un `Node2D` con uno `Sprite2D` (`res://Assets/Effects/Hearts/kiss_heart.png`, scala 4, nearest), **senza Area2D né collisioni**, così `SandBall` non lo vede.
   - Figlio del livello. Parte dalla testa della nemica e arriva al ragazzo in `KISS_FLIGHT` 0,8 s, con un tween su un leggero arco.
   - All'arrivo, se `Global.game_over_sequence` è falso, emette `SignalManager.attack_target.emit(damage, attacker)`, poi uno scoppio breve e `queue_free`.
   - Se l'Influencer muore mentre il cuoricino è in volo, il cuoricino arriva lo stesso. `attacker` può non essere più valida: `GameOverSequence` sceglie già la prima nemica viva. Verifica che anche `boyfriend.gd` e `playtest_log.gd` reggano un attaccante liberato (`is_instance_valid`).
   - Se il game over parte mentre il cuoricino è in volo, il cuoricino sparisce senza danno.

7. **Test headless.**
   - Nuovo `tests/test_enemy_classes.gd`, con lo stesso schema di `tests/test_shop_items.gd`. Controlla:
     - il catalogo: colonne e valori della tabella della sezione 2;
     - sotto l'ondata 5 esce sempre la Base;
     - l'Influencer non esce prima dell'ondata 7;
     - con 3 Influencer vive non ne esce un'altra;
     - `first_of_wave` dà sempre la Base;
     - `special_chance`: 0,2 all'ondata 5, 0,4 all'ondata 15 e 0,4 all'ondata 25.
   - Si esegue con `C:\Godot\Godot_v4.7-stable_win64.exe --headless --path . --quit-after 600 -s <runner>`. Il runner estende `SceneTree` e controlla `suite._failed`, che è un bool. Riesegui anche `tests/test_shop_items.gd`.

8. **Prova in gioco con debug temporaneo.**
   - Con riga `TEMP-DEBUG` in `level.gd`, parti dall'ondata 7 con molte nemiche e la probabilità delle speciali alzata. Verifica con Godot AI (`level.tscn` aperto, `project_run(mode="current")`, screenshot, `logs_read`):
     - velocità e cadenze diverse tra le classi;
     - le Influencer sull'anello esterno, mai più di 3;
     - i cuoricini che arrivano e tolgono moralità e fedeltà, e che le palle attraversano;
     - le monete per classe nel registro `KILL`.
   - Provoca anche un game over causato da un cuoricino, per esempio abbassando temporaneamente la fedeltà del ragazzo: la scenetta deve arrivare fino in fondo con la nemica segnaposto.
   - Alla fine rimuovi tutte le righe `TEMP-DEBUG`.

9. **Documentazione.**
   - Aggiorna `PROJECT_CONTEXT.md`: le classi passano da 10.3 a 10.2, "in lavorazione", con il segnaposto; descrivi come funzionano in gioco.
   - Aggiorna `CODE_MAP.md`: catalogo, `EnemyClasses`, segnale `defeated(enemy)`, anello, cuoricini, segnaposto, test. Nessuno storico.
   - Aggiorna `Docs/GODOT.md` e la guida generica `references/godot.md` con le eventuali lezioni verificate.

## 5. Fuori da questo piano

Le loro regole non sono ancora decise:
- **Ladra di monete:** manca il modo in cui ruba.
- **Miss Spiaggia.**
- **Ondata difficile.**
- **Sprite veri delle nuove classi.**

## 6. Stato di avanzamento

Piano approvato dall'utente, esecuzione non ancora avviata.

| Compito | Stato |
| --- | --- |
| 1. Catalogo e scelta della classe | da fare |
| 2. Valori per classe sulla nemica | da fare |
| 3. Monete per classe | da fare |
| 4. Segnaposto | da fare |
| 5. Anello dell'Influencer | da fare |
| 6. Cuoricini | da fare |
| 7. Test headless | da fare |
| 8. Prova in gioco con debug temporaneo | da fare |
| 9. Documentazione | da fare |
