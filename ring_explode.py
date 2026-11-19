"""
ring_explode.py - Smart ring: assembled -> exploded view -> re-assembled.

Run headless:
    blender -b -P ring_explode.py                    # uses the variables below
    blender -b -P ring_explode.py -- --mode final    # override MODE from the CLI
    blender -b -P ring_explode.py -- --no-render     # only build + save the .blend

Optional CLI overrides (after "--"):
    --mode test|final   --engine CYCLES|EEVEE   --samples N
    --res WxH           --frames 1,40,80 | --frames 1-240
    --out DIR           --device AUTO|CPU|GPU    --no-render   --no-save

Units: 1 Blender unit = 1 mm (scene unit scale 0.001, metric, millimetres).
All parts are solids of revolution (full rings or arcs) around the local Z axis
of the "Ring_Root" empty, so every part shares the centre and axis of the shell.
Blender 4.2+ (tested on 4.5 LTS). No image textures are used.
"""

import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Quaternion, Vector

# =============================================================================
# GLOBAL SETTINGS
# =============================================================================
MODE = "test"            # "test" or "final"
ENGINE = "CYCLES"        # "CYCLES" or "EEVEE"
DEVICE = "AUTO"          # "AUTO" (GPU if available), "CPU" or "GPU"

if MODE == "test":
    RESOLUTION = (480, 270)
    SAMPLES = 32
    FRAME_RANGE = [1, 40, 80, 120, 180, 240]   # list = render just these frames
    OUTPUT_DIR = "test"
else:
    RESOLUTION = (1920, 1080)
    SAMPLES = 256
    FRAME_RANGE = (1, 240)                     # tuple = (start, end) animation
    OUTPUT_DIR = "final"

DENOISE = True           # OpenImageDenoise (always on in final mode)
DO_RENDER = True         # False = just build the scene and save the .blend
SAVE_BLEND = True
BLEND_NAME = "ring_explode.blend"

FPS = 24
FRAME_START, FRAME_END = 1, 240


# -----------------------------------------------------------------------------
# CLI overrides (everything after "--")
# -----------------------------------------------------------------------------
def _apply_cli_overrides():
    global MODE, ENGINE, DEVICE, RESOLUTION, SAMPLES, FRAME_RANGE, OUTPUT_DIR
    global DO_RENDER, SAVE_BLEND
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

    def val(flag):
        if flag in argv:
            i = argv.index(flag)
            if i + 1 < len(argv):
                return argv[i + 1]
        return None

    mode = val("--mode")
    if mode and mode != MODE:
        MODE = mode
        if MODE == "final":
            RESOLUTION, SAMPLES, FRAME_RANGE, OUTPUT_DIR = (1920, 1080), 256, (1, 240), "final"
        else:
            RESOLUTION, SAMPLES, FRAME_RANGE, OUTPUT_DIR = (480, 270), 32, [1, 40, 80, 120, 180, 240], "test"
    if val("--engine"):
        ENGINE = val("--engine").upper()
    if val("--device"):
        DEVICE = val("--device").upper()
    if val("--samples"):
        SAMPLES = int(val("--samples"))
    if val("--res"):
        w, h = val("--res").lower().split("x")
        RESOLUTION = (int(w), int(h))
    if val("--frames"):
        f = val("--frames")
        if "-" in f:
            a, b = f.split("-")
            FRAME_RANGE = (int(a), int(b))
        else:
            FRAME_RANGE = [int(x) for x in f.split(",")]
    if val("--out"):
        OUTPUT_DIR = val("--out")
    if "--no-render" in argv:
        DO_RENDER = False
    if "--no-save" in argv:
        SAVE_BLEND = False


_apply_cli_overrides()

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()
OUT_ABS = OUTPUT_DIR if os.path.isabs(OUTPUT_DIR) else os.path.join(BASE_DIR, OUTPUT_DIR)


def log(*a):
    print("[ring_explode]", *a, flush=True)


# =============================================================================
# DIMENSIONS (mm).  Radii measured from the common ring axis.
# =============================================================================
HALF_W = 4.0                 # ring width 8 mm
# Outer titanium shell (OD 22)
SH_R_OUT = 10.92             # + crown 0.08 -> 11.0 at the centre line
SH_CROWN = 0.08
SH_R_BORE = 10.42            # inner bore
SH_R_STEP = 10.56            # thin recess (rebate) on the inner edge
SH_Z_STEP = 3.5
# Sensor frame
SF_R0, SF_R1, SF_HZ = 10.10, 10.40, 3.30
# Flexible PCB
PCB_R0, PCB_R1, PCB_HZ = 9.95, 10.03, 2.80
# Battery arc (200 deg)
BAT_R0, BAT_R1, BAT_HZ = 8.56, 9.94, 3.00
BAT_A0, BAT_A1 = 80.0, 280.0
# Inner transparent shell (ID 17 -> wall 2.5 mm total; 1.0 mm clear wall)
IN_R0, IN_R1, IN_HZ = 8.50, 9.50, 3.40
IN_FLANGE_R = 10.38          # front/back flange that closes the ring faces
# Charging pins
PIN_R, PIN_H, PIN_RING = 0.45, 3.0, 9.0
CHIP_T = 0.20               # chip height; chip top + wire stay below SF_R0..SF_R1
PIN_ANGLES = (24.0, 36.0)

EXPLODE_GAP = 18.0           # distance between neighbouring parts
# explode axis in world space: ~45 deg from vertical, tilted toward the camera
EXPLODE_DIR = Vector((0.70, -0.50, -0.55)).normalized()
RING_SPIN = 0.0              # extra roll of the assembly around its own axis (deg)

random.seed(7)


