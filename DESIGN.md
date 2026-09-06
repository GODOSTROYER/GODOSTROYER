---
name: Arnav Bule GitHub Profile
description: A developer terminal with original branching signal artwork and inspectable public work.
colors:
  dark-bg: "#10191b"
  dark-surface: "#162225"
  dark-text: "#edf2e8"
  dark-muted: "#a6b5ad"
  dark-accent: "#bce16b"
  dark-warm: "#f4b68a"
  light-bg: "#f3f5ec"
  light-surface: "#e8edde"
  light-text: "#172722"
  light-muted: "#50645a"
  light-accent: "#47691e"
  light-warm: "#88441d"
typography:
  display-desktop:
    fontFamily: "Space Grotesk"
    fontSize: "88px"
    fontWeight: 700
    letterSpacing: "0"
  display-mobile:
    fontFamily: "Space Grotesk"
    fontSize: "73px"
    fontWeight: 700
    letterSpacing: "0"
  prose-desktop:
    fontFamily: "Space Grotesk"
    fontSize: "20px"
    fontWeight: 400
  prose-mobile:
    fontFamily: "Space Grotesk"
    fontSize: "24px"
    fontWeight: 400
  terminal-desktop:
    fontFamily: "Cascadia Code, SFMono-Regular, Consolas, monospace"
    fontSize: "15px"
  terminal-mobile:
    fontFamily: "Cascadia Code, SFMono-Regular, Consolas, monospace"
    fontSize: "22px"
rounded:
  artwork: "8px"
  console: "4px"
spacing:
  hero-inset-desktop: "64px"
  hero-inset-mobile: "40px"
  console-text-inset: "23px"
components:
  console-dark:
    backgroundColor: "{colors.dark-surface}"
    textColor: "{colors.dark-text}"
    rounded: "{rounded.console}"
    typography: "{typography.terminal-desktop}"
  console-light:
    backgroundColor: "{colors.light-surface}"
    textColor: "{colors.light-text}"
    rounded: "{rounded.console}"
    typography: "{typography.terminal-desktop}"
---

# Design System: Arnav Bule GitHub Profile

## Overview

**Creative North Star: “A builder's terminal.”** This is an extracted description of the accepted developer-terminal direction, not a new brand workshop. Graphite and warm paper support strong lettering, a small console, and original branching circuit geometry. Descriptive language remains provisional; the implemented values above are the current reference.

This system has three boundaries: custom SVG identity and data artwork, GitHub-controlled README content, and a separate local preview. Tokens above describe the custom artwork only. Source truth is `scripts/render_identity.py`; `scripts/render_profile.py` composes the README and work map. Edit content in `profile.config.json`, then regenerate; do not hand-edit generated assets.

**Key Characteristics:**

- Quiet green signal paths with one warm identity response.
- Strong outlined lettering paired with readable terminal text.
- Real project imagery and direct textual links.
- Theme-specific artwork and a recomposed mobile introduction.

## Colors

### Primary

The paired accent tokens provide the green signal, command prompts, short top rule, console rail, and repository nodes. Dark mode uses a pale lively green; light mode uses a deeper moss green for legibility.

### Secondary

The paired warm tokens distinguish the `whoami` response, including the handle. Their role is limited and informational.

### Neutral

Background and inset surface tokens form a subtle two-level composition. Text tokens carry primary reading; muted tokens carry the tagline, focus text, and quieter geometry. Each artwork variant uses its complete theme palette.

**The Host Boundary Rule.** These colors do not override GitHub's page, links, headings, or code labels. The local approximation in `scripts/preview.py` has its own GitHub-style body palette and separate control-shell palette.

## Typography

Display and supporting hero prose use Space Grotesk, with weights 700 and 400 extracted to SVG glyph paths. The official unmodified font, SIL OFL 1.1 license, and reproducible extraction are recorded in `assets/fonts/README.md`. Viewers load no external font. Title tracking is natural, with no added spacing; the uppercase name is width-capped at 635 desktop or 565 mobile SVG units, so actual scale can shrink to fit.

