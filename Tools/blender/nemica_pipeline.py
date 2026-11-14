"""
Pipeline sprite Nemica (Beatch Slash!) - da eseguire DENTRO Blender 5.x con
Tools/blender/nemica.blend aperto (modello ricostruito dal concept della nemica,
capelli viola #7043A1, costume smeraldo).

Uso (Blender MCP execute_blender_code):
    exec(open(r"<percorso>/nemica_pipeline.py").read())
    build_enemy()     # rigenera enemy_spritesheet.png in Assets/Characters/Enemy
    # oppure consumare build_enemy_steps(): una posa nelle otto direzioni per next()

Riusa utilita', render e stile (toon 4 toni, contorno, occhi a pixel, ombra) di
blender_pipeline.py. Atlante: righe = gruppo*8 + direzione, colonne = frame (12).
Celle 64x64 con la stessa scala di pixel del Player; margine per chioma e caduta.
Gruppi: 0 = walk (8 frame), 1 = flirt (12 frame, posa ammiccante davanti al ragazzo),
2 = idle (6 frame, da ferma quando e' bloccata; riusa idle() del Player),
3 = dead (8 frame, caduta a sedere, non in loop: l'ultimo frame resta a terra; vedi fall()).
Direzioni (ordine righe): up, down, right, left, up_right, up_left, down_right, down_left.

Palette: capelli #2a1240 #4b2a78 #7043a1 #a97fd9; costume #16503a #25805a #3db57d #8de0b4.
Geometria e materiali provengono dal modello nemica.blend, ricostruito dal turnaround approvato.
"""
import bpy, os, math, numpy as np
exec(open(os.path.join(os.path.dirname(bpy.data.filepath), "blender_pipeline.py")).read()) if "build_all" not in globals() else None
PROJ = os.path.normpath(os.path.join(BLEND_DIR, "..", "..", "Assets", "Characters", "Enemy"))
DIR8 = [180, 0, 90, -90, 135, -135, 45, -45]
FLIRT_FRAMES = 12
SIZE, ORTHO = 64, 2.2*64/48
EYE_VISIBILITY_THRESHOLD, EYE_SKIN_FIT = .20, True


def walk_e(t):
    """Passo e busto del Player, con gomiti piegati e chioma mossa della nemica."""
    walk(t); P = pb(); s = math.sin(t)
    # Gambe, bacino e busto riusano il Player; il gesto resta nelle braccia e nella chioma.
    P["upper_arm.L"].rotation_euler = (R(18*s), 0, R(-9)); P["upper_arm.R"].rotation_euler = (R(-18*s), 0, R(9))
    P["forearm.L"].rotation_euler = (R(-45-10*max(0, -s)), 0, 0); P["forearm.R"].rotation_euler = (R(-45-10*max(0, s)), 0, 0)
    P["hair"].rotation_euler = (R(12+9*math.sin(2*t-1.2)), R(7*math.sin(t-0.9)), 0)


REST_FEET = None

def pin_feet(targets):
    """IK numerico in spazio rig: coscia (X,Z) + stinco (X) fissano la caviglia; piede tenuto piatto"""
    from mathutils import Matrix
    P = pb()
    def ankle(s):
        bpy.context.view_layer.update(); return P["foot."+s].head.copy()
    for s in "LR":
        th, sh = P["thigh."+s], P["shin."+s]
        def get(): return [th.rotation_euler.x, th.rotation_euler.z, sh.rotation_euler.x]
        def put(v): th.rotation_euler = (v[0], th.rotation_euler.y, v[1]); sh.rotation_euler = (v[2], 0, 0)
        for _ in range(40):
            e = ankle(s) - targets[s]
            if e.length < 0.001: break
            base = get(); cols = []
            for k in range(3):
                b = list(base); b[k] += 0.02; put(b); cols.append((ankle(s) - targets[s] - e)/0.02); put(base)
            J = Matrix(cols).transposed()          # minimi quadrati smorzati: regge anche la gamba quasi tesa
            d = J.transposed() @ ((J @ J.transposed() + Matrix.Identity(3)*0.002).inverted() @ (-e))
            put([b + max(-0.3, min(0.3, x)) for b, x in zip(base, d)])
        x, _, k = get(); P["foot."+s].rotation_euler = (-(x + k), 0, 0)

