"""Scrive Scenes/tutorial_map.tscn: la mappa del livello tutorial (solo sabbia, battigia e mare), con le tile di Assets/Tiles/terrain/terrain_tileset.tres.

Layout dell'atlante e significato delle configurazioni in Tools/pixelorama/terrain_gen.py (c = bit TL1 TR2 BR4 BL8 dei quattro
angoli di una cella, colonna = c % 4, riga = 1 + c // 4). Le tile si scelgono da una griglia di valori sugli angoli, non con i
terreni di Godot: cosi' non restano celle vuote ai bordi e ogni cella e' decisa qui.

Sistema di coordinate: l'origine della scena e' un angolo di tile e coincide col centro della camera fissa del livello (la scena si
istanzia in quel punto). La mappa va da x=-31 a 30 e da y=-21 a 20 (62x42 tile da 64 px), cioe' 8 tile oltre l'inquadratura
(45x25 tile) per lato.

Uso:  python tutorial_map_gen.py <radice_del_progetto>
"""
import base64
import math
import os
import random
import struct
import sys

X0, X1 = -31, 30   # colonne di celle, estremi inclusi
Y0, Y1 = -21, 20   # righe di celle, estremi inclusi
SOURCE = 0


def water(vx, vy):
    """Baia in alto a destra: tre rettangoli a gradini larghi che escono dai bordi della mappa (la costa non corre mai lungo il bordo)."""
    return (vx >= 12 and vy <= -12) or (vx >= 17 and vy <= -8) or (vx >= 23 and vy <= -5)


def cfg(field, cx, cy):
    return (field(cx, cy) * 1 + field(cx + 1, cy) * 2 + field(cx + 1, cy + 1) * 4 + field(cx, cy + 1) * 8)


# Sabbia: variante 0 liscia (colonna 0, riga 0), 1-3 in riga 0, 4-21 nelle righe 5-6 (vedi terrain_gen.py)
SAND_TILES = [(i, 0) for i in range(4)] + [((i - 4) % 9, 5 + (i - 4) // 9) for i in range(4, 22)]


def sand_variant(rng, sand, cx, cy):
    """Per lo piu' sabbia liscia; un particolare solo se i vicini (sinistra, sopra, diagonali) non ne hanno, e mai la stessa variante."""
    near = [sand.get(k, 0) for k in ((cx - 1, cy), (cx, cy - 1), (cx - 1, cy - 1), (cx + 1, cy - 1))]
    if rng.random() < (0.7 if any(near) else 0.3):
        return 0
    return rng.choice([v for v in range(1, len(SAND_TILES)) if v not in near])


def cells():
    ground = []
    rng = random.Random(7)
    sand = {}  # variante di sabbia scelta per cella
    for cy in range(Y0, Y1 + 1):
        for cx in range(X0, X1 + 1):
            c = cfg(water, cx, cy)
            if c == 0:
                v = sand_variant(rng, sand, cx, cy)
                sand[(cx, cy)] = v
                ground.append((cx, cy) + SAND_TILES[v])
            elif c == 15:
                ground.append((cx, cy, 6 + rng.choices([0, 1], weights=[7, 3])[0], 0))
            else:
                assert c not in (5, 10), f"costa diagonale in ({cx},{cy})"
                ground.append((cx, cy, c % 4, 1 + c // 4))
    return ground


def encode(entries):
    data = bytearray(b"\x00\x00")  # versione del formato dei dati
    for x, y, ax, ay in entries:
        data += struct.pack("<6h", x, y, SOURCE, ax, ay, 0)
    return base64.b64encode(bytes(data)).decode()


def main(root):
    ground = cells()
    text = f"""[gd_scene format=4]

[ext_resource type="TileSet" path="res://Assets/Tiles/terrain/terrain_tileset.tres" id="1_tileset"]

[node name="TutorialMap" type="Node2D"]

[node name="Ground" type="TileMapLayer" parent="."]
texture_filter = 1
tile_map_data = PackedByteArray("{encode(ground)}")
tile_set = ExtResource("1_tileset")

"""
    path = os.path.join(root, "Scenes", "tutorial_map.tscn")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    water_cells = sum(1 for e in ground if e[3] == 0 and e[2] in (6, 7))
    print("scritto", path, "- ground", len(ground), "acqua", water_cells)


if __name__ == "__main__":
    main(sys.argv[1])
