"""Genera l'atlante degli elementi di scena (props) nello stesso stile dei tile del terreno.

Stile: pixel d'arte (1 px = 4 px a schermo, come Player e terreno), 4 toni per materiale, luce dall'alto a sinistra, contorno
esterno 1 px #3a1418, nessun anti-aliasing. L'ombra a terra e' incorporata nella cella con alpha 97/255 (#3a1418) e viene separata in
Godot da Scripts/ground_shadow.gd (contratto alpha 0/97/255, vedi Docs/GODOT.md §9). Le forme si disegnano a codice partendo dal
concept Assets/ConceptArt/Terrain/props_concept.png; le varianti (colori, forme, ribaltamenti) escono da parametri e semi fissi.

Uso:  python props_gen.py <cartella_di_uscita>
Scrive props_atlas.png (art a 1 px, da esportare identico), props_atlas_x4.png, props_sheet_x4.png (anteprima su sabbia, con nomi) e
props.json (rettangoli, punto d'appoggio e collisione di ogni prop: letto da Tools/level/props_gen.py).
Dipendenze: pillow, numpy.
"""
import json
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw

OUT = (0x3a, 0x14, 0x18)
SHADOW_ALPHA = 97
LIGHT = np.array([-0.62, -0.78])  # direzione verso la luce (alto a sinistra), y verso il basso


def hx(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# Palette: 4 toni (scuro -> chiaro) per materiale. Sabbia/acqua come in terrain_gen.py; gli altri dal concept e dal negozio.
PAL = {k: [hx(c) for c in v] for k, v in {
    "sand": ["#d29c58", "#e7b269", "#f4c77a", "#fcd993"],
    "wood": ["#63311c", "#a65c28", "#d28a40", "#efb55e"],
    "woodlight": ["#81421f", "#bb7330", "#e8a34c", "#ffcd78"],
    "trunk": ["#7a3f1e", "#a85a28", "#d17f3a", "#eeaa58"],
    "leaf": ["#235c2c", "#3b8a30", "#7fc03a", "#c8de4c"],
    "leafdark": ["#1d4d2c", "#2f7a36", "#58a83a", "#9ccc42"],
    "leafyellow": ["#3b7a2c", "#6fb02f", "#b0d33e", "#e6ec6a"],
    "rock": ["#4a3566", "#775a8f", "#dc8a3e", "#f6b85c"],
    "rocksand": ["#6b4a6e", "#a0786f", "#e4a257", "#fad07c"],
    "coconut": ["#3a1c12", "#5e2f1c", "#8a4a2a", "#b06a3c"],
    "red": ["#8c2328", "#c73633", "#ee4b45", "#ff7970"],
    "cream": ["#aa8155", "#ddbf84", "#f4dcaa", "#fff2d2"],
    "blue": ["#1f3f7a", "#2f6cc0", "#4f9be0", "#a6d6f6"],
    "yellow": ["#b8791c", "#e9a826", "#ffd04a", "#fff09a"],
    "green": ["#1f5a3a", "#2f8a4c", "#55b862", "#a2e08a"],
    "teal": ["#174c4f", "#287d7f", "#4badab", "#8bd5cc"],
    "pink": ["#803a48", "#b65d64", "#e8808a", "#f8c0c4"],
    "orange": ["#a8421a", "#d9662b", "#f58b3c", "#ffb86a"],
    "purple": ["#4a2f78", "#6e4aa6", "#9a78d0", "#c6aef0"],
    "metal": ["#484449", "#68616a", "#8b8180", "#b5a99b"],
    "white": ["#a39aa6", "#d2cbd6", "#f2eef4", "#ffffff"],
    "canvas": ["#e0ccae", "#efe0c6", "#fdf3de", "#ffffff"],  # tela chiara degli spicchi bianchi degli ombrelloni
    "starfish": ["#a8421a", "#d9662b", "#f58b3c", "#ffc27a"],
    "shell": ["#b08a62", "#dcb88c", "#f6dcb4", "#fff3dc"],
    "crab": ["#8c2328", "#c73633", "#ee5a48", "#ff8a78"],
}.items()}


class Cv:
    """Tela RGBA. Le coordinate sono in pixel d'arte; (bx, by) e' il punto d'appoggio al suolo."""

    def __init__(self, w=96, h=112, bx=None, by=None):
        self.w, self.h = w, h
        self.bx = w // 2 if bx is None else bx
        self.by = h - 14 if by is None else by
        self.a = np.zeros((h, w, 4), np.uint8)
        self.yy, self.xx = np.mgrid[0:h, 0:w]

    # ---- primitive ----
    def mask_poly(self, pts):
        im = Image.new("L", (self.w, self.h), 0)
        ImageDraw.Draw(im).polygon([(float(x), float(y)) for x, y in pts], fill=255)
        return np.array(im) > 0

    def mask_ellipse(self, cx, cy, rx, ry):
        return ((self.xx + 0.5 - cx) / rx) ** 2 + ((self.yy + 0.5 - cy) / ry) ** 2 <= 1.0

    def paint(self, mask, color):
        self.a[mask] = (*color, 255)

    def shade(self, mask, pal, cx=None, cy=None, rx=None, ry=None, bias=0.0, steps=(-0.5, -0.05, 0.45)):
        """Pittura mask con 4 toni secondo una cupola (luce in alto a sinistra)."""
        ys, xs = np.nonzero(mask)
        if len(xs) == 0:
            return
        cx = (xs.min() + xs.max() + 1) / 2 if cx is None else cx
        cy = (ys.min() + ys.max() + 1) / 2 if cy is None else cy
        rx = max((xs.max() - xs.min() + 1) / 2, 1) if rx is None else rx
        ry = max((ys.max() - ys.min() + 1) / 2, 1) if ry is None else ry
        nx = (self.xx + 0.5 - cx) / rx
        ny = (self.yy + 0.5 - cy) / ry
        lit = -(nx * LIGHT[0] + ny * LIGHT[1]) + bias
        tone = np.where(lit < steps[0], 0, np.where(lit < steps[1], 1, np.where(lit < steps[2], 2, 3)))
        for t in range(4):
            self.paint(mask & (tone == t), pal[t])

    def px(self, x, y, color):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x] = (*color, 255)

    def line(self, x0, y0, x1, y1, color):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(n + 1):
            t = i / max(n, 1)
            self.px(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t), color)

    def stroke(self, pts, widths, pal, tone_fn=None, light_left=True):
        """Tratto di larghezza variabile lungo una spezzata (tronchi, steli, rami): toni in base al lato verso la luce."""
        pts = [np.array(p, float) for p in pts]
        total = sum(np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1))
        steps = int(total * 3) + 1
        acc = 0.0
        seg = 0
        seglen = [np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)]
        for k in range(steps + 1):
            d = total * k / steps
            while seg < len(seglen) - 1 and acc + seglen[seg] < d:
                acc += seglen[seg]
                seg += 1
            t = (d - acc) / max(seglen[seg], 1e-6)
            p = pts[seg] + (pts[seg + 1] - pts[seg]) * t
            u = d / max(total, 1e-6)
            w = np.interp(u, np.linspace(0, 1, len(widths)), widths)
            tang = (pts[seg + 1] - pts[seg]) / max(seglen[seg], 1e-6)
            nrm = np.array([-tang[1], tang[0]])
            if nrm @ LIGHT < 0:
                nrm = -nrm  # normale verso la luce
            r = w / 2
            for s in np.linspace(-r, r, int(w * 2) + 1):
                q = p + nrm * s
                side = s / max(r, 1e-6)  # +1 verso la luce
                tone = 3 if side > 0.55 else 2 if side > -0.05 else 1 if side > -0.6 else 0
                if tone_fn:
                    tone = tone_fn(u, tone)
                self.px(math.floor(q[0]), math.floor(q[1]), pal[max(0, min(3, tone))])

    def blit(self, other, ox, oy):
        h, w = other.a.shape[:2]
        for y in range(h):
            for x in range(w):
                if other.a[y, x, 3] and 0 <= x + ox < self.w and 0 <= y + oy < self.h:
                    self.a[y + oy, x + ox] = other.a[y, x]

    def flip(self):
        """Ribalta in orizzontale rispetto al punto d'appoggio."""
        out = Cv(self.w, self.h, self.bx, self.by)
        a = self.a[:, ::-1].copy()
        shift = (self.w - 1 - self.bx) - self.bx
        out.a = np.roll(a, -shift, axis=1)
        if shift > 0:
            out.a[:, -shift:] = 0
        elif shift < 0:
            out.a[:, :-shift] = 0
        return out

    # ---- finitura ----
    def outline(self):
        op = self.a[..., 3] > 0
        n = np.zeros_like(op)
        n[1:] |= op[:-1]
        n[:-1] |= op[1:]
        n[:, 1:] |= op[:, :-1]
        n[:, :-1] |= op[:, 1:]
        edge = n & ~op
        self.a[edge] = (*OUT, 255)

    def shadow(self, kx=0.5, ky=0.18, base_rx=0, base_ry=None, shrink=1.0, floor_only=False, offset=None):
        """Ombra a terra: proiezione del corpo (alto a sinistra -> ombra in basso a destra) piu' un'ellisse sotto la base."""
        body = self.a[..., 3] > 0
        sh = np.zeros_like(body)
        ys, xs = np.nonzero(body)
        for y, x in zip(ys, xs):
            h = max(self.by - y, 0) * shrink
            if floor_only and h > 0:
                continue
            sx = int(round(x + kx * h))
            sy = int(round(self.by + 1 + ky * h))
            if 0 <= sx < self.w and 0 <= sy < self.h:
                sh[sy, sx] = True
        if offset:  # oggetto piatto: ombra = corpo spostato in basso a destra
            dx, dy = offset
            sh |= np.roll(np.roll(body, dy, axis=0), dx, axis=1)
        if base_rx:
            base_ry = base_ry or max(base_rx * 0.42, 1.5)
            sh |= self.mask_ellipse(self.bx + 1, self.by + 1.5, base_rx, base_ry)
        # chiusura 3x3: toglie i buchi della proiezione
        for _ in range(2):
            d = sh.copy()
            d[1:] |= sh[:-1]
            d[:-1] |= sh[1:]
            d[:, 1:] |= sh[:, :-1]
            d[:, :-1] |= sh[:, 1:]
            sh = d
        for _ in range(1):
            e = sh.copy()
            e[1:] &= sh[:-1]
            e[:-1] &= sh[1:]
            e[:, 1:] &= sh[:, :-1]
            e[:, :-1] &= sh[:, 1:]
            sh = e
        sh &= ~body
        self.a[sh] = (*OUT, SHADOW_ALPHA)

    def crop(self):
        al = self.a[..., 3] > 0
        ys, xs = np.nonzero(al)
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        return self.a[y0:y1, x0:x1].copy(), (self.bx - x0, self.by - y0)


