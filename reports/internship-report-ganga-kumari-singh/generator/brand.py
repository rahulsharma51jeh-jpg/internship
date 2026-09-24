"""
Brand system for the Infinity Interns internship report.

Colours are sampled from the Infinity Interns logo supplied by the student:
a deep navy wordmark with a blue-to-orange gradient infinity mark.
"""

# ---------------------------------------------------------------- palette ----
NAVY        = (0x12, 0x2F, 0x5C)   # primary - wordmark navy
NAVY_DEEP   = (0x0B, 0x1F, 0x40)   # darkest shade, cover band
NAVY_MID    = (0x1B, 0x4B, 0x8A)   # mid navy
BLUE        = (0x1E, 0x76, 0xC8)   # ribbon blue
BLUE_LIGHT  = (0x4F, 0x9E, 0xE3)   # light blue
BLUE_PALE   = (0xD8, 0xE7, 0xF7)   # table row tint
BLUE_MIST   = (0xEE, 0xF4, 0xFB)   # alternating row tint

ORANGE      = (0xE8, 0x7A, 0x1E)   # accent - ribbon orange
ORANGE_LT   = (0xF4, 0xA3, 0x4A)
ORANGE_PALE = (0xFD, 0xEF, 0xDD)

TEAL        = (0x11, 0x8A, 0x8E)
GREEN       = (0x1E, 0x8E, 0x4A)
GREEN_PALE  = (0xE4, 0xF3, 0xE9)
RED         = (0xC0, 0x39, 0x2B)
RED_PALE    = (0xFB, 0xE9, 0xE7)
PURPLE      = (0x5B, 0x3E, 0x96)
GOLD        = (0xC9, 0x9A, 0x22)

INK         = (0x1A, 0x1A, 0x1A)   # body text
INK_SOFT    = (0x44, 0x4A, 0x55)   # secondary text
GREY        = (0x8A, 0x91, 0x9C)
GREY_LIGHT  = (0xC8, 0xCE, 0xD6)
GREY_HAIR   = (0xE3, 0xE7, 0xEC)   # hairline rules
PAPER       = (0xFF, 0xFF, 0xFF)
PAPER_WARM  = (0xFA, 0xFB, 0xFD)

# Ordered series palette for charts
SERIES = [NAVY, ORANGE, BLUE_LIGHT, TEAL, PURPLE, GOLD, GREEN, RED]


def hex_of(rgb):
    """(r, g, b) -> 'RRGGBB' for OOXML attributes."""
    return "%02X%02X%02X" % rgb


def unit(rgb):
    """(r, g, b) 0-255 -> (r, g, b) 0.0-1.0 for PDF operators."""
    return (rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)


def mix(a, b, t):
    """Linear interpolation between two colours; t in [0, 1]."""
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    return (
        int(round(a[0] + (b[0] - a[0]) * t)),
        int(round(a[1] + (b[1] - a[1]) * t)),
        int(round(a[2] + (b[2] - a[2]) * t)),
    )


def lighten(rgb, t):
    """Blend a colour towards white."""
    return mix(rgb, (255, 255, 255), t)


def darken(rgb, t):
    """Blend a colour towards black."""
    return mix(rgb, (0, 0, 0), t)


# ------------------------------------------------------------- typography ----
# The DOCX uses Arial + Times New Roman; the PDF uses the metric-compatible
# base-14 faces Helvetica + Times-Roman, so both files paginate near-identically.
FONT_SANS_DOCX   = "Arial"
FONT_SERIF_DOCX  = "Times New Roman"

FONT_SANS        = "Helvetica"
FONT_SANS_BOLD   = "Helvetica-Bold"
FONT_SANS_IT     = "Helvetica-Oblique"
FONT_SERIF       = "Times-Roman"
FONT_SERIF_BOLD  = "Times-Bold"
FONT_SERIF_IT    = "Times-Italic"

# ------------------------------------------------------------ report meta ----
STUDENT_NAME   = "GANGA KUMARI SINGH"
FATHER_NAME    = "Krishna Prasad Singh"
ROLL_NO        = "24269010026"
REG_NO         = "1053595/20"
COURSE         = "Financial Management (FM)"
SPECIALISATION = "Financial Management"
DEGREE         = "Master of Business Administration (M.B.A.)"
DEGREE_SHORT   = "M.B.A."
SEMESTER       = "Semester IV"
UNIVERSITY     = "Magadh University, Bodh Gaya"
UNIVERSITY_LN  = "MAGADH UNIVERSITY, BODH GAYA"
SESSION        = "2024 - 2026"

COMPANY_BRAND  = "Infinity Interns"
COMPANY_LEGAL  = "Infinitya1 Career Counselling Private Limited"
COMPANY_TAG    = "A unit of Infinitya1 Career Counselling Private Limited"
COMPANY_ADDR1  = "B-Hub, Maurya Lok Complex"
COMPANY_ADDR2  = "Dak Bungalow Road, Patna, Bihar 800001"
COMPANY_ADDR   = "B-Hub, Maurya Lok Complex, Patna, Bihar"

INTERN_FROM    = "6th June 2026"
INTERN_TO      = "21st July 2026"
INTERN_SPAN    = "6th June 2026 to 21st July 2026"
INTERN_WEEKS   = "Six Weeks and Five Days"
INTERN_DAYS    = "46 Days"

REPORT_TITLE   = "SUMMER INTERNSHIP PROJECT REPORT"
REPORT_SUBJECT = ("A Study on Financial Management Practices, Budgetary Control "
                  "and Financial Performance Analysis")
