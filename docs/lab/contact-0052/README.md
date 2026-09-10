# Field Lab 005.2 — 关系开合

An isolated continuation of `local-dynamics-005`. Existing labs, whitepaper pages,
public homepage and publication workflows are untouched.

## What this experiment tests

A contact is not merely a drawing line: its current open/closed state is a gua
record and affects which local transfers are allowed. The complete current graph,
with the matching versioned interpreter, is sufficient to continue the experiment.
No event history, camera state or cached terrain is required to resume.

This is an authored finite simulation, not a claim to simulate real cosmology,
quantum physics, consciousness or validated divination. The classical line order,
hexagram names and trigram imagery are inherited from Lab 005. The numerical
contact rules below are Field experimental choices, not equations in the Yijing.

## Implementation and current graph

Uses the existing same-origin `../local-dynamics-005/core.js`, version
`field-005.1`, verified Git blob `e7bf6be91a829fd21511136eab7889be83059578`.
The extension version is `field-contact-005.2`.

- 49 fixed spatial domains, 120 declared potential contacts.
- 682 initial gua records; 688 after the explicit test-participation relation.
- The inherited formed/mobile/retained quantities are bounded experimental shares,
  not physical mass, water or energy units. Their total is 1,851.
- Numeric gua use six-bit Gray encoding. Classical six-line organization codes
  retain ordinary bottom-to-top yin/yang encoding; these encodings are not conflated.
- The same region records participate in row and column group references.
- `gate-model` references the mode, opening/closing conditions and all gate records.
  Each gate also references its contact and the condition records.

For an eligible local contact, let the mobile-share difference be `d`:

```
ineligible or d <= close-gap : closed
eligible and d >= open-gap  : open
otherwise                   : retain the current gate state
```

Default `open-gap=4`, `close-gap=1`. Both values are numeric gua in the current
network. The gap between them permits persistence of a current contact state;
this is a small hysteresis experiment, not a history lookup.

At one local scheduler step, the first incident gate requiring change is updated.
If no incident gate needs change, the inherited local operation may transfer ONE
share in the domain or across ONE open contact. A gate change and a quantity
transfer never occur in the same microstep. The scheduler is also in the graph.
There are 64 scheduler steps per displayed round; 49 address regions.

The eight inherited local operations are reused, not replaced by an animation.
Turning off `gate-mode` reproduces Lab 005 quantity evolution. The fixed/dynamic
preset exposes that ablation. The Tai/Pi preset changes only the common six-line
source; the local-intervention preset changes one B source through a participant
relation. Previewing a moving line does not commit a change.

## Reproducible observations

Starting with identical Tai graphs, commit R19 line 4 in B: Dui (兑) becomes Jie
(节). No quantity or gate is directly changed at commitment. After 64 rounds:

| Readout | A | B |
| --- | ---: | ---: |
| Total shares | 1851 | 1851 |
| Open contacts | 51 | 58 |
| Connected components | 10 | 6 |
| Largest component size | 33 | 43 |
| Cumulative gate openings | 109 | 106 |
| Cumulative gate closings | 58 | 48 |
| Quantity transfers | 892 | 827 |

The worlds differ in 16 of 49 domains and 11 gate states. These figures describe
this fixed test, not a guarantee that every single-line intervention spreads.
Diagnostics and event counters are not used as inputs to subsequent updates.

## Limits retained rather than hidden

1. The 120 potential spatial contacts remain fixed. Gate openness evolves; arbitrary
   creation/deletion of spatial adjacency is not implemented.
2. Connected components are derived readouts with references to current regions
   and gates. They are NOT yet self-maintaining higher-level organizations and do
   not feed back into the dynamics.
3. The inherited common-contact rule still distinguishes only eight contact classes
   among 64 root hexagrams. A correct names table is not full 64-hexagram semantics.
4. Finite deterministic runs enter cycles. Exact full snapshots at round boundaries
   repeat for pristine Tai at rounds 93/94 and Pi at 43/44 (one-round periods).
   This does not mean no events occur within the repeated round. No ongoing
   novelty or unlimited world creation is claimed; no random drift hides cycles.
5. Initial ridges and the staggered geometric arrangement are shared test fixtures,
   not proof that mountains/rivers arise automatically from the classics.
6. Full Five-Phase dynamics, founder creation and multiplayer authority/persistence
   are not implemented. No private user information or telemetry is collected.

## Self-observation

Run from this folder with the sibling baseline present:

```
node checks.js
python verify.py
```

The Python runner requires Playwright and Chromium at `/usr/bin/chromium`.
25 model checks pass, including 384 single-line inverse mutations, local gate and
quantity changes, 16,384-step conservation/bounds, read-only previews, exact
snapshot continuation, input validation, ablation and cycle reporting.

Browser checks use Chromium 144.0.7559.96 at 1440x1080, 390x844, 320x568, 430x932
and 844x390, DPR 1–3. Checks cover actual canvas painting, no horizontal overflow,
preview nonmutation, local commitment, pause/resume, mobile tabs, camera
nonmutation, real file-input restoration and disabled-script/script-error/Canvas
failure fallback. The default camera was adjusted after inspecting captured images.

Authoring-environment navigation is restricted. The runner uses `set_content`
with intercepted same-origin requests serving the exact file bytes. This is NOT
physical iPhone/Safari/WebKit testing or live-site browser certification. Git blob
identity and GitHub Pages deployment are checked separately.

Runtime HTML plus the three scripts: 42,921 UTF-8 bytes before compression,
including the shared baseline. No CDN, WebGL, model, image or font download is
required. The visible fallback explicitly identifies itself as static, not running.

The current-state export deliberately excludes diagnostic histories and derived
component caches; restore requires this interpreter version.
