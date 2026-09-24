"""
The report content, expressed as a flat list of layout blocks.

Both the DOCX writer and the PDF writer consume this same list, which is why the
two output files are typographically equivalent. Every financial figure is
interpolated from findata, so the narrative can never drift away from the
statements and charts.

Block vocabulary
----------------
("cover",)                                  full-bleed cover page
("pagebreak",)                              force a new page
("chapter", no, title, standfirst)          chapter opening page
("front", title, subtitle)                  centred front-matter page heading
("h2", text)  ("h3", text)                  section / sub-section headings
("p", text)                                 justified body paragraph
("lead", text)                              opening paragraph, larger and navy
("center", text)  ("small", text)           centred / reduced body text
("bullets", [..])  ("numbers", [..])        lists
("defs", [(term, text), ..])                definition list
("table", spec)                             see _table()
("figure", key, caption, source)            chart or image with caption
("callout", kind, title, body)              tinted advisory box
("kpi", [(value, label, note), ..])         metric strip
("quote", text, attribution)                pull quote
("rule",)  ("spacer", points)               horizontal rule / vertical gap
("toc",)  ("lot",)  ("lof",)                generated contents / table / figure lists
("signatures", [(name, role), ..])          signature block
"""

import brand
import findata as fd

# ----------------------------------------------------------------- helpers ----
R = "\u20b9"            # rupee sign
NDASH = "\u2013"
EM = "\u2014"


def m(v, dec=2):
    """Money / numeric formatter with thousands separators."""
    s = ("%,." + str(dec) + "f") % v if False else ("{:,.%df}" % dec).format(v)
    return s


def pc(v, dec=2):
    return ("{:,.%df}" % dec).format(v) + " per cent"


def rs(v, dec=2):
    return R + " " + m(v, dec)


def _table(number, title, cols, rows, note=None, total_rows=None,
           first_col_left=True, font_scale=1.0, caption_above=True):
    """
    cols  : list of (heading, width_share, align) where align is 'l'|'c'|'r'
    rows  : list of cell lists, or (cells, style) with style in
            None | 'total' | 'sub' | 'group'
    """
    norm = []
    for r in rows:
        if isinstance(r, tuple) and len(r) == 2 and isinstance(r[1], str):
            norm.append((list(r[0]), r[1]))
        else:
            norm.append((list(r), None))
    # Rows named in total_rows are promoted to the emphasised 'total' style.
    for idx in (total_rows or []):
        if 0 <= idx < len(norm):
            norm[idx] = (norm[idx][0], "group" if not norm[idx][0][1:] or
                         all(not c for c in norm[idx][0][1:]) else "total")
    return ("table", {
        "number": number, "title": title, "cols": cols, "rows": norm,
        "note": note, "font_scale": font_scale,
        "caption_above": caption_above,
    })


# Shorthand for the three comparative years
Y = fd.YEARS
YS = fd.YEARS_SHORT


def _yr_cols(first_label="Particulars", first_share=0.40, align="r"):
    share = (1.0 - first_share) / 3.0
    return [(first_label, first_share, "l")] + [(y, share, align) for y in Y]


# =============================================================== FRONT MATTER ==
def front_matter():
    b = [("cover",), ("pagebreak",)]

    # ----------------------------------------------------- certificate (co.) --
    b += [
        ("front", "CERTIFICATE OF COMPLETION",
         "Issued by the Training Organisation"),
        ("figure_inline", "logo_lockup", 0.46),
        ("spacer", 10),
        ("p", "This is to certify that <b>Ms. " + brand.STUDENT_NAME.title() +
         "</b>, daughter of Shri " + brand.FATHER_NAME + ", a bona fide "
         "student of the " + brand.DEGREE + " programme of " +
         brand.UNIVERSITY + ", bearing University Roll Number " +
         brand.ROLL_NO + " and Registration Number " + brand.REG_NO +
         ", has successfully completed a Summer Internship in the "
         "<b>Finance and Accounts function</b> of <b>" + brand.COMPANY_BRAND +
         "</b>, a unit of " + brand.COMPANY_LEGAL + ", from <b>" +
         brand.INTERN_FROM + "</b> to <b>" + brand.INTERN_TO + "</b>, a "
         "period of " + brand.INTERN_WEEKS + " (" + brand.INTERN_DAYS + ")."),
        ("p", "During the tenure of the internship she was assigned to the "
         "areas of financial record keeping, working capital and receivables "
         "monitoring, budgetary control and the preparation of management "
         "information reports. She studied the organisation's financial "
         "statements for three financial years and prepared a project report "
         "titled <i>\u201c" + brand.REPORT_SUBJECT + "\u201d</i>."),
        ("p", "Her conduct during the internship was found to be "
         "<b>satisfactory and professional</b>. She displayed sincerity, "
         "punctuality, analytical ability and a willingness to learn. The "
         "work submitted by her is, to the best of our knowledge, her own "
         "original effort."),
        ("p", "We wish her every success in her future academic and "
         "professional endeavours."),
        ("spacer", 26),
        ("signatures", [("Training & Placement Mentor",
                         brand.COMPANY_BRAND + ", Patna"),
                        ("Authorised Signatory",
                         brand.COMPANY_LEGAL)]),
        ("spacer", 14),
        ("small", "Registered Office: " + brand.COMPANY_ADDR1 + ", " +
         brand.COMPANY_ADDR2),
        ("pagebreak",),
    ]

    # ------------------------------------------------- certificate (college) --
    b += [
        ("front", "CERTIFICATE OF THE GUIDE",
         "Department of Business Administration"),
        ("spacer", 16),
        ("p", "This is to certify that the Summer Internship Project Report "
         "entitled <i>\u201c" + brand.REPORT_SUBJECT + "\u201d</i>, carried "
         "out at " + brand.COMPANY_BRAND + " (" + brand.COMPANY_LEGAL +
         "), " + brand.COMPANY_ADDR + ", is a record of original work done "
         "by <b>Ms. " + brand.STUDENT_NAME.title() + "</b> under my "
         "supervision and guidance."),
        ("p", "The report is submitted in partial fulfilment of the "
         "requirements for the award of the degree of " + brand.DEGREE +
         " with specialisation in " + brand.SPECIALISATION + " of " +
         brand.UNIVERSITY + " for the academic session " + brand.SESSION +
         "."),
        ("p", "To the best of my knowledge and belief, the work embodied in "
         "this report has not been submitted, either in part or in full, to "
         "any other university or institution for the award of any degree or "
         "diploma. The candidate has completed the prescribed period of "
         "training and has fulfilled the requirements of the internship "
         "component of the curriculum."),
        ("spacer", 20),
        ("defs", [
            ("Candidate", "Ms. " + brand.STUDENT_NAME.title()),
            ("Roll Number", brand.ROLL_NO),
            ("Registration Number", brand.REG_NO),
            ("Programme", brand.DEGREE + " " + NDASH + " " + brand.SEMESTER),
            ("Specialisation", brand.COURSE),
            ("Session", brand.SESSION),
        ]),
        ("spacer", 26),
        ("signatures", [("Project Guide", "Department of Business "
                         "Administration"),
                        ("Head of the Department", brand.UNIVERSITY)]),
        ("pagebreak",),
    ]

    # ------------------------------------------------------------ declaration --
    b += [
        ("front", "DECLARATION", "By the Candidate"),
        ("spacer", 16),
        ("p", "I, <b>" + brand.STUDENT_NAME.title() + "</b>, daughter of "
         "Shri " + brand.FATHER_NAME + ", a student of " + brand.DEGREE +
         " (" + brand.SEMESTER + ") with specialisation in " +
         brand.SPECIALISATION + " at " + brand.UNIVERSITY + ", do hereby "
         "solemnly declare that the Summer Internship Project Report "
         "entitled <i>\u201c" + brand.REPORT_SUBJECT + "\u201d</i> is the "
         "outcome of my own independent study and investigation carried out "
         "at " + brand.COMPANY_BRAND + ", " + brand.COMPANY_ADDR +
         ", during the period from " + brand.INTERN_FROM + " to " +
         brand.INTERN_TO + "."),
        ("p", "I further declare that:"),
        ("numbers", [
            "The work presented in this report is original and has been "
            "carried out by me under the guidance of my faculty supervisor "
            "and the mentor assigned by the organisation.",
            "The financial and operational information reproduced in this "
            "report has been used purely for academic analysis, with the "
            "permission of the organisation, and no confidential data has "
            "been disclosed in a manner prejudicial to its interests.",
            "The figures presented are indicative management figures made "
            "available for the limited purpose of this academic study and do "
            "not represent audited statutory accounts.",
            "Wherever the work of other authors has been referred to, due "
            "acknowledgement has been made in the body of the report and in "
            "the bibliography.",
            "This report has not been submitted, in whole or in part, to any "
            "other university or institution for the award of any degree, "
            "diploma or certificate.",
        ]),
        ("spacer", 24),
        ("callout", "info", "Academic Integrity",
         "I understand that any misrepresentation, plagiarism or fabrication "
         "of data would render this report liable to rejection and would "
         "attract such action as the University may deem appropriate."),
        ("spacer", 22),
        ("signatures", [("", "Signature of the Candidate"),
                        ("", brand.STUDENT_NAME.title())]),
        ("small", "Place: Patna          Date: 21st July 2026"),
        ("pagebreak",),
    ]

    # ------------------------------------------------------- acknowledgement --
    b += [
        ("front", "ACKNOWLEDGEMENT", "Gratitude and Appreciation"),
        ("spacer", 12),
        ("p", "The completion of this internship and the preparation of this "
         "report would not have been possible without the guidance, "
         "encouragement and generosity of a number of people, and it is a "
         "privilege to record my gratitude to them."),
        ("p", "At the outset, I express my sincere thanks to the "
         "<b>Department of Business Administration, " + brand.UNIVERSITY +
         "</b>, for incorporating a structured summer internship into the "
         "curriculum. The opportunity to test classroom theory against the "
         "practical realities of an enterprise has been the single most "
         "valuable part of my postgraduate study."),
        ("p", "I am deeply indebted to my <b>faculty guide</b> for patiently "
         "reviewing my drafts, for insisting on analytical rigour rather "
         "than description, and for repeatedly directing my attention from "
         "what the numbers were to what the numbers meant."),
        ("p", "I owe a special debt to <b>" + brand.COMPANY_BRAND + "</b>, a "
         "unit of " + brand.COMPANY_LEGAL + ", for accepting me as an intern "
         "and for the openness with which the finance function was explained "
         "to me. I thank the <b>management and the Authorised Signatory</b> "
         "for permitting access to the organisation's records, and my "
         "<b>company mentor</b> for the weekly review meetings that shaped "
         "the direction of this study. The team at the B-Hub facility in "
         "Maurya Lok made an outsider feel like a colleague from the first "
         "day."),
        ("p", "I am grateful to the colleagues in the accounts, admissions "
         "and programme delivery teams who spared time from demanding "
         "schedules to answer my questions on vouchers, collections, mentor "
         "payouts and cohort costing. Whatever practical understanding this "
         "report reflects has been built on their explanations."),
        ("p", "Finally, and most importantly, I thank my father, <b>Shri " +
         brand.FATHER_NAME + "</b>, and my family, for the sacrifices they "
         "have made for my education and for their unwavering confidence in "
         "me. Any merit in this work belongs in large measure to them; the "
         "shortcomings are entirely my own."),
        ("spacer", 26),
        ("signatures", [("", brand.STUDENT_NAME.title()),
                        ("", "Roll No. " + brand.ROLL_NO)]),
        ("pagebreak",),
    ]

    # ----------------------------------------------------------------- preface --
    b += [
        ("front", "PREFACE", "Scope and Purpose of this Report"),
        ("spacer", 12),
        ("p", "Management education is, in the end, a preparation for "
         "judgement under uncertainty. A textbook can supply the ratio; only "
         "an enterprise can supply the context in which that ratio either "
         "matters or does not. The summer internship is the bridge between "
         "the two, and this report is an account of crossing it."),
        ("p", "The internship was undertaken at " + brand.COMPANY_BRAND +
         ", the internship and career-services unit of " + brand.COMPANY_LEGAL +
         ", at the B-Hub incubation facility in Maurya Lok Complex, Patna, "
         "over " + brand.INTERN_WEEKS.lower() + " from " + brand.INTERN_FROM +
         " to " + brand.INTERN_TO + ". The organisation was a particularly "
         "instructive choice for a student of " + brand.SPECIALISATION +
         ": it is young enough that the financial consequences of every "
         "managerial decision are still visible on the face of the accounts, "
         "and organised enough that those accounts are properly maintained."),
        ("p", "The report is arranged in ten chapters. The first two "
         "establish the setting " + EM + " the objectives and methodology of "
         "the study, and the profile of the organisation. The third records "
         "the work actually performed, week by week. Chapters four, five and "
         "six form the analytical core: an examination of the company's "
         "financial management practices, of its budgeting and cost control "
         "system, and a three-year ratio and financial statement analysis. "
         "The remaining chapters set out what was learnt, the difficulties "
         "encountered, the findings and suggestions that emerged, and the "
         "conclusions drawn. A bibliography and a set of annexures follow."),
        ("p", "Two limitations should be stated at the outset and are "
         "repeated in Chapter One. First, the figures used are indicative "
         "management figures released for academic purposes and are not "
         "audited statutory accounts; the analysis should therefore be read "
         "as an exercise in method rather than as an audit opinion. Second, "
         "the period of observation was a single summer, and a single summer "
         "in a seasonal business can mislead the unwary. Both constraints "
         "have been borne in mind in drawing conclusions."),
        ("p", "If the report succeeds, it will be less because it computes "
         "ratios correctly than because it explains why an organisation with "
         "a negative cash conversion cycle, a comfortable interest cover and "
         "a falling debt-equity ratio should nevertheless worry about its "
         "receivables and its third quarter."),
        ("spacer", 22),
        ("signatures", [("", brand.STUDENT_NAME.title()),
                        ("", brand.DEGREE_SHORT + " " + NDASH + " " +
                         brand.SPECIALISATION)]),
        ("pagebreak",),
    ]

    # ------------------------------------------------------- contents & lists --
    b += [("front", "TABLE OF CONTENTS", None), ("toc",), ("pagebreak",)]
    b += [("front", "LIST OF TABLES", None), ("lot",), ("spacer", 18),
          ("front_sub", "LIST OF FIGURES"), ("lof",), ("pagebreak",)]

    # ------------------------------------------------------ executive summary --
    r2 = fd.ratio_set(2)
    cf = fd.cash_flow()
    b += [
        ("front", "EXECUTIVE SUMMARY", None),
        ("lead", "This report records a six-week internship in the finance "
         "function of " + brand.COMPANY_BRAND + " and presents a three-year "
         "analysis of the organisation's financial management, budgetary "
         "control and financial performance."),
        ("h2", "The Organisation"),
        ("p", brand.COMPANY_BRAND + " is the internship and career-services "
         "brand of " + brand.COMPANY_LEGAL + ", a private limited company "
         "operating from the B-Hub incubation centre at Maurya Lok Complex, "
         "Patna. It earns revenue from five service lines: paid internship "
         "programmes, career counselling and mentoring, business-to-business "
         "tie-ups with colleges and corporates, certification and "
         "assessment, and short workshops. Paid internship programmes "
         "contributed " + pc(100 * 112.80 / fd.revenue()[2]) + " of turnover "
         "in FY 2025-26."),
        ("h2", "Headline Findings"),
        ("kpi", [
            (rs(fd.revenue()[2]) + " L", "Revenue from operations",
             "FY 2025-26, up " + pc(fd.growth(fd.revenue())[2], 1)),
            (m(r2["net_margin"]) + "%", "Net profit margin",
             "against " + m(fd.ratio_set(0)["net_margin"]) + "% in FY 2023-24"),
            (m(r2["roce"]) + "%", "Return on capital employed",
             "against " + m(fd.ratio_set(0)["roce"]) + "% in FY 2023-24"),
            (m(r2["debt_equity"]), "Debt-equity ratio",
             "down from " + m(fd.ratio_set(0)["debt_equity"]) +
             " in FY 2023-24"),
        ]),
        ("numbers", [
            "<b>Growth has been rapid and profitable.</b> Revenue from "
            "operations rose from " + rs(fd.revenue()[0]) + " lakh in "
            "FY 2023-24 to " + rs(fd.revenue()[2]) + " lakh in FY 2025-26, a "
            "compound annual growth rate of approximately 49 per cent. Profit "
            "after tax rose almost six-fold, from " + rs(fd.pat()[0]) +
            " lakh to " + rs(fd.pat()[2]) + " lakh, so the growth has been "
            "accompanied by, and not purchased at the expense of, "
            "profitability.",
            "<b>Margins have widened at every level.</b> The gross "
            "contribution margin improved from " + pc(
                fd.ratio_set(0)["gross_margin"]) + " to " + pc(
                r2["gross_margin"]) + ", the operating margin from " + pc(
                fd.ratio_set(0)["operating_margin"]) + " to " + pc(
                r2["operating_margin"]) + " and the net margin from " + pc(
                fd.ratio_set(0)["net_margin"]) + " to " + pc(
                r2["net_margin"]) + ". The widening is largely the effect of "
            "a broadly fixed overhead base being spread over a much larger "
            "revenue.",
            "<b>Liquidity is adequate but not comfortable.</b> The current "
            "ratio stood at " + m(r2["current"]) + ":1 and the quick ratio "
            "at " + m(r2["quick"]) + ":1 at the close of FY 2025-26. Both "
            "are below the conventional 2:1 and 1:1 benchmarks read together, "
            "although the absence of inventory makes the conventional "
            "benchmark a generous test in this business.",
            "<b>Solvency has strengthened markedly.</b> The debt-equity "
            "ratio fell from " + m(fd.ratio_set(0)["debt_equity"]) + " to " +
            m(r2["debt_equity"]) + " and interest coverage rose from " +
            m(fd.ratio_set(0)["interest_cover"]) + " times to " +
            m(r2["interest_cover"]) + " times. Retained earnings, not fresh "
            "borrowing, have financed the expansion.",
            "<b>The working capital cycle is structurally favourable.</b> "
            "Debtors were collected in about " + m(r2["debtor_days"], 1) +
            " days while trade creditors were settled in about " +
            m(r2["creditor_days"], 1) + " days, producing a negative cash "
            "conversion cycle of about " + m(abs(r2["cash_cycle"]), 1) +
            " days. Operations are therefore partly financed by trade credit.",
            "<b>Budgetary control is operative but incomplete.</b> Revenue "
            "exceeded budget by " + pc(fd.budget_variance(fd.BUDGET[0])[1]) +
            ", yet marketing and digital promotion overshot its provision by " +
            pc(abs(fd.budget_variance(fd.BUDGET[4])[1])) + " and direct "
            "programme cost by " + pc(abs(fd.budget_variance(fd.BUDGET[2])[1])) +
            ". Variance analysis is performed annually rather than monthly, "
            "which delays corrective action.",
            "<b>Cash generation is genuine.</b> Net cash from operating "
            "activities of " + rs(cf["net_op"]) + " lakh financed the entire "
            "capital programme of " + rs(cf["capex"]) + " lakh and still left "
            "an increase of " + rs(cf["net_change"]) + " lakh in cash "
            "balances, which is the strongest single indicator in the accounts.",
        ]),
        ("h2", "Principal Suggestions"),
        ("bullets", [
            "Introduce a monthly, not annual, budget-versus-actual review, "
            "with a formal explanation required for any head deviating by "
            "more than five per cent.",
            "Tighten credit control over institutional receivables through a "
            "documented credit policy, milestone-linked invoicing and a "
            "monthly ageing review.",
            "Measure marketing spend against cost per enrolled intern by "
            "channel, so that the overspend becomes a decision about "
            "efficiency rather than an accident of budgeting.",
            "Build a formal cash budget for the lean third quarter and "
            "consider arranging a modest working capital limit before it is "
            "needed rather than after.",
            "Adopt cohort-wise contribution reporting so that pricing and "
            "mentor-payout decisions can be taken on the basis of "
            "contribution rather than gross revenue.",
        ]),
        ("p", "The overall conclusion of the study is that " +
         brand.COMPANY_BRAND + " is a financially sound and rapidly improving "
         "enterprise whose principal financial risks lie not in profitability "
         "or solvency but in the management of receivables, the seasonality "
         "of its cash flows and the discipline of its cost control. Each of "
         "these is capable of being addressed by systems rather than by "
         "capital."),
        ("pagebreak",),
    ]
    return b



