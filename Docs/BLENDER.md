# Blender per Beatch Slash! — guida operativa

Tutto ciò che serve per lavorare sui personaggi in Blender via MCP: installazione, regole, file, procedure, comandi, parametri ed errori già incontrati. Si aggiorna **ogni volta che si impara qualcosa** (nuova procedura, nuovo errore, parametro cambiato). Le lezioni valide in ogni progetto vanno (in forma generale) anche nella guida generica `C:\Users\stefa\.agent-knowledge\game-tools\references\blender.md`, da leggere prima di questa. Le specifiche di gioco dei personaggi (animazioni, layout degli atlanti, palette approvate) stanno in `Docs/PROJECT_CONTEXT.md`; il codice di gioco in `Docs/CODE_MAP.md`.

## 1. Strumenti e collegamento

- **Blender 5.2** con l'add-on ufficiale **MCP di Blender Lab** (v1.0.3). Server MCP: repo projects.blender.org/lab/blender_mcp (cartella `mcp`), avviato con `uv --directory <repo>\mcp run blender-mcp`; Codex lo ha in `~/.codex/config.toml` come `[mcp_servers.blender]`. Nome atteso del server: `blender`.
- Blender deve essere aperto con l'add-on attivo (porta 9876). Se lo strumento non risponde: fermarsi e dirlo all'utente, non improvvisare con altri metodi.
- Si lavora con `execute_blender_code` (codice Python con `bpy`); il valore di ritorno va assegnato a `result` e **deve essere un dict**.
- Il namespace della chiamata **non persiste tra una chiamata e l'altra**: ogni chiamata rifà gli `exec(open(...).read(), globals())` dei file che le servono. Per una build a lotti conservare invece generatore e relativo dizionario di globals in `bpy.app.driver_namespace['_player_build']` (vedi §5).

## 2. Accortezze (indicazione dell'utente, dopo due blocchi di Blender)

- Uno script lanciato via MCP gira sul thread principale: finché lavora Blender non risponde (non si apre nemmeno la finestra). Oltre un paio di minuti l'MCP va in timeout mentre Blender resta bloccato; anche le chiamate successive vanno in timeout finché non ha finito.
- **Fasi brevi**: una chiamata per fase (es. `make_girl("body")`, poi `make_girl("hair")`), con i tempi misurati (`time.time()`), e salvataggio del .blend dopo ogni fase.
- **Salvare prima dei passaggi pesanti**: se Blender si blocca lo chiude l'utente da Gestione attività e lo riapre riattivando l'add-on; il lavoro non salvato si perde.
- **Niente cicli Python con un'operazione costosa per elemento** (es. un raycast per ogni cubetto): usare mappe calcolate una volta e operazioni vettoriali numpy. Creare molta geometria con `mesh.from_pydata` da array numpy, non con `bmesh.ops.create_cube` uno per uno (la chioma è passata da 247 s a 13 s).
- **Niente remesh o levigature su griglie troppo fini**: il remesh voxel a 0.0084 sulla chioma ha bloccato Blender; 0.015-0.02 basta per sprite da 48-64 px.
- Provare prima a risoluzione bassa (es. `VOX = 0.03`), poi affinare.
- Se una chiamata va in timeout: non rilanciarla; attendere (comando in background con `sleep`) e verificare con una chiamata leggera (`bpy.data.filepath`, `is_dirty`).
- Le build complete degli sprite (centinaia di render) vanno lanciate una alla volta e cronometrate. Non modificare modello o materiali durante una build: altrimenti i frame mescolano stati diversi e la build va riavviata.

## 3. File (cartella `Tools/blender/`, versionata in Git, ignorata da Godot)

