# -*- coding: utf-8 -*-
"""
Rotary circular platform with a 2-stage compound planetary reduction (concept macro).

Usage
-----
1. Open FreeCAD.
2. Open this file as a macro (or paste into FreeCAD Python console).
3. Run it to generate a grouped assembly in a new document.

Design disclaimer
-----------------
This is a concept/visualization macro, not a production transmission design.
Validate load capacity, tooth strength, backlash, materials, tolerances,
bearing fits, and lubrication before fabrication.
"""

import math
import FreeCAD as App
import Part


# -------------------------
# Parameters
# -------------------------
MODULE = 1.8
SUN_TEETH = 81
PLANET_TEETH = 9
RING_TEETH = 99
PLANET_COUNT = 11

STAGES = [
    {"name": "Stage1", "module": MODULE, "sun": SUN_TEETH, "planet": PLANET_TEETH, "ring": RING_TEETH, "z": 20.0},
    {"name": "Stage2", "module": MODULE, "sun": SUN_TEETH, "planet": PLANET_TEETH, "ring": RING_TEETH, "z": 38.0},
]

GEAR_WIDTH = 8.0
PLANET_CLEARANCE = 0.5
PLATFORM_THICKNESS = 10.0
HOUSING_TOP_Z = 66.0
BEARING_BALL_COUNT = 14

COLORS = {
    "fixed_dark": (0.28, 0.31, 0.36),
    "fixed_mid": (0.40, 0.43, 0.48),
    "fixed_light": (0.55, 0.58, 0.62),
    "rotating": (0.82, 0.58, 0.26),
    "rotating_alt": (0.90, 0.72, 0.35),
    "shaft": (0.65, 0.50, 0.22),
    "platform": (0.88, 0.84, 0.78),
}


# We cannot use standard equal angular spacing for 11 planets here:
# (S + R) / N = (81 + 99) / 11 = 180 / 11 is not integer.
# For simultaneous sun/planet and ring/planet tooth indexing, each planet center
# angle must satisfy a tooth-phase slot of:
#   Δθ_slot = 2π * P / (S + R) = 2π * 9 / 180 = 18°
# which yields 20 valid mesh slots around 360°. We place 11 planets on these
# valid slots using near-uniform slot picking; this is intentionally phased/unequal
# spacing, but each chosen slot keeps valid mesh phase with the fixed ring and sun.
PLANET_MESH_SLOT_COUNT = int((SUN_TEETH + RING_TEETH) / PLANET_TEETH)  # 20
PLANET_SLOT_ANGLE = (2.0 * math.pi) / PLANET_MESH_SLOT_COUNT


def choose_planet_slots(slot_count, planet_count):
    slots = [int(math.floor((i * slot_count) / float(planet_count))) for i in range(planet_count)]
    if len(set(slots)) != planet_count:
        raise ValueError("Planet slot calculation produced duplicate slots.")
    return slots


PLANET_SLOT_INDICES = choose_planet_slots(PLANET_MESH_SLOT_COUNT, PLANET_COUNT)


def polar_xy(radius, angle_rad):
    return App.Vector(radius * math.cos(angle_rad), radius * math.sin(angle_rad), 0.0)


def add_feature(group, name, shape, color, transparency=0):
    obj = DOC.addObject("Part::Feature", name)
    obj.Shape = shape
    group.addObject(obj)
    if hasattr(obj, "ViewObject"):
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.Transparency = transparency
    return obj


def make_external_gear(module, teeth, width, phase=0.0, bore_radius=0.0):
    pitch_r = 0.5 * module * teeth
    addendum = 0.60 * module
    dedendum = 0.70 * module
    root_r = max(0.8, pitch_r - dedendum)
    tip_r = pitch_r + addendum
    tooth_depth = tip_r - root_r
    circular_pitch = 2.0 * math.pi * pitch_r / teeth
    tooth_width = 0.52 * circular_pitch

    gear_shape = Part.makeCylinder(root_r, width)
    tooth_solids = []
    for t in range(teeth):
        ang = phase + (2.0 * math.pi * t / teeth)
        tooth = Part.makeBox(tooth_depth, tooth_width, width)
        tooth.translate(App.Vector(root_r, -0.5 * tooth_width, 0.0))
        tooth.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), math.degrees(ang))
        tooth_solids.append(tooth)

    if tooth_solids:
        gear_shape = gear_shape.multiFuse(tooth_solids)

    if bore_radius > 0.0:
        bore = Part.makeCylinder(bore_radius, width + 0.4)
        bore.translate(App.Vector(0.0, 0.0, -0.2))
        gear_shape = gear_shape.cut(bore)

    return gear_shape, pitch_r, root_r, tip_r