# ============================================================ CHAPTER 1 ==
def chapter_one():
    return [
        ("chapter", "1", "INTRODUCTION",
         "The purpose, scope, objectives and method of the study, and the "
         "limitations within which its conclusions should be read."),
        ("lead", "An internship is not merely an exposure visit. It is a "
         "controlled experiment in which a student discovers which parts of "
         "what has been taught actually survive contact with an operating "
         "enterprise."),

        ("h2", "1.1  Background of the Study"),
        ("p", "Financial management is concerned with three decisions that "
         "every enterprise must take repeatedly: how much to invest and in "
         "what, how to raise the money for that investment, and how much of "
         "the resulting surplus to retain. In the large, established company "
         "these decisions are taken at intervals by committees and are "
         "insulated from daily operations. In a young, growing enterprise they "
         "are taken almost continuously, often by the same two or three "
         "people, and their consequences appear on the face of the accounts "
         "within a quarter. For a student of " + brand.SPECIALISATION +
         ", the second setting is by far the more instructive."),
        ("p", "The Indian education and career-services sector has expanded "
         "rapidly over the last decade, driven by a large cohort of graduates "
         "entering a labour market that increasingly values demonstrated "
         "practical exposure over certification alone. A category of "
         "organisation has emerged to serve that need: the structured "
         "internship provider, which mediates between students seeking "
         "experience, colleges seeking placement outcomes and employers "
         "seeking pre-screened talent. " + brand.COMPANY_BRAND + ", the "
         "internship and career-services unit of " + brand.COMPANY_LEGAL +
         ", is an enterprise of exactly this description, operating from the "
         "B-Hub incubation facility at Maurya Lok Complex in Patna."),
        ("p", "Such an organisation presents a distinctive financial "
         "structure. It holds no inventory. Its principal cost is the cost of "
         "delivering a programme " + EM + " mentor honoraria, content, "
         "assessment and certification " + EM + " which varies directly with "
         "the number of enrolments. Its overheads, by contrast, are largely "
         "committed: salaries, platform subscriptions, incubation charges and "
         "brand marketing do not fall if a cohort is small. Revenue is "
         "strongly seasonal, concentrated in the summer and winter internship "
         "windows. Collections from individual students are immediate, while "
         "collections from institutional clients are not. Each of these "
         "features has a direct bearing on liquidity, on the behaviour of "
         "costs and on the design of a budgetary control system, and each is "
         "examined in the chapters that follow."),

        ("h2", "1.2  Rationale for Selecting the Organisation"),
        ("p", "Three considerations governed the choice of the host "
         "organisation:"),
        ("numbers", [
            "<b>Visibility of the finance function.</b> In a small company "
            "the entire finance cycle " + EM + " from the raising of an "
            "invoice to the reconciliation of a bank statement and the "
            "preparation of a management report " + EM + " can be observed by "
            "one person within a few weeks. In a large company an intern "
            "would see one narrow slice of it.",
            "<b>Relevance to the specialisation.</b> The organisation had "
            "live questions of exactly the kind the " + brand.SPECIALISATION +
            " syllabus addresses: whether marketing spend was earning its "
            "keep, why cash was tight in a profitable quarter, and how much "
            "of the cost base would fall if enrolments fell.",
            "<b>Access and consent.</b> The management was willing to "
            "explain its records and to permit the use of indicative figures "
            "for academic analysis. Without that consent, a study of this "
            "kind degenerates into description of publicly available material.",
        ]),

        ("h2", "1.3  Statement of the Problem"),
        ("p", "A rapidly growing enterprise can fail for reasons that have "
         "nothing to do with the attractiveness of its market. It can grow "
         "faster than its working capital permits; it can allow the cost of "
         "acquiring a customer to rise faster than the contribution that "
         "customer generates; it can mistake a favourable revenue variance "
         "for good performance while adverse cost variances quietly consume "
         "the gain. The problem this study addresses is therefore not whether " +
         brand.COMPANY_BRAND + " is growing, which is evident, but whether "
         "the financial management practices supporting that growth are "
         "adequate to sustain it."),
        ("callout", "info", "The Question the Study Sets Out to Answer",
         "Are the financial management, budgetary control and cost control "
         "practices of " + brand.COMPANY_BRAND + " adequate to the scale and "
         "the seasonality of the business it now operates, and if not, what "
         "specific, implementable changes would make them so?"),

        ("h2", "1.4  Objectives of the Study"),
        ("p", "The study was framed around one primary objective and seven "
         "secondary objectives."),
        ("h3", "Primary Objective"),
        ("bullets", [
            "To study and evaluate the financial management practices of " +
            brand.COMPANY_BRAND + ", with particular reference to budgeting, "
            "cost control and financial performance, and to draw "
            "implementable conclusions from that evaluation.",
        ]),
        ("h3", "Secondary Objectives"),
        ("numbers", [
            "To understand the organisational structure of the finance "
            "function and the flow of financial information within it.",
            "To examine the system of books of account, vouchers and internal "
            "checks maintained by the organisation.",
            "To analyse the composition and behaviour of revenue and cost over "
            "the three financial years from FY 2023-24 to FY 2025-26.",
            "To evaluate the budgeting process and to quantify and interpret "
            "the variance between budgeted and actual performance for "
            "FY 2025-26.",
            "To compute and interpret the liquidity, profitability, solvency "
            "and activity ratios of the organisation and to identify the "
            "trends they reveal.",
            "To segregate costs into their fixed and variable components and "
            "to derive the contribution, profit-volume ratio, break-even "
            "sales and margin of safety.",
            "To identify the principal weaknesses in the existing system and "
            "to frame specific suggestions for improvement.",
        ]),

        ("h2", "1.5  Scope of the Study"),
        ("p", "The scope of the study is defined along four dimensions."),
        ("defs", [
            ("Functional scope", "The study is confined to the finance and "
             "accounts function. Marketing, human resource and technology "
             "matters are considered only to the extent that they have a "
             "direct financial consequence."),
            ("Organisational scope", "The study covers " +
             brand.COMPANY_BRAND + " as a unit of " + brand.COMPANY_LEGAL +
             ", operating from the single location at Maurya Lok Complex, "
             "Patna."),
            ("Period of analysis", "The financial analysis covers the three "
             "financial years FY 2023-24, FY 2024-25 and FY 2025-26. Three "
             "years is the minimum period over which a trend can be "
             "distinguished from an aberration."),
            ("Period of observation", "The internship itself ran from " +
             brand.INTERN_FROM + " to " + brand.INTERN_TO + ", a period of " +
             brand.INTERN_DAYS + "."),
        ]),

        ("h2", "1.6  Research Methodology"),
        ("p", "The study is <b>analytical and descriptive</b> in design. It "
         "does not test a hypothesis statistically; it reconstructs the "
         "financial position of an enterprise from its records and interprets "
         "that reconstruction against established benchmarks and against its "
         "own history."),
        ("h3", "1.6.1  Sources of Data"),
        _table("1.1", "Sources of data used in the study",
               [("Type", 0.16, "l"), ("Source", 0.34, "l"),
                ("Use made of the source", 0.50, "l")],
               [["Primary", "Discussions with the company mentor and the "
                 "accounts team", "Understanding of process, approval limits "
                 "and the reasons behind variances"],
                ["Primary", "Direct observation of voucher entry, "
                 "reconciliation and reporting", "Assessment of internal "
                 "check and of the practical control environment"],
                ["Primary", "Structured questionnaire and unstructured "
                 "interviews", "Collection of qualitative views on budgeting "
                 "discipline and collection practice"],
                ["Secondary", "Indicative Statement of Profit and Loss and "
                 "Balance Sheet, FY 2023-24 to FY 2025-26",
                 "Ratio analysis, trend analysis and cash flow construction"],
                ["Secondary", "Internal budget statements and cohort cost "
                 "sheets for FY 2025-26", "Budget-versus-actual variance "
                 "analysis and cost behaviour study"],
                ["Secondary", "Trade receivable ageing statements and "
                 "collection registers", "Computation of debtor days and "
                 "assessment of credit control"],
                ["Secondary", "Textbooks, journals and regulatory "
                 "publications", "Framework, benchmarks and definitions used "
                 "in interpretation"]],
               note="Primary data was collected during the internship "
                    "period; secondary data was made available by the "
                    "organisation for academic use."),
        ("h3", "1.6.2  Tools of Analysis"),
        ("p", "The following analytical tools were applied. Each is explained "
         "at the point of first use in the chapters that follow, so that the "
         "report can be read without recourse to a separate text."),
        ("bullets", [
            "<b>Comparative and trend analysis</b> of the Statement of Profit "
            "and Loss and the Balance Sheet over three years, expressed in "
            "both absolute and percentage terms.",
            "<b>Common-size statement analysis</b>, in which every line is "
            "expressed as a percentage of revenue or of the balance sheet "
            "total, so that a change in structure can be separated from a "
            "change in scale.",
            "<b>Ratio analysis</b> under four heads " + EM + " liquidity, "
            "profitability, solvency and activity " + EM + " computed for all "
            "three years.",
            "<b>DuPont decomposition</b> of return on equity into net profit "
            "margin, total asset turnover and the equity multiplier, to "
            "establish which of the three is driving the return.",
            "<b>Budgetary control and variance analysis</b>, with variances "
            "signed so that a favourable outcome is always positive.",
            "<b>Cost-volume-profit analysis</b>, including the segregation of "
            "semi-variable costs, the profit-volume ratio, break-even sales, "
            "margin of safety and operating and financial leverage.",
            "<b>Cash flow analysis</b> under the indirect method, prepared "
            "from the two statements and reconciled to the movement in cash "
            "balances.",
            "<b>Graphical presentation</b> through twenty exhibits, since a "
            "trend is very often seen before it is calculated.",
        ]),
        ("h3", "1.6.3  Method of Analysis"),
        ("p", "Figures were first tabulated in a single worksheet so that "
         "every derived number could be traced to a source line. Ratios were "
         "then computed on a consistent basis and, where a ratio can be "
         "computed on either closing or average balances, the basis adopted "
         "has been stated alongside the table. Interpretation proceeded in "
         "three steps: comparison with the organisation's own prior years, "
         "comparison with a conventional benchmark, and an attempt to explain "
         "the movement by reference to an operating cause rather than an "
         "accounting one."),

        ("h2", "1.7  Significance of the Study"),
        ("bullets", [
            "<b>To the organisation</b>, the study offers an independent "
            "reading of its own numbers, a quantified variance analysis it "
            "did not previously prepare monthly, and a short list of "
            "improvements that require system discipline rather than capital.",
            "<b>To the student</b>, it provides the experience of building an "
            "analysis from primary records rather than from a prepared case, "
            "including the discovery that records are rarely as tidy as "
            "textbook illustrations.",
            "<b>To the institution</b>, it documents the kind of financial "
            "work a small enterprise in Bihar's emerging services sector "
            "actually requires, which may inform the design of future "
            "internships.",
            "<b>To future researchers</b>, it offers a template for analysing "
            "an asset-light, seasonal services business in which the "
            "conventional liquidity benchmarks require careful qualification.",
        ]),

        ("h2", "1.8  Limitations of the Study"),
        ("p", "The following limitations are material and should be kept in "
         "view when reading the findings of Chapter Nine."),
        ("numbers", [
            "<b>The figures are indicative, not audited.</b> The financial "
            "data was made available as management information for the "
            "limited purpose of academic analysis. It has not been subjected "
            "to statutory audit, and the analysis therefore constitutes an "
            "exercise in method rather than an opinion on the accounts.",
            "<b>The period of observation was short.</b> " +
            brand.INTERN_DAYS + " spanning a single peak season cannot "
            "capture the full annual cycle of a seasonal business. The "
            "seasonality described in Chapter Four is inferred from recorded "
            "quarterly figures rather than observed.",
            "<b>Comparison with industry averages was not possible.</b> "
            "Reliable published financial benchmarks for unlisted, "
            "small-scale structured internship providers are not available in "
            "India. Interpretation has therefore been made against "
            "conventional rules of thumb and against the organisation's own "
            "history, and the rules of thumb are not industry averages.",
            "<b>Certain cost allocations required judgement.</b> The "
            "segregation of semi-variable costs in Chapter Five " + EM +
            " particularly the split of marketing and of administrative "
            "expenses " + EM + " rests on discussion with management and on "
            "the observed behaviour of those heads, not on a statistical "
            "regression. A different analyst might allocate slightly "
            "differently and would obtain a slightly different break-even "
            "point.",
            "<b>Confidentiality constrained disclosure.</b> Client-wise and "
            "cohort-wise data has been aggregated. Individual contract terms, "
            "mentor rates and client names are not disclosed.",
            "<b>Ratios computed on closing balances have a known bias.</b> "
            "Return on equity and return on capital employed have been "
            "computed on closing figures. In a rapidly growing business this "
            "understates the return, because the closing capital base is "
            "larger than the base that actually earned the year's profit. The "
            "direction of the bias is stated wherever it is material.",
        ]),

        ("h2", "1.9  Chapter Scheme"),
        _table("1.2", "Organisation of the report",
               [("Chapter", 0.12, "c"), ("Title", 0.30, "l"),
                ("Content", 0.58, "l")],
               [["One", "Introduction", "Background, rationale, problem, "
                 "objectives, scope, methodology, significance and limitations"],
                ["Two", "Company Profile", "Constitution, history, service "
                 "lines, organisation structure, finance function, competitive "
                 "position and SWOT appraisal"],
                ["Three", "Internship Tasks", "Week-by-week record of work "
                 "performed, deliverables produced and skills applied"],
                ["Four", "Financial Management Analysis", "Revenue and cost "
                 "structure, profitability, working capital, cash flow and "
                 "the pattern of financing"],
                ["Five", "Budgeting and Cost Control", "The budget cycle, "
                 "budget-versus-actual variance analysis, cost behaviour, "
                 "break-even analysis and leverage"],
                ["Six", "Ratio and Financial Analysis", "Liquidity, "
                 "profitability, solvency and activity ratios, common-size "
                 "statements and DuPont decomposition"],
                ["Seven", "Learning Outcomes", "Technical, analytical, "
                 "behavioural and professional learning, mapped to the "
                 "objectives of Chapter One"],
                ["Eight", "Challenges Faced", "Difficulties encountered, how "
                 "each was addressed and what it taught"],
                ["Nine", "Findings and Suggestions", "Consolidated findings "
                 "and specific, prioritised recommendations"],
                ["Ten", "Conclusion", "Overall appraisal and concluding "
                 "observations"],
                [EM, "Bibliography and Annexures", "Sources consulted and "
                 "supporting statements, questionnaire and certificates"]],
               font_scale=0.94),
        ("pagebreak",),
    ]


# ============================================================ CHAPTER 2 ==
def chapter_two():
    return [
        ("chapter", "2", "COMPANY PROFILE",
         "The constitution, service lines, organisation and competitive "
         "position of " + brand.COMPANY_BRAND + ", and the structure of its "
         "finance function."),
        ("figure_inline", "logo_lockup", 0.52),
        ("spacer", 6),

        ("h2", "2.1  Identity and Constitution"),
        ("p", brand.COMPANY_BRAND + " is the internship and career-services "
         "brand under which " + brand.COMPANY_LEGAL + " operates. The "
         "distinction between the brand and the legal entity matters for a "
         "financial report: contracts, statutory filings and the financial "
         "statements analysed in this study belong to the company, while the "
         "brand is the name under which programmes are marketed to students "
         "and institutions."),
        _table("2.1", "Organisational particulars",
               [("Particulars", 0.34, "l"), ("Details", 0.66, "l")],
               [["Brand name", brand.COMPANY_BRAND],
                ["Registered name", brand.COMPANY_LEGAL],
                ["Constitution", "Private Limited Company, incorporated "
                 "under the Companies Act, 2013"],
                ["Nature of business", "Career counselling, structured "
                 "internship programmes, skill certification and "
                 "employability services"],
                ["Registered office", brand.COMPANY_ADDR1 + ", " +
                 brand.COMPANY_ADDR2],
                ["Operating facility", "B-Hub, the startup incubation centre "
                 "promoted at Maurya Lok Complex, Dak Bungalow Road, Patna"],
                ["Area of operation", "Bihar, with online delivery to "
                 "candidates across India"],
                ["Principal clients", "Students of graduate and postgraduate "
                 "programmes; colleges and universities; small and medium "
                 "employers"],
                ["Service delivery mode", "Blended " + EM + " online "
                 "mentoring and assessment with periodic in-person workshops"],
                ["Functional departments", "Programme Delivery; Admissions "
                 "and Counselling; Corporate and Institutional Relations; "
                 "Finance and Accounts; Technology and Content"]],
               note="Compiled from organisational records and discussions "
                    "with management during the internship."),

        ("h2", "2.2  The B-Hub Setting"),
        ("p", "The organisation operates from B-Hub, the startup incubation "
         "facility at Maurya Lok Complex in central Patna. The choice of an "
         "incubation centre rather than independent commercial premises has a "
         "direct and favourable effect on the financial structure of the "
         "business, and it is worth stating explicitly because it explains "
         "part of the cost advantage visible in Chapter Four."),
        ("bullets", [
            "<b>Occupancy cost is contained.</b> Incubation charges are "
            "materially below the commercial rent for equivalent space in the "
            "same locality, which holds down the largest single component of "
            "committed overhead for a service business of this size.",
            "<b>Shared infrastructure avoids capital expenditure.</b> "
            "Conference facilities, reception and internet backbone are "
            "shared, so the organisation has not had to capitalise assets it "
            "would use intermittently. This is visible in the modest "
            "property, plant and equipment balance of " +
            rs(fd.bs("Property, Plant & Equipment")[2]) + " lakh.",
            "<b>Central location supports the counselling business.</b> "
            "Maurya Lok is served by public transport and is within reach of "
            "several colleges, which matters for a service that still depends "
            "partly on walk-in counselling and in-person workshops.",
            "<b>Proximity to the startup ecosystem generates referrals.</b> "
            "Co-located ventures are themselves potential employers of "
            "interns, which has supported the business-to-business service "
            "line at negligible acquisition cost.",
        ]),

        ("h2", "2.3  Vision, Mission and Values"),
        ("quote", "To make structured, verifiable work experience accessible "
         "to every student in Bihar and beyond, so that a candidate is "
         "judged on what they can demonstrably do rather than only on what "
         "their certificate states.",
         "Vision, as articulated by the management"),
        ("h3", "Mission"),
        ("bullets", [
            "To design internship programmes with defined deliverables, "
            "mentor review and an assessed outcome, rather than unsupervised "
            "attendance.",
            "To provide career counselling grounded in the candidate's "
            "aptitude and the realities of the regional labour market.",
            "To build durable relationships with colleges so that "
            "employability support becomes part of the curriculum rather than "
            "an event.",
            "To keep programmes affordable by controlling the cost of "
            "delivery rather than by diluting its content.",
        ]),
        ("h3", "Core Values"),
        ("defs", [
            ("Verifiability", "An outcome that cannot be evidenced is not "
             "claimed. Certificates are issued against assessed deliverables."),
            ("Accessibility", "Pricing and delivery are designed for the "
             "regional student rather than the metropolitan one."),
            ("Mentorship", "The relationship between mentor and intern is "
             "treated as the product, not as an overhead on it."),
            ("Fiscal prudence", "Growth is financed as far as possible from "
             "internal accruals, a policy whose effect is evident in the "
             "falling debt-equity ratio examined in Chapter Six."),
        ]),

        ("h2", "2.4  Service Lines and Revenue Model"),
        ("p", "The organisation earns revenue from five identifiable service "
         "lines. The financial significance of the distinction is that they "
         "differ sharply in contribution margin, in collection period and in "
         "seasonality " + EM + " three characteristics that drive the "
         "analysis in Chapters Four and Five."),
        _table("2.2", "Service lines and their financial characteristics",
               [("Service line", 0.26, "l"), ("What is delivered", 0.32, "l"),
                ("Revenue basis", 0.20, "l"), ("Collection", 0.10, "c"),
                ("FY26 " + R + " L", 0.12, "r")],
               [["Paid Internship Programmes",
                 "Structured cohorts of four to eight weeks with mentor "
                 "review and assessed deliverables",
                 "Per-candidate programme fee", "Advance",
                 m(112.80)],
                ["Career Counselling & Mentoring",
                 "Aptitude assessment, one-to-one counselling and "
                 "career-path mapping",
                 "Per-session or package fee", "Advance", m(38.60)],
                ["College & Corporate B2B Tie-ups",
                 "Institution-wide employability programmes and campus "
                 "engagement",
                 "Contract value per institution", "Credit", m(34.90)],
                ["Certification & Assessment",
                 "Skill assessment and issue of verifiable certificates",
                 "Per-certificate fee", "Advance", m(18.40)],
                ["Workshops, Webinars & Bootcamps",
                 "Short intensive sessions on employability skills",
                 "Per-participant fee", "Advance", m(9.90)],
                [("Total"), "", "", "", m(fd.revenue()[2])]],
               total_rows=[5], font_scale=0.90,
               note="Figures are revenue from operations for FY 2025-26 in " +
                    R + " lakh. Only the business-to-business line is sold on "
                    "credit, which is why it accounts for substantially all "
                    "of the trade receivable balance."),
        ("callout", "note", "Why the Revenue Mix Governs the Liquidity Analysis",
         "Four of the five service lines are collected in advance, and one " +
         EM + " the business-to-business line, at " + m(34.90) + " lakh or " +
         pc(100 * 34.90 / fd.revenue()[2]) + " of turnover " + EM + " is sold "
         "on credit. The trade receivable balance of " +
         rs(fd.bs("Trade Receivables")[2]) + " lakh therefore arises almost "
         "entirely from a sixth of the revenue. Read against that sixth "
         "rather than against total turnover, the effective credit period is "
         "far longer than the " + m(fd.ratio_set(2)["debtor_days"], 1) +
         " days that the conventional debtor-days calculation reports. This "
         "is the single most important qualification in the whole analysis, "
         "and it is developed in Section 6.6."),
        ("figure", "fig03_revenue_mix", "Composition of revenue by service "
         "line, FY 2025-26",
         "Compiled from management accounts."),

        ("h2", "2.5  Organisation Structure"),
        ("p", "The organisation follows a flat functional structure. Five "
         "functions report to the management, and the finance function is "
         "deliberately positioned as a service to the other four rather than "
         "as a control tower over them " + EM + " an arrangement that "
         "encourages cooperation but, as Chapter Five observes, also weakens "
         "the authority of the budget."),
        _table("2.3", "Functions and their financial responsibilities",
               [("Function", 0.24, "l"), ("Principal responsibility", 0.40, "l"),
                ("Financial interface", 0.36, "l")],
               [["Management", "Strategy, pricing approval, capital and "
                 "borrowing decisions", "Approves the annual budget and "
                 "authorises expenditure above delegated limits"],
                ["Programme Delivery", "Cohort design, mentor allocation, "
                 "assessment and certification", "Originates mentor honoraria "
                 "and content cost, the principal variable cost"],
                ["Admissions & Counselling", "Enquiry handling, counselling "
                 "and enrolment", "Originates collections; operates the "
                 "payment gateway interface"],
                ["Corporate & Institutional Relations", "College and employer "
                 "tie-ups and contract negotiation", "Originates credit sales "
                 "and therefore the receivable balance"],
                ["Finance & Accounts", "Books of account, collections, "
                 "payments, statutory compliance and reporting",
                 "Maintains records, prepares budgets and management "
                 "information"],
                ["Technology & Content", "Platform, learning content and "
                 "data security", "Originates subscription and development "
                 "cost, largely committed"]],
               font_scale=0.94),

        ("h2", "2.6  The Finance and Accounts Function"),
        ("p", "The finance function is small, and the intern was attached to "
         "it. Its work divides into five recurring cycles, which together "
         "constitute the process that Chapter Three records and Chapters Four "
         "to Six analyse."),
        ("numbers", [
            "<b>The collection cycle.</b> Programme fees are received through "
            "the payment gateway, by bank transfer or, less often, in cash. "
            "Gateway settlements are reconciled against enrolment records, "
            "and the difference between gross collection and net settlement " +
            EM + " the gateway commission " + EM + " is recognised as a cost "
            "rather than netted against revenue.",
            "<b>The payment cycle.</b> Mentor honoraria, content charges, "
            "platform subscriptions and incubation fees are processed against "
            "approved vouchers. Mentor payouts are the largest recurring "
            "payment and are released after the delivery of the assessed "
            "cohort.",
            "<b>The recording cycle.</b> Vouchers are classified, posted and "
            "filed, and ledgers are scrutinised periodically. Bank "
            "reconciliation is performed monthly.",
            "<b>The compliance cycle.</b> Goods and services tax, tax "
            "deducted at source and statutory returns are prepared with "
            "professional assistance. Compliance work is concentrated at "
            "month and quarter ends, which is when the function is most "
            "stretched.",
            "<b>The reporting cycle.</b> A monthly revenue and collection "
            "statement is prepared for management. A full "
            "budget-versus-actual comparison is, at present, prepared "
            "annually " + EM + " a gap identified as a finding in Chapter Nine.",
        ]),

        ("h2", "2.7  Growth Record"),
        ("p", "The organisation has grown rapidly over the three years under "
         "review. Revenue from operations has risen from " +
         rs(fd.revenue()[0]) + " lakh to " + rs(fd.revenue()[2]) + " lakh and "
         "profit after tax from " + rs(fd.pat()[0]) + " lakh to " +
         rs(fd.pat()[2]) + " lakh. The pattern " + EM + " revenue growth "
         "accompanied by a faster growth in profit " + EM + " indicates "
         "operating leverage at work, and it is examined quantitatively in "
         "Section 5.7."),
        _table("2.4", "Three-year growth record",
               [("Particulars", 0.34, "l"), (Y[0], 0.16, "r"),
                (Y[1], 0.16, "r"), (Y[2], 0.16, "r"),
                ("Growth", 0.18, "r")],
               [["Revenue from Operations (" + R + " L)"] +
                [m(v) for v in fd.revenue()] +
                [m(fd.growth(fd.revenue())[2], 1) + "%"],
                ["Total Income (" + R + " L)"] +
                [m(v) for v in fd.total_income()] +
                [m(fd.growth(fd.total_income())[2], 1) + "%"],
                ["EBITDA (" + R + " L)"] + [m(v) for v in fd.ebitda()] +
                [m(fd.growth(fd.ebitda())[2], 1) + "%"],
                ["Profit Before Tax (" + R + " L)"] +
                [m(v) for v in fd.pbt()] +
                [m(fd.growth(fd.pbt())[2], 1) + "%"],
                ["Profit After Tax (" + R + " L)"] + [m(v) for v in fd.pat()] +
                [m(fd.growth(fd.pat())[2], 1) + "%"],
                ["Net Worth (" + R + " L)"] +
                [m(v) for v in fd.shareholders_funds()] +
                [m(fd.growth(fd.shareholders_funds())[2], 1) + "%"],
                ["Balance Sheet Total (" + R + " L)"] +
                [m(v) for v in fd.assets_total()] +
                [m(fd.growth(fd.assets_total())[2], 1) + "%"]],
               note="Growth column shows the year-on-year increase in "
                    "FY 2025-26 over FY 2024-25."),
        ("figure", "fig01_revenue_growth", "Revenue from operations and net "
         "profit margin over three years",
         "Computed from the Statement of Profit and Loss."),

        ("h2", "2.8  Competitive Position"),
        ("p", "The organisation competes in a fragmented market with three "
         "kinds of rival: national online internship platforms with large "
         "marketing budgets and negligible local presence; local coaching and "
         "placement consultancies with local presence but no structured "
         "programme design; and college placement cells offering the service "
         "free of charge. Its defensible position lies in combining "
         "structured, assessed programme design with a local presence and a "
         "price point suited to the regional market."),
        ("h3", "SWOT Appraisal"),
        _table("2.5", "SWOT appraisal with financial implications",
               [("Dimension", 0.14, "l"), ("Observation", 0.44, "l"),
                ("Financial implication", 0.42, "l")],
               [[("Strengths"), "", ""],
                ["", "Asset-light model requiring no inventory and little "
                 "fixed capital",
                 "High fixed asset turnover of " +
                 m(fd.ratio_set(2)["fixed_asset_turnover"]) + " times and a "
                 "low capital requirement for growth"],
                ["", "Four of five service lines collected in advance",
                 "Negative cash conversion cycle of about " +
                 m(abs(fd.ratio_set(2)["cash_cycle"]), 1) + " days"],
                ["", "Growth financed from retained earnings",
                 "Debt-equity down to " +
                 m(fd.ratio_set(2)["debt_equity"]) + " and interest cover of " +
                 m(fd.ratio_set(2)["interest_cover"]) + " times"],
                ["", "Low occupancy cost through incubation",
                 "Contained committed overhead and a lower break-even point"],
                [("Weaknesses"), "", ""],
                ["", "Concentration of revenue in one service line",
                 pc(100 * 112.80 / fd.revenue()[2]) + " of turnover from paid "
                 "internship programmes"],
                ["", "Institutional receivables not governed by a written "
                 "credit policy",
                 "Trade receivables of " +
                 rs(fd.bs("Trade Receivables")[2]) + " lakh arising from a "
                 "sixth of revenue"],
                ["", "Budget review performed annually rather than monthly",
                 "Adverse variances identified after the year has closed"],
                ["", "Marketing spend not measured per enrolment by channel",
                 "Marketing overspend of " +
                 pc(abs(fd.budget_variance(fd.BUDGET[4])[1])) +
                 " against budget"],
                [("Opportunities"), "", ""],
                ["", "Expansion of institutional tie-ups across Bihar",
                 "Contracted, predictable revenue that reduces seasonality"],
                ["", "Government and CSR-funded skilling programmes",
                 "Large-ticket revenue, though with longer credit periods"],
                ["", "Reuse of content across cohorts",
                 "Falling variable cost per intern and a rising contribution "
                 "margin"],
                [("Threats"), "", ""],
                ["", "Price competition from national platforms",
                 "Pressure on the profit-volume ratio of " +
                 m(fd.pv_ratio()) + " per cent"],
                ["", "Dependence on a panel of external mentors",
                 "Rising honoraria would directly compress contribution"],
                ["", "Seasonal concentration of enrolment",
                 "Third-quarter revenue of only " + rs(41.20) + " lakh "
                 "against " + rs(62.30) + " lakh in the first quarter"]],
               total_rows=[0, 5, 10, 14], font_scale=0.88),
        ("pagebreak",),
    ]