| File | Contenuto |
| --- | --- |
| `base_personaggio.blend` | Modello e rig originali comuni a tutti i personaggi (17 ossa, action idle/walk/run, materiali toon, camera `CamSprite`, luce, palla `SandBall`). **Base da cui si ricostruisce ogni personaggio; non va modificata.** |
| `personaggio.blend` | Protagonista (Player). In ricostruzione dal concept con `personaggio_modello.py`; viene sovrascritto partendo da `base_personaggio.blend`. |
| `nemica.blend` | Nemica base (modello precedente al nuovo metodo: copia del Player con chioma più piena). |
| `ragazzo.blend` | Ragazzo (Boyfriend), ricostruito dal concept. |
| `blender_pipeline.py` | Utilità comuni (render, contorno, ombra, viso a pixel) e pipeline del Player: pose, `build_all()`, `build_diagonals()`, `build_steps()` per lotti MCP. Va sempre eseguito per primo. |
| `concept_model.py` | Codice comune per ricostruire un personaggio dal concept (vedi §6). |
| `personaggio_modello.py` | `make_girl()`: ricostruzione della protagonista dal concept. |
| `nemica_pipeline.py` | `build_enemy()`: sprite della nemica (walk, flirt, idle, dead). |
| `ragazzo_pipeline.py` | `make_boy()`, pose e animazioni del ragazzo, `build_boyfriend()`. |
| `ref/<nome>_<vista>.png` | Viste ritagliate dei concept, usate come immagini di riferimento in scena. |

`Tools/.gitignore` esclude i backup `.blend1` e `__pycache__`. I percorsi negli script sono relativi al .blend aperto (`BLEND_DIR`), quindi va aperto il .blend giusto prima dell'`exec`. Per ogni nuovo elemento con sprite: .blend e script in `Tools/blender/`, prompt dei concept in `Tools/concept/prompts.json`.

## 4. Stile di render (vincolante, implementato in `blender_pipeline.py`)

- EEVEE, 1 sample (`taa_render_samples = 1`), `filter_size = 0`, view transform Standard, sfondo trasparente: pixel interi, nessun anti-aliasing.
- Materiali toon a 4 toni: Diffuse BSDF -> Shader to RGB -> ColorRamp CONSTANT (posizioni 0 / 0.12 / 0.40 / 0.80) -> Emission. Nuovi materiali: `toon_mat(nome, [4 colori])` (copia di `Skin`); colori piatti (perline, cordino): `flat_mat`.
- Luce Sun fissa rispetto alla camera (alto, davanti, da sinistra): si ruota il personaggio (oggetto `Root`), mai la camera. Direzioni: N = Root 180, S = 0, E = 90, W = -90; diagonali NE 135, NW -135, SE 45, SW -45.
- Camera ortografica `CamSprite`, elevazione 25°, `ORTHO` 2.2 per celle 48 (`ORTHO = 2.2*SIZE/48` per mantenere la scala di pixel con celle diverse, es. 64), target z `TARGET_Z` 0.9 (ragazzo 1.0).
- `render_sprites(yaws, shadow=True)`: per ogni direzione render, contorno esterno 1 px #3a1418, viso timbrato (`stamp_face`), ombra = proiezione verticale del corpo (Root scalato a z=0.002) #3a1418 alpha 97/255, più piccola con i piedi in aria; gli oggetti in `SHADOW_HIDE` (`Hair` e `FrontHair`) non proiettano ombra, altrimenti una chioma voluminosa dà un grande semicerchio innaturale (indicazione dell'utente). Restituisce array RGBA (righe dall'alto).
- Viso timbrato (Player e nemica, `stamp_face` di `blender_pipeline.py`): usa gli oggetti marcatori `Eye_L`, `Eye_R`, `Mouth`, `Head`. Occhi 2x3 (scuro + riflesso in alto a destra, riga bassa più chiara), di lato un occhio 1x3; bocca 2 px #c25a4a se il marcatore è rivolto alla camera (soglia 0.3). Il ragazzo ha il suo `stamp_face` (vedi §7).
- Convenzioni delle ossa: per le ossa rivolte in basso (cosce, braccia) rotazione X negativa = in avanti; abduzione: coscia/braccio sinistro verso l'esterno = Z negativa (destro positiva); per la testa la rotazione Y è la torsione (stesso verso dello yaw di Root), X positiva = testa in avanti/giù. Avambraccio: Z ±110 con braccio abbassato porta la mano al fianco; con braccio orizzontale Z negativa (sinistro) piega l'avambraccio verso l'alto.

