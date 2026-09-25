# -*- coding: utf-8 -*-
"""
Two-stage parametric planetary gearbox generator for FreeCAD.

Run inside FreeCAD with the FreeCAD Gears addon installed:
  - FreeCAD GUI Python console / macro runner
  - FreeCADCmd for headless execution
  - some installations also support passing the script to the GUI-capable `freecad` launcher
"""

import math
import os
import sys


def fail(message):
    try:
        import FreeCAD as _App  # pragma: no cover - only available in FreeCAD runtime

        _App.Console.PrintError(message + "\n")
    except Exception:
        sys.stderr.write(message + "\n")
    raise SystemExit(1)


try:
    import FreeCAD as App
    import Part
except ImportError:
    fail(
        "This script must be run inside FreeCAD (for example with FreeCADCmd or "
        "from the FreeCAD GUI Python console / macro runner; some installations "
        "also accept the script via the `freecad` launcher)."
    )

try:
    from freecad.gears.commands import CreateInvoluteGear, CreateInternalInvoluteGear
except ImportError:
    fail(
        "This script requires the FreeCAD Gears / FCGear addon. Install it from "
        "FreeCAD's Addon Manager and rerun the script."
    )


DOC_NAME = "TwoStagePlanetaryGearbox"
SCRIPT_DIR = (
    os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
)
SAVE_PATH = os.path.join(SCRIPT_DIR, "planetary_gearbox.FCStd")

# -----------------
# User parameters
# -----------------
MODULE_MM = 1.0
PRESSURE_ANGLE_DEG = 20.0
NUM_PLANETS = 3
GEAR_HEIGHT_MM = 8.0
RING_HEIGHT_MM = 10.0
RING_RIM_THICKNESS_MM = 7.0
SUN_BORE_DIA_MM = 8.0
PLANET_PIN_DIA_MM = 2.4
CARRIER_PLATE_THICKNESS_MM = 5.0
CARRIER_MARGIN_MM = 5.0
INTERSTAGE_GAP_MM = 8.0
STAGE_SPACING_MM = GEAR_HEIGHT_MM + CARRIER_PLATE_THICKNESS_MM + INTERSTAGE_GAP_MM

# Requirement 1: exact 5:1 overall reduction using two fixed-ring planetary stages.
# Stage 1 ratio = 1 + R1 / S1 = 1 + 90 / 72 = 9/4 = 2.25
# Stage 2 ratio = 1 + R2 / S2 = 1 + 99 / 81 = 20/9 = 2.222222...
# Overall ratio = (9/4) * (20/9) = 5 exactly
STAGE_1 = {"sun": 72, "planet": 9, "ring": 90}
STAGE_2 = {"sun": 81, "planet": 9, "ring": 99}

COLORS = {
    "sun": (0.92, 0.67, 0.22),
    "planet": (0.88, 0.80, 0.38),
    "ring": (0.52, 0.60, 0.68),
    "carrier": (0.80, 0.83, 0.88),
    "shaft": (0.65, 0.67, 0.72),
}


def mm_string(value):
    return "{:.3f} mm".format(float(value))



def deg_string(value):
    return "{:.3f} deg".format(float(value))



def quantity_mm(value):
    if hasattr(value, "Value"):
        return float(value.Value)
    return float(str(value).split()[0])



def set_color(obj, color, transparency=0):
    if hasattr(obj, "ViewObject"):
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.Transparency = transparency



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



def hide_if_possible(obj):
    if hasattr(obj, "ViewObject"):
        obj.ViewObject.Visibility = False



def add_group(doc, name, parent=None):
    group = doc.addObject("App::DocumentObjectGroup", name)
    if parent is not None:
        parent.addObject(group)
    return group



def add_shape_feature(doc, group, name, shape, color, transparency=0):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    group.addObject(obj)
    set_color(obj, color, transparency=transparency)
    return obj