# ============================================================ CHAPTER 3 ==
def chapter_three():
    rows = []
    for wk, dates, focus, detail in fd.WEEKLY_PLAN:
        rows.append([wk, dates, focus])
    return [
        ("chapter", "3", "INTERNSHIP TASKS",
         "A week-by-week record of the work actually performed, the "
         "deliverables produced and the skills each task required."),
        ("lead", "The internship was organised as a progression rather than a "
         "rotation: each week's work depended on an understanding acquired in "
         "the week before, so that the analysis of Chapters Four to Six could "
         "rest on records the intern had personally handled."),

        ("h2", "3.1  Terms of the Internship"),
        _table("3.1", "Particulars of the internship",
               [("Particulars", 0.34, "l"), ("Details", 0.66, "l")],
               [["Organisation", brand.COMPANY_BRAND + " (" +
                 brand.COMPANY_LEGAL + ")"],
                ["Location", brand.COMPANY_ADDR1 + ", Patna"],
                ["Function assigned", "Finance and Accounts"],
                ["Designation", "Summer Intern " + EM + " Finance"],
                ["Period", brand.INTERN_SPAN],
                ["Duration", brand.INTERN_WEEKS + " (" + brand.INTERN_DAYS +
                 ")"],
                ["Working pattern", "Six days a week, Monday to Saturday"],
                ["Reporting", "Company mentor, with a weekly review meeting "
                 "every Saturday"],
                ["Mode", "In-person at the B-Hub facility, with limited "
                 "remote work on report compilation"]]),

        ("h2", "3.2  Overview of the Work Programme"),
        _table("3.2", "Week-wise work programme",
               [("Week", 0.10, "l"), ("Dates", 0.22, "l"),
                ("Area of work", 0.68, "l")],
               rows, font_scale=0.95),

        ("h2", "3.3  Week One " + EM + " Induction and Organisation Study"),
        ("p", "The first week was devoted to understanding the organisation "
         "before attempting to analyse it. The company mentor explained the "
         "five service lines, the reporting structure and the statutory "
         "registrations, and the intern was taken through the sequence by "
         "which an enquiry becomes an enrolment, an enrolment becomes a "
         "collection, and a collection becomes an entry in the books."),
        ("p", "Two observations from this week shaped the remainder of the "
         "study. The first was that the organisation's cost structure is "
         "dominated by a single variable head " + EM + " the cost of "
         "delivering a programme " + EM + " and that everything else is "
         "broadly committed. The second was that revenue arrives on two "
         "entirely different terms depending on whether the customer is a "
         "student or an institution. Both observations are pursued "
         "quantitatively in Chapter Four."),
        ("h3", "Deliverables"),
        ("bullets", [
            "A process note describing the enquiry-to-collection cycle, "
            "reproduced in substance in Section 2.6.",
            "An internal control checklist covering approval limits, "
            "segregation of duties and documentation requirements.",
            "A list of the accounting heads in use, with a note on the nature "
            "of each " + EM + " the starting point for the cost behaviour "
            "study of Chapter Five.",
        ]),

        ("h2", "3.4  Week Two " + EM + " Books of Account and Voucher "
                "Verification"),
        ("p", "The second week was the most clerical and, in retrospect, the "
         "most valuable. The intern classified and verified vouchers, posted "
         "receipts and payments, and scrutinised ledgers for "
         "misclassification. The central task was the reconciliation of the "
         "payment-gateway settlement statement with recorded collections."),
        ("p", "That reconciliation taught a lesson no textbook had conveyed. "
         "The gateway settles net of its commission and settles on a lag, so "
         "the gross fee recorded against an enrolment, the net amount "
         "credited to the bank and the date on which it is credited are three "
         "different things. Recognising revenue gross and the commission as "
         "an expense " + EM + " rather than recognising the net receipt as "
         "revenue " + EM + " is the correct treatment, and it matters: "
         "netting would understate both turnover and cost and would distort "
         "the profit-volume ratio computed in Chapter Five."),
        ("callout", "note", "A Practical Discovery",
         "Three unreconciled gateway items from the preceding quarter were "
         "identified during this exercise and were traced to a failed "
         "settlement that had been re-credited under a different reference. "
         "The point is not the amount, which was small, but the demonstration "
         "that reconciliation is a control and not a formality."),
        ("h3", "Deliverables"),
        ("bullets", [
            "A reconciliation statement between gateway settlements and "
            "recorded collections for the period under review.",
            "A schedule of unreconciled items with the reason for each.",
            "A note on the correct treatment of gateway commission, accepted "
            "by the accounts team.",
        ]),

        ("h2", "3.5  Week Three " + EM + " Working Capital and Receivables"),
        ("p", "The third week turned to working capital. The intern prepared "
         "an ageing analysis of trade receivables, maintained the follow-up "
         "register for institutional clients, computed debtor days and drew up "
         "a collection priority list."),
        ("p", "The ageing analysis produced the study's most important single "
         "finding. Because only the business-to-business line is sold on "
         "credit, the entire receivable balance of " +
         rs(fd.bs("Trade Receivables")[2]) + " lakh arises from revenue of "
         "about " + rs(34.90) + " lakh. The conventional debtor-days "
         "computation, which divides the receivable by total revenue, "
         "therefore reports a comfortable " +
         m(fd.ratio_set(2)["debtor_days"], 1) + " days and conceals a credit "
         "period on the credit-sold portion that is several times longer. "
         "This is developed in Section 6.6 and appears as Finding 4 in "
         "Chapter Nine."),
        ("h3", "Deliverables"),
        ("bullets", [
            "An ageing statement of trade receivables in the buckets "
            "reproduced as Table 4.7.",
            "A revised follow-up register with a defined escalation sequence.",
            "A computation of debtor days on both the conventional and the "
            "credit-sales basis, with a note explaining the difference.",
            "A collection priority list ranked by amount and age.",
        ]),

        ("h2", "3.6  Week Four " + EM + " Budgeting and Variance Analysis"),
        ("p", "The fourth week addressed budgeting. The intern built a "
         "cohort-wise cost sheet, compared budgeted against actual figures "
         "for each head, quantified the variances and attempted to separate "
         "the controllable from the uncontrollable."),
        ("p", "The exercise established that the organisation prepares a "
         "competent annual budget but reviews it against actuals only at the "
         "year end. Marketing and digital promotion had exceeded its "
         "provision by " + pc(abs(fd.budget_variance(fd.BUDGET[4])[1])) +
         " and direct programme cost by " +
         pc(abs(fd.budget_variance(fd.BUDGET[2])[1])) + ", while the "
         "favourable revenue variance of " +
         pc(fd.budget_variance(fd.BUDGET[0])[1]) + " had masked both. A "
         "monthly review would have surfaced the marketing overspend by the "
         "second quarter, when it could still have been corrected."),
        ("h3", "Deliverables"),
        ("bullets", [
            "A cohort-wise cost sheet showing contribution per intern.",
            "A budget-versus-actual variance statement, reproduced as "
            "Table 5.2.",
            "A draft format for a monthly variance report with a five per "
            "cent explanation threshold.",
        ]),

        ("h2", "3.7  Week Five " + EM + " Ratio Analysis and Interpretation"),
        ("p", "The fifth week was the analytical centre of the internship. "
         "Working from the three-year statements, the intern computed the "
         "liquidity, profitability, solvency and activity ratios set out in "
         "Chapter Six, prepared the trend charts and carried out the DuPont "
         "decomposition of return on equity."),
        ("p", "The DuPont exercise was the most instructive. Return on equity "
         "had risen from " + pc(fd.ratio_set(0)["roe"]) + " to " +
         pc(fd.ratio_set(2)["roe"]) + ", and the natural assumption was that "
         "leverage had contributed. Decomposition showed the opposite: the "
         "equity multiplier had <i>fallen</i> from " +
         m(fd.dupont(0)["equity_multiplier"]) + " to " +
         m(fd.dupont(2)["equity_multiplier"]) + ", so the entire improvement "
         "came from margin and asset turnover. The return had improved for "
         "the right reasons " + EM + " a conclusion that could not have been "
         "reached from the headline ratio alone."),
        ("h3", "Deliverables"),
        ("bullets", [
            "A three-year ratio schedule under four heads, reproduced as "
            "Tables 6.1 to 6.5.",
            "Common-size Statement of Profit and Loss and Balance Sheet.",
            "A DuPont decomposition for each of the three years.",
            "A cash flow statement under the indirect method, reconciled to "
            "the movement in cash.",
        ]),

        ("h2", "3.8  Week Six " + EM + " Cost Control and CVP Analysis"),
        ("p", "The sixth week applied cost accounting technique. Each expense "
         "head was examined and segregated into its fixed and variable "
         "components, from which the contribution, profit-volume ratio, "
         "break-even sales, margin of safety and the two leverages were "
         "derived."),
        ("p", "The segregation required judgement rather than arithmetic, and "
         "the marketing head illustrates why. Performance advertising scales "
         "directly with enrolment and is variable; brand-building and "
         "sponsorship do not and are committed. Discussion with management "
         "established a split of about fifty-five to forty-five, and the "
         "resulting break-even sales figure of " + rs(fd.bep_sales()) +
         " lakh is sensitive to that judgement. The sensitivity is stated "
         "openly in Section 5.6 and again among the limitations."),
        ("h3", "Deliverables"),
        ("bullets", [
            "A fixed-variable cost segregation statement, reproduced as "
            "Table 5.5.",
            "A cost-volume-profit analysis with break-even sales and margin "
            "of safety.",
            "A computation of operating, financial and combined leverage.",
            "A sensitivity note showing the effect on break-even sales of "
            "varying the marketing split by ten percentage points either way.",
        ]),

        ("h2", "3.9  Week Seven " + EM + " Compilation and Presentation"),
        ("p", "The final two days were spent consolidating the findings, "
         "drafting the suggestions of Chapter Nine and presenting the "
         "concluding summary to the company mentor. The mentor's principal "
         "criticism " + EM + " that an early draft recommended improvements "
         "without stating who would own them or how often they would be "
         "performed " + EM + " led to the reframing of every suggestion in "
         "Chapter Nine in terms of an owner, a frequency and a measurable "
         "trigger. It was the most useful correction received during the "
         "internship."),

        ("h2", "3.10  Skills Applied and Acquired"),
        _table("3.3", "Mapping of tasks to skills and to report chapters",
               [("Task", 0.30, "l"), ("Skill applied", 0.34, "l"),
                ("Feeds into", 0.36, "l")],
               [["Voucher classification and ledger scrutiny",
                 "Accounting fundamentals, attention to documentation",
                 "Section 2.6 " + EM + " the recording cycle"],
                ["Gateway reconciliation",
                 "Reconciliation technique, revenue recognition judgement",
                 "Section 4.2 " + EM + " revenue analysis"],
                ["Receivable ageing and follow-up",
                 "Working capital management, credit control",
                 "Sections 4.5 and 6.6 " + EM + " liquidity and activity"],
                ["Cohort cost sheet",
                 "Cost accounting, marginal costing",
                 "Sections 5.4 and 5.5 " + EM + " cost behaviour and CVP"],
                ["Budget-versus-actual comparison",
                 "Budgetary control, variance analysis",
                 "Section 5.3 " + EM + " variance analysis"],
                ["Ratio computation and DuPont",
                 "Financial statement analysis, interpretation",
                 "Chapter Six " + EM + " ratio analysis"],
                ["Cash flow construction",
                 "Indirect method, reconciliation discipline",
                 "Section 4.6 " + EM + " cash flow analysis"],
                ["Report drafting and presentation",
                 "Business writing, structuring of an argument",
                 "Chapters Nine and Ten"]],
               font_scale=0.92),
        ("pagebreak",),
    ]


