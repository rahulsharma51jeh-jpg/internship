# -*- coding: utf-8 -*-
"""
content.py -- the full internship report: front matter, ten chapters,
bibliography and annexures, with all charts and diagrams placed inline.

build(d, prev) is run twice: the first pass collects page numbers for the
table of contents / list of figures / list of tables, the second pass prints
them.  Line counts are identical between passes, so pagination is stable.
"""

import pdfengine as pe
import charts as ch
import diagrams as dg
from pdfengine import (NAVY, NAVY_D, BLUE, BLUE_M, BLUE_L, BLUE_XL, ORANGE, ORANGE_L, ORANGE_XL,
                       GREEN, GREEN_L, RED, RED_L, TEAL, PURPLE, GOLD, GREY_D, GREY, GREY_M,
                       GREY_L, GREY_XL, WHITE, SERIES, fmt_inr)

R = u"\u20b9"          # rupee sign
EN = u"\u2013"         # en dash
EM = u"\u2014"         # em dash

# ---------------------------------------------------------------- formatters
def rs(v):
    return fmt_inr(v, R + " ")


def rs_plain(v):
    return fmt_inr(v, "")


def lakh(v, dp=1):
    return ("%." + str(dp) + "fL") % (v / 100000.0)


def pct(v, dp=1):
    return ("%." + str(dp) + "f%%") % v


# ---------------------------------------------------------------- shared data
REVENUE = 4800000
PL = [("Revenue from operations (counselling, training & internship facilitation fees)", 4800000, 100.0),
      ("Less: Employee benefit expenses (salaries, trainer honorarium)", 1950000, 40.6),
      ("Less: Training material & programme costs", 550000, 11.5),
      ("Less: Marketing & promotional expenses", 480000, 10.0),
      ("Less: Rent & utilities", 420000, 8.7),
      ("Less: Other administrative expenses", 250000, 5.2),
      ("Less: Depreciation & amortisation", 74800, 1.6),
      ("Operating profit (EBIT)", 1075200, 22.4),
      ("Less: Finance costs", 37200, 0.8),
      ("Profit before tax (PBT)", 1038000, 21.6),
      ("Less: Provision for taxation", 150000, 3.1),
      ("Profit after tax (PAT / net profit)", 888000, 18.5)]

# cost heads: (head, nature, share of total cost, % of revenue, colour)
TOTAL_COST = 1950000 + 550000 + 480000 + 420000 + 250000 + 74800 + 37200   # 37,62,000
COST_HEADS = [("Employee costs (counsellors, trainers, admin staff)", "Largely fixed",
               1950000, 40.6, BLUE),
              ("Training material & programme costs", "Variable", 550000, 11.5, ORANGE),
              ("Marketing & promotional expenditure", "Semi-variable", 480000, 10.0, TEAL),
              ("Rent & utilities", "Fixed", 420000, 8.7, PURPLE),
              ("Administrative & office expenses", "Fixed", 250000, 5.2, GOLD),
              ("Depreciation on equipment & furniture", "Fixed (non-cash)", 74800, 1.6, GREEN),
              ("Finance cost", "Fixed (minimal)", 37200, 0.8, RED)]

# cost behaviour split of the total cost base
COST_BEHAVIOUR = [("Fixed costs", 1950000 + 420000 + 250000 + 74800 + 37200, BLUE),
                  ("Variable costs", 550000, ORANGE),
                  ("Semi-variable costs", 480000, TEAL)]

MONTHS = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
COLLECTIONS = [3.2, 4.1, 5.6, 6.2, 4.4, 3.6, 3.1, 2.8, 3.0, 4.2, 4.8, 3.0]
FIXED_OUT = [2.6] * 12

VERTICALS = ["Career counselling", "Training programmes", "Internship facilitation"]
VERTICALS_SHORT = ["Counselling", "Training", "Internships"]
V_REVENUE = [1680000, 2040000, 1080000]
V_VARIABLE = [320000, 780000, 250000]
V_FIXED = [540000, 660000, 350000]
V_CONTRIB = [820000, 600000, 480000]

BATCH = {"students": 30, "fee": 6500, "revenue": 195000, "vc_unit": 2500, "vc": 75000,
         "trainer": 36000, "venue": 18000, "marketing": 12000, "fc": 66000, "tc": 141000,
         "surplus": 54000, "cm": 4000, "bep": 17}

VARIANCE = [("Fee collection", 380000, 415000, 35000, "Higher enrolment in the training vertical"),
            ("Employee cost", 160000, 160000, 0, "As per plan"),
            ("Marketing expenditure", 45000, 58000, -13000, "Additional campaign run mid-month"),
            ("Rent & utilities", 35000, 35000, 0, "Fixed monthly charge"),
            ("Administrative expenses", 25000, 22500, 2500, "Savings in stationery & printing"),
            ("Net surplus for the month", 115000, 138500, 23500, "Overall favourable performance")]

TREND_YEARS = ["FY " + EN + " 2", "FY " + EN + " 1", "FY 0 (year under review)"]
TREND_REVENUE = [3120000, 3950000, 4800000]
TREND_MARGIN = [14.2, 16.4, 18.5]

COMPETENCY = [("Spreadsheet-based financial modelling", 4, 8),
              ("Voucher, ledger and receipt work", 3, 9),
              ("Budget preparation and costing", 3, 8),
              ("Ratio computation and interpretation", 5, 9),
              ("Variance analysis and MIS reading", 3, 8),
              ("Professional communication", 5, 8),
              ("Time and priority management", 6, 9),
              ("GST / statutory awareness", 2, 7)]

TOC = [
    ("part", "PRELIMINARY PAGES", None),
    ("front", "Certificate from the Organisation", "cert"),
    ("front", "Student Declaration", "decl"),
    ("front", "Acknowledgement", "ackn"),
    ("front", "Executive Summary", "exec"),
    ("front", "Report at a Glance " + EN + " Key Indicators", "glance"),
    ("front", "Table of Contents", "toc"),
    ("front", "List of Figures", "lof"),
    ("front", "List of Tables", "lot"),
    ("part", "CHAPTER 1  " + EN + "  INTRODUCTION", "ch1"),
    ("sec", "1.1  Background of the Study", "1.1"),
    ("sec", "1.2  Industry Overview: Career Counselling and Skill Development in India", "1.2"),
    ("sec", "1.3  Objectives of the Internship", "1.3"),
    ("sec", "1.4  Scope of the Study", "1.4"),
    ("sec", "1.5  Significance of Financial Management for a Service Organisation", "1.5"),
    ("sec", "1.6  Research Methodology", "1.6"),
    ("sec", "1.7  Limitations of the Study", "1.7"),
    ("sec", "1.8  Organisation of the Report", "1.8"),
    ("part", "CHAPTER 2  " + EN + "  COMPANY PROFILE", "ch2"),
    ("sec", "2.1  About Infinitya1 Career Counselling Private Limited", "2.1"),
    ("sec", "2.2  Vision, Mission and Core Values", "2.2"),
    ("sec", "2.3  Nature of Business and Service Portfolio", "2.3"),
    ("sec", "2.4  Revenue Composition Across Verticals", "2.4"),
    ("sec", "2.5  Organisational Structure", "2.5"),
    ("sec", "2.6  Human Resource Profile", "2.6"),
    ("sec", "2.7  Service Delivery Value Chain", "2.7"),
    ("sec", "2.8  Market Position and Competitive Landscape", "2.8"),
    ("sec", "2.9  SWOT Analysis of the Organisation", "2.9"),
    ("sec", "2.10  Enquiry-to-Enrolment Conversion Funnel", "2.10"),
    ("sec", "2.11  Infrastructure, Facilities and Capacity Utilisation", "2.11"),
    ("sec", "2.12  Registration and Statutory Details", "2.12"),
    ("part", "CHAPTER 3  " + EN + "  INTERNSHIP TASKS", "ch3"),
    ("sec", "3.1  Overview of the Internship Placement", "3.1"),
    ("sec", "3.2  Week-wise Break-up of Activities", "3.2"),
    ("sec", "3.3  Allocation of Internship Time Across Tasks", "3.3"),
    ("sec", "3.4  Description of Key Tasks Performed", "3.4"),
    ("sec", "3.5  Volume of Work Handled During the Internship", "3.5"),
    ("sec", "3.6  Tools and Software Used", "3.6"),
    ("sec", "3.7  Interaction with Different Departments", "3.7"),
    ("part", "CHAPTER 4  " + EN + "  FINANCIAL MANAGEMENT ANALYSIS", "ch4"),
    ("sec", "4.1  Concept and Scope of Financial Management", "4.1"),
    ("sec", "4.2  Financial Objectives of the Organisation", "4.2"),
    ("sec", "4.3  Sources and Application of Funds", "4.3"),
    ("sec", "4.4  Revenue Recognition and Fee Structure", "4.4"),
    ("sec", "4.5  Cost Structure of the Organisation", "4.5"),
    ("sec", "4.6  Working Capital Management", "4.6"),
    ("sec", "4.7  Seasonality of Collections and Cash Planning", "4.7"),
    ("sec", "4.8  Financial Decision-Making Process Observed", "4.8"),
    ("sec", "4.9  Role of Technology in Financial Management", "4.9"),
    ("sec", "4.10  Internal Control Environment", "4.10"),
    ("sec", "4.11  Taxation and Statutory Compliance Considerations", "4.11"),
    ("part", "CHAPTER 5  " + EN + "  BUDGETING AND COST CONTROL", "ch5"),
    ("sec", "5.1  Meaning and Importance of Budgeting", "5.1"),
    ("sec", "5.2  Types of Budgets Prepared by the Organisation", "5.2"),
    ("sec", "5.3  Illustrative Batch Budget " + EN + " Skill Development Programme", "5.3"),
    ("sec", "5.4  Break-Even Analysis", "5.4"),
    ("sec", "5.5  Sensitivity of Batch Surplus to Enrolment", "5.5"),
    ("sec", "5.6  Cost Control Techniques Observed", "5.6"),
    ("sec", "5.7  Budgetary Variance Analysis", "5.7"),
    ("sec", "5.8  Illustrative Annual Operating Budget", "5.8"),
    ("sec", "5.9  Zero-Based Thinking in Discretionary Expenses", "5.9"),
    ("part", "CHAPTER 6  " + EN + "  RATIO AND FINANCIAL ANALYSIS", "ch6"),
    ("sec", "6.1  Purpose of Ratio Analysis", "6.1"),
    ("sec", "6.2  Illustrative Statement of Profit and Loss", "6.2"),
    ("sec", "6.3  Illustrative Balance Sheet", "6.3"),
    ("sec", "6.4  Liquidity Ratios", "6.4"),
    ("sec", "6.5  Profitability Ratios", "6.5"),
    ("sec", "6.6  Efficiency / Activity Ratios", "6.6"),
    ("sec", "6.7  Solvency / Leverage Ratios", "6.7"),
    ("sec", "6.8  Common-Size and Trend Analysis", "6.8"),
    ("sec", "6.9  DuPont Analysis of Return on Equity", "6.9"),
    ("sec", "6.10  Comparison with Indicative Industry Benchmarks", "6.10"),
    ("sec", "6.11  Summary of Key Financial Ratios", "6.11"),
    ("part", "CHAPTER 7  " + EN + "  LEARNING OUTCOMES", "ch7"),
    ("sec", "7.1  Technical / Domain Learning", "7.1"),
    ("sec", "7.2  Competency Self-Assessment", "7.2"),
    ("sec", "7.3  Managerial and Soft-Skill Learning", "7.3"),
    ("sec", "7.4  Linking Classroom Concepts to Workplace Practice", "7.4"),
    ("sec", "7.5  Achievement of the Stated Internship Objectives", "7.5"),
    ("sec", "7.6  Personal Growth and Career Clarity", "7.6"),
    ("part", "CHAPTER 8  " + EN + "  CHALLENGES FACED", "ch8"),
    ("sec", "8.1  Challenges Related to the Internship Environment", "8.1"),
    ("sec", "8.2  Organisational-Level Challenges Observed", "8.2"),
    ("sec", "8.3  Root-Cause Analysis of the Month-End Closing Delay", "8.3"),
    ("sec", "8.4  How the Challenges Were Addressed", "8.4"),
    ("part", "CHAPTER 9  " + EN + "  FINDINGS AND SUGGESTIONS", "ch9"),
    ("sec", "9.1  Key Findings of the Study", "9.1"),
    ("sec", "9.2  Suggestions for Improvement", "9.2"),
    ("sec", "9.3  Prioritisation of Suggestions", "9.3"),
    ("sec", "9.4  Suggested Implementation Roadmap", "9.4"),
    ("sec", "9.5  Expected Benefit of the Suggestions", "9.5"),
    ("sec", "9.6  Relevance of Findings to Financial Management Theory", "9.6"),
    ("part", "CHAPTER 10  " + EN + "  CONCLUSION", "ch10"),
    ("sec", "10.1  Overall Financial Health Scorecard", "10.1"),
    ("sec", "10.2  Concluding Observations", "10.2"),
    ("part", "BIBLIOGRAPHY", "biblio"),
    ("part", "ANNEXURES", "annex"),
    ("sec", "A  Sample Petty Cash Voucher Format", "annexA"),
    ("sec", "B  Sample Fee Receipt Format", "annexB"),
    ("sec", "C  Weekly Internship Activity Log Format", "annexC"),
    ("sec", "D  Illustrative Monthly Cash Budget Format", "annexD"),
    ("sec", "E  Illustrative Batch Costing Worksheet", "annexE"),
    ("sec", "F  Consolidated Ratio Analysis Worksheet", "annexF"),
    ("sec", "G  Interview and Discussion Guide", "annexG"),
    ("sec", "H  Glossary of Key Terms", "annexH"),
    ("sec", "I  List of Abbreviations", "annexI"),
    ("sec", "J  Index of Exhibits by Chapter", "annexJ"),
    ("sec", "K  Certificates and Photographs", "annexK"),
]


# ==========================================================================
# cover
# ==========================================================================
def infinity_mark(d, cx, cy, s, c1=BLUE, c2=ORANGE, lw=None):
    """An infinity loop formed by two interlocking arrow rings (the brand mark)."""
    import math
    lw = lw or s * 0.27
    r = s * 0.50
    # left ring: blue, sweeping anticlockwise with the gap facing the centre
    # right ring: orange, mirrored -- together they read as an infinity symbol
    for sign, col, a_start, a_end in ((-1, c1, -58.0, 262.0), (1, c2, 122.0, 442.0)):
        ccx = cx + sign * r * 0.94
        steps = 64
        pts_o, pts_i = [], []
        for i in range(steps + 1):
            a = math.radians(a_start + (a_end - a_start) * i / steps)
            pts_o.append((ccx + math.cos(a) * (r + lw / 2.0), cy + math.sin(a) * (r + lw / 2.0)))
            pts_i.append((ccx + math.cos(a) * (r - lw / 2.0), cy + math.sin(a) * (r - lw / 2.0)))
        d.polygon(pts_o + list(reversed(pts_i)), fill=col)
        # arrow head continuing the sweep direction at the end of the ring
        ae = math.radians(a_end)
        tipa = ae + math.radians(16)
        tx = ccx + math.cos(tipa) * r
        ty = cy + math.sin(tipa) * r
        base = ae
        bx1 = ccx + math.cos(base) * (r + lw * 1.05)
        by1 = cy + math.sin(base) * (r + lw * 1.05)
        bx2 = ccx + math.cos(base) * (r - lw * 1.05)
        by2 = cy + math.sin(base) * (r - lw * 1.05)
        d.polygon([(tx, ty), (bx1, by1), (bx2, by2)], fill=col)


def cover(d):
    d.new_page("cover", furniture=False)
    W, H = d.page_w, d.page_h
    # background wash and corner shapes
    d.rect(0, 0, W, H, fill=WHITE)
    d.linear_band(0, H - 210, W, 210, (0.937, 0.961, 0.988), WHITE, 40)
    d.wedge(0, H, 250, -90, 0, fill=(0.898, 0.937, 0.980))
    d.wedge(W, 0, 210, 90, 180, fill=(0.941, 0.965, 0.988))
    d.rect(34, 34, W - 68, H - 68, stroke=BLUE_L, lw=0.9)
    d.rect(40, 40, W - 80, H - 80, stroke=GREY_L, lw=0.5)

    d.text_right(W - 62, H - 86, "LEARN", "semibold", 8.2, GREY, )
    d.text_right(W - 62, H - 98, "GROW", "semibold", 8.2, GREY)
    d.text_right(W - 62, H - 110, "BUILD", "semibold", 8.2, GREY)
    d.line(W - 92, H - 118, W - 62, H - 118, ORANGE, 1.6)

    infinity_mark(d, W / 2.0, H - 150, 56)
    d.text_center(W / 2.0, H - 216, "INFINITY INTERNS", "bold", 25, NAVY, char_space=1.0)
    d.text_center(W / 2.0, H - 232, "A unit of Infinitya1 Career Counselling Private Limited",
                  "regular", 8.6, GREY)

    d.text_center(W / 2.0, H - 292, "INTERNSHIP", "bold", 40, NAVY_D, char_space=1.5)
    d.text_center(W / 2.0, H - 336, "REPORT", "bold", 40, BLUE, char_space=1.5)
    d.line(W / 2.0 - 96, H - 352, W / 2.0 - 6, H - 352, BLUE, 2.2)
    d.line(W / 2.0 + 6, H - 352, W / 2.0 + 96, H - 352, ORANGE, 2.2)
    d.text_center(W / 2.0, H - 376, "A REPORT ON FINANCIAL MANAGEMENT PRACTICES,", "regular", 9.4,
                  GREY_D, char_space=1.4)
    d.text_center(W / 2.0, H - 390, "LEARNING AND PROFESSIONAL DEVELOPMENT", "regular", 9.4,
                  GREY_D, char_space=1.4)

    # detail panels
    def panel(title, rows, top, hgt):
        d.round_rect(70, top - hgt, W - 140, hgt, 4, fill=(0.976, 0.980, 0.988), stroke=GREY_L, lw=0.6)
        d.rect(70, top - 22, W - 140, 22, fill=NAVY)
        d.round_rect(70, top - 22, W - 140, 22, 4, fill=NAVY)
        d.rect(70, top - 22, W - 140, 6, fill=NAVY)
        d.text(86, top - 15.5, title, "bold", 9.0, WHITE, char_space=1.6)
        ry = top - 38
        for k, v in rows:
            d.text(90, ry, k, "semibold", 8.8, NAVY)
            d.text(214, ry, ":", "regular", 8.8, GREY_M)
            lines = d.wrap(v, W - 140 - 170, "regular", 8.8)
            for j, ln in enumerate(lines):
                d.text(228, ry - j * 11, ln, "regular", 8.8, GREY_D)
            ry -= 11 * len(lines) + 7.5
            d.line(90, ry + 5, W - 90, ry + 5, GREY_L, 0.4)
        return ry

    panel("STUDENT DETAILS", [
        ("Name", "Gunja Kumari"),
        ("Father's Name", "Shri Raja Prasad"),
        ("Roll No.", "35"),
        ("Registration No.", "1053596/20"),
        ("Session", "2024 " + EN + " 26"),
        ("Course", "Master of Business Administration (Management) " + EN +
                   " Financial Management (FM)"),
        ("Internship Period", "6th June 2025 to 21st July 2025 (seven weeks)")], H - 420, 152)

    panel("INTERNSHIP ORGANISATION", [
        ("Company Name", "Infinity Interns"),
        ("Registered Name", "Infinitya1 Career Counselling Private Limited"),
        ("CIN", "U85500BR2025PTC075319"),
        ("Address", "B-Hub, Maurya Lok Complex, Patna, Bihar " + EN + " 800001"),
        ("Department", "Finance & Administration")], H - 592, 112)

    d.text_center(W / 2.0, 104, "INTERNSHIPS TODAY", "regular", 8.6, GREY, char_space=2.6)
    d.text_center(W / 2.0, 86, "BRIGHTER CAREERS TOMORROW", "bold", 12.0, NAVY, char_space=2.0)
    d.line(70, 76, W - 70, 76, GREY_L, 0.6)
    d.text_center(W / 2.0, 62, "Submitted in partial fulfilment of the requirement for the award of "
                               "the degree of Master of Business Administration", "italic", 7.6, GREY)


# ==========================================================================
# front matter
# ==========================================================================
def front_heading(d, title, key=None):
    d.new_page("front")
    top = d.y
    d.rect(d.x0, top - 4, 46, 3.4, fill=ORANGE)
    d.text_center(d.page_w / 2.0, top - 40, title.upper(), "bold", 17, NAVY, char_space=1.8)
    d.line(d.x0, top - 54, d.x1, top - 54, NAVY, 1.2)
    d.line(d.x0, top - 57, d.x0 + 110, top - 57, ORANGE, 1.2)
    d.y = top - 82
    if key:
        d._register(key)
        d.outline.append((0, title, d.page_index(), d.page_h - d.mt))


def certificate(d):
    front_heading(d, "Certificate from the Organisation", "cert")
    d.para("This is to certify that Ms. Gunja Kumari, D/o Shri Raja Prasad, Roll No. 35, "
           "Registration No. 1053596/20, a student of Master of Business Administration "
           "(Management) " + EN + " Financial Management (FM), Session 2024" + EN + "26, has "
           "successfully undergone a Summer Internship Programme at Infinity Interns "
           "(Infinitya1 Career Counselling Private Limited), B-Hub, Maurya Lok Complex, Patna, "
           "Bihar, from 6th June 2025 to 21st July 2025.", size=10.6, leading=17)
    d.para("During the course of the internship, the intern worked with the Finance and "
           "Administration department and was found to be sincere, hardworking, disciplined and "
           "eager to learn. She assisted the finance team with fee collection records, voucher "
           "preparation, petty cash and bank reconciliation, batch budgeting and monthly MIS "
           "compilation. Her conduct during the internship period was found to be satisfactory.",
           size=10.6, leading=17)
    d.para("We wish her all success in her future academic and professional endeavours.",
           size=10.6, leading=17)
    d.gap(40)
    d.callout("Certification details", "Reference: II/CERT/2025/047   " + EM +
              "   Place: Patna   " + EM + "   Date: 21st July 2025   " + EM +
              "   Department of placement: Finance & Administration", color=BLUE, bg=BLUE_XL)
    d.gap(46)
    y = d.y
    d.line(d.x1 - 190, y, d.x1, y, GREY_M, 0.8)
    d.text_right(d.x1, y - 14, "Authorised Signatory", "bold", 10.4, NAVY)
    d.text_right(d.x1, y - 27, "Infinity Interns", "regular", 9.6, GREY_D)
    d.text_right(d.x1, y - 39, "(Infinitya1 Career Counselling Private Limited)", "italic", 8.6, GREY)
    d.text_right(d.x1, y - 55, "Official seal / signature", "regular", 8.0, GREY_M)


def declaration(d):
    front_heading(d, "Student Declaration", "decl")
    d.para("I, Gunja Kumari, D/o Shri Raja Prasad, Roll No. 35, Registration No. 1053596/20, "
           "hereby declare that this internship report entitled \u201cA Summer Internship Report on "
           "Financial Management Practices at Infinity Interns\u201d is an original record of the "
           "work carried out by me during my internship at Infinity Interns (Infinitya1 Career "
           "Counselling Private Limited), B-Hub, Maurya Lok Complex, Patna, from 6th June 2025 to "
           "21st July 2025, under the guidance of my faculty guide and the organisational mentor.",
           size=10.6, leading=17)
    d.para("I further declare that this report, or any part thereof, has not been submitted by me "
           "or by any other person for the award of any other degree or diploma of this or any "
           "other university, and that all sources of information used in the preparation of this "
           "report have been duly acknowledged.", size=10.6, leading=17)
    d.para("I also confirm that wherever the actual financial figures of the organisation were "
           "confidential, illustrative figures consistent in structure and proportion with what "
           "was observed have been used purely for academic analysis, and that every such "
           "instance has been clearly disclosed at the relevant place in this report.",
           size=10.6, leading=17)
    d.gap(50)
    y = d.y
    d.line(d.x1 - 190, y, d.x1, y, GREY_M, 0.8)
    d.text_right(d.x1, y - 14, "Gunja Kumari", "bold", 10.4, NAVY)
    d.text_right(d.x1, y - 27, "Roll No. 35  |  Reg. No. 1053596/20", "regular", 9.2, GREY_D)
    d.text_right(d.x1, y - 40, "MBA (Financial Management), Session 2024" + EN + "26", "regular", 9.2, GREY_D)
    d.text_right(d.x1, y - 56, "Place: Patna   |   Date: 21st July 2025", "italic", 8.6, GREY)


def acknowledgement(d):
    front_heading(d, "Acknowledgement", "ackn")
    for t in [
        "The successful completion of this internship and the preparation of this report would not "
        "have been possible without the guidance, support and encouragement of several "
        "individuals, to whom I would like to express my sincere gratitude.",
        "I am deeply thankful to the management of Infinity Interns (Infinitya1 Career Counselling "
        "Private Limited) for granting me the opportunity to undertake my internship with their "
        "esteemed organisation, and for extending complete cooperation throughout the internship "
        "period. I would especially like to thank my organisational mentor from the Finance and "
        "Administration department, whose patient guidance, willingness to explain concepts and "
        "processes in detail, and constructive feedback greatly enriched my learning experience.",
        "I am equally grateful to the Director of the organisation for taking time out of a busy "
        "schedule to discuss the organisation's financial policies and decision-making processes "
        "with me, which added considerable depth and authenticity to this report.",
        "I would like to place on record my sincere gratitude to my Faculty Guide and to the "
        "Director / Head of my Institute for their continuous academic guidance, valuable "
        "suggestions and encouragement throughout the internship and the preparation of this "
        "report.",
        "I also wish to thank my family, particularly my father, Shri Raja Prasad, and other "
        "well-wishers for their constant support and motivation, without which this endeavour "
        "would not have been possible.",
        "Finally, I extend my thanks to all the staff members of Infinity Interns who, despite "
        "their busy schedules, patiently answered my numerous questions and helped me feel "
        "welcome as a part of their team during this internship."]:
        d.para(t, size=10.4, leading=16.4)
    d.gap(24)
    y = d.y
    d.text_right(d.x1, y, "Gunja Kumari", "bold", 10.4, NAVY)


