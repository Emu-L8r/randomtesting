/*
  Large-scale industrial pan-tilt concept
  Units: mm, kg, N·m

  This remains a conceptual OpenSCAD study rather than a certified machine.
  The geometry is arranged so that:
    - the stationary base, slew-drive pedestals, and service enclosure never tilt
    - the full upper assembly pans about Z
    - only the payload cradle/platform rotates about the single horizontal trunnion axis

  Clearances are intentionally generous around the yoke and side-mounted tilt drives so the
  default poses at -90, 0, and +90 degrees do not obviously pass through gearbox housings.
  Gear teeth, bearings, and bolts are simplified to keep a 5 m-class model responsive.
*/

$fn = 48;

// -----------------------------------------------------------------------------
// 1. GLOBAL PARAMETERS
//    Coordinate system: X = left/right, Y = front/back, Z = vertical.
//    Base sits on the XY plane. Pan rotates about +Z. Tilt rotates about +X.
// -----------------------------------------------------------------------------
SHOW_ASSEMBLY = true;
SHOW_EXPLODED = false;
SHOW_MOTORS = true;
SHOW_GEARS = true;
SHOW_BEARINGS = true;
SHOW_FASTENERS = true;
SHOW_ELECTRONICS = true;
SHOW_INTERNALS = false;
SHOW_DEBUG = false;
SHOW_TILT_SWEEP = true;

PAN_ANGLE = 0;
TILT_ANGLE = 0;

overall_target_envelope = 5000;   // mm, design target for the overall concept envelope
structural_scale = 1.0;           // keep at 1.0 for ~5 m envelope, tune cautiously

s = structural_scale;

// -----------------------------------------------------------------------------
// 2. MATERIAL / MANUFACTURING PARAMETERS
// -----------------------------------------------------------------------------
manufacturing_clearance = 1.5 * s;
print_clearance = 2.0 * s;
pressure_angle = 20;                // degrees, simplified gear representation only
planet_count = 4;
planetary_efficiency = 0.93;
gearbox_stage_count = 2;

// -----------------------------------------------------------------------------
// 3. MOTOR PARAMETERS
// -----------------------------------------------------------------------------
motor_body_width = 340 * s;
motor_body_height = 340 * s;
motor_body_length = 520 * s;
motor_shaft_diameter = 100 * s;
motor_shaft_length = 120 * s;
motor_mount_spacing = 220 * s;
motor_mount_hole_diameter = 18 * s;
motor_flange_diameter = 260 * s;

// -----------------------------------------------------------------------------
// 4. GEAR PARAMETERS
// -----------------------------------------------------------------------------
pan_sun_teeth = 18;
pan_planet_teeth = 27;
pan_ring_teeth = pan_sun_teeth + 2 * pan_planet_teeth;
pan_planetary_ratio = 1 + pan_ring_teeth / pan_sun_teeth;

tilt_sun_teeth = 20;
tilt_planet_teeth = 32;
tilt_ring_teeth = tilt_sun_teeth + 2 * tilt_planet_teeth;
tilt_planetary_ratio = 1 + tilt_ring_teeth / tilt_sun_teeth;

// -----------------------------------------------------------------------------
// 5. BEARING PARAMETERS
// -----------------------------------------------------------------------------

base_length = 3000 * s;
base_width = 2400 * s;
base_height = 360 * s;
base_wall = 24 * s;
anchor_foot_length = 430 * s;
anchor_foot_width = 220 * s;
anchor_foot_height = 120 * s;

service_bay_length = 1600 * s;
service_bay_width = 1200 * s;
service_bay_height = 260 * s;
service_panel_width = 980 * s;
service_panel_height = 520 * s;

pedestal_od = 1900 * s;
pedestal_id = 420 * s;
pedestal_height = 430 * s;

slew_od = 2200 * s;
slew_id = 1520 * s;
slew_height = 220 * s;
slew_tooth_depth = 70 * s;
slew_tooth_count = 96;

rotating_deck_length = 2350 * s;
rotating_deck_width = 1850 * s;
rotating_deck_thickness = 140 * s;
column_width = 180 * s;
column_depth = 240 * s;
column_height = 930 * s;

