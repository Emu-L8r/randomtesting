# -*- coding: utf-8 -*-
"""
Rotary circular platform with a compound helical planetary gear concept.

Usage
-----
1. Install the FreeCAD Gears addon (Addon Manager: search for "Gears" / "FCGear").
2. Open FreeCAD.
3. Open this file as a macro (or paste it into the FreeCAD Python console).
4. Run it to generate a grouped assembly in a new document.

Design disclaimer
-----------------
This is a concept/visualization macro, not a production transmission design.
Validate load capacity, tooth strength, backlash, materials, tolerances,
bearing fits, and lubrication before fabrication.
"""

import math

import FreeCAD as App
import Part

try:
    from freecad.gears.commands import CreateInvoluteGear, CreateInternalInvoluteGear
except ImportError as exc:
    message = (
        "This macro requires the FreeCAD Gears addon. "
        "Install it via the Addon Manager (search for 'Gears' / 'FCGear') and retry."
    )
    App.Console.PrintError(message + "\n")
    raise RuntimeError(message) from exc


DOC = App.newDocument("CompoundPlanetaryPlatform")
App.setActiveDocument(DOC.Name)


# -------------------------
# Compound planetary choice
# -------------------------
# Lower power mesh uses the requested 9-tooth planet pinion.
# The second gear on each rigid compound planet intentionally uses a different
# tooth count so the planet body is truly compound rather than two identical gears.
#   sun_1 = 21, planet_1 = 9, ring_1 = 39
#   ring_1 = sun_1 + 2 * planet_1 = 21 + 18 = 39
#   (sun_1 + ring_1) / 6 = 60 / 6 = 10 -> equal 60° spacing is valid
# Upper transfer mesh uses the second, smaller-diameter member of the rigid compound
# planet pair to expose the next mesh interface without reintroducing the old stacked
# multi-stage train.
#   sun_2 = 18, planet_2 = 12, ring_2 = 42
#   ring_2 = sun_2 + 2 * planet_2 = 18 + 24 = 42
#   (sun_2 + ring_2) / 6 = 60 / 6 = 10 -> equal 60° spacing is valid
# Both meshes also share the same carrier pitch radius with a common module because:
#   sun_1 + planet_1 = 21 + 9 = 30
#   sun_2 + planet_2 = 18 + 12 = 30
# so both planet gears sit on the same six carrier pins.
MESH_PRIMARY = {"name": "Primary", "sun": 21, "planet": 9, "ring": 39}
MESH_TRANSFER = {"name": "Transfer", "sun": 18, "planet": 12, "ring": 42}
PLANET_COUNT = 6
HELIX_ANGLE_DEG = 22.0
MODULE_MM = 2.0
PRESSURE_ANGLE_DEG = 20.0
GEAR_HEIGHT_MM = 8.0
RING_HEIGHT_MM = 10.0
RING_RIM_THICKNESS_MM = 8.0
PLANET_AXLE_DIAMETER_MM = 5.0
PLANET_JOIN_SLEEVE_DIAMETER_MM = 12.0
INPUT_SHAFT_DIAMETER_MM = 8.0
OUTPUT_HUB_DIAMETER_MM = 58.0
PLATFORM_DIAMETER_MM = 128.0
PLATFORM_THICKNESS_MM = 10.0
BASE_THICKNESS_MM = 10.0
HOUSING_WALL_MM = 8.0
BEARING_HEIGHT_MM = 8.0
BEARING_RADIAL_WIDTH_MM = 7.0
BEARING_BALL_DIAMETER_MM = 4.0
BEARING_BALL_COUNT = 18
PRIMARY_Z0 = 16.0
TRANSFER_Z0 = PRIMARY_Z0 + GEAR_HEIGHT_MM + 8.0
CARRIER_PLATE_Z0 = TRANSFER_Z0 + GEAR_HEIGHT_MM + 3.0
CARRIER_PLATE_THICKNESS_MM = 6.0
PLATFORM_Z0 = CARRIER_PLATE_Z0 + CARRIER_PLATE_THICKNESS_MM + 22.0
HOUSING_TOP_Z = PLATFORM_Z0 + PLATFORM_THICKNESS_MM + 6.0

