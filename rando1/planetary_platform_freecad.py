# -*- coding: utf-8 -*-
"""
Rotary circular platform with a 3-stage compound planetary reduction (concept macro).

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

Stage data (module m, teeth S/P/R, nominal fixed-ring reduction i = 1 + R/S)
- Stage 1: m=1.8, S=18, P=18, R=54, i=4.000
- Stage 2: m=1.8, S=15, P=15, R=45, i=4.000
- Stage 3: m=1.8, S=12, P=12, R=36, i=4.000
Overall nominal reduction: 64:1
"""

import math
import FreeCAD as App
import Part


# -------------------------
# Parameters
# -------------------------
STAGES = [
    {"name": "Stage1", "module": 1.8, "sun": 18, "planet": 18, "z": 18.0},
    {"name": "Stage2", "module": 1.8, "sun": 15, "planet": 15, "z": 38.0},
    {"name": "Stage3", "module": 1.8, "sun": 12, "planet": 12, "z": 58.0},
]

for cfg in STAGES:
    cfg["ring"] = cfg["sun"] + 2 * cfg["planet"]

GEAR_WIDTH = 8.0
PLANET_CLEARANCE = 0.5
HOUSING_TOP_Z = 80.0
PLATFORM_THICKNESS = 10.0

COLORS = {
    "fixed_dark": (0.28, 0.31, 0.36),
    "fixed_mid": (0.40, 0.43, 0.48),
    "fixed_light": (0.55, 0.58, 0.62),
    "rotating": (0.82, 0.58, 0.26),
    "rotating_alt": (0.90, 0.72, 0.35),
    "shaft": (0.65, 0.50, 0.22),
    "platform": (0.88, 0.84, 0.78),
}


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
    for t in range(teeth):
        ang = phase + (2.0 * math.pi * t / teeth)
        tooth = Part.makeBox(tooth_depth, tooth_width, width)
        tooth.translate(App.Vector(root_r, -0.5 * tooth_width, 0.0))
        tooth.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), math.degrees(ang))
        gear_shape = gear_shape.fuse(tooth)

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

    for t in range(ring_teeth):
        ang = phase + (2.0 * math.pi * t / ring_teeth)
        slot = Part.makeBox(slot_depth, slot_width, width + 0.2)
        slot.translate(App.Vector(tip_r_inward, -0.5 * slot_width, -0.1))
        slot.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), math.degrees(ang))
        ring_shape = ring_shape.cut(slot)

    return ring_shape, pitch_r, root_r_inward, rim_outer_r


def make_carrier(planet_center_r, planet_tip_r, width, sun_root_r):
    plate_thickness = width * 0.45
    outer_r = planet_center_r + 0.72 * planet_tip_r
    inner_r = max(2.5, sun_root_r + 1.0)

    plate = Part.makeCylinder(outer_r, plate_thickness).cut(Part.makeCylinder(inner_r, plate_thickness))

    pin_r = 1.5
    pin_h = width + 2.0
    for idx in range(3):
        ang = math.radians(120.0 * idx)
        center = polar_xy(planet_center_r, ang)
        pin = Part.makeCylinder(pin_r, pin_h)
        pin.translate(App.Vector(center.x, center.y, -1.0))
        plate = plate.fuse(pin)

    return plate


