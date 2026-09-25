# -*- coding: utf-8 -*-
# FreeCAD macro: three-stage planetary gear platform
#
# Usage:
#   1. Open FreeCAD.
#   2. Open this file as a macro or paste into the Python console.
#   3. The script builds a circular top platform with a three-stage planetary gear
#      assembly underneath.
#
# This is a concept model intended for quick visualization and iteration.

import math
import FreeCAD as App
import Part


def make_cylinder(name, radius, height, center=(0, 0, 0), color=(0.55, 0.57, 0.60)):
    obj = App.ActiveDocument.addObject("Part::Cylinder", name)
    obj.Radius = radius
    obj.Height = height
    obj.Placement = App.Placement(App.Vector(*center), App.Rotation())
    obj.ViewObject.ShapeColor = color
    return obj


def make_ring(name, outer_radius, inner_radius, height, center=(0, 0, 0), color=(0.58, 0.60, 0.63)):
    outer = Part.makeCylinder(outer_radius, height)
    inner = Part.makeCylinder(inner_radius, height + 2)
    ring = outer.cut(inner)
    feat = App.ActiveDocument.addObject("Part::Feature", name)
    feat.Shape = ring
    feat.Placement = App.Placement(App.Vector(*center), App.Rotation())
    feat.ViewObject.ShapeColor = color
    return feat


def add_support_arms(prefix, z_center, arm_length, arm_thickness, color):
    for i in range(3):
        angle = math.radians(120 * i)
        x = math.cos(angle) * arm_length * 0.55
        y = math.sin(angle) * arm_length * 0.55
        arm = App.ActiveDocument.addObject("Part::Box", f"{prefix}_Arm_{i}")
        arm.Length = arm_length
        arm.Width = arm_thickness
        arm.Height = 10
        arm.Placement = App.Placement(
            App.Vector(x, y, z_center),
            App.Rotation(App.Vector(0, 0, 1), math.degrees(angle) + 90),
        )
        arm.ViewObject.ShapeColor = color


def make_stage(prefix, z_center, ring_outer, ring_inner, sun_radius, planet_radius, stage_height, planet_offset, color_ring, color_sun, color_planet):
    ring = make_ring(
        f"{prefix}_Ring",
        outer_radius=ring_outer,
        inner_radius=ring_inner,
        height=stage_height,
        center=(0, 0, z_center),
        color=color_ring,
    )

    sun = make_cylinder(
        f"{prefix}_Sun",
        radius=sun_radius,
        height=stage_height + 4,
        center=(0, 0, z_center),
        color=color_sun,
    )

    for i in range(3):
        angle = math.radians(120 * i + 30)
        x = math.cos(angle) * planet_offset
        y = math.sin(angle) * planet_offset
        gear = make_cylinder(
            f"{prefix}_Planet_{i}",
            radius=planet_radius,
            height=stage_height + 5,
            center=(x, y, z_center),
            color=color_planet,
        )

    carrier = make_cylinder(
        f"{prefix}_Carrier",
        radius=planet_offset * 0.55,
        height=8,
        center=(0, 0, z_center),
        color=(0.42, 0.43, 0.46),
    )

    return ring, sun, carrier


# -----------------------------------------------------------------------------
# Create document
# -----------------------------------------------------------------------------
doc = App.newDocument("ThreeStagePlanetaryPlatform")
App.setActiveDocument("ThreeStagePlanetaryPlatform")
App.ActiveDocument = doc

# -----------------------------------------------------------------------------
# Main platform and support structure
# -----------------------------------------------------------------------------
platform = make_cylinder(
    "TopPlatform",
    radius=110,
    height=14,
    center=(0, 0, 118),
    color=(0.76, 0.77, 0.80),
)

hub = make_cylinder(
    "TopHub",
    radius=28,
    height=60,
    center=(0, 0, 88),
    color=(0.51, 0.52, 0.55),
)

center_column = make_cylinder(
    "CenterColumn",
    radius=16,
    height=120,
    center=(0, 0, 52),
    color=(0.44, 0.46, 0.49),
)

# A slight central bore to make the shaft more realistic
center_bore = make_cylinder(
    "CenterColumnBore",
    radius=6,
    height=130,
    center=(0, 0, 52),
    color=(0.18, 0.18, 0.18),
)
center_column.Shape = center_column.Shape.cut(center_bore.Shape)

# -----------------------------------------------------------------------------
# Stacked planetary gear stages
# -----------------------------------------------------------------------------
# Stage 1: largest ring gear set, highest in the assembly
make_stage(
    prefix="Stage1",
    z_center=66,
    ring_outer=80,
    ring_inner=60,
    sun_radius=18,
    planet_radius=16,
    stage_height=15,
    planet_offset=42,
    color_ring=(0.68, 0.70, 0.72),
    color_sun=(0.84, 0.85, 0.87),
    color_planet=(0.74, 0.75, 0.78),
)

# Stage 2: smaller and lower
make_stage(
    prefix="Stage2",
    z_center=38,
    ring_outer=62,
    ring_inner=44,
    sun_radius=13,
    planet_radius=11,
    stage_height=13,
    planet_offset=30,
    color_ring=(0.62, 0.64, 0.67),
    color_sun=(0.79, 0.80, 0.82),
    color_planet=(0.69, 0.70, 0.73),
)

# Stage 3: smallest ring set near the base
make_stage(
    prefix="Stage3",
    z_center=10,
    ring_outer=46,
    ring_inner=30,
    sun_radius=9,
    planet_radius=8,
    stage_height=11,
    planet_offset=20,
    color_ring=(0.58, 0.60, 0.62),
    color_sun=(0.74, 0.75, 0.78),
    color_planet=(0.64, 0.65, 0.68),
)

# Additional structural supports between stages
add_support_arms("StageSpokes1", z_center=52, arm_length=70, arm_thickness=7, color=(0.46, 0.48, 0.50))
add_support_arms("StageSpokes2", z_center=24, arm_length=50, arm_thickness=6, color=(0.40, 0.42, 0.45))

# Base pedestal under the gear stack
base_disk = make_cylinder(
    "BaseDisk",
    radius=92,
    height=12,
    center=(0, 0, -10),
    color=(0.54, 0.56, 0.60),
)

base_ring = make_ring(
    "BaseRing",
    outer_radius=90,
    inner_radius=36,
    height=18,
    center=(0, 0, -22),
    color=(0.45, 0.47, 0.50),
)

# A few stabilizer feet
for angle in [0, 90, 180, 270]:
    x = math.cos(math.radians(angle)) * 58
    y = math.sin(math.radians(angle)) * 58
    foot = App.ActiveDocument.addObject("Part::Cylinder", f"Leg_{angle}")
    foot.Radius = 8
    foot.Height = 18
    foot.Placement = App.Placement(App.Vector(x, y, -30), App.Rotation())
    foot.ViewObject.ShapeColor = (0.30, 0.31, 0.33)

# -----------------------------------------------------------------------------
# Finalize and fit view
# -----------------------------------------------------------------------------
App.ActiveDocument.recompute()

try:
    import FreeCADGui
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except Exception:
    pass

print("Three-stage planetary gear platform created successfully.")
