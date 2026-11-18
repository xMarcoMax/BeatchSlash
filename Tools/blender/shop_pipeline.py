"""Chiosco dal concept approvato. Eseguire in Blender via MCP, non da Python esterno."""
import bpy
import bmesh
import math
import os
import json
import re
import tempfile
import numpy as np
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.normpath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(PROJECT, 'Assets', 'Objects', 'Shop')
CONCEPT = os.path.join(PROJECT, 'Assets', 'ConceptArt', 'Shop', 'shop_with_shopkeeper_turnaround.png')
SIZE = 160
ORTHO = 2.2 * SIZE / 48
ELEV = math.radians(25)
YAW = 0.0  # vista frontale: bancone davanti (prima -20 gradi, quasi isometrica)
TARGET_Z = 1.55
TMP = tempfile.gettempdir()
ANIMS = [('idle', 8, 5, True), ('clean_glass', 16, 8, False), ('wipe_counter', 16, 8, False)]
COMMON = {}
exec(open(os.path.join(HERE, 'blender_pipeline.py'), encoding='utf-8').read(), COMMON)
HELPERS = dict(COMMON)
exec(open(os.path.join(HERE, 'concept_model.py'), encoding='utf-8').read(), HELPERS)
toon_mat, flat_mat = HELPERS['toon_mat'], HELPERS['flat_mat']
grab, save_rgba = COMMON['grab'], COMMON['save_rgba']
M = {m.name[5:]: m for m in bpy.data.materials if m.name.startswith('Shop_') and '.' not in m.name}


def mesh(name, vertices, faces, mat, group='Front'):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.data.collections[group].objects.link(obj)
    if mat:
        data.materials.append(M[mat] if isinstance(mat, str) else mat)
    obj.parent = bpy.data.objects['ShopRoot']
    return obj


def box(name, loc, size, mat, group='Front', bevel=0.015):
    x, y, z = [d / 2 for d in size]
    o = mesh(name, [(a*x, b*y, c*z) for a,b,c in
        [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]],
        [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)], mat, group)
    o.location = loc
    if bevel:
        mod = o.modifiers.new('SoftEdges', 'BEVEL')
        mod.width, mod.segments = bevel, 1
    return o


def ellipsoid(name, loc, scale, mat, group='Front', segments=16, rings=8):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, radius=1)
    data = bpy.data.meshes.new(name)
    bm.to_mesh(data)
    bm.free()
    obj = bpy.data.objects.new(name, data)
    bpy.data.collections[group].objects.link(obj)
    obj.parent = bpy.data.objects['ShopRoot']
    obj.location, obj.scale = loc, scale
    data.materials.append(M[mat])
    for p in data.polygons:
        p.use_smooth = True
    return obj


def cylinder(name, loc, radius, depth, mat, group='Front', top=None, sides=16):
    rt = radius if top is None else top
    vertices = [(r*math.cos(a*math.tau/sides),r*math.sin(a*math.tau/sides),z)
                for r,z in [(radius,-depth/2),(rt,depth/2)] for a in range(sides)]
    faces = [tuple(reversed(range(sides))), tuple(range(sides,2*sides))]
    faces += [(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)]
    o = mesh(name, vertices, faces, mat, group)
    o.location = loc
    return o


def rod(name, a, b, radius, mat, group='Front', top=None):
    a, b = Vector(a), Vector(b)
    o = cylinder(name,(a+b)/2,radius,(b-a).length,mat,group,top=top,sides=10)
    o.rotation_euler = (b-a).to_track_quat('Z','Y').to_euler()
    return o


def curve(name, points, radius, mat, group='Front'):
    data = bpy.data.curves.new(name,'CURVE')
    data.dimensions = '3D'
    data.bevel_depth, data.bevel_resolution = radius, 2
    s = data.splines.new('POLY')
    s.points.add(len(points)-1)
    for p,co in zip(s.points,points):
        p.co = (*co,1)
    o = bpy.data.objects.new(name,data)
    bpy.data.collections[group].objects.link(o)
    o.parent = bpy.data.objects['ShopRoot']
    data.materials.append(M[mat])
    return o


