"""Scrive le scene dei singoli props (Objects/Props/<nome>.tscn) e Scenes/tutorial_props.tscn, che le istanzia nel livello tutorial.

Scena di un prop: radice Node2D (StaticBody2D per i solidi, layer 1, gruppo solid_prop: la palla di sabbia ci scoppia contro) con due
Sprite2D, corpo (materiale ground_body) e ombra (ground_shadow, Z -1 assoluto), sulla stessa regione di Assets/Props/props_atlas.png
(contratto alpha 0/97/255, Docs/GODOT.md §9) e un CollisionPolygon2D ricavato dal corpo dello sprite (props.json, campo footprint).
Teli, conchiglie, fiori e ciottoli sono decalcomanie a Z -2 assoluto (sempre sotto i personaggi). Il granchio e' un AnimatedSprite2D.
L'origine della scena sta 52 px SOPRA i piedi (come i personaggi): cosi' nel Y-sort del livello si ordina per y come loro. Per piazzare
un prop con i piedi in (X, Y) basta posizionare l'istanza in (X, Y - 52). Rettangoli, punto d'appoggio e collisioni vengono da
Tools/pixelorama/props.json (prodotto da Tools/pixelorama/props_gen.py).

Disposizione (LAYOUT): coordinate in TILE (64 px) rispetto al centro della camera fissa, cioe' all'origine della mappa: la scena
tutorial_props si istanzia in (800, -560) come Scenes/tutorial_map.tscn. y positivo verso il basso. Inquadratura: x da -22,5 a 22,5,
y da -12,5 a 12,5 (le bande dell'HUD coprono circa 1,7 tile in alto e in basso). Il ragazzo sta in (0,0); il negozio in (-4,5, -6,1)
con l'area frontale sotto di lui: tenere libere queste zone dai solidi. La baia (acqua) e' in alto a destra: x >= 17 per y <= -8.

CONVENZIONE DI POSIZIONE (importante): l'origine di ogni scena sta 52 px SOPRA i piedi. Per mettere un prop con i piedi in (X, Y)
si posiziona l'istanza in (X, Y - 52). Nel test di collisione la nemica va posta in prop.global_position + Vector2(-300, 0)
(stessa altezza dell'origine, NON +52).

Uso:  python props_gen.py <radice_del_progetto> [--scenes] [--layout] [--force]
  (nessun flag)  scrive solo le scene dei props che non esistono ancora in Objects/Props/ (nuovi props in props.json); non tocca
                 le scene esistenti ne' Scenes/tutorial_props.tscn, quindi i ritocchi fatti a mano restano.
  --scenes       riscrive TUTTE le scene dei props (serve quando l'atlante o props.json cambiano: i rettangoli si spostano).
  --layout       riscrive Scenes/tutorial_props.tscn da LAYOUT, cancellando i ritocchi a mano. Se il file esiste rifiuta
                 (exit 1) a meno di --force; se non esiste lo scrive.
  --force        autorizza la sovrascrittura di tutorial_props.tscn con --layout.
All'avvio controlla che props.json esista, che ogni nome di LAYOUT sia un prop e che ogni rect stia nell'atlante.
"""
import json
import os
import struct
import sys

TILE = 64
SORT_OFFSET = 52  # i personaggi hanno l'origine 52 px sopra i piedi

