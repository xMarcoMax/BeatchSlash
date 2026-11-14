"""
Ricostruzione della protagonista (Player) dal suo concept - da eseguire DENTRO Blender 5.x.

    bpy.ops.wm.open_mainfile(filepath=".../Tools/blender/base_personaggio.blend")
    bpy.ops.wm.save_as_mainfile(filepath=".../Tools/blender/personaggio.blend")
    exec(open(r".../Tools/blender/blender_pipeline.py").read())
    exec(open(r".../Tools/blender/personaggio_modello.py").read())
    make_girl(); bpy.ops.wm.save_mainfile()
Poi gli sprite con build_all() e build_diagonals() di blender_pipeline.py (animazioni invariate).

Stesso metodo del ragazzo (concept_model.py) con la scala del concept della ragazza = altezza del modello base.
- corpo: adattato alle sole zone di pelle e costume (i capelli coprono fianchi e schiena);
- testa: la sfera prende il viso (dall'attaccatura al mento); occhi e bocca dove sono nel concept;
- capelli: chioma ricostruita dalle tre sagome (visual hull): un cubetto e' capello se in ogni vista cade
  nella sagoma e li' il concept mostra capelli oppure il cubetto e' nascosto dietro corpo o testa; poi
  superficie levigata (remesh) e pesi sulle ossa head/hair, come la chioma originale, per le animazioni.
Palette e stile invariati (pelle, capelli, costume del Player).
"""
import bpy, os, math, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
exec(open(os.path.join(BLEND_DIR, "concept_model.py")).read())
GIRL_CONCEPT = os.path.normpath(os.path.join(BLEND_DIR, "..", "..", "Assets", "ConceptArt", "Player", "player_turnaround.png"))
ZONE_SMOOTH = 3         # passaggi del filtro di maggioranza sulle zone di colore (niente macchie isolate)
BODY_SMOOTH = 3        # passaggi di levigatura del corpo dopo l'adattamento alle sagome
VOX = 0.015             # lato dei cubetti della chioma (spazio del rig); piu' fine blocca Blender (remesh e levigatura)
HAIR_BEHIND = 0.35      # attorno alla testa la chioma sta dietro questa frazione della profondita' (piano delle guance)
GIRL_H = 1.9476547      # altezza del modello base (base_personaggio.blend) = altezza della ragazza nel concept
HAIR_BLUR = 1           # raggio (in cubetti) della sfumatura del volume della chioma
STRAND_SCALE, STRAND_STRETCH, STRAND_DEPTH = 0.12, 6.0, 0.02  # ciocche: grana del rumore, allungamento verticale, rilievo
NECK_FROM = 1.24       # sopra questa quota (spazio del rig) il collo si allunga fino al mento
MOUTH_LIFT_G = 12       # px: senza, il raggio colpisce il sotto del mento e la bocca non si vede
EYE_LIFT_G = 23         # px del concept di cui alzare occhi e bocca (compensa la camera inclinata)

# colori di riferimento campionati dal concept (zona -> colori); il piu' vicino decide la zona
GIRL_REFS = {
    1: [(250, 176, 116), (255, 187, 119), (232, 156, 104), (215, 150, 98), (211, 123, 75)],
    2: [(241, 98, 81), (242, 110, 88), (209, 61, 59), (204, 68, 51), (204, 51, 51), (153, 51, 51), (142, 44, 40), (136, 34, 34), (119, 34, 34), (102, 34, 34)],
    3: [(154, 204, 207), (153, 204, 204), (140, 190, 195), (120, 175, 180)],
    0: [(51, 17, 17), (68, 34, 17), (68, 17, 17), (89, 28, 25), (87, 48, 32), (40, 20, 15),
        (197, 196, 198), (185, 183, 188), (170, 165, 170)],      # sfondo e bordi sfumati: non sono costume
}

def girl_classify(c):
    keys, refs = [], []
    for k, cols in GIRL_REFS.items():
        for col in cols: keys.append(k); refs.append(col)
    refs = np.array(refs, float)/255; keys = np.array(keys)
    d = ((c[..., None, :] - refs[None, None])**2).sum(-1)
    return keys[d.argmin(-1)]

