/*
  pantilty - parametric dual-axis pan-tilt robot concept
  Units: mm, N, N·mm, kg, seconds, degrees

  This file is intentionally structured as a conceptual engineering model.
  It is not a certified design and requires prototype validation.

  Design focus:
    - mechanically coherent two-axis pan-tilt architecture
    - dual motors per axis
    - planetary reduction
    - bearing and shaft support
    - electronics bay for four Raspberry Pi-class boards
    - industrial-style frame and serviceability
*/

$fn = 36;

// ---------------------------------------------------------------------
// 1. GLOBAL PARAMETERS
// ---------------------------------------------------------------------
SHOW_ASSEMBLY = true;
SHOW_EXPLODED = false;
SHOW_GEARS = true;
SHOW_MOTORS = true;
SHOW_BEARINGS = true;
SHOW_FASTENERS = true;
SHOW_ELECTRONICS = true;
SHOW_INTERNALS = false;
SHOW_DEBUG = false;

PAN_ANGLE = 0;
TILT_ANGLE = 0;

// ---------------------------------------------------------------------
// 2. MATERIAL / MANUFACTURING PARAMETERS
// ---------------------------------------------------------------------
material_steel = "steel";
material_aluminum = "aluminum";
manufacturing_clearance = 0.5;
print_clearance = 0.7;
frame_wall = 8;
structural_plate = 10;
service_panel_thickness = 3;
castor_gap = 0.4;

// ---------------------------------------------------------------------
// 3. MOTOR PARAMETERS
// ---------------------------------------------------------------------
motor_count = 2;
stepper_motor_body_width = 57;
stepper_motor_body_height = 57;
stepper_motor_body_length = 100;
servo_motor_body_width = 65;
servo_motor_body_height = 65;
servo_motor_body_length = 90;
motor_shaft_diameter = 14;
motor_shaft_length = 25;
motor_mount_spacing = 47;
motor_mount_hole_diameter = 5.5;
motor_flange_diameter = 75;
motor_body_clearance = 6;
motor_body_material = "aluminum";
motor_torque = 2.2; // N·m per motor (conceptual)
motor_speed = 300; // rpm
motor_count_pan = 2;
motor_count_tilt = 2;
gear_ratio = 18; // conceptual drive reduction
gear_efficiency = 0.91;
planetary_efficiency = 0.90;

// ---------------------------------------------------------------------
// 4. GEAR PARAMETERS
// ---------------------------------------------------------------------
module_size = 2.5; // mm per tooth module (conceptual)
pressure_angle = 20;
gear_backlash = 0.35;
gearbox_stage_count = 2;
planet_count = 4;
planetary_stage_ratio = 4.5;
planetary_ratio_total = pow(planetary_stage_ratio, gearbox_stage_count);

sun_teeth = 18;
planet_teeth = 30;
ring_teeth = sun_teeth + 2 * planet_teeth; // 78 for compatible simple stage
gear_width = 18;
planet_clearance = 0.8;
module_pitch = 2.8;

// ---------------------------------------------------------------------
// 5. BEARING PARAMETERS
// ---------------------------------------------------------------------
base_bearing_od = 52;
base_bearing_id = 22;
base_bearing_width = 18;

pan_bearing_od = 60;
pan_bearing_id = 25;
pan_bearing_width = 18;

tilt_bearing_od = 45;
tilt_bearing_id = 20;
tilt_bearing_width = 16;

bearing_outer_diameter = 50;
bearing_inner_diameter = 20;
bearing_width = 18;

// ---------------------------------------------------------------------
// 6. STRUCTURAL PARAMETERS
// ---------------------------------------------------------------------
base_diameter = 260;
base_height = 70;
base_thickness = 18;

pan_ring_outer_d = 230;
pan_ring_inner_d = 135;
pan_ring_width = 34;
pan_upper_height = 140;

tilt_side_plate_length = 270;
tilt_side_plate_height = 110;
tilt_side_plate_thickness = 12;

payload_shelf_length = 300;
payload_shelf_width = 280;
payload_shelf_thickness = 18;

