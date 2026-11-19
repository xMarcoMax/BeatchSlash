# GIMP per Beatch Slash! — guida operativa

Come si usa GIMP via MCP in questo progetto: collegamento, ruolo rispetto agli altri strumenti, file, verifiche, errori incontrati. Si aggiorna ogni volta che si impara qualcosa. Le lezioni valide in ogni progetto vanno (in forma generale) anche nella guida generica `C:\Users\stefa\.agent-knowledge\game-tools\references\gimp.md`, da leggere prima di questa. Lo stile grafico vincolante è in `Docs/PROJECT_CONTEXT.md` (sezione "Pipeline grafica e stile visivo").

## 1. Strumenti e collegamento

- **GIMP 3.2.8** (cartella utente `C:\Users\stefa\AppData\Roaming\GIMP\3.2`) con plug-in **gimp-mcp-plugin 0.5.0** (server MCP `gimp`, stesso numero di versione di plug-in e server: `version_ok: true`). Strumenti esposti: 80 (livelli, selezioni, regolazioni, filtri, testo, trasformazioni, esportazioni, `call_api` per Python-Fu).
- **Porta 9890** (non la 9877 predefinita): il client usa `GIMP_MCP_PORT=9890`, uguale a quella di `gimp-mcp.json`.
- GIMP deve essere aperto con il server MCP avviato (Tools > MCP > Start MCP Server, oppure avvio automatico). Prima di ogni lavoro: `check_server`. Se non risponde, **fermarsi e dirlo all'utente** invece di ripiegare su altri metodi.
- Il progetto non ha un'immagine aperta di default: `list_images` può restituire zero immagini.

## 2. Quando usarlo

- **Immagini raster che non sono sprite di personaggio:** loghi, copertine, icone e illustrazioni dell'interfaccia (stile illustrato, non pixel art), sfondi, composizione di più immagini, ritaglio e rimozione di sfondi, correzioni di colore e tono, testo, ridimensionamento ed esportazione in blocco.
- **Direzione indicata dall'utente:** in futuro Claude userà GIMP direttamente per ogni immagine del gioco (loghi, sfondi, concept e altro), con Codex/ImageGen solo come punto di riferimento (immagini guida da imitare o confrontare), non come produttore delle immagini finali. Finché non è stata provata su un'immagine di gioco reale, la qualità va verificata con l'utente a ogni passo (anteprime in VS Code).
- **Come si crea un'immagine:** `new_canvas`, forme, gradienti, testo, livelli e filtri, più `call_api` (Python-Fu) per poligoni e curve. GIMP non ha un generatore IA: l'immagine si costruisce a mano, con forme e livelli.
- **Sprite e pixel art:** restano Blender (personaggi) e Pixelorama (oggetti, effetti, tile, ritocchi). GIMP non sostituisce Pixelorama nel pixel per pixel. Se si usa GIMP su pixel art, rispettare lo stile: pixel interi, nessun anti-aliasing, nessuna semitrasparenza tranne l'ombra (vedi PROJECT_CONTEXT); evitare filtri che sfumano e controllare i bordi con `get_pixel_color`.

## 3. Metodo

- Dopo ogni modifica `get_state_snapshot` (con `region` per i dettagli) per vedere il risultato senza salvare file.
- `undo`/`redo` non funzionano su GIMP 3.x: salvare un `.xcf` prima dei passi distruttivi (`save_xcf`) e duplicare i livelli invece di modificarli sul posto.
- Sorgenti editabili `.xcf` nella cartella `Tools/gimp/` (versionata); concept e basi esportate in `Assets/ConceptArt/<soggetto>/` (ignorata da Godot). Esportazione con `export_image` (PNG con alpha) nella cartella `Assets/` pertinente; controllare dimensioni e alpha del file esportato, poi `reimport` in Godot.
- Nel progetto restano solo le risorse in uso, senza copie `_v2`/`_old`.

## 4. File (cartella `Tools/gimp/`)

| File | Contenuto |
| --- | --- |
| `menu_background.xcf` | Scena di spiaggia 960×540 a livelli (sky, sun, sea, sand, palm), scelta dall'utente come punto di partenza per lo sfondo del menù principale e le sue voci. Esportata (appiattita) in `Assets/ConceptArt/MenuBackground/menu_background_base.png`. Non ancora usata nel gioco. |

## 5. Verifiche eseguite

- Collegamento: `check_server` (connesso, porta 9890, GIMP 3.2.8, plug-in e server 0.5.0), `get_gimp_info` (Python 3.14 integrato, moduli Gimp/Gegl/Gio disponibili), `list_images` (zero immagini).
- Ciclo di prova su una tela temporanea (chiusa dopo il test, nessun file nel progetto): `new_canvas` 64×64 RGBA `fill: transparent`; `fill_rectangle` 16×16 con `#3a1418`; `get_pixel_color` dentro il quadrato = `#3a1418` alpha 255, fuori e subito fuori dal bordo = alpha 0 (bordi netti, senza anti-aliasing); `export_image` PNG riuscito; `close_image` riuscito.
- **Scena di prova 960×540** (spiaggia: cielo a gradiente, sole con alone, mare, battigia ondulata a quattro fasce, palma), costruita solo con `gradient_fill`, `fill_ellipse`, `select_ellipse` con `feather`, `fill_selection` e `call_api` (poligoni con `select_polygon` e `edit_fill`), un livello per elemento. Risultato leggibile e pulito, stile vettoriale piatto (non pixel art); salvata fuori dal progetto come prova, non è un asset. Servono molte chiamate per elemento: per soggetti complessi il costo cresce in fretta.
- Non ancora verificati in questo progetto: `open_image` su un asset esistente, testo, filtri, `save_xcf`, esportazioni multiple e qualsiasi flusso reale di produzione di un'immagine di gioco.

## 6. Errori incontrati

- `gradient_fill` ignora l'alpha del colore finale (un `#rrggbb00` diventa opaco): un alone sfumato si ottiene con una selezione ellittica con `feather` riempita con `fill_selection`.
- `select_polygon` con un poligono degenerato (area nulla, per esempio una fronda perfettamente verticale con punti allineati) dà una selezione vuota e il successivo `edit_fill` riempie **tutto il livello**. Controllare `Gimp.Selection.is_empty(image)` prima di riempire.
- Con più immagini aperte `call_api` non ha un'immagine "attiva" ovvia: ricavarla da `Gimp.get_images()` filtrando per dimensioni o nome.
