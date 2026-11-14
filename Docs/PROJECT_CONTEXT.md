# Beatch Slash! — contesto condiviso per Codex e Claude

## Regole di questo file (indicazione dell'utente)

Serve a Codex e Claude per capire la situazione attuale e come procedere. Contiene solo:

- situazione attuale e breve descrizione di cosa è stato fatto di recente (non la storia del progetto);
- specifiche tecniche di ogni elemento, vecchie e nuove (parametri, layout dei file, valori, regole): servono a capire cosa toccare e analizzare;
- vincoli e regole dell'utente (restano, scritti in modo conciso e non ambiguo);
- "Prossimi passi": i punti aperti indicati dall'utente. Si aggiungono quando l'utente li dice; quelli completati o superati si **rimuovono** (nessuna voce barrata né storico).

Non scrivere: cronologia, correzioni fatte, processo di realizzazione, come le cose sono state integrate, resoconti di verifica. Il comportamento del codice sta in Docs/CODE_MAP.md.

A fine intervento riscrivi le voci toccate, senza note datate. Confronta sempre con i file correnti, git status e le ultime istruzioni dell'utente.

Ultimo aggiornamento: 14 novembre 2026.

**Per capire il codice leggi prima Docs/CODE_MAP.md** (mappa di flussi, autoload, segnali, scene e script). Questo file descrive visione, specifiche, stile grafico e stato.

Nel progetto esistono solo le risorse in uso, senza suffissi di versione: non ricreare né citare versioni precedenti di sprite e strumenti.

## Concept del gioco (visione dell'utente, da rispettare)

Tono ironico e leggero. Tower defense a ondate, 2D top-down, ambientato per ora in un solo livello: una spiaggia (altri livelli possibili in futuro).

