# Player - sprite e animazioni (approvati il 10/11/2026)

Sprite generato con Blender (modello 3D chibi + rig 17 ossa) e renderizzato a 48x48 senza anti-aliasing: materiali toon a 4 toni, contorno esterno 1 px #3a1418, occhi disegnati per pixel, ombra a terra. Sorgente: Tools/blender/personaggio.blend (versionato in Git). Script per rigenerare tutto: Tools/blender/blender_pipeline.py (anche dentro il .blend come testo).

## Risorse utilizzate dal gioco

- player_spritesheet.png: RGBA 384x768, 8 colonne e 16 righe, celle 48x48. Gruppi: Idle (6 frame), Walk (8), Dash (8), Throw (8); direzioni Nord, Sud, Est, Ovest.
- player_frames.tres: 16 animazioni (idle/walk/dash/throw _up/_down/_right/_left). Idle 5 FPS, Walk 8 FPS, Dash 12 FPS in loop; Throw 32 FPS una volta.
- player_moving_throw.png: RGBA 384x3072, 512 pose per i lanci durante Walk/Dash. Riga = azione*32 + direzione*8 + fase_del_passo; colonna = frame_del_lancio. Azioni Walk=0/Dash=1, direzioni Nord/Sud/Est/Ovest=0..3.
- Characters/player.tscn: AnimatedSprite2D e MovingThrow con scala (4, 4), filtro nearest, offset (0, -3).

## Ombra

Ogni frame contiene l'ombra a terra: proiezione verticale del corpo (sole a picco), colore #3a1418 con alpha 97/255, disegnata sotto il contorno. Si rimpicciolisce quando i piedi si staccano da terra (corsa).

## Comportamento

Rilascio del proiettile al frame indice 3 (throw_release_frame in player.gd). La palla e visibile in mano nei frame 0-2. Gli ultimi due frame del lancio riportano il busto alla posa base (idle o passo corrente), quindi il ritorno all'animazione base e continuo. Collisioni, raycast e fisica del Player non vanno toccati per interventi grafici.
