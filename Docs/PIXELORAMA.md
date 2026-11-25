# Pixelorama per Beatch Slash! — guida operativa

Come si usa Pixelorama via MCP in questo progetto: installazione, metodo di disegno, file, errori incontrati. Si aggiorna ogni volta che si impara qualcosa. Le lezioni valide in ogni progetto vanno (in forma generale) anche nella guida generica `C:\Users\stefa\.agent-knowledge\game-tools\references\pixelorama.md`, da leggere prima di questa. Lo stile grafico vincolante è in `Docs/PROJECT_CONTEXT.md` (sezione "Pipeline grafica e stile visivo").

## 1. Strumenti e collegamento

- **Pixelorama 1.2.3** (NON 1.2.4: l'estensione richiede l'API 9) con estensione **pixelorama-mcp** (github.com/CyberIce2077/pixelorama-mcp, server `node <repo>\dist\index.js`, porta 7651). Nome atteso del server MCP: `pixelorama`. Pixelorama deve essere aperto; se lo strumento non risponde, dirlo all'utente.
- Strumenti: `get_project`, `open_file` (.pxo o immagini), `new_project`, `read_pixels` (griglia di caratteri + palette, max 16384 px per chiamata), `draw_pixels`, `fill_rect`, `clear_cel`, `add_layer`, `add_frame`, `select_cel`, `get_image` (anteprima ingrandita nearest), `export_png` (frame o tutti i frame affiancati), `save_project`.

## 2. Quando usarlo