def dilate(m, r):
    out = m.copy()
    for dy in range(-r, r+1):
        for dx in range(-r, r+1):
            out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out

def girl_body_mask(cc):
    """pelle + costume (con il loro contorno): il corpo senza i capelli che lo coprono"""
    return dilate((cc.cls == 1) | (cc.cls == 3), 3) & cc.fg


# ---------- testa ----------
def girl_face_rows(cc):
    """attaccatura dei capelli e mento sulla colonna centrale della vista frontale"""
    c = int(round(cc.cf)); col = cc.cls[:, c-3:c+4]
    hairline = next(py for py in range(cc.top, cc.foot) if (col[py] == 1).sum() >= 5)
    # La bocca e' scura come il mento, ma ai suoi lati il viso e' ancora largo; sotto il mento resta il collo.
    chin = next(py for py in range(hairline + 60, cc.foot)
                if (col[py] == 0).sum() >= 4 and cc.fg[py, c]
                and (cc.cls[py+5, c-40:c+41] == 1).sum() < 50)
    return hairline, chin

def fit_girl_head(cc, head, hairline, chin):
    """testa regolare: ellissoide largo come il viso del concept (pelle piu' larga tra attaccatura e mento),
    profondo come largo, alto dal mento alla cima del cranio, con il davanti sul profilo e il mento appena
    piu' stretto (niente adattamento fascia per fascia: veniva una testa a cono)"""
    mw = head.matrix_world; mi = mw.inverted()
    w = np.array([(mw @ v.co)[:] for v in head.data.vertices])
    skin = cc.cls == 1
    z_chin = (cc.foot - chin)/cc.K; z_hl = (cc.foot - hairline)/cc.K
    z_top = min(z_hl + 0.6*(z_hl - z_chin), (cc.foot - cc.top)/cc.K - VOX)
    halves = []
    for py in range(hairline + 10, chin - 10, 4):
        F = cc.segs("front", py, mask=skin)
        if F:
            s = min(F, key=lambda q: abs((q[0] + q[1])/2 - cc.cf)); halves.append((s[1] - s[0])/2/cc.K)
    # larghezza e profondita': almeno quelle della testa del modello base (stile chibi approvato); nel concept
    # i capelli coprono i lati del viso, quindi la pelle visibile e' piu' stretta del cranio
    r_base = (w.max(0) - w.min(0))/2
    rx = max(float(np.percentile(halves, 90)), r_base[0]); ry = max(rx, r_base[1]); rz = (z_top - z_chin)/2
    ey = int(hairline + 0.45*(chin - hairline)); S = cc.segs("side", ey)
    yf = cc.wy(max(S, key=lambda q: q[1] - q[0])[1]) if S else -rx
    c0 = (w.max(0) + w.min(0))/2; r0 = (w.max(0) - w.min(0))/2
    u = (w - c0)/r0
    taper = 1 - 0.15*np.clip(-u[:, 2], 0, 1)                    # mento appena piu' stretto
    new = np.stack([u[:, 0]*rx*taper, yf + ry + u[:, 1]*ry, (z_chin + z_top)/2 + u[:, 2]*rz], 1)
    for v, p in zip(head.data.vertices, new): v.co = mi @ Vector(p)

def paint_girl_scalp(cc, head, hairline, chin):
    """Fronte aperta sotto le ciocche, con punta centrale e tempie curve come nel concept."""
    mw = head.matrix_world; nm = mw.to_3x3().inverted().transposed()
    for face in head.data.polygons:
        p = mw @ face.center
        row = cc.foot - p.z * cc.K; x = abs(p.x) * cc.K
        # La camera inclinata richiede di alzare anche l'attaccatura, come i marcatori degli occhi.
        edge = hairline - 39 + 0.009*x*x + 10*math.exp(-(x/10)**2)
        face.material_index = 0 if row > edge and (nm @ face.normal).normalized().y < 0.1 else 1
    head.data.update()


