"""
Pipeline sprite Player (Beatch Slash!) - da eseguire DENTRO Blender 5.x
con Tools/blender/personaggio.blend aperto (modello, rig 17 ossa,
action idle/walk/run, camera CamSprite, palla SandBall).

Uso (Blender MCP execute_blender_code oppure Text Editor > Run Script):
    exec(open(r"<percorso>/blender_pipeline.py").read())
    build_all()     # rigenera i due atlanti del Player nel progetto Godot

Stile: 48x48, nessun anti-aliasing (EEVEE 1 sample, filter 0), materiali toon a 4 toni
(ShaderToRGB -> ColorRamp CONSTANT -> Emission), contorno esterno 1px #3a1418,
occhi disegnati a pixel (2x3, riflesso alto-destra), ombra = proiezione verticale
del corpo, colore #3a1418 con alpha 97/255.
"""
import bpy, math, os, tempfile, numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

# percorsi relativi al .blend (Tools/blender/) -> Assets/Characters/Player del progetto
BLEND_DIR = os.path.dirname(bpy.data.filepath)
PROJ = os.path.normpath(os.path.join(BLEND_DIR, "..", "..", "Assets", "Characters", "Player"))
TMP = tempfile.gettempdir()
SIZE, ELEV, ORTHO, TARGET_Z = 48, 25.0, 2.2, 0.9
DIRY = [180, 0, 90, -90]          # N, S, E, W (rotazione di Root)
R = math.radians
scene = bpy.context.scene

def hx8(h):
    h = h.lstrip('#'); return np.array([int(h[i:i+2], 16)/255 for i in (0, 2, 4)])
OUTLINE = hx8("#3a1418"); SHADOW_RGB = hx8("#3a1418"); SHADOW_A = 97/255
EYE = {"D": hx8("#3b1d14"), "H": hx8("#fff6e8"), "B": hx8("#7a4127")}

# ---------- utilità immagine ----------
def grab(path):
    im = bpy.data.images.load(path, check_existing=False)
    w, h = im.size; a = np.array(im.pixels[:]).reshape(h, w, 4)[::-1]
    bpy.data.images.remove(im); return a

def save_rgba(a, path):
    h, w = a.shape[:2]
    o = bpy.data.images.new("tmpout", w, h, alpha=True)
    o.pixels = a[::-1].ravel().tolist()
    o.filepath_raw = path; o.file_format = 'PNG'; o.save(); bpy.data.images.remove(o)

def place_cam(cam, elev, target_z):
    e = R(elev); d = Vector((0, -math.cos(e), math.sin(e)))
    cam.location = Vector((0, 0, target_z)) + d*10
    cam.rotation_euler = (R(90) - e, 0, 0)

# ---------- viso disegnato a pixel ----------
def stamp_face(rgb, alpha, cam, size):
    head = bpy.data.objects["Head"]; hc = head.matrix_world.translation
    cd = (cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))).normalized()
    hcx = world_to_camera_view(scene, cam, hc).x*size
    vis = [bpy.data.objects[n].matrix_world.translation for n in ("Eye_L", "Eye_R")]
    vis = [p for p in vis if -((p-hc).normalized()).dot(cd) > 0.12]
    side = len(vis) == 1
    for p in vis:
        v = world_to_camera_view(scene, cam, p); cx, cy = v.x*size, (1-v.y)*size
        if side: pat = ["D", "D", "B"]; x0 = int(round(cx-0.5)) + (-1 if cx > hcx else 1)
        else:    pat = ["DH", "DD", "BB"]; x0 = int(round(cx-1))
        y0 = int(round(cy-1.5))
        for j, row in enumerate(pat):
            for i, ch in enumerate(row):
                x, y = x0+i, y0+j
                if 0 <= x < size and 0 <= y < size and alpha[y, x] > 0: rgb[y, x] = EYE[ch]
    p = bpy.data.objects["Mouth"].matrix_world.translation
    if -((p-hc).normalized()).dot(cd) > 0.6:
        v = world_to_camera_view(scene, cam, p)
        x, y = int(round(v.x*size-0.5)), int(round((1-v.y)*size))
        if 0 <= x < size and 0 <= y < size: rgb[y, x] = hx8("#a8473a")