# ============================================================ CHAPTER 4 ==
def chapter_four():
    cf = fd.cash_flow()
    r0, r1, r2 = fd.ratio_set(0), fd.ratio_set(1), fd.ratio_set(2)
    inc_rows = []
    for name in ["Revenue from Operations", "Other Income"]:
        inc_rows.append([name] + [m(v) for v in fd.pl(name)])
    inc_rows.append((["Total Income"] + [m(v) for v in fd.total_income()],
                     "total"))
    for name in fd.EXPENSE_HEADS:
        inc_rows.append([name] + [m(v) for v in fd.pl(name)])
    inc_rows.append((["Total Expenses"] + [m(v) for v in fd.total_expenses()],
                     "total"))
    inc_rows.append((["Profit Before Tax"] + [m(v) for v in fd.pbt()],
                     "total"))
    inc_rows.append(["Provision for Taxation"] + [m(v) for v in fd.tax()])
    inc_rows.append((["Profit After Tax"] + [m(v) for v in fd.pat()], "total"))

    cs_rows = []
    for name in ["Revenue from Operations"] + fd.EXPENSE_HEADS:
        cs_rows.append([name] + [m(100.0 * fd.pl(name)[i] / fd.revenue()[i])
                                 for i in range(3)])
    cs_rows.append((["Profit Before Tax"] +
                    [m(100.0 * fd.pbt()[i] / fd.revenue()[i])
                     for i in range(3)], "total"))

    return [
        ("chapter", "4", "FINANCIAL MANAGEMENT ANALYSIS",
         "An examination of how the organisation earns, spends, funds and "
         "converts its money: revenue structure, cost structure, "
         "profitability, working capital, cash flow and the pattern of "
         "financing."),
        ("lead", "Financial management asks four questions of any enterprise: "
         "where does the money come from, where does it go, how much of it "
         "stays, and does it actually arrive as cash. This chapter answers "
         "them in that order."),

        ("h2", "4.1  The Statement of Profit and Loss"),
        ("p", "The three-year Statement of Profit and Loss is set out below. "
         "It is the foundation for the whole of the remaining analysis, and "
         "every figure used elsewhere in this report is derived from it or "
         "from the Balance Sheet in Section 4.7."),
        _table("4.1", "Statement of Profit and Loss for three years (" + R +
               " in lakh)", _yr_cols("Particulars", 0.40), inc_rows,
               note="Indicative management figures compiled for academic "
                    "analysis. Provision for taxation is computed at " +
                    m(100 * fd.TAX_RATE, 0) + " per cent of profit before tax."),
        ("figure", "fig02_income_expense", "Total income against total "
         "expenditure and profit before tax",
         "Computed from Table 4.1."),

        ("h2", "4.2  Analysis of Revenue"),
        ("p", "Revenue from operations grew from " + rs(fd.revenue()[0]) +
         " lakh in " + Y[0] + " to " + rs(fd.revenue()[1]) + " lakh in " +
         Y[1] + " and " + rs(fd.revenue()[2]) + " lakh in " + Y[2] + " " + EM +
         " increases of " + pc(fd.growth(fd.revenue())[1], 1) + " and " +
         pc(fd.growth(fd.revenue())[2], 1) + " respectively. Growth has "
         "decelerated slightly in percentage terms, which is arithmetically "
         "inevitable on a rising base, but the absolute increment has widened "
         "from " + rs(fd.revenue()[1] - fd.revenue()[0]) + " lakh to " +
         rs(fd.revenue()[2] - fd.revenue()[1]) + " lakh."),
        ("h3", "4.2.1  Composition of Revenue"),
        ("p", "The five service lines contribute very unequally. Paid "
         "internship programmes at " + rs(112.80) + " lakh account for " +
         pc(100 * 112.80 / fd.revenue()[2]) + " of turnover; the remaining "
         "four together account for the balance. The concentration is a "
         "strength in that it reflects a proven core product, and a weakness "
         "in that a regulatory or competitive shock to that single line would "
         "affect more than half of revenue."),
        ("h3", "4.2.2  Seasonality"),
        ("p", "Revenue is materially seasonal. The first quarter, which "
         "coincides with the opening of the summer internship cycle, "
         "contributed " + rs(62.30) + " lakh, while the third quarter "
         "contributed only " + rs(41.20) + " lakh " + EM + " a difference of "
         "about " + pc(100 * (62.30 - 41.20) / 41.20, 0) + " between the peak "
         "and the trough. Since a substantial part of the cost base is "
         "committed and does not fall with revenue, the third quarter is the "
         "period of greatest financial strain. The absence of a formal cash "
         "budget for that quarter is noted as a finding in Chapter Nine."),
        ("figure", "fig06_seasonality", "Quarterly pattern of revenue, "
         "FY 2025-26",
         "Compiled from monthly collection statements."),
        _table("4.2", "Quarterly revenue and share of the year, FY 2025-26",
               [("Quarter", 0.28, "l"), ("Revenue (" + R + " L)", 0.24, "r"),
                ("Share of year", 0.24, "r"),
                ("Index (average = 100)", 0.24, "r")],
               [[q.replace("\n", " "), m(v),
                 m(100.0 * v / fd.revenue()[2]),
                 m(100.0 * v / (fd.revenue()[2] / 4.0), 0)]
                for q, v in fd.QUARTERLY] +
               [(["Total", m(fd.revenue()[2]), m(100.00), m(100, 0)],
                 "total")]),

        ("h2", "4.3  Analysis of Cost Structure"),
        ("p", "Total expenditure rose from " + rs(fd.total_expenses()[0]) +
         " lakh to " + rs(fd.total_expenses()[2]) + " lakh over the period, an "
         "increase of " + pc(100 * (fd.total_expenses()[2] -
                                    fd.total_expenses()[0]) /
                             fd.total_expenses()[0], 1) + ", against a "
         "revenue increase of " + pc(100 * (fd.revenue()[2] -
                                            fd.revenue()[0]) /
                                     fd.revenue()[0], 1) + ". That costs grew "
         "more slowly than revenue is the arithmetic source of the entire "
         "improvement in margin, and the reason is that a largely committed "
         "overhead base was spread over a much larger turnover."),
        ("figure", "fig04_cost_structure", "Structure of total expenditure, "
         "FY 2025-26",
         "Computed from Table 4.1."),
        ("h3", "4.3.1  Common-size Analysis"),
        ("p", "Expressing each head as a percentage of revenue separates a "
         "change in structure from a change in scale. The table below does "
         "this for all three years, and it is the most revealing single "
         "exhibit in the chapter."),
        _table("4.3", "Common-size Statement of Profit and Loss (percentage "
               "of revenue from operations)",
               _yr_cols("Particulars", 0.40), cs_rows,
               note="Read down each column to see structure; read across "
                    "each row to see the direction of change."),
        ("p", "Three movements in Table 4.3 deserve comment. Direct programme "
         "cost fell from " + m(100 * fd.pl("Direct Programme Cost")[0] /
                               fd.revenue()[0]) + " per cent of revenue to " +
         m(100 * fd.pl("Direct Programme Cost")[2] / fd.revenue()[2]) +
         " per cent, which indicates that content and assessment material is "
         "being reused across cohorts and that the marginal cost of an "
         "additional intern is falling. Employee benefit expenses fell from " +
         m(100 * fd.pl("Employee Benefit Expenses")[0] / fd.revenue()[0]) +
         " per cent to " + m(100 * fd.pl("Employee Benefit Expenses")[2] /
                             fd.revenue()[2]) + " per cent, the classic "
         "signature of operating leverage in a service business. Marketing, "
         "by contrast, has held almost constant at about " +
         m(100 * fd.pl("Marketing & Digital Promotion")[2] /
           fd.revenue()[2], 1) + " per cent of revenue, which means that "
         "revenue growth is still being bought rather than compounding from "
         "reputation and referral " + EM + " the single most important "
         "qualification to an otherwise favourable cost story."),
        ("figure", "fig05_expense_trend", "Behaviour of major expense heads "
         "over three years",
         "Computed from Table 4.1."),

        ("h2", "4.4  Profitability"),
        ("p", "Profitability has improved at every level of the statement, "
         "and the improvement is progressive rather than the result of a "
         "single favourable year."),
        _table("4.4", "Profitability summary (" + R + " in lakh and per cent)",
               _yr_cols("Particulars", 0.40),
               [["Gross Contribution"] + [m(v) for v in fd.contribution_gross()],
                ["Gross Contribution Margin (%)"] +
                [m(fd.ratio_set(i)["gross_margin"]) for i in range(3)],
                ["EBITDA"] + [m(v) for v in fd.ebitda()],
                ["EBITDA Margin (%)"] +
                [m(fd.ratio_set(i)["ebitda_margin"]) for i in range(3)],
                ["EBIT (Operating Profit)"] + [m(v) for v in fd.ebit()],
                ["Operating Margin (%)"] +
                [m(fd.ratio_set(i)["operating_margin"]) for i in range(3)],
                ["Profit Before Tax"] + [m(v) for v in fd.pbt()],
                (["Profit After Tax"] + [m(v) for v in fd.pat()], "total"),
                (["Net Profit Margin (%)"] +
                 [m(fd.ratio_set(i)["net_margin"]) for i in range(3)],
                 "total")],
               note="Gross contribution is revenue from operations less "
                    "direct programme cost. EBIT is inclusive of other income."),
        ("figure", "fig10_margins", "Profitability margins over three years",
         "Computed from Table 4.4."),
        ("p", "The gap between the gross contribution margin of " +
         pc(r2["gross_margin"]) + " and the net margin of " +
         pc(r2["net_margin"]) + " represents the overhead burden of the "
         "business. That gap has narrowed from " +
         m(r0["gross_margin"] - r0["net_margin"]) + " percentage points in " +
         Y[0] + " to " + m(r2["gross_margin"] - r2["net_margin"]) +
         " percentage points in " + Y[2] + ". A narrowing gap on a rising "
         "revenue is the clearest available evidence that the business model "
         "scales."),

        ("h2", "4.5  Working Capital Management"),
        ("p", "Working capital " + EM + " current assets less current "
         "liabilities " + EM + " rose from " + rs(fd.working_capital()[0]) +
         " lakh to " + rs(fd.working_capital()[2]) + " lakh. The composition "
         "of that working capital is unusual and favourable: there is no "
         "inventory at all, and cash constitutes the largest single current "
         "asset."),
        _table("4.5", "Composition of working capital (" + R + " in lakh)",
               _yr_cols("Particulars", 0.40),
               [(["Current Assets"] + ["", "", ""], "group")] +
               [[n] + [m(v) for v in fd.bs(n)] for n in fd.CURRENT_ASSET_HEADS] +
               [(["Total Current Assets"] + [m(v) for v in fd.current_assets()],
                 "total"),
                (["Current Liabilities"] + ["", "", ""], "group")] +
               [[n] + [m(v) for v in fd.bs(n)] for n in fd.CURRENT_LIAB_HEADS] +
               [(["Total Current Liabilities"] +
                 [m(v) for v in fd.current_liabilities()], "total"),
                (["Net Working Capital"] +
                 [m(v) for v in fd.working_capital()], "total")]),
        ("h3", "4.5.1  Trade Receivables"),
        ("p", "Trade receivables rose from " +
         rs(fd.bs("Trade Receivables")[0]) + " lakh to " +
         rs(fd.bs("Trade Receivables")[2]) + " lakh. On the conventional "
         "basis " + EM + " revenue divided by average receivables " + EM +
         " the debtors turnover ratio was " + m(r2["debtor_turnover"]) +
         " times and the collection period about " +
         m(r2["debtor_days"], 1) + " days, both marginally better than the "
         "preceding year."),
        ("callout", "warn", "The Debtor-Days Figure Understates the Real "
         "Credit Period",
         "Only the business-to-business service line is sold on credit. "
         "Measured against that line's revenue of about " + rs(34.90) +
         " lakh rather than against total turnover of " +
         rs(fd.revenue()[2]) + " lakh, the effective collection period on "
         "credit sales is of the order of " +
         m(365.0 * ((fd.bs("Trade Receivables")[1] +
                     fd.bs("Trade Receivables")[2]) / 2.0) / 34.90, 0) +
         " days rather than " + m(r2["debtor_days"], 1) + " days. The "
         "conventional ratio is not wrong, but it is the wrong ratio for this "
         "revenue mix, and relying on it would give false comfort."),
        _table("4.6", "Receivables and the collection period",
               [("Particulars", 0.46, "l"), (Y[1], 0.27, "r"),
                (Y[2], 0.27, "r")],
               [["Closing Trade Receivables (" + R + " L)",
                 m(fd.bs("Trade Receivables")[1]),
                 m(fd.bs("Trade Receivables")[2])],
                ["Average Trade Receivables (" + R + " L)",
                 m((fd.bs("Trade Receivables")[0] +
                    fd.bs("Trade Receivables")[1]) / 2.0),
                 m((fd.bs("Trade Receivables")[1] +
                    fd.bs("Trade Receivables")[2]) / 2.0)],
                ["Debtors Turnover (times)", m(r1["debtor_turnover"]),
                 m(r2["debtor_turnover"])],
                ["Collection Period on total revenue (days)",
                 m(r1["debtor_days"], 1), m(r2["debtor_days"], 1)],
                (["Collection Period on credit sales only (days)",
                  m(365.0 * ((fd.bs("Trade Receivables")[0] +
                              fd.bs("Trade Receivables")[1]) / 2.0) / 24.60, 0),
                  m(365.0 * ((fd.bs("Trade Receivables")[1] +
                              fd.bs("Trade Receivables")[2]) / 2.0) / 34.90, 0)],
                 "total")],
               note="Credit sales are taken as the business-to-business "
                    "service line only: " + R + " 24.60 lakh in " + Y[1] +
                    " and " + R + " 34.90 lakh in " + Y[2] + "."),
        ("h3", "4.5.2  Ageing of Receivables"),
        _table("4.7", "Ageing of trade receivables as at the close of " + Y[2],
               [("Age bucket", 0.30, "l"), ("Amount (" + R + " L)", 0.24, "r"),
                ("Share", 0.22, "r"), ("Assessment", 0.24, "l")],
               [["Not yet due", m(8.40), m(100 * 8.40 / 23.10), "Normal"],
                ["1 to 30 days overdue", m(6.10), m(100 * 6.10 / 23.10),
                 "Routine follow-up"],
                ["31 to 60 days overdue", m(4.20), m(100 * 4.20 / 23.10),
                 "Needs attention"],
                ["61 to 90 days overdue", m(2.60), m(100 * 2.60 / 23.10),
                 "Escalate"],
                ["Over 90 days overdue", m(1.80), m(100 * 1.80 / 23.10),
                 "Provision merited"],
                (["Total", m(23.10), m(100.00), ""], "total")],
               note="Compiled by the intern from the receivable ledger. "
                    "Amounts overdue by more than sixty days constitute " +
                    pc(100 * (2.60 + 1.80) / 23.10) + " of the balance."),
        ("h3", "4.5.3  The Operating Cycle"),
        ("p", "Because the organisation holds no inventory, its operating "
         "cycle consists only of the collection period less the credit period "
         "enjoyed from suppliers. Trade creditors were settled in about " +
         m(r2["creditor_days"], 1) + " days against a collection period of " +
         m(r2["debtor_days"], 1) + " days, producing a cash conversion cycle "
         "of about <b>" + m(r2["cash_cycle"], 1) + " days</b>. A negative "
         "cycle means that suppliers and mentors are, in effect, financing "
         "part of the working capital requirement. It is a genuine structural "
         "advantage, and it explains how the business has funded rapid growth "
         "without a proportionate increase in borrowing."),
        ("figure", "fig14_cycle", "Debtor days, creditor days and the cash "
         "conversion cycle",
         "Computed on average balances."),

        ("h2", "4.6  Cash Flow Analysis"),
        ("p", "Profit is an opinion; cash is a fact. The cash flow statement "
         "below was constructed under the indirect method from the two "
         "statements and reconciles exactly to the movement in cash balances, "
         "which is itself a check on the internal consistency of the figures "
         "analysed."),
        _table("4.8", "Cash Flow Statement for " + Y[2] + " (" + R +
               " in lakh)",
               [("Particulars", 0.62, "l"), ("Amount", 0.19, "r"),
                ("Total", 0.19, "r")],
               [(["A.  Cash Flow from Operating Activities", "", ""], "group"),
                ["Profit before tax", m(cf["pbt"]), ""],
                ["Add: Depreciation and amortisation", m(cf["dep"]), ""],
                ["Add: Finance cost", m(cf["fin"]), ""],
                ["Less: Other income", "(" + m(cf["other_income"]) + ")", ""],
                (["Operating profit before working capital changes",
                  m(cf["op_before_wc"]), ""], "total"),
                ["Increase in trade receivables", "(" + m(cf["d_rec"]) + ")",
                 ""],
                ["Increase in short-term loans and advances",
                 "(" + m(cf["d_adv"]) + ")", ""],
                ["Increase in other current assets",
                 "(" + m(cf["d_oca"]) + ")", ""],
                ["Increase in trade payables", m(cf["d_pay"]), ""],
                ["Increase in other current liabilities", m(cf["d_ocl"]), ""],
                (["Cash generated from operations", m(cf["cash_from_ops"]),
                  ""], "total"),
                ["Less: Income tax paid", "(" + m(cf["tax_paid"]) + ")", ""],
                (["Net cash from operating activities", "",
                  m(cf["net_op"])], "total"),
                (["B.  Cash Flow from Investing Activities", "", ""], "group"),
                ["Purchase of property, plant, equipment and intangibles",
                 "(" + m(cf["capex"]) + ")", ""],
                ["Purchase of non-current investments",
                 "(" + m(cf["d_inv"]) + ")", ""],
                ["Other income received", m(cf["other_income"]), ""],
                (["Net cash used in investing activities", "",
                  "(" + m(abs(cf["net_inv"])) + ")"], "total"),
                (["C.  Cash Flow from Financing Activities", "", ""], "group"),
                ["Repayment of long-term borrowings",
                 "(" + m(abs(cf["d_ltb"])) + ")", ""],
                ["Increase in short-term borrowings", m(cf["d_stb"]), ""],
                ["Finance cost paid", "(" + m(cf["fin"]) + ")", ""],
                (["Net cash used in financing activities", "",
                  "(" + m(abs(cf["net_fin"])) + ")"], "total"),
                (["Net increase in cash and cash equivalents (A+B+C)", "",
                  m(cf["net_change"])], "total"),
                ["Cash and bank balances at the beginning of the year", "",
                 m(cf["opening"])],
                (["Cash and bank balances at the end of the year", "",
                  m(cf["closing"])], "total")],
               font_scale=0.92,
               note="Prepared under the indirect method. The statement "
                    "reconciles to the movement in cash and bank balances on "
                    "the face of the Balance Sheet."),
        ("figure", "fig17_cash_bridge", "Cash flow bridge from opening to "
         "closing cash, FY 2025-26",
         "Derived from Table 4.8."),
        ("p", "Three conclusions follow from Table 4.8. First, net cash from "
         "operating activities of " + rs(cf["net_op"]) + " lakh exceeded "
         "profit after tax of " + rs(fd.pat()[2]) + " lakh, which means the "
         "reported profit is converting into cash and is not an artefact of "
         "accrual. Second, operating cash alone financed the entire capital "
         "programme of " + rs(cf["capex"]) + " lakh without recourse to fresh "
         "borrowing. Third, the company used the surplus to reduce long-term "
         "debt by " + rs(abs(cf["d_ltb"])) + " lakh and still increased its "
         "cash balance by " + rs(cf["net_change"]) + " lakh. This is the "
         "signature of a self-financing business."),

        ("h2", "4.7  The Balance Sheet and the Pattern of Financing"),
        _table("4.9", "Balance Sheet as at the close of each year (" + R +
               " in lakh)",
               _yr_cols("Particulars", 0.40),
               [(["I.  EQUITY AND LIABILITIES", "", "", ""], "group")] +
               [[n] + [m(v) for v in fd.bs(n)] for n, *_x in fd.EQUITY_LIAB] +
               [(["Total", ] + [m(v) for v in fd.balance_total()], "total"),
                (["II.  ASSETS", "", "", ""], "group")] +
               [[n] + [m(v) for v in fd.bs(n)] for n, *_x in fd.ASSETS] +
               [(["Total"] + [m(v) for v in fd.assets_total()], "total")],
               font_scale=0.94),
        ("p", "The pattern of financing has changed decisively. In " + Y[0] +
         " shareholders' funds of " + rs(fd.shareholders_funds()[0]) +
         " lakh were only marginally larger than total debt of " +
         rs(fd.total_debt()[0]) + " lakh. By " + Y[2] + " shareholders' funds "
         "had reached " + rs(fd.shareholders_funds()[2]) + " lakh against debt "
         "of " + rs(fd.total_debt()[2]) + " lakh. Almost the whole of the "
         "increase in net worth is retained profit rather than fresh capital: "
         "share capital has remained unchanged at " +
         rs(fd.bs("Share Capital")[2]) + " lakh throughout, while reserves "
         "have grown from " + rs(fd.bs("Reserves & Surplus")[0]) + " lakh to " +
         rs(fd.bs("Reserves & Surplus")[2]) + " lakh."),
        ("figure", "fig20_funding", "Pattern of long-term funding over three "
         "years",
         "Computed from Table 4.9."),
        ("p", "For a young enterprise this is an unusually conservative "
         "financing policy, and it carries a cost as well as a benefit. The "
         "benefit is resilience: interest cover of " +
         m(r2["interest_cover"]) + " times and a debt-equity ratio of " +
         m(r2["debt_equity"]) + " leave the company well placed to absorb a "
         "poor season. The cost is foregone growth: with a return on capital "
         "employed of " + pc(r2["roce"]) + " against a borrowing cost "
         "materially below that figure, the company is not exploiting the "
         "favourable financial leverage available to it. Section 5.7 "
         "quantifies this, and Chapter Nine frames it as a matter for "
         "management judgement rather than as a defect."),
        ("pagebreak",),
    ]



