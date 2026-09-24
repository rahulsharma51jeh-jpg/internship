"""
Character width tables for the PDF base-14 fonts.

The standard 14 fonts are guaranteed to be present in every conforming PDF
reader, so nothing needs to be embedded; but the widths must be known in order
to wrap and justify text. The tables below are the Adobe Font Metrics advance
widths in 1/1000 em, covering ASCII 32-126 plus the WinAnsi punctuation the
report actually uses.

Arial is metrically identical to Helvetica and Times New Roman to Times-Roman,
which is why the DOCX and the PDF paginate almost identically.
"""

_ASCII = [chr(c) for c in range(32, 127)]


def _tbl(widths):
    """Zip the 95 printable ASCII codes against a width list."""
    assert len(widths) == 95, len(widths)
    return dict(zip(_ASCII, widths))


# ------------------------------------------------------------------- Times ----
_TIMES_ROMAN = _tbl([
    250, 333, 408, 500, 500, 833, 778, 180, 333, 333, 500, 564, 250, 333, 250,
    278,                                                   # space .. /
    500, 500, 500, 500, 500, 500, 500, 500, 500, 500,      # 0-9
    278, 278, 564, 564, 564, 444, 921,                     # : .. @
    722, 667, 667, 722, 611, 556, 722, 722, 333, 389, 722, 611, 889, 722, 722,
    556, 722, 667, 556, 611, 722, 722, 944, 722, 722, 611,  # A-Z
    333, 278, 333, 469, 500, 333,                          # [ .. `
    444, 500, 444, 500, 444, 333, 500, 500, 278, 278, 500, 278, 778, 500, 500,
    500, 500, 333, 389, 278, 500, 500, 722, 500, 500, 444,  # a-z
    480, 200, 480, 541,                                    # { | } ~
])

_TIMES_BOLD = _tbl([
    250, 333, 555, 500, 500, 1000, 833, 278, 333, 333, 500, 570, 250, 333, 250,
    278,
    500, 500, 500, 500, 500, 500, 500, 500, 500, 500,
    333, 333, 570, 570, 570, 500, 930,
    722, 667, 722, 722, 667, 611, 778, 778, 389, 500, 778, 667, 944, 722, 778,
    611, 778, 722, 556, 667, 722, 722, 1000, 722, 722, 667,
    333, 278, 333, 581, 500, 333,
    500, 556, 444, 556, 444, 333, 500, 556, 278, 333, 556, 278, 833, 556, 500,
    556, 556, 444, 389, 333, 556, 500, 722, 500, 500, 444,
    394, 220, 394, 520,
])

_TIMES_ITALIC = _tbl([
    250, 333, 420, 500, 500, 833, 778, 214, 333, 333, 500, 675, 250, 333, 250,
    278,
    500, 500, 500, 500, 500, 500, 500, 500, 500, 500,
    333, 333, 675, 675, 675, 500, 920,
    611, 611, 667, 722, 611, 611, 722, 722, 333, 444, 667, 556, 833, 667, 722,
    611, 722, 611, 500, 556, 722, 611, 833, 611, 556, 556,
    389, 278, 389, 422, 500, 333,
    500, 500, 444, 500, 444, 278, 500, 500, 278, 278, 444, 278, 722, 500, 500,
    500, 500, 389, 389, 278, 500, 444, 667, 444, 444, 389,
    400, 275, 400, 541,
])

_TIMES_BOLDITALIC = _tbl([
    250, 389, 555, 500, 500, 833, 778, 278, 333, 333, 500, 570, 250, 333, 250,
    278,
    500, 500, 500, 500, 500, 500, 500, 500, 500, 500,
    333, 333, 570, 570, 570, 500, 832,
    667, 667, 667, 722, 667, 667, 722, 778, 389, 500, 667, 611, 889, 722, 722,
    611, 722, 667, 556, 611, 722, 667, 889, 667, 611, 611,
    333, 278, 333, 570, 500, 333,
    500, 500, 444, 500, 444, 333, 500, 556, 278, 278, 500, 278, 778, 556, 500,
    500, 500, 389, 389, 278, 556, 444, 667, 500, 444, 389,
    348, 220, 348, 570,
])

# --------------------------------------------------------------- Helvetica ----
_HELVETICA = _tbl([
    278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278,
    278,
    556, 556, 556, 556, 556, 556, 556, 556, 556, 556,
    278, 278, 584, 584, 584, 556, 1015,
    667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778,
    667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611,
    278, 278, 278, 469, 556, 333,
    556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556,
    556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500,
    334, 260, 334, 584,
])

