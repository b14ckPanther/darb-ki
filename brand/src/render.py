# Renders the Darb Ki masters in Blender Cycles from src/tokens.json. Nothing is drawn by hand.
#   blender -b -P src/render.py -- <tile|hero> <out.png> <width> <height> <samples>
#   tile  the watchtower globe on a transparent background (icons are composed from it)
#   hero  the honeycomb lure, subject on the right, room for copy on the left
# The globe uses the same tokens.globe numbers as src/globe.mjs, which draws the flat marks.
import bpy, sys, math, json, random
from pathlib import Path
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
D, OUT, W, H, SAMPLES = argv[0], argv[1], int(argv[2]), int(argv[3]), int(argv[4])
SIZE = W
ROOT = Path(__file__).resolve().parents[1]
T = json.loads((ROOT / 'src' / 'tokens.json').read_text())
G = T['globe']
rng = random.Random(T['render']['seed'])


def lin(hexstr, k=1.0):
    """sRGB hex to linear RGBA, optionally scaled."""
    h = hexstr.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (c[0] * k, c[1] * k, c[2] * k, 1.0)


COL = {k: v['hex'] for k, v in T['color'].items()}

# ---------- scene, renderer, colour ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
prefs = bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    scene.cycles.device = 'GPU'
except Exception as e:
    print('GPU unavailable, using CPU:', e)
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.cycles.volume_step_rate = 1.0
scene.cycles.max_bounces = 12
scene.render.resolution_x, scene.render.resolution_y = W, H
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = OUT
scene.view_settings.view_transform = 'AgX'
for look in ('AgX - Medium High Contrast', 'AgX - Punchy', 'AgX - Base Contrast'):
    try:
        scene.view_settings.look = look
        break
    except TypeError:
        pass
coll = scene.collection


def link(obj):
    coll.objects.link(obj)
    return obj


def node_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    return m, nt, out


def metal(name, hexstr, rough=0.22, aniso=0.0):
    m, nt, out = node_mat(name)
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = lin(hexstr)
    b.inputs['Metallic'].default_value = 1.0
    b.inputs['Roughness'].default_value = rough
    if aniso:
        b.inputs['Anisotropic'].default_value = aniso
    nt.links.new(b.outputs[0], out.inputs['Surface'])
    return m


def glossy(name, hexstr, rough=0.3, coat=1.0):
    m, nt, out = node_mat(name)
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = lin(hexstr)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Coat Roughness'].default_value = 0.06
    nt.links.new(b.outputs[0], out.inputs['Surface'])
    return m


def emissive(name, hexstr, strength):
    m, nt, out = node_mat(name)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = lin(hexstr)
    e.inputs['Strength'].default_value = strength
    nt.links.new(e.outputs[0], out.inputs['Surface'])
    return m


def to_mesh(obj):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    return bpy.context.view_layer.objects.active


def nimbus_hull(name, length=3.0, h=0.7, loc=(0, 0, 0), rot=0.0, res=0.035):
    """The cloud's envelope from metaballs: round, high crown at the front, thinning to a tail behind.
    The volume material erodes it into vapour; displacement breaks the silhouette."""
    mb = bpy.data.metaballs.new(name)
    mb.resolution = res
    mb.threshold = 0.6
    ob = link(bpy.data.objects.new(name, mb))
    n = 14
    for i in range(n):
        t = i / (n - 1)
        r = h * (0.16 + 0.84 * math.sin(math.pi * (0.06 + 0.6 * t)))
        e = mb.elements.new(); e.co = (-length / 2 + length * t, 0, r * 0.35); e.radius = r * 1.25
    for t, k in ((0.5, 0.9), (0.72, 1.15), (0.9, 0.85)):
        e = mb.elements.new(); e.co = (-length / 2 + length * t, rng.uniform(-.1, .1), h * 0.62 + h * k * 0.4); e.radius = h * k * 1.2
    ob = to_mesh(ob)
    tex = bpy.data.textures.new(name + '-clouds', 'CLOUDS'); tex.noise_scale = 0.35; tex.noise_depth = 4
    d = ob.modifiers.new('break', 'DISPLACE'); d.texture = tex; d.strength = 0.22; d.mid_level = 0.5
    ob.location = loc
    ob.rotation_euler = (0, rot, 0)  # Z is up, the camera looks along +Y, so Y rotation tilts it in the picture
    bpy.context.view_layer.update()
    return ob


