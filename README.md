# Pantilty

This repository contains a parametric OpenSCAD **concept model** for a large industrial-style pan-tilt positioner. The current design intent is an approximately **5 m overall envelope** machine, expressed in millimeters.

## Files

- `pan_tilt_robot.scad` — complete parametric OpenSCAD model

## Revised 5 m design intent

The model now represents a large-scale concept with:

- a wide anchored stationary base and service enclosure
- a substantial slew-ring / cross-roller-bearing style pan interface with a central cable passage
- two **external** pan drive units arranged tangentially to the pan ring gear
- a rigid U-yoke above the pan deck with coaxial left/right tilt trunnions
- two **external** tilt gearmotor / planetary drive modules mounted outside the yoke side plates
- a payload cradle/platform that rotates only about the defined horizontal trunnion axis
- structural hard stops that land on stop blocks rather than on gearbox teeth
- a resized internal electronics bay for four Raspberry Pi-class boards plus panel and cable gland

## Corrected torque paths and geometry

The pan stage is now shown as a stationary-base slew-drive arrangement: motor + gearbox modules sit outside the pan bearing envelope and drive pinions into the external pan ring gear. The tilt stage is arranged around a single explicit trunnion axis, and only the payload cradle/platform is a child of that tilt rotation.

This replaces the earlier small-machine-style layout, where the payload shelf/frame could visually overlap the displayed tilt gearbox and the transforms did not cleanly make the tilt assembly pivot about one defined horizontal axis.

## Engineering assumptions

The OpenSCAD file includes first-order `echo()` outputs for:

- static gravity torque
- simplified acceleration torque
- required torque with safety factor
- available pan and tilt drive torque

These numbers are clearly labeled as **first-order estimates only**. They are intended for concept iteration, not for structural sign-off, duty-cycle approval, or certification.

## Notes

- This remains a conceptual model rather than a production-ready machine.
- Production controls for a 5 m industrial positioner would normally use industrial PLC/drive hardware rather than Raspberry Pis alone.
- Gear teeth, bearings, bolts, and cable paths are simplified for clarity and OpenSCAD performance.
- No certification or final structural validation is claimed.

## Usage

Open `/home/runner/work/randomtesting/randomtesting/pan_tilt_robot.scad` in OpenSCAD and adjust the parameters at the top of the file.

Key parameters and toggles include:

- `overall_target_envelope`
- `PAN_ANGLE`
- `TILT_ANGLE`
- `SHOW_ASSEMBLY`
- `SHOW_EXPLODED`
- `SHOW_MOTORS`
- `SHOW_GEARS`
- `SHOW_BEARINGS`
- `SHOW_ELECTRONICS`
- `SHOW_INTERNALS`
- `SHOW_DEBUG`
- `SHOW_TILT_SWEEP`