# FreeCAD Gears uses the sign of helix_angle to pick handedness. For parallel-axis
# helical meshes, the planets need the opposite hand from the mating sun/ring, so this
# macro keeps sun/ring/interface gears at +22° and mirrors the planet gears to -22°.
SUN_RING_HELIX_DEG = HELIX_ANGLE_DEG
PLANET_HELIX_DEG = -HELIX_ANGLE_DEG

COLORS = {
    "fixed_dark": (0.27, 0.30, 0.35),
    "fixed_mid": (0.39, 0.43, 0.48),
    "fixed_light": (0.56, 0.60, 0.66),
    "sun": (0.84, 0.60, 0.24),
    "planet_large": (0.93, 0.77, 0.34),
    "planet_small": (0.78, 0.57, 0.23),
    "carrier": (0.83, 0.84, 0.86),
    "platform": (0.89, 0.85, 0.79),
    "bearing": (0.78, 0.80, 0.84),
}


def set_color(obj, color, transparency=0):
    if hasattr(obj, "ViewObject"):
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.Transparency = transparency


def add_group(name):
    return DOC.addObject("App::DocumentObjectGroup", name)


FIXED_GROUP = add_group("FixedHousing")
SUN_GROUP = add_group("Sun")
COMPOUND_PLANETS_GROUP = add_group("CompoundPlanets")
CARRIER_GROUP = add_group("Carrier")
OUTPUT_GROUP = add_group("RotatingOutput")
BEARING_GROUP = add_group("BearingRollingElements")


def require(condition, message):
    if not condition:
        raise ValueError(message)


for mesh in (MESH_PRIMARY, MESH_TRANSFER):
    require(
        mesh["ring"] == mesh["sun"] + 2 * mesh["planet"],
        "{} mesh must satisfy ring = sun + 2 * planet".format(mesh["name"]),
    )
    equal_spacing_value = (mesh["sun"] + mesh["ring"]) / float(PLANET_COUNT)
    require(
        equal_spacing_value.is_integer(),
        "{} mesh must satisfy equal-spacing integer condition for {} planets".format(mesh["name"], PLANET_COUNT),
    )


PRIMARY_CENTER_RADIUS_MM = 0.5 * MODULE_MM * (MESH_PRIMARY["sun"] + MESH_PRIMARY["planet"])
TRANSFER_CENTER_RADIUS_MM = 0.5 * MODULE_MM * (MESH_TRANSFER["sun"] + MESH_TRANSFER["planet"])
require(
    abs(PRIMARY_CENTER_RADIUS_MM - TRANSFER_CENTER_RADIUS_MM) < 1e-9,
    "Primary and transfer meshes must share the same carrier radius.",
)
PLANET_CENTER_RADIUS_MM = PRIMARY_CENTER_RADIUS_MM
PLANET_ANGLES_RAD = [math.radians(60.0 * idx) for idx in range(PLANET_COUNT)]


def polar_xy(radius, angle_rad):
    return App.Vector(radius * math.cos(angle_rad), radius * math.sin(angle_rad), 0.0)


def mm_string(value):
    return "{:.3f} mm".format(float(value))


def deg_string(value):
    return "{:.3f} deg".format(float(value))


def set_first_supported_property(obj, names, value):
    properties = set(getattr(obj, "PropertiesList", []))
    last_error = None
    for name in names:
        if properties and name not in properties:
            continue
        try:
            setattr(obj, name, value)
            return name
        except Exception as exc:  # pragma: no cover - FreeCAD runtime compatibility path
            last_error = exc
    for name in names:
        try:
            setattr(obj, name, value)
            return name
        except Exception as exc:  # pragma: no cover - FreeCAD runtime compatibility path
            last_error = exc
    raise AttributeError(
        "Unable to set any of properties {} on {} ({})".format(names, obj.Name, last_error)
    )


def create_external_gear(name, teeth, helix_deg, height_mm, z0_mm, group, color, module_mm=MODULE_MM):
    gear = CreateInvoluteGear.create()
    gear.Label = name
    set_first_supported_property(gear, ["num_teeth", "teeth"], teeth)
    set_first_supported_property(gear, ["module", "modul"], mm_string(module_mm))
    set_first_supported_property(gear, ["height", "width"], mm_string(height_mm))
    set_first_supported_property(gear, ["pressure_angle"], deg_string(PRESSURE_ANGLE_DEG))
    set_first_supported_property(gear, ["helix_angle", "beta"], deg_string(helix_deg))
    set_first_supported_property(gear, ["double_helix"], False)
    if "properties_from_tool" in getattr(gear, "PropertiesList", []):
        gear.properties_from_tool = False
    DOC.recompute()
    gear.Placement = App.Placement(App.Vector(0.0, 0.0, z0_mm), App.Rotation())
    group.addObject(gear)
    set_color(gear, color)
    DOC.recompute()
    return gear


