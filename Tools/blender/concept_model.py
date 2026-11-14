"""
Ricostruzione di un personaggio dal suo concept (Beatch Slash!) - modulo comune, da eseguire DENTRO Blender
dopo blender_pipeline.py. Lo usano ragazzo_pipeline.py (ragazzo), make_girl() in blender_pipeline.py
(protagonista) e la pipeline della nemica.

Il concept e' un turnaround con tre viste affiancate (fronte, profilo destro, retro) su sfondo uniforme.
- Concept: viste, sagome (fg) e zone di colore (cls: 0 contorno/altro, 1 pelle, 2 capelli, 3 costume),
  scala K = px del concept per unita' del rig (altezza del concept = altezza del modello).
- fit_body: busto, braccia, gambe adattati fascia per fascia alla larghezza frontale e alla profondita' del
  profilo (una maschera puo' escludere i capelli che coprono il corpo).
- paint_zones: il materiale di ogni faccia dalla zona del concept proiettata secondo la normale.
- add_refs: immagini di riferimento in scena (Empty), allineate al modello.
"""
import bpy, os, math, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

BIN = 0.02              # altezza delle fasce usate per adattare le sagome (spazio del rig)
REF_DIR = os.path.join(BLEND_DIR, "ref")


# ---------- utilita' ----------
def lin(h):
    """colore sRGB esadecimale -> valore lineare per i nodi"""
    c = hx8(h); return [((v+0.055)/1.055)**2.4 if v > 0.04045 else v/12.92 for v in c] + [1.0]

def set_ramp(ramp, cols):
    for e, h in zip(ramp.color_ramp.elements, cols): e.color = lin(h)

def flat_mat(name, h):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = lin(h)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs[0], out.inputs[0])
    return m

def toon_mat(name, cols):
    m = bpy.data.materials["Skin"].copy(); m.name = name
    set_ramp(m.node_tree.nodes["Color Ramp"], cols); return m

def new_obj(name, build):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); build(bm); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.data.objects["Body"].users_collection[0].objects.link(o); return o

def subdivide(o):
    """un livello di Catmull-Clark applicato (i gruppi di vertici restano): zone di colore piu' fini"""
    m = o.modifiers.new("Sub", 'SUBSURF'); m.levels = m.render_levels = 1
    with bpy.context.temp_override(object=o, active_object=o):
        bpy.ops.object.modifier_move_to_index(modifier="Sub", index=0)
        bpy.ops.object.modifier_apply(modifier="Sub")

def parent_to_bone(o, rig, bone):
    bpy.context.view_layer.update(); mw = o.matrix_world.copy()
    o.parent = rig; o.parent_type = 'BONE'; o.parent_bone = bone; o.matrix_world = mw

def model_height():
    zs = [(o.matrix_world @ Vector(c)).z for o in bpy.data.objects
          if o.type == 'MESH' and o.name != "SandBall" for c in o.bound_box]
    return max(zs)

def affine(vals, lo, hi):
    a, b = vals.min(), vals.max()
    return lo + (vals - a)/(b - a)*(hi - lo) if b - a > 1e-6 else np.full_like(vals, (lo + hi)/2)


