# Field Lab 005 — 共相与局变

New isolated experiment. Existing `manifestation-004`, `tai-universe-004`, `tai-universe-003`, `world-001`, whitepaper pages and publication workflows are untouched.

## Purpose

Test a finite, inspectable current-state network with real local updates. This is not a claimed simulation of physical cosmology, consciousness, divination accuracy, or a completed Yijing dynamics.

Two worlds start with identical quantities, local roles, positions and contacts. One local six-line source in B can be changed through an explicit test-participant relation. Both worlds then execute the same interpreter. Drawing does not drive simulation.

## Current network

- 49 coarse spatial domains and 120 contact relations.
- 558 initial gua records, 564 after a test-participation relation is present.
- Each domain has a six-line organization source and three bounded quantity gua: formed, mobile, retained. These are experimental shares, not physical mass/water/energy units.
- Quantity gua use Gray-coded six-bit integers 0..63. A unit increment/decrement changes one encoding bit. Classical hexagram line codes remain ordinary ordered yin/yang lines; they are not Gray-coded.
- Row and column compositions reference the same region records. They demonstrate overlapping membership, not extra forces or instantaneous distant effects.
- Contact port, common source, enabled-rule records, thresholds, and scheduler position are in the current graph.
- IDs/role keys and the versioned JavaScript interpreter are implementation contracts. No claim is made that data execute without interpretation.

Current snapshots contain the records and references, not just a six-line summary, hash, seed, event log or cached terrain. Restore requires the same interpreter version. Snapshot import validates record widths, required topology, references, opcodes, limits and size.

## Classical anchors versus authored choices

Classical anchors:
- Ordered line structures, trigram names and 64 upper/lower combinations.
- Shuo Gua: 健、順、動、入、陷、麗、止、說, and its action imagery.
- Tai: 天地交，而萬物通也.
- Pi: 天地不交，而萬物不通也.

Sources:
- https://ctext.org/book-of-changes/shuo-gua
- https://ctext.org/book-of-changes/tai
- https://ctext.org/book-of-changes/pi

Authored experimental mapping, not classical equations:
- Upper trigram selects a local operation; lower three lines supply local contact conditions.
- A local contact needs at least one outward line at its corresponding port.
- A cross-domain common contact pairs a lower outward 1 with an upper inward 0.
- Qian: ordered transport; Dui: bidirectional local leveling; Li: release retained shares; Zhen: mobilize formed shares; Xun: outward diffusion with a direction tie-break; Kan: transfer down a combined-quantity difference; Gen: retain a share as formed; Kun: store a mobile share.
- Each event transfers ONE share in-domain or across ONE open contact. There is no remote overwrite, new quantity creation, random drift, wall-clock input or stored collapse animation.
- Initial twin ridges, 7x7 staggered spatial embedding, local trigram arrangement, numeric thresholds, scheduler and visual scales are explicit test scaffolding.

Moving-line reading is separate from actual commitment. Computing the corresponding hexagram does not mutate the world or promise a future event. The commit button deliberately changes one local source bit, after establishing a player/test and participant-contact gua. No personal information, fingerprinting, account lookup or telemetry is performed.

## Observations from the actual implementation

Fixed local intervention: R19 is Dui; line 4 flips it to Jie. At commitment only that source changes; no quantity is edited. After 1,024 microsteps (16 rounds), A and B differ in 16 of 49 domains. Both retain exactly 1,851 total shares. Cross-domain transfers in this experiment: A 54, B 63.

Pristine Tai/Pi comparison after 4,096 microsteps (64 rounds):
- Tai: 93 open contacts, 178 cross-domain transfers.
- Pi: 84 open contacts, 0 cross-domain transfers.
- Both: 1,851 total shares.
- Disabling only the common-contact condition makes their quantity evolution identical. This tests the source of the difference; it does not independently prove a classical interpretation.

Eight operations all execute in the fixed Tai run. Disabling each in turn changes quantity outputs in 27, 27, 15, 12, 27, 19, 17 and 30 domains respectively.

Negative observations are retained:
1. The common-contact interpretation reads only three paired conditions, so all 64 common hexagrams currently collapse to EIGHT contact classes. The full names table is not a full semantic dynamics.
2. Fixed-rule worlds enter cycles. Exact current-snapshot comparison at round boundaries finds a two-round cycle: Tai first seen at round 63 and repeated at 65; Pi at 54 and 56. Continued new organization is NOT claimed.
3. Existing terrain is a shared numerical fixture. This iteration does not prove that mountains and rivers spontaneously arise from the classical text.
4. The layout graph is fixed. Contact openness changes, but this is not yet an evolving hypergraph topology with new higher-order organizations.
5. Wuxing, founder creation, cross-device persistence and multiplayer authority are not implemented.

## Self-observation and reproducibility

Model tests: `checks.js`, also executable with Node:

```sh
node -e "console.log(JSON.stringify(require('./checks.js')(),null,2))"
```

23 groups pass: all 384 single-line inverse mutations, six-bit Gray round trips, shared references, preview nonmutation, one-local-bit commitment, participant records, branch isolation, 16,384-step conservation/bounds, contact-local updates, cache/log-free snapshot continuation, key-order independence, common-state comparison and ablation, eight-operation activation and ablations, 64 root states, no RNG or wall-clock dependency, invalid snapshot rejection and a diagnostic exposing the eight contact classes.

Browser test runner: `verify.py`.

```sh
python -m pip install playwright
python verify.py
```

The runner uses Chromium at `/usr/bin/chromium`. Five viewport cases: 1440x1100, 390x844, 320x568, 430x932, 844x390, DPR 1-3. Tested painting, no JS errors, no horizontal overflow, preview nonmutation, one-bit commitment, 16-round comparison, camera nonmutation, mobile tabs, actual file-input restoration, pause/resume and no-JavaScript fallback.

Browser navigation in the authoring environment is administratively blocked; tests use `set_content` with inline copies of the exact local classic scripts. This is not an iPhone/Safari/WebKit or live-site browser certification. Repository file identity is checked by Git blob SHA, and Pages deployment is checked separately.

Runtime HTML + three scripts total 46,742 UTF-8 bytes before compression, with no third-party runtime downloads, WebGL dependency, images, models, external fonts or build dependencies. The page uses four same-origin files. Its static fallback explicitly states that it is not a running simulation.