def make_stage_rotating_members(stage_cfg, group, phase):
    module = stage_cfg["module"]
    sun_teeth = stage_cfg["sun"]
    planet_teeth = stage_cfg["planet"]
    z_center = stage_cfg["z"]

    sun_shape, sun_pitch_r, sun_root_r, _ = make_external_gear(
        module=module,
        teeth=sun_teeth,
        width=GEAR_WIDTH,
        phase=phase,
        bore_radius=2.2,
    )
    sun_shape.translate(App.Vector(0.0, 0.0, z_center - 0.5 * GEAR_WIDTH))
    add_feature(group, f"{stage_cfg['name']}_Sun", sun_shape, COLORS["rotating"])

    planet_shape_proto, planet_pitch_r, _, planet_tip_r = make_external_gear(
        module=module,
        teeth=planet_teeth,
        width=GEAR_WIDTH,
        phase=-phase * (sun_teeth / float(planet_teeth)),
        bore_radius=1.8,
    )

    planet_center_r = sun_pitch_r + planet_pitch_r
    for idx in range(3):
        ang = math.radians(120.0 * idx + 15.0)
        offset = polar_xy(planet_center_r, ang)
        pl_shape = planet_shape_proto.copy()
        pl_shape.translate(App.Vector(offset.x, offset.y, z_center - 0.5 * GEAR_WIDTH))
        add_feature(group, f"{stage_cfg['name']}_Planet_{idx+1}", pl_shape, COLORS["rotating_alt"])

    carrier_shape = make_carrier(
        planet_center_r=planet_center_r,
        planet_tip_r=planet_tip_r,
        width=GEAR_WIDTH,
        sun_root_r=sun_root_r,
    )
    carrier_shape.translate(App.Vector(0.0, 0.0, z_center + 0.5 * GEAR_WIDTH + PLANET_CLEARANCE))
    add_feature(group, f"{stage_cfg['name']}_Carrier", carrier_shape, COLORS["shaft"])

    stage_cfg["sun_pitch_r"] = sun_pitch_r
    stage_cfg["planet_pitch_r"] = planet_pitch_r
    stage_cfg["planet_center_r"] = planet_center_r
    stage_cfg["planet_tip_r"] = planet_tip_r


def add_ring_to_housing(stage_cfg, group, phase):
    ring_shape, _, root_r_inward, rim_outer_r = make_internal_ring_gear(
        module=stage_cfg["module"],
        ring_teeth=stage_cfg["ring"],
        width=GEAR_WIDTH,
        phase=phase,
    )
    ring_shape.translate(App.Vector(0.0, 0.0, stage_cfg["z"] - 0.5 * GEAR_WIDTH))
    add_feature(group, f"{stage_cfg['name']}_FixedRing", ring_shape, COLORS["fixed_light"])

    stage_cfg["ring_root_r_inward"] = root_r_inward
    stage_cfg["ring_outer_r"] = rim_outer_r


def add_coupler(group, name, z_start, z_end, radius):
    height = max(0.2, z_end - z_start)
    shape = Part.makeCylinder(radius, height)
    shape.translate(App.Vector(0.0, 0.0, z_start))
    add_feature(group, name, shape, COLORS["shaft"])


def nominal_stage_ratio(stage_cfg):
    return 1.0 + (stage_cfg["ring"] / float(stage_cfg["sun"]))


DOC = App.newDocument("ThreeStagePlanetaryPlatform")
App.setActiveDocument(DOC.Name)

fixed_group = DOC.addObject("App::DocumentObjectGroup", "FixedHousing")
stage1_group = DOC.addObject("App::DocumentObjectGroup", "Stage1")
stage2_group = DOC.addObject("App::DocumentObjectGroup", "Stage2")
stage3_group = DOC.addObject("App::DocumentObjectGroup", "Stage3")
output_group = DOC.addObject("App::DocumentObjectGroup", "RotatingOutput")
bearing_elements_group = DOC.addObject("App::DocumentObjectGroup", "BearingRollingElements")

stage_groups = [stage1_group, stage2_group, stage3_group]

for i, cfg in enumerate(STAGES):
    phase = (i + 1) * math.radians(4.0)
    add_ring_to_housing(cfg, fixed_group, phase=phase)
    make_stage_rotating_members(cfg, stage_groups[i], phase=phase)

max_ring_outer = max(cfg["ring_outer_r"] for cfg in STAGES)
housing_wall_r = max_ring_outer + 6.0
housing_inner_clear_r = max_ring_outer + 1.0