def place_girl_face(cc, head, hairline, chin):
    """occhi (le zone scure dentro il viso) e bocca dove sono nel concept; ciglia e sopracciglia restano pelle"""
    dg = bpy.context.evaluated_depsgraph_get(); tree = BVHTree.FromObject(head, dg)
    mw = head.matrix_world; mi = mw.inverted()
    # occhi: i pixel scuri non-capelli (zona 0) nel viso, colonne dove sono fitti; un occhio per lato
    y0, y1 = hairline + 40, chin - 20; x0, x1 = int(cc.cf) - 80, int(cc.cf) + 80
    dark = (cc.cls[y0:y1, x0:x1] == 0) & cc.fg[y0:y1, x0:x1]
    cols = dark.sum(0); dark &= (cols > 0.4*cols.max())[None, :]
    ys, xs = np.where(dark); xs = xs + x0; ys = ys + y0
    mid = (xs.min() + xs.max())/2
    pts = {n: (xs[m].mean(), ys[m].mean()) for n, m in (("Eye_R", xs < mid), ("Eye_L", xs >= mid))}
    ey = (pts["Eye_R"][1] + pts["Eye_L"][1])/2
    pts["Mouth"] = (cc.cf, ey + 0.6*(chin - ey))
    for n in ("Eye_R", "Eye_L"):
        px, py = (int(round(v)) for v in pts[n])
        box = cc.cls[py-45:py+30, px-35:px+36]; box[box == 2] = 1
    for name, (px, py) in pts.items():
        py -= MOUTH_LIFT_G if name == "Mouth" else EYE_LIFT_G    # la bocca sale meno: resta staccata dagli occhi
        x, z = cc.wx(px, "front"), (cc.foot - py)/cc.K
        o = mi @ Vector((x, -5.0, z)); d = (mi.to_3x3() @ Vector((0, 1, 0))).normalized()
        hit = tree.ray_cast(o, d)[0]
        if hit is None: continue
        ob = bpy.data.objects[name]; m = ob.matrix_world.copy(); m.translation = mw @ hit; ob.matrix_world = m
    return pts


