# Rolling objects, each matched to a real recording

Four rolling objects on the floor of their matching recording in proto/recordings/Rolling/. Speeds come from the recordings' revolution-rate modulation. Each entry ends with render-vs-real texture statistics (proto/analysis/texture_stats.py).

All files in this folder share one gain: louder here = louder in the physics.
Stems in `stems/` are each sound source on its own (same gain).

## `roll_baseball-r37mm_from-0.65mps_on_wood-floor.wav`

**What you hear:** a baseball rolls from 0.65 m/s across a wooden plank floor (match: 520792-FLY_PROP_Baseball_Rolling_on_Hardwood_Floor_Loop_2.wav)

- **Mover:** baseball, radius 3.7 cm, 145 g (cork/yarn core, leather cover: soft, heavily damped). Audible modes: 2558, 3833, 4936, 5163 Hz.
- **Target:** wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- rolling speed 0.65 -> 0.48 m/s (rolling resistance c_rr 0.003); mid-render 0.56 m/s = the recording's 4.9 Hz modulation peak / 2 bump(s) per revolution
- surface: sanded boards, grain ~1.7 mm, a groove between 12 cm boards, a little household grit
- contact: Hertz point law, k = 2.87e+07, alpha 1.5; static penetration 13.490 um, contact resonance 166 Hz, damping ratio 0.22 (micro-landing restitution 0.49); random roughness seen 6.0 um rms
- airborne 15.0% of the time, 44 landings/s, revolution rate 2.42 Hz
- vs recording (render vs real): centroid Hz 152 vs 223; <300 Hz share 0.87 vs 0.96; level sd dB 3.5 vs 4.5; >1k kurtosis 38 vs 301; clicks/s 60 vs 57; mod peak Hz 4.9 vs 4.9; mod depth dB 23 vs 11; narrow peaks 0 vs 0; LTAS shape distance 12.9 dB (above 300 Hz: 14.0 dB)
- Energy share: baseball-r37mm 0 %, wood-floor 100 %
- Note: two raised seam crossings per revolution (0.12 mm, 6 mm wide) + 30 um lumpiness
- Note: stitches: 12 ridges (40 um, 1.5 mm) around each seam crossing where the track runs along the stitched seam -- count set to the recording's ~57 clicks/s
- Note: pebbled leather: 10 um rms surface texture
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)

## `roll_soda-can-full_from-0.46mps_on_wood-floor.wav`

**What you hear:** a full 330 ml aluminium soda can rolls from 0.46 m/s across a wooden plank floor (match: 522505-ROLL_FULL_SODA_CAN_ON_HARDWOOD_FLOOR_LOOP.wav)

- **Mover:** full 330 ml aluminium soda can, radius 3.3 cm, 12.2 cm long, 370 g, rolling on its side. Audible modes: 61, 172, 330, 533 Hz.
- **Target:** wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- rolling speed 0.46 -> 0.29 m/s (rolling resistance c_rr 0.003); mid-render 0.37 m/s = the recording's 1.8 Hz modulation peak / 1 bump(s) per revolution
- surface: sanded boards, grain ~1.7 mm, a groove between 12 cm boards, a little household grit
- contact: Hertz line law, k = 1.04e+08, alpha 1.0; static penetration 0.035 um, contact resonance 2666 Hz, damping ratio 0.22 (micro-landing restitution 0.49); random roughness seen 0.5 um rms (averaged along the line contact)
- airborne 5.1% of the time, 51 landings/s, revolution rate 1.77 Hz
- vs recording (render vs real): centroid Hz 779 vs 199; <300 Hz share 0.04 vs 0.96; level sd dB 6.1 vs 4.1; >1k kurtosis 184 vs 25; clicks/s 72 vs 6; mod peak Hz 12.9 vs 1.8; mod depth dB 11 vs 18; narrow peaks 1 vs 0; LTAS shape distance 12.9 dB (above 300 Hz: 7.9 dB)
- Energy share: soda-can-full 0 %, wood-floor 100 %
- Note: shell ring modes, mass-loaded and damped by the liquid (modal mass x full/empty, tan phi 0.03)
- Note: rim: 50 um eccentricity + one 0.5 mm, 6 mm wide dent (a used can; sized so the can just lifts off once per revolution, the recording's 17 dB swell)
- Note: painted aluminium: 1 um rms surface texture
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)

## `roll_soda-can-full_from-0.77mps_on_rug.wav`

**What you hear:** a full 330 ml aluminium soda can rolls from 0.77 m/s across a cut-pile rug on a wooden floor (match: 522506-ROLL_FULL_SODA_CAN_ON_RUG_LOOP.wav)