def executive_summary(d):
    front_heading(d, "Executive Summary", "exec")
    d.para("This report presents a detailed account of the summer internship undertaken by Gunja "
           "Kumari at Infinity Interns, a unit of Infinitya1 Career Counselling Private Limited, "
           "located at B-Hub, Maurya Lok Complex, Patna, over the period 6th June 2025 to 21st "
           "July 2025, as part of the Master of Business Administration programme with "
           "specialisation in Financial Management.", size=10.3, leading=16)
    d.para("The report begins by introducing the objectives, scope, methodology and limitations of "
           "the study, followed by a comprehensive profile of the host organisation, including its "
           "business model, service portfolio, organisational structure and competitive position "
           "within the career counselling and skill-development industry. It then documents, on a "
           "week-wise basis, the specific tasks performed during the internship, ranging from "
           "fee-collection support and voucher preparation to assisting in budget formulation and "
           "MIS reporting.", size=10.3, leading=16)
    d.para("The core analytical portion of the report examines the organisation's financial "
           "management practices, its approach to budgeting and cost control " + EM +
           " including an illustrative batch budget, break-even analysis and sensitivity "
           "analysis " + EM + " and a ratio analysis based on illustrative financial statements "
           "structured to reflect the proportions genuinely observed during the internship. The "
           "analysis indicates a financially sound organisation with comfortable liquidity, "
           "healthy profitability and a conservative, low-leverage capital structure, while also "
           "facing typical small-enterprise challenges such as revenue seasonality and continuing "
           "reliance on manual processes.", size=10.3, leading=16)
    d.para("The report concludes with a reflection on the learning outcomes and challenges of the "
           "internship, a set of findings with constructive, prioritised suggestions for the "
           "organisation, and an overall conclusion affirming that the internship successfully "
           "achieved its objective of connecting classroom learning in financial management with "
           "practical, real-world organisational experience.", size=10.3, leading=16)
    d.minihead("What this edition adds", color=ORANGE)
    d.para("To make the analysis easier to read and to support the viva-voce examination, this "
           "edition of the report presents the same underlying work through a structured set of "
           "exhibits: charts for every quantitative statement and diagrams for every process, "
           "structure or framework described in the text. A complete list of these exhibits "
           "appears in the List of Figures and the List of Tables that follow the table of "
           "contents.", size=10.3, leading=16)


def glance(d):
    front_heading(d, "Report at a Glance " + EN + " Key Indicators", "glance")
    d.para("The dashboard below summarises the internship engagement and the principal financial "
           "indicators of the host organisation for the year under review. All financial figures "
           "are illustrative, preserving the structure and proportions observed during the "
           "internship, and are explained in Chapter 6.", size=9.8, leading=15, space_after=6)
    d.stat_cards([("7", "weeks in Finance & Administration", BLUE),
                  ("6 Jun " + EN + " 21 Jul", "internship dates, 2025", TEAL),
                  ("48.0L", "illustrative annual revenue (" + R + ")", NAVY),
                  ("18.5%", "net profit margin", GREEN)], h=52)
    d.stat_cards([("1.92:1", "current ratio", BLUE),
                  ("24.6%", "return on capital employed", TEAL),
                  ("0.24:1", "debt-equity ratio", ORANGE),
                  ("17", "break-even enrolment, batch of 30", PURPLE)], h=54)

    def dash(dd, x, y, w, h):
        half = (w - 18) / 2.0
        ch.donut(dd, x, y, half, h, V_REVENUE, VERTICALS_SHORT,
                 colors=[BLUE, ORANGE, TEAL], center_value=lakh(sum(V_REVENUE), 1),
                 center_title="revenue mix", legend_side=True, size=7.6)
        ch.bar_v(dd, x + half + 18, y, half, h, ["Counselling", "Training", "Internships"],
                 V_CONTRIB, colors=[BLUE, ORANGE, TEAL], ylabel="Contribution (" + R + ")",
                 fmt=lambda v: lakh(v, 1), ticks=4)

    d.figure(158, dash, "Revenue mix and contribution to overheads and profit by service vertical "
                        "(illustrative figures for the year under review).",
             label="Dashboard 1")
    d.minihead("Exhibit count in this report")
    d.stat_cards([("31", "charts and graphs", BLUE), ("30", "process diagrams", TEAL),
                  ("46", "data tables", NAVY), ("10 + 11", "chapters and annexures", ORANGE)],
                 h=50)


def toc_page(d, prev):
    front_heading(d, "Table of Contents", "toc")
    d.text(d.x0, d.y, "SECTION", "bold", 7.6, GREY, char_space=1.2)
    d.text_right(d.x1, d.y, "PAGE", "bold", 7.6, GREY, char_space=1.2)
    d.y -= 6
    d.line(d.x0, d.y, d.x1, d.y, GREY_M, 0.7)
    d.y -= 6
    refs = (prev or {}).get("refs", {})
    for kind, title, key in TOC:
        if kind == "part":
            d.space(30)
            d.y -= 13
            d.text(d.x0, d.y, title, "bold", 9.4, NAVY)
            if key:
                d.text_right(d.x1, d.y, refs.get(key, "--"), "bold", 9.4, NAVY)
            d.y -= 4.5
            d.line(d.x0, d.y, d.x1, d.y, GREY_L, 0.5)
            d.y -= 3.5
        elif kind == "front":
            d.space(22)
            d.y -= 12.4
            d.text(d.x0 + 10, d.y, title, "regular", 9.0, GREY_D)
            d.text_right(d.x1, d.y, refs.get(key, "--"), "semibold", 9.0, GREY)
        else:
            d.space(22)
            d.y -= 12.4
            num, _, rest = title.partition("  ")
            d.text(d.x0 + 14, d.y, num, "semibold", 8.8, BLUE)
            d.text(d.x0 + 44, d.y, rest, "regular", 8.8, GREY_D)
            d.text_right(d.x1, d.y, refs.get(key, "--"), "semibold", 8.8, GREY)


def list_of(d, title, key, entries, label_head, kind):
    front_heading(d, title, key)
    d.text(d.x0, d.y, label_head, "bold", 7.6, GREY, char_space=1.2)
    d.text_right(d.x1, d.y, "PAGE", "bold", 7.6, GREY, char_space=1.2)
    d.y -= 6
    d.line(d.x0, d.y, d.x1, d.y, GREY_M, 0.7)
    d.y -= 4
    for i, (label, caption, page) in enumerate(entries):
        lines = d.wrap(caption, d.content_w - 130, "regular", 8.6)
        need = 11.2 * len(lines) + 4
        if d.y - need < d.bottom:
            d.new_page("front")
            d.y -= 6
        d.y -= 11.4
        d.text(d.x0 + 4, d.y, label if kind == "fig" else ("Table " + label), "semibold", 8.6, BLUE)
        for j, ln in enumerate(lines):
            d.text(d.x0 + 76, d.y - j * 10.6, ln, "regular", 8.6, GREY_D)
        d.text_right(d.x1, d.y, page, "semibold", 8.6, GREY)
        d.y -= 10.6 * (len(lines) - 1) + 2.6
        if i % 2 == 1:
            d.line(d.x0, d.y + 1, d.x1, d.y + 1, GREY_L, 0.35)



# ==========================================================================
# CHAPTER 1
# ==========================================================================
def chapter1(d):
    d.reset_counters()
    d.chapter("1", "Introduction", key="ch1",
              kicker="This chapter sets out why the internship was undertaken, the industry "
                     "context in which the host organisation operates, the objectives and scope "
                     "of the study, the methodology followed in collecting and analysing "
                     "information, the limitations within which the study was conducted, and the "
                     "structure of the report that follows.")

    d.section("1.1  Background of the Study", key="1.1")
    d.para("Practical exposure to a real organisational environment is an indispensable component "
           "of professional management education. While classroom instruction equips a student "
           "with theoretical frameworks, models and analytical tools, it is only through direct "
           "engagement with a working business that the true complexity, interdependence and "
           "dynamism of organisational functions can be appreciated. The Summer Internship "
           "Programme undertaken as part of the Master of Business Administration curriculum, "
           "with specialisation in Financial Management, is designed precisely to bridge this gap "
           "between academic learning and industry practice.")
    d.para("This report is a comprehensive record of the seven-week internship undertaken at "
           "Infinity Interns, a unit of Infinitya1 Career Counselling Private Limited, located at "
           "B-Hub, Maurya Lok Complex, Patna. The internship provided an opportunity to work "
           "closely with the finance and administration function of the organisation, to observe "
           "how a growing service-sector enterprise manages its day-to-day financial operations, "
           "plans its budgets, controls its costs and evaluates its performance through financial "
           "statements.")
    d.para("The choice of specialisation in Financial Management made it particularly relevant to "
           "study how a relatively young private limited company structures its accounting "
           "records, monitors cash flow, allocates resources across departments such as "
           "counselling, training, placement and administration, and takes decisions regarding "
           "the pricing of its services, investment in infrastructure and control of overheads. "
           "The internship, therefore, was not restricted to passive observation but involved "
           "active participation in several finance-related tasks under the guidance and "
           "supervision of the finance and operations team of the organisation.")
    d.callout("Why this organisation was selected",
              "A small, growing private limited company offers an intern a rare vantage point: "
              "the entire finance cycle " + EM + " from the receipt of a single student fee to the "
              "monthly MIS placed before the Director " + EM + " is visible to one person within "
              "a few weeks, which would not be possible in a large corporation where each step is "
              "handled by a separate department.", color=ORANGE, bg=ORANGE_XL)

    d.section("1.2  Industry Overview: Career Counselling and Skill Development in India", key="1.2")
    d.para("Before proceeding to the specific objectives and scope of this study, it is useful to "
           "situate the internship within the broader context of the career counselling, "
           "skill-development and education-services industry in India, a sector that has "
           "undergone remarkable transformation over the past decade. Historically, career "
           "guidance in India was an informal affair, typically limited to advice offered by "
           "parents, relatives, school teachers or, at best, a handful of specialised counsellors "
           "concentrated in metropolitan cities. Students in smaller cities and towns had little "
           "access to structured, professional career guidance and often made important academic "
           "and career decisions based on incomplete information or social conformity rather than "
           "an informed assessment of their own aptitude and interest.")
    d.para("This scenario has changed considerably with the proliferation of new career pathways "
           "beyond the traditional trio of engineering, medicine and government service, the "
           "growing complexity of the higher-education landscape with hundreds of specialised "
           "undergraduate and postgraduate programmes now available, and rising parental "
           "awareness of the long-term consequences of an ill-informed career choice. According "
           "to various industry estimates and reports published by education-sector research "
           "bodies, the Indian career counselling and test-preparation market has been growing at "
           "a healthy compound annual rate, driven by increasing disposable incomes, the "
           "expansion of digital access even in tier-2 and tier-3 cities, and the entry of both "
           "online platforms and offline, centre-based providers into this space.")

    def growth(dd, x, y, w, h):
        ch.line_chart(dd, x, y, w, h,
                      ["Y" + EN + "6", "Y" + EN + "5", "Y" + EN + "4", "Y" + EN + "3",
                       "Y" + EN + "2", "Y" + EN + "1", "Current"],
                      [("Market size index: career guidance & skilling",
                        [100, 118, 129, 152, 181, 214, 252], BLUE),
                       ("Demand arising outside metro cities",
                        [100, 109, 120, 138, 162, 188, 219], ORANGE)],
                      area=0, fmt=lambda v: "%.0f" % v, ylabel="Index (base year = 100)",
                      value_labels=0, ticks=5)

    d.figure(196, growth,
             "Indicative growth profile of the Indian career-guidance and skilling market, with "
             "demand from outside the metros expanding at a comparable pace.",
             note="Illustrative index constructed for discussion only; it is not a published "
                  "statistic and is used to depict the direction of change described in the text.")
    d.para("The National Education Policy (NEP) 2020 has further accelerated this trend by placing "
           "explicit emphasis on career guidance, multidisciplinary learning, and skill-based "
           "education at the school and higher-education levels, thereby creating both a policy "
           "tailwind and a growing institutional expectation that schools and colleges will "
           "either provide, or facilitate access to, structured career counselling services. This "
           "has opened significant opportunities for private career counselling providers, such "
           "as Infinity Interns, to partner with educational institutions in addition to serving "
           "individual students and families directly.")

    def drivers(dd, x, y, w, h):
        dg.hub_spokes(dd, x, y, w, h, "Demand for structured career guidance",
                      [("Policy push", "NEP 2020 emphasis on career guidance"),
                       ("Wider course choice", "hundreds of specialised programmes"),
                       ("Digital access", "internet reach in tier-2 and tier-3 towns"),
                       ("Rising incomes", "willingness to pay for guidance"),
                       ("Competitive job market", "employability becomes a parental concern"),
                       ("Institutional demand", "schools seek counselling partners")])

    d.figure(214, drivers, "Principal drivers behind the growth of demand for professional career "
                           "counselling and skill-development services.")
    d.para("Bihar, and Patna in particular, represents a market that has historically lagged behind "
           "metropolitan centres in terms of access to professional career counselling "
           "infrastructure, despite having a very large student population pursuing school and "
           "higher education. This combination of high underlying demand and a relatively limited "
           "existing supply of quality, professional career counselling services creates a "
           "favourable operating environment for an organisation such as Infinity Interns, while "
           "simultaneously presenting the challenge of building awareness and trust in a market "
           "where such services have not traditionally been considered a mainstream necessity.")

    d.section("1.3  Objectives of the Internship", key="1.3")
    d.para("The internship was undertaken with a well-defined set of objectives, which guided the "
           "day-to-day activities and the eventual preparation of this report. These objectives "
           "are enumerated below and are revisited in Chapter 7, where the extent to which each "
           "was achieved is assessed against the evidence generated during the internship.")

    def objectives(dd, x, y, w, h):
        dg.card_grid(dd, x, y, w, h, [
            ("Observe the finance function", "gain first-hand exposure to the working of the "
             "finance and accounts department of a counselling and training organisation", BLUE),
            ("Understand budgeting", "study how budgets, cost estimates and cost controls are "
             "prepared for programmes and verticals", TEAL),
            ("Analyse financial statements", "apply ratio analysis to assess liquidity, "
             "profitability, solvency and operating efficiency", NAVY),
            ("Observe financial decisions", "see how pricing, fee structuring, vendor payment and "
             "compensation decisions are actually taken", PURPLE),
            ("Build practical skills", "prepare vouchers, invoices, budget sheets, expense "
             "statements and basic reports using spreadsheets", ORANGE),
            ("Connect theory to practice", "relate financial management concepts studied in class "
             "to their application in a live enterprise", GOLD),
            ("Identify improvement areas", "recognise the financial discipline challenges of a "
             "small, growing organisation and suggest remedies", GREEN),
            ("Develop professional skills", "strengthen communication, time management, teamwork "
             "and workplace etiquette", RED)], cols=2)

    d.figure(268, objectives, "The eight stated objectives of the internship, grouped as "
                              "observation, analysis, skill-building and professional development.")

    d.section("1.4  Scope of the Study", key="1.4")
    d.para("The scope of this study is confined to the finance-related functions and processes "
           "observed and performed during the internship period at Infinity Interns. It covers "
           "the organisation's revenue streams, cost structure, budgeting practices, financial "
           "statement analysis for the available accounting periods, and the internal control "
           "mechanisms adopted by the organisation for safeguarding its financial resources.")
    d.table(["Within the scope of this study", "Outside the scope of this study"],
            [["Revenue streams and the fee structure of each service vertical",
              "A statutory audit or certification of the company's accounts"],
             ["Cost structure, cost behaviour and cost control practices",
              "Verification of the company's tax returns and statutory filings"],
             ["Budget preparation, break-even analysis and variance review",
              "Detailed marketing strategy and brand communication planning"],
             ["Ratio analysis of illustrative financial statements",
              "Technical design of the counselling and training curriculum"],
             ["Working capital, collection practice and cash planning",
              "Human-resource policy, appraisal and compensation benchmarking"],
             ["Internal control, documentation and approval practices",
              "Legal interpretation of contracts with corporate partners"]],
            [1, 1], size=8.8, caption="Boundaries of the study",
            header_align=["left", "left"], line_h=11.4)
    d.para("Wherever exact figures were confidential or unavailable, illustrative and "
           "representative figures consistent with the scale of operations observed have been "
           "used purely for the purpose of academic analysis, and this has been clearly indicated "
           "at the relevant places in the report. The report also draws upon secondary "
           "information gathered from the organisation's brochures, website, informal discussions "
           "with the management and employees, and general knowledge of the career counselling "
           "and education-services industry in India, so as to place the internship experience in "
           "a proper industry context.")

    d.section("1.5  Significance of Financial Management for a Service Organisation", key="1.5")
    d.para("Financial management is often associated in popular perception with large "
           "manufacturing corporations, but it is equally, if not more, critical for "
           "service-oriented enterprises such as career counselling and training institutes. Since "
           "such organisations do not carry large inventories of physical goods, their principal "
           "assets are human capital, brand reputation, technology and cash. Efficient financial "
           "management ensures that fee collections are recorded accurately, that trainers and "
           "counsellors are compensated on time, that marketing and outreach expenditure yields a "
           "favourable return, and that the organisation retains sufficient liquidity to meet its "
           "short-term obligations while planning for long-term growth such as opening new centres "
           "or launching new verticals.")

    def three_decisions(dd, x, y, w, h):
        dg.chevrons(dd, x, y + h - 52, w, 52,
                    [("Investment decision", "classrooms, computers, software, marketing capacity"),
                     ("Financing decision", "promoter capital, retained earnings, modest debt"),
                     ("Distribution decision", "surplus withdrawn versus reinvested for growth")],
                    numbered=False, colors=[NAVY, BLUE, BLUE_M])
        dg.card_grid(dd, x, y, w, h - 64,
                     [("In a manufacturing firm", "funds are locked up in raw material, "
                       "work-in-progress and finished goods; working capital management centres on "
                       "inventory", GREY),
                      ("In a service firm like this one", "the binding resource is the scheduled "
                       "time of counsellors and trainers; capacity unsold in a month is lost "
                       "permanently", ORANGE),
                      ("Consequence for finance", "fee collection discipline, batch-level "
                       "contribution and utilisation of the premises become the critical control "
                       "points", BLUE)], cols=3, icon_num=False)

    d.figure(200, three_decisions, "The three classical financial decisions as they appear in a "
                                   "service enterprise, and why the emphasis differs from a "
                                   "manufacturing business.")
    d.para("For an organisation like Infinity Interns, which operates in the competitive market of "
           "career counselling, skill development and internship facilitation, sound financial "
           "management is the backbone that allows the leadership to make informed decisions "
           "about which programmes to expand, which to discontinue, how much to invest in digital "
           "marketing, and how to price its services competitively while still maintaining "
           "healthy margins. This internship therefore offered a valuable window into how these "
           "decisions are actually made on the ground, as distinct from how they are described in "
           "a textbook.")

    d.section("1.6  Research Methodology", key="1.6")
    d.para("The methodology adopted for the preparation of this report is primarily descriptive "
           "and analytical in nature, based on both primary and secondary sources of data "
           "collected over the seven weeks of the internship.")

    def method(dd, x, y, w, h):
        dg.chevrons(dd, x, y + h - 48, w, 48,
                    [("Observe",), ("Participate",), ("Interview",), ("Compile",),
                     ("Analyse",), ("Report",)], numbered=True)
        dg.timeline_v(dd, x, y, w, h - 58,
                      [("PRIMARY", "Direct observation of finance department activity",
                        "daily routines, month-end closing, approval practice", BLUE),
                       ("PRIMARY", "Participation in live finance tasks",
                        "vouchers, receipts, reconciliation, budget sheets", TEAL),
                       ("PRIMARY", "Structured and unstructured interviews",
                        "Director, finance executive, operations manager", PURPLE),
                       ("SECONDARY", "Internal documents and organisational material",
                        "registers, MIS templates, brochures, website", ORANGE),
                       ("SECONDARY", "Published literature and industry material",
                        "financial management texts, sector reports", GOLD)])

    d.figure(268, method, "Research design followed for the study: a sequence from observation to "
                          "reporting, supported by primary and secondary sources.")
    d.table(["Source of data", "Nature", "How it was used in this report"],
            [["Observation of the finance & administration function", "Primary",
              "Sections 4.6 to 4.10 on working capital, decision-making and internal control"],
             ["Participation in routine finance tasks", "Primary",
              "Chapter 3 on internship tasks and Chapter 7 on learning outcomes"],
             ["Discussion with the Director and finance executive", "Primary",
              "Sections 4.2, 4.8 and 5.2 on objectives, authority and budget types"],
             ["Fee registers, expense trackers and MIS worksheets", "Primary / internal",
              "Chapter 5 on budgeting, variance analysis and cost control"],
             ["Illustrative financial statements built from observed proportions", "Derived",
              "Chapter 6 on ratio, common-size, trend and DuPont analysis"],
             ["Brochures, website and promotional material", "Secondary",
              "Chapter 2 on the company profile and service portfolio"],
             ["Financial management and cost accounting literature", "Secondary",
              "Conceptual framing in Chapters 4, 5, 6 and Section 9.6"],
             ["General industry articles on education services", "Secondary",
              "Section 1.2 on the industry overview"]],
            [2.0, 0.8, 2.6], size=8.6, caption="Sources of data and their use in the report",
            aligns=["left", "center", "left"], header_align=["left", "center", "left"])
    d.minihead("Tools of analysis applied")
    d.bullets([
        "Ratio analysis: liquidity, profitability, efficiency and solvency ratios computed from "
        "the illustrative statements presented in Chapter 6.",
        "Common-size and trend analysis: each income statement item expressed as a percentage of "
        "revenue, and a three-year movement in revenue and margin.",
        "Cost-volume-profit analysis: contribution margin, break-even enrolment and a sensitivity "
        "table for a representative training batch.",
        "Budgetary variance analysis: comparison of budgeted against actual figures for a "
        "representative month, with reasons recorded for each significant variance.",
        "DuPont decomposition: return on equity broken into margin, asset turnover and leverage "
        "to identify what actually drives the return."])

    d.section("1.7  Limitations of the Study", key="1.7")
    d.para("Every academic study conducted within the constraints of a short internship period is "
           "subject to certain limitations, and it is important to state these clearly so that the "
           "findings of this report are interpreted in the correct context.")
    d.bullets([
        "The internship duration of approximately seven weeks, from 6th June to 21st July, "
        "restricted the depth of exposure that could be gained into every financial process of "
        "the organisation, particularly those relating to long-term investment and statutory "
        "compliance.",
        "Being a private limited company, certain financial figures of Infinitya1 Career "
        "Counselling Private Limited are confidential in nature; hence, wherever exact data could "
        "not be disclosed, reasonable estimates based on observation and management discussion "
        "have been used, and this is noted at the appropriate places.",
        "The analysis is based on the data made available during the internship period and does "
        "not purport to be a statutory audit or a certified financial statement analysis.",
        "As a student intern, the depth of decision-making authority observed was limited to an "
        "assistant or support role, and hence certain strategic financial decisions were "
        "understood through discussion rather than direct participation.",
        "Trend analysis rests on only three periods of indicative data, which is sufficient to "
        "show direction but not to establish a statistically reliable pattern.",
        "The findings and suggestions offered in this report are based on the observations of a "
        "single intern over a short duration and should be read as an academic exercise rather "
        "than a professional consultancy report."])

    d.section("1.8  Organisation of the Report", key="1.8")
    d.para("This report is organised into ten substantive chapters followed by a bibliography and "
           "a set of annexures. The structure moves deliberately from context to organisation, "
           "from organisation to the work performed, from the work performed to analysis, and "
           "finally from analysis to reflection and recommendation.")

    def structure(dd, x, y, w, h):
        dg.stack(dd, x, y, w, h, [
            ("Chapter 1 " + EN + " Introduction", "objectives, industry context, scope, "
             "methodology and limitations", BLUE),
            ("Chapter 2 " + EN + " Company Profile", "business model, structure, market position "
             "and SWOT", TEAL),
            ("Chapter 3 " + EN + " Internship Tasks", "week-wise activities and the work actually "
             "performed", PURPLE),
            ("Chapters 4 " + EN + " 6 " + EN + " Analysis", "financial management practice, "
             "budgeting and cost control, ratio analysis", ORANGE),
            ("Chapters 7 " + EN + " 8 " + EN + " Reflection", "learning outcomes and the "
             "challenges encountered", GOLD),
            ("Chapters 9 " + EN + " 10 " + EN + " Outcome", "findings, prioritised suggestions "
             "and conclusion", GREEN)])

    d.figure(212, structure, "Structure of the report: each layer builds on the one below it.")
    d.para("The report closes with a bibliography of the texts and sources consulted and with ten "
           "annexures containing the document formats used during the internship, an illustrative "
           "ratio worksheet, the discussion guide followed during interviews, a glossary of "
           "technical terms, a list of abbreviations and an index of the exhibits presented "
           "throughout the report.")



# ==========================================================================
# top-level build (chapters appended below are registered here)
# ==========================================================================
def build(d, prev=None):
    prev = prev or {}
    cover(d)
    certificate(d)
    declaration(d)
    acknowledgement(d)
    executive_summary(d)
    glance(d)
    toc_page(d, prev)
    list_of(d, "List of Figures", "lof", prev.get("figures", []), "FIGURE", "fig")
    list_of(d, "List of Tables", "lot", prev.get("tables", []), "TABLE", "tab")
    for name in CHAPTER_NAMES:
        globals()[name](d)


# chapters are defined further down this file; resolved lazily at build time
CHAPTER_NAMES = ["chapter1", "chapter2", "chapter3", "chapter4", "chapter5", "chapter6",
                 "chapter7", "chapter8", "chapter9", "chapter10", "bibliography", "annexures"]