def create_internal_ring(name, teeth, height_mm, z0_mm, group, color, module_mm=MODULE_MM):
    ring = CreateInternalInvoluteGear.create()
    ring.Label = name
    set_first_supported_property(ring, ["num_teeth", "teeth"], teeth)
    set_first_supported_property(ring, ["module", "modul"], mm_string(module_mm))
    set_first_supported_property(ring, ["height", "width"], mm_string(height_mm))
    set_first_supported_property(ring, ["thickness"], mm_string(RING_RIM_THICKNESS_MM))
    set_first_supported_property(ring, ["pressure_angle"], deg_string(PRESSURE_ANGLE_DEG))
    set_first_supported_property(ring, ["helix_angle", "beta"], deg_string(SUN_RING_HELIX_DEG))
    set_first_supported_property(ring, ["double_helix"], False)
    if "properties_from_tool" in getattr(ring, "PropertiesList", []):
        ring.properties_from_tool = False
    DOC.recompute()
    ring.Placement = App.Placement(App.Vector(0.0, 0.0, z0_mm), App.Rotation())
    group.addObject(ring)
    set_color(ring, color, transparency=8)
    DOC.recompute()
    return ring


def add_shape_feature(container, name, shape, color, transparency=0):
    obj = DOC.addObject("Part::Feature", name)
    obj.Shape = shape
    container.addObject(obj)
    set_color(obj, color, transparency=transparency)
    return obj


PRIMARY_RING = create_internal_ring(
    name="PrimaryFixedRing",
    teeth=MESH_PRIMARY["ring"],
    height_mm=RING_HEIGHT_MM,
    z0_mm=PRIMARY_Z0 - 1.0,
    group=FIXED_GROUP,
    color=COLORS["fixed_light"],
)
TRANSFER_RING = create_internal_ring(
    name="TransferFixedRing",
    teeth=MESH_TRANSFER["ring"],
    height_mm=RING_HEIGHT_MM,
    z0_mm=TRANSFER_Z0 - 1.0,
    group=FIXED_GROUP,
    color=COLORS["fixed_light"],
)
INPUT_SUN = create_external_gear(
    name="InputSun",
    teeth=MESH_PRIMARY["sun"],
    helix_deg=SUN_RING_HELIX_DEG,
    height_mm=GEAR_HEIGHT_MM,
    z0_mm=PRIMARY_Z0,
    group=SUN_GROUP,
    color=COLORS["sun"],
)
TRANSFER_INTERFACE_SUN = create_external_gear(
    name="TransferInterfaceSun",
    teeth=MESH_TRANSFER["sun"],
    helix_deg=SUN_RING_HELIX_DEG,
    height_mm=GEAR_HEIGHT_MM,
    z0_mm=TRANSFER_Z0,
    group=SUN_GROUP,
    color=COLORS["sun"],
)


