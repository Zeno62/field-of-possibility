# Field Manifestation Lab 004

Purpose: test whether the same trigram-derived manifestation kernel can generate all 64 ordered upper/lower compositions without per-hexagram drawing templates.

## What is classical source material
- Eight trigrams, line structures, traditional natural images and Later-Heaven directions.
- Shuo Gua action phrases such as movement, dispersal, moistening, illumination, stopping, delight/opening, governing and storing.
- Later traditional Five-Phase correspondences: Zhen/Xun Wood, Li Fire, Kun/Gen Earth, Qian/Dui Metal, Kan Water.
- 64 hexagram names generated from ordered upper/lower trigram pairs.

## What is experimental Field abstraction
- A solid line is rendered as one continuous local band; a broken line as two separated lobes.
- Yang/yin polarity shifts an upper/lower trigram field upward/downward. This is used to test whether Tai and Pi can diverge without a name-specific branch.
- Later-Heaven direction rotates the local field.
- The overlap index is only a diagnostic of this experimental geometry, not a classical Yijing quantity.
- Five-Phase relations are currently read-only diagnostics; they do not yet drive geometry.

## Automated checks
The self-check iterates all 64 hexagrams and all six single-line mutations (384 cases), verifies mutation reversibility, verifies 64 distinct field signatures, checks that moving-line preview does not mutate the current gua, and checks desktop/mobile overflow.