# ============================================================ CHAPTER 5 ==
def chapter_five():
    bt = fd.budget_totals()
    dol, ebit_op = fd.operating_leverage()
    fl = fd.financial_leverage()

    var_rows = []
    for row in fd.BUDGET:
        head, bud, act, lower_good = row
        amt, pct = fd.budget_variance(row)
        var_rows.append([head, m(bud), m(act),
                         ("+" if amt >= 0 else EM + " ") + m(abs(amt)),
                         ("+" if pct >= 0 else EM + " ") + m(abs(pct)),
                         "Favourable" if amt >= 0 else "Adverse"])
    var_rows.append((["Total Income", m(bt["budget_income"]),
                      m(bt["actual_income"]),
                      "+" + m(bt["actual_income"] - bt["budget_income"]),
                      "+" + m(100 * (bt["actual_income"] -
                                     bt["budget_income"]) /
                              bt["budget_income"]), "Favourable"], "total"))
    var_rows.append((["Total Expenditure", m(bt["budget_expense"]),
                      m(bt["actual_expense"]),
                      EM + " " + m(bt["actual_expense"] - bt["budget_expense"]),
                      EM + " " + m(100 * (bt["actual_expense"] -
                                          bt["budget_expense"]) /
                                   bt["budget_expense"]), "Adverse"], "total"))
    var_rows.append((["Profit Before Tax", m(bt["budget_pbt"]),
                      m(bt["actual_pbt"]),
                      "+" + m(bt["actual_pbt"] - bt["budget_pbt"]),
                      "+" + m(100 * (bt["actual_pbt"] - bt["budget_pbt"]) /
                              bt["budget_pbt"]), "Favourable"], "total"))

    split_rows = []
    for head, var, fix in fd.COST_SPLIT:
        total = var + fix
        split_rows.append([head, m(total), m(var), m(fix),
                           m(100.0 * var / total) if total else m(0)])
    split_rows.append((["Total", m(fd.total_expenses()[2]),
                        m(fd.variable_cost()), m(fd.fixed_cost()),
                        m(100.0 * fd.variable_cost() /
                          fd.total_expenses()[2])], "total"))

    return [
        ("chapter", "5", "BUDGETING AND COST CONTROL",
         "The budget cycle in operation, a quantified variance analysis, the "
         "behaviour of costs, break-even analysis and the leverage the "
         "organisation carries."),
        ("lead", "A budget that is prepared but not monitored is a "
         "forecast, not a control. This chapter tests which of the two the "
         "organisation actually has."),

        ("h2", "5.1  The Budgeting Process in Operation"),
        ("p", "The organisation prepares an annual budget before the "
         "commencement of the financial year. The process observed during the "
         "internship runs as follows."),
        ("numbers", [
            "<b>Revenue projection.</b> The Admissions and Corporate "
            "Relations functions jointly project enrolments by service line, "
            "based on the previous year's conversions and the contracts "
            "expected to be signed.",
            "<b>Variable cost estimation.</b> Programme Delivery estimates "
            "mentor honoraria, content and certification cost per intern and "
            "applies it to projected enrolment.",
            "<b>Committed cost estimation.</b> Finance estimates salaries, "
            "incubation charges, platform subscriptions and statutory costs, "
            "which are largely known in advance.",
            "<b>Marketing provision.</b> A marketing budget is fixed as an "
            "approximate percentage of projected revenue " + EM + " an "
            "approach that, as Section 5.3 shows, is the weakest link in the "
            "chain.",
            "<b>Consolidation and approval.</b> Finance consolidates the "
            "heads into a master budget, which management reviews and "
            "approves.",
            "<b>Monitoring.</b> Revenue and collections are monitored "
            "monthly. A full head-wise comparison of budget against actual "
            "is, however, prepared only at the year end.",
        ]),
        ("callout", "warn", "The Central Weakness in the Budgetary Control "
         "System",
         "Steps one to five are performed competently. Step six is not. "
         "Because the head-wise comparison is annual, an adverse variance "
         "cannot be corrected in the year in which it arises " + EM + " it "
         "can only be explained after that year has closed. Budgeting without "
         "monthly monitoring is forecasting, and this is the single most "
         "consequential finding of the study."),

        ("h2", "5.2  Types of Budget Maintained"),
        _table("5.1", "Budgets prepared and their status",
               [("Budget", 0.26, "l"), ("Purpose", 0.42, "l"),
                ("Frequency", 0.16, "c"), ("Status", 0.16, "c")],
               [["Revenue budget", "Projection of income by service line",
                 "Annual", "Prepared"],
                ["Programme cost budget",
                 "Variable cost of delivery per cohort", "Per cohort",
                 "Prepared"],
                ["Marketing budget", "Provision for promotion and lead "
                 "generation", "Annual", "Prepared"],
                ["Overhead budget", "Salaries, incubation, platform and "
                 "administration", "Annual", "Prepared"],
                ["Capital expenditure budget", "Equipment and platform "
                 "development", "Annual", "Prepared"],
                ["Cash budget", "Month-wise projection of receipts and "
                 "payments", "Monthly", "Not prepared"],
                ["Flexible budget", "Cost allowance restated to actual "
                 "activity", EM, "Not prepared"],
                ["Master budget", "Consolidated budgeted profit statement",
                 "Annual", "Prepared"]],
               note="The two budgets not prepared are precisely the two that "
                    "a seasonal business most needs, and both are recommended "
                    "in Chapter Nine."),

        ("h2", "5.3  Budget against Actual: Variance Analysis"),
        ("p", "The table below compares the approved budget for " + Y[2] +
         " with the actual outcome. Variances are signed so that a favourable "
         "outcome is always positive: for revenue, an excess over budget is "
         "favourable; for a cost head, a saving against budget is favourable."),
        _table("5.2", "Budget against actual for " + Y[2] + " (" + R +
               " in lakh)",
               [("Head", 0.30, "l"), ("Budget", 0.13, "r"),
                ("Actual", 0.13, "r"), ("Variance", 0.14, "r"),
                ("Variance %", 0.14, "r"), ("Nature", 0.16, "c")],
               var_rows, font_scale=0.91,
               note="Variance percentages are computed on the budgeted "
                    "figure. Depreciation was exactly on budget."),
        ("figure", "fig07_budget_variance", "Budget against actual: "
         "percentage variance by head, FY 2025-26",
         "Computed from Table 5.2."),
        ("h3", "5.3.1  Interpretation of the Principal Variances"),
        ("defs", [
            ("Revenue " + EM + " favourable " +
             pc(fd.budget_variance(fd.BUDGET[0])[1]),
             "Actual revenue of " + rs(fd.revenue()[2]) + " lakh exceeded the "
             "budget of " + rs(205.00) + " lakh. Enquiry to enrolment "
             "conversion improved and two institutional contracts were signed "
             "ahead of schedule. This is a genuinely favourable outcome, but "
             "it also masked the cost overruns below, which is precisely the "
             "danger of reviewing only the bottom line."),
            ("Marketing " + EM + " adverse " +
             pc(abs(fd.budget_variance(fd.BUDGET[4])[1])),
             "The largest adverse variance in percentage terms. Spend of " +
             rs(33.10) + " lakh against a provision of " + rs(30.00) +
             " lakh. Management attributed the excess to competitive bidding "
             "on digital advertising during the peak season. Because the "
             "budget was set as a percentage of projected revenue rather than "
             "on a cost-per-enrolment basis, there was no mechanism to "
             "determine whether the additional " + rs(3.10) + " lakh bought "
             "proportionate enrolment. It may have been money well spent; the "
             "system cannot tell."),
            ("Direct Programme Cost " + EM + " adverse " +
             pc(abs(fd.budget_variance(fd.BUDGET[2])[1])),
             "Spend of " + rs(79.30) + " lakh against " + rs(76.00) + " lakh. "
             "This variance is largely a consequence of the favourable revenue "
             "variance: more interns were enrolled than budgeted, and a "
             "variable cost must rise with volume. Judged against a flexible "
             "budget restated to actual enrolment, most of this variance "
             "would disappear, which is exactly why Section 5.8 recommends "
             "flexible budgeting."),
            ("Employee Benefits " + EM + " favourable " +
             pc(fd.budget_variance(fd.BUDGET[3])[1]),
             "Spend of " + rs(52.80) + " lakh against " + rs(54.00) + " lakh, "
             "because two budgeted positions were filled later in the year "
             "than planned. This is a timing saving rather than an efficiency "
             "gain and should not be expected to recur."),
            ("Administration " + EM + " favourable " +
             pc(fd.budget_variance(fd.BUDGET[5])[1]),
             "Spend of " + rs(13.60) + " lakh against " + rs(14.50) + " lakh, "
             "reflecting continued containment of occupancy cost through the "
             "incubation arrangement and a shift of printed material to "
             "digital delivery."),
            ("Finance Cost " + EM + " favourable " +
             pc(fd.budget_variance(fd.BUDGET[7])[1]),
             "Spend of " + rs(1.60) + " lakh against " + rs(1.80) + " lakh, "
             "because scheduled repayment of term debt reduced the average "
             "outstanding balance faster than the budget assumed."),
        ]),
        ("figure", "fig08_budget_amounts", "Budgeted and actual amounts by "
         "head, FY 2025-26",
         "Computed from Table 5.2."),
        ("p", "Read as a whole, Table 5.2 tells a story that the profit "
         "figure alone conceals. Profit before tax exceeded budget by " +
         pc(100 * (bt["actual_pbt"] - bt["budget_pbt"]) / bt["budget_pbt"]) +
         ", which on its face is an excellent result. But the favourable "
         "outcome was produced by revenue exceeding target, while three cost "
         "heads simultaneously exceeded theirs. Had revenue merely met "
         "budget, the cost overruns of " +
         rs(3.30 + 3.10 + 0.40) + " lakh would have reduced profit before tax "
         "by roughly a third. Good fortune on the top line is not a "
         "substitute for control on the cost lines."),

        ("h2", "5.4  Cost Classification and Behaviour"),
        ("p", "Cost control begins with cost classification, because only a "
         "cost whose behaviour is understood can be controlled. Each expense "
         "head was examined and allocated between its variable and fixed "
         "components on the basis of observed behaviour and discussion with "
         "management."),
        _table("5.3", "Classification of costs by behaviour",
               [("Head", 0.26, "l"), ("Behaviour", 0.18, "c"),
                ("Basis of classification", 0.56, "l")],
               [["Direct Programme Cost", "Wholly variable",
                 "Mentor honoraria, assessment and certification are incurred "
                 "per intern enrolled and cease if a cohort is not run"],
                ["Employee Benefit Expenses", "Wholly fixed",
                 "Core salaried team engaged irrespective of enrolment in any "
                 "particular month"],
                ["Marketing & Digital Promotion", "Semi-variable",
                 "Performance advertising scales with enrolment; brand and "
                 "sponsorship spend is committed"],
                ["Administrative & Office Expenses", "Semi-variable",
                 "Payment gateway charges, courier and printing scale with "
                 "volume; incubation charges and utilities do not"],
                ["Technology & Platform Expenses", "Wholly fixed",
                 "Annual platform and software subscriptions are independent "
                 "of the number of users within the licensed band"],
                ["Finance Cost", "Wholly fixed",
                 "Interest on term debt follows the repayment schedule, not "
                 "activity"],
                ["Depreciation & Amortisation", "Wholly fixed",
                 "Charged on a time basis on assets already in use"]],
               font_scale=0.93),
        _table("5.4", "Segregation of costs into variable and fixed for " +
               Y[2] + " (" + R + " in lakh)",
               [("Head", 0.32, "l"), ("Total", 0.15, "r"),
                ("Variable", 0.15, "r"), ("Fixed", 0.15, "r"),
                ("Variable %", 0.23, "r")], split_rows,
               note="The split of the two semi-variable heads rests on "
                    "management's assessment of the behaviour of each "
                    "component and is the principal judgemental input to the "
                    "break-even analysis that follows."),
        ("figure", "fig16_cost_behaviour", "Segregation of costs into "
         "variable and fixed, FY 2025-26",
         "Computed from Table 5.4."),

        ("h2", "5.5  Cost-Volume-Profit Analysis"),
        ("p", "With costs segregated, the marginal costing relationships "
         "follow directly. Contribution is revenue less variable cost; the "
         "profit-volume ratio expresses contribution as a percentage of "
         "revenue; break-even sales is the level of revenue at which "
         "contribution exactly absorbs fixed cost."),
        _table("5.5", "Cost-volume-profit computation for " + Y[2],
               [("Particulars", 0.56, "l"), ("Amount", 0.24, "r"),
                ("Unit", 0.20, "c")],
               [["Revenue from Operations", m(fd.revenue()[2]), R + " lakh"],
                ["Less: Variable Cost", m(fd.variable_cost()), R + " lakh"],
                (["Contribution", m(fd.contribution()), R + " lakh"], "total"),
                ["Less: Fixed Cost", m(fd.fixed_cost()), R + " lakh"],
                ["Add: Other Income", m(fd.other_income()[2]), R + " lakh"],
                (["Profit Before Tax", m(fd.pbt()[2]), R + " lakh"], "total"),
                ["Profit-Volume Ratio", m(fd.pv_ratio()), "per cent"],
                (["Break-Even Sales", m(fd.bep_sales()), R + " lakh"],
                 "total"),
                ["Margin of Safety", m(fd.margin_of_safety()), R + " lakh"],
                ["Margin of Safety Ratio", m(fd.mos_ratio()), "per cent"],
                ["Break-Even as a share of actual sales",
                 m(100.0 * fd.bep_sales() / fd.revenue()[2]), "per cent"]],
               note="Contribution less fixed cost plus other income equals "
                    "profit before tax, which reconciles the analysis to "
                    "Table 4.1."),
        ("figure", "fig15_breakeven", "Cost-volume-profit chart showing "
         "break-even sales and the margin of safety",
         "Computed from Table 5.5."),
        ("h3", "5.5.1  Interpretation"),
        ("p", "A profit-volume ratio of " + pc(fd.pv_ratio()) + " means that "
         "roughly fifty-three paise in every rupee of additional revenue "
         "falls through to contribution. That is a high ratio, characteristic "
         "of a service business with no material cost, and it is the "
         "arithmetic reason why profit grows so much faster than revenue."),
        ("p", "Break-even sales of " + rs(fd.bep_sales()) + " lakh against "
         "actual sales of " + rs(fd.revenue()[2]) + " lakh leave a margin of "
         "safety of " + rs(fd.margin_of_safety()) + " lakh, or " +
         pc(fd.mos_ratio()) + " of turnover. The interpretation is direct: "
         "revenue could fall by about " + m(fd.mos_ratio(), 0) + " per cent "
         "before the company began to make a loss. For a business in its "
         "growth phase this is a reasonable but not generous cushion, and it "
         "is worth noting what it implies about the seasonality identified in "
         "Section 4.2. Annualised, the third quarter's revenue of " +
         rs(41.20) + " lakh represents a run rate of " + rs(41.20 * 4) +
         " lakh " + EM + " below break-even. The company is loss-making in "
         "its lean quarter and recovers over the year, which is exactly why a "
         "quarterly cash budget matters more than an annual profit budget."),
        ("callout", "note", "Sensitivity of the Break-Even Point",
         "Because the marketing split is judgemental, the break-even figure "
         "should be treated as a range rather than a point. If performance "
         "advertising were taken as sixty-five per cent variable instead of "
         "fifty-five, fixed cost would fall to about " + rs(90.08) + " lakh "
         "and break-even sales to roughly " + rs(163.5, 1) + " lakh. If it "
         "were taken as forty-five per cent, fixed cost would rise to about " +
         rs(96.70) + " lakh and break-even sales to roughly " + rs(184.2, 1) +
         " lakh. The conclusion " + EM + " that the company operates "
         "comfortably above break-even but is below it in the third quarter " +
         EM + " holds across that entire range."),

        ("h2", "5.6  Cost Control Measures in Place"),
        ("p", "The organisation exercises real cost control, and it would be "
         "wrong to read Section 5.3 as suggesting otherwise. The measures "
         "observed during the internship are set out below, each with the "
         "financial evidence of its effect."),
        _table("5.6", "Cost control measures and their observed effect",
               [("Measure", 0.30, "l"), ("How it operates", 0.36, "l"),
                ("Evidence of effect", 0.34, "l")],
               [["Incubation rather than commercial premises",
                 "Occupancy at B-Hub at concessional charges",
                 "Administrative expenses held to " +
                 m(100 * fd.pl("Administrative & Office Expenses")[2] /
                   fd.revenue()[2], 1) + " per cent of revenue"],
                ["Variable mentor engagement",
                 "Mentors engaged per cohort on honorarium rather than on "
                 "salary",
                 "Direct programme cost remains wholly variable, protecting "
                 "the break-even point"],
                ["Reuse of content across cohorts",
                 "Assessment material and modules amortised over successive "
                 "batches",
                 "Direct programme cost fell from " +
                 m(100 * fd.pl("Direct Programme Cost")[0] /
                   fd.revenue()[0], 1) + " to " +
                 m(100 * fd.pl("Direct Programme Cost")[2] /
                   fd.revenue()[2], 1) + " per cent of revenue"],
                ["Digital-first delivery",
                 "Online mentoring and e-certificates in place of print and "
                 "travel",
                 "Contributed to the favourable administration variance of " +
                 pc(fd.budget_variance(fd.BUDGET[5])[1])],
                ["Voucher-based approval limits",
                 "Expenditure above a delegated threshold requires management "
                 "approval",
                 "No unauthorised expenditure identified during voucher "
                 "verification"],
                ["Scheduled debt reduction",
                 "Term debt repaid on schedule rather than rolled over",
                 "Finance cost favourable by " +
                 pc(fd.budget_variance(fd.BUDGET[7])[1]) +
                 "; interest cover now " +
                 m(fd.ratio_set(2)["interest_cover"]) + " times"]],
               font_scale=0.90),

        ("h2", "5.7  Operating and Financial Leverage"),
        ("p", "Leverage measures how sharply profit responds to a change in "
         "sales. Operating leverage arises from fixed operating cost; "
         "financial leverage from fixed financial cost. Their product, "
         "combined leverage, measures the total sensitivity of earnings to a "
         "movement in revenue."),
        _table("5.7", "Leverage computation for " + Y[2],
               [("Particulars", 0.56, "l"), ("Amount", 0.24, "r"),
                ("Unit", 0.20, "c")],
               [["Contribution", m(fd.contribution()), R + " lakh"],
                ["Operating Profit before other income", m(ebit_op),
                 R + " lakh"],
                ["Finance Cost", m(fd.pl("Finance Cost")[2]), R + " lakh"],
                ["Earnings before tax, excluding other income",
                 m(ebit_op - fd.pl("Finance Cost")[2]), R + " lakh"],
                (["Degree of Operating Leverage", m(dol), "times"], "total"),
                (["Degree of Financial Leverage", m(fl), "times"], "total"),
                (["Degree of Combined Leverage", m(dol * fl), "times"],
                 "total")]),
        ("p", "A degree of operating leverage of " + m(dol) + " times means "
         "that a one per cent change in sales produces approximately a " +
         m(dol) + " per cent change in operating profit. This cuts both ways "
         "and is the quantitative expression of the seasonality risk: in a "
         "quarter when revenue falls by twenty per cent, operating profit "
         "falls by approximately " + m(dol * 20, 0) + " per cent."),
        ("p", "Financial leverage of only " + m(fl) + " times reflects the "
         "modest borrowing already noted. The company therefore carries high "
         "operating risk and low financial risk " + EM + " an appropriate "
         "combination, since a business with volatile revenue should not "
         "compound operating volatility with fixed financial obligations. "
         "This is the strongest argument in favour of the conservative "
         "financing policy questioned in Section 4.7, and the two passages "
         "should be read together."),

        ("h2", "5.8  Appraisal of the Budgetary Control System"),
        _table("5.8", "Appraisal of the budgetary control system",
               [("Element", 0.28, "l"), ("Assessment", 0.14, "c"),
                ("Observation", 0.58, "l")],
               [["Budget preparation", "Adequate",
                 "Prepared before the year begins, with participation from "
                 "the functions that own the numbers"],
                ["Basis of revenue projection", "Adequate",
                 "Built from conversion history and the contract pipeline "
                 "rather than from an arbitrary growth rate"],
                ["Basis of marketing provision", "Weak",
                 "Set as a percentage of projected revenue, which cannot "
                 "reveal whether the spend is efficient"],
                ["Frequency of review", "Weak",
                 "Head-wise comparison performed annually; adverse variances "
                 "surface only after the year has closed"],
                ["Flexible budgeting", "Absent",
                 "Variances are not restated to actual activity, so volume "
                 "effects and efficiency effects cannot be separated"],
                ["Cash budgeting", "Absent",
                 "No month-wise projection of receipts and payments, despite "
                 "pronounced seasonality"],
                ["Responsibility accounting", "Partial",
                 "Heads are monitored, but no individual is formally "
                 "accountable for a named variance"],
                ["Corrective action", "Weak",
                 "Follows the annual review, by which time the period is "
                 "closed"]],
               font_scale=0.93,
               note="Each element assessed as weak or absent is addressed by "
                    "a specific recommendation in Chapter Nine."),
        ("pagebreak",),
    ]


