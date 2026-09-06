"""Original identity artwork for Arnav Bule, drawn from first principles.

The branching trace composition is original vector geometry (not a stock asset,
icon pack, or traced illustration). Importing this module has no side effects.
"""

from __future__ import annotations

import json
from pathlib import Path
import textwrap
from functools import lru_cache
from xml.sax.saxutils import escape


THEMES = {
    "dark": dict(bg="#10191b", surface="#162225", text="#edf2e8",
                 muted="#a6b5ad", accent="#bce16b", warm="#f4b68a"),
    "light": dict(bg="#f3f5ec", surface="#e8edde", text="#172722",
                  muted="#50645a", accent="#47691e", warm="#88441d"),
}


@lru_cache(maxsize=1)
def _lettering() -> dict:
    source = Path(__file__).resolve().parents[1] / "assets/fonts/space-grotesk-outlines.json"
    return json.loads(source.read_text(encoding="utf-8"))


def _outline(text: str, x: float, y: float, size: float, color: str,
             weight: int = 400, max_width: float = 1000) -> str:
    """Place precomputed, OFL-licensed glyphs with natural (zero) tracking."""
    font = _lettering()[str(weight)]
    glyphs = font["glyphs"]
    if any(char not in glyphs for char in text):
        # Preserve arbitrary configured Unicode instead of losing characters.
        return (f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
                f'font-family="monospace">{_text(text)}</text>')
    advance = sum(glyphs[char][0] for char in text)
    scale = min(size / font["units"], max_width / max(advance, 1))
    parts = []
    position = 0
    for char in text:
        width, path = glyphs[char]
        if path:
            parts.append(f'<path transform="translate({position} 0)" d="{path}"/>')
        position += width
    return (f'<g fill="{color}" transform="translate({x} {y}) scale({scale:.6f} {-scale:.6f})" '
            f'aria-label="{_text(text)}">{"".join(parts)}</g>')


def _text(value: object) -> str:
    return escape(str(value), {'"': "&quot;", "'": "&apos;"})


def _lines(value: object, width: int, limit: int) -> list[str]:
    if isinstance(value, (list, tuple)):
        value = " / ".join(str(item) for item in value)
    lines = textwrap.wrap(" ".join(str(value).split()), width=width)
    if len(lines) > limit:
        lines = lines[:limit]
        lines[-1] = lines[-1].rstrip(" .") + "…"
    return lines


def _signal(theme: dict[str, str], mobile: bool) -> str:
    """A rooted, directed geometric graph; all coordinates are authored here."""
    # Desktop art is a tall growth network; mobile is a compact horizontal fan.
    transform = "translate(170 465) scale(.72 .55)" if mobile else "translate(770 44)"
    branches = [
        "M210 348V298L143 231V158L104 119V70",
        "M210 298V237L253 194V114L304 63V31",
        "M143 231H96L58 193V146",
        "M143 158L191 110V62",
        "M253 194H293L333 154V112",
        "M210 237L190 217V172",
        "M253 114L222 83V42",
        "M104 119H66L39 92V61",
        "M304 63H343L362 44V23",
        "M210 348L159 399H83",
        "M210 348L250 388H335",
        "M159 399L145 413H119",
        "M250 388L280 418H311",
    ]
    leaves = [
        "M104 70V36L72 4V37Z", "M191 62V31L220 2V32Z",
        "M304 31V3L277 30V57Z", "M58 146V118L30 90V118Z",
        "M333 112V81L364 50V81Z", "M190 172V147L167 124V149Z",
        "M222 42V18L200 -4V20Z", "M39 61V40L16 17V38Z",
        "M362 23V3L384 -19V1Z",
    ]
    nodes = [(143, 231), (253, 194), (104, 119), (210, 298), (304, 63)]
    paths = "".join(f'<path d="{path}"/>' for path in branches)
    foliage = "".join(f'<path d="{path}"/>' for path in leaves)
    points = "".join(
        f'<circle cx="{x}" cy="{y}" r="3.5" fill="{theme["bg"]}" '
        f'stroke="{theme["accent"]}" stroke-opacity=".65"/>' for x, y in nodes
    )
    return f'''<g transform="{transform}" aria-hidden="true">
      <g fill="none" stroke="{theme['muted']}" stroke-width="1" opacity=".12">
        <path d="M0 298H384M0 194H384M104 -19V418M304 -19V418"/>
        <circle cx="210" cy="194" r="145" stroke-dasharray="2 9"/>
      </g>
      <g fill="none" stroke="{theme['accent']}" stroke-width="1.5"
         stroke-linejoin="round" stroke-linecap="round" opacity=".34">{paths}</g>
      <g fill="{theme['accent']}" fill-opacity=".035" stroke="{theme['accent']}"
         stroke-opacity=".43" stroke-width="1.25">{foliage}</g>
      <path d="M210 348V298V237L253 194V114L304 63V31" fill="none"
            stroke="{theme['accent']}" stroke-opacity=".62" stroke-width="1.75"/>
      <path class="pulse" pathLength="100" d="M210 348V298V237L253 194V114L304 63V31"
            fill="none" stroke="{theme['accent']}" stroke-width="2.4"
            stroke-linecap="round" stroke-dasharray="5 95" stroke-dashoffset="100"/>
      {points}
      <circle cx="210" cy="348" r="6" fill="{theme['bg']}" stroke="{theme['accent']}"/>
      <circle cx="210" cy="348" r="2" fill="{theme['accent']}"/>
    </g>'''