shelf_mount_offset = 28;

pan_shaft_diameter = 25;
tilt_shaft_diameter = 24;

hub_diameter = 42;
shaft_key_width = 6;
shaft_key_depth = 3;

// ---------------------------------------------------------------------
// 7. ELECTRONICS PARAMETERS
// ---------------------------------------------------------------------
pi_count = 4;
pi_length = 85;
pi_width = 56;
pi_height = 20;
pi_spacing = 14;
pi_standoff_height = 20;

electronics_wall_thickness = 4;
electronics_clearance = 8;
service_access_clearance = 10;

// ---------------------------------------------------------------------
// 8. ENGINEERING PARAMETERS
// ---------------------------------------------------------------------
payload_mass = 8; // kg
payload_cog_offset = 0.135; // m from tilt axis
pan_acceleration = 1.5; // rad/s^2
tilt_acceleration = 1.2; // rad/s^2
gravity = 9.81;
safety_factor = 2.0;

// First-order torque estimates
T_gravity = payload_mass * gravity * payload_cog_offset; // N·m approximate
T_acceleration = payload_mass * payload_cog_offset * tilt_acceleration; // N·m approximate
T_required = (T_gravity + T_acceleration) * safety_factor; // N·m
T_available = motor_torque * gear_ratio * gear_efficiency * motor_count; // N·m concept

// Display engineering estimates in the console / OpenSCAD output
echo("Design assumptions:");
echo("payload_mass_kg", payload_mass);
echo("payload_cog_offset_m", payload_cog_offset);
echo("motor_torque_Nm", motor_torque);
echo("motor_speed_rpm", motor_speed);
echo("gear_ratio", gear_ratio);
echo("gear_efficiency", gear_efficiency);
echo("bearing_assumption", "generic heavy-duty bearing envelope");
echo("safety_factor", safety_factor);
echo("manufacturing_method", "CNC / machined aluminum with 3D printed prototype option");
echo("T_gravity_Nm", T_gravity);
echo("T_acceleration_Nm", T_acceleration);
echo("T_required_Nm", T_required);
echo("T_available_Nm", T_available);
echo("planetary_ratio_total", planetary_ratio_total);

echo("Planetary gear geometry check: ring teeth = sun + 2*planet ->", ring_teeth, "=", sun_teeth, "+ 2*", planet_teeth);

// ---------------------------------------------------------------------
// 9. UTILITY FUNCTIONS
// ---------------------------------------------------------------------
function mm_to_m(mm) = mm / 1000;

module rounded_plate(size_x, size_y, size_z, r = 8) {
  hull() {
    for (x = [-1, 1])
      for (y = [-1, 1])
        translate([x * (size_x / 2 - r), y * (size_y / 2 - r), 0])
          cylinder(h = size_z, r = r, center = true);
  }
}

module bolt_hole(diameter = 5.5, length = 30, head_d = 10, head_h = 5) {
  color([0.6, 0.6, 0.6]) {
    cylinder(h = length, d = diameter, center = true);
    translate([0, 0, length / 2 + head_h / 2])
      cylinder(h = head_h, d = head_d, center = true);
  }
}

module hex_nut(d = 10, h = 6) {
  color([0.55, 0.55, 0.55])
    cylinder(h = h, d = d, $fn = 6, center = true);
}

module boss(d = 18, h = 18, hole_d = 5) {
  difference() {
    cylinder(h = h, d = d, center = true);
    cylinder(h = h + 1, d = hole_d, center = true);
  }
}

module service_panel(width = 120, height = 120, thickness = 3) {
  color([0.3, 0.3, 0.35])
    difference() {
      rounded_plate(width, height, thickness, 6);
      for (x = [-1, 1])
        for (y = [-1, 1])
          translate([x * (width / 2 - 18), y * (height / 2 - 18), 0])
            cylinder(h = thickness + 1, d = 6, center = true);
    }
}

module cylinder_shell(outer_d, inner_d, h) {
  difference() {
    cylinder(h = h, d = outer_d, center = true);
    cylinder(h = h + 1, d = inner_d, center = true);
  }
}

