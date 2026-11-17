"""Ricava le due bande dell'HUD (Assets/UI/band_top.png e band_bottom.png) dalle immagini generate in Assets/ConceptArt/Hud/.

Le immagini del concept sono una striscia di assi su sfondo grigio con quattro chiodi vicino ai lati. Lo script ritaglia la parte
centrale senza chiodi, la ridimensiona all'altezza finale e la ripete in orizzontale specchiando una copia si' e una no, cosi' le
giunzioni non si vedono. La banda finale ha le stesse proporzioni dell'area occupata nell'HUD (1152 x 44 px logici, 3x).

Uso:  python hud_bands_gen.py <radice_del_progetto>
Dipendenze: pillow, numpy.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageEnhance

SCALE = 3
WIDTH, HEIGHT = 1152 * SCALE, 44 * SCALE
CROP_X = (140, 1390)  # tra i chiodi
DARKEN = 0.72  # il legno del concept risultava troppo chiaro nell'HUD


def band(src, dst):
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(int)
    bg = np.median(a[:50, :50].reshape(-1, 3), axis=0)
    rows = np.where(np.abs(a[:, im.width // 2] - bg).sum(1) > 30)[0]
    strip = im.crop((CROP_X[0], rows.min() + 1, CROP_X[1], rows.max()))  # un pixel in meno ai bordi: niente grigio sfumato
    strip = strip.resize((round(strip.width * HEIGHT / strip.height), HEIGHT), Image.LANCZOS)
    strip = ImageEnhance.Brightness(strip).enhance(DARKEN)
    mirrored = strip.transpose(Image.FLIP_LEFT_RIGHT)
    out = Image.new("RGB", (WIDTH, HEIGHT))
    x, flip = 0, False
    while x < WIDTH:
        out.paste(mirrored if flip else strip, (x, 0))
        x, flip = x + strip.width, not flip
    out.save(dst)


if __name__ == "__main__":
    root = sys.argv[1]
    for name in ("band_top", "band_bottom"):
        band(os.path.join(root, "Assets/ConceptArt/Hud", name + ".png"), os.path.join(root, "Assets/UI", name + ".png"))
    print("ok")
