"""
Pipeline sprite Ragazzo / Boyfriend (Beatch Slash!) - da eseguire DENTRO Blender 5.x.

Il modello si ricostruisce dal concept (Assets/ConceptArt/Boyfriend/boyfriend_turnaround.png) partendo
da una copia di base_personaggio.blend (modello e rig originali comuni a tutti i personaggi: stesso rig,
materiali toon e camera di ragazza e nemiche):
    bpy.ops.wm.open_mainfile(filepath=".../Tools/blender/base_personaggio.blend")
    bpy.ops.wm.save_as_mainfile(filepath=".../Tools/blender/ragazzo.blend")
    exec(open(r".../Tools/blender/ragazzo_pipeline.py").read())
    make_boy(); bpy.ops.wm.save_mainfile()
Con ragazzo.blend gia' pronto basta l'exec e poi preview_boy() (posa base nelle 4 direzioni N,S,E,W).

Come usa il concept (le tre viste del turnaround: fronte, profilo destro, retro):
- immagini di riferimento in scena (Empty "Ref_Front", "Ref_Side", "Ref_Back", file in Tools/blender/ref/)
  allineate al modello, per il confronto visivo in Blender;
- scala: la stessa del concept della ragazza rispetto al suo modello (GIRL_CONCEPT_H px = altezza del
  modello della ragazza), quindi il ragazzo e' alto 879/759 delle ragazze come nei concept;
- sagome: per ogni fascia di altezza busto, braccia, gambe, collo e testa sono adattati in larghezza alla
  vista frontale e in profondita' al profilo;
- colori: le facce di corpo e testa prendono la zona (pelle, capelli/barba, bermuda) dal concept
  proiettato (fronte, retro o profilo secondo la normale), cosi' attaccatura, barba, vita e orlo
  corrispondono al disegno; occhi e bocca vanno dove sono nel concept.
Lo sprite che esce va poi ritoccato in Pixelorama solo dentro la silhouette; le correzioni che
riguardano forme e proporzioni si riportano nel modello (vedi PROJECT_CONTEXT.md, Pipeline grafica).

Cella 64x64 (il ragazzo e' piu' alto) con la stessa scala di pixel del Player (ORTHO = 2.2*64/48).
"""
import bpy, os, math, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
exec(open(os.path.join(os.path.dirname(bpy.data.filepath), "blender_pipeline.py")).read()) if "build_all" not in globals() else None
PROJ = os.path.normpath(os.path.join(BLEND_DIR, "..", "..", "Assets", "Characters", "Boyfriend"))
CONCEPT = os.path.normpath(os.path.join(BLEND_DIR, "..", "..", "Assets", "ConceptArt", "Boyfriend", "boyfriend_turnaround.png"))
SIZE = 64
ORTHO = 2.2*SIZE/48
TARGET_Z = 1.0
GIRL_CONCEPT_H = 759     # px: altezza (piedi-capelli) della ragazza in Assets/ConceptArt/Player/player_turnaround.png
EYE_LIFT = 23           # px del concept (~1 px di sprite): la camera inclinata schiaccia il basso del viso
MOUTH_LIFT = 35         # bocca sopra il pizzetto, non sul bordo del mento
BEARD_UP = 25           # px del concept di cui la barba sale sui lati della mandibola
EYE = {"D": hx8("#1f3319"), "H": hx8("#fff6e8"), "B": hx8("#4e7a34")}
BEAD_COLORS = [0, 1, 0, 2, 0, 3]    # perline scure con accenti rosso, giallo, verde

# palette ricavate dai colori del concept, 4 toni come gli altri personaggi
SKIN = ["#8f4a2c", "#c97847", "#e99d63", "#f8b47a"]
HAIR = ["#2b140c", "#4d2a1e", "#6b3a26", "#9b573b"]
SHORTS = ["#6e2818", "#9e3f2c", "#c4553a", "#dd7050"]


exec(open(os.path.join(BLEND_DIR, "concept_model.py")).read())


def boy_classify(c):
    """0 contorno/altro, 1 pelle, 2 capelli e barba, 3 bermuda"""
    r, g = c[..., 0]*255, c[..., 1]*255
    skin = (r >= 195) & (g >= 110)
    shorts = (r >= 140) & (g < 0.5*r) & ~skin
    hair = (r >= 60) & (r < 195) & (g < 0.75*r) & ~skin & ~shorts
    return skin*1 + hair*2 + shorts*3