for index, theta in enumerate(PLANET_ANGLES_RAD, start=1):
    planet_part = DOC.addObject("App::Part", "CompoundPlanet_{:02d}".format(index))
    COMPOUND_PLANETS_GROUP.addObject(planet_part)
    center = polar_xy(PLANET_CENTER_RADIUS_MM, theta)
    planet_part.Placement = App.Placement(
        App.Vector(center.x, center.y, 0.0),
        App.Rotation(App.Vector(0.0, 0.0, 1.0), math.degrees(theta)),
    )

    primary_planet = create_external_gear(
        name="CompoundPlanet_{:02d}_PrimaryGear".format(index),
        teeth=MESH_PRIMARY["planet"],
        helix_deg=PLANET_HELIX_DEG,
        height_mm=GEAR_HEIGHT_MM,
        z0_mm=PRIMARY_Z0,
        group=planet_part,
        color=COLORS["planet_large"],
    )
    transfer_planet = create_external_gear(
        name="CompoundPlanet_{:02d}_TransferGear".format(index),
        teeth=MESH_TRANSFER["planet"],
        helix_deg=PLANET_HELIX_DEG,
        height_mm=GEAR_HEIGHT_MM,
        z0_mm=TRANSFER_Z0,
        group=planet_part,
        color=COLORS["planet_small"],
    )

    primary_planet.Placement = App.Placement(
        App.Vector(0.0, 0.0, PRIMARY_Z0),
        App.Rotation(
            App.Vector(0.0, 0.0, 1.0),
            -((MESH_PRIMARY["sun"] / float(MESH_PRIMARY["planet"])) + 1.0) * math.degrees(theta),
        ),
    )
    transfer_planet.Placement = App.Placement(
        App.Vector(0.0, 0.0, TRANSFER_Z0),
        App.Rotation(
            App.Vector(0.0, 0.0, 1.0),
            -((MESH_TRANSFER["sun"] / float(MESH_TRANSFER["planet"])) + 1.0) * math.degrees(theta),
        ),
    )

    axle = Part.makeCylinder(0.5 * PLANET_AXLE_DIAMETER_MM, CARRIER_PLATE_Z0 + CARRIER_PLATE_THICKNESS_MM - PRIMARY_Z0)
    axle.translate(App.Vector(0.0, 0.0, PRIMARY_Z0))
    add_shape_feature(
        planet_part,
        "CompoundPlanet_{:02d}_Axle".format(index),
        axle,
        COLORS["carrier"],
    )

    sleeve = Part.makeCylinder(0.5 * PLANET_JOIN_SLEEVE_DIAMETER_MM, TRANSFER_Z0 + GEAR_HEIGHT_MM - PRIMARY_Z0)
    sleeve.translate(App.Vector(0.0, 0.0, PRIMARY_Z0))
    add_shape_feature(
        planet_part,
        "CompoundPlanet_{:02d}_JoinSleeve".format(index),
        sleeve,
        COLORS["carrier"],
    )

planet_tip_radius_mm = 0.5 * MODULE_MM * (MESH_PRIMARY["planet"] + 2)
carrier_outer_radius_mm = PLANET_CENTER_RADIUS_MM + planet_tip_radius_mm + 10.0
carrier_inner_radius_mm = 0.5 * OUTPUT_HUB_DIAMETER_MM
carrier_plate = Part.makeCylinder(carrier_outer_radius_mm, CARRIER_PLATE_THICKNESS_MM)
carrier_plate = carrier_plate.cut(Part.makeCylinder(carrier_inner_radius_mm, CARRIER_PLATE_THICKNESS_MM))
carrier_plate.translate(App.Vector(0.0, 0.0, CARRIER_PLATE_Z0))
add_shape_feature(CARRIER_GROUP, "CarrierPlate", carrier_plate, COLORS["carrier"])

input_shaft = Part.makeCylinder(0.5 * INPUT_SHAFT_DIAMETER_MM, CARRIER_PLATE_Z0 + CARRIER_PLATE_THICKNESS_MM)
add_shape_feature(SUN_GROUP, "InputShaft", input_shaft, COLORS["sun"])

output_hub_height_mm = PLATFORM_Z0 - (CARRIER_PLATE_Z0 + CARRIER_PLATE_THICKNESS_MM)
output_hub = Part.makeCylinder(0.5 * OUTPUT_HUB_DIAMETER_MM, output_hub_height_mm)
output_hub.translate(App.Vector(0.0, 0.0, CARRIER_PLATE_Z0 + CARRIER_PLATE_THICKNESS_MM))
add_shape_feature(OUTPUT_GROUP, "OutputHub", output_hub, COLORS["platform"])

platform = Part.makeCylinder(0.5 * PLATFORM_DIAMETER_MM, PLATFORM_THICKNESS_MM)
platform.translate(App.Vector(0.0, 0.0, PLATFORM_Z0))
add_shape_feature(OUTPUT_GROUP, "TopPlatform", platform, COLORS["platform"])

max_ring_outer_radius_mm = 0.5 * MODULE_MM * max(MESH_PRIMARY["ring"], MESH_TRANSFER["ring"]) + RING_RIM_THICKNESS_MM
housing_outer_radius_mm = max_ring_outer_radius_mm + HOUSING_WALL_MM
housing_inner_radius_mm = max_ring_outer_radius_mm + 2.0

base_plate = Part.makeCylinder(housing_outer_radius_mm + 10.0, BASE_THICKNESS_MM)
add_shape_feature(FIXED_GROUP, "BasePlate", base_plate, COLORS["fixed_dark"])