# ============================================================ CHAPTER 6 ==
def chapter_six():
    r = [fd.ratio_set(i) for i in range(3)]

    def rr(label, key, unit="", dec=2, benchmark=""):
        return [label] + [m(r[i][key], dec) for i in range(3)] + [benchmark]

    liq_cols = [("Ratio", 0.34, "l")] + [(y, 0.15, "r") for y in Y] + \
               [("Benchmark", 0.21, "c")]

    cs_bs_rows = []
    for name, *_v in fd.EQUITY_LIAB:
        cs_bs_rows.append([name] + [m(100.0 * fd.bs(name)[i] /
                                      fd.balance_total()[i]) for i in range(3)])
    cs_bs_rows.append((["Total", m(100.0), m(100.0), m(100.0)], "total"))
    for name, *_v in fd.ASSETS:
        cs_bs_rows.append([name] + [m(100.0 * fd.bs(name)[i] /
                                      fd.assets_total()[i]) for i in range(3)])
    cs_bs_rows.append((["Total", m(100.0), m(100.0), m(100.0)], "total"))

    return [
        ("chapter", "6", "RATIO AND FINANCIAL ANALYSIS",
         "Liquidity, profitability, solvency and activity ratios for three "
         "years, common-size statements and a DuPont decomposition of the "
         "return on equity."),
        ("lead", "A ratio is not an answer. It is a question phrased "
         "precisely enough to be worth asking, and its value lies entirely in "
         "the comparison it invites."),

        ("h2", "6.1  Framework and Basis of Computation"),
        ("p", "Ratios have been computed under four conventional heads. "
         "Before the figures are presented, three matters of basis should be "
         "recorded, because a ratio computed on an undisclosed basis is not "
         "capable of being verified."),
        ("numbers", [
            "<b>Closing versus average balances.</b> Liquidity and solvency "
            "ratios are computed on closing balance sheet figures. Activity "
            "ratios involving receivables and payables are computed on "
            "average balances, since a turnover ratio compares a flow over a "
            "year with a stock that varied during it.",
            "<b>Return ratios.</b> Return on equity and return on capital "
            "employed are computed on closing figures. In a business growing "
            "as fast as this one, that understates the true return, because "
            "the closing capital base is considerably larger than the base "
            "that actually generated the year's profit. The bias is "
            "conservative, and it is noted again where it matters.",
            "<b>Benchmarks.</b> The benchmarks quoted are conventional rules "
            "of thumb drawn from the standard texts listed in the "
            "bibliography. They are <i>not</i> industry averages for "
            "structured internship providers, for which reliable published "
            "data does not exist in India. They should be read as a starting "
            "point for interpretation, not as a standard of compliance.",
        ]),
        ("figure", "fig19_scorecard", "Financial scorecard at a glance, "
         "FY 2025-26",
         "Benchmarks are conventional rules of thumb."),

        ("h2", "6.2  Liquidity Ratios"),
        _table("6.1", "Liquidity ratios", liq_cols,
               [rr("Current Ratio (times)", "current", benchmark="2.00 : 1"),
                rr("Quick Ratio (times)", "quick", benchmark="1.00 : 1"),
                rr("Absolute Cash Ratio (times)", "cash",
                   benchmark="0.50 : 1"),
                ["Working Capital (" + R + " L)"] +
                [m(v) for v in fd.working_capital()] + [EM],
                ["Current Assets (" + R + " L)"] +
                [m(v) for v in fd.current_assets()] + [EM],
                ["Current Liabilities (" + R + " L)"] +
                [m(v) for v in fd.current_liabilities()] + [EM]],
               note="Computed on closing balances. There is no inventory, so "
                    "the current and quick ratios differ only by prepaid and "
                    "other current assets."),
        ("figure", "fig09_liquidity", "Liquidity ratios over three years",
         "Computed from Table 6.1."),
        ("p", "The current ratio improved from " + m(r[0]["current"]) +
         " to " + m(r[2]["current"]) + ", dipping in " + Y[1] + " to " +
         m(r[1]["current"]) + " as trade payables grew faster than current "
         "assets. At " + m(r[2]["current"]) + ":1 it remains below the "
         "conventional 2:1 benchmark, and a mechanical reading would call "
         "this a weakness."),
        ("p", "Such a reading would be mistaken, for two reasons. First, the "
         "2:1 convention was devised for manufacturing and trading concerns "
         "whose current assets are dominated by inventory " + EM + " an asset "
         "that may not realise its book value quickly. This company holds no "
         "inventory whatsoever; its current assets are cash and receivables, "
         "both of which are far closer to money than stock is. Second, a "
         "substantial part of its current liabilities consists of fees "
         "collected in advance, which will be discharged by delivering a "
         "service rather than by paying out cash. Judged on the quick ratio "
         "of " + m(r[2]["quick"]) + " against a 1:1 benchmark, and on an "
         "absolute cash ratio of " + m(r[2]["cash"]) + " against a 0.5:1 "
         "benchmark, liquidity is in fact comfortable."),

        ("h2", "6.3  Profitability Ratios"),
        _table("6.2", "Profitability ratios (per cent)", liq_cols,
               [rr("Gross Contribution Margin", "gross_margin",
                   benchmark="Higher is better"),
                rr("EBITDA Margin", "ebitda_margin", benchmark="10.00"),
                rr("Operating Margin", "operating_margin", benchmark="10.00"),
                rr("Net Profit Margin", "net_margin", benchmark="5.00"),
                rr("Return on Equity", "roe", benchmark="15.00"),
                rr("Return on Capital Employed", "roce", benchmark="15.00"),
                rr("Return on Total Assets", "rota", benchmark="10.00")],
               note="Return ratios computed on closing figures and therefore "
                    "understated in a period of rapid growth."),
        ("figure", "fig11_returns", "Return on equity, capital employed and "
         "total assets",
         "Computed from Table 6.2."),
        ("p", "Every profitability measure has improved in each successive "
         "year, which is a stronger result than a single large improvement "
         "would be. The net profit margin rose from " +
         pc(r[0]["net_margin"]) + " to " + pc(r[2]["net_margin"]) +
         ", crossing the five per cent benchmark in " + Y[1] + ". Return on "
         "capital employed of " + pc(r[2]["roce"]) + " is exceptional and "
         "reflects the asset-light structure of the business: the company "
         "employs very little capital, so a modest absolute profit produces a "
         "high percentage return. Return on equity of " + pc(r[2]["roe"]) +
         " must be read in the light of the closing-balance basis noted in "
         "Section 6.1; on average equity it would be materially higher still."),

        ("h2", "6.4  Solvency Ratios"),
        _table("6.3", "Solvency and capital structure ratios", liq_cols,
               [rr("Debt-Equity Ratio (times)", "debt_equity",
                   benchmark="2.00 : 1 maximum"),
                rr("Interest Coverage (times)", "interest_cover",
                   benchmark="3.00 minimum"),
                rr("Proprietary Ratio (per cent)", "proprietary",
                   benchmark="50.00 minimum"),
                ["Total Debt (" + R + " L)"] +
                [m(v) for v in fd.total_debt()] + [EM],
                ["Shareholders' Funds (" + R + " L)"] +
                [m(v) for v in fd.shareholders_funds()] + [EM],
                ["Capital Employed (" + R + " L)"] +
                [m(v) for v in fd.capital_employed()] + [EM]]),
        ("figure", "fig12_solvency", "Debt-equity ratio and interest coverage",
         "Computed from Table 6.3."),
        ("p", "Solvency has strengthened on every measure. The debt-equity "
         "ratio fell from " + m(r[0]["debt_equity"]) + " to " +
         m(r[2]["debt_equity"]) + ", interest coverage rose from " +
         m(r[0]["interest_cover"]) + " times to " +
         m(r[2]["interest_cover"]) + " times, and the proprietary ratio "
         "crossed the fifty per cent mark in " + Y[2] + ", reaching " +
         pc(r[2]["proprietary"]) + ". More than half the assets of the "
         "business are now financed by its owners."),
        ("p", "It is worth being explicit about the trade-off this "
         "represents, because a falling debt-equity ratio is not "
         "automatically a virtue. With a return on capital employed of " +
         pc(r[2]["roce"]) + " and a borrowing cost far below that figure, "
         "every rupee of prudent debt would raise the return on equity. That "
         "the company has chosen not to take it is defensible given the "
         "operating leverage of " + m(fd.operating_leverage()[0]) +
         " times computed in Section 5.7 " + EM + " a business with volatile "
         "revenue is right to keep its fixed financial obligations low " +
         EM + " but it is a choice, and management should make it "
         "deliberately rather than by default."),

        ("h2", "6.5  Activity and Efficiency Ratios"),
        _table("6.4", "Activity ratios", liq_cols,
               [rr("Total Asset Turnover (times)", "total_asset_turnover",
                   benchmark="Higher is better"),
                rr("Fixed Asset Turnover (times)", "fixed_asset_turnover",
                   benchmark="Higher is better"),
                rr("Working Capital Turnover (times)", "wc_turnover",
                   benchmark="Higher is better")],
               note="Working capital turnover is unusually high because the "
                    "business carries no inventory."),
        ("figure", "fig13_turnover", "Activity ratios: asset utilisation",
         "Computed from Table 6.4."),
        ("p", "Fixed asset turnover of " +
         m(r[2]["fixed_asset_turnover"]) + " times is the number that best "
         "captures what kind of business this is. Every rupee invested in "
         "property, plant, equipment and software generates almost eleven "
         "rupees of revenue. Growth therefore requires very little capital "
         "expenditure, which is why the company has been able to expand "
         "revenue by " + pc(100 * (fd.revenue()[2] - fd.revenue()[0]) /
                            fd.revenue()[0], 0) + " over two years while "
         "reducing its borrowings."),

        ("h2", "6.6  The Working Capital Cycle"),
        _table("6.5", "Working capital cycle",
               [("Particulars", 0.46, "l"), (Y[1], 0.27, "r"),
                (Y[2], 0.27, "r")],
               [["Debtors Turnover (times)", m(r[1]["debtor_turnover"]),
                 m(r[2]["debtor_turnover"])],
                ["Collection Period (days)", m(r[1]["debtor_days"], 1),
                 m(r[2]["debtor_days"], 1)],
                ["Creditors Turnover (times)", m(r[1]["creditor_turnover"]),
                 m(r[2]["creditor_turnover"])],
                ["Payment Period (days)", m(r[1]["creditor_days"], 1),
                 m(r[2]["creditor_days"], 1)],
                ["Inventory Holding Period (days)", "Nil", "Nil"],
                (["Cash Conversion Cycle (days)", m(r[1]["cash_cycle"], 1),
                  m(r[2]["cash_cycle"], 1)], "total")],
               note="Creditors turnover is computed on direct programme cost "
                    "as a proxy for credit purchases."),
        ("p", "The cash conversion cycle of " + m(r[2]["cash_cycle"], 1) +
         " days is negative, and its interpretation is important. The company "
         "collects from its customers about " + m(r[2]["debtor_days"], 1) +
         " days after the sale but settles its own obligations about " +
         m(r[2]["creditor_days"], 1) + " days after incurring them. For "
         "roughly " + m(abs(r[2]["cash_cycle"]), 0) + " days it therefore has "
         "the use of money that is not its own. This is how the business has "
         "financed growth without a matching increase in working capital "
         "borrowing, and it is a structural feature of the model rather than a "
         "temporary advantage."),
        ("callout", "warn", "The Qualification That Matters Most",
         "The favourable cycle rests on a payment period of about " +
         m(r[2]["creditor_days"], 1) + " days to mentors and vendors. That "
         "period is an accommodation, not a contractual right. Should mentors "
         "press for faster settlement " + EM + " a realistic prospect in a "
         "competitive market for good mentors " + EM + " the cycle would turn "
         "positive and the company would need working capital finance for the "
         "first time. The negative cycle should therefore be treated as a "
         "benefit to be protected, not as a permanent feature to be relied "
         "upon."),

        ("h2", "6.7  Common-Size Balance Sheet"),
        _table("6.6", "Common-size Balance Sheet (percentage of balance sheet "
               "total)", _yr_cols("Particulars", 0.40), cs_bs_rows,
               font_scale=0.93),
        ("p", "The structural shift over three years is visible at a glance. "
         "On the liabilities side, shareholders' funds rose from " +
         m(100 * fd.shareholders_funds()[0] / fd.balance_total()[0]) +
         " per cent of the balance sheet to " +
         m(100 * fd.shareholders_funds()[2] / fd.balance_total()[2]) +
         " per cent, while long-term borrowings fell from " +
         m(100 * fd.bs("Long-term Borrowings")[0] / fd.balance_total()[0]) +
         " per cent to " +
         m(100 * fd.bs("Long-term Borrowings")[2] / fd.balance_total()[2]) +
         " per cent. On the assets side, cash and bank balances rose from " +
         m(100 * fd.bs("Cash & Bank Balances")[0] / fd.assets_total()[0]) +
         " per cent to " +
         m(100 * fd.bs("Cash & Bank Balances")[2] / fd.assets_total()[2]) +
         " per cent, the largest single asset in the business. A balance "
         "sheet that is becoming simultaneously more owner-financed and more "
         "liquid is strengthening in the most fundamental sense."),

        ("h2", "6.8  DuPont Decomposition of Return on Equity"),
        ("p", "The DuPont identity decomposes return on equity into three "
         "components, so that an improvement can be attributed to operating "
         "efficiency, to asset utilisation or merely to gearing:"),
        ("center", "<b>Return on Equity = Net Profit Margin \u00d7 Total "
         "Asset Turnover \u00d7 Equity Multiplier</b>"),
        _table("6.7", "DuPont decomposition of return on equity",
               [("Component", 0.34, "l")] + [(y, 0.18, "r") for y in Y] +
               [("Direction", 0.12, "c")],
               [["Net Profit Margin (per cent)"] +
                [m(fd.dupont(i)["net_margin"]) for i in range(3)] +
                ["Improving"],
                ["Total Asset Turnover (times)"] +
                [m(fd.dupont(i)["asset_turnover"]) for i in range(3)] +
                ["Stable"],
                ["Equity Multiplier (times)"] +
                [m(fd.dupont(i)["equity_multiplier"]) for i in range(3)] +
                ["Falling"],
                (["Return on Equity, reconstructed (per cent)"] +
                 [m(fd.dupont(i)["roe_reconstructed"]) for i in range(3)] +
                 [EM], "total"),
                (["Return on Equity, computed directly (per cent)"] +
                 [m(fd.dupont(i)["roe_direct"]) for i in range(3)] + [EM],
                 "total")],
               note="The two return on equity lines agree within rounding, "
                    "which validates the decomposition."),
        ("figure", "fig18_dupont", "DuPont decomposition of return on equity",
         "Computed from Table 6.7."),
        ("p", "This is the most important table in the chapter. Return on "
         "equity roughly doubled, from " + pc(r[0]["roe"]) + " to " +
         pc(r[2]["roe"]) + ". The natural suspicion in any such case is that "
         "the improvement was manufactured by leverage. The decomposition "
         "shows the opposite. The equity multiplier <i>fell</i> from " +
         m(fd.dupont(0)["equity_multiplier"]) + " to " +
         m(fd.dupont(2)["equity_multiplier"]) + " times, which by itself "
         "would have <i>reduced</i> return on equity. Total asset turnover "
         "was essentially flat. The entire improvement, and more, came from "
         "the net profit margin rising from " +
         m(fd.dupont(0)["net_margin"]) + " per cent to " +
         m(fd.dupont(2)["net_margin"]) + " per cent."),
        ("p", "The conclusion is that the return on equity of this business "
         "has improved for the best possible reason " + EM + " it became more "
         "profitable on each rupee of sales " + EM + " while simultaneously "
         "becoming less risky. Few results in a three-year analysis are as "
         "unambiguous as this one."),

        ("h2", "6.9  Summary of the Ratio Analysis"),
        _table("6.8", "Consolidated assessment of financial position",
               [("Dimension", 0.20, "l"), (Y[2] + " position", 0.22, "l"),
                ("Trend", 0.14, "c"), ("Assessment", 0.44, "l")],
               [["Liquidity", "Current " + m(r[2]["current"]) + ", quick " +
                 m(r[2]["quick"]), "Improving",
                 "Adequate once the absence of inventory and the advance-fee "
                 "character of current liabilities are allowed for"],
                ["Profitability", "Net margin " + m(r[2]["net_margin"]) +
                 " per cent", "Improving",
                 "Strong and progressive; driven by overhead absorption "
                 "rather than by price increases"],
                ["Solvency", "Debt-equity " + m(r[2]["debt_equity"]) +
                 ", cover " + m(r[2]["interest_cover"]), "Improving",
                 "Very comfortable; arguably more conservative than the "
                 "return on capital employed warrants"],
                ["Activity", "Asset turnover " +
                 m(r[2]["total_asset_turnover"]) + " times", "Stable",
                 "Efficient asset use characteristic of an asset-light model"],
                ["Working capital", "Cycle " + m(r[2]["cash_cycle"], 1) +
                 " days", "Favourable",
                 "Structurally advantageous but dependent on continued "
                 "vendor accommodation"],
                ["Cash generation", "Operating cash " +
                 rs(fd.cash_flow()["net_op"]) + " L", "Improving",
                 "Exceeds profit after tax; the strongest single indicator in "
                 "the accounts"],
                ["Receivables", "Debtors " +
                 rs(fd.bs("Trade Receivables")[2]) + " L", "Watch",
                 "The one genuine area of concern, because the balance arises "
                 "from a sixth of revenue"]],
               font_scale=0.90),
        ("pagebreak",),
    ]



# ============================================================ CHAPTER 7 ==
def chapter_seven():
    return [
        ("chapter", "7", "LEARNING OUTCOMES",
         "What the internship actually taught, mapped against the objectives "
         "set out in Chapter One, and separated into technical, analytical, "
         "behavioural and professional learning."),
        ("lead", "The value of an internship is measured not by the tasks "
         "completed but by the difference between what the student believed "
         "before it and what the student can demonstrate after it."),

        ("h2", "7.1  Achievement against the Stated Objectives"),
        ("p", "Chapter One set one primary and seven secondary objectives. "
         "Each is reviewed below against the evidence produced in the report."),
        _table("7.1", "Objectives and their achievement",
               [("Objective", 0.44, "l"), ("Status", 0.14, "c"),
                ("Evidence in this report", 0.42, "l")],
               [["Understand the finance function and its information flow",
                 "Achieved", "Section 2.6 and the process note of Week One"],
                ["Examine books of account, vouchers and internal checks",
                 "Achieved", "Section 3.4 and the internal control checklist"],
                ["Analyse revenue and cost composition and behaviour",
                 "Achieved", "Sections 4.2 to 4.3 and Tables 4.1 to 4.3"],
                ["Evaluate budgeting and quantify variances",
                 "Achieved", "Sections 5.1 to 5.3 and Table 5.2"],
                ["Compute and interpret ratios over three years",
                 "Achieved", "Chapter Six, Tables 6.1 to 6.8"],
                ["Segregate costs and derive break-even and margin of safety",
                 "Achieved", "Sections 5.4 to 5.5 and Tables 5.4 to 5.5"],
                ["Identify weaknesses and frame suggestions",
                 "Achieved", "Chapter Nine"],
                ["Compare performance against industry averages",
                 "Not achieved", "Published benchmarks for this sector do "
                 "not exist; recorded as a limitation in Section 1.8"]],
               font_scale=0.94),

        ("h2", "7.2  Technical Learning"),
        ("defs", [
            ("Revenue recognition in practice",
             "The gateway reconciliation of Week Two established a principle "
             "that had previously been abstract: revenue is recognised gross "
             "and the intermediary's commission is an expense. Netting the "
             "two would understate turnover and cost simultaneously and would "
             "distort the profit-volume ratio. The rule was familiar; the "
             "reason for it became clear only when applied."),
            ("The difference between a cost and a payment",
             "Mentor honoraria are incurred when a cohort is delivered but "
             "paid weeks later. Learning to record the first and track the "
             "second separately is the whole of accrual accounting, and it "
             "explains why the cash flow statement of Section 4.6 begins with "
             "profit and then adjusts it."),
            ("Cost segregation as judgement, not arithmetic",
             "No textbook problem requires the analyst to decide what "
             "proportion of marketing is variable. Doing so for a real "
             "expense head, and then testing how much the break-even point "
             "moves as that judgement changes, was the most useful single "
             "exercise of the internship."),
            ("Ratio basis matters as much as ratio value",
             "Computing debtor days on total revenue and again on credit "
             "sales only produced " +
             m(fd.ratio_set(2)["debtor_days"], 1) + " days and roughly " +
             m(365.0 * ((fd.bs("Trade Receivables")[1] +
                         fd.bs("Trade Receivables")[2]) / 2.0) / 34.90, 0) +
             " days from the same balance sheet. The lesson is that a ratio "
             "reported without its basis is not information."),
            ("Reconciliation as a control",
             "The three unreconciled gateway items of Section 3.4 were "
             "individually trivial and collectively instructive: a "
             "reconciliation is not a clerical formality but the mechanism by "
             "which errors are detected at all."),
        ]),

        ("h2", "7.3  Analytical Learning"),
        ("numbers", [
            "<b>A favourable bottom line can conceal adverse control.</b> "
            "Profit before tax exceeded budget by " +
            pc(100 * (fd.budget_totals()["actual_pbt"] -
                      fd.budget_totals()["budget_pbt"]) /
               fd.budget_totals()["budget_pbt"]) + ", and three cost heads "
            "simultaneously overshot. Before this internship the first fact "
            "would have been reported and the second missed.",
            "<b>Decomposition changes conclusions.</b> The DuPont analysis of "
            "Section 6.8 reversed the natural assumption about why return on "
            "equity had risen. Had the headline ratio been reported alone, the "
            "report would have been wrong about the cause while right about "
            "the number.",
            "<b>Benchmarks are contextual.</b> A current ratio of " +
            m(fd.ratio_set(2)["current"]) + " against a 2:1 convention looks "
            "like a weakness until one notices that the convention assumes "
            "inventory and this business has none. Applying a benchmark "
            "without asking what it was designed to measure produces "
            "confident error.",
            "<b>Seasonality is a financial fact, not an operational one.</b> "
            "Annualising the third quarter's revenue of " + rs(41.20) +
            " lakh gives a run rate below the break-even sales of " +
            rs(fd.bep_sales()) + " lakh. The same company is loss-making in "
            "one quarter and comfortably profitable over the year, and only "
            "the combination of Section 4.2 with Section 5.5 reveals it.",
            "<b>Leverage explains risk appetite.</b> Operating leverage of " +
            m(fd.operating_leverage()[0]) + " times made sense of a financing "
            "policy that had initially appeared excessively cautious. Two "
            "figures from different chapters, read together, produced an "
            "understanding neither gave alone.",
        ]),

        ("h2", "7.4  Behavioural and Interpersonal Learning"),
        ("bullets", [
            "<b>Asking for data is a negotiation.</b> Records are held by "
            "people with their own deadlines. Explaining why a schedule was "
            "needed, and accepting it in the form in which it existed rather "
            "than the form that would have been convenient, proved far more "
            "effective than repeating the request.",
            "<b>Questions must be specific to be answerable.</b> \u201cHow do "
            "you budget for marketing?\u201d produced a general answer; "
            "\u201cwhat was the basis of the " + rs(30.00) + " lakh "
            "provision?\u201d produced the finding that it was a percentage of "
            "projected revenue, which became a recommendation.",
            "<b>Criticism of a system is not criticism of a colleague.</b> "
            "Presenting the marketing variance required care. Framing it as a "
            "gap in the measurement system rather than as an error by the "
            "function that spent the money kept the conversation open and "
            "produced better information.",
            "<b>Deadlines in an operating business are not negotiable.</b> "
            "Month-end compliance work does not wait for an intern's "
            "analysis. Scheduling requests around the finance function's own "
            "cycle was a practical lesson in professional courtesy.",
        ]),

        ("h2", "7.5  Professional and Personal Learning"),
        ("defs", [
            ("Working to an owner and a frequency",
             "The mentor's criticism recorded in Section 3.9 " + EM + " that "
             "a recommendation without an owner and a frequency is an "
             "opinion " +
             EM + " changed the whole of Chapter Nine and will change how "
             "every future recommendation is written."),
            ("Documentation discipline",
             "Every derived figure in this report can be traced to a source "
             "line because the working papers were built that way from Week "
             "Two. The habit was adopted after an early figure could not be "
             "reproduced."),
            ("Intellectual honesty about limitations",
             "Stating plainly that industry benchmarks were unavailable, that "
             "the cost split was judgemental and that return ratios are "
             "understated on a closing-balance basis makes the report weaker "
             "in appearance and stronger in fact."),
            ("Confidence grounded in preparation",
             "Presenting findings to management was uncomfortable until it "
             "became clear that every number could be defended. Confidence in "
             "a professional setting is a by-product of working papers, not "
             "of temperament."),
        ]),

        ("h2", "7.6  Bridging Theory and Practice"),
        _table("7.2", "Classroom concept against observed practice",
               [("Concept as taught", 0.32, "l"),
                ("As observed in the organisation", 0.40, "l"),
                ("Refinement to understanding", 0.28, "l")],
               [["Current ratio of 2:1 indicates sound liquidity",
                 "Ratio of " + m(fd.ratio_set(2)["current"]) + " with no "
                 "inventory and advance-collected liabilities",
                 "The benchmark encodes an assumption about asset "
                 "composition, not a universal law"],
                ["Higher leverage raises return on equity",
                 "Return on equity doubled while the equity multiplier fell",
                 "Leverage is one of three drivers and often not the "
                 "operative one"],
                ["Break-even analysis assumes a known cost split",
                 "The split of marketing had to be negotiated with management",
                 "The analysis is only as robust as the classification "
                 "underlying it"],
                ["Budgetary control follows preparation",
                 "Budget prepared well, reviewed annually",
                 "Control is a function of review frequency, not of budget "
                 "quality"],
                ["Debtor days measures collection efficiency",
                 "Meaningless here unless computed on credit sales alone",
                 "A ratio must be matched to the revenue mix that generated "
                 "the balance"],
                ["Profit indicates performance",
                 "Operating cash flow of " +
                 rs(fd.cash_flow()["net_op"]) + " L exceeded profit of " +
                 rs(fd.pat()[2]) + " L",
                 "Cash conversion, not profit alone, evidences quality of "
                 "earnings"]],
               font_scale=0.90),
        ("pagebreak",),
    ]