def materials():
    palettes = {
        'Wood':['#63311c','#a65c28','#d28a40','#efb55e'],
        'WoodLight':['#81421f','#bb7330','#e8a34c','#ffcd78'],
        'WoodDark':['#3a2119','#653b25','#8f5931','#b27844'],
        'Straw':['#a45a24','#cf812d','#f2b648','#ffda79'],
        'StrawLight':['#b56b29','#e39a37','#ffc85c','#ffe096'],
        'StrawDark':['#82421f','#b76c27','#e2a13c','#f5bf58'],
        'Red':['#8c2328','#c73633','#ee4b45','#ff7970'],
        'Cream':['#aa8155','#ddbf84','#f4dcaa','#fff2d2'],
        'Metal':['#484449','#68616a','#8b8180','#b5a99b'],
        'SkinShop':['#8f4a2c','#c77843','#e49c60','#f6bc7e'],
        'Shirt':['#8b352a','#bd503b','#e47553','#f7a079'],
        'HairShop':['#5c4435','#8d7560','#b8a184','#d7c6a1'],
        'Teal':['#174c4f','#287d7f','#4badab','#8bd5cc'],
        'Green':['#606221','#929c32','#bdc24e','#e8df7a'],
        'Pink':['#803a48','#b65d64','#e18d8a','#f4bcaa'],
        'Juice':['#bf6519','#e69928','#ffc54b','#ffe78b'],
    }
    for name,cols in palettes.items():
        M[name] = toon_mat('Shop_'+name,cols)
    for name,col in [('Ink','#3a1418'),('Lamp','#ffd05a'),('Highlight','#fff6e8'),('Pupil','#3b1d14')]:
        M[name] = flat_mat('Shop_'+name,col)


def building():
    box('RearWall',(0,.94,1.44),(4.0,.14,2.88),'WoodDark','Back')
    for i in range(12):
        x = -1.83+i*.333
        box('RearPlank', (x,1.03,1.43),(.322,.065,2.8),'Wood' if i%3 else 'WoodLight','Back')
    for side in (-1,1):
        for j in range(7):
            box('SidePlank',(side*1.96,-.85+j*.28,1.43),(.14,.267,2.83),
                'Wood' if j%3 else 'WoodLight','Back')
        for y in (-1,1):
            box('CornerPost',(side*1.96,y,1.46),(.25,.25,2.92),'WoodLight',
                'Front' if y<0 else 'Back',.04)
        rod('FrontBrace',(side*1.84,-1.005,2.43),(side*1.36,-1.005,2.89),.075,'WoodLight')
        rod('SideBrace',(side*2.02,-.85,2.44),(side*2.02,-.3,2.91),.07,'WoodLight','Back')
    box('FrontBase',(0,-1.4,.065),(4.08,.21,.13),'WoodLight')
    box('FrontDarkGaps',(0,-1.4,.65),(3.95,.13,1.3),'WoodDark')
    for i in range(12):
        box('CounterPlank',(-1.81+i*.33,-1.49,.67),(.315,.14,1.23),'Wood' if i%3 else 'WoodLight')
    box('CounterTop',(0,-1.38,1.35),(4.28,1.1,.18),'WoodLight','Back',bevel=.045)
    box('CounterLip',(0,-1.93,1.35),(4.28,.05,.18),'WoodLight',bevel=.025)
    box('FrontHeader',(0,-1,2.91),(4.18,.24,.2),'WoodLight',bevel=.035)
    box('RearDoor',(.2,1.085,1.03),(1.19,.07,2.02),'WoodDark','Back')
    for i in range(5):
        box('DoorSlat',(-.26+i*.23,1.13,1.03),(.215,.03,1.91),'Wood','Back')
    for x in (-.47,.87):
        box('DoorFrame',(x,1.11,1.09),(.13,.12,2.15),'WoodLight','Back')
    box('DoorLintel',(.2,1.11,2.17),(1.47,.12,.13),'WoodLight','Back')
    ellipsoid('DoorHandle',(.63,1.21,1.0),(.07,.05,.07),'Metal','Back')
    box('BottleShelf',(0,-.12,1.49),(3.1,.32,.09),'WoodLight','Back')
    for x in (-1.25,1.25):
        box('ShelfBracket',(x,-.02,1.32),(.09,.11,.29),'WoodDark','Back')
    for x,col in [(-1.26,'Green'),(-.82,'Juice'),(.77,'Pink'),(1.22,'Teal')]:
        cylinder('Bottle',(x,-.12,1.76),.105,.44,col,'Back',top=.09,sides=12)
        cylinder('BottleNeck',(x,-.12,2.03),.045,.16,col,'Back',sides=10)
        cylinder('BottleCap',(x,-.12,2.12),.052,.04,'Cream','Back',sides=10)
    for x in (-1.18,-.73):
        cylinder('JuiceCup',(x,-1.4,1.57),.09,.29,'Cream',top=.12,sides=12)
        cylinder('JuiceFill',(x,-1.4,1.719),.10,.008,'Juice',sides=12)
        curve('PinkStraw',[(x,-1.4,1.68),(x+.035,-1.4,1.94),(x+.15,-1.4,1.98)],.017,'Pink')


def roof_point(side,u,t):
    w = .72 + 1.97*t
    d = .025 + 1.3*t
    z = 4.02 - 1.08*t
    if side == 0: return (u*w,-d,z)
    if side == 1: return (w,u*d,z)
    if side == 2: return (-u*w,d,z)
    return (-w,-u*d,z)