_HELVETICA_BOLD = _tbl([
    278, 333, 474, 556, 556, 889, 722, 238, 333, 333, 389, 584, 278, 333, 278,
    278,
    556, 556, 556, 556, 556, 556, 556, 556, 556, 556,
    333, 333, 584, 584, 584, 611, 975,
    722, 722, 722, 722, 667, 611, 778, 722, 278, 556, 722, 611, 833, 722, 778,
    667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611,
    333, 278, 333, 584, 556, 333,
    556, 611, 556, 611, 556, 333, 611, 611, 278, 278, 556, 278, 889, 611, 611,
    611, 611, 389, 556, 333, 611, 556, 778, 556, 556, 500,
    389, 280, 389, 584,
])

# WinAnsi punctuation used by the report, added to each face.
_EXTRA = {
    "Times-Roman": {"\u2013": 500, "\u2014": 1000, "\u2018": 333,
                    "\u2019": 333, "\u201c": 444, "\u201d": 444,
                    "\u2022": 350, "\u00d7": 564, "\u00a0": 250,
                    "\u00b0": 400, "\u00bd": 750, "\u2026": 1000},
    "Times-Bold": {"\u2013": 500, "\u2014": 1000, "\u2018": 333,
                   "\u2019": 333, "\u201c": 500, "\u201d": 500,
                   "\u2022": 350, "\u00d7": 570, "\u00a0": 250,
                   "\u00b0": 400, "\u00bd": 750, "\u2026": 1000},
    "Times-Italic": {"\u2013": 500, "\u2014": 889, "\u2018": 333,
                     "\u2019": 333, "\u201c": 556, "\u201d": 556,
                     "\u2022": 350, "\u00d7": 675, "\u00a0": 250,
                     "\u00b0": 400, "\u00bd": 750, "\u2026": 889},
    "Times-BoldItalic": {"\u2013": 500, "\u2014": 1000, "\u2018": 333,
                         "\u2019": 333, "\u201c": 500, "\u201d": 500,
                         "\u2022": 350, "\u00d7": 570, "\u00a0": 250,
                         "\u00b0": 400, "\u00bd": 750, "\u2026": 1000},
    "Helvetica": {"\u2013": 556, "\u2014": 1000, "\u2018": 222,
                  "\u2019": 222, "\u201c": 333, "\u201d": 333,
                  "\u2022": 350, "\u00d7": 584, "\u00a0": 278,
                  "\u00b0": 400, "\u00bd": 834, "\u2026": 1000},
    "Helvetica-Bold": {"\u2013": 556, "\u2014": 1000, "\u2018": 278,
                       "\u2019": 278, "\u201c": 500, "\u201d": 500,
                       "\u2022": 350, "\u00d7": 584, "\u00a0": 278,
                       "\u00b0": 400, "\u00bd": 834, "\u2026": 1000},
}

WIDTHS = {
    "Times-Roman": _TIMES_ROMAN,
    "Times-Bold": _TIMES_BOLD,
    "Times-Italic": _TIMES_ITALIC,
    "Times-BoldItalic": _TIMES_BOLDITALIC,
    "Helvetica": _HELVETICA,
    "Helvetica-Bold": _HELVETICA_BOLD,
    "Helvetica-Oblique": _HELVETICA,
    "Helvetica-BoldOblique": _HELVETICA_BOLD,
}
for _face, _ex in _EXTRA.items():
    WIDTHS[_face].update(_ex)
WIDTHS["Helvetica-Oblique"] = WIDTHS["Helvetica"]
WIDTHS["Helvetica-BoldOblique"] = WIDTHS["Helvetica-Bold"]

# The rupee sign is drawn by a Type3 font (see pdfwriter); this is its advance.
RUPEE = "\u20b9"
RUPEE_WIDTH = 520

# WinAnsiEncoding byte values for the non-Latin-1 characters we use.
_WINANSI = {
    "\u2013": 0x96, "\u2014": 0x97, "\u2018": 0x91, "\u2019": 0x92,
    "\u201c": 0x93, "\u201d": 0x94, "\u2022": 0x95, "\u2026": 0x85,
}


def char_width(ch, face, size):
    """Advance width of a single character in points."""
    if ch == RUPEE:
        return RUPEE_WIDTH * size / 1000.0
    w = WIDTHS[face].get(ch)
    if w is None:
        w = WIDTHS[face].get("?", 500)
    return w * size / 1000.0


def text_width(text, face, size):
    """Advance width of a string in points (rupee included)."""
    tbl = WIDTHS[face]
    total = 0
    for ch in text:
        if ch == RUPEE:
            total += RUPEE_WIDTH
        else:
            total += tbl.get(ch, 500)
    return total * size / 1000.0


def encode(text):
    """Encode a string to WinAnsi bytes, escaped for a PDF literal string."""
    out = bytearray()
    for ch in text:
        code = _WINANSI.get(ch)
        if code is None:
            try:
                code = ch.encode("cp1252")[0]
            except (UnicodeEncodeError, IndexError):
                code = ord("?")
        if code in (0x28, 0x29, 0x5C):       # ( ) backslash
            out.append(0x5C)
        out.append(code)
    return bytes(out)