def _hero(config: dict, mode: str, mobile: bool) -> str:
    t = THEMES[mode]
    name = str(config.get("name", "Arnav Bule"))
    username = str(config.get("username", "GODOSTROYER")).lstrip("@")
    width, height = (640, 720) if mobile else (1200, 460)
    x = 40 if mobile else 64
    name_y = 139 if mobile else 154
    tagline = _lines(config.get("tagline", "Ideas into working software."), 33 if mobile else 53, 2)
    focus = _lines(config.get("focus", "Building, learning, and sharing the work."), 33 if mobile else 55, 2)
    tag_rows = "".join(_outline(line, x, name_y + 43 + (31 if mobile else 27) * i,
                               24 if mobile else 20, t['muted'])
                       for i, line in enumerate(tagline))
    # The mobile console precedes the network, allowing readable type at 320px.
    console_y = 250 if mobile else 256
    console_width = 560 if mobile else 615
    console_height = 185 if mobile else 151
    console_baselines = (32, 63, 99, 130) if mobile else (31, 55, 86, 112)
    focus_rows = "".join(
        f'<tspan x="{x + 23}" dy="{0 if i == 0 else (31 if mobile else 23)}">{_text(line)}</tspan>'
        for i, line in enumerate(focus)
    )
    title_size = 73 if mobile else 88
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
 viewBox="0 0 {width} {height}" role="img" aria-labelledby="identity-title identity-desc">
 <title id="identity-title">{_text(name)} — @{_text(username)}</title>
 <desc id="identity-desc">{_text(config.get('tagline', 'Ideas into working software.'))}
 Terminal: whoami, {_text(name)} / @{_text(username)}; cat focus.txt, {_text(config.get('focus', 'Building, learning, and sharing the work.'))}.
 Original branching circuit artwork represents ideas growing into connected work.</desc>
 <style>
  .mono {{ font-family: 'Cascadia Code', 'SFMono-Regular', Consolas, monospace; }}
  .pulse {{ animation: travel 12s linear infinite; }}
  @keyframes travel {{ 0% {{stroke-dashoffset:100;opacity:0;}}
   8% {{opacity:.9;}} 72% {{opacity:.9;}} 86%,100% {{stroke-dashoffset:0;opacity:0;}} }}
  @media (prefers-reduced-motion: reduce) {{ .pulse {{animation:none;opacity:0;}} }}
 </style>
 <rect width="{width}" height="{height}" rx="8" fill="{t['bg']}"/>
 <path d="M{x} 29H{x + 24}" stroke="{t['accent']}" stroke-width="3"/>
 {_outline(name.upper(), x - 3, name_y, title_size, t['text'], 700, 565 if mobile else 635)}
 {tag_rows}
 <rect x="{x}" y="{console_y}" width="{console_width}" height="{console_height}" rx="4" fill="{t['surface']}"/>
 <path d="M{x} {console_y + 20}V{console_y + console_height - 19}" stroke="{t['accent']}"
       stroke-width="1" stroke-opacity=".72"/>
 <g class="mono" font-size="{22 if mobile else 15}">
  <text x="{x + 23}" y="{console_y + console_baselines[0]}" fill="{t['text']}"><tspan fill="{t['accent']}">$</tspan> whoami</text>
  <text x="{x + 23}" y="{console_y + console_baselines[1]}" fill="{t['warm']}">{_text(name)} / @{_text(username)}</text>
  <text x="{x + 23}" y="{console_y + console_baselines[2]}" fill="{t['text']}"><tspan fill="{t['accent']}">$</tspan> cat focus.txt</text>
  <text x="{x + 23}" y="{console_y + console_baselines[3]}" fill="{t['muted']}">{focus_rows}</text>
 </g>
 {_signal(t, mobile)}
</svg>'''


def render_identity(config: dict) -> dict[str, str]:
    """Return standalone theme and viewport variants, without touching disk."""
    return {
        f"hero{'-mobile' if mobile else ''}-{mode}.svg": _hero(config, mode, mobile)
        for mobile in (False, True) for mode in THEMES
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / "profile.config.json").read_text(encoding="utf-8"))
    output = root / "assets" / "generated"
    output.mkdir(parents=True, exist_ok=True)
    for filename, content in render_identity(config).items():
        (output / filename).write_text(content + "\n", encoding="utf-8")
