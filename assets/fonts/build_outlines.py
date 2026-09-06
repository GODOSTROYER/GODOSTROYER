"""Author-time outline extraction; fontTools is not needed by the renderer."""
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen

root = Path(__file__).resolve().parent
result = {}
for weight in (400, 700):
    font = instantiateVariableFont(TTFont(root / "SpaceGrotesk-variable.ttf"), {"wght": weight})
    glyph_set = font.getGlyphSet()
    glyphs = {}
    for char, glyph_name in font.getBestCmap().items():
        if char < 32 or char > 591:
            continue
        pen = SVGPathPen(glyph_set)
        glyph_set[glyph_name].draw(pen)
        glyphs[chr(char)] = [font["hmtx"][glyph_name][0], pen.getCommands()]
    result[str(weight)] = {"units": font["head"].unitsPerEm, "glyphs": glyphs}
(root / "space-grotesk-outlines.json").write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