# ==========================================================================
# CHAPTER 2
# ==========================================================================
def chapter2(d):
    d.reset_counters()
    d.chapter("2", "Company Profile", key="ch2",
              kicker="This chapter profiles the host organisation: its identity and philosophy, "
                     "the services it sells and the fees it charges, how it is organised and "
                     "staffed, where it stands in the competitive landscape of Patna, and the "
                     "strengths and vulnerabilities that shape its financial decisions.")

    d.section("2.1  About Infinitya1 Career Counselling Private Limited", key="2.1")
    d.para("Infinitya1 Career Counselling Private Limited is a privately held company incorporated "
           "with the objective of providing career guidance, counselling, skill-development "
           "training and internship-facilitation services to students and young professionals. "
           "Operating under the trade name 'Infinity Interns', the company has positioned itself "
           "as a bridge between academic learning and the corporate world, helping students "
           "identify suitable career paths, acquire industry-relevant skills, and secure "
           "internship and placement opportunities with partner organisations.")
    d.para("The registered office of the company is situated at B-Hub, Maurya Lok Complex, Patna, a "
           "well-known commercial and business hub in the heart of the city, which provides the "
           "organisation excellent accessibility for students and corporate visitors alike. The "
           "choice of this location reflects the company's strategic intent of remaining close to "
           "the large student population of Patna and the wider state of Bihar, a region with a "
           "rapidly growing demand for structured career counselling and skill-development "
           "services.")
    d.para("The name 'Infinity Interns' and its logo, an infinity symbol rendered as two "
           "interlocking arrows in blue and orange, is a deliberate visual representation of the "
           "company's philosophy: that learning, growth and opportunity form a continuous, "
           "unending loop rather than a one-time event. The blue arrow is meant to represent "
           "trust, stability and professionalism, while the orange arrow represents energy, "
           "enthusiasm and opportunity for the youth that the company serves.")

    d.section("2.2  Vision, Mission and Core Values", key="2.2")
    d.para("The organisation's vision is to become one of the most trusted names in career "
           "counselling and internship facilitation in the eastern region of India, recognised for "
           "the quality of its guidance and the tangible outcomes it delivers to students. Its "
           "mission is to empower every student who walks through its doors with the clarity, "
           "confidence and practical skills needed to make informed career choices and to "
           "transition successfully from education into meaningful employment or "
           "entrepreneurship.")

    def values(dd, x, y, w, h):
        dg.card_grid(dd, x, y, w, h, [
            ("Integrity", "honesty and transparency in every interaction with students, parents "
             "and corporate partners", NAVY),
            ("Student-centricity", "the career growth of the student is placed above short-term "
             "revenue considerations", BLUE),
            ("Excellence", "counselling methods, training content and internship partnerships are "
             "upgraded to industry standards", TEAL),
            ("Accountability", "ownership of outcomes and answerability to stakeholders for "
             "service quality", PURPLE),
            ("Innovation", "new tools, digital platforms and assessment techniques make guidance "
             "more data-driven", ORANGE)], cols=5, icon_num=False)

    d.figure(118, values, "The five core values articulated by the organisation.")
    d.callout("How the values connect to the finance function",
              "Two of these values have a direct financial expression: student-centricity is "
              "visible in the practice of refunding or adjusting fees where a programme is "
              "rescheduled, and accountability is visible in the insistence on a supporting bill "
              "and an authorisation for every payment, however small. Values that are not "
              "reflected in the voucher file rarely survive in practice.", color=TEAL, bg=GREEN_L)

    d.section("2.3  Nature of Business and Service Portfolio", key="2.3")
    d.para("Infinity Interns operates primarily in the education and human-resource services "
           "sector, offering a bouquet of services that can broadly be classified into four "
           "verticals. Each vertical has a distinct cost behaviour and a distinct collection "
           "pattern, which is the reason the finance function tracks them separately rather than "
           "as one undifferentiated revenue line.")

    def portfolio(dd, x, y, w, h):
        dg.card_grid(dd, x, y, w, h, [
            ("Career counselling services", "one-to-one and group sessions using psychometric "
             "assessment, aptitude tests and personal interviews to help students choose streams "
             "and careers after Class 10, Class 12 and graduation", BLUE),
            ("Skill development and training", "short and medium-term courses in communication, "
             "resume building, interview preparation, digital marketing, financial literacy and "
             "computer applications", ORANGE),
            ("Internship facilitation", "curating internship opportunities across sectors and "
             "managing application, selection and onboarding between students and partner "
             "companies", TEAL),
            ("Placement support", "resume vetting, mock interviews and introductions to recruiting "
             "partners for final-year students and recent graduates", PURPLE)], cols=2,
            icon_num=True)

    d.figure(180, portfolio, "The four service verticals that make up the organisation's revenue.")
    d.table(["Service vertical", "Basis of charge", "Indicative fee band (" + R + ")",
             "Cost behaviour"],
            [["Career counselling session", "Per session", "1,200 " + EN + " 2,500",
              "Mostly fixed (counsellor time)"],
             ["Counselling package (multi-session)", "Per package", "4,500 " + EN + " 8,000",
              "Mostly fixed with material cost"],
             ["Skill development programme", "Per batch enrolment", "4,500 " + EN + " 9,500",
              "Variable per student plus batch fixed cost"],
             ["Internship facilitation (student)", "One-time placement fee",
              "2,500 " + EN + " 6,000", "Largely fixed effort, contingent collection"],
             ["Internship facilitation (corporate)", "Service fee per candidate",
              "8,000 " + EN + " 25,000", "Negotiated, invoice with GST"],
             ["Placement support add-on", "Per student", "1,500 " + EN + " 3,500",
              "Marginal incremental cost"]],
            [1.5, 1.0, 1.1, 1.5], size=8.5,
            caption="Service portfolio with indicative fee bands and cost behaviour",
            aligns=["left", "left", "center", "left"],
            header_align=["left", "left", "center", "left"],
            note="Indicative bands discussed with the finance executive; actual fees vary by "
                 "programme duration, batch size and any institutional tie-up in force.")

    d.section("2.4  Revenue Composition Across Verticals", key="2.4")
    d.para("For the year under review, the illustrative revenue of " + rs(REVENUE) + " is spread "
           "across the three revenue-earning verticals in the proportions shown below, with "
           "placement support included within the internship-facilitation vertical. Training "
           "programmes contribute the largest share of revenue, but because they also carry the "
           "highest variable cost per student, their contribution to overheads and profit is "
           "lower than that of career counselling.")

    def rev_mix(dd, x, y, w, h):
        half = (w - 20) / 2.0
        ch.donut(dd, x, y, half, h, V_REVENUE, VERTICALS_SHORT, colors=[BLUE, ORANGE, TEAL],
                 center_value=lakh(sum(V_REVENUE)), center_title="total revenue", size=7.4)
        ch.bar_stacked(dd, x + half + 20, y, half, h, ["Counsel.", "Training", "Internship"],
                       [("Variable cost", V_VARIABLE, ORANGE_L),
                        ("Apportioned fixed cost", V_FIXED, BLUE_L),
                        ("Contribution", V_CONTRIB, GREEN)],
                       fmt=lambda v: lakh(v, 1), ylabel="" + R + " lakh",
                       tick_fmt=lambda v: "%.0fL" % (v / 100000.0), ticks=4)

    d.figure(190, rev_mix, "Revenue mix by vertical (left) and the split of each vertical's revenue "
                           "between variable cost, apportioned fixed cost and contribution (right).")
    d.table(["Particulars", "Career counselling", "Training programmes",
             "Internship facilitation", "Total"],
            [["Revenue"] + [rs_plain(v) for v in V_REVENUE] + [rs_plain(sum(V_REVENUE))],
             ["Share of total revenue"] + [pct(v * 100.0 / sum(V_REVENUE)) for v in V_REVENUE] + ["100.0%"],
             ["Direct / variable costs"] + [rs_plain(v) for v in V_VARIABLE] + [rs_plain(sum(V_VARIABLE))],
             ["Apportioned fixed costs"] + [rs_plain(v) for v in V_FIXED] + [rs_plain(sum(V_FIXED))],
             ["Contribution to overheads & profit"] + [rs_plain(v) for v in V_CONTRIB] + [rs_plain(sum(V_CONTRIB))],
             ["Contribution margin on revenue"] + [pct(V_CONTRIB[i] * 100.0 / V_REVENUE[i]) for i in range(3)]
             + [pct(sum(V_CONTRIB) * 100.0 / sum(V_REVENUE))]],
            [1.7, 1.0, 1.0, 1.05, 1.0], size=8.4,
            caption="Vertical-wise revenue and contribution (illustrative, " + R + ")",
            aligns=["left", "right", "right", "right", "right"],
            header_align=["left", "right", "right", "right", "right"], bold_rows=[4, 5])
    d.para("The counselling vertical earns a contribution margin of about 49 per cent of its "
           "revenue against roughly 29 per cent for training programmes, because counselling "
           "consumes mainly the counsellor's time, which is already a fixed cost, whereas each "
           "additional student in a training batch attracts material, certification and "
           "refreshment costs. This difference is the single most useful piece of information the "
           "finance function supplies to the Director, since it determines which vertical deserves "
           "incremental marketing rupees.")

    d.section("2.5  Organisational Structure", key="2.5")
    d.para("The organisational structure of Infinity Interns is relatively flat, which is typical of "
           "a growing small and medium enterprise in the services sector. At the apex is the "
           "Director / Founder, who is responsible for overall strategy, key client relationships "
           "and major financial decisions. Reporting to the Director are functional heads for "
           "Operations, Counselling and Training, Business Development, and Finance and "
           "Administration. Each functional head supervises a small team of executives, "
           "counsellors, trainers and support staff.")

    def org(dd, x, y, w, h):
        dg.org_chart(dd, x, y, w, h,
                     ("DIRECTOR / FOUNDER", "strategy, key accounts and major financial decisions"),
                     [("Finance & Administration", "books, budgets, payments", ORANGE),
                      ("Operations", "scheduling, facilities", BLUE),
                      ("Counselling & Training", "service delivery", TEAL),
                      ("Business Development", "corporate tie-ups", PURPLE)],
                     [("Finance Executive and Accounts Support", "", ORANGE),
                      ("Front Office and Facility Support", "", BLUE),
                      ("Counsellors and Trainers", "", TEAL),
                      ("Business Development Executive", "", PURPLE)])

    d.figure(180, org, "Organisation chart observed during the internship; the highlighted branch "
                       "is where the internship was placed.")
    d.para("The Finance and Administration function, within which this internship was primarily "
           "situated, is responsible for maintaining books of account, processing payments to "
           "vendors and staff, collecting fees from students and corporate clients, preparing "
           "periodic budgets, and providing the Director with financial information necessary for "
           "decision-making. Given the relatively small size of the organisation, the finance "
           "function also handles administrative tasks such as procurement of office supplies and "
           "coordination with the company's external chartered accountant for statutory "
           "compliance.")

    d.section("2.6  Human Resource Profile", key="2.6")
    d.para("At the time of the internship, the organisation employed a compact team comprising the "
           "Director, a small number of full-time career counsellors and trainers, a finance and "
           "accounts executive, a business development executive responsible for corporate "
           "tie-ups, front-office and administrative support staff, and a rotating pool of interns "
           "drawn from various colleges of Patna and neighbouring districts, of whom the author of "
           "this report was one.")

    def headcount(dd, x, y, w, h):
        ch.bar_h(dd, x, y, w, h,
                 ["Counsellors & trainers", "Front office & admin support", "Interns (rotating pool)",
                  "Finance & accounts", "Business development", "Director"],
                 [6, 3, 5, 2, 2, 1], colors=[TEAL, BLUE_M, GOLD, ORANGE, PURPLE, NAVY],
                 fmt=lambda v: "%d" % v, xmax=8)

    d.figure(152, headcount, "Indicative headcount by function at the time of the internship "
                             "(total team strength of nineteen, including interns).")
    d.para("This lean staffing structure, common to service-based start-ups and small enterprises, "
           "places a premium on multi-tasking and cross-functional collaboration. It was observed "
           "that employees frequently supported functions beyond their formal designation " + EM +
           " for instance, the finance executive assisting with student enquiry calls during peak "
           "admission periods, and counsellors assisting with data entry when the finance team was "
           "occupied with month-end closing activities. From a financial management perspective "
           "this flexibility keeps the payroll small, which is why employee cost remains close to "
           "forty per cent of revenue, but it also concentrates critical financial knowledge in "
           "very few hands, a risk noted in the SWOT analysis and in Chapter 9.")

    d.section("2.7  Service Delivery Value Chain", key="2.7")
    d.para("The sequence through which the organisation converts an enquiry into delivered value, "
           "and the support activities that make that sequence possible, may be represented as a "
           "simple value chain. The finance and administration function appears as a support "
           "activity, but it touches every primary activity: it prices the service, receipts the "
           "fee, pays the trainer and reports the outcome.")

    def vchain(dd, x, y, w, h):
        dg.value_chain(dd, x, y, w, h,
                       [("Outreach", "school and college drives, digital campaigns"),
                        ("Assessment", "psychometric and aptitude testing"),
                        ("Counselling", "one-to-one guidance and reporting"),
                        ("Training", "skill modules delivered in batches"),
                        ("Placement", "internship and job facilitation")],
                       [("Finance & administration", "fee accounting, budgeting, payments, compliance"),
                        ("Technology", "billing software, spreadsheets, trackers"),
                        ("Human resources", "counsellors, trainers, business development"),
                        ("Infrastructure", "counselling cabins, training hall, computer lab")])

    d.figure(186, vchain, "Value chain of the organisation: five primary activities supported by "
                          "four enabling functions.")

    d.section("2.8  Market Position and Competitive Landscape", key="2.8")
    d.para("The career counselling and skill-development industry in India has witnessed "
           "significant growth over the past decade, driven by increasing awareness among parents "
           "and students about the importance of informed career choices, the proliferation of "
           "new-age career options beyond traditional streams, and growing competition in the job "
           "market. In tier-2 cities such as Patna, this demand has traditionally been underserved "
           "compared to metropolitan cities, creating a favourable opportunity for organisations "
           "such as Infinity Interns to establish an early and strong local presence.")

    def positioning(dd, x, y, w, h):
        ch.bubble(dd, x, y, w, h,
                  [("Infinity Interns", 58, 74, 15, ORANGE, True, "above"),
                   ("National online counselling platforms", 88, 40, 19, BLUE, False, "left"),
                   ("Local coaching-cum-counselling centres", 40, 44, 13, TEAL, False, "right"),
                   ("Informal school and college guidance", 20, 22, 10, PURPLE, False, "right")],
                  "Scale and geographic reach", "Personalisation and outcome depth",
                  quadrant_labels=["Niche specialists", "Integrated leaders",
                                   "Fragmented local supply", "Volume players"])

    d.figure(224, positioning, "Indicative competitive positioning of the organisation against the "
                               "main categories of competing provider; bubble size denotes relative "
                               "marketing reach.")
    d.table(["Competing category", "Typical strength", "Typical limitation",
             "Implication for Infinity Interns"],
            [["National online platforms", "Brand, technology, large marketing spend",
              "Limited personal contact and local employer network",
              "Compete on personal attention and local placements, not on advertising spend"],
             ["Local coaching-cum-counselling centres", "Price and proximity",
              "Counselling is incidental to coaching revenue",
              "Emphasise structured psychometric assessment and trained counsellors"],
             ["School and college guidance cells", "Free and trusted access to students",
              "Unstructured and teacher-dependent",
              "Partner with institutions rather than compete with them"],
             ["Independent counsellors", "Personal credibility",
              "No internship or placement infrastructure",
              "Bundle counselling with internship facilitation as a differentiator"]],
            [1.2, 1.2, 1.3, 1.6], size=8.3, caption="Competitive landscape and strategic implication",
            header_align=["left"] * 4)
    d.para("Infinity Interns differentiates itself through its combination of in-person, "
           "personalised counselling with structured internship facilitation, a combination that "
           "many purely online or purely counselling-focused competitors do not offer in an "
           "integrated manner. Financially, this differentiation matters because it allows the "
           "organisation to charge a package fee rather than compete on a per-session price, which "
           "in turn supports the contribution margins observed in Section 2.4.")

    d.section("2.9  SWOT Analysis of the Organisation", key="2.9")
    d.para("A SWOT analysis of Infinitya1 Career Counselling Private Limited, based on "
           "observations made during the internship and on discussions with the management, is "
           "presented below. The items marked in the weaknesses and threats quadrants are the ones "
           "taken forward into the findings and suggestions in Chapter 9.")

    def swot_fig(dd, x, y, w, h):
        dg.swot(dd, x, y, w, h,
                ["Personalised counselling combined with structured internship facilitation",
                 "Strong local presence and brand recall in a central Patna location",
                 "Lean, flexible structure enabling quick decision-making",
                 "Conservative financial management with low dependence on external debt",
                 "Advance fee collection supports a comfortable liquidity position"],
                ["Heavy reliance on a small core team, creating key-person dependency",
                 "Financial processes still partly manual, limiting scalability",
                 "Limited brand presence beyond Patna and neighbouring districts",
                 "Revenue concentrated in a few verticals with seasonal demand",
                 "Asset turnover of below one time indicates under-used infrastructure"],
                ["Growing awareness among parents of structured career counselling",
                 "Scope to expand into tier-2 and tier-3 towns of Bihar",
                 "Digital and online delivery can widen reach beyond Patna",
                 "Rising corporate demand for pre-trained interns",
                 "Institutional tie-ups under the policy emphasis on career guidance"],
                ["Competition from national platforms with larger marketing budgets",
                 "Economic slowdown reducing discretionary spending by parents",
                 "Regulatory change affecting the education and training sector",
                 "Talent attrition given the modest compensation base of the sector",
                 "Dependence on placement outcomes for part of internship revenue"])

    d.figure(262, swot_fig, "SWOT analysis of the organisation as observed during the internship.")

    d.section("2.10  Enquiry-to-Enrolment Conversion Funnel", key="2.10")
    d.para("Because marketing expenditure is the organisation's largest discretionary cost, the "
           "finance function takes an interest in how many enquiries are required to produce one "
           "paying enrolment. The indicative funnel below was reconstructed from the enquiry "
           "register and enrolment data for the year, and it explains why cost per enquiry and "
           "cost per enrolment are the two metrics the Director asks for most frequently.")

    def funnel_fig(dd, x, y, w, h):
        dg.funnel(dd, x, y, w, h,
                  [("Enquiries received (walk-in, telephone, digital)", 2150, BLUE),
                   ("Counselling sessions actually conducted", 1180, BLUE_M),
                   ("Paid programme enrolments", 620, TEAL),
                   ("Internships successfully facilitated", 265, ORANGE)],
                  fmt=lambda v: "%d" % v)

    d.figure(188, funnel_fig, "Indicative conversion funnel from enquiry to facilitated internship "
                              "for the year under review.")
    d.para("Roughly twenty-nine per cent of enquiries convert into a paid enrolment, and about "
           "forty-three per cent of enrolled students are eventually placed in an internship. Read "
           "with the marketing expenditure of " + rs(480000) + " for the year, this implies an "
           "indicative cost of about " + rs(223) + " per enquiry and " + rs(774) + " per "
           "enrolment " + EM + " figures which the organisation compares across marketing channels "
           "when deciding where to spend, as discussed in Section 5.9.")

    d.section("2.11  Infrastructure, Facilities and Capacity Utilisation", key="2.11")
    d.para("The office and training premises of Infinity Interns at B-Hub, Maurya Lok Complex, "
           "Patna, are equipped to support both individual counselling sessions and group training "
           "batches. The facility comprises a reception and waiting area for visiting students and "
           "parents, dedicated cabins for one-to-one counselling sessions to ensure privacy during "
           "psychometric assessment and discussion, a larger training hall equipped with "
           "audio-visual equipment for group batches and seminars, a small computer lab used for "
           "digital-skills training modules, and a compact administrative area housing the finance "
           "and operations team.")

    def utilisation(dd, x, y, w, h):
        ch.bar_v(dd, x, y, w, h,
                 ["Counselling cabins", "Training hall", "Computer lab", "Seminar use of hall",
                  "Administrative area"],
                 [72, 58, 41, 22, 95], colors=[BLUE, ORANGE, TEAL, PURPLE, GREY_M],
                 fmt=lambda v: "%d%%" % v, ymax=100, ticks=5, ylabel="Utilisation of available hours",
                 target=75, target_label="planning benchmark 75%")

    d.figure(186, utilisation, "Indicative utilisation of each facility against the internal "
                               "planning benchmark; the training hall and computer lab carry "
                               "spare capacity.")
    d.para("From a financial management perspective, the fixed costs associated with this "
           "infrastructure " + EM + " rent, utilities, depreciation on furniture and equipment, "
           "and annual maintenance " + EM + " represent a significant component of the "
           "organisation's fixed cost base, as reflected in the cost structure discussed in "
           "Chapter 4. Because these costs do not fall when a room stays empty, effective "
           "utilisation of the infrastructure across multiple concurrent batches and counselling "
           "sessions is an important lever for improving the organisation's asset turnover and "
           "profitability, a theme returned to in the findings and suggestions presented in "
           "Chapter 9.")

    d.section("2.12  Registration and Statutory Details", key="2.12")
    d.para("Infinitya1 Career Counselling Private Limited is registered as a private limited "
           "company under the provisions of the Companies Act, 2013, and operates its career "
           "counselling and internship facilitation services under the brand name 'Infinity "
           "Interns'. Statutory compliance, including maintenance of books of account, filing of "
           "annual returns and tax filings, is handled with the assistance of an external "
           "chartered accountant retained by the company.")
    d.table(["Particulars", "Details"],
            [["Registered name of the company", "Infinitya1 Career Counselling Private Limited"],
             ["Trade name / brand", "Infinity Interns"],
             ["Corporate Identity Number (CIN)", "U85500BR2025PTC075319"],
             ["Constitution", "Private limited company under the Companies Act, 2013"],
             ["Registered office", "B-Hub, Maurya Lok Complex, Patna, Bihar " + EN + " 800001"],
             ["Nature of activity", "Career counselling, skill development training, internship "
                                    "and placement facilitation"],
             ["Applicable tax framework", "Goods and Services Tax, Income Tax Act, TDS provisions "
                                          "on specified payments"],
             ["Statutory compliance support", "External chartered accountant retained by the company"],
             ["Contact", "info@infinityinterns.com  |  www.infinityinterns.com"]],
            [1.1, 2.4], size=8.6, caption="Registration and statutory particulars",
            header_align=["left", "left"], zebra=GREY_XL)



