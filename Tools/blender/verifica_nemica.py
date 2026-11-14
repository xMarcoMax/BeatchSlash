"""Self-check della nemica, dentro Blender dopo blender_pipeline.py e nemica_pipeline.py.

Con nemica.blend aperto e atlante rigenerato: check_enemy(). Non modifica i file.
"""
import re


def check_walk_eyes():
    """Il timbro della diagonale non deve alternare occhi mancanti durante il passo."""
    counts = []
    for frame in range(8):
        clear_pose(); walk_e(frame/8*2*math.pi)
        render_sprites([-45])
        stamps = globals()['LAST_EYE_STAMPS']
        assert len(stamps) == 1 and stamps[0]['width'] == 2 and stamps[0]['written'] == 6, (frame, stamps)
        counts.append(stamps[0]['written'])
    clear_pose(); idle(0)
    return counts


def check_base_actions():
    """Le action della base devono conservare il passo raccolto anche senza la pipeline procedurale."""
    names = ['walk', 'run', 'attack_walk', 'attack_run']
    with bpy.data.libraries.load(os.path.join(BLEND_DIR, 'base_personaggio.blend'), link=False) as (source, loaded):
        loaded.actions = list(names)
    try:
        for name, action in zip(names, loaded.actions):
            assert action is not None, f'Action della base mancante: {name}'
            curves = [fc for layer in action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
            hips = next(fc for fc in curves if fc.data_path == 'pose.bones["hips"].rotation_euler' and fc.array_index == 1)
            peak = 4 if 'run' in name else 3
            assert abs(max(abs(k.co.y) for k in hips.keyframe_points)-math.radians(peak)) < 1e-6, f'Bacino della base troppo aperto: {name}'
            for side, sign in [('L', -1), ('R', 1)]:
                thigh = next(fc for fc in curves if fc.data_path == f'pose.bones["thigh.{side}"].rotation_euler' and fc.array_index == 2)
                assert all(abs(k.co.y-sign*math.radians(1.5)) < 1e-6 for k in thigh.keyframe_points), f'Divaricazione nella base: {name}/{side}'
        return names
    finally:
        for action in loaded.actions:
            if action is not None: bpy.data.actions.remove(action)


def check_enemy():
    """Controlla modello, IK del flirt e contratto dell'atlante usato da Godot."""
    global REST_FEET
    mesh_counts = {}
    for name in ('Body', 'Head', 'Hair', 'FrontHair', 'SuitTies'):
        obj = bpy.data.objects.get(name)
        assert obj is not None and obj.type == 'MESH', f'Mesh mancante: {name}'
        coords = np.array([v.co[:] for v in obj.data.vertices])
        assert len(coords) and np.isfinite(coords).all(), f'Vertici non validi: {name}'
        mesh_counts[name] = len(coords)

    body = bpy.data.objects['Body']
    rest = body.data.attributes.get('rest_co')
    assert rest is not None and len(rest.data) == len(body.data.vertices), 'rest_co mancante o incompleto'
    coords = np.array([v.co[:] for v in body.data.vertices])
    coords[:, 2] *= body.scale.z
    assert np.allclose(coords, [v.vector[:] for v in rest.data], atol=1e-6), 'rest_co non segue il corpo ricostruito'
    hair = bpy.data.objects['Hair']
    assert all(abs(sum(g.weight for g in v.groups)-1) < 1e-5 for v in hair.data.vertices), 'Pesi Hair non normalizzati'

    clear_pose(); bpy.context.view_layer.update()
    head = bpy.data.objects['Head']; mw = head.matrix_world
    normal_matrix = mw.to_3x3().inverted().transposed()
    temples, cheeks = [], []
    for face in head.data.polygons:
        p = mw @ face.center; row = 912-p.z*(759/1.9476547); x = abs(p.x)*(759/1.9476547)
        normal = (normal_matrix @ face.normal).normalized()
        if 70 < x < 125 and 200 < row < 280 and -0.5 < normal.y < 0.18:
            temples.append(face.material_index)
        if 315 < row < 370 and normal.y < 0.12 and x < 110:
            cheeks.append(face.material_index)
    assert len(temples) > 20 and temples.count(1)/len(temples) > 0.85, 'Attaccatura troppo aperta alle tempie'
    assert len(cheeks) > 20 and cheeks.count(0)/len(cheeks) > 0.95, 'Capelli dipinti sulle guance'

    # Passo e busto della nemica devono mantenere le stesse trasformazioni del Player.
    shared_bones = ['hips', 'spine', 'chest'] + [bone+'.'+side for bone in ('thigh', 'shin', 'foot') for side in 'LR']
    for frame in range(8):
        clear_pose(); walk(frame/8*2*math.pi)
        expected = {name: (pb()[name].location.copy(), pb()[name].rotation_euler.copy()) for name in shared_bones}
        clear_pose(); walk_e(frame/8*2*math.pi)
        for name, (location, rotation) in expected.items():
            assert (pb()[name].location-location).length < 1e-6, f'Passo divergente: {name}/{frame}'
            assert max(abs(a-b) for a,b in zip(pb()[name].rotation_euler, rotation)) < 1e-6, f'Rotazione diversa dal Player: {name}/{frame}'

    max_foot_error = 0.0
    try:
        REST_FEET = None
        for frame in range(12):
            clear_pose()
            flirt(frame/12*2*math.pi)
            bpy.context.view_layer.update()
            for side in 'LR':
                error = (pb()['foot.'+side].head-REST_FEET[side]).length
                max_foot_error = max(max_foot_error, error)
                assert error < 0.005, f'Piede {side} scivola nel flirt, frame {frame}: {error:.6f}'
    finally:
        REST_FEET = None
        clear_pose()
        idle(0)
        bpy.context.view_layer.update()

    groups = [('walk', 8, 8.0, True), ('flirt', 12, 8.0, True),
              ('idle', 6, 5.0, True), ('dead', 8, 12.0, False)]
    directions = ['up', 'down', 'right', 'left', 'up_right', 'up_left', 'down_right', 'down_left']
    sheet = grab(os.path.join(PROJ, 'enemy_spritesheet.png'))
    assert SIZE == 64, f'Cella nemica errata: {SIZE}'
    assert sheet.shape == (32*SIZE, 12*SIZE, 4), f'Dimensioni atlante errate: {sheet.shape}'
    assert np.isfinite(sheet).all(), 'Atlante con valori non finiti'
    checked_frames = 0
    for group, (name, count, _, _) in enumerate(groups):
        for direction, suffix in enumerate(directions):
            row = sheet[(group*8+direction)*SIZE:(group*8+direction+1)*SIZE]
            assert not row[:, count*SIZE:, 3].any(), f'Padding non vuoto: {name}_{suffix}'
            for frame in range(count):
                alpha = row[:, frame*SIZE:(frame+1)*SIZE, 3]
                opaque = alpha > 0.5
                assert opaque.any(), f'Frame vuoto: {name}_{suffix}/{frame}'
                assert not (opaque[0].any() or opaque[-1].any() or opaque[:, 0].any() or opaque[:, -1].any()), f'Clipping sul bordo: {name}_{suffix}/{frame}'
                checked_frames += 1

    with open(os.path.join(PROJ, 'enemy_frames.tres'), encoding='utf-8-sig') as source:
        text = source.read()
    atlases = {}
    for match in re.finditer(r'^\[sub_resource type="AtlasTexture" id="([^"]+)"\]\s*(.*?)(?=^\[|\Z)', text, re.S | re.M):
        resource_id, properties = match.groups()
        assert resource_id not in atlases, f'AtlasTexture duplicata: {resource_id}'
        region = re.search(r'^region\s*=\s*Rect2\(([^)]+)\)', properties, re.M)
        assert region is not None, f'Regione mancante: {resource_id}'
        assert re.search(r'^filter_clip\s*=\s*(true|1)\s*$', properties, re.M), f'filter_clip disattivo: {resource_id}'
        atlases[resource_id] = tuple(float(value.strip()) for value in region.group(1).split(','))
    animations = re.findall(r'"frames":\s*\[(.*?)\],\s*"loop":\s*(true|false|[01]),\s*"name":\s*&"([^"]+)",\s*"speed":\s*([\d.]+)', text, re.S)
    assert len(animations) == 32, f'Numero animazioni errato: {len(animations)}'
    expected = {name+'_'+direction: (count, speed, loop, group*8+index)
                for group, (name, count, speed, loop) in enumerate(groups)
                for index, direction in enumerate(directions)}
    seen = set()
    checked_regions = 0
    for frames, loop, name, speed in animations:
        assert name in expected and name not in seen, f'Animazione inattesa o duplicata: {name}'
        count, expected_speed, expected_loop, row = expected[name]
        textures = re.findall(r'"texture":\s*SubResource\("([^"]+)"\)', frames)
        assert len(textures) == count, f'Numero frame errato: {name}'
        for frame, resource_id in enumerate(textures):
            assert resource_id in atlases, f'AtlasTexture mancante: {name}/{frame}: {resource_id}'
            expected_region = (frame*SIZE, row*SIZE, SIZE, SIZE)
            assert atlases[resource_id] == expected_region, f'Regione errata: {name}/{frame}: {atlases[resource_id]}, attesa {expected_region}'
            checked_regions += 1
        assert float(speed) == expected_speed and (loop in ('true', '1')) == expected_loop, f'Tempi o loop errati: {name}'
        seen.add(name)
    assert seen == set(expected), 'Animazioni mancanti'
    return {'meshes': mesh_counts, 'max_foot_error': max_foot_error, 'base_actions': check_base_actions(),
            'walk_eyes': check_walk_eyes(),
            'frames': checked_frames, 'animations': len(animations),
            'regions': checked_regions, 'atlas_shape': list(sheet.shape)}