trunnion_axis_z = base_height + pedestal_height + slew_height + rotating_deck_thickness + 1280 * s;
yoke_inner_span = 1860 * s;
yoke_plate_thickness = 120 * s;
yoke_plate_depth = 1120 * s;
yoke_plate_height = 1720 * s;
yoke_base_z = base_height + pedestal_height + slew_height + rotating_deck_thickness;
yoke_top_tie_height = 220 * s;

tilt_bearing_od = 420 * s;
tilt_bearing_id = 220 * s;
tilt_bearing_width = 120 * s;
trunnion_hub_od = 680 * s;
trunnion_hub_id = 250 * s;
trunnion_hub_width = 140 * s;

tilt_sector_od = 880 * s;
tilt_sector_id = 560 * s;
tilt_sector_width = 90 * s;
tilt_sector_teeth = 44;

payload_frame_width = 1580 * s;
payload_frame_depth = 1380 * s;
payload_frame_height = 900 * s;
payload_frame_tube = 120 * s;
payload_platform_length = 1500 * s;
payload_platform_width = 1180 * s;
payload_platform_thickness = 90 * s;
payload_platform_drop = 210 * s;

pan_drive_offset = slew_od / 2 + 320 * s;
pan_drive_pedestal_length = 760 * s;
pan_drive_pedestal_width = 420 * s;
pan_drive_gearbox_d = 430 * s;
pan_drive_gearbox_h = 340 * s;
pan_pinion_d = 240 * s;
pan_pinion_h = 170 * s;

tilt_drive_gearbox_d = 470 * s;
tilt_drive_gearbox_h = 320 * s;
tilt_motor_length = 520 * s;
tilt_motor_width = 340 * s;
tilt_motor_height = 340 * s;
pan_motor_length = 520 * s;
pan_motor_width = 320 * s;
pan_motor_height = 320 * s;

stop_block_size = [220 * s, 180 * s, 220 * s];
stop_lug_size = [160 * s, 110 * s, 170 * s];
stop_radius = 710 * s;

central_cable_passage_d = 280 * s;
service_cable_d = 90 * s;

pi_count = 4;
pi_length = 90 * s;
pi_width = 62 * s;
pi_height = 18 * s;
pi_standoff_h = 28 * s;
pi_pitch_x = 270 * s;
pi_pitch_y = 220 * s;

// -----------------------------------------------------------------------------
// 6. STRUCTURAL PARAMETERS / FIRST-ORDER ENGINEERING ASSUMPTIONS
// -----------------------------------------------------------------------------
payload_mass = 750;          // kg, conceptual mounted package mass
payload_cg_offset = 900;     // mm from tilt axis to payload CG assumption
payload_radius_of_gyration = 1200; // mm simplified inertia radius for acceleration estimate
safety_factor = 1.8;
gravity = 9.81;
tilt_acceleration = 0.18;    // rad/s^2, first-order tilt acceleration target
pan_acceleration = 0.10;     // rad/s^2, first-order pan acceleration target

motor_torque = 28;           // N·m per motor, conceptual industrial servo
pan_motor_count = 2;
tilt_motor_count = 2;
pan_drive_ratio = 180;
tilt_drive_ratio = 420;
drive_efficiency = 0.86;

// First-order estimates only: these are not a structural, duty-cycle, or certification analysis.
function mm_to_m(v) = v / 1000;

T_gravity = payload_mass * gravity * mm_to_m(payload_cg_offset);
I_tilt_est = payload_mass * pow(mm_to_m(payload_radius_of_gyration), 2);
T_acceleration = I_tilt_est * tilt_acceleration;
T_required = (T_gravity + T_acceleration) * safety_factor;
T_available_tilt = tilt_motor_count * motor_torque * tilt_drive_ratio * drive_efficiency;
T_available_pan = pan_motor_count * motor_torque * pan_drive_ratio * drive_efficiency;