def roof():
    corners = [(-2.69,-1.325,2.91),(2.69,-1.325,2.91),(2.69,1.325,2.91),(-2.69,1.325,2.91)]
    mesh('RoofUnderlay',corners+[(-.72,0,4.02),(.72,0,4.02)],
         [(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4),(3,2,1,0)],'StrawDark')
    for side in range(4):
        count = 14 if side%2==0 else 9
        for row,(t0,t1) in enumerate([(0,.4),(.31,.73),(.64,1.05)]):
            for i in range(count):
                u0,u1 = -1+2*i/count,-1+2*(i+1)/count
                v = [roof_point(side,u,t) for u,t in
                     [(u0,t0),(u1,t0),(u1,t1-.065),((u0+u1)/2+.012,t1), (u0,t1-.06)]]
                v = [(x,y,z+.035*(3-row)+.012*math.sin(i*3.7)) for x,y,z in v]
                bottom = [(x,y,z-.045) for x,y,z in v]
                mesh('Thatch',v+bottom,[(0,1,2,3,4),(5,9,8,7,6)]+[(j,(j+1)%5,(j+1)%5+5,j+5) for j in range(5)],
                     ['Straw','StrawLight','Straw','StrawDark'][(i+row+side)%4])
    box('RidgeCap',(0,0,4.055),(1.63,.3,.17),'StrawLight',bevel=.08)
    # La balza è un oggetto anteriore: la sua profondità copre il negoziante.
    for i in range(7):
        x0 = -1.88+i*3.76/7
        x1 = x0+3.76/7
        mat = 'Red' if i%2==0 else 'Cream'
        mesh('AwningSlope',[(x0,-.98,2.87),(x1,-.98,2.87),(x1,-1.57,2.93),(x0,-1.57,2.93)],[(0,1,2,3)],mat)  # bordo alto sotto la paglia: il tetto lo copre con la sua frangia
        center = (x0+x1)/2
        verts = [(x0,-1.575,2.94),(x1,-1.575,2.94),(x1,-1.575,2.82)]
        verts += [(center+(x1-x0)/2*math.cos(a),-1.575,2.82-.14*math.sin(a))
                  for a in np.linspace(0,math.pi,10)]
        verts += [(x0,-1.575,2.82)]
        mesh('AwningScallop',verts,[tuple(range(len(verts)))],mat)


def props():
    # Tavola con bordo rosso e ibisco, ricavata dalla sagoma del concept.
    points = [(-.27,0),(-.4,.52),(-.37,1.35),(-.24,1.93),(0,2.3),(.24,1.93),(.37,1.35),(.4,.52),(.27,0)]
    board = mesh('Surfboard',[(x,-.045,z) for x,z in points]+[(x,.045,z) for x,z in points],
        [tuple(reversed(range(9))),tuple(range(9,18))]+[(i,(i+1)%9,(i+1)%9+9,i+9) for i in range(9)],'Red')
    pivot = bpy.data.objects.new('SurfPivot',None)
    bpy.data.collections['Front'].objects.link(pivot)
    pivot.parent = bpy.data.objects['ShopRoot']
    pivot.location = (-2.2,-.96,.02)
    pivot.rotation_euler = (math.radians(-6),math.radians(-12),math.radians(-4))
    board.parent=pivot
    inset = mesh('SurfboardCream',[(x*.82,-.05,.08+z*.92) for x,z in points],[tuple(reversed(range(9)))],'Cream')
    inset.parent = pivot
    for a in np.linspace(0,math.tau,6)[:-1]:
        petal = ellipsoid('HibiscusPetal',(.12*math.sin(a),-.075,1.2+.12*math.cos(a)),(.105,.018,.22),'Red')
        petal.parent=pivot
        petal.rotation_euler[1]=a
    center = ellipsoid('HibiscusCenter',(0,-.1,1.2),(.065,.025,.065),'Red')
    center.parent=pivot
    for z in (.35,1.8):
        mark=mesh('SurfChevron',[(-.27,-.07,z+.1),(0,-.07,z),(.27,-.07,z+.1),(0,-.07,z+.22)],[(0,1,2,3)],'Red')
        mark.parent=pivot
    x,y=-2.33,-1.52
    rings=[(0,.35),(.1,.39),(.5,.44),(.92,.39),(1.0,.35)]
    vertices=[(x+r*math.cos(i*math.tau/16),y+r*math.sin(i*math.tau/16),z) for z,r in rings for i in range(16)]
    barrel=mesh('Barrel',vertices,[(j*16+i,j*16+(i+1)%16,(j+1)*16+(i+1)%16,(j+1)*16+i)
        for j in range(4) for i in range(16)]+[tuple(range(64,80))],'Wood')
    barrel.data.materials.append(M['WoodLight'])
    for p in barrel.data.polygons:
        p.material_index = int(p.index%3==0)
    for z,r in [(.17,.407),(.79,.418)]:
        cylinder('BarrelBand',(x,y,z),r,.085,'Metal',sides=16)
    cylinder('BarrelRim',(x,y,.998),.37,.07,'WoodLight',sides=16)
    cylinder('BarrelInside',(x,y,1.037),.295,.008,'WoodDark',sides=16)
    curve('Rope',[(x+.05,y+.15,1.06),(x+.28,y+.1,1.08),(x+.4,y-.2,1.0),
        (x+.46,y-.33,.67),(x+.35,y-.4,.52),(x+.2,y-.4,.64),(x+.18,y-.32,.95),
        (x+.02,y-.16,1.06)],.035,'Cream')
    # Lanterna sul montante sinistro, davanti alla tavola.
    rod('LanternHook',(-1.96,-1,2.85),(-1.64,-1.16,2.85),.035,'WoodDark')
    rod('LanternCord',(-1.64,-1.16,2.85),(-1.64,-1.16,2.56),.018,'Ink')
    ellipsoid('Lantern',(-1.64,-1.16,2.36),(.23,.23,.25),'Lamp')
    for z in (2.13,2.28,2.44,2.59):
        cylinder('LanternRing',(-1.64,-1.16,z),.235 if z in (2.28,2.44) else .11,.025,'Wood',sides=16)
    for a in np.linspace(0,math.tau,7)[:-1]:
        curve('LanternRib',[(-1.64+r*math.cos(a),-1.16+r*math.sin(a),z)
              for r,z in [(.1,2.13),(.22,2.23),(.24,2.36),(.22,2.49),(.1,2.59)]],.013,'Wood')


