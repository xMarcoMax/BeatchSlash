"""Nemica dal turnaround approvato; eseguire dopo blender_pipeline.py su base_personaggio.blend.

Salvare come nemica.blend, poi make_enemy('body') e make_enemy('hair'), salvando ogni fase.
Riusa corpo regolare, testa, visual hull, rig e materiale continuo della protagonista.
Le misure del bikini e delle ciocche appartengono invece al concept della nemica.
"""
exec(open(os.path.join(BLEND_DIR, 'personaggio_modello.py'), encoding='utf-8-sig').read())

GIRL_CONCEPT = os.path.normpath(os.path.join(BLEND_DIR, '../../Assets/ConceptArt/Enemies/enemy_turnaround.png'))
STRAND_SCALE, STRAND_STRETCH, STRAND_DEPTH = 0.16, 9.0, 0.009
_girl_suit = apply_girl_suit
_front_hair = build_front_hair


def girl_classify(c):
    """Zone cromatiche del concept; sfondo grigio e contorni restano esclusi."""
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    return np.select([(r > g*1.18) & (r > b*1.3) & (r > 0.28),
                      (b > g*1.22) & (r > g*1.18) & (b > r*0.85) & (b > 0.15),
                      (g > r*1.25) & (g > b*1.05) & (g > 0.15)], [1, 2, 3], default=0)


def apply_girl_suit(cc, body):
    """Bikini triangolare a lacci su coordinate di riposo, con le stesse rampe toon del Player."""
    _girl_suit(cc, body)
    mat = body.data.materials[0]
    nodes, links = mat.node_tree.nodes, mat.node_tree.links

    def op(kind, a, b=0):
        n = nodes.new('ShaderNodeMath'); n.operation = kind
        for socket, value in zip(n.inputs, (a, b)):
            if isinstance(value, (int, float)): socket.default_value = value
            else: links.new(value, socket)
        return n.outputs[0]

    def between(v, low, high):
        return op('MULTIPLY', op('GREATER_THAN', v, low), op('LESS_THAN', v, high))

    xyz = next(n for n in nodes if n.type == 'SEPXYZ')
    x = op('MULTIPLY', op('ABSOLUTE', xyz.outputs['X']), cc.K)
    row = op('SUBTRACT', cc.foot, op('MULTIPLY', xyz.outputs['Z'], cc.K))
    front = op('LESS_THAN', xyz.outputs['Y'], 0)
    # Coppe: vertice (38, 443), scollo fino al centro (4, 493), bordo inferiore curvo.
    neckline = op('SUBTRACT', 499, op('MULTIPLY', x, 1.45))
    upper = op('MAXIMUM', neckline, op('ADD', 443-38*1.1, op('MULTIPLY', x, 1.1)))
    cup_x = op('SUBTRACT', x, 36)
    hem = op('SUBTRACT', 503, op('MULTIPLY', op('MULTIPLY', cup_x, cup_x), 0.009))
    cups = op('MULTIPLY', between(row, upper, hem), op('LESS_THAN', x, 70))
    # Lacci verso il collo, fascia sottile dietro e nodo centrale.
    strap_x = op('ADD', 22, op('MULTIPLY', op('SUBTRACT', row, 410), 0.52))
    strap = op('MULTIPLY', between(row, 410, 451), op('LESS_THAN', op('ABSOLUTE', op('SUBTRACT', x, strap_x)), 2.8))
    center = op('MULTIPLY', between(row, 490, 497), op('LESS_THAN', x, 12))
    top = op('MAXIMUM', op('MAXIMUM', cups, strap), center)
    back = op('MULTIPLY', between(row, 487, 494), op('LESS_THAN', x, 85))
    top = op('ADD', op('MULTIPLY', top, front), op('MULTIPLY', back, op('SUBTRACT', 1, front)))
    waist = op('SUBTRACT', 597, op('MULTIPLY', op('MULTIPLY', x, x), 0.0045))
    leg = op('SUBTRACT', 635, op('MULTIPLY', x, 1.12))
    bottom_front = between(row, waist, leg)
    bottom_back = between(row, op('SUBTRACT', 603, op('MULTIPLY', x, 0.33)), op('SUBTRACT', 652, op('MULTIPLY', x, 1.15)))
    bottom = op('ADD', op('MULTIPLY', bottom_front, front), op('MULTIPLY', bottom_back, op('SUBTRACT', 1, front)))
    hip_string = op('MULTIPLY', between(row, op('SUBTRACT', waist, 3), op('ADD', waist, 3)), between(x, 40, 90))
    mask = op('MAXIMUM', top, op('MAXIMUM', bottom, hip_string))
    links.new(mask, nodes['SuitMask'].inputs[0])
    # Rimuovere i vecchi confini del costume, ora scollegati dalla nuova maschera.
    output = next(n for n in nodes if n.type == 'OUTPUT_MATERIAL')
    used = set()
    def visit(n):
        if n in used: return
        used.add(n)
        for s in n.inputs:
            for link in s.links: visit(link.from_node)
    visit(output)
    for n in list(nodes):
        if n not in used: nodes.remove(n)