# ---------- capelli ----------
def build_hair(cc, body, head, rig, z_chin, hairline):
    """chioma dalle tre viste: visual hull con il colore dei capelli, superficie levigata, pesi head/hair"""
    dg = bpy.context.evaluated_depsgraph_get()
    objs = [(BVHTree.FromObject(o, dg), o.matrix_world.copy(), o.matrix_world.inverted()) for o in (body, head)]
    hairish = dilate(cc.cls == 2, 4) & cc.fg & (cc.cls != 1) & (cc.cls != 3)
    (f0, f1), (s0, s1) = cc.views["front"], cc.views["side"]
    hair_rows = np.where((cc.cls == 2).any(1))[0]
    xs = np.arange(cc.wx(f0, "front"), cc.wx(f1, "front"), VOX); ys = np.arange(cc.wy(s1), cc.wy(s0), VOX)
    zs = np.arange((cc.foot - hair_rows.max())/cc.K, (cc.foot - cc.top)/cc.K, VOX)

    def first_hit(t, mw, mi, o, d, axis):
        """coordinata 'axis' del primo punto colpito dal raggio o->d (mondo), NaN se manca"""
        h = t.ray_cast(mi @ o, (mi.to_3x3() @ d).normalized())[0]
        return (mw @ h)[axis] if h is not None else np.nan
    # mappe di profondita' di corpo e testa: davanti/dietro su (x, z), fianco sinistro/destro su (y, z)
    yf = np.full((2, len(xs), len(zs)), np.nan); yb = yf.copy()
    xl = np.full((2, len(ys), len(zs)), np.nan); xr = xl.copy()
    for k, (t, mw, mi) in enumerate(objs):
        for i, x in enumerate(xs):
            for j, z in enumerate(zs):
                yf[k, i, j] = first_hit(t, mw, mi, Vector((x, -5, z)), Vector((0, 1, 0)), 1)
                yb[k, i, j] = first_hit(t, mw, mi, Vector((x, 5, z)), Vector((0, -1, 0)), 1)
        for i, y in enumerate(ys):
            for j, z in enumerate(zs):
                xl[k, i, j] = first_hit(t, mw, mi, Vector((-5, y, z)), Vector((1, 0, 0)), 0)
                xr[k, i, j] = first_hit(t, mw, mi, Vector((5, y, z)), Vector((-1, 0, 0)), 0)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    H, W = cc.fg.shape
    py = np.clip(np.round(cc.foot - Z*cc.K).astype(int), 0, H-1)
    pxs = {"front": np.clip(np.round(cc.cf + X*cc.K).astype(int), 0, W-1),
           "side": np.clip(np.round(cc.cs - Y*cc.K).astype(int), 0, W-1),
           "back": np.clip(np.round(cc.cb - X*cc.K).astype(int), 0, W-1)}
    keep = np.ones(X.shape, bool)
    for v in pxs: keep &= cc.fg[py, pxs[v]]                                 # dentro la sagoma in ogni vista
    hairy = {v: hairish[py, pxs[v]] for v in pxs}
    with np.errstate(invalid="ignore"):
        F = lambda m: m[:, :, None, :]; S = lambda m: m[:, None, :, :]          # (oggetto, x, y, z)
        hid_front = (Y[None] > F(yf)).any(0); hid_back = (Y[None] < F(yb)).any(0)
        hid_side = np.where(X <= 0, (X[None] > S(xl)).any(0), (X[None] < S(xr)).any(0))
        inside = ((Y[None] > F(yf)) & (Y[None] < F(yb)) & (X[None] > S(xl)) & (X[None] < S(xr))).any(0)
    # dove il concept non mostra capelli il cubetto deve essere nascosto dietro corpo o testa
    keep &= (hairy["front"] | hid_front) & (hairy["back"] | hid_back) & (hairy["side"] | hid_side) & ~inside
    # profondita' (le sagome da sole non la danno): sotto il mento i capelli stanno dietro il piano centrale del
    # busto, attorno alla testa dietro il piano delle guance (incorniciano il viso dai lati e da dietro)
    # davanti al viso (tra l'attaccatura e il mento, entro la larghezza della pelle) solo dietro la meta' della testa:
    # vista dall'alto la chioma coprirebbe guance e occhi
    bm_ = girl_body_mask(cc); hw = np.array([(head.matrix_world @ v.co)[:] for v in head.data.vertices])
    skin = cc.cls == 1; z_hl = (cc.foot - hairline)/cc.K
    limit = np.full(len(zs), np.nan); face_lim = np.full(len(zs), np.nan); face_half = np.zeros(len(zs))
    for j, z in enumerate(zs):
        if z < z_chin:
            S = cc.segs("side", cc.row(z), mask=bm_)
            if S: limit[j] = cc.wy(np.mean(max(S, key=lambda q: q[1] - q[0])))
        else:
            m = np.abs(hw[:, 2] - z) < VOX
            if m.any():
                y0, y1 = hw[m, 1].min(), hw[m, 1].max()
                limit[j] = y0 + HAIR_BEHIND*(y1 - y0)
                if z <= z_hl:
                    F = cc.segs("front", cc.row(z), mask=skin)
                    if F:
                        seg = min(F, key=lambda q: abs((q[0] + q[1])/2 - cc.cf))
                        face_half[j] = max(abs(cc.wx(seg[0], "front")), abs(cc.wx(seg[1], "front"))) + VOX
                        face_lim[j] = (y0 + y1)/2
    with np.errstate(invalid="ignore"):
        keep &= ~(Y < limit[None, None, :])
        keep &= ~((np.abs(X) < face_half[None, None, :]) & (Y < face_lim[None, None, :]))
    # volume sfumato prima di farne la superficie (due box blur per asse ~ gaussiana): niente gradini a cubetti
    f = keep.astype(float); B = HAIR_BLUR
    for ax in range(3):
        for _ in range(2):
            c = np.cumsum(np.pad(f, [(B + 1, B) if a == ax else (0, 0) for a in range(3)], mode="edge"), axis=ax)
            f = (np.take(c, range(2*B + 1, c.shape[ax]), axis=ax) - np.take(c, range(0, c.shape[ax] - 2*B - 1), axis=ax))/(2*B + 1)
    keep = f > 0.5
    # solo i cubetti di superficie: il remesh chiude comunque il volume
    n = np.zeros_like(keep)
    for ax in range(3):
        for s in (1, -1): n |= ~np.roll(keep, s, ax)
    surf = keep & n
    # cubetti costruiti tutti insieme (numpy + from_pydata): uno per uno con bmesh e' lentissimo
    P = np.stack([X[surf], Y[surf], Z[surf]], 1); h = VOX*0.525
    corner = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]])*h
    quads = np.array([[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]])
    verts = (P[:, None, :] + corner[None]).reshape(-1, 3)
    faces = (quads[None] + 8*np.arange(len(P))[:, None, None]).reshape(-1, 4)
    me = bpy.data.meshes.new("Hair"); me.from_pydata(verts.tolist(), [], faces.tolist()); me.update()
    hair = bpy.data.objects.new("Hair", me); body.users_collection[0].objects.link(hair)
    for mod, kw in (("REMESH", {"mode": 'VOXEL', "voxel_size": VOX}),
                    ("LAPLACIANSMOOTH", {"iterations": 40, "lambda_factor": 1.0, "use_volume_preserve": True})):
        m = hair.modifiers.new(mod.lower(), mod)
        for k, v in kw.items(): setattr(m, k, v)
        with bpy.context.temp_override(object=hair, active_object=hair):
            bpy.ops.object.modifier_apply(modifier=m.name)
    # solo il pezzo principale: i frammenti staccati (bordi del concept) spariscono
    bm = bmesh.new(); bm.from_mesh(hair.data); bm.verts.ensure_lookup_table(); seen = set(); parts = []
    for v0 in bm.verts:
        if v0.index in seen: continue
        stack, comp = [v0], []; seen.add(v0.index)
        while stack:
            v = stack.pop(); comp.append(v)
            for e in v.link_edges:
                w = e.other_vert(v)
                if w.index not in seen: seen.add(w.index); stack.append(w)
        parts.append(comp)
    parts.sort(key=len)
    bmesh.ops.delete(bm, geom=[v for comp in parts[:-1] for v in comp], context='VERTS')
    bm.to_mesh(hair.data); bm.free()
    # ciocche: leggero rilievo da un rumore stirato in verticale, che con lo shading toon da' riflessi a striscia
    tex = bpy.data.textures.get("HairStrands") or bpy.data.textures.new("HairStrands", 'CLOUDS')
    tex.noise_scale = STRAND_SCALE; tex.noise_depth = 1
    emp = bpy.data.objects.new("HairStrandsMap", None); body.users_collection[0].objects.link(emp)
    emp.scale = (1, 1, STRAND_STRETCH); bpy.context.view_layer.update()
    d = hair.modifiers.new("strands", 'DISPLACE'); d.texture = tex; d.texture_coords = 'OBJECT'
    d.texture_coords_object = emp; d.strength = STRAND_DEPTH; d.mid_level = 0.5
    s = hair.modifiers.new("soft", 'LAPLACIANSMOOTH'); s.iterations = 4; s.lambda_factor = 1.0; s.use_volume_preserve = True
    with bpy.context.temp_override(object=hair, active_object=hair):
        bpy.ops.object.modifier_apply(modifier=d.name)
        bpy.ops.object.modifier_apply(modifier=s.name)              # via le punte del rilievo
    bpy.data.objects.remove(emp)
    for f in hair.data.polygons: f.use_smooth = True
    hair.data.materials.append(bpy.data.materials["Hair"])
    # pesi: sopra il mento segue la testa, sotto passa all'osso dei capelli (ondeggia nelle animazioni)
    gh, gr = hair.vertex_groups.new(name="head"), hair.vertex_groups.new(name="hair")
    for v in hair.data.vertices:
        wr = min(1.0, max(0.0, (z_chin + 0.05 - v.co.z)/0.35))
        gh.add([v.index], 1.0 - wr, 'REPLACE'); gr.add([v.index], wr, 'REPLACE')
    hair.parent = rig
    a = hair.modifiers.new("Armature", 'ARMATURE'); a.object = rig
    return hair, int(keep.sum())