def foot_height():
    rig = bpy.data.objects["Rig"]; pb = rig.pose.bones
    return min((rig.matrix_world @ p).z for s in "LR" for p in (pb["foot."+s].head, pb["foot."+s].tail))

# ---------- render di una posa in 4 direzioni ----------
def render_sprites(yaws=DIRY, frame=None, shadow=True):
    r = scene.render; cam = bpy.data.objects["CamSprite"]; scene.camera = cam
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = ORTHO; place_cam(cam, ELEV, TARGET_Z)
    r.resolution_x = r.resolution_y = SIZE; r.resolution_percentage = 100
    r.film_transparent = True; scene.view_settings.view_transform = 'Standard'
    scene.eevee.taa_render_samples = 1; r.filter_size = 0.0
    root = bpy.data.objects["Root"]
    if frame is not None: scene.frame_set(frame)
    bpy.context.view_layer.update()
    h = max(0.0, foot_height() - 0.045); k = max(0.6, 1.15 - 2.4*h)   # ombra più piccola se in aria
    out = []
    for yaw in yaws:
        root.rotation_euler = (0, 0, R(yaw)); root.scale = (1, 1, 1); bpy.context.view_layer.update()
        r.filepath = os.path.join(TMP, "_sprite_tmp.png"); bpy.ops.render.render(write_still=True)
        a = grab(r.filepath); op = a[..., 3] > 0.5; rgb = a[..., :3].copy()
        stamp_face(rgb, op.astype(float), cam, SIZE)
        nb = np.zeros_like(op)
        nb[1:] |= op[:-1]; nb[:-1] |= op[1:]; nb[:, 1:] |= op[:, :-1]; nb[:, :-1] |= op[:, 1:]
        ol = nb & ~op; rgb[ol] = OUTLINE; body = op | ol; alpha = body.astype(float)
        if shadow:
            root.scale = (k, k, 0.002); bpy.context.view_layer.update()
            bpy.ops.render.render(write_still=True)
            sm = grab(r.filepath)[..., 3] > 0.5; root.scale = (1, 1, 1)
            sh = sm & ~body; rgb[sh] = SHADOW_RGB; alpha[sh] = SHADOW_A
        f = np.concatenate([rgb, alpha[..., None]], axis=2); f[alpha == 0] = 0; out.append(f)
    root.rotation_euler = (0, 0, 0); root.scale = (1, 1, 1); bpy.context.view_layer.update()
    return out

# ---------- pose ----------
def pb(): return bpy.data.objects["Rig"].pose.bones
def clear_pose():
    for b in pb(): b.rotation_mode = 'XYZ'; b.rotation_euler = (0, 0, 0); b.location = (0, 0, 0); b.scale = (1, 1, 1)
# Convenzioni: ossa che puntano in basso (cosce, braccia): rotazione X negativa = in avanti.
# Abduzione coscia sinistra verso l'esterno = Z negativa (destra: positiva).
def idle(t):
    P = pb(); br = (1 - math.cos(t))/2
    P["chest"].location = (0, 0.045*br, 0)                     # solo il busto respira, piedi fermi
    P["spine"].rotation_euler = (R(1.5*math.sin(t)), 0, 0)
    P["head"].rotation_euler = (R(-2*math.sin(t-0.6)), 0, 0)
    for s, sg in (("L", 1), ("R", -1)):
        P["upper_arm."+s].rotation_euler = (R(-2+3*math.sin(t)), 0, R(sg*-(3+3*br)))
        P["forearm."+s].rotation_euler = (R(-10-4*br), 0, 0)
    P["hair"].rotation_euler = (R(4+4*math.sin(t-1.0)), 0, 0)