def bind(obj,bone):
    rig=bpy.data.objects['ShopRig']
    bpy.context.view_layer.update()
    mw=obj.matrix_world.copy()
    obj.parent, obj.parent_type, obj.parent_bone=rig,'BONE',bone
    obj.matrix_world=mw
    return obj


def merchant():
    with bpy.data.libraries.load(os.path.join(HERE,'base_personaggio.blend'),link=False) as (src,dst):
        dst.objects=['Rig']
    rig=dst.objects[0]
    rig.name='ShopRig'
    bpy.data.collections['Merchant'].objects.link(rig)
    rig.animation_data_clear()
    rig.parent=bpy.data.objects['ShopRoot']
    for pb in rig.pose.bones:
        pb.matrix_basis=Matrix.Identity(4)
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    rig.select_set(True)
    bpy.context.view_layer.objects.active=rig
    with bpy.context.temp_override(object=rig,active_object=rig,selected_objects=[rig],selected_editable_objects=[rig]):
        bpy.ops.object.mode_set(mode='EDIT')
        for b in rig.data.edit_bones:
            b.use_connect=False
        for name,a,b in [('hips',(0,-.71,.8),(0,-.71,1.0)),
            ('spine',(0,-.71,1.0),(0,-.71,1.3)),('chest',(0,-.71,1.3),(0,-.71,1.56)),
            ('head',(0,-.71,1.56),(0,-.71,2.08))]:
            rig.data.edit_bones[name].head=a
            rig.data.edit_bones[name].tail=b
        for side,s in [('L',1),('R',-1)]:
            shoulder=(s*.29,-.72,1.53)
            elbow=(s*.49,-1.01,1.43)
            wrist=(s*.14,-1.27,1.44)
            for n,a,b in [('upper_arm',shoulder,elbow),('forearm',elbow,wrist),
                         ('hand',wrist,(s*.06,-1.33,1.44))]:
                rig.data.edit_bones[n+'.'+side].head=a
                rig.data.edit_bones[n+'.'+side].tail=b
        bpy.ops.object.mode_set(mode='OBJECT')
    bind(ellipsoid('ShopShirt',(0,-.7,1.27),(.37,.23,.4),'Shirt','Merchant'),'chest')
    bind(ellipsoid('TankTop',(0,-.927,1.3),(.16,.025,.29),'Cream','Merchant'),'chest')
    for s in (-1,1):
        collar=mesh('Collar',[(s*.08,-.963,1.54),(s*.25,-.94,1.51),(s*.17,-.965,1.34)],[(0,1,2)],'Cream','Merchant')
        bind(collar,'chest')
        for x,z in [(s*.26,1.43),(s*.23,1.18)]:
            petal=ellipsoid('ShirtLeaf',(x,-.94,z),(.045,.015,.09),'Cream','Merchant')
            petal.rotation_euler[1]=s*.6
            bind(petal,'chest')
    bind(cylinder('Neck',(0,-.71,1.6),.105,.19,'SkinShop','Merchant'),'head')
    bind(ellipsoid('ShopHead',(0,-.73,1.82),(.235,.205,.285),'SkinShop','Merchant'),'head')
    bind(ellipsoid('ShopChin',(0,-.79,1.67),(.15,.14,.11),'SkinShop','Merchant'),'head')
    bind(ellipsoid('Nose',(0,-.943,1.81),(.073,.10,.085),'SkinShop','Merchant'),'head')
    for s in (-1,1):
        bind(ellipsoid('Ear',(s*.235,-.73,1.81),(.055,.06,.09),'SkinShop','Merchant'),'head')
        for j in range(3):
            bind(ellipsoid('SideHair',(s*(.20+.015*(j%2)),-.65+j*.014,1.88-j*.075),
                (.07,.095,.1),'HairShop','Merchant'),'head')
        eye=ellipsoid('ShopEye'+str(s),(s*.092,-.923,1.87),(.033,.018,.038),'Pupil','Merchant')
        bind(eye,'head')
        bind(ellipsoid('EyeGlint'+str(s),(s*.092+.008,-.939,1.881),(.009,.006,.012),'Highlight','Merchant'),'head')
        bind(curve('Brow',[(s*.06,-.934,1.928),(s*.13,-.918,1.92)],.014,'HairShop','Merchant'),'head')
        bind(curve('CheekCrease',[(s*.13,-.92,1.82),(s*.15,-.89,1.78)],.009,'WoodDark','Merchant'),'head')
    bind(curve('ShopSmile',[(-.065,-.935,1.725),(0,-.95,1.71),(.075,-.929,1.735)],.009,'WoodDark','Merchant'),'head')
    bind(ellipsoid('HatBrim',(0,-.71,2.065),(.36,.30,.042),'StrawLight','Merchant'),'head')
    bind(cylinder('HatCrown',(0,-.7,2.15),.22,.19,'Straw','Merchant',top=.18,sides=20),'head')
    bind(cylinder('HatBand',(0,-.7,2.085),.223,.055,'Teal','Merchant',sides=20),'head')
    for side in ('L','R'):
        for part,mat,r in [('upper_arm','Shirt',.115),('forearm','SkinShop',.078)]:
            b=rig.data.bones[part+'.'+side]
            o=rod('Shop_'+part+'.'+side,b.head_local,b.tail_local,r,mat,'Merchant',top=r*.9)
            bind(o,part+'.'+side)
        b=rig.data.bones['hand.'+side]
        bind(ellipsoid('ShopHand.'+side,b.head_local,(.085,.095,.047),'SkinShop','Merchant'),'hand.'+side)
    glass=cylinder('CleaningGlass',(.12,-1.15,1.62),.08,.25,'Teal','Merchant',top=.105,sides=12)
    bind(glass,'hand.L')
    cloth=box('Cloth',(0,-1.34,1.455),(.21,.16,.026),'Cream','Merchant',.02)
    bind(cloth,'hand.R')
    for n in ('CleaningGlass','Cloth'):
        bpy.data.objects[n].hide_render=True
    for name,b in rig.pose.bones.items():
        b.rotation_mode='XYZ'
    rig['rest_matrices']=json.dumps({n:[list(row) for row in b.matrix] for n,b in rig.pose.bones.items()})