## 5. Comandi

Aprire e preparare (ogni chiamata):
```python
import bpy, os
TB = r"C:\Users\stefa\Documents\Progetti\GodotProjects\beatch-slash!\Tools\blender"
bpy.ops.wm.open_mainfile(filepath=os.path.join(TB, "personaggio.blend"))   # solo se serve cambiare file
exec(open(os.path.join(TB, "blender_pipeline.py")).read(), globals())
```
- Player: `build_all()` (player_spritesheet.png e player_moving_throw.png), `build_diagonals()` (atlanti diagonali). Pose: `idle(t)`, `walk(t)`, `run(t)`, lancio `pose_combo(base_fn, t, i, static)` con `KEYS`/`P_THROW` (rilascio al frame 3, palla visibile nei frame 0-2).
- Build Player a lotti MCP: `build_steps(yaws=DIRY, sheet_name="player_spritesheet.png", mt_name="player_moving_throw.png")` restituisce un generatore che rende una posa nelle quattro direzioni per ogni `next()`. Una build contiene 158 pose; lotti di 20 richiedono circa 11 s. Eseguire la pipeline in un dizionario `ns`, conservare `ns['build'] = ns['build_steps'](...)` e `ns` in `bpy.app.driver_namespace['_player_build']`, poi recuperarlo nelle chiamate successive. Per le diagonali passare `DIAG` e i nomi dei due atlanti diagonali. **Solo `StopIteration` conferma che i PNG sono stati scritti**: dopo l'ultima posa serve ancora avanzare il generatore. `build_all()` consuma lo stesso generatore fino in fondo e mantiene firma e risultato precedenti; `build_diagonals()` continua a chiamarlo. Frame, pose, ordine, dimensioni e indici degli atlanti sono invariati.
- Nemica: aprire `nemica.blend`, `exec` di `blender_pipeline.py` e `nemica_pipeline.py`, poi `build_enemy()` (atlante 48x48, 12 colonne, 32 righe = gruppo*8 + direzione; le animazioni `dead_*` del .tres non sono scritte dalla pipeline). Flirt con piedi fissi via IK `pin_feet()`, caduta `fall()` con la tabella `FALL`.
- Ragazzo: aprire `ragazzo.blend`, `exec` di `blender_pipeline.py` e `ragazzo_pipeline.py`, poi `build_boyfriend()` (scrive `Assets/Characters/Boyfriend/boyfriend_spritesheet.png` e riscrive per intero `boyfriend_frames.tres`; ~40 s).
- Ricostruzione dal concept (da `base_personaggio.blend`):
```python
bpy.ops.wm.open_mainfile(filepath=os.path.join(TB, "base_personaggio.blend"))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(TB, "ragazzo.blend"))      # o personaggio.blend
exec(open(os.path.join(TB, "blender_pipeline.py")).read(), globals())
exec(open(os.path.join(TB, "ragazzo_pipeline.py")).read(), globals())        # o personaggio_modello.py
make_boy(); bpy.ops.wm.save_mainfile()                                       # ragazza: make_girl("body"), salva, make_girl("hair"), salva
```

## 6. Ricostruire un personaggio dal concept (`concept_model.py`)

Modalità voluta dall'utente: il concept è la base del modello (vedi PROJECT_CONTEXT, "Modalità di lavoro per un nuovo personaggio"). Il turnaround ha tre viste affiancate (fronte, profilo destro, retro) su sfondo uniforme.

