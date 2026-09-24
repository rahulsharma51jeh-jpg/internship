"""
Builds every chart used in the report and returns a name -> PNG-bytes mapping.

Each exhibit is numbered so the figure captions in content.py and the
List of Figures stay in step with the images actually generated.
"""

import brand
import charts
import findata as fd
import logo

LAKH = "\u20b9 Lakh"


def _cat_years():
    return ["FY 2023-24", "FY 2024-25", "FY 2025-26"]


def build_all(width=1200):
    ex = {}
    h = int(width * 0.60)

    # --- Fig 1: revenue and profit growth -----------------------------------
    ex["fig01_revenue_growth"] = charts.combo_bar_line(
        "Revenue from Operations and Net Profit Margin",
        _cat_years(), "Revenue from Operations", fd.revenue(),
        "Net Profit Margin", [fd.ratio_set(i)["net_margin"] for i in range(3)],
        subtitle="Turnover has grown at a compound annual rate of 49.2 per cent "
                 "while the net margin has widened steadily",
        y_title=LAKH, y2_title="Per cent", bar_dec=2,
        note="Source: Compiled from the management accounts of Infinitya1 "
             "Career Counselling Private Limited (indicative figures).",
        width=width, height=h)

    # --- Fig 2: income and expenditure -------------------------------------
    ex["fig02_income_expense"] = charts.grouped_bars(
        "Total Income against Total Expenditure",
        _cat_years(),
        [("Total Income", fd.total_income()),
         ("Total Expenses", fd.total_expenses()),
         ("Profit Before Tax", fd.pbt())],
        subtitle="The widening gap between the first two columns is the source "
                 "of the improvement in profitability",
        y_title=LAKH, value_dec=2, width=width, height=h,
        colours=[brand.NAVY, brand.ORANGE, brand.GREEN],
        note="Figures in \u20b9 lakh. Profit before tax is total income less "
             "total expenditure.")

    # --- Fig 3: revenue mix -------------------------------------------------
    ex["fig03_revenue_mix"] = charts.donut(
        "Composition of Revenue by Service Line, FY 2025-26",
        [l for l, _v in fd.REVENUE_MIX], [v for _l, v in fd.REVENUE_MIX],
        subtitle="Paid internship programmes contribute a little over half of "
                 "total turnover",
        unit_label=" L", value_dec=2, centre_label="TOTAL",
        centre_value="\u20b9 214.60 L", width=width, height=h,
        colours=[brand.NAVY, brand.ORANGE, brand.BLUE_LIGHT, brand.TEAL,
                 brand.PURPLE],
        note="Percentages are of revenue from operations for FY 2025-26.")

    # --- Fig 4: cost structure ---------------------------------------------
    heads = [h_ for h_ in fd.EXPENSE_HEADS]
    ex["fig04_cost_structure"] = charts.h_bars(
        "Structure of Total Expenditure, FY 2025-26",
        [h_.replace(" & ", " and ") for h_ in heads],
        [fd.pl(h_)[2] for h_ in heads],
        subtitle="Direct programme cost and employee benefits together absorb "
                 "roughly two-thirds of total expenditure",
        value_dec=2, suffix=" L", sort=True, width=width, height=h,
        note="Total expenditure for FY 2025-26 is \u20b9 193.30 lakh.")

    # --- Fig 5: expense trend (stacked) ------------------------------------
    ex["fig05_expense_trend"] = charts.stacked_bars(
        "Behaviour of Major Expense Heads over Three Years",
        _cat_years(),
        [("Direct Programme Cost", fd.pl("Direct Programme Cost")),
         ("Employee Benefits", fd.pl("Employee Benefit Expenses")),
         ("Marketing & Promotion", fd.pl("Marketing & Digital Promotion")),
         ("Administration", fd.pl("Administrative & Office Expenses")),
         ("Technology", fd.pl("Technology & Platform Expenses")),
         ("Finance & Depreciation",
          [round(fd.pl("Finance Cost")[i] +
                 fd.pl("Depreciation & Amortisation")[i], 2)
           for i in range(3)])],
        subtitle="Absolute costs rise with scale, but the mix remains stable, "
                 "indicating a repeatable delivery model",
        y_title=LAKH, value_dec=1, width=width, height=h,
        colours=[brand.NAVY, brand.ORANGE, brand.BLUE_LIGHT, brand.TEAL,
                 brand.PURPLE, brand.GREY],
        note="Figures in \u20b9 lakh.")

    # --- Fig 6: quarterly seasonality --------------------------------------
    ex["fig06_seasonality"] = charts.line_chart(
        "Quarterly Pattern of Revenue, FY 2025-26",
        [l for l, _v in fd.QUARTERLY], [("Revenue", [v for _l, v in fd.QUARTERLY])],
        subtitle="Collections peak in the first quarter, when the summer "
                 "internship cycle opens",
        y_title=LAKH, value_dec=2, area=True, width=width, height=h,
        note="The third quarter is the leanest period and drives the need for "
             "a cash buffer.")

    # --- Fig 7: budget variance -------------------------------------------
    rows = [r for r in fd.BUDGET if r[0] != "Other Income"]
    ex["fig07_budget_variance"] = charts.variance_bars(
        "Budget against Actual: Percentage Variance, FY 2025-26",
        [r[0].replace(" & ", " and ") for r in rows],
        [fd.budget_variance(r)[1] for r in rows],
        subtitle="Positive bars are favourable; marketing and direct programme "
                 "cost are the two heads that overshot",
        width=width, height=h,
        note="Variance is measured against the approved annual budget and "
             "signed so that a favourable outcome is positive.")

    # --- Fig 8: budget vs actual amounts ----------------------------------
    ex["fig08_budget_amounts"] = charts.grouped_bars(
        "Budgeted and Actual Amounts by Head, FY 2025-26",
        ["Revenue", "Direct\nProgramme", "Employee\nBenefits",
         "Marketing", "Admini-\nstration", "Technology"],
        [("Budget", [205.00, 76.00, 54.00, 30.00, 14.50, 9.00]),
         ("Actual", [214.60, 79.30, 52.80, 33.10, 13.60, 9.40])],
        subtitle="Revenue exceeded target, yet two cost heads also exceeded "
                 "their approved provision",
        y_title=LAKH, value_dec=2, width=width, height=h,
        colours=[brand.BLUE_LIGHT, brand.NAVY],
        note="Figures in \u20b9 lakh.")

    # --- Fig 9: liquidity ratios ------------------------------------------
    ex["fig09_liquidity"] = charts.grouped_bars(
        "Liquidity Ratios over Three Years",
        _cat_years(),
        [("Current Ratio", [fd.ratio_set(i)["current"] for i in range(3)]),
         ("Quick Ratio", [fd.ratio_set(i)["quick"] for i in range(3)]),
         ("Absolute Cash Ratio", [fd.ratio_set(i)["cash"] for i in range(3)])],
        subtitle="Short-term solvency is adequate and improving, though still "
                 "below the conventional 2:1 benchmark",
        y_title="Times", value_dec=2, width=width, height=h,
        colours=[brand.NAVY, brand.ORANGE, brand.TEAL],
        note="Computed on closing balance sheet figures.")

    # --- Fig 10: profitability margins ------------------------------------
    ex["fig10_margins"] = charts.line_chart(
        "Profitability Margins over Three Years",
        _cat_years(),
        [("Gross Contribution Margin",
          [fd.ratio_set(i)["gross_margin"] for i in range(3)]),
         ("EBITDA Margin", [fd.ratio_set(i)["ebitda_margin"] for i in range(3)]),
         ("Operating Margin",
          [fd.ratio_set(i)["operating_margin"] for i in range(3)]),
         ("Net Profit Margin", [fd.ratio_set(i)["net_margin"] for i in range(3)])],
        subtitle="Every margin has improved, and the widening gap between the "
                 "gross and net lines is narrowing as overheads are absorbed",
        y_title="Per cent", value_dec=2, suffix="", width=width, height=h,
        colours=[brand.NAVY, brand.TEAL, brand.ORANGE, brand.GREEN],
        note="Margins expressed as a percentage of revenue from operations.")

    # --- Fig 11: return ratios --------------------------------------------
    ex["fig11_returns"] = charts.grouped_bars(
        "Return on Equity and Return on Capital Employed",
        _cat_years(),
        [("Return on Equity", [fd.ratio_set(i)["roe"] for i in range(3)]),
         ("Return on Capital Employed",
          [fd.ratio_set(i)["roce"] for i in range(3)]),
         ("Return on Total Assets", [fd.ratio_set(i)["rota"] for i in range(3)])],
        subtitle="Returns have more than doubled, helped by both margin "
                 "expansion and a lighter asset base",
        y_title="Per cent", value_dec=2, width=width, height=h,
        colours=[brand.NAVY, brand.ORANGE, brand.BLUE_LIGHT],
        note="Return on equity is computed on closing shareholders' funds.")

    # --- Fig 12: solvency --------------------------------------------------
    ex["fig12_solvency"] = charts.combo_bar_line(
        "Debt-Equity Ratio and Interest Coverage",
        _cat_years(), "Debt-Equity Ratio (times)",
        [fd.ratio_set(i)["debt_equity"] for i in range(3)],
        "Interest Coverage (times)",
        [fd.ratio_set(i)["interest_cover"] for i in range(3)],
        subtitle="Gearing has fallen sharply while the cushion available to "
                 "service interest has more than tripled",
        y_title="Times", y2_title="Times", bar_dec=2, line_dec=2,
        line_suffix="", width=width, height=h,
        note="A falling debt-equity ratio alongside rising interest cover "
             "indicates strengthening solvency.")

    # --- Fig 13: activity / turnover --------------------------------------
    ex["fig13_turnover"] = charts.grouped_bars(
        "Activity Ratios: Asset Utilisation",
        _cat_years(),
        [("Total Asset Turnover",
          [fd.ratio_set(i)["total_asset_turnover"] for i in range(3)]),
         ("Fixed Asset Turnover",
          [fd.ratio_set(i)["fixed_asset_turnover"] for i in range(3)]),
         ("Working Capital Turnover",
          [fd.ratio_set(i)["wc_turnover"] for i in range(3)])],
        subtitle="The company generates between two and eleven rupees of "
                 "revenue for every rupee deployed, depending on the base used",
        y_title="Times", value_dec=2, width=width, height=h,
        colours=[brand.NAVY, brand.TEAL, brand.ORANGE],
        note="Working capital turnover is high because the business carries no "
             "inventory.")

    # --- Fig 14: working capital cycle ------------------------------------
    r2 = fd.ratio_set(2)
    r1 = fd.ratio_set(1)
    ex["fig14_cycle"] = charts.grouped_bars(
        "Debtor Days, Creditor Days and the Cash Conversion Cycle",
        ["FY 2024-25", "FY 2025-26"],
        [("Debtor Days", [r1["debtor_days"], r2["debtor_days"]]),
         ("Creditor Days", [r1["creditor_days"], r2["creditor_days"]]),
         ("Cash Conversion Cycle",
          [r1["cash_cycle"], r2["cash_cycle"]])],
        subtitle="Because suppliers are paid later than customers pay, the "
                 "cash conversion cycle is negative - a structural advantage",
        y_title="Days", value_dec=1, width=width, height=h,
        colours=[brand.ORANGE, brand.NAVY, brand.TEAL],
        note="A negative cycle means operations are partly financed by trade "
             "credit rather than by the company's own funds.")

    # --- Fig 15: break-even -----------------------------------------------
    ex["fig15_breakeven"] = charts.breakeven(
        "Cost-Volume-Profit Chart, FY 2025-26",
        sales_max=260.0, fixed=fd.fixed_cost(),
        pv_ratio=fd.pv_ratio() / 100.0, actual_sales=fd.revenue()[2],
        subtitle="Break-even sales of \u20b9 174.76 lakh leave a margin of "
                 "safety of 18.56 per cent of turnover",
        width=width, height=h,
        note="Fixed cost \u20b9 93.39 lakh; profit-volume ratio 53.44 per cent.")

    # --- Fig 16: cost behaviour split -------------------------------------
    ex["fig16_cost_behaviour"] = charts.stacked_bars(
        "Segregation of Costs into Variable and Fixed, FY 2025-26",
        [r[0].replace(" & ", " and ").replace(" Expenses", "")
            .replace("Administrative and Office", "Admin")
            .replace("Technology and Platform", "Technology")
            .replace("Marketing and Digital Promotion", "Marketing")
            .replace("Direct Programme Cost", "Direct\nProgramme")
            .replace("Employee Benefit", "Employee")
            .replace("Depreciation and Amortisation", "Depreciation")
         for r in fd.COST_SPLIT],
        [("Variable Portion", [r[1] for r in fd.COST_SPLIT]),
         ("Fixed Portion", [r[2] for r in fd.COST_SPLIT])],
        subtitle="Only programme delivery cost is wholly variable; most other "
                 "heads are committed in nature",
        y_title=LAKH, value_dec=1, width=width, height=h,
        colours=[brand.ORANGE, brand.NAVY], show_total=False,
        note="Variable cost \u20b9 99.91 lakh; fixed cost \u20b9 93.39 lakh.")

    # --- Fig 17: cash flow waterfall --------------------------------------
    cf = fd.cash_flow()
    ex["fig17_cash_bridge"] = charts.waterfall(
        "Cash Flow Bridge, FY 2025-26",
        ["Operating\nProfit", "Working\nCapital", "Tax\nPaid",
         "Capital\nExpenditure", "Invest-\nments", "Other\nIncome",
         "Net\nBorrowings", "Finance\nCost"],
        [cf["op_before_wc"],
         round(cf["cash_from_ops"] - cf["op_before_wc"], 2),
         -cf["tax_paid"], -cf["capex"], -cf["d_inv"], cf["other_income"],
         round(cf["d_ltb"] + cf["d_stb"], 2), -cf["fin"]],
        subtitle="Operations funded the entire capital programme and still left "
                 "\u20b9 10.41 lakh of additional cash on the balance sheet",
        start_label="Opening\nCash", start_value=cf["opening"],
        end_label="Closing\nCash", y_title=LAKH, value_dec=2,
        width=width, height=h,
        note="Derived from the FY 2025-26 cash flow statement prepared under "
             "the indirect method.")

    # --- Fig 18: DuPont ----------------------------------------------------
    ex["fig18_dupont"] = charts.grouped_bars(
        "DuPont Decomposition of Return on Equity",
        _cat_years(),
        [("Net Profit Margin (%)",
          [fd.dupont(i)["net_margin"] for i in range(3)]),
         ("Total Asset Turnover (times)",
          [fd.dupont(i)["asset_turnover"] for i in range(3)]),
         ("Equity Multiplier (times)",
          [fd.dupont(i)["equity_multiplier"] for i in range(3)])],
        subtitle="Margin improvement, not additional leverage, is what has "
                 "driven return on equity higher",
        value_dec=2, width=width, height=h,
        colours=[brand.ORANGE, brand.TEAL, brand.NAVY],
        note="Return on equity is the product of the three components; the "
             "equity multiplier has fallen, so gearing is not the driver.")

    # --- Fig 19: headline gauges ------------------------------------------
    ex["fig19_scorecard"] = charts.gauge_row(
        "Financial Scorecard at a Glance, FY 2025-26",
        [("Current Ratio", r2["current"], 0.0, 2.5, 2.0, 2),
         ("Net Margin %", r2["net_margin"], 0.0, 15.0, 10.0, 2),
         ("ROCE %", r2["roce"], 0.0, 60.0, 25.0, 2),
         ("Debt-Equity", r2["debt_equity"], 0.0, 1.5, 0.50, 2),
         ("Interest Cover", r2["interest_cover"], 0.0, 20.0, 5.0, 2)],
        subtitle="The black needle on each dial marks the benchmark adopted "
                 "for this study",
        width=width,
        note="Benchmarks are conventional rules of thumb used for "
             "interpretation and are not industry averages.")

    # --- Fig 20: shareholders' funds vs debt ------------------------------
    ex["fig20_funding"] = charts.stacked_bars(
        "Pattern of Long-term Funding",
        _cat_years(),
        [("Share Capital", fd.bs("Share Capital")),
         ("Reserves & Surplus", fd.bs("Reserves & Surplus")),
         ("Long-term Borrowings", fd.bs("Long-term Borrowings"))],
        subtitle="Retained earnings have replaced borrowing as the principal "
                 "source of long-term finance",
        y_title=LAKH, value_dec=2, width=width, height=h,
        colours=[brand.NAVY, brand.BLUE_LIGHT, brand.ORANGE],
        note="Capital employed rose from \u20b9 24.35 lakh to \u20b9 49.41 "
             "lakh over the period.")

    # --- Brand assets ------------------------------------------------------
    ex["logo_lockup"] = logo.render_lockup(1200)
    ex["logo_mark"] = logo.render_mark(760)
    ex["logo_mark_mono"] = logo.render_mark(760, bg=brand.NAVY_DEEP, mono=True)

    # Charts are flat artwork, so an indexed palette is visually lossless and
    # roughly a quarter of the size of truecolour; the logo keeps its full
    # colour range because of the gradient in the ribbon.
    out = {}
    for k, v in ex.items():
        if not hasattr(v, "to_png"):
            out[k] = v
        elif k.startswith("logo"):
            out[k] = v.to_png()
        else:
            out[k] = v.to_png(indexed=True)
    return out, ex