# ---------- testa e viso del ragazzo ----------
def fit_head(cc, head):
    """la sfera della testa prende la sagoma di testa + capelli + orecchie; dal mento alla cima dei capelli"""
    mw = head.matrix_world; mi = mw.inverted()
    w = np.array([(mw @ v.co)[:] for v in head.data.vertices])
    x0, x1 = cc.views["front"]; c = int(round(cc.cf)); col = cc.cls[:, c-3:c+4]
    skin = [(col[py] == 1).sum() >= 5 for py in range(cc.foot + 1)]
    start = cc.top + int(0.25*(cc.foot - cc.top))             # sotto gli occhi
    chin = next(py - 1 for py in range(start, cc.foot) if all(skin[py:py+15]))  # sotto la barba inizia il collo
    z_chin, z_top = (cc.foot - chin)/cc.K, (cc.foot - cc.top)/cc.K
    w[:, 2] = affine(w[:, 2], z_chin, z_top)
    bins = np.round(w[:, 2]/BIN).astype(int); new = w.copy()
    for b in np.unique(bins):
        idx = bins == b; py = cc.row(b*BIN)
        F = cc.segs("front", py); S = cc.segs("side", py)
        if F:
            seg = min(F, key=lambda q: abs((q[0] + q[1])/2 - cc.cf))
            new[idx, 0] = affine(w[idx, 0], cc.wx(seg[0], "front"), cc.wx(seg[1], "front"))
        if S:
            s, e = max(S, key=lambda q: q[1] - q[0])
            new[idx, 1] = affine(w[idx, 1], cc.wy(e), cc.wy(s))
    for v, p in zip(head.data.vertices, new): v.co = mi @ Vector(p)
    return chin

def place_face(cc, head, chin):
    """occhi e bocca dove sono nel concept, appoggiati sulla superficie della testa"""
    dg = bpy.context.evaluated_depsgraph_get(); tree = BVHTree.FromObject(head, dg)
    mw = head.matrix_world; mi = mw.inverted()
    x0, x1 = cc.views["front"]; r = cc.rgb[cc.top:chin, x0:x1+1]
    eye = (r[..., 1] > r[..., 0]) & (r[..., 1] > r[..., 2] + 0.05) & (r.sum(2) < 1.2)
    ys, xs = np.where(eye); xs = xs + x0; ys = ys + cc.top
    pts = {}
    for name, m in (("Eye_R", xs < cc.cf), ("Eye_L", xs >= cc.cf)):
        pts[name] = (xs[m].mean(), ys[m].mean())
    ey = (pts["Eye_R"][1] + pts["Eye_L"][1])/2
    pts["Mouth"] = (cc.cf, ey + 0.62*(chin - ey))
    # occhi, ciglia e sopracciglia del concept non diventano zone di capelli: li timbra stamp_face
    for n in ("Eye_R", "Eye_L"):
        px, py = (int(round(v)) for v in pts[n])
        cc.cls[py-40:py+20, px-28:px+29][cc.cls[py-40:py+20, px-28:px+29] == 2] = 1
    # barba sui lati della mandibola un po' piu' alta (fino alle basette, non sulle orecchie): con la camera
    # inclinata il basso del viso occupa poche righe e la barba del concept sparirebbe
    reg = cc.cls[chin-110:chin+1, x0:x1+1]; dx = np.abs(np.arange(x0, x1+1) - cc.cf)
    jaw = ((dx > 50) & (dx < 95))[None, :]; beard = (reg == 2) & jaw; up = np.zeros_like(beard)
    for k in range(1, BEARD_UP + 1): up[:-k] |= beard[k:]
    reg[up & jaw & (reg == 1)] = 2
    for name, (px, py) in pts.items():
        py -= MOUTH_LIFT if name == "Mouth" else EYE_LIFT
        x, z = cc.wx(px, "front"), (cc.foot - py)/cc.K
        o = mi @ Vector((x, -5.0, z)); d = (mi.to_3x3() @ Vector((0, 1, 0))).normalized()
        hit = tree.ray_cast(o, d)[0]
        if hit is None: continue
        ob = bpy.data.objects[name]; m = ob.matrix_world.copy(); m.translation = mw @ hit; ob.matrix_world = m