- **Mover:** full 330 ml aluminium soda can, radius 3.3 cm, 12.2 cm long, 370 g, rolling on its side. Audible modes: 61, 172, 330, 533 Hz.
- **Target:** cut-pile rug over a wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- rolling speed 0.77 -> 0.48 m/s (rolling resistance c_rr 0.005); mid-render 0.63 m/s = the recording's 3.0 Hz modulation peak / 1 bump(s) per revolution
- surface: cut-pile rug: tufts ~3 mm, very soft and lossy
- contact: Hertz line law, k = 2.11e+04, alpha 1.0; static penetration 172.359 um, contact resonance 38 Hz, damping ratio 0.59 (micro-landing restitution 0.10); random roughness seen 23.5 um rms (averaged along the line contact)
- airborne 0.0% of the time, 0 landings/s, revolution rate 2.97 Hz
- vs recording (render vs real): centroid Hz 38 vs 185; <300 Hz share 1.00 vs 0.97; level sd dB 4.0 vs 4.3; >1k kurtosis 764 vs 13; clicks/s 1 vs 4; mod peak Hz 3.0 vs 3.0; mod depth dB 22 vs 16; narrow peaks 0 vs 0; LTAS shape distance 7.4 dB (above 300 Hz: 4.1 dB)
- Energy share: soda-can-full 0 %, rug 100 %
- Note: shell ring modes, mass-loaded and damped by the liquid (modal mass x full/empty, tan phi 0.03)
- Note: rim: 50 um eccentricity + one 0.5 mm, 6 mm wide dent (a used can; sized so the can just lifts off once per revolution, the recording's 17 dB swell)
- Note: painted aluminium: 1 um rms surface texture
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)

## `roll_aa-battery_from-0.20mps_on_tile-floor.wav`

**What you hear:** a AA battery rolls from 0.20 m/s across a ceramic tile floor (match: 520951-ROLL_BATTERY_TILE_LOOP.wav)

- **Mover:** AA battery, radius 7.3 mm, 5 cm long, 23 g, steel can, rolling on its side. Audible modes: none audible (all modes > 16 kHz).
- **Target:** ceramic tiles bonded to a concrete slab on ground, 4 x 4 m, 15 cm thick, installed loss 0.05. Lowest modes: 31, 77, 77, 123 Hz (475 modes used).
- rolling speed 0.20 -> 0.09 m/s (rolling resistance c_rr 0.002); mid-render 0.14 m/s = the recording's 3.2 Hz modulation peak / 1 bump(s) per revolution
- surface: glazed ceramic tiles, 30 cm grid, 4 mm grout lines 1.2 mm deep, a little grit
- contact: Hertz line law, k = 1.94e+09, alpha 1.0; static penetration 0.000 um, contact resonance 46229 Hz (solved softened to 35280 Hz, still above hearing), damping ratio 0.16 (micro-landing restitution 0.60); random roughness seen 0.1 um rms (averaged along the line contact)
- airborne 0.2% of the time, 0 landings/s, revolution rate 3.08 Hz
- vs recording (render vs real): centroid Hz 1077 vs 576; <300 Hz share 0.37 vs 0.32; level sd dB 3.3 vs 3.5; >1k kurtosis 1310 vs 607; clicks/s 28 vs 22; mod peak Hz nan vs 3.2; mod depth dB nan vs 13; narrow peaks 0 vs 0; LTAS shape distance 5.7 dB (above 300 Hz: 6.2 dB)
- Energy share: aa-battery 37 %, tile-floor 63 %
- Note: no audible modes (all above 16 kHz): you hear its rigid click and the floor
- Note: rim: 10 um eccentricity + a 30 um label seam
- Note: plastic label: 2 um rms surface texture
- Note: simply supported plate; radiates per Maidanik, coincidence 120 Hz (inefficient below)

## `roll_aa-battery_from-0.20mps_on_tile-on-timber.wav`

**What you hear:** a AA battery rolls from 0.20 m/s across ceramic tiles on a timber floor (match: 520951-ROLL_BATTERY_TILE_LOOP.wav)

- **Mover:** AA battery, radius 7.3 mm, 5 cm long, 23 g, steel can, rolling on its side. Audible modes: none audible (all modes > 16 kHz).
- **Target:** ceramic tiles bonded to a wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- rolling speed 0.20 -> 0.09 m/s (rolling resistance c_rr 0.002); mid-render 0.14 m/s = the recording's 3.2 Hz modulation peak / 1 bump(s) per revolution
- surface: glazed ceramic tiles, 30 cm grid, 4 mm grout lines 1.2 mm deep, a little grit
- contact: Hertz line law, k = 1.94e+09, alpha 1.0; static penetration 0.000 um, contact resonance 46229 Hz (solved softened to 35280 Hz, still above hearing), damping ratio 0.16 (micro-landing restitution 0.60); random roughness seen 0.1 um rms (averaged along the line contact)
- airborne 0.2% of the time, 0 landings/s, revolution rate 3.08 Hz
- vs recording (render vs real): centroid Hz 944 vs 576; <300 Hz share 0.07 vs 0.32; level sd dB 3.7 vs 3.5; >1k kurtosis 686 vs 607; clicks/s 38 vs 22; mod peak Hz nan vs 3.2; mod depth dB nan vs 13; narrow peaks 0 vs 0; LTAS shape distance 7.8 dB (above 300 Hz: 7.9 dB)
- Energy share: aa-battery 0 %, tile-on-timber 100 %
- Note: no audible modes (all above 16 kHz): you hear its rigid click and the floor
- Note: rim: 10 um eccentricity + a 30 um label seam
- Note: plastic label: 2 um rms surface texture
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)