def flirt(t):
    """posa ammiccante da ferma, piedi piantati a terra: il peso passa da una gamba all'altra
    (bacino che si sposta, si abbassa e ruota), busto in contro-movimento, mano sul fianco,
    l'altra tra i capelli, testa inclinata"""
    global REST_FEET
    P = pb()
    if REST_FEET is None:
        clear_pose(); bpy.context.view_layer.update()
        REST_FEET = {s: P["foot."+s].head.copy() for s in "LR"}
    s, c = math.sin(t), math.cos(t); a = 0.5 + 0.5*math.sin(t - 0.6)
    P["hips"].location = (0.045*s, -0.055 - 0.012*c*c, -0.012*s)   # Y locale = verticale
    P["hips"].rotation_euler = (R(3), R(9*s), R(-6*s))
    P["spine"].rotation_euler = (R(5), R(-7*s), R(8*s)); P["chest"].rotation_euler = (R(2), R(-6*s), R(3*s))
    P["head"].rotation_euler = (R(-3), R(5*s), R(-7*s + 8*math.sin(t+0.8)))
    P["thigh.L"].rotation_euler = (R(-4), 0, 0); P["thigh.R"].rotation_euler = (R(-4), 0, 0)
    P["shin.L"].rotation_euler = (R(18), 0, 0); P["shin.R"].rotation_euler = (R(18), 0, 0)
    pin_feet(REST_FEET)
    # assi braccia (provati a vista): Z = abduzione (R +, L -), Z dell'avambraccio = piega verso il corpo (R -, L +)
    P["upper_arm.R"].rotation_euler = (0, 0, R(30+105*a)); P["forearm.R"].rotation_euler = (0, 0, R(-(10+70*a)))
    P["upper_arm.L"].rotation_euler = (R(-8), 0, R(-42)); P["forearm.L"].rotation_euler = (R(-10), 0, R(95))
    P["hair"].rotation_euler = (R(6+6*a+3*math.sin(2*t)), R(8*s), 0)


# Caduta a sedere (morte): 8 frame, non in loop. Ogni riga:
# (bacino giu', bacino indietro, spine X, chest X, head X, head Z, cosce X, cosce aperte Z, stinchi X,
#  piedi X, braccia X (indietro +), braccia aperte Z, avambracci X, capelli X)
FALL_FRAMES = 8
FALL = [
    (0.00, 0.00,  -4,  -4,  -6,   0,    0,  4,   0,    0,  -25, 35, -30, 18),   # sussulto: braccia in alto
    (-0.12, 0.02, -10, -6,  -8,   2,  -30,  5,  55,  -25,    0, 50, -20, 24),   # ginocchia che cedono
    (-0.30, 0.08, -18, -8, -10,   4,  -58,  6,  35,   -5,   25, 60, -10, 30),   # busto indietro, braccia a ventaglio
    (-0.50, 0.12, -22, -8,  -6,   5, -100,  8,  15,   25,   40, 45,  -5, 36),   # gambe all'aria prima dell'impatto
    (-0.58, 0.12, -12, -4,   4,   4,  -86, 10,   0,  -12,   55, 25,   0, 12),   # impatto sulla sabbia
    (-0.585, 0.12, -8, -2,   9,   6,  -84, 11,   4,  -14,   58, 20,   0,  4),   # rimbalzo
    (-0.585, 0.12, -6, -1,   7,   5,  -84, 11,   5,  -14,   58, 20,   0,  1),   # assestamento
    (-0.585, 0.12, -6,  0,   6,   6,  -84, 11,   5,  -14,   58, 20,   0,  0),   # seduta, stordita
]

