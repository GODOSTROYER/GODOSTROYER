# Space Grotesk artwork source

The identity wordmark and supporting prose use outlined Space Grotesk, designed
by Florian Karsten. Copyright 2020 The Space Grotesk Project Authors.

- Official distribution: https://github.com/google/fonts/tree/main/ofl/spacegrotesk
- Original project: https://github.com/floriankarsten/space-grotesk
- License: SIL Open Font License 1.1; the full license is in `OFL.txt`.
- Retrieved: 2026-09-06.

`SpaceGrotesk-variable.ttf` is the unmodified official source. The reproducible
author-time `build_outlines.py` uses fontTools to instantiate weights 400 and 700
and extract Latin glyph paths into `space-grotesk-outlines.json`. The identity
renderer uses only Python's standard library and emits self-contained SVG paths;
viewers never load a font. The extracted outlines remain under the included OFL.

The title has natural glyph spacing (zero tracking). The geometric signal artwork
is original; only the lettering is derived from this licensed font.
