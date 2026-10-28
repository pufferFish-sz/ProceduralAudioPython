# Objects dragged by hand, matched to real recordings

A wooden plank and a sheet-steel box dragged back and forth on wood and concrete. A = noise exciter, B = surface-profile exciter as in scenes/slide.py, C = B with oversampled contact, cubic profile read and contact damping on the slider. Each entry ends with render-vs-real texture statistics.

All files in this folder share one gain: louder here = louder in the physics.
Stems in `stems/` are each sound source on its own (same gain).

## `drag_wood-plank-40x8x2cm_by-hand-1.7-strokes-per-s_on_wood-floor_A-noise-model.wav`

**What you hear:** a wood plank 40 x 8 x 2cm is dragged back and forth by hand on a wooden plank floor (match: 479718-Sliding_Chess_Pieces_04.wav)

- **Mover:** wood plank 40 x 8 x 2cm, 0.42 kg, lying flat on its broad face, contact at 30 % of its length. Audible modes: 529, 1457, 2856, 4722 Hz.
- **Target:** wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- hand strokes: 1.7 per second, peak speed 0.8 m/s +-20 % per stroke, back and forth over the same ~0.38 m of floor, quick reversals
- vs recording (render vs real): centroid Hz 4663 vs 2380; <300 Hz share 0.01 vs 0.30; level sd dB 2.1 vs 2.5; >1k kurtosis 4 vs 20; clicks/s 0 vs 3; mod peak Hz 1.6 vs nan; mod depth dB 32 vs nan; narrow peaks 4 vs 0; LTAS shape distance 7.9 dB (above 300 Hz: 5.4 dB)
- Energy share: wood-plank-40x8x2cm 26 %, wood-floor 74 %
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)

## `drag_wood-plank-40x8x2cm_by-hand-1.7-strokes-per-s_on_wood-floor_B-profile-model.wav`

**What you hear:** a wood plank 40 x 8 x 2cm is dragged back and forth by hand on a wooden plank floor (match: 479718-Sliding_Chess_Pieces_04.wav)

- **Mover:** wood plank 40 x 8 x 2cm, 0.42 kg, lying flat on its broad face, contact at 30 % of its length. Audible modes: 529, 1457, 2856, 4722 Hz.
- **Target:** wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- hand strokes: 1.7 per second, peak speed 0.8 m/s +-20 % per stroke, back and forth over the same ~0.38 m of floor, quick reversals
- profile contact: 1 track(s) at patch scale 100 um; airborne 0% per track, 25 micro-impacts/s per track, force kurtosis 27, normal-force wobble +-25%
- vs recording (render vs real): centroid Hz 573 vs 2380; <300 Hz share 0.04 vs 0.30; level sd dB 3.2 vs 2.5; >1k kurtosis 27 vs 20; clicks/s 36 vs 3; mod peak Hz 1.7 vs nan; mod depth dB 24 vs nan; narrow peaks 4 vs 0; LTAS shape distance 15.4 dB (above 300 Hz: 16.3 dB)
- Energy share: wood-plank-40x8x2cm 22 %, wood-floor 78 %
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)

## `drag_wood-plank-40x8x2cm_by-hand-1.7-strokes-per-s_on_wood-floor_C-profile-damped-oversampled.wav`

**What you hear:** a wood plank 40 x 8 x 2cm is dragged back and forth by hand on a wooden plank floor (match: 479718-Sliding_Chess_Pieces_04.wav)

- **Mover:** wood plank 40 x 8 x 2cm, 0.42 kg, lying flat on its broad face, contact at 30 % of its length. Audible modes: 529, 1457, 2856, 4722 Hz.
- **Target:** wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- hand strokes: 1.7 per second, peak speed 0.8 m/s +-20 % per stroke, back and forth over the same ~0.38 m of floor, quick reversals
- profile contact: 6 track(s) at asperity scales 20-150 um; airborne 0% per track, 43 micro-impacts/s per track, force kurtosis 74, normal-force wobble +-25%
- vs recording (render vs real): centroid Hz 646 vs 2380; <300 Hz share 0.12 vs 0.30; level sd dB 3.6 vs 2.5; >1k kurtosis 14 vs 20; clicks/s 19 vs 3; mod peak Hz 1.8 vs nan; mod depth dB 21 vs nan; narrow peaks 0 vs 0; LTAS shape distance 8.2 dB (above 300 Hz: 7.5 dB)
- Energy share: wood-plank-40x8x2cm 4 %, wood-floor 96 %
- Note: contact damping: loss factor +0.1 while in contact (dragged flat on the floor)
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)

## `drag_wood-plank-40x8x2cm_by-hand-1.7-strokes-per-s_on_concrete-slab_C-profile-damped-oversampled.wav`

**What you hear:** a wood plank 40 x 8 x 2cm is dragged back and forth by hand on a concrete slab (match: 50124-FOLEY_WOOD_BOX_DRAG_ON_CEMENT_FAST_STUTTER_01.wav)