def pose(action='idle',frame=0):
    rig=bpy.data.objects['ShopRig']
    for pb in rig.pose.bones:
        pb.matrix_basis=Matrix.Identity(4)
    n=next(a[1] for a in ANIMS if a[0]==action)
    t=frame/n*math.tau
    rig.pose.bones['chest'].rotation_euler[0]=.009*math.sin(t)
    rig.pose.bones['head'].rotation_euler[1]=.018*math.sin(t)
    for name in ('CleaningGlass','Cloth'):
        bpy.data.objects[name].hide_render=True
    blink = action=='idle' and frame==6
    for o in bpy.data.collections['Merchant'].objects:
        if o.name.startswith('ShopEye'):
            o.scale.z=.006 if blink else .038
        if o.name.startswith('EyeGlint'):
            o.hide_render=blink
    if action!='idle':
        # Le pose partono e finiscono sull'appoggio; nessuno scatto tra gesto e idle.
        k=math.sin(math.pi*frame/(n-1))**2
        if action=='clean_glass':
            rig.pose.bones['upper_arm.L'].rotation_euler[0]=-.32*k
            rig.pose.bones['forearm.L'].rotation_euler[0]=-.55*k
            rig.pose.bones['forearm.R'].rotation_euler[0]=-.42*k
            rig.pose.bones['forearm.R'].rotation_euler[1]=.24*k*math.sin(t*3)
            rig.pose.bones['hand.R'].rotation_euler[1]=.35*k*math.sin(t*3)
            bpy.data.objects['CleaningGlass'].hide_render=k<.12
            bpy.data.objects['Cloth'].hide_render=k<.12
            rig.pose.bones['head'].rotation_euler[0]=.07*k
        else:
            rig.pose.bones['upper_arm.R'].rotation_euler[1]=.28*k*math.sin(t*2)
            rig.pose.bones['forearm.R'].rotation_euler[1]=.5*k*math.sin(t*2)
            rig.pose.bones['hand.R'].rotation_euler[1]=.2*k*math.sin(t*2)
            bpy.data.objects['Cloth'].hide_render=k<.08
            rig.pose.bones['head'].rotation_euler[1]=.12*k*math.sin(t*2)
    bpy.context.view_layer.update()