def make_internal_ring_gear(module, ring_teeth, width, phase=0.0):
    pitch_r = 0.5 * module * ring_teeth
    addendum = 0.60 * module
    dedendum = 0.70 * module
    tip_r_inward = pitch_r - addendum
    root_r_inward = pitch_r + dedendum
    rim_outer_r = root_r_inward + 7.5

    ring_shape = Part.makeCylinder(rim_outer_r, width).cut(Part.makeCylinder(tip_r_inward, width))

    circular_pitch = 2.0 * math.pi * pitch_r / ring_teeth
    slot_width = 0.50 * circular_pitch
    slot_depth = max(0.8, root_r_inward - tip_r_inward)

    slot_solids = []
    for t in range(ring_teeth):
        ang = phase + (2.0 * math.pi * t / ring_teeth)
        slot = Part.makeBox(slot_depth, slot_width, width + 0.2)
        slot.translate(App.Vector(tip_r_inward, -0.5 * slot_width, -0.1))
        slot.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), math.degrees(ang))
        slot_solids.append(slot)

    if slot_solids:
        ring_shape = ring_shape.cut(Part.makeCompound(slot_solids))

    return ring_shape, pitch_r, root_r_inward, rim_outer_r


def make_carrier(planet_center_r, planet_tip_r, width, sun_root_r, planet_angles):
    plate_thickness = width * 0.45
    outer_r = planet_center_r + 0.72 * planet_tip_r
    hub_r = max(3.2, 0.24 * sun_root_r)
    plate = Part.makeCylinder(outer_r, plate_thickness)
    hub = Part.makeCylinder(hub_r, plate_thickness)
    plate = plate.fuse(hub)

    pin_r = 1.5
    pin_h = width * 0.80
    pin_solids = []
    for ang in planet_angles:
        center = polar_xy(planet_center_r, ang)
        pin = Part.makeCylinder(pin_r, pin_h)
        pin.translate(App.Vector(center.x, center.y, -0.5))
        pin_solids.append(pin)

    if pin_solids:
        plate = plate.multiFuse(pin_solids)

    return plate, plate_thickness


def build_stage_geometry(stage_cfg, stage_phase):
    module = stage_cfg["module"]
    sun_teeth = stage_cfg["sun"]
    planet_teeth = stage_cfg["planet"]
    z_center = stage_cfg["z"]

    sun_shape, sun_pitch_r, sun_root_r, _ = make_external_gear(
        module=module,
        teeth=sun_teeth,
        width=GEAR_WIDTH,
        phase=stage_phase,
        bore_radius=2.2,
    )
    sun_shape.translate(App.Vector(0.0, 0.0, z_center - 0.5 * GEAR_WIDTH))

    planet_center_r = sun_pitch_r + (0.5 * module * planet_teeth)
    planet_shapes = []
    planet_angles = []
    planet_tip_r = None

    for slot_idx in PLANET_SLOT_INDICES:
        theta = stage_phase + (slot_idx * PLANET_SLOT_ANGLE)
        planet_angles.append(theta)

        # Phase planet teeth from sun mesh at this angular position. Because theta
        # is chosen from valid mesh slots, this phase is also compatible with the
        # fixed-ring mesh for the same planet.
        planet_phase = -(sun_teeth / float(planet_teeth)) * theta
        planet_shape, _, _, stage_planet_tip_r = make_external_gear(
            module=module,
            teeth=planet_teeth,
            width=GEAR_WIDTH,
            phase=planet_phase,
            bore_radius=1.8,
        )
        planet_tip_r = stage_planet_tip_r
        offset = polar_xy(planet_center_r, theta)
        planet_shape.translate(App.Vector(offset.x, offset.y, z_center - 0.5 * GEAR_WIDTH))
        planet_shapes.append(planet_shape)

    carrier_shape, plate_thickness = make_carrier(
        planet_center_r=planet_center_r,
        planet_tip_r=planet_tip_r,
        width=GEAR_WIDTH,
        sun_root_r=sun_root_r,
        planet_angles=planet_angles,
    )
    carrier_z = z_center + 0.5 * GEAR_WIDTH + PLANET_CLEARANCE
    carrier_shape.translate(App.Vector(0.0, 0.0, carrier_z))

    return {
        "sun": sun_shape,
        "planets": planet_shapes,
        "carrier": carrier_shape,
        "sun_pitch_r": sun_pitch_r,
        "sun_root_r": sun_root_r,
        "planet_center_r": planet_center_r,
        "planet_tip_r": planet_tip_r,
        "carrier_plate_top_z": carrier_z + plate_thickness,
        "sun_bottom_z": z_center - 0.5 * GEAR_WIDTH,
        "sun_top_z": z_center + 0.5 * GEAR_WIDTH,
    }


