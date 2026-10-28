# Wooden plank sliding to a stop: A (noise) vs B (surface profile)

The same 40 x 8 x 2 cm wooden plank shoved at 2.5 m/s on three floors, rendered with the old noise exciter (A) and the new surface-profile exciter (B). Last file: A on the wood floor with stick-slip.

All files in this folder share one gain: louder here = louder in the physics.
Stems in `stems/` are each sound source on its own (same gain).

## `slide_wood-plank-40x8x2cm_shoved-2.5mps_on_wood-floor_A-noise-model.wav`

**What you hear:** a wooden plank is shoved at 2.5 m/s across a wooden plank floor and slides to a stop -- old noise exciter

- **Mover:** wood plank 40 x 8 x 2cm, 0.42 kg, sliding flat on its broad face, contact at 30 % of its length. Audible modes: 529, 1457, 2856, 4722 Hz.
- **Target:** wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- shove speed 2.5 m/s, kinetic friction mu_k = 0.35 -> slides 0.91 m and stops after 0.73 s
- model A (noise): fluctuating force = 10% of the Coulomb force 1.43 N at 0.5 m/s, brightness 9000 Hz per m/s
- gate: level~speed corr 0.983, silent after stop yes
- Energy share: wood-plank-40x8x2cm 25 %, wood-floor 75 %
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)

## `slide_wood-plank-40x8x2cm_shoved-2.5mps_on_wood-floor_B-profile-model.wav`

**What you hear:** a wooden plank is shoved at 2.5 m/s across a wooden plank floor and slides to a stop -- new surface-profile exciter

- **Mover:** wood plank 40 x 8 x 2cm, 0.42 kg, sliding flat on its broad face, contact at 30 % of its length. Audible modes: 529, 1457, 2856, 4722 Hz.
- **Target:** wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- shove speed 2.5 m/s, kinetic friction mu_k = 0.35 -> slides 0.91 m and stops after 0.73 s
- model B (surface profile): sanded boards, grain ~1.7 mm, a groove between 12 cm boards, a little household grit; roughness 6 um rms, PSD ~ k^-2.6, texture resonance 600 /m (heard at 600 x v Hz, e.g. 600 Hz at 1 m/s), meso feature every 12 cm (groove 0.3 mm)
- contact mass 10 g pressed by the plank weight (+-15 % slow wobble): airborne 6% of the slide, 562 micro-impacts per second, force kurtosis 43 (3 = Gaussian noise)
- gate: level~speed corr 0.977, silent after stop yes
- Energy share: wood-plank-40x8x2cm 40 %, wood-floor 60 %
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)

## `slide_wood-plank-40x8x2cm_shoved-2.5mps_on_concrete-slab_A-noise-model.wav`

**What you hear:** a wooden plank is shoved at 2.5 m/s across a concrete slab and slides to a stop -- old noise exciter

- **Mover:** wood plank 40 x 8 x 2cm, 0.42 kg, sliding flat on its broad face, contact at 30 % of its length. Audible modes: 529, 1457, 2856, 4722 Hz.
- **Target:** concrete slab on ground, 4 x 4 m, 15 cm thick, installed loss 0.05. Lowest modes: 31, 77, 77, 123 Hz (475 modes used).
- shove speed 2.5 m/s, kinetic friction mu_k = 0.6 -> slides 0.53 m and stops after 0.42 s
- model A (noise): fluctuating force = 25% of the Coulomb force 2.45 N at 0.5 m/s, brightness 2500 Hz per m/s
- gate: level~speed corr 0.997, silent after stop yes
- Energy share: wood-plank-40x8x2cm 100 %, concrete-slab 0 %
- Note: simply supported plate; radiates per Maidanik, coincidence 120 Hz (inefficient below)

## `slide_wood-plank-40x8x2cm_shoved-2.5mps_on_concrete-slab_B-profile-model.wav`

**What you hear:** a wooden plank is shoved at 2.5 m/s across a concrete slab and slides to a stop -- new surface-profile exciter