def build_front_hair(cc, head, rig, paths=None, part_color="#912a2a"):
    """Due ciocche dalla riga centrale alle tempie, tracciate sul concept e adagiate sul cranio."""
    paths = paths if paths is not None else [
        [(321, 170, 2), (306, 173, 15), (289, 192, 22), (278, 226, 27), (268, 263, 28), (243, 292, 22), (207, 307, 1)],
        [(326, 170, 2), (345, 175, 15), (368, 198, 24), (380, 229, 26), (390, 269, 23), (409, 300, 17), (421, 325, 1)],
    ]
    hw = np.array([(head.matrix_world @ v.co)[:] for v in head.data.vertices])
    center = (hw.min(0) + hw.max(0))/2; radius = (hw.max(0) - hw.min(0))/2
    verts, faces = [], []
    rings, sides = 49, 12
    for path in paths:
        p = np.asarray(path, dtype=float)
        t = np.linspace(0, len(p)-1, rings)
        line = np.stack([np.interp(t, np.arange(len(p)), p[:, i]) for i in range(3)], axis=1)
        for _ in range(3):
            line[1:-1] = (line[:-2] + 2*line[1:-1] + line[2:])/4
        x = (line[:, 0]-cc.cf)/cc.K
        z = (cc.foot-line[:, 1] + 35*np.clip((line[:, 1]-170)/90, 0, 1))/cc.K
        tangents = np.stack([np.gradient(x), np.gradient(z)], axis=1)
        tangents /= np.linalg.norm(tangents, axis=1)[:, None]
        offset = len(verts)
        for j in range(rings):
            width = line[j, 2]/cc.K
            for k in range(sides):
                angle = 2*math.pi*k/sides
                xx = x[j] - tangents[j, 1]*width*math.cos(angle)
                zz = z[j] + tangents[j, 0]*width*math.cos(angle)
                q = ((xx-center[0])/radius[0])**2 + ((zz-center[2])/radius[2])**2
                yy = center[1] - radius[1]*math.sqrt(max(0, 1-q))
                yy -= 0.008 + min(width*0.3, 0.018)*math.sin(angle)
                verts.append((xx, yy, zz))
        for j in range(rings-1):
            for k in range(sides):
                a = offset + j*sides+k; b = offset+j*sides+(k+1)%sides
                faces.append((a, b, b+sides, a+sides))
        faces.extend([tuple(offset+k for k in reversed(range(sides))), tuple(offset+(rings-1)*sides+k for k in range(sides))])
    strand_faces = len(faces)
    # Riga centrale sul cranio: segue la superficie anche nelle viste laterali e nelle pose.
    offset = len(verts)
    for t, angle in zip(np.linspace(0, 1, 25), np.linspace(0.9, -0.2, 25)):
        for side in (-1, 1):
            verts.append((-0.012*math.sin(math.pi*t) + side*0.011*math.sin(math.pi*t), center[1]-(radius[1]+0.009)*math.sin(angle),
                          center[2]+(radius[2]+0.009)*math.cos(angle)))
    for j in range(24):
        a = offset + j*2; faces.append((a, a+1, a+3, a+2))
    me = bpy.data.meshes.new('FrontHair'); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new('FrontHair', me); head.users_collection[0].objects.link(ob)
    me.materials.append(bpy.data.materials['Hair'])
    part = flat_mat('HairPart', part_color)
    me.materials.append(part)
    for face in me.polygons:
        face.use_smooth = True
        face.material_index = int(face.index >= strand_faces)
    parent_to_bone(ob, rig, 'head')