- **Mover:** wood plank 40 x 8 x 2cm, 0.42 kg, lying flat on its broad face, contact at 30 % of its length. Audible modes: 529, 1457, 2856, 4722 Hz.
- **Target:** concrete slab on ground, 4 x 4 m, 15 cm thick, installed loss 0.05. Lowest modes: 31, 77, 77, 123 Hz (475 modes used).
- hand strokes: 1.7 per second, peak speed 0.8 m/s +-20 % per stroke, back and forth over the same ~0.38 m of floor, quick reversals
- profile contact: 6 track(s) at asperity scales 60-200 um; airborne 1% per track, 448 micro-impacts/s per track, force kurtosis 5, normal-force wobble +-25%
- vs recording (render vs real): centroid Hz 1103 vs 269; <300 Hz share 0.03 vs 0.92; level sd dB 2.5 vs 3.0; >1k kurtosis 4 vs 10; clicks/s 4 vs 5; mod peak Hz 1.8 vs nan; mod depth dB 26 vs nan; narrow peaks 0 vs 0; LTAS shape distance 11.9 dB (above 300 Hz: 8.9 dB)
- Energy share: wood-plank-40x8x2cm 99 %, concrete-slab 1 %
- Note: contact damping: loss factor +0.1 while in contact (dragged flat on the floor)
- Note: simply supported plate; radiates per Maidanik, coincidence 120 Hz (inefficient below)

## `drag_sheet-steel-box-40x30x25cm_by-hand-1.7-strokes-per-s_on_concrete-slab_B-profile-model.wav`

**What you hear:** a sheet-steel box 40 x 30 x 25cm is dragged back and forth by hand on a concrete slab (match: 331763-Slide_Metal_Box_Big_Quick_Smooth_Calm_Close.wav)

- **Mover:** sheet-steel box 40 x 30 x 25cm, 0.8 mm walls, 3.71 kg, empty, sliding on its bottom panel. Audible modes: 33, 69, 97, 129 Hz.
- **Target:** concrete slab on ground, 4 x 4 m, 15 cm thick, installed loss 0.05. Lowest modes: 31, 77, 77, 123 Hz (475 modes used).
- hand strokes: 1.7 per second, peak speed 0.8 m/s +-20 % per stroke, back and forth over the same ~0.38 m of floor, quick reversals
- profile contact: 1 track(s) at patch scale 100 um; airborne 0% per track, 0 micro-impacts/s per track, force kurtosis 5, normal-force wobble +-25%
- vs recording (render vs real): centroid Hz 444 vs 1240; <300 Hz share 0.32 vs 0.24; level sd dB 2.4 vs 2.1; >1k kurtosis 5 vs 9; clicks/s 0 vs 0; mod peak Hz 30.9 vs 1.7; mod depth dB 19 vs 19; narrow peaks 6 vs 1; LTAS shape distance 19.2 dB (above 300 Hz: 20.2 dB)
- Energy share: sheet-steel-box-40x30x25cm 100 %, concrete-slab 0 %
- Note: bottom panel modes (simply supported, welded box loss 0.002); coincidence 15373 Hz
- Note: floor rubs the panel at (37%, 43%) of its sides
- Note: simply supported plate; radiates per Maidanik, coincidence 120 Hz (inefficient below)

## `drag_sheet-steel-box-40x30x25cm_by-hand-1.7-strokes-per-s_on_concrete-slab_C-profile-damped-oversampled.wav`

**What you hear:** a sheet-steel box 40 x 30 x 25cm is dragged back and forth by hand on a concrete slab (match: 331763-Slide_Metal_Box_Big_Quick_Smooth_Calm_Close.wav)

- **Mover:** sheet-steel box 40 x 30 x 25cm, 0.8 mm walls, 3.71 kg, empty, sliding on its bottom panel. Audible modes: 33, 69, 97, 129 Hz.
- **Target:** concrete slab on ground, 4 x 4 m, 15 cm thick, installed loss 0.05. Lowest modes: 31, 77, 77, 123 Hz (475 modes used).
- hand strokes: 1.7 per second, peak speed 0.8 m/s +-20 % per stroke, back and forth over the same ~0.38 m of floor, quick reversals
- profile contact: 6 track(s) at asperity scales 60-200 um; airborne 0% per track, 0 micro-impacts/s per track, force kurtosis 5, normal-force wobble +-25%
- vs recording (render vs real): centroid Hz 1052 vs 1240; <300 Hz share 0.17 vs 0.24; level sd dB 2.5 vs 2.1; >1k kurtosis 5 vs 9; clicks/s 0 vs 0; mod peak Hz 1.7 vs 1.7; mod depth dB 30 vs 19; narrow peaks 0 vs 1; LTAS shape distance 12.2 dB (above 300 Hz: 13.1 dB)
- Energy share: sheet-steel-box-40x30x25cm 100 %, concrete-slab 0 %
- Note: bottom panel modes (simply supported, welded box loss 0.002); coincidence 15373 Hz
- Note: floor rubs the panel at (37%, 43%) of its sides
- Note: contact damping: loss factor +0.1 while in contact (dragged flat on the floor)
- Note: simply supported plate; radiates per Maidanik, coincidence 120 Hz (inefficient below)
