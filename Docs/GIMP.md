# GIMP per Beatch Slash! — guida operativa

Come si usa GIMP via MCP in questo progetto: collegamento, ruolo rispetto agli altri strumenti, file, verifiche, errori incontrati. Si aggiorna ogni volta che si impara qualcosa. Le lezioni valide in ogni progetto vanno (in forma generale) anche nella guida generica `C:\Users\stefa\.agent-knowledge\game-tools\references\gimp.md`, da leggere prima di questa. Lo stile grafico vincolante è in `Docs/PROJECT_CONTEXT.md` (sezione "Pipeline grafica e stile visivo").

## 1. Strumenti e collegamento

- **GIMP 3.2.8** (cartella utente `C:\Users\stefa\AppData\Roaming\GIMP\3.2`) con plug-in **gimp-mcp-plugin 0.5.0** (server MCP `gimp`, stesso numero di versione di plug-in e server: `version_ok: true`). Strumenti esposti: 80 (livelli, selezioni, regolazioni, filtri, testo, trasformazioni, esportazioni, `call_api` per Python-Fu).
- **Porta 9890** (non la 9877 predefinita): il client usa `GIMP_MCP_PORT=9890`, uguale a quella di `gimp-mcp.json`.
- GIMP deve essere aperto con il server MCP avviato (Tools > MCP > Start MCP Server, oppure avvio automatico). Prima di ogni lavoro: `check_server`. Se non risponde, **fermarsi e dirlo all'utente** invece di ripiegare su altri metodi.
- Il progetto non ha un'immagine aperta di default: `list_images` può restituire zero immagini.

## 2. Quando usarlo

- **Immagini raster che non sono sprite di personaggio:** loghi, copertine, icone e illustrazioni dell'interfaccia (stile illustrato, non pixel art), sfondi, composizione di più immagini, ritaglio e rimozione di sfondi, correzioni di colore e tono, testo, ridimensionamento ed esportazione in blocco.
- **Immagini create direttamente da GIMP:** `new_canvas`, forme, gradienti, testo, livelli e filtri permettono di costruire un'immagine senza passare da Codex/ImageGen. GIMP non genera immagini con l'IA: per concept art con soggetti disegnati restano ImageGen e i turnaround esistenti; GIMP serve a rifinirli, comporli e portarli alla misura giusta.
- **Sprite e pixel art:** restano Blender (personaggi) e Pixelorama (oggetti, effetti, tile, ritocchi). GIMP non sostituisce Pixelorama nel pixel per pixel. Se si usa GIMP su pixel art, rispettare lo stile: pixel interi, nessun anti-aliasing, nessuna semitrasparenza tranne l'ombra (vedi PROJECT_CONTEXT); evitare filtri che sfumano e controllare i bordi con `get_pixel_color`.

## 3. Metodo

- Dopo ogni modifica `get_state_snapshot` (con `region` per i dettagli) per vedere il risultato senza salvare file.
- `undo`/`redo` non funzionano su GIMP 3.x: salvare un `.xcf` prima dei passi distruttivi (`save_xcf`) e duplicare i livelli invece di modificarli sul posto.
- Sorgenti editabili `.xcf` nella cartella `Tools/gimp/` (versionata; da creare al primo lavoro che ne produce uno). Esportazione con `export_image` (PNG con alpha) nella cartella `Assets/` pertinente; controllare dimensioni e alpha del file esportato, poi `reimport` in Godot.
- Nel progetto restano solo le risorse in uso, senza copie `_v2`/`_old`.

## 4. Verifiche eseguite

- Collegamento: `check_server` (connesso, porta 9890, GIMP 3.2.8, plug-in e server 0.5.0), `get_gimp_info` (Python 3.14 integrato, moduli Gimp/Gegl/Gio disponibili), `list_images` (zero immagini).
- Ciclo di prova su una tela temporanea (chiusa dopo il test, nessun file nel progetto): `new_canvas` 64×64 RGBA `fill: transparent`; `fill_rectangle` 16×16 con `#3a1418`; `get_pixel_color` dentro il quadrato = `#3a1418` alpha 255, fuori e subito fuori dal bordo = alpha 0 (bordi netti, senza anti-aliasing); `export_image` PNG riuscito; `close_image` riuscito.
- Non ancora verificati in questo progetto: `open_image` su un asset esistente, testo, filtri, `save_xcf`, esportazioni multiple e qualsiasi flusso reale di produzione di un'immagine di gioco.

## 5. Errori incontrati

- Nessuno finora.