- `Concept(path, model_h, classify, name, axis_mask=None)`: trova le viste (colonne non di sfondo, larghe più di 40 px), `fg` = sagoma (diversa dallo sfondo di più di 0.12), `cls` = zone per pixel (0 contorno/altro, 1 pelle, 2 capelli/barba, 3 costume) dalla funzione `classify`; scala `K` = px del concept per unità del rig (altezza del concept = `model_h`); centri `cf` (fronte), `cb` (retro), `cs` (asse del profilo, alla vita). Con `axis_mask(cc)` (es. pelle + costume) i centri si calcolano sul solo corpo: **una chioma lunga o asimmetrica sposta i centri** (gambe storte, profilo sbagliato).
- `classify`: regole sui colori (ragazzo, `boy_classify`) o colore più vicino a una tabella di riferimento campionata dal concept (ragazza, `GIRL_REFS`). **Includere sfondo e bordi sfumati nella classe 0**, altrimenti i pixel di bordo diventano costume (macchie azzurre).
- Scala tra personaggi: altezza del modello base (`model_height()` su `base_personaggio.blend` = 1.9476547) corrisponde all'altezza della ragazza nel suo concept (759 px); un altro personaggio prende `rig.scale = altezza_concept/759` (ragazzo 879/759 = 1.158).
- `fit_body(cc, body, mask, smooth, split_legs, interp_arms)`: fascia per fascia (`BIN` 0.02) i vertici (classificati dai gruppi di vertici: braccia, gambe, busto, testa) vengono mappati alla larghezza dei segmenti della vista frontale e alla profondità del profilo. Opzioni: `mask` per escludere i capelli che coprono il corpo; `split_legs` divide a metà la sagoma dove le cosce si toccano (altrimenti gambe sbilenche); `interp_arms` interpola le braccia nelle fasce in cui il concept le nasconde (altrimenti vengono schiacciate nel busto e spuntano punte di pelle). Poi `smooth` passaggi di levigatura su x,y (troppi assottigliano il corpo: 3).
- `subdivide(o)`: Catmull-Clark applicato (i gruppi di vertici restano). Corpo una volta per il ragazzo, due per la ragazza (il costume del concept ha zone piccole).
- `paint_zones(cc, obj, materiali, zone, smooth)`: ogni faccia prende la zona del concept proiettata secondo la normale (fronte se n.y < -0.25, retro se > 0.25, altrimenti profilo destro, anche per il fianco sinistro), per maggioranza in una finestra 9x9. `smooth`: pulizia che cambia solo le facce senza vicine della loro zona (o con una sola e almeno tre diverse); un filtro di maggioranza vero **erode e cancella le zone piccole** (il costume spariva).
- `add_refs(cc, scale)`: Empty immagine `Ref_Front`/`Ref_Side`/`Ref_Back` allineati al modello (non si renderizzano).
- Viso: occhi e bocca sono marcatori posati sulla testa con un raycast dalla posizione del concept. La camera inclinata di 25° schiaccia la parte bassa del viso: per il ragazzo occhi alzati di `EYE_LIFT` 23 px, bocca di `MOUTH_LIFT` 35 px e barba sui lati della mandibola alzata di `BEARD_UP` 25 px. Le zone attorno agli occhi del concept (ciglia, sopracciglia) vanno riportate a pelle: li timbra `stamp_face`.

## 7. Ragazzo (`ragazzo_pipeline.py`)

