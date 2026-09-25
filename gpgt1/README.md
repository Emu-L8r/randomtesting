# Two-stage planetary gearbox FreeCAD script

`gpgt1/planetary_gearbox.py` creates a **parametric, two-stage planetary gear train** in FreeCAD using the **FreeCAD Gears / FCGear** addon.

## Requirements covered

1. **5:1 overall reduction**
2. **Two planetary stages in series**
3. **Sun input, carrier output, fixed rings**
4. **Real involute gears from `freecad.gears.commands`**
5. **Sun and planet center bores**
6. **Carrier pins passing through matching planet bores**
7. **Consistent module / pressure angle / tooth counts / center distances**

## Chosen tooth counts and ratio math

A single fixed-ring planetary stage with carrier output has reduction:

- `ratio = 1 + ring / sun`

The script uses these two stages:

### Stage 1

- Sun: **72 teeth**
- Planet: **9 teeth**
- Ring: **90 teeth**

Checks:

- `ring = sun + 2 * planet`
- `90 = 72 + 2 * 9` ✅
- `stage_1_ratio = 1 + 90 / 72 = 9/4 = 2.25 : 1`

### Stage 2

- Sun: **81 teeth**
- Planet: **9 teeth**
- Ring: **99 teeth**

Checks:

- `ring = sun + 2 * planet`
- `99 = 81 + 2 * 9` ✅
- `stage_2_ratio = 1 + 99 / 81 = 20/9 = 2.222222... : 1`

### Overall reduction

- `overall = (9/4) * (20/9) = 5 : 1` ✅

So the assembly meets the requested **exact 5:1 overall ratio** with **two planetary stages in series**.

## Stage arrangement

- **Stage 1**
  - sun gear is the driven input
  - ring gear is fixed to the housing
  - carrier is the output
- **Stage 2**
  - stage 1 carrier is represented by the interstage coupler on the common axis
  - that coupler drives the stage 2 sun
  - stage 2 ring is also fixed
  - stage 2 carrier is the final output

Both stages share a common axis and are separated axially by `STAGE_SPACING_MM`.

## Main parameters

At the top of `gpgt1/planetary_gearbox.py` you can adjust:

- `MODULE_MM`
- `PRESSURE_ANGLE_DEG`
- `NUM_PLANETS`
- `GEAR_HEIGHT_MM`
- `RING_HEIGHT_MM`
- `SUN_BORE_DIA_MM`
- `PLANET_PIN_DIA_MM`
- `CARRIER_PLATE_THICKNESS_MM`
- `INTERSTAGE_GAP_MM`
- `STAGE_1` and `STAGE_2` tooth counts

## Bore and pin details

- The **sun gears** get a center bore by **boolean cutting** the involute gear body with a `Part::Cylinder`.
- The **planet gears** get a center bore the same nominal diameter as the carrier pin.
- Each **carrier** is modeled as a plate/disc with **cylindrical pins** located on the planet circle radius.
- Those pins pass through the matching planet bores in the static CAD assembly.

If you need manufacturing clearance, slightly increase the planet bore diameter or slightly reduce the pin diameter.

## Running the script

### In FreeCAD GUI

1. Install the **Gears / FCGear** addon with **Tools → Addon Manager**.
2. Open FreeCAD.
3. Open `gpgt1/planetary_gearbox.py` as a macro, or paste it into the Python console.
4. Run it.

### Headless / command line

Run it with FreeCAD's Python environment, for example:

```bash
FreeCADCmd /absolute/path/to/gpgt1/planetary_gearbox.py
```

If your local FreeCAD installation supports script arguments on the GUI-capable launcher, you can also try:

```bash
freecad /absolute/path/to/gpgt1/planetary_gearbox.py
```

## Output

The script:

- creates a new document named `TwoStagePlanetaryGearbox`
- builds `Stage1`, `Stage2`, and `InterstageDrive` groups
- recomputes the document
- attempts to save `gpgt1/planetary_gearbox.FCStd`

## Notes

This is a **conceptual, parametric CAD assembly** intended to satisfy the requested kinematic and geometry constraints inside FreeCAD with the Gears addon installed. Validate backlash, profile shift, tooth strength, bearing details, tolerances, and materials before fabrication.
