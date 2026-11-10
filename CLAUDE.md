# Istruzioni per Claude Code

Progetto: **Beatch Slash!**, gioco Godot 4.7 (GDScript). L'utente comunica in italiano.

1. **Prima di qualsiasi intervento leggi `Docs/PROJECT_CONTEXT.md`**: struttura del gioco, vincoli dell'utente, parametri di Player e proiettile, pipeline grafica, stato e prossimi passi.
2. Per sprite e grafica segui **sempre** la sezione "Pipeline grafica e stile visivo" del contesto: Blender (MCP di Blender Lab) con i sorgenti in `Tools/blender/`, Pixelorama 1.2.3 (pixelorama-mcp) per ritocchi ed effetti, stesso stile del Player.
3. Non modificare CollisionShape2D, RayCast2D e relativo codice per interventi grafici; non toccare `.vscode/settings.json`; i commit li fa l'utente.
4. Nel progetto restano solo le risorse in uso, senza suffissi di versione: non creare copie `_v2`, `_old` e simili.
5. **A fine intervento aggiorna `Docs/PROJECT_CONTEXT.md`** con cosa e cambiato, approvazioni dell'utente e punti aperti.