def setup():
    expected=os.path.normcase(os.path.join(HERE,'shop.blend'))
    current=os.path.normcase(bpy.data.filepath)
    if current!=expected and (current or bpy.data.is_dirty):
        raise RuntimeError('Aprire shop.blend o un file iniziale pulito prima di costruire il negozio')
    if len(bpy.data.scenes)!=1:
        raise RuntimeError('La ricostruzione richiede una sola scena dedicata al negozio')
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o,do_unlink=True)
    for name in ('Back','Front','Merchant','Shadow','References'):
        col=bpy.data.collections.get(name) or bpy.data.collections.new(name)
        if name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(col)
    root=bpy.data.objects.new('ShopRoot',None)
    bpy.context.scene.collection.objects.link(root)
    with bpy.data.libraries.load(os.path.join(HERE,'base_personaggio.blend'),link=False) as (src,dst):
        dst.materials=['Skin']
        dst.objects=['Key']
    for o in dst.objects:
        bpy.context.scene.collection.objects.link(o)
    # toon_mat usa il template Skin già caricato, senza cambiare i materiali dei personaggi.
    materials()
    building();roof();props();merchant()
    ellipsoid('GroundShadow',(0,-.4,.005),(2.93,1.95,.003),'Ink','Shadow',segments=32)
    root.rotation_euler[2]=YAW
    camera=bpy.data.cameras.new('ShopCamera')
    obj=bpy.data.objects.new('ShopCamera',camera)
    bpy.context.scene.collection.objects.link(obj)
    camera.type='ORTHO';camera.ortho_scale=ORTHO
    COMMON['place_cam'](obj,25,TARGET_Z)
    scene=bpy.context.scene
    scene.camera=obj
    scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_x=scene.render.resolution_y=SIZE
    scene.render.resolution_percentage=100
    scene.render.film_transparent=True
    scene.render.filter_size=0
    scene.eevee.taa_render_samples=1
    scene.view_settings.view_transform='Standard'
    scene.view_settings.look='None'
    scene.world.color=(.18,.18,.18)
    # Viste del concept nelle coordinate del modello; solo riferimento, mai renderizzate.
    source=grab(CONCEPT)
    refdir=os.path.join(HERE,'ref')
    os.makedirs(refdir,exist_ok=True)
    for name,crop,loc,rot in [('Ref_ShopFront',(130,8,650,458),(0,1.4,2),(math.pi/2,0,0)),
        ('Ref_ShopSide',(890,8,1380,450),(-3,0,2),(math.pi/2,0,math.pi/2)),
        ('Ref_ShopBack',(140,518,655,965),(0,-1.4,2),(math.pi/2,0,math.pi))]:
        x0,y0,x1,y1=crop
        path=os.path.join(refdir,name.lower()+'.png')
        save_rgba(source[y0:y1,x0:x1],path)
        image=bpy.data.images.load(path,check_existing=True)
        ref=bpy.data.objects.new(name,None)
        ref.empty_display_type='IMAGE';ref.data=image
        ref.empty_display_size=5.8
        ref.location=loc;ref.rotation_euler=rot;ref.hide_render=True
        bpy.data.collections['References'].objects.link(ref)
        ref.hide_viewport=True
    bpy.context.view_layer.update()
    pose()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE,'shop.blend'))
    return {'objects':len(bpy.data.objects),'file':bpy.data.filepath}


def show_groups(groups):
    for name in ('Back','Front','Merchant','Shadow'):
        bpy.data.collections[name].hide_render=name not in groups


def render_raw(size=SIZE):
    s=bpy.context.scene
    s.render.resolution_x=s.render.resolution_y=size
    s.render.filepath=os.path.join(TMP,'beatch_shop_render.png')
    bpy.ops.render.render(write_still=True)
    return grab(s.render.filepath)