def walk(t):
    P = pb(); s, c = math.sin(t), math.cos(t)
    P["hips"].location = (0, 0.035*abs(s)-0.02, 0); P["hips"].rotation_euler = (0, R(7*s), 0)
    P["spine"].rotation_euler = (R(7), R(-5*s), 0); P["chest"].rotation_euler = (0, R(-4*s), 0)
    P["head"].rotation_euler = (R(-5), R(2*s), 0)
    P["thigh.L"].rotation_euler = (R(-32*s), 0, R(-5)); P["thigh.R"].rotation_euler = (R(32*s), 0, R(5))
    P["shin.L"].rotation_euler = (R(10+62*max(0, c)), 0, 0); P["shin.R"].rotation_euler = (R(10+62*max(0, -c)), 0, 0)
    P["foot.L"].rotation_euler = (R(-10*s), 0, 0); P["foot.R"].rotation_euler = (R(10*s), 0, 0)
    P["upper_arm.L"].rotation_euler = (R(30*s), 0, R(-6)); P["upper_arm.R"].rotation_euler = (R(-30*s), 0, R(6))
    P["forearm.L"].rotation_euler = (R(-35-15*max(0, -s)), 0, 0); P["forearm.R"].rotation_euler = (R(-35-15*max(0, s)), 0, 0)
    P["hair"].rotation_euler = (R(12+7*math.sin(2*t-1.2)), R(5*math.sin(t-0.9)), 0)

def run(t):
    P = pb(); s, c = math.sin(t), math.cos(t)
    P["hips"].location = (0, 0.06*abs(s)-0.035, -0.02); P["hips"].rotation_euler = (0, R(9*s), 0)
    P["spine"].rotation_euler = (R(14), R(-7*s), 0); P["chest"].rotation_euler = (R(3), R(-5*s), 0)
    P["head"].rotation_euler = (R(-12), R(3*s), 0)
    P["thigh.L"].rotation_euler = (R(-46*s), 0, R(-5)); P["thigh.R"].rotation_euler = (R(46*s), 0, R(5))
    P["shin.L"].rotation_euler = (R(15+85*max(0, c)), 0, 0); P["shin.R"].rotation_euler = (R(15+85*max(0, -c)), 0, 0)
    P["foot.L"].rotation_euler = (R(-15*s), 0, 0); P["foot.R"].rotation_euler = (R(15*s), 0, 0)
    P["upper_arm.L"].rotation_euler = (R(45*s), 0, R(-10)); P["upper_arm.R"].rotation_euler = (R(-45*s), 0, R(10))
    P["forearm.L"].rotation_euler = (R(-70-15*max(0, -s)), 0, 0); P["forearm.R"].rotation_euler = (R(-70-15*max(0, s)), 0, 0)
    P["hair"].rotation_euler = (R(26+9*math.sin(2*t-1.2)), R(7*math.sin(t-0.9)), 0)

# Lancio (braccio destro): (uaR X, uaR Z, faR X, uaL X, chest Y, spine X, head X)
KEYS = [(5, 8, -15, -5, 0, 2, 0), (95, 38, 35, -30, -22, -4, 3), (160, 48, 80, -45, -32, -7, 5),
        (-120, 12, -10, 35, 24, 13, -4), (-60, 8, -20, 22, 26, 15, -4), (-12, 8, -15, 6, 10, 6, -2)]
P_THROW = [0.5, 1.2, 2.0, 3.0, 3.7, 4.4, 5.2, 5.75]    # 8 frame, rilascio all'indice 3, poi rientro
BALL_FRAMES = {0, 1, 2}
UPPER = ["upper_arm.L", "upper_arm.R", "forearm.L", "forearm.R", "chest", "spine", "head", "hips"]

def throw_upper(p):
    P = pb(); i = min(int(p), len(KEYS)-2); f = p - i
    uaRx, uaRz, faRx, uaLx, tw, sp, hd = [a+(b-a)*f for a, b in zip(KEYS[i], KEYS[i+1])]
    P["upper_arm.R"].rotation_euler = (R(uaRx), 0, R(uaRz)); P["forearm.R"].rotation_euler = (R(faRx), 0, 0)
    P["upper_arm.L"].rotation_euler = (R(uaLx), 0, R(-8)); P["forearm.L"].rotation_euler = (R(-30), 0, 0)
    P["chest"].rotation_euler = (P["chest"].rotation_euler.x, R(tw), 0)
    P["spine"].rotation_euler = (R(sp), P["spine"].rotation_euler.y, 0)
    P["head"].rotation_euler = (R(hd), R(-tw*0.5), 0)