def build_front_hair(cc, head, rig):
    paths = [
        [(321, 170, 1), (294, 182, 12), (267, 210, 17), (246, 249, 14), (230, 292, 12), (222, 338, 8), (231, 380, 1)],
        [(330, 170, 1), (358, 182, 12), (383, 210, 17), (399, 249, 14), (408, 292, 12), (413, 338, 8), (403, 380, 1)],
    ]
    _front_hair(cc, head, rig, paths=paths, part_color='#4b2a78')


def paint_girl_scalp(cc, head, hairline, chin):
    mw = head.matrix_world; nm = mw.to_3x3().inverted().transposed()
    for face in head.data.polygons:
        p = mw @ face.center
        row, x = cc.foot-p.z*cc.K, abs(p.x)*cc.K
        edge = hairline-39 + 75*(1-math.exp(-(x/75)**2)) + 10*math.exp(-(x/12)**2)
        # Chiudere le tempie senza dipingere capelli sulle guance viste di profilo.
        side_limit = -0.12 + 0.3*min(1, max(0, (row-hairline-20)/55))
        face.material_index = 0 if row > edge and (nm @ face.normal).normalized().y < side_limit else 1
    head.data.update()


def refine_enemy_body(body):
    """Volumi morbidi del concept, continui con il busto invece di sfere sovrapposte."""
    for v in body.data.vertices:
        x, y, z = v.co.x, v.co.y, v.co.z*body.scale.z
        arm = sum(g.weight for g in v.groups if body.vertex_groups[g.group].name.startswith(('upper_arm.', 'forearm.', 'hand.')))
        chest = math.exp(-((abs(x)-0.09)/0.075)**2-((z-1.10)/0.085)**2)
        hip = math.exp(-((abs(x)-0.10)/0.10)**2-((z-0.77)/0.10)**2)
        v.co.y += (1-arm)*(-0.065*chest*min(1, max(0, -y/0.06)) + 0.03*hip*min(1, max(0, y/0.06)))
    body.data.update()


def build_ties(body, rig, cc):
    """Fiocchi ai fianchi: piccoli tubi adagiati sul corpo e legati al bacino."""
    old = bpy.data.objects.get('SuitTies')
    if old: bpy.data.objects.remove(old, do_unlink=True)
    mw = body.matrix_world; mi = mw.inverted()
    tree = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    vertices, faces = [], []
    paths = [[(0, 0), (-6, -8), (-14, -5), (-10, 2), (0, 0), (7, -8), (14, -4), (9, 3), (0, 0)],
             [(0, 0), (-3, 12), (-7, 25)], [(0, 0), (6, 13), (8, 28)]]
    for sign in (-1, 1):
        for path in paths:
            p = np.array(path, float); t = np.linspace(0, len(p)-1, (len(p)-1)*5+1)
            points = np.stack([np.interp(t, np.arange(len(p)), p[:, k]) for k in range(2)], 1)
            offset = len(vertices)
            for dx, dy in points:
                x, z = sign*(72+dx)/cc.K, (cc.foot-583-dy)/cc.K
                hit = tree.ray_cast(mi @ Vector((x, -5, z)), (mi.to_3x3() @ Vector((0, 1, 0))).normalized())[0]
                y = (mw @ hit).y-0.007 if hit is not None else -0.08
                for k in range(6):
                    a = 2*math.pi*k/6
                    vertices.append((x+0.0045*math.cos(a), y+0.0045*math.sin(a), z))
            for j in range(len(points)-1):
                for k in range(6):
                    a = offset+j*6+k; b = offset+j*6+(k+1)%6
                    faces.append((a,b,b+6,a+6))
    mesh = bpy.data.meshes.new('SuitTies'); mesh.from_pydata(vertices, [], faces); mesh.update()
    ob = bpy.data.objects.new('SuitTies', mesh);body.users_collection[0].objects.link(ob)
    mesh.materials.append(bpy.data.materials['Suit'])
    for f in mesh.polygons: f.use_smooth = True
    parent_to_bone(ob, rig, 'hips')


def make_enemy(stage='all'):
    if stage == 'all':
        info = make_enemy('body')
        info.update(make_enemy('hair'))
        return info
    for name, colors in [('Hair', ['#2a1240', '#4b2a78', '#7043a1', '#a97fd9']),
                         ('Suit', ['#16503a', '#25805a', '#3db57d', '#8de0b4'])]:
        ramp = next(n for n in bpy.data.materials[name].node_tree.nodes if n.type == 'VALTORGB')
        set_ramp(ramp, colors)
    info = make_girl(stage, concept_name='enemy')
    if stage in ('body', 'all'):
        body = bpy.data.objects['Body']
        refine_enemy_body(body)
        cc = Concept(GIRL_CONCEPT, GIRL_H, girl_classify, 'enemy', axis_mask=girl_body_mask)
        apply_girl_suit(cc, body)
        bpy.context.view_layer.update()
        build_ties(body, bpy.data.objects['Rig'], cc)
    bpy.data.objects['SandBall'].hide_render = True
    return info
