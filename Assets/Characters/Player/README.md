# Player - animazioni V20 approvate

Il giocatore e concluso e approvato dall'utente. Le versioni precedenti e gli strumenti intermedi sono stati eliminati su richiesta.

## Risorse utilizzate dal gioco

- player_spritesheet_v20.png: RGBA 384x768, 8 colonne e 16 righe, celle 48x48. Ordine dei gruppi: Idle, Walk, Dash, Throw; direzioni Nord, Sud, Est, Ovest.
- player_frames.tres: 16 animazioni di 8 frame. Idle 4 FPS, Walk 8 FPS, Dash 12 FPS in loop; Throw 32 FPS una volta.
- player_moving_throw_v20.png: RGBA 384x3072, celle 48x48, 512 pose per lanci durante Walk/Dash. Riga = azione*32 + direzione*8 + fase_del_passo; colonna = frame_del_lancio. Azioni Walk=0/Dash=1, direzioni Nord/Sud/Est/Ovest=0..3.
- Characters/player.tscn usa queste risorse con nearest-neighbor. I file .png.import conservano le impostazioni d'importazione di Godot.

## Comportamento approvato

Rilascio del proiettile al frame indice 4, dopo 0,125 s; durata Throw 0,25 s. Il passo continua durante il lancio mobile e riprende dalla fase corrente. Le corse Nord/Sud hanno una postura inclinata coerente con i profili laterali. Gambe, piedi, braccia e proporzioni sono approvati.

Il Player conserva il suo CharacterBody2D, collision shape e RayCast2D; non modificarli per interventi grafici.

## Strumenti locali

Tools/player_sprites contiene solo preview, controlli e tavole della V20. La cartella Tools e esclusa interamente da Git: non fa parte delle risorse richieste per eseguire il gioco. I generatori storici dipendenti dalle versioni eliminate sono stati rimossi.

Controlli: validate.tscn nel motore Godot e test_preview_timing.cjs con Node. Contesto condiviso aggiornato in .godot/PROJECT_CONTEXT.md.
