from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable, getTableModule
from fontTools.ttLib.tables._c_m_a_p import cmap_classes
from fontTools.colorLib import builder
from fontTools.ttLib.tables import otTables as ot
from fontTools.ttLib.tables._g_l_y_f import Glyph


# Make a font with a "tofu" .notdef glyph
# Ref https://github.com/fonttools/fonttools/blob/main/Lib/fontTools/fontBuilder.py

def drawTofuGlyph(strokeWidth = 50) -> Glyph:
    pen = TTGlyphPen(None)
    pen.moveTo((100, 100))
    pen.lineTo((100, 1000))
    pen.lineTo((500, 1000))
    pen.lineTo((500, 100))
    pen.closePath()
    pen.moveTo((100+strokeWidth, 100+strokeWidth))
    pen.lineTo((100+strokeWidth, 1000-strokeWidth))
    pen.lineTo((500-strokeWidth, 1000-strokeWidth))
    pen.lineTo((500-strokeWidth, 100+strokeWidth))
    pen.closePath()
    return pen.glyph()

fb = FontBuilder(1024, isTTF=True)

glyph_order = ['.notdef', 'tofu']
fb.setupGlyphOrder(glyph_order)
advanceWidths = {n: 600 for n in glyph_order}
familyName = 'Tofu'
styleName = 'Regular'
version = '0.1'
nameStrings = dict(
    familyName=dict(en=familyName),
    styleName=dict(en=styleName),
    uniqueFontIdentifier='fontBuilder: ' + familyName + '.' + styleName,
    fullName=familyName + '-' + styleName,
    psName=familyName + '-' + styleName,
    version='Version ' + version,
)

glyphs = {'.notdef': TTGlyphPen(None).glyph(), 'tofu': drawTofuGlyph()}
fb.setupGlyf(glyphs)

metrics = {}
glyphTable = fb.font['glyf']
for gn, advanceWidth in advanceWidths.items():
    metrics[gn] = (advanceWidth, glyphTable[gn].xMin)

fb.setupHorizontalMetrics(metrics)
fb.setupHorizontalHeader(ascent=824, descent=-200)

# OTS is unhappy if we *only* have format 13
fb.setupCharacterMap({1: 'tofu'})

# format 13: many to one
# https://docs.microsoft.com/en-us/typography/opentype/spec/cmap#format-13-many-to-one-range-mappings
# spec: subtable format 13 should only be used under platform ID 0 and encoding ID 6.
# https://github.com/behdad/tofudetector/blob/master/tofu.ttx uses 3/10 and that seems to work.
cmap_many_to_one = cmap_classes[13](13)
cmap_many_to_one.platformID = 3
cmap_many_to_one.platEncID = 10
cmap_many_to_one.language = 0
cmap_many_to_one.cmap = {cp: 'tofu' for cp in range(0x10FFFF + 1) if cp > 1}

fb.font['cmap'].tables.append(cmap_many_to_one)

fb.setupNameTable(nameStrings)
fb.setupOS2(sTypoAscender=824, usWinAscent=824, usWinDescent=200)
fb.setupPost(keepGlyphNames=False)

fb.save('tofu.ttf')