def apply_girl_suit(cc, body):
    """Costume continuo sul corpo a riposo; misure in pixel del turnaround, indipendenti dalle facce."""
    me = body.data
    rest = me.attributes.get("rest_co") or me.attributes.new("rest_co", 'FLOAT_VECTOR', 'POINT')
    arms = me.attributes.get("suit_arm") or me.attributes.new("suit_arm", 'FLOAT', 'POINT')
    arm_groups = {g.index for g in body.vertex_groups if g.name.startswith(("upper_arm.", "forearm.", "hand."))}
    for v in me.vertices:
        rest.data[v.index].vector = (v.co.x, v.co.y, v.co.z * body.scale.z)
        arms.data[v.index].value = sum(g.weight for g in v.groups if g.group in arm_groups)

    mat = bpy.data.materials.get("BodyMat") or bpy.data.materials.new("BodyMat")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()

    def math_node(op, a, b=0):
        n = nodes.new('ShaderNodeMath'); n.operation = op
        for socket, value in zip(n.inputs, (a, b)):
            if isinstance(value, (int, float)): socket.default_value = value
            else: links.new(value, socket)
        return n.outputs[0]

    def between(value, low, high):
        return math_node('MULTIPLY', math_node('GREATER_THAN', value, low), math_node('LESS_THAN', value, high))

    attr = nodes.new('ShaderNodeAttribute'); attr.attribute_name = 'rest_co'
    xyz = nodes.new('ShaderNodeSeparateXYZ'); links.new(attr.outputs['Vector'], xyz.inputs[0])
    x = math_node('MULTIPLY', math_node('ABSOLUTE', xyz.outputs['X']), cc.K)
    row = math_node('SUBTRACT', cc.foot, math_node('MULTIPLY', xyz.outputs['Z'], cc.K))
    front = math_node('LESS_THAN', xyz.outputs['Y'], 0)
    x2 = math_node('MULTIPLY', x, x)
    # Scollo a U e bordo sotto le coppe: righe 472/497, spalline dalle spalle (416).
    neck = math_node('SUBTRACT', 472, math_node('MULTIPLY', x2, 0.006))
    cup_x = math_node('SUBTRACT', x, 38)
    hem = math_node('SUBTRACT', 497, math_node('MULTIPLY', math_node('MULTIPLY', cup_x, cup_x), 0.003))
    cups = between(row, neck, hem)
    band = between(row, 458, 497)
    top = math_node('ADD', math_node('MULTIPLY', cups, front), math_node('MULTIPLY', band, math_node('SUBTRACT', 1, front)))
    strap_x = math_node('SUBTRACT', 55, math_node('MULTIPLY', math_node('SUBTRACT', 470, row), 0.35))
    strap = math_node('MULTIPLY', between(row, 410, 490), math_node('LESS_THAN', math_node('ABSOLUTE', math_node('SUBTRACT', x, strap_x)), 7))
    top = math_node('MULTIPLY', math_node('MAXIMUM', top, strap), math_node('LESS_THAN', x, 80))
    # Vita curva e sgambatura a V misurate sullo slip (righe 570-634).
    waist = math_node('SUBTRACT', 589, math_node('MULTIPLY', x2, 0.0035))
    leg = math_node('SUBTRACT', 634, math_node('MULTIPLY', x, 0.75))
    bottom = math_node('MULTIPLY', between(row, waist, leg), math_node('LESS_THAN', x, 100))
    arm = nodes.new('ShaderNodeAttribute'); arm.attribute_name = 'suit_arm'
    mask = math_node('MULTIPLY', math_node('MAXIMUM', top, bottom), math_node('LESS_THAN', arm.outputs['Fac'], 0.5))
    mask.node.name = 'SuitMask'

    diffuse = nodes.new('ShaderNodeBsdfDiffuse')
    diffuse.inputs['Color'].default_value = next(n for n in bpy.data.materials['Skin'].node_tree.nodes if n.type == 'BSDF_DIFFUSE').inputs['Color'].default_value
    light = nodes.new('ShaderNodeShaderToRGB'); links.new(diffuse.outputs[0], light.inputs[0])
    ramps = []
    for source in ('Skin', 'Suit'):
        ramp = nodes.new('ShaderNodeValToRGB'); ramp.name = source + 'Palette'
        original = next(n for n in bpy.data.materials[source].node_tree.nodes if n.type == 'VALTORGB').color_ramp
        ramp.color_ramp.interpolation = original.interpolation
        for i, element in enumerate(original.elements):
            target = ramp.color_ramp.elements[i] if i < 2 else ramp.color_ramp.elements.new(element.position)
            target.position = element.position; target.color = element.color
        links.new(light.outputs['Color'], ramp.inputs[0]); ramps.append(ramp)
    mix = nodes.new('ShaderNodeMixRGB'); links.new(mask, mix.inputs[0])
    for i, ramp in enumerate(ramps, 1): links.new(ramp.outputs['Color'], mix.inputs[i])
    emission = nodes.new('ShaderNodeEmission'); links.new(mix.outputs[0], emission.inputs[0])
    output = nodes.new('ShaderNodeOutputMaterial'); links.new(emission.outputs[0], output.inputs['Surface'])
    me.materials.clear(); me.materials.append(mat)
    for face in me.polygons: face.material_index = 0
    me.update()