# =============================================================================
# HELPERS - scene / collections
# =============================================================================
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    scn.name = "SmartRing"
    us = scn.unit_settings
    us.system = 'METRIC'
    us.scale_length = 0.001
    us.length_unit = 'MILLIMETERS'
    scn.render.fps = FPS
    scn.frame_start = FRAME_START
    scn.frame_end = FRAME_END
    return scn


def new_collection(name, parent=None):
    col = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(col)
    return col


def link(obj, col):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj


def new_empty(name, col, parent=None, size=5.0):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = 'PLAIN_AXES'
    e.empty_display_size = size
    col.objects.link(e)
    if parent:
        e.parent = parent
    return e


# =============================================================================
# HELPERS - geometry (everything is a solid of revolution around local Z)
# =============================================================================
def fillet_polygon(corners, segs=4):
    """corners: [(x, y, radius)] closed polygon -> list of Vector((x, y)) with
    every corner rounded by its radius (works for convex and concave corners)."""
    n = len(corners)
    out = []
    for i, (px, py, rad) in enumerate(corners):
        P = Vector((px, py))
        if rad <= 0:
            out.append(P)
            continue
        A = Vector(corners[i - 1][:2])
        B = Vector(corners[(i + 1) % n][:2])
        u1, u2 = A - P, B - P
        l1, l2 = u1.length, u2.length
        u1.normalize()
        u2.normalize()
        ang = math.acos(max(-0.9999, min(0.9999, u1.dot(u2))))
        if ang > math.pi - 0.02:          # practically straight
            out.append(P)
            continue
        t = rad / math.tan(ang / 2)
        tmax = 0.49 * min(l1, l2)
        if t > tmax:
            t = tmax
            rad = t * math.tan(ang / 2)
        T1, T2 = P + u1 * t, P + u2 * t
        C = P + (u1 + u2).normalized() * (rad / math.sin(ang / 2))
        a1 = math.atan2(T1.y - C.y, T1.x - C.x)
        a2 = math.atan2(T2.y - C.y, T2.x - C.x)
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for k in range(segs + 1):
            a = a1 + da * k / segs
            out.append(C + Vector((math.cos(a), math.sin(a))) * rad)
    return out


def rounded_rect(r0, r1, z0, z1, rad=0.0, segs=4):
    return fillet_polygon([(r0, z0, rad), (r1, z0, rad), (r1, z1, rad), (r0, z1, rad)], segs)


def add_revolve(bm, profile, a0_deg=0.0, a1_deg=360.0, segs=None,
                taper_len=0.0, taper_min=0.25):
    """Revolve a closed (r, z) profile around Z between two angles.
    Full 360 deg -> closed ring; otherwise an arc with end caps.  taper_len (mm)
    rounds the arc ends by shrinking the profile toward its centroid."""
    full = abs((a1_deg - a0_deg) - 360.0) < 1e-6
    span = math.radians(a1_deg - a0_deg)
    if segs is None:
        segs = max(2, int(math.ceil(abs(a1_deg - a0_deg) / 1.4)))
    a0 = math.radians(a0_deg)
    prof = [Vector((p[0], p[1])) for p in profile]
    rc = sum(p.x for p in prof) / len(prof)
    zc = sum(p.y for p in prof) / len(prof)
    count = segs if full else segs + 1
    rings = []
    for k in range(count):
        a = a0 + span * k / segs
        s = 1.0
        if taper_len > 0 and not full:
            d = min(a - a0, a0 + span - a) * rc
            if d < taper_len:
                x = 1.0 - d / taper_len
                s = max(taper_min, math.sqrt(max(0.0, 1.0 - x * x)))
        ca, sa = math.cos(a), math.sin(a)
        ring = []
        for p in prof:
            r = rc + (p.x - rc) * s
            z = zc + (p.y - zc) * s
            ring.append(bm.verts.new((r * ca, r * sa, z)))
        rings.append(ring)
    n = len(prof)
    last = count if full else count - 1
    for k in range(last):
        ra, rb = rings[k], rings[(k + 1) % count]
        for j in range(n):
            bm.faces.new((ra[j], ra[(j + 1) % n], rb[(j + 1) % n], rb[j]))
    if not full:
        bm.faces.new(rings[0])
        bm.faces.new(list(reversed(rings[-1])))


def add_curved_box(bm, r0, r1, ang_deg, width, z0, z1, rad=0.0, rsegs=3):
    """Small rectangular part that hugs the cylinder (an arc of a ring)."""
    rm = 0.5 * (r0 + r1)
    half = math.degrees(0.5 * width / rm)
    segs = max(2, int(math.ceil(2 * half / 1.0)))
    add_revolve(bm, rounded_rect(r0, r1, z0, z1, rad, rsegs),
                ang_deg - half, ang_deg + half, segs)


def mesh_object(name, bm, col, mat=None, parent=None, smooth=True, sharp_angle=40.0):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
        if hasattr(me, "set_sharp_from_angle"):
            me.set_sharp_from_angle(angle=math.radians(sharp_angle))
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    if mat:
        me.materials.append(mat)
    if parent:
        ob.parent = parent
    return ob


# =============================================================================
# HELPERS - materials (Principled BSDF only, value based / procedural)
# =============================================================================
def srgb(hexstr):
    """'#rrggbb' -> linear RGBA"""
    h = hexstr.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def set_in(node, names, value):
    """Set the first existing input among `names` (handles API renames)."""
    for n in (names if isinstance(names, (list, tuple)) else [names]):
        if n in node.inputs:
            node.inputs[n].default_value = value
            return node.inputs[n]
    return None