// Explicit console output for quick concept iteration.
echo("pan_planetary_ratio", pan_planetary_ratio);
echo("tilt_planetary_ratio", tilt_planetary_ratio);
echo("planet_count", planet_count);
echo("pressure_angle_deg", pressure_angle);
echo("First-order torque estimates only");
echo("overall_target_envelope_mm", overall_target_envelope);
echo("payload_mass_kg", payload_mass);
echo("payload_cg_offset_mm", payload_cg_offset);
echo("payload_radius_of_gyration_mm", payload_radius_of_gyration);
echo("motor_torque_Nm_each", motor_torque);
echo("pan_drive_ratio", pan_drive_ratio);
echo("tilt_drive_ratio", tilt_drive_ratio);
echo("safety_factor", safety_factor);
echo("static_gravity_torque_Nm", T_gravity);
echo("simplified_acceleration_torque_Nm", T_acceleration);
echo("required_torque_Nm", T_required);
echo("available_tilt_torque_Nm", T_available_tilt);
echo("available_pan_torque_Nm", T_available_pan);

// -----------------------------------------------------------------------------
// 7. ELECTRONICS PARAMETERS
// -----------------------------------------------------------------------------
electronics_wall_thickness = base_wall;
electronics_clearance = 30 * s;
pi_spacing = min(pi_pitch_x, pi_pitch_y);

// -----------------------------------------------------------------------------
// 8. UTILITY FUNCTIONS
// -----------------------------------------------------------------------------
module rounded_box(size = [100, 100, 100], r = 12) {
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

module bolt_circle(radius, count = 16, bolt_d = 24, bolt_h = 40) {
  for (i = [0 : count - 1])
    rotate([0, 0, i * 360 / count])
      translate([radius, 0, 0])
        cylinder(h = bolt_h, d = bolt_d, center = true);
}

module external_ring_gear(od, id, h, tooth_count, tooth_depth) {
  tooth_pitch = max(22, PI * od / tooth_count * 0.50);
  difference() {
    union() {
      tube(od, id, h);
      for (i = [0 : tooth_count - 1])
        rotate([0, 0, i * 360 / tooth_count])
          translate([od / 2 + tooth_depth / 2 - 6, 0, 0])
            cube([tooth_depth, tooth_pitch, h], center = true);
    }
    cylinder(h = h + 1, d = id - 40 * s, center = true);
  }
}

module bearing_race(od, id, h, bolt_count = 24) {
  color([0.70, 0.72, 0.75]) {
    tube(od, id, h);
    if (SHOW_FASTENERS)
      bolt_circle((od + id) / 4, count = bolt_count, bolt_d = 18 * s, bolt_h = h + 8 * s);
  }
}

module equipment_motor(length, width, height, shaft_d, shaft_len) {
  color([0.80, 0.81, 0.84]) {
    rounded_box([length, width, height], r = min(width, height) * 0.08);
    translate([length / 2 + shaft_len / 2, 0, 0])
      cylinder(h = shaft_len, d = shaft_d, center = true);
  }
  color([0.12, 0.12, 0.12])
    translate([-length / 2 + 18 * s, 0, height * 0.22])
      rotate([0, 90, 0])
        cylinder(h = 100 * s, d = 24 * s, center = true);
}

module gearbox_can(length, d, shaft_d, shaft_len) {
  color([0.64, 0.66, 0.69]) {
    rotate([0, 90, 0])
      cylinder(h = length, d = d, center = true);
    translate([length / 2 + shaft_len / 2, 0, 0])
      rotate([0, 90, 0])
        cylinder(h = shaft_len, d = shaft_d, center = true);
  }
}

// -----------------------------------------------------------------------------
// 9. FASTENER MODULES / 10. BEARING MODULES / 11. MOTOR MODULES / 12. GEAR MODULES
// -----------------------------------------------------------------------------
module cable_gland(d = 90, h = 70) {
  color([0.18, 0.18, 0.18])
    cylinder(h = h, d = d, center = true);
}

module vertical_cable_riser(height, d) {
  color([0.16, 0.16, 0.16, 0.85])
    cylinder(h = height, d = d, center = true);
}

// -----------------------------------------------------------------------------
// 5. STATIONARY BASE / SERVICE ENCLOSURE
// -----------------------------------------------------------------------------
module base_platform_shell() {
  color([0.33, 0.34, 0.37]) {
    difference() {
      translate([0, 0, base_height / 2])
        rounded_box([base_length, base_width, base_height], r = 110 * s);
      translate([0, 0, base_height / 2 + base_wall])
        rounded_box([base_length - 2 * base_wall, base_width - 2 * base_wall, base_height], r = 85 * s);
      translate([0, 0, base_height / 2])
        cylinder(h = base_height + 2, d = central_cable_passage_d, center = true);
    }
  }