# ---------- concept ----------
class Concept:
    """le tre viste del turnaround, con sagome e zone di colore; py = riga, px = colonna dell'immagine"""
    def __init__(self, path, model_h, classify, name, axis_mask=None):
        im = bpy.data.images.load(path, check_existing=False); w, h = im.size
        self.rgb = np.array(im.pixels[:]).reshape(h, w, 4)[::-1, :, :3].copy(); bpy.data.images.remove(im)
        self.name = name
        bg = np.median(self.rgb[:20].reshape(-1, 3), axis=0)
        self.fg = np.abs(self.rgb - bg).sum(2) > 0.12
        cols = self.fg.sum(0) > 0; views = []; x = 0
        while x < w:
            if cols[x]:
                s = x
                while x < w and cols[x]: x += 1
                if x - s > 40: views.append((s, x-1))
            x += 1
        ys = np.where(self.fg.any(1))[0]
        self.top, self.foot = int(ys.min()), int(ys.max())
        self.K = (self.foot - self.top)/model_h                 # px per unita' del rig
        (f0, f1), (s0, s1), (b0, b1) = views[:3]
        self.views = {"front": (f0, f1), "side": (s0, s1), "back": (b0, b1)}
        self.cf, self.cb = (f0 + f1)/2, (b0 + b1)/2
        self.cls = classify(self.rgb) * self.fg
        # profilo: l'asse del corpo e' il centro della sagoma all'altezza della vita; con capelli lunghi sulla
        # schiena si usa axis_mask(cls) (pelle + costume) e il suo segmento piu' largo
        m = None if axis_mask is None else axis_mask(self)
        if m is not None:
            # anche i centri di fronte e retro dal solo corpo (una chioma asimmetrica sposterebbe il riquadro)
            fm = [np.mean(max(S, key=lambda q: q[1] - q[0])) for z in np.arange(0.85, 1.05, 0.02)
                  for S in [self.segs("front", self.row(z), mask=m)] if S]
            bm_ = [(S[0][0] + S[-1][1])/2 for z in np.arange(0.2, 0.5, 0.02) for S in [self.segs("back", self.row(z), mask=m)] if S]
            if fm: self.cf = float(np.mean(fm))
            if bm_: self.cb = float(np.mean(bm_))
        mids = []
        for z in np.arange(0.85, 1.05, 0.02):
            S = self.segs("side", self.row(z), mask=m)
            if S: mids.append(np.mean(S[0] if m is None else max(S, key=lambda q: q[1] - q[0])))
        self.cs = float(np.mean(mids))

    def row(self, z): return int(round(self.foot - z*self.K))

    def segs(self, view, py, merge=3, mask=None):
        x0, x1 = self.views[view]; m = self.fg if mask is None else mask
        if not 0 <= py < m.shape[0]: return []
        xs = np.where(m[py, x0:x1+1])[0] + x0
        if not len(xs): return []
        out = []; s = p = xs[0]
        for x in xs[1:]:
            if x - p > merge: out.append((s, p)); s = x
            p = x
        out.append((s, p)); return out

    def wx(self, px, view): return (px - self.cf)/self.K if view == "front" else (self.cb - px)/self.K
    def wy(self, px): return -(px - self.cs)/self.K          # profilo destro: il viso (-y) e' a destra

    def zone(self, p, n, allowed, r=4):
        """zona di colore del concept nel punto p (normale n), scelta fra 'allowed' per maggioranza"""
        py = self.row(p.z)
        if n.y < -0.25: px = self.cf + p.x*self.K             # anche le facce oblique (mandibola) dal fronte
        elif n.y > 0.25: px = self.cb - p.x*self.K
        else: px = self.cs - p.y*self.K                        # entrambi i fianchi dal profilo destro
        px = int(round(px))
        win = self.cls[max(py-r, 0):py+r+1, max(px-r, 0):px+r+1].ravel()
        best, cnt = allowed[0], -1
        for a in allowed:
            c = int((win == a).sum())
            if c > cnt: best, cnt = a, c
        return best

    def save_refs(self):
        os.makedirs(REF_DIR, exist_ok=True); paths = {}
        for v, (x0, x1) in self.views.items():
            a = np.concatenate([self.rgb[self.top:self.foot+1, x0:x1+1], np.ones((self.foot-self.top+1, x1-x0+1, 1))], 2)
            paths[v] = os.path.join(REF_DIR, "%s_%s.png" % (self.name, v)); save_rgba(a, paths[v])
        return paths


def add_refs(cc, scale):
    """immagini di riferimento in scena, allineate al modello finale (non si renderizzano: sono Empty)"""
    paths = cc.save_refs(); h = (cc.foot - cc.top)/cc.K*scale
    for v, rot, loc_off in (("front", (R(90), 0, 0), (0, 1.2, 0)), ("side", (R(90), 0, R(-90)), (-1.2, 0, 0)),
                            ("back", (R(90), 0, R(180)), (0, -1.2, 0))):
        x0, x1 = cc.views[v]; w = (x1 - x0 + 1)/cc.K*scale
        img = bpy.data.images.load(paths[v], check_existing=True)
        e = bpy.data.objects.new("Ref_" + v.capitalize(), None); e.empty_display_type = 'IMAGE'; e.data = img
        e.empty_display_size = max(w, h); e.empty_image_offset = (-0.5, 0.0)
        cx = {"front": cc.cf, "back": cc.cb, "side": cc.cs}[v]
        off = ((x0 + x1)/2 - cx)/cc.K*scale                       # centro immagine rispetto all'asse del corpo
        e.rotation_euler = rot
        if v == "front": e.location = (off, loc_off[1], 0)
        elif v == "back": e.location = (-off, loc_off[1], 0)
        else: e.location = (loc_off[0], -off, 0)
        e.empty_image_side = 'FRONT'; e.show_in_front = False
        bpy.data.objects["Body"].users_collection[0].objects.link(e)