def principled(name, base="#808080", metallic=0.0, roughness=0.5, ior=1.5,
               transmission=0.0, coat=0.0, coat_rough=0.03, emission=None,
               emission_strength=0.0, aniso=0.0, radial_tangent=False,
               shadow_transparent=False, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = nodes.get("Principled BSDF")
    out = nodes.get("Material Output")
    set_in(bsdf, "Base Color", srgb(base) if isinstance(base, str) else base)
    set_in(bsdf, "Metallic", metallic)
    set_in(bsdf, "Roughness", roughness)
    set_in(bsdf, "IOR", ior)
    set_in(bsdf, ["Transmission Weight", "Transmission"], transmission)
    set_in(bsdf, ["Coat Weight", "Clearcoat"], coat)
    set_in(bsdf, ["Coat Roughness", "Clearcoat Roughness"], coat_rough)
    set_in(bsdf, "Alpha", alpha)
    if emission is not None:
        set_in(bsdf, ["Emission Color", "Emission"],
               srgb(emission) if isinstance(emission, str) else emission)
        set_in(bsdf, "Emission Strength", emission_strength)
    if aniso > 0:
        set_in(bsdf, ["Anisotropic"], aniso)
        if radial_tangent and "Tangent" in bsdf.inputs:
            tan = nodes.new("ShaderNodeTangent")
            tan.direction_type = 'RADIAL'
            tan.axis = 'Z'
            tan.location = (-300, -400)
            links.new(tan.outputs["Tangent"], bsdf.inputs["Tangent"])
    if shadow_transparent:
        # Let shadow rays pass through clear parts so the electronics inside
        # the clear shell stay lit and the shadow catcher gets a soft shadow.
        lp = nodes.new("ShaderNodeLightPath")
        tr = nodes.new("ShaderNodeBsdfTransparent")
        mix = nodes.new("ShaderNodeMixShader")
        lp.location, tr.location, mix.location = (-300, 300), (-50, -650), (300, 0)
        out.location = (550, 0)
        links.new(lp.outputs["Is Shadow Ray"], mix.inputs[0])
        links.new(bsdf.outputs[0], mix.inputs[1])
        links.new(tr.outputs[0], mix.inputs[2])
        links.new(mix.outputs[0], out.inputs["Surface"])
    # EEVEE niceties (ignored by Cycles)
    if transmission > 0 or alpha < 1:
        for attr, v in (("use_screen_refraction", True), ("surface_render_method", 'BLENDED')):
            if hasattr(mat, attr):
                try:
                    setattr(mat, attr, v)
                except Exception:
                    pass
    return mat


def build_materials():
    M = {}
    # 1 outer shell: black titanium, metallic 1, rough 0.15, radial anisotropy,
    #   plus a thin clear coat (the black DLC-like finish of the reference).
    M["shell"] = principled("M_Shell_Titanium_Black", "#1a1a1a", metallic=1.0, roughness=0.15,
                            aniso=0.35, radial_tangent=True, coat=0.6, coat_rough=0.04)
    # 2 sensor frame / 3 battery: metallic 0.8, rough 0.35
    M["frame"] = principled("M_SensorFrame_Dark", "#2b2b2b", metallic=0.8, roughness=0.35)
    M["battery"] = principled("M_Battery_DarkMetal", "#3a3934", metallic=0.8, roughness=0.35)
    # 4 PCB
    M["pcb"] = principled("M_PCB_DarkGreen", "#13261a", metallic=0.0, roughness=0.38,
                          coat=0.4, coat_rough=0.12)
    M["gold"] = principled("M_PCB_Gold", "#ffcf7a", metallic=1.0, roughness=0.3)
    M["chip"] = principled("M_PCB_Chip_Black", "#0b0b0b", metallic=0.0, roughness=0.5)
    M["wire"] = principled("M_Wire_Red", "#d10a0a", metallic=0.0, roughness=0.4,
                           emission="#ff1010", emission_strength=0.25)
    # 5 pins
    M["pin"] = principled("M_Pin_Silver", "#e6e6ea", metallic=1.0, roughness=0.2)
    # 6 clear shell
    M["glass"] = principled("M_Shell_Clear", "#f2f6f8", metallic=0.0, roughness=0.02,
                            ior=1.45, transmission=1.0, shadow_transparent=True)
    # LEDs / sensor windows
    M["led_green"] = principled("M_LED_Green", "#0a0a0a", roughness=0.3,
                                emission="#00ff40", emission_strength=6.0)
    M["led_red"] = principled("M_LED_Red", "#0a0a0a", roughness=0.3,
                              emission="#ff2a10", emission_strength=4.0)
    M["window"] = principled("M_Sensor_Window", "#5a5a5a", roughness=0.08, ior=1.5,
                             transmission=0.85, shadow_transparent=True)
    M["module"] = principled("M_Sensor_Module", "#1c1c1e", metallic=0.3, roughness=0.4)
    # helpers
    M["guide"] = principled("M_Guide_Dotted", "#3a3a3a", roughness=0.6,
                            emission="#2a2a2a", emission_strength=0.4)
    M["floor"] = principled("M_ShadowCatcher", "#eeeeee", roughness=0.8)
    return M


# =============================================================================
# COMPONENTS
# =============================================================================
def build_shell_outer(col, root, M):
    corners = [
        (SH_R_STEP, -HALF_W, 0.06),
        (SH_R_OUT, -HALF_W, 0.65),
    ]
    # slightly domed outer face
    for k in range(1, 10):
        z = -HALF_W + 2 * HALF_W * k / 10
        corners.append((SH_R_OUT + SH_CROWN * (1 - (z / HALF_W) ** 2), z, 0.0))
    corners += [
        (SH_R_OUT, HALF_W, 0.65),
        (SH_R_STEP, HALF_W, 0.06),
        (SH_R_STEP, SH_Z_STEP, 0.03),     # thin recess on the inner edge
        (SH_R_BORE, SH_Z_STEP, 0.04),
        (SH_R_BORE, -SH_Z_STEP, 0.04),
        (SH_R_STEP, -SH_Z_STEP, 0.03),
    ]
    bm = bmesh.new()
    add_revolve(bm, fillet_polygon(corners, 6), 0, 360, 256)
    return mesh_object("Shell_Outer", bm, col, M["shell"], root, sharp_angle=50)


def build_sensor_frame(col, root, M):
    bm = bmesh.new()
    add_revolve(bm, rounded_rect(SF_R0, SF_R1, -SF_HZ, SF_HZ, 0.08, 3), 0, 360, 256)
    frame = mesh_object("Sensor_Frame", bm, col, M["frame"], root)

    # two sensor windows (housing = dark translucent, core = emissive)
    win = bmesh.new()
    core_g, core_r = bmesh.new(), bmesh.new()
    for ang, core in ((-28.0, core_g), (-52.0, core_r)):
        add_curved_box(win, 9.70, SF_R0 + 0.02, ang, 1.9, -1.0, 1.0, 0.12)
        add_curved_box(core, 9.80, 9.95, ang, 0.9, -0.45, 0.45, 0.05)
    mesh_object("Sensor_Frame_Windows", win, col, M["window"], frame)
    mesh_object("Sensor_Frame_Window_Green", core_g, col, M["led_green"], frame)
    mesh_object("Sensor_Frame_Window_Red", core_r, col, M["led_red"], frame)

    # 4 small green LED dots on the inner face
    dots = bmesh.new()
    for ang, z in ((60.0, 2.2), (140.0, -2.2), (215.0, 2.2), (300.0, -2.0)):
        add_curved_box(dots, SF_R0 - 0.06, SF_R0 + 0.01, ang, 0.45, z - 0.22, z + 0.22, 0.06)
    mesh_object("Sensor_Frame_LED_Dots", dots, col, M["led_green"], frame)
    return frame


def build_battery(col, root, M):
    bm = bmesh.new()
    add_revolve(bm, rounded_rect(BAT_R0, BAT_R1, -BAT_HZ, BAT_HZ, 0.45, 5),
                BAT_A0, BAT_A1, 180, taper_len=1.6, taper_min=0.3)
    bat = mesh_object("Battery_Arc", bm, col, M["battery"], root, sharp_angle=60)
    # tiny terminal tab at one end
    tab = bmesh.new()
    add_curved_box(tab, BAT_R1 - 0.05, BAT_R1 + 0.02, BAT_A1 - 6.0, 1.4, -0.6, 0.6, 0.05)
    mesh_object("Battery_Tab", tab, col, M["gold"], bat)
    return bat


def build_pcb(col, root, M):
    bm = bmesh.new()
    add_revolve(bm, rounded_rect(PCB_R0, PCB_R1, -PCB_HZ, PCB_HZ, 0.03, 2), 0, 360, 256)
    pcb = mesh_object("PCB_Flex", bm, col, M["pcb"], root)

    out_r = PCB_R1             # outer copper level
    in_r = PCB_R0              # inner copper level
    gold = bmesh.new()
    chips = bmesh.new()

    # --- chips (black, 4) with gold leads on two of them ------------------
    chip_defs = [  # angle, width(mm, tangential), z0, z1, leads
        # (camera sees the outer face of the PCB around local 100-200 deg)
        (112.0, 2.2, -1.0, 1.2, True),
        (146.0, 1.5, 0.6, 2.1, False),
        (176.0, 2.6, -2.0, 0.2, True),
        (214.0, 1.3, 0.4, 1.8, False),
    ]
    for ang, w, z0, z1, leads in chip_defs:
        add_curved_box(chips, out_r, out_r + CHIP_T, ang, w, z0, z1, 0.05)
        if leads:
            n = 5
            for i in range(n):
                a = ang + math.degrees((-0.4 * w + 0.8 * w * i / (n - 1)) / out_r)
                add_curved_box(gold, out_r, out_r + 0.06, a, 0.16, z0 - 0.3, z0 + 0.05)
                add_curved_box(gold, out_r, out_r + 0.06, a, 0.16, z1 - 0.05, z1 + 0.3)

    # --- gold traces: circumferential runs with axial jogs (both sides) ----
    def trace(r, t_dir, ang0, z0, legs):
        a, z = ang0, z0
        w = 0.11
        for da, dz in legs:
            if da:
                a1 = a + da
                lo, hi = min(a, a1), max(a, a1)
                add_revolve(gold, rounded_rect(r, r + t_dir * 0.018, z - w / 2, z + w / 2),
                            lo - 0.3, hi + 0.3)
                a = a1
            if dz:
                z1 = max(-PCB_HZ + 0.25, min(PCB_HZ - 0.25, z + dz))
                add_curved_box(gold, r, r + t_dir * 0.018, a, w, min(z, z1) - w / 2, max(z, z1) + w / 2)
                z = z1

    for side_r, t_dir, n_tr in ((out_r, 1, 36), (in_r, -1, 16)):
        for _ in range(n_tr):
            a0 = random.uniform(0, 360)
            z0 = random.choice([-2.3, -1.8, -1.3, -0.7, 0.0, 0.6, 1.2, 1.7, 2.3])
            legs = []
            for _ in range(random.randint(1, 3)):
                legs.append((random.choice([-1, 1]) * random.uniform(6, 26),
                             random.choice([0, 0, -0.6, 0.6, -1.1, 1.1])))
            trace(side_r, t_dir, a0, z0, legs)

    # --- square gold pads + connector fingers ------------------------------
    for ang, z in ((70.0, 1.5), (128.0, -1.6), (190.0, 1.2), (275.0, -1.4), (335.0, 1.6), (20.0, -1.5)):
        add_curved_box(gold, out_r, out_r + 0.03, ang, 0.9, z - 0.45, z + 0.45, 0.04)
    for i in range(6):
        add_curved_box(gold, out_r, out_r + 0.03, 200.0 + i * 2.2, 0.22, -2.6, -1.5, 0.02)
    for ang, z in ((40.0, 0.8), (250.0, -1.2), (180.0, 0.4)):   # pads inside
        add_curved_box(gold, in_r - 0.03, in_r, ang, 0.8, z - 0.4, z + 0.4, 0.04)

    mesh_object("PCB_Traces_Gold", gold, col, M["gold"], pcb, smooth=False)
    mesh_object("PCB_Chips", chips, col, M["chip"], pcb, sharp_angle=35)

    # --- thin red wires -----------------------------------------------------
    def wire(name, pts):
        cu = bpy.data.curves.new(name, 'CURVE')
        cu.dimensions = '3D'
        cu.bevel_depth = 0.06
        cu.bevel_resolution = 4
        cu.use_fill_caps = True
        sp = cu.splines.new('NURBS')
        sp.points.add(len(pts) - 1)
        for p, co in zip(sp.points, pts):
            p.co = (*co, 1.0)
        sp.order_u = 4
        sp.use_endpoint_u = True
        sp.use_smooth = True
        ob = bpy.data.objects.new(name, cu)
        col.objects.link(ob)
        cu.materials.append(M["wire"])
        ob.parent = pcb
        return ob

    # The wires lie on the PCB and stay below the sensor frame's inner face
    # (r < 10.4) so they are hidden once assembled; they hop over the chips.
    wr = 0.06
    chip_top = out_r + CHIP_T + 0.01

    def lift(a_deg, z):
        best = 0.0
        for ang, w, z0, z1, _ in chip_defs:
            half = math.degrees(0.5 * w / out_r)
            d = abs((a_deg - ang + 180) % 360 - 180) - half
            fa = 1.0 if d <= 0 else max(0.0, 1.0 - d / 3.0)
            fz = 1.0 if z0 - 0.25 <= z <= z1 + 0.25 else 0.0
            best = max(best, fa * fz)
        return best * best * (3 - 2 * best)

    pts = []
    for k in range(140):
        t = k / 139
        a_deg = -20 + 250 * t
        a = math.radians(a_deg)
        z = 2.15 * math.sin(t * math.pi * 2.3 + 0.4) * 0.9
        r = out_r + wr + (chip_top - out_r) * lift(a_deg, z)
        pts.append((r * math.cos(a), r * math.sin(a), z))
    wire("PCB_Wire_Red", pts)
    pts = []
    for k in range(24):
        t = k / 23
        a = math.radians(305 + 30 * t)
        r = out_r + wr + 0.25 * math.sin(t * math.pi)     # small loop off the board
        z = 2.4 - 0.6 * t
        pts.append((r * math.cos(a), r * math.sin(a), z))
    wire("PCB_Wire_Red_Loop", pts)
    return pcb


def build_pins(col, root, M):
    holder = new_empty("Charging_Pins", col, root, 3)
    pins = []
    for name, ang in (("Pin_L", PIN_ANGLES[0]), ("Pin_R", PIN_ANGLES[1])):
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=48,
                              radius1=PIN_R, radius2=PIN_R, depth=PIN_H)
        # small collar near the base
        collar = bmesh.ops.create_cone(bm, cap_ends=True, segments=48,
                                       radius1=PIN_R + 0.15, radius2=PIN_R + 0.15, depth=0.35)
        bmesh.ops.translate(bm, verts=collar["verts"], vec=(0, 0, -PIN_H / 2 + 0.6))
        ob = mesh_object(name, bm, col, M["pin"], holder, sharp_angle=40)
        a = math.radians(ang)
        ob.location = (PIN_RING * math.cos(a), PIN_RING * math.sin(a), 0.0)
        bev = ob.modifiers.new("Bevel", 'BEVEL')
        bev.width = 0.07
        bev.segments = 3
        bev.limit_method = 'ANGLE'
        pins.append(ob)
    return holder