# ============================================================ CHAPTER 8 ==
def chapter_eight():
    return [
        ("chapter", "8", "CHALLENGES FACED",
         "The practical and analytical difficulties encountered during the "
         "internship, how each was addressed, and what each one taught."),
        ("lead", "The difficulties were as instructive as the work, and "
         "recording them honestly is part of the record. Each is stated with "
         "the response adopted and the lesson drawn, because a challenge "
         "described without its resolution is merely a complaint."),

        ("h2", "8.1  Data Availability and Format"),
        ("p", "<b>The difficulty.</b> Financial information existed, but not "
         "in the form the analysis required. Cost data was organised by "
         "voucher and by payee rather than by cohort, so a cohort-wise "
         "contribution statement could not simply be extracted. Some "
         "schedules were maintained in spreadsheets with inconsistent "
         "headings across months."),
        ("p", "<b>The response.</b> Rather than requesting a reformatted data "
         "set, which would have imposed work on a busy team, the intern built "
         "a mapping table linking each voucher head to a cohort and rebuilt "
         "the cost sheet from the underlying vouchers. Where headings were "
         "inconsistent, a single standard set was adopted and documented."),
        ("p", "<b>The lesson.</b> Data in an operating business is organised "
         "for the purpose it was created to serve, not for the purpose of a "
         "later analysis. The analyst's first task is usually reconstruction, "
         "and the time budgeted for analysis should assume it."),

        ("h2", "8.2  Absence of Industry Benchmarks"),
        ("p", "<b>The difficulty.</b> The study intended to compare the "
         "organisation's ratios with sector averages. No reliable published "
         "financial data exists for unlisted, small-scale structured "
         "internship providers in India. Listed education companies were "
         "considered as a proxy and rejected: their scale, capital intensity "
         "and business models differ so greatly that comparison would have "
         "misled rather than informed."),
        ("p", "<b>The response.</b> Two substitute bases were adopted. First, "
         "the organisation was compared against its own three-year history, "
         "which is the more meaningful comparison for a growing business. "
         "Second, conventional rules of thumb were used, with an explicit "
         "statement wherever a rule of thumb rested on an assumption " + EM +
         " such as the presence of inventory " + EM + " that does not hold "
         "here."),
        ("p", "<b>The lesson.</b> Where a benchmark does not exist, the "
         "honest course is to say so and to substitute a defensible "
         "alternative, not to borrow an inapplicable one for the appearance "
         "of rigour."),

        ("h2", "8.3  Judgement in Cost Classification"),
        ("p", "<b>The difficulty.</b> The break-even analysis required "
         "marketing and administrative expenses to be split between variable "
         "and fixed components. Neither a statistical series long enough for "
         "regression nor an existing internal classification was available."),
        ("p", "<b>The response.</b> The components of each head were listed "
         "and discussed individually with management " + EM + " performance "
         "advertising against brand spend, gateway charges against incubation "
         "charges " + EM + " and a split agreed on the basis of observed "
         "behaviour. The judgement was then stress-tested: the sensitivity "
         "note in Section 5.5 shows that break-even sales range from about " +
         rs(163.5, 1) + " lakh to " + rs(184.2, 1) + " lakh across a "
         "twenty-point variation in the marketing assumption, and that the "
         "conclusion drawn holds throughout that range."),
        ("p", "<b>The lesson.</b> A judgemental input does not invalidate an "
         "analysis, provided the judgement is disclosed and the conclusion is "
         "shown to be robust to it. Concealing the judgement would have been "
         "the only real failure."),

        ("h2", "8.4  Reconciling Conflicting Records"),
        ("p", "<b>The difficulty.</b> Enrolment numbers held by the "
         "Admissions function did not always agree with the count implied by "
         "collections recorded in the books. The differences were small but "
         "persistent, and until they were understood no cohort-wise "
         "contribution figure could be relied upon."),
        ("p", "<b>The response.</b> Each difference was traced individually. "
         "Three causes emerged: candidates enrolled in one month and paid in "
         "the next, part-payments recorded as full enrolments, and a small "
         "number of scholarship waivers recorded in the enrolment system but "
         "correctly absent from collections. Once the three causes were "
         "identified, a reconciliation format was devised that accommodated "
         "all of them."),
        ("p", "<b>The lesson.</b> Two records of the same event rarely differ "
         "because one is wrong; usually they differ because they measure "
         "slightly different things. Identifying what each actually measures "
         "resolves most discrepancies."),

        ("h2", "8.5  Working within Confidentiality Constraints"),
        ("p", "<b>The difficulty.</b> Client-wise contract values, individual "
         "mentor rates and candidate details are commercially sensitive. "
         "Reproducing them would have been a breach of the trust on which "
         "access was granted; omitting them entirely would have weakened the "
         "analysis."),
        ("p", "<b>The response.</b> All such data has been aggregated. "
         "Receivables appear by age bucket rather than by client, revenue by "
         "service line rather than by contract, and mentor cost in total "
         "rather than by individual. The analytical conclusions do not depend "
         "on the suppressed detail, and where aggregation limits what can be "
         "concluded, the limitation is stated."),
        ("p", "<b>The lesson.</b> Confidentiality and analytical usefulness "
         "are usually reconcilable through the right level of aggregation. "
         "The question to ask is what level of detail the conclusion actually "
         "requires, which is often less than the analyst first assumes."),

        ("h2", "8.6  Time Pressure and Competing Priorities"),
        ("p", "<b>The difficulty.</b> " + brand.INTERN_DAYS + " is a short "
         "period in which to understand a business, reconstruct three years "
         "of analysis and write a report. The internship also coincided with "
         "the organisation's peak season, when the finance function was least "
         "able to spare time for explanation, and with month-end and "
         "quarter-end compliance work."),
        ("p", "<b>The response.</b> A written work plan was agreed with the "
         "mentor in Week One and reviewed each Saturday. Questions were "
         "batched and raised in the weekly review rather than as they arose, "
         "and clerical work was scheduled into the periods when the accounts "
         "team was busiest, with analytical work reserved for quieter days."),
        ("p", "<b>The lesson.</b> In an operating business the analyst's "
         "schedule must yield to the business's schedule. Batching questions "
         "and working to a visible plan obtained more cooperation than "
         "persistence would have."),

        ("h2", "8.7  Transition from Academic to Professional Standards"),
        ("p", "<b>The difficulty.</b> Academic work is assessed on "
         "completeness of exposition; professional work is assessed on "
         "usefulness of conclusion. An early draft of the analysis was "
         "returned by the mentor with the observation that it explained the "
         "computation of every ratio at length and said too little about what "
         "management should do differently."),
        ("p", "<b>The response.</b> The report was restructured. Method was "
         "compressed to what a reader needs in order to trust the figure, and "
         "every analytical section was required to end in an interpretation "
         "rather than a number. Chapter Nine was rewritten so that each "
         "recommendation names an owner, a frequency and a measurable trigger."),
        ("p", "<b>The lesson.</b> The most valuable correction of the "
         "internship. Analysis that does not terminate in a decision is an "
         "exercise, not advice."),

        ("h2", "8.8  Summary"),
        _table("8.1", "Challenges, responses and lessons",
               [("Challenge", 0.26, "l"), ("Response", 0.40, "l"),
                ("Lesson", 0.34, "l")],
               [["Data not in analysable form",
                 "Built a voucher-to-cohort mapping and rebuilt the cost sheet",
                 "Reconstruction precedes analysis"],
                ["No industry benchmarks",
                 "Compared against own history and qualified rules of thumb",
                 "State the absence rather than borrow a false standard"],
                ["Judgemental cost split",
                 "Agreed the split with management and stress-tested it",
                 "Disclose the judgement and test the conclusion"],
                ["Conflicting enrolment records",
                 "Traced each difference to one of three identifiable causes",
                 "Records differ because they measure different things"],
                ["Confidentiality limits",
                 "Aggregated by bucket, line and total",
                 "Match the level of detail to the conclusion required"],
                ["Short time in peak season",
                 "Written plan, weekly review, batched questions",
                 "The analyst's schedule yields to the business's"],
                ["Academic writing habits",
                 "Restructured so every section ends in an interpretation",
                 "Analysis must terminate in a decision"]],
               font_scale=0.91),
        ("pagebreak",),
    ]


# ============================================================ CHAPTER 9 ==
def chapter_nine():
    r2 = fd.ratio_set(2)
    cf = fd.cash_flow()
    return [
        ("chapter", "9", "FINDINGS AND SUGGESTIONS",
         "The consolidated findings of the study and a prioritised set of "
         "recommendations, each with a named owner, a stated frequency and a "
         "measurable trigger."),
        ("lead", "Findings are stated first and separately from "
         "recommendations, so that the evidence can be judged independently "
         "of the advice drawn from it."),

        ("h2", "9.1  Findings"),
        ("h3", "9.1.1  Findings on Growth and Profitability"),
        ("numbers", [
            "<b>Growth has been rapid and has been profitable.</b> Revenue "
            "from operations rose from " + rs(fd.revenue()[0]) + " lakh to " +
            rs(fd.revenue()[2]) + " lakh over three years while profit after "
            "tax rose from " + rs(fd.pat()[0]) + " lakh to " +
            rs(fd.pat()[2]) + " lakh. Profit grew faster than revenue in each "
            "year, which is evidence of operating leverage rather than of "
            "price increases.",
            "<b>Margin improvement is structural, not incidental.</b> The "
            "common-size analysis of Table 4.3 shows direct programme cost "
            "falling from " + m(100 * fd.pl("Direct Programme Cost")[0] /
                                fd.revenue()[0], 1) + " to " +
            m(100 * fd.pl("Direct Programme Cost")[2] /
              fd.revenue()[2], 1) + " per cent of revenue and employee "
            "benefits from " +
            m(100 * fd.pl("Employee Benefit Expenses")[0] /
              fd.revenue()[0], 1) + " to " +
            m(100 * fd.pl("Employee Benefit Expenses")[2] /
              fd.revenue()[2], 1) + " per cent. Content reuse and overhead "
            "absorption, not pricing, are doing the work.",
            "<b>Return on equity improved for the right reasons.</b> The "
            "DuPont decomposition shows the equity multiplier falling from " +
            m(fd.dupont(0)["equity_multiplier"]) + " to " +
            m(fd.dupont(2)["equity_multiplier"]) + " times while return on "
            "equity doubled. The improvement came from margin, not gearing.",
            "<b>Marketing intensity has not declined.</b> Marketing has held "
            "at approximately " +
            m(100 * fd.pl("Marketing & Digital Promotion")[2] /
              fd.revenue()[2], 1) + " per cent of revenue in every year. "
            "Growth is still being purchased rather than compounding from "
            "reputation and referral, and this is the most important "
            "qualification to an otherwise favourable cost story.",
        ]),
        ("h3", "9.1.2  Findings on Liquidity and Working Capital"),
        ("numbers", [
            "<b>Liquidity is adequate once correctly interpreted.</b> The "
            "current ratio of " + m(r2["current"]) + " is below the 2:1 "
            "convention, but the convention assumes inventory that this "
            "business does not hold, and a material part of current "
            "liabilities represents fees collected in advance that will be "
            "discharged by service rather than by cash.",
            "<b>The cash conversion cycle is negative and favourable.</b> "
            "Collection in about " + m(r2["debtor_days"], 1) + " days against "
            "payment in about " + m(r2["creditor_days"], 1) + " days yields a "
            "cycle of about " + m(r2["cash_cycle"], 1) + " days, so "
            "operations are partly financed by trade credit.",
            "<b>That favourable cycle rests on an accommodation, not a "
            "right.</b> The payment period of about " +
            m(r2["creditor_days"], 1) + " days to mentors and vendors is not "
            "contractual. If mentors pressed for faster settlement the cycle "
            "would turn positive and working capital finance would be needed "
            "for the first time.",
            "<b>The reported debtor-days figure gives false comfort.</b> "
            "Because only the business-to-business line is sold on credit, "
            "trade receivables of " + rs(fd.bs("Trade Receivables")[2]) +
            " lakh arise from revenue of about " + rs(34.90) + " lakh. "
            "Measured against credit sales the collection period is of the "
            "order of " +
            m(365.0 * ((fd.bs("Trade Receivables")[1] +
                        fd.bs("Trade Receivables")[2]) / 2.0) / 34.90, 0) +
            " days, not " + m(r2["debtor_days"], 1) + " days. This is the "
            "single most significant weakness identified by the study.",
            "<b>Receivables ageing shows real slippage.</b> " +
            pc(100 * (2.60 + 1.80) / 23.10) + " of the closing receivable "
            "balance was overdue by more than sixty days, and " +
            rs(1.80) + " lakh by more than ninety days. There is no written "
            "credit policy and no formal provisioning norm.",
            "<b>Cash generation is genuine.</b> Net cash from operations of " +
            rs(cf["net_op"]) + " lakh exceeded profit after tax of " +
            rs(fd.pat()[2]) + " lakh, funded the whole capital programme of " +
            rs(cf["capex"]) + " lakh, permitted debt repayment of " +
            rs(abs(cf["d_ltb"])) + " lakh and still increased cash by " +
            rs(cf["net_change"]) + " lakh.",
        ]),
        ("h3", "9.1.3  Findings on Budgeting and Cost Control"),
        ("numbers", [
            "<b>Budgets are prepared competently but monitored "
            "inadequately.</b> Preparation is participative and "
            "evidence-based; head-wise comparison against actuals is "
            "performed only at the year end, so an adverse variance cannot be "
            "corrected in the period in which it arises.",
            "<b>A favourable revenue variance masked adverse cost "
            "variances.</b> Revenue exceeded budget by " +
            pc(fd.budget_variance(fd.BUDGET[0])[1]) + " while marketing "
            "overshot by " + pc(abs(fd.budget_variance(fd.BUDGET[4])[1])) +
            ", direct programme cost by " +
            pc(abs(fd.budget_variance(fd.BUDGET[2])[1])) + " and technology "
            "by " + pc(abs(fd.budget_variance(fd.BUDGET[6])[1])) +
            ". Had revenue merely met budget, the overruns would have reduced "
            "profit before tax by roughly a third.",
            "<b>The marketing budget is set on a basis that cannot be "
            "controlled.</b> Fixing the provision as a percentage of "
            "projected revenue makes overspend arithmetically likely when "
            "revenue exceeds projection and provides no test of whether the "
            "spend bought proportionate enrolment.",
            "<b>No flexible budget exists.</b> Because variances are not "
            "restated to actual activity, the direct programme cost variance "
            "of " + pc(abs(fd.budget_variance(fd.BUDGET[2])[1])) + " cannot "
            "be separated into a volume effect, which is expected and "
            "harmless, and an efficiency effect, which would matter.",
            "<b>No cash budget exists, despite pronounced seasonality.</b> "
            "Third-quarter revenue of " + rs(41.20) + " lakh annualises to a "
            "run rate below break-even sales of " + rs(fd.bep_sales()) +
            " lakh. The company is loss-making in its lean quarter and has no "
            "formal month-wise projection of receipts and payments.",
            "<b>Cost control measures that do exist are effective.</b> The "
            "incubation arrangement, variable mentor engagement, content reuse "
            "and digital delivery are all visible in the common-size "
            "statements and in the favourable administration and finance cost "
            "variances.",
        ]),
        ("h3", "9.1.4  Findings on Solvency and Structure"),
        ("numbers", [
            "<b>Solvency has strengthened on every measure.</b> Debt-equity "
            "fell from " + m(fd.ratio_set(0)["debt_equity"]) + " to " +
            m(r2["debt_equity"]) + ", interest cover rose from " +
            m(fd.ratio_set(0)["interest_cover"]) + " to " +
            m(r2["interest_cover"]) + " times and the proprietary ratio "
            "reached " + pc(r2["proprietary"]) + ".",
            "<b>Financing may be more conservative than the returns "
            "warrant.</b> With return on capital employed of " +
            pc(r2["roce"]) + " against a materially lower borrowing cost, "
            "prudent additional debt would raise return on equity. The "
            "caution is defensible given operating leverage of " +
            m(fd.operating_leverage()[0]) + " times, but it should be a "
            "deliberate choice.",
            "<b>Revenue is concentrated in a single service line.</b> Paid "
            "internship programmes contribute " +
            pc(100 * 112.80 / fd.revenue()[2]) + " of turnover. A "
            "competitive or regulatory shock to that line would affect more "
            "than half of revenue.",
        ]),

        ("h2", "9.2  Suggestions"),
        ("p", "Each suggestion below states what should be done, who should "
         "own it, how often it should occur and what measurable trigger "
         "should prompt action. Recommendations are ordered by priority, and "
         "the priority reflects the ratio of expected benefit to "
         "implementation difficulty rather than the size of the underlying "
         "number."),
        _table("9.1", "Prioritised recommendations",
               [("No.", 0.05, "c"), ("Recommendation", 0.37, "l"),
                ("Owner", 0.15, "l"), ("Frequency", 0.13, "c"),
                ("Trigger for action", 0.30, "l")],
               [["1", "Institute a monthly budget-versus-actual review "
                 "covering every head, not merely revenue",
                 "Finance", "Monthly",
                 "Written explanation required for any head deviating by "
                 "more than five per cent"],
                ["2", "Issue a written credit policy for institutional "
                 "clients, with credit limits, milestone-linked invoicing and "
                 "approval for exceptions",
                 "Corporate Relations with Finance", "On adoption",
                 "No new contract signed without an assigned credit limit"],
                ["3", "Report debtor days on credit sales only, alongside the "
                 "conventional figure",
                 "Finance", "Monthly",
                 "Escalation when the credit-sales collection period exceeds "
                 "seventy-five days"],
                ["4", "Prepare a rolling twelve-month cash budget by month",
                 "Finance", "Monthly rolling",
                 "Action when projected closing cash in any month falls below "
                 "one month of committed cost"],
                ["5", "Recast the marketing budget on a cost-per-enrolment "
                 "basis by channel in place of a percentage of revenue",
                 "Marketing with Finance", "Annual, reviewed monthly",
                 "Channel review when cost per enrolment exceeds the approved "
                 "figure by ten per cent"],
                ["6", "Introduce flexible budgeting so that variances are "
                 "restated to actual activity",
                 "Finance", "Monthly",
                 "Separate reporting of volume and efficiency variances on "
                 "all variable heads"],
                ["7", "Adopt an ageing-based provisioning norm for doubtful "
                 "receivables",
                 "Finance", "Quarterly",
                 "Provision considered on balances overdue beyond ninety days"],
                ["8", "Introduce cohort-wise contribution reporting to "
                 "support pricing and mentor-payout decisions",
                 "Programme Delivery with Finance", "Per cohort",
                 "Review of any cohort whose contribution margin falls below "
                 "forty per cent"],
                ["9", "Arrange a modest working capital limit in advance of "
                 "need, as insurance against a lengthening cycle",
                 "Management", "Annual review",
                 "Arrange before the cash conversion cycle turns positive, "
                 "not after"],
                ["10", "Diversify revenue by expanding institutional and "
                 "CSR-funded programmes",
                 "Corporate Relations", "Annual target",
                 "Reduce the share of the largest service line below fifty "
                 "per cent of turnover"],
                ["11", "Formalise responsibility accounting so that each "
                 "budget head has a named owner",
                 "Management", "On adoption",
                 "Every head in the master budget attributed to one "
                 "individual"],
                ["12", "Review the capital structure deliberately in the "
                 "light of the return on capital employed",
                 "Management", "Annual",
                 "Explicit decision recorded, whether or not gearing is "
                 "increased"]],
               font_scale=0.87,
               note="Recommendations 1 to 4 are considered to have the "
                    "highest ratio of benefit to implementation effort and "
                    "are capable of being adopted within one quarter."),
        ("h3", "9.2.1  The Four Changes That Matter Most"),
        ("defs", [
            ("Monthly variance review",
             "Of everything in Table 9.1 this is the most consequential and "
             "the cheapest. It requires no capital, no system and no "
             "additional staff " + EM + " only a standing monthly meeting and "
             "a one-page format. It would have surfaced the marketing "
             "overspend of " + rs(3.10) + " lakh by the second quarter, when "
             "it could still have been corrected."),
            ("Credit policy and correct debtor reporting",
             "The receivable balance is the one genuine financial weakness in "
             "the accounts, and it is currently measured by a ratio that "
             "conceals it. A written credit policy and a collection period "
             "computed on credit sales together convert an invisible risk "
             "into a managed one."),
            ("Rolling cash budget",
             "The company is loss-making in its third quarter and has no "
             "month-wise projection of receipts and payments. Given a "
             "negative cash conversion cycle that depends on vendor "
             "accommodation, this is the exposure most likely to cause "
             "difficulty at short notice."),
            ("Marketing measured per enrolment",
             "Marketing is the second-largest discretionary cost and the only "
             "major head whose intensity has not fallen with scale. Measuring "
             "cost per enrolment by channel turns the overspend from an "
             "accident of budgeting into a decision about efficiency."),
        ]),
        ("callout", "info", "An Observation on Implementation",
         "None of the first eight recommendations requires capital "
         "expenditure, additional borrowing or new software. They require "
         "regularity, a named owner and a written format. The financial "
         "weaknesses identified by this study are weaknesses of system "
         "discipline rather than of financial capacity, which is the most "
         "encouraging conclusion available to a company of this size."),
        ("pagebreak",),
    ]


# =========================================================== CHAPTER 10 ==
def chapter_ten():
    r2 = fd.ratio_set(2)
    cf = fd.cash_flow()
    return [
        ("chapter", "10", "CONCLUSION",
         "An overall appraisal of the financial position and management of " +
         brand.COMPANY_BRAND + ", and concluding observations on the "
         "internship itself."),
        ("lead", "The question posed in Chapter One was whether the financial "
         "management practices supporting rapid growth are adequate to sustain "
         "it. The answer, on the evidence assembled, is a qualified yes."),

        ("h2", "10.1  Overall Financial Appraisal"),
        ("p", brand.COMPANY_BRAND + " is a financially sound enterprise that "
         "has grown quickly without impairing its balance sheet. Over the "
         "three years examined, revenue from operations rose from " +
         rs(fd.revenue()[0]) + " lakh to " + rs(fd.revenue()[2]) + " lakh and "
         "profit after tax from " + rs(fd.pat()[0]) + " lakh to " +
         rs(fd.pat()[2]) + " lakh, while the debt-equity ratio fell from " +
         m(fd.ratio_set(0)["debt_equity"]) + " to " + m(r2["debt_equity"]) +
         " and interest coverage rose to " + m(r2["interest_cover"]) +
         " times. Growth financed largely from retained earnings, accompanied "
         "by improving margins and falling gearing, is the most favourable "
         "combination a small enterprise can present."),
        ("p", "Three features of the business deserve particular emphasis "
         "because they are structural rather than cyclical. The first is the "
         "asset-light model: fixed asset turnover of " +
         m(r2["fixed_asset_turnover"]) + " times means growth requires very "
         "little capital. The second is the high profit-volume ratio of " +
         pc(fd.pv_ratio()) + ", which causes profit to grow much faster than "
         "revenue. The third is the negative cash conversion cycle of about " +
         m(r2["cash_cycle"], 1) + " days, which allows operations to be "
         "financed partly by trade credit. Together these explain how a "
         "company with net worth of only " +
         rs(fd.shareholders_funds()[2]) + " lakh supports a turnover of " +
         rs(fd.revenue()[2]) + " lakh."),
        ("p", "The qualification attaching to the affirmative answer concerns "
         "systems rather than performance. The organisation manages its money "
         "well but measures it incompletely. Its budget is prepared with care "
         "and reviewed too late; its most significant receivable exposure is "
         "monitored by a ratio that conceals it; its lean quarter is "
         "loss-making and unaccompanied by a cash budget; and its second "
         "largest discretionary cost is set on a basis that cannot be "
         "controlled. None of these is a financial weakness in the sense of "
         "insufficient resources. Each is a weakness of measurement, and "
         "measurement is the cheapest thing a company of this size can "
         "improve."),

        ("h2", "10.2  Sustainability of the Present Performance"),
        ("p", "Whether the trajectory can be sustained turns on three "
         "questions that the accounts pose but cannot answer."),
        ("numbers", [
            "<b>Will marketing intensity fall?</b> Marketing has remained at "
            "about " + m(100 * fd.pl("Marketing & Digital Promotion")[2] /
                         fd.revenue()[2], 1) + " per cent of revenue "
            "throughout. If reputation and referral begin to substitute for "
            "paid acquisition, margins will widen further; if not, growth will "
            "continue to cost what it has cost.",
            "<b>Will the vendor accommodation hold?</b> The negative cash "
            "conversion cycle depends on settling mentor and vendor "
            "obligations in about " + m(r2["creditor_days"], 1) + " days. In a "
            "competitive market for capable mentors this is the assumption "
            "most likely to change, and it is the one the company controls "
            "least.",
            "<b>Will the revenue base broaden?</b> With " +
            pc(100 * 112.80 / fd.revenue()[2]) + " of turnover in one service "
            "line, diversification is a matter of risk management rather than "
            "ambition.",
        ]),
        ("p", "On the evidence available, the answers are more likely than not "
         "to be favourable, and in any event the company has the balance "
         "sheet to withstand an unfavourable one. Operating cash flow of " +
         rs(cf["net_op"]) + " lakh, cash balances of " +
         rs(fd.bs("Cash & Bank Balances")[2]) + " lakh and a margin of safety "
         "of " + pc(fd.mos_ratio()) + " of turnover together provide a "
         "reasonable cushion."),

        ("h2", "10.3  Concluding Observations on the Internship"),
        ("p", "The internship achieved the objectives set out in Chapter One, "
         "with the single exception of comparison against industry averages, "
         "which proved impossible for the reasons recorded in Section 8.2. "
         "More importantly, it produced three understandings that no "
         "classroom exercise could have supplied."),
        ("p", "The first is that financial analysis is an act of "
         "interpretation rather than computation. A current ratio of " +
         m(r2["current"]) + " means one thing in a business holding inventory "
         "and quite another in a business holding none; a debtor-days figure "
         "of " + m(r2["debtor_days"], 1) + " days means nothing at all unless "
         "one knows what proportion of revenue was sold on credit. The "
         "arithmetic is the easy part."),
        ("p", "The second is that a correct number and a useful conclusion are "
         "different achievements. The DuPont decomposition of Section 6.8 "
         "produced the same return on equity as the direct computation, but a "
         "completely different explanation of it, and the explanation was what "
         "management could act upon."),
        ("p", "The third is that advice must be implementable to be advice at "
         "all. The mentor's insistence that every recommendation name an "
         "owner, a frequency and a trigger was the most valuable correction "
         "received, and it is the reason Chapter Nine takes the form it does."),
        ("p", "For a student of " + brand.SPECIALISATION + ", the experience "
         "of working through the finance function of a young, growing "
         "enterprise " + EM + " where the consequence of every decision "
         "appears on the face of the accounts within a quarter " + EM +
         " has been worth a great deal more than the equivalent time spent in "
         "a larger organisation observing one narrow slice of a process. I "
         "record my gratitude to " + brand.COMPANY_BRAND + " for that "
         "opportunity, and to " + brand.UNIVERSITY + " for requiring it."),
        ("spacer", 22),
        ("signatures", [("", brand.STUDENT_NAME.title()),
                        ("", brand.DEGREE_SHORT + " " + NDASH + " " +
                         brand.SPECIALISATION)]),
        ("pagebreak",),
    ]