// ---------------------------------------------------------------------
// 10. FASTENER MODULES
// ---------------------------------------------------------------------
module m3_fastener(length = 16) {
  color([0.7, 0.7, 0.7]) {
    cylinder(h = length, d = 3.2, center = true);
    translate([0, 0, length / 2 + 2.5])
      cylinder(h = 2.2, d = 6.3, center = true);
  }
}

module m5_fastener(length = 22) {
  color([0.72, 0.72, 0.72]) {
    cylinder(h = length, d = 5.3, center = true);
    translate([0, 0, length / 2 + 3])
      cylinder(h = 4.5, d = 9.5, center = true);
  }
}

module m6_fastener(length = 28) {
  color([0.72, 0.72, 0.72]) {
    cylinder(h = length, d = 6.4, center = true);
    translate([0, 0, length / 2 + 4])
      cylinder(h = 5.7, d = 11.1, center = true);
  }
}

module m8_fastener(length = 34) {
  color([0.7, 0.7, 0.7]) {
    cylinder(h = length, d = 8.5, center = true);
    translate([0, 0, length / 2 + 5])
      cylinder(h = 6.8, d = 15.0, center = true);
  }
}

// ---------------------------------------------------------------------
// 11. BEARING MODULES
// ---------------------------------------------------------------------
module bearing_module(outer_d = 50, inner_d = 20, width = 18, roller_count = 12, show_rollers = false) {
  color([0.7, 0.7, 0.72]) {
    difference() {
      cylinder(h = width, d = outer_d, center = true);
      cylinder(h = width + 1, d = inner_d, center = true);
    }
    if (show_rollers) {
      for (i = [0:roller_count - 1])
        rotate([0, 0, i * 360 / roller_count])
          translate([inner_d / 2 + (outer_d - inner_d) / 4, 0, 0])
            rotate([90, 0, 0])
              cylinder(h = width * 0.96, d = 4.5, center = true);
    }
  }
}

module bearing_seat(outer_d = 50, inner_d = 20, width = 18) {
  color([0.88, 0.88, 0.88])
    cylinder_shell(outer_d + 2, inner_d + 0.2, width + 2);
}

// ---------------------------------------------------------------------
// 12. MOTOR MODULES
// ---------------------------------------------------------------------
motor_plate_thickness = 8;

module motor_mount_plate(motor_width = 57, motor_length = 90, plate_thickness = 8) {
  color([0.4, 0.4, 0.45]) {
    difference() {
      rounded_plate(motor_width + 20, motor_length + 20, plate_thickness, 5);
      for (x = [-1, 1])
        for (y = [-1, 1])
          translate([x * motor_mount_spacing / 2, y * motor_mount_spacing / 2, 0])
            cylinder(h = plate_thickness + 1, d = motor_mount_hole_diameter + 0.2, center = true);
    }
  }
}

module motor_module(
  body_width = 57,
  body_height = 57,
  body_length = 100,
  shaft_d = 14,
  shaft_len = 25,
  flange_d = 75,
  mounting_spacing = 47,
  show_cable = true
) {
  color([0.82, 0.82, 0.84]) {
    translate([0, 0, body_height/2])
      rounded_plate(body_width, body_length, body_height, 5);
    translate([0, 0, body_height])
      cylinder(h = 8, d = flange_d, center = true);
    for (x = [-1, 1])
      for (y = [-1, 1])
        translate([x * mounting_spacing / 2, y * mounting_spacing / 2, body_height / 2])
          cylinder(h = 10, d = 5.4, center = true);
  }
  color([0.2, 0.2, 0.2])
    translate([0, 0, body_height + 10])
      cylinder(h = shaft_len, d = shaft_d, center = true);
  if (show_cable)
    color([0.15, 0.15, 0.15])
      translate([body_width / 2, 0, body_height * 0.7])
        rotate([90, 0, 0])
          cylinder(h = 40, d = 4, center = true);
}

