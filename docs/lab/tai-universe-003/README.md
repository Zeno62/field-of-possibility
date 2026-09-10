# Field Lab 003 — Tai / Pi and local line changes

This is an isolated engineering experiment, not whitepaper text, a divination reading, a complete Yijing dynamics model, or a simulation of physical reality. No production entry point is modified.

## Runtime

`index.html` contains all CSS, JavaScript and an SVG no-script fallback. It makes no runtime HTTP requests for libraries, models, fonts or textures. It uses a small three-dimensional vertex model rendered by Canvas 2D projection, not WebGL. Both mouse/pointer rotation and touch pinch code are present. Desktop arrow keys and zoom buttons are also supported. No personal data, telemetry or multiplayer persistence is implemented.

The page never intentionally hides the fallback until the corresponding canvas has successfully rendered. A visible error message replaces silent failure. Mobile displays one comparison at a time. There is no perpetual animation loop; camera changes never mutate the world model.

## What is actually implemented

- Bottom-first six-line words, standard upper/lower lookup, and an XOR flip of one selected line.
- One local relationship gua, initially Meng, used by two ordered nine-line compositions, which are themselves combined into eighteen lines. These longer compositions do not receive invented classical hexagram names.
- Shared references and derivation provenance. Each displayed geometric primitive identifies its source gua. Numeric relation summaries are represented as gua records as well as derived rendering data.
- A root-condition Tai/Pi comparison using the same child words and the same drawing function.
- Trend inspection and explicit test mutation are separate. Selecting a line or displaying its corresponding hexagram does not advance time or commit the change.
- Current graph and tests can be exported as JSON.

## Explicit, replaceable assumptions

The directional projection is `d(g) = (2 * popcount(g) - 3) / 3` and inward alignment is `clamp((d(lower) - d(upper)) / 2, 0, 1)`. The six passage constraints compare local lines with a fixed initial support configuration. These are OUR TEST CONVENTIONS, not equations derived from the classics. Tai/Pi do not have separate renderer branches, but the semantic projection is deliberately designed to test a reading of inward/outward relations.

The two terrain banks are a shared presentation scaffold. Their shape does not establish that the model has generated mountains, rivers, ecosystems, consciousness, or a self-evolving universe. No full Wuxing interaction, founder-based creation or server persistence is claimed. The `layout` gua identifies the presentation fixture; it does not magically encode every implementation constant. Computational conventions remain explicit in source.

## Verification

`window.FieldLab.check()` runs 14 checks, including all 384 six-line/single-line-flip combinations. Tests verify deterministic rebuilding, current-versus-trend separation, shared dependent recomposition and unchanged unrelated branches.

The development verification used Chromium through Playwright at desktop (1440 x 1050), phone-size (320 x 568, 390 x 844, 430 x 932) and landscape (844 x 390) viewports, including device pixel ratios 1–3 and JavaScript-disabled fallback. JavaScript errors and horizontal overflow were checked. These are emulated viewport tests, NOT physical iPhone/Safari certification. The container's browser policy blocks URL navigation, so local browser tests execute the complete HTML with `set_content`. GitHub Pages deployment is verified separately.

`verify.py` reruns the non-visual browser checks against this exact file; it requires Python Playwright and Chromium. It prints a JSON report and exits nonzero on failure.

## Classical reference points

- Tai: upper Kun, lower Qian.
- Pi: upper Qian, lower Kun.
- Meng: upper Gen, lower Kan; changing line 2 gives Bo (upper Gen, lower Kun).
- Higher 9/18-line compositions and the numerical projection are modern experimental constructions.

The project-specific reading of moving line and corresponding gua follows the user's supplied project instructions; this experiment does not claim those instructions are verbatim Takashima text.
