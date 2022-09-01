""" Make a font with a "tofu" .notdef glyph

Ref https://github.com/fonttools/fonttools/blob/main/Lib/fontTools/fontBuilder.py
"""
from base64 import b64encode
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables._c_m_a_p import cmap_classes
from fontTools.ttLib.tables._g_l_y_f import Glyph


class Rectangle:
  def __init__(self, top, right, bottom, left):
      self.top = top
      self.right = right
      self.bottom = bottom
      self.left = left


FAMILY_NAME = 'Tofu'
STYLE_NAME = 'Regular'
VERSION = '0.1'
GLYPH_NAME = 'tofu'

ADVANCE_WIDTH = 600
BASELINE = 0
CAP_HEIGHT = 800
ASCENDER_Y = 1000
DESCENDER_Y = -200

STROKE_WIDTH = 50
PADDING = 50
TOFU_OUTER_RECT = Rectangle(
  top=CAP_HEIGHT,
  right=ADVANCE_WIDTH-PADDING,
  bottom=BASELINE,
  left=PADDING)
TOFU_INNER_RECT = Rectangle(
  top=CAP_HEIGHT-STROKE_WIDTH,
  right=ADVANCE_WIDTH-PADDING-STROKE_WIDTH,
  bottom=BASELINE+STROKE_WIDTH,
  left=PADDING+STROKE_WIDTH)

def drawTofuGlyph(strokeWidth = 50) -> Glyph:
    pen = TTGlyphPen(None)
    # Draw outer rectangle starting from bottom-left clockwise
    pen.moveTo((TOFU_OUTER_RECT.left, TOFU_OUTER_RECT.bottom))
    pen.lineTo((TOFU_OUTER_RECT.left, TOFU_OUTER_RECT.top))
    pen.lineTo((TOFU_OUTER_RECT.right, TOFU_OUTER_RECT.top))
    pen.lineTo((TOFU_OUTER_RECT.right, TOFU_OUTER_RECT.bottom))
    pen.lineTo((TOFU_OUTER_RECT.left, TOFU_OUTER_RECT.bottom))
    # Draw inner rectangle starting from bottom-left counter-clockwise
    pen.lineTo((TOFU_INNER_RECT.left, TOFU_INNER_RECT.bottom))
    pen.lineTo((TOFU_INNER_RECT.right, TOFU_INNER_RECT.bottom))
    pen.lineTo((TOFU_INNER_RECT.right, TOFU_INNER_RECT.top))
    pen.lineTo((TOFU_INNER_RECT.left, TOFU_INNER_RECT.top))
    pen.lineTo((TOFU_INNER_RECT.left, TOFU_INNER_RECT.bottom))
    pen.closePath()
    return pen.glyph()


def createTtf() -> str:
  """Create the Tofu font binary (*.ttf)."""
  fb = FontBuilder(1024, isTTF=True)

  glyph_order = ['.notdef', GLYPH_NAME]
  fb.setupGlyphOrder(glyph_order)
  nameStrings = dict(
      familyName=dict(en=FAMILY_NAME),
      styleName=dict(en=STYLE_NAME),
      uniqueFontIdentifier='fontBuilder: ' + FAMILY_NAME + '.' + STYLE_NAME,
      fullName=FAMILY_NAME + '-' + STYLE_NAME,
      psName=FAMILY_NAME + '-' + STYLE_NAME,
      version='Version ' + VERSION,
  )

  glyphs = {'.notdef': TTGlyphPen(None).glyph(), GLYPH_NAME: drawTofuGlyph()}
  fb.setupGlyf(glyphs)

  metrics = {}
  glyphTable = fb.font['glyf']
  for name in glyph_order:
      metrics[name] = (ADVANCE_WIDTH, glyphTable[name].xMin)

  fb.setupHorizontalMetrics(metrics)
  fb.setupHorizontalHeader(ascent=ASCENDER_Y, descent=DESCENDER_Y)

  # OTS is unhappy if we *only* have format 13
  fb.setupCharacterMap({1: GLYPH_NAME})

  # format 13: many to one
  # https://docs.microsoft.com/en-us/typography/opentype/spec/cmap#format-13-many-to-one-range-mappings
  # spec: subtable format 13 should only be used under platform ID 0 and encoding ID 6.
  # https://github.com/behdad/tofudetector/blob/master/tofu.ttx uses 3/10 and that seems to work.
  cmap_many_to_one = cmap_classes[13](13)
  cmap_many_to_one.platformID = 3
  cmap_many_to_one.platEncID = 10
  cmap_many_to_one.language = 0
  cmap_many_to_one.cmap = {cp: GLYPH_NAME for cp in range(0x10FFFF + 1) if cp > 1}

  fb.font['cmap'].tables.append(cmap_many_to_one)

  fb.setupNameTable(nameStrings)
  fb.setupOS2(sTypoAscender=ASCENDER_Y, usWinAscent=ASCENDER_Y, usWinDescent=abs(DESCENDER_Y))
  fb.setupPost(keepGlyphNames=False)

  filename = FAMILY_NAME.lower() + '.ttf'
  fb.save(filename)
  return filename


def createCss(ttf_filename):
  """Create the stylesheet with inlined font data."""
  css_filename = FAMILY_NAME.lower() + '.css'
  with open(ttf_filename, mode='rb') as ttf_file:
    with open(css_filename, mode='w') as css_file:
      content = '@font-face {{\n' \
          '  font-family: Tofu;\n' \
          '  src: url("data:font/ttf;base64,{ttf_data}");\n' \
          '}}\n'.format(ttf_data=b64encode(ttf_file.read()).decode('utf-8'))
      css_file.write(content)


def main():
  ttf_filename = createTtf()
  createCss(ttf_filename)


if __name__ == '__main__':
  main()
