"""Genera l'atlante del terreno (tile 16x16 pixel d'arte) dal concept Assets/ConceptArt/Terrain/terrain_concept.png.

Colori, spessori di schiuma/sabbia bagnata/contorno e aspetto delle texture vengono dal concept; la geometria e' calcolata
per essere sempre combaciante: ogni costa passa per il punto medio dei bordi della tile e li attraversa in perpendicolare,
quindi due tile vicine qualsiasi (16 configurazioni "a angoli") si uniscono senza scatti. Le texture di riempimento sono
periodiche (toroidali), quindi non mostrano giunzioni.

Uso:  python terrain_gen.py <cartella_di_uscita>
Scrive terrain_atlas.png (16 px/tile), terrain_atlas_x4.png (64 px/tile, nearest) e terrain_preview.png (mappa di prova).
Dipendenze: pillow, numpy (nel Python di sistema: pip install pillow numpy).

Layout (col, riga) dell'atlante, 12 x 5 tile:
  riga 0: sabbia a..d (0-3), sabbia bagnata a,b (4-5), acqua a..c (6-8)
  righe 1-4: blocco costa  (col 0-3)  sabbia/acqua, configurazione c in col = c % 4, riga = 1 + c // 4
             blocco scoglio (col 4-7)  roccia su trasparente
             blocco erba    (col 8-11) erba su trasparente
  configurazione c = bit TL=1, TR=2, BR=4, BL=8 (angolo "dentro" la regione: acqua/roccia/erba).
"""
import math
import os
import sys

import numpy as np
from PIL import Image

T = 16
OUT = "#3a1418"
PAL = {
    "OUT": OUT,
    # sabbia (4 toni) e sabbia bagnata
    "S0": "#d29c58", "S1": "#e7b269", "S2": "#f4c77a", "S3": "#fcd993",
    "D0": "#a8754a", "D1": "#c08c58",
    # acqua (4 toni) e schiuma
    "W0": "#0b9ca8", "W1": "#1fc5c3", "W2": "#4fdcd0", "W3": "#9ceee6", "F": "#fafcfb",
    # roccia
    "R0": "#7a5069", "R1": "#9c6b7c", "R2": "#ef9c5c", "R3": "#f8b878",
    # erba
    "G0": "#3f7a1c", "G1": "#549920", "G2": "#8fc01e", "G3": "#b5da3a",
}


def rgba(key):
    if key is None:
        return (0, 0, 0, 0)
    h = PAL[key].lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


CORNERS = {1: (0, 0), 2: (T, 0), 4: (T, T), 8: (0, T)}  # TL, TR, BR, BL (coordinate dell'angolo)
R = T / 2


def wobble(amps, t):
    """Spostamento della costa in pixel; nullo a t=0 e t=1 (estremi) cosi' combacia con le tile vicine."""
    return sum(a * math.sin(math.pi * (k + 1) * t) for k, a in enumerate(amps))


def disc_s(cx, cy, x, y, amps):
    ang = math.atan2(abs(y - cy), abs(x - cx))  # 0..pi/2 dentro la tile
    return R - math.hypot(x - cx, y - cy) + wobble(amps, ang / (math.pi / 2))


def region_s(cfg, x, y, amps):
    """Distanza con segno dalla costa: positiva dentro la regione (acqua/roccia/erba)."""
    on = [b for b in (1, 2, 4, 8) if cfg & b]
    n = len(on)
    if n == 0:
        return -99.0
    if n == 4:
        return 99.0
    if n == 1:
        cx, cy = CORNERS[on[0]]
        return disc_s(cx, cy, x, y, amps)
    if n == 3:
        miss = [b for b in (1, 2, 4, 8) if not cfg & b][0]
        cx, cy = CORNERS[miss]
        return -disc_s(cx, cy, x, y, amps)
    if cfg in (3, 6, 12, 9):  # due angoli adiacenti: bordo dritto
        if cfg == 3:
            return R - y + wobble(amps, x / T)
        if cfg == 12:
            return y - R + wobble(amps, x / T)
        if cfg == 9:
            return R - x + wobble(amps, y / T)
        return x - R + wobble(amps, y / T)
    # due angoli opposti: due dischi separati
    a, b = on
    return max(disc_s(*CORNERS[a], x, y, amps), disc_s(*CORNERS[b], x, y, amps))


def wrap_d(a, b):
    d = abs(a - b)
    return min(d, T - d)


def voronoi(seeds, x, y):
    ds = sorted((math.hypot(wrap_d(x, sx), wrap_d(y, sy)), i) for i, (sx, sy) in enumerate(seeds))
    return ds[0], ds[1]


