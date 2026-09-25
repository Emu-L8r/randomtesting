# Two-stage planetary rotary platform (FreeCAD macro)

`planetary_platform_freecad.py` builds a concept model of an inline, coaxial **2-stage** drivetrain where:

- **Fixed (stationary):** base plate, housing shell, and both internal ring gears (`R=99` each stage).
- **Rotating:** Stage 1 input sun, Stage 1 planets/carrier, Stage 2 sun/planets/carrier, output hub, and top circular platform.

## Drivetrain relationship

1. Input shaft drives the **Stage 1 sun** (`S=81`).
2. Stage 1 fixed-ring planetary outputs at the **Stage 1 carrier**.
3. Stage 1 carrier is rigidly fused to the **Stage 2 sun** (`S=81`).
4. Stage 2 carrier is rigidly fused to the **output hub + top platform**.

An annular output bearing depiction is included between fixed housing and rotating output hub/platform.

## Gear selections (shared module `m = 1.8`)

Per stage:

- Sun: `S=81`
- Planets: `11 × P=9`
- Ring: `R=99` (fixed)
- Mesh identity check: `R = S + 2P = 81 + 18 = 99` ✅

Per-stage fixed-ring ratio (sun input, carrier output):

- `i = 1 + R/S = 1 + 99/81 = 2.222222...`

Overall 2-stage nominal reduction:

- `(1 + 99/81)^2 = 4.938272... : 1`

## 11-planet spacing solution

Standard equal angular spacing requires `(S + R) / N` to be an integer. Here:

- `(81 + 99) / 11 = 180/11` (not integer)

So the script uses a **phased/unequal angular arrangement** on valid mesh-index slots instead:

- valid slot angle: `Δθ = 2π * P / (S + R) = 18°`
- total valid slots around 360°: `20`
- planets are placed on 11 selected valid slots, which keeps each planet tooth phase compatible with both sun and fixed ring meshes.
- the script computes the minimum center spacing and tip-clearance for the chosen arrangement and raises an error if tip clearance is negative.

## Document groups

The script creates:

- `FixedHousing`
- `Stage1`
- `Stage2`
- `RotatingOutput`
- `BearingRollingElements`

## Run

1. Open FreeCAD.
2. Open `rando1/planetary_platform_freecad.py` as a macro.
3. Run it.

## Disclaimer

This is a **concept visualization**, not a production gearbox design.
Validate loads, tooth strength, backlash, tolerances, bearing fits, materials, and lubrication before fabrication.