def pose_combo(base_fn, t, i, static=False):
    """gambe/base dalla fase t, busto dal frame i del lancio; gli ultimi frame rientrano nella posa base"""
    P = pb(); clear_pose(); base_fn(t)
    snap = {b: tuple(P[b].rotation_euler) for b in UPPER}
    p = P_THROW[i]; throw_upper(min(p, 5.0))
    if static and p < 5.0: P["hips"].rotation_euler = (0, R(-6 if p < 3 else 4), 0)
    if p > 5.0:
        w = min(1.0, (p-5.0)/0.9)
        for b in UPPER:
            r1 = tuple(P[b].rotation_euler)
            P[b].rotation_euler = tuple(a*(1-w)+c*w for a, c in zip(r1, snap[b]))
    if static: P["hair"].rotation_euler = (R(6 + (6 if 3.0 <= p <= 5.0 else 2)), 0, 0)

def render_pose(fn, t, ball=False, yaws=DIRY):
    clear_pose(); fn(t); bpy.data.objects["SandBall"].hide_render = not ball
    return render_sprites(yaws)

# ---------- costruzione degli atlanti nel formato del progetto ----------
DIAG = [135, -135, 45, -45]       # NE, NW, SE, SW (rotazione di Root)

def build_diagonals():
    """atlanti delle diagonali, stesso formato dei principali ma direzioni NE,NW,SE,SW"""
    return build_all(DIAG, "player_diagonals_spritesheet.png", "player_diagonals_moving_throw.png")

def build_all(yaws=DIRY, sheet_name="player_spritesheet.png", mt_name="player_moving_throw.png"):
    rig = bpy.data.objects["Rig"]; rig.animation_data_create(); rig.animation_data.action = None
    ball = bpy.data.objects["SandBall"]
    groups = []   # Idle(6), Walk(8), Dash(8), Throw(8) x N,S,E,W
    for fn, n in ((idle, 6), (walk, 8), (run, 8)):
        arr = np.zeros((4, 8, SIZE, SIZE, 4))
        for f in range(n):
            out = render_pose(fn, f/n*2*math.pi, yaws=yaws)
            for d in range(4): arr[d, f] = out[d]
        groups.append(arr)
    arr = np.zeros((4, 8, SIZE, SIZE, 4))
    for i in range(8):
        pose_combo(idle, 0.0, i, static=True); ball.hide_render = i not in BALL_FRAMES
        out = render_sprites(yaws)
        for d in range(4): arr[d, i] = out[d]
    groups.append(arr)
    sheet = np.zeros((16*SIZE, 8*SIZE, 4))
    for gi, a in enumerate(groups):
        for d in range(4):
            for c in range(8):
                r = gi*4+d; sheet[r*SIZE:(r+1)*SIZE, c*SIZE:(c+1)*SIZE] = a[d, c]
    # lanci in movimento: riga = azione*32 + dir*8 + fase passo, colonna = frame lancio
    mt = np.zeros((64*SIZE, 8*SIZE, 4))
    for ai, fn in enumerate((walk, run)):
        for g in range(8):
            for i in range(8):
                pose_combo(fn, g/8*2*math.pi, i); ball.hide_render = i not in BALL_FRAMES
                out = render_sprites(yaws)
                for d in range(4):
                    r = ai*32+d*8+g; mt[r*SIZE:(r+1)*SIZE, i*SIZE:(i+1)*SIZE] = out[d]
    ball.hide_render = True; clear_pose()
    save_rgba(sheet, os.path.join(PROJ, sheet_name))
    save_rgba(mt, os.path.join(PROJ, mt_name))
    return sheet.shape, mt.shape
