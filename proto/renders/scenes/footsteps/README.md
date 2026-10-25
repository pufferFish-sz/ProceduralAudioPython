# Footsteps on gravel / dirt / grass

The same four-step walk on each surface. Only the aggregate texture preset changes.

Levels here are NOT physical: the aggregate layer is normalized per layer, so compare textures, not loudness. All files share one gain.
Stems in `stems/` are each sound source on its own (same gain).

## `walk_4-steps_every-0.55s_on_gravel.wav`

**What you hear:** four footsteps (heel then toe) on loose gravel; only the surface texture is synthesized

- surface model: every stone its own pitch (PhISEM v2)
- gait: 4 steps, 0.55 s apart; heel 5 ms attack / 70 ms decay, toe hump +150 ms at 60 %
- Energy share: gravel-texture 100 %

## `walk_4-steps_every-0.55s_on_dirt.wav`

**What you hear:** four footsteps (heel then toe) on packed dirt; only the surface texture is synthesized

- surface model: low, dull, fast-dying grains + low rustle (PhISEM v2)
- gait: 4 steps, 0.55 s apart; heel 5 ms attack / 70 ms decay, toe hump +150 ms at 60 %
- Energy share: dirt-texture 100 %

## `walk_4-steps_every-0.55s_on_grass.wav`

**What you hear:** four footsteps (heel then toe) on grass; only the surface texture is synthesized

- surface model: layered v3: swishing blades + stem snaps + thin bed
- gait: 4 steps, 0.55 s apart; heel 5 ms attack / 70 ms decay, toe hump +150 ms at 60 %
- Energy share: grass-texture 100 %

## `walk_4-steps_every-0.55s_on_grass-v2-old.wav`

**What you hear:** four footsteps (heel then toe) on grass, OLD v2 preset; only the surface texture is synthesized

- surface model: v2: 80 % stationary 2.8-11 kHz hiss (kept for A/B)
- gait: 4 steps, 0.55 s apart; heel 5 ms attack / 70 ms decay, toe hump +150 ms at 60 %
- Energy share: grass-v2-old-texture 100 %