# ---------------------------------------------------------------- foglie e vegetazione
def bez(p0, p1, p2, t):
    p0, p1, p2 = np.array(p0, float), np.array(p1, float), np.array(p2, float)
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2


def leaf(c, p0, p1, p2, width, pal, rng, teeth=0.0, tone_shift=0, rib=True, steps=24, sep=True):
    """Foglia: spina curva (bezier) con larghezza a fuso; il lato verso la luce e' piu' chiaro, nervatura piu' scura."""
    spine = [bez(p0, p1, p2, i / steps) for i in range(steps + 1)]
    left, right = [], []
    for i, p in enumerate(spine):
        t = i / steps
        q = spine[min(i + 1, steps)] - spine[max(i - 1, 0)]
        q = q / (np.linalg.norm(q) + 1e-9)
        n = np.array([-q[1], q[0]])
        w = width * (math.sin(math.pi * min(t * 1.08, 1.0)) ** 0.75) / 2
        if teeth and 0.15 < t < 0.95:
            w *= 1 - teeth * (0.5 + 0.5 * math.sin(i * 2.6))
        left.append(p + n * w)
        right.append(p - n * w)
    lit_side = left if (np.mean([l - r for l, r in zip(left, right)], axis=0) @ LIGHT) > 0 else right
    dark_side = right if lit_side is left else left
    up = c.mask_poly(lit_side + spine[::-1])
    dn = c.mask_poly(dark_side + spine[::-1])
    mid = c.mask_poly(left + right[::-1])
    t_up = max(0, min(3, 2 + tone_shift))
    t_dn = max(0, min(3, 1 + tone_shift))
    if sep:  # bordo scuro sopra le foglie gia' disegnate: ogni foglia resta leggibile
        grown = mid.copy()
        grown[1:] |= mid[:-1]
        grown[:-1] |= mid[1:]
        grown[:, 1:] |= mid[:, :-1]
        grown[:, :-1] |= mid[:, 1:]
        c.paint(grown & ~mid & (c.a[..., 3] > 0), pal[0])
    c.paint(mid & ~up & ~dn, pal[t_dn])
    c.paint(dn, pal[t_dn])
    c.paint(up, pal[t_up])
    if rib:
        for i in range(1, steps - 2):
            c.px(*np.floor(spine[i]), pal[max(0, t_dn - 1)])
    # punta chiara
    return spine