// ---------------------------------------------------------------------
// 13. GEAR MODULES
// ---------------------------------------------------------------------
module spur_gear_approx(teeth = 20, module_pitch = 2.5, face_width = 12, bore = 10, backlash = 0.3) {
  outer_d = module_pitch * teeth;
  tooth_height = module_pitch * 0.8;
  tooth_width = module_pitch * 0.9;
  ring_d = outer_d;

  difference() {
    union() {
      cylinder(h = face_width, d = outer_d, center = true);
      for (i = [0:teeth - 1])
        rotate([0, 0, i * 360 / teeth])
          translate([outer_d / 2 - tooth_height * 0.7, 0, 0])
            cube([tooth_height, tooth_width, face_width + 0.25], center = true);
    }
    cylinder(h = face_width + 1, d = bore, center = true);
  }
}

module ring_gear_approx(teeth = 78, module_pitch = 2.5, face_width = 18, bore = 28, ring_thickness = 8) {
  outer_d = module_pitch * teeth;
  inner_d = bore + 18;
  difference() {
    cylinder(h = face_width, d = outer_d, center = true);
    cylinder(h = face_width + 1, d = inner_d, center = true);
    for (i = [0:teeth - 1])
      rotate([0, 0, i * 360 / teeth])
        translate([(outer_d + inner_d) / 4, 0, 0])
          cube([module_pitch * 1.2, module_pitch * 0.7, face_width + 1], center = true);
  }
}

module planetary_stage(
  sun_teeth = 18,
  planet_teeth = 30,
  ring_teeth = 78,
  gear_width = 18,
  planet_count = 4,
  module_pitch = 2.5,
  planet_clearance = 0.8,
  show_housing = true
) {
  sun_radius = (module_pitch * sun_teeth) / 2;
  planet_radius = (module_pitch * planet_teeth) / 2;
  ring_radius = (module_pitch * ring_teeth) / 2;
  planet_center_radius = (ring_radius - sun_radius) / 2 - planet_clearance;

  color([0.85, 0.82, 0.76]) {
    if (show_housing) {
      difference() {
        cylinder(h = gear_width * 1.6, d = ring_radius * 2 + 20, center = true);
        cylinder(h = gear_width * 1.8, d = ring_radius * 2 - 22, center = true);
      }
    }
  }

  color([0.5, 0.56, 0.6])
    translate([0, 0, 0])
      spur_gear_approx(teeth = sun_teeth, module_pitch = module_pitch, face_width = gear_width, bore = 14);

  color([0.62, 0.65, 0.7])
    for (i = [0:planet_count - 1])
      rotate([0, 0, i * 360 / planet_count])
        translate([planet_center_radius, 0, 0])
          spur_gear_approx(teeth = planet_teeth, module_pitch = module_pitch, face_width = gear_width, bore = 12);

  color([0.68, 0.7, 0.72])
    translate([0, 0, 0])
      ring_gear_approx(teeth = ring_teeth, module_pitch = module_pitch, face_width = gear_width, bore = 42);
}

// ---------------------------------------------------------------------
// 14. PLANETARY GEARBOX MODULE
// ---------------------------------------------------------------------
module planetary_gearbox(
  sun_teeth = 18,
  planet_teeth = 30,
  ring_teeth = 78,
  gear_width = 18,
  planet_count = 4,
  module_pitch = 2.5
) {
  gearbox_case = 95;
  translate([0, 0, 0]) {
    rotate([0, 0, 90])
      planetary_stage(
        sun_teeth = sun_teeth,
        planet_teeth = planet_teeth,
        ring_teeth = ring_teeth,
        gear_width = gear_width,
        planet_count = planet_count,
        module_pitch = module_pitch,
        planet_clearance = 0.8
      );
    color([0.5, 0.5, 0.5])
      cylinder(h = gear_width * 2 + 10, d = 30, center = true);
  }
}

// ---------------------------------------------------------------------
// 15. SHAFT MODULES
// ---------------------------------------------------------------------
module keyed_shaft(diameter = 24, length = 180, key_length = 24) {
  color([0.9, 0.9, 0.9]) {
    cylinder(h = length, d = diameter, center = true);
    translate([0, 0, 0]) rotate([0, 0, 90])
      cube([key_length, shaft_key_width, shaft_key_depth], center = true);
  }
}

