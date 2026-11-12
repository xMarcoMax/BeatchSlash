# Beatch Slash! — contesto condiviso per Codex e Claude

## Regole di questo file (indicazione dell'utente)

Serve a Codex e Claude per capire la situazione attuale e come procedere. Contiene solo:

- situazione attuale e breve descrizione di cosa è stato fatto di recente (non la storia del progetto);
- specifiche tecniche di ogni elemento, vecchie e nuove (parametri, layout dei file, valori, regole): servono a capire cosa toccare e analizzare;
- vincoli e regole dell'utente (restano, scritti in modo conciso e non ambiguo);
- "Prossimi passi": i punti aperti indicati dall'utente. Si aggiungono quando l'utente li dice; quelli completati o superati si **rimuovono** (nessuna voce barrata né storico).

Non scrivere: cronologia, correzioni fatte, processo di realizzazione, come le cose sono state integrate, resoconti di verifica. Il comportamento del codice sta in Docs/CODE_MAP.md.

A fine intervento riscrivi le voci toccate, senza note datate. Confronta sempre con i file correnti, git status e le ultime istruzioni dell'utente.

Ultimo aggiornamento: 12 novembre 2026.

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
- Scripts/level.gd: ondate, spawn, punteggio, valuta, HUD e timer. Scripts/enemy.gd: movimento, attacchi, salute e morte. Scripts/boyfriend.gd: salute/scudo e bonus; set_max_hp() e set_max_shield() sono stub (pass).
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

Characters/player.tscn: AnimatedSprite2D con Assets/Characters/Player/player_frames.tres e nodo MovingThrow (Sprite2D, hframes 8, vframes 64) con player_moving_throw.png. Scala (4, 4), offset (0, -3), filtro nearest.

| Righe di player_spritesheet.png | Animazioni | Frame | FPS | Loop |
| --- | --- | --- | --- | --- |
| 0-3 | idle_up, idle_down, idle_right, idle_left | 6 | 5 | Sì |
| 4-7 | walk_up, walk_down, walk_right, walk_left | 8 | 8 | Sì |
| 8-11 | dash_up, dash_down, dash_right, dash_left | 8 | 12 | Sì |
| 12-15 | throw_up, throw_down, throw_right, throw_left | 8 | 32 | No |

up = Nord, down = Sud, right = Est, left = Ovest.