  for (sx = [-1, 1])
    for (sy = [-1, 1])
      color([0.28, 0.29, 0.31])
        translate([sx * (base_length / 2 - anchor_foot_length * 0.60), sy * (base_width / 2 - anchor_foot_width * 0.80), anchor_foot_height / 2])
          rounded_box([anchor_foot_length, anchor_foot_width, anchor_foot_height], r = 30 * s);
}

module service_enclosure() {
  shell_color = SHOW_INTERNALS ? [0.24, 0.28, 0.34, 0.35] : [0.24, 0.28, 0.34, 1.0];
  color(shell_color) {
    difference() {
      translate([0, 0, service_bay_height / 2 + 28 * s])
        rounded_box([service_bay_length, service_bay_width, service_bay_height], r = 70 * s);
      translate([0, 0, service_bay_height / 2 + 40 * s])
        rounded_box([service_bay_length - 2 * base_wall, service_bay_width - 2 * base_wall, service_bay_height], r = 50 * s);
      translate([0, -service_bay_width / 2 - 1, service_panel_height / 2 + 26 * s])
        cube([service_panel_width, base_wall + 4, service_panel_height], center = true);
      translate([0, service_bay_width / 2 - 12 * s, service_bay_height * 0.45])
        rotate([90, 0, 0])
          cylinder(h = 60 * s, d = service_cable_d, center = true);
    }
  }

  color([0.36, 0.38, 0.41])
    translate([0, -service_bay_width / 2 - base_wall / 2, service_panel_height / 2 + 26 * s])
      rounded_box([service_panel_width, base_wall, service_panel_height], r = 24 * s);

  // The Raspberry Pi-class boards are preserved for continuity with the original concept;
  // production hardware at this scale would normally use industrial PLC/drive controls instead.
  if (SHOW_ELECTRONICS) {
    for (ix = [-1, 1])
      for (iy = [-1, 1]) {
        translate([ix * pi_pitch_x / 2, iy * pi_pitch_y / 2, pi_standoff_h / 2 + 36 * s])
          color([0.72, 0.72, 0.74])
            cylinder(h = pi_standoff_h, d = 16 * s, center = true);
        translate([ix * pi_pitch_x / 2, iy * pi_pitch_y / 2, pi_standoff_h + pi_height / 2 + 36 * s])
          color([0.12, 0.50, 0.16])
            rounded_box([pi_length, pi_width, pi_height], r = 8 * s);
      }
  }

  translate([0, service_bay_width / 2 + 10 * s, service_bay_height * 0.45])
    rotate([90, 0, 0])
      cable_gland(d = service_cable_d, h = 80 * s);
}

module slew_pedestal() {
  color([0.48, 0.49, 0.52])
    translate([0, 0, base_height + pedestal_height / 2])
      tube(pedestal_od, pedestal_id, pedestal_height);