def palm_crown(c, cx, cy, size, pal, rng, n=9, droop=0.55, coconuts=True, flip_light=False):
    """Chioma: fronde ad arco con la punta che cade, pennate (bordo a denti), dalle piu' lontane (dietro, scure) alle piu' vicine."""
    # (angolo, lunghezza relativa, strato 0=dietro 2=davanti)
    base = [(-176, 1.0, 0), (-152, 1.1, 1), (-128, 1.0, 0), (-104, 0.85, 1), (-76, 0.85, 1), (-52, 1.0, 0), (-28, 1.1, 1), (-4, 1.0, 0),
            (-166, 0.68, 2), (-14, 0.68, 2), (100, 0.5, 2), (80, 0.5, 2)]
    sel = base[:n] if n >= len(base) else [t for t in base if t[2] < 2][: n - 2] + [t for t in base if t[2] == 2][:2]
    for ang, rel, layer in sorted(sel, key=lambda t: t[2]):
        a = math.radians(ang + rng.uniform(-5, 5))
        L = size * rel * rng.uniform(0.92, 1.06)
        down = ang > 0
        up = -math.sin(a)
        side = 1 if math.cos(a) >= 0 else -1
        ctrl = (cx + math.cos(a) * L * 0.55 + (side * L * 0.1 if up > 0.9 else 0), cy + math.sin(a) * L * 0.55 - (0 if down else size * 0.42))
        end = (cx + math.cos(a) * L * 0.92 + (side * L * 0.34 if up > 0.9 else 0),
               cy + math.sin(a) * L * 0.2 + (L * 0.3 if down else L * (0.66 - 0.45 * up) * droop / 0.55))
        shift = 1 if math.cos(a) < -0.15 else (-1 if math.cos(a) > 0.35 else 0)
        shift = max(-1, min(1, shift + {0: -1, 1: 0, 2: 1}[layer] // 1))
        leaf(c, (cx, cy), ctrl, end, size * 0.24, pal, rng, teeth=0.55, tone_shift=shift, steps=44)
    if coconuts:
        for dx, dy in [(-2, 2), (1, 3), (3, 1)]:
            c.shade(c.mask_ellipse(cx + dx, cy + dy, 2.1, 2.1), PAL["coconut"])


def tuft(c, bx, by, rng, n=4):
    """Ciuffo d'erba alla base del tronco."""
    for dx, ang in [(-3, -130), (3, -50), (-1, -105), (1, -78)][:n]:
        a = math.radians(ang + rng.uniform(-8, 8))
        L = rng.uniform(5, 7)
        leaf(c, (bx + dx, by), (bx + dx + math.cos(a) * L * 0.4, by + math.sin(a) * L * 0.8),
             (bx + dx + math.cos(a) * L, by + math.sin(a) * L), 2.6, PAL["leaf"], rng, rib=False, steps=8, sep=False)


def palm_trunk(c, base, top, bend, w0, w1):
    bx, by = base
    tx, ty = top
    mx, my = (bx + tx) / 2 + bend, (by + ty) / 2
    H = by - ty
    p1 = np.array([bx, by - 0.42 * H])  # tangente iniziale verticale
    p2 = np.array([mx + bend * 0.9, ty + 0.28 * H])
    p0, p3 = np.array(base, float), np.array(top, float)
    pts = []
    for i in range(13):
        t = i / 12
        pts.append((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)
    pal = PAL["trunk"]

    def rings(u, tone):  # anelli del tronco
        return tone - 1 if int(u * 30) % 3 == 0 else tone

    c.stroke(pts, [w0, (w0 + w1) / 2, w1], pal, tone_fn=rings)
    return pts


def palm(kind, seed, flip=False, pal_name="leaf"):
    rng = random.Random(seed)
    c = Cv(96, 112)
    pal = PAL[pal_name]
    bx, by = c.bx, c.by
    if kind == "tall":
        top = (bx + 9, by - 62)
        pts = palm_trunk(c, (bx, by), top, -5, 6.2, 4)
        # base: ciuffo
        tuft(c, bx, by, rng)
        palm_crown(c, top[0], top[1], 35, pal, rng, n=10)
        c.__dict__["_trunk_w"] = 6
    elif kind == "lean":
        top = (bx + 18, by - 44)
        palm_trunk(c, (bx, by), top, 7, 6, 3.6)
        tuft(c, bx, by, rng)
        palm_crown(c, top[0], top[1], 29, pal, rng, n=9)
    elif kind == "young":
        top = (bx + 1, by - 11)
        palm_trunk(c, (bx, by), top, 1, 3.6, 3)
        tuft(c, bx, by, rng)
        palm_crown(c, top[0], top[1] - 1, 15, pal, rng, n=8, droop=0.5)
    elif kind == "bent":
        top = (bx - 14, by - 36)
        palm_trunk(c, (bx, by), top, -9, 6, 3.6)
        tuft(c, bx, by, rng)
        palm_crown(c, top[0], top[1], 28, pal, rng, n=9)
    if flip:
        c = c.flip()
    c.outline()
    c.shadow(kx=0.55, ky=0.1, base_rx=7, shrink=0.8)
    return c


def bush(kind, seed, pal_name="leaf", flip=False):
    rng = random.Random(seed)
    c = Cv(64, 48, by=40)
    pal = PAL[pal_name]
    bx, by = c.bx, c.by
    if kind == "broad":
        n, L, wd = 8, 17, 9
        angs = [-165, -140, -118, -95, -72, -48, -22, 0]
        for i in sorted(range(n), key=lambda i: abs(angs[i] + 90) * -1):
            a = math.radians(angs[i])
            e = (bx + math.cos(a) * L, by - 4 + math.sin(a) * L * 0.95)
            ctrl = (bx + math.cos(a) * L * 0.45, by - 4 + math.sin(a) * L * 0.9 - 3)
            leaf(c, (bx, by - 2), ctrl, e, wd, pal, rng, teeth=0.2, tone_shift=1 if math.cos(a) < 0 else 0, steps=18)
    elif kind == "round":
        n = 13
        for i in range(n):
            a = math.radians(-175 + 170 * i / (n - 1) + rng.uniform(-6, 6))
            L = rng.uniform(10, 15)
            e = (bx + math.cos(a) * L * 1.1, by - 3 + math.sin(a) * L * 0.9)
            ctrl = (bx + math.cos(a) * L * 0.4, by - 3 + math.sin(a) * L * 0.8 - 2)
            leaf(c, (bx, by - 1), ctrl, e, 6, pal, rng, teeth=0.0, tone_shift=1 if math.cos(a) < -0.1 else (-1 if math.cos(a) > 0.4 else 0), rib=False, steps=14)
    elif kind == "spiky":
        n = 11
        for i in range(n):
            a = math.radians(-160 + 140 * i / (n - 1) + rng.uniform(-5, 5))
            L = rng.uniform(15, 21)
            e = (bx + math.cos(a) * L * 0.9, by - 3 + math.sin(a) * L)
            ctrl = (bx + math.cos(a) * L * 0.25, by - 3 + math.sin(a) * L * 0.7)
            leaf(c, (bx + rng.uniform(-2, 2), by), ctrl, e, 4.2, pal, rng, rib=False, tone_shift=1 if math.cos(a) < 0 else 0, steps=16)
    elif kind == "small":
        n = 7
        for i in range(n):
            a = math.radians(-165 + 150 * i / (n - 1))
            L = rng.uniform(8, 11)
            e = (bx + math.cos(a) * L, by - 2 + math.sin(a) * L)
            ctrl = (bx + math.cos(a) * L * 0.4, by - 2 + math.sin(a) * L * 0.7 - 1)
            leaf(c, (bx, by - 1), ctrl, e, 4.5, pal, rng, rib=False, tone_shift=1 if math.cos(a) < 0 else 0, steps=12)
    if flip:
        c = c.flip()
    c.outline()
    c.shadow(kx=0.45, ky=0.14, base_rx={"broad": 15, "round": 13, "spiky": 12, "small": 8}[kind], shrink=0.9)
    return c


# ---------------------------------------------------------------- rocce
def rock(w, h, seed, pal_name="rock", grass=0, facets=4, flip=False):
    rng = random.Random(seed)
    cv = Cv(w + 24, h + 28, by=h + 18)
    bx, by = cv.bx, cv.by
    pal = PAL[pal_name]
    cx, cy = bx, by - h * 0.5
    # contorno: ellisse irregolare, base piu' piatta
    pts = []
    n = 14
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 1 + rng.uniform(-0.12, 0.1)
        px_ = cx + math.cos(a) * w / 2 * r
        py_ = cy + math.sin(a) * h / 2 * r
        py_ = min(py_, by - 0.5)
        pts.append((px_, py_))
    mask = cv.mask_poly(pts)
    ys, xs = np.nonzero(mask)
    # facce: seed di Voronoi, tono secondo la posizione (alto-sinistra chiaro, basso-destra viola)
    seeds = []
    for i in range(facets):
        sx = rng.uniform(xs.min() + 2, xs.max() - 2)
        sy = rng.uniform(ys.min() + 2, ys.max() - 2)
        seeds.append((sx, sy))
    seeds.sort(key=lambda s: s[1])
    sx0 = np.array([s[0] for s in seeds])[:, None, None]
    sy0 = np.array([s[1] for s in seeds])[:, None, None]
    d = (cv.xx[None] - sx0) ** 2 + (cv.yy[None] - sy0) ** 2
    face = np.argmin(d, axis=0)
    for i, (sx, sy) in enumerate(seeds):
        lit = -(((sx - cx) / (w / 2)) * LIGHT[0] + ((sy - cy) / (h / 2)) * LIGHT[1])
        tone = 3 if lit > 0.45 else 2 if lit > -0.1 else 1 if lit > -0.6 else 0
        if i == 0:
            tone = 3
        cv.paint(mask & (face == i), pal[tone])
    # cima chiara: lato alto-sinistra
    top = mask & (((cv.xx + 0.5 - cx) / (w / 2)) * LIGHT[0] + ((cv.yy + 0.5 - cy) / (h / 2)) * LIGHT[1] < -0.45) & (cv.yy < cy)
    cv.paint(top & (face == face[int(cy - h * 0.25), int(cx)]), pal[3])
    # crepe scure fra le facce
    brd = np.zeros_like(mask)
    brd[:-1] |= (face[:-1] != face[1:]) & mask[:-1] & mask[1:]
    brd[:, :-1] |= (face[:, :-1] != face[:, 1:]) & mask[:, :-1] & mask[:, 1:]
    if grass:
        r2 = random.Random(seed + 7)
        for gx in [-w * 0.34, w * 0.36][:grass]:
            for k, (dx, a) in enumerate([(-2, -120), (0, -90), (2, -55)]):
                ang = math.radians(a)
                L = r2.uniform(5, 7)
                leaf(cv, (bx + gx + dx, by), (bx + gx + dx + math.cos(ang) * L * 0.4, by + math.sin(ang) * L * 0.8),
                     (bx + gx + dx + math.cos(ang) * L, by + math.sin(ang) * L), 2.6, PAL["leaf"], r2, rib=False, steps=8, tone_shift=0)
    if flip:
        cv = cv.flip()
    cv.outline()
    cv.shadow(kx=0.6, ky=0.2, base_rx=w * 0.55, shrink=0.9)
    return cv


# ---------------------------------------------------------------- fiori
def flower(kind, seed):
    rng = random.Random(seed)
    c = Cv(24, 22, by=18)
    bx, by = c.bx, c.by
    # fogliame alla base
    for dx, a in [(-5, -150), (4, -35), (-1, -100)]:
        ang = math.radians(a)
        leaf(c, (bx + dx * 0.3, by), (bx + dx * 0.6 + math.cos(ang) * 2, by - 2),
             (bx + dx + math.cos(ang) * 3, by - 4 + math.sin(ang) * 2), 3.4, PAL["leaf"], rng, rib=False, steps=8)
    fx, fy = bx + rng.choice([-1, 0, 1]), by - 5
    if kind in ("hibiscus_red", "hibiscus_orange", "hibiscus_pink"):
        pal = PAL[{"hibiscus_red": "red", "hibiscus_orange": "orange", "hibiscus_pink": "pink"}[kind]]
        for i in range(5):
            a = math.radians(-90 + 72 * i + 18)
            m = c.mask_ellipse(fx + math.cos(a) * 3.0, fy + math.sin(a) * 2.6, 2.7, 2.5)
            c.shade(m, pal)
        c.paint(c.mask_ellipse(fx, fy, 1.1, 1.1), PAL["yellow"][2])
        c.px(fx + 1, fy - 3, PAL["yellow"][3])
        c.px(fx + 2, fy - 4, PAL["yellow"][2])
    elif kind in ("daisy_yellow", "daisy_white", "daisy_blue"):
        pal = PAL[{"daisy_yellow": "yellow", "daisy_white": "white", "daisy_blue": "blue"}[kind]]
        for i in range(6):
            a = math.radians(60 * i + 10)
            m = c.mask_ellipse(fx + math.cos(a) * 2.6, fy + math.sin(a) * 2.3, 1.9, 1.7)
            c.shade(m, pal)
        c.paint(c.mask_ellipse(fx, fy, 1.4, 1.3), PAL["orange"][2] if kind != "daisy_yellow" else PAL["orange"][1])
    elif kind in ("pink_cluster", "white_cluster", "purple_cluster"):
        pal = PAL[{"pink_cluster": "pink", "white_cluster": "cream", "purple_cluster": "purple"}[kind]]
        for ddx, ddy in [(-4, -1), (2, -3), (3, 0)]:
            for i in range(5):
                a = math.radians(72 * i + 20)
                m = c.mask_ellipse(fx + ddx + math.cos(a) * 1.6, fy + ddy + math.sin(a) * 1.5, 1.2, 1.1)
                c.shade(m, pal)
            c.px(fx + ddx, fy + ddy, PAL["yellow"][2])
    c.outline()
    c.shadow(kx=0.3, ky=0.1, base_rx=6)
    return c


# ---------------------------------------------------------------- conchiglie e animaletti
def shellprop(kind, seed=0, pose=0):
    rng = random.Random(seed)
    c = Cv(24, 20, by=15)
    bx, by = c.bx, c.by
    if kind == "spiral":
        m = c.mask_ellipse(bx, by - 3, 5.2, 4.2)
        c.shade(m, PAL["shell"])
        for t in np.linspace(0, 6.5, 40):
            r = 0.4 + t * 0.55
            c.px(bx - 1 + math.cos(t) * r * 0.85, by - 3 + math.sin(t) * r * 0.6, PAL["shell"][0])
        c.px(bx + 3, by - 6, PAL["shell"][3])
    elif kind == "cone":
        pts = [(bx - 4, by - 1), (bx + 1, by - 9), (bx + 4, by - 1)]
        m = c.mask_poly(pts)
        c.shade(m, PAL["shell"])
        for yy_ in (-3, -5, -7):
            c.line(bx - 3 + (yy_ + 3) * -0.3 + 1, by + yy_, bx + 2 - (yy_ + 3) * 0.2, by + yy_ + 1, PAL["shell"][0])
        c.paint(c.mask_ellipse(bx - 1, by - 1, 2.8, 1.4), PAL["pink"][2])
    elif kind in ("starfish", "starfish_pink"):
        pal = PAL["starfish" if kind == "starfish" else "pink"]
        pts = []
        for i in range(10):
            r = 6.5 if i % 2 == 0 else 2.9
            a = math.radians(-90 + 36 * i + 10)
            pts.append((bx + math.cos(a) * r, by - 4 + math.sin(a) * r * 0.78))
        m = c.mask_poly(pts)
        c.shade(m, pal, bias=0.05)
        for i in range(5):
            a = math.radians(-90 + 72 * i + 10)
            c.px(bx + math.cos(a) * 3.2, by - 4 + math.sin(a) * 2.5, pal[3])
    elif kind == "sanddollar":
        m = c.mask_ellipse(bx, by - 3, 5.5, 4.6)
        c.shade(m, PAL["shell"], steps=(-0.6, -0.2, 0.55))
        for i in range(5):
            a = math.radians(-90 + 72 * i)
            c.px(bx + math.cos(a) * 2.2, by - 3 + math.sin(a) * 1.8, PAL["shell"][0])
        c.px(bx, by - 3, PAL["shell"][0])
    elif kind == "clam":
        m = c.mask_ellipse(bx, by - 3, 6, 4.3) & (c.yy <= by - 1)
        c.shade(m, PAL["pink"], bias=0.15)
        for i in range(-3, 4):
            c.line(bx + i * 0.5, by - 1, bx + i * 1.4, by - 6, PAL["pink"][1])
    elif kind == "crab":
        # pose: 0 a riposo, 1 chela sinistra alzata + occhi su, 2 chela destra alzata, 3 solo occhi su (animazione di 4 fotogrammi)
        body = c.mask_ellipse(bx, by - 4, 4.6, 3.1)
        c.shade(body, PAL["crab"])
        eyes_up = pose in (1, 3)
        for s in (-1, 1):
            up = (pose == 1 and s == -1) or (pose == 2 and s == 1)
            cy = by - 10 if up else by - 7
            c.paint(c.mask_ellipse(bx + s * 6.3, cy, 2.2, 2.0), PAL["crab"][2])
            if up:
                c.px(bx + s * 6.3, cy - 1, PAL["crab"][0])  # chela aperta
            c.line(bx + s * 4, by - 5, bx + s * 5.5, cy + 1, PAL["crab"][1])
            for k in range(3):
                c.line(bx + s * 3.6, by - 3 + k * 0.6, bx + s * (6 + k * 0.8), by - 1 + k * 0.4 - (1 if pose in (1, 2) and k == 1 else 0), PAL["crab"][0])
            ey = by - 8 - (1 if eyes_up else 0)
            c.px(bx + s * 1.4, ey, PAL["white"][3])
            c.px(bx + s * 1.4, ey + 1, PAL["crab"][0])
    c.outline()
    c.shadow(kx=0.4, ky=0.15, base_rx=5)
    return c


# ---------------------------------------------------------------- oggetti
def umbrella_closed(pal_name, seed, lean=2):
    rng = random.Random(seed)
    c = Cv(48, 80, by=66)
    bx, by = c.bx, c.by
    pole = [(bx, by), (bx + lean * 0.5, by - 24), (bx + lean, by - 46)]
    c.stroke(pole, [2.2, 2.0, 1.8], PAL["wood"])
    top = (bx + lean, by - 52)
    # telo chiuso: cono con pieghe a strisce
    cx = bx + lean
    pts = [(cx - 1, by - 56), (cx + 1, by - 56), (cx + 7, by - 22), (cx + 2, by - 17), (cx - 4, by - 17), (cx - 7, by - 22)]
    m = c.mask_poly(pts)
    pal = PAL[pal_name]
    cream = PAL["cream"]
    for i in range(7):
        x0 = cx - 7 + i * 2
        stripe = m & (c.xx >= x0) & (c.xx < x0 + 2)
        c.paint(stripe, (pal if i % 2 == 0 else cream)[2])
    lit = m & (c.xx < cx - 2)
    for i in range(7):
        x0 = cx - 7 + i * 2
        stripe = m & (c.xx >= x0) & (c.xx < x0 + 2)
        base = pal if i % 2 == 0 else cream
        tone = 3 if x0 < cx - 3 else 2 if x0 < cx else 1 if x0 < cx + 3 else 0
        c.paint(stripe, base[tone])
    # orlo a punte
    for i in range(4):
        px_ = cx - 6 + i * 3.6
        c.paint(c.mask_poly([(px_ - 1.5, by - 18), (px_ + 1.5, by - 18), (px_, by - 14)]), (pal if i % 2 == 0 else cream)[1])
    # cima
    c.paint(c.mask_ellipse(cx, by - 57, 1.7, 1.7), PAL["wood"][3])
    c.outline()
    c.shadow(kx=0.45, ky=0.12, base_rx=3, shrink=0.8)
    return c


def umbrella_open(pal_name, seed, pattern="stripes", lean=0, second=None, tilt=0):
    """Ombrellone aperto: calotta a spicchi vista da 25 gradi (cima in alto, bordo ellittico con festoni sull'orlo anteriore),
    luce per spicchio secondo la sua pendenza, asta leggermente inclinata e calotta che puo' pendere da un lato."""
    c = Cv(96, 100, by=88)
    bx, by = c.bx, c.by
    pal = PAL[pal_name]
    pal2 = PAL[second] if second else PAL["cream"]
    cx, cy = bx + lean, by - 36
    rx, ry, H = 29.0, 11.0, 11.0
    apex = np.array([cx + tilt, cy - H])
    c.stroke([(bx, by), (bx + lean * 0.5, by - 20), (cx, cy - 4)], [2.4, 2.2, 2], PAL["wood"])
    k = 8
    thetas = [2 * math.pi * i / k + 0.2 for i in range(k)]

    def rim(t, drop=0.0):
        return np.array([cx + rx * math.cos(t), cy + ry * math.sin(t) + drop])

    order = sorted(range(k), key=lambda i: math.sin(thetas[i] + math.pi / k))  # prima gli spicchi dietro
    for i in order:
        t0 = thetas[i]
        t1 = thetas[i + 1] if i + 1 < k else thetas[0] + 2 * math.pi
        tm = (t0 + t1) / 2
        r0, r1 = rim(t0), rim(t1)
        rim_pts = [rim(t0 + (t1 - t0) * j / 6) for j in range(7)]
        mid0 = apex + (r0 - apex) * 0.5 + np.array([0, -2.2])
        mid1 = apex + (r1 - apex) * 0.5 + np.array([0, -2.2])
        poly = [tuple(apex), tuple(mid0)] + [tuple(p) for p in rim_pts] + [tuple(mid1)]
        m = c.mask_poly(poly)
        # i pannelli rivolti verso l'alto a sinistra sono i piu' chiari
        lit = 1.0 + 1.2 * (math.cos(tm) * LIGHT[0] + math.sin(tm) * LIGHT[1])
        tone = 3 if lit > 1.35 else 2 if lit > 0.6 else 1 if lit > 0.0 else 0
        base = pal if (i % 2 == 0 or pattern == "solid") else pal2
        if pattern == "solid" and i % 2 == 1:
            tone = max(tone - 1, 0)
        c.paint(m, base[tone])
        if math.sin(tm) > -0.15:  # orlo a festone sul lato anteriore
            lip = [tuple(p) for p in rim_pts] + [
                tuple(rim(t1 - (t1 - t0) * j / 6, drop=2.6 + 1.8 * math.sin(math.pi * (1 - j / 6)))) for j in range(7)]
            lm = c.mask_poly(lip)
            c.paint(lm & ~m, base[max(tone - 1, 0)])
    for t in thetas:  # nervature
        r = rim(t)
        for u in np.linspace(0.1, 1, 30):
            q = apex + (r - apex) * u + np.array([0, -2.2 * math.sin(math.pi * u)])
            if c.a[int(q[1]), int(q[0]), 3]:
                c.px(q[0], q[1], pal[0])
    c.paint(c.mask_ellipse(apex[0], apex[1] - 0.5, 1.9, 1.6), PAL["wood"][3])
    c.px(apex[0], apex[1] - 2.5, PAL["wood"][2])
    c.px(apex[0], apex[1] - 3.5, PAL["wood"][1])
    c.outline()
    c.shadow(kx=0.3, ky=0.32, base_rx=3, shrink=0.5)
    return c


def surfboard(design, seed, tone="cream", pose="stuck", tilt=0.0):
    """Tavola da surf: 'stuck' dritta e infilata nella sabbia (la coda sparisce in un monticello), 'lean' piantata inclinata
    (tilt in gradi, + a destra), 'flat' sdraiata sulla sabbia (tilt = rotazione sul terreno). Forma e disegni dipendono da (u, v):
    u lungo la tavola (0 coda, 1 punta), v di traverso (-1..1)."""
    c = Cv(64, 72, by=62)
    bx, by = c.bx, c.by
    L, W = 46.0, 17.0
    base = PAL[tone]
    flat = pose == "flat"
    th = math.radians(tilt)
    if flat:
        cx, cy = bx, by - 8
        gx = c.xx + 0.5 - cx
        gy = (c.yy + 0.5 - cy) / 0.46  # prospettiva 25 gradi sul terreno
        along = gx * math.cos(th) + gy * math.sin(th)
        across = -gx * math.sin(th) + gy * math.cos(th)
        u = (along + L / 2) / L
    else:
        dx = c.xx + 0.5 - bx
        dy = by - (c.yy + 0.5)
        along = dx * math.sin(th) + dy * math.cos(th)
        across = dx * math.cos(th) - dy * math.sin(th)
        u = (along + 2.0) / L  # la coda sta 2 px sotto il punto d'appoggio: affonda nella sabbia
    v = across / (W / 2)
    ut = np.clip(u, 0, 1)
    wprof = np.sin(np.pi * np.clip(ut * 0.97 + 0.02, 0, 1)) ** 0.55 * np.where(ut > 0.55, 0.95 - 0.1 * (ut - 0.55), 1.0)
    m = (u >= 0) & (u <= 1) & (np.abs(v) <= wprof)
    if flat:
        c.paint(np.roll(m, 1, axis=0) & ~m, base[0])  # spessore: bordo scuro sotto
        tone_ = np.where(np.abs(v) > 0.82, np.where(v < 0, 3, 1), np.where(u > 0.5, 2, 3))
        tone_ = np.where((np.abs(v) <= 0.82) & (v < -0.35), 3, tone_)
    else:
        tone_ = np.where(v < -0.55, 3, np.where(v < 0.25, 2, np.where(v < 0.72, 1, 0)))
    for t in range(4):
        c.paint(m & (tone_ == t), base[t])
    if design == "hibiscus":
        cu = 0.56
        r = np.hypot((u - cu) * L, v * W / 2)
        ang = np.arctan2(v * W / 2, (u - cu) * L)
        petal = m & (r < 7.6 * (0.62 + 0.38 * np.abs(np.cos(2.5 * (ang + 0.3)))))
        pal = PAL["red"]
        c.paint(petal & (r < 7.6), pal[2])
        c.paint(petal & (v < -0.15), pal[3])
        c.paint(petal & (v > 0.3), pal[1])
        c.paint(m & (r < 1.5), PAL["yellow"][2])
        c.paint(m & (np.abs(v) < 0.07) & (u < 0.42), PAL["red"][1])
        c.paint(m & (np.abs(v) < 0.07) & (u > 0.72) & (u < 0.9), PAL["red"][1])
    elif design == "stripes":
        pal = PAL["red"] if tone != "blue" else PAL["yellow"]
        for u0 in (0.18, 0.22, 0.66, 0.70):
            c.paint(m & (u >= u0) & (u < u0 + 0.03), pal[2])
        c.paint(m & (np.abs(v) < 0.07), pal[1])
    elif design == "wave":
        pal = PAL["teal"] if tone not in ("teal", "blue") else PAL["white"]
        wv = 0.5 + 0.05 * np.sin(v * 5.0)
        c.paint(m & (np.abs(u - wv) < 0.045), pal[2])
        c.paint(m & (np.abs(u - wv + 0.11) < 0.03), pal[3] if tone != "teal" else pal[2])
        c.paint(m & (np.abs(v) < 0.07), base[0])
    elif design == "bolt":
        pal = PAL["orange"] if tone != "orange" else PAL["yellow"]
        zz = 0.5 + 0.12 * np.sign(np.sin(u * 22))
        c.paint(m & (np.abs(v - (zz - 0.5) * 2.2) < 0.2) & (u > 0.25) & (u < 0.8), pal[2])
        c.paint(m & (np.abs(v) < 0.07), base[0])
    if not flat:
        # monticello di sabbia che nasconde la coda: la tavola e' infilata, non appoggiata sulla punta
        mound = c.mask_ellipse(bx, by - 0.5, 11, 3.6) & (c.yy >= by - 3)
        mound |= c.mask_ellipse(bx + 3, by - 2, 6, 2.6)
        c.shade(mound, PAL["sand"], cx=bx, cy=by - 1, rx=11, ry=4, steps=(-0.55, -0.05, 0.5))
        for gx_, gy_ in ((-6, 0), (5, 1), (-2, 1)):
            c.px(bx + gx_, by + gy_, PAL["sand"][3])
        c.px(bx + 7, by, PAL["sand"][1])
    c.outline()
    if flat:
        c.shadow(kx=0, ky=0, floor_only=True, offset=(1, 2))
    else:
        c.shadow(kx=0.35, ky=0.12, base_rx=10, shrink=0.7)
    return c


def log(seed, flip=False, branch=True):
    rng = random.Random(seed)
    c = Cv(64, 40, by=30)
    bx, by = c.bx, c.by
    a, b = (bx - 17, by - 5), (bx + 17, by - 12)
    pts = [a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 1), b]
    c.stroke(pts, [11, 11.5, 11], PAL["woodlight"])
    # estremita' sinistra: sezione con anelli
    m = c.mask_ellipse(a[0], a[1], 3.6, 5.6)
    c.paint(m, PAL["wood"][3])
    c.paint(c.mask_ellipse(a[0], a[1], 2.4, 3.8), PAL["wood"][2])
    c.paint(c.mask_ellipse(a[0], a[1], 1.2, 2.0), PAL["wood"][1])
    # nodi e venature
    for x in (bx - 8, bx + 2, bx + 9):
        y = (a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]))
        c.line(x, y - 3, x + 3, y - 3, PAL["woodlight"][0])
    if branch:
        c.stroke([(bx + 5, by - 14), (bx + 8, by - 20), (bx + 12, by - 24)], [4, 3.6, 3], PAL["woodlight"])
        c.paint(c.mask_ellipse(bx + 12.5, by - 24.5, 1.8, 1.6), PAL["wood"][3])
    if flip:
        c = c.flip()
    c.outline()
    c.shadow(kx=0.3, ky=0.12, base_rx=0, floor_only=False)
    return c