def validate_stage(stage_name, sun_teeth, planet_teeth, ring_teeth, num_planets):
    if ring_teeth != sun_teeth + 2 * planet_teeth:
        raise ValueError(
            "{} must satisfy ring = sun + 2 * planet ({} != {} + 2*{})".format(
                stage_name, ring_teeth, sun_teeth, planet_teeth
            )
        )
    spacing_value = (sun_teeth + ring_teeth) / float(num_planets)
    if not spacing_value.is_integer():
        raise ValueError(
            "{} must satisfy (sun + ring) / planets being an integer for equal spacing".format(
                stage_name
            )
        )
    return int(spacing_value)



def create_external_gear(doc, group, name, teeth, module_mm, pressure_angle_deg, height_mm, placement, color):
    # Requirement 4: generate real involute gears via the FreeCAD Gears addon.
    gear = CreateInvoluteGear.create()
    gear.Label = name
    set_first_supported_property(gear, ["num_teeth", "teeth"], teeth)
    set_first_supported_property(gear, ["module", "modul"], mm_string(module_mm))
    set_first_supported_property(gear, ["height", "width"], mm_string(height_mm))
    set_first_supported_property(gear, ["pressure_angle"], deg_string(pressure_angle_deg))
    set_first_supported_property(gear, ["double_helix"], False)
    if "properties_from_tool" in getattr(gear, "PropertiesList", []):
        gear.properties_from_tool = False
    doc.recompute()
    gear.Placement = placement
    group.addObject(gear)
    set_color(gear, color)
    doc.recompute()
    return gear



def create_internal_ring(doc, group, name, teeth, module_mm, pressure_angle_deg, height_mm, z_offset, color):
    # Requirement 4: ring gear also comes from the FreeCAD Gears addon as an internal involute gear.
    ring = CreateInternalInvoluteGear.create()
    ring.Label = name
    set_first_supported_property(ring, ["num_teeth", "teeth"], teeth)
    set_first_supported_property(ring, ["module", "modul"], mm_string(module_mm))
    set_first_supported_property(ring, ["height", "width"], mm_string(height_mm))
    set_first_supported_property(ring, ["thickness"], mm_string(RING_RIM_THICKNESS_MM))
    set_first_supported_property(ring, ["pressure_angle"], deg_string(pressure_angle_deg))
    set_first_supported_property(ring, ["double_helix"], False)
    if "properties_from_tool" in getattr(ring, "PropertiesList", []):
        ring.properties_from_tool = False
    doc.recompute()
    ring.Placement = App.Placement(App.Vector(0.0, 0.0, z_offset), App.Rotation())
    group.addObject(ring)
    set_color(ring, color, transparency=10)
    doc.recompute()
    return ring



def create_bored_gear(doc, group, gear, name, bore_dia, z_offset, height_mm, color):
    # Requirement 5 and 6: bores are made by boolean-cutting a real gear body with a cylinder.
    bore = doc.addObject("Part::Cylinder", name + "_BoreTool")
    bore.Radius = 0.5 * bore_dia
    bore.Height = height_mm + 2.0
    bore.Placement = App.Placement(
        App.Vector(gear.Placement.Base.x, gear.Placement.Base.y, z_offset - 1.0),
        App.Rotation(),
    )
    group.addObject(bore)

    cut = doc.addObject("Part::Cut", name)
    cut.Base = gear
    cut.Tool = bore
    group.addObject(cut)
    doc.recompute()
    set_color(cut, color)
    hide_if_possible(gear)
    hide_if_possible(bore)
    return cut, bore