  if (SHOW_FASTENERS)
    color([0.70, 0.71, 0.73])
      translate([0, 0, base_height + 24 * s])
        bolt_circle(pedestal_od * 0.43, count = 20, bolt_d = 22 * s, bolt_h = 48 * s);
}

// -----------------------------------------------------------------------------
// 13. PLANETARY GEARBOX MODULE (simplified visual envelope for performance)
// -----------------------------------------------------------------------------
module planetary_gear_stage_preview(stage_od, stage_id, stage_width, sun_teeth, planet_teeth, ring_teeth) {
  planet_center = (stage_od + stage_id) / 8;
  color([0.74, 0.74, 0.76])
    tube(stage_od, stage_id, stage_width);
  color([0.58, 0.60, 0.63])
    cylinder(h = stage_width * 0.80, d = stage_id * 0.55, center = true);
  for (i = [0 : planet_count - 1])
    rotate([0, 0, i * 360 / planet_count])
      translate([planet_center, 0, 0])
        color([0.66, 0.67, 0.69])
          cylinder(h = stage_width * 0.70, d = stage_id * 0.26, center = true);
}

// -----------------------------------------------------------------------------
// 14. SHAFT MODULES
// -----------------------------------------------------------------------------
module keyed_shaft(length, d, key_w = 28 * s, key_h = 10 * s) {
  color([0.78, 0.79, 0.80]) {
    rotate([0, 90, 0]) cylinder(h = length, d = d, center = true);
    translate([0, d / 2 - key_h / 2, 0]) cube([length * 0.65, key_w, key_h], center = true);
  }
}

// -----------------------------------------------------------------------------
// 15. PAN MODULE
// -----------------------------------------------------------------------------
module lower_slew_race() {
  if (SHOW_BEARINGS)
    translate([0, 0, base_height + pedestal_height + slew_height / 2])
      bearing_race(slew_od, slew_id, slew_height, bolt_count = 28);
  else
    color([0.68, 0.70, 0.72])
      translate([0, 0, base_height + pedestal_height + slew_height / 2])
        tube(slew_od, slew_id, slew_height);
}

module pan_drive_unit(sign = 1) {
  module_origin_y = sign * pan_drive_offset;
  ring_axis_z = base_height + pedestal_height + slew_height / 2;
  pedestal_h = ring_axis_z - base_height;

  color([0.38, 0.39, 0.42])
    translate([0, module_origin_y, base_height + pedestal_h / 2])
      rounded_box([pan_drive_pedestal_length, pan_drive_pedestal_width, pedestal_h], r = 36 * s);

  if (SHOW_GEARS)
    color([0.64, 0.65, 0.68])
      translate([0, module_origin_y - sign * (pan_pinion_d / 2 - 16 * s), ring_axis_z])
        cylinder(h = pan_pinion_h, d = pan_pinion_d, center = true);

  color([0.56, 0.58, 0.61])
    translate([0, module_origin_y, ring_axis_z - pan_drive_gearbox_h * 0.10])
      cylinder(h = pan_drive_gearbox_h, d = pan_drive_gearbox_d, center = true);

  if (SHOW_INTERNALS)
    translate([0, module_origin_y, ring_axis_z - pan_drive_gearbox_h * 0.10])
      planetary_gear_stage_preview(pan_drive_gearbox_d * 0.88, pan_drive_gearbox_d * 0.38, pan_drive_gearbox_h * 0.45, pan_sun_teeth, pan_planet_teeth, pan_ring_teeth);

  if (SHOW_MOTORS)
    translate([-pan_motor_length / 2 - pan_drive_gearbox_d * 0.20, module_origin_y, ring_axis_z + 20 * s])
      equipment_motor(pan_motor_length, pan_motor_width, pan_motor_height, 90 * s, 120 * s);

  color([0.52, 0.53, 0.57])
    translate([-pan_motor_length * 0.22, module_origin_y, ring_axis_z + 20 * s])
      cube([pan_motor_length * 0.34, 160 * s, 130 * s], center = true);
}

module stationary_base_assembly() {
  base_platform_shell();
  service_enclosure();
  slew_pedestal();
  lower_slew_race();
  pan_drive_unit(1);
  pan_drive_unit(-1);

  // Cable path from the service enclosure to the central vertical passage.
  color([0.16, 0.16, 0.16, 0.85])
    translate([0, service_bay_width / 2 - 150 * s, service_bay_height * 0.45])
      rotate([90, 0, 0])
        cylinder(h = service_bay_width - 220 * s, d = service_cable_d * 0.65, center = true);

