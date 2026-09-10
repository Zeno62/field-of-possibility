# 小宇宙 004：共相、局部与延续

Continuation of lab 003. New isolated files only; no whitepaper, homepage, release tool, or previous lab is modified.

## What this actually tests

The same six-line source S is referenced by two nine-line compositions, A (S + Kun) and B (S + Xun). C uses T, a separate six-line source initially equal in value to S. A/B are composed into an eighteen-line summary. All three branches share the same ordered upper/lower root condition. Nine/eighteen-line compositions are project constructs, not newly named classical hexagrams.

Default S/T = Meng (34 in bottom-line-as-bit-0 encoding). Reading line 2 yields Bo (32), without mutating S or advancing time. A deliberate local test action flips exactly one source bit. The default observation is A 6→5, B 6→5, C 6→6. C geometry and fixed-camera canvas pixels are unchanged. Switching the common Tai/Pi condition can affect all three, without erasing previous source changes.

This is shared reference, not magical action at a distance. Equal bit strings do not automatically become the same referenced occurrence. Drawing positions are not physical distance or relation distance.

## State / rule representation

87 records in the current fixture. One record shape is used for literal values and derived compositions:

```text
{id, label, bits: string | null, links: [{role, ref}]}
```

Sources, classical trigrams, rule opcodes, physical scale and displacement values, attribute records, structure positions and threshold values are in the current graph. Derived values are recalculated from references. A finite whitelist interpreter is still required: recording rules is not a claim that a program can run without execution semantics. Technical IDs/role keys, camera, display sampling, numerical precision and debug audit are implementation/inspection concerns, not new simulated ontology.

The displayed 33-bit world summary is NOT the complete world archive. The archive contains all current records and their links. It does not depend on event history, old evaluation caches, or saved geometry. Rebuilding and then continuing is tested against uninterrupted continuation.

Incremental recomputation uses the actual reverse dependency closure. The default single-line experiment changes 15 evaluated values, recomputes 37 records, and reuses 50 unaffected records. Recompute scope and changed outputs are deliberately reported separately.

## Explicit experimental choices

The numerical rule is carried over from lab003:

```text
exchange = max(0, 2 * (popcount(lower) - popcount(upper)))   // 0..6
local[i] == reference[i] ? exchange : 0
open[i] = potential[i] >= threshold
```

The rule is an authored toy interpretation, not a quantitative law deduced from Yijing. The common two-bank terrain is an explicit rendering fixture. Lin is provided as a middle numeric condition for threshold testing, not a complete reading of Lin.

Classical anchors only:
- Tai / Tuan: 天地交，而萬物通也 — https://ctext.org/book-of-changes/tai
- Pi / Tuan: 天地不交，而萬物不通也 — https://ctext.org/book-of-changes/pi
- Meng / Xiang: 山下出泉，蒙 — https://ctext.org/book-of-changes/meng

No Takashima quotation is invented. Selected-line reading is separate from a developer's deliberate mutation action. Neither is an automatic prediction of a future event.

## Browser delivery

`index.html` is self-contained (55,249 UTF-8 bytes). No CDN, imported modules, models, textures, external fonts, WebGL, telemetry or personal information collection. Canvas projects genuine 3D coordinates; static SVG and explicit errors remain when JavaScript/Canvas cannot run.

Git blob of the verified HTML: `b9ec3aac8685101f37143c94bc3808c33772b6b9`.

## Repeatable verification

```sh
python -m pip install playwright Pillow
CHROMIUM=/usr/bin/chromium python verify.py --html index.html --out qa
# Optional, when network access is permitted:
python verify.py --html index.html --out qa-live --url https://zeno62.github.io/field-of-possibility/lab/tai-universe-004/
```

The browser uses the page's exact implementation, not an independently reconstructed screenshot. Local verification passed 33 model groups and 48 browser checks, including:

- All 384 classical six-line single-bit mutations and inverse mutations.
- 768 source/line/target cases: incremental versus full evaluation equality.
- 384 root/line cases: valid bounds and topology counts.
- Shared-source scope, independent-source scope, untouched branch geometry and pixel equality.
- Context replacement preserves prior local changes.
- Attribute/number/rule provenance; a threshold value actually changes output.
- Physical scale changes do not change relation topology.
- Snapshot export/import, cache-free rebuild, fresh-page restore and continuation.
- Broken references, cyclic dependencies, invalid bits/opcodes and out-of-range values rejected.
- Chromium desktop 1440×1100, plus 320×568, 390×844, 430×932, 844×390 and 1024×768; DPR 1–3; no horizontal page overflow.
- Drag, keyboard, zoom, CDP touch pinch, tabs, disabled JavaScript and unavailable Canvas.

A pointer-capture failure exposed by synthetic input was guarded; actual Chromium CDP touch input subsequently verified pinch changes zoom without changing state. The phone graph was re-laid out vertically after visual inspection, rather than shrinking desktop labels into unreadable text.

Local browser testing uses `set_content` because outbound runtime DNS/navigation is unavailable. This is not physical iPhone/Safari/WebKit certification. Pages deployment is verified separately, and repository/tested file identity is checked using the Git blob SHA.

## Not implemented / not claimed

- Full feedback cycles: the evaluation dependency graph is currently acyclic, with shared references and ordered multi-input relation nodes.
- Autonomous dynamics, Wuxing self-balancing, physical erosion/fracture, true life, quantum mechanics, divination validity, or automatic mountain generation from classical texts.
- Founder participation, personal-data-derived inputs, authoritative multiplayer state or cross-device synchronization.

The useful advance is narrow: shared current structure yields bounded consequences; current graph records suffice to rebuild and continue under the same interpreter. This is a foundation for the next experiment, not evidence that the complete philosophical framework has been implemented or proved.