# ---------------------------------------------------------------- texture di riempimento (toroidali)
def sand_tex(variant):
    img = np.full((T, T), "S2", dtype=object)
    rng = np.random.default_rng(10 + variant)
    if variant == 3:  # onde di sabbia: due linee ondulate periodiche
        for x in range(T):
            for base_y in (4, 12):
                y = int(round(base_y + 1.2 * math.sin(2 * math.pi * x / T + base_y)))
                img[y % T, x] = "S1"
                img[(y + 1) % T, x] = "S3"
        return img
    for _ in range(4):  # nuvolette chiare
        cx, cy, r = rng.integers(0, T), rng.integers(0, T), rng.uniform(1.8, 3.2)
        for y in range(T):
            for x in range(T):
                if math.hypot(wrap_d(x, cx) * 1.0, wrap_d(y, cy) * 1.4) < r:
                    img[y, x] = "S3"
    for _ in range(5):  # puntini piu' scuri
        x, y = rng.integers(0, T), rng.integers(0, T)
        if img[y, x] == "S2":
            img[y, x] = "S1"
    stamps = {
        1: (4, 8, [".AA.", "BAAB", ".BB."], {"A": "S0", "B": "D0"}),  # sassolino
        2: (10, 5, [".FF.", "FCCF", ".FF."], {"F": "F", "C": "S3"}),  # conchiglia
    }
    if variant in stamps:
        x0, y0, rows, keys = stamps[variant]
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch in keys:
                    img[(y0 + dy) % T, (x0 + dx) % T] = keys[ch]
    return img


def damp_tex(variant):
    img = np.full((T, T), "D1", dtype=object)
    rng = np.random.default_rng(30 + variant)
    for _ in range(3):
        cx, cy, r = rng.integers(0, T), rng.integers(0, T), rng.uniform(2.0, 3.4)
        for y in range(T):
            for x in range(T):
                if math.hypot(wrap_d(x, cx), wrap_d(y, cy) * 1.3) < r:
                    img[y, x] = "D0"
    for _ in range(3):
        x, y = rng.integers(0, T), rng.integers(0, T)
        if img[y, x] == "D1":
            img[y, x] = "S0"
    return img


def water_tex(variant):
    base = ["W2", "W2", "W1"][variant]
    light = ["W3", "W1", "W0"][variant]
    img = np.full((T, T), base, dtype=object)
    rng = np.random.default_rng(50 + variant)
    for _ in range(4):  # onde orizzontali chiare
        cx, cy, ln = rng.integers(0, T), rng.integers(0, T), rng.integers(3, 6)
        for i in range(ln):
            img[(cy + (1 if i in (0, ln - 1) else 0)) % T, (cx + i) % T] = light
    if variant != 1:
        sx, sy = int(rng.integers(0, T)), int(rng.integers(0, T))
        img[sy, sx] = "F"
        img[sy, (sx + 1) % T] = "F"
    return img


ROCK_SEEDS = [(3.5, 4), (11.5, 2.5), (7, 11.5), (14, 10)]


def rock_tex_px(x, y):
    (d1, i1), (d2, _) = voronoi(ROCK_SEEDS, x + 0.5, y + 0.5)
    if d2 - d1 < 1.3:
        return "R1"
    sx, sy = ROCK_SEEDS[i1]
    dx, dy = wrap_signed(x + 0.5, sx), wrap_signed(y + 0.5, sy)
    if dx + dy > 3.2:
        return "R0"
    if dx + dy < -2.0:
        return "R3"
    return "R2"


def wrap_signed(a, b):
    d = a - b
    if d > T / 2:
        d -= T
    if d < -T / 2:
        d += T
    return d


GRASS_TUFTS = [(3, 4), (11, 3), (7, 10), (14, 12), (2, 13)]


def grass_tex_px(x, y):
    for cx, cy in GRASS_TUFTS:
        dx, dy = wrap_signed(x, cx), wrap_signed(y, cy)
        if (dx, dy) == (0, 0) or (abs(dx) == 1 and dy == -1) or (abs(dx) == 2 and dy == -2):
            return "G3" if dx <= 0 else "G2"
        if (dx, dy) in ((0, 1), (0, 2), (-1, 1), (1, 1)):
            return "G0"
    return "G1"


# ---------------------------------------------------------------- tile di transizione
COAST_AMPS = [0.9, 0.35]
ROCK_AMPS = [0.8, 0.0, 0.7, 0.0, 0.5]
GRASS_AMPS = [0.4, 0.0, 1.1, 0.0, 0.6, 0.0, 0.5]


def sand_base_px(x, y):
    return "S3" if (x * 7 + y * 3) % 23 == 0 else "S2"


def coast_tile(cfg):
    out = np.empty((T, T), dtype=object)
    for y in range(T):
        for x in range(T):
            s = region_s(cfg, x + 0.5, y + 0.5, COAST_AMPS)
            if s >= 3.4:
                k = "W1" if ((x * 5 + y * 3) % 17 == 0) else "W2"
            elif s >= 1.8:
                k = "W3"
            elif s >= 0:
                k = "F"
            elif s > -1.4:
                k = "D0"
            elif s > -2.8:
                k = "D1"
            else:
                k = sand_base_px(x, y)
            out[y, x] = k
    return out