base = Part.makeCylinder(housing_wall_r + 8.0, 8.0)
add_feature(fixed_group, "BasePlate", base, COLORS["fixed_dark"])

housing_shell = Part.makeCylinder(housing_wall_r, HOUSING_TOP_Z).cut(Part.makeCylinder(housing_inner_clear_r, HOUSING_TOP_Z))
housing_shell.translate(App.Vector(0.0, 0.0, 8.0))
add_feature(fixed_group, "HousingShell", housing_shell, COLORS["fixed_mid"], transparency=10)

# Input shaft drives Stage 1 sun
input_shaft = Part.makeCylinder(2.0, STAGES[0]["z"] + 0.5 * GEAR_WIDTH)
add_feature(stage1_group, "InputShaft", input_shaft, COLORS["shaft"])

# Compound couplers: Stage1 carrier -> Stage2 sun, Stage2 carrier -> Stage3 sun
z1_carrier_top = STAGES[0]["z"] + 0.5 * GEAR_WIDTH + PLANET_CLEARANCE + (GEAR_WIDTH * 0.45)
z2_sun_bottom = STAGES[1]["z"] - 0.5 * GEAR_WIDTH
z2_carrier_top = STAGES[1]["z"] + 0.5 * GEAR_WIDTH + PLANET_CLEARANCE + (GEAR_WIDTH * 0.45)
z3_sun_bottom = STAGES[2]["z"] - 0.5 * GEAR_WIDTH

add_coupler(stage1_group, "Carrier1_to_Sun2_Coupler", z1_carrier_top - 0.2, z2_sun_bottom + 0.2, 2.8)
add_coupler(stage2_group, "Carrier2_to_Sun3_Coupler", z2_carrier_top - 0.2, z3_sun_bottom + 0.2, 2.6)

# Output hub + platform rigid to Stage 3 carrier
z3_carrier_top = STAGES[2]["z"] + 0.5 * GEAR_WIDTH + PLANET_CLEARANCE + (GEAR_WIDTH * 0.45)
output_hub_base_z = z3_carrier_top - 0.2
bearing_z = HOUSING_TOP_Z - 12.0
platform_z = HOUSING_TOP_Z + 8.0

output_hub_r = STAGES[2]["planet_center_r"] + 0.55 * STAGES[2]["planet_tip_r"]
output_hub = Part.makeCylinder(output_hub_r, platform_z - output_hub_base_z)
output_hub.translate(App.Vector(0.0, 0.0, output_hub_base_z))
add_feature(output_group, "OutputHub", output_hub, COLORS["shaft"])

platform = Part.makeCylinder(max_ring_outer + 12.0, PLATFORM_THICKNESS)
platform.translate(App.Vector(0.0, 0.0, platform_z))
add_feature(output_group, "TopPlatform", platform, COLORS["platform"])

# Annular output bearing / race depiction between fixed housing and rotating output
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

for idx in range(14):
    ball_angle = math.radians((360.0 / 14.0) * idx)
    center = polar_xy(ball_center_r, ball_angle)
    ball = Part.makeSphere(ball_r)
    ball.translate(App.Vector(center.x, center.y, bearing_z + 0.5 * bearing_height))
    add_feature(bearing_elements_group, f"OutputBearing_Ball_{idx+1}", ball, (0.78, 0.80, 0.84))

DOC.recompute()

ratios = [nominal_stage_ratio(cfg) for cfg in STAGES]
overall_ratio = ratios[0] * ratios[1] * ratios[2]
print("Three-stage planetary concept generated.")
for i, cfg in enumerate(STAGES):
    print(
        "  {}: m={:.2f}, S={}, P={}, R={}, nominal i={:.3f}:1".format(
            cfg["name"], cfg["module"], cfg["sun"], cfg["planet"], cfg["ring"], ratios[i]
        )
    )
print("  Overall nominal fixed-ring reduction: {:.3f}:1".format(overall_ratio))

try:
    import FreeCADGui

    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except Exception:
    pass
