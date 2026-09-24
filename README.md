# Pantilty

This repository contains a parametric, engineering-oriented OpenSCAD concept for a dual-axis pan-tilt robot intended as a realistic industrial-style platform rather than a decorative toy model.

## Files

- `pan_tilt_robot.scad` — complete parametric OpenSCAD model.

## Design intent

The model includes:

- dual motors on pan and tilt axes
- planetary reduction architecture
- realistic bearing and shaft interfaces
- electronics compartment for approximately four Raspberry Pi boards
- payload shelf and cable routing provisions
- modular motor mounting patterns for NEMA-style stepper and servo-like motors
- configurable assembly and exploded-view modes

## Notes

This is a conceptual engineering CAD model intended for further refinement with prototype testing, bearing selection, shaft stress analysis, and gear tooth load validation.

The design targets roughly:

- 5–10 kg payload
- 250–350 mm shelf width
- 360° pan concept with a realistic bearing and spindle layout
- ±90° tilt concept with mechanical stops
- 2 motors per axis
- planetary reduction in the roughly 10:1 to 30:1 range depending on the final stage configuration

## Usage

Open `pan_tilt_robot.scad` in OpenSCAD and adjust the parameters at the top of the file. Typical options include:

- `PAN_ANGLE`
- `TILT_ANGLE`
- `SHOW_ASSEMBLY`
- `SHOW_EXPLODED`
- `SHOW_GEARS`
- `SHOW_MOTORS`
- `SHOW_BEARINGS`
- `SHOW_ELECTRONICS`
- `SHOW_INTERNALS`

