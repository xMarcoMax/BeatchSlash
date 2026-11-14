# Godot AI per Beatch Slash! — guida operativa

Come si lavora sul progetto Godot via MCP (plugin Godot AI): configurazione, strumenti, verifiche in gioco, limiti ed errori incontrati. Si aggiorna ogni volta che si impara qualcosa. Le lezioni valide in ogni progetto vanno (in forma generale) anche nella guida generica `C:\Users\stefa\.agent-knowledge\game-tools\references\godot.md`, da leggere prima di questa. La mappa del codice è in `Docs/CODE_MAP.md`.

## 1. Plugin e collegamento

- **Godot AI** (plugin `addons/godot_ai`, v4.4.1, MCP con ~46 strumenti: scene, nodi, script, segnali, UI, animazioni, screenshot dell'editor e del gioco, avvio del progetto, log). Nome atteso del server: `godot-ai`. Richiede l'editor Godot 4.7 aperto con il progetto. `addons/` è esclusa da Git: il plugin resta solo in locale.
- Client configurati dal pannello Godot AI: Claude Code (`~/.claude.json`), Codex (`~/.codex/config.toml`), Claude Desktop.
- Claude Desktop: il plugin scrive in `...\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json`, ma l'app legge `...\AppData\Local\Claude-Data\claude_pzs8sxrjxfjjc\claude_desktop_config.json`: dopo aggiornamenti del plugin o cambi di porta (8000/9500) ricopiare a mano il blocco `"godot-ai"` nel file giusto. Nel pannello NON premere "Reconfigure" o "Configure all" per Claude Desktop (riscriverebbe la voce nel file sbagliato); "Rimuovi" su Claude Desktop è innocuo (toglie solo la copia inutilizzata), su Claude Code e Codex va evitato (cancella la connessione funzionante). Telemetria del plugin attiva di default, disattivabile dal pannello.
- Ogni client ha la propria configurazione MCP: se lo strumento non è collegato, dirlo all'utente.

## 2. Flusso di lavoro

- Dopo aver scritto o generato file da fuori (PNG, .tres, .tscn): `filesystem_manage(op="scan")`, poi `scene_open(path, force_reload=True)` per le scene modificate su disco. Lo scan e il reload della scena non garantiscono aggiornamento delle risorse esterne già tenute in memoria: prima di salvare scene che le usano, seguire §7.
- Avvio: `project_run(mode="custom", scene="res://Scenes/level.tscn", autosave=False)` per andare dritti al livello (la scena principale è il menu). Fermare con `project_manage(op="stop")`.
- Controlli: `logs_read(source="game")` (stampe ed errori del gioco), `logs_read(source="editor")` (errori di script); `editor_screenshot(source="game")` per vedere il gioco; `game_manage(op="get_node_info", params={"path": "Boyfriend/AnimatedSprite2D", "include_properties": true})` per leggere proprietà a runtime (animazione, hp, shield...).
- Le chiamate MCP sono lente (alcuni secondi l'una): non si riesce a seguire passo passo uno stato che cambia in fretta (la partita arriva al game over prima). Per verificare una sequenza: una `print` temporanea a ogni cambio di stato, lettura con `logs_read(source="game")`, poi **togliere la stampa**.
- All'avvio del livello compaiono sempre circa 970 errori del TileSet (`create_tile`, `has_alternative_tile`...), preesistenti e rimandati: non sono causati dalle modifiche.
- `editor_screenshot(source="viewport_2d")` non inquadra il nodo voluto: per vedere uno sprite meglio avviare il gioco.

## 3. Risorse generate da fuori

- `SpriteFrames` scritto come testo: `[gd_resource type="SpriteFrames" format=3]`, `ext_resource` della texture con solo `path` (l'uid lo aggiunge Godot), un `AtlasTexture` per frame (`region = Rect2(x, y, w, h)`, `filter_clip = true`), `animations` con `frames`, `loop`, `name` (`&"..."`), `speed`. Esempi: `enemy_frames.tres`, `boyfriend_frames.tres` (scritto da `write_frames_tres` in `Tools/blender/ragazzo_pipeline.py`).
- Sprite dei personaggi: `AnimatedSprite2D` con `texture_filter = 1` (nearest), scala 4; Player con celle 48 e offset (0,-3), nemica con celle 64 e offset (0,-3), ragazzo con celle 64 e offset (0,-5). Il margine simmetrico della nemica mantiene la figura nella stessa posizione e alla stessa scala di pixel.
- `Files/item_list.csv` è letto con FileAccess: il suo `.import` deve usare `importer="keep"` (Import As -> Keep File nel dock Import), altrimenti il CSV non entra negli export.

## 4. Limiti ed errori incontrati

- `filesystem_manage` rifiuta di rimuovere o spostare file se un'altra scena è troppo grande da leggere (`Objects/Items/item.tscn` supera 256 KB) e non riscrive i riferimenti: per spostare file usare il dock FileSystem dell'editor.
- Le avvertenze `UNUSED_PARAMETER` su `set_max_hp`/`set_max_shield` di `boyfriend.gd` sono di stub preesistenti.
- `editor_manage(op="game_eval")` inserisce il codice in una funzione indentata con tab: usare tab anche nei blocchi interni, altrimenti il parser segnala `Mixed use of tabs and spaces` e ferma il debugger. Dopo un errore di compilazione, fermare e riavviare il test; non modificare gli script del progetto per correggere il solo codice di verifica.

## 5. Verifica della nemica ricostruita

- Godot 4.7 ha caricato `enemy_spritesheet.png` a 768x2048 e le 32 animazioni con celle 64x64; controllati tutti i 272 riferimenti a runtime. Scene, collider, shader e logica non richiedono modifiche.
- Verificati idle e flirt selezionati da `enemy.gd`, lampo di 0.1 s, rinculo 220 e danno applicato. La morte raggiunge frame 7, resta visibile, crea un puff e libera la nemica. Screenshot in gioco della camminata aggiornata accanto al Player, con camera ingrandita solo a runtime; le impostazioni di prova non sono state salvate.
- Il primo `project_run` ha restituito `not_live` alla scadenza della finestra iniziale; il successivo `editor_state` ha confermato il helper live. Non considerare il solo timeout iniziale prova di errore degli sprite. Lettura dei log editor/game: presenti gli errori TileSet e warning già noti, nessun nuovo errore di sprite o script osservato.
- Busto della camminata allineato al Player e attaccatura frontale più piena: atlante rigenerato, verificati in gioco idle frontale e walk frontale, profili e diagonale. Prova con camera ingrandita e istanze ferme nello spazio, animazioni attive; nessuna impostazione runtime salvata.

## 6. Contatto fra Player e nemica: evitare il trascinamento

Sintomo: Player fermo, nemica che lo urta e cerca un altro percorso; il Player si muove insieme alla nemica finché riceve un nuovo comando. Entrambe le scene ereditavano `motion_mode = 0` (Grounded) e `platform_floor_layers = 4294967295`: la nemica sottostante diventava un pavimento mobile per il Player.

Correzione in `Characters/player.tscn` e `Characters/enemy.tscn`: `motion_mode = 1` (Floating), proprietà delle radici CharacterBody2D. Collisioni trattate come pareti, senza nozione di pavimento o soffitto; layer, maschere, forme e pathfinding restano invariati. La base grafica Blender non interviene nel problema.

Prova ripetibile con Godot 4.7 via Godot AI:

1. Avviare il menu per una prova isolata; creare un SubViewport con `world_2d = World2D.new()`. `own_world_2d` non è una proprietà valida: è una World2D separata a isolare la fisica.
2. Istanziare le due scene, rimuovere gli script prima di entrare nel tree e rimuovere i gruppi dalle copie. Il mondo fisico separato non isola i gruppi del SceneTree: lasciare una copia senza script nel gruppo enemy fa leggere proprietà `hp` inesistenti alle nemiche reali. Dopo un errore nell'eval, fermare e riavviare il gioco prima di ripetere.
3. Porre Player a (200,150), nemica a (200,300); per 50 frame fisici muovere la nemica verso l'alto a 100 px/s, poi verso destra. Ogni frame porre a zero la velocità del Player e chiamare `move_and_slide()` su entrambi. Con Grounded, in 180 frame il Player veniva trascinato circa 215 px e `get_platform_velocity()` raggiungeva 100 px/s.
4. Con Floating verificare contatto e deviazione laterale sui quattro lati: nessuna velocità ereditata, nessun trascinamento tangenziale; circa 0.87 px di assestamento normale nella prova da 120 frame. Player diretto contro nemica ferma: collisione mantenuta; muovendolo in senso opposto si allontana normalmente (circa 200 px in 30 frame a 400 px/s).
5. Nel livello reale, mettere la nemica a contatto sotto il Player, lasciare attivi `_steer()` e Pathfinder e tenere fermo il Player. Osservati contatto, ricalcolo e arrivo al ragazzo; `get_platform_velocity()` del Player sempre zero, piccolo assestamento iniziale di circa 3.2 px e poi posizione stabile. Nessuna impostazione della prova è stata salvata.

Le modifiche finali alle scene sono due righe. Il salvataggio dell'editor aggiorna anche UID, unique_id e serializzazione delle proprietà predefinite: il diff è stato ridotto alle sole due proprietà richieste, conservando il formato precedente. Il playtest completo resta separato; gli errori TileSet preesistenti non dipendono da questa correzione.

## 7. SpriteFrames esterni e cache dell'editor

Sintomo verificato: PNG nemica 768x2048 con celle 64x64, ma `enemy_frames.tres` riscritto con regioni 48x48. In gioco compaiono frammenti di capelli e corpi tagliati. La risorsa vecchia tenuta dall'editor può essere salvata sopra al file generato correttamente da Blender. Un controllo del PNG e una prova runtime precedente al salvataggio non bastano.

- Ripristinare le 32 animazioni/272 regioni con `resource_manage(op="sprite_frames_create", params={resource_path, animations, overwrite:true})`: conserva lo UID e aggiorna le referenze native già caricate tramite `copy_from_resource`. In questa versione del backend gli AtlasTexture creati hanno `filter_clip = false` e il payload non espone il flag: impostarlo a true sugli AtlasTexture della risorsa dell'editor e salvare con ResourceSaver. Qui è stata eseguita una routine di authoring temporanea via MCP, poi rimossa; il test persistente non modifica le risorse.
- Non limitarsi a inserire `filter_clip = true` nel testo: verificato che scan e reload della scena lasciavano il flag vecchio nella risorsa esterna in memoria, e un successivo `scene_save` lo riscriveva a false. Il refresh deve raggiungere la risorsa tenuta dalla scena, preservandone l'identità, prima del salvataggio.
- `write_enemy_frames()` conserva lo UID già presente nell'intestazione; la sua prova isolata verifica sia creazione senza UID sia rigenerazione con UID, senza modificare la scena Blender o l'atlante. Lo UID stabile non sostituisce il refresh della cache quando cambia il layout.
- Test persistente: `tests/test_enemy_frames.gd`, suite `enemy_frames`. Serve `@tool` e la base `res://addons/godot_ai/testing/test_suite.gd`; il runner rifiuta un semplice RefCounted. Usare le assertion della suite (`assert_true`, `assert_eq`) per risultati tracciati. Avviare `test_run(suite="enemy_frames")`: carica il PackedScene e verifica la risorsa tenuta dal suo AnimatedSprite2D, poi confronta la copia disco caricata con `CACHE_MODE_IGNORE_DEEP`. Controlla nomi, conteggi, FPS, loop, 272 regioni, filter_clip, scala, offset e nearest.
- Prima di chiudere: salvare la scena nell'editor, ripetere il test e controllare il file riscritto; avviare un nuovo processo del gioco e leggere tutte le 272 regioni a runtime. Verifica conclusa con screenshot delle cinque nemiche intere nelle viste frontale/posteriore/laterale/diagonali. `motion_mode = 1` resta su Player e nemica.
- Le riscritture automatiche di Boyfriend e SandBall sono state confrontate per animazione (regioni, texture, durate, FPS, loop e clipping): erano soltanto UID/ordine/serializzazione. Rimossi i diff estranei alla correzione.

### Aggiornamento delle sole pose raster

Per le braccia del ragazzo e il lancio Ovest del Player sono cambiati soltanto tre PNG: `boyfriend_spritesheet.png`, `player_spritesheet.png`, `player_moving_throw.png`. Scan/reimport dei tre file concluso senza errori. Dimensioni, SpriteFrames, scala/offset e codice di gioco invariati; nessuna ricostruzione delle risorse nativa necessaria perché il layout non cambia.

Verifica nel livello con nemiche ferme e nascoste, Player vicino al ragazzo e camera temporaneamente ingrandita: sei lanci sinistra/destra × fermo/walk/run, tutti conclusi con un solo segnale `throw_released`; MovingThrow visibile solo nei casi in movimento. Controllato `throw_left` al frame2 (Rect2(96,720,48,48)), preparazione alta e rilascio sempre al frame3; ragazzo con mani sui fianchi più raccolte. Nessuna impostazione della verifica salvata nelle scene.

Prima di questa verifica controllare `get_tree().paused`: una sessione lasciata nel livello può essere arrivata al game over. I timer dell'eval possono continuare mentre gli AnimatedSprite2D restano fermi al frame0; in una fixture temporanea togliere la pausa e nascondere GameOver prima di concludere che gli sprite non avanzano. Al termine fermare la fixture e avviare una partita nuova dal menu. Restano gli errori TileSet già noti.

### Occhi e contorni condivisi

La revisione successiva riguarda sei PNG: foglio nemica, foglio ragazzo e quattro atlanti del Player (cardinali/diagonali, inclusi entrambi i lanci in movimento). Il pass contorni usa OUTSIDE rispetto al braccio, ma resta dentro la sagoma opaca totale; il ragazzo aggiunge sopracciglia più leggere e occhi alzati1px. Sono modifiche RGB: mantenere dimensioni, alpha, regioni, SpriteFrames, scene e controller. Confrontare i sei canali alpha con i PNG di partenza prima del reimport, quindi verificare le texture effettivamente caricate; non basta controllare i file su disco.

Lotto finale OUTSIDE e nuovo viso del ragazzo completati: sei PNG reimportati senza errori, canali alpha identici e metadati preservati. Verificati in un nuovo processo del livello i profili e le diagonali di Player/nemica, il profilo del ragazzo a occhi chiusi e il frontale `admire_down` a occhi aperti: pelle delle braccia leggibile e sopracciglia alleggerite. Player `walk_right` avanza dal frame0 al2 in0.26s e la texture importata resta48x48. Nemica `walk_down_left`: tre pixel EyeDark RGB(59,29,20) in ciascuno degli otto frame; suite `enemy_frames` finale1pass/0fail. Nessuna fixture salvata; prova fermata e gioco riavviato dal menu con autosave disattivato. Gli errori TileSet preesistenti restano fuori da questo intervento.
