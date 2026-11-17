"""Scrive Assets/Tiles/terrain/terrain_tileset.tres per l'atlante prodotto da terrain_gen.py (stesso layout).

TileSet con tile 64x64 (atlante esportato a scala 4), una sola sorgente atlante, un layer fisico (collision_layer 1, come il vecchio
TileSet) e un set di terreno a angoli: 0 Sabbia/Acqua. Collisioni: acqua e battigia (solo la parte d'acqua). Le poligonali sono ricavate dalla stessa costa ideale (senza ondulazione) usata per disegnare le tile.

Uso:  python terrain_tileset_gen.py <percorso del .tres>
"""
import math
import sys

TEX = "res://Assets/Tiles/terrain/terrain_atlas.png"
TILE = 64  # px nel livello (16 px d'arte x 4)
H = TILE / 2
R = TILE / 4  # raggio della costa: 8 px d'arte
CORNERS = [(-H, -H), (H, -H), (H, H), (-H, H)]  # TL, TR, BR, BL; bit = 1, 2, 4, 8
BIT = [1, 2, 4, 8]
PEER = ["top_left_corner", "top_right_corner", "bottom_right_corner", "bottom_left_corner"]


def fmt(pts):
    return "PackedVector2Array(" + ", ".join(f"{round(x, 2):g}, {round(y, 2):g}" for x, y in pts) + ")"


def arc(center, p_from, p_to, n=6):
    """Punti dell'arco di raggio R attorno a center da p_from a p_to (un quarto di cerchio)."""
    a0 = math.atan2(p_from[1] - center[1], p_from[0] - center[0])
    a1 = math.atan2(p_to[1] - center[1], p_to[0] - center[0])
    d = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    return [(center[0] + R * math.cos(a0 + d * i / n), center[1] + R * math.sin(a0 + d * i / n)) for i in range(n + 1)]


def toward(c, other):
    dx, dy = other[0] - c[0], other[1] - c[1]
    n = math.hypot(dx, dy)
    return (c[0] + R * dx / n, c[1] + R * dy / n)


def region_polygons(cfg):
    on = [i for i in range(4) if cfg & BIT[i]]
    n = len(on)
    if n == 0:
        return []
    if n == 4:
        return [list(CORNERS)]
    if n == 1:
        c = CORNERS[on[0]]
        return [[c] + arc(c, toward(c, CORNERS[(on[0] + 1) % 4]), toward(c, CORNERS[(on[0] - 1) % 4]))]
    if n == 3:
        m = [i for i in range(4) if i not in on][0]
        cm = CORNERS[m]
        p1 = toward(cm, CORNERS[(m - 1) % 4])
        p2 = toward(cm, CORNERS[(m + 1) % 4])
        return [[CORNERS[(m + 1) % 4], CORNERS[(m + 2) % 4], CORNERS[(m - 1) % 4], p1] + arc(cm, p1, p2)[1:]]
    if cfg in (5, 10):  # angoli opposti: due dischi
        return [region_polygons(BIT[i])[0] for i in on]
    # due angoli adiacenti: meta' tile
    a, b = on
    if (a, b) == (0, 1):
        return [[CORNERS[0], CORNERS[1], (H, 0), (-H, 0)]]
    if (a, b) == (1, 2):
        return [[CORNERS[1], CORNERS[2], (0, H), (0, -H)]]
    if (a, b) == (2, 3):
        return [[CORNERS[2], CORNERS[3], (-H, 0), (H, 0)]]
    return [[CORNERS[3], CORNERS[0], (0, -H), (0, H)]]  # (0, 3)


def tile_lines(col, row, set_idx=None, terrain=None, peers=None, probability=None, polys=()):
    p = f"{col}:{row}/0"
    out = [f"{p} = 0"]
    if probability is not None:
        out.append(f"{p}/probability = {probability}")
    if set_idx is not None:
        out.append(f"{p}/terrain_set = {set_idx}")
        out.append(f"{p}/terrain = {terrain}")
        for name, t in zip(PEER, peers):
            if t >= 0:
                out.append(f"{p}/terrains_peering_bit/{name} = {t}")
    if polys:
        if len(polys) > 1:
            out.append(f"{p}/physics_layer_0/polygons_count = {len(polys)}")
        for i, poly in enumerate(polys):
            out.append(f"{p}/physics_layer_0/polygon_{i}/points = {fmt(poly)}")
    return out


def build():
    lines = []
    full = [list(CORNERS)]
    # riga 0: sabbia (a..d), sabbia bagnata (a,b), acqua (a..c)
    for col, prob in enumerate([1.0, 0.06, 0.06, 0.05]):
        lines += tile_lines(col, 0, 0, 0, [0, 0, 0, 0], prob)
    lines += tile_lines(4, 0)
    lines += tile_lines(5, 0)
    lines += tile_lines(6, 0, 0, 1, [1, 1, 1, 1], 1.0, full)
    lines += tile_lines(7, 0, 0, 1, [1, 1, 1, 1], 0.5, full)
    lines += tile_lines(8, 0, None, None, None, None, full)  # acqua profonda: solo pittura manuale
    for cfg in range(1, 16):
        c, r = cfg % 4, 1 + cfg // 4
        peers_on = [i for i in range(4) if cfg & BIT[i]]
        # costa: ogni angolo e' sabbia (0) o acqua (1); la tile tutta acqua e' acqua_a (riga 0)
        if cfg < 15:
            peers = [1 if cfg & BIT[i] else 0 for i in range(4)]
            lines += tile_lines(c, r, 0, 1 if len(peers_on) >= 2 else 0, peers, None, region_polygons(cfg))
    return lines


def main(path):
    body = "\n".join(build())
    text = f"""[gd_resource type="TileSet" format=3]

[ext_resource type="Texture2D" path="{TEX}" id="1_atlas"]

[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_terrain"]
texture = ExtResource("1_atlas")
texture_region_size = Vector2i({TILE}, {TILE})
{body}

[resource]
tile_size = Vector2i({TILE}, {TILE})
physics_layer_0/collision_layer = 1
terrain_set_0/mode = 1
terrain_set_0/terrain_0/name = "Sabbia"
terrain_set_0/terrain_0/color = Color(0.96, 0.78, 0.48, 1)
terrain_set_0/terrain_1/name = "Acqua"
terrain_set_0/terrain_1/color = Color(0.12, 0.77, 0.76, 1)
sources/0 = SubResource("TileSetAtlasSource_terrain")
"""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("scritto", path)


if __name__ == "__main__":
    main(sys.argv[1])
