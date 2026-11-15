# Godot AI per Beatch Slash! — guida operativa

Come si lavora sul progetto Godot via MCP (plugin Godot AI): configurazione, strumenti, verifiche in gioco, limiti ed errori incontrati. Si aggiorna ogni volta che si impara qualcosa. Le lezioni valide in ogni progetto vanno (in forma generale) anche nella guida generica `C:\Users\stefa\.agent-knowledge\game-tools\references\godot.md`, da leggere prima di questa. La mappa del codice è in `Docs/CODE_MAP.md`.

## Tipografia e visuale a dimensione fissa

`Assets/UI/game_theme.tres` è il tema globale (`gui/theme/custom`). Font originali Google Fonts: Luckiest Guy, Apache2.0; Fredoka variabile, OFL. `Docs/FONTS.md` descrive ruoli e taglie adattate alla base1152×648. Le nove scene UI usano `theme_type_variation`; eliminati font locali e cache FontFile/Image della scheda oggetto. Le licenze `.txt` sono incluse nei tre preset tramite `Assets/Fonts/Licenses/*.txt`; pacchetto esportato non ancora verificato.

Fredoka ha default reale wght300, anche se i metadati della raccolta indicano400. Creare quattro FontVariation esplicite per400/500/600/700. Su questa combinazione Godot4.7/font, chiavi `"wght"` e `&"wght"` venivano lette dal resource ma `TextServer.font_get_variation_coordinates(font.get_rids()[0])` restituiva `{}`: il testo restava Light. Il tag intero restituito da `TextServer.name_to_tag("wght")`,2003265652, raggiunge invece il renderer. Il solo `get_font_name()` continua a dire Fredoka Light, quindi non prova il peso effettivo. Verificati a runtime600 su pulsanti,500 sul tutorial,700 sull'HUD e400 sulle descrizioni. Il TabContainer imposta il tema del TabBar interno: aggiungere font/size a **entrambi**; il solo TabBar lasciava i tab a400/20. Controllo finale tab:600/22.

`display/window/stretch/mode = "canvas_items"`, aspect `keep`, base1152×648: le misure native sono quelle di default della versione attuale e Godot le omette da `project.godot` quando si salvano valori uguali al default. Camera del livello conservata a zoom(0.5,0.5): area di mondo2304×1296 anche con viewport fisico2544×1422. I tentativi di cambiare `get_window().size` nel gioco incorporato vengono sovrascritti dal contenitore dell'editor: non usarli come prova di diverse dimensioni fisiche.

Per verificare il ridimensionamento nativo senza cambiare le preferenze dell'editor, creata una Window temporanea con le stesse tre proprietà `content_scale_*`: a1152×648,1920×1080,800×800 e2560×1080 mantiene sempre1152×648 logici, con scale uniformi1,1.6667,0.6944,1.6667. Rimossa dopo la prova. Menu, Opzioni, Tutorial, HUD, countdown, invito, negozio Player/Partner, Pausa e Game Over controllati con screenshot; margine superiore del Game Over32px. Nessuna fixture salvata. Non è un playtest completo né una verifica su monitor fisici differenti.

Chiusura verificata dopo un nuovo avvio dell'editor: `project_run(mode="main", autosave=False)` apre `Scenes/main_menu.tscn`, helper live, albero non in pausa, tema corretto e peso effettivo600 sui pulsanti. Screenshot del menu senza tagli e nessun errore all'avvio. Il gioco resta sul menu, senza fixture. Anche in questa sessione il contenitore del gioco ripristina mode0 e1152×648 dopo una richiesta di fullscreen: la prova non verifica il cambio di modalità fisico del monitor.

## 1. Plugin e collegamento