# ---------- adattamento delle sagome ----------
def fit_body(cc, body, mask=None, smooth=3, split_legs=False, interp_arms=False):
    """busto, braccia e gambe: larghezza dalla vista frontale, profondita' dal profilo, fascia per fascia;
    mask (stessa forma dell'immagine) limita le sagome, per esempio a pelle + costume senza i capelli;
    split_legs: dove le cosce si toccano (una sola sagoma) ogni gamba prende la sua meta', cosi' le gambe
    restano dritte e continue con le fasce sotto, dove ogni gamba ha la sua sagoma;
    interp_arms: dove le braccia non si vedono (coperte dai capelli) la loro posizione si interpola dalle fasce
    in cui si vedono, invece di schiacciarle nella sagoma del busto"""
    me = body.data; sz = body.scale.z
    co = np.array([v.co[:] for v in me.vertices]); co[:, 2] *= sz      # spazio del rig
    gi = {g.index: g.name for g in body.vertex_groups}; part = []
    for v in me.vertices:
        ws = [(g.weight, gi[g.group]) for g in v.groups]; d = max(ws)[1] if ws else "chest"
        b = d.split(".")[0]; s = d.split(".")[-1] if "." in d else ""
        part.append(("a" + s) if b in ("upper_arm", "forearm", "hand") else ("l" + s) if b in ("thigh", "shin", "foot") else "h" if b == "head" else "t")
    part = np.array(part); new = co.copy()
    bins = np.round(co[:, 2]/BIN).astype(int)
    arm_fit = {"aL": [], "aR": []}; arm_pending = []
    for b in np.unique(bins):
        idx = bins == b; z = b*BIN; py = cc.row(z)
        F = cc.segs("front", py, mask=mask); S = cc.segs("side", py, mask=mask)
        P = part[idx]; I = np.where(idx)[0]
        center = I[np.isin(P, ["t", "lL", "lR", "h"])]; armL = I[P == "aL"]; armR = I[P == "aR"]
        legs = [I[P == "lL"], I[P == "lR"]]
        # larghezza dalla vista frontale (sinistra dell'immagine = destra del personaggio = -x)
        if F:
            Fw = [(cc.wx(s, "front"), cc.wx(e, "front")) for s, e in F]
            mid = min(range(len(Fw)), key=lambda i: abs((Fw[i][0] + Fw[i][1])/2))
            if len(Fw) >= 3:
                if len(center): new[center, 0] = affine(co[center, 0], *Fw[mid])
                if len(armR): new[armR, 0] = affine(co[armR, 0], *Fw[0]); arm_fit["aR"].append((z, co[armR, 0].min(), co[armR, 0].max(), *Fw[0]))
                if len(armL): new[armL, 0] = affine(co[armL, 0], *Fw[-1]); arm_fit["aL"].append((z, co[armL, 0].min(), co[armL, 0].max(), *Fw[-1]))
            elif interp_arms and (len(armL) or len(armR)) and \
                    (Fw[-1][1] - Fw[0][0]) < 0.8*(co[I, 0].max() - co[I, 0].min()):
                # sagoma stretta: le braccia sono coperte (dai capelli), si adatta solo il busto
                if len(center): new[center, 0] = affine(co[center, 0], *Fw[mid])
                arm_pending += [(z, armL, "aL"), (z, armR, "aR")]
            elif len(Fw) == 2 and not np.isin(P, ["t", "h"]).any():
                for leg, seg in ((legs[1], Fw[0]), (legs[0], Fw[1])):
                    if len(leg): new[leg, 0] = affine(co[leg, 0], *seg)
            else:
                allv = I if len(Fw) == 1 else center
                lo, hi = (Fw[0][0], Fw[-1][1]) if len(Fw) == 1 else Fw[mid]
                if split_legs and (len(legs[0]) or len(legs[1])):
                    trunk = I[np.isin(P, ["t", "h"])]
                    if len(trunk): new[trunk, 0] = affine(co[trunk, 0], lo, hi)
                    for leg, (a_, b_) in ((legs[1], (lo, 0.0)), (legs[0], (0.0, hi))):
                        if len(leg): new[leg, 0] = affine(co[leg, 0], a_, b_)
                elif len(allv): new[allv, 0] = affine(co[allv, 0], lo, hi)
                for grp, side in ((armL, "aL"), (armR, "aR")):         # riferimento per le fasce con braccia coperte
                    if len(grp) and len(Fw) == 1: arm_fit[side].append((z, co[grp, 0].min(), co[grp, 0].max(), new[grp, 0].min(), new[grp, 0].max()))
        # profondita' dal profilo: busto e gambe sulla sagoma, braccia con la stessa trasformazione
        if S and len(center):
            s, e = max(S, key=lambda q: q[1] - q[0]); ylo, yhi = cc.wy(e), cc.wy(s)
            a, bb = co[center, 1].min(), co[center, 1].max()
            if bb - a > 1e-6:
                k = (yhi - ylo)/(bb - a)
                for grp in (center, armL, armR):
                    if len(grp): new[grp, 1] = ylo + (co[grp, 1] - a)*k
    # braccia coperte: spostamento e scala interpolati in altezza dalle fasce dove si vedono
    for z, grp, side in arm_pending:
        fits = arm_fit[side]
        if not len(grp) or not fits: continue
        zs_, a0, a1, b0, b1 = (np.array(c) for c in zip(*sorted(fits)))
        k = np.interp(z, zs_, (b1 - b0)/np.maximum(a1 - a0, 1e-6)); off = np.interp(z, zs_, b0 - a0*(b1 - b0)/np.maximum(a1 - a0, 1e-6))
        new[grp, 0] = co[grp, 0]*k + off
    # un passaggio di levigatura per togliere i gradini tra le fasce
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    for v, c in zip(bm.verts, new): v.co = Vector((c[0], c[1], c[2]/sz))
    for _ in range(smooth):
        bmesh.ops.smooth_vert(bm, verts=bm.verts, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=False)
    bm.to_mesh(me); bm.free()