housing_shell = Part.makeCylinder(housing_outer_radius_mm, HOUSING_TOP_Z - BASE_THICKNESS_MM)
housing_shell = housing_shell.cut(Part.makeCylinder(housing_inner_radius_mm, HOUSING_TOP_Z - BASE_THICKNESS_MM))
housing_shell.translate(App.Vector(0.0, 0.0, BASE_THICKNESS_MM))
add_shape_feature(FIXED_GROUP, "HousingShell", housing_shell, COLORS["fixed_mid"], transparency=15)

bearing_z0 = PLATFORM_Z0 - 12.0
bearing_inner_radius_mm = 0.5 * OUTPUT_HUB_DIAMETER_MM + 2.0
bearing_outer_radius_mm = bearing_inner_radius_mm + BEARING_RADIAL_WIDTH_MM
ball_radius_mm = 0.5 * BEARING_BALL_DIAMETER_MM
ball_center_radius_mm = 0.5 * (bearing_inner_radius_mm + bearing_outer_radius_mm)
inner_race_outer_radius_mm = ball_center_radius_mm - ball_radius_mm - 0.2
outer_race_inner_radius_mm = ball_center_radius_mm + ball_radius_mm + 0.2

fixed_race = Part.makeCylinder(bearing_outer_radius_mm, BEARING_HEIGHT_MM)
fixed_race = fixed_race.cut(Part.makeCylinder(outer_race_inner_radius_mm, BEARING_HEIGHT_MM))
fixed_race.translate(App.Vector(0.0, 0.0, bearing_z0))
add_shape_feature(FIXED_GROUP, "OutputBearing_FixedOuterRace", fixed_race, COLORS["fixed_light"])

rotating_race = Part.makeCylinder(inner_race_outer_radius_mm, BEARING_HEIGHT_MM)
rotating_race = rotating_race.cut(Part.makeCylinder(bearing_inner_radius_mm - 1.0, BEARING_HEIGHT_MM))
rotating_race.translate(App.Vector(0.0, 0.0, bearing_z0))
add_shape_feature(OUTPUT_GROUP, "OutputBearing_RotatingInnerRace", rotating_race, COLORS["carrier"])

for index in range(BEARING_BALL_COUNT):
    angle = math.radians((360.0 / BEARING_BALL_COUNT) * index)
    center = polar_xy(ball_center_radius_mm, angle)
    ball = Part.makeSphere(ball_radius_mm)
    ball.translate(App.Vector(center.x, center.y, bearing_z0 + 0.5 * BEARING_HEIGHT_MM))
    add_shape_feature(BEARING_GROUP, "OutputBearing_Ball_{:02d}".format(index + 1), ball, COLORS["bearing"])

DOC.recompute()

primary_ratio = 1.0 + (MESH_PRIMARY["ring"] / float(MESH_PRIMARY["sun"]))
transfer_ratio = 1.0 + (MESH_TRANSFER["ring"] / float(MESH_TRANSFER["sun"]))

print("Compound helical planetary concept generated.")
for mesh in (MESH_PRIMARY, MESH_TRANSFER):
    equal_spacing_value = (mesh["sun"] + mesh["ring"]) / float(PLANET_COUNT)
    print(
        "  {} mesh tooth check: R = S + 2P -> {} = {} + 2*{}".format(
            mesh["name"], mesh["ring"], mesh["sun"], mesh["planet"]
        )
    )
    print(
        "  {} mesh spacing check: (S + R) / N -> ({} + {}) / {} = {:.1f}".format(
            mesh["name"], mesh["sun"], mesh["ring"], PLANET_COUNT, equal_spacing_value
        )
    )
print("  Helix angle: +{:.1f}° sun/rings, {:.1f}° planets".format(SUN_RING_HELIX_DEG, PLANET_HELIX_DEG))
print("  Shared carrier pitch radius: {:.3f} mm".format(PLANET_CENTER_RADIUS_MM))
print("  Primary carrier-output reduction: {:.6f}:1".format(primary_ratio))
print("  Transfer interface simple-mesh equivalent: {:.6f}:1".format(transfer_ratio))
print(
    "  Output platform remains rigidly connected to the carrier while the upper 18/12/42 mesh is modeled as the compound-planet transfer interface."
)

try:
    import FreeCADGui

    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except (ImportError, AttributeError):
    pass
