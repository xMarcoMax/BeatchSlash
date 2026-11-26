# LMMS per Beatch Slash! — guida operativa

Come si usa LMMS via MCP in questo progetto: collegamento, file, metodo, errori incontrati. Si aggiorna ogni volta che si impara qualcosa. Le lezioni valide in ogni progetto vanno nella guida generica della skill `game-tools` (`C:\Users\stefa\.agent-knowledge\game-tools\references\lmms.md`); qui restano i dettagli e le scelte di Beatch Slash!.

## 1. Strumenti e collegamento

- **LMMS 1.2.2** (`C:\Program Files\LMMS\lmms.exe`) con il server MCP **lmms-mcp 0.9.1** (repo `SarutobiSasuke8/lmms-mcp`, clone al tag `v0.9.1` in `C:\Users\stefa\Documents\Progetti\Repository Online\lmms-mcp`, Node 24, `npm ci` fatto, 82 strumenti). Nome del server: `lmms`.
- **Cartella di lavoro:** `C:\Users\stefa\Documents\Progetti\LMMS Workspace` (variabile `LMMS_WORKSPACE`): progetti `.mmp`, render e export. I nomi dei file sono semplici (minuscole, senza spazi). Da qui i file finali si copiano nel progetto Godot; la cartella non è nel repository del gioco.
- **Registrato in tre client**, ognuno con la sua configurazione: Claude Code (utente, `~/.claude.json`), Codex (`~/.codex/config.toml`, `tool_timeout_sec = 600`) e Claude Desktop (`%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json`). Dopo ogni modifica alla configurazione riavviare il client. Copie di sicurezza delle config originali: `config.toml.bak-lmms` e `claude_desktop_config.json.bak-lmms` accanto agli originali.
- Prima di ogni lavoro: `get_started`. Se il server non risponde, **fermarsi e dirlo all'utente** invece di improvvisare.
- Non aggiornare il clone: resta fissato a `v0.9.1` finché l'utente non decide altrimenti.

## 2. Quando usarlo

- **Musica del gioco** (menu, livello, negozio, game over, stinger di ondata, vittoria) scritta a mano da note, accordi, griglie di batteria e melodie, non generata da un modello. Alternativa generativa: server `music-studio-mcp-for-ace-step`.
- **Effetti sonori costruiti** (stinger, jingle, suoni di interfaccia): LMMS è adatto a quelli musicali o stratificati; per gli effetti in stile retrò è più rapido `bfxr-mcp` (vedi `Docs/BFXR.md`).
- Chi giudica la musica è l'utente: io non sento, misuro (`analyze_audio`) e l'utente ascolta i render e dà le correzioni.

## 3. Metodo

- Un progetto per brano, in `LMMS Workspace`; i loop del gioco si esportano con `export_game_audio` (loop, intro, layer adattivi, stinger, manifest) a circa −16 LUFS.
- Il progetto `.mmp` resta modificabile a mano in LMMS; se l'utente lo ritocca, rileggerlo con `inspect_project` prima di continuare.
- File finali per il gioco: copiati in `Assets/Music/<contesto>/` (già presente `Assets/Music/Menu/`); i sorgenti `.mmp` restano in `LMMS Workspace` finché l'utente non decide dove versionarli.

## 4. Verifica

- Fatto (25/11/2026): il server parte e elenca 82 strumenti; `create_project` (kick a griglia + pluck con melodia, 110 BPM, 2 battute) e `render_mix` producono un WAV stereo 48 kHz (−16,6 LUFS); Claude Code lo vede collegato. File di prova rimossi.
- Fatto (25/11/2026), primo effetto sonoro (lancio della palla di sabbia): progetto `sand_throw.mmp` in `LMMS Workspace`, tre tracce `sample` (soffio `misc/breath01.ogg`, granelli `drums/shaker02.ogg`, colpetto `drums/kick_soft02.ogg`) a 240 BPM, 1 battuta; `render_mix` con `tail: keep`, poi `export_one_shots` → `sand_throw_sfx/sand_throw.wav` (mono 48 kHz, 0,51 s, picco −3 dBFS). Primo giro: il colpetto dava energia sub pari al medio (troppo pesante); volume 55 → 18 e soffio 90 → 110. Non ancora ascoltato dall'utente né collegato al gioco.
- Lancio di sabbia, giudizio dell'utente sul primo giro: «pistola ad aria compressa, pennarello su un foglio, qualcuno che soffia» (colpetto, shaker, soffio). Secondo giro: tre varianti senza soffio/shaker/kick in `LMMS Workspace\sand_throw_sfx_v2\` (`sand_throw_a/b/c.wav`, 0,22–0,29 s, mono, −3 dBFS): crash/hi-hat aperto/rullante smorzato abbassati di 11–21 semitoni e tagliati corti (A e B scure, baricentro 700–850 Hz, con un po' di tonfo grave dal rullante; C più media, senza corpo grave). Esito dell'ascolto: da annotare.
- Fatto (25/11/2026), stinger del game over: l'utente ha scartato più versioni Bfxr («troppo povero», «sembra una kalimba», «voglio un jingle vero, con contorno, più corposo, con il wha wha wha»). Progetto `game_over_stinger.mmp`: 170 BPM, 2 battute, Fa poi Do; sette tracce: `wah_brass` (preset Zyn `Brass/0009-Wah Brass.xiz`, lead, volume 200; melodia `G4:3 r:1 F#4:3 r:1 F4:3 r:1 r:4 E4:7 D#4:1 D4:1 C#4:1 C4:6` a 16 passi per battuta), `strings_pad` (voce `pad`, accordi a blocchi, 50), `uke_chops` (voce `pluck`, accordi `pulse` con `rate` 2, 100), `bass_line` (voce `bass`, figura `syncopated`, 65), `kick` (65), `clap` (90), `hats` (75). Primo render: clip a fondo scala e sub/bassi troppo alti (sub −20 dBFS contro −24 del medio) con il lead sepolto; dopo aver alzato il lead (140 → 200) e abbassato pad, basso e cassa il baricentro è passato da 509 a 836 Hz e il sub da −20 a −28 dBFS. `render_mix` con `targetLufs` −16 e `ceilingDb` −2, `tail: keep` (4,2 s); `export_one_shots` → `game_over_sfx/game_over.wav` (mono 48 kHz, 2,99 s, −3 dBFS), copiato in `Assets/Sfx/game_over.wav`. Esito dell'ascolto: da annotare.
- Da verificare alla prima musica vera: Codex e Claude Desktop dopo il riavvio, effetti, `export_game_audio`, importazione in Godot (loop e tracce sincronizzate).

## 5. Problemi e soluzioni

- `create_project` rifiuta tracce senza `volume` (campo obbligatorio).
- Il Claude Desktop installato da Microsoft Store tiene la configurazione in `%LOCALAPPDATA%\Packages\Claude_*\LocalCache\Roaming\Claude\`, non in `%APPDATA%`.