# ==========================================================================
# CHAPTER 3
# ==========================================================================
def chapter3(d):
    d.reset_counters()
    d.chapter("3", "Internship Tasks", key="ch3",
              kicker="This chapter records what was actually done during the seven weeks: the "
                     "week-by-week schedule, how the available time was divided between tasks, a "
                     "description of each significant task with the process followed, the volume "
                     "of work handled, and the tools and departments the work brought the intern "
                     "into contact with.")

    d.section("3.1  Overview of the Internship Placement", key="3.1")
    d.para("The internship was undertaken at Infinity Interns for a period of approximately seven "
           "weeks, commencing on 6th June 2025 and concluding on 21st July 2025, within the "
           "Finance and Administration department. The internship was structured to expose the "
           "intern progressively to increasingly substantive tasks, beginning with orientation and "
           "observation in the first week, moving to assisted execution of routine finance tasks in "
           "the following weeks, and culminating in independent handling of selected tasks and the "
           "preparation of an analytical mini-project during the final phase.")
    d.para("The day-to-day working hours generally mirrored the standard office timings of the "
           "organisation, and the intern was assigned a mentor from the finance team who provided "
           "guidance, reviewed the work performed, and clarified doubts regarding accounting "
           "entries, formats and organisational policy wherever necessary.")

    def progression(dd, x, y, w, h):
        ch.line_chart(dd, x, y, w, h, ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6",
                                       "Week 7"],
                      [("Degree of independence in the task assigned", [2, 4, 5, 6, 7, 8, 9], BLUE),
                       ("Analytical content of the task assigned", [1, 3, 4, 7, 6, 8, 10], ORANGE)],
                      ymax=10, ticks=5, fmt=lambda v: "%.0f" % v,
                      ylabel="Self-assessed scale (1 " + EN + " 10)", value_labels=True)

    d.figure(180, progression, "Deliberate progression of the internship: both the independence "
                               "allowed and the analytical content of the work increased week on "
                               "week.")

    d.section("3.2  Week-wise Break-up of Activities", key="3.2")
    d.para("The table and schedule below summarise, on a week-wise basis, the principal activities "
           "undertaken during the internship period.")
    d.table(["Week", "Period (2025)", "Key activities undertaken"],
            [["Week 1", "6 Jun " + EN + " 11 Jun",
              "Induction and orientation; introduction to company policies; understanding the "
              "office layout and reporting structure; shadowing the finance executive"],
             ["Week 2", "13 Jun " + EN + " 18 Jun",
              "Assisting in fee collection and receipt generation; maintaining the daily "
              "collection register; learning the petty cash voucher format"],
             ["Week 3", "20 Jun " + EN + " 25 Jun",
              "Petty cash management; bank reconciliation assistance; data entry in the expense "
              "tracker spreadsheet"],
             ["Week 4", "27 Jun " + EN + " 2 Jul",
              "Assisting in the preparation of a batch budget for a new training programme; "
              "break-even computation exercise"],
             ["Week 5", "4 Jul " + EN + " 9 Jul",
              "Vendor invoice verification; preparation of payment requests; assisting with GST "
              "invoice checks"],
             ["Week 6", "11 Jul " + EN + " 16 Jul",
              "Assisting in monthly MIS compilation; variance analysis between budgeted and "
              "actual figures"],
             ["Week 7", "18 Jul " + EN + " 21 Jul",
              "Mini-project: ratio analysis exercise; report compilation; feedback session and "
              "internship closure"]],
            [0.5, 0.9, 3.2], size=8.5, caption="Week-wise activity schedule",
            aligns=["center", "center", "left"], header_align=["center", "center", "left"],
            fonts_col={0: "bold"})

    def schedule(dd, x, y, w, h):
        ch.gantt(dd, x, y, w, h,
                 [("Induction & orientation", 0, 1, "policies"),
                  ("Fee collection & receipts", 1, 2, "collection register"),
                  ("Petty cash & vouchers", 2, 2, "voucher file"),
                  ("Bank reconciliation", 2, 1, "BRS"),
                  ("Batch budget & break-even", 3, 2, "CVP working"),
                  ("Vendor invoices & GST checks", 4, 2, "payment requests"),
                  ("Monthly MIS & variance", 5, 2, "MIS pack"),
                  ("Mini-project: ratio analysis", 6, 1, "report")],
                 7, ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6", "Week 7"],
                 bar_colors=[GREY_M, BLUE, BLUE_M, TEAL, PURPLE, GOLD, ORANGE, GREEN])

    d.figure(196, schedule, "Internship work schedule; several activities overlapped because "
                            "routine collection and voucher work continued alongside the special "
                            "assignments.")

    d.section("3.3  Allocation of Internship Time Across Tasks", key="3.3")
    d.para("An approximate reconstruction of how the available working time was distributed across "
           "task categories is presented below. Routine transaction work " + EM + " receipting, "
           "vouchers, data entry and reconciliation " + EM + " accounted for close to three-fifths "
           "of the time, which is itself an instructive finding about the nature of a small "
           "enterprise finance function.")

    def timeuse(dd, x, y, w, h):
        half = (w - 20) / 2.0
        ch.donut(dd, x, y, half, h,
                 [22, 18, 16, 14, 12, 10, 8],
                 ["Data entry & reconciliation", "Fee collection & receipts",
                  "Vouchers & petty cash", "Budget preparation", "Vendor invoice verification",
                  "MIS & variance analysis", "Mini-project & report"],
                 colors=[BLUE, BLUE_M, TEAL, PURPLE, GOLD, ORANGE, GREEN],
                 center_value="100%", center_title="of internship time", size=6.8)
        ch.bar_h(dd, x + half + 20, y, half, h,
                 ["Routine transaction work", "Analytical & reporting work", "Verification & control",
                  "Learning & orientation"],
                 [56, 22, 12, 10], colors=[BLUE, ORANGE, TEAL, GREY_M],
                 fmt=lambda v: "%d%%" % v, xmax=60, label_w=88, size=7.2)

    d.figure(184, timeuse, "Distribution of internship time by individual task (left) and by the "
                           "nature of the work performed (right).")

    d.section("3.4  Description of Key Tasks Performed", key="3.4")
    d.subsection("3.4.1  Assistance in fee collection and receipt generation")
    d.para("One of the primary responsibilities assigned during the internship was to assist the "
           "front office and finance team in recording fee payments made by students enrolling for "
           "counselling sessions, training programmes and internship-facilitation packages. This "
           "involved verifying the amount paid against the applicable fee structure for the "
           "specific programme, recording the transaction in the fee register and accounting "
           "software, and generating an official receipt for the student. The task provided a "
           "practical understanding of how a service organisation recognises revenue at the point "
           "of cash or digital receipt, and how discrepancies such as partial payments or discount "
           "applications are handled and documented.")

    def fee_flow(dd, x, y, w, h):
        dg.flowchart(dd, x, y, w, h,
                     [("start", "Student presents fee (cash / UPI / transfer)"),
                      ("process", "Verify amount against the applicable fee structure"),
                      ("decision", "Does the amount tally?"),
                      ("process", "Record in fee register and billing software"),
                      ("doc", "Sequentially numbered receipt issued to the student"),
                      ("end", "Daily collection register totalled and signed")],
                     side_notes=[(2, "If a partial payment or an approved discount is involved, "
                                     "the mentor's authorisation is recorded before the receipt is "
                                     "raised.", ORANGE),
                                 (4, "The receipt copy feeds the monthly bank reconciliation and "
                                     "the MIS collection figure.", BLUE)])

    d.figure(252, fee_flow, "Fee collection and receipting process followed at the front office, "
                            "with the control points observed during the internship.")

    d.subsection("3.4.2  Preparation of vouchers and petty cash management")
    d.para("The intern was trained in the preparation of payment vouchers for petty cash expenses "
           "such as stationery purchases, refreshments for guest sessions, local conveyance for "
           "staff, and minor repairs. Each voucher required supporting bills to be attached, "
           "appropriate authorisation to be obtained, and the expense head to be correctly "
           "classified for entry into the books of account. Maintaining the petty cash register and "
           "periodically reconciling the physical cash balance with the recorded balance offered "
           "valuable insight into the discipline required in cash handling and the importance of "
           "the voucher system as an internal control mechanism.")

    def voucher_flow(dd, x, y, w, h):
        dg.chevrons(dd, x, y + h - 50, w, 50,
                    [("Requirement",), ("Supporting bill",), ("Voucher prepared",),
                     ("Authorisation",), ("Payment",), ("Filing & numbering",)])
        dg.card_grid(dd, x, y, w, h - 62,
                     [("Where errors were caught", "expense heads misclassified between "
                       "'printing' and 'marketing material'; corrected on mentor review", ORANGE),
                      ("Why the sequence matters", "an unnumbered voucher can be lost without trace, "
                       "which is why numbering precedes payment", BLUE),
                      ("Control learning", "the person preparing the voucher is not the person "
                       "authorising payment, even in a small team", TEAL)], cols=3, icon_num=False)

    d.figure(168, voucher_flow, "Petty cash voucher cycle, and the practical lessons drawn from "
                                "working within it.")

    d.subsection("3.4.3  Data entry and maintenance of financial records")
    d.para("A significant portion of the internship involved data entry tasks, including updating "
           "the daily collection register, maintaining the expense tracker in a spreadsheet format, "
           "and assisting in the reconciliation of bank statements with the internal cash book. "
           "This task, while repetitive in nature, was instrumental in developing familiarity with "
           "spreadsheet functions such as SUM, VLOOKUP and conditional formatting, which were used "
           "to flag discrepancies and to generate quick summaries for the finance executive.")
    d.subsection("3.4.4  Assistance in budget preparation for a training batch")
    d.para("During the fourth and fifth weeks of the internship, the intern was involved in "
           "assisting the preparation of a budget for an upcoming batch of a skill-development "
           "training programme. This required estimating the likely enrolment based on past trends "
           "and current enquiry levels, computing the variable cost per student covering trainer "
           "fees, study material and certificates, estimating the fixed costs to be apportioned "
           "such as venue, utilities and marketing for the batch, and arriving at a break-even "
           "enrolment figure together with a recommended fee per student that would ensure a "
           "reasonable contribution margin. The resulting working is presented as Table 5.1 and "
           "analysed in Sections 5.3 to 5.5.")
    d.subsection("3.4.5  Vendor payment processing and invoice verification")
    d.para("The intern also assisted in verifying invoices received from vendors, such as suppliers "
           "of study material, digital marketing agencies and facility maintenance contractors, "
           "checking them against the corresponding purchase order or agreed terms, and preparing "
           "payment requests for approval by the Director. This task highlighted the importance of "
           "a proper approval hierarchy and documentation trail in preventing unauthorised or "
           "erroneous payments, and introduced the practical checks required on a GST invoice "
           "before input tax credit can be claimed.")
    d.subsection("3.4.6  Support in preparation of monthly MIS and financial summary")
    d.para("Towards the concluding phase of the internship, the intern assisted in compiling a "
           "simplified Management Information System (MIS) report summarising total collections, "
           "total expenses, department-wise cost break-up and a comparison against the budgeted "
           "figures for the month. This exercise provided direct exposure to how variance analysis "
           "is used by management to identify areas of overspending or underperformance in revenue "
           "collection, and to take timely corrective action. The illustrative output of this "
           "exercise appears as Table 5.2 and Figure 5.5.")
    d.subsection("3.4.7  Mini-project: financial analysis exercise")
    d.para("As a capstone task for the internship, the intern was asked to compile an analytical "
           "note on the organisation's cost structure and to compute basic financial ratios using "
           "the data made available, which forms the basis of Chapters 4, 5 and 6 of this report. "
           "This exercise was reviewed by the finance mentor and discussed with the Director as "
           "part of the internship completion process.")

    d.section("3.5  Volume of Work Handled During the Internship", key="3.5")
    d.para("To give a concrete sense of the scale of work handled, the following approximate counts "
           "were maintained in the personal activity log kept through the internship. They are "
           "modest numbers in absolute terms, but for a first exposure to a live accounting "
           "environment they represented sufficient repetition for the underlying formats and "
           "controls to become familiar.")
    d.stat_cards([("148", "fee receipts assisted or verified", BLUE),
                  ("96", "petty cash vouchers prepared", TEAL),
                  ("34", "vendor invoices verified", PURPLE),
                  ("16", "financial ratios computed", ORANGE)], h=52)
    d.table(["Work item", "Approximate volume handled", "Nature of involvement"],
            [["Fee receipts recorded or verified", "148 receipts", "Assisted, then independent"],
             ["Petty cash vouchers prepared", "96 vouchers", "Independent after week 3"],
             ["Entries made in the expense tracker", "Over 500 line items", "Independent"],
             ["Bank reconciliation statements assisted", "7 weekly reconciliations", "Assisted"],
             ["Vendor invoices verified against terms", "34 invoices", "Assisted"],
             ["Payment requests drafted for approval", "21 requests", "Assisted"],
             ["Batch budgets prepared or revised", "3 budget sheets", "Assisted"],
             ["Monthly MIS packs compiled", "2 MIS packs", "Assisted"],
             ["Financial ratios computed and interpreted", "16 ratios", "Independent"]],
            [1.8, 1.2, 1.3], size=8.5, caption="Indicative volume of work handled during the "
                                               "internship",
            aligns=["left", "center", "left"], header_align=["left", "center", "left"])

    d.section("3.6  Tools and Software Used", key="3.6")
    d.para("During the course of the internship, the intern gained working familiarity with the "
           "following tools, which are commonly used in small and medium enterprises for finance "
           "and administration functions: spreadsheets (MS Excel and Google Sheets) for registers, "
           "budgets, ratio computation and simple charts for MIS reporting; the basic accounting "
           "and billing software used by the organisation for recording student fee receipts and "
           "generating GST-compliant invoices; MS Word for internal notes, minutes and vendor "
           "correspondence; and WhatsApp Business together with email for coordinating fee "
           "reminders with students and invoice clarifications with vendors.")

    def tools(dd, x, y, w, h):
        ch.dumbbell(dd, x, y, w, h,
                    ["Spreadsheet formulas & lookups", "Pivot tables & summaries",
                      "Accounting / billing software", "GST invoice checking",
                      "Chart preparation for MIS", "Professional email drafting"],
                    [3, 2, 1, 1, 3, 5], [8, 7, 7, 6, 8, 8],
                    fmt=lambda v: "%.0f/10" % v, maxv=10,
                    legend_labels=("Self-assessed at start", "Self-assessed at close"))

    d.figure(176, tools, "Self-assessed familiarity with the principal tools used, at the start and "
                         "at the close of the internship.")

    d.section("3.7  Interaction with Different Departments", key="3.7")
    d.para("Although the internship was based in the Finance and Administration department, the "
           "nature of a small organisation meant that the intern regularly interacted with the "
           "Counselling and Training team to obtain enrolment data, with the Business Development "
           "team to understand corporate tie-up arrangements that had revenue implications, and "
           "with the front office to cross-verify daily collection figures. This cross-functional "
           "interaction was instrumental in appreciating how financial data flows from operational "
           "activities into the accounting system, and how, in turn, financial constraints and "
           "targets shape operational decisions such as batch scheduling and marketing spend.")

    def interaction(dd, x, y, w, h):
        dg.hub_spokes(dd, x, y, w, h, "Finance & Administration",
                      [("Front office", "daily collection figures and receipts"),
                       ("Counselling team", "session and enrolment data"),
                       ("Training team", "batch cost estimates and attendance"),
                       ("Business development", "corporate billing terms"),
                       ("External chartered accountant", "GST, TDS and annual filings"),
                       ("Director", "approvals above the delegated limit")])

    d.figure(214, interaction, "Information flows between the finance function and the rest of the "
                               "organisation, as experienced during the internship.")



# ==========================================================================
# CHAPTER 4
# ==========================================================================
def chapter4(d):
    d.reset_counters()
    d.chapter("4", "Financial Management Analysis", key="ch4",
              kicker="This chapter analyses how the organisation actually manages money: the "
                     "objectives it sets, where its funds come from and go to, how revenue is "
                     "recognised, how its costs behave, how working capital and seasonality are "
                     "handled, how financial decisions are authorised, and the internal control "
                     "and compliance framework within which all of this operates.")

    d.section("4.1  Concept and Scope of Financial Management", key="4.1")
    d.para("Financial management may be defined as the planning, organising, directing and "
           "controlling of the financial activities of an enterprise, including the procurement and "
           "utilisation of funds. It encompasses decisions relating to investment, that is where "
           "funds should be deployed; financing, that is from where funds should be raised; and "
           "distribution, that is how much of the surplus should be reinvested rather than "
           "withdrawn " + EM + " all aimed at maximising the value of the enterprise while "
           "ensuring adequate liquidity and an acceptable level of risk.")

    def fm_cycle(dd, x, y, w, h):
        dg.cycle(dd, x, y, w, h,
                 [("Planning", "forecast revenue, cost and cash for the year and for each batch"),
                  ("Organising", "decide who records, who approves and who reports"),
                  ("Directing", "price services, release payments, allocate marketing spend"),
                  ("Controlling", "compare actual against budget and act on the variance")],
                 center_title="Financial management", center_sub="a continuous function",
                 colors=[NAVY, BLUE, BLUE_M, TEAL])

    d.figure(214, fm_cycle, "The four functions of financial management as they were observed "
                            "operating within the organisation.")
    d.para("In the context of a service-sector small enterprise such as Infinity Interns, financial "
           "management manifests in a somewhat simplified but equally important form. Investment "
           "decisions relate to expenditure on infrastructure such as classrooms, computers and "
           "furniture, on technology such as accounting software and learning platforms, and on "
           "marketing. Financing decisions relate to the extent to which the promoter's own "
           "capital, retained earnings or short-term borrowings are used to fund working capital "
           "requirements. Distribution decisions relate to how much of the surplus generated is "
           "withdrawn by the promoters as against retained for reinvestment into expansion, such "
           "as opening a second centre.")

    d.section("4.2  Financial Objectives of the Organisation", key="4.2")
    d.para("Through discussions with the finance executive and the Director, it was observed that "
           "the organisation's financial objectives during the period under review could be "
           "summarised under five heads. Each objective is paired below with the indicator the "
           "finance function actually uses to judge whether the objective is being met, since an "
           "objective without a measure tends not to influence behaviour.")
    d.table(["Financial objective", "Indicator used in practice", "Position in the year under review"],
            [["Maintain liquidity sufficient to meet monthly fixed obligations without external "
              "borrowing", "Current ratio; cash balance against one month of fixed cost",
              "Current ratio 1.92:1; cash of " + rs(597000) + " against fixed monthly cost of "
              "about " + rs(260000)],
             ["Achieve a target contribution margin on every batch and counselling package",
              "Contribution per student; break-even enrolment",
              "Contribution of " + rs(4000) + " per student; break-even at 17 of 30 seats"],
             ["Build retained earnings to fund future capital expenditure",
              "Reserves and surplus; proportion of profit retained",
              "Reserves of " + rs(2525000) + ", being 72 per cent of shareholders' funds"],
             ["Ensure timely and complete collection of fees",
              "Debtors' turnover; average collection period",
              "9.6 times a year; about 38 days"],
             ["Control discretionary expenditure in line with enrolment performance",
              "Marketing cost per enrolment; monthly variance against budget",
              "About " + rs(774) + " per enrolment; adverse marketing variance of "
              + rs(13000) + " in the month reviewed"]],
            [1.5, 1.2, 1.7], size=8.4, caption="Financial objectives and the indicators used to "
                                               "monitor them", header_align=["left"] * 3)

    d.section("4.3  Sources and Application of Funds", key="4.3")
    d.para("The primary source of funds for Infinity Interns is the fee income collected from "
           "students and corporate clients for counselling, training and internship-facilitation "
           "services, supplemented by the promoters' own capital contribution at the time of "
           "incorporation and expansion. As a relatively young private limited company, the "
           "organisation has, to the extent observed, relied minimally on external debt, preferring "
           "to fund its working capital and modest capital expenditure requirements through "
           "internal accruals and promoter capital " + EM + " a conservative financing approach "
           "common among small service enterprises seeking to avoid the fixed interest burden "
           "associated with borrowed funds.")

    def funds(dd, x, y, w, h):
        dg.fund_flow(dd, x, y, w, h,
                     [("Student fee income", 4000000, BLUE),
                      ("Corporate service fees", 800000, BLUE_M),
                      ("Promoter capital", 1000000, TEAL),
                      ("Retained earnings", 2525000, GREEN),
                      ("Long-term borrowings", 845000, ORANGE)],
                     [("Salaries & honorarium", 1950000, PURPLE),
                      ("Rent & administration", 670000, BLUE_M),
                      ("Marketing & outreach", 480000, GOLD),
                      ("Infrastructure", 3526000, TEAL),
                      ("Study material", 550000, ORANGE),
                      ("Taxes & statutory", 150000, RED)],
                     hub_label="Pool of funds available", fmt=lambda v: rs_plain(v))

    d.figure(228, funds, "Sources of funds and their application, as observed during the internship "
                         "(illustrative amounts in " + R + ").")
    d.para("The principal applications of funds observed during the internship period included "
           "payment of staff salaries and trainer honorariums, rent for the office and training "
           "premises, marketing and promotional expenditure covering digital advertising, print "
           "material and outreach events at schools and colleges, technology and software "
           "subscription costs, and statutory payments such as GST and advance tax remitted "
           "through the company's chartered accountant. The largest single application is "
           "infrastructure, which is a cumulative figure carried in the balance sheet rather than "
           "an annual outflow, and this is the reason the organisation's asset turnover requires "
           "attention even though its margins are healthy.")

    def sources_bars(dd, x, y, w, h):
        ch.composition_bars(dd, x, y, w, h,
                            [("Sources of long-term and short-term funds",
                              [("Promoter capital", 1000000, BLUE),
                               ("Reserves & surplus", 2525000, BLUE_M),
                               ("Long-term borrowings", 845000, ORANGE),
                               ("Current liabilities", 700000, GREY_M)]),
                             ("Application of those funds",
                              [("Net fixed assets", 3526000, TEAL),
                               ("Investments", 200000, PURPLE),
                               ("Receivables", 500000, GOLD),
                               ("Cash & bank", 597000, GREEN),
                               ("Inventory & other current assets", 247000, GREY_M)])],
                            fmt=lambda v: rs(v), legends=True, bar_h=28, gap=44)

    d.figure(186, sources_bars, "Balance-sheet view of the same picture: how the funds raised are "
                                "deployed across assets at the year-end.")

    d.section("4.4  Revenue Recognition and Fee Structure", key="4.4")
    d.para("Revenue for the organisation is generated through distinct fee structures for each of "
           "its service verticals. Career counselling sessions are typically charged on a "
           "per-session or package basis, skill-development training programmes are charged per "
           "batch enrolment with fees varying by course duration and content, and "
           "internship-facilitation services are charged either as a one-time placement fee "
           "payable by the student or, in certain arrangements, as a service fee payable by the "
           "partner company availing candidates through the platform.")
    d.para("Revenue is recognised at the point of service delivery or, in the case of package-based "
           "programmes spanning multiple sessions, proportionately as sessions are conducted " +
           EM + " a practice consistent with the accrual concept of accounting and appropriate for "
           "a service business where the obligation to the customer is fulfilled progressively "
           "rather than at a single point in time.")
    d.table(["Vertical", "When cash is received", "When revenue is recognised",
             "Balance-sheet consequence"],
            [["Single counselling session", "At the time of the session",
              "Immediately on delivery of the session", "No timing difference"],
             ["Counselling package", "Substantially in advance at enrolment",
              "Proportionately as each session is conducted",
              "Unearned portion carried as a current liability"],
             ["Training programme", "Majority at enrolment, balance before the final module",
              "Spread over the duration of the batch",
              "Advance collection funds part of the batch cost"],
             ["Internship facilitation (student)", "Part upfront, part on placement",
              "On successful placement of the candidate",
              "Receivable until the placement is confirmed"],
             ["Internship facilitation (corporate)", "On invoice, typically 15 to 30 days",
              "On completion of the candidate hand-over", "Trade receivable with GST payable"]],
            [1.0, 1.4, 1.4, 1.35], size=8.3,
            caption="Fee collection and revenue recognition pattern by vertical",
            header_align=["left"] * 4)
    d.callout("Why this distinction mattered during the internship",
              "The receipting work described in Section 3.4.1 records a cash inflow, not "
              "necessarily revenue of that month. Learning to separate the two " + EM +
              " a receipt in June for a batch running through July " + EM + " was the clearest "
              "practical illustration of the accrual concept encountered during the internship.",
              color=BLUE, bg=BLUE_XL)

    d.section("4.5  Cost Structure of the Organisation", key="4.5")
    d.para("The cost structure of Infinity Interns, like that of most service organisations, is "
           "dominated by personnel-related costs rather than material costs. Based on observation "
           "and discussion with the finance team, the major cost heads may be classified as shown "
           "below, expressed both as a share of the total cost base of " + rs(TOTAL_COST) +
           " and as a percentage of revenue.")
    d.table(["Cost head", "Cost behaviour", "Amount (" + R + ")", "Share of total cost",
             "% of revenue"],
            [[h, n, rs_plain(a), pct(a * 100.0 / TOTAL_COST), pct(p)]
             for (h, n, a, p, c) in COST_HEADS]
            + [["Total cost base", "", rs_plain(TOTAL_COST), "100.0%",
                pct(TOTAL_COST * 100.0 / REVENUE)]],
            [2.1, 1.0, 0.95, 0.85, 0.75], size=8.3,
            caption="Cost structure of the organisation (illustrative)",
            aligns=["left", "left", "right", "right", "right"],
            header_align=["left", "left", "right", "right", "right"],
            bold_rows=[7],
            note="Management describes employee cost as running at forty to forty-five per cent of "
                 "revenue; the illustrative statement reflects this at 40.6 per cent.")

    def cost_fig(dd, x, y, w, h):
        half = (w - 22) / 2.0
        ch.bar_h(dd, x, y, half, h,
                 ["Employee costs", "Training material", "Marketing", "Rent & utilities",
                  "Administration", "Depreciation", "Finance cost"],
                 [c[3] for c in COST_HEADS], colors=[c[4] for c in COST_HEADS],
                 fmt=lambda v: pct(v), xmax=45, label_w=78, size=7.2)
        ch.donut(dd, x + half + 22, y, half, h,
                 [c[1] for c in COST_BEHAVIOUR], [c[0] for c in COST_BEHAVIOUR],
                 colors=[c[2] for c in COST_BEHAVIOUR], center_value="73%",
                 center_title="of cost is fixed", size=7.0, legend_side=True)

    d.figure(180, cost_fig, "Cost heads as a percentage of revenue (left) and the fixed, variable "
                            "and semi-variable split of the total cost base (right).")
    d.para("Nearly three-quarters of the cost base does not vary with the number of students "
           "enrolled in a given month. This single fact drives much of the financial behaviour "
           "described in the remainder of this report: it explains why break-even analysis is "
           "taken seriously before a batch is launched, why utilisation of the training hall "
           "matters, and why a shortfall in enrolment translates almost immediately into a "
           "shortfall in surplus rather than being cushioned by a fall in costs.")

    d.section("4.6  Working Capital Management", key="4.6")
    d.para("Working capital management assumes particular importance for a fee-based service "
           "organisation such as Infinity Interns, since the timing mismatch between fee "
           "collection, which is often received in advance or in instalments, and expenditure, "
           "which is largely fixed and recurring in nature such as monthly salaries and rent, "
           "determines the organisation's day-to-day liquidity position.")
    d.stat_cards([(rs(1344000), "current assets", BLUE),
                  (rs(700000), "current liabilities", ORANGE),
                  (rs(644000), "net working capital", GREEN),
                  ("38 days", "average collection period", TEAL)], h=54)
    d.para("It was observed that the organisation follows a policy of collecting a substantial "
           "portion of the programme fee at the time of enrolment, with the balance, if any, "
           "collected before the commencement of the concluding module of the programme. This "
           "practice of advance collection helps the organisation maintain a favourable working "
           "capital cycle for its training and counselling verticals, effectively allowing student "
           "fee collections to fund a part of the operating expenses even before the corresponding "
           "services are fully delivered. The internship-facilitation vertical, however, where "
           "fees are sometimes contingent upon the successful placement of the candidate, exhibits "
           "a longer collection cycle and requires closer monitoring.")

    def wc_cycle(dd, x, y, w, h):
        dg.cycle(dd, x, y, w, h,
                 [("Enquiry and enrolment", "advance fee collected at the point of enrolment"),
                  ("Service delivery", "counsellor and trainer time consumed over the batch"),
                  ("Balance collection", "residual fee collected before the final module"),
                  ("Payment of costs", "salaries, honorarium, rent and vendor bills settled"),
                  ("Surplus retained", "reserves built for infrastructure and expansion")],
                 center_title="Cash cycle", center_sub="advance-funded",
                 colors=[NAVY, BLUE, BLUE_M, ORANGE, GREEN])

    d.figure(222, wc_cycle, "Working capital cycle of the organisation; because cash is largely "
                            "collected before the service is delivered, the cycle funds itself.")
    d.table(["Element of the cycle", "Observed position", "Financial effect"],
            [["Advance fee collection at enrolment",
              "A substantial share of the programme fee is collected upfront",
              "Reduces the need for external working capital"],
             ["Average collection period", "About 38 days overall",
              "Acceptable for a business with limited credit sales"],
             ["Internship facilitation receipts", "Partly contingent on placement outcome",
              "Lengthens the cycle and introduces collection risk"],
             ["Trade payables of " + rs(400000), "Vendor bills settled on agreed terms",
              "Provides a short, interest-free source of funds"],
             ["Cash and bank balance of " + rs(597000),
              "Equivalent to roughly two months of fixed cost",
              "Comfortable buffer against a lean collection month"]],
            [1.2, 1.5, 1.4], size=8.4, caption="Components of the working capital cycle",
            header_align=["left"] * 3)

    d.section("4.7  Seasonality of Collections and Cash Planning", key="4.7")
    d.para("Collections in this business are not spread evenly through the year. They cluster around "
           "the school and college admission cycle, with a pronounced peak between May and July and "
           "a secondary peak in the January to February window when board examinations approach and "
           "parents seek guidance on course selection. Fixed costs, by contrast, accrue evenly every "
           "month. The chart below places the two series together, which is the single most useful "
           "picture for cash planning in this organisation.")

    def seasonality(dd, x, y, w, h):
        ch.line_chart(dd, x, y, w, h, MONTHS,
                      [("Monthly fee collections", COLLECTIONS, BLUE),
                       ("Fixed monthly cash outflow", FIXED_OUT, ORANGE)],
                      area=0, fmt=lambda v: "%.1f" % v, tick_fmt=lambda v: "%.0fL" % v,
                      ylabel="" + R + " lakh", ticks=4, value_labels=0, label_size=6.9)

    d.figure(190, seasonality, "Monthly collections against the largely unchanging monthly fixed "
                              "outflow; the shaded gap in the lean months is what a rolling cash "
                              "forecast is meant to anticipate.")
    d.table(["Quarter", "Collections (" + R + " lakh)", "Share of annual collection",
             "Fixed outflow (" + R + " lakh)", "Cash position"],
            [["Q1 (Apr " + EN + " Jun)", "12.9", "26.9%", "7.8", "Strong surplus"],
             ["Q2 (Jul " + EN + " Sep)", "14.2", "29.6%", "7.8", "Peak surplus"],
             ["Q3 (Oct " + EN + " Dec)", "8.9", "18.5%", "7.8", "Thin surplus"],
             ["Q4 (Jan " + EN + " Mar)", "12.0", "25.0%", "7.8", "Recovering surplus"],
             ["Full year", "48.0", "100.0%", "31.2", "Comfortable"]],
            [1.2, 1.0, 1.0, 1.0, 1.0], size=8.5, caption="Quarterly pattern of collections against "
                                                         "fixed outflow",
            aligns=["left", "right", "right", "right", "left"],
            header_align=["left", "right", "right", "right", "left"], bold_rows=[4])
    d.para("The October to December quarter contributes less than a fifth of annual collections "
           "while carrying a quarter of the annual fixed cost. The organisation manages this "
           "through the surplus accumulated in the first two quarters rather than through "
           "borrowing, which works at the present scale but becomes progressively riskier as fixed "
           "costs grow. This is the reasoning behind the suggestion in Chapter 9 that a rolling "
           "twelve-month cash forecast be maintained and reviewed monthly.")

    d.section("4.8  Financial Decision-Making Process Observed", key="4.8")
    d.para("During the internship, it was observed that significant financial decisions " + EM +
           " approval of expenditure above a certain threshold, the launch of a new training "
           "programme, or a revision of the fee structure " + EM + " were taken by the Director in "
           "consultation with the finance executive, based on a combination of quantitative "
           "analysis such as expected enrolment, cost estimates and break-even calculations, and "
           "qualitative judgement such as market demand, competitive positioning and brand "
           "considerations. Routine and recurring expenditure within pre-approved limits was "
           "authorised directly by the finance executive, reflecting a sensible delegation of "
           "financial authority appropriate to the size of the organisation.")

    def decision_flow(dd, x, y, w, h):
        dg.flowchart(dd, x, y, w, h,
                     [("start", "Proposal raised by a department"),
                      ("process", "Finance executive prepares a cost estimate"),
                      ("decision", "Within the delegated limit?"),
                      ("process", "Director reviews demand, margin and break-even"),
                      ("doc", "Approval recorded on the payment request or budget sheet"),
                      ("end", "Expenditure released and entered in the books")],
                     side_notes=[(2, "If within the limit, the finance executive authorises the "
                                     "payment directly and the proposal skips the Director's "
                                     "review.", TEAL),
                                 (3, "Quantitative test: does the proposal clear the required "
                                     "contribution margin at a realistic enrolment level?",
                                  ORANGE)])

    d.figure(248, decision_flow, "Path followed by a spending or pricing proposal from the "
                                 "originating department to release of funds.")
    d.table(["Decision or expenditure type", "Authority observed", "Basis of the decision"],
            [["Routine recurring expense within the pre-approved limit", "Finance executive",
              "Budget already sanctioned for the head"],
             ["Petty cash expense supported by a bill", "Finance executive",
              "Voucher with supporting bill and expense head"],
             ["Vendor payment against a verified invoice", "Director on recommendation",
              "Invoice matched to the purchase order or agreed terms"],
             ["Launch or postponement of a training batch", "Director with the finance executive",
              "Pre-enrolment count against break-even enrolment"],
             ["Revision of the fee structure of a programme", "Director",
              "Contribution margin, competitor pricing and demand"],
             ["Capital expenditure on equipment or premises", "Director / promoters",
              "Availability of reserves and expected utilisation"],
             ["Marketing campaign above the monthly allocation", "Director",
              "Expected cost per enrolment and channel history"]],
            [1.9, 1.15, 1.7], size=8.4, caption="Delegation of financial authority as observed",
            header_align=["left"] * 3)

    d.section("4.9  Role of Technology in Financial Management", key="4.9")
    d.para("The organisation has progressively adopted spreadsheet-based and basic accounting "
           "software tools to bring greater accuracy and speed to its financial processes, moving "
           "away from the manual registers used in its early years of operation. This gradual "
           "digitisation was observed to reduce reconciliation errors, speed up the generation of "
           "receipts and invoices, and provide the Director with quicker access to summary "
           "financial information for decision-making, illustrating the broader trend among small "
           "and medium enterprises in India towards the adoption of digital financial tools even in "
           "the absence of a full-fledged Enterprise Resource Planning system.")

    def tech_ladder(dd, x, y, w, h):
        dg.stack(dd, x, y, w, h,
                 [("Stage 1 " + EN + " Manual registers", "handwritten fee and expense registers; "
                   "used in the early years of operation", GREY_M),
                  ("Stage 2 " + EN + " Spreadsheets", "expense tracker, budget sheets and ratio "
                   "workings; the present working backbone", BLUE),
                  ("Stage 3 " + EN + " Billing software", "GST-compliant invoices and receipts "
                   "generated from a single master", TEAL),
                  ("Stage 4 " + EN + " Integrated accounting (proposed)", "one ledger feeding "
                   "receipts, payments, MIS and statutory returns", ORANGE),
                  ("Stage 5 " + EN + " Analytics and dashboards (aspirational)",
                   "cost per enrolment and contribution tracked automatically", GREEN)])

    d.figure(180, tech_ladder, "Digitisation ladder of the finance function: the organisation "
                               "currently operates across stages two and three.")

    d.section("4.10  Internal Control Environment", key="4.10")
    d.para("Internal control refers to the policies and procedures adopted by an organisation to "
           "ensure the orderly and efficient conduct of its business, including adherence to "
           "management policies, safeguarding of assets, prevention and detection of fraud and "
           "error, accuracy and completeness of accounting records, and timely preparation of "
           "reliable financial information. Even though Infinity Interns is a small enterprise not "
           "statutorily required to maintain the elaborate internal control frameworks mandated for "
           "larger listed companies, several sound internal control practices were nonetheless "
           "observed during the internship.")

    def controls(dd, x, y, w, h):
        dg.pyramid(dd, x, y, w, h,
                   [("Supporting documents retained",
                     "bills, invoices and agreements filed against every payment, supporting both "
                     "internal review and the annual audit", BLUE_L),
                    ("Sequential vouchers and receipts",
                     "numbering makes an omitted or duplicated transaction traceable", BLUE_M),
                    ("Periodic verification",
                     "physical petty cash count and monthly bank reconciliation", BLUE),
                    ("Segregation of duties",
                     "collection, recording and approval kept with different people so far as the "
                     "team size permits", NAVY_D)])

    d.figure(176, controls, "Internal control practices observed, arranged from the routine "
                            "documentary base upward to the segregation of duties.")
    d.para("These practices, while modest in scale compared to the internal control frameworks of "
           "large corporations, reflect a reasonable and proportionate approach for an organisation "
           "of this size, and were observed to function effectively in preventing and detecting the "
           "kind of small errors and discrepancies that are common in any organisation handling "
           "daily cash transactions. A defined approval hierarchy for expenditure above specified "
           "thresholds, as set out in Section 4.8, completes the framework.")

    d.section("4.11  Taxation and Statutory Compliance Considerations", key="4.11")
    d.para("As a private limited company providing taxable services, Infinitya1 Career Counselling "
           "Private Limited is required to comply with the applicable provisions of the Goods and "
           "Services Tax law, the Income Tax Act and the Companies Act, 2013. During the "
           "internship, exposure was gained to the process of verifying that fee invoices raised to "
           "corporate clients correctly reflected the applicable GST rate and the company's GST "
           "registration details, and that vendor invoices received by the company similarly "
           "complied with GST invoicing requirements so as to enable the company to claim eligible "
           "input tax credit.")
    d.table(["Compliance obligation", "Periodicity", "Responsibility observed",
             "Role of the finance function"],
            [["GST return filing and payment", "Monthly / quarterly", "External chartered accountant",
              "Provides invoice-wise sales and purchase data"],
             ["Input tax credit reconciliation", "Monthly", "Finance executive with the accountant",
              "Verifies vendor invoices and GST details"],
             ["TDS deduction on specified payments", "At the time of payment", "Finance executive",
              "Deducts on trainer honorarium and professional fees"],
             ["TDS return filing", "Quarterly", "External chartered accountant",
              "Supplies the payment and deduction schedule"],
             ["Advance tax instalments", "Quarterly", "Director with the accountant",
              "Estimates profit for the instalment computation"],
             ["Annual accounts and audit", "Annual", "External chartered accountant",
              "Provides ledgers, vouchers and supporting files"],
             ["Annual return to the Registrar of Companies", "Annual",
              "External chartered accountant", "Supplies financial statements and particulars"]],
            [1.5, 0.9, 1.3, 1.6], size=8.3, caption="Statutory compliance calendar and the "
                                                    "finance function's role",
            header_align=["left"] * 4)
    d.para("While the detailed preparation and filing of statutory returns is handled by the "
           "company's external chartered accountant, the finance team within the organisation is "
           "responsible for maintaining the underlying transaction records in a manner that "
           "facilitates smooth and timely compliance. This coordination between the internal "
           "finance function and the external compliance professional was observed to be an "
           "important, if often understated, dimension of overall financial management in a small "
           "private limited company.")



