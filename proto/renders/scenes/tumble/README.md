# Small block tumbling to rest

20 x 5 x 2 cm pieces thrown sideways at 3 m/s. Two wood-block files differ only in the floor; the steel file differs from the second only in the object's material. Same random seed for all three.

All files in this folder share one gain: louder here = louder in the physics.
Stems in `stems/` are each sound source on its own (same gain).

## `tumble_wood-block-20x5x2cm_thrown-3mps_onto_wood-floor.wav`

**What you hear:** a small wood block is thrown onto a wooden plank floor and tumbles to rest: irregular clacks, getting softer

- **Mover:** wood block 20 x 5 x 2cm, 0.13 kg, tumbling, lands on edges, contact at 50 % of its length. Audible modes: 2114, 11426 Hz.
- **Target:** wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- thrown 3 m/s sideways, first landing 2.5 m/s vertical; 8 contacts over 0.72 s
- contact stiffness k = 4.01e+07 N/m^1.5 (Hertz, wood edge r = 3 mm on wood)
- contact points vary along the length (5-95 %), so each hit colours the same modes differently
- impulse check: max error 0.00 % vs m (v_in + v_out)
- Energy share: wood-block-20x5x2cm 0 %, wood-floor 100 %
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)

## `tumble_wood-block-20x5x2cm_thrown-3mps_onto_concrete-slab.wav`

**What you hear:** a small wood block is thrown onto a concrete slab and tumbles to rest: irregular clacks, getting softer

- **Mover:** wood block 20 x 5 x 2cm, 0.13 kg, tumbling, lands on edges, contact at 50 % of its length. Audible modes: 2114, 11426 Hz.
- **Target:** concrete slab on ground, 4 x 4 m, 15 cm thick, installed loss 0.05. Lowest modes: 31, 77, 77, 123 Hz (475 modes used).
- thrown 3 m/s sideways, first landing 2.5 m/s vertical; 8 contacts over 0.68 s
- contact stiffness k = 7.75e+07 N/m^1.5 (Hertz, wood edge r = 3 mm on concrete)
- contact points vary along the length (5-95 %), so each hit colours the same modes differently
- impulse check: max error 0.00 % vs m (v_in + v_out)
- Energy share: wood-block-20x5x2cm 95 %, concrete-slab 5 %
- Note: simply supported plate; radiates per Maidanik, coincidence 120 Hz (inefficient below)

## `tumble_steel-bar-20x5x2cm_thrown-3mps_onto_concrete-slab.wav`

**What you hear:** a small steel bar is thrown onto a concrete slab and tumbles to rest: irregular clacks, getting softer

- **Mover:** steel bar 20 x 5 x 2cm, 1.57 kg, tumbling, lands on edges, contact at 50 % of its length. Audible modes: 2594, 14019 Hz.
- **Target:** concrete slab on ground, 4 x 4 m, 15 cm thick, installed loss 0.05. Lowest modes: 31, 77, 77, 123 Hz (475 modes used).
- thrown 3 m/s sideways, first landing 2.5 m/s vertical; 8 contacts over 0.76 s
- contact stiffness k = 2.00e+09 N/m^1.5 (Hertz, metal edge r = 3 mm on concrete)
- contact points vary along the length (5-95 %), so each hit colours the same modes differently
- impulse check: max error 0.00 % vs m (v_in + v_out)
- Energy share: steel-bar-20x5x2cm 41 %, concrete-slab 59 %
- Note: simply supported plate; radiates per Maidanik, coincidence 120 Hz (inefficient below)
