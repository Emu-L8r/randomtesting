# Compound helical planetary platform (FreeCAD macro)

`planetary_platform_freecad.py` now rebuilds the concept as a **FreeCAD macro that depends on the FreeCAD Gears addon** (`freecad.gears`) instead of the earlier hand-made boolean tooth approximation.

## Addon dependency

This macro requires the **FreeCAD Gears / FCGear** addon.

Install it in FreeCAD via:

1. **Tools** → **Addon Manager**
2. Search for **Gears** or **FCGear**
3. Install it, restart FreeCAD if prompted, then rerun the macro

If the addon is missing, the macro stops with a clear message instead of failing with a bare import traceback.

## Architecture

The model is a **single compound planetary carrier-output layout** with **6 evenly spaced compound planets** at **60° increments** and **22° helical gears** throughout.

- **Fixed to the housing/base:**
  - lower internal ring gear
  - base plate / housing shell
  - fixed outer bearing race
- **Input:**
  - one lower sun gear on the centerline
- **Compound planets:**
  - 6 rigid planet bodies
  - each planet body contains:
    - a **9-tooth primary helical gear** meshing with the input sun and lower fixed ring
    - a **6-tooth smaller transfer helical gear** stacked on the same shaft as the second member of the compound planet
    - a rigid join sleeve / axle tying both gears together as one rotating body
- **Rotating output:**
  - carrier plate
  - output hub
  - top circular platform
  - rotating inner bearing race

The macro intentionally stops at **one real carrier-output planetary mesh** rather than reviving the previous multi-stage stack. The smaller upper gear is still modeled as the rigid compound member on each planet body, ready to serve as the follow-on interface if the concept is extended later.

## Chosen tooth counts

### Primary carrier-output mesh

- Sun: **21 teeth**
- Planet: **9 teeth** (the requested planet pinion on each compound planet body)
- Ring: **39 teeth**

Checks:

- `ring = sun + 2 * planet`
- `39 = 21 + 2 * 9` ✅
- `(sun + ring) / 6 = (21 + 39) / 6 = 10` ✅

This means the requested **6-planet equal-spacing condition is valid**, so the planets are placed at exact 60° increments.

### Compound transfer member on the same rigid planet body

- Transfer gear: **6 teeth**
- Transfer module: **1.5**

This upper member is deliberately **smaller in diameter** than the primary `9-tooth @ module 2.0` gear, so each planet position is visibly a **compound two-gear stack** rather than two adjacent copies of the same pinion.

The 9-tooth requirement is therefore satisfied by the primary planet pinion at each of the 6 planet locations, while the stacked 6-tooth member provides the required different tooth count/diameter for a true compound planet body.
Both stacked gears keep one shared keyed body orientation in the macro, so the compound planet is modeled as a single rigid rotating member rather than as two independently phased gears.

## Helix handedness

All gears use a **22° helix magnitude**.

- sun / ring: **+22°**
- compound planets: **-22°**

That handedness choice follows the usual parallel-axis helical-mesh convention used by the FreeCAD Gears addon: the planet gears are mirrored relative to the sun/ring gears so the meshes are shown with opposite hand where needed.

## Reduction ratio

For the chosen primary tooth counts, the **theoretical fixed-ring carrier ratio** is:

- `i = 1 + ring/sun = 1 + 39/21 = 2.857142857... : 1`

So the selected `21/9/39` tooth counts correspond to a **2.857143:1 theoretical carrier-output ratio** for the main fixed-ring planetary mesh.

The upper `6-tooth @ module 1.5` gear is included as the compound-planet transfer interface geometry rather than as a reintroduced separate stacked reduction stage.

## FreeCAD document groups

The macro creates these named groups:

- `FixedHousing`
- `Sun`
- `CompoundPlanets`
- `Carrier`
- `RotatingOutput`
- `BearingRollingElements`

## Run

1. Open FreeCAD.
2. Ensure the **Gears / FCGear** addon is installed.
3. Open `rando1/planetary_platform_freecad.py` as a macro.
4. Run it.

## Disclaimer

This is a **concept visualization macro**.

Validate loads, tooth strength, backlash, tolerances, bearing fits, materials, and lubrication before fabrication.