# ==========================================================================
# CHAPTER 5
# ==========================================================================
SENS = [(12, -18000), (15, -6000), (17, 2000), (20, 14000), (24, 30000), (27, 42000), (30, 54000)]
CHANNELS = [("School and college outreach drives", 1.35, 48, 14.0, 343, TEAL),
            ("Student referral and word of mouth", 0.55, 18, 22.0, 82, GREEN),
            ("Digital advertising (search and social)", 1.70, 62, 9.0, 689, BLUE),
            ("Organic social media and content", 0.45, 24, 11.0, 218, PURPLE),
            ("Print advertising and hoardings", 0.75, 95, 4.0, 2375, ORANGE)]


def chapter5(d):
    d.reset_counters()
    d.chapter("5", "Budgeting and Cost Control", key="ch5",
              kicker="This chapter presents the budgeting work carried out during the internship: "
                     "the types of budget the organisation prepares, a complete illustrative batch "
                     "budget with its break-even and sensitivity analysis, the cost control "
                     "practices observed, a monthly variance analysis, and the annual operating "
                     "budget that ties the individual batches together.")

    d.section("5.1  Meaning and Importance of Budgeting", key="5.1")
    d.para("A budget is a quantitative statement, prepared in advance of a defined period, of the "
           "policy to be pursued during that period for the purpose of attaining a given objective. "
           "Budgeting is the process of preparing such statements and using them for planning, "
           "coordination and control. For an organisation such as Infinity Interns, budgeting "
           "serves the vital function of translating the Director's strategic intentions, such as "
           "launching a new training vertical or expanding to a second city, into specific, "
           "measurable financial targets that can be monitored and acted upon.")
    d.para("The importance of budgeting for a growing small enterprise cannot be overstated. In the "
           "absence of a formal budget, expenditure tends to be reactive and unplanned, revenue "
           "targets remain vague, and it becomes difficult to evaluate whether a particular "
           "programme or vertical is financially viable. During the internship, it was observed "
           "that the organisation had begun to formalise its budgeting process over the preceding "
           "year, moving from an informal, intuition-based approach to a more structured, "
           "spreadsheet-driven monthly and batch-wise budgeting exercise.")

    def budget_cycle(dd, x, y, w, h):
        dg.cycle(dd, x, y, w, h,
                 [("Forecast enrolment", "past trends and live enquiry levels"),
                  ("Estimate costs", "variable per student plus apportioned fixed"),
                  ("Approve the budget", "Director's sign-off on fee and seats"),
                  ("Record actuals", "receipts, vouchers and invoices"),
                  ("Analyse variance", "monthly MIS with reasons recorded"),
                  ("Revise the plan", "mid-year reset of the annual budget")],
                 center_title="Budget control cycle", center_sub="planning to control")

    d.figure(230, budget_cycle, "The budget cycle as practised: a loop in which the variance "
                                "analysis of one period becomes the planning input of the next.")

    d.section("5.2  Types of Budgets Prepared by the Organisation", key="5.2")
    d.para("During the internship period, exposure was gained to four categories of budget prepared "
           "or used by the organisation. They form a hierarchy: the annual operating budget sets "
           "the frame, the monthly cash budget protects liquidity within that frame, and the "
           "batch-wise and departmental budgets control the individual decisions that make up the "
           "year.")

    def budget_stack(dd, x, y, w, h):
        dg.stack(dd, x, y, w, h,
                 [("Annual operating budget", "total expected revenue and expenditure across all "
                   "verticals; used by the Director for planning and expansion decisions", NAVY),
                  ("Monthly cash budget", "rolling estimate of collections against salaries, rent "
                   "and vendor payments to protect liquidity", BLUE),
                  ("Batch-wise / programme budget", "variable and fixed cost of each batch and the "
                   "minimum enrolment required to break even", TEAL),
                  ("Departmental expense budget", "monthly ceiling on discretionary spend such as "
                   "travel, refreshments and office supplies", ORANGE)])

    d.figure(168, budget_stack, "Hierarchy of budgets prepared by the organisation, from the annual "
                                "frame down to departmental discretionary limits.")

    d.section("5.3  Illustrative Batch Budget " + EN + " Skill Development Programme", key="5.3")
    d.para("As part of the internship assignment described in Section 3.4.4, the intern assisted in "
           "preparing an illustrative budget for a batch of thirty students for a six-week "
           "skill-development training programme. This budget, based on figures discussed with the "
           "finance team and adjusted for confidentiality, is reproduced below.")
    d.table(["Particulars", "Basis", "Amount (" + R + ")"],
            [["Number of students in the batch", "Planned capacity", "30"],
             ["Fee per student", "Approved fee for the programme", "6,500"],
             ["Total expected revenue", "30 students x " + R + " 6,500", "1,95,000"],
             ["Variable cost per student", "Material, certificate, refreshment", "2,500"],
             ["Total variable cost", "30 students x " + R + " 2,500", "75,000"],
             ["Trainer honorarium", "Fixed for the batch", "36,000"],
             ["Venue and utilities apportioned", "Fixed for the batch", "18,000"],
             ["Marketing apportioned to the batch", "Fixed for the batch", "12,000"],
             ["Total fixed cost for the batch", "Sum of the three fixed heads", "66,000"],
             ["Total cost", "Variable plus fixed", "1,41,000"],
             ["Expected surplus", "Revenue less total cost", "54,000"],
             ["Contribution margin per student", R + " 6,500 less " + R + " 2,500", "4,000"],
             ["Break-even enrolment", R + " 66,000 divided by " + R + " 4,000", "17 students"]],
            [1.9, 1.5, 0.95], size=8.5,
            caption="Illustrative batch budget for a skill development training programme "
                    "(30 students)",
            aligns=["left", "left", "right"], header_align=["left", "left", "right"],
            bold_rows=[2, 8, 9, 10, 12])

    def batch_waterfall(dd, x, y, w, h):
        ch.waterfall(dd, x, y, w, h,
                     [("Revenue 30 x " + R + "6,500", 195000, "start"),
                      ("Variable cost", -75000, "neg"),
                      ("Trainer honorarium", -36000, "neg"),
                      ("Venue & utilities", -18000, "neg"),
                      ("Batch marketing", -12000, "neg"),
                      ("Expected surplus", 54000, "total")],
                     fmt=lambda v: "%.0fk" % (v / 1000.0), ylabel="" + R + " thousand")

    d.figure(206, batch_waterfall, "Walk from batch revenue to batch surplus; the variable cost "
                                   "block is the only one that moves with enrolment.")

    d.section("5.4  Break-Even Analysis", key="5.4")
    d.para("Break-even analysis, a direct application of cost-volume-profit relationships, was used "
           "during the internship to determine the minimum number of student enrolments required "
           "for a training batch to cover its total cost without incurring a loss. Using the "
           "figures above, with a fixed cost of " + rs(66000) + " for the batch and a variable cost "
           "of " + rs(2500) + " per student against a fee of " + rs(6500) + " per student, the "
           "contribution margin per student works out to " + rs(4000) + ". Dividing the total fixed "
           "cost by the contribution margin per student gives a break-even enrolment of "
           "approximately seventeen students, since 66,000 divided by 4,000 equals 16.5, which is "
           "rounded up to the next whole student.")

    def be_chart(dd, x, y, w, h):
        ch.breakeven(dd, x, y, w, h, 66000, 2500, 6500, 30,
                     fmt=lambda v: "%.0fk" % (v / 1000.0), bep=17,
                     unit_label="Number of students enrolled in the batch")

    d.figure(248, be_chart, "Cost-volume-profit chart for the illustrative batch: the batch turns "
                            "profitable at the seventeenth enrolment.")
    d.para("Every enrolment beyond the seventeenth adds " + rs(4000) + " directly to the "
           "organisation's surplus, because the fixed cost of the batch has already been recovered. "
           "Equally, every seat left unfilled below seventeen costs the organisation " + rs(4000) +
           " of contribution it can never recover, since an unsold seat in a scheduled batch cannot "
           "be stored and sold later. This asymmetry is why the break-even framework was found to "
           "be actively used by management while deciding whether to proceed with a proposed batch "
           "or to postpone it when pre-enrolment numbers appeared insufficient, and it illustrates "
           "the direct practical relevance of a concept taught in the financial management "
           "curriculum.")
    d.callout("Margin of safety at the planned enrolment",
              "At the planned thirty students the batch operates thirteen students above "
              "break-even, a margin of safety of about 43 per cent of planned enrolment. A batch "
              "planned at twenty students would carry a margin of safety of only 15 per cent, which "
              "is the practical reason the organisation prefers to consolidate two thin batches "
              "into one full batch rather than run both.", color=TEAL, bg=GREEN_L)

    d.section("5.5  Sensitivity of Batch Surplus to Enrolment", key="5.5")
    d.para("Because the break-even point is a single figure, it does not by itself convey how "
           "quickly the result deteriorates if enrolment falls short. The sensitivity analysis "
           "below, prepared as an extension of the budgeting assignment, sets out the surplus or "
           "deficit of the same batch at different enrolment levels.")
    d.table(["Students enrolled", "Revenue (" + R + ")", "Variable cost (" + R + ")",
             "Contribution (" + R + ")", "Fixed cost (" + R + ")", "Surplus / (deficit) (" + R + ")"],
            [[str(n), rs_plain(6500 * n), rs_plain(2500 * n), rs_plain(4000 * n), "66,000",
              ("(" + rs_plain(abs(s)) + ")") if s < 0 else rs_plain(s)] for n, s in SENS],
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.2], size=8.4,
            caption="Sensitivity of batch surplus to the level of enrolment",
            aligns=["center"] + ["right"] * 5, header_align=["center"] + ["right"] * 5,
            row_colors={0: RED_L, 1: RED_L, 2: GREEN_L, 6: GREEN_L})

    def sens_chart(dd, x, y, w, h):
        ch.line_chart(dd, x, y, w, h, [str(n) for n, _ in SENS],
                      [("Surplus / (deficit) of the batch", [s for _, s in SENS], BLUE)],
                      ymin=-30000, ymax=60000, ticks=6,
                      fmt=lambda v: "%.0fk" % (v / 1000.0), ylabel="" + R + " thousand",
                      value_labels=0, legend_on=True)
        dd.text_center(x + w / 2.0, y + 2, "Number of students enrolled", "semibold", 7.6, GREY)

    d.figure(196, sens_chart, "Surplus of the batch at different enrolment levels; the line crosses "
                              "zero between the sixteenth and seventeenth student.")
    d.para("The analysis shows that the batch swings from a deficit of " + rs(18000) + " at twelve "
           "students to a surplus of " + rs(54000) + " at thirty students, a range of " +
           rs(72000) + " driven entirely by eighteen enrolments. For management this quantifies the "
           "value of the final few enrolments in a batch and, by extension, the value of the "
           "marketing effort that produces them, which is the link between this chapter and the "
           "channel analysis in Section 5.9.")

    d.section("5.6  Cost Control Techniques Observed", key="5.6")
    d.para("Several cost control techniques were observed during the internship, reflecting the "
           "organisation's efforts to manage its cost structure prudently despite its small scale "
           "of operations.")

    def cost_controls(dd, x, y, w, h):
        dg.card_grid(dd, x, y, w, h,
                     [("Pre-approval of discretionary spend", "any discretionary expenditure above "
                       "a defined threshold requires approval before it is incurred, which checks "
                       "small but recurring leakages", BLUE),
                      ("Budget against actual review", "significant variances are discussed in the "
                       "periodic review meeting between the Director and the finance executive",
                       TEAL),
                      ("Vendor rate negotiation", "printing and stationery are bought on annual or "
                       "bulk terms rather than through ad-hoc purchases", PURPLE),
                      ("Trainer mix rationalisation", "in-house trainers take recurring modules and "
                       "external experts only specialised sessions", ORANGE),
                      ("Channel-wise marketing review", "spend is monitored on a cost-per-enquiry "
                       "and cost-per-enrolment basis and weak channels are discontinued", GOLD),
                      ("Periodic reconciliation", "petty cash and bank balances are reconciled so "
                       "discrepancies are caught early", GREEN)], cols=3)

    d.figure(196, cost_controls, "Cost control techniques in use, each of which the intern observed "
                                 "or participated in during the internship.")

    d.section("5.7  Budgetary Variance Analysis", key="5.7")
    d.para("As part of the monthly MIS exercise described in Section 3.4.6, the intern assisted in "
           "preparing a variance analysis comparing budgeted and actual figures for a "
           "representative month during the internship period. An illustrative version, with "
           "figures adjusted for confidentiality while preserving the proportional relationships "
           "observed, is presented below. A favourable variance is marked (F) and an adverse "
           "variance (A).")
    d.table(["Particulars", "Budgeted (" + R + ")", "Actual (" + R + ")", "Variance (" + R + ")",
             "Remarks"],
            [[n, rs_plain(b), rs_plain(a),
              ("Nil" if v == 0 else (("+" if v > 0 else "-") + rs_plain(abs(v)) +
                                     (" (F)" if v > 0 else " (A)"))), r]
             for (n, b, a, v, r) in VARIANCE],
            [1.35, 0.9, 0.9, 1.0, 1.7], size=8.4,
            caption="Illustrative monthly budget variance analysis",
            aligns=["left", "right", "right", "right", "left"],
            header_align=["left", "right", "right", "right", "left"], bold_rows=[5])

    def variance_figs(dd, x, y, w, h):
        half = (w - 24) / 2.0
        ch.tornado(dd, x, y, half, h,
                   [v[0] for v in VARIANCE[:5]], [v[3] for v in VARIANCE[:5]],
                   fmt=lambda v: ("%+.1fk" % (v / 1000.0)) if v else "nil", size=7.0)
        ch.bar_grouped(dd, x + half + 24, y, half, h,
                       ["Fee coll.", "Employee", "Marketing", "Rent", "Admin"],
                       [("Budget", [v[1] for v in VARIANCE[:5]], BLUE_L),
                        ("Actual", [v[2] for v in VARIANCE[:5]], BLUE)],
                       fmt=lambda v: "%.0fk" % (v / 1000.0),
                       tick_fmt=lambda v: "%.0fk" % (v / 1000.0), ticks=4, label_size=6.8)

    d.figure(196, variance_figs, "Variance by head, favourable to the right and adverse to the left "
                                 "(left panel), with budget against actual for the same heads "
                                 "(right panel).")
    d.para("The illustrative variance analysis indicates a favourable variance in fee collection, "
           "arising from higher-than-expected enrolment in the training vertical, and a marginally "
           "unfavourable variance in marketing expenditure, attributable to a mid-month decision to "
           "run an additional promotional campaign to capitalise on the strong enrolment momentum. "
           "It is worth noting that the adverse marketing variance of " + rs(13000) + " was "
           "incurred deliberately to secure the favourable collection variance of " + rs(35000) +
           ", which is precisely the distinction between an adverse variance and a bad decision. "
           "Such exercises were found to be a valuable management tool for understanding not merely "
           "whether actual performance deviated from the plan, but why it deviated, and whether the "
           "underlying cause warranted a change in future budgets or merely represented a one-off "
           "event.")

    d.section("5.8  Illustrative Annual Operating Budget", key="5.8")
    d.para("In addition to the batch-level budget discussed above, the organisation prepares a "
           "consolidated annual operating budget aggregating expected revenue and expenditure "
           "across its service verticals. An illustrative version, structured on the pattern "
           "discussed with the finance team and consistent with the income-statement figures used "
           "in Chapter 6, is presented below.")
    d.table(["Particulars", "Career counselling (" + R + ")", "Training programmes (" + R + ")",
             "Internship facilitation (" + R + ")", "Total (" + R + ")"],
            [["Revenue"] + [rs_plain(v) for v in V_REVENUE] + [rs_plain(sum(V_REVENUE))],
             ["Direct / variable costs"] + [rs_plain(v) for v in V_VARIABLE] + [rs_plain(sum(V_VARIABLE))],
             ["Apportioned fixed costs"] + [rs_plain(v) for v in V_FIXED] + [rs_plain(sum(V_FIXED))],
             ["Contribution to overheads & profit"] + [rs_plain(v) for v in V_CONTRIB]
             + [rs_plain(sum(V_CONTRIB))]],
            [1.6, 1.05, 1.05, 1.15, 1.0], size=8.5,
            caption="Illustrative annual operating budget, vertical-wise",
            aligns=["left", "right", "right", "right", "right"],
            header_align=["left", "right", "right", "right", "right"], bold_rows=[3])

    def annual_fig(dd, x, y, w, h):
        ch.bar_stacked(dd, x, y, w, h, VERTICALS,
                       [("Direct / variable cost", V_VARIABLE, ORANGE),
                        ("Apportioned fixed cost", V_FIXED, BLUE_L),
                        ("Contribution to overheads & profit", V_CONTRIB, GREEN)],
                       fmt=lambda v: lakh(v, 1), tick_fmt=lambda v: "%.0fL" % (v / 100000.0),
                       ticks=5, ylabel="" + R + " lakh", bar_frac=0.42)

    d.figure(200, annual_fig, "Annual budget by vertical: the height of each bar is the vertical's "
                              "revenue, split into cost and contribution.")
    d.para("This annual budget serves as the master planning document against which monthly and "
           "quarterly performance is tracked, and it forms the starting point for the batch-wise and "
           "departmental budgets discussed earlier in this chapter. It was observed that the annual "
           "budget is typically revised once at the mid-year point in the light of actual "
           "performance during the first two quarters, reflecting a sensible balance between the "
           "stability needed for planning and the flexibility needed to respond to actual market "
           "conditions.")

    d.section("5.9  Zero-Based Thinking in Discretionary Expenses", key="5.9")
    d.para("Although the organisation does not formally practise Zero-Based Budgeting in the strict "
           "technical sense of justifying every line item from a zero base each period, a similar "
           "discipline was observed in respect of discretionary expenditure such as marketing "
           "campaigns and event sponsorships, where each proposed expenditure was required to be "
           "justified afresh in terms of its expected return rather than being renewed "
           "automatically from the previous period's allocation. The channel analysis reproduced "
           "below is the working that supports this discipline.")
    d.table(["Marketing channel", "Spend (" + R + " lakh)", "Cost per enquiry (" + R + ")",
             "Enquiry-to-enrolment conversion", "Cost per enrolment (" + R + ")"],
            [[n, "%.2f" % s, rs_plain(cpe), pct(cv), rs_plain(cpr)]
             for (n, s, cpe, cv, cpr, col) in CHANNELS],
            [1.9, 0.9, 1.05, 1.2, 1.1], size=8.4,
            caption="Indicative effectiveness of marketing channels",
            aligns=["left", "right", "right", "center", "right"],
            header_align=["left", "right", "right", "center", "right"],
            note="Cost per enrolment is derived as cost per enquiry divided by the conversion rate; "
                 "figures are indicative and were used for relative comparison, not for external "
                 "reporting.")

    def channels_fig(dd, x, y, w, h):
        ch.bar_h(dd, x, y, w, h, [c[0] for c in CHANNELS], [c[4] for c in CHANNELS],
                 colors=[c[5] for c in CHANNELS], fmt=lambda v: rs(v), xmax=2500,
                 label_w=152, size=7.4)

    d.figure(158, channels_fig, "Indicative cost per enrolment by marketing channel; referral and "
                                "institutional outreach are an order of magnitude cheaper than "
                                "print advertising.")
    d.para("Referral and school outreach acquire an enrolment at a small fraction of the cost of "
           "print advertising, which is why the organisation has progressively shifted spend towards "
           "the former. This pragmatic, hybrid approach " + EM + " incremental budgeting for fixed "
           "and recurring costs combined with zero-based justification for discretionary "
           "costs " + EM + " appeared well suited to the size and stage of growth of the "
           "organisation.")



# ==========================================================================
# CHAPTER 6
# ==========================================================================
BS_LIAB = [("Share capital", 1000000, BLUE, 1),
           ("Reserves & surplus", 2525000, BLUE_M, 1),
           ("Long-term borrowings", 845000, ORANGE, 0),
           ("Trade payables", 400000, GOLD, 0),
           ("Other current liabilities & provisions", 300000, GREY_M, 0)]
BS_ASSET = [("Fixed assets (net block)", 3526000, TEAL, 0),
            ("Non-current investments", 200000, PURPLE, 0),
            ("Inventories (study material & consumables)", 147000, GREY_M, 0),
            ("Trade receivables", 500000, GOLD, 0),
            ("Cash & bank balances", 597000, GREEN, 0),
            ("Other current assets (prepaid expenses)", 100000, BLUE_L, 0)]