def create_stage(doc, stage_name, z_offset, sun_teeth, planet_teeth, ring_teeth, num_planets, module, pressure_angle, gear_height, bore_dia, pin_dia):
    stage_group = add_group(doc, stage_name)
    spacing_index = validate_stage(stage_name, sun_teeth, planet_teeth, ring_teeth, num_planets)

    pitch_radius_sun = 0.5 * module * sun_teeth
    pitch_radius_planet = 0.5 * module * planet_teeth
    pitch_radius_ring = 0.5 * module * ring_teeth
    center_distance = 0.5 * module * (sun_teeth + planet_teeth)
    planet_outer_radius = 0.5 * module * (planet_teeth + 2.0)
    carrier_outer_radius = center_distance + planet_outer_radius + CARRIER_MARGIN_MM
    carrier_hub_radius = max(bore_dia, 2.5 * pin_dia)

    # Requirement 7: center distance and tooth counts are computed from one common module so the stage meshes correctly.
    ring = create_internal_ring(
        doc,
        stage_group,
        stage_name + "_Ring",
        ring_teeth,
        module,
        pressure_angle,
        RING_HEIGHT_MM,
        z_offset - 1.0,
        COLORS["ring"],
    )

    sun_base = create_external_gear(
        doc,
        stage_group,
        stage_name + "_SunBase",
        sun_teeth,
        module,
        pressure_angle,
        gear_height,
        App.Placement(App.Vector(0.0, 0.0, z_offset), App.Rotation()),
        COLORS["sun"],
    )
    sun, _sun_bore = create_bored_gear(
        doc,
        stage_group,
        sun_base,
        stage_name + "_Sun",
        bore_dia,
        z_offset,
        gear_height,
        COLORS["sun"],
    )

    planet_group = add_group(doc, stage_name + "_Planets", parent=stage_group)
    planets = []
    planet_bores = []
    planet_pin_locations = []
    for planet_index in range(num_planets):
        angle_rad = (2.0 * math.pi * spacing_index * planet_index) / float(sun_teeth + ring_teeth)
        angle_deg = math.degrees(angle_rad)
        center = App.Vector(
            center_distance * math.cos(angle_rad),
            center_distance * math.sin(angle_rad),
            z_offset,
        )
        # Requirement 7: phase each planet with the sun using the actual tooth-count ratio.
        spin_deg = -(sun_teeth / float(planet_teeth)) * angle_deg
        placement = App.Placement(center, App.Rotation(App.Vector(0.0, 0.0, 1.0), spin_deg))
        planet_base = create_external_gear(
            doc,
            planet_group,
            "{}_Planet{:02d}_Base".format(stage_name, planet_index + 1),
            planet_teeth,
            module,
            pressure_angle,
            gear_height,
            placement,
            COLORS["planet"],
        )
        planet, planet_bore = create_bored_gear(
            doc,
            planet_group,
            planet_base,
            "{}_Planet{:02d}".format(stage_name, planet_index + 1),
            pin_dia,
            z_offset,
            gear_height,
            COLORS["planet"],
        )
        planets.append(planet)
        planet_bores.append(planet_bore)
        planet_pin_locations.append((center.x, center.y))

    # Requirement 6: the carrier is a disc plus cylindrical pins on the planet circle.
    plate_bottom_z = z_offset - CARRIER_PLATE_THICKNESS_MM - 1.0
    plate = Part.makeCylinder(carrier_outer_radius, CARRIER_PLATE_THICKNESS_MM)
    plate.translate(App.Vector(0.0, 0.0, plate_bottom_z))
    hub = Part.makeCylinder(carrier_hub_radius, CARRIER_PLATE_THICKNESS_MM + 2.0)
    hub.translate(App.Vector(0.0, 0.0, plate_bottom_z))
    carrier_shape = plate.fuse(hub)
    pin_height = gear_height + CARRIER_PLATE_THICKNESS_MM + 2.0
    for pin_x, pin_y in planet_pin_locations:
        pin = Part.makeCylinder(0.5 * pin_dia, pin_height)
        pin.translate(App.Vector(pin_x, pin_y, plate_bottom_z))
        carrier_shape = carrier_shape.fuse(pin)
    carrier = add_shape_feature(doc, stage_group, stage_name + "_Carrier", carrier_shape, COLORS["carrier"])

    doc.recompute()
    return {
        "group": stage_group,
        "sun": sun,
        "planets": planets,
        "planet_bores": planet_bores,
        "ring": ring,
        "carrier": carrier,
        "center_distance": center_distance,
        "plate_top_z": plate_bottom_z + CARRIER_PLATE_THICKNESS_MM,
        "hub_top_z": plate_bottom_z + CARRIER_PLATE_THICKNESS_MM + 2.0,
        "carrier_top_z": plate_bottom_z + pin_height,
        "sun_base_z": z_offset,
        "sun_top_z": z_offset + gear_height,
        "pitch_radius_ring": pitch_radius_ring,
        "pitch_radius_sun": pitch_radius_sun,
        "pitch_radius_planet": pitch_radius_planet,
    }