module pan_shaft() {
  color([0.9, 0.9, 0.9]) {
    cylinder(h = 110, d = pan_shaft_diameter, center = true);
    translate([0, 0, -8])
      cylinder(h = 12, d = hub_diameter, center = true);
  }
}

module tilt_shaft() {
  color([0.9, 0.9, 0.9]) {
    cylinder(h = tilt_side_plate_length + 30, d = tilt_shaft_diameter, center = true);
    translate([0, 0, 0])
      cylinder(h = 20, d = hub_diameter, center = true);
  }
}

// ---------------------------------------------------------------------
// 16. PAN MODULE
// ---------------------------------------------------------------------
module pan_base() {
  color([0.35, 0.35, 0.38]) {
    difference() {
      cylinder(h = base_height, d = base_diameter, center = true);
      translate([0, 0, 18])
        cylinder(h = base_height + 1, d = base_diameter - 40, center = true);
      for (i = [0:7])
        rotate([0, 0, i * 45])
          translate([base_diameter * 0.36, 0, 0])
            rotate([90, 0, 0])
              cylinder(h = 18, d = 8, center = true);
    }
    translate([0, 0, -base_height / 2 + 18])
      cylinder(h = 12, d = base_diameter * 0.7, center = true);
  }
}

module pan_bearing_stack() {
  translate([0, 0, 30])
    bearing_module(outer_d = pan_bearing_od, inner_d = pan_bearing_id, width = pan_bearing_width, show_rollers = true);
  translate([0, 0, -30])
    bearing_module(outer_d = pan_bearing_od, inner_d = pan_bearing_id, width = pan_bearing_width, show_rollers = true);
}

module pan_frame() {
  color([0.52, 0.52, 0.56]) {
    difference() {
      cylinder(h = pan_ring_width, d = pan_ring_outer_d, center = true);
      cylinder(h = pan_ring_width + 1, d = pan_ring_inner_d, center = true);
    }
  }
  // support ribs
  for (i = [0:3]) {
    rotate([0, 0, i * 90])
      translate([0, pan_ring_outer_d * 0.25, 0])
        cube([18, pan_ring_outer_d * 0.5, pan_ring_width], center = true);
  }
}

module pan_motor_mount() {
  translate([0, 0, 55]) {
    for (i = [0:1])
      rotate([0, 0, i * 180])
        translate([base_diameter * 0.44, 0, 0])
          rotate([90, 0, 0])
            motor_mount_plate(motor_width = stepper_motor_body_width, motor_length = stepper_motor_body_length, plate_thickness = motor_plate_thickness);
  }
}

module pan_motor_pair() {
  if (SHOW_MOTORS) {
    for (i = [0:1])
      rotate([0, 0, i * 180])
        translate([base_diameter * 0.44, 0, 80])
          rotate([90, 0, 0])
            motor_module(
              body_width = stepper_motor_body_width,
              body_height = stepper_motor_body_height,
              body_length = stepper_motor_body_length,
              shaft_d = motor_shaft_diameter,
              shaft_len = motor_shaft_length,
              flange_d = motor_flange_diameter,
              mounting_spacing = motor_mount_spacing,
              show_cable = true
            );
  }
}

module pan_gearbox() {
  if (SHOW_GEARS) {
    translate([0, 0, 10])
      planetary_gearbox(
        sun_teeth = sun_teeth,
        planet_teeth = planet_teeth,
        ring_teeth = ring_teeth,
        gear_width = gear_width,
        planet_count = planet_count,
        module_pitch = module_pitch
      );
  }
}

module pan_axis() {
  translate([0, 0, 30])
    pan_shaft();
}

module pan_module() {
  translate([0, 0, base_height / 2 + 10]) {
    pan_base();
    pan_bearing_stack();
    translate([0, 0, 70])
      pan_frame();
    pan_motor_mount();
    pan_motor_pair();
    pan_gearbox();
    pan_axis();
  }
}

