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

- L'ambiente Python del progetto `.sprite-tools-env` punta a un interprete non più presente (`python314` mancante): per calcoli su immagini usare il Python di Blender (numpy disponibile) oppure riparare l'ambiente.
- Pixel orfani dopo un ritocco (vecchi contorni fuori dalla nuova silhouette): cercarli con `get_image` e cancellarli con `fill_rect` `transparent`.

## 6. Ispezione della nemica dal concept

- Pixelorama 1.2.3 collegato via MCP; aperti il render di prova e `Assets/Characters/Enemy/enemy_spritesheet.png` (768x2048, celle 64x64) per ispezione. `read_pixels` ha confermato palette e timbri di occhi/bocca nel render.
- Tutte le correzioni condivise tra direzioni e frame sono nei sorgenti Blender: fronte e ciocche, volumi, bikini e passo. Nessun ritocco raster persistente e nessun nuovo `.pxo`; per rigenerare usare `Docs/BLENDER.md` §11.
## 7. Ispezione del negoziante

Pixelorama1.2.3/MCP collegato: aperto `Assets/Objects/Shop/shopkeeper.png` (2560×480, celle160×160) e letta una regione25×25 della prima posa con read_pixels. L'atlante contiene idle e due gesti su tre righe; l'edificio statico è separato. Nessun ritocco raster e nessun nuovo .pxo: geometria, volto e gesti sono riproducibili da `Tools/blender/shop_pipeline.py` e `shop.blend`. La composizione con tetto/tenda/bancone e la leggibilità finale sono verificate in Blender e Godot; Pixelorama mostra qui il solo livello del negoziante.
## 8. Atlante del terreno (tile 16×16 da concept)

- **Procedura usata:** ritagliando i campioni del concept di ImageGen (box ricavati dalle righe/colonne vuote dell'immagine) e riducendoli a 16×16 con media d'area si ottengono tile leggibili, ma i campioni non combaciano tra loro: nuvolette di sabbia tagliate ai bordi, costa che attraversa il bordo a quote diverse. Per questo `Tools/pixelorama/terrain_gen.py` usa il concept solo per palette, spessori e aspetto, e **calcola** le tile: costa che passa sempre per il punto medio dei bordi (distanza con segno da un cerchio o da un semipiano, con ondulazione nulla agli estremi) e riempimenti periodici. Palette fissa di circa 20 colori (4 toni per materiale, contorno #3a1418): una quantizzazione k-means libera dava 6 sabbie quasi uguali e contorni di colori diversi.
- **Flusso con Pixelorama:** lo script scrive l'atlante a 16 px/tile (192×80); `open_file` lo apre, `save_project` in `Tools/pixelorama/terrain.pxo`, `export_png` con `scale: 4` produce `Assets/Tiles/terrain/terrain_atlas.png` (768×320). Confronto pixel per pixel con l'uscita dello script: nessuna differenza, alpha solo 0/255. Dopo ogni rigenerazione ripetere apertura, salvataggio ed esportazione e fare un `reimport` in Godot.
- **Dipendenze dello script:** Python di sistema 3.14 con pillow e numpy installati in una cartella temporanea (`pip install --target <cartella> pillow numpy`, poi `PYTHONPATH=<cartella>`). L'ambiente `.sprite-tools-env` resta non funzionante. Uso: `python Tools/pixelorama/terrain_gen.py <cartella_di_uscita>`; lo script scrive anche `terrain_preview.png`, una mappa di prova per controllare le giunzioni.
- **Ritocchi a mano:** modificare l'atlante in Pixelorama vale solo finché non si rigenera dallo script; per conservare un ritocco, riportarlo nello script.