- **Mover:** wood plank 40 x 8 x 2cm, 0.42 kg, sliding flat on its broad face, contact at 30 % of its length. Audible modes: 529, 1457, 2856, 4722 Hz.
- **Target:** concrete slab on ground, 4 x 4 m, 15 cm thick, installed loss 0.05. Lowest modes: 31, 77, 77, 123 Hz (475 modes used).
- shove speed 2.5 m/s, kinetic friction mu_k = 0.6 -> slides 0.53 m and stops after 0.42 s
- model B (surface profile): broom-finish concrete: rough, aggregate texture ~4 mm; roughness 60 um rms, PSD ~ k^-2.4, texture resonance 250 /m (heard at 250 x v Hz, e.g. 250 Hz at 1 m/s)
- contact mass 10 g pressed by the plank weight (+-15 % slow wobble): airborne 20% of the slide, 1218 micro-impacts per second, force kurtosis 8 (3 = Gaussian noise)
- gate: level~speed corr 0.992, silent after stop yes
- Energy share: wood-plank-40x8x2cm 100 %, concrete-slab 0 %
- Note: simply supported plate; radiates per Maidanik, coincidence 120 Hz (inefficient below)

## `slide_wood-plank-40x8x2cm_shoved-2.5mps_on_steel-plate-floor_A-noise-model.wav`

**What you hear:** a wooden plank is shoved at 2.5 m/s across a steel deck plate and slides to a stop -- old noise exciter

- **Mover:** wood plank 40 x 8 x 2cm, 0.42 kg, sliding flat on its broad face, contact at 30 % of its length. Audible modes: 529, 1457, 2856, 4722 Hz.
- **Target:** steel deck plate walkway, 1 x 1 m, 6 mm, installed loss 0.005. Lowest modes: 29, 72, 72, 115 Hz (507 modes used).
- shove speed 2.5 m/s, kinetic friction mu_k = 0.3 -> slides 1.06 m and stops after 0.85 s
- model A (noise): fluctuating force = 5% of the Coulomb force 1.22 N at 0.5 m/s, brightness 20000 Hz per m/s
- gate: level~speed corr 0.991, silent after stop yes
- Energy share: wood-plank-40x8x2cm 36 %, steel-plate-floor 64 %
- Note: simply supported plate; radiates per Maidanik, coincidence 2050 Hz (inefficient below)

## `slide_wood-plank-40x8x2cm_shoved-2.5mps_on_steel-plate-floor_B-profile-model.wav`

**What you hear:** a wooden plank is shoved at 2.5 m/s across a steel deck plate and slides to a stop -- new surface-profile exciter

- **Mover:** wood plank 40 x 8 x 2cm, 0.42 kg, sliding flat on its broad face, contact at 30 % of its length. Audible modes: 529, 1457, 2856, 4722 Hz.
- **Target:** steel deck plate walkway, 1 x 1 m, 6 mm, installed loss 0.005. Lowest modes: 29, 72, 72, 115 Hz (507 modes used).
- shove speed 2.5 m/s, kinetic friction mu_k = 0.3 -> slides 1.06 m and stops after 0.85 s
- model B (surface profile): smooth steel with a raised tread pattern every 25 mm; roughness 1.5 um rms, PSD ~ k^-2.8, texture resonance 1500 /m (heard at 1500 x v Hz, e.g. 1500 Hz at 1 m/s), meso feature every 2.5 cm (bump 0.4 mm)
- contact mass 10 g pressed by the plank weight (+-15 % slow wobble): airborne 2% of the slide, 357 micro-impacts per second, force kurtosis 6 (3 = Gaussian noise)
- gate: level~speed corr 0.976, silent after stop yes
- Energy share: wood-plank-40x8x2cm 29 %, steel-plate-floor 71 %
- Note: simply supported plate; radiates per Maidanik, coincidence 2050 Hz (inefficient below)

## `slide_wood-plank-40x8x2cm_shoved-2.5mps_on_wood-floor_A-noise-model_squeaky.wav`

**What you hear:** a wooden plank is shoved at 2.5 m/s across a wooden plank floor and slides to a stop -- old noise exciter, squeaking (stick-slip)

- **Mover:** wood plank 40 x 8 x 2cm, 0.42 kg, sliding flat on its broad face, contact at 30 % of its length. Audible modes: 529, 1457, 2856, 4722 Hz.
- **Target:** wooden plank floor bay, 2.4 x 1.2 m, 22 mm boards, installed loss 0.03. Lowest modes: 37, 60, 97, 127 Hz (479 modes used).
- shove speed 2.5 m/s, kinetic friction mu_k = 0.35 -> slides 0.91 m and stops after 0.73 s
- model A (noise): fluctuating force = 10% of the Coulomb force 1.43 N at 0.5 m/s, brightness 9000 Hz per m/s
- stick-slip on: the noise is chopped by a relaxation oscillator whose rate follows speed (squeak)
- gate: level~speed corr 0.983, silent after stop yes
- Energy share: wood-plank-40x8x2cm 26 %, wood-floor 74 %
- Note: simply supported plate; radiates per Maidanik, coincidence 684 Hz (inefficient below)
