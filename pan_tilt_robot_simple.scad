/*
  Simple pan-tilt robot concept model
  OpenSCAD parametric study for a compact two-axis camera/aiming platform.

  The model is intentionally simple and easy to modify:
    - Pan rotates around Z
    - Tilt rotates around X
    - Base, pedestal, upper frame, and payload are all built from basic primitives

  Use the parameters near the top of the file to resize or reconfigure the model.
*/

$fn = 48;

SHOW_ASSEMBLY = true;
SHOW_EXPLODED = false;
SHOW_MOTORS = true;
SHOW_GEARS = true;
SHOW_PAYLOAD = true;

PAN_ANGLE = 0;    // degrees
TILT_ANGLE = 25;  // degrees

// -----------------------------------------------------------------------------
// Global dimensions (mm)
// -----------------------------------------------------------------------------
base_length = 220;
base_width = 180;
base_height = 18;
base_r = 12;

pedestal_height = 70;
pedestal_outer_d = 80;
pedestal_inner_d = 32;

pan_ring_outer_d = 160;
pan_ring_inner_d = 110;
pan_ring_height = 18;

rotating_deck_length = 150;
rotating_deck_width = 120;
rotating_deck_height = 16;

column_width = 24;
column_depth = 22;
column_height = 110;

upper_frame_height = 80;
yoke_width = 28;
yoke_depth = 100;
yoke_height = 120;

trunnion_axis_z = base_height + pedestal_height + pan_ring_height + rotating_deck_height + 45;
trunnion_bearing_od = 60;
trunnion_bearing_id = 20;
trunnion_bearing_h = 18;

payload_length = 90;
payload_width = 70;
payload_height = 10;
payload_drop = 30;
payload_mount_offset = 18;

motor_body_length = 80;
motor_body_d = 34;
motor_shaft_d = 10;
motor_shaft_length = 22;
gearbox_d = 42;
gearbox_h = 38;

// -----------------------------------------------------------------------------
// Utility functions
// -----------------------------------------------------------------------------
module rounded_box(size = [10, 10, 10], r = 4) {
    x = size[0];
    y = size[1];
    z = size[2];
    hull() {
        for (sx = [-1, 1])
            for (sy = [-1, 1])
                translate([sx * (x / 2 - r), sy * (y / 2 - r), 0])
                    cylinder(h = z, r = r, center = true);
    }
}

module tube(od, id, h) {
    difference() {
        cylinder(h = h, d = od, center = true);
        cylinder(h = h + 1, d = id, center = true);
    }
}

module motor_block(length, d) {
    color([0.78, 0.80, 0.82])
        rounded_box([length, d, d], r = 5);
    color([0.18, 0.18, 0.20])
        translate([length / 2 + motor_shaft_length / 2, 0, 0])
            rotate([0, 90, 0])
                cylinder(h = motor_shaft_length, d = motor_shaft_d, center = true);
}

module gearbox_block(diameter, h) {
    color([0.55, 0.57, 0.60])
        rotate([0, 90, 0])
            cylinder(h = h, d = diameter, center = true);
}

module bolt_circle(radius, count = 8, bolt_d = 5, bolt_h = 20) {
    for (i = [0 : count - 1])
        rotate([0, 0, i * 360 / count])
            translate([radius, 0, 0])
                cylinder(h = bolt_h, d = bolt_d, center = true);
}

module pan_drive_unit(side = 1) {
    y_offset = side * (pan_ring_outer_d * 0.52);
    z_base = base_height + pedestal_height + pan_ring_height / 2;

    color([0.38, 0.39, 0.42])
        translate([0, y_offset, z_base - 12])
            rounded_box([90, 40, 50], r = 8);

    color([0.70, 0.72, 0.75])
        translate([0, y_offset - side * 18, z_base])
            rotate([90, 0, 0])
                cylinder(h = 18, d = 22, center = true);

    if (SHOW_MOTORS) {
        translate([-motor_body_length / 2 - 12, y_offset, z_base + 18])
            rotate([0, 90, 0])
                motor_block(motor_body_length, motor_body_d);
    }
}

module base_plate() {
    color([0.42, 0.44, 0.47])
        translate([0, 0, base_height / 2])
            rounded_box([base_length, base_width, base_height], r = base_r);

    for (sx = [-1, 1])
        for (sy = [-1, 1])
            color([0.30, 0.31, 0.34])
                translate([sx * (base_length * 0.32), sy * (base_width * 0.28), base_height / 2 + 8])
                    rounded_box([28, 24, 16], r = 5);
}

module pedestal() {
    color([0.50, 0.51, 0.54])
        translate([0, 0, base_height + pedestal_height / 2])
            tube(pedestal_outer_d, pedestal_inner_d, pedestal_height);

    color([0.72, 0.73, 0.75])
        translate([0, 0, base_height + pedestal_height / 2])
            bolt_circle(24, count = 8, bolt_d = 6, bolt_h = 30);
}

module pan_ring() {
    color([0.58, 0.60, 0.63])
        translate([0, 0, base_height + pedestal_height + pan_ring_height / 2])
            difference() {
                cylinder(h = pan_ring_height, d = pan_ring_outer_d, center = true);
                cylinder(h = pan_ring_height + 1, d = pan_ring_inner_d, center = true);
            }

