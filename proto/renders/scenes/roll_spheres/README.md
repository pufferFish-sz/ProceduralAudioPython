# Solid wooden and steel balls rolling on a varnished wooden floor

Small and large solid balls of wood and steel, rolled at the same 0.5 m/s across the same varnished wooden floor (core/rolling.py); the last two files repeat the small balls on the same floor with tight flush board joints. One shared gain for all files.

All files in this folder share one gain: louder here = louder in the physics.
Stems in `stems/` are each sound source on its own (same gain).

## `roll_wooden-ball-small-r20mm_from-0.59mps_on_varnished-wood-floor.wav`

**What you hear:** a solid wooden ball (turned hardwood) rolls across a varnished wooden plank floor

- **Mover:** solid wooden ball, radius 2.0 cm, 22 g, turned hardwood. Audible modes: none audible (all modes > 16 kHz).
- **Target:** varnished wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- rolling speed 0.59 -> 0.41 m/s (rolling resistance c_rr 0.003); mid-render 0.50 m/s (same for all balls)
- surface: varnished boards (grain filled, 1.5 um rms), a groove between 12 cm boards, a little household grit
- contact: Hertz point law, k = 1.04e+08, alpha 1.5; static penetration 1.620 um, contact resonance 480 Hz, damping ratio 0.22 (micro-landing restitution 0.49); random roughness seen 1.5 um rms
- airborne 11.1% of the time, 32 landings/s, revolution rate 3.93 Hz
- rim: 20 um out of round, surface texture 3 um rms
- Energy share: wooden-ball-small-r20mm 0 %, varnished-wood-floor 100 %
- Note: no audible modes (lowest sphere mode above 16 kHz): you hear its rigid click and the floor
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)

## `roll_wooden-ball-large-r50mm_from-0.59mps_on_varnished-wood-floor.wav`

**What you hear:** a solid wooden ball (turned hardwood) rolls across a varnished wooden plank floor

- **Mover:** solid wooden ball, radius 5.0 cm, 340 g, turned hardwood. Audible modes: none audible (all modes > 16 kHz).
- **Target:** varnished wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- rolling speed 0.59 -> 0.41 m/s (rolling resistance c_rr 0.003); mid-render 0.50 m/s (same for all balls)
- surface: varnished boards (grain filled, 1.5 um rms), a groove between 12 cm boards, a little household grit
- contact: Hertz point law, k = 1.64e+08, alpha 1.5; static penetration 7.461 um, contact resonance 224 Hz, damping ratio 0.22 (micro-landing restitution 0.49); random roughness seen 1.5 um rms
- airborne 0.0% of the time, 0 landings/s, revolution rate 1.57 Hz
- rim: 40 um out of round, surface texture 3 um rms
- Energy share: wooden-ball-large-r50mm 0 %, varnished-wood-floor 100 %
- Note: no audible modes (lowest sphere mode above 16 kHz): you hear its rigid click and the floor
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)

## `roll_steel-ball-small-r10mm_from-0.59mps_on_varnished-wood-floor.wav`

**What you hear:** a solid steel ball (polished (ball bearing)) rolls across a varnished wooden plank floor

- **Mover:** solid steel ball, radius 1.0 cm, 33 g, polished (ball bearing). Audible modes: none audible (all modes > 16 kHz).
- **Target:** varnished wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- rolling speed 0.59 -> 0.41 m/s (rolling resistance c_rr 0.003); mid-render 0.50 m/s (same for all balls)
- surface: varnished boards (grain filled, 1.5 um rms), a groove between 12 cm boards, a little household grit
- contact: Hertz point law, k = 1.46e+08, alpha 1.5; static penetration 1.698 um, contact resonance 469 Hz, damping ratio 0.22 (micro-landing restitution 0.49); random roughness seen 1.5 um rms
- airborne 25.6% of the time, 44 landings/s, revolution rate 7.85 Hz
- rim: 1 um out of round, surface texture 0.1 um rms
- Energy share: steel-ball-small-r10mm 0 %, varnished-wood-floor 100 %
- Note: no audible modes (lowest sphere mode above 16 kHz): you hear its rigid click and the floor
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)