def nominal_stage_ratio(stage_cfg):
    return 1.0 + (stage_cfg["ring"] / float(stage_cfg["sun"]))


DOC = App.newDocument("TwoStagePlanetaryPlatform")
App.setActiveDocument(DOC.Name)

fixed_group = DOC.addObject("App::DocumentObjectGroup", "FixedHousing")
stage1_group = DOC.addObject("App::DocumentObjectGroup", "Stage1")
stage2_group = DOC.addObject("App::DocumentObjectGroup", "Stage2")
output_group = DOC.addObject("App::DocumentObjectGroup", "RotatingOutput")
bearing_elements_group = DOC.addObject("App::DocumentObjectGroup", "BearingRollingElements")

stage1_phase = math.radians(3.0)
stage2_phase = math.radians(7.0)

stage1_geom = build_stage_geometry(STAGES[0], stage1_phase)
stage2_geom = build_stage_geometry(STAGES[1], stage2_phase)

# Fixed ring gears are part of the fixed housing in both stages.
for idx, cfg in enumerate(STAGES):
    phase = stage1_phase if idx == 0 else stage2_phase
    ring_shape, _, root_r_inward, rim_outer_r = make_internal_ring_gear(
        module=cfg["module"],
        ring_teeth=cfg["ring"],
        width=GEAR_WIDTH,
        phase=phase,
    )
    ring_shape.translate(App.Vector(0.0, 0.0, cfg["z"] - 0.5 * GEAR_WIDTH))
    add_feature(fixed_group, f"{cfg['name']}_FixedRing", ring_shape, COLORS["fixed_light"])
    cfg["ring_root_r_inward"] = root_r_inward
    cfg["ring_outer_r"] = rim_outer_r

max_ring_outer = max(cfg["ring_outer_r"] for cfg in STAGES)
housing_wall_r = max_ring_outer + 6.0
housing_inner_clear_r = max_ring_outer + 1.0

base = Part.makeCylinder(housing_wall_r + 8.0, 8.0)
add_feature(fixed_group, "BasePlate", base, COLORS["fixed_dark"])

housing_shell = Part.makeCylinder(housing_wall_r, HOUSING_TOP_Z).cut(Part.makeCylinder(housing_inner_clear_r, HOUSING_TOP_Z))
housing_shell.translate(App.Vector(0.0, 0.0, 8.0))
add_feature(fixed_group, "HousingShell", housing_shell, COLORS["fixed_mid"], transparency=10)

# Input shaft + Stage 1 sun (sun input for stage 1).
input_shaft = Part.makeCylinder(2.0, STAGES[0]["z"] + 0.5 * GEAR_WIDTH)
stage1_input = stage1_geom["sun"].fuse(input_shaft)
add_feature(stage1_group, "Stage1_InputSunAndShaft", stage1_input, COLORS["shaft"])
for idx, pl_shape in enumerate(stage1_geom["planets"]):
    add_feature(stage1_group, f"Stage1_Planet_{idx+1}", pl_shape, COLORS["rotating_alt"])

# Real rigid compound coupling: Stage 1 carrier drives Stage 2 sun.
c12_start = stage1_geom["carrier_plate_top_z"] - 0.2
c12_end = stage2_geom["sun_bottom_z"] + 0.2
carrier1_to_sun2_connector = Part.makeCylinder(3.0, max(0.2, c12_end - c12_start))
carrier1_to_sun2_connector.translate(App.Vector(0.0, 0.0, c12_start))
stage12_compound = stage1_geom["carrier"].fuse(carrier1_to_sun2_connector).fuse(stage2_geom["sun"])
add_feature(stage2_group, "Stage1Carrier_to_Stage2Sun_Rigid", stage12_compound, COLORS["rotating"])
for idx, pl_shape in enumerate(stage2_geom["planets"]):
    add_feature(stage2_group, f"Stage2_Planet_{idx+1}", pl_shape, COLORS["rotating_alt"])

