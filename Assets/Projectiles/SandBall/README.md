# Palla di sabbia (approvata il 10/11/2026)

- sand_ball.png: RGBA 96x48, 4 colonne x 2 righe, celle 24x24. Riga 1 volo (palla che ruota + granelli dietro). Riga 2 impatto rivolto verso il nemico (+x, direzione di volo): la palla si schiaccia sul bersaglio, la sabbia resta spiaccicata sul punto di contatto e gli schizzi rimbalzano indietro e di lato. Frame d'impatto simmetrici rispetto all'asse orizzontale.
- sand_ball_frames.tres: flight 4 frame 12 FPS loop, impact 4 frame 26 FPS una volta.
- Stile identico al Player: palette sabbia a 4 toni #8a6a3e #b8925a #e3c084 #f6e2b0, contorno 1 px #3a1418, nessun anti-aliasing, luce dall'alto a sinistra. Il granello di coda sta a sinistra (-x) perché il proiettile ruota verso la direzione di lancio (transform.x).
- Objects/projectiles.tscn: AnimatedSprite2D con scale (2, 2); il proiettile eredita già scala 2 dal RayCast2D del Player, quindi ogni pixel risulta 4x come quelli del Player.
- Scripts/projectiles.gd imposta flip_v quando il lancio va verso sinistra (nodo ruotato ~180 gradi), così la luce resta dall'alto in ogni direzione.