def smooth_profile(z, vals, sigma, line=False):
    """profilo lungo l'altezza: riempie i buchi (NaN) per interpolazione e leviga con una gaussiana (sigma in fasce);
    line=True lo sostituisce con la retta che meglio lo approssima (assi di gambe e braccia dritti)"""
    v = np.array(vals, float); ok = ~np.isnan(v)
    if ok.sum() == 0: return v
    if ok.sum() == 1: return np.full_like(v, v[ok][0])
    v = np.interp(z, z[ok], v[ok])
    if line: return np.polyval(np.polyfit(z[ok], np.array(vals, float)[ok], 1), z)
    r = int(round(3*sigma)); k = np.arange(-r, r + 1); g = np.exp(-0.5*(k/sigma)**2); g /= g.sum()
    return np.convolve(np.pad(v, r, mode="edge"), g, mode="valid")

def fit_body_regular(cc, body, mask, sigma=2.5, smooth=2):
    """corpo regolare dal concept: dalle sagome si prendono solo le misure (meta' larghezza e profondita' di busto,
    gambe e braccia lungo l'altezza), rese simmetriche e levigate; assi di gambe e braccia dritti. Il modello base,
    gia' regolare e simmetrico, viene scalato in modo continuo attorno ai suoi assi; alle giunture le parti si
    fondono con i pesi del rig; alla fine simmetria destra/sinistra esatta. Niente deformazioni fascia per fascia
    (copierebbero le irregolarita' del disegno: gambe storte, zig-zag)."""
    me = body.data; sz = body.scale.z
    co = np.array([v.co[:] for v in me.vertices]); co[:, 2] *= sz
    gi = {g.index: g.name for g in body.vertex_groups}
    PARTS = ["t", "lL", "lR", "aL", "aR"]
    def part_of(name):
        b = name.split(".")[0]; s = name.split(".")[-1] if "." in name else ""
        return ("a" + s) if b in ("upper_arm", "forearm", "hand") else ("l" + s) if b in ("thigh", "shin", "foot") else "t"
    W = np.zeros((len(co), len(PARTS)))
    for v in me.vertices:
        for g in v.groups: W[v.index, PARTS.index(part_of(gi[g.group]))] += g.weight
    W[W.sum(1) == 0, 0] = 1; W /= W.sum(1, keepdims=True)
    dom = W.argmax(1)
    zs = np.arange(co[:, 2].min(), co[:, 2].max() + BIN, BIN); n = len(zs)
    # misure del concept per fascia (simmetriche): busto, gamba, braccio
    tw = np.full(n, np.nan); yf = tw.copy(); yb = tw.copy()
    lc, lw = tw.copy(), tw.copy(); ac, aw = tw.copy(), tw.copy(); ly0, ly1 = tw.copy(), tw.copy()
    has = lambda p, k: ((dom == PARTS.index(p)) & (np.abs(co[:, 2] - zs[k]) < BIN/2)).any()
    for k, z in enumerate(zs):
        py = cc.row(z); F = cc.segs("front", py, mask=mask); S = cc.segs("side", py, mask=mask)
        Fw = [(cc.wx(s, "front"), cc.wx(e, "front")) for s, e in F]
        legs = has("lL", k) or has("lR", k); torso = has("t", k); arms = has("aL", k) or has("aR", k)
        if len(Fw) >= 3:
            mid = min(Fw, key=lambda q: abs(q[0] + q[1]))
            if torso: tw[k] = (mid[1] - mid[0])/2
            if arms: ac[k] = (abs(Fw[0][0] + Fw[0][1]) + abs(Fw[-1][0] + Fw[-1][1]))/4; aw[k] = ((Fw[0][1] - Fw[0][0]) + (Fw[-1][1] - Fw[-1][0]))/4
        elif len(Fw) == 2 and legs and not torso:
            lc[k] = (abs(Fw[0][0] + Fw[0][1]) + abs(Fw[1][0] + Fw[1][1]))/4; lw[k] = ((Fw[0][1] - Fw[0][0]) + (Fw[1][1] - Fw[1][0]))/4
        elif len(Fw) == 1 and not arms:
            h = (Fw[0][1] - Fw[0][0])/2
            if torso: tw[k] = h
            if legs: lc[k], lw[k] = h/2, h/2                    # cosce che si toccano: meta' sagoma per gamba
        if S:
            s, e = max(S, key=lambda q: q[1] - q[0])
            if torso: yf[k], yb[k] = cc.wy(e), cc.wy(s)
            if legs and not torso: ly0[k], ly1[k] = cc.wy(e), cc.wy(s)
    T = {"tw": smooth_profile(zs, tw, sigma), "yf": smooth_profile(zs, yf, sigma), "yb": smooth_profile(zs, yb, sigma),
         "lc": smooth_profile(zs, lc, sigma, line=True), "lw": smooth_profile(zs, lw, sigma),
         "ly0": smooth_profile(zs, ly0, sigma), "ly1": smooth_profile(zs, ly1, sigma),
         "ac": smooth_profile(zs, ac, sigma, line=True), "aw": smooth_profile(zs, aw, sigma)}
    # le stesse misure sul modello base (levigate), per scalare attorno ai suoi assi
    def cur(p, f, minimum=None):
        out = np.full(n, np.nan); m = np.isin(dom, [PARTS.index(q) for q in p.split("+")])
        for k, z in enumerate(zs):
            sel = m & (np.abs(co[:, 2] - z) < BIN/2)
            if sel.sum() >= 3:
                val = f(co[sel])
                if minimum is None or val > minimum: out[k] = val
        return smooth_profile(zs, out, sigma)
    # busto confrontato con busto + gambe (la sagoma del concept ai fianchi comprende le cosce)
    C = {"tw": cur("t+lL+lR", lambda c: np.abs(c[:, 0]).max(), minimum=0.03),
         "ty0": cur("t+lL+lR", lambda c: c[:, 1].min()), "ty1": cur("t+lL+lR", lambda c: c[:, 1].max())}
    for p in ("lL", "aL"):
        C[p + "c"] = cur(p, lambda c: c[:, 0].mean()); C[p + "w"] = cur(p, lambda c: np.abs(c[:, 0] - c[:, 0].mean()).max())
        C[p + "y"] = cur(p, lambda c: c[:, 1].mean()); C[p + "d"] = cur(p, lambda c: np.abs(c[:, 1] - c[:, 1].mean()).max())
    at = lambda arr, z: np.interp(z, zs, arr)
    z = co[:, 2]; x, y = co[:, 0], co[:, 1]; out = np.zeros((len(co), len(PARTS), 2))
    # busto: scala in x attorno al centro, in y sul davanti/dietro del profilo
    sx = np.clip(at(T["tw"], z)/np.maximum(at(C["tw"], z), 1e-4), 0.6, 1.6)     # mai scale estreme
    y0c, y1c = at(C["ty0"], z), at(C["ty1"], z); y0t, y1t = at(T["yf"], z), at(T["yb"], z)
    sy = np.clip((y1t - y0t)/np.maximum(y1c - y0c, 1e-4), 0.6, 1.6)
    out[:, 0, 0] = x*sx; out[:, 0, 1] = (y0t + y1t)/2 + (y - (y0c + y1c)/2)*sy
    # gambe e braccia: attorno al proprio asse (lato sinistro +x, destro -x, stesse misure)
    for j, p, (kc, kw) in ((1, "lL", ("lc", "lw")), (2, "lR", ("lc", "lw")), (3, "aL", ("ac", "aw")), (4, "aR", ("ac", "aw"))):
        sg = 1 if p.endswith("L") else -1; q = p[0] + "L"
        cc_ = sg*np.abs(at(C[q + "c"], z)); cw = at(C[q + "w"], z)
        out[:, j, 0] = sg*at(T[kc], z) + (x - cc_)*np.clip(at(T[kw], z)/np.maximum(cw, 1e-4), 0.6, 1.6)
        if p[0] == "l":
            yc_, yd = at(C[q + "y"], z), at(C[q + "d"], z); y0, y1 = at(T["ly0"], z), at(T["ly1"], z)
            out[:, j, 1] = (y0 + y1)/2 + (y - yc_)*np.clip(((y1 - y0)/2)/np.maximum(yd, 1e-4), 0.6, 1.6)
        else:
            out[:, j, 1] = out[:, 0, 1]                           # braccia: profondita' come il busto
    new = co.copy(); new[:, 0] = (W*out[:, :, 0]).sum(1); new[:, 1] = (W*out[:, :, 1]).sum(1)
    # simmetria esatta: ogni vertice e il suo specchio (nel modello base) prendono posizioni speculari
    from mathutils.kdtree import KDTree
    kd = KDTree(len(co))
    for i, c in enumerate(co): kd.insert(c, i)
    kd.balance()
    for i, c in enumerate(co):
        j = kd.find((-c[0], c[1], c[2]))[1]
        if j > i:
            xa = (new[i, 0] - new[j, 0])/2; ya = (new[i, 1] + new[j, 1])/2
            new[i, 0], new[j, 0] = xa, -xa; new[i, 1] = new[j, 1] = ya
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    for v, c in zip(bm.verts, new): v.co = Vector((c[0], c[1], c[2]/sz))
    for _ in range(smooth):
        bmesh.ops.smooth_vert(bm, verts=bm.verts, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    bm.to_mesh(me); bm.free()


def paint_zones(cc, o, mats, allowed, smooth=0):
    """materiale di ogni faccia dalla zona del concept: allowed = codici zona nell'ordine degli slot;
    smooth = passaggi di pulizia: una faccia senza vicine della sua zona (o con una sola e almeno tre diverse)
    prende la zona prevalente tra le vicine: spariscono faccette isolate e punte, le zone piccole come il bikini
    non vengono erose"""
    o.data.materials.clear()
    for m in mats: o.data.materials.append(m)
    mw = o.matrix_world; nm = mw.to_3x3().inverted().transposed()
    idx = []
    for f in o.data.polygons:
        p = mw @ f.center; n = (nm @ f.normal).normalized()
        idx.append(allowed.index(cc.zone(p, n, allowed)))
    if smooth:
        bm = bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
        nbr = [[g.index for e in f.edges for g in e.link_faces if g.index != f.index] for f in bm.faces]; bm.free()
        for _ in range(smooth):
            new = []
            for i, ns in enumerate(nbr):
                votes = np.bincount([idx[j] for j in ns], minlength=len(allowed))
                own = votes[idx[i]]; other = len(ns) - own
                new.append(int(votes.argmax()) if own == 0 or (own == 1 and other >= 3) else idx[i])
            idx = new
    for f, i in zip(o.data.polygons, idx): f.material_index = i