def build_shell_inner(col, root, M):
    corners = [
        (IN_R0, -HALF_W, 0.35),
        (IN_FLANGE_R, -HALF_W, 0.12),
        (IN_FLANGE_R, -IN_HZ, 0.05),
        (IN_R1, -IN_HZ, 0.12),
        (IN_R1, IN_HZ, 0.12),
        (IN_FLANGE_R, IN_HZ, 0.05),
        (IN_FLANGE_R, HALF_W, 0.12),
        (IN_R0, HALF_W, 0.35),
    ]
    bm = bmesh.new()
    add_revolve(bm, fillet_polygon(corners, 6), 0, 360, 256)
    shell = mesh_object("Shell_Inner", bm, col, M["glass"], root, sharp_angle=60)

    # embedded sensor module with green LEDs (sits inside the clear wall)
    mod = bmesh.new()
    add_curved_box(mod, 8.66, 9.30, 0.0, 2.6, -1.9, 1.9, 0.12)
    mesh_object("Shell_Inner_Sensor_Module", mod, col, M["module"], shell)
    g = bmesh.new()
    for ang in (-3.0, 3.0):
        add_curved_box(g, 8.60, 8.68, ang, 0.55, -1.25, -0.65, 0.05)
    mesh_object("Shell_Inner_LED_Green", g, col, M["led_green"], shell)
    r = bmesh.new()
    add_curved_box(r, 8.60, 8.68, 0.0, 0.7, 0.75, 1.35, 0.05)
    mesh_object("Shell_Inner_LED_Red", r, col, M["led_red"], shell)
    pd = bmesh.new()
    add_curved_box(pd, 8.61, 8.68, 0.0, 1.0, -0.25, 0.35, 0.03)
    mesh_object("Shell_Inner_Photodiode", pd, col, M["gold"], shell)
    return shell