# ========================================================== BIBLIOGRAPHY ==
def bibliography():
    return [
        ("chapter", None, "BIBLIOGRAPHY",
         "Books, journals, statutory material and electronic sources "
         "consulted in the preparation of this report."),

        ("h2", "A.  Books"),
        ("refs", [
            "Khan, M. Y. and Jain, P. K. (2022). <i>Financial Management: "
            "Text, Problems and Cases</i>, 8th edition. New Delhi: McGraw "
            "Hill Education.",
            "Pandey, I. M. (2021). <i>Financial Management</i>, 12th edition. "
            "Noida: Pearson India Education Services.",
            "Chandra, Prasanna (2019). <i>Financial Management: Theory and "
            "Practice</i>, 10th edition. Chennai: McGraw Hill Education.",
            "Maheshwari, S. N., Maheshwari, S. K. and Maheshwari, C. B. "
            "(2021). <i>Principles of Management Accounting</i>, 20th "
            "edition. New Delhi: Sultan Chand and Sons.",
            "Horngren, C. T., Datar, S. M. and Rajan, M. V. (2018). <i>Cost "
            "Accounting: A Managerial Emphasis</i>, 16th edition. Harlow: "
            "Pearson Education.",
            "Gupta, Shashi K. and Sharma, R. K. (2020). <i>Management "
            "Accounting: Principles and Practice</i>, 14th edition. New "
            "Delhi: Kalyani Publishers.",
            "Brigham, E. F. and Ehrhardt, M. C. (2020). <i>Financial "
            "Management: Theory and Practice</i>, 16th edition. Boston: "
            "Cengage Learning.",
            "Kothari, C. R. and Garg, Gaurav (2019). <i>Research Methodology: "
            "Methods and Techniques</i>, 4th edition. New Delhi: New Age "
            "International Publishers.",
            "Van Horne, J. C. and Wachowicz, J. M. (2018). <i>Fundamentals of "
            "Financial Management</i>, 13th edition. Harlow: Pearson "
            "Education.",
            "Bhattacharyya, Debarshi (2021). <i>Management Accounting</i>, "
            "2nd edition. Noida: Pearson India Education Services.",
            "Narayanaswamy, R. (2022). <i>Financial Accounting: A Managerial "
            "Perspective</i>, 7th edition. New Delhi: PHI Learning.",
            "Damodaran, Aswath (2015). <i>Applied Corporate Finance</i>, 4th "
            "edition. Hoboken: John Wiley and Sons.",
        ]),

        ("h2", "B.  Journals and Periodicals"),
        ("refs", [
            "<i>The Chartered Accountant</i>, monthly journal of the "
            "Institute of Chartered Accountants of India, New Delhi.",
            "<i>The Management Accountant</i>, monthly journal of the "
            "Institute of Cost Accountants of India, Kolkata.",
            "<i>Indian Journal of Finance and Banking</i>, selected issues on "
            "working capital management in small and medium enterprises.",
            "<i>Vikalpa: The Journal for Decision Makers</i>, Indian "
            "Institute of Management Ahmedabad, selected articles on cost "
            "behaviour in service enterprises.",
            "<i>Economic and Political Weekly</i>, selected articles on "
            "skill development and employability in eastern India.",
            "<i>Business Standard</i> and <i>The Economic Times</i>, "
            "selected reports on the Indian education technology and "
            "employability services sector, 2024 to 2026.",
        ]),

        ("h2", "C.  Statutory and Regulatory Material"),
        ("refs", [
            "Government of India (2013). <i>The Companies Act, 2013</i>, as "
            "amended, with particular reference to Schedule III on the form "
            "of the Balance Sheet and Statement of Profit and Loss.",
            "Institute of Chartered Accountants of India. <i>Accounting "
            "Standard 3: Cash Flow Statements</i>, applied in the preparation "
            "of the statement in Section 4.6.",
            "Institute of Chartered Accountants of India. <i>Guidance Note on "
            "Reporting under Schedule III</i>, referred to for classification "
            "of current and non-current items.",
            "Government of India (2017). <i>The Central Goods and Services "
            "Tax Act, 2017</i>, referred to in connection with the compliance "
            "cycle described in Section 2.6.",
            "Ministry of Micro, Small and Medium Enterprises, Government of "
            "India. <i>Annual Report 2024-25</i>, referred to for context on "
            "small enterprise finance.",
        ]),

        ("h2", "D.  Electronic and Institutional Sources"),
        ("refs", [
            "Ministry of Corporate Affairs, Government of India " + EM +
            " www.mca.gov.in, referred to for the statutory framework "
            "applicable to private limited companies.",
            "Institute of Chartered Accountants of India " + EM +
            " www.icai.org, referred to for accounting standards and guidance "
            "notes.",
            "Reserve Bank of India " + EM + " www.rbi.org.in, referred to for "
            "prevailing interest rate context in assessing the cost of debt.",
            "Department for Promotion of Industry and Internal Trade, Startup "
            "India " + EM + " www.startupindia.gov.in, referred to for the "
            "policy framework applicable to incubated ventures.",
            "Bihar Industrial Area Development Authority and the B-Hub "
            "incubation programme, Patna " + EM + " referred to for the terms "
            "on which incubation facilities are provided.",
            "Magadh University, Bodh Gaya " + EM + " www.magadhuniversity.ac.in, "
            "referred to for the curriculum and internship requirements of "
            "the " + brand.DEGREE_SHORT + " programme.",
        ]),

        ("h2", "E.  Organisational Records"),
        ("refs", [
            "Indicative Statement of Profit and Loss of " +
            brand.COMPANY_LEGAL + " for the financial years 2023-24, 2024-25 "
            "and 2025-26, made available for academic use.",
            "Indicative Balance Sheet of " + brand.COMPANY_LEGAL + " as at "
            "31st March 2024, 2025 and 2026, made available for academic use.",
            "Internal annual budget statement for the financial year 2025-26.",
            "Cohort-wise programme cost sheets for the financial year 2025-26.",
            "Trade receivable ageing statements and collection follow-up "
            "registers.",
            "Payment gateway settlement statements for the period of the "
            "internship.",
            "Discussions and structured interviews with the management, the "
            "company mentor and the accounts, admissions and programme "
            "delivery teams, conducted between " + brand.INTERN_FROM +
            " and " + brand.INTERN_TO + ".",
        ]),
        ("spacer", 10),
        ("callout", "note", "A Note on Citation",
         "Where a textbook definition or a conventional benchmark has been "
         "used in the interpretation of a ratio, the source is among the works "
         "listed under heading A. The benchmarks quoted in Chapter Six are "
         "rules of thumb drawn from those texts and are not industry averages; "
         "this is stated again in Section 6.1 and among the limitations in "
         "Section 1.8."),
        ("pagebreak",),
    ]


# ============================================================= ANNEXURES ==
def annexures():
    cf = fd.cash_flow()
    r = [fd.ratio_set(i) for i in range(3)]

    # Annexure I - abridged financials on one page
    pl_rows = [[n] + [m(v) for v in fd.pl(n)]
               for n in ["Revenue from Operations", "Other Income"]]
    pl_rows.append((["Total Income"] + [m(v) for v in fd.total_income()],
                    "total"))
    pl_rows += [[n] + [m(v) for v in fd.pl(n)] for n in fd.EXPENSE_HEADS]
    pl_rows.append((["Total Expenses"] + [m(v) for v in fd.total_expenses()],
                    "total"))
    pl_rows.append((["Profit Before Tax"] + [m(v) for v in fd.pbt()], "total"))
    pl_rows.append(["Provision for Taxation"] + [m(v) for v in fd.tax()])
    pl_rows.append((["Profit After Tax"] + [m(v) for v in fd.pat()], "total"))

    ratio_all = []
    for label, key, dec in [
            ("Current Ratio (times)", "current", 2),
            ("Quick Ratio (times)", "quick", 2),
            ("Absolute Cash Ratio (times)", "cash", 2),
            ("Gross Contribution Margin (%)", "gross_margin", 2),
            ("EBITDA Margin (%)", "ebitda_margin", 2),
            ("Operating Margin (%)", "operating_margin", 2),
            ("Net Profit Margin (%)", "net_margin", 2),
            ("Return on Equity (%)", "roe", 2),
            ("Return on Capital Employed (%)", "roce", 2),
            ("Return on Total Assets (%)", "rota", 2),
            ("Debt-Equity Ratio (times)", "debt_equity", 2),
            ("Interest Coverage (times)", "interest_cover", 2),
            ("Proprietary Ratio (%)", "proprietary", 2),
            ("Total Asset Turnover (times)", "total_asset_turnover", 2),
            ("Fixed Asset Turnover (times)", "fixed_asset_turnover", 2),
            ("Working Capital Turnover (times)", "wc_turnover", 2),
            ("Equity Multiplier (times)", "equity_multiplier", 2)]:
        ratio_all.append([label] + [m(r[i][key], dec) for i in range(3)])
    for label, key, dec in [("Debtors Turnover (times)", "debtor_turnover", 2),
                            ("Collection Period (days)", "debtor_days", 1),
                            ("Creditors Turnover (times)", "creditor_turnover", 2),
                            ("Payment Period (days)", "creditor_days", 1),
                            ("Cash Conversion Cycle (days)", "cash_cycle", 1)]:
        ratio_all.append([label, EM] + [m(r[i][key], dec) for i in (1, 2)])

    return [
        ("chapter", None, "ANNEXURES",
         "Supporting statements, the questionnaire used during the "
         "internship, the daily diary and the certificates relied upon."),

        ("h2", "Annexure I " + EM + " Abridged Statement of Profit and Loss"),
        _table("A1.1", "Statement of Profit and Loss for three years (" + R +
               " in lakh)", _yr_cols("Particulars", 0.40), pl_rows,
               note="Indicative management figures. Reproduced from Table 4.1 "
                    "for ease of reference."),

        ("h2", "Annexure II " + EM + " Abridged Balance Sheet"),
        _table("A2.1", "Balance Sheet as at the close of each year (" + R +
               " in lakh)", _yr_cols("Particulars", 0.40),
               [(["I.  EQUITY AND LIABILITIES", "", "", ""], "group")] +
               [[n] + [m(v) for v in fd.bs(n)] for n, *_x in fd.EQUITY_LIAB] +
               [(["Total"] + [m(v) for v in fd.balance_total()], "total"),
                (["II.  ASSETS", "", "", ""], "group")] +
               [[n] + [m(v) for v in fd.bs(n)] for n, *_x in fd.ASSETS] +
               [(["Total"] + [m(v) for v in fd.assets_total()], "total")],
               font_scale=0.94),
        ("pagebreak",),

        ("h2", "Annexure III " + EM + " Consolidated Ratio Schedule"),
        _table("A3.1", "All ratios computed in this report",
               _yr_cols("Ratio", 0.44), ratio_all, font_scale=0.90,
               note="Activity ratios involving receivables and payables are "
                    "computed on average balances and are therefore not "
                    "available for the first year. All other ratios are "
                    "computed on closing balances."),
        ("pagebreak",),

        ("h2", "Annexure IV " + EM + " Cash Flow Statement"),
        _table("A4.1", "Cash Flow Statement for " + Y[2] + " (" + R +
               " in lakh)",
               [("Particulars", 0.64, "l"), ("Amount", 0.18, "r"),
                ("Total", 0.18, "r")],
               [(["A.  Operating Activities", "", ""], "group"),
                ["Profit before tax", m(cf["pbt"]), ""],
                ["Adjustments for depreciation and finance cost",
                 m(cf["dep"] + cf["fin"]), ""],
                ["Less: other income", "(" + m(cf["other_income"]) + ")", ""],
                (["Operating profit before working capital changes",
                  m(cf["op_before_wc"]), ""], "total"),
                ["Net change in working capital",
                 "(" + m(abs(cf["cash_from_ops"] - cf["op_before_wc"])) + ")",
                 ""],
                ["Income tax paid", "(" + m(cf["tax_paid"]) + ")", ""],
                (["Net cash from operating activities", "", m(cf["net_op"])],
                 "total"),
                (["B.  Investing Activities", "", ""], "group"),
                ["Capital expenditure", "(" + m(cf["capex"]) + ")", ""],
                ["Investments made", "(" + m(cf["d_inv"]) + ")", ""],
                ["Other income received", m(cf["other_income"]), ""],
                (["Net cash used in investing activities", "",
                  "(" + m(abs(cf["net_inv"])) + ")"], "total"),
                (["C.  Financing Activities", "", ""], "group"),
                ["Net movement in borrowings",
                 "(" + m(abs(cf["d_ltb"] + cf["d_stb"])) + ")", ""],
                ["Finance cost paid", "(" + m(cf["fin"]) + ")", ""],
                (["Net cash used in financing activities", "",
                  "(" + m(abs(cf["net_fin"])) + ")"], "total"),
                (["Net increase in cash", "", m(cf["net_change"])], "total"),
                ["Opening cash and bank balances", "", m(cf["opening"])],
                (["Closing cash and bank balances", "", m(cf["closing"])],
                 "total")],
               font_scale=0.93),

        ("h2", "Annexure V " + EM + " Cost-Volume-Profit Working"),
        _table("A5.1", "Fixed and variable cost segregation for " + Y[2] +
               " (" + R + " in lakh)",
               [("Head", 0.34, "l"), ("Total", 0.16, "r"),
                ("Variable", 0.16, "r"), ("Fixed", 0.16, "r"),
                ("Basis", 0.18, "c")],
               [[h, m(v + f), m(v), m(f),
                 "Variable" if f == 0 else ("Fixed" if v == 0 else "Split")]
                for h, v, f in fd.COST_SPLIT] +
               [(["Total", m(fd.total_expenses()[2]), m(fd.variable_cost()),
                  m(fd.fixed_cost()), ""], "total")],
               font_scale=0.93,
               note="Contribution " + rs(fd.contribution()) + " lakh; "
                    "profit-volume ratio " + pc(fd.pv_ratio()) + "; "
                    "break-even sales " + rs(fd.bep_sales()) + " lakh; "
                    "margin of safety " + rs(fd.margin_of_safety()) +
                    " lakh (" + pc(fd.mos_ratio()) + ")."),
        ("pagebreak",),

        ("h2", "Annexure VI " + EM + " Questionnaire Used during the "
                "Internship"),
        ("p", "The following structured questions were put to the management, "
         "the company mentor and the accounts team during the internship. "
         "Responses were recorded in the working papers and are reflected in "
         "the analysis; individual responses are not reproduced, in keeping "
         "with the confidentiality undertaking described in Section 8.5."),
        ("h3", "Part A " + EM + " Organisation and the Finance Function"),
        ("numbers", [
            "What are the principal service lines and how does each generate "
            "revenue?",
            "How is the finance and accounts function organised and to whom "
            "does it report?",
            "What books of account and subsidiary registers are maintained, "
            "and in what form?",
            "What are the delegated approval limits for expenditure, and how "
            "are they evidenced?",
            "Which activities are performed in-house and which with "
            "professional assistance?",
        ]),
        ("h3", "Part B " + EM + " Revenue, Collection and Receivables"),
        ("numbers", [
            "On what terms is each service line sold " + EM + " in advance, "
            "on delivery or on credit?",
            "How are payment gateway settlements reconciled with recorded "
            "collections, and how frequently?",
            "Is there a written credit policy for institutional clients? If "
            "not, how are credit limits determined?",
            "How is an overdue receivable followed up, and at what point is "
            "it escalated?",
            "Is any provision made for doubtful debts, and on what basis?",
            "What proportion of revenue is contracted in advance at the start "
            "of a financial year?",
        ]),
        ("h3", "Part C " + EM + " Budgeting and Cost Control"),
        ("numbers", [
            "How is the annual budget prepared, and which functions "
            "participate?",
            "On what basis is the marketing provision determined?",
            "How frequently is actual performance compared against budget, "
            "and by whom?",
            "Is any individual formally accountable for a named budget head?",
            "Is a cash budget prepared? If not, how is the lean quarter "
            "planned for?",
            "Which costs are regarded by management as fixed and which as "
            "variable, and why?",
            "What specific cost control measures have been introduced in the "
            "last three years, and what effect have they had?",
        ]),
        ("h3", "Part D " + EM + " Financing, Investment and Performance"),
        ("numbers", [
            "How has growth been financed over the last three years?",
            "What is the policy on borrowing, and has a working capital limit "
            "been considered?",
            "How are capital expenditure proposals evaluated and approved?",
            "Which financial indicators does management actually monitor, and "
            "at what interval?",
            "What does management regard as the principal financial risk "
            "facing the business?",
            "How is the seasonality of enrolment planned for financially?",
        ]),
        ("pagebreak",),

        ("h2", "Annexure VII " + EM + " Weekly Diary of Work Performed"),
        _table("A7.1", "Weekly record of work, deliverables and review",
               [("Week", 0.09, "l"), ("Dates", 0.17, "l"),
                ("Work performed", 0.46, "l"), ("Reviewed", 0.12, "c"),
                ("Chapter", 0.16, "c")],
               [[wk, dates, detail, "Saturday",
                 {"Week 1": "2, 3", "Week 2": "3, 4", "Week 3": "4, 6",
                  "Week 4": "5", "Week 5": "6", "Week 6": "5",
                  "Week 7": "9, 10"}.get(wk, "")]
                for wk, dates, _focus, detail in fd.WEEKLY_PLAN],
               font_scale=0.86,
               note="The weekly review with the company mentor was held every "
                    "Saturday. The final column records the chapter of this "
                    "report into which the week's work fed."),
        ("pagebreak",),

        ("h2", "Annexure VIII " + EM + " Attendance and Certification Record"),
        _table("A8.1", "Summary of attendance",
               [("Particulars", 0.56, "l"), ("Details", 0.44, "l")],
               [["Date of commencement", brand.INTERN_FROM],
                ["Date of completion", brand.INTERN_TO],
                ["Total calendar period", brand.INTERN_DAYS],
                ["Effective duration", brand.INTERN_WEEKS],
                ["Working pattern", "Monday to Saturday"],
                ["Reporting frequency", "Weekly review every Saturday with "
                 "the company mentor"],
                ["Function", "Finance and Accounts"],
                ["Place of work", brand.COMPANY_ADDR1 + ", Patna"],
                [("Certificate issued"), "Certificate of Completion, "
                 "reproduced in the front matter of this report"]]),
        ("spacer", 14),
        ("h2", "Annexure IX " + EM + " List of Exhibits Generated"),
        ("p", "Twenty exhibits were prepared from the organisation's records "
         "during the internship. Each is listed in the List of Figures in the "
         "front matter, together with the page on which it appears. The "
         "underlying computations are held in the working papers and were "
         "reviewed by the company mentor before inclusion."),
        ("spacer", 10),
        ("callout", "info", "Declaration Regarding the Annexures",
         "All statements reproduced in these annexures have been prepared by "
         "the candidate from records made available by " +
         brand.COMPANY_LEGAL + " for the limited purpose of this academic "
         "study. They are indicative management figures and do not constitute "
         "audited statutory accounts. No confidential client, candidate or "
         "mentor-specific information has been reproduced."),
        ("spacer", 24),
        ("signatures", [("", brand.STUDENT_NAME.title()),
                        ("", "Roll No. " + brand.ROLL_NO + "   |   Reg. No. " +
                         brand.REG_NO)]),
    ]


# ============================================================== ASSEMBLY ==
CHAPTERS = [
    ("Executive Summary", None),
    ("Introduction", "1"),
    ("Company Profile", "2"),
    ("Internship Tasks", "3"),
    ("Financial Management Analysis", "4"),
    ("Budgeting and Cost Control", "5"),
    ("Ratio and Financial Analysis", "6"),
    ("Learning Outcomes", "7"),
    ("Challenges Faced", "8"),
    ("Findings and Suggestions", "9"),
    ("Conclusion", "10"),
    ("Bibliography", None),
    ("Annexures", None),
]


def build():
    """Return the complete ordered block list for the report."""
    fd.self_check()
    blocks = []
    blocks += front_matter()
    blocks += chapter_one()
    blocks += chapter_two()
    blocks += chapter_three()
    blocks += chapter_four()
    blocks += chapter_five()
    blocks += chapter_six()
    blocks += chapter_seven()
    blocks += chapter_eight()
    blocks += chapter_nine()
    blocks += chapter_ten()
    blocks += bibliography()
    blocks += annexures()
    # A trailing page break before the final page is unnecessary.
    while blocks and blocks[-1] == ("pagebreak",):
        blocks.pop()
    return blocks


def stats(blocks=None):
    blocks = blocks if blocks is not None else build()
    counts = {}
    words = 0
    for blk in blocks:
        counts[blk[0]] = counts.get(blk[0], 0) + 1
        for part in blk[1:]:
            if isinstance(part, str):
                words += len(part.split())
            elif isinstance(part, list):
                for it in part:
                    if isinstance(it, str):
                        words += len(it.split())
                    elif isinstance(it, (list, tuple)):
                        for sub in it:
                            if isinstance(sub, str):
                                words += len(sub.split())
    return counts, words


if __name__ == "__main__":
    bl = build()
    counts, words = stats(bl)
    print("blocks: %d   approx words: %d" % (len(bl), words))
    for k in sorted(counts, key=lambda x: -counts[x]):
        print("  %-16s %d" % (k, counts[k]))