- `make_boy()`: toglie seni e capelli del modello base, `Concept` con `boy_classify`, suddivisione, `fit_body`, `fit_head` (sfera della testa sulla sagoma di testa + capelli + orecchie, dal mento, riga 337 del concept, alla cima), `place_face`, zone (pelle/bermuda sul corpo, pelle/capelli-barba sulla testa), collanina (22 perline cubiche poggiate sul collo con raycast, 15 px sotto il mento, colori `BEAD_COLORS`), scala del Rig, riferimenti. Il mento è la prima riga sotto gli occhi seguita da 15 righe di pelle (prima regola sbagliata: prendeva la fronte o la collanina).
- Cella 64x64, `ORTHO = 2.2*64/48`, `TARGET_Z = 1.0`.
- `stamp_face` del ragazzo: di fronte occhi 2x2 (scuro + riflesso, riga bassa verde), sopracciglia 2 px una riga sopra, bocca 2 px #b5483a; di profilo occhio 1x2 a 2 px dal bordo del viso (uguale nei due lati), sopracciglio 2 px, bocca 1 px sul bordo 3 righe sotto l'occhio. `EYES_CLOSED` (globale) timbra occhi chiusi.
- Animazioni (`ANIMS`): `boy_idle` (mani sui fianchi `hands_on_hips`, occhi chiusi), `boy_glance(i, yaw)` (corpo sempre verso S, testa fino a 90° e busto al massimo 30° verso la direzione, profilo `GLANCE_W`), `boy_admire`, `boy_flex`. `anim_frames` rende ogni animazione nelle 8 direzioni (`DIR8`, ordine `DIR_NAMES` delle nemiche); `write_frames_tres` scrive il .tres (AtlasTexture con regioni 64x64).
- Verifica: con il codice riorganizzato il ragazzo ricostruito è identico al pixel all'atlante in gioco (confronto del frame idle).

## 8. Protagonista (`personaggio_modello.py`, in corso)