def build_guide_line(col, root, M, length=220.0, dash=0.8, gap=1.4, radius=0.11):
    bm = bmesh.new()
    z = -length / 2
    while z < length / 2:
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=radius,
                                    radius2=radius, depth=dash)
        bmesh.ops.translate(bm, verts=res["verts"], vec=(0, 0, z + dash / 2))
        z += dash + gap
    ob = mesh_object("Guide_Axis_Dotted", bm, col, M["guide"], root, smooth=False)
    for attr in ("visible_shadow", "visible_glossy", "visible_transmission", "visible_diffuse"):
        if hasattr(ob, attr):
            setattr(ob, attr, False)
    return ob


# =============================================================================
# WORLD, LIGHTS, CAMERA
# =============================================================================
def build_world():
    w = bpy.data.worlds.new("World_Studio")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    n, l = nt.nodes, nt.links
    for x in list(n):
        n.remove(x)
    out = n.new("ShaderNodeOutputWorld")
    out.location = (900, 0)
    # camera sees a flat #eeeeee backdrop ...
    bg_cam = n.new("ShaderNodeBackground")
    bg_cam.inputs[0].default_value = srgb("#eeeeee")
    bg_cam.inputs[1].default_value = 1.0
    bg_cam.location = (400, 200)
    # ... everything else sees a soft light-grey studio gradient (ambient + reflections)
    tc = n.new("ShaderNodeTexCoord")
    tc.location = (-600, -100)
    sep = n.new("ShaderNodeSeparateXYZ")
    sep.location = (-400, -100)
    mr = n.new("ShaderNodeMapRange")
    mr.location = (-200, -100)
    mr.inputs["From Min"].default_value = -0.4
    mr.inputs["From Max"].default_value = 0.9
    ramp = n.new("ShaderNodeValToRGB")
    ramp.location = (0, -100)
    ramp.color_ramp.elements[0].color = (0.30, 0.30, 0.31, 1)
    ramp.color_ramp.elements[1].color = (0.95, 0.95, 0.96, 1)
    bg_env = n.new("ShaderNodeBackground")
    bg_env.location = (400, -100)
    bg_env.inputs[1].default_value = 0.55
    lp = n.new("ShaderNodeLightPath")
    lp.location = (400, 450)
    mix = n.new("ShaderNodeMixShader")
    mix.location = (700, 0)
    l.new(tc.outputs["Generated"], sep.inputs[0])
    l.new(sep.outputs["Z"], mr.inputs["Value"])
    l.new(mr.outputs["Result"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], bg_env.inputs["Color"])
    l.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    l.new(bg_env.outputs[0], mix.inputs[1])
    l.new(bg_cam.outputs[0], mix.inputs[2])
    l.new(mix.outputs[0], out.inputs["Surface"])