def rock_tile(cfg):
    out = np.empty((T, T), dtype=object)
    for y in range(T):
        for x in range(T):
            s = region_s(cfg, x + 0.5, y + 0.5, ROCK_AMPS)
            if s < 0:
                k = None
            elif s < 1.0:
                k = "OUT"
            elif s < 2.0:
                k = "R1" if (x + y) % 2 == 0 or s < 1.5 else "R0"
            else:
                k = rock_tex_px(x, y)
            out[y, x] = k
    return out


def grass_tile(cfg):
    out = np.empty((T, T), dtype=object)
    for y in range(T):
        for x in range(T):
            s = region_s(cfg, x + 0.5, y + 0.5, GRASS_AMPS)
            if s < 0:
                k = None
            elif s < 1.0:
                k = "OUT"
            elif s < 2.0:
                k = "G0"
            else:
                k = grass_tex_px(x, y)
            out[y, x] = k
    return out


# ---------------------------------------------------------------- atlante
COLS, ROWS = 12, 5


def build_atlas():
    tiles = {}
    for i in range(4):
        tiles[(i, 0)] = sand_tex(i)
    for i in range(2):
        tiles[(4 + i, 0)] = damp_tex(i)
    for i in range(3):
        tiles[(6 + i, 0)] = water_tex(i)
    for cfg in range(1, 16):
        c, r = cfg % 4, 1 + cfg // 4
        if cfg < 15:
            tiles[(c, r)] = coast_tile(cfg)
        tiles[(4 + c, r)] = rock_tile(cfg)
        tiles[(8 + c, r)] = grass_tile(cfg)
    img = np.zeros((ROWS * T, COLS * T, 4), np.uint8)
    for (c, r), t in tiles.items():
        for y in range(T):
            for x in range(T):
                img[r * T + y, c * T + x] = rgba(t[y, x])
    return img


def tile_at(c, r):
    return (c, r)


def preview(atlas):
    """Mappa di prova 14x10: acqua con baia, battigia, scogli e cespugli su sabbia, per controllare le giunzioni."""
    W, H = 14, 10
    water = np.zeros((H + 1, W + 1), int)  # valori agli angoli
    for y in range(H + 1):
        for x in range(W + 1):
            if y <= 2 or (y <= 4 and 8 <= x <= 12):
                water[y, x] = 1
    rock = np.zeros((H + 1, W + 1), int)
    for y in range(6, 9):
        for x in range(2, 6):
            rock[y, x] = 1
    rock[7, 7] = rock[8, 8] = 1  # due angoli opposti
    grass = np.zeros((H + 1, W + 1), int)
    for y in range(6, 9):
        for x in range(9, 13):
            grass[y, x] = 1
    grass[5, 11] = 1
    out = np.zeros((H * T, W * T, 4), np.uint8)
    rng = np.random.default_rng(3)

    def cfg_of(m, x, y):
        return m[y, x] * 1 + m[y, x + 1] * 2 + m[y + 1, x + 1] * 4 + m[y + 1, x] * 8

    def blit(c, r, x, y):
        out_t = atlas[r * T:(r + 1) * T, c * T:(c + 1) * T]
        a = out_t[..., 3:4] / 255.0
        dst = out[y * T:(y + 1) * T, x * T:(x + 1) * T].astype(float)
        dst[..., :3] = out_t[..., :3] * a + dst[..., :3] * (1 - a)
        dst[..., 3] = np.maximum(dst[..., 3], out_t[..., 3])
        out[y * T:(y + 1) * T, x * T:(x + 1) * T] = dst.astype(np.uint8)

    for y in range(H):
        for x in range(W):
            cfg = cfg_of(water, x, y)
            if cfg == 0:
                blit(int(rng.choice([0] * 8 + [1, 2, 3])), 0, x, y)
            elif cfg == 15:
                blit(int(6 + rng.choice([0, 0, 1])), 0, x, y)
            else:
                blit(cfg % 4, 1 + cfg // 4, x, y)
    for y in range(H):
        for x in range(W):
            cr = cfg_of(rock, x, y)
            if cr:
                blit(4 + cr % 4, 1 + cr // 4, x, y)
            cg = cfg_of(grass, x, y)
            if cg:
                blit(8 + cg % 4, 1 + cg // 4, x, y)
    return out


if __name__ == "__main__":
    outdir = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(outdir, exist_ok=True)
    atlas = build_atlas()
    Image.fromarray(atlas).save(os.path.join(outdir, "terrain_atlas.png"))
    Image.fromarray(atlas).resize((atlas.shape[1] * 4, atlas.shape[0] * 4), Image.NEAREST).save(
        os.path.join(outdir, "terrain_atlas_x4.png"))
    pv = preview(atlas)
    bg = Image.new("RGBA", (pv.shape[1], pv.shape[0]), (255, 0, 255, 255))
    bg.alpha_composite(Image.fromarray(pv))
    bg.resize((pv.shape[1] * 4, pv.shape[0] * 4), Image.NEAREST).save(os.path.join(outdir, "terrain_preview.png"))
    print("ok", atlas.shape)