- **Protagonista (Player):** una ragazza che difende il fidanzato lanciando palle di sabbia contro le altre ragazze finché non le sconfigge.
- **Il fidanzato (Boyfriend, la "torre"):** un ragazzo bellissimo, per questo le altre ragazze della spiaggia se ne invaghiscono e vogliono portarselo via. Non si muove: è l'oggetto da difendere.
- **Due valori di difesa del ragazzo:**
  - **Moralità = scudo** (shield nel codice): la sua caratura morale e il rispetto per la fidanzata. I nemici intaccano prima questa.
  - **Fedeltà = salute** (hp nel codice): entra in gioco quando la moralità è a zero e cala man mano che i nemici attaccano.
  - Quando moralità e fedeltà sono a zero il ragazzo non è più fedele e scappa con le altre ragazze (idea da valutare: scappa con l'ultima che lo ha attaccato). È il game over.
- **Come attaccano le nemiche:** non fanno danno fisico: pose, avances e movimenti sensuali verso il ragazzo; quando la moralità è a zero arrivano anche a toccarlo fisicamente.
- **Reazioni del ragazzo (animazioni/sprite da prevedere):** con la moralità attiva guarda le ragazze con curiosità, senza malizia; a moralità zero le guarda con più interesse; infine cede e scappa.
- **Ondate:** a ogni ondata il numero di nemiche aumenta gradualmente, così come la loro salute. Prevista una varietà di "classi" di nemiche, da quelle molto resistenti e che fanno molto danno ma lente (movimento e frequenza di attacco) a quelle fragili e veloci con danno costante nel tempo, con un ampio range intermedio. Per ora nel gioco c'è una sola nemica base con azioni standard, da migliorare aggiungendo i diversi tipi.
- **Valuta e negozio:** a fine ondata si guadagnano monete (nel contesto di gioco, quelle perse dalle ragazze sconfitte). Tra un'ondata e l'altra passano circa 20 secondi, durante i quali la protagonista può andare in un negozietto sulla spiaggia per comprare potenziamenti, ricaricare moralità e fedeltà del ragazzo e altri bonus tipici del genere.
- **Idee future (non decise):** ondate infinite oppure un limite; modalità di sfida diverse; obiettivi o una campagna; altri livelli.
- **Per la grafica:** le nemiche sono ragazze in spiaggia più belle della protagonista, con la chioma voluminosa del concept (Assets/ConceptArt/Player/player_turnaround.png) e colori variabili di capelli, occhi, costume e pelle; ogni classe può avere un aspetto distinto.
- **Stile delle avances:** le nemiche restano sempre vestite (costumi da spiaggia), niente nudità. Le pose sono ammiccanti e ironiche, in stile fumettistico e volutamente esagerate (sguardi, baci, capelli, appoggiarsi, braccio al collo). A moralità zero arrivano a toccare il ragazzo in modo sensuale ma ironico (contatto breve e comico, con cuoricini ed espressioni esagerate). Deve essere sempre evidente che le ragazze ci provano attivamente.

## Gioco e struttura

- Gioco 2D top-down da spiaggia, pixel art; Godot **4.7 stable**, renderer Mobile.
- Menu principale -> Scenes/level.tscn. Difesa a ondate: il Player lancia palle di sabbia contro i nemici diretti al partner Boyfriend; la morte del partner causa game over.
- Scripts/level.gd: ondate, spawn, punteggio, valuta, HUD e timer. Scripts/enemy.gd: movimento, attacchi, salute e morte. Scripts/boyfriend.gd: salute/scudo, bonus e scelta dell'animazione del ragazzo in base a moralità, fedeltà e nemiche che attaccano; set_max_hp() e set_max_shield() sono stub (pass).
- Objects/projectiles.tscn e Scripts/projectiles.gd: proiettile Area2D (palla di sabbia).
- Acquisti: Scripts/upgrades_purchase.gd e Files/item_list.csv (separatore `;`, categorie Player/Target/Bonus). Oggi funzionano solo gli oggetti che ripristinano moralità e fedeltà del ragazzo, senza spendere valuta.
- Presenti menu, opzioni audio, tutorial, pausa (Esc) e game over.
- Autoload: Formulas, SignalManager, MusicManager, Global. Global.is_in_purchase blocca movimento e nuovi lanci durante gli acquisti.
- Gli script di Player, Boyfriend e Upgrades sono agganciati alle rispettive scene base (Characters/player.tscn, Characters/boyfriend.tscn, Objects/upgrades.tscn); level.tscn le istanzia senza override di script.
- Files/item_list.csv è letto con FileAccess: il suo .import deve usare `importer="keep"` (Import As -> Keep File nel dock Import), altrimenti il CSV grezzo non entra negli export.

## Vincoli dell'utente

- Collisioni (CollisionShape2D) e RayCast2D possono essere modificati se serve per adattarli alla grafica o al gioco; dopo ogni modifica verificare in gioco (Godot AI).
- Modificare il gameplay preesistente solo se strettamente necessario.
- Solo nearest-neighbor; mantenere lo stile visivo descritto sotto.
- Lancio rapido e sincronizzato col braccio; la palla non deve partire prima del frame di rilascio.
- **.vscode/settings.json è gestito dall'utente: non toccarlo.**
- I commit li fa l'utente.
- Errori noti di TileSet/tilemap e rifinitura del negozio sono rimandati a sessioni dedicate: non toccarli senza richiesta.

## Player: specifiche

Characters/player.tscn: AnimatedSprite2D con Assets/Characters/Player/player_frames.tres e nodo MovingThrow (Sprite2D, hframes 8, vframes 64) con player_moving_throw.png. Scala (4, 4), offset (0, -3), filtro nearest. CharacterBody2D in modalità Floating (`motion_mode = 1`): le nemiche non trascinano il Player come piattaforme mobili.

| Righe di player_spritesheet.png | Animazioni | Frame | FPS | Loop |
| --- | --- | --- | --- | --- |
| 0-3 | idle_up, idle_down, idle_right, idle_left | 6 | 5 | Sì |
| 4-7 | walk_up, walk_down, walk_right, walk_left | 8 | 8 | Sì |
| 8-11 | dash_up, dash_down, dash_right, dash_left | 8 | 12 | Sì |
| 12-15 | throw_up, throw_down, throw_right, throw_left | 8 | 32 | No |

up = Nord, down = Sud, right = Est, left = Ovest.

- **Diagonali:** gli stessi 4 gruppi con suffissi `_up_right` (NE), `_up_left` (NW), `_down_right` (SE), `_down_left` (SW) in player_frames.tres. Atlanti: Assets/Characters/Player/player_diagonals_spritesheet.png (righe = gruppo*4 + direzione NE,NW,SE,SW; stessi frame e FPS) e player_diagonals_moving_throw.png (righe = azione*32 + direzione*8 + fase). Rigenerazione: `build_diagonals()` in Tools/blender/blender_pipeline.py (yaw Root NE 135, NW -135, SE 45, SW -45). La scelta tra 8 direzioni sta in `Formulas.direction_name()` (diagonale se l'asse minore > 0.414 del maggiore), usata per movimento, mira del lancio e nemici. Durante i lanci in movimento MovingThrow cambia texture tra atlante cardinale e diagonale.
- player_moving_throw.png (384x3072): riga = azione*32 + direzione*8 + fase_del_passo; colonna = frame del lancio. Azioni Walk=0/Dash=1, direzioni N/S/E/W = 0..3. Durante i lanci in movimento: gambe dal passo corrente, busto dal lancio.
- Lancio cardinale verso sinistra: preparazione alta del braccio destro, sinistro di accompagnamento vicino al corpo e arco dall'alto al basso. Vale da ferma, camminando e correndo; rilascio al frame3. La posa destra resta il riferimento invariato. Dettagli in `Docs/BLENDER.md` §12.
- Movimento ui_left/right/up/down a 400; run (Spazio) porta a 800 e seleziona Dash. Asse dominante del movimento, precedenza orizzontale sulle diagonali esatte. Idle mantiene l'ultima direzione.
- shoot_sand (tasto destro) avvia start_throw(); durante Throw il movimento continua. **throw_release_frame = 3**: la palla è in mano nei frame 0-2 e parte al 3; throw_released è emesso dopo lo spawn. A fine Throw torna Idle se fermo; in movimento riprende Walk/Dash dalla fase raggiunta.
- Collider: RectangleShape2D 72x120, posizione (0, 17) (sprite 48x48 a scala 4; il bbox visibile è circa 80 px in larghezza e va da -95 a +77 in altezza). RayCast2D: scala (2, 2), target (50, 0).

## Palla di sabbia: specifiche

- Assets/Projectiles/SandBall/sand_ball.png (celle 24x24) e sand_ball_frames.tres: flight 4 frame 12 FPS loop; impact 4 frame 26 FPS una volta; land 8 frame 14 FPS una volta (texture separata sand_ball_land.png, vedi sotto).
- In projectiles.tscn l'AnimatedSprite2D ha scale (2, 2): il nodo eredita scala 2 dal RayCast2D, quindi 1 pixel = 4 px a schermo come il Player.
- Lo sprite ruota con la direzione di lancio: l'impatto è disegnato verso +x (il nemico) e simmetrico in verticale; projectiles.gd imposta flip_v quando il lancio va a sinistra, così la luce resta in alto. Ogni nuovo proiettile o effetto che ruota con la mira va disegnato con la stessa regola.
- Collider RectangleShape2D 24x22 in posizione (1, 0), sulla testa della palla (coordinate locali, il nodo eredita scala 2).
- Danno immediato una sola volta al contatto con un nemico vivo; la palla si ferma e sparisce a fine impatto. I colpi mancati, dopo 3 s di volo, cadono sulla sabbia: animazione `land` (8 frame 24x24, 14 FPS, una volta) da Assets/Projectiles/SandBall/sand_ball_land.png (sorgenti Tools/pixelorama/sand_ball_land.pxo e sand_ball_land_gen.py): la palla si rimpicciolisce di poco (3 frame), si schiaccia a terra, scoppia in granelli e si dissolve in granelli scuri visibili sulla sabbia. Simmetrica, quindi vale per ogni direzione di lancio. Mentre cade non colpisce più e rallenta fino a fermarsi.

## Nemica base: specifiche

- Sorgenti: Tools/blender/nemica.blend, ricostruito da base_personaggio.blend sul turnaround approvato con `nemica_modello.py:make_enemy()`. Riusa corpo regolare, testa e visual hull del Player; chioma viola lunga e liscia, ciocche alle tempie, bikini smeraldo triangolare con lacci e fiocchi ai fianchi. Volumi morbidi di seno e glutei continui nel corpo. `nemica_pipeline.py` genera atlante e SpriteFrames; procedura in Docs/BLENDER.md §11.
- Palette: capelli viola #2a1240 #4b2a78 #7043a1 #a97fd9; costume smeraldo #16503a #25805a #3db57d #8de0b4; pelle e viso invariati rispetto al Player.
- Occhi stabili nelle diagonali anteriori: il singolo occhio leggibile mantiene il timbro2x3 con riflesso, sulla pelle sopra la bocca. Frontale con due occhi e profili con uno1x3. Parametri di selezione e verifica in `Docs/BLENDER.md` §13.
- Atlante enemy_spritesheet.png: **768x2048, celle 64x64**, 12 colonne, 32 righe; righe = gruppo*8 + direzione. Camera `ORTHO = 2.2*64/48`: stessa scala di pixel del Player, con margine per capelli e caduta. Gruppi: walk (righe 0-7, 8 frame), flirt (8-15, 12 frame), idle (16-23, 6 frame, riusa idle() del Player), dead (24-31, 8 frame: caduta a sedere, `fall()` in nemica_pipeline.py, tabella `FALL` di 8 pose; gambe all'aria, impatto, rimbalzo, seduta stordita). Ordine direzioni: up, down, right, left, up_right, up_left, down_right, down_left.
- Assets/Characters/Enemy/enemy_frames.tres: `walk_<dir>` 8 FPS, `flirt_<dir>` 8 FPS, `idle_<dir>` 5 FPS, tutte in loop; `dead_<dir>` 12 FPS, una volta sola (resta sull'ultimo frame). La pipeline scrive tutte le 32 animazioni insieme all'atlante, inclusa la morte, mantenendo lo UID esistente della risorsa. Tutte le regioni sono 64x64 anche nel riferimento caricato dall'editor, coerenti con la texture 768x2048. `build_enemy_steps()` permette la stessa build in lotti MCP.
- Il passo riusa gambe, bacino e busto del Player: cosce ±1.5°, rotazione Y del bacino massima 3°. Il busto eredita le rotazioni del Player (spine Y ±5°, chest Y ±4°); braccia e chioma mantengono il gesto della nemica. Attaccatura frontale più piena alle tempie, con guance libere di profilo, coerente con il turnaround. Anche le action walk/run/attack_walk/attack_run della base generica hanno il passo raccolto; geometria e rig a riposo sono invariati. Il flirt è la posa da ferma davanti al ragazzo: piedi fissi a terra (IK `pin_feet()` su coscia e stinco), peso che passa da una gamba all'altra con bacino che si sposta, si abbassa e ruota, busto in contro-movimento, una mano sul fianco e l'altra tra i capelli, testa inclinata.
- Characters/enemy.tscn: CharacterBody2D in modalità Floating (`motion_mode = 1`), senza trasporto da pavimenti mobili; AnimatedSprite2D scala 4, offset (0, -3); barra salute spostata in alto di 40 px; collider 72x120 in (0, 17). La logica che sceglie flirt, idle e walk sta in enemy.gd `update_animation()` (vedi CODE_MAP.md).
- Colpita e morte: lampo bianco 0,1 s con shader `Assets/Characters/Enemy/hit_flash.gdshader` (solo pixel opachi, l'ombra non cambia), piccolo rinculo e stordimento di 0,15 s (non durante il flirt). Alla morte cade a sedere nella direzione in cui guardava, resta a terra circa 1 s e sparisce in un "puff": `Objects/puff.tscn`, nuvoletta di 6 frame 32x32 (scala 4) disegnata in Pixelorama con palette sabbia #fff6e8 #f6e2b0 #e3c084 e contorno #3a1418 (sorgenti: Tools/pixelorama/puff.pxo e puff_gen.py; sheet Assets/Effects/Puff/puff.png). Cresce, copre il corpo al picco e si scioglie in sbuffi più piccoli. Niente particelle di Godot (`CPUParticles2D`/`GPUParticles2D`): l'idea dei granelli di sabbia non è stata realizzata.
- Concept: Assets/ConceptArt/Enemies/enemy_turnaround.png (1536x1024, fronte/profilo destro/retro); look generale approvato dall'utente. Prompt in Tools/concept/prompts.json, voce enemy_base. Donna adulta atletica e formosa, proporzioni chibi, vita definita, seno e glutei leggermente più pieni rispetto alla protagonista senza eccessi. Capelli viola lunghi e lisci fino alla vita bassa, braccia libere nella vista posteriore; bikini smeraldo a triangolo con lacci sopra e ai fianchi, slip sgambato. Modello e sprite attuali derivano da questo concept e sono approvati, compresi passo raccolto, busto e attaccatura.

## Ragazzo: concept

- Assets/ConceptArt/Boyfriend/boyfriend_turnaround.png: tavola 1536x1024, fronte/profilo destro/retro, nello stile dei turnaround Player e nemica; prompt in Tools/concept/prompts.json, voce boyfriend. **Concept approvato dall'utente.**
- Specifiche richieste: adulto leggermente più alto delle ragazze, atletico e robusto senza eccessi muscolari; viso bello e affascinante, occhi verdi, pelle moderatamente abbronzata; capelli corti castano scuro, taglio ordinato con lati corti e parte superiore pettinata lateralmente, ispirato al taglio di George Clooney.
- Barba corta castana su mento e mandibola, ispirata al riferimento di Can Yaman: spazio di pelle libera sotto il labbro inferiore con piccolo pizzetto triangolare centrale rivolto in basso. Collanina sottile da spiaggia, piccole perline scure con accenti rosso/giallo/verde d'ispirazione giamaicana.
- Costume richiesto: bermuda fino a metà ginocchio. Colore scelto: terracotta caldo (riferimento #B85B41), con cordino chiaro, in una palette ispirata ai toni Autunno dell'armocromia.
- Per i concept è sufficiente ImageGen con i turnaround esistenti come riferimento; Pixelorama serve solo quando sono necessari ritocchi o pixel art.

## Ragazzo: sprite (in lavorazione, render di prova da approvare)

- Modello ricostruito dal concept (Tools/blender/ragazzo.blend, `ragazzo_pipeline.py`; procedura e parametri in `Docs/BLENDER.md` §6-7).
- **Altezza dal concept (priorità dell'utente):** rapporto delle altezze dei due turnaround, 879/759 = 1.158. Cella **64x64** (non 48x48) con la stessa scala di pixel del Player; figura circa 48 px (righe 5-53), piedi alla riga 53.
- Viso a pixel: di fronte occhi2x2 (scuro + riflesso, riga bassa verde), di profilo1x2 a2px dal bordo del viso. Occhi alzati di un ulteriore pixel nel timbro, sopracciglia piatte2x1 #6b3a26 sulla riga subito sopra; eliminate le piccole sopracciglia dipinte sulla testa che si sommavano al timbro. Bocca2px #b5483a frontale e1px laterale; bocca, barba e marcatori3D conservano le quote precedenti, già corrette per la camera inclinata. Occhi chiusi dell'idle preservati. Procedura riproducibile in `Docs/BLENDER.md` §13.
- Palette (dai colori del concept): pelle #8f4a2c #c97847 #e99d63 #f8b47a; capelli e barba #2b140c #4d2a1e #6b3a26 #9b573b; bermuda #6e2818 #9e3f2c #c4553a #dd7050; occhi #1f3319 / #4e7a34; perline #1e0d07 con #c0392b #e8c547 #2e8b45.
- **Modello approvato dall'utente** (nota dell'utente: davanti sembra senza collo, accettato). Ancora da fare: capelli con la forma pettinata del concept (oggi la sagoma è giusta ma la superficie è liscia), cordino dei bermuda. Tools/pixelorama/boyfriend.pxo contiene un ritocco a mano del modello precedente, superato.
- **Animazioni (richiesta dell'utente)**, `build_boyfriend()` scrive Assets/Characters/Boyfriend/boyfriend_spritesheet.png e boyfriend_frames.tres; 8 direzioni come le nemiche:
  - `idle` (6 frame, 5 FPS, loop): fermo al sole, mani sui fianchi, mento alzato, occhi chiusi (`EYES_CLOSED`), respira solo il busto.
    Gomiti più bassi e raccolti; mani rivolte verso il basso, vicine ai fianchi. La stessa posa di appoggio è condivisa con glance e con il braccio sinistro di admire.
  - `glance` (8 frame, 8 FPS, una volta): corpo sempre rivolto in basso come l'idle, testa (fino a 90°) e busto (al massimo 30°) girati per un attimo verso la direzione della nemica, poi tornano; occhiata curiosa senza attenzione.
  - `admire` (8 frame, 6 FPS, loop): rivolto verso la nemica, sporto in avanti, testa inclinata, mano destra al mento, sinistra sul fianco, ondeggia.
  - `flex` (8 frame, 8 FPS, loop): rivolto verso la nemica, doppio bicipite col petto in fuori a impulsi.
- Regole di scelta (utente): con moralità > 0 sempre lo stesso comportamento (idle con occhiate ogni 2,5-5 s), qualunque sia la fedeltà; con moralità a 0 dipende dalla fedeltà: sopra metà `admire`, a metà o meno `flex`. Senza nemiche che attaccano: idle. Verificato in gioco (sequenza glance -> admire a moralità 0 -> flex a fedeltà 50). Da far approvare all'utente in gioco.

## Pipeline grafica e stile visivo - LEGGERE PRIMA DI TOCCARE SPRITE

Tutte le nuove risorse grafiche (nemici, ragazzo, oggetti, effetti) devono seguire questo stile e questi strumenti. Strumenti MCP del progetto: **Blender** (personaggi animati), **Pixelorama** (pixel art a mano, effetti, ritocchi), **Godot AI** (editor e gioco: scene, nodi, script, avvio, log, screenshot per verificare in gioco).

### Strumenti (guide operative dedicate)

Il catalogo della skill è estendibile: Blender, Godot e Pixelorama sono la dotazione iniziale. Quando viene usato un nuovo programma tramite MCP, l'agente aggiunge la guida generica, la voce nel catalogo e la guida locale; un nuovo backend dello stesso programma integra la guida esistente distinguendo le proprie API. Anche le nuove guide seguono l'aggiornamento obbligatorio e la separazione tra know-how generico e dettagli del progetto.

Server MCP attesi: `blender`, `pixelorama`, `godot-ai`, con i programmi aperti. La skill condivisa `game-tools`, in `C:\Users\stefa\.agent-knowledge\game-tools\SKILL.md`, instrada alle tre guide generiche in `references/`. Codex e Claude Code usano la stessa copia. Le tre guide locali esistenti restano dedicate al progetto: leggere quella pertinente prima dell'uso e aggiornarla con le nuove lezioni verificate; trasferire obbligatoriamente il know-how riutilizzabile nei riferimenti della skill in forma generica. Le scelte di stile di questo progetto restano vincolanti qui:

- **Blender** (personaggi animati: modello 3D chibi + rig renderizzato a pixel): `Docs/BLENDER.md`. Sorgenti in `Tools/blender/` (base comune `base_personaggio.blend`, un .blend e uno script per personaggio).
- **Pixelorama** (oggetti piccoli, effetti, icone, ritocchi dentro la silhouette): `Docs/PIXELORAMA.md`. Sorgenti in `Tools/pixelorama/`.
- **Godot AI** (scene, nodi, script, avvio, log, screenshot per verificare in gioco): `Docs/GODOT.md`.
- Cartella `Tools/` versionata in Git (sorgenti grafici; `.gitignore` esclude `.blend1` e `__pycache__`) e ignorata da Godot. Prompt dei concept in `Tools/concept/prompts.json`; concept art in `Assets/ConceptArt/<soggetto>/` (ignorata da Godot). Per ogni nuovo elemento con sprite: sorgenti in `Tools/` e prompt in `Tools/concept/`.

### Modalità di lavoro per un nuovo personaggio (indicazione dell'utente)

1. **Il turnaround è il riferimento principale del modello 3D.** Si porta in Blender come immagini di riferimento (fronte, profilo, retro) allineate al modello, e il personaggio si ricostruisce sopra: sagome di busto, braccia, gambe, testa e capelli adattate alle viste, zone di colore (pelle, capelli, barba, costume) prese dal concept. Non si deforma a occhio un modello esistente.
2. **Coerenza con gli altri personaggi:** stesso rig, materiali toon, camera, contorno, occhi a pixel e ombra della protagonista e delle nemiche; la scala viene dal confronto dei concept (altezze relative come nei turnaround).
3. **Dopo ogni revisione del modello**, mostrare all'utente sia il render del modello sia lo sprite 2D generato (posa base nelle 4 direzioni, ingrandimento nearest), aprendoli direttamente in VS Code. Mostrare le anteprime man mano, senza aspettare il risultato finale.
4. **Pixelorama solo per ritoccare lo sprite risultante**, dentro la silhouette (ciocche, viso, dettagli del costume, linee muscolari), se serve.
5. **Le correzioni di forma e proporzione tornano nel modello:** si usa lo sprite ritoccato come riferimento per rifare correttamente il modello, così ogni frame delle animazioni esce già giusto e coerente tra le direzioni. Non ridisegnare a mano la silhouette vista per vista (le direzioni diventano incoerenti: N/S ed E/O sembrano persone diverse).

### Regole di stile (vincolanti)

Stile pixel confermato per tutti i personaggi.

- Player in celle 48x48; ragazzo e nemica in celle 64x64, alla stessa scala di pixel (ragazzo più alto dal concept; nemica con margine per capelli e caduta). In gioco scala 4 con filtro nearest. Proiettili/effetti in celle più piccole con scala tale che 1 pixel = 4 px a schermo come il Player.
- Pixel interi, nessun anti-aliasing, nessuna semitrasparenza tranne l'ombra; toon a 4 toni con luce fissa dall'alto a sinistra; camera dall'alto a 25° (impostazioni tecniche in `Docs/BLENDER.md` §4).
- Palette Player: pelle #9c5536 #d9864f #faaf72 #ffc994; capelli #5e1c1f #912a2a #d13d3b #ec6a52; costume #4f7f88 #6a9ea6 #96cbcf #c4eef0; sabbia #8a6a3e #b8925a #e3c084 #f6e2b0. Contorno esterno 1 px #3a1418.
- Occhi NON renderizzati: si timbrano a pixel dopo il render (2x3: scuro + riflesso in alto a destra, riga bassa più chiara; nei profili un solo occhio1x3). La nemica mantiene un occhio2x3 nelle diagonali anteriori, vincolato alla pelle. Sguardo dolce, mai inclinato (inclinato sembra arrabbiata). Bocca2px #c25a4a solo di fronte.
- Braccia leggibili nelle viste laterali e diagonali di Player, nemica e ragazzo: contorno1px #3a1418 sul busto dove il braccio lo nasconde, esterno al braccio per conservarne la pelle e limitato all'interno della sagoma opaca totale. Sagoma esterna e ombra restano quelle del render3D; nessun anello disegnato sull'attaccatura della spalla. Layout, tempi, scene e controller invariati.
- Ombra: proiezione verticale del corpo (Root scalato a z=0.002), #3a1418 alpha 97/255, sotto il contorno, più piccola quando i piedi sono in aria.
- Proporzioni: chibi ma vicine al concept (testa grande, corpo non troppo schiacciato). Capelli compatti nel Player per leggibilità a 48 px.
- Animazioni: l'idle muove solo il busto con piedi e bacino fermi (non deve "saltellare"); nella camminata Nord/Sud le gambe vanno leggermente divaricate per distinguerle; ogni animazione d'attacco deve chiudere il ciclo tornando alla posa base.

## Stato

- **Fatto di recente:** la nemica base ha walk, flirt, idle, colpita (lampo bianco, rinculo, stordimento) e morte (caduta a sedere, poi puff) in 8 direzioni, collegate a enemy.tscn e enemy.gd; i colpi mancati cadono sulla sabbia e si disperdono (animazione `land`). Le nemiche seguono un percorso verso un proprio posto sul bordo dell'area del ragazzo (A* su griglia in `Scripts/pathfinder.gd`, posti e separazione in `enemy.gd`), non si urtano tra loro (layer di collisione 2) e il livello ordina gli sprite per y.
- **Approvati dall'utente:** nuovo aspetto del Player, inclusi capelli e attaccatura; animazioni, diagonali, ombra e lanci in movimento, con la sola correzione richiesta alle gambe troppo divaricate in camminata/corsa. Approvati anche palla di sabbia, aspetto e animazioni della nemica base (walk, flirt, idle, colpita, morte con puff), pathfinding con posti attorno al ragazzo, collisioni tra nemiche, ordine di disegno per y, caduta a terra dei colpi mancati.
- **Incompleti o con errori noti:** negozio (solo gli oggetti per moralità e fedeltà funzionano, senza spendere valuta; gli acquisti Giocatore e Bonus non hanno effetto; set_max_hp() e set_max_shield() sono stub); TileSet della mappa (circa 970 errori all'avvio del livello, preesistenti).

## Prossimi passi

Punti aperti indicati dall'utente. L'utente li aggiorna: aggiungere quelli nuovi, **rimuovere** quelli completati.


- Sistemare il negozio: spesa della valuta e acquisti Giocatore e Bonus.
- Sistemare gli errori di TileSet e tilemap (non toccarli prima).
- Varianti di colore e classi di nemiche (la nemica base è completa: walk, flirt, idle, colpita, morte).
- Ragazzo: capelli pettinati e cordino nel modello; animazione di fuga al game over (idea: scappa con l'ultima che lo ha attaccato). Animazioni idle/glance/admire/flex approvate dall'utente.
- **Player: aspetto approvato e passo corretto.** Il turnaround resta il riferimento principale; costume da bagno da donna a due pezzi, corpo e capelli attuali approvati. Camminata e corsa hanno gambe più raccolte e minore rotazione del bacino, anche nei lanci in movimento. Idle, tempi e sincronismo preservati; lanci Ovest da ferma e in movimento con caricamento alto del destro. Anteprime del confronto e delle pose aperte in VS Code; nuova andatura da valutare dall'utente. Dettagli in `Docs/BLENDER.md` §8/12.
- Provare un export reale: Files/item_list.csv deve essere nel pacchetto e il negozio deve popolarsi.
- Valutare la mira durante il lancio: posa scelta all'inizio e raycast al mouse al rilascio, muovendo il mouse possono divergere.
- Playtest completo: menu -> ondate -> acquisti -> game over.
- Riordino cartelle (facoltativo, proposta in CODE_MAP.md, sezione Risorse).

Verifica conclusa degli occhi della nemica, dei contorni delle braccia sui tre personaggi e del viso del ragazzo: sei atlanti finali reimportati, alpha e metadati preservati; controlli dei pixel, animazioni e screenshot in Godot superati. Dettagli in `Docs/BLENDER.md` §13 e `Docs/GODOT.md` §7. La valutazione estetica dell'utente resta aperta.

## Persistenza

Per riprendere il Player dopo l'intervento Codex sul lavoro di Claude: `Docs/BLENDER.md` §8, "Ripresa del lavoro condiviso con Claude", elenca sorgenti e atlanti toccati, parti precedenti mantenute, verifiche e limiti. L'aspetto attuale è approvato; la correzione dell'andatura è applicata e verificata, in attesa della valutazione visiva dell'utente. Le altre modifiche presenti nel working tree non sono automaticamente attribuibili a questo intervento.

Questo file sta in Docs/PROJECT_CONTEXT.md, versionato in Git; Docs/ è ignorata da Godot (.gdignore). Accanto: Docs/CODE_MAP.md (codice) e le guide degli strumenti Docs/BLENDER.md, Docs/PIXELORAMA.md, Docs/GODOT.md. AGENTS.md (Codex) nella radice contiene le regole fisse e rimanda qui; CLAUDE.md (Claude Code) importa AGENTS.md con `@AGENTS.md`, quindi le regole si modificano solo in AGENTS.md. Entrambi vengono letti automaticamente all'avvio della sessione. Ambiente .sprite-tools-env (Pillow/NumPy) escluso da Git/Godot. Tools/ è versionata in Git (sorgenti .blend, script e prompt) e invisibile a Godot (.gdignore).