def make_girl(stage="all", concept_name="player"):
    """stage: "body", "hair", "suit" (solo materiale sul corpo attuale) o "all"; separati per restare nei
    tempi dell'MCP. L'altezza del concept corrisponde a GIRL_H, l'altezza del modello base."""
    rig = bpy.data.objects["Rig"]; body = bpy.data.objects["Body"]; head = bpy.data.objects["Head"]
    cc = Concept(GIRL_CONCEPT, GIRL_H, girl_classify, concept_name, axis_mask=girl_body_mask)
    hairline, chin = girl_face_rows(cc); info = {"hairline": hairline, "chin": chin}
    if stage in ("body", "all"):
        for n in ("Bust_L", "Bust_R", "Hair"): bpy.data.objects.remove(bpy.data.objects[n])
        subdivide(body); subdivide(body); subdivide(head)        # corpo due volte: il costume ha zone piccole
        fit_body_regular(cc, body, girl_body_mask(cc))
        fit_girl_head(cc, head, hairline, chin)
        # il collo arriva dentro il mento del concept (altrimenti tra testa e spalle resta un buco e si vedono i capelli)
        me = body.data; sz = body.scale.z; z_to = (cc.foot - chin)/cc.K + 0.04
        zv = np.array([v.co.z*sz for v in me.vertices]); top = zv.max()
        if top < z_to:
            for v, z in zip(me.vertices, zv):
                if z > NECK_FROM: v.co.z = (NECK_FROM + (z - NECK_FROM)*(z_to - NECK_FROM)/(top - NECK_FROM))/sz
        bpy.context.view_layer.update()
        pts = place_girl_face(cc, head, hairline, chin)
        skin, hair_m = bpy.data.materials["Skin"], bpy.data.materials["Hair"]
        apply_girl_suit(cc, body)
        paint_zones(cc, head, [skin, hair_m], [1, 2], smooth=ZONE_SMOOTH)
        paint_girl_scalp(cc, head, hairline, chin)
        info["eyes"] = {k: [round(a) for a in v] for k, v in pts.items()}
    if stage == "suit":
        apply_girl_suit(cc, body)
    if stage in ("hair", "all"):
        paint_girl_scalp(cc, head, hairline, chin)
        for n in ("Hair", "FrontHair", "Ref_Front", "Ref_Side", "Ref_Back"):          # rifare la fase sostituisce la chioma
            if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n])
        bpy.context.view_layer.update()
        hair, nvox = build_hair(cc, body, head, rig, (cc.foot - chin)/cc.K, hairline)
        build_front_hair(cc, head, rig)
        add_refs(cc, 1.0)
        info.update(voxels=nvox, hair_verts=len(hair.data.vertices))
    return info
