"""Corregge i pixel di pelle isolati sulla chioma del ragazzo (Assets/Characters/Boyfriend/boyfriend_spritesheet.png).

Nei frame in cui il ragazzo muove la testa (glance, admire, flex) compaiono, sulla sommita' della testa, uno o due pixel del
colore della pelle circondati dai capelli. Lo script cerca i gruppi (4-connessi) di al piu' MAX_SPOT pixel di pelle nelle prime
CROWN_MAX_Y righe di ogni cella i cui vicini fuori dal gruppo sono tutti capelli, contorno o trasparenti, e li sostituisce col
colore dei capelli piu' frequente tra quei vicini (escluso il contorno, se ce ne sono altri). Tocca solo pixel opachi dentro la sagoma, quindi alpha, ombra e metadati restano identici.

Va rilanciato dopo ogni rigenerazione dell'atlante da Blender (`build_boyfriend()`), finche' la causa non e' corretta nel modello.

Uso:  python boyfriend_crown_fix.py <radice_del_progetto> [--dry-run]
Dipendenze: pillow, numpy.
"""
import re
import sys
from collections import Counter

import numpy as np
from PIL import Image

OUTLINE = (58, 20, 24)
CROWN_MAX_Y = 12  # sotto questa riga (dentro la cella 64x64) c'e' solo chioma; piu' in basso ci sono viso e orecchie
MAX_SPOT = 4      # un gruppo di pelle piu' grande e' viso, orecchio o attaccatura dei capelli, non un puntino


def is_skin(p):
    r, g, b, a = (int(v) for v in p)
    return a == 255 and r >= 190 and 110 <= g <= 190 and 60 <= b <= 135 and 30 <= r - g <= 110


def is_hair(p):
    r, g, b, a = (int(v) for v in p)
    return a == 255 and ((r, g, b) == OUTLINE or (60 <= r <= 165 and 25 <= g <= 95 and 20 <= b <= 65))


def main(root, dry):
    sheet = f"{root}/Assets/Characters/Boyfriend/boyfriend_spritesheet.png"
    frames = open(f"{root}/Assets/Characters/Boyfriend/boyfriend_frames.tres", encoding="utf-8").read()
    regions = {m.group(1): (int(m.group(2)), int(m.group(3))) for m in re.finditer(
        r'\[sub_resource type="AtlasTexture" id="([^"]+)"\]\n(?:[^\n]*\n)*?region = Rect2\((\d+), (\d+), 64, 64\)', frames)}
    img = np.asarray(Image.open(sheet).convert("RGBA")).copy()
    fixed = []
    for x0, y0 in set(regions.values()):
        cell = img[y0:y0 + 64, x0:x0 + 64]
        seen = set()
        for y in range(1, CROWN_MAX_Y + 1):
            for x in range(1, 63):
                if (x, y) in seen or not is_skin(cell[y, x]):
                    continue
                spot, todo = {(x, y)}, [(x, y)]
                while todo:
                    px, py = todo.pop()
                    for nx, ny in ((px + 1, py), (px - 1, py), (px, py + 1), (px, py - 1)):
                        if (nx, ny) not in spot and 0 <= nx < 64 and 0 <= ny < 64 and is_skin(cell[ny, nx]):
                            spot.add((nx, ny))
                            todo.append((nx, ny))
                seen |= spot
                if len(spot) > MAX_SPOT or max(py for _, py in spot) > CROWN_MAX_Y:
                    continue
                near = [cell[ny, nx] for px, py in spot for nx, ny in ((px + 1, py), (px - 1, py), (px, py + 1), (px, py - 1))
                        if (nx, ny) not in spot]
                if not all(q[3] == 0 or is_hair(q) for q in near):
                    continue
                colors = Counter(tuple(int(v) for v in q[:3]) for q in near if q[3] == 255)
                inner = {c: n for c, n in colors.items() if c != OUTLINE}
                new = max(inner or colors, key=(inner or colors).get)
                for px, py in spot:
                    fixed.append((x0 // 64, y0 // 64, px, py, tuple(int(v) for v in cell[py, px][:3]), new))
                    cell[py, px, :3] = new
    print(len(fixed), "pixel corretti")
    if not dry:
        Image.fromarray(img).save(sheet)
    return fixed


if __name__ == "__main__":
    main(sys.argv[1], "--dry-run" in sys.argv)