FIGURE_ORDER = [
    ("fig01_revenue_growth", "Revenue from Operations and Net Profit Margin"),
    ("fig02_income_expense", "Total Income against Total Expenditure"),
    ("fig03_revenue_mix", "Composition of Revenue by Service Line, FY 2025-26"),
    ("fig04_cost_structure", "Structure of Total Expenditure, FY 2025-26"),
    ("fig05_expense_trend", "Behaviour of Major Expense Heads over Three Years"),
    ("fig06_seasonality", "Quarterly Pattern of Revenue, FY 2025-26"),
    ("fig07_budget_variance",
     "Budget against Actual: Percentage Variance, FY 2025-26"),
    ("fig08_budget_amounts", "Budgeted and Actual Amounts by Head, FY 2025-26"),
    ("fig09_liquidity", "Liquidity Ratios over Three Years"),
    ("fig10_margins", "Profitability Margins over Three Years"),
    ("fig11_returns", "Return on Equity and Return on Capital Employed"),
    ("fig12_solvency", "Debt-Equity Ratio and Interest Coverage"),
    ("fig13_turnover", "Activity Ratios: Asset Utilisation"),
    ("fig14_cycle", "Debtor Days, Creditor Days and the Cash Conversion Cycle"),
    ("fig15_breakeven", "Cost-Volume-Profit Chart, FY 2025-26"),
    ("fig16_cost_behaviour",
     "Segregation of Costs into Variable and Fixed, FY 2025-26"),
    ("fig17_cash_bridge", "Cash Flow Bridge, FY 2025-26"),
    ("fig18_dupont", "DuPont Decomposition of Return on Equity"),
    ("fig19_scorecard", "Financial Scorecard at a Glance, FY 2025-26"),
    ("fig20_funding", "Pattern of Long-term Funding"),
]


if __name__ == "__main__":
    import os
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "/projects/sandbox/build/charts"
    os.makedirs(out, exist_ok=True)
    fd.self_check()
    pngs, _cv = build_all()
    for name, data in pngs.items():
        with open(os.path.join(out, name + ".png"), "wb") as fh:
            fh.write(data)
    print("wrote %d images to %s" % (len(pngs), out))