def area_light(name, col, loc, target, size, power, shape='RECTANGLE', size_y=None,
               color=(1, 1, 1), parent=None):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.shape = shape
    ld.size = size
    if size_y is not None:
        ld.size_y = size_y
    ld.energy = power
    ld.color = color
    ob = bpy.data.objects.new(name, ld)
    col.objects.link(ob)
    ob.location = loc
    if parent:
        ob.parent = parent
    con = ob.constraints.new('TRACK_TO')
    con.target = target
    con.track_axis = 'TRACK_NEGATIVE_Z'
    con.up_axis = 'UP_Y'
    if hasattr(ob, "visible_camera"):
        ob.visible_camera = False
    return ob


def build_lights(col, target, rig=None):
    """Key upper-left, fill right, rim behind - all relative to the camera.
    The lights are parented to the camera pivot so the studio set-up orbits
    with the camera and the look stays consistent during the 60 deg orbit."""
    # Power scales with distance^2 because 1 unit = 1 mm.
    def p(watts_at_1m_equiv, dist):
        return watts_at_1m_equiv * dist * dist

    key_loc = Vector((-170, -160, 210))
    fill_loc = Vector((230, -130, 40))
    rim_loc = Vector((70, 230, 120))
    area_light("Light_Key", col, key_loc, target, 170, p(LIGHT_KEY, key_loc.length),
               'RECTANGLE', 120, (1.0, 0.98, 0.96), rig)
    area_light("Light_Fill", col, fill_loc, target, 240, p(LIGHT_FILL, fill_loc.length),
               'RECTANGLE', 160, (0.96, 0.98, 1.0), rig)
    area_light("Light_Rim", col, rim_loc, target, 140, p(LIGHT_RIM, rim_loc.length),
               'RECTANGLE', 60, (1.0, 1.0, 1.0), rig)


LIGHT_KEY, LIGHT_FILL, LIGHT_RIM = 20.0, 6.0, 25.0     # tuned from test renders

CAM_ELEV = 12.0          # degrees above the ring centre
CAM_DIST_NEAR = 108.0    # assembled close-up
CAM_DIST_FAR = 250.0     # framing for the exploded stack
CAM_ORBIT = -60.0         # degrees, frames 120 -> 180 (negative = toward the left)