## `roll_steel-ball-large-r30mm_from-0.59mps_on_varnished-wood-floor.wav`

**What you hear:** a solid steel ball (polished (ball bearing)) rolls across a varnished wooden plank floor

- **Mover:** solid steel ball, radius 3.0 cm, 888 g, polished (ball bearing). Audible modes: none audible (all modes > 16 kHz).
- **Target:** varnished wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- rolling speed 0.59 -> 0.41 m/s (rolling resistance c_rr 0.003); mid-render 0.50 m/s (same for all balls)
- surface: varnished boards (grain filled, 1.5 um rms), a groove between 12 cm boards, a little household grit
- contact: Hertz point law, k = 2.53e+08, alpha 1.5; static penetration 10.596 um, contact resonance 188 Hz, damping ratio 0.22 (micro-landing restitution 0.49); random roughness seen 1.5 um rms
- airborne 1.0% of the time, 4 landings/s, revolution rate 2.62 Hz
- rim: 2 um out of round, surface texture 0.1 um rms
- Energy share: steel-ball-large-r30mm 0 %, varnished-wood-floor 100 %
- Note: no audible modes (lowest sphere mode above 16 kHz): you hear its rigid click and the floor
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)

## `roll_wooden-ball-small-r20mm_from-0.59mps_on_varnished-wood-floor-tight.wav`

**What you hear:** a solid wooden ball (turned hardwood) rolls across a varnished wooden plank floor with tight joints

- **Mover:** solid wooden ball, radius 2.0 cm, 22 g, turned hardwood. Audible modes: none audible (all modes > 16 kHz).
- **Target:** varnished wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- rolling speed 0.59 -> 0.41 m/s (rolling resistance c_rr 0.003); mid-render 0.50 m/s (same for all balls)
- surface: varnished boards (1.5 um rms), tight flush joints every 12 cm (1 mm, 0.1 mm deep), a little grit
- contact: Hertz point law, k = 1.04e+08, alpha 1.5; static penetration 1.620 um, contact resonance 480 Hz, damping ratio 0.22 (micro-landing restitution 0.49); random roughness seen 1.5 um rms
- airborne 7.9% of the time, 29 landings/s, revolution rate 3.93 Hz
- rim: 20 um out of round, surface texture 3 um rms
- Energy share: wooden-ball-small-r20mm 0 %, varnished-wood-floor-tight 100 %
- Note: no audible modes (lowest sphere mode above 16 kHz): you hear its rigid click and the floor
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)

## `roll_steel-ball-small-r10mm_from-0.59mps_on_varnished-wood-floor-tight.wav`

**What you hear:** a solid steel ball (polished (ball bearing)) rolls across a varnished wooden plank floor with tight joints

- **Mover:** solid steel ball, radius 1.0 cm, 33 g, polished (ball bearing). Audible modes: none audible (all modes > 16 kHz).
- **Target:** varnished wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- rolling speed 0.59 -> 0.41 m/s (rolling resistance c_rr 0.003); mid-render 0.50 m/s (same for all balls)
- surface: varnished boards (1.5 um rms), tight flush joints every 12 cm (1 mm, 0.1 mm deep), a little grit
- contact: Hertz point law, k = 1.46e+08, alpha 1.5; static penetration 1.698 um, contact resonance 469 Hz, damping ratio 0.22 (micro-landing restitution 0.49); random roughness seen 1.5 um rms
- airborne 16.1% of the time, 41 landings/s, revolution rate 7.85 Hz
- rim: 1 um out of round, surface texture 0.1 um rms
- Energy share: steel-ball-small-r10mm 0 %, varnished-wood-floor-tight 100 %
- Note: no audible modes (lowest sphere mode above 16 kHz): you hear its rigid click and the floor
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)