def chapter6(d):
    d.reset_counters()
    d.chapter("6", "Ratio and Financial Analysis", key="ch6",
              kicker="This chapter converts the illustrative financial statements of the "
                     "organisation into ratios, and then interprets them: liquidity, "
                     "profitability, efficiency and solvency, followed by common-size and trend "
                     "analysis, a DuPont decomposition of the return on equity, a comparison with "
                     "indicative sector benchmarks and a consolidated summary.")

    d.section("6.1  Purpose of Ratio Analysis", key="6.1")
    d.para("Ratio analysis is one of the most widely used tools of financial statement analysis, "
           "converting raw accounting figures into meaningful relationships that facilitate "
           "comparison across time periods, against industry benchmarks, or against the "
           "organisation's own targets. For the purpose of this report, an illustrative set of "
           "financial statements, consistent in structure and proportion with the figures observed "
           "during the internship but adjusted in absolute value to preserve the confidentiality of "
           "the organisation's actual accounts, has been used to demonstrate the application of "
           "ratio analysis to a service-sector small enterprise.")
    d.callout("An important qualification",
              "The figures presented in this chapter are illustrative and prepared for academic "
              "purposes. They reflect the proportions and relationships genuinely observed during "
              "the internship rather than the exact audited figures of Infinitya1 Career "
              "Counselling Private Limited, which remain confidential in accordance with the "
              "organisation's policy. Every ratio below is therefore an exercise in method, not a "
              "certified statement of the company's position.", color=ORANGE, bg=ORANGE_XL)

    d.section("6.2  Illustrative Statement of Profit and Loss", key="6.2")
    d.para("The illustrative income statement for the financial year under review, structured on the "
           "pattern observed during the internship, is presented below, with each item also "
           "expressed as a percentage of revenue so that the common-size analysis of Section 6.8 "
           "follows directly from it.")
    d.table(["Particulars", "Amount (" + R + ")", "% of revenue"],
            [[n, rs_plain(a), pct(p)] for (n, a, p) in PL],
            [3.0, 1.0, 0.85], size=8.5,
            caption="Illustrative statement of profit and loss for the year",
            aligns=["left", "right", "right"], header_align=["left", "right", "right"],
            bold_rows=[0, 7, 9, 11])

    def pl_waterfall(dd, x, y, w, h):
        ch.waterfall(dd, x, y, w, h,
                     [("Revenue", 4800000, "start"),
                      ("Employee cost", -1950000, "neg"),
                      ("Material & programme", -550000, "neg"),
                      ("Marketing", -480000, "neg"),
                      ("Rent & utilities", -420000, "neg"),
                      ("Administration", -250000, "neg"),
                      ("Depreciation", -74800, "neg"),
                      ("Finance cost", -37200, "neg"),
                      ("Taxation", -150000, "neg"),
                      ("Profit after tax", 888000, "total")],
                     fmt=lambda v: "%.1fL" % (v / 100000.0), ylabel="" + R + " lakh")

    d.figure(212, pl_waterfall, "Walk from revenue to profit after tax; employee cost alone absorbs "
                                "two-fifths of revenue.")

    d.section("6.3  Illustrative Balance Sheet", key="6.3")
    d.para("The illustrative balance sheet as at the end of the financial year under review is "
           "presented below, followed by a graphical view of the same information which makes the "
           "asset-light nature of the current assets and the equity-dominated funding structure "
           "immediately visible.")
    d.table(["Particulars", "Amount (" + R + ")"],
            [["I.  EQUITY AND LIABILITIES", ""],
             ["1.  Shareholders' funds", ""],
             ["      (a)  Share capital", "10,00,000"],
             ["      (b)  Reserves and surplus", "25,25,000"],
             ["      Total shareholders' funds", "35,25,000"],
             ["2.  Non-current liabilities", ""],
             ["      Long-term borrowings", "8,45,000"],
             ["3.  Current liabilities", ""],
             ["      (a)  Trade payables", "4,00,000"],
             ["      (b)  Other current liabilities and provisions", "3,00,000"],
             ["      Total current liabilities", "7,00,000"],
             ["TOTAL EQUITY AND LIABILITIES", "50,70,000"],
             ["II.  ASSETS", ""],
             ["1.  Non-current assets", ""],
             ["      (a)  Fixed assets (net block)", "35,26,000"],
             ["      (b)  Non-current investments", "2,00,000"],
             ["      Total non-current assets", "37,26,000"],
             ["2.  Current assets", ""],
             ["      (a)  Inventories (study material and consumables)", "1,47,000"],
             ["      (b)  Trade receivables", "5,00,000"],
             ["      (c)  Cash and bank balances", "5,97,000"],
             ["      (d)  Other current assets (prepaid expenses)", "1,00,000"],
             ["      Total current assets", "13,44,000"],
             ["TOTAL ASSETS", "50,70,000"]],
            [3.2, 1.0], size=8.4, caption="Illustrative balance sheet as at the year-end",
            aligns=["left", "right"], header_align=["left", "right"],
            bold_rows=[0, 4, 10, 11, 12, 16, 22, 23], zebra=None, line_h=11.0, pad=4.4)

    def bs_fig(dd, x, y, w, h):
        ch.composition_bars(dd, x, y, w, h,
                            [("Equity and liabilities", [(n, v, c) for (n, v, c, _) in BS_LIAB]),
                             ("Assets", [(n, v, c) for (n, v, c, _) in BS_ASSET])],
                            fmt=lambda v: rs(v), legends=True, bar_h=28, gap=46)

    d.figure(196, bs_fig, "Composition of the balance sheet: shareholders' funds finance 70 per "
                          "cent of the total, and fixed assets absorb 70 per cent of it.")

    d.section("6.4  Liquidity Ratios", key="6.4")
    d.para("Liquidity ratios measure the organisation's ability to meet its short-term obligations "
           "as they fall due, and are of particular relevance for a service organisation dependent "
           "on the timely collection of student and corporate fees.")
    d.table(["Ratio", "Formula", "Computation", "Result", "Indicative norm"],
            [["Current ratio", "Current assets / current liabilities",
              "13,44,000 / 7,00,000", "1.92 : 1", "1.3 to 2.0 : 1"],
             ["Quick (acid-test) ratio", "(Current assets " + EN + " inventory) / current liabilities",
              "11,97,000 / 7,00,000", "1.71 : 1", "1.0 : 1 and above"],
             ["Cash ratio", "Cash and bank / current liabilities",
              "5,97,000 / 7,00,000", "0.85 : 1", "0.5 : 1 and above"],
             ["Net working capital", "Current assets " + EN + " current liabilities",
              "13,44,000 " + EN + " 7,00,000", rs(644000), "Positive"]],
            [1.1, 1.6, 1.1, 0.75, 0.95], size=8.3, caption="Liquidity ratios",
            aligns=["left", "left", "right", "center", "center"],
            header_align=["left", "left", "right", "center", "center"])

    def liquidity_fig(dd, x, y, w, h):
        ch.gauge_row(dd, x, y, w, h,
                     [("Current ratio\n(norm 2.0)", 1.92, 3.0, "1.92", BLUE, 2.0),
                      ("Quick ratio\n(norm 1.0)", 1.71, 3.0, "1.71", TEAL, 1.0),
                      ("Cash ratio\n(norm 0.5)", 0.85, 3.0, "0.85", GREEN, 0.5)])

    d.figure(150, liquidity_fig, "Liquidity ratios against their indicative norms; the marker on "
                                 "each dial shows the conventional benchmark.")
    d.para("The current ratio of 1.92:1 indicates that the organisation holds nearly twice the "
           "current assets required to cover its current liabilities, a comfortable position for a "
           "service enterprise of this scale and only marginally below the conventionally cited norm "
           "of 2:1. The quick ratio, which excludes the relatively illiquid inventory of study "
           "material, remains healthy at 1.71:1 and reinforces the conclusion that the organisation "
           "is well placed to meet its immediate obligations, including staff salaries and vendor "
           "payments, without resorting to emergency borrowing. The cash ratio of 0.85:1 shows that "
           "cash alone covers 85 per cent of current liabilities, which is a strong position and "
           "suggests that a modest portion of the cash balance could be redeployed into productive "
           "investment without endangering short-term solvency.")

    d.section("6.5  Profitability Ratios", key="6.5")
    d.para("Profitability ratios assess the organisation's ability to generate surplus in relation "
           "to its revenue, its assets and the capital employed in the business.")
    d.table(["Ratio", "Formula", "Computation", "Result"],
            [["Operating profit margin", "EBIT / revenue x 100", "10,75,200 / 48,00,000 x 100", "22.4%"],
             ["Net profit margin", "Net profit / revenue x 100", "8,88,000 / 48,00,000 x 100", "18.5%"],
             ["Return on equity (ROE)", "Net profit / shareholders' funds x 100",
              "8,88,000 / 35,25,000 x 100", "25.2%"],
             ["Return on capital employed (ROCE)", "EBIT / capital employed x 100",
              "10,75,200 / 43,70,000 x 100", "24.6%"],
             ["Return on total assets (ROA)", "Net profit / total assets x 100",
              "8,88,000 / 50,70,000 x 100", "17.5%"]],
            [1.55, 1.6, 1.4, 0.7], size=8.4, caption="Profitability ratios",
            aligns=["left", "left", "right", "center"],
            header_align=["left", "left", "right", "center"])

    def profit_fig(dd, x, y, w, h):
        half = (w - 24) / 2.0
        ch.bar_v(dd, x, y, half, h, ["Operating\nmargin", "Net\nmargin", "ROE", "ROCE", "ROA"],
                 [22.4, 18.5, 25.2, 24.6, 17.5], colors=[BLUE, BLUE_M, TEAL, GREEN, PURPLE],
                 fmt=lambda v: pct(v), ymax=30, ticks=6, ylabel="Per cent", label_size=6.9)
        ch.radar(dd, x + half + 24, y, half, h,
                 ["Net margin", "ROCE", "Liquidity", "Asset use", "Interest cover", "Collection"],
                 [("Infinity Interns", [92, 88, 96, 63, 97, 76], BLUE),
                  ("Indicative sector norm", [70, 65, 75, 78, 60, 70], ORANGE)])

    d.figure(200, profit_fig, "Profitability ratios (left) and a normalised comparison of the "
                              "organisation's financial profile against indicative sector norms "
                              "(right), where each axis is scored out of 100.")
    d.para("A net profit margin of approximately 18.5 per cent reflects a healthy surplus for a "
           "service-sector enterprise of this nature, indicating that the organisation retains a "
           "reasonable portion of every rupee of fee income after meeting all operating and "
           "non-operating expenses. The operating profit margin of 22.4 per cent, being higher than "
           "the net margin, reflects the effect of finance cost and taxation, and is consistent with "
           "an organisation that relies minimally on external borrowing and therefore bears only a "
           "modest finance cost. The return on capital employed of 24.6 per cent suggests that the "
           "promoters' invested capital is being deployed efficiently to generate returns well above "
           "what could typically be earned through passive investment avenues, which is a favourable "
           "sign for the sustainability and attractiveness of the business. The radar chart also "
           "makes the one weak axis visible: asset utilisation, which is examined next.")

    d.section("6.6  Efficiency / Activity Ratios", key="6.6")
    d.para("Efficiency ratios measure how effectively the organisation utilises its resources and "
           "manages its receivables.")
    d.table(["Ratio", "Formula", "Computation", "Result"],
            [["Debtors' turnover ratio", "Revenue / trade receivables", "48,00,000 / 5,00,000",
              "9.6 times"],
             ["Average collection period", "365 / debtors' turnover ratio", "365 / 9.6",
              "About 38 days"],
             ["Fixed asset turnover ratio", "Revenue / net fixed assets", "48,00,000 / 35,26,000",
              "1.36 times"],
             ["Total asset turnover ratio", "Revenue / total assets", "48,00,000 / 50,70,000",
              "0.95 times"],
             ["Working capital turnover", "Revenue / net working capital", "48,00,000 / 6,44,000",
              "7.45 times"]],
            [1.55, 1.5, 1.35, 0.8], size=8.4, caption="Efficiency and activity ratios",
            aligns=["left", "left", "right", "center"],
            header_align=["left", "left", "right", "center"])

    def efficiency_fig(dd, x, y, w, h):
        ch.progress_bars(dd, x, y, w, h,
                         [("Debtors' turnover (times a year)", 9.6, 12, "9.6x", BLUE, 9.0),
                          ("Average collection period (days)", 38, 90, "38 days", TEAL, 45),
                          ("Fixed asset turnover (times)", 1.36, 3.0, "1.36x", PURPLE, 1.5),
                          ("Total asset turnover (times)", 0.95, 3.0, "0.95x", ORANGE, 1.2),
                          ("Working capital turnover (times)", 7.45, 12, "7.45x", GREEN, 6.0)])
        dd.text(x, y + 2, "The vertical marker on each bar is the internal target or indicative "
                          "benchmark.", "italic", 6.8, GREY_M)

    d.figure(168, efficiency_fig, "Efficiency ratios against internal targets: collection is "
                                  "comfortably inside target, while asset turnover falls short.")
    d.para("The debtors' turnover ratio of 9.6 times a year, translating to an average collection "
           "period of about thirty-eight days, is a reasonable figure for a service organisation "
           "that follows a policy of substantial advance collection at the time of enrolment, with "
           "only a limited portion of fees collected on a deferred basis, primarily in the "
           "internship-facilitation vertical where payment is sometimes contingent on placement "
           "outcomes. Continued monitoring of this ratio is advisable as that vertical grows, since "
           "a lengthening collection period there could exert pressure on overall liquidity.")
    d.para("Total asset turnover of 0.95 times means the organisation generates ninety-five paise of "
           "revenue for every rupee invested in assets. Read together with the facility utilisation "
           "figures in Section 2.11, this is the clearest quantitative evidence that the existing "
           "premises and equipment could support a materially larger volume of batches and "
           "counselling sessions without proportionate additional investment " + EM + " which is "
           "why improving utilisation, rather than raising fees, is identified in Chapter 9 as the "
           "most promising route to a higher return on equity.")

    d.section("6.7  Solvency / Leverage Ratios", key="6.7")
    d.para("Solvency ratios assess the extent to which the organisation relies on external borrowing "
           "as opposed to owners' funds, and the consequent long-term financial risk.")
    d.table(["Ratio", "Formula", "Computation", "Result"],
            [["Debt-equity ratio", "Long-term debt / shareholders' funds", "8,45,000 / 35,25,000",
              "0.24 : 1"],
             ["Total debt ratio", "Total debt / total assets", "8,45,000 / 50,70,000", "16.7%"],
             ["Proprietary ratio", "Shareholders' funds / total assets", "35,25,000 / 50,70,000",
              "69.5%"],
             ["Interest coverage ratio", "EBIT / finance cost", "10,75,200 / 37,200", "28.9 times"]],
            [1.5, 1.55, 1.35, 0.8], size=8.4, caption="Solvency and leverage ratios",
            aligns=["left", "left", "right", "center"],
            header_align=["left", "left", "right", "center"])

    def solvency_fig(dd, x, y, w, h):
        half = (w - 24) / 2.0
        ch.donut(dd, x, y, half, h, [3525000, 845000, 700000],
                 ["Owners' funds", "Borrowings", "Current dues"],
                 colors=[NAVY, ORANGE, GREY_M], center_value="69.5%",
                 center_title="owners' funds", size=7.2)
        ch.bar_v(dd, x + half + 24, y, half, h,
                 ["Interest\ncover", "Sector\ncomfort level"], [28.9, 4.0],
                 colors=[GREEN, GREY_M], fmt=lambda v: "%.1fx" % v, ymax=30, ticks=6,
                 ylabel="Times", bar_frac=0.42)

    d.figure(186, solvency_fig, "Capital structure of the organisation (left) and its interest "
                                "coverage against a commonly cited comfort level of four times "
                                "(right).")
    d.para("A debt-equity ratio of 0.24:1 indicates that the organisation relies predominantly on "
           "owners' funds rather than external borrowing to finance its operations and modest "
           "capital expenditure, a conservative capital structure that minimises financial risk and "
           "fixed interest obligations. Interest is covered almost twenty-nine times over by "
           "operating profit, so the debt burden is trivial in servicing terms. The same "
           "conservatism, however, implies that the organisation is not using the potential benefits "
           "of financial leverage, such as a lower overall cost of capital, that could be available "
           "were it to increase its use of debt responsibly to fund future expansion such as the "
           "establishment of a second training centre.")

    d.section("6.8  Common-Size and Trend Analysis", key="6.8")
    d.para("A common-size analysis, which expresses each item of the income statement as a "
           "percentage of total revenue, was carried out to understand the relative weight of the "
           "different cost heads. Employee-related costs, comprising trainer honorariums, "
           "counsellor salaries and administrative staff salaries, together constitute the single "
           "largest cost category, consistent with the labour-intensive nature of a career "
           "counselling and training business, followed by material, marketing and rent.")

    def common_size(dd, x, y, w, h):
        ch.composition_bars(dd, x, y, w, h,
                            [("Every " + R + " 100 of revenue is absorbed as follows",
                              [("Employee cost", 40.6, BLUE), ("Material", 11.5, ORANGE),
                               ("Marketing", 10.0, TEAL), ("Rent", 8.7, PURPLE),
                               ("Admin", 5.2, GOLD), ("Dep.", 1.6, GREEN),
                               ("Fin.", 0.8, RED), ("Tax", 3.1, GREY_M),
                               ("Profit after tax", 18.5, NAVY)])],
                            fmt=lambda v: "%.0f%%" % v, legends=True, bar_h=34)

    d.figure(128, common_size, "Common-size view of the income statement: the disposition of every "
                               "hundred rupees of fee income.")
    d.para("A limited trend analysis, based on discussion with the finance executive regarding the "
           "growth in enrolment and revenue over the preceding two years, indicated consistent "
           "year-on-year growth in both the counselling and training verticals, with the "
           "internship-facilitation vertical showing more volatile but generally increasing revenue, "
           "reflecting its relative novelty and its dependence on the strength of corporate "
           "partnerships, which the organisation has been actively working to expand.")
    d.table(["Particulars", TREND_YEARS[0], TREND_YEARS[1], TREND_YEARS[2]],
            [["Revenue (" + R + ")"] + [rs_plain(v) for v in TREND_REVENUE],
             ["Revenue index (base = 100)"] + ["%.0f" % (v * 100.0 / TREND_REVENUE[0])
                                               for v in TREND_REVENUE],
             ["Year-on-year growth", EN, pct((TREND_REVENUE[1] / float(TREND_REVENUE[0]) - 1) * 100),
              pct((TREND_REVENUE[2] / float(TREND_REVENUE[1]) - 1) * 100)],
             ["Net profit margin"] + [pct(m) for m in TREND_MARGIN],
             ["Net profit (" + R + ")"] + [rs_plain(TREND_REVENUE[i] * TREND_MARGIN[i] / 100.0)
                                           for i in range(3)]],
            [1.6, 1.0, 1.0, 1.2], size=8.4,
            caption="Three-year trend in revenue and profitability (indicative)",
            aligns=["left", "right", "right", "right"],
            header_align=["left", "right", "right", "right"], bold_rows=[0, 4])

    def trend_fig(dd, x, y, w, h):
        ch.combo_bar_line(dd, x, y, w, h, ["Two years ago", "Last year", "Year under review"],
                          TREND_REVENUE, TREND_MARGIN, bar_name="Revenue (" + R + ")",
                          line_name="Net profit margin (%)",
                          fmt_bar=lambda v: "%.1fL" % (v / 100000.0),
                          fmt_line=lambda v: pct(v), y2max=25)

    d.figure(196, trend_fig, "Revenue has grown by about 54 per cent over two years while the net "
                             "margin has improved by four percentage points, indicating operating "
                             "leverage rather than mere volume growth.")
    d.para("The simultaneous improvement in revenue and in margin is analytically significant: it "
           "indicates that the additional revenue is being earned without a proportionate increase "
           "in the fixed cost base, which is exactly the behaviour predicted by the cost structure "
           "described in Section 4.5, where nearly three-quarters of costs are fixed. If the trend "
           "continues, each additional batch should contribute progressively more to the surplus.")

    d.section("6.9  DuPont Analysis of Return on Equity", key="6.9")
    d.para("The DuPont framework decomposes return on equity into three constituent components " +
           EM + " net profit margin, asset turnover and financial leverage " + EM + " thereby "
           "providing deeper insight into the specific drivers of the organisation's return to its "
           "shareholders, rather than treating the return as a single, undifferentiated figure.")

    def dupont(dd, x, y, w, h):
        dg.driver_tree(dd, x, y, w, h, ("Return on equity", "25.2%"),
                       [("Net profit margin", "18.5%", BLUE),
                        ("Total asset turnover", "0.95x", TEAL),
                        ("Equity multiplier", "1.44x", ORANGE)],
                       [[("Profit after tax", "8.88L"), ("Revenue", "48.0L")],
                        [("Revenue", "48.0L"), ("Total assets", "50.7L")],
                        [("Total assets", "50.7L"), ("Equity", "35.25L")]])

    d.figure(182, dupont, "DuPont decomposition of the return on equity into margin, asset turnover "
                          "and leverage.")
    d.para("Using the illustrative figures developed in this chapter, the return on equity may be "
           "expressed as a net profit margin of 18.5 per cent multiplied by a total asset turnover "
           "of 0.95 times multiplied by an equity multiplier of 1.44 times, which yields "
           "approximately 25.2 per cent and reconciles closely with the return on equity "
           "independently computed in Section 6.5.")
    d.para("This decomposition reveals that the organisation's healthy return on equity is driven "
           "primarily by a strong net profit margin rather than by aggressive use of financial "
           "leverage or rapid asset turnover, both of which remain moderate. It follows that any "
           "future improvement in return on equity is more likely to come from improving asset "
           "utilisation, for instance by running more batches and counselling sessions from the same "
           "physical infrastructure, than from a significant increase in financial leverage, which "
           "would raise the organisation's risk profile. The table below quantifies that "
           "proposition.")
    d.table(["Scenario", "Net margin", "Asset turnover", "Equity multiplier", "Resulting ROE"],
            [["Position in the year under review", "18.5%", "0.95x", "1.44x", "25.2%"],
             ["Utilisation improved to 1.15 times asset turnover", "18.5%", "1.15x", "1.44x", "30.6%"],
             ["Margin improved by one percentage point", "19.5%", "0.95x", "1.44x", "26.6%"],
             ["Leverage raised to an equity multiplier of 1.70", "18.5%", "0.95x", "1.70x", "29.8%"]],
            [1.9, 0.85, 1.0, 1.05, 0.95], size=8.4,
            caption="What would move the return on equity: an illustrative DuPont sensitivity",
            aligns=["left", "center", "center", "center", "center"],
            header_align=["left", "center", "center", "center", "center"],
            row_colors={1: GREEN_L}, note="Improving utilisation delivers a larger gain than "
                                          "additional borrowing, and without the accompanying risk.")

    d.section("6.10  Comparison with Indicative Industry Benchmarks", key="6.10")
    d.para("While detailed, published industry-wide financial benchmarks specific to small career "
           "counselling and training enterprises in India are not widely available in the public "
           "domain, a broad comparison with general benchmarks applicable to the education and "
           "professional-services sector suggests that the liquidity and profitability position of "
           "the organisation compares favourably. Providers of a similar scale typically report net "
           "profit margins in the range of twelve to twenty per cent, current ratios between 1.3:1 "
           "and 2:1, and debt-equity ratios below 0.5:1, given the asset-light, people-driven nature "
           "of the business.")

    def benchmark_fig(dd, x, y, w, h):
        ch.scorecard(dd, x, y, w, h,
                     [("Current ratio", [("1.92 : 1", None), ("1.3 " + EN + " 2.0", None),
                                         ("Healthy", GREEN)]),
                      ("Quick ratio", [("1.71 : 1", None), ("1.0 and above", None),
                                       ("Healthy", GREEN)]),
                      ("Net profit margin", [("18.5%", None), ("12 " + EN + " 20%", None),
                                             ("Upper end", GREEN)]),
                      ("Return on capital employed", [("24.6%", None), ("15 " + EN + " 25%", None),
                                                      ("Strong", TEAL)]),
                      ("Debt-equity ratio", [("0.24 : 1", None), ("Below 0.50", None),
                                             ("Conservative", TEAL)]),
                      ("Interest coverage", [("28.9 times", None), ("Above 4 times", None),
                                             ("Very safe", GREEN)]),
                      ("Average collection period", [("38 days", None), ("30 " + EN + " 60 days", None),
                                                     ("Satisfactory", GREEN)]),
                      ("Total asset turnover", [("0.95 times", None), ("1.0 " + EN + " 1.5 times", None),
                                                ("Below range", GOLD)])],
                     ["Organisation", "Indicative sector range", "Assessment"])

    d.figure(190, benchmark_fig, "Ratio-by-ratio comparison against indicative sector ranges; only "
                                 "asset turnover falls short of the range.")
    d.para("The organisation's illustrative figures fall comfortably within, or towards the healthier "
           "end of, these indicative ranges, suggesting a financially well-managed enterprise "
           "relative to its peer group, notwithstanding the acknowledged limitations of comparing a "
           "single small enterprise against broad sectoral averages. The one indicator outside the "
           "range, total asset turnover, is consistent with the under-utilised training capacity "
           "identified independently in Chapter 2.")

    d.section("6.11  Summary of Key Financial Ratios", key="6.11")
    d.para("The table below consolidates the key ratios computed and discussed in the preceding "
           "sections for ease of reference during evaluation and viva-voce.")
    d.table(["Category", "Ratio", "Result", "Inference"],
            [["Liquidity", "Current ratio", "1.92 : 1", "Comfortable"],
             ["Liquidity", "Quick ratio", "1.71 : 1", "Comfortable"],
             ["Liquidity", "Cash ratio", "0.85 : 1", "Strong cash cover"],
             ["Profitability", "Operating profit margin", "22.4%", "Healthy"],
             ["Profitability", "Net profit margin", "18.5%", "Healthy"],
             ["Profitability", "Return on equity", "25.2%", "Strong"],
             ["Profitability", "Return on capital employed", "24.6%", "Strong"],
             ["Profitability", "Return on total assets", "17.5%", "Satisfactory"],
             ["Efficiency", "Debtors' turnover", "9.6 times", "Satisfactory"],
             ["Efficiency", "Average collection period", "38 days", "Within norms"],
             ["Efficiency", "Fixed asset turnover", "1.36 times", "Scope to improve"],
             ["Efficiency", "Total asset turnover", "0.95 times", "Below sector range"],
             ["Solvency", "Debt-equity ratio", "0.24 : 1", "Conservative, low risk"],
             ["Solvency", "Total debt ratio", "16.7%", "Low"],
             ["Solvency", "Proprietary ratio", "69.5%", "Owner-funded"],
             ["Solvency", "Interest coverage ratio", "28.9 times", "Very safe"]],
            [0.9, 1.9, 0.9, 1.4], size=8.3, caption="Summary of key financial ratios",
            aligns=["left", "left", "center", "left"],
            header_align=["left", "left", "center", "left"],
            col_colors={0: BLUE})