# Real rigid output coupling: Stage 2 carrier -> output hub -> top platform.
output_hub_base_z = stage2_geom["carrier_plate_top_z"] - 0.2
platform_z = HOUSING_TOP_Z + 8.0
output_hub_r = stage2_geom["planet_center_r"] + 0.55 * stage2_geom["planet_tip_r"]
output_hub = Part.makeCylinder(output_hub_r, (platform_z + PLATFORM_THICKNESS) - output_hub_base_z)
output_hub.translate(App.Vector(0.0, 0.0, output_hub_base_z))
platform = Part.makeCylinder(max_ring_outer + 12.0, PLATFORM_THICKNESS)
platform.translate(App.Vector(0.0, 0.0, platform_z))
stage2_output_compound = stage2_geom["carrier"].fuse(output_hub).fuse(platform)
add_feature(output_group, "Stage2Carrier_OutputHub_TopPlatform_Rigid", stage2_output_compound, COLORS["platform"])

# Annular output bearing depiction between fixed housing and rotating output.
bearing_z = HOUSING_TOP_Z - 12.0
bearing_inner_r = output_hub_r + 0.8
bearing_outer_r = bearing_inner_r + 5.8
bearing_height = 8.0
ball_r = 0.9
ball_center_r = bearing_inner_r + 3.0
inner_race_outer_r = ball_center_r - ball_r - 0.15
outer_race_inner_r = ball_center_r + ball_r + 0.15

fixed_race = Part.makeCylinder(bearing_outer_r, bearing_height).cut(Part.makeCylinder(outer_race_inner_r, bearing_height))
fixed_race.translate(App.Vector(0.0, 0.0, bearing_z))
add_feature(fixed_group, "OutputBearing_FixedOuterRace", fixed_race, COLORS["fixed_light"])

rotating_race_inner_r = max(0.5, output_hub_r - 0.6)
rotating_race = Part.makeCylinder(inner_race_outer_r, bearing_height).cut(Part.makeCylinder(rotating_race_inner_r, bearing_height))
rotating_race.translate(App.Vector(0.0, 0.0, bearing_z))
add_feature(output_group, "OutputBearing_RotatingInnerRace", rotating_race, COLORS["rotating"])

for idx in range(BEARING_BALL_COUNT):
    ball_angle = math.radians((360.0 / BEARING_BALL_COUNT) * idx)
    center = polar_xy(ball_center_r, ball_angle)
    ball = Part.makeSphere(ball_r)
    ball.translate(App.Vector(center.x, center.y, bearing_z + 0.5 * bearing_height))
    add_feature(bearing_elements_group, f"OutputBearing_Ball_{idx+1}", ball, (0.78, 0.80, 0.84))

DOC.recompute()

ratios = [nominal_stage_ratio(cfg) for cfg in STAGES]
overall_ratio = ratios[0] * ratios[1]

equal_spacing_value = (SUN_TEETH + RING_TEETH) / float(PLANET_COUNT)
print("Two-stage planetary concept generated.")
print("  Tooth check (R = S + 2P): {} = {} + 2*{}".format(RING_TEETH, SUN_TEETH, PLANET_TEETH))
print("  Equal-spacing check ((S+R)/N): {}/{} = {:.6f} (non-integer => phased slots used)".format(SUN_TEETH + RING_TEETH, PLANET_COUNT, equal_spacing_value))
print("  Mesh slot count: {}, slot angle: {:.1f} deg, chosen slots: {}".format(PLANET_MESH_SLOT_COUNT, math.degrees(PLANET_SLOT_ANGLE), PLANET_SLOT_INDICES))
for i, cfg in enumerate(STAGES):
    print(
        "  {}: m={:.2f}, S={}, P={}, R={}, nominal i={:.6f}:1".format(
            cfg["name"], cfg["module"], cfg["sun"], cfg["planet"], cfg["ring"], ratios[i]
        )
    )
print("  Overall nominal fixed-ring reduction (2-stage): {:.6f}:1".format(overall_ratio))

try:
    import FreeCADGui

    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except (ImportError, AttributeError):
    pass