def render_pixel():
    a=render_raw()
    scene=bpy.context.scene
    settings=bpy.context.view_layer.freestyle_settings
    lines=settings.linesets.get('ShopEdges') or settings.linesets.new('ShopEdges')
    enabled={'select_silhouette','select_border','select_crease','select_by_visibility','select_by_edge_types','select_by_face_marks'}
    for prop in lines.bl_rna.properties:
        if prop.type=='BOOLEAN' and prop.identifier.startswith(('select_','exclude_')):
            setattr(lines,prop.identifier,prop.identifier in enabled)
    lines.visibility='VISIBLE'
    lines.face_mark_condition='BOTH'
    lines.face_mark_negation='INCLUSIVE'
    for o in bpy.context.scene.objects:
        if o.type!='MESH':
            continue
        marks=o.data.attributes.get('freestyle_face') or o.data.attributes.new(name='freestyle_face',type='BOOLEAN',domain='FACE')
        marked=not o.name.startswith(('Thatch','RoofUnderlay','Hat','ShopHead','ShopEye','EyeGlint','Nose','Ear','SideHair'))
        marks.data.foreach_set('value',[marked]*len(o.data.polygons))
    lines.linestyle.color=(0,1,0)
    lines.linestyle.thickness=.8
    lines.linestyle.thickness_position='CENTER'
    for line in settings.linesets:
        line.show_render=line==lines
    settings.mode='EDITOR'
    settings.as_render_pass=False
    bpy.context.view_layer.use_freestyle=True
    scene.render.use_freestyle=True
    try:
        line_image=render_raw()
    finally:
        scene.render.use_freestyle=False
    r,g,b=line_image[...,:3].transpose(2,0,1)
    ink=(g>.65)&(g>r+.3)&(g>b+.3)
    op=a[...,3]>.5
    inside=np.zeros_like(op)
    inside[1:-1,1:-1]=op[1:-1,1:-1]&op[:-2,1:-1]&op[2:,1:-1]&op[1:-1,:-2]&op[1:-1,2:]
    a[ink&inside,:3]=COMMON['OUTLINE']
    if not bpy.data.collections['Merchant'].hide_render:
        for s in (-1,1):
            eye=bpy.data.objects['ShopEye'+str(s)]
            p=world_to_camera_view(scene,scene.camera,eye.matrix_world.translation)
            x,y=round(p.x*SIZE)-1,round((1-p.y)*SIZE)-1
            for dy,row in enumerate(['DD'] if eye.scale.z<.01 else ['DH','DD']):
                for dx,c in enumerate(row):
                    if 0<=x+dx<SIZE and 0<=y+dy<SIZE and op[y+dy,x+dx]:
                        a[y+dy,x+dx,:3]=COMMON['hx8']('#fff6e8' if c=='H' else '#3b1d14')
    return outline(a)


def outline(a):
    rgb=a[...,:3].copy();mask=a[...,3]>.5
    rgb[~mask]=0
    neighbors=np.zeros_like(mask)
    neighbors[1:] |= mask[:-1];neighbors[:-1] |= mask[1:]
    neighbors[:,1:] |= mask[:,:-1];neighbors[:,:-1] |= mask[:,1:]
    edge=neighbors & ~mask
    out=np.zeros_like(a)
    out[mask,:3]=rgb[mask];out[mask,3]=1
    out[edge,:3]=COMMON['OUTLINE'];out[edge,3]=1
    return out


def composite(images):
    out=np.zeros_like(images[0])
    for a in images:
        alpha=a[...,3:4]
        out[...,:3]=a[...,:3]*alpha+out[...,:3]*(1-alpha)
        out[...,3:4]=alpha+out[...,3:4]*(1-alpha)
    return out


def preview():
    os.makedirs(OUT,exist_ok=True)
    pose()
    show_groups(('Back','Front','Merchant'))
    bpy.context.scene.eevee.taa_render_samples=32
    model=render_raw(640)
    bpy.context.scene.eevee.taa_render_samples=1
    save_rgba(model,os.path.join(TMP,'shop_model_preview.png'))
    pixel=render_pixel()
    save_rgba(np.repeat(np.repeat(pixel,4,0),4,1),os.path.join(TMP,'shop_sprite_preview.png'))
    return {'model':os.path.join(TMP,'shop_model_preview.png'),'sprite':os.path.join(TMP,'shop_sprite_preview.png')}


def project_point(co):
    root=bpy.data.objects['ShopRoot']
    v=world_to_camera_view(bpy.context.scene,bpy.context.scene.camera,root.matrix_world@Vector(co))
    return [round(v.x*SIZE,3),round((1-v.y)*SIZE,3)]