def paint_zones(cc, o, mats, allowed):
    """materiale di ogni faccia dalla zona del concept: allowed = codici zona nell'ordine degli slot"""
    o.data.materials.clear()
    for m in mats: o.data.materials.append(m)
    mw = o.matrix_world; nm = mw.to_3x3().inverted().transposed()
    for f in o.data.polygons:
        p = mw @ f.center; n = (nm @ f.normal).normalized()
        f.material_index = allowed.index(cc.zone(p, n, allowed))


# ---------- costruzione ----------
def make_boy():
    rig = bpy.data.objects["Rig"]; body = bpy.data.objects["Body"]; head = bpy.data.objects["Head"]
    girl_h = model_height()                                   # altezza del modello della ragazza
    for n in ("Bust_L", "Bust_R", "Hair"): bpy.data.objects.remove(bpy.data.objects[n])
    cc = Concept(CONCEPT, girl_h, boy_classify, "boyfriend")
    height = (cc.foot - cc.top)/GIRL_CONCEPT_H                # 879/759: rapporto d'altezza dei due concept
    subdivide(body); subdivide(head)
    fit_body(cc, body)
    chin = fit_head(cc, head)
    bpy.context.view_layer.update(); place_face(cc, head, chin)

    skin = bpy.data.materials["Skin"]; set_ramp(skin.node_tree.nodes["Color Ramp"], SKIN)
    hair = toon_mat("BoyHair", HAIR); shorts = toon_mat("Shorts", SHORTS)
    paint_zones(cc, body, [skin, shorts], [1, 3])
    paint_zones(cc, head, [skin, hair], [1, 2])

    # collanina: perline appoggiate sul collo alla quota del concept, davanti scendono un po'
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
    tree = BVHTree.FromObject(body, dg); mwb = body.matrix_world; mib = mwb.inverted()
    bz = (cc.foot - (chin + 15))/cc.K; NB = 22                # nel concept la collanina e' ~15 px sotto il mento
    def bead(bm, i):
        th = 2*math.pi*i/NB; d = Vector((math.cos(th), math.sin(th), 0))
        zz = bz - 0.03*max(0.0, -math.sin(th))**2
        hit = tree.ray_cast(mib @ Vector((0, 0, zz)), (mib.to_3x3() @ d).normalized())[0]
        p = mwb @ hit + d*0.012 if hit else Vector((0, 0, zz)) + d*0.12
        geo = bmesh.ops.create_cube(bm, size=0.03)["verts"]; bmesh.ops.translate(bm, verts=geo, vec=p)
        for f in {f for v in geo for f in v.link_faces}: f.material_index = BEAD_COLORS[i % len(BEAD_COLORS)]
    neck = new_obj("Necklace", lambda bm: [bead(bm, i) for i in range(NB)])
    for h in ("#1e0d07", "#c0392b", "#e8c547", "#2e8b45"): neck.data.materials.append(flat_mat("Bead" + h[1:], h))
    parent_to_bone(neck, rig, "chest")

    rig.scale = (height,)*3
    add_refs(cc, height)
    return {"girl_h": girl_h, "height": height, "chin_py": chin, "K": cc.K, "views": cc.views, "cs": cc.cs}


# ---------- render ----------
BROW = hx8("#2b140c"); MOUTH = hx8("#b5483a")