def main():
    doc = App.newDocument(DOC_NAME)
    App.setActiveDocument(doc.Name)

    # Requirement 2 and 3: two planetary stages share one axis, with stage 1 carrier driving stage 2 sun.
    stage_1 = create_stage(
        doc,
        "Stage1",
        0.0,
        STAGE_1["sun"],
        STAGE_1["planet"],
        STAGE_1["ring"],
        NUM_PLANETS,
        MODULE_MM,
        PRESSURE_ANGLE_DEG,
        GEAR_HEIGHT_MM,
        SUN_BORE_DIA_MM,
        PLANET_PIN_DIA_MM,
    )
    stage_2 = create_stage(
        doc,
        "Stage2",
        STAGE_SPACING_MM,
        STAGE_2["sun"],
        STAGE_2["planet"],
        STAGE_2["ring"],
        NUM_PLANETS,
        MODULE_MM,
        PRESSURE_ANGLE_DEG,
        GEAR_HEIGHT_MM,
        SUN_BORE_DIA_MM,
        PLANET_PIN_DIA_MM,
    )

    interstage_group = add_group(doc, "InterstageDrive")
    coupler_height = max(2.0, stage_2["sun_top_z"] - stage_1["hub_top_z"])
    coupler = Part.makeCylinder(0.5 * SUN_BORE_DIA_MM, coupler_height)
    coupler.translate(App.Vector(0.0, 0.0, stage_1["hub_top_z"]))
    add_shape_feature(doc, interstage_group, "Stage1CarrierToStage2SunCoupler", coupler, COLORS["shaft"])

    # Requirement 1: report the exact fixed-ring reduction math in the model-generation output.
    stage_1_ratio = 1.0 + (STAGE_1["ring"] / float(STAGE_1["sun"]))
    stage_2_ratio = 1.0 + (STAGE_2["ring"] / float(STAGE_2["sun"]))
    total_ratio = stage_1_ratio * stage_2_ratio

    doc.recompute()

    print("Generated two-stage planetary gearbox document: {}".format(doc.Name))
    print("  Stage 1 teeth (sun / planet / ring): {sun} / {planet} / {ring}".format(**STAGE_1))
    print("  Stage 2 teeth (sun / planet / ring): {sun} / {planet} / {ring}".format(**STAGE_2))
    print("  Stage 1 ratio = 1 + {ring}/{sun} = {:.6f}:1".format(stage_1_ratio, **STAGE_1))
    print("  Stage 2 ratio = 1 + {ring}/{sun} = {:.6f}:1".format(stage_2_ratio, **STAGE_2))
    print("  Overall reduction = {:.6f}:1".format(total_ratio))
    print("  Shared module = {:.3f} mm, pressure angle = {:.1f} deg".format(MODULE_MM, PRESSURE_ANGLE_DEG))
    print("  Stage 1 planet center distance = {:.3f} mm".format(stage_1["center_distance"]))
    print("  Stage 2 planet center distance = {:.3f} mm".format(stage_2["center_distance"]))

    try:
        doc.saveAs(SAVE_PATH)
        print("  Saved FreeCAD document to {}".format(SAVE_PATH))
    except Exception as exc:  # pragma: no cover - save can fail in restricted/headless runs
        print("  Skipped saveAs: {}".format(exc))

    try:
        import FreeCADGui  # pragma: no cover - GUI only

        FreeCADGui.ActiveDocument.ActiveView.fitAll()
    except Exception:
        pass


if __name__ == "__main__":
    main()