// ---------------------------------------------------------------------
// 17. TILT MODULE
// ---------------------------------------------------------------------
module tilt_side_plates() {
  color([0.5, 0.5, 0.52]) {
    for (x = [-1, 1])
      translate([x * (tilt_side_plate_length / 2 + 18), 0, pan_upper_height / 2 + 40])
        rotate([90, 0, 0])
          difference() {
            cube([tilt_side_plate_thickness, tilt_side_plate_height, tilt_side_plate_length], center = true);
            translate([0, 0, 0])
              cube([tilt_side_plate_thickness + 1, tilt_side_plate_height - 18, tilt_side_plate_length - 42], center = true);
          }
  }
}

module tilt_bearing_pair() {
  for (x = [-1, 1])
    translate([x * 90, 0, pan_upper_height / 2 + 40])
      rotate([90, 0, 0])
        bearing_module(outer_d = tilt_bearing_od, inner_d = tilt_bearing_id, width = tilt_bearing_width, show_rollers = true);
}

module tilt_shaft_support() {
  color([0.7, 0.7, 0.72])
    translate([0, 0, pan_upper_height / 2 + 40])
      rotate([90, 0, 0])
        cylinder(h = tilt_side_plate_length + 30, d = tilt_shaft_diameter, center = true);
}

module tilt_hard_stops() {
  color([0.4, 0.4, 0.42]) {
    for (x = [-1, 1])
      translate([x * 100, 0, pan_upper_height / 2 + 10])
        rotate([90, 0, 0])
          cylinder(h = 18, d = 16, center = true);
  }
}

module tilt_motor_pair() {
  if (SHOW_MOTORS) {
    for (x = [-1, 1])
      translate([x * 110, 0, pan_upper_height / 2 + 70])
        rotate([90, 0, 90])
          motor_module(
            body_width = stepper_motor_body_width,
            body_height = stepper_motor_body_height,
            body_length = stepper_motor_body_length,
            shaft_d = motor_shaft_diameter,
            shaft_len = motor_shaft_length,
            flange_d = motor_flange_diameter,
            mounting_spacing = motor_mount_spacing,
            show_cable = true
          );
  }
}

module tilt_gearbox() {
  if (SHOW_GEARS) {
    translate([0, 0, pan_upper_height / 2 + 55])
      rotate([90, 0, 0])
        planetary_gearbox(
          sun_teeth = sun_teeth,
          planet_teeth = planet_teeth,
          ring_teeth = ring_teeth,
          gear_width = gear_width,
          planet_count = planet_count,
          module_pitch = module_pitch
        );
  }
}

module payload_shelf() {
  color([0.6, 0.62, 0.68]) {
    translate([0, 0, pan_upper_height + 120])
      rotate([90, 0, 0])
        difference() {
          rounded_plate(payload_shelf_length, payload_shelf_width, payload_shelf_thickness, 18);
          for (x = [-2, -1, 0, 1, 2])
            for (y = [-2, -1, 0, 1, 2])
              translate([x * 52, y * 52, 0])
                cylinder(h = payload_shelf_thickness + 1, d = 7, center = true);
        }
  }
}

module tilt_module() {
  translate([0, 0, 0]) {
    tilt_side_plates();
    tilt_bearing_pair();
    tilt_shaft_support();
    tilt_hard_stops();
    tilt_motor_pair();
    tilt_gearbox();
    payload_shelf();
  }
}

// ---------------------------------------------------------------------
// 18. ELECTRONICS HOUSING
// ---------------------------------------------------------------------
module electronics_housing() {
  if (SHOW_ELECTRONICS) {
    color([0.25, 0.28, 0.34]) {
      translate([0, 0, 20])
        difference() {
          rounded_plate(220, 200, 140, 14);
          translate([0, 0, 8])
            rounded_plate(220 - electronics_wall_thickness * 2, 200 - electronics_wall_thickness * 2, 130, 10);
          // access cutout
          translate([0, -80, 55])
            cube([120, 70, 25], center = true);
          // cable routing hole
          translate([0, 105, 0])
            rotate([90, 0, 0])
              cylinder(h = 30, d = 20, center = true);
        }
    }

    // standoffs and board volume
    for (x = [-1, 1])
      for (y = [-1, 1])
        translate([x * 52, y * 52, 0])
          cylinder(h = 24, d = 6, center = true);

    color([0.88, 0.88, 0.88]) {
      for (i = [0:pi_count - 1])
        rotate([0, 0, i * 90])
          translate([0, 0, 5])
            rounded_plate(pi_length, pi_width, pi_height, 8);
    }

    // removable service panel
    translate([0, -105, 0])
      service_panel(width = 140, height = 80, thickness = 3);
  }
}