def vapour(hull, name, density=6.0, glow=0.5, push=0.22, voxel=0.025, scale=1.6, detail=2.4):
    """Turns a hull mesh into a real cloud: mesh-to-volume, then displaced by a cloud texture so the edges
    tear into wisps; the shader multiplies the voxel density by fine noise for billowing detail."""
    vol = link(bpy.data.objects.new(name, bpy.data.volumes.new(name)))
    m2v = vol.modifiers.new('fill', 'MESH_TO_VOLUME'); m2v.object = hull
    m2v.resolution_mode = 'VOXEL_SIZE'; m2v.voxel_size = voxel; m2v.interior_band_width = 0.2; m2v.density = 1.0
    tex = bpy.data.textures.new(name + '-billow', 'CLOUDS'); tex.noise_scale = 0.45; tex.noise_depth = 5
    dsp = vol.modifiers.new('tear', 'VOLUME_DISPLACE'); dsp.texture = tex; dsp.strength = push; dsp.texture_mid_level = (0.5, 0.5, 0.5)
    hull.hide_render = True
    m, nt, out = node_mat(name + '-m')
    at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_name = 'density'
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = scale * detail; nz.inputs['Detail'].default_value = 14; nz.inputs['Roughness'].default_value = 0.6
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeMapRange'); ramp.inputs['From Min'].default_value = 0.38; ramp.inputs['From Max'].default_value = 0.66
    nt.links.new(nz.outputs['Fac'], ramp.inputs['Value'])
    a = nt.nodes.new('ShaderNodeMath'); a.operation = 'MULTIPLY'; nt.links.new(at.outputs['Fac'], a.inputs[0]); nt.links.new(ramp.outputs[0], a.inputs[1])
    b = nt.nodes.new('ShaderNodeMath'); b.operation = 'MULTIPLY'; b.inputs[1].default_value = density; nt.links.new(a.outputs[0], b.inputs[0])
    v = nt.nodes.new('ShaderNodeVolumePrincipled')
    v.inputs['Color'].default_value = lin('#F2C46A')
    v.inputs['Anisotropy'].default_value = 0.4
    v.inputs['Emission Color'].default_value = lin(COL['gold'])
    nt.links.new(b.outputs[0], v.inputs['Density'])
    e = nt.nodes.new('ShaderNodeMath'); e.operation = 'MULTIPLY'; e.inputs[1].default_value = glow; nt.links.new(a.outputs[0], e.inputs[0])
    nt.links.new(e.outputs[0], v.inputs['Emission Strength'])
    nt.links.new(v.outputs[0], out.inputs['Volume'])
    vol.data.materials.append(m)
    return vol


def tube_mesh(name, pts, radii, bevel):
    """A tapered tube as a mesh, used as a hull for vapour trails."""
    ob = tube(name, pts, radii, emissive(name + '-x', '#000000', 0), bevel=bevel, res=8)
    ob = to_mesh(ob)
    return ob


def tube(name, pts, radii, mat, bevel=1.0, res=6):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = bevel; cu.bevel_resolution = res; cu.use_fill_caps = True
    sp = cu.splines.new('NURBS'); sp.points.add(len(pts) - 1)
    for p, co, r in zip(sp.points, pts, radii):
        p.co = (*co, 1.0); p.radius = r
    sp.use_endpoint_u = True; sp.order_u = 4
    ob = link(bpy.data.objects.new(name, cu)); ob.data.materials.append(mat)
    return ob


def world(stars=True):
    w = bpy.data.worlds.new('night'); scene.world = w; w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputWorld')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = lin(COL['forest'], 0.5); ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[1].color = lin(COL['night'], 0.6); ramp.color_ramp.elements[1].position = 0.75
    nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = 0.6
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    if stars:
        vor = nt.nodes.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 260
        nt.links.new(tc.outputs['Generated'], vor.inputs['Vector'])
        st = nt.nodes.new('ShaderNodeMath'); st.operation = 'LESS_THAN'; st.inputs[1].default_value = 0.018
        nt.links.new(vor.outputs['Distance'], st.inputs[0])
        sb = nt.nodes.new('ShaderNodeBackground'); sb.inputs['Color'].default_value = (1, .95, .85, 1); sb.inputs['Strength'].default_value = 1.4
        add = nt.nodes.new('ShaderNodeMixShader')
        nt.links.new(st.outputs[0], add.inputs['Fac']); nt.links.new(bg.outputs[0], add.inputs[1]); nt.links.new(sb.outputs[0], add.inputs[2])
        nt.links.new(add.outputs[0], out.inputs['Surface'])
    else:
        nt.links.new(bg.outputs[0], out.inputs['Surface'])


