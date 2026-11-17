"""Corregge i pixel di pelle isolati sulla chioma del ragazzo (Assets/Characters/Boyfriend/boyfriend_spritesheet.png).

Nei frame in cui il ragazzo muove la testa (glance, admire, flex) compare, sulla sommita' della testa, un pixel del colore della
pelle circondato dai capelli. Lo script lo sostituisce col colore dei capelli piu' frequente tra i suoi quattro vicini (escluso il
contorno, se ce ne sono altri). Tocca solo pixel opachi dentro la sagoma, quindi alpha, ombra e metadati restano identici.

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
        for y in range(1, CROWN_MAX_Y + 1):
            for x in range(1, 63):
                if not is_skin(cell[y, x]):
                    continue
                near = [cell[y - 1, x], cell[y + 1, x], cell[y, x - 1], cell[y, x + 1]]
                if not all(is_hair(q) for q in near):
                    continue
                colors = Counter(tuple(int(v) for v in q[:3]) for q in near)
                inner = {c: n for c, n in colors.items() if c != OUTLINE}
                new = max(inner or colors, key=(inner or colors).get)
                fixed.append((x0 // 64, y0 // 64, x, y, tuple(int(v) for v in cell[y, x][:3]), new))
                cell[y, x, :3] = new
    print(len(fixed), "pixel corretti")
    if not dry:
        Image.fromarray(img).save(sheet)
    return fixed


if __name__ == "__main__":
    main(sys.argv[1], "--dry-run" in sys.argv)
