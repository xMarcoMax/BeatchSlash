# Godot AI per Beatch Slash! — guida operativa

Come si lavora sul progetto Godot via MCP (plugin Godot AI): configurazione, strumenti, verifiche in gioco, limiti ed errori incontrati. Si aggiorna ogni volta che si impara qualcosa. Le lezioni valide in ogni progetto vanno (in forma generale) anche nella guida generica `C:\Users\stefa\.agent-knowledge\game-tools\references\godot.md`, da leggere prima di questa. La mappa del codice è in `Docs/CODE_MAP.md`.

## 1. Plugin e collegamento

- **Godot AI** (plugin `addons/godot_ai`, v4.4.1, MCP con ~46 strumenti: scene, nodi, script, segnali, UI, animazioni, screenshot dell'editor e del gioco, avvio del progetto, log). Nome atteso del server: `godot-ai`. Richiede l'editor Godot 4.7 aperto con il progetto. `addons/` è esclusa da Git: il plugin resta solo in locale.
- Client configurati dal pannello Godot AI: Claude Code (`~/.claude.json`), Codex (`~/.codex/config.toml`), Claude Desktop.
- Claude Desktop: il plugin scrive in `...\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json`, ma l'app legge `...\AppData\Local\Claude-Data\claude_pzs8sxrjxfjjc\claude_desktop_config.json`: dopo aggiornamenti del plugin o cambi di porta (8000/9500) ricopiare a mano il blocco `"godot-ai"` nel file giusto. Nel pannello NON premere "Reconfigure" o "Configure all" per Claude Desktop (riscriverebbe la voce nel file sbagliato); "Rimuovi" su Claude Desktop è innocuo (toglie solo la copia inutilizzata), su Claude Code e Codex va evitato (cancella la connessione funzionante). Telemetria del plugin attiva di default, disattivabile dal pannello.
- Ogni client ha la propria configurazione MCP: se lo strumento non è collegato, dirlo all'utente.

## 2. Flusso di lavoro

- Dopo aver scritto o generato file da fuori (PNG, .tres, .tscn): `filesystem_manage(op="scan")`, poi `scene_open(path, force_reload=True)` per le scene modificate su disco.
- Avvio: `project_run(mode="custom", scene="res://Scenes/level.tscn", autosave=False)` per andare dritti al livello (la scena principale è il menu). Fermare con `project_manage(op="stop")`.
- Controlli: `logs_read(source="game")` (stampe ed errori del gioco), `logs_read(source="editor")` (errori di script); `editor_screenshot(source="game")` per vedere il gioco; `game_manage(op="get_node_info", params={"path": "Boyfriend/AnimatedSprite2D", "include_properties": true})` per leggere proprietà a runtime (animazione, hp, shield...).
- Le chiamate MCP sono lente (alcuni secondi l'una): non si riesce a seguire passo passo uno stato che cambia in fretta (la partita arriva al game over prima). Per verificare una sequenza: una `print` temporanea a ogni cambio di stato, lettura con `logs_read(source="game")`, poi **togliere la stampa**.
- All'avvio del livello compaiono sempre circa 970 errori del TileSet (`create_tile`, `has_alternative_tile`...), preesistenti e rimandati: non sono causati dalle modifiche.
- `editor_screenshot(source="viewport_2d")` non inquadra il nodo voluto: per vedere uno sprite meglio avviare il gioco.

## 3. Risorse generate da fuori

- `SpriteFrames` scritto come testo: `[gd_resource type="SpriteFrames" format=3]`, `ext_resource` della texture con solo `path` (l'uid lo aggiunge Godot), un `AtlasTexture` per frame (`region = Rect2(x, y, w, h)`, `filter_clip = true`), `animations` con `frames`, `loop`, `name` (`&"..."`), `speed`. Esempi: `enemy_frames.tres`, `boyfriend_frames.tres` (scritto da `write_frames_tres` in `Tools/blender/ragazzo_pipeline.py`).
- Sprite dei personaggi: `AnimatedSprite2D` con `texture_filter = 1` (nearest), scala 4, offset tale che i piedi cadano come quelli del Player (Player e nemica (0, -3) con celle 48; ragazzo (0, -5) con celle 64).
- `Files/item_list.csv` è letto con FileAccess: il suo `.import` deve usare `importer="keep"` (Import As -> Keep File nel dock Import), altrimenti il CSV non entra negli export.

## 4. Limiti ed errori incontrati

- `filesystem_manage` rifiuta di rimuovere o spostare file se un'altra scena è troppo grande da leggere (`Objects/Items/item.tscn` supera 256 KB) e non riscrive i riferimenti: per spostare file usare il dock FileSystem dell'editor.
- Le avvertenze `UNUSED_PARAMETER` su `set_max_hp`/`set_max_shield` di `boyfriend.gd` sono di stub preesistenti.
- `editor_manage(op="game_eval")` inserisce il codice in una funzione indentata con tab: usare tab anche nei blocchi interni, altrimenti il parser segnala `Mixed use of tabs and spaces` e ferma il debugger. Dopo un errore di compilazione, fermare e riavviare il test; non modificare gli script del progetto per correggere il solo codice di verifica.
