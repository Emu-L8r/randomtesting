# -*- coding: utf-8 -*-
# Pan-tilt robot model for FreeCAD
#
# Usage:
#   1. Open FreeCAD.
#   2. Open the Python console or run this file as a macro.
#   3. The model will be created in a new FreeCAD document.
#
# This is a simple mechanical concept model intended for rapid iteration.
# It is not a production-ready engineering design.

import math
import FreeCAD as App
import Part


def make_box(name, size, center=(0, 0, 0), color=(0.55, 0.57, 0.60)):
    obj = App.ActiveDocument.addObject("Part::Box", name)
    obj.Length = size[0]
    obj.Width = size[1]
    obj.Height = size[2]
    obj.Placement = App.Placement(App.Vector(*center), App.Rotation())
    obj.ViewObject.ShapeColor = color
    return obj


def make_cylinder(name, radius, height, center=(0, 0, 0), color=(0.52, 0.54, 0.57)):
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


def make_assembly_group(name):
    group = App.ActiveDocument.addObject("App::DocumentObjectGroup", name)
    return group


def add_to_group(group, *objs):
    for obj in objs:
        if obj is not None:
            group.addObject(obj)


# -----------------------------------------------------------------------------
# Model parameters
# -----------------------------------------------------------------------------
base_length = 220
base_width = 180
base_height = 18

pedestal_height = 70
pedestal_outer_d = 80
pedestal_inner_d = 32

pan_ring_outer_d = 160
pan_ring_inner_d = 110
pan_ring_height = 18

rotating_deck_length = 150
rotating_deck_width = 120
rotating_deck_height = 16

column_width = 24
column_depth = 22
column_height = 110

yoke_plate_thickness = 20
yoke_plate_depth = 90
yoke_plate_height = 120
side_x = 52

trunnion_axis_z = base_height + pedestal_height + pan_ring_height + rotating_deck_height + 45
trunnion_bearing_od = 60
trunnion_bearing_id = 20
trunnion_bearing_h = 18

payload_length = 90
payload_width = 70
payload_height = 12
payload_drop = 28

motor_body_length = 80
motor_body_d = 34
motor_shaft_d = 10
motor_shaft_length = 22
gearbox_d = 42
gearbox_h = 38

PAN_ANGLE = 30
TILT_ANGLE = 25


# -----------------------------------------------------------------------------
# Create document
# -----------------------------------------------------------------------------
doc = App.newDocument("PanTiltRobot")
App.setActiveDocument("PanTiltRobot")
App.ActiveDocument = doc

assembly = make_assembly_group("PanTiltAssembly")

# -----------------------------------------------------------------------------
# Base and pedestal
# -----------------------------------------------------------------------------
base = make_box(
    "BasePlate",
    [base_length, base_width, base_height],
    center=(0, 0, base_height / 2),
    color=(0.42, 0.44, 0.47),
)
add_to_group(assembly, base)

pedestal = make_cylinder(
    "Pedestal",
    radius=pedestal_outer_d / 2,
    height=pedestal_height,
    center=(0, 0, base_height + pedestal_height / 2),
    color=(0.50, 0.51, 0.54),
)
add_to_group(assembly, pedestal)

# Inner bore in pedestal for visual realism
pedestal_hole = make_cylinder(
    "PedestalHole",
    radius=pedestal_inner_d / 2,
    height=pedestal_height + 2,
    center=(0, 0, base_height + pedestal_height / 2),
    color=(0.18, 0.18, 0.18),
)
# Cut the bore from pedestal
pedestal.Shape = pedestal.Shape.cut(pedestal_hole.Shape)

# -----------------------------------------------------------------------------
# Pan ring and rotating deck
# -----------------------------------------------------------------------------
ring = make_ring(
    "PanRing",
    outer_radius=pan_ring_outer_d / 2,
    inner_radius=pan_ring_inner_d / 2,
    height=pan_ring_height,
    center=(0, 0, base_height + pedestal_height + pan_ring_height / 2),
    color=(0.58, 0.60, 0.63),
)
add_to_group(assembly, ring)

deck = make_box(
    "RotatingDeck",
    [rotating_deck_length, rotating_deck_width, rotating_deck_height],
    center=(0, 0, base_height + pedestal_height + pan_ring_height + rotating_deck_height / 2),
    color=(0.47, 0.48, 0.51),
)
add_to_group(assembly, deck)

for sx in (-1, 1):
    for sy in (-1, 1):
        column = make_box(
            f"Column_{sx}_{sy}",
            [column_width, column_depth, column_height],
            center=(sx * 38, sy * 30, base_height + pedestal_height + pan_ring_height + rotating_deck_height + column_height / 2 + 12),
            color=(0.40, 0.41, 0.44),
        )
        add_to_group(assembly, column)

# -----------------------------------------------------------------------------
# Yoke structure
# -----------------------------------------------------------------------------
for sx in (-1, 1):
    side_plate = make_box(
        f"YokePlate_{sx}",
        [yoke_plate_thickness, yoke_plate_depth, yoke_plate_height],
        center=(sx * side_x, 0, base_height + pedestal_height + pan_ring_height + rotating_deck_height + 35 + yoke_plate_height / 2),
        color=(0.52, 0.53, 0.56),
    )
    add_to_group(assembly, side_plate)