  translate([0, 0, (base_height + pedestal_height + slew_height) / 2])
    vertical_cable_riser(base_height + pedestal_height + slew_height, central_cable_passage_d * 0.50);
}

// -----------------------------------------------------------------------------
// 16. TILT MODULE
// -----------------------------------------------------------------------------
module upper_slew_ring() {
  translate([0, 0, base_height + pedestal_height + slew_height / 2]) {
    color([0.52, 0.54, 0.57])
      external_ring_gear(slew_od, slew_id, slew_height, slew_tooth_count, slew_tooth_depth);
    if (SHOW_BEARINGS)
      color([0.76, 0.77, 0.79])
        tube(slew_od - 180 * s, slew_id + 180 * s, slew_height * 0.55);
  }
}

module rotating_deck() {
  deck_z = base_height + pedestal_height + slew_height + rotating_deck_thickness / 2;
  color([0.42, 0.43, 0.46])
    translate([0, 0, deck_z])
      rounded_box([rotating_deck_length, rotating_deck_width, rotating_deck_thickness], r = 60 * s);

  for (sx = [-1, 1])
    for (sy = [-1, 1]) {
      x_pos = sx * (rotating_deck_length * 0.28);
      y_pos = sy * (rotating_deck_width * 0.30);
      color([0.46, 0.47, 0.50])
        translate([x_pos, y_pos, deck_z + rotating_deck_thickness / 2 + column_height / 2])
          rounded_box([column_width, column_depth, column_height], r = 24 * s);
      color([0.40, 0.41, 0.44])
        hull() {
          translate([x_pos, y_pos, deck_z + rotating_deck_thickness / 2 + 40 * s])
            cube([column_width, column_depth, 20 * s], center = true);
          translate([sx * (x_pos * 0.55), y_pos, deck_z + rotating_deck_thickness / 2 + 220 * s])
            cube([50 * s, column_depth, 20 * s], center = true);
        }
    }
}

module yoke_structure() {
  side_x = yoke_inner_span / 2 + yoke_plate_thickness / 2;
  plate_center_z = yoke_base_z + yoke_plate_height / 2;

  for (sx = [-1, 1]) {
    color([0.50, 0.51, 0.54])
      translate([sx * side_x, 0, plate_center_z])
        rounded_box([yoke_plate_thickness, yoke_plate_depth, yoke_plate_height], r = 28 * s);

    color([0.44, 0.45, 0.48])
      hull() {
        translate([sx * side_x, 0, yoke_base_z + 80 * s])
          cube([yoke_plate_thickness, 420 * s, 30 * s], center = true);
        translate([sx * (side_x - 140 * s), 0, yoke_base_z + 480 * s])
          cube([30 * s, 300 * s, 30 * s], center = true);
      }
  }

  color([0.46, 0.47, 0.50])
    translate([0, 0, yoke_base_z + yoke_plate_height - yoke_top_tie_height / 2])
      rounded_box([yoke_inner_span + 2 * yoke_plate_thickness, 420 * s, yoke_top_tie_height], r = 26 * s);

  color([0.44, 0.45, 0.48])
    translate([0, -yoke_plate_depth * 0.38, yoke_base_z + 280 * s])
      rounded_box([yoke_inner_span + 2 * yoke_plate_thickness, 180 * s, 180 * s], r = 18 * s);
}

module yoke_trunnion_bearings() {
  if (SHOW_BEARINGS) {
    side_x = yoke_inner_span / 2 + yoke_plate_thickness / 2;
    for (sx = [-1, 1])
      translate([sx * side_x, 0, trunnion_axis_z])
        rotate([0, 90, 0])
          bearing_race(tilt_bearing_od, tilt_bearing_id, tilt_bearing_width, bolt_count = 16);
  }
}

module yoke_hard_stops() {
  side_x = yoke_inner_span / 2 - yoke_plate_thickness * 0.10;
  for (sy = [-1, 1])
    for (sx = [-1, 1])
      color([0.33, 0.34, 0.35])
        translate([sx * side_x, sy * 450 * s, trunnion_axis_z - 600 * s])
          rounded_box(stop_block_size, r = 18 * s);
}

module tilt_drive_module(side = 1) {
  side_x = side * (yoke_inner_span / 2 + yoke_plate_thickness + tilt_bearing_width / 2 + tilt_drive_gearbox_h / 2 + 30 * s);

