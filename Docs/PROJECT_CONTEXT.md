# Beatch Slash! — contesto condiviso per Codex e Claude

Ultimo aggiornamento: **11 novembre 2026** (Claude). Confrontare sempre con i file correnti, git status e le ultime istruzioni dell'utente. Aggiornare questo file a fine di ogni intervento (stato, approvazioni, punti aperti), mantenendolo descrittivo dello stato attuale e non come diario.

Nel progetto esistono solo le risorse grafiche attualmente in uso, senza suffissi di versione. Le versioni precedenti di sprite e strumenti sono state eliminate su richiesta dell'utente; non vanno ricreate né citate.

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
- **Ondate:** a ogni ondata il numero di nemiche aumenta gradualmente, così come la loro salute. Prevista una varietà di "classi" di nemiche, da quelle molto resistenti e che fanno molto danno ma lente (movimento e frequenza di attacco) a quelle fragili e veloci con danno costante nel tempo, con un ampio range intermedio. Per ora nel gioco ci sono placeholder con azioni standard, da migliorare aggiungendo i diversi tipi.
- **Valuta e negozio:** a fine ondata si guadagnano monete (nel contesto di gioco, quelle perse dalle ragazze sconfitte). Tra un'ondata e l'altra passano circa 20 secondi, durante i quali la protagonista può andare in un negozietto sulla spiaggia per comprare potenziamenti, ricaricare moralità e fedeltà del ragazzo e altri bonus tipici del genere.
- **Idee future (non decise):** ondate infinite oppure un limite; modalità di sfida diverse; obiettivi o una campagna; altri livelli.
- **Per la grafica:** le nemiche sono ragazze in spiaggia più belle della protagonista, con la chioma voluminosa del concept (Assets/ConceptArt/Player/player_turnaround.png) e colori variabili di capelli, occhi, costume e pelle; ogni classe può avere un aspetto distinto.
- **Stile delle avances (indicazione dell'utente):** le nemiche restano sempre vestite (costumi da spiaggia), niente nudità. Le pose sono ammiccanti e ironiche, in stile fumettistico e volutamente esagerate (sguardi, baci, capelli, appoggiarsi, braccio al collo). A moralità zero arrivano a toccare il ragazzo in modo sensuale ma ironico (contatto breve e comico, con cuoricini ed espressioni esagerate). Deve essere sempre evidente che le ragazze ci provano attivamente.

## Gioco e struttura

- Gioco 2D top-down da spiaggia, pixel art; Godot **4.7 stable**, renderer Mobile.
- Menu principale -> Scenes/level.tscn. Difesa a ondate: il Player lancia palle di sabbia contro i nemici diretti al partner Boyfriend; la morte del partner causa game over.
- Scripts/level.gd: ondate, spawn, punteggio, valuta, HUD e timer. Scripts/enemy.gd: movimento, attacchi, salute e morte.
- Scripts/boyfriend.gd: salute/scudo e bonus; set_max_hp() e set_max_shield() ancora stub con pass.
- Objects/projectiles.tscn e Scripts/projectiles.gd: proiettile Area2D (palla di sabbia).
- Acquisti: Scripts/upgrades_purchase.gd e Files/item_list.csv, categorie Player/Target/Bonus; flusso completo non certificato.
- Presenti menu, opzioni audio, tutorial, pausa e game over.
- Autoload: Formulas, SignalManager, MusicManager, Global. Global.is_in_purchase blocca movimento/nuovi lanci durante acquisti.

## Vincoli dell'utente

- Collisioni (CollisionShape2D) e RayCast2D possono essere modificati se serve per adattarli alla grafica o al gioco; dopo ogni modifica verificare in gioco (Godot AI). Player e CharacterBody2D con Scripts/player.gd.
- Modificare il gameplay preesistente solo se strettamente necessario.
- Solo nearest-neighbor; mantenere lo stile visivo descritto sotto.
- Lancio rapido e sincronizzato col braccio; la palla non deve partire prima del frame di rilascio.
- **.vscode/settings.json è gestito dall'utente: non toccarlo.**
- I commit li fa l'utente.

## Player: integrazione e parametri

Characters/player.tscn: AnimatedSprite2D con Assets/Characters/Player/player_frames.tres e nodo MovingThrow (Sprite2D, hframes 8, vframes 64) con player_moving_throw.png. Scala (4, 4), offset (0, -3), filtro nearest.

| Righe di player_spritesheet.png | Animazioni | Frame | FPS | Loop |
| --- | --- | --- | --- | --- |
| 0-3 | idle_up, idle_down, idle_right, idle_left | 6 | 5 | Sì |
| 4-7 | walk_up, walk_down, walk_right, walk_left | 8 | 8 | Sì |
| 8-11 | dash_up, dash_down, dash_right, dash_left | 8 | 12 | Sì |
| 12-15 | throw_up, throw_down, throw_right, throw_left | 8 | 32 | No |

up = Nord, down = Sud, right = Est, left = Ovest.

- player_moving_throw.png (384x3072): riga = azione*32 + direzione*8 + fase_del_passo; colonna = frame del lancio. Azioni Walk=0/Dash=1, direzioni N/S/E/W = 0..3. player.gd la usa durante i lanci in movimento: gambe dal passo corrente, busto dal lancio.
- Movimento ui_left/right/up/down a 400; run (Spazio) porta a 800 e seleziona Dash. Asse dominante del movimento, precedenza orizzontale sulle diagonali esatte. Idle mantiene l'ultima direzione.
- shoot_sand (tasto destro) avvia start_throw(); durante Throw il movimento continua. **throw_release_frame = 3**: la palla è in mano nei frame 0-2 e parte al 3; throw_released emesso dopo lo spawn.
- A fine Throw torna Idle se fermo; in movimento riprende Walk/Dash dalla fase raggiunta.
- Collider: RectangleShape2D 130x129, posizione (0, 0.5). Raycast: scala (2, 2), target (50, 0).

## Palla di sabbia: integrazione

- Assets/Projectiles/SandBall/sand_ball.png (celle 24x24) e sand_ball_frames.tres: flight 4 frame 12 FPS loop; impact 4 frame 26 FPS una volta.
- In projectiles.tscn l'AnimatedSprite2D ha scale (2, 2): il nodo eredita scala 2 dal RayCast2D, quindi 1 pixel = 4 px a schermo come il Player.
- Lo sprite ruota con la direzione di lancio: l'impatto è disegnato verso +x (il nemico) e simmetrico in verticale; projectiles.gd imposta flip_v quando il lancio va a sinistra, così la luce resta in alto. Ogni nuovo proiettile/effetto che ruota con la mira va disegnato con la stessa regola.
- Danno immediato una sola volta al contatto con un nemico vivo; la palla si ferma e sparisce a fine impatto; colpi mancati eliminati dopo 3 s.

## Pipeline grafica e stile visivo - LEGGERE PRIMA DI TOCCARE SPRITE

Tutte le nuove risorse grafiche (nemici, ragazzo, oggetti, effetti) devono seguire questo stile e questi strumenti. Strumenti MCP del progetto: **Blender** (personaggi animati), **Pixelorama** (pixel art a mano, effetti, ritocchi), **Godot AI** (editor e gioco: scene, nodi, script, avvio, log, screenshot per verificare in gioco).

### Strumenti

Nomi attesi dei server MCP: `blender`, `pixelorama`, `godot-ai`. I programmi corrispondenti devono essere aperti (Blender con l'add-on, Pixelorama 1.2.3, editor Godot con il progetto). Ogni client (Claude Code, Codex, Claude Desktop) ha la propria configurazione MCP sul computer dell'utente e non è condivisa tra loro: se uno strumento non è collegato, avvisare l'utente.

- **Blender 5.2** con l'add-on ufficiale **MCP di Blender Lab** (v1.0.3) per i personaggi animati: modello 3D chibi low-poly + rig, renderizzato a pixel. Server MCP: repo projects.blender.org/lab/blender_mcp (cartella mcp), avviato con `uv --directory <repo>\mcp run blender-mcp`; Codex lo ha in ~/.codex/config.toml come [mcp_servers.blender]. Lavorare con execute_blender_code.
- **Pixelorama 1.2.3** (NON 1.2.4: l'estensione richiede l'API 9) con estensione **pixelorama-mcp** (github.com/CyberIce2077/pixelorama-mcp, server `node <repo>\dist\index.js`, porta 7651) per oggetti piccoli, effetti, icone e ritocchi a mano. Disegna con griglie di caratteri + palette.
- **Godot AI** (plugin addons/godot_ai, v4.4.1, MCP con ~46 strumenti: scene, nodi, script, segnali, UI, animazioni, screenshot dell'editor e del gioco, avvio del progetto, log). Richiede l'editor aperto. addons/ è esclusa da Git: il plugin resta solo in locale. Client configurati dal pannello Godot AI: Claude Code (~/.claude.json), Codex (~/.codex/config.toml), Claude Desktop. Attenzione: per Claude Desktop il plugin scrive in ...\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json, ma l'app legge ...\AppData\Local\Claude-Data\claude_pzs8sxrjxfjjc\claude_desktop_config.json: dopo aggiornamenti del plugin o cambi di porta (8000/9500) ricopiare a mano il blocco "godot-ai" nel file giusto. Nel pannello Godot AI NON premere "Reconfigure" o "Configure all" per Claude Desktop (riscriverebbe la voce nel file sbagliato); "Rimuovi" su Claude Desktop è innocuo (toglie solo la copia inutilizzata), mentre su Claude Code e Codex va evitato perché cancella la connessione funzionante. Telemetria del plugin attiva di default, disattivabile dal pannello.
- **Cartella Tools/** (versionata in Git per conservare i sorgenti grafici; Tools/.gitignore esclude solo i backup .blend1 e __pycache__; ignorata da Godot con Tools/.gdignore):
  - Tools/blender/personaggio.blend: sorgente della protagonista (modello, rig 17 ossa, action idle/walk/run, materiali, camera CamSprite, palla SandBall). È la copia di riferimento: aprire questa in Blender.
  - Tools/blender/blender_pipeline.py (anche come testo dentro il .blend): con il .blend aperto, `exec(open(...).read()); build_all()` rigenera player_spritesheet.png e player_moving_throw.png in Assets/Characters/Player. Percorsi relativi al .blend, render temporanei nella cartella temp di sistema.
  - Tools/concept/prompts.json: prompt usati per il turnaround della protagonista.
  - Per nemici e ragazzo aggiungere i loro .blend (ed eventuali script) in Tools/blender/ e i prompt dei concept in Tools/concept/.
- Concept di partenza: Assets/ConceptArt/Player/player_turnaround.png (fronte/lato/retro).

### Regole di stile (vincolanti)

- Personaggi in celle 48x48, in gioco scala 4 con filtro nearest. Proiettili/effetti in celle più piccole con scala tale che 1 pixel = 4 px a schermo come il Player.
- Nessun anti-aliasing: EEVEE 1 sample, filter size 0, view transform Standard. Pixel interi, nessuna semitrasparenza tranne l'ombra.
- Materiali toon a 4 toni: Diffuse -> Shader to RGB -> ColorRamp CONSTANT (0 / 0.12 / 0.40 / 0.80) -> Emission. Luce Sun fissa rispetto alla camera (alto, davanti, da sinistra); si ruota il personaggio (oggetto Root), non la camera.
- Palette Player: pelle #9c5536 #d9864f #faaf72 #ffc994; capelli #5e1c1f #912a2a #d13d3b #ec6a52; costume #4f7f88 #6a9ea6 #96cbcf #c4eef0; sabbia #8a6a3e #b8925a #e3c084 #f6e2b0. Contorno esterno 1 px #3a1418. Le zone del costume sono decise nello shader da un attributo rest_co (posizione a riposo), così non si spostano sulle braccia in animazione.
- Camera ortografica, elevazione 25 gradi, ortho_scale 2.2, target z 0.9. Direzioni: N = Root ruotato 180, S = 0, E = 90, W = -90.
- Occhi NON renderizzati: si timbrano a pixel dopo il render (2x3: scuro + riflesso in alto a destra, riga bassa più chiara; di lato un solo occhio 1x3 spostato verso l'interno). Sguardo dolce, mai inclinato (inclinato sembrava arrabbiata). Bocca 1 px #a8473a solo di fronte.
- Ombra: proiezione verticale del corpo (Root scalato a z=0.002), #3a1418 alpha 97/255, sotto il contorno, più piccola quando i piedi sono in aria.
- Proporzioni: chibi ma vicine al concept (testa grande, corpo non troppo schiacciato). Capelli compatti nel Player per leggibilita a 48 px.
- Animazioni: l'idle muove solo il busto con piedi e bacino fermi (non deve "saltellare"); nella camminata Nord/Sud le gambe vanno leggermente divaricate per distinguerle; ogni animazione d'attacco deve chiudere il ciclo tornando alla posa base.

## Stato

- [x] **Player approvato** dall'utente ("animazione davvero perfetta"): sprite, animazioni, ombra e lanci in movimento. Non modificarlo senza nuova richiesta.
- [x] **Palla di sabbia approvata** ("perfetto"): volo, impatto rivolto verso il nemico, flip_v sui lanci a sinistra.
- [ ] Commit da fare (utente): nuovi PNG con i .import rigenerati da Godot, .tres, Assets/ConceptArt/, Tools/, .gitignore, player.tscn, projectiles.tscn, player.gd, projectiles.gd, README, eliminazione dei file precedenti.
- [ ] **TileSet mappa:** l'import dell'editor segnala celle fuori texture/mancanti (TileSetAtlasSource). Preesistente, causa da diagnosticare.
- [ ] **Mira durante Throw:** posa scelta all'inizio, raycast al mouse al rilascio; muovendo il mouse durante il lancio possono divergere. Da valutare se migliorarlo.
- [ ] Playtest completo menu -> ondate -> acquisti -> game over; flusso potenziamenti e stub statistiche massime da verificare.

## Prossimi passi (NON ancora iniziati, l'utente li chiederà a tempo debito)

1. **Nemici**: ragazze in spiaggia, "più belle della protagonista". Partire dal concept con la **chioma piena e voluminosa** (Assets/ConceptArt/Player/player_turnaround.png), mantenendola, e variare colori di capelli, occhi, costumi, pelle (e altri dettagli) per avere più varianti. Oggi Characters/enemy.tscn usa ancora il placeholder Assets/icon.svg (Sprite2D, CharacterBody2D, RayCast2D scala 2). Servono anche le loro animazioni (da definire con l'utente: movimento, attacco, colpite, morte...).
2. **Il ragazzo ("la torre")**: Characters/boyfriend.tscn, gruppo "target", oggi placeholder icon.svg. Sprite e animazioni da creare.
3. Per entrambi usare la stessa pipeline e le stesse regole di stile del Player: Blender (modello chibi + rig, render 48x48 senza anti-aliasing, toon 4 toni, contorno #3a1418, occhi timbrati a pixel, ombra a terra) e Pixelorama per ritocchi ed effetti. Partire da un turnaround per ciascun personaggio; per le varianti dei nemici basta cambiare le palette dei materiali dello stesso modello. Prima di animare, mostrare all'utente un render di prova 48x48 nelle 4 direzioni e farlo approvare.

## Persistenza

Questo file sta in Docs/PROJECT_CONTEXT.md, versionato in Git; Docs/ è ignorata da Godot (.gdignore). AGENTS.md (Codex) nella radice contiene le regole fisse e rimanda qui; CLAUDE.md (Claude Code) importa AGENTS.md con `@AGENTS.md`, quindi le regole si modificano solo in AGENTS.md. Entrambi vengono letti automaticamente all'avvio della sessione. Ambiente .sprite-tools-env (Pillow/NumPy) escluso da Git/Godot. Tools/ è versionata in Git (sorgenti .blend, script e prompt) e invisibile a Godot (.gdignore).