The terminal uses the fallback stack in the frontmatter. Unsupported configured glyphs in the outline renderer fall back to SVG monospace text. The work map uses `Consolas, Liberation Mono, monospace`, with larger labels in its mobile variant.

All artwork sizes are intrinsic SVG units, not guaranteed rendered CSS pixels. GitHub controls README body type, headings, links, and inline code. The preview approximates these with a system sans stack (16px desktop, 15px mobile); that is a review aid, not a portable README typography contract.

## Layout

The identity has desktop (1200 × 460) and mobile (640 × 720) canvases. Desktop places the name and console left and a tall branching trace right. Mobile puts the console above a compressed horizontal network. Console dimensions are 615 × 151 desktop and 560 × 185 mobile.

README `<picture>` sources switch at a maximum viewport width of 600px and select dark assets through `prefers-color-scheme`; light is the fallback. Images carry a width of 1200 and scale within their host. The README remains a single column: introduction and links, three project sections, public workbench updates, work map, disclosure, and contact links.

The work map uses up to four language groups with 12 nodes per row; its height grows with the data. Desktop groups run across a 1200-unit canvas; mobile uses two columns in 640 units. Nodes represent actual included repositories, not a decorative fixed count.

The local preview article is capped at 1012px with 32px/40px padding, changing to 20px/16px at 600px. Its optional mobile frame is 390px wide. The wrapper controls reflow at 700px. None of these wrapper measurements define GitHub itself.

## Elevation & Depth

The artwork uses no shadows. Depth comes from the inset console tone, thin geometry, and varied line opacity. The signal's faint grid and dotted circle sit behind its brighter main route. Project screenshots retain the visual systems of their actual applications.

## Shapes

Artwork containers have gently rounded corners; consoles are slightly tighter. A thin vertical console rail echoes the branching signal. The geometry combines vertical, horizontal, and diagonal runs, angular leaf forms, and small circular junctions. Preserve the original authored paths rather than substituting generic icons.

## Components

**Identity console.** Two commands establish identity and focus. The handle belongs in the warm `whoami` response. Prompts use the green accent, command text uses primary text, and focus output uses muted text.

**Signal trace.** A single pulse travels over a persistent route on a 12-second linear infinite cycle. It fades in and out rather than blinking. `prefers-reduced-motion: reduce` removes and hides the pulse while leaving the complete static artwork readable.

**Selected work.** Sentinel, Zenith.ai, and QR Tree Studio each have a native heading, linked real image, concise description, inline-code stack labels, and explicit source/demo/release links where available. QR Tree Studio uses a captured seasons GIF with a static image selected for reduced motion. Keep attribution and limitations adjacent to the relevant project. Link arrows stay attached with a nonbreaking space.

**Work map.** One node equals one public non-fork, non-archived repository, excluding the profile repository. The image alt text includes actual grouped counts from the same distribution function as the drawing. The graph describes distribution, not proficiency.

**Native disclosure and links.** Additional work uses `<details>`/`<summary>`; actions are ordinary anchors. Their interaction and focus treatment on GitHub belong to the host. JavaScript width/theme controls and custom focus outlines exist only in the local preview shell.

## Do's and Don'ts

- **Do** keep light/dark and mobile/desktop artwork generated from shared sources.
- **Do** preserve meaningful image alternatives and a complete static reading under reduced motion.
- **Do** use inspectable project captures and maintain their provenance.
- **Do** keep link arrows attached and derive graph text and nodes from the same data.
- **Don't** infer exact GitHub sanitization or Markdown spacing from the local preview.
- **Don't** introduce arbitrary JavaScript into the README or external font/image services into the identity.
- **Don't** convert repository counts into skill scores or decorate the profile with unsupported claims.