- **Diagonali:** gli stessi 4 gruppi con suffissi `_up_right` (NE), `_up_left` (NW), `_down_right` (SE), `_down_left` (SW) in player_frames.tres. Atlanti: Assets/Characters/Player/player_diagonals_spritesheet.png (righe = gruppo*4 + direzione NE,NW,SE,SW; stessi frame e FPS) e player_diagonals_moving_throw.png (righe = azione*32 + direzione*8 + fase). Rigenerazione: `build_diagonals()` in Tools/blender/blender_pipeline.py (yaw Root NE 135, NW -135, SE 45, SW -45). La scelta tra 8 direzioni sta in `Formulas.direction_name()` (diagonale se l'asse minore > 0.414 del maggiore), usata per movimento, mira del lancio e nemici. Durante i lanci in movimento MovingThrow cambia texture tra atlante cardinale e diagonale.
- player_moving_throw.png (384x3072): riga = azione*32 + direzione*8 + fase_del_passo; colonna = frame del lancio. Azioni Walk=0/Dash=1, direzioni N/S/E/W = 0..3. Durante i lanci in movimento: gambe dal passo corrente, busto dal lancio.
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

- Sorgenti: Tools/blender/nemica.blend (copia del modello del Player con chioma più piena: mesh Hair allargata X 1.10-1.24 e Y dietro 1.12-1.30, crescente verso le punte) e Tools/blender/nemica_pipeline.py (`build_enemy()`, riusa blender_pipeline.py, scrive in Assets/Characters/Enemy).
- Palette: capelli viola #2a1240 #4b2a78 #7043a1 #a97fd9; costume smeraldo #16503a #25805a #3db57d #8de0b4; pelle e viso invariati rispetto al Player.
- Atlante enemy_spritesheet.png: celle 48x48, 12 colonne, 32 righe; righe = gruppo*8 + direzione. Gruppi: walk (righe 0-7, 8 frame), flirt (8-15, 12 frame), idle (16-23, 6 frame, riusa idle() del Player), dead (24-31, 8 frame: caduta a sedere, `fall()` in nemica_pipeline.py, tabella `FALL` di 8 pose; gambe all'aria, impatto, rimbalzo, seduta stordita). Ordine direzioni: up, down, right, left, up_right, up_left, down_right, down_left.
- Assets/Characters/Enemy/enemy_frames.tres: `walk_<dir>` 8 FPS, `flirt_<dir>` 8 FPS, `idle_<dir>` 5 FPS, tutte in loop; `dead_<dir>` 12 FPS, una volta sola (resta sull'ultimo frame). Le animazioni `dead_*` sono nel .tres ma non le scrive la pipeline: se rigeneri la sheet con `build_enemy()` i frame restano validi (stesse righe), ma il .tres va ritoccato a mano per eventuali nuovi frame.
- Il flirt è la posa da ferma davanti al ragazzo: piedi fissi a terra (IK `pin_feet()` su coscia e stinco), peso che passa da una gamba all'altra con bacino che si sposta, si abbassa e ruota, busto in contro-movimento, una mano sul fianco e l'altra tra i capelli, testa inclinata.
- Characters/enemy.tscn: AnimatedSprite2D scala 4, offset (0, -3); barra salute spostata in alto di 40 px; collider 72x120 in (0, 17). La logica che sceglie flirt, idle e walk sta in enemy.gd `update_animation()` (vedi CODE_MAP.md).
- Colpita e morte: lampo bianco 0,1 s con shader `Assets/Characters/Enemy/hit_flash.gdshader` (solo pixel opachi, l'ombra non cambia), piccolo rinculo e stordimento di 0,15 s (non durante il flirt). Alla morte cade a sedere nella direzione in cui guardava, resta a terra circa 1 s e sparisce in un "puff": `Objects/puff.tscn`, nuvoletta di 6 frame 32x32 (scala 4) disegnata in Pixelorama con palette sabbia #fff6e8 #f6e2b0 #e3c084 e contorno #3a1418 (sorgenti: Tools/pixelorama/puff.pxo e puff_gen.py; sheet Assets/Effects/Puff/puff.png). Cresce, copre il corpo al picco e si scioglie in sbuffi più piccoli. Niente particelle di Godot (`CPUParticles2D`/`GPUParticles2D`): l'idea dei granelli di sabbia non è stata realizzata.
- Concept: Assets/ConceptArt/Enemies/enemy_turnaround.png (1536x1024, fronte/lato/retro), variante del concept Player con capelli viola e costume smeraldo; prompt in Tools/concept/prompts.json, voce enemy_base.

## Ragazzo: concept

- Assets/ConceptArt/Boyfriend/boyfriend_turnaround.png: tavola 1536x1024, fronte/profilo destro/retro, nello stile dei turnaround Player e nemica; prompt in Tools/concept/prompts.json, voce boyfriend. Concept da approvare visivamente; sprite e animazioni non ancora realizzati.
- Specifiche richieste: adulto leggermente più alto delle ragazze, atletico e robusto senza eccessi muscolari; viso bello e affascinante, occhi verdi, pelle moderatamente abbronzata; capelli corti castano scuro, taglio ordinato con lati corti e parte superiore pettinata lateralmente, ispirato al taglio di George Clooney.
- Barba corta castana su mento e mandibola, ispirata al riferimento di Can Yaman: spazio di pelle libera sotto il labbro inferiore con piccolo pizzetto triangolare centrale rivolto in basso. Collanina sottile da spiaggia, piccole perline scure con accenti rosso/giallo/verde d'ispirazione giamaicana.
- Costume richiesto: bermuda fino a metà ginocchio. Colore scelto: terracotta caldo (riferimento #B85B41), con cordino chiaro, in una palette ispirata ai toni Autunno dell'armocromia.
- Per i concept è sufficiente ImageGen con i turnaround esistenti come riferimento; Pixelorama serve solo quando sono necessari ritocchi o pixel art.

## Pipeline grafica e stile visivo - LEGGERE PRIMA DI TOCCARE SPRITE

Tutte le nuove risorse grafiche (nemici, ragazzo, oggetti, effetti) devono seguire questo stile e questi strumenti. Strumenti MCP del progetto: **Blender** (personaggi animati), **Pixelorama** (pixel art a mano, effetti, ritocchi), **Godot AI** (editor e gioco: scene, nodi, script, avvio, log, screenshot per verificare in gioco).

### Strumenti

Nomi attesi dei server MCP: `blender`, `pixelorama`, `godot-ai`. I programmi corrispondenti devono essere aperti (Blender con l'add-on, Pixelorama 1.2.3, editor Godot con il progetto). Ogni client (Claude Code, Codex, Claude Desktop) ha la propria configurazione MCP sul computer dell'utente e non è condivisa tra loro: se uno strumento non è collegato, avvisare l'utente.

- **Blender 5.2** con l'add-on ufficiale **MCP di Blender Lab** (v1.0.3) per i personaggi animati: modello 3D chibi low-poly + rig, renderizzato a pixel. Server MCP: repo projects.blender.org/lab/blender_mcp (cartella mcp), avviato con `uv --directory <repo>\mcp run blender-mcp`; Codex lo ha in ~/.codex/config.toml come [mcp_servers.blender]. Lavorare con execute_blender_code.
- **Pixelorama 1.2.3** (NON 1.2.4: l'estensione richiede l'API 9) con estensione **pixelorama-mcp** (github.com/CyberIce2077/pixelorama-mcp, server `node <repo>\dist\index.js`, porta 7651) per oggetti piccoli, effetti, icone e ritocchi a mano. Disegna con griglie di caratteri + palette.
- **Godot AI** (plugin addons/godot_ai, v4.4.1, MCP con ~46 strumenti: scene, nodi, script, segnali, UI, animazioni, screenshot dell'editor e del gioco, avvio del progetto, log). Richiede l'editor aperto. addons/ è esclusa da Git: il plugin resta solo in locale. Client configurati dal pannello Godot AI: Claude Code (~/.claude.json), Codex (~/.codex/config.toml), Claude Desktop. Attenzione: per Claude Desktop il plugin scrive in ...\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json, ma l'app legge ...\AppData\Local\Claude-Data\claude_pzs8sxrjxfjjc\claude_desktop_config.json: dopo aggiornamenti del plugin o cambi di porta (8000/9500) ricopiare a mano il blocco "godot-ai" nel file giusto. Nel pannello Godot AI NON premere "Reconfigure" o "Configure all" per Claude Desktop (riscriverebbe la voce nel file sbagliato); "Rimuovi" su Claude Desktop è innocuo (toglie solo la copia inutilizzata), mentre su Claude Code e Codex va evitato perché cancella la connessione funzionante. Telemetria del plugin attiva di default, disattivabile dal pannello.
- Limite del tool godot-ai `filesystem_manage`: rifiuta di rimuovere o spostare file se un'altra scena è troppo grande da leggere (Objects/Items/item.tscn supera 256 KB) e non riscrive i riferimenti; per spostare file usare il dock FileSystem dell'editor.
- **Cartella Tools/** (versionata in Git per conservare i sorgenti grafici; Tools/.gitignore esclude solo i backup .blend1 e __pycache__; ignorata da Godot con Tools/.gdignore):
  - Tools/blender/personaggio.blend: sorgente della protagonista (modello, rig 17 ossa, action idle/walk/run, materiali, camera CamSprite, palla SandBall). È la copia di riferimento: aprire questa in Blender.
  - Tools/blender/blender_pipeline.py (anche come testo dentro il .blend): con il .blend aperto, `exec(open(...).read()); build_all()` rigenera player_spritesheet.png e player_moving_throw.png in Assets/Characters/Player. Percorsi relativi al .blend, render temporanei nella cartella temp di sistema.
  - Tools/concept/prompts.json: prompt dei concept (protagonista, nemica base, ragazzo).
  - Per ogni nuovo elemento con sprite (personaggio, nemica, oggetto, effetto) salvare il .blend (ed eventuali script) in Tools/blender/ e i prompt dei concept in Tools/concept/, così i sorgenti restano disponibili.
- Concept art di base: cartella Assets/ConceptArt/ (ignorata da Godot con .gdignore), una sottocartella per soggetto, per esempio Player/player_turnaround.png (fronte/lato/retro) ed Enemies/enemy_turnaround.png.

### Regole di stile (vincolanti)

- Personaggi in celle 48x48, in gioco scala 4 con filtro nearest. Proiettili/effetti in celle più piccole con scala tale che 1 pixel = 4 px a schermo come il Player.
- Nessun anti-aliasing: EEVEE 1 sample, filter size 0, view transform Standard. Pixel interi, nessuna semitrasparenza tranne l'ombra.
- Materiali toon a 4 toni: Diffuse -> Shader to RGB -> ColorRamp CONSTANT (0 / 0.12 / 0.40 / 0.80) -> Emission. Luce Sun fissa rispetto alla camera (alto, davanti, da sinistra); si ruota il personaggio (oggetto Root), non la camera.
- Palette Player: pelle #9c5536 #d9864f #faaf72 #ffc994; capelli #5e1c1f #912a2a #d13d3b #ec6a52; costume #4f7f88 #6a9ea6 #96cbcf #c4eef0; sabbia #8a6a3e #b8925a #e3c084 #f6e2b0. Contorno esterno 1 px #3a1418. Le zone del costume sono decise nello shader da un attributo rest_co (posizione a riposo), così non si spostano sulle braccia in animazione.
- Camera ortografica, elevazione 25 gradi, ortho_scale 2.2, target z 0.9. Direzioni: N = Root ruotato 180, S = 0, E = 90, W = -90.
- Occhi NON renderizzati: si timbrano a pixel dopo il render (2x3: scuro + riflesso in alto a destra, riga bassa più chiara; di lato un solo occhio 1x3 spostato verso l'interno). Sguardo dolce, mai inclinato (inclinato sembra arrabbiata). Bocca 1 px #a8473a solo di fronte.
- Ombra: proiezione verticale del corpo (Root scalato a z=0.002), #3a1418 alpha 97/255, sotto il contorno, più piccola quando i piedi sono in aria.
- Proporzioni: chibi ma vicine al concept (testa grande, corpo non troppo schiacciato). Capelli compatti nel Player per leggibilità a 48 px.
- Animazioni: l'idle muove solo il busto con piedi e bacino fermi (non deve "saltellare"); nella camminata Nord/Sud le gambe vanno leggermente divaricate per distinguerle; ogni animazione d'attacco deve chiudere il ciclo tornando alla posa base.

## Stato

- **Fatto di recente:** la nemica base ha walk, flirt, idle, colpita (lampo bianco, rinculo, stordimento) e morte (caduta a sedere, poi puff) in 8 direzioni, collegate a enemy.tscn e enemy.gd; i colpi mancati cadono sulla sabbia e si disperdono (animazione `land`). Le nemiche seguono un percorso verso un proprio posto sul bordo dell'area del ragazzo (A* su griglia in `Scripts/pathfinder.gd`, posti e separazione in `enemy.gd`), non si urtano tra loro (layer di collisione 2) e il livello ordina gli sprite per y.
- **Approvati dall'utente:** Player (sprite, animazioni, diagonali, ombra, lanci in movimento; non modificarlo senza nuova richiesta), palla di sabbia, aspetto e animazioni della nemica base (walk, flirt, idle, colpita, morte con puff), pathfinding con posti attorno al ragazzo, collisioni tra nemiche, ordine di disegno per y, caduta a terra dei colpi mancati.
- **Incompleti o con errori noti:** negozio (solo gli oggetti per moralità e fedeltà funzionano, senza spendere valuta; gli acquisti Giocatore e Bonus non hanno effetto; set_max_hp() e set_max_shield() sono stub); TileSet della mappa (circa 970 errori all'avvio del livello, preesistenti).

## Prossimi passi

Punti aperti indicati dall'utente. L'utente li aggiorna: aggiungere quelli nuovi, **rimuovere** quelli completati.

- Sistemare il negozio: spesa della valuta e acquisti Giocatore e Bonus.
- Sistemare gli errori di TileSet e tilemap (non toccarli prima).
- Varianti di colore e classi di nemiche (la nemica base è completa: walk, flirt, idle, colpita, morte).
- Approvare il concept del ragazzo in Assets/ConceptArt/Boyfriend/boyfriend_turnaround.png; poi creare sprite e animazioni (Characters/boyfriend.tscn, gruppo "target", oggi placeholder Assets/icon.svg) con la stessa pipeline del Player: render di prova 48x48 nelle 4 direzioni da far approvare prima di animare.
- Provare un export reale: Files/item_list.csv deve essere nel pacchetto e il negozio deve popolarsi.
- Valutare la mira durante il lancio: posa scelta all'inizio e raycast al mouse al rilascio, muovendo il mouse possono divergere.
- Playtest completo: menu -> ondate -> acquisti -> game over.
- Riordino cartelle (facoltativo, proposta in CODE_MAP.md, sezione Risorse).

## Persistenza

Questo file sta in Docs/PROJECT_CONTEXT.md, versionato in Git; Docs/ è ignorata da Godot (.gdignore). AGENTS.md (Codex) nella radice contiene le regole fisse e rimanda qui; CLAUDE.md (Claude Code) importa AGENTS.md con `@AGENTS.md`, quindi le regole si modificano solo in AGENTS.md. Entrambi vengono letti automaticamente all'avvio della sessione. Ambiente .sprite-tools-env (Pillow/NumPy) escluso da Git/Godot. Tools/ è versionata in Git (sorgenti .blend, script e prompt) e invisibile a Godot (.gdignore).
