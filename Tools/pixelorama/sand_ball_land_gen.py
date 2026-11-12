# Genera le griglie di caratteri dell'animazione "land" della palla di sabbia (8 frame 24x24, da incollare in Pixelorama con draw_pixels).
# Palette: o #3a1418 (contorno), d #8a6a3e, m #b8925a, l #e3c084, h #f6e2b0. Simmetrica: il nodo ruota con la direzione di lancio.
import json, math
N = 24
C = (11.5, 11.5)

def blank():
    return [['.'] * N for _ in range(N)]

def shade(dx, dy, r, flat=False):
    l = ((-dx) + (-dy)) / (math.sqrt(2) * max(r, 1.0))      # >0: alto-sinistra
    if flat:
        return 'l' if l > 0.1 else 'm'
    return 'h' if l > 0.55 else ('l' if l > 0.1 else ('m' if l > -0.45 else 'd'))

def ellipse(g, cx, cy, rx, ry, flat=False, outline=True):
    inside = set()
    for y in range(N):
        for x in range(N):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                inside.add((x, y)); g[y][x] = shade(x - cx, y - cy, max(rx, ry), flat)
    if outline:
        for (x, y) in list(inside):
            for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                if 0 <= nx < N and 0 <= ny < N and (nx, ny) not in inside and g[ny][nx] == '.':
                    g[ny][nx] = 'o'

def grain(g, cx, cy, w, h, outline=True):
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    cells = [(x0 + i, y0 + j) for i in range(w) for j in range(h)]
    for x, y in cells:
        if 0 <= x < N and 0 <= y < N: g[y][x] = 'l' if (x - x0 + y - y0) == 0 else 'm'
    if outline:
        for x, y in cells:
            for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                if 0 <= nx < N and 0 <= ny < N and (nx, ny) not in cells and g[ny][nx] == '.':
                    g[ny][nx] = 'o'

# granelli: (angolo in gradi, fattore del raggio), irregolari per non sembrare una figura simmetrica
GRAINS = [(15, 1.0), (62, 0.85), (110, 1.1), (160, 0.9), (205, 1.05), (250, 0.8), (295, 1.1), (340, 0.95)]

def scatter(g, radius, w, h, outline, dark):
    for ang, f in GRAINS:
        a = math.radians(ang)
        x, y = C[0] + radius * f * math.cos(a), C[1] + 1 + radius * f * 0.8 * math.sin(a)
        if dark:    # senza contorno: toni scuri, visibili sulla sabbia del terreno
            x0, y0 = int(round(x - w / 2)), int(round(y - h / 2))
            for i in range(w):
                for j in range(h):
                    if 0 <= x0 + i < N and 0 <= y0 + j < N: g[y0 + j][x0 + i] = 'm' if i + j == 0 else 'd'
        else:
            grain(g, x, y, w, h, outline)

frames = []
for r in (5.5, 4.8, 4.2):                       # 0-2: la palla si rimpicciolisce di poco (cade verso il basso)
    g = blank(); ellipse(g, C[0], C[1], r, r); frames.append(g)
g = blank(); ellipse(g, C[0], C[1] + 1.5, 5.6, 3.2, flat=True); frames.append(g)   # 3: schiacciata a terra
g = blank(); scatter(g, 6.0, 2, 2, True, False); ellipse(g, C[0], C[1] + 1.5, 3.0, 1.5, flat=True); frames.append(g)   # 4: scoppio
g = blank(); scatter(g, 8.5, 2, 2, False, True); ellipse(g, C[0], C[1] + 1.5, 2.2, 1.0, flat=True, outline=False); frames.append(g)   # 5
g = blank(); scatter(g, 10.0, 1, 2, False, True); frames.append(g)                 # 6: granelli sparsi
g = blank(); scatter(g, 11.0, 1, 1, False, True); frames.append(g)                 # 7: gli ultimi granelli

out = [["".join(r) for r in g] for g in frames]
json.dump(out, open("sand_ball_land.json", "w"))
if __name__ == "__main__":
    for i in (0, 2, 3, 4, 5):
        print(i); print("\n".join(out[i])); print()