def build_camera(col, target):
    pivot = new_empty("Cam_Pivot", col, None, 10)
    cd = bpy.data.cameras.new("Camera")
    cd.type = 'PERSP'
    cd.lens = 50.0
    cd.sensor_width = 36.0
    cd.sensor_fit = 'HORIZONTAL'
    cd.clip_start = 1.0
    cd.clip_end = 5000.0
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = 5.6
    cd.dof.focus_object = target
    cam = bpy.data.objects.new("Camera", cd)
    col.objects.link(cam)
    cam.parent = pivot
    con = cam.constraints.new('TRACK_TO')
    con.target = target
    con.track_axis = 'TRACK_NEGATIVE_Z'
    con.up_axis = 'UP_Y'
    bpy.context.scene.camera = cam
    return pivot, cam


def cam_local(dist):
    e = math.radians(CAM_ELEV)
    return Vector((0.0, -dist * math.cos(e), dist * math.sin(e)))


# =============================================================================
# ANIMATION
# =============================================================================
def key(obj, path, frame, value=None, index=-1, interp=None):
    if value is not None:
        prop = getattr(obj, path)
        if index >= 0:
            prop[index] = value
        else:
            setattr(obj, path, value)
    obj.keyframe_insert(data_path=path, frame=frame, index=index)
    if interp:
        ad = obj.animation_data
        if ad and ad.action:
            for fc in iter_fcurves(ad.action):
                if fc.data_path == path:
                    for kp in fc.keyframe_points:
                        if abs(kp.co[0] - frame) < 1e-4:
                            kp.interpolation = interp


def iter_fcurves(action):
    if hasattr(action, "fcurves") and len(action.fcurves):
        return list(action.fcurves)
    out = []          # Blender 4.4+/5.x layered actions
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            for bag in getattr(strip, "channelbags", []):
                out.extend(bag.fcurves)
    return out


def ease_all(obj):
    """Bezier + auto-clamped handles = smooth ease-in / ease-out between holds."""
    ad = obj.animation_data
    if not (ad and ad.action):
        return
    for fc in iter_fcurves(ad.action):
        for kp in fc.keyframe_points:
            if kp.interpolation != 'CONSTANT':
                kp.interpolation = 'BEZIER'
            kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
        fc.update()


def animate(parts, turntable, guide, pivot, cam):
    # Frames 1-40: assembled ring, slow turn.
    turntable.rotation_euler = (0, 0, math.radians(-18))
    key(turntable, "rotation_euler", 1, index=2)
    turntable.rotation_euler = (0, 0, 0)
    key(turntable, "rotation_euler", 40, index=2)
    ease_all(turntable)

    n = len(parts)
    # Final exploded slot along the axis = outside -> inside order, centred on 0:
    #   Shell_Outer -45, Sensor_Frame -27, Battery -9, PCB +9, Pins +27, Shell_Inner +45
    # Departure order works from both ends inward so that no part has to travel
    # through a part that is still sitting in the assembly:
    #   Shell_Outer, Shell_Inner, Sensor_Frame, Pins, Battery, PCB
    # Frames 40-120: one by one (stagger 8 f, 40 f each, last one lands on 120).
    # Frames 180-240: exact reverse order (stagger 6 f, 28 f each, done by 238).
    order = [0, 5, 1, 4, 2, 3]
    spins = [12, -16, 22, -18, 26, -14]
    tilts = [4, -3, 5, -4, 3, -5]
    for i, ob in enumerate(parts):
        off = (i - (n - 1) / 2.0) * EXPLODE_GAP
        rank = order.index(i)
        s_out = 40 + 8 * rank
        e_out = s_out + 40
        s_in = 180 + 6 * (n - 1 - rank)
        e_in = s_in + 28
        for f, z, rz, rx in ((s_out, 0, 0, 0), (e_out, off, spins[i], tilts[i]),
                             (s_in, off, spins[i], tilts[i]), (e_in, 0, 0, 0)):
            ob.location = (0, 0, z)
            ob.rotation_euler = (math.radians(rx), 0, math.radians(rz))
            ob.keyframe_insert("location", frame=f)
            ob.keyframe_insert("rotation_euler", frame=f)
        ease_all(ob)

    # dotted axis grows with the explosion, retracts on re-assembly
    for f, s in ((40, 0.02), (112, 1.0), (186, 1.0), (236, 0.02)):
        guide.scale = (1, 1, s)
        guide.keyframe_insert("scale", frame=f)
    ease_all(guide)
    for f, hide in ((1, True), (41, False), (236, True)):
        guide.hide_render = hide
        guide.hide_viewport = hide
        guide.keyframe_insert("hide_render", frame=f)
        guide.keyframe_insert("hide_viewport", frame=f)

    # Camera: gentle push-in, pull back while exploding, orbit 60 deg 120-180,
    # push back in while re-assembling.
    for f, d in ((1, CAM_DIST_NEAR + 6), (40, CAM_DIST_NEAR), (96, CAM_DIST_FAR),
                 (184, CAM_DIST_FAR), (240, CAM_DIST_NEAR + 4)):
        cam.location = cam_local(d)
        cam.keyframe_insert("location", frame=f)
    ease_all(cam)
    for f, a in ((120, 0.0), (180, CAM_ORBIT)):
        pivot.rotation_euler = (0, 0, math.radians(a))
        pivot.keyframe_insert("rotation_euler", frame=f, index=2)
    ease_all(pivot)


# =============================================================================
# RENDER SETTINGS
# =============================================================================
def engine_id(name):
    items = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    if name.upper().startswith("EEVEE"):
        for cand in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
            if cand in items:
                return cand
    return "CYCLES"


def setup_cycles_device(scn):
    scn.cycles.device = 'CPU'
    if DEVICE == "CPU":
        return "CPU"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for backend in ("OPTIX", "CUDA", "HIP", "ONEAPI", "METAL"):
            try:
                prefs.compute_device_type = backend
            except TypeError:
                continue
            prefs.get_devices()
            devs = [d for d in prefs.devices if d.type == backend]
            if devs:
                for d in prefs.devices:
                    d.use = d.type == backend
                scn.cycles.device = 'GPU'
                return backend
    except Exception as ex:  # pragma: no cover
        log("GPU detection failed:", ex)
    return "CPU"