  color([0.60, 0.62, 0.65])
    translate([side_x, 0, trunnion_axis_z])
      rotate([0, 90, 0])
        cylinder(h = tilt_drive_gearbox_h, d = tilt_drive_gearbox_d, center = true);

  color([0.50, 0.52, 0.55])
    translate([side_x - side * 120 * s, 0, trunnion_axis_z])
      rotate([0, 90, 0])
        cylinder(h = 220 * s, d = 160 * s, center = true);

  if (SHOW_INTERNALS)
    translate([side_x, 0, trunnion_axis_z])
      rotate([0, 90, 0])
        planetary_gear_stage_preview(tilt_drive_gearbox_d * 0.86, tilt_drive_gearbox_d * 0.34, tilt_drive_gearbox_h * 0.42, tilt_sun_teeth, tilt_planet_teeth, tilt_ring_teeth);

  if (SHOW_MOTORS) {
    if (side > 0)
      translate([side_x + side * (tilt_drive_gearbox_h / 2 + tilt_motor_length / 2), 0, trunnion_axis_z])
        equipment_motor(tilt_motor_length, tilt_motor_width, tilt_motor_height, motor_shaft_diameter, motor_shaft_length);
    else
      mirror([1, 0, 0])
        translate([-side_x + (tilt_drive_gearbox_h / 2 + tilt_motor_length / 2), 0, trunnion_axis_z])
          equipment_motor(tilt_motor_length, tilt_motor_width, tilt_motor_height, motor_shaft_diameter, motor_shaft_length);
  }
}

module upper_structure_without_payload() {
  upper_slew_ring();
  rotating_deck();
  yoke_structure();
  yoke_trunnion_bearings();
  yoke_hard_stops();
  limit_switch_mounts();
  tilt_drive_module(1);
  tilt_drive_module(-1);
}

// -----------------------------------------------------------------------------
// 17. ELECTRONICS HOUSING / 18. PAYLOAD SHELF / 19. CABLE MANAGEMENT
// -----------------------------------------------------------------------------
module trunnion_sector(side = 1) {
  cheek_x = side * (payload_frame_width / 2 + payload_frame_tube / 2);
  color([0.55, 0.57, 0.60])
    translate([cheek_x + side * (trunnion_hub_width / 2 + 8 * s), 0, 0])
      rotate([0, 90, 0])
        tube(trunnion_hub_od, trunnion_hub_id, trunnion_hub_width);

  if (SHOW_GEARS)
    color([0.66, 0.67, 0.70])
      translate([cheek_x + side * (trunnion_hub_width + tilt_sector_width / 2), 0, 0])
        rotate([0, 90, 0])
          external_ring_gear(tilt_sector_od, tilt_sector_id, tilt_sector_width, tilt_sector_teeth, 40 * s);
}

module limit_switch_mounts() {
  side_x = yoke_inner_span / 2 - 120 * s;
  for (sx = [-1, 1])
    color([0.42, 0.43, 0.45])
      translate([sx * side_x, -yoke_plate_depth / 2 - 80 * s, trunnion_axis_z + 140 * s])
        rounded_box([100 * s, 60 * s, 120 * s], r = 10 * s);
}

module payload_frame() {
  color([0.58, 0.60, 0.63]) {
    for (sx = [-1, 1])
      translate([sx * (payload_frame_width / 2 - payload_frame_tube / 2), 0, 0])
        rounded_box([payload_frame_tube, payload_frame_depth, payload_frame_height], r = 18 * s);

    for (sz = [-1, 1])
      translate([0, 0, sz * (payload_frame_height / 2 - payload_frame_tube / 2)])
        rounded_box([payload_frame_width, payload_frame_depth, payload_frame_tube], r = 18 * s);

    for (sy = [-1, 1])
      translate([0, sy * (payload_frame_depth / 2 - payload_frame_tube / 2), 0])
        rounded_box([payload_frame_width, payload_frame_tube, payload_frame_height], r = 18 * s);

    translate([0, 0, -payload_platform_drop])
      rounded_box([payload_platform_length, payload_platform_width, payload_platform_thickness], r = 22 * s);
  }