def sign(seed, text=False):
    c = Cv(40, 48, by=40)
    bx, by = c.bx, c.by
    c.stroke([(bx, by), (bx + 0.3, by - 9), (bx + 0.5, by - 18)], [2.6, 2.4, 2.2], PAL["wood"])
    board = c.mask_poly([(bx - 8, by - 26), (bx + 9, by - 27), (bx + 9, by - 17), (bx - 8, by - 16)])
    c.shade(board, PAL["woodlight"], steps=(-0.5, 0.0, 0.5))
    for yy_ in (-22, -19):
        c.line(bx - 6, by + yy_ + 1, bx + 7, by + yy_, PAL["woodlight"][1])
    c.px(bx - 7, by - 25, PAL["metal"][2])
    c.px(bx + 8, by - 26, PAL["metal"][2])
    mound = c.mask_ellipse(bx + 0.5, by, 6, 2.4) & (c.yy >= by - 1)
    c.shade(mound, PAL["sand"], steps=(-0.6, -0.1, 0.5))
    c.outline()
    c.shadow(kx=0.45, ky=0.12, base_rx=5, shrink=0.8)
    return c


def barrel(seed, open_=True, flip=False):
    c = Cv(40, 48, by=38)
    bx, by = c.bx, c.by
    rings = [(0, 8.4), (3, 9.6), (9, 10.4), (15, 9.8), (22, 8.8)]
    top_y = by - 24
    pts_l = [(bx - r, by - 24 + 24 * (1 - i / 24)) for i, r in [(0, 8.4)]]
    body = c.mask_ellipse(bx, by - 12, 10.2, 13.5) & (c.yy > top_y + 2) & (c.yy < by)
    body |= c.mask_poly([(bx - 9, top_y + 2), (bx + 9, top_y + 2), (bx + 10, by - 12), (bx + 8, by - 1), (bx - 8, by - 1), (bx - 10, by - 12)])
    c.shade(body, PAL["woodlight"], cx=bx, cy=by - 12, rx=11, ry=40, steps=(-0.45, -0.05, 0.35))
    for k in range(-3, 4):  # doghe
        x = bx + k * 3
        c.paint(body & (c.xx == x), PAL["wood"][1] if k > 0 else PAL["woodlight"][1])
    for yy_ in (top_y + 6, by - 7):
        band = body & (c.yy >= yy_) & (c.yy < yy_ + 3)
        c.shade(band, PAL["metal"], steps=(-0.6, -0.1, 0.4))
    rim = c.mask_ellipse(bx, top_y + 2, 9.6, 3.6)
    c.paint(rim, PAL["woodlight"][3])
    c.paint(c.mask_ellipse(bx, top_y + 2.4, 7.6, 2.6), PAL["wood"][0] if open_ else PAL["woodlight"][2])
    if not open_:
        c.line(bx - 6, top_y + 2, bx + 6, top_y + 3, PAL["woodlight"][1])
    # corda
    c.stroke([(bx - 4, top_y + 3), (bx - 11, top_y + 10), (bx - 10, top_y + 17)], [2.2, 2.2, 2.2], PAL["cream"])
    c.px(bx - 11, top_y + 13, PAL["cream"][0])
    if flip:
        c = c.flip()
    c.outline()
    c.shadow(kx=0.4, ky=0.14, base_rx=10, shrink=0.8)
    return c


