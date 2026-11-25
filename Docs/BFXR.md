# Bfxr per Beatch Slash! — guida operativa

Come si usa Bfxr via MCP in questo progetto: collegamento, file, metodo, errori incontrati. Si aggiorna ogni volta che si impara qualcosa. Le lezioni valide in ogni progetto vanno nella guida generica della skill `game-tools` (`C:\Users\stefa\.agent-knowledge\game-tools\references\bfxr.md`); qui restano i dettagli e le scelte di Beatch Slash!.

## 1. Strumenti e collegamento

- **Bfxr App** dell'utente (`C:\Users\stefa\Documents\Progetti\Bfxr`: app Electron, server MCP `mcp/`, launcher) attorno al clone di increpare/bfxr2 in `C:\Users\stefa\Documents\Progetti\Repository Online\bfxr2` (commit del 18/11/2026). Server MCP `bfxr-mcp` (`node …\Bfxr\mcp\src\index.js`), registrato in Claude Code, Codex e Claude Desktop. L'app non deve essere aperta perché l'MCP funzioni.
- **Cartella dei suoni:** `C:\Users\stefa\Documents\Bfxr Sounds` (chiave `sounds_dir` di `Bfxr\config.json`, riletta a ogni chiamata; cambia anche dal menu Output dell'app). Contiene solo `.wav`; sorgenti `.bfxr` e immagini di analisi vanno in `Bfxr\mcp\.data\`. Uscita: WAV 44100 Hz, 16 bit, mono.
- 23 sintetizzatori (elenco e preset con `list_synths`). Prima di lavorare: `bfxr_status`. Se non risponde, **fermarsi e dirlo all'utente**.
- Regole del progetto Bfxr App: nomi camelCase inglesi di massimo 4 parole, solo lettere; varianti numerate; mai sovrascrivere; analizzare sempre i suoni generati; mai riprodurre audio. Non modificare il clone di bfxr2.

## 2. Quando usarlo

- **Effetti sonori del gioco in stile arcade e stilizzati:** lancio e impatto della palla di sabbia, colpo alla nemica, monete e acquisto al negozio, conferme e rifiuti dell'interfaccia, passi sulla sabbia (`Footsteppr`), stinger brevi (`Jinglr`).
- Per musica e per suoni musicali o stratificati si usa `lmms` (`Docs/LMMS.md`).
- Chi giudica il suono è l'utente: io leggo le metriche e l'immagine, l'utente ascolta i WAV e cancella quelli che non vuole.

## 3. Metodo

- `generate_sound` con 3–5 varianti (di default 4), poi si presentano solo le migliori con una descrizione breve; si raffina con `mutate_sound` o con i parametri (`list_parameters`).
- I suoni scelti si copiano nella cartella audio del progetto Godot (da definire alla prima aggiunta) con un nome che descrive l'effetto; la cartella `Bfxr Sounds` resta lo spazio di prova.

## 4. Verifica

- Fatto (25/11/2026): `bfxr_status`, `list_synths` e `generate_sound` (Bfxr/`pickup_coin`, 1 variante, seed 1, `open_folder` falso, `output_dir` fuori dalla cartella dei suoni): WAV da 0,385 s con metriche e immagine; i file di prova sono stati rimossi.
- Fatto (25/11/2026), lancio della palla di sabbia dopo il fallimento di LMMS (le tre versioni con campioni stock sono state giudicate «fanno schifo»; per gli effetti sonori si parte da Bfxr): `generate_sound` con Transfxr/`sand_sprays` (4 varianti, seed 100, 0,19–0,29 s, attacco 0–10 ms, decadimento rapido) e Whooshr/`cloth_swipe` (3 varianti, seed 200, 0,36–0,64 s, attacco lento 108–223 ms, molto brillante). WAV in `C:\Users\stefa\Documents\Bfxr Sounds` (`sandThrowSpray1–4.wav`, `sandThrowSwipe1–3.wav`). Esito dell'ascolto: `sandThrowSwipe2` giudicata la migliore, ma migliorabile. Parametri di partenza (preset `cloth_swipe`): `seed` 0,5226, `duration` 0,359, `size` 0,447, `air` 0,676, `whistle` 0,037, `movement` 0,297, `focus` 0,511, `flutter` 0,642. Rifacimenti con `seed` Whooshr fisso: `sandSwipeDark` (`size` 0,65, `air` 0,6, `whistle` 0, `flutter` 0,75: baricentro 3915 Hz contro 4922), `sandSwipeGrain` (`focus` 0,75, `flutter` 0,9, 0,3 s: resta molto brillante, 4888 Hz), `sandSwipeDarkGrain` (misto: 4183 Hz). Esito dell'ascolto: le tre varianti sembrano uguali all'orecchio dell'utente (i cambi di `size`/`air` misurati non si sentono); scelta `sandSwipeGrain` come suono del lancio. Consegna: silenzio iniziale (43 ms) e coda tagliati con uno script Python inline (soglia −48 dB), picco a −3 dBFS, copiato in `Assets/Sfx/sand_throw.wav` e collegato in `player.gd` (`ThrowSound`, vedi `CODE_MAP.md` sezione 8). Test in gioco da parte dell'utente: suono approvato («mi piace»). Varianti: richieste dall'utente per non avere sempre lo stesso suono. Ho rigenerato la stessa Whooshr cambiando solo il parametro `seed` (0,2 / 0,45 / 0,8; `sandGrainOne/Two/Three.wav`): misure quasi uguali (baricentro 4,7–4,9 kHz, attacco 81–101 ms), cioè stesso carattere con grana e inviluppo diversi. Preparate con `trim_normalize_wav.py` e raggruppate in un `AudioStreamRandomizer` (dettagli in `CODE_MAP.md`). Ascolto delle varianti: da annotare.
- Da verificare alla prima sessione vera: `mutate_sound`, `mix_sounds`, `load_sound`, `analyze_sound`, importazione dei WAV in Godot.

## 5. Problemi e soluzioni

- Con `output_dir` diverso dalla cartella dei suoni, il WAV va lì ma `.bfxr` e PNG di analisi restano in `Bfxr\mcp\.data\`: da ripulire a mano se il suono era solo una prova.
