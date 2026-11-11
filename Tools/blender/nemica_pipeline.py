"""
Pipeline sprite Nemica (Beatch Slash!) - da eseguire DENTRO Blender 5.x con
Tools/blender/nemica.blend aperto (copia del modello della protagonista con
chioma piu' piena e voluminosa del concept, capelli viola #7043A1, costume smeraldo).

Uso (Blender MCP execute_blender_code):
    exec(open(r"<percorso>/nemica_pipeline.py").read())
    build_enemy()     # rigenera enemy_spritesheet.png in Assets/Characters/Enemy

Riusa utilita', render e stile (48x48, toon 4 toni, contorno, occhi a pixel, ombra) di
blender_pipeline.py. Atlante: righe = gruppo*8 + direzione, colonne = frame (12).
Gruppi: 0 = walk (8 frame), 1 = flirt (12 frame, posa ammiccante davanti al ragazzo),
2 = idle (6 frame, da ferma quando e' bloccata; riusa idle() del Player).
Direzioni (ordine righe): up, down, right, left, up_right, up_left, down_right, down_left.

Palette: capelli #2a1240 #4b2a78 #7043a1 #a97fd9; costume #16503a #25805a #3db57d #8de0b4.
Il volume dei capelli e' gia' nella mesh di nemica.blend (X x1.10-1.24 e Y dietro x1.12-1.30,
crescente verso le punte).
"""
import bpy, os, math, numpy as np
exec(open(os.path.join(os.path.dirname(bpy.data.filepath), "blender_pipeline.py")).read()) if "build_all" not in globals() else None
PROJ = os.path.normpath(os.path.join(BLEND_DIR, "..", "..", "Assets", "Characters", "Enemy"))
DIR8 = [180, 0, 90, -90, 135, -135, 45, -45]
FLIRT_FRAMES = 12


def walk_e(t):
    """camminata sensuale: bacino che dondola, busto in contro-rotazione, gomiti piegati, chioma mossa"""
    walk(t); P = pb(); s = math.sin(t)
    P["hips"].location = (0.02*s, 0.035*abs(s)-0.02, 0); P["hips"].rotation_euler = (0, R(12*s), R(3*s))
    P["spine"].rotation_euler = (R(5), R(-9*s), 0); P["chest"].rotation_euler = (0, R(-6*s), 0)
    P["upper_arm.L"].rotation_euler = (R(18*s), 0, R(-9)); P["upper_arm.R"].rotation_euler = (R(-18*s), 0, R(9))
    P["forearm.L"].rotation_euler = (R(-45-10*max(0, -s)), 0, 0); P["forearm.R"].rotation_euler = (R(-45-10*max(0, s)), 0, 0)
    P["hair"].rotation_euler = (R(12+9*math.sin(2*t-1.2)), R(7*math.sin(t-0.9)), 0)


REST_FEET = None

def pin_feet(targets):
    """IK numerico: coscia (X,Z) + stinco (X) portano la caviglia sul punto a terra; piede tenuto piatto"""
    from mathutils import Matrix
    rig = bpy.data.objects["Rig"]; P = pb()
    def ankle(s):
        bpy.context.view_layer.update(); return rig.matrix_world @ P["foot."+s].head
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
    P = pb(); rig = bpy.data.objects["Rig"]
    if REST_FEET is None:
        bpy.context.view_layer.update(); REST_FEET = {s: rig.matrix_world @ P["foot."+s].head.copy() for s in "LR"}
    s, c = math.sin(t), math.cos(t); a = 0.5 + 0.5*math.sin(t - 0.6)
    P["hips"].location = (0.045*s, -0.055 - 0.012*c*c, -0.012*s)   # Y locale = verticale; P["hips"].rotation_euler = (R(3), R(9*s), R(-6*s))
    P["spine"].rotation_euler = (R(5), R(-7*s), R(8*s)); P["chest"].rotation_euler = (R(2), R(-6*s), R(3*s))
    P["head"].rotation_euler = (R(-3), R(5*s), R(-7*s + 8*math.sin(t+0.8)))
    P["thigh.L"].rotation_euler = (R(-4), 0, 0); P["thigh.R"].rotation_euler = (R(-4), 0, 0)
    P["shin.L"].rotation_euler = (R(18), 0, 0); P["shin.R"].rotation_euler = (R(18), 0, 0)
    pin_feet(REST_FEET)
    # assi braccia (provati a vista): Z = abduzione (R +, L -), Z dell'avambraccio = piega verso il corpo (R -, L +)
    P["upper_arm.R"].rotation_euler = (0, 0, R(30+105*a)); P["forearm.R"].rotation_euler = (0, 0, R(-(10+70*a)))
    P["upper_arm.L"].rotation_euler = (R(-8), 0, R(-42)); P["forearm.L"].rotation_euler = (R(-10), 0, R(95))
    P["hair"].rotation_euler = (R(6+6*a+3*math.sin(2*t)), R(8*s), 0)


def build_enemy():
    rig = bpy.data.objects["Rig"]; rig.animation_data_create(); rig.animation_data.action = None
    bpy.data.objects["SandBall"].hide_render = True
    sheet = np.zeros((24*SIZE, FLIRT_FRAMES*SIZE, 4))
    for g, (fn, n) in enumerate(((walk_e, 8), (flirt, FLIRT_FRAMES), (idle, 6))):
        for f in range(n):
            out = render_pose(fn, f/n*2*math.pi, yaws=DIR8)
            for d in range(8):
                r = g*8+d; sheet[r*SIZE:(r+1)*SIZE, f*SIZE:(f+1)*SIZE] = out[d]
    clear_pose()
    os.makedirs(PROJ, exist_ok=True)
    save_rgba(sheet, os.path.join(PROJ, "enemy_spritesheet.png"))
    return sheet.shape