def towel(pal_name, second, seed, pattern="stripes", angle=0, w=38, h=26):
    """Telo steso a terra, visto in prospettiva (25°): parallelogramma con frange; ruotato di poco."""
    rng = random.Random(seed)
    c = Cv(w + 20, h + 20, by=h // 2 + 12)
    ox, oy = 10, 8
    sk = angle
    p0 = (ox + 3 + sk, oy)
    p1 = (ox + w + sk, oy)
    p2 = (ox + w - 3, oy + h * 0.62)
    p3 = (ox, oy + h * 0.62)
    m = c.mask_poly([p0, p1, p2, p3])
    pal = PAL[pal_name]
    pal2 = PAL[second]
    ys, xs = np.nonzero(m)
    c.paint(m, pal[2])
    u = (c.xx - ox) / w
    if pattern == "stripes":
        for i in range(7):
            band = m & (u >= i / 7) & (u < (i + 1) / 7)
            c.paint(band, (pal if i % 2 == 0 else pal2)[2])
    elif pattern == "hstripes":
        v = (c.yy - oy) / (h * 0.62)
        for i in range(4):
            band = m & (v >= i / 4) & (v < (i + 1) / 4)
            c.paint(band, (pal if i % 2 == 0 else pal2)[2])
    elif pattern == "check":
        v = (c.yy - oy) / (h * 0.62)
        for i in range(8):
            for j in range(3):
                if (i + j) % 2 == 0:
                    band = m & (u >= i / 8) & (u < (i + 1) / 8) & (v >= j / 3) & (v < (j + 1) / 3)
                    c.paint(band, pal2[2])
    elif pattern == "solid":
        v = (c.yy - oy) / (h * 0.62)
        c.paint(m & (v > 0.36) & (v < 0.5), pal2[2])
        c.paint(m & (v > 0.7) & (v < 0.84), pal2[2])
    # luce: bordo superiore/sinistro chiaro, inferiore/destro scuro
    top = m & (c.yy <= oy + 1)
    left = m & (c.xx <= ox + 3 + (c.yy - oy) * (-3 / (h * 0.62)) * -1)
    for yy_, xx_ in zip(*np.nonzero(m)):
        pass
    arr = c.a
    edge_b = m & ~np.roll(m, -1, axis=0)
    edge_r = m & ~np.roll(m, -1, axis=1)
    for mm, d in ((edge_b, -1), (edge_r, -1)):
        ys_, xs_ = np.nonzero(mm)
        for y_, x_ in zip(ys_, xs_):
            col = tuple(arr[y_, x_, :3])
            # scurisce di un tono
            for pl in (pal, pal2):
                if col == pl[2]:
                    arr[y_, x_, :3] = pl[1]
    edge_t = m & ~np.roll(m, 1, axis=0)
    for y_, x_ in zip(*np.nonzero(edge_t)):
        col = tuple(arr[y_, x_, :3])
        for pl in (pal, pal2):
            if col == pl[2]:
                arr[y_, x_, :3] = pl[3]
    c.outline()
    # frange alle estremita' corte (dopo il contorno, cosi' restano chiare)
    for side in (0, 1):
        for k in range(5):
            t = (k + 0.5) / 5
            if side == 0:
                x0 = p0[0] + (p3[0] - p0[0]) * t
                y0 = p0[1] + (p3[1] - p0[1]) * t
                for dx in (1, 2, 3):
                    c.px(round(x0 - dx), round(y0), PAL["cream"][2] if dx < 3 else PAL["cream"][1])
            else:
                x0 = p1[0] + (p2[0] - p1[0]) * t
                y0 = p1[1] + (p2[1] - p1[1]) * t
                for dx in (1, 2, 3):
                    c.px(round(x0 + dx), round(y0), PAL["cream"][2] if dx < 3 else PAL["cream"][1])
    c.shadow(kx=0.0, ky=0.0, floor_only=True, offset=(1, 2))
    return c


# ---------------------------------------------------------------- catalogo
def catalog():
    items = {}

    def add(name, cv, solid=None, group="deco"):
        items[name] = dict(cv=cv, solid=solid, group=group)

    # palme
    add("palm_tall_a", palm("tall", 1), solid=(5, 0), group="palm")
    add("palm_tall_b", palm("tall", 2, flip=True, pal_name="leafdark"), solid=(5, 0), group="palm")
    add("palm_tall_c", palm("tall", 5, pal_name="leafyellow"), solid=(5, 0), group="palm")
    add("palm_lean_a", palm("lean", 3), solid=(5, 0), group="palm")
    add("palm_lean_b", palm("lean", 4, flip=True, pal_name="leafyellow"), solid=(5, 0), group="palm")
    add("palm_bent_a", palm("bent", 6, pal_name="leafdark"), solid=(5, 0), group="palm")
    add("palm_bent_b", palm("bent", 7, flip=True), solid=(5, 0), group="palm")
    add("palm_young_a", palm("young", 8), solid=None, group="palm")
    add("palm_young_b", palm("young", 9, flip=True, pal_name="leafyellow"), solid=None, group="palm")
    # rocce
    add("rock_pebble_a", rock(8, 5, 11, facets=2), group="rock")
    add("rock_pebble_b", rock(9, 6, 12, "rocksand", facets=2), group="rock")
    add("rock_pebble_c", rock(7, 5, 13, facets=2, flip=True), group="rock")
    add("rock_small_a", rock(13, 9, 14, facets=3), solid=(0.55, 0.5), group="rock")
    add("rock_small_b", rock(14, 10, 15, "rocksand", facets=3, flip=True), solid=(0.55, 0.5), group="rock")
    add("rock_med_a", rock(22, 14, 16, facets=4, grass=1), solid=(0.55, 0.5), group="rock")
    add("rock_med_b", rock(24, 15, 17, "rocksand", facets=4, grass=2, flip=True), solid=(0.55, 0.5), group="rock")
    add("rock_big_a", rock(34, 22, 18, facets=5, grass=2), solid=(0.55, 0.5), group="rock")
    add("rock_big_b", rock(32, 20, 19, "rocksand", facets=5, grass=1, flip=True), solid=(0.55, 0.5), group="rock")
    add("rock_tall_a", rock(24, 34, 20, facets=6, grass=2), solid=(0.55, 0.5), group="rock")
    # fiori
    for i, k in enumerate(["hibiscus_red", "hibiscus_orange", "hibiscus_pink", "daisy_yellow", "daisy_white", "daisy_blue",
                           "pink_cluster", "white_cluster", "purple_cluster"]):
        add("flower_" + k, flower(k, 30 + i), group="flower")
    # cespugli
    add("bush_broad_a", bush("broad", 40), solid=(0.4, 1), group="bush")
    add("bush_broad_b", bush("broad", 41, "leafdark", flip=True), solid=(0.4, 1), group="bush")
    add("bush_round_a", bush("round", 42), solid=(0.4, 1), group="bush")
    add("bush_round_b", bush("round", 43, "leafyellow", flip=True), solid=(0.4, 1), group="bush")
    add("bush_spiky_a", bush("spiky", 44), solid=(0.3, 1), group="bush")
    add("bush_spiky_b", bush("spiky", 45, "leafyellow", flip=True), solid=(0.3, 1), group="bush")
    add("bush_small_a", bush("small", 46), solid=(0.45, 0.5), group="bush")
    add("bush_small_b", bush("small", 47, "leafdark", flip=True), solid=(0.45, 0.5), group="bush")
    # conchiglie e animaletti
    for i, k in enumerate(["spiral", "cone", "starfish", "starfish_pink", "sanddollar", "clam"]):
        add("shell_" + k, shellprop(k, 50 + i), group="shell")
    for pose in range(4):  # granchio animato: fotogrammi shell_crab_0..3 (stessa cella e stesso punto d'appoggio)
        add(f"shell_crab_{pose}", shellprop("crab", 56, pose), solid=(5, 0), group="shell")
    # ombrelloni
    for nm, pal_, sec in [("red", "red", "cream"), ("blue", "blue", "cream"), ("yellow", "yellow", "white"), ("green", "green", "cream"),
                          ("teal", "teal", "cream"), ("orange", "orange", "cream"), ("pink", "pink", "cream")]:
        add("umbrella_closed_" + nm, umbrella_closed(pal_, 60), solid=(4, 0), group="object")
    for nm, pal_, sec, pat, lean, tilt in [("red", "red", "canvas", "stripes", 0, 0), ("blue", "blue", "canvas", "stripes", 1, 3),
                                          ("yellow", "yellow", "canvas", "stripes", -1, -3), ("green", "green", "canvas", "stripes", 0, 4),
                                          ("teal", "teal", "canvas", "solid", 1, -4), ("orange", "orange", "canvas", "stripes", -1, 2),
                                          ("pink", "pink", "canvas", "stripes", 0, -2)]:
        add("umbrella_open_" + nm, umbrella_open(pal_, 70, pat, lean=lean, second=sec, tilt=tilt), solid=(4, 0), group="object")
    # tavole da surf: piantate dritte, inclinate (sinistra/destra) e sdraiate
    add("surf_hibiscus_stuck", surfboard("hibiscus", 80, "cream", "stuck"), solid=(5, 0), group="object")
    add("surf_wave_stuck", surfboard("wave", 81, "yellow", "stuck", tilt=3), solid=(5, 0), group="object")
    add("surf_stripes_lean_l", surfboard("stripes", 82, "white", "lean", tilt=-16), solid=(5, 0), group="object")
    add("surf_bolt_lean_r", surfboard("bolt", 83, "teal", "lean", tilt=14), solid=(5, 0), group="object")
    add("surf_blue_lean_l", surfboard("stripes", 84, "blue", "lean", tilt=-9), solid=(5, 0), group="object")
    add("surf_hibiscus_lean_r", surfboard("hibiscus", 85, "white", "lean", tilt=18), solid=(5, 0), group="object")
    add("surf_wave_flat", surfboard("wave", 86, "teal", "flat", tilt=-12), group="towel")
    add("surf_stripes_flat", surfboard("stripes", 87, "orange", "flat", tilt=8), group="towel")
    add("surf_hibiscus_flat", surfboard("hibiscus", 88, "cream", "flat", tilt=-32), group="towel")
    add("surf_bolt_flat", surfboard("bolt", 89, "yellow", "flat", tilt=24), group="towel")
    # tronchi, cartello, botti
    add("log_a", log(90), solid=(9, 1), group="object")
    add("log_b", log(91, flip=True, branch=False), solid=(9, 1), group="object")
    add("sign_blank", sign(92), solid=(4, 0), group="object")
    add("barrel_open", barrel(93, True), solid=(9, 0.5), group="object")
    add("barrel_closed", barrel(94, False, flip=True), solid=(9, 0.5), group="object")
    # teli
    add("towel_red", towel("red", "cream", 100, "stripes", angle=3), group="towel")
    add("towel_blue", towel("blue", "cream", 101, "stripes", angle=-3), group="towel")
    add("towel_yellow", towel("yellow", "orange", 102, "hstripes", angle=2), group="towel")
    add("towel_green", towel("green", "cream", 103, "check", angle=-2), group="towel")
    add("towel_teal", towel("teal", "yellow", 104, "solid", angle=4), group="towel")
    add("towel_pink", towel("pink", "cream", 105, "stripes", angle=-4), group="towel")
    add("towel_orange", towel("orange", "cream", 106, "hstripes", angle=0), group="towel")
    return items


def hull(points):
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def footprint(img, feet, rows, shrink=0):
    """Poligono (coordinate relative al punto d'appoggio, in pixel d'arte) dell'impronta a terra: inviluppo convesso dei pixel
    di corpo (alpha 255, ombra esclusa) nelle ultime `rows` righe, con i bordi esterni ridotti di `shrink` px."""
    body = img[..., 3] == 255
    ys, xs = np.nonzero(body)
    ymax = ys.max()
    sel = [(x, y) for x, y in zip(xs, ys) if y > ymax - rows]
    pts = []
    for x, y in sel:
        pts += [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]
    poly = hull(pts)
    cx = sum(p[0] for p in poly) / len(poly)
    out = []
    for x, y in poly:
        x -= np.sign(x - cx) * shrink
        out.append([round(float(x - feet[0]), 2), round(float(y - feet[1]), 2)])
    return out


def pack(items, width=640, pad=2):
    """Impacchetta le celle in righe (altezze decrescenti). Restituisce atlante RGBA e metadati."""
    cells = []
    for name, it in items.items():
        img, feet = it["cv"].crop()
        cells.append((name, img, feet, it))
    fr = [c for c in cells if c[0].startswith("shell_crab_")]
    if fr:  # fotogrammi animati: stessa cella e stesso punto d'appoggio, cosi' l'animazione non salta
        fx, fy = max(c[2][0] for c in fr), max(c[2][1] for c in fr)
        W = fx + max(c[1].shape[1] - c[2][0] for c in fr)
        H = fy + max(c[1].shape[0] - c[2][1] for c in fr)
        padded = []
        for name, img, feet, it in fr:
            cell = np.zeros((H, W, 4), np.uint8)
            cell[fy - feet[1]:fy - feet[1] + img.shape[0], fx - feet[0]:fx - feet[0] + img.shape[1]] = img
            padded.append((name, cell, (fx, fy), it))
        cells = [c for c in cells if not c[0].startswith("shell_crab_")] + padded
    cells.sort(key=lambda c: -c[1].shape[0])
    x = y = rowh = 0
    place = {}
    for name, img, feet, it in cells:
        h, w = img.shape[:2]
        if x + w + pad > width:
            x, y, rowh = 0, y + rowh + pad, 0
        place[name] = (x, y, w, h, feet, img, it)
        x += w + pad
        rowh = max(rowh, h)
    H = y + rowh + pad
    atlas = np.zeros((H, width, 4), np.uint8)
    meta = {}
    for name, (x, y, w, h, feet, img, it) in place.items():
        atlas[y:y + h, x:x + w] = img
        meta[name] = {"rect": [x, y, w, h], "feet": [int(feet[0]), int(feet[1])], "group": it["group"]}
        if it["solid"]:
            rows, shrink = it["solid"]
            body_h = int((img[..., 3] == 255).any(axis=1).sum())
            if isinstance(rows, float):  # frazione dell'altezza del corpo
                rows = max(3, round(body_h * rows))
            meta[name]["footprint"] = footprint(img, feet, rows, shrink)
    return atlas, meta


def sheet(atlas, meta, scale=4):
    """Anteprima su sabbia (palette del terreno), con ombra visibile e punto d'appoggio."""
    names = sorted(meta, key=lambda n: (meta[n]["group"], n))
    colw = 0
    bg = np.zeros((1, 1, 4), np.uint8)
    cols = 6
    cell_w, cell_h = 120, 128
    rows = (len(names) + cols - 1) // cols
    W, H = cols * cell_w, rows * cell_h
    out = np.zeros((H, W, 4), np.uint8)
    out[...] = (*PAL["sand"][2], 255)
    for i, n in enumerate(names):
        r, c_ = divmod(i, cols)
        x, y, w, h = meta[n]["rect"]
        fx, fy = meta[n]["feet"]
        ox = c_ * cell_w + cell_w // 2 - fx
        oy = r * cell_h + cell_h - 14 - fy
        spr = atlas[y:y + h, x:x + w]
        for yy in range(h):
            for xx in range(w):
                px_ = spr[yy, xx]
                X, Y = ox + xx, oy + yy
                if px_[3] and 0 <= X < W and 0 <= Y < H:
                    a = px_[3] / 255
                    out[Y, X, :3] = (px_[:3] * a + out[Y, X, :3] * (1 - a)).astype(np.uint8)
    im = Image.fromarray(out).resize((W * scale // 2, H * scale // 2), Image.NEAREST)
    return im


if __name__ == "__main__":
    outdir = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(outdir, exist_ok=True)
    items = catalog()
    atlas, meta = pack(items)
    Image.fromarray(atlas).save(os.path.join(outdir, "props_atlas.png"))
    Image.fromarray(atlas).resize((atlas.shape[1] * 4, atlas.shape[0] * 4), Image.NEAREST).save(os.path.join(outdir, "props_atlas_x4.png"))
    sheet(atlas, meta).save(os.path.join(outdir, "props_sheet_x4.png"))
    with open(os.path.join(outdir, "props.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    al = np.unique(atlas[..., 3])
    print("ok", atlas.shape, len(meta), "alpha", al)