    if (SHOW_GEARS) {
        color([0.66, 0.67, 0.70])
            translate([0, 0, base_height + pedestal_height + pan_ring_height / 2])
                rotate([90, 0, 0])
                    cylinder(h = 12, d = 18, center = true);
    }
}

module rotating_deck() {
    deck_z = base_height + pedestal_height + pan_ring_height + rotating_deck_height / 2;
    color([0.47, 0.48, 0.51])
        translate([0, 0, deck_z])
            rounded_box([rotating_deck_length, rotating_deck_width, rotating_deck_height], r = 12);

    for (sx = [-1, 1])
        for (sy = [-1, 1])
            translate([sx * 38, sy * 30, deck_z + 25])
                color([0.40, 0.41, 0.44])
                    rounded_box([column_width, column_depth, column_height], r = 5);
}

module yoke_structure() {
    yoke_z = base_height + pedestal_height + pan_ring_height + rotating_deck_height + 25;
    side_x = 52;

    color([0.52, 0.53, 0.56]) {
        for (sx = [-1, 1])
            translate([sx * side_x, 0, yoke_z + 22])
                rounded_box([yoke_width, yoke_depth, yoke_height], r = 8);

        translate([0, 0, yoke_z + 60])
            rounded_box([120, 40, 20], r = 8);
    }
}

module tilt_bearings() {
    side_x = 52;
    for (sx = [-1, 1])
        translate([sx * side_x, 0, trunnion_axis_z])
            rotate([0, 90, 0])
                color([0.72, 0.73, 0.76])
                    tube(trunnion_bearing_od, trunnion_bearing_id, trunnion_bearing_h);
}

module tilt_drive_module(side = 1) {
    x_offset = side * 80;
    z_offset = trunnion_axis_z;

    color([0.60, 0.62, 0.65])
        translate([x_offset, 0, z_offset])
            rotate([0, 90, 0])
                cylinder(h = gearbox_h, d = gearbox_d, center = true);

    if (SHOW_MOTORS) {
        translate([x_offset + gearbox_h / 2 + motor_body_length / 2, 0, z_offset])
            rotate([0, 90, 0])
                motor_block(motor_body_length, motor_body_d);
    }
}

module payload_frame() {
    color([0.60, 0.62, 0.65]) {
        translate([0, 0, -payload_drop])
            rounded_box([payload_length, payload_width, payload_height], r = 8);

        for (sx = [-1, 1])
            translate([sx * (payload_length / 2 - 8), 0, -payload_drop])
                rounded_box([12, payload_width, payload_height], r = 4);

        for (sy = [-1, 1])
            translate([0, sy * (payload_width / 2 - 8), -payload_drop])
                rounded_box([payload_length, 12, payload_height], r = 4);
    }

    color([0.18, 0.18, 0.18, 0.9])
        translate([0, 0, -payload_drop - 18])
            cylinder(h = 36, d = 16, center = true);
}

module rear_mount_block() {
    color([0.38, 0.39, 0.41])
        translate([0, 0, trunnion_axis_z])
            rotate([0, 90, 0])
                cylinder(h = 40, d = 26, center = true);
}

module payload_group() {
    rear_mount_block();
    payload_frame();
}

module tilt_pose(angle) {
    translate([0, 0, trunnion_axis_z])
        rotate([angle, 0, 0])
            children();
}

module upper_pan_structure() {
    rotating_deck();
    yoke_structure();
    tilt_bearings();
    tilt_drive_module(1);
    tilt_drive_module(-1);
}

module complete_assembly() {
    base_plate();
    pedestal();
    pan_ring();
    pan_drive_unit(1);
    pan_drive_unit(-1);

    rotate([0, 0, PAN_ANGLE])
        upper_pan_structure();

    rotate([0, 0, PAN_ANGLE])
        tilt_pose(TILT_ANGLE)
            payload_group();
}

module exploded_view() {
    base_plate();
    translate([0, 0, 60])
        pedestal();
    translate([0, 0, 120])
        pan_ring();
    translate([0, 0, 170])
        rotate([0, 0, PAN_ANGLE])
            upper_pan_structure();
    translate([0, 0, 260])
        rotate([0, 0, PAN_ANGLE])
            tilt_pose(TILT_ANGLE)
                payload_group();
}

if (SHOW_ASSEMBLY) {
    if (SHOW_EXPLODED)
        exploded_view();
    else
        complete_assembly();
}

// -----------------------------------------------------------------------------
// Optional reference guides for tuning
// -----------------------------------------------------------------------------
module reference_axes() {
    color([1, 0, 0, 0.4])
        translate([0, 0, 0])
            cube([200, 2, 2], center = true);
    color([0, 1, 0, 0.4])
        translate([0, 0, 0])
            cube([2, 200, 2], center = true);
    color([0, 0, 1, 0.4])
        translate([0, 0, 0])
            cube([2, 2, 200], center = true);
}

// Uncomment to inspect the coordinate system if needed.
// reference_axes();
