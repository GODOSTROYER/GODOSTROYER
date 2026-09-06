# Using this profile

This is the GitHub profile README for **GODOSTROYER / Arnav Bule**. Its images live in this repository, with no third-party stats-card server required.

## Preview locally

Use Python 3.11 or newer. No pip packages are needed for normal generation.

```sh
python scripts/render_profile.py
python scripts/preview.py --serve
```

Open http://127.0.0.1:8765/preview/. The controls show the actual README with GitHub-style typography in desktop/mobile widths and light/dark themes. GitHub remains the final rendering authority; its spacing may differ slightly.

## Put it on the profile

GitHub displays the root README of a public repository named exactly **GODOSTROYER**, owned by **GODOSTROYER**. Copy this project's shipping files into that repository, or publish this repository under that name after reviewing the content. The repository, assets and workflow must be present together; copying README.md alone loses the local images.

The local preview, research notes, caches, and discovery scratch data are excluded by .gitignore. No public profile has been changed merely by creating these files.

## Change the content

Edit `profile.config.json`, then run `python scripts/render_profile.py`. It controls identity, focus, project descriptions, project links, and screenshot paths. Write factual descriptions of what each project currently does. Replace screenshots with real product images and update their provenance in `assets/projects/SOURCES.md`.

The three featured projects are Sentinel, Zenith.ai and QR Tree Studio. QR Tree Studio uses the open-source magic-tree-qr renderer; its attribution remains in the profile. Zenith's cloud plan/export limitation is stated next to its demonstration.

## Update the activity

```sh
python scripts/update_profile.py
python scripts/render_profile.py
python -m unittest discover -s tests -v
python scripts/render_profile.py --check
```

On GitHub, the included Action refreshes public data daily, manually, and on relevant source changes. Enable Actions for the profile repository. See [AUTOMATION.md](AUTOMATION.md) for permissions and failure behavior. Optional contribution data needs an appropriate GitHub token; the profile works without it and does not invent contribution counts.

## Assets and accessibility

The hero includes separately composed mobile artwork and light/dark versions. Reduced-motion preferences disable the traveling signal. Main text remains visible without animation; native HTML descriptions and links accompany project images. The type is converted from licensed Space Grotesk into vector outlines, so it renders without an external font service. Font license and original source are in `assets/fonts/`.

The work diagram counts public, non-fork, non-archived repositories by their primary language, excluding this profile repository. It is not a skills score or contribution heatmap.