# Criterio di posizione (spiaggia libera italiana, non stabilimento): dal mare verso l'interno la costa ha la linea delle mareggiate
# (ciottoli, conchiglie, tronco spiaggiato) e gli scogli sulla punta della baia; la sabbia aperta a meta' spiaggia; la macchia
# (palme, cespugli, fiori, sempre a gruppi e con i cespugli ai piedi delle palme) sul bordo opposto al mare, cioe' a sinistra e in
# basso a sinistra. Gli ombrelloni sono due soli gruppi (con telo e tavola vicini), non in fila: uno a destra, sulla sabbia aperta
# tra mare e macchia, uno a sinistra in basso, vicino alla macchia per l'ombra. Niente solidi tra il negozio e il ragazzo e nessuna
# coppia di solidi a meno di ~2,5 tile (le nemiche restano incastrate nelle tasche strette).
# (nome del prop, tile x, tile y dei piedi).
LAYOUT = [
    # --- macchia in alto a sinistra: palmeto con cespuglio e fiori ai piedi
    ("palm_tall_a", -19.6, -8.6), ("palm_lean_b", -17.9, -7.2), ("palm_young_a", -16.6, -8.2),
    ("bush_round_a", -18.8, -6.4), ("flower_hibiscus_red", -17.0, -6.0),
    # --- due palme dietro il negozio, con cespuglio e margherite
    ("palm_tall_b", -10.2, -9.2), ("bush_round_a", -11.6, -9.6), ("flower_daisy_white", -10.6, -8.2),
    # --- macchia a sinistra
    ("bush_spiky_a", -21.8, -2.6), ("flower_daisy_blue", -20.8, -1.6),
    # --- macchia in basso a sinistra
    ("palm_tall_b", -20.6, 7.4), ("palm_bent_b", -18.6, 9.6), ("bush_round_b", -21.6, 9.8), ("bush_small_b", -17.0, 10.3),
    # --- macchia in basso
    ("palm_lean_b", -8.6, 10.9), ("bush_spiky_a", -6.6, 10.9), ("flower_white_cluster", -5.0, 10.2),
    # --- in alto
    ("palm_bent_b", 7.4, -10.2), ("bush_broad_b", 6.0, -10.4),
    # --- cartello sulla sabbia aperta in alto a destra, lontano dal ragazzo e dalle traiettorie delle nemiche
    ("sign_blank", 8.0, -5.0),
    # --- punta della baia: scogli a gruppo, ciottoli e conchiglie sulla linea delle mareggiate, tronco spiaggiato lungo la riva
    ("rock_tall_a", 18.0, -7.3), ("rock_big_a", 19.5, -6.9), ("rock_med_b", 21.1, -6.5), ("rock_pebble_c", 16.5, -6.9),
    ("shell_starfish", 16.4, -8.8), ("shell_cone", 21.9, -5.3), ("shell_crab", 18.8, -5.3), ("log_a", 20.0, -3.9),
    # --- ombrelloni a destra: due aperti, due teli e una tavola piantata
    ("umbrella_open_yellow", 16.6, 1.8), ("towel_green", 15.0, 3.0), ("surf_stripes_lean_l", 14.0, 0.8),
    ("umbrella_open_blue", 19.8, 3.6), ("towel_blue", 18.4, 5.0),
    # --- ombrelloni a sinistra, vicino alla macchia: uno aperto, uno chiuso, un telo e una tavola
    ("umbrella_open_red", -12.6, 5.4), ("towel_red", -11.0, 6.7),("surf_hibiscus_lean_r", -14.8, 6.4),
]


# Animati: nome del prop -> (fotogrammi di props.json con durata relativa, fps). Corpo e ombra sono due AnimatedSprite2D in sincronia.
ANIMS = {
    "shell_crab": ([("shell_crab_0", 3), ("shell_crab_1", 1), ("shell_crab_0", 2), ("shell_crab_3", 1), ("shell_crab_0", 2), ("shell_crab_2", 1)], 3),
}
PROPS_DIR = os.path.join("Objects", "Props")
RES_PROPS = "res://Objects/Props/"


def prop_info(meta, name):
    """Metadati del prop (per i granchi animati, quelli del primo fotogramma)."""
    return meta[ANIMS[name][0][0][0] if name in ANIMS else name]


def prop_names(meta):
    frames = {f for seq, _ in ANIMS.values() for f, _ in seq}
    return [n for n in meta if n not in frames] + list(ANIMS)