def stamp_face(rgb, alpha, cam, size):
    """viso a pixel del ragazzo (sostituisce quello del Player): occhi 2x2 di fronte (scuro + riflesso,
    riga bassa verde), di lato 1x2 sempre a 2 px dal bordo del viso; sopracciglia 2 px con una riga
    libera; bocca 2 px di fronte, 1 px di lato"""
    head = bpy.data.objects["Head"]; hc = head.matrix_world.translation
    cd = (cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))).normalized()
    hcx = world_to_camera_view(scene, cam, hc).x*size
    def proj(n):
        p = bpy.data.objects[n].matrix_world.translation
        v = world_to_camera_view(scene, cam, p)
        return v.x*size, (1-v.y)*size, -((p-hc).normalized()).dot(cd)
    def put(x, y, c):
        if 0 <= x < size and 0 <= y < size and alpha[y, x] > 0: rgb[y, x] = c
    def edge(y, right):
        """colonna del contorno del viso sulla riga y, dal lato verso cui guarda"""
        xs = np.where(alpha[y] > 0)[0]
        return (xs.max() if right else xs.min()) if len(xs) else None
    eyes = [e for e in (proj("Eye_L"), proj("Eye_R")) if e[2] > 0.12]
    side = len(eyes) == 1; ey0 = None
    for cx, cy, _ in eyes:
        y0 = ey0 = int(round(cy - 1))
        closed = globals().get("EYES_CLOSED", False)          # idle al sole: occhi chiusi, una riga scura
        if side:
            right = cx > hcx; xe = edge(y0, right)
            if xe is None: continue
            x0 = xe - 2 if right else xe + 2; back = -1 if right else 1
            if closed: put(x0, y0+1, EYE["D"])
            else: put(x0, y0, EYE["D"]); put(x0, y0+1, EYE["B"])
            put(x0, y0-2, BROW); put(x0 + back, y0-2, BROW)
        else:
            x0 = int(round(cx - 1))
            if closed: put(x0, y0+1, EYE["D"]); put(x0+1, y0+1, EYE["D"])
            else: put(x0, y0, EYE["D"]); put(x0+1, y0, EYE["H"]); put(x0, y0+1, EYE["B"]); put(x0+1, y0+1, EYE["B"])
            put(x0, y0-2, BROW); put(x0+1, y0-2, BROW)
    mx, my, mf = proj("Mouth")
    if mf > 0.3 or side:                                       # di profilo la bocca e' sul bordo del viso
        y = int(round(my))
        if side and ey0 is not None: y = ey0 + 3                # di profilo la proiezione la alzerebbe sull'occhio
        if side:
            right = mx > hcx; xe = edge(y, right)
            if xe is not None: put(xe - 1 if right else xe + 1, y, MOUTH)
        else:
            x0 = int(round(mx - 1)); put(x0, y, MOUTH); put(x0+1, y, MOUTH)

def preview_boy():
    clear_pose(); idle(0.0); bpy.data.objects["SandBall"].hide_render = True
    return render_sprites()


# ---------- animazioni ----------
# Direzioni come le nemiche (righe = gruppo*8 + direzione): up, down, right, left, up_right, up_left, down_right, down_left
DIR_NAMES = ["up", "down", "right", "left", "up_right", "up_left", "down_right", "down_left"]
DIR8 = [180, 0, 90, -90, 135, -135, 45, -45]
EYES_CLOSED = False

def hands_on_hips(P, side="LR"):
    for s, sg in (("L", 1), ("R", -1)):
        if s in side:
            P["upper_arm."+s].rotation_euler = (R(25), 0, R(sg*-40))
            P["forearm."+s].rotation_euler = (R(-30), 0, R(sg*110))

def boy_idle(t):
    """al sole con le mani sui fianchi, mento un po' alzato, occhi chiusi; respira solo il busto"""
    P = pb(); br = (1 - math.cos(t))/2; hands_on_hips(P)
    P["chest"].location = (0, 0.03*br, 0)
    P["spine"].rotation_euler = (R(1.5*math.sin(t)), 0, 0)
    P["head"].rotation_euler = (R(-10 + 2*math.sin(t - 0.6)), 0, 0)

GLANCE_W = [0.0, 0.4, 0.85, 1.0, 1.0, 1.0, 0.6, 0.2]      # quanto e' girato verso la nemica in ogni frame

def boy_glance(i, yaw):
    """corpo rivolto in basso come nell'idle; testa (e se serve il busto) girati verso la nemica per un attimo"""
    P = pb(); boy_idle(0.0); w = GLANCE_W[i]
    if yaw == 0:
        P["head"].rotation_euler = (R(-10 + 18*w), 0, 0)      # nemica davanti: abbassa lo sguardo
        return
    tot = yaw*w; head = max(-90, min(90, tot)); rest = max(-30, min(30, tot - head))   # occhiata, non si gira
    P["head"].rotation_euler = (R(-10 + 6*w), R(head), 0)
    P["spine"].rotation_euler = (P["spine"].rotation_euler.x, R(rest*0.5), 0)
    P["chest"].rotation_euler = (0, R(rest*0.5), 0)