  // Central utility mast path for conceptual sensor/payload cabling through the cradle.
  color([0.18, 0.18, 0.18, 0.80])
    translate([0, 0, -payload_platform_drop / 2])
      cylinder(h = payload_frame_height + 240 * s, d = 90 * s, center = true);
}

module payload_stop_lugs() {
  for (sx = [-1, 1])
    for (sy = [-1, 1])
      color([0.36, 0.37, 0.39])
        translate([sx * (payload_frame_width / 2 + 40 * s), sy * 470 * s, -stop_radius])
          rounded_box(stop_lug_size, r = 16 * s);
}

module payload_sweep_envelope() {
  color([1.0, 0.65, 0.20, 0.08])
    rounded_box([payload_platform_length, payload_platform_width, payload_frame_height + payload_platform_drop * 2], r = 40 * s);
}

module tilting_payload_group() {
  trunnion_sector(1);
  trunnion_sector(-1);
  payload_frame();
  payload_stop_lugs();
}

module tilt_sweep_visualization() {
  // Sampled ghost positions keep the model responsive while still showing the usable sweep envelope.
  for (a = [-90 : 30 : 90])
    rotate([a, 0, 0])
      payload_sweep_envelope();
}

// -----------------------------------------------------------------------------
// 20. ASSEMBLY / 21. EXPLODED VIEW / 22. ENGINEERING VISUALIZATION / 23. VALIDATION
// -----------------------------------------------------------------------------
module rotating_pan_tilt_assembly(show_payload = true) {
  upper_structure_without_payload();

  if (SHOW_TILT_SWEEP)
    translate([0, 0, trunnion_axis_z])
      tilt_sweep_visualization();

  if (show_payload)
    translate([0, 0, trunnion_axis_z])
      rotate([TILT_ANGLE, 0, 0])
        tilting_payload_group();

  // Pan-rotating cable riser inside the central passage.
  color([0.16, 0.16, 0.16, 0.85])
    translate([0, 0, trunnion_axis_z * 0.50])
      cylinder(h = trunnion_axis_z, d = central_cable_passage_d * 0.36, center = true);
}

module complete_assembly() {
  stationary_base_assembly();
  rotate([0, 0, PAN_ANGLE])
    rotating_pan_tilt_assembly(show_payload = true);
}

module exploded_view() {
  stationary_base_assembly();
  translate([0, 0, 520 * s])
    rotate([0, 0, PAN_ANGLE])
      upper_structure_without_payload();
  if (SHOW_TILT_SWEEP)
    translate([0, 0, trunnion_axis_z + 520 * s])
      tilt_sweep_visualization();
  translate([0, 0, trunnion_axis_z + 980 * s])
    rotate([TILT_ANGLE, 0, 0])
      tilting_payload_group();
}

module engineering_debug() {
  if (SHOW_DEBUG) {
    color([1, 0, 0, 0.50])
      translate([0, 0, trunnion_axis_z])
        rotate([0, 90, 0])
          cylinder(h = yoke_inner_span + 700 * s, d = 28 * s, center = true);
    color([0, 1, 0, 0.45])
      translate([0, 0, trunnion_axis_z / 2])
        cylinder(h = trunnion_axis_z * 1.05, d = 24 * s, center = true);
    color([0, 0, 1, 0.18])
      translate([0, 0, overall_target_envelope / 2])
        cube([overall_target_envelope, overall_target_envelope, overall_target_envelope], center = true);
    echo("Debug note", "blue cube marks the target 5 m envelope reference volume");
  }
}

module validation_debug() {
  echo("Concept validation reminders");
  echo("- verify actual bearing selection, bolt preload, and overturning loads");
  echo("- verify real cable bend radius, slip-ring strategy, and motor cooling");
  echo("- verify hard-stop energy absorption and stop pad materials");
  echo("- verify payload CG, duty cycle, and trunnion shaft sizing");
  echo("- model is conceptual only; no certification or final structural validation is claimed");
}

if (SHOW_ASSEMBLY) {
  if (SHOW_EXPLODED)
    exploded_view();
  else
    complete_assembly();
}

engineering_debug();
validation_debug();