// ---------------------------------------------------------------------
// 19. CABLE MANAGEMENT
// ---------------------------------------------------------------------
module cable_channel() {
  color([0.18, 0.18, 0.18]) {
    translate([0, 0, base_height / 2 + 18])
      rotate([90, 0, 0])
        cylinder(h = 180, d = 14, center = true);
    translate([0, 0, pan_upper_height / 2 + 35])
      rotate([90, 0, 0])
        cylinder(h = 120, d = 12, center = true);
  }
}

module cable_gland() {
  color([0.2, 0.2, 0.2])
    translate([0, 120, 20])
      rotate([90, 0, 0])
        cylinder(h = 8, d = 18, center = true);
}

// ---------------------------------------------------------------------
// 20. ASSEMBLY
// ---------------------------------------------------------------------
module complete_assembly() {
  union() {
    base();
    translate([0, 0, 20])
      electronics_housing();
    translate([0, 0, base_height + 12])
      rotate([0, 0, PAN_ANGLE])
        pan_module();
    translate([0, 0, 0])
      rotate([0, 0, PAN_ANGLE])
        rotate([0, TILT_ANGLE, 0])
          tilt_module();
    cable_channel();
    cable_gland();
  }
}

module base() {
  color([0.45, 0.45, 0.48]) {
    difference() {
      cylinder(h = base_height, d = base_diameter, center = true);
      translate([0, 0, 18])
        cylinder(h = base_height + 1, d = base_diameter - 40, center = true);
      // central pan bore
      translate([0, 0, 18])
        cylinder(h = 40, d = 50, center = true);
    }
  }
}

// ---------------------------------------------------------------------
// 21. EXPLODED VIEW
// ---------------------------------------------------------------------
module exploded_view() {
  translate([0, 0, 0]) base();
  translate([0, 0, 180]) electronics_housing();
  translate([0, 0, 320]) rotate([0, 0, PAN_ANGLE]) pan_module();
  translate([0, 0, 560]) rotate([0, 0, PAN_ANGLE]) rotate([0, TILT_ANGLE, 0]) tilt_module();
}

// ---------------------------------------------------------------------
// 22. ENGINEERING VISUALIZATION
// ---------------------------------------------------------------------
module engineering_visualization() {
  if (SHOW_DEBUG) {
    // show approximate load vectors and angular description
    color([1, 0, 0, 0.4])
      translate([0, 0, 80])
        rotate([90, 0, 0])
          cylinder(h = 200, d = 4, center = true);
    color([0, 1, 0, 0.4])
      translate([0, 0, 150])
        rotate([0, 90, 0])
          cylinder(h = 220, d = 4, center = true);
  }
}

// ---------------------------------------------------------------------
// 23. VALIDATION / DEBUGGING
// ---------------------------------------------------------------------
module validation_debug() {
  // The model is intentionally simplified and should be checked against actual hardware.
  echo("Validation reminder:");
  echo("- verify shaft engagement and keying");
  echo("- verify gear tooth clearance and ring interference");
  echo("- verify bearing load and deflection");
  echo("- verify payload center of gravity and tilt range");
  echo("- verify cable strain relief and service access");
  echo("- verify fastener wrench access and mechanical stop positioning");
}

if (SHOW_EXPLODED) {
  exploded_view();
} else {
  complete_assembly();
}

if (SHOW_DEBUG) {
  engineering_visualization();
}

validation_debug();

// End of model