def prop_scene(meta, name):
    """Testo della scena di un singolo prop: radice all'altezza dei personaggi (52 px sopra i piedi), cosi' si ordina per y come loro."""
    anim = name in ANIMS
    m = prop_info(meta, name)
    fx, fy = m["feet"]
    rx, ry, rw, rh = m["rect"]
    solid = m.get("footprint")
    # decalcomanie: stanno sul livello del terreno (sotto i personaggi), cosi' nessun personaggio sembra "dietro" una stella marina
    decal = m["group"] in ("towel", "shell", "flower") or name.startswith("rock_pebble")
    out = ['[gd_scene format=3]', '',
           '[ext_resource type="Texture2D" path="res://Assets/Props/props_atlas.png" id="1_atlas"]',
           '[ext_resource type="Material" path="res://Assets/Shaders/ground_body.tres" id="2_body"]',
           '[ext_resource type="Material" path="res://Assets/Shaders/ground_shadow.tres" id="3_shadow"]', '']
    if anim:
        seq, fps = ANIMS[name]
        for fr in dict.fromkeys(f for f, _ in seq):
            frx, fry, frw, frh = meta[fr]["rect"]
            out += [f'[sub_resource type="AtlasTexture" id="AtlasTexture_{fr}"]', 'atlas = ExtResource("1_atlas")',
                    f"region = Rect2({frx}, {fry}, {frw}, {frh})", ""]
        frames = ", ".join('{\n"duration": %s,\n"texture": SubResource("AtlasTexture_%s")\n}' % (d, f) for f, d in seq)
        out += ['[sub_resource type="SpriteFrames" id="SpriteFrames_prop"]',
                'animations = [{\n"frames": [' + frames + '],\n"loop": true,\n"name": &"default",\n"speed": %s\n}]' % fps, ""]
    out.append(f'[node name="{name}" type="{"StaticBody2D" if solid else "Node2D"}"' + (' groups=["solid_prop"]]' if solid else ']'))
    if solid:  # i solidi fermano Player e nemiche (layer 1) e la palla di sabbia ci scoppia contro (gruppo solid_prop)
        out += ['collision_layer = 1', 'collision_mask = 0']
    out += ['metadata/_edit_group_ = true', ""]

    def sprite_node(sname, material, extra=()):
        nonlocal out
        out.append(f'[node name="{sname}" type="{"AnimatedSprite2D" if anim else "Sprite2D"}" parent="."]')
        out.append('texture_filter = 1')
        out.extend(extra)
        out += [f"position = Vector2(0, {SORT_OFFSET})", 'scale = Vector2(4, 4)', f'material = ExtResource("{material}")',
                'centered = false', f"offset = Vector2({-fx}, {-fy})"]
        if anim:
            out += ['sprite_frames = SubResource("SpriteFrames_prop")', 'autoplay = "default"']
        else:
            out += ['texture = ExtResource("1_atlas")', 'region_enabled = true', f"region_rect = Rect2({rx}, {ry}, {rw}, {rh})"]
        out.append("")

    if decal:
        if m["group"] != "towel":  # i teli hanno gia' l'ombra nello sprite (scartata dal materiale del corpo)
            sprite_node("Shadow", "3_shadow", ['z_index = -1', 'z_as_relative = false'])
        sprite_node("Sprite2D", "2_body", ['z_index = -2', 'z_as_relative = false'])
    else:
        sprite_node("Shadow", "3_shadow", ['z_index = -1', 'z_as_relative = false'])
        sprite_node("Sprite2D", "2_body")
    if solid:
        pts = ", ".join(f"{p[0] * 4:g}, {p[1] * 4:g}" for p in solid)
        out += ['[node name="CollisionPolygon2D" type="CollisionPolygon2D" parent="."]', f"position = Vector2(0, {SORT_OFFSET})",
                f"polygon = PackedVector2Array({pts})", ""]
    return "\n".join(out)


