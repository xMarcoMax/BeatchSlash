# Istruzioni per gli agenti (Codex e Claude Code)

Progetto: **Beatch Slash!**, gioco Godot 4.7 (GDScript). L'utente comunica in italiano.

1. **Prima di qualsiasi intervento leggi `Docs/PROJECT_CONTEXT.md`**: struttura del gioco, vincoli dell'utente, parametri di Player e proiettile, pipeline grafica, stato e prossimi passi.
2. Per sprite e grafica segui **sempre** la sezione "Pipeline grafica e stile visivo" del contesto: Blender (MCP di Blender Lab) con i sorgenti in `Tools/blender/`, Pixelorama 1.2.3 (pixelorama-mcp) per ritocchi ed effetti, stesso stile del Player.
3. Per lavorare sul gioco usa l'MCP **Godot AI** (plugin in `addons/godot_ai`, editor aperto): leggi scene e nodi, modifica, avvia il progetto, controlla log ed errori e fai screenshot per verificare il risultato invece di chiedere all'utente di provarlo.
   - **Strumenti MCP da usare** (nomi dei server): `blender` (Blender aperto con l'add-on attivo), `pixelorama` (Pixelorama 1.2.3 aperto), `godot-ai` (editor Godot aperto con il progetto). Verifica all'inizio che gli strumenti che ti servono siano collegati. Se uno manca o non risponde, **fermati e dillo all'utente** (e come aggiungerlo al tuo client) invece di improvvisare con metodi diversi o rigenerare la grafica a mano.
4. Collisioni e RayCast2D si possono modificare se serve per adattarli alla grafica o al gioco, verificando poi in gioco con Godot AI; non toccare `.vscode/settings.json`; i commit li fa l'utente.
5. Nel progetto restano solo le risorse in uso, senza suffissi di versione: non creare copie `_v2`, `_old` e simili.
6. **A fine intervento aggiorna `Docs/PROJECT_CONTEXT.md`** con cosa è cambiato, approvazioni dell'utente e punti aperti.