# ==========================================================================
# CHAPTER 7
# ==========================================================================
def chapter7(d):
    d.reset_counters()
    d.chapter("7", "Learning Outcomes", key="ch7",
              kicker="This chapter reflects on what the internship produced in terms of learning: "
                     "technical competence in financial management, a self-assessment of the "
                     "change in that competence, managerial and interpersonal skills, the link "
                     "established between classroom concepts and workplace practice, and an "
                     "honest assessment of whether the stated objectives were met.")

    d.section("7.1  Technical / Domain Learning", key="7.1")
    d.para("The internship provided substantial technical learning that directly reinforced and "
           "extended the concepts studied in the Financial Management specialisation of the MBA "
           "programme.")
    d.bullets([
        "Revenue recognition in practice: a clear, practical understanding of how revenue is "
        "recorded in a fee-based service organisation, including the handling of advance receipts "
        "and instalment-based collections, and the distinction between a cash receipt and revenue "
        "earned.",
        "Internal control through documentation: hands-on experience in preparing vouchers, "
        "maintaining petty cash records and reconciling bank statements, which brought to life the "
        "theoretical concept of internal control.",
        "Cost classification and batch costing: the ability to construct a batch-wise budget from "
        "first principles, distinguishing fixed from variable costs and apportioning shared "
        "overheads to a specific programme.",
        "Cost-volume-profit analysis: applying break-even and sensitivity analysis to a live "
        "decision on whether a batch should run, be consolidated or be postponed.",
        "Variance analysis as control: practical exposure to variance analysis as a tool of "
        "managerial control, and an appreciation of how management uses it to understand causes "
        "rather than merely to identify deviations.",
        "Spreadsheet modelling: improved proficiency in spreadsheet-based financial work, including "
        "formulas, lookups and simple summary dashboards that convert transaction data into "
        "decision-useful information.",
        "Ratio analysis in a small-enterprise context: a grounded understanding of how ratio "
        "analysis, usually taught with reference to large listed companies, applies just as "
        "meaningfully, with appropriate adaptation, to a small service enterprise.",
        "Statutory awareness: familiarity with the practical checks required on a GST invoice and "
        "with the points at which tax deducted at source arises in routine payments."])

    d.section("7.2  Competency Self-Assessment", key="7.2")
    d.para("To assess the learning gained in a structured manner, a self-assessment was carried out "
           "on a ten-point scale at the beginning and again at the close of the internship across "
           "eight competency areas relevant to the Financial Management specialisation. The "
           "assessment is necessarily subjective, but the pattern is instructive: the largest gains "
           "occurred in areas where the classroom had provided theory but no practice.")

    def competency_fig(dd, x, y, w, h):
        ch.dumbbell(dd, x, y, w, h, [c[0] for c in COMPETENCY],
                    [c[1] for c in COMPETENCY], [c[2] for c in COMPETENCY],
                    fmt=lambda v: "%.0f/10" % v, maxv=10,
                    legend_labels=("Start of internship", "Close of internship"))

    d.figure(206, competency_fig, "Self-assessed competency at the start and at the close of the "
                                  "internship across eight areas, on a ten-point scale.")
    d.table(["Competency area", "Start", "Close", "Gain", "What produced the gain"],
            [[c[0], str(c[1]), str(c[2]), "+%d" % (c[2] - c[1]), g] for c, g in zip(COMPETENCY, [
                "Building the batch budget and the ratio worksheet in spreadsheets",
                "Preparing 96 vouchers and 148 receipts under mentor review",
                "Assisting three batch budgets including the break-even working",
                "Computing and interpreting sixteen ratios for the mini-project",
                "Compiling two monthly MIS packs with reasons for each variance",
                "Corresponding with vendors and explaining fee matters to parents",
                "Balancing routine daily work against special assignments",
                "Verifying GST details on 34 vendor invoices"])],
            [1.8, 0.5, 0.5, 0.5, 2.0], size=8.3,
            caption="Competency self-assessment with the activity that produced the improvement",
            aligns=["left", "center", "center", "center", "left"],
            header_align=["left", "center", "center", "center", "left"])
    d.para("The two areas where the closing self-assessment remains below eight " + EM +
           " statutory and GST awareness, and pivot-table proficiency " + EM + " correspond to "
           "work that was handled substantially by the external chartered accountant or that arose "
           "only occasionally during a seven-week window. They are recorded here as areas "
           "identified for further study rather than as achievements.")

    d.section("7.3  Managerial and Soft-Skill Learning", key="7.3")
    d.para("Beyond the technical domain of financial management, the internship offered significant "
           "learning in the managerial and interpersonal dimensions of working life, which are "
           "harder to teach in a classroom and were acquired largely by observation and correction.")
    d.bullets([
        "Professional communication: learning to communicate fee-related matters with students and "
        "parents tactfully, and to correspond professionally with vendors regarding invoices and "
        "payments.",
        "Time management: balancing multiple concurrent tasks, such as daily data entry alongside a "
        "special budgeting assignment, within fixed office hours.",
        "Attention to detail: recognising that even a small error in a voucher or a fee receipt has "
        "downstream consequences for the accuracy of the financial records and for the monthly "
        "reconciliation.",
        "Teamwork and cross-functional coordination: working with the counselling, training and "
        "business development teams to obtain accurate operational data for financial reporting.",
        "Workplace etiquette and professionalism: adapting to organisational norms regarding "
        "punctuality, dress, meeting conduct and respectful communication with seniors and "
        "colleagues.",
        "Receiving and acting on feedback: learning to treat a correction, such as a misclassified "
        "expense head, as a learning opportunity rather than a setback."])

    d.section("7.4  Linking Classroom Concepts to Workplace Practice", key="7.4")
    d.para("One of the most valuable outcomes of the internship was the opportunity to observe, in a "
           "live setting, concepts that had previously been understood only in an abstract, textbook "
           "sense. The distinction between fixed and variable costs, the logic of the contribution "
           "margin, the mechanics of the current and quick ratios, and the principle that a budget "
           "is a tool for control rather than merely a forecasting exercise, all acquired a far "
           "richer and more durable meaning once observed in the context of real organisational "
           "decisions, such as whether to proceed with a training batch that had received fewer "
           "pre-enrolments than hoped.")

    def bridge_fig(dd, x, y, w, h):
        dg.bridge(dd, x, y, w, h, "CLASSROOM CONCEPT",
                  ["Fixed and variable cost behaviour", "Contribution margin and break-even",
                   "Ratio analysis of statements", "Budget as an instrument of control",
                   "Accrual concept of revenue"],
                  "WORKPLACE APPLICATION",
                  ["Batch cost sheet with apportioned overhead",
                   "Go or no-go decision on a proposed batch",
                   "Mini-project ratio worksheet reviewed by the mentor",
                   "Monthly variance review with the Director",
                   "Advance fee receipted but revenue spread over the batch"],
                  ["Week 1: observation", "Weeks 2 to 3: assisted execution",
                   "Weeks 4 to 6: independent tasks", "Week 7: analytical mini-project"],
                  caption="progressive exposure over the seven weeks of the internship")

    d.figure(228, bridge_fig, "How each classroom concept found a specific workplace application "
                              "during the internship.")
    d.para("This experience reinforced the understanding that financial management, at its core, is "
           "not a purely quantitative discipline but one that requires the exercise of judgement, "
           "informed both by the numbers and by a contextual understanding of the business, its "
           "customers and its competitive environment. The decision to postpone a thin batch, for "
           "example, was supported by a break-even calculation but ultimately turned on a judgement "
           "about whether postponement would damage the organisation's credibility with the "
           "students who had already enrolled.")

    d.section("7.5  Achievement of the Stated Internship Objectives", key="7.5")
    d.para("The eight objectives set out in Section 1.3 are revisited below against the evidence "
           "generated during the internship. Seven were substantially achieved; one was achieved "
           "only in part, and this is recorded honestly rather than claimed.")
    d.table(["Objective set out in Section 1.3", "Evidence from the internship", "Extent achieved"],
            [["Exposure to the working of the finance and accounts function",
              "Seven weeks inside the department covering the full monthly cycle", "Achieved"],
             ["Understanding budgeting, cost estimation and cost control",
              "Assisted three batch budgets; observed six cost control practices", "Achieved"],
             ["Applying ratio analysis to assess financial position",
              "Sixteen ratios computed, interpreted and benchmarked in Chapter 6", "Achieved"],
             ["Observing how pricing and payment decisions are taken",
              "Documented the authority matrix and the decision path in Section 4.8", "Achieved"],
             ["Practical skills in vouchers, invoices and budget sheets",
              "96 vouchers, 148 receipts, 34 invoices and 3 budget sheets handled", "Achieved"],
             ["Relating theoretical concepts to live application",
              "Concept-to-application mapping set out in Figure 7.2", "Achieved"],
             ["Identifying improvement areas and suggesting remedies",
              "Eight findings and eight prioritised suggestions in Chapter 9", "Achieved"],
             ["Developing professional and interpersonal skills",
              "Vendor correspondence and parent interaction, though limited exposure to "
              "formal presentation and negotiation", "Partly achieved"]],
            [1.85, 2.1, 0.85], size=8.3,
            caption="Objectives of the internship assessed against evidence",
            aligns=["left", "left", "center"], header_align=["left", "left", "center"],
            row_colors={7: ORANGE_XL})

    d.section("7.6  Personal Growth and Career Clarity", key="7.6")
    d.para("On a personal level, the internship contributed meaningfully to greater clarity regarding "
           "career interests within the broad field of financial management. Exposure to the "
           "day-to-day realities of budgeting, cost control and financial reporting in a small "
           "enterprise setting helped in appreciating both the challenges and the satisfaction "
           "associated with building financial discipline in a growing organisation, and has "
           "strengthened an interest in pursuing further specialisation and career opportunities in "
           "the areas of financial planning and analysis and corporate finance.")
    d.callout("A specific realisation",
              "Working in a small organisation made visible something a large-company internship "
              "might have hidden: that the quality of financial information available to a decision "
              "maker depends almost entirely on the discipline of the person entering the "
              "transactions. The apparently routine work of receipting and voucher preparation is "
              "the foundation on which every ratio in Chapter 6 ultimately rests.",
              color=TEAL, bg=GREEN_L)


# ==========================================================================
# CHAPTER 8
# ==========================================================================
def chapter8(d):
    d.reset_counters()
    d.chapter("8", "Challenges Faced", key="ch8",
              kicker="This chapter records the difficulties encountered, both those personal to an "
                     "intern entering an unfamiliar environment and those structural to the "
                     "organisation itself, together with a root-cause analysis of the single "
                     "recurring operational problem observed and an account of how the personal "
                     "challenges were overcome.")

    d.section("8.1  Challenges Related to the Internship Environment", key="8.1")
    d.para("Like any real-world learning experience, the internship was accompanied by a set of "
           "genuine challenges, engagement with which itself constituted an important part of the "
           "learning process.")
    d.bullets([
        "Unfamiliar systems: initial unfamiliarity with the specific accounting software and "
        "internal formats used by the organisation, which required an adjustment period before "
        "tasks could be performed independently and confidently.",
        "Shifting priorities: the relatively informal and fast-paced nature of a small organisation "
        "meant that priorities could shift quickly, for instance when an urgent fee-reconciliation "
        "requirement arose during peak admission days, requiring adaptability and re-prioritisation.",
        "Confidentiality limits: limited access to certain confidential financial figures, which, "
        "while entirely understandable from the organisation's perspective, occasionally required "
        "working with representative data for analytical exercises rather than the complete actual "
        "dataset.",
        "Time constraint against academic depth: balancing the depth of academic rigour expected in "
        "an internship report with the practical constraint of a seven-week duration, which limited "
        "the extent to which longer-term financial trends could be directly observed.",
        "Dependence on other departments: coordinating with multiple departments to obtain timely "
        "operational data such as enrolment numbers, particularly during the busier weeks when "
        "departmental staff had limited bandwidth."])

    def challenge_matrix(dd, x, y, w, h):
        dg.matrix_2x2(dd, x, y, w, h, "Difficulty of resolving the challenge",
                      "Impact on the internship work",
                      [("Manage actively", BLUE), ("Escalate to the mentor", ORANGE),
                       ("Absorb and adapt", GREY_M), ("Accept as a constraint", PURPLE)],
                      [("Unfamiliar accounting software", 0.22, 0.72, BLUE),
                       ("Shifting daily priorities", 0.34, 0.60, BLUE),
                       ("Access to confidential figures", 0.78, 0.80, ORANGE),
                       ("Seven-week time constraint", 0.86, 0.62, ORANGE),
                       ("Delays in receiving enrolment data", 0.46, 0.34, GREY),
                       ("Unfamiliar internal formats", 0.16, 0.26, GREY)])

    d.figure(222, challenge_matrix, "Challenges positioned by their impact on the work and the "
                                    "difficulty of resolving them, with the response adopted in "
                                    "each quadrant.")

    d.section("8.2  Organisational-Level Challenges Observed", key="8.2")
    d.para("In addition to challenges faced personally as an intern, certain broader financial "
           "management challenges facing the organisation itself were observed, and these have "
           "informed the findings and suggestions presented in Chapter 9.")
    d.bullets([
        "Reliance on manual and semi-manual processes for certain finance tasks, which, while "
        "manageable at the current scale, could become a bottleneck as the organisation grows and "
        "transaction volumes increase.",
        "Seasonality in enrolment, particularly a concentration of demand around the school and "
        "college admission cycles, creating uneven cash flow across the year that requires careful "
        "cash budgeting to manage the lean quarter.",
        "The contingent nature of a portion of internship-facilitation revenue, dependent on "
        "successful placement outcomes, which introduces unpredictability into that vertical's "
        "revenue recognition and collection timeline.",
        "Key-person dependency, in that critical financial knowledge and system access rest with a "
        "very small number of individuals.",
        "Under-utilised physical capacity, evidenced by a total asset turnover of below one time and "
        "training-hall utilisation of under sixty per cent.",
        "The need to balance investment in marketing and outreach, essential for sustaining "
        "enrolment growth, against the imperative of cost discipline, particularly given "
        "intensifying competition from both local and online providers."])
    d.table(["Organisational challenge", "Financial symptom observed", "Where it is addressed"],
            [["Manual and disconnected records", "Time lost in month-end reconciliation",
              "Suggestion 1, Section 9.2"],
             ["Seasonal collections against level fixed cost", "Thin third-quarter cash surplus",
              "Suggestion 3, Section 9.2"],
             ["Placement-contingent internship fees", "Longer collection cycle in that vertical",
              "Suggestion 4, Section 9.2"],
             ["Key-person dependency", "Process knowledge concentrated in one role",
              "Suggestion 7, Section 9.2"],
             ["Under-used training capacity", "Total asset turnover of 0.95 times",
              "Sections 6.9 and 9.5"],
             ["Marketing spend discipline", "Adverse marketing variance in the month reviewed",
              "Suggestion 8, Section 9.2"]],
            [1.5, 1.6, 1.1], size=8.4,
            caption="Organisational challenges, their financial symptoms and where each is taken up",
            header_align=["left"] * 3)

    d.section("8.3  Root-Cause Analysis of the Month-End Closing Delay", key="8.3")
    d.para("The most frequently recurring operational difficulty observed was the time taken to "
           "close the accounts at month-end. Rather than treat this as an isolated inconvenience, "
           "the causes were grouped using a cause-and-effect analysis, which proved a useful "
           "discipline because it distinguished causes the organisation can act upon from those "
           "inherent in its scale.")

    def fishbone_fig(dd, x, y, w, h):
        dg.fishbone(dd, x, y, w, h, "Delay in closing the accounts at month-end",
                    [("Process", ["No standard data cut-off date", "Manual register entries"]),
                     ("People", ["A single finance executive", "Peak-season multitasking"]),
                     ("Systems", ["Disconnected spreadsheets", "No integrated ledger"]),
                     ("Information", ["Enrolment data arrives late", "Supporting bills missing"])])

    d.figure(214, fishbone_fig, "Cause-and-effect analysis of the month-end closing delay, grouped "
                                "under process, people, systems and information.")
    d.para("Of the eight causes identified, three " + EM + " the absence of a standard cut-off date, "
           "late receipt of enrolment data and missing supporting bills " + EM + " require no "
           "expenditure to resolve and are addressed by the short-term suggestions in Section 9.4. "
           "The remaining causes relate to systems and staffing and require the medium-term "
           "investment discussed there.")

    d.section("8.4  How the Challenges Were Addressed", key="8.4")
    d.para("Most of the personal challenges faced during the internship were addressed through a "
           "combination of proactive questioning, seeking guidance from the assigned mentor, and a "
           "willingness to revisit and correct initial mistakes, such as a misclassified voucher "
           "entry, promptly upon feedback. Over the course of the seven weeks, increasing "
           "familiarity with the organisation's systems and processes led to a marked improvement in "
           "both the speed and the accuracy with which tasks were completed, illustrating the value "
           "of a structured, progressively challenging internship design.")
    d.table(["Challenge", "Response adopted", "Outcome by the close of the internship"],
            [["Unfamiliarity with software and formats",
              "Maintained a personal note of each format and its purpose",
              "Independent voucher and receipt work from week three"],
             ["Shifting priorities during peak days",
              "Kept a daily task list and confirmed priorities with the mentor each morning",
              "Routine work completed alongside special assignments"],
             ["Limited access to confidential figures",
              "Worked with representative figures and disclosed this clearly",
              "Analysis in Chapter 6 remains methodologically sound"],
             ["Errors in expense classification",
              "Reviewed every correction and built a reference list of expense heads",
              "Classification errors ceased after the third week"],
             ["Delay in receiving operational data",
              "Agreed an informal weekly cut-off with the counselling team",
              "MIS compilation completed within the mentor's timeline"]],
            [1.3, 1.8, 1.7], size=8.4, caption="Challenges, the response adopted and the outcome",
            header_align=["left"] * 3)



# ==========================================================================
# CHAPTER 9
# ==========================================================================
SUGGESTIONS = [
    ("Adopt integrated accounting software", "Replace multiple disconnected spreadsheets with an "
     "ERP-lite accounting package suited to small enterprises, reducing reconciliation effort and "
     "the risk of manual error.", 0.76, 0.90, BLUE, "Medium term", "ERP-lite accounting"),
    ("Formalise the budgeting calendar", "Document the annual budgeting process as a policy with "
     "fixed dates for preparation, review and revision, so that budgeting does not depend on "
     "individual initiative.", 0.30, 0.68, GREEN, "Short term", "Budgeting calendar"),
    ("Introduce a rolling cash-flow forecast", "Maintain a twelve-month rolling forecast updated "
     "monthly to anticipate the lean third quarter and smooth liquidity across the year.",
     0.60, 0.62, BLUE, "Medium term", "Rolling cash forecast"),
    ("Restructure internship fee terms", "Introduce a modest non-refundable registration fee "
     "collected upfront so that the vertical depends less on placement-contingent collections.",
     0.52, 0.80, TEAL, "Medium term", "Internship fee terms"),
    ("Build a monthly KPI dashboard", "Track cost per enquiry, cost per enrolment, collection "
     "efficiency, capacity utilisation and contribution per batch on one page each month.",
     0.11, 0.84, GREEN, "Short term", "Monthly KPI dashboard"),
    ("Establish a banking credit line", "Arrange a modest working-capital facility even if unused, "
     "to build a credit record ahead of future expansion financing.", 0.72, 0.24, PURPLE,
     "Long term", "Banking credit line"),
    ("Cross-train finance and admin staff", "Train a second person on the critical finance "
     "processes and digital tools to reduce key-person dependency.", 0.30, 0.42, GOLD,
     "Short term", "Cross-training of staff"),
    ("Review cost structure half-yearly", "Renegotiate recurring vendor contracts and reallocate "
     "marketing spend by demonstrated return on investment per channel.", 0.14, 0.30, ORANGE,
     "Short term", "Half-yearly cost review")]

BENEFITS = [("Reconciliation and closing time", 100, 55, "hours a month, indexed"),
            ("Manual entry errors detected late", 100, 40, "incidence, indexed"),
            ("Marketing cost per enrolment", 100, 82, "indexed"),
            ("Lean-quarter cash visibility", 40, 95, "months of forward visibility, indexed"),
            ("Capacity utilisation of training hall", 58, 75, "per cent of available hours"),
            ("Total asset turnover", 95, 115, "times, indexed at 100 = 1.0x")]


def chapter9(d):
    d.reset_counters()
    d.chapter("9", "Findings and Suggestions", key="ch9",
              kicker="This chapter consolidates what the analysis in Chapters 4 to 6 shows, offers "
                     "eight practical suggestions, prioritises them by impact and effort, sets "
                     "them into a phased roadmap with an indication of expected benefit, and "
                     "relates the findings back to established financial management theory.")

    d.section("9.1  Key Findings of the Study", key="9.1")
    d.para("Based on the observations, tasks performed and analysis carried out during the "
           "internship, the following key findings emerge. Each is stated with the evidence in this "
           "report that supports it, so that the suggestions which follow can be traced back to a "
           "finding rather than to opinion.")
    d.table(["No.", "Finding", "Supporting evidence in this report"],
            [["1", "The organisation follows a conservative financing approach, relying "
                   "predominantly on internal accruals and promoter capital rather than external "
                   "debt, which minimises risk but may constrain the pace of expansion.",
              "Debt-equity 0.24:1; proprietary ratio 69.5% (Section 6.7)"],
             ["2", "Liquidity is comfortable and the organisation can meet short-term obligations "
                   "without difficulty.",
              "Current ratio 1.92:1; quick ratio 1.71:1; cash ratio 0.85:1 (Section 6.4)"],
             ["3", "Profitability is healthy and the underlying business model is financially sound "
                   "and scalable.",
              "Net margin 18.5%; ROCE 24.6%; margin improving over three years (Sections 6.5, 6.8)"],
             ["4", "Budgeting practices, particularly batch budgeting and break-even analysis, are "
                   "used meaningfully to decide whether and when to run a batch.",
              "Batch budget and break-even at 17 students (Sections 5.3 to 5.5)"],
             ["5", "Cost control operates largely through pre-approval and monthly comparison, but "
                   "the process remains manual and would benefit from systematisation.",
              "Cost control practices and variance analysis (Sections 5.6, 5.7)"],
             ["6", "The cost structure is dominated by personnel cost and is nearly three-quarters "
                   "fixed, which makes enrolment volume the decisive profit driver.",
              "Employee cost 40.6% of revenue; 73% of cost fixed (Section 4.5)"],
             ["7", "Revenue in the internship-facilitation vertical is more volatile and collected "
                   "more slowly than in the other verticals.",
              "Revenue recognition pattern and collection cycle (Sections 4.4, 4.6)"],
             ["8", "Physical capacity is under-utilised, which is the clearest available route to a "
                   "higher return on equity.",
              "Asset turnover 0.95 times; hall utilisation 58% (Sections 2.11, 6.6, 6.9)"]],
            [0.32, 2.3, 1.85], size=8.2, caption="Key findings with supporting evidence",
            aligns=["center", "left", "left"], header_align=["center", "left", "left"],
            fonts_col={0: "bold"})

    d.section("9.2  Suggestions for Improvement", key="9.2")
    d.para("On the basis of the above findings, the following suggestions are respectfully offered "
           "for consideration by the management of Infinity Interns. They are offered in the "
           "constructive spirit of an academic exercise and take into account the resource "
           "constraints typical of a small and growing enterprise: none of them requires "
           "professional staff the organisation does not already employ.")
    d.bullets(["%s: %s" % (t, b) for (t, b, _, _, _, _, _) in SUGGESTIONS], size=9.6,
              leading=14.2)

    def finding_map(dd, x, y, w, h):
        dg.mapping(dd, x, y, w, h,
                   ["Manual, spreadsheet-based records",
                    "Seasonal collections against level fixed cost",
                    "Placement-contingent internship fees",
                    "Manual, informal cost control",
                    "Key-person dependency",
                    "Under-utilised physical capacity"],
                   ["Integrated accounting software",
                    "Rolling twelve-month cash forecast",
                    "Upfront non-refundable registration fee",
                    "Monthly KPI dashboard",
                    "Cross-training of a second person",
                    "Half-yearly cost and channel review"],
                   [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 3), (5, 5), (0, 3)],
                   "Finding", "Suggestion")

    d.figure(232, finding_map, "Each suggestion traced to the finding that gives rise to it; two "
                               "findings are addressed by more than one measure.")

    d.section("9.3  Prioritisation of Suggestions", key="9.3")
    d.para("Because administrative bandwidth in a small organisation is the binding constraint, the "
           "suggestions are positioned below by expected financial impact against implementation "
           "effort. The four measures in the upper-left quadrant require little effort and are "
           "recommended for immediate attention.")

    def priority(dd, x, y, w, h):
        dg.matrix_2x2(dd, x, y, w, h, "Implementation effort and cost",
                      "Expected financial impact",
                      [("Quick wins " + EN + " do first", GREEN), ("Major projects " + EN + " plan", BLUE),
                       ("Fill-ins " + EN + " when time permits", GREY_M),
                       ("Re-think " + EN + " defer", ORANGE)],
                      [(short, fx, fy, col)
                       for (_, _, fx, fy, col, _, short) in SUGGESTIONS])

    d.figure(228, priority, "Impact-effort prioritisation of the eight suggestions.")

    d.section("9.4  Suggested Implementation Roadmap", key="9.4")
    d.para("Translating that prioritisation into a time-phased plan gives the roadmap below, which "
           "classifies the suggestions into short-term measures within three months, medium-term "
           "measures over three to twelve months, and long-term measures beyond twelve months.")

    def roadmap_fig(dd, x, y, w, h):
        dg.roadmap(dd, x, y, w, h,
                   [("0 " + EN + " 3 MONTHS", "Quick wins, no outlay",
                     ["Budgeting policy and calendar",
                      "Monthly KPI dashboard",
                      "Monthly data cut-off date",
                      "Renegotiate vendor contracts"], GREEN),
                    ("3 " + EN + " 12 MONTHS", "System and process build",
                     ["Implement ERP-lite accounting",
                      "Rolling 12-month cash forecast",
                      "Restructure internship fee terms",
                      "Cross-train a second person"], BLUE),
                    ("BEYOND 12 MONTHS", "Growth preparation",
                     ["Modest working-capital facility",
                      "Feasibility of a second centre",
                      "Online counselling delivery",
                      "Asset turnover above one time"], ORANGE)])

    d.figure(214, roadmap_fig, "Phased implementation roadmap for the suggestions offered.")
    d.table(["Suggestion", "Horizon", "Indicative cost", "Owner suggested", "Primary benefit"],
            [[SUGGESTIONS[1][0], "Short term", "Nil, time only", "Finance executive",
              "Budgeting becomes institutional practice"],
             [SUGGESTIONS[4][0], "Short term", "Nil, time only", "Finance executive",
              "Faster, data-driven management decisions"],
             [SUGGESTIONS[6][0], "Short term", "Low", "Director",
              "Reduced key-person dependency"],
             [SUGGESTIONS[7][0], "Short term", "Nil, time only", "Finance executive with Director",
              "Lower recurring cost and better marketing return"],
             [SUGGESTIONS[0][0], "Medium term", "Moderate, one-time and annual licence",
              "Director with the accountant", "Fewer errors and faster month-end closing"],
             [SUGGESTIONS[2][0], "Medium term", "Nil, time only", "Finance executive",
              "Liquidity smoothed across the lean quarter"],
             [SUGGESTIONS[3][0], "Medium term", "Nil, policy change", "Director",
              "Shorter and more certain collection cycle"],
             [SUGGESTIONS[5][0], "Long term", "Processing charges only", "Director",
              "Credit record established ahead of expansion"]],
            [1.65, 0.8, 1.25, 1.2, 1.6], size=8.2,
            caption="Implementation plan for each suggestion",
            header_align=["left"] * 5,
            row_colors={0: GREEN_L, 1: GREEN_L, 2: GREEN_L, 3: GREEN_L})

    d.section("9.5  Expected Benefit of the Suggestions", key="9.5")
    d.para("The indicative effect of implementing the short and medium-term suggestions is set out "
           "below. The figures are directional rather than forecast: they express the improvement "
           "that the mechanics of the measures would be expected to produce, and they are presented "
           "as indices so that no claim is made about absolute rupee outcomes.")

    def benefit_fig(dd, x, y, w, h):
        ch.bar_grouped(dd, x, y, w, h,
                       ["Closing\ntime", "Late-caught\nerrors", "Marketing\ncost/enrolment",
                        "Cash\nvisibility", "Hall\nutilisation", "Asset\nturnover"],
                       [("Present position (indexed)", [b[1] for b in BENEFITS], GREY_M),
                        ("After the suggested measures", [b[2] for b in BENEFITS], BLUE)],
                       fmt=lambda v: "%.0f" % v, ymax=120, ticks=4, label_size=6.6,
                       ylabel="Index (present position = 100 unless stated)")

    d.figure(196, benefit_fig, "Indicative direction and scale of improvement expected from the "
                               "suggested measures; for the first three indicators a lower value is "
                               "better, for the last three a higher value is better.")
    d.para("Two of these effects deserve emphasis. First, raising training-hall utilisation from "
           "about fifty-eight to seventy-five per cent of available hours would lift total asset "
           "turnover towards 1.15 times which, on the DuPont sensitivity presented in Table 6.8, "
           "would carry the return on equity from about 25 per cent to about 31 per cent without any "
           "additional investment or borrowing. Second, a rolling cash forecast does not by itself "
           "create cash, but it converts the third-quarter squeeze from a surprise into a planned "
           "position, which is what allows a small organisation to avoid expensive emergency "
           "funding.")

    d.section("9.6  Relevance of Findings to Financial Management Theory", key="9.6")
    d.para("It is instructive to note that the findings of this internship-based study reinforce, "
           "rather than contradict, several well-established principles of financial management "
           "theory, and reading the observations against the theory sharpens both.")
    d.table(["Observation in this study", "Corresponding theoretical proposition",
             "What the comparison suggests"],
            [["Preference for internal accruals and promoter capital over external debt",
              "Pecking-order theory: firms prefer internal to external finance, and debt to equity "
              "when external finance is required",
              "Behaviour is consistent with theory, reinforced by the information asymmetry typical "
              "of small, closely held companies"],
             ["Substantial advance collection of programme fees",
              "Working capital theory: minimising the cash conversion cycle reduces the need for "
              "external funding",
              "The organisation earns an interest-free source of funds from its own customers"],
             ["Break-even analysis used before launching a batch",
              "Cost-volume-profit analysis under a high operating-leverage cost structure",
              "With 73 per cent of cost fixed, the theory's predictions about volume sensitivity "
              "hold visibly"],
             ["Healthy return on equity driven by margin rather than leverage",
              "DuPont decomposition of return on equity",
              "Improvement should be sought in asset utilisation, since margin is already strong "
              "and leverage is deliberately low"],
             ["Segregation of duties maintained despite a very small team",
              "Internal control theory on the prevention and detection of error and fraud",
              "Proportionate control is achievable at small scale and need not be elaborate"],
             ["Discretionary spend justified afresh each period",
              "Zero-based budgeting applied selectively rather than wholesale",
              "A hybrid of incremental and zero-based budgeting suits an organisation of this size"]],
            [1.5, 1.7, 1.8], size=8.2,
            caption="Findings read against established financial management theory",
            header_align=["left"] * 3)


