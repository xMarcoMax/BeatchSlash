# Piano di lavoro: sequenza di game over (fuga del ragazzo)

File di lavoro per Claude Code e Codex. **Lo elimina solo l'utente**, quando lo dice lui. Non è un file di contesto: può contenere stato e storico del lavoro. Il funzionamento approvato va poi riscritto in `PROJECT_CONTEXT.md` e `CODE_MAP.md` secondo le regole di `AGENTS.md`.

Prima di lavorare leggi: `AGENTS.md`, `Docs/CODE_MAP.md`, `Docs/PROJECT_CONTEXT.md` (sezioni 2, 3, 6, 8 e 10.3), la skill `game-tools` e, per gli sprite, `Docs/BLENDER.md`, `Docs/PIXELORAMA.md` e la skill `blender-skills` (sequenza obbligatoria: brief prima di modellare). Le funzioni di `projectiles.gd`, `game_over.gd`, `pause_menu.gd` e `upgrades.gd` (`_input`) vanno lette per intero prima di toccarle.

## Indice

1. [Obiettivo](#1-obiettivo)
2. [Decisioni dell'utente](#2-decisioni-dellutente)
3. [Stato del codice di partenza](#3-stato-del-codice-di-partenza)
4. [Scelte dell'agente da far confermare](#4-scelte-dellagente-da-far-confermare)
5. [Fase A: logica e coreografia](#5-fase-a-logica-e-coreografia)
6. [Fase B: sprite ed elementi di gioco](#6-fase-b-sprite-ed-elementi-di-gioco)
7. [Fase C: integrazione e verifica](#7-fase-c-integrazione-e-verifica)
8. [Fase D: documenti e guide](#8-fase-d-documenti-e-guide)
9. [Stato di avanzamento](#9-stato-di-avanzamento)

## 1. Obiettivo

Quando la fedeltà del ragazzo arriva a zero non compare subito il pannello di game over: parte una scenetta in cui il ragazzo cede e se ne va con l'ultima nemica che lo ha attaccato; la protagonista piange e le altre nemiche restano deluse. Dopo la scenetta compare il pannello (Ricomincia, Torna al Menù, Esci).

## 2. Decisioni dell'utente

Sequenza, nell'ordine:

1. Fedeltà a zero: tutto si ferma. Le nemiche in animazione di morte e le palle in volo finiscono; le palle che toccano qualcuno a sequenza iniziata non fanno alcun danno. Tutti guardano il ragazzo.
2. Il ragazzo si volta verso l'ultima nemica che lo ha attaccato. Ragazzo e nemica camminano verso il basso; **nello stesso momento** la protagonista, da dove si trova, cammina (non si teletrasporta) verso il suo ombrellone (telo rosso accanto all'ombrellone rosso di sinistra, posizione di partenza del Player in (108, −211)).
3. Il ragazzo e la nemica si voltano e si mettono uno di fronte all'altra: **ragazzo a sinistra, nemica a destra**.
4. **La scenetta vera e propria non parte finché protagonista, ragazzo e nemica non sono tutti nelle loro posizioni.**
5. Il ragazzo manda un bacio (bacia la mano e soffia verso di lei). Dalla mano parte un cuoricino che colpisce la nemica. Lei lo accoglie: reazione di imbarazzo (arrossisce, mani sulle guance) e due cuoricini piccoli compaiono sopra di lei partendo dal centro e muovendosi in diagonale in dissolvenza, come i numeri dei danni. Bacio e ricezione durano circa **2 secondi**.
6. Il ragazzo si avvicina a lei; poi escono insieme dall'inquadratura **verso destra**, con il ragazzo che segue la nemica (è lei che lo ha sedotto).
7. **Appena si allontanano** la protagonista, che fino a quel momento guarda il ragazzo, si volta verso il basso e piange con le mani in faccia. **Unica direzione del pianto: verso il basso.** Nessuna altra direzione.
8. Nello stesso momento le altre nemiche assumono una posa triste, curva in avanti a gobba, con espressione delusa.
9. Quando il ragazzo e la nemica sono usciti, attesa di circa **1 secondo**, poi compare il pannello di game over.

Altre decisioni:

- Percorsi: liberi per evitare il Player e, dove serve, un percorso prestabilito per evitare le props.
- Salto della scenetta: per ora no; si valuta dopo averla provata (va tenuta come possibilità nel contesto).
- Gli **sprite e gli elementi di gioco vanno realizzati davvero** (non segnaposto). Musiche, suoni e grafiche non di gioco (menu e simili) vengono dopo.
- Il punto di partenza del Player (ombrellone di sinistra) è già stato spostato in `level.tscn` e verificato.

## 3. Stato del codice di partenza

- `boyfriend.gd`: `_on_enemy_attack(damage)` toglie moralità e poi fedeltà; a `hp <= 0` emette `SignalManager.game_over` **a ogni colpo successivo** (nessuna guardia). Non ricorda chi ha attaccato per ultimo. `attack_target` porta solo il danno e lo emette `enemy.gd.attack()`; non ci sono altri ascoltatori.
- `level.gd._on_game_over`: mostra `UI/GameOver` e mette in pausa l'albero. `_process` continua a generare nemiche e a controllare la fine dell'ondata; `NextWaveTimer` può scadere.
- `player.gd`: input e movimento fermi solo con `Global.is_in_purchase`; lancio con `ball`; si muove con `move_and_slide` e `Input.get_vector`, limitato a `play_area`.
- `enemy.gd`: cammina verso il proprio posto con `Pathfinder`, flirta e attacca con `AttackCooldown` (1,4 s); animazioni 8 direzioni `idle_`, `walk_`, `flirt_`, `dead_`.
- Boyfriend ha solo `idle`, `glance`, `admire`, `flex` (8 direzioni ciascuna) e **nessuna camminata**. Player: `idle`, `walk`, `dash`, `throw`. Nemica: `idle`, `walk`, `flirt`, `dead`.
- `projectiles.gd`: contatto con `enemy` fa danno; palle in volo.
- Il negozio (F) e la pausa (Esc) sono ascoltati da `upgrades.gd` e `pause_menu.gd` con `_input`.

## 4. Scelte dell'agente da far confermare

Decise dall'agente dove l'utente non ha specificato; da riportare all'utente a lavoro fatto:

- Posa triste delle altre nemiche: **una sola**, frontale (verso il basso), per tutte, in analogia al pianto. Prima del cambio posa guardano il ragazzo con `idle_<dir>`.
- Camminata del ragazzo: solo giù e destra (le due direzioni della scena). Bacio: solo verso destra.
- Nemica che riceve il bacio: solo rivolta verso sinistra (verso il ragazzo).
- Cuoricino del bacio: sprite nuovo, in volo dal ragazzo alla nemica, con piccolo scoppio all'arrivo.
- Due cuoricini piccoli sopra la nemica: elemento nuovo, comportamento come `FloatingText` (sale in diagonale e sfuma).
- Posizioni di sosta e durate (provvisorie, da tarare provandole): sosta a una distanza fissa sotto il ragazzo, circa 2 secondi di bacio, 1 secondo di attesa finale.

## 5. Fase A: logica e coreografia

A1. **Ultima attaccante e guardia del game over** (`boyfriend.gd`, `enemy.gd`, `SignalManager`): `attack_target` porta anche la nemica; il ragazzo la memorizza in `last_attacker`; `game_over` viene emesso una sola volta, con la nemica.

A2. **Stato "sequenza di game over"**: un flag in `Global` (si azzera al ricaricamento del livello) che ferma tutto il resto. Una nuova scena/script `game_over_sequence` figlia del livello coordina la coreografia.

A3. **Congelamento del gioco**:
- `level.gd`: niente più spawn, `check_all_eliminated` e `NextWaveTimer` fermi; game over che vince sul bonus di fine ondata; niente pausa dell'albero finché non finisce la sequenza.
- Nemiche: ferme (niente passi, flirt, attacchi, `AttackCooldown`), tranne quelle già in animazione di morte che finiscono; tutte rivolte al ragazzo con `idle_<dir>`.
- Player: input e lancio disattivati (come `is_in_purchase`), ma muove da solo verso l'ombrellone.
- Proiettili: i colpi a sequenza iniziata non fanno danno.
- Negozio (F), pausa (Esc) e bonus popup: non interferiscono.

A4. **Coreografia**: macchina a stati con attese su segnali/animazioni; spostamenti con `Pathfinder` e, dove serve, tappe prestabilite; arrivo di tutti e tre alle loro posizioni prima di iniziare; bacio, cuoricino, reazione, avvicinamento, uscita a destra fuori dall'inquadratura; pianto e pose tristi; attesa di 1 secondo; pausa e pannello.

A5. **Reset**: Ricomincia e Torna al Menù non devono portarsi dietro il flag, le collisioni disattivate o lo stato di pausa.

## 6. Fase B: sprite ed elementi di gioco

Per ogni elemento: brief e riferimenti, posa in Blender (pipeline in `Tools/blender/`, stile del Player), render, ritocchi in Pixelorama se servono, import nell'atlante e nel `SpriteFrames`, aggiornamento dei test (`tests/test_enemy_frames.gd` e simili) e di `Docs/CODE_MAP.md`.

B1. Ragazzo: `walk_down`, `walk_right`, bacio verso destra (`blow_kiss_right`).
B2. Nemica: `blush_left` (arrossire con le mani sulle guance, rivolta a sinistra) e posa triste frontale (`sad_down`).
B3. Player: pianto frontale con le mani in faccia (`cry_down`, in loop).
B4. Cuoricino del bacio (volo e scoppio) e due cuoricini piccoli sopra la nemica.

### Brief di produzione (pose sul rig comune a 17 ossa, nessuna modifica a modelli o materiali)

- **Tipo:** animazioni di personaggi esistenti; render con la pipeline del progetto (toon 4 toni, contorno #3a1418, ombra alpha 97/255, viso timbrato), celle 64×64 per ragazzo e nemica, 48×48 per il Player.
- **Ragazzo** (`ragazzo_pipeline.py`, gruppi nuovi in `ANIMS`, rese nelle 8 direzioni come gli altri gruppi, solo i gruppi nuovi vengono resi e aggiunti all'atlante esistente):
  - `walk`: passo del Player (`walk(t)`), 8 frame, 12,8 FPS (passo della coppia: 1,6 × la camminata della nemica), loop; occhi aperti.
  - `kiss` (bacio mandato): 10 frame a 8 FPS, non in loop. 0 riposo; 1–3 la mano destra sale alle labbra (avambraccio piegato come la mano al mento di `admire`); 4 bacio sulla mano, occhi chiusi; 5–7 il braccio si distende in avanti verso di lei, busto appena sporto (il soffio); 8–9 tiene la posa. Il cuoricino parte al frame 6. Mano sinistra sul fianco.
- **Nemica** (`nemica_pipeline.py`, gruppi nuovi nell'atlante, 8 direzioni):
  - `blush`: mani sulle guance, spalle alzate, testa che dondola, ginocchio piegato; guance rosa timbrate sotto gli occhi; 8 frame a 8 FPS, loop.
  - `sad`: delusa e curva in avanti a gobba (busto e testa giù, spalle cadenti, braccia penzoloni in avanti), sospiro lento; 6 frame a 4 FPS, loop.
- **Player** (`blender_pipeline.py`, atlante a parte `player_cry.png`, sola direzione verso il basso, animazione `cry_down` aggiunta a `player_frames.tres`): mani sul viso, testa china, spalle scosse dai singhiozzi; niente viso timbrato (lo coprono le mani); 6 frame a 8 FPS, loop.
- **Verifica:** anteprime ingrandite del modello in posa e degli sprite prima di esportare, controllo che le celle esistenti degli atlanti restino identiche al pixel, alpha solo 0/97/255, test `enemy_frames` e self-check della nemica aggiornati ai nuovi gruppi.

L'MCP di Blender, Pixelorama e GIMP vanno verificati all'inizio; se manca uno strumento, ci si ferma e si avvisa l'utente.

## 7. Fase C: integrazione e verifica

- Cablare le animazioni nuove nella coreografia.
- Verificare in gioco con una scena di debug temporanea (cartella `DebugTmp/`), aprendo e avviando direttamente la scena del livello: forzare la fedeltà a zero con la Player in vari punti, con molte nemiche, con palle in volo, con la nemica in animazione di morte, con il negozio aperto; screenshot a ogni fase; log; poi cancellare la cartella e controllare `git status`.
- Verificare i casi limite: più colpi nello stesso istante, ultima nemica sconfitta insieme al game over, Ricomincia e Torna al Menù dopo la sequenza.

## 8. Fase D: documenti e guide

- `Docs/PROJECT_CONTEXT.md`: il punto passa da Aperti a In lavorazione (e ad Approvati solo quando l'utente lo approva); sezioni 3 (game over), 6 (personaggi) e concept aggiornati ("scappa con una ragazza").
- `Docs/CODE_MAP.md`: nuovi script, flag, segnali, costanti, animazioni e atlanti, test.
- Guide: `Docs/BLENDER.md`, `Docs/PIXELORAMA.md` e i riferimenti generici della skill `game-tools` con le lezioni verificate.

## 9. Stato di avanzamento

- [x] Punto di partenza del Player spostato all'ombrellone di sinistra e verificato.
- [x] A1 Ultima attaccante e guardia del game over (`attack_target(damage, attacker)`, `game_over(last_attacker)`, flag impostato nel ragazzo al colpo fatale).
- [x] A2 Stato della sequenza (`Global.game_over_sequence`, `Scripts/game_over_sequence.gd`).
- [x] A3 Congelamento del gioco (livello, nemiche, Player, proiettili, pausa).
- [x] A4 Coreografia, con animazioni di ripiego finché mancano gli sprite nuovi (`_play` prende la prima animazione esistente). Verificata in gioco fino al pannello.
- [x] A5 Reset (Ricomincia verificato: albero non in pausa, flag a falso).
- [x] B1 Sprite del ragazzo (`walk`, `kiss` in 8 direzioni).
- [x] B2 Sprite della nemica (`blush`, `sad` in 8 direzioni; `check_enemy()` superato).
- [x] B3 Sprite del Player (`cry_down`, con lacrime).
- [x] B4 Cuoricini (`kiss_heart.png`, `small_heart.png`).
- [x] C Integrazione e verifica in gioco (sequenza completa, casi limite, Esc bloccato).
- [x] D Documenti e guide.
- [x] Richieste dopo la prima prova: uscita più svelta (`EXIT_PACE` 1,4), partenza immediata, nemiche deluse che seguono la coppia con lo sguardo (`sad` nelle 8 direzioni), Player spostato accanto al telo (378, −235), ombrellone chiuso rimosso (scena e `Tools/level/props_gen.py`).
- [x] Approvazione finale dell'utente (punto spostato tra gli approvati del contesto).
