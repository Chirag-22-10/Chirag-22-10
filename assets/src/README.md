# theme source

Everything in `assets/` is generated here: 2D-only SVGs with subset fonts embedded and CSS/SMIL animation. They
make no external requests and come in a light and a dark variant each. The palette is white, black and one red, with
Valorant-style cut corners and HUD labels; pink and cyan appear only as signal colours inside the figures.

| file | what it draws | code |
|---|---|---|
| `hero-*` | top banner: stacked name with a rare glitch, red role tag, typed tagline, three numbers; a terminal prints `whoami.json` | `build.py` |
| `btn-*` | LinkedIn, email and repositories buttons | `build.py` |
| `h-*` | section headers: red index kicker, hairline, title in display caps | `build.py` |
| `fig01-reading-*` | on-device reading: app → AIDL → Engine → local ONNX or API; analog in cyan, fallback in pink | `bp.py` |
| `fig02-sync-*` | offline sync: Room outbox → worker → S3 → contract check → intake or failed API; retries in pink | `bp.py` |
| `fig03-models-*` | a model update passing five gates; the warm gate sometimes rolls back | `bp.py` |
| `fig04-dlms-*` | DLMS/COSEM over Bluetooth: every HDLC frame between phone and meter | `bp.py` |
| `fig05-splits-*` | Room-Splits on Kotlin Multiplatform; planned parts dashed | `bp.py` |
| `fig06-fieldproof-*` | FieldProof's sync state machine with idempotent uploads | `bp.py` |
| `loadout-*` | brand-colour tool pack in two tiers: primary (big tiles) and sidearms by category | `loadout.py` |

```bash
npm install                       # fonts (Big Shoulders Display, JetBrains Mono) + Simple Icons
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # fonttools + brotli
.venv/bin/python build.py         # writes ../*.svg
```

To change content, edit `KICKER`, `TAGLINE`, `STATS`, `WHOAMI`, `LINKS` and `SECTIONS` in `build.py`, the drawings in `bp.py`,
or `PRIMARY` and `SIDEARMS` in `loadout.py`. Colours live in `PALETTES` in `common.py`; the type pair lives in `FACES`.
The build asserts that every glyph exists in its font and that labels fit their boxes.

Type: Big Shoulders Display (900/800) for display caps, JetBrains Mono for labels and code, both SIL OFL 1.1.
Logos: Simple Icons (CC0); monograms stand in for brands Simple Icons does not carry.