# ==========================================================================
# CHAPTER 10
# ==========================================================================
def chapter10(d):
    d.reset_counters()
    d.chapter("10", "Conclusion", key="ch10",
              kicker="This closing chapter presents a consolidated scorecard of the organisation's "
                     "financial health and sets out the concluding observations on the internship "
                     "as a whole.")

    d.section("10.1  Overall Financial Health Scorecard", key="10.1")
    d.para("Drawing together the analysis of the preceding chapters, the organisation's financial "
           "position may be summarised across five dimensions. The scorecard records a strong "
           "position on four of the five, with asset utilisation as the single clear improvement "
           "opportunity " + EM + " a conclusion reached independently from the capacity data in "
           "Chapter 2 and from the ratio analysis in Chapter 6.")

    def scorecard_fig(dd, x, y, w, h):
        half = (w - 24) / 2.0
        ch.radar(dd, x, y, half, h,
                 ["Liquidity", "Profitability", "Solvency", "Asset utilisation",
                  "Collection discipline", "Cost control"],
                 [("Assessed position", [94, 90, 96, 62, 82, 74], BLUE)], legend_on=True)
        ch.progress_bars(dd, x + half + 24, y, half, h,
                         [("Liquidity", 94, 100, "Strong", BLUE, 75),
                          ("Profitability", 90, 100, "Strong", GREEN, 75),
                          ("Solvency", 96, 100, "Very strong", TEAL, 75),
                          ("Asset utilisation", 62, 100, "Improve", ORANGE, 75),
                          ("Collection discipline", 82, 100, "Good", PURPLE, 75),
                          ("Cost control", 74, 100, "Adequate", GOLD, 75)])

    d.figure(212, scorecard_fig, "Consolidated financial health scorecard; the marker on each bar is "
                                 "the level at which a dimension was treated as satisfactory.")
    d.table(["Dimension", "Principal evidence", "Assessment"],
            [["Liquidity", "Current ratio 1.92:1, quick ratio 1.71:1, cash covering 85 per cent of "
                           "current liabilities", "Strong"],
             ["Profitability", "Net margin 18.5 per cent, ROCE 24.6 per cent, margin improving "
                               "across three years", "Strong"],
             ["Solvency", "Debt-equity 0.24:1, interest covered 28.9 times", "Very strong"],
             ["Asset utilisation", "Total asset turnover 0.95 times, training hall used 58 per cent "
                                   "of available hours", "Improvement opportunity"],
             ["Collection discipline", "Average collection period 38 days, substantial advance "
                                       "collection at enrolment", "Good"],
             ["Cost control", "Pre-approval and monthly variance review in place, but largely "
                              "manual", "Adequate, systematisation needed"]],
            [1.0, 2.6, 1.1], size=8.4, caption="Summary assessment of financial health",
            aligns=["left", "left", "left"], header_align=["left", "left", "left"],
            col_colors={2: NAVY_D})

    d.section("10.2  Concluding Observations", key="10.2")
    d.para("The seven-week internship undertaken at Infinity Interns, a unit of Infinitya1 Career "
           "Counselling Private Limited, proved to be a rich and rewarding learning experience that "
           "fulfilled its primary objective of bridging the gap between the theoretical study of "
           "financial management and its practical application within a real, functioning "
           "organisation. Working within the finance and administration function of a growing career "
           "counselling and skill-development enterprise offered a vantage point from which to "
           "observe, and in a modest way contribute to, the day-to-day and periodic financial "
           "decisions that determine an organisation's stability and growth.")
    d.para("The internship confirmed that the core principles of financial management taught in the "
           "classroom " + EM + " from the recognition of revenue and the classification of costs to "
           "the construction of budgets, the analysis of variances and the computation and "
           "interpretation of financial ratios " + EM + " are not abstract exercises but living "
           "tools which, when applied with judgement and adapted sensibly to the scale and nature of "
           "the organisation, provide genuine and continuing value to management decision-making.")
    d.para("The analysis presented in this report indicates that the organisation follows a broadly "
           "prudent and financially sound approach, characterised by comfortable liquidity, healthy "
           "profitability and a conservative capital structure, while also facing the typical "
           "challenges of a growing small enterprise, including the seasonality of revenue, reliance "
           "on manual processes, under-utilised physical capacity and the need for further "
           "systematisation of its budgeting and cost-control practices. The suggestions offered in "
           "Chapter 9 are intended as constructive, practically implementable recommendations that "
           "build upon the organisation's existing strengths rather than requiring it to change its "
           "character.")
    d.para("On a personal note, this internship has significantly enhanced both the technical "
           "financial-management competencies and the professional soft skills of the author, as "
           "documented in the self-assessment in Section 7.2, and has provided valuable clarity "
           "regarding future career direction within the broad and dynamic field of finance. The "
           "experience is expected to serve as a strong foundation for subsequent academic and "
           "professional pursuits, and the author remains sincerely grateful to Infinity Interns and "
           "its team for the opportunity, guidance and support extended throughout the internship "
           "period.")
    d.gap(6)
    d.callout("In one sentence",
              "A small organisation that manages its money conservatively, prices its services with "
              "a clear view of contribution, and collects its fees in advance has earned itself the "
              "financial room to grow " + EM + " and the most valuable growth available to it "
              "requires filling the classrooms it already pays for rather than raising new funds.",
              color=NAVY, bg=BLUE_XL)



# ==========================================================================
# BIBLIOGRAPHY
# ==========================================================================
def bibliography(d):
    d.reset_counters()
    d.chapter("", "Bibliography", key="biblio",
              kicker="The following sources, both primary and secondary, were referred to and "
                     "relied upon during the internship and in the preparation of this report.")
    d.minihead("Books and standard texts", color=BLUE)
    d.bullets([
        "Khan, M. Y. and Jain, P. K., Financial Management: Text, Problems and Cases, McGraw Hill "
        "Education, latest edition.",
        "Pandey, I. M., Financial Management, Vikas Publishing House, latest edition.",
        "Chandra, Prasanna, Financial Management: Theory and Practice, McGraw Hill Education, "
        "latest edition.",
        "Horngren, C. T., Datar, S. M. and Rajan, M. V., Cost Accounting: A Managerial Emphasis, "
        "Pearson Education, latest edition.",
        "Maheshwari, S. N., Financial and Management Accounting, Sultan Chand and Sons, latest "
        "edition.",
        "Brigham, E. F. and Houston, J. F., Fundamentals of Financial Management, Cengage Learning, "
        "latest edition."], marker="number", bold_lead=False, size=9.6, leading=14.0)
    d.minihead("Organisational sources", color=TEAL)
    d.bullets([
        "Company brochures, promotional material and website of Infinity Interns / Infinitya1 "
        "Career Counselling Private Limited.",
        "Internal, non-confidential formats, registers and MIS templates shared by the organisation "
        "during the internship period, used purely for illustrative purposes in this report.",
        "Discussions and interviews conducted with the Director, the Finance Executive and other "
        "staff members of Infinity Interns during the internship period, June to July 2025.",
        "Personal activity log maintained by the author through the seven weeks of the internship, "
        "from which the work volumes in Section 3.5 are drawn."],
        marker="number", bold_lead=False, size=9.6, leading=14.0)
    d.minihead("Regulatory and sector material", color=PURPLE)
    d.bullets([
        "Ministry of Corporate Affairs, Government of India: general reference on the private "
        "limited company regulatory framework under the Companies Act, 2013.",
        "Goods and Services Tax framework: general reference on invoicing and input tax credit "
        "requirements applicable to service providers.",
        "National Education Policy 2020: reference to the policy emphasis on career guidance and "
        "skill-based education.",
        "General industry articles and reports on the career counselling, education-services and "
        "skill-development sector in India, consulted for contextual background in Section 1.2."],
        marker="number", bold_lead=False, size=9.6, leading=14.0)
    d.callout("A note on the use of sources",
              "Where a figure in this report is derived from the organisation's records it is "
              "described as observed; where it has been reconstructed to preserve confidentiality it "
              "is described as illustrative; and where it reflects general sector experience rather "
              "than a published statistic it is described as indicative. This distinction is "
              "maintained consistently throughout the report.", color=BLUE, bg=BLUE_XL)


# ==========================================================================
# ANNEXURES
# ==========================================================================
def annexures(d):
    d.reset_counters()
    d.chapter("", "Annexures", key="annex",
              kicker="This section presents the supporting formats used during the internship, an "
                     "illustrative consolidated ratio worksheet, the discussion guide followed "
                     "during interviews, a glossary, a list of abbreviations and an index of the "
                     "exhibits presented in this report.")

    d.section("Annexure A  " + EN + "  Sample Petty Cash Voucher Format", key="annexA")
    d.para("The format below reproduces the petty cash voucher used by the organisation, which the "
           "intern prepared on 96 occasions during the internship, as described in Section 3.4.2.")
    d.table(["Field", "Entry"],
            [["Voucher No.", "_______________________________"],
             ["Date", "_______________________________"],
             ["Paid to", "_______________________________"],
             ["Amount (" + R + ")", "_______________________________"],
             ["Amount in words", "_______________________________"],
             ["Purpose / narration", "_______________________________"],
             ["Expense head", "_______________________________"],
             ["Supporting bill attached", "Yes  /  No"],
             ["Prepared by", "_______________________________"],
             ["Approved by", "_______________________________"]],
            [1.0, 2.2], size=8.6, caption="Petty cash voucher format", header_align=["left", "left"])

    d.section("Annexure B  " + EN + "  Sample Fee Receipt Format", key="annexB")
    d.table(["Field", "Entry"],
            [["Receipt No.", "_______________________________"],
             ["Date", "_______________________________"],
             ["Student name", "_______________________________"],
             ["Programme enrolled", "_______________________________"],
             ["Total programme fee (" + R + ")", "_______________________________"],
             ["Amount received (" + R + ")", "_______________________________"],
             ["Mode of payment", "Cash  /  UPI  /  Bank transfer  /  Card"],
             ["Balance outstanding, if any", "_______________________________"],
             ["Next instalment due on", "_______________________________"],
             ["Received by (signature)", "_______________________________"]],
            [1.0, 2.2], size=8.6, caption="Fee receipt format", header_align=["left", "left"])

    d.section("Annexure C  " + EN + "  Weekly Internship Activity Log Format", key="annexC")
    d.table(["Day", "Date", "Task performed", "Learning noted", "Mentor's remarks"],
            [[day, "", "", "", ""] for day in ["Monday", "Tuesday", "Wednesday", "Thursday",
                                               "Friday", "Saturday"]],
            [0.7, 0.7, 1.7, 1.5, 1.3], size=8.6, caption="Weekly activity log format",
            min_row_h=22, header_align=["left"] * 5, fonts_col={0: "bold"})

    d.section("Annexure D  " + EN + "  Illustrative Monthly Cash Budget Format", key="annexD")
    d.table(["Particulars", "Budgeted (" + R + ")", "Actual (" + R + ")", "Variance (" + R + ")"],
            [["Opening cash and bank balance", "", "", ""],
             ["Add: fee collections " + EN + " counselling", "", "", ""],
             ["Add: fee collections " + EN + " training", "", "", ""],
             ["Add: internship facilitation receipts", "", "", ""],
             ["Add: other receipts", "", "", ""],
             ["Total cash available", "", "", ""],
             ["Less: salaries and trainer honorarium", "", "", ""],
             ["Less: rent and utilities", "", "", ""],
             ["Less: marketing expenses", "", "", ""],
             ["Less: study material and programme cost", "", "", ""],
             ["Less: administrative expenses", "", "", ""],
             ["Less: statutory payments (GST, TDS, advance tax)", "", "", ""],
             ["Closing cash and bank balance", "", "", ""]],
            [2.2, 1.0, 1.0, 1.0], size=8.5, caption="Monthly cash budget format",
            aligns=["left", "right", "right", "right"], bold_rows=[5, 12],
            header_align=["left", "right", "right", "right"], min_row_h=17)

    d.section("Annexure E  " + EN + "  Illustrative Batch Costing Worksheet", key="annexE")
    d.table(["Step", "Particulars", "Working", "Result"],
            [["1", "Planned enrolment", "Capacity of the batch", "30 students"],
             ["2", "Fee per student", "Approved programme fee", rs(6500)],
             ["3", "Expected revenue", "Step 1 x Step 2", rs(195000)],
             ["4", "Variable cost per student", "Material + certificate + refreshment", rs(2500)],
             ["5", "Contribution per student", "Step 2 " + EN + " Step 4", rs(4000)],
             ["6", "Fixed cost of the batch", "Trainer + venue + batch marketing", rs(66000)],
             ["7", "Break-even enrolment", "Step 6 / Step 5", "17 students"],
             ["8", "Margin of safety at plan", "(Step 1 " + EN + " Step 7) / Step 1", "43%"],
             ["9", "Expected surplus at plan", "(Step 1 x Step 5) " + EN + " Step 6", rs(54000)]],
            [0.4, 1.6, 1.6, 1.0], size=8.5,
            caption="Batch costing and break-even worksheet as used during the internship",
            aligns=["center", "left", "left", "right"],
            header_align=["center", "left", "left", "right"], fonts_col={0: "bold"})

    d.section("Annexure F  " + EN + "  Consolidated Ratio Analysis Worksheet", key="annexF")
    d.para("The worksheet below reproduces, in a single consolidated format, the ratio computations "
           "discussed across Sections 6.4 to 6.9 of this report, for ease of reference during "
           "evaluation or viva-voce.")
    d.table(["S. No.", "Ratio", "Formula", "Computation", "Result"],
            [["1", "Current ratio", "Current assets / current liabilities", "13,44,000 / 7,00,000",
              "1.92 : 1"],
             ["2", "Quick ratio", "(Current assets " + EN + " inventory) / current liabilities",
              "11,97,000 / 7,00,000", "1.71 : 1"],
             ["3", "Cash ratio", "Cash and bank / current liabilities", "5,97,000 / 7,00,000",
              "0.85 : 1"],
             ["4", "Net working capital", "Current assets " + EN + " current liabilities",
              "13,44,000 " + EN + " 7,00,000", rs(644000)],
             ["5", "Operating profit margin", "EBIT / revenue", "10,75,200 / 48,00,000", "22.4%"],
             ["6", "Net profit margin", "Net profit / revenue", "8,88,000 / 48,00,000", "18.5%"],
             ["7", "Return on equity", "Net profit / shareholders' funds", "8,88,000 / 35,25,000",
              "25.2%"],
             ["8", "Return on capital employed", "EBIT / capital employed", "10,75,200 / 43,70,000",
              "24.6%"],
             ["9", "Return on total assets", "Net profit / total assets", "8,88,000 / 50,70,000",
              "17.5%"],
             ["10", "Debtors' turnover ratio", "Revenue / trade receivables", "48,00,000 / 5,00,000",
              "9.6 times"],
             ["11", "Average collection period", "365 / debtors' turnover", "365 / 9.6", "38 days"],
             ["12", "Fixed asset turnover", "Revenue / net fixed assets", "48,00,000 / 35,26,000",
              "1.36 times"],
             ["13", "Total asset turnover", "Revenue / total assets", "48,00,000 / 50,70,000",
              "0.95 times"],
             ["14", "Working capital turnover", "Revenue / net working capital",
              "48,00,000 / 6,44,000", "7.45 times"],
             ["15", "Debt-equity ratio", "Long-term debt / shareholders' funds",
              "8,45,000 / 35,25,000", "0.24 : 1"],
             ["16", "Total debt ratio", "Total debt / total assets", "8,45,000 / 50,70,000", "16.7%"],
             ["17", "Proprietary ratio", "Shareholders' funds / total assets",
              "35,25,000 / 50,70,000", "69.5%"],
             ["18", "Interest coverage ratio", "EBIT / finance cost", "10,75,200 / 37,200",
              "28.9 times"]],
            [0.45, 1.5, 1.9, 1.3, 0.85], size=8.1,
            caption="Consolidated ratio analysis worksheet",
            aligns=["center", "left", "left", "right", "center"],
            header_align=["center", "left", "left", "right", "center"], fonts_col={0: "bold"},
            line_h=10.8, pad=4.4)

    d.section("Annexure G  " + EN + "  Interview and Discussion Guide", key="annexG")
    d.para("The following indicative set of questions guided the structured discussions held with "
           "the Director and the Finance Executive during the internship, and informed the analysis "
           "presented in Chapters 4 to 6 of this report.")
    d.bullets([
        "How are the annual and monthly budgets for the organisation prepared, and who is involved "
        "in the process?",
        "What is the broad fee-collection policy followed across the counselling, training and "
        "internship-facilitation verticals?",
        "What proportion of the organisation's funding requirement is met through owners' capital as "
        "against external borrowing, and what is the rationale for this approach?",
        "What internal control measures are in place to prevent unauthorised or erroneous cash "
        "payments?",
        "How does the organisation decide whether to proceed with, postpone or cancel a proposed "
        "training batch?",
        "What are the major cost heads that management monitors most closely on a monthly basis, and "
        "why?",
        "How is marketing expenditure evaluated, and which channels have historically produced the "
        "best conversion?",
        "How is the seasonality of collections managed through the lean months of the year?",
        "What financial or operational challenges does the organisation currently consider most "
        "significant to its continued growth?",
        "What would the organisation need in place before it could consider opening a second "
        "centre?"], marker="number", bold_lead=False, size=9.4, leading=13.6)

    d.section("Annexure H  " + EN + "  Glossary of Key Terms", key="annexH")
    d.table(["Term", "Meaning as used in this report"],
            [["Accrual concept", "Recognition of revenue and expenses when they are earned or "
                                 "incurred, not necessarily when cash is received or paid"],
             ["Break-even point", "The level of enrolment at which total revenue equals total cost, "
                                  "resulting in neither profit nor loss"],
             ["Contribution margin", "Revenue less variable cost, being the amount available to "
                                     "cover fixed costs and generate surplus"],
             ["Common-size statement", "A statement in which each item is expressed as a percentage "
                                       "of revenue or of total assets"],
             ["Current ratio", "A liquidity ratio measuring current assets relative to current "
                               "liabilities"],
             ["Debt-equity ratio", "A solvency ratio comparing long-term external debt to "
                                   "shareholders' funds"],
             ["DuPont analysis", "Decomposition of return on equity into net margin, asset turnover "
                                 "and the equity multiplier"],
             ["Input tax credit", "Credit available for GST paid on eligible business purchases, set "
                                  "off against GST payable on services supplied"],
             ["Margin of safety", "The extent by which actual or planned enrolment exceeds the "
                                  "break-even enrolment"],
             ["MIS report", "A periodic management information summary of key operational and "
                            "financial data used for decision-making"],
             ["Operating leverage", "The sensitivity of profit to a change in volume, which rises as "
                                    "the proportion of fixed cost rises"],
             ["Variance analysis", "Comparison of actual results against budgeted figures to "
                                   "identify and explain deviations"],
             ["Working capital", "The difference between current assets and current liabilities, "
                                 "representing short-term operating liquidity"],
             ["Zero-based budgeting", "A method requiring each item of expenditure to be justified "
                                      "afresh rather than carried forward"]],
            [1.0, 2.9], size=8.4, caption="Glossary of key financial management terms",
            header_align=["left", "left"], fonts_col={0: "bold"})

    d.section("Annexure I  " + EN + "  List of Abbreviations", key="annexI")
    abbr = [("BRS", "Bank Reconciliation Statement"), ("CIN", "Corporate Identity Number"),
            ("CVP", "Cost-Volume-Profit"), ("EBIT", "Earnings Before Interest and Tax"),
            ("ERP", "Enterprise Resource Planning"), ("FM", "Financial Management"),
            ("FP&A", "Financial Planning and Analysis"), ("GST", "Goods and Services Tax"),
            ("KPI", "Key Performance Indicator"), ("MBA", "Master of Business Administration"),
            ("MIS", "Management Information System"), ("NEP", "National Education Policy"),
            ("NWC", "Net Working Capital"), ("PAT", "Profit After Tax"),
            ("PBT", "Profit Before Tax"), ("ROA", "Return on Assets"),
            ("ROCE", "Return on Capital Employed"), ("ROE", "Return on Equity"),
            ("ROI", "Return on Investment"), ("SME", "Small and Medium Enterprise"),
            ("SWOT", "Strengths, Weaknesses, Opportunities, Threats"),
            ("TDS", "Tax Deducted at Source"), ("ZBB", "Zero-Based Budgeting")]
    half = (len(abbr) + 1) // 2
    rows = []
    for i in range(half):
        left = abbr[i]
        right = abbr[i + half] if i + half < len(abbr) else ("", "")
        rows.append([left[0], left[1], right[0], right[1]])
    d.table(["Abbreviation", "Full form", "Abbreviation", "Full form"], rows,
            [0.75, 1.7, 0.75, 1.7], size=8.4, caption="Abbreviations used in this report",
            header_align=["left"] * 4, fonts_col={0: "bold", 2: "bold"})

    d.section("Annexure J  " + EN + "  Index of Exhibits by Chapter", key="annexJ")
    d.para("The report contains the following count of exhibits, which are listed individually in "
           "the List of Figures and the List of Tables in the preliminary pages. Charts present "
           "quantitative relationships; diagrams present processes, structures and frameworks.")
    d.table(["Chapter", "Charts", "Diagrams", "Tables", "Principal exhibits"],
            [["Preliminary pages", "1", "0", "0",
              "Key-indicator dashboard with revenue mix and contribution"],
             ["1  Introduction", "1", "5", "2",
              "Industry growth index, demand drivers, objectives, research design, report "
              "structure"],
             ["2  Company profile", "4", "6", "4",
              "Revenue mix and contribution, headcount, capacity utilisation, competitive "
              "positioning, values, portfolio, organisation chart, value chain, SWOT, conversion "
              "funnel"],
             ["3  Internship tasks", "4", "3", "2",
              "Task progression, work schedule, time allocation, tool proficiency, fee process, "
              "voucher cycle, department interaction"],
             ["4  Financial management", "3", "6", "7",
              "Balance-sheet composition, cost structure, seasonality, management cycle, fund "
              "flow, cash cycle, decision path, digitisation ladder, control pyramid"],
             ["5  Budgeting & cost control", "6", "3", "5",
              "Batch waterfall, break-even chart, sensitivity, variance tornado, budget against "
              "actual, channel cost, budget cycle, budget hierarchy, cost controls"],
             ["6  Ratio analysis", "9", "1", "9",
              "Profit walk, balance-sheet bars, liquidity dials, profitability radar, efficiency "
              "bars, capital structure, common-size bar, trend combo, benchmark scorecard, DuPont "
              "tree"],
             ["7  Learning outcomes", "1", "1", "2",
              "Competency dumbbell, concept-to-practice bridge"],
             ["8  Challenges faced", "0", "2", "2",
              "Challenge impact-effort matrix, cause-and-effect analysis"],
             ["9  Findings & suggestions", "1", "3", "3",
              "Finding-to-suggestion map, priority matrix, roadmap, expected benefit"],
             ["10  Conclusion", "1", "0", "1", "Financial health radar and scorecard"],
             ["Annexures A to K", "0", "0", "9",
              "Formats, batch costing and ratio worksheets, glossary, abbreviations, exhibit index"],
             ["Total", "31", "30", "46", "61 figures and 46 tables across 80 numbered pages"]],
            [1.15, 0.5, 0.58, 0.5, 2.6], size=8.1,
            caption="Index of exhibits by chapter",
            aligns=["left", "center", "center", "center", "left"],
            header_align=["left", "center", "center", "center", "left"], bold_rows=[12])

    d.section("Annexure K  " + EN + "  Certificates and Photographs", key="annexK")
    d.para("The internship completion certificate issued by Infinity Interns is enclosed as a "
           "separate scanned attachment along with the physical copy of this report submitted to the "
           "institute. Photographs of the office premises and of training sessions attended have "
           "been omitted from this digital version to preserve the organisation's privacy and are "
           "available with the author upon request for verification purposes.")
    d.gap(10)
    y = d.y
    for i, lab in enumerate(["Internship offer letter", "Completion certificate",
                             "Mentor's feedback form"]):
        bx = d.x0 + i * (d.content_w / 3.0)
        bw = d.content_w / 3.0 - 12
        d.round_rect(bx, y - 96, bw, 96, 3, fill=GREY_XL, stroke=GREY_L, lw=0.7, )
        d.line(bx + 10, y - 30, bx + bw - 10, y - 30, GREY_M, 0.6, dash=(3, 2))
        d.text_center(bx + bw / 2.0, y - 44, "enclosed separately", "italic", 7.4, GREY_M)
        d.text_center(bx + bw / 2.0, y - 84, lab, "semibold", 8.4, NAVY)
    d.y = y - 110
    d.text_center(d.page_w / 2.0, d.y, "END OF REPORT", "bold", 9.0, GREY_M, char_space=2.4)