- `make_girl(stage)`: `"body"` (≈2 s) = toglie seni e vecchia chioma, suddivide (corpo due volte), **`fit_body_regular`** con maschera pelle+costume (`girl_body_mask`); `fit_girl_head` (ellissoide: larghezza e profondità almeno quelle della testa base, altezza dal mento del concept alla cima del cranio, mento appena più stretto); collo allungato fino dentro il mento (`NECK_FROM`, altrimenti tra testa e spalle resta un buco da cui si vedono i capelli); `place_girl_face` (occhi = pixel scuri di zona 0 nel viso, colonne dove sono fitti, uno per lato, alzati di `EYE_LIFT_G` 23 px; bocca al 60% tra occhi e mento alzata di `MOUTH_LIFT_G` 12 px, altrimenti il raggio colpisce il sotto del mento); materiale del costume con `apply_girl_suit`. `"hair"` (≈9-11 s) = `paint_girl_scalp`, `build_hair` e `build_front_hair`; `"suit"` aggiorna solo il materiale sul corpo attuale, senza ricostruire geometria o capelli. Costanti: `GIRL_H`, `VOX` 0.015, `HAIR_BEHIND` 0.35.
- **Mento e cranio:** `girl_face_rows` rileva l'attaccatura alla riga 239 e il mento alla riga 393 del turnaround attuale. La linea scura deve avere sotto una zona di pelle stretta (il collo): la bocca alla riga 371 ha ancora il viso largo ai lati e va esclusa. Il cranio non supera la quota superiore del concept meno `VOX`. `paint_girl_scalp` apre il viso sotto le ciocche con tempie curve e una piccola punta centrale: il bordo dipinto orizzontale produceva l'effetto cuffia. Il bordo è alzato di circa 39 px del concept per compensare la camera inclinata; solo le facce rivolte in avanti diventano pelle.
- **`fit_body_regular` (concept_model.py) — il metodo per avere un modello regolare (richiesta dell'utente: "deve essere un modello fatto bene"):** dalle sagome si prendono solo le misure lungo l'altezza (metà larghezza del busto, centro e metà larghezza di gamba e braccio, profondità del profilo), rese simmetriche (media dei due lati) e levigate (`smooth_profile`, gaussiana; assi di gambe e braccia come retta); le stesse misure sul modello base; il modello base viene scalato attorno ai suoi assi (scale limitate a 0.6-1.6), le parti si fondono alle giunture con i pesi del rig, poi simmetria esatta (coppie di vertici speculari via KDTree) e 2 passaggi di levigatura. Regole imparate: il busto si confronta con busto + gambe (ai fianchi la sagoma del concept comprende le cosce: confrontandolo col solo bacino la scala era 2.4 e i fianchi esplodevano); misure del modello troppo piccole (collo, < 0.03) non valgono (collare); nelle fasce dove la sagoma frontale è unica e ci sono braccia la misura del busto è ignota e si interpola. Il vecchio `fit_body` fascia per fascia (usato dal ragazzo) copia le irregolarità della mappatura: gambe storte, zig-zag, superfici bitorzolute.
- `build_hair` (visual hull con colore): griglia di cubetti `VOX` nel volume del concept; un cubetto resta se in tutte e tre le viste cade nella sagoma e lì il concept mostra capelli (zona 2 dilatata di 4 px) oppure il cubetto è nascosto dietro corpo o testa; via i cubetti dentro corpo o testa. Il "nascosto/dentro" usa **mappe di profondità** calcolate una volta (un raycast per cella da davanti, dietro e dai due fianchi). Vincoli di profondità (le sagome da sole non la danno): sotto il mento dietro il piano centrale del busto; attorno alla testa dietro il piano delle guance (`HAIR_BEHIND`); davanti al viso (tra attaccatura e mento, entro la larghezza della pelle) solo dietro la metà della testa, altrimenti copre guance e occhi. Il volume dei cubetti viene sfumato (due box blur per asse di raggio `HAIR_BLUR`, poi soglia 0.5) prima di farne la superficie: senza, i capelli in pixel sembrano "cubici" (indicazione dell'utente). Poi cubetti di superficie con numpy, remesh voxel `VOX`, levigatura laplaciana 40 passaggi con volume preservato, solo il pezzo principale (via i frammenti), rilievo delle ciocche (modificatore Displace con texture Clouds `STRAND_SCALE`, coordinate di un Empty scalato `STRAND_STRETCH` in verticale, profondità `STRAND_DEPTH`; poi 4 passaggi laplaciani per togliere le punte; un rumore troppo fine dà un effetto granuloso), pesi `head`/`hair` (sotto il mento passa all'osso `hair`, che ondeggia nelle animazioni), modificatore Armature.
- **Costume continuo (`apply_girl_suit`)**: un solo `BodyMat` su tutto il corpo miscela le rampe toon di `Skin` e `Suit`, copiando anche il colore Diffuse di `Skin` per mantenere la stessa risposta alla luce. `rest_co` viene riscritto dalle coordinate della mesh ricostruita, con z moltiplicata per `body.scale.z`: l'attributo ereditato dal modello base descriverebbe il corpo precedente. `suit_arm` contiene la somma dei pesi di braccia e mani; la soglia 0.5 le esclude dal costume. La maschera usa quote in pixel del turnaround (`row = foot - z*K`, x simmetrica): coppe con scollo a U e bordo inferiore curvo (righe 472/497), fascia posteriore (458-497), spalline (410-490), slip con vita curva e sgambatura a V (circa 570-634). I confini sono continui e restano legati al corpo durante le pose, senza frammenti assegnati faccia per faccia.
- **Ciocche frontali (`build_front_hair`)**: `FrontHair` contiene due ciocche rastremate, tracciate con punti della vista frontale del turnaround e adagiate sull'ellissoide della testa. Ogni percorso viene interpolato e levigato, poi trasformato in una sezione schiacciata; le estremità restano sottili. Le quote sono alzate gradualmente fino a 35 px del concept per compensare la camera, mantenendo leggibili fronte e occhi. Nella stessa mesh una striscia sottile, curva e rastremata segue la sommità del cranio come riga centrale (`HairPart`, #912a2a della palette). Tutta la mesh è parentata all'osso `head`; `SHADOW_HIDE` esclude anche `FrontHair` dalla proiezione a terra. Lo stage `"hair"` sostituisce entrambe le mesh e aggiorna `paint_girl_scalp`.
- **Stato:** aspetto del Player approvato dall'utente, inclusa l'attaccatura. Correzione della divaricazione applicata ai quattro atlanti, con dimensioni e layout invariati. Idle e lancio da ferma identici al pixel in cardinali e diagonali; walk/run aggiornati. Verificata in Godot la nuova andatura nelle 16 combinazioni camminata/corsa × otto direzioni con lancio: atlante corretto, `MovingThrow` visibile, animazione conclusa e rilascio unico sempre al frame 3. Controllato screenshot `walk_down`; nessun nuovo errore rispetto ai TileSet preesistenti. La nuova andatura è ancora da valutare visivamente dall'utente.
- **Passo più raccolto:** in `walk`/`run` abduzione delle cosce Z da ±5° a ±1.5°; rotazione del bacino Y da `7*sin(t)` a `3*sin(t)` per walk e da `9*sin(t)` a `4*sin(t)` per run. La falcata X, le altre articolazioni, i tempi e il layout restano invariati. Distanza laterale massima tra caviglie nelle otto fasi: walk 0.4318 → 0.3266, run 0.4660 → 0.3437 (idle 0.2700, unità del rig). `pose_combo` eredita il passo corretto nei lanci in movimento. `nemica_pipeline.py:walk_e` reimposta esplicitamente Z delle cosce a ±5°: confronto delle rotazioni e posizioni di tutte le ossa in otto fasi identico al precedente.
- Anteprime dell'andatura nella cartella temporanea: `player_gait_comparison.png` (righe: walk prima/dopo, run prima/dopo; otto fasi) e `player_gait_model_preview.png` (idle/walk/run del modello). Aperte in VS Code.

### Ripresa del lavoro condiviso con Claude

Perimetro dell'intervento Codex sul Player, successivo alla ricostruzione avviata da Claude:

| File | Intervento |
| --- | --- |
| `Tools/blender/personaggio_modello.py` | Costume continuo (`apply_girl_suit`, attributi `rest_co`/`suit_arm`, stage `suit`); rilevamento del mento e limite superiore del cranio; classificazione dei riflessi rossi dei capelli; apertura curva della fronte (`paint_girl_scalp`), ciocche e riga centrale (`build_front_hair`). |
| `Tools/blender/blender_pipeline.py` | `build_steps` per eseguire la stessa build in lotti MCP, con `build_all` che ne consuma il generatore; aggiunta di `FrontHair` a `SHADOW_HIDE`. La bocca a due pixel e l'esclusione della chioma `Hair` dall'ombra erano già presenti nel lavoro ripreso e sono state mantenute. |
| `Tools/blender/blender_pipeline.py`, `Tools/blender/nemica_pipeline.py` | Correzione successiva richiesta dall'utente: passo del Player più raccolto in `walk`/`run`, con ripristino esplicito della divaricazione originale in `walk_e` per preservare la nemica. |
| `Tools/blender/personaggio.blend` | Modello, materiali e ciocche aggiornati; salvato in posa idle con palla nascosta. La base `base_personaggio.blend` è preservata. |
| `Assets/Characters/Player/` | Rigenerati `player_spritesheet.png`, `player_moving_throw.png`, `player_diagonals_spritesheet.png`, `player_diagonals_moving_throw.png`. `player_frames.tres`, `Characters/player.tscn` e `Scripts/player.gd` non modificati dall'intervento. |

`concept_model.py` e la ricostruzione regolare del corpo sono il lavoro precedente riutilizzato. Il working tree comprende anche modifiche preesistenti al ragazzo, alle guide e ai concept: **il diff rispetto a HEAD non identifica da solo l'autore delle modifiche**, e non va usato per annullare il lavoro di Claude. Nessun commit eseguito.

Per proseguire le pose, usare il `.blend` corrente e la pipeline, senza ricostruire il corpo approvato. Gli stage `body`/`all` richiedono invece di ripartire da `base_personaggio.blend`: non sono idempotenti sul modello già ricostruito, perché eliminano i seni della base e aggiungono suddivisioni. Non è stata ripetuta una ricostruzione integrale dalla base dopo l'ultima rifinitura dei capelli; l'aspetto attuale, inclusa l'attaccatura, è approvato.

## 9. Errori incontrati e soluzioni

- `bpy.context.object` non esiste nel contesto MCP: usare `bpy.context.temp_override(object=o, active_object=o, ...)` per `mode_set`, `modifier_apply` ecc.; gli operatori `primitive_*_add` non restituiscono l'oggetto: creare la mesh con bmesh (`new_obj(name, build)`).
- Gli oggetti figli di un osso (`parent_type = 'BONE'`) hanno la posizione relativa alla coda dell'osso: lavorare in coordinate mondo (`matrix_world`) e riconvertire; per riparentare senza spostare: `parent_to_bone` (salva e reimposta `matrix_world`).
- Modifiche alle ossa in Edit Mode non deformano la mesh a riposo (l'Armature lavora sulla differenza posa-riposo): si possono spostare ossa e vertici separatamente.
- Una funzione definita dentro un `exec` che chiama sé stessa in un secondo `exec` (override di `stamp_face`) va in ricorsione: tenere il riferimento originale con `globals().get("_stamp_base", stamp_face)` oppure sostituire la funzione per intero.
- File scritti con PowerShell `Set-Content -Encoding UTF8` hanno il BOM e `exec(open(...).read())` fallisce: scrivere con `[IO.File]::WriteAllText(p, t, (New-Object Text.UTF8Encoding($false)))` o con gli strumenti Edit/Write.
- La sfera della testa del modello base ha coordinate locali normalizzate (sfera unitaria) con assi allineati al mondo: utile per regole sulle facce in coordinate locali.
- Le zone colorate per faccia hanno la risoluzione delle facce: per dettagli piccoli suddividere la mesh.
- Un contorno scuro del viso può essere la bocca: per il mento verificare anche la larghezza della pelle subito sotto, non solo il colore centrale (§8).
- In questa sessione `code --reuse-window <immagini>` sotto sandbox ha segnalato un errore Crashpad con accesso negato; l'esecuzione con autorizzazione estesa ha aperto le anteprime. Non è un requisito generale di VS Code: verificare il risultato nel client in uso.

## 10. Anteprime e confronto

- Anteprima sprite: render a `SIZE = 48`, poi ingrandimento nearest dell'array su fondo grigio. Anteprima del modello: `SIZE = 384`, **`ORTHO = 2.2` costante** e `shadow=False`, con `stamp_face` disabilitato solo nel namespace dell'anteprima (il viso a pixel non va timbrato a 384). Scalare anche `ORTHO` manterrebbe la figura piccola invece di ingrandire la stessa inquadratura. Prima della build rieseguire `blender_pipeline.py` in un namespace fresco: ripristina `SIZE = 48` e il vero `stamp_face`.
- **Il turnaround è il riferimento principale** per forme, proporzioni, capelli e costume. Affiancarlo alle viste del modello; lo sprite attuale (`grab()` dell'atlante in `Assets/...`) serve come confronto aggiuntivo.
- **Dopo ogni revisione del modello**, aprire in VS Code sia il render del modello sia lo sprite 2D generato e ingrandito nearest, senza aspettare la build finale e senza chiedere all'utente di cercarli. Anteprime correnti nella cartella temporanea di sistema: `player_model_preview.png` (modello, quattro viste) e `player_sprite_preview.png` (sprite 48x48 ingranditi), entrambe su fondo grigio. Comando: `code --reuse-window <render_modello> <sprite_2d>`.
- Prima di dichiarare finito: vedere le 4 direzioni a 48/64 px e ad alta risoluzione, cercare sbavature (faccette di colore sbagliato, punte, frammenti), simmetria di gambe e viso, distanza degli occhi, bocca leggibile.
- `player_animation_preview.png`, nella stessa cartella temporanea, mostra un campione delle quattro animazioni nelle otto direzioni. Le anteprime sono temporanee e rigenerabili; i sorgenti persistenti sono il `.blend` e gli script nel progetto.