def build_steps():
    os.makedirs(OUT,exist_ok=True)
    pose()
    for group,name in [('Shadow','shop_shadow.png'),('Back','shop_back.png'),('Front','shop_front.png')]:
        show_groups((group,))
        if group=='Shadow':
            a=render_raw();op=a[...,3]>.5
            a[...,:3]=COMMON['OUTLINE'];a[...,3]=op*(97/255)
        else:
            a=render_pixel()
        save_rgba(a,os.path.join(OUT,name))
        yield name
    sheet=np.zeros((SIZE*len(ANIMS),SIZE*max(a[1] for a in ANIMS),4),dtype=np.float32)
    show_groups(('Merchant',))
    for row,(name,count,fps,loop) in enumerate(ANIMS):
        for frame in range(count):
            pose(name,frame)
            sheet[row*SIZE:(row+1)*SIZE,frame*SIZE:(frame+1)*SIZE]=render_pixel()
            yield name,frame
    save_rgba(sheet,os.path.join(OUT,'shopkeeper.png'))
    frames_path=os.path.join(OUT,'shopkeeper_frames.tres')
    previous=open(frames_path,encoding='utf-8').read() if os.path.exists(frames_path) else ''
    uid=re.search(r'uid="([^"]+)"',previous.split('\n',1)[0])
    lines=['[gd_resource type="SpriteFrames" format=3'+(' uid="'+uid[1]+'"' if uid else '')+']','',
        '[ext_resource type="Texture2D" path="res://Assets/Objects/Shop/shopkeeper.png" id="1"]','']
    anims=[]
    for row,(name,count,fps,loop) in enumerate(ANIMS):
        frames=[]
        for frame in range(count):
            id=f'{name}_{frame}'
            lines += [f'[sub_resource type="AtlasTexture" id="{id}"]','atlas = ExtResource("1")',
                f'region = Rect2({frame*SIZE}, {row*SIZE}, {SIZE}, {SIZE})','filter_clip = true','']
            frames.append('{"duration": 1.0, "texture": SubResource("'+id+'")}')
        anims.append('{"frames": ['+', '.join(frames)+'], "loop": '+str(loop).lower()+
                     ', "name": &"'+name+'", "speed": '+str(float(fps))+'}')
    lines+=['[resource]','animations = ['+',\n'.join(anims)+']','']
    open(frames_path,'w',encoding='utf-8').write('\n'.join(lines))
    anchor=project_point((0,-1.18,0))
    ground=[project_point(p) for p in [(-2.1,-1.9,0),(2.1,-1.9,0),(2.1,1.1,0),(-2.1,1.1,0)]]
    interact=[project_point(p) for p in [(-1.5,-1.9,0),(1.5,-1.9,0),(1.5,-3.75,0),(-1.5,-3.75,0)]]
    meta={'cell':SIZE,'scale':4,'sprite_position':[(SIZE/2-anchor[0])*4,(SIZE/2-anchor[1])*4],
          'body_polygon':[[(p[i]-anchor[i])*4 for i in (0,1)] for p in ground],
          'interaction_polygon':[[(p[i]-anchor[i])*4 for i in (0,1)] for p in interact],
          'props':[{'name':'barrel','point':project_point((-2.33,-1.52,0)),'radius':.42}],
          'anchor':anchor,'animations':ANIMS}
    open(os.path.join(HERE,'shop_layout.json'),'w',encoding='utf-8').write(json.dumps(meta,indent=2))
    pose();show_groups(('Back','Front','Merchant'))
    bpy.ops.wm.save_mainfile()
    yield 'saved'


def check():
    a=grab(os.path.join(OUT,'shopkeeper.png'))
    assert a.shape==(SIZE*3,SIZE*16,4),a.shape
    back=grab(os.path.join(OUT,'shop_back.png'))
    front=grab(os.path.join(OUT,'shop_front.png'))
    for row,(name,count,_,_) in enumerate(ANIMS):
        frames=[]
        for i in range(count):
            cell=a[row*SIZE:(row+1)*SIZE,i*SIZE:(i+1)*SIZE]
            alpha=cell[...,3]
            assert np.isin(np.round(alpha*255),[0,255]).all(),name
            assert alpha.sum()>30,(name,i)
            assert not alpha[[0,-1],:].any() and not alpha[:,[0,-1]].any(),(name,i)
            frames.append(cell)
        assert any(not np.array_equal(frames[0],f) for f in frames[1:]),name
        visible=[composite([back,f,front]) for f in frames]
        assert max(np.any(abs(f-visible[0])>.02,axis=2).sum() for f in visible)>5, name+' nascosta dal bancone/tetto'
    for file in ('shop_front.png','shop_back.png'):
        a=grab(os.path.join(OUT,file));assert a.shape==(SIZE,SIZE,4)
        assert not a[[0,-1],:,3].any() and not a[:,[0,-1],3].any(),file
    return {'animations':len(ANIMS),'frames':sum(a[1] for a in ANIMS),'cell':SIZE,'checks':'passed'}