def area(name, loc, target, power, hexstr, size=3.0, shape='DISK'):
    li = bpy.data.lights.new(name, 'AREA'); li.energy = power; li.color = lin(hexstr)[:3]; li.size = size; li.shape = shape
    ob = link(bpy.data.objects.new(name, li)); ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


def point(name, loc, power, hexstr, radius=0.2):
    li = bpy.data.lights.new(name, 'POINT'); li.energy = power; li.color = lin(hexstr)[:3]; li.shadow_soft_size = radius
    ob = link(bpy.data.objects.new(name, li)); ob.location = loc
    return ob


def camera(loc, target, lens=60):
    cam = bpy.data.cameras.new('cam'); cam.lens = lens
    ob = link(bpy.data.objects.new('cam', cam)); ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = ob


def poly_curve(name, polys, extrude, bevel, mat, res=8):
    """Flat outlines (outer + nested holes) extruded and bevelled like cast metal."""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
    cu.extrude = extrude; cu.bevel_depth = bevel; cu.bevel_resolution = res
    for poly in polys:
        sp = cu.splines.new('POLY'); sp.points.add(len(poly) - 1)
        for p, (x, y) in zip(sp.points, poly):
            p.co = (x, y, 0, 1)
        sp.use_cyclic_u = True
    ob = link(bpy.data.objects.new(name, cu)); ob.data.materials.append(mat)
    return ob


def medallion(r=2.25):
    bpy.ops.mesh.primitive_cylinder_add(vertices=256, radius=r, depth=0.2, location=(0, 0, 0))
    disc = bpy.context.active_object
    bv = disc.modifiers.new('b', 'BEVEL'); bv.width = 0.05; bv.segments = 6
    bpy.ops.object.shade_smooth()
    disc.data.materials.append(glossy('lacquer', '#04140C', 0.32, 1.0))
    bpy.ops.mesh.primitive_torus_add(major_radius=r - 0.19, minor_radius=0.05, major_segments=256, minor_segments=24, location=(0, 0, 0.1))
    bpy.ops.object.shade_smooth()
    bpy.context.active_object.data.materials.append(metal('gold', COL['gold'], 0.16))



def sph(lat, lon, r):
    la, lo = math.radians(lat), math.radians(lon)
    return Vector((r * math.cos(la) * math.sin(lo), -r * math.cos(la) * math.cos(lo), r * math.sin(la)))


def arc_pts(a, b, r, lift, n=48):
    """A great-circle arc from a to b over a sphere of radius r, lifted in the middle like a thrown thread."""
    out = []
    for i in range(n + 1):
        t = i / n
        p = a.normalized().slerp(b.normalized(), t) if hasattr(Vector, 'slerp') else (a.normalized() * (1 - t) + b.normalized() * t).normalized()
        out.append(tuple(p.normalized() * (r * (1 + lift * math.sin(math.pi * t)))))
    return out


def thread(name, pts, hexstr, strength, width):
    """A thread of hostile ki: thin at its origin, full where it lands."""
    n = len(pts)
    return tube(name, pts, [0.15 + 0.85 * (i / (n - 1)) ** 1.2 for i in range(n)], emissive(name, hexstr, strength), bevel=width, res=4)