cross_bar = make_box(
    "YokeTopBar",
    [120, 40, 20],
    center=(0, 0, base_height + pedestal_height + pan_ring_height + rotating_deck_height + 35 + yoke_plate_height + 10),
    color=(0.50, 0.51, 0.54),
)
add_to_group(assembly, cross_bar)

# -----------------------------------------------------------------------------
# Tilt trunnion/bearings and drives
# -----------------------------------------------------------------------------
for sx in (-1, 1):
    bearing = make_cylinder(
        f"TrunnionBearing_{sx}",
        radius=trunnion_bearing_od / 2,
        height=trunnion_bearing_h,
        center=(sx * side_x, 0, trunnion_axis_z),
        color=(0.72, 0.73, 0.76),
    )
    # make the bore by subtracting a smaller cylinder from the bearing
    hole = make_cylinder(
        f"TrunnionBearingHole_{sx}",
        radius=trunnion_bearing_id / 2,
        height=trunnion_bearing_h + 2,
        center=(sx * side_x, 0, trunnion_axis_z),
        color=(0.18, 0.18, 0.18),
    )
    bearing.Shape = bearing.Shape.cut(hole.Shape)
    add_to_group(assembly, bearing)

    gearbox = make_cylinder(
        f"TiltGearbox_{sx}",
        radius=gearbox_d / 2,
        height=gearbox_h,
        center=(sx * 80, 0, trunnion_axis_z),
        color=(0.60, 0.62, 0.65),
    )
    add_to_group(assembly, gearbox)

    motor = make_cylinder(
        f"TiltMotor_{sx}",
        radius=motor_body_d / 2,
        height=motor_body_length,
        center=(sx * 80 + gearbox_h / 2 + motor_body_length / 2, 0, trunnion_axis_z),
        color=(0.78, 0.80, 0.82),
    )
    # Orient the motor as a cylinder along X for a more motor-like look.
    motor.Placement = App.Placement(
        App.Vector(sx * 80 + gearbox_h / 2 + motor_body_length / 2, 0, trunnion_axis_z),
        App.Rotation(App.Vector(0, 1, 0), 90),
    )
    add_to_group(assembly, motor)

# -----------------------------------------------------------------------------
# Payload and tilt group
# -----------------------------------------------------------------------------
payload = make_box(
    "PayloadPlatform",
    [payload_length, payload_width, payload_height],
    center=(0, 0, -payload_drop),
    color=(0.60, 0.62, 0.65),
)
add_to_group(assembly, payload)

center_mount = make_cylinder(
    "CenterMount",
    radius=18,
    height=36,
    center=(0, 0, -payload_drop - 18),
    color=(0.18, 0.18, 0.18),
)
add_to_group(assembly, center_mount)

# Add a few payload frame members
for sx in (-1, 1):
    frame_member = make_box(
        f"FrameMember_{sx}",
        [12, payload_width, payload_height],
        center=(sx * (payload_length / 2 - 8), 0, -payload_drop),
        color=(0.60, 0.62, 0.65),
    )
    add_to_group(assembly, frame_member)

for sy in (-1, 1):
    frame_member = make_box(
        f"FrameMemberY_{sy}",
        [payload_length, 12, payload_height],
        center=(0, sy * (payload_width / 2 - 8), -payload_drop),
        color=(0.60, 0.62, 0.65),
    )
    add_to_group(assembly, frame_member)

# -----------------------------------------------------------------------------
# Pan and tilt rotations as placement transforms
# -----------------------------------------------------------------------------
# Apply a pan rotation to the upper assembly by rotating the assembly group.
# For a simple concept model, this is enough to define the orientation visually.
assembly.Placement = App.Placement(
    App.Vector(0, 0, 0),
    App.Rotation(App.Vector(0, 0, 1), PAN_ANGLE),
)

# The payload is tilted about the trunnion axis by rotating a local sub-assembly.
# The payload group is placed directly in a rotated pose for demonstration.
payload.Placement = App.Placement(
    App.Vector(0, 0, trunnion_axis_z),
    App.Rotation(App.Vector(1, 0, 0), TILT_ANGLE),
)

# Since the payload group is not nested under the pan assembly, it remains in the world frame.
# This keeps the model simple and easy to understand within FreeCAD.

# -----------------------------------------------------------------------------
# Make a small reference axis block for quick understanding
# -----------------------------------------------------------------------------
# Uncomment this block if you want to see the coordinate axes in the model.
#
# axis_x = make_box("AxisX", [200, 2, 2], center=(0, 0, 0), color=(1.0, 0.0, 0.0))
# axis_y = make_box("AxisY", [2, 200, 2], center=(0, 0, 0), color=(0.0, 1.0, 0.0))
# axis_z = make_box("AxisZ", [2, 2, 200], center=(0, 0, 0), color=(0.0, 0.0, 1.0))
# add_to_group(assembly, axis_x, axis_y, axis_z)

# Fit the view and finalize
App.ActiveDocument.recompute()
# The following is optional in GUI mode; it helps the view fit immediately.
try:
    import FreeCADGui
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except Exception:
    pass

print("Pan-tilt robot FreeCAD model created successfully.")