def setup_render(scn):
    r = scn.render
    r.engine = engine_id(ENGINE)
    r.resolution_x, r.resolution_y = RESOLUTION
    r.resolution_percentage = 100
    r.film_transparent = False
    r.image_settings.file_format = 'PNG'
    r.image_settings.color_mode = 'RGB'
    r.image_settings.color_depth = '8'
    r.use_persistent_data = True
    vs = scn.view_settings
    vs.view_transform = 'Standard'       # keeps the #eeeeee backdrop exact
    vs.look = 'None'
    vs.exposure = 0.0
    vs.gamma = 1.0

    if r.engine == 'CYCLES':
        c = scn.cycles
        dev = setup_cycles_device(scn)
        c.samples = SAMPLES
        c.preview_samples = 32
        c.use_adaptive_sampling = True
        c.adaptive_threshold = 0.01
        c.use_denoising = DENOISE or MODE == "final"
        try:
            c.denoiser = 'OPENIMAGEDENOISE'
        except TypeError:
            pass
        c.max_bounces = 16
        c.diffuse_bounces = 4
        c.glossy_bounces = 8
        c.transmission_bounces = 16
        c.transparent_max_bounces = 16
        c.caustics_reflective = False
        c.caustics_refractive = False
        c.blur_glossy = 1.0
        c.sample_clamp_indirect = 10.0
        log("Cycles device:", dev)
    else:
        e = scn.eevee
        for attr, v in (("taa_render_samples", SAMPLES), ("use_raytracing", True),
                        ("use_shadows", True), ("use_gtao", True), ("use_ssr", True),
                        ("use_ssr_refraction", True)):
            if hasattr(e, attr):
                try:
                    setattr(e, attr, v)
                except Exception:
                    pass
        # EEVEE has no shadow catcher: hide the floor plane
        floor = bpy.data.objects.get("Shadow_Catcher")
        if floor:
            floor.hide_render = True


# =============================================================================
# BUILD
# =============================================================================
def build():
    scn = reset_scene()
    M = build_materials()

    c_rig = new_collection("00_Rig")
    c_shell = new_collection("01_Shell_Outer")
    c_frame = new_collection("02_Sensor_Frame")
    c_bat = new_collection("03_Battery_Arc")
    c_pcb = new_collection("04_PCB_Flex")
    c_pins = new_collection("05_Charging_Pins")
    c_inner = new_collection("06_Shell_Inner")
    c_env = new_collection("07_Environment")
    c_cam = new_collection("08_Camera_Lights")

    turntable = new_empty("Ring_Turntable", c_rig, None, 15)
    root = new_empty("Ring_Root", c_rig, turntable, 12)
    root.rotation_mode = 'QUATERNION'
    root.rotation_quaternion = (EXPLODE_DIR.to_track_quat('Z', 'Y')
                                @ Quaternion((0, 0, 1), math.radians(RING_SPIN)))

    parts = [
        build_shell_outer(c_shell, root, M),
        build_sensor_frame(c_frame, root, M),
        build_battery(c_bat, root, M),
        build_pcb(c_pcb, root, M),
        build_pins(c_pins, root, M),
        build_shell_inner(c_inner, root, M),
    ]
    guide = build_guide_line(c_env, root, M)

    # shadow catcher under the exploded stack
    bpy.ops.mesh.primitive_plane_add(size=2000, location=(0, 0, -48))
    floor = bpy.context.active_object
    floor.name = "Shadow_Catcher"
    link(floor, c_env)
    floor.data.materials.append(M["floor"])
    floor.is_shadow_catcher = True
    # only the camera sees the catcher; glass/metal reflect the studio gradient
    for attr in ("visible_glossy", "visible_transmission"):
        if hasattr(floor, attr):
            setattr(floor, attr, False)

    target = new_empty("Cam_Target", c_cam, None, 4)
    pivot, cam = build_camera(c_cam, target)
    build_lights(c_cam, target, pivot)
    build_world()

    animate(parts, turntable, guide, pivot, cam)
    setup_render(scn)
    scn.frame_set(1)
    return scn


def render(scn):
    os.makedirs(OUT_ABS, exist_ok=True)
    if isinstance(FRAME_RANGE, (list, set)):
        for f in FRAME_RANGE:
            scn.frame_set(f)
            scn.render.filepath = os.path.join(OUT_ABS, "frame_%04d.png" % f)
            log("rendering frame", f, "->", scn.render.filepath)
            bpy.ops.render.render(write_still=True)
    else:
        scn.frame_start, scn.frame_end = FRAME_RANGE
        scn.render.filepath = os.path.join(OUT_ABS, "frame_")
        log("rendering animation", FRAME_RANGE, "->", OUT_ABS)
        bpy.ops.render.render(animation=True)


def main():
    log("MODE=%s ENGINE=%s RES=%s SAMPLES=%s FRAMES=%s OUT=%s"
        % (MODE, ENGINE, RESOLUTION, SAMPLES, FRAME_RANGE, OUT_ABS))
    scn = build()
    if SAVE_BLEND:
        # relative output path stored in the .blend (//final/frame_ or //test/frame_)
        scn.render.filepath = "//" + OUTPUT_DIR.strip("/") + "/frame_"
        path = os.path.join(BASE_DIR, BLEND_NAME)
        bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)
        log("saved", path)
    if DO_RENDER:
        render(scn)
    log("done")


if __name__ == "__main__":
    main()
