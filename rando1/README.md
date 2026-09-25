# Three-stage planetary rotary platform (FreeCAD macro)

`planetary_platform_freecad.py` builds a concept model of an inline, coaxial drivetrain where:

- **Fixed (stationary):** base plate, housing shell, and all three internal ring gears.
- **Rotating:** Stage 1 sun/planets/carrier, Stage 2 sun/planets/carrier, Stage 3 sun/planets/carrier, output hub, and top circular platform.

## Drivetrain relationship

1. Input shaft drives the **Stage 1 sun**.
2. Stage 1 fixed-ring planetary outputs at the **Stage 1 carrier**.
3. Stage 1 carrier is rigidly coupled to **Stage 2 sun**.
4. Stage 2 carrier is rigidly coupled to **Stage 3 sun**.
5. Stage 3 carrier is rigidly connected to the **output hub + top platform**.

An annular output bearing depiction is included between fixed housing and rotating output hub/platform.

## Gear selections (module `m = 1.8`)

For each stage, `R = S + 2P` and `(S + R) / 3` is an integer (3-planet equal spacing condition):

- Stage 1: `S=18`, `P=18`, `R=54`, ratio `1 + R/S = 4.000`
- Stage 2: `S=15`, `P=15`, `R=45`, ratio `1 + R/S = 4.000`
- Stage 3: `S=12`, `P=12`, `R=36`, ratio `1 + R/S = 4.000`

Approximate overall reduction (fixed ring, sun input, carrier output):

- `4.0 × 4.0 × 4.0 = 64:1`

## Run

1. Open FreeCAD.
2. Open `rando1/planetary_platform_freecad.py` as a macro.
3. Run it.

The script creates document groups: `FixedHousing`, `Stage1`, `Stage2`, `Stage3`, `RotatingOutput`, `BearingRollingElements`, and `CompoundCouplers`.

## Disclaimer

This is a **concept visualization**, not a production gearbox design.
Validate loads, tooth strength, backlash, tolerances, bearing fits, materials, and lubrication before fabrication.