def fall(i):
    """posa i (0..7) della caduta a sedere; l'ultima e' la posa che resta a terra"""
    dy, dz, sp, ch, hd, hz, th, tz, sh, ft, ua, uz, fa, hr = FALL[i]
    P = pb()
    P["hips"].location = (0, dy, dz)
    P["spine"].rotation_euler = (R(sp), 0, 0); P["chest"].rotation_euler = (R(ch), 0, 0)
    P["head"].rotation_euler = (R(hd), 0, R(hz))
    for s, g in (("L", -1), ("R", 1)):
        P["thigh."+s].rotation_euler = (R(th), 0, R(g*tz)); P["shin."+s].rotation_euler = (R(sh), 0, 0)
        P["foot."+s].rotation_euler = (R(ft), 0, 0)
        P["upper_arm."+s].rotation_euler = (R(ua), 0, R(g*uz)); P["forearm."+s].rotation_euler = (R(fa), 0, 0)
    P["hair"].rotation_euler = (R(hr), 0, 0)


def build_enemy():
    steps = build_enemy_steps()
    while True:
        try: next(steps)
        except StopIteration as done: return done.value


def build_enemy_steps():
    """Una posa per next(); il PNG viene scritto solo all'esaurimento del generatore."""
    global REST_FEET
    REST_FEET = None
    rig = bpy.data.objects["Rig"]; rig.animation_data_create(); rig.animation_data.action = None
    clear_pose()
    bpy.data.objects["SandBall"].hide_render = True
    sheet = np.zeros((32*SIZE, FLIRT_FRAMES*SIZE, 4))
    for g, (fn, n) in enumerate(((walk_e, 8), (flirt, FLIRT_FRAMES), (idle, 6), (None, FALL_FRAMES))):
        for f in range(n):
            out = render_pose(fn if fn else (lambda t, f=f: fall(f)), f/n*2*math.pi, yaws=DIR8)
            for d in range(8):
                r = g*8+d; sheet[r*SIZE:(r+1)*SIZE, f*SIZE:(f+1)*SIZE] = out[d]
            yield (fn.__name__ if fn else 'dead'), f
    clear_pose()
    os.makedirs(PROJ, exist_ok=True)
    save_rgba(sheet, os.path.join(PROJ, "enemy_spritesheet.png"))
    write_enemy_frames()
    return sheet.shape


def write_enemy_frames():
    """Atlante e SpriteFrames condividono celle, ordine e numero di frame."""
    import re
    path = os.path.join(PROJ, 'enemy_frames.tres')
    uid = ''
    if os.path.exists(path):
        with open(path, encoding='utf-8-sig') as existing:
            match = re.search(r'uid="([^"]+)"', existing.readline())
            if match: uid = f' uid="{match.group(1)}"'
    groups = [('walk', 8, 8, True), ('flirt', FLIRT_FRAMES, 8, True),
              ('idle', 6, 5, True), ('dead', FALL_FRAMES, 12, False)]
    directions = ['up', 'down', 'right', 'left', 'up_right', 'up_left', 'down_right', 'down_left']
    lines = [f'[gd_resource type="SpriteFrames" format=3{uid}]', '',
             '[ext_resource type="Texture2D" path="res://Assets/Characters/Enemy/enemy_spritesheet.png" id="1"]', '']
    animations = []
    for g, (name, count, speed, loop) in enumerate(groups):
        for d, direction in enumerate(directions):
            frames = []
            for f in range(count):
                key = f'{name}_{direction}_{f}'
                lines.extend([f'[sub_resource type="AtlasTexture" id="{key}"]', 'atlas = ExtResource("1")',
                              f'region = Rect2({f*SIZE}, {(g*8+d)*SIZE}, {SIZE}, {SIZE})', 'filter_clip = true', ''])
                frames.append('{"duration": 1.0, "texture": SubResource("'+key+'")}')
            animations.append('{"frames": ['+', '.join(frames)+'], "loop": '+str(loop).lower()+
                              ', "name": &"'+name+'_'+direction+'", "speed": '+str(float(speed))+'}')
    lines.extend(['[resource]', 'animations = ['+',\n'.join(animations)+']', ''])
    with open(path, 'w', encoding='utf-8') as out:
        out.write('\n'.join(lines))