if D == 'tile':
    # A "The Watchtower": the night globe, your one gold beacon on it, and hostile threads arriving
    # from every side of the world. You don't go looking; they come to you, and you feel each one land.
    world(stars=False)
    scene.render.film_transparent = True
    scene.render.image_settings.color_mode = 'RGBA'
    R = G['radius']
    bpy.ops.mesh.primitive_uv_sphere_add(segments=160, ring_count=80, radius=R)
    g = bpy.context.active_object; bpy.ops.object.shade_smooth()
    g.data.materials.append(glossy('ocean', '#061A12', 0.42, 0.6))
    # engraved graticule: fine gold rings for latitude and longitude
    hair = metal('hair', COL['goldDeep'], 0.35)
    for lat in range(-90 + G['graticule'], 90, G['graticule']):
        bpy.ops.mesh.primitive_torus_add(major_radius=R * math.cos(math.radians(lat)) * 1.002, minor_radius=0.0035, major_segments=200, minor_segments=6, location=(0, 0, R * math.sin(math.radians(lat))))
        bpy.context.active_object.data.materials.append(hair)
    for lon in range(0, 180, G['graticule']):
        bpy.ops.mesh.primitive_torus_add(major_radius=R * 1.002, minor_radius=0.0035, major_segments=200, minor_segments=6, rotation=(math.radians(90), 0, math.radians(lon)))
        bpy.context.active_object.data.materials.append(hair)
    beacon = sph(*G['beacon'], R)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.07, depth=0.08, location=tuple(beacon * 1.01))
    b = bpy.context.active_object; b.rotation_euler = beacon.to_track_quat('Z', 'Y').to_euler(); b.data.materials.append(metal('gold', COL['gold'], 0.18))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=tuple(beacon * 1.05)); bpy.context.active_object.data.materials.append(emissive('flare', COL['goldLight'], 60))
    point('answer', tuple(beacon * 1.15), 60, COL['goldLight'], 0.1)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.2, minor_radius=0.006, location=tuple(beacon * 1.012), rotation=beacon.to_track_quat('Z', 'Y').to_euler())
    bpy.context.active_object.data.materials.append(emissive('ring', COL['goldLight'], 12))
    origins = G['threads']
    for i, (la, lo, c) in enumerate(origins):
        o = sph(la, lo, R)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.022, location=tuple(o * 1.004)); bpy.context.active_object.data.materials.append(emissive(f'o{i}', COL[c], 12))
        thread(f't{i}', arc_pts(o, beacon, R, G['lift'] + G['liftStep'] * (i % 3)), COL[c], 9 if c != 'bone' else 4, 0.009)
    area('key', (-5, -6, 5), (0, 0, 0), 900, COL['goldLight'], 4)
    area('rim', (4, 6, 2), (0, 0, 0), 1400, COL['sky'], 4)
    camera(tuple(G['camera']), tuple(G['target']), G['lens'])

elif D == 'hero':
    # B "The Lure": a honeycomb, because a honeypot is bait. One cell glows gold (your sensor looks like an
    # easy meal); hostile threads curl in from the dark and end inside it, caught and recorded.
    world()
    gold_m = metal('gold', COL['gold'], 0.2); dull = metal('dull', '#9A7130', 0.32)
    r, h = 0.62, 0.9
    cells = [(0, 0)] + [(math.cos(math.radians(30 + 60 * k)) * r * 1.78, math.sin(math.radians(30 + 60 * k)) * r * 1.78) for k in range(6)]
    for i, (x, y) in enumerate(cells):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=r, depth=h if i == 0 else h * 0.75, location=(x, y, 0 if i == 0 else -0.12))
        c = bpy.context.active_object
        sol = c.modifiers.new('wall', 'SOLIDIFY'); sol.thickness = 0.05
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='DESELECT'); bpy.ops.object.mode_set(mode='OBJECT')
        for f in c.data.polygons:
            f.select = f.normal.z > 0.9
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.delete(type='FACE'); bpy.ops.object.mode_set(mode='OBJECT')
        bv = c.modifiers.new('b', 'BEVEL'); bv.width = 0.012; bv.segments = 3
        c.data.materials.append(gold_m if i == 0 else dull)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=r * 0.95, depth=0.02, location=(0, 0, -0.3))
    bpy.context.active_object.data.materials.append(emissive('honey', COL['gold'], 6))
    point('inside', (0, 0, 0.0), 120, COL['goldLight'], 0.3)
    ends = []
    for i, (ang, lift, c) in enumerate([(95, 1.4, 'ember'), (25, 1.0, 'bone'), (130, 1.8, 'verdigris'), (-35, 1.6, 'ember')]):
        a = math.radians(ang)
        start = Vector((math.cos(a) * 2.9, math.sin(a) * 2.9, 0.9 + lift * 0.3))
        mid = Vector((math.cos(a + 0.9) * 1.3, math.sin(a + 0.9) * 1.3, 1.1 + lift * 0.35))
        end = Vector((math.cos(a) * 0.2, math.sin(a) * 0.2, -0.2))
        pts = [tuple(start.lerp(mid, t) * (1 - t) + mid.lerp(end, t) * t) for t in (k / 40 for k in range(41))]
        thread(f't{i}', pts, COL[c], 10 if c != 'bone' else 5, 0.013)
    area('key', (-3, -4, 6), (0, 0, 0), 1300, COL['goldLight'], 3)
    area('rim', (4, 4, 3), (0, 0, 0), 900, COL['sky'], 3)
    camera((0.0, -4.6, 5.0), (0, 0.1, -0.05), 30)
    scene.camera.data.sensor_fit = 'VERTICAL'
    scene.camera.data.shift_x = -0.28  # subject to the right, copy goes on the left


bpy.ops.render.render(write_still=True)
print('rendered', OUT)