- **Godot AI** (plugin `addons/godot_ai`, v4.4.1, MCP con ~46 strumenti: scene, nodi, script, segnali, UI, animazioni, screenshot dell'editor e del gioco, avvio del progetto, log). Nome atteso del server: `godot-ai`. Richiede l'editor Godot 4.7 aperto con il progetto. `addons/` è esclusa da Git: il plugin resta solo in locale.
- Client configurati dal pannello Godot AI: Claude Code (`~/.claude.json`), Codex (`~/.codex/config.toml`), Claude Desktop.
- Claude Desktop: il plugin scrive in `...\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json`, ma l'app legge `...\AppData\Local\Claude-Data\claude_pzs8sxrjxfjjc\claude_desktop_config.json`: dopo aggiornamenti del plugin o cambi di porta (8000/9500) ricopiare a mano il blocco `"godot-ai"` nel file giusto. Nel pannello NON premere "Reconfigure" o "Configure all" per Claude Desktop (riscriverebbe la voce nel file sbagliato); "Rimuovi" su Claude Desktop è innocuo (toglie solo la copia inutilizzata), su Claude Code e Codex va evitato (cancella la connessione funzionante). Telemetria del plugin attiva di default, disattivabile dal pannello.
- Ogni client ha la propria configurazione MCP: se lo strumento non è collegato, dirlo all'utente.
- Connessione attuale verificata: `session_manage(list)` vede una sessione del progetto e `editor_state` restituisce ready, Godot4.7/plugin e server4.4.1. Codex e Godot usano HTTP8000/WS9500. Il precedente rapporto di porta occupata non dimostrava la causa della disconnessione; nessuna configurazione modificata né processo terminato per risolverla.

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

## 8. Negozio animato e area frontale

`Objects/upgrades.tscn` mantiene radice StaticBody2D e posizione nel livello(512,−950). Shadow/Back/Shopkeeper/Front condividono scala4, nearest e posizione(35,−163); risorse in `Assets/Objects/Shop/`. Il negozio è un solo elemento nell'ordinamento per y del livello. Un CollisionPolygon2D segue il corpo a terra e uno la botte; il tetto non determina le collisioni. Sgabelli e relativi nodi stool_left/stool_right rimossi su richiesta dell'utente per liberare l'accesso al bancone. Area2D frontale con layer0/mask1 e filtro gruppo player. Le coordinate derivano da `Tools/blender/shop_layout.json`.

`Scripts/upgrades.gd` richiede prossimità e NextWaveTimer attivo per F. La prossimità resta registrata durante l'ondata; se inizia la pausa con Player già davanti, compare l'invito. Esc, uscita o fine pausa chiudono il pannello e azzerano Global.is_in_purchase. Esc conserva il comportamento purchase_just_closed di PauseMenu. Riferimenti UI/timer opzionali consentono l'anteprima standalone. Gli acquisti e la valuta hanno ancora i limiti già documentati nel contesto.

GestureTimer one-shot: pausa casuale5–10s, primo gesto casuale fra clean_glass/wipe_counter, nessuna ripetizione consecutiva. animation_finished riporta idle e riavvia il timer. Con due gesti il divieto di ripetizione implica alternanza dopo la prima scelta; i tempi restano casuali. Le animazioni seguono la pausa ordinaria del gioco.

### Verifica ripetibile

- Suite `shop` in `tests/test_shop.gd`:3test superati. Il runner è nell'editor, il cui InputMap non include necessariamente buy_upgrades/esc: il test aggiunge solo le azioni assenti e poi le rimuove. La prima prova emetteva errori action missing e poteva saltare i rami; la suite corretta non aggiunge errori nel log. Rami che usano gli autoload verificati anche nel gioco reale.
- Nuovo processo del livello: fermare solo la logica del livello e le nemiche della fixture, portare temporaneamente Player davanti al negozio e avviare NextWaveTimer. F fuori area non apre; davanti apre e blocca il movimento. Esc chiude senza aprire PauseMenu né mettere in pausa; uscita e fine timer chiudono e sbloccano. Dopo un teletrasporto attendere la sincronizzazione fisica prima di leggere overlaps: nella prova0.15s è bastato, due await physics_frame non davano sempre il segnale aggiornato.
- Fixture SubViewport con World2D separato: copie del negozio e Player senza script/gruppi gameplay. Contatto provato da sinistra/destra/retro/fronte:4collisioni col negozio mantenute. Fixture eliminata al termine. Nel livello, griglia Pathfinder costruita e quattro celle interne al nuovo ingombro solide.
- Dopo la rimozione degli sgabelli: reimport del solo shop_front.png senza errori, nuovo processo del livello con2shape owners sul negozio. Player guidato verso l'alto nei due corridoi prima occupati dagli sgabelli (x relativa−94 e50): raggiunge il corpo del bancone, fermandosi rispettivamente a y42.67 e64.82. Area frontale rileva il Player e F apre il pannello; screenshot verificato. Fixture di movimento rimossa fermando la prova.
- Resource realmente caricato: idle8frame/5FPS loop, clean_glass e wipe_counter16frame/8FPS non loop, regioni160×160. Entrambi i gesti raggiungono frame5 dopo0.65s, poi idle con nuovo timer. Screenshot controllati sia con camera ingrandita temporanea sia a zoom0.5 ordinario; nessuna impostazione della fixture salvata.
- La navigazione/salvataggio dell'editor ha riserializzato anche Boyfriend/SandBall/Theme. Confronto nativo con HEAD: identiche32animazioni del ragazzo,3del proiettile e43proprietà del tema. Ripristinate solo queste riscritture estranee, con copie recuperabili in Temp; nessun cambiamento funzionale ai tre asset.

Godot4.7 e Godot AI4.4.1. Restano gli errori TileSet preesistenti e il playtest completo; non sono stati corretti in questo intervento. Il know-how generico sugli InputMap dei test è nella guida Godot condivisa.

## 9. Ombre sotto tutti i personaggi

Causa del difetto: Shadow del negozio era nello stesso ordinamento per y dell'edificio, quindi copriva un personaggio posizionato sopra la radice del negozio. Nei sei atlanti di Player/nemica/ragazzo l'ombra è incorporata nel PNG: un solo sprite non può ordinare diversamente corpo e ombra.

Convenzione attuale sul canvas del mondo: World.z_index=−2; ombre.z_index=−1 con z_as_relative=false; corpi.z_index=0 e Y-sort esistente. `Objects/upgrades.tscn/Shadow` usa direttamente il livello ombre. In ogni AnimatedSprite2D di Player, Enemy e Boyfriend e nello Sprite2D MovingThrow del Player c'è un figlio Sprite2D GroundShadow con `Scripts/ground_shadow.gd`. Il componente eredita trasformazione e visibilità, copia frame/texture, centratura/offset/flip e, per gli Sprite2D, suddivisione e regione dell'atlante. Materiale del corpo standard assegnato soltanto se manca un materiale personalizzato.

`Assets/Shaders/ground_split.gdshader` e i due ShaderMaterial condivisi separano per alpha: corpo≥0.5, ombra<0.5. COLOR resta invariato: mantiene texture e modulazione già applicate da Godot. Il materiale del figlio non eredita quello del padre. Lo shader hit_flash della nemica scarta anch'esso alpha<0.5, così il lampo bianco non colpisce l'ombra. Sono passaggi distinti della stessa texture: nessun atlante o frame rigenerato.

### Nuovi personaggi e oggetti

- Conservare il contratto grafico: alpha0/255 per trasparenza/corpo, alpha97/255 solo per l'ombra. Verificati tutti e sei gli atlanti correnti con Blender/numpy: nessun altro alpha. Gli atlanti SandBall sono solo0/255 e non richiedono il componente.
- Nei personaggi, riusare le scene con GroundShadow o aggiungere quel figlio allo sprite sorgente. Un eventuale shader personalizzato del corpo deve scartare i pixel dell'ombra, come hit_flash; il componente conserva i materiali personalizzati.
- Per un oggetto con texture ombra già separata, basta assegnare al suo nodo Z−1 assoluto. Corpi e mappa rispettano gli altri due livelli. Non mettere l'intero oggetto al livello ombre.
- Se si introducono altre trasparenze nel corpo, la sola soglia alpha non basta: distinguere con una maschera o un asset ombra separato prima di usare il componente.

### Prove concluse

Suite `ground_shadows`:3/3; gate `enemy_frames`:1/1. La prima esecuzione leggeva una PackedScene Enemy precedente in cache; i test ora caricano scene con CACHE_MODE_IGNORE_DEEP. Il caricamento del livello nei test riproduce i già noti errori TileSet, non nuovi errori degli shader/helper.

Prova pixel reale in SubViewport con World2D separato e Y-sort: immagine2×1 (rosso opaco e nero alpha97), sprite ingrandito32, rettangolo blu che viene prima del proiettore nello Y-sort, fondo bianco aZ−2. Dopo due frame_post_draw: corpo rosso sopra il blu; blu puro sopra l'ombra; ombra ancora visibile fuori dal rettangolo, RGB(0.6196,0.6196,0.6196). Fixture eliminata. Questo verifica l'ordine effettivo del nipote con Z assoluto, non soltanto i valori delle proprietà.

Nel livello, screenshot del Player accanto al lato destro del negozio: ombra dell'edificio sotto piedi/corpo. Lanci in movimento cardinali e diagonali: stesso atlante/frame/offset per corpo e ombra, nessuna ombra fantasma del normale AnimatedSprite2D quando viene nascosto. Nemica colpita: flash=1 sul materiale del corpo, materiale ombra indipendente con shadow_only=true. Le fixture sono state fermate; collisioni, input, tempi e PNG preservati. Restano gli errori TileSet e il playtest completo già aperti.
## 10. Braccio della nemica durante il flirt

Correzione della posa in Blender, non del controller: reimport del solo `Assets/Characters/Enemy/enemy_spritesheet.png`, senza errori. Restano32animazioni/272regioni64×64; solo le96celle flirt sono cambiate. Walk/idle/dead identici al pixel, SpriteFrames e shader delle ombre invariati.

Prova in un nuovo processo del livello con otto nemiche disposte attorno al ragazzo e movimento temporaneamente fermato: update_animation seleziona tutte le flirt_<dir> corrette;12frame/8FPS loop, avanzamento osservato e ombra del frame sincronizzata per ciascuna direzione. Screenshot delle otto viste verificato, senza il gomito destro rovesciato. Per creare le istanze di verifica aggiungerle al tree prima di set_spawn_values: quest'ultimo usa il ProgressBar inizializzato da @onready. Un primo eval che invertiva i passaggi è stato scartato e la prova riavviata; nessuna modifica al metodo di gameplay.

Gate `enemy_frames`1/1 e `ground_shadows`3/3 superati. Self-check Blender su mesh, passo, occhi, piedi e braccio superati. Fixture di camera/posizioni/numero nemiche non salvata; prova fermata al termine. Restano i problemi TileSet preesistenti e il playtest completo.

## 11. Origine del proiettile con livello spostato

Il livello corrente ha posizione(-392,847). Prima del fix, al frame3 il Player era a(619,424), ma la palla a(227,1271): lo spostamento del livello veniva applicato una seconda volta da `b.transform = ray_cast.global_transform`. `Scripts/player.gd:shoot_sand` ora assegna `b.global_transform`. Nessun cambiamento alla posizione del livello, alla mira o al controller delle animazioni.

`tests/test_player_projectile.gd` controlla origine globale, danno e avanzamento della palla con padre identità, traslato, ruotato e scalato. Richiede il runtime: nel runner editor viene saltato esplicitamente. Una fixture incompleta nell'editor incontrava MovingThrow assente e placeholder degli script non @tool/autoload; non era una prova valida del bug. Nel gioco la scena Player completa inizializza correttamente tutti i riferimenti.

Con un nuovo processo del gioco avviato da Godot AI, eseguire tramite `editor_manage(op="game_eval")`:

```gdscript
var suite = load("res://tests/test_player_projectile.gd").new()
suite.test_launch_uses_world_transform_under_transformed_parent()
var result = {"failed": suite._failed, "message": suite._message, "assertions": suite._assertion_count}
suite._free_tracked()
return result
```

Prima del fix: failed=true. Dopo il fix e nuovo processo: failed=false,9assert. Gate `ground_shadows`:3/3,93assert. Nel livello originale, input di lancio da ferma e in movimento e InputEventMouseButton destro attraverso Input.parse_input_event: tutti rilasciano al frame3 con distanza palla/Player=0. Screenshot della palla accanto alla protagonista verificato; fixture fermata. Restano gli errori TileSet preesistenti.

### Scena Player avviata direttamente

Nel caso F6 l'owner è nullo e current_scene è il Player stesso: usare quest'ultimo come padre della palla la trascinava con il personaggio. Riproduzione: palla ferma, spostamento del solo Player di100px, spostamento indesiderato della palla di100px. Il fallback di `shoot_sand` ora usa `get_parent()`.

Per la regressione avviare `res://Characters/player.tscn` con autosave=false e usare lo stesso game_eval sopra, chiamando `test_standalone_player_does_not_carry_released_projectile()` al posto del primo metodo.3assert, prima failed=true e dopo nuovo processo failed=false. Il test ripristina posizione e stato fisico del Player ed elimina la palla creata.

## 12. Spawn nemiche e audit delle coordinate

`enemy_spawn.gd` restituisce punti globali, ma `level.gd` li assegnava alla posizione locale della nemica: anche qui veniva riapplicata la traslazione(-392,847) del livello. `spawn_enemy` ora usa `spawn.position = to_local(spawn_point)` prima di add_child, preservando la posizione corretta già durante _ready.

Avviare il livello in un nuovo processo. Tramite game_eval caricare `res://tests/test_enemy_spawn.gd`, chiamare `test_spawn_matches_sampled_world_point_in_each_area()`, restituire _failed/_message/_assertion_count e chiamare _free_tracked come in §11. Il test isola ciascuna delle tre aree, replica con lo stesso seed il campionamento per confrontare il punto estratto con la posizione effettiva, controlla l'appartenenza al rettangolo e il decremento del contatore. Ripristina aree e contatore; la prova altera il generatore casuale runtime, quindi fermare la fixture prima di tornare al gioco normale.24spawn,73assert: fallimento prima del fix, tutti superati dopo un nuovo processo. Gate lancio:9assert superati anche dopo il fix F6.

Integrazione: due ondate attraverso _process,5+6nemiche,11spawn tutti nelle aree designate e contatore finale0. Posizioni rilevate al child_entered_tree prima del movimento. Screenshot panoramico con contorni temporanei dei tre rettangoli: origini delle nemiche all'interno. Nessuna area, camera o posizione di fixture salvata.

Audit aggiuntivo di script e gerarchia: puff assegnato nello stesso spazio locale della nemica e allo stesso padre, errore globale misurato0; nemiche e ragazzo fratelli, quindi sottrazioni e distanze locali coerenti; AStar pronto e comprensivo di tutti i vertici globali delle tre aree di spawn. Movimento proiettile coerente con il suo transform locale; collisioni/prossimità e ombre ereditano le trasformazioni dei nodi. Nessun altro doppio offset attivo individuato. Il campionamento dei rettangoli e i loro bounds presuppongono assenza di scala/rotazione, rispettata nella scena attuale: rivederli se si cambiano tali trasformazioni.

## 13. Caduta della nemica: postura e verifica nelle otto direzioni

Riesportate solo le64celle dead dell'atlante Enemy da Blender: braccia pendenti, busto raccolto, collo/testa avanzati e ginocchia piegate. `enemy_frames.tres` conservato nei byte:8frame,12FPS, senza loop per ogni direzione. Righe walk/flirt/idle identiche al pixel; alpha0/97/255 conserva la separazione delle ombre. Dettagli del rig e della build in `Docs/BLENDER.md` §11.

Blender `check_enemy()` superato con i nuovi check_fall_arms/check_seated_fall, oltre ai controlli di mesh, rest pose, passi, piedi del flirt, occhi e272frame/32animazioni/272regioni. In Godot scan/reimport del solo enemy_spritesheet.png conclusi senza errori di import. Gate `enemy_frames`1/1 e `ground_shadows`3/3 (93assert) superati dopo l'ultima revisione. Gli errori TileSet già noti compaiono caricando il livello nei test.

Prova in un nuovo processo del livello: logica delle ondate temporaneamente fermata, otto istanze disposte in griglia, facing impostato nelle otto direzioni e dead() eseguito realmente. Per ispezionare l'ultimo frame sono stati fermati soltanto i DeadTimer della fixture. Tutte le animazioni dead_<dir> raggiungono frame3 a circa0.26s e frame7 dopo ulteriori0.5s, conservano12FPS/loop=false e GroundShadow usa la texture esatta del frame corrente. Screenshot finale degli otto orientamenti verificato. Player e Boyfriend nascosti alla radice, così i callback di frame del Player non riattivano lo sprite nell'inquadratura. Camera, etichette e istanze temporanee non salvate; fixture fermata al termine.
