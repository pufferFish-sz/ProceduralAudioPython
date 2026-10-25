# Wooden stick strikes bars: wood / steel / stone

One 2 m/s hit with the same stick on bars of identical size. Only the bar material changes.

All files in this folder share one gain: louder here = louder in the physics.
Stems in `stems/` are each sound source on its own (same gain).

## `strike_wood-stick-30cm_at-2mps_on_wood-bar-30x4x2cm.wav`

**What you hear:** a wooden stick hits a wood bar (30 x 4 x 2 cm) once at 2 m/s; the bar rings and the stick adds a short wooden tick

- **Mover:** wooden stick 30 cm long, 12 mm diameter, 22 g, swung from one end (tip effective mass M/3), rounded 6 mm tip. Audible modes: none audible (all modes > 16 kHz).
- **Target:** wood bar 30 x 4 x 2cm, 0.16 kg, resting on soft supports (free-free), contact at 30 % of its length. Lowest modes: 940, 2590, 5078, 8394 Hz (5 modes used).
- strike speed 2 m/s; contact stiffness k = 5.67e+07 N/m^1.5 (Hertz, wood tip on wood)
- contact time 0.337 ms, 1 contact(s) (micro-bounces), stick rebound 1.20 m/s (calibrated mu = 0.445 s/m)
- effective mass in contact 7.0 g (stick tip vs free bar, reduced mass)
- Energy share: wood-stick-30cm 28 %, wood-bar-30x4x2cm 72 %
- Note: stick = rigid striker: you hear its contact click, not its own ring (no hand-grip model yet)

## `strike_wood-stick-30cm_at-2mps_on_steel-bar-30x4x2cm.wav`

**What you hear:** a wooden stick hits a steel bar (30 x 4 x 2 cm) once at 2 m/s; the bar rings and the stick adds a short wooden tick

- **Mover:** wooden stick 30 cm long, 12 mm diameter, 22 g, swung from one end (tip effective mass M/3), rounded 6 mm tip. Audible modes: none audible (all modes > 16 kHz).
- **Target:** steel bar 30 x 4 x 2cm, 1.88 kg, resting on soft supports (free-free), contact at 30 % of its length. Lowest modes: 1153, 3178, 6231, 10300 Hz (5 modes used).
- strike speed 2 m/s; contact stiffness k = 1.13e+08 N/m^1.5 (Hertz, wood tip on metal)
- contact time 0.252 ms, 1 contact(s) (micro-bounces), stick rebound 1.20 m/s (calibrated mu = 0.483 s/m)
- effective mass in contact 7.3 g (stick tip vs free bar, reduced mass)
- Energy share: wood-stick-30cm 55 %, steel-bar-30x4x2cm 45 %
- Note: stick = rigid striker: you hear its contact click, not its own ring (no hand-grip model yet)

## `strike_wood-stick-30cm_at-2mps_on_stone-bar-30x4x2cm.wav`

**What you hear:** a wooden stick hits a stone bar (30 x 4 x 2 cm) once at 2 m/s; the bar rings and the stick adds a short wooden tick

- **Mover:** wooden stick 30 cm long, 12 mm diameter, 22 g, swung from one end (tip effective mass M/3), rounded 6 mm tip. Audible modes: none audible (all modes > 16 kHz).
- **Target:** stone bar 30 x 4 x 2cm, 0.65 kg, resting on soft supports (free-free), contact at 30 % of its length. Lowest modes: 983, 2710, 5312, 8781 Hz (5 modes used).
- strike speed 2 m/s; contact stiffness k = 1.11e+08 N/m^1.5 (Hertz, wood tip on stone)
- contact time 0.255 ms, 1 contact(s) (micro-bounces), stick rebound 1.20 m/s (calibrated mu = 0.466 s/m)
- effective mass in contact 7.3 g (stick tip vs free bar, reduced mass)
- Energy share: wood-stick-30cm 70 %, stone-bar-30x4x2cm 30 %
- Note: stick = rigid striker: you hear its contact click, not its own ring (no hand-grip model yet)