def write_prop_scenes(root, meta, all_scenes):
    """Una scena per ogni prop in Objects/Props/<nome>.tscn, riutilizzabile in qualsiasi livello. Senza all_scenes salta le esistenti."""
    d = os.path.join(root, PROPS_DIR)
    os.makedirs(d, exist_ok=True)
    written = skipped = 0
    for name in prop_names(meta):
        path = os.path.join(d, name + ".tscn")
        if os.path.exists(path) and not all_scenes:
            skipped += 1
            continue
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(prop_scene(meta, name))
        written += 1
    print("scritte", written, "scene, saltate", skipped, "in", d)


def png_size(path):
    """(larghezza, altezza) dall'intestazione IHDR del PNG, o None se illeggibile."""
    try:
        with open(path, "rb") as f:
            h = f.read(24)
        if h[:8] == b"\x89PNG\r\n\x1a\n" and h[12:16] == b"IHDR":
            return struct.unpack(">II", h[16:24])
    except OSError:
        pass
    return None


def check(root, meta):
    """Esce con messaggio chiaro se LAYOUT cita props inesistenti o se un rect sfora l'atlante."""
    names = set(prop_names(meta))
    bad = sorted({n for n, _, _ in LAYOUT if n not in names})
    if bad:
        sys.exit("ERRORE: in LAYOUT props non presenti in props.json: " + ", ".join(bad))
    size = png_size(os.path.join(root, "Assets", "Props", "props_atlas.png"))
    if size:
        for n, m in meta.items():
            x, y, w, h = m["rect"]
            if x < 0 or y < 0 or x + w > size[0] or y + h > size[1]:
                sys.exit(f"ERRORE: rect di '{n}' {m['rect']} fuori dall'atlante {size[0]}x{size[1]}")


def write_layout(root, meta):
    """Scrive Scenes/tutorial_props.tscn, che istanzia i props nelle posizioni di LAYOUT."""
    used = list(dict.fromkeys(n for n, _, _ in LAYOUT))
    lines = ['[gd_scene format=3]', '']
    lines += [f'[ext_resource type="PackedScene" path="{RES_PROPS}{n}.tscn" id="{i + 1}_{n}"]' for i, n in enumerate(used)]
    lines += ['', '[node name="TutorialProps" type="Node2D"]', 'y_sort_enabled = true', ""]
    ids = {n: f"{i + 1}_{n}" for i, n in enumerate(used)}
    counts = {}
    for name, tx, ty in LAYOUT:
        counts[name] = counts.get(name, 0) + 1
        x, y = round(tx * TILE, 2), round(ty * TILE - SORT_OFFSET, 2)
        lines += [f'[node name="{name}_{counts[name]}" parent="." instance=ExtResource("{ids[name]}")]', f"position = Vector2({x:g}, {y:g})", ""]
    out = os.path.join(root, "Scenes", "tutorial_props.tscn")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    solids = sum(1 for n, _, _ in LAYOUT if prop_info(meta, n).get("footprint"))
    print("scritto", out, "- props", len(LAYOUT), "solidi", solids)


def main(argv):
    flags = {a for a in argv if a.startswith("--")}
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1 or flags - {"--scenes", "--layout", "--force"}:
        sys.exit(__doc__.split("Uso:", 1)[1])
    root = args[0]
    pj = os.path.join(root, "Tools", "pixelorama", "props.json")
    if not os.path.exists(pj):
        sys.exit("ERRORE: manca " + pj)
    meta = json.load(open(pj, encoding="utf-8"))
    check(root, meta)
    layout = os.path.join(root, "Scenes", "tutorial_props.tscn")
    if "--layout" in flags and os.path.exists(layout) and "--force" not in flags:
        sys.exit("ERRORE: " + layout + " esiste gia': --layout cancellerebbe i ritocchi a mano. Usa --layout --force per sovrascrivere.")
    write_prop_scenes(root, meta, "--scenes" in flags)
    if "--layout" in flags:
        write_layout(root, meta)


if __name__ == "__main__":
    main(sys.argv[1:])