- Oggetti piccoli, effetti, icone (es. puff, caduta della palla di sabbia): disegnati interamente qui.
- **Personaggi: solo ritocchi dello sprite ottenuto da Blender, dentro la silhouette** (ciocche, viso, dettagli del costume, linee muscolari leggere col tono d'ombra della pelle). Le correzioni di forma e proporzione si riportano nel modello Blender (vedi `Docs/BLENDER.md`): ridisegnare a mano la silhouette vista per vista rende le direzioni incoerenti (N/S ed E/O sembrano persone diverse) e non si trasferisce agli altri frame delle animazioni.
- Per i concept basta ImageGen con i turnaround esistenti come riferimento; Pixelorama serve solo per ritocchi o pixel art.

## 3. Metodo di disegno

- `draw_pixels(x, y, rows, palette)`: ogni stringa di `rows` è una riga a partire da (x, y); ogni carattere è cercato in `palette`. I caratteri non in palette (es. `.`) lasciano il pixel invariato: usare `.` per "non toccare" e una lettera mappata a `"transparent"` (es. `t`) per cancellare. **Attenzione agli spazi** dentro le stringhe: non sono in palette, quindi lasciano il pixel com'era (residui di contorno).
- Contare sempre la lunghezza delle righe: una riga più corta o più lunga sposta il bordo destro. Per griglie lunghe conviene generarle con uno script (come `Tools/pixelorama/puff_gen.py`) e controllare le lunghezze.
- Prima di ritoccare: `read_pixels` della zona (palette con i colori presenti) per conoscere coordinate di contorni, occhi, orecchie ecc.; dopo: `get_image` con `scale` 8 per controllare l'insieme.
- Ombra semitrasparente dei personaggi: colore `#3a141861` (#3a1418 con alpha 97/255); sotto i piedi usare questo colore al posto della trasparenza per non bucare l'ombra.
- Lo shading segue la luce dall'alto a sinistra anche nelle viste specchiate: specchiare una vista laterale per ottenere l'altra inverte la luce e la pettinatura (es. la riga dei capelli); va valutato caso per caso.

## 4. File (cartella `Tools/pixelorama/`, versionata)

| File | Contenuto |
| --- | --- |
| `puff.pxo`, `puff_gen.py` | Nuvoletta del puff della nemica (6 frame 32x32, palette sabbia #fff6e8 #f6e2b0 #e3c084, contorno #3a1418); lo script genera le griglie da incollare con `draw_pixels`. Esportato in `Assets/Effects/Puff/puff.png`. |
| `sand_ball_land.pxo`, `sand_ball_land_gen.py` | Caduta della palla di sabbia (8 frame 24x24). Esportato in `Assets/Projectiles/SandBall/sand_ball_land.png`. |
| `boyfriend.pxo` | Ritocco a mano di un modello del ragazzo ormai superato: non usarlo come base. |

## 5. Errori incontrati

- L'ambiente Python del progetto `.sprite-tools-env` è ricreato con il Python di sistema 3.14 (Pillow e NumPy installati): `.sprite-tools-env/Scripts/python.exe` per gli script di `Tools/`. Se l'interprete cambia di nuovo e l'ambiente non parte: `python -m venv --clear .sprite-tools-env` e `pip install pillow numpy`.
- Pixel orfani dopo un ritocco (vecchi contorni fuori dalla nuova silhouette): cercarli con `get_image` e cancellarli con `fill_rect` `transparent`.

## 6. Ispezione della nemica dal concept

- Pixelorama 1.2.3 collegato via MCP; aperti il render di prova e `Assets/Characters/Enemy/enemy_spritesheet.png` (768x2048, celle 64x64) per ispezione. `read_pixels` ha confermato palette e timbri di occhi/bocca nel render.
- Tutte le correzioni condivise tra direzioni e frame sono nei sorgenti Blender: fronte e ciocche, volumi, bikini e passo. Nessun ritocco raster persistente e nessun nuovo `.pxo`; per rigenerare usare `Docs/BLENDER.md` §11.
## 7. Ispezione del negoziante

Pixelorama1.2.3/MCP collegato: aperto `Assets/Objects/Shop/shopkeeper.png` (2560×480, celle160×160) e letta una regione25×25 della prima posa con read_pixels. L'atlante contiene idle e due gesti su tre righe; l'edificio statico è separato. Nessun ritocco raster e nessun nuovo .pxo: geometria, volto e gesti sono riproducibili da `Tools/blender/shop_pipeline.py` e `shop.blend`. La composizione con tetto/tenda/bancone e la leggibilità finale sono verificate in Blender e Godot; Pixelorama mostra qui il solo livello del negoziante.
## 8. Atlante del terreno (tile 16×16 da concept)

- **Procedura usata:** ritagliando i campioni del concept di ImageGen (box ricavati dalle righe/colonne vuote dell'immagine) e riducendoli a 16×16 con media d'area si ottengono tile leggibili, ma i campioni non combaciano tra loro: nuvolette di sabbia tagliate ai bordi, costa che attraversa il bordo a quote diverse. Per questo `Tools/pixelorama/terrain_gen.py` usa il concept solo per palette, spessori e aspetto, e **calcola** le tile: costa che passa sempre per il punto medio dei bordi (distanza con segno da un cerchio o da un semipiano, con ondulazione nulla agli estremi) e riempimenti periodici. Palette fissa di circa 20 colori (4 toni per materiale, contorno #3a1418): una quantizzazione k-means libera dava 6 sabbie quasi uguali e contorni di colori diversi.
- **Flusso con Pixelorama:** lo script scrive l'atlante a 16 px/tile (144×80); `open_file` lo apre, `save_project` in `Tools/pixelorama/terrain.pxo`, `export_png` con `scale: 4` produce `Assets/Tiles/terrain/terrain_atlas.png` (576×320). Confronto pixel per pixel con l'uscita dello script: nessuna differenza, alpha solo 0/255. Dopo ogni rigenerazione ripetere apertura, salvataggio ed esportazione e fare un `reimport` in Godot.
- **Dipendenze dello script:** Python di sistema 3.14 con pillow e numpy (oggi anche nell'ambiente `.sprite-tools-env`, ricreato). Uso: `python Tools/pixelorama/terrain_gen.py <cartella_di_uscita>`; lo script scrive anche `terrain_preview.png`, una mappa di prova per controllare le giunzioni.
- **Ritocchi a mano:** modificare l'atlante in Pixelorama vale solo finché non si rigenera dallo script; per conservare un ritocco, riportarlo nello script.

Aggiornamento 17/11/2026: l'atlante non contiene più scogli ed erba (richiesta dell'utente: saranno sprite), ma solo sabbia, sabbia bagnata, acqua e costa; 9×5 tile, 144×80 px a 16 px/tile, 576×320 dopo l'esportazione a scala 4. Ricaricato in Pixelorama (`open_file`), salvato in `terrain.pxo` e riesportato con `export_png` `scale: 4`.

Aggiornamento 18/11/2026: atlante 9×7 (righe 5-6 = sabbia extra, 22 varianti totali; 144×112 px, 576×448 esportato). Python con pillow e numpy: l'ambiente `.sprite-tools-env` era rotto e si è ricreato con `python -m venv --clear` e `pip install pillow numpy`. Il confronto atlante esportato/uscita dello script è a zero pixel diversi.

## 9. Pixel di pelle isolato sulla chioma del ragazzo

- **Sintomo (segnalato dall'utente):** quando il ragazzo muove la testa (animazioni glance, admire, flex, anche le viste di schiena) compare in cima alla testa un puntino del colore della pelle (`#f8b47a`, `#e99d63`, `#c97847`) in mezzo ai capelli.
- **Ricerca:** nessuna componente connessa isolata (anche con 4-connessione), quindi non è un pixel staccato dalla sagoma. Si trova cercando, in ogni cella 64×64 e nelle prime 12 righe (la chioma), i pixel con colore di pelle i cui quattro vicini sono tutti capelli o contorno (`#3a1418`, `#6b3a26`, `#9b573b`, `#4d2a1e`...). Nelle righe più in basso quel criterio prende orecchie e sopracciglia, che sono legittime.
- **Correzione:** `Tools/pixelorama/boyfriend_crown_fix.py` (pillow, numpy) rimpiazza ognuno di quei pixel con il colore di capelli più frequente tra i suoi vicini (escluso il contorno). Corretti **160 pixel** in `boyfriend_spritesheet.png`; confronto prima/dopo: 160 pixel diversi, alpha identico ovunque, nessun'altra modifica. Reimport in Godot senza errori.
- **Seconda segnalazione dell'utente** ("puntino rosa sopra i capelli in alcuni movimenti"): restavano **54 pixel** di pelle in gruppi da 1 o 2 pixel (orizzontali) nelle righe 6-12 di 24 celle; il criterio dei quattro vicini non li prendeva perché due pixel di pelle affiancati sono vicini l'uno dell'altro. Lo script ora cerca i gruppi 4-connessi di al massimo `MAX_SPOT` (4) pixel di pelle nelle prime `CROWN_MAX_Y` righe, con tutti i vicini esterni capelli, contorno o trasparenti, e li riempie col colore di capelli più frequente tra i vicini (escluso il contorno). Verificato: 54 pixel diversi, alpha identico, nessun'altra modifica; confronto visivo prima/dopo su 16 celle (viso, orecchie e attaccatura dei capelli intatti); reimport senza errori; ricontrollo dopo la correzione: 0 pixel da correggere.
- **Attenzione:** la causa sta nel modello Blender (un'isola di materiale pelle sulla chioma); rigenerando l'atlante con `build_boyfriend()` i pixel ricompaiono, quindi dopo ogni rigenerazione rilanciare lo script (`python Tools/pixelorama/boyfriend_crown_fix.py <radice>`, con `--dry-run` per solo contare) finché non si corregge il materiale nel modello.

## 10. Atlante degli elementi di scena (props)

- `Tools/pixelorama/props_gen.py` (pillow, numpy; stesso metodo di `terrain_gen.py`) disegna a codice tutti i props in pixel d'arte: primitive (ellissi, poligoni, tratti a larghezza variabile, foglie a bezier con denti e bordo scuro sopra le foglie già disegnate), 4 toni per materiale dalla stessa palette del resto, luce in alto a sinistra, contorno esterno #3a1418 aggiunto automaticamente, ombra a terra calcolata proiettando il corpo in basso a destra (alpha 97). Le varianti escono da parametri e semi fissi (colori, ribaltamento, inclinazione, disegni delle tavole). Per le tavole da surf ogni pixel è calcolato da coordinate (u lungo la tavola, v di traverso) e quindi ruota senza scalettature; la calotta degli ombrelloni è una cupola a spicchi con luce per spicchio.
- Flusso con Pixelorama: lo script scrive `props_atlas.png` (art a 1 px, impaccato in righe con 2 px di margine) e `props.json`; `open_file` → `save_project` in `Tools/pixelorama/props.pxo` → `export_png` con `scale: 1` in `Assets/Props/props_atlas.png`. Il confronto con l'uscita dello script dà alpha identico e RGB identico sul corpo; i pixel d'ombra (alpha 97) escono con il verde di 1 diverso (#391418 al posto di #3a1418), irrilevante perché Godot li separa per alpha.
- Ogni apertura con `open_file` aggiunge una scheda a Pixelorama: prima di `save_project` ed `export_png` verificare che quella corrente sia il file appena aperto (il risultato lo dice).
- Ambiente Python: `.sprite-tools-env` è ricreato con il Python 3.14 di sistema; se si rompe di nuovo, `python -m venv --clear .sprite-tools-env` e `pip install pillow numpy`.
- Lezioni di stile: foglie e fronde vanno disegnate a strati (dietro scuro, davanti chiaro) con un bordo scuro sopra le sottostanti, altrimenti diventano una macchia; una chioma di palma resta leggibile con fronde ad arco che cadono e denti sul bordo; il tronco deve partire verticale dalla base (curva cubica) perché il ciuffo d'erba resti allineato; una tela chiara degli ombrelloni con tono scuro marrone sembra sporca: usare una palette di crema dedicata più chiara.
- Animazioni nell'atlante dei props: i fotogrammi (`shell_crab_0..3`) devono avere la stessa cella e lo stesso punto d'appoggio, altrimenti l'animazione salta: `pack()` li riempie alla dimensione massima prima dell'impaccamento. Il granchio cambia solo chele (alzate/aperte con un pixel scuro) e occhi (steli alzati di 1 px).

## 11. Cuoricini della scenetta di game over

- `Tools/pixelorama/kiss_heart.pxo` (11×10) e `small_heart.pxo` (7×6) disegnati a mano con `draw_pixels` (palette: contorno #3a1418, ombra #a8243f, base #e8436a, luce #ff8fab, riflesso #fff6e8; luce in alto a sinistra) ed esportati a scala 1 in `Assets/Effects/Hearts/`. In gioco sono scalati ×4 come i personaggi; volo, scoppio e dissolvenza sono tween nel codice, quindi un solo frame per cuore.
- `export_png` fallisce con "File not found" se la cartella di destinazione non esiste: crearla prima.
- Non esiste uno strumento per cambiare scheda: per esportare un progetto aperto prima di un altro si riapre il suo `.pxo` con `open_file` (diventa la scheda corrente).
