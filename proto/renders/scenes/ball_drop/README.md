# Rubber ball drop: 2 sizes x 3 floors

Solid rubber balls dropped from 1 m. Same material and height everywhere; only ball size and floor change.

All files in this folder share one gain: louder here = louder in the physics.
Stems in `stems/` are each sound source on its own (same gain).

## `drop_rubber-ball-small-r15mm_from-1m_onto_concrete-slab.wav`

**What you hear:** a small solid rubber ball (r = 1.5 cm) falls 1 m onto a concrete slab and bounces until it rests; both the ball and the floor sound

- **Mover:** solid rubber ball, radius 1.5 cm, 16 g (bouncy-ball type). Audible modes: 1562, 2344, 3022, 3196 Hz.
- **Target:** concrete slab on ground, 4 x 4 m, 15 cm thick, installed loss 0.05. Lowest modes: 31, 77, 77, 123 Hz (475 modes used).
- drop height 1 m -> first impact 4.43 m/s; 14 bounces over 3.77 s
- contact stiffness k = 2.15e+06 N/m^1.5 (Hertz, rubber on concrete); first contact 1.45 ms
- restitution 0.80 on the first bounce (calibrated, mu * v = 0.469), 0.77 on the last
- impulse check: max error 0.00 % vs m (v_in + v_out)
- Energy share: rubber-ball-small-r15mm 76 %, concrete-slab 24 %
- Note: solid, not air-filled: a hollow playground ball adds an air-cavity resonance this model does not have
- Note: simply supported plate; radiates per Maidanik, coincidence 120 Hz (inefficient below)

## `drop_rubber-ball-small-r15mm_from-1m_onto_wood-floor.wav`

**What you hear:** a small solid rubber ball (r = 1.5 cm) falls 1 m onto a wooden plank floor and bounces until it rests; both the ball and the floor sound

- **Mover:** solid rubber ball, radius 1.5 cm, 16 g (bouncy-ball type). Audible modes: 1562, 2344, 3022, 3196 Hz.
- **Target:** wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- drop height 1 m -> first impact 4.43 m/s; 15 bounces over 3.84 s
- contact stiffness k = 2.12e+06 N/m^1.5 (Hertz, rubber on wood); first contact 1.45 ms
- restitution 0.80 on the first bounce (calibrated, mu * v = 0.428), 0.78 on the last
- impulse check: max error 0.00 % vs m (v_in + v_out)
- Energy share: rubber-ball-small-r15mm 0 %, wood-floor 100 %
- Note: solid, not air-filled: a hollow playground ball adds an air-cavity resonance this model does not have
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)

## `drop_rubber-ball-small-r15mm_from-1m_onto_steel-plate-floor.wav`

**What you hear:** a small solid rubber ball (r = 1.5 cm) falls 1 m onto a steel deck plate and bounces until it rests; both the ball and the floor sound

- **Mover:** solid rubber ball, radius 1.5 cm, 16 g (bouncy-ball type). Audible modes: 1562, 2344, 3022, 3196 Hz.
- **Target:** steel deck plate walkway, 1 x 1 m, 6 mm, installed loss 0.005. Lowest modes: 29, 72, 72, 115 Hz (507 modes used).
- drop height 1 m -> first impact 4.43 m/s; 15 bounces over 3.84 s
- contact stiffness k = 2.15e+06 N/m^1.5 (Hertz, rubber on metal); first contact 1.45 ms
- restitution 0.80 on the first bounce (calibrated, mu * v = 0.432), 0.78 on the last
- impulse check: max error 0.00 % vs m (v_in + v_out)
- Energy share: rubber-ball-small-r15mm 1 %, steel-plate-floor 99 %
- Note: solid, not air-filled: a hollow playground ball adds an air-cavity resonance this model does not have
- Note: simply supported plate; radiates per Maidanik, coincidence 2050 Hz (inefficient below)

## `drop_rubber-ball-large-r40mm_from-1m_onto_concrete-slab.wav`

**What you hear:** a large solid rubber ball (r = 4.0 cm) falls 1 m onto a concrete slab and bounces until it rests; both the ball and the floor sound

- **Mover:** solid rubber ball, radius 4.0 cm, 295 g (bouncy-ball type). Audible modes: 586, 879, 1133, 1199 Hz.
- **Target:** concrete slab on ground, 4 x 4 m, 15 cm thick, installed loss 0.05. Lowest modes: 31, 77, 77, 123 Hz (475 modes used).
- drop height 1 m -> first impact 4.43 m/s; 14 bounces over 3.81 s
- contact stiffness k = 3.51e+06 N/m^1.5 (Hertz, rubber on concrete); first contact 3.86 ms
- restitution 0.80 on the first bounce (calibrated, mu * v = 0.467), 0.77 on the last
- impulse check: max error 0.00 % vs m (v_in + v_out)
- Energy share: rubber-ball-large-r40mm 25 %, concrete-slab 75 %
- Note: solid, not air-filled: a hollow playground ball adds an air-cavity resonance this model does not have
- Note: simply supported plate; radiates per Maidanik, coincidence 120 Hz (inefficient below)

## `drop_rubber-ball-large-r40mm_from-1m_onto_wood-floor.wav`

**What you hear:** a large solid rubber ball (r = 4.0 cm) falls 1 m onto a wooden plank floor and bounces until it rests; both the ball and the floor sound

- **Mover:** solid rubber ball, radius 4.0 cm, 295 g (bouncy-ball type). Audible modes: 586, 879, 1133, 1199 Hz.
- **Target:** wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- drop height 1 m -> first impact 4.43 m/s; 17 bounces over 4.21 s
- contact stiffness k = 3.47e+06 N/m^1.5 (Hertz, rubber on wood); first contact 3.87 ms
- restitution 0.80 on the first bounce (calibrated, mu * v = 0.180), 0.83 on the last
- impulse check: max error 0.00 % vs m (v_in + v_out)
- Energy share: rubber-ball-large-r40mm 0 %, wood-floor 100 %
- Note: solid, not air-filled: a hollow playground ball adds an air-cavity resonance this model does not have
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)

## `drop_rubber-ball-large-r40mm_from-1m_onto_steel-plate-floor.wav`

**What you hear:** a large solid rubber ball (r = 4.0 cm) falls 1 m onto a steel deck plate and bounces until it rests; both the ball and the floor sound

- **Mover:** solid rubber ball, radius 4.0 cm, 295 g (bouncy-ball type). Audible modes: 586, 879, 1133, 1199 Hz.
- **Target:** steel deck plate walkway, 1 x 1 m, 6 mm, installed loss 0.005. Lowest modes: 29, 72, 72, 115 Hz (507 modes used).
- drop height 1 m -> first impact 4.43 m/s; 17 bounces over 4.21 s
- contact stiffness k = 3.51e+06 N/m^1.5 (Hertz, rubber on metal); first contact 3.87 ms
- restitution 0.80 on the first bounce (calibrated, mu * v = 0.207), 0.83 on the last
- impulse check: max error 0.00 % vs m (v_in + v_out)
- Energy share: rubber-ball-large-r40mm 0 %, steel-plate-floor 100 %
- Note: solid, not air-filled: a hollow playground ball adds an air-cavity resonance this model does not have
- Note: simply supported plate; radiates per Maidanik, coincidence 2050 Hz (inefficient below)
