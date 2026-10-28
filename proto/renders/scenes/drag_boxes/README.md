# Cardboard and steel boxes pulled across concrete

Small (30 x 20 x 20 cm) and large (60 x 40 x 40 cm) empty boxes of corrugated cardboard and sheet steel, each pulled in one long drag across the same concrete slab with model C (scenes/drag.py). One shared gain for all four files.

All files in this folder share one gain: louder here = louder in the physics.
Stems in `stems/` are each sound source on its own (same gain).

## `drag_cardboard-box-30x20x20cm_pulled-3.4m-at-0.5mps_on_concrete-slab.wav`

**What you hear:** a small empty cardboard box is pulled in one long drag across a concrete slab

- **Mover:** cardboard box 30 x 20 x 20cm, 4 mm walls, 0.18 kg, empty, sliding on its bottom panel. Audible modes: 239, 460, 736, 828 Hz.
- **Target:** concrete slab on ground, 4 x 4 m, 15 cm thick, installed loss 0.05. Lowest modes: 31, 77, 77, 123 Hz (475 modes used).
- one pull: 0.5 m/s +-12 % (slow hand variation), 3.4 m in 7.5 s, smooth 0.6 s start and stop; normal force = box weight 1.8 N (+-25%)
- contact mass 3.0 g (bottom panel point impedance at 1 kHz)
- model C: 6 asperity tracks, scales 60-200 um, force kurtosis 3
- level trim -6 dB (designer setting, not physics: this file is that much quieter than the shared gain makes it)
- Energy share: cardboard-box-30x20x20cm 100 %, concrete-slab 0 %
- Note: bottom panel modes (simply supported, glued/taped corrugated board loss 0.05); coincidence 4439 Hz
- Note: floor rubs the panel at (37%, 43%) of its sides
- Note: contact damping: loss factor +0.1 while in contact (dragged flat on the floor)
- Note: simply supported plate; radiates per Maidanik, coincidence 120 Hz (inefficient below)

## `drag_cardboard-box-60x40x40cm_pulled-3.4m-at-0.5mps_on_concrete-slab.wav`

**What you hear:** a large empty cardboard box is pulled in one long drag across a concrete slab

- **Mover:** cardboard box 60 x 40 x 40cm, 4 mm walls, 0.72 kg, empty, sliding on its bottom panel. Audible modes: 60, 115, 184, 207 Hz.
- **Target:** concrete slab on ground, 4 x 4 m, 15 cm thick, installed loss 0.05. Lowest modes: 31, 77, 77, 123 Hz (475 modes used).
- one pull: 0.5 m/s +-12 % (slow hand variation), 3.4 m in 7.5 s, smooth 0.6 s start and stop; normal force = box weight 7.0 N (+-25%)
- contact mass 3.0 g (bottom panel point impedance at 1 kHz)
- model C: 6 asperity tracks, scales 60-200 um, force kurtosis 3
- level trim -6 dB (designer setting, not physics: this file is that much quieter than the shared gain makes it)
- Energy share: cardboard-box-60x40x40cm 100 %, concrete-slab 0 %
- Note: bottom panel modes (simply supported, glued/taped corrugated board loss 0.05); coincidence 4439 Hz
- Note: floor rubs the panel at (37%, 43%) of its sides
- Note: contact damping: loss factor +0.1 while in contact (dragged flat on the floor)
- Note: simply supported plate; radiates per Maidanik, coincidence 120 Hz (inefficient below)

## `drag_sheet-steel-box-30x20x20cm_pulled-3.4m-at-0.5mps_on_concrete-slab.wav`

**What you hear:** a small empty sheet-steel box is pulled in one long drag across a concrete slab

- **Mover:** sheet-steel box 30 x 20 x 20cm, 0.8 mm walls, 2.01 kg, empty, sliding on its bottom panel. Audible modes: 69, 133, 239, 388 Hz.
- **Target:** concrete slab on ground, 4 x 4 m, 15 cm thick, installed loss 0.05. Lowest modes: 31, 77, 77, 123 Hz (475 modes used).
- one pull: 0.5 m/s +-12 % (slow hand variation), 3.4 m in 7.5 s, smooth 0.6 s start and stop; normal force = box weight 19.7 N (+-25%)
- contact mass 9.7 g (bottom panel point impedance at 1 kHz)
- model C: 6 asperity tracks, scales 60-200 um, force kurtosis 3
- Energy share: sheet-steel-box-30x20x20cm 98 %, concrete-slab 2 %
- Note: bottom panel modes (simply supported, welded box loss 0.002); coincidence 15373 Hz
- Note: floor rubs the panel at (3%, 50%) of its sides
- Note: contact damping: loss factor +0.1 while in contact (dragged flat on the floor)
- Note: simply supported plate; radiates per Maidanik, coincidence 120 Hz (inefficient below)

## `drag_sheet-steel-box-60x40x40cm_pulled-3.4m-at-0.5mps_on_concrete-slab.wav`

**What you hear:** a large empty sheet-steel box is pulled in one long drag across a concrete slab

- **Mover:** sheet-steel box 60 x 40 x 40cm, 1 mm walls, 10.05 kg, empty, sliding on its bottom panel. Audible modes: 22, 42, 75, 121 Hz.
- **Target:** concrete slab on ground, 4 x 4 m, 15 cm thick, installed loss 0.05. Lowest modes: 31, 77, 77, 123 Hz (475 modes used).
- one pull: 0.5 m/s +-12 % (slow hand variation), 3.4 m in 7.5 s, smooth 0.6 s start and stop; normal force = box weight 98.6 N (+-25%)
- contact mass 15.2 g (bottom panel point impedance at 1 kHz)
- model C: 6 asperity tracks, scales 60-200 um, force kurtosis 3
- Energy share: sheet-steel-box-60x40x40cm 99 %, concrete-slab 1 %
- Note: bottom panel modes (simply supported, welded box loss 0.002); coincidence 12298 Hz
- Note: floor rubs the panel at (3%, 50%) of its sides
- Note: contact damping: loss factor +0.1 while in contact (dragged flat on the floor)
- Note: simply supported plate; radiates per Maidanik, coincidence 120 Hz (inefficient below)