def boy_admire(t):
    """affascinato: sporto in avanti, testa inclinata, mano destra al mento, sinistra sul fianco, ondeggia"""
    P = pb(); s = math.sin(t); hands_on_hips(P, "L")
    P["spine"].rotation_euler = (R(11 + 2*s), 0, 0)
    P["hips"].rotation_euler = (0, R(3*s), 0)
    P["head"].rotation_euler = (R(6), 0, R(-9 - 4*s))
    P["upper_arm.R"].rotation_euler = (R(-60), 0, R(10)); P["forearm.R"].rotation_euler = (R(-120 - 4*s), 0, 0)

def boy_flex(t):
    """doppio bicipite col petto in fuori, a impulsi"""
    P = pb(); s = math.sin(t)
    P["chest"].rotation_euler = (R(-6 - 3*s), 0, 0); P["head"].rotation_euler = (R(-5), 0, 0)
    for side, sg in (("L", 1), ("R", -1)):
        P["upper_arm."+side].rotation_euler = (0, 0, R(sg*-(85 + 6*s)))
        P["forearm."+side].rotation_euler = (0, 0, R(sg*-(115 + 12*s)))

# nome, frame, FPS, loop
ANIMS = [("idle", 6, 5.0, True), ("glance", 8, 8.0, False), ("admire", 8, 6.0, True), ("flex", 8, 8.0, True)]

def anim_frames(name, n):
    """frame [direzione][frame] di un'animazione"""
    global EYES_CLOSED
    out = [[None]*n for _ in DIR8]
    for f in range(n):
        t = f/n*2*math.pi
        if name == "glance":
            EYES_CLOSED = False
            for d, yaw in enumerate(DIR8):
                clear_pose(); boy_glance(f, yaw); out[d][f] = render_sprites(yaws=[0])[0]
            continue
        EYES_CLOSED = name == "idle"
        clear_pose(); {"idle": boy_idle, "admire": boy_admire, "flex": boy_flex}[name](t)
        for d, fr in enumerate(render_sprites(yaws=DIR8)): out[d][f] = fr
    EYES_CLOSED = False; clear_pose()
    return out

def build_boyfriend():
    """boyfriend_spritesheet.png (celle 64x64, righe = gruppo*8 + direzione, 8 colonne) e boyfriend_frames.tres"""
    bpy.data.objects["SandBall"].hide_render = True
    os.makedirs(PROJ, exist_ok=True)
    sheet = np.zeros((len(ANIMS)*8*SIZE, 8*SIZE, 4))
    for g, (name, n, fps, loop) in enumerate(ANIMS):
        fr = anim_frames(name, n)
        for d in range(8):
            for f in range(n):
                r = g*8 + d; sheet[r*SIZE:(r+1)*SIZE, f*SIZE:(f+1)*SIZE] = fr[d][f]
    save_rgba(sheet, os.path.join(PROJ, "boyfriend_spritesheet.png"))
    write_frames_tres(os.path.join(PROJ, "boyfriend_frames.tres"))
    return sheet.shape

def write_frames_tres(path):
    subs, anims = [], []
    for g, (name, n, fps, loop) in enumerate(ANIMS):
        for d, dn in enumerate(DIR_NAMES):
            an = "%s_%s" % (name, dn); frames = []
            for f in range(n):
                sid = "Atlas_%s_%d" % (an, f)
                subs.append('[sub_resource type="AtlasTexture" id="%s"]\natlas = ExtResource("1")\nregion = Rect2(%d, %d, %d, %d)\nfilter_clip = true\n'
                            % (sid, f*SIZE, (g*8 + d)*SIZE, SIZE, SIZE))
                frames.append('{\n"duration": 1.0,\n"texture": SubResource("%s")\n}' % sid)
            anims.append('{\n"frames": [%s],\n"loop": %s,\n"name": &"%s",\n"speed": %.1f\n}' % (", ".join(frames), "true" if loop else "false", an, fps))
    txt = ('[gd_resource type="SpriteFrames" format=3]\n\n'
           '[ext_resource type="Texture2D" path="res://Assets/Characters/Boyfriend/boyfriend_spritesheet.png" id="1"]\n\n'
           + "\n".join(subs) + '\n[resource]\nanimations = [' + ", ".join(anims) + ']\n')
    open(path, "w", encoding="utf-8", newline="\n").write(txt)
