"""
The financial data set used throughout the report.

All figures are in Rupees lakh and are *indicative* management figures compiled
by the intern during the internship for academic analysis only; they are not
audited statutory accounts. Every derived figure in the report is computed from
this single module so the Profit & Loss, Balance Sheet, Cash Flow, ratio tables
and charts can never disagree with one another. The self-check at the bottom is
run by build.py before any document is produced.
"""

YEARS = ["FY 2023-24", "FY 2024-25", "FY 2025-26"]
YEARS_SHORT = ["FY24", "FY25", "FY26"]
TAX_RATE = 0.25

# ------------------------------------------------- statement of profit & loss ----
PL = [
    # (line item, FY24, FY25, FY26)
    ("Revenue from Operations",            96.40, 148.75, 214.60),
    ("Other Income",                        1.20,   2.05,   3.40),
    ("Direct Programme Cost",              38.20,  56.90,  79.30),
    ("Employee Benefit Expenses",          24.60,  37.40,  52.80),
    ("Marketing & Digital Promotion",      14.80,  22.60,  33.10),
    ("Administrative & Office Expenses",    7.90,  10.20,  13.60),
    ("Technology & Platform Expenses",      4.60,   6.80,   9.40),
    ("Finance Cost",                        1.10,   1.40,   1.60),
    ("Depreciation & Amortisation",         2.20,   2.80,   3.50),
]
_PL = {k: v for (k, *v) in [(r[0], r[1], r[2], r[3]) for r in PL]}

EXPENSE_HEADS = [
    "Direct Programme Cost",
    "Employee Benefit Expenses",
    "Marketing & Digital Promotion",
    "Administrative & Office Expenses",
    "Technology & Platform Expenses",
    "Finance Cost",
    "Depreciation & Amortisation",
]


def pl(item):
    return _PL[item]


def revenue():
    return _PL["Revenue from Operations"]


def other_income():
    return _PL["Other Income"]


def total_income():
    return [a + b for a, b in zip(revenue(), other_income())]


def total_expenses():
    return [sum(_PL[h][i] for h in EXPENSE_HEADS) for i in range(3)]


def pbt():
    return [round(a - b, 2) for a, b in zip(total_income(), total_expenses())]


def tax():
    return [round(v * TAX_RATE, 2) for v in pbt()]


def pat():
    return [round(a - b, 2) for a, b in zip(pbt(), tax())]


def ebit():
    """Earnings before interest and tax, inclusive of other income."""
    return [round(p + f, 2) for p, f in zip(pbt(), _PL["Finance Cost"])]


def ebitda():
    return [round(e + d, 2)
            for e, d in zip(ebit(), _PL["Depreciation & Amortisation"])]


def contribution_gross():
    """Revenue less direct programme cost."""
    return [round(r - d, 2)
            for r, d in zip(revenue(), _PL["Direct Programme Cost"])]


# ------------------------------------------------------------- balance sheet ----
EQUITY_LIAB = [
    ("Share Capital",                      10.00, 10.00, 10.00),
    ("Reserves & Surplus",                  4.85, 14.38, 32.91),
    ("Long-term Borrowings",                9.50,  8.00,  6.50),
    ("Short-term Borrowings",               3.20,  4.10,  4.60),
    ("Trade Payables",                      7.40, 11.30, 15.80),
    ("Other Current Liabilities & Provisions", 5.05, 7.62, 10.70),
]
ASSETS = [
    ("Property, Plant & Equipment",         8.60, 10.40, 13.20),
    ("Intangible Assets (Platform/Software)", 3.40, 4.60,  6.80),
    ("Non-current Investments",             1.00,  1.50,  2.00),
    ("Trade Receivables",                  11.80, 16.90, 23.10),
    ("Cash & Bank Balances",                9.70, 14.20, 24.61),
    ("Short-term Loans & Advances",         2.90,  4.10,  5.80),
    ("Other Current Assets",                2.60,  3.70,  5.00),
]
_EL = {r[0]: list(r[1:]) for r in EQUITY_LIAB}
_AS = {r[0]: list(r[1:]) for r in ASSETS}

CURRENT_ASSET_HEADS = ["Trade Receivables", "Cash & Bank Balances",
                       "Short-term Loans & Advances", "Other Current Assets"]
CURRENT_LIAB_HEADS = ["Short-term Borrowings", "Trade Payables",
                      "Other Current Liabilities & Provisions"]


def bs(item):
    return _EL.get(item) or _AS[item]


def balance_total():
    return [round(sum(_EL[k][i] for k in _EL), 2) for i in range(3)]


def assets_total():
    return [round(sum(_AS[k][i] for k in _AS), 2) for i in range(3)]


def shareholders_funds():
    return [round(_EL["Share Capital"][i] + _EL["Reserves & Surplus"][i], 2)
            for i in range(3)]


def current_assets():
    return [round(sum(_AS[k][i] for k in CURRENT_ASSET_HEADS), 2)
            for i in range(3)]


def current_liabilities():
    return [round(sum(_EL[k][i] for k in CURRENT_LIAB_HEADS), 2)
            for i in range(3)]


def quick_assets():
    return [round(current_assets()[i] - _AS["Other Current Assets"][i], 2)
            for i in range(3)]


def working_capital():
    return [round(a - b, 2)
            for a, b in zip(current_assets(), current_liabilities())]


def total_debt():
    return [round(_EL["Long-term Borrowings"][i] +
                  _EL["Short-term Borrowings"][i], 2) for i in range(3)]


def capital_employed():
    return [round(shareholders_funds()[i] + _EL["Long-term Borrowings"][i], 2)
            for i in range(3)]


def net_fixed_assets():
    return [round(_AS["Property, Plant & Equipment"][i] +
                  _AS["Intangible Assets (Platform/Software)"][i], 2)
            for i in range(3)]


# -------------------------------------------------------------------- ratios ----
def _pct(a, b):
    return round(100.0 * a / b, 2)


def _times(a, b):
    return round(a / b, 2)


def ratio_set(i):
    """All headline ratios for year index i (0 = FY24 ... 2 = FY26)."""
    ca, cl = current_assets()[i], current_liabilities()[i]
    r = {
        "current": _times(ca, cl),
        "quick": _times(quick_assets()[i], cl),
        "cash": _times(bs("Cash & Bank Balances")[i], cl),
        "gross_margin": _pct(contribution_gross()[i], revenue()[i]),
        "ebitda_margin": _pct(ebitda()[i], revenue()[i]),
        "operating_margin": _pct(ebit()[i], revenue()[i]),
        "net_margin": _pct(pat()[i], revenue()[i]),
        "roe": _pct(pat()[i], shareholders_funds()[i]),
        "roce": _pct(ebit()[i], capital_employed()[i]),
        "rota": _pct(ebit()[i], assets_total()[i]),
        "debt_equity": _times(total_debt()[i], shareholders_funds()[i]),
        "interest_cover": _times(ebit()[i], pl("Finance Cost")[i]),
        "proprietary": _pct(shareholders_funds()[i], assets_total()[i]),
        "total_asset_turnover": _times(revenue()[i], assets_total()[i]),
        "fixed_asset_turnover": _times(revenue()[i], net_fixed_assets()[i]),
        "wc_turnover": _times(revenue()[i], working_capital()[i]),
        "equity_multiplier": _times(assets_total()[i],
                                    shareholders_funds()[i]),
    }
    if i > 0:
        avg_rec = (bs("Trade Receivables")[i - 1] +
                   bs("Trade Receivables")[i]) / 2.0
        avg_pay = (bs("Trade Payables")[i - 1] + bs("Trade Payables")[i]) / 2.0
        r["debtor_turnover"] = _times(revenue()[i], avg_rec)
        r["debtor_days"] = round(365.0 / r["debtor_turnover"], 1)
        r["creditor_turnover"] = _times(pl("Direct Programme Cost")[i], avg_pay)
        r["creditor_days"] = round(365.0 / r["creditor_turnover"], 1)
        r["cash_cycle"] = round(r["debtor_days"] - r["creditor_days"], 1)
    return r


def growth(series):
    """Year-on-year growth percentages; first year returns None."""
    out = [None]
    for i in range(1, len(series)):
        out.append(round(100.0 * (series[i] - series[i - 1]) /
                         series[i - 1], 2))
    return out


# --------------------------------------------------- revenue & cost analysis ----
REVENUE_MIX = [
    ("Paid Internship Programmes", 112.80),
    ("Career Counselling & Mentoring", 38.60),
    ("College & Corporate B2B Tie-ups", 34.90),
    ("Certification & Assessment", 18.40),
    ("Workshops, Webinars & Bootcamps", 9.90),
]

QUARTERLY = [("Q1\nApr-Jun", 62.30), ("Q2\nJul-Sep", 58.40),
             ("Q3\nOct-Dec", 41.20), ("Q4\nJan-Mar", 52.70)]

# Cost behaviour split for FY 2025-26 used in the CVP analysis.
COST_SPLIT = [
    # (head, variable portion, fixed portion)
    ("Direct Programme Cost",               79.30,  0.00),
    ("Employee Benefit Expenses",            0.00, 52.80),
    ("Marketing & Digital Promotion",       18.21, 14.89),
    ("Administrative & Office Expenses",     2.40, 11.20),
    ("Technology & Platform Expenses",       0.00,  9.40),
    ("Finance Cost",                         0.00,  1.60),
    ("Depreciation & Amortisation",          0.00,  3.50),
]


def variable_cost():
    return round(sum(r[1] for r in COST_SPLIT), 2)


def fixed_cost():
    return round(sum(r[2] for r in COST_SPLIT), 2)


def contribution():
    return round(revenue()[2] - variable_cost(), 2)


def pv_ratio():
    return round(100.0 * contribution() / revenue()[2], 2)


def bep_sales():
    return round(fixed_cost() / (pv_ratio() / 100.0), 2)


def margin_of_safety():
    return round(revenue()[2] - bep_sales(), 2)


def mos_ratio():
    return round(100.0 * margin_of_safety() / revenue()[2], 2)


def operating_leverage():
    """Contribution / EBIT measured before other income."""
    ebit_op = round(contribution() - (fixed_cost() - pl("Finance Cost")[2]), 2)
    return round(contribution() / ebit_op, 2), ebit_op


def financial_leverage():
    _dol, ebit_op = operating_leverage()
    return round(ebit_op / (ebit_op - pl("Finance Cost")[2]), 2)


# ------------------------------------------------------- budget vs actual ----
BUDGET = [
    # (head, budget, actual, favourable_when_lower)
    ("Revenue from Operations",           205.00, 214.60, False),
    ("Other Income",                        3.00,   3.40, False),
    ("Direct Programme Cost",              76.00,  79.30, True),
    ("Employee Benefit Expenses",          54.00,  52.80, True),
    ("Marketing & Digital Promotion",      30.00,  33.10, True),
    ("Administrative & Office Expenses",   14.50,  13.60, True),
    ("Technology & Platform Expenses",      9.00,   9.40, True),
    ("Finance Cost",                        1.80,   1.60, True),
    ("Depreciation & Amortisation",         3.50,   3.50, True),
]


def budget_variance(head_row):
    """Return (variance_amount, variance_pct) signed so + is favourable."""
    _h, bud, act, lower_is_good = head_row
    diff = (bud - act) if lower_is_good else (act - bud)
    pct = round(100.0 * diff / bud, 2) if bud else 0.0
    return round(diff, 2), pct


def budget_totals():
    exp = [r for r in BUDGET if r[3]]
    bud_exp = round(sum(r[1] for r in exp), 2)
    act_exp = round(sum(r[2] for r in exp), 2)
    bud_inc = round(BUDGET[0][1] + BUDGET[1][1], 2)
    act_inc = round(BUDGET[0][2] + BUDGET[1][2], 2)
    return {
        "budget_income": bud_inc, "actual_income": act_inc,
        "budget_expense": bud_exp, "actual_expense": act_exp,
        "budget_pbt": round(bud_inc - bud_exp, 2),
        "actual_pbt": round(act_inc - act_exp, 2),
    }


# ------------------------------------------------------ cash flow statement ----
def cash_flow():
    """FY 2025-26 indirect-method cash flow, derived from the two statements."""
    i, p = 2, 1
    d_rec = round(bs("Trade Receivables")[i] - bs("Trade Receivables")[p], 2)
    d_adv = round(bs("Short-term Loans & Advances")[i] -
                  bs("Short-term Loans & Advances")[p], 2)
    d_oca = round(bs("Other Current Assets")[i] -
                  bs("Other Current Assets")[p], 2)
    d_pay = round(bs("Trade Payables")[i] - bs("Trade Payables")[p], 2)
    d_ocl = round(bs("Other Current Liabilities & Provisions")[i] -
                  bs("Other Current Liabilities & Provisions")[p], 2)
    dep = pl("Depreciation & Amortisation")[i]
    fin = pl("Finance Cost")[i]
    oi = other_income()[i]

    op_before_wc = round(pbt()[i] + dep + fin - oi, 2)
    cash_from_ops = round(op_before_wc - d_rec - d_adv - d_oca + d_pay + d_ocl, 2)
    net_op = round(cash_from_ops - tax()[i], 2)

    capex = round(net_fixed_assets()[i] - net_fixed_assets()[p] + dep, 2)
    d_inv = round(bs("Non-current Investments")[i] -
                  bs("Non-current Investments")[p], 2)
    net_inv = round(-capex - d_inv + oi, 2)

    d_ltb = round(bs("Long-term Borrowings")[i] -
                  bs("Long-term Borrowings")[p], 2)
    d_stb = round(bs("Short-term Borrowings")[i] -
                  bs("Short-term Borrowings")[p], 2)
    net_fin = round(d_ltb + d_stb - fin, 2)

    net_change = round(net_op + net_inv + net_fin, 2)
    return {
        "pbt": pbt()[i], "dep": dep, "fin": fin, "other_income": oi,
        "op_before_wc": op_before_wc,
        "d_rec": d_rec, "d_adv": d_adv, "d_oca": d_oca,
        "d_pay": d_pay, "d_ocl": d_ocl,
        "cash_from_ops": cash_from_ops, "tax_paid": tax()[i],
        "net_op": net_op, "capex": capex, "d_inv": d_inv, "net_inv": net_inv,
        "d_ltb": d_ltb, "d_stb": d_stb, "net_fin": net_fin,
        "net_change": net_change,
        "opening": bs("Cash & Bank Balances")[p],
        "closing": bs("Cash & Bank Balances")[i],
    }


def dupont(i):
    r = ratio_set(i)
    prod = (r["net_margin"] / 100.0) * r["total_asset_turnover"] * \
        r["equity_multiplier"]
    return {
        "net_margin": r["net_margin"],
        "asset_turnover": r["total_asset_turnover"],
        "equity_multiplier": r["equity_multiplier"],
        "roe_reconstructed": round(100.0 * prod, 2),
        "roe_direct": r["roe"],
    }


# ------------------------------------------------------- internship diary ----
WEEKLY_PLAN = [
    ("Week 1", "08 Jun - 13 Jun 2026",
     "Induction, orientation and organisation study",
     "Company overview, service lines, reporting structure, statutory "
     "registrations, familiarisation with the accounting environment and the "
     "internal control checklist."),
    ("Week 2", "15 Jun - 20 Jun 2026",
     "Books of account and voucher verification",
     "Classification of vouchers, ledger scrutiny, receipt and payment "
     "posting, reconciliation of the payment-gateway statement with recorded "
     "collections."),
    ("Week 3", "22 Jun - 27 Jun 2026",
     "Working capital and receivables management",
     "Ageing of trade receivables, follow-up register for college tie-ups, "
     "computation of debtor days and preparation of a collection priority "
     "list."),
    ("Week 4", "29 Jun - 04 Jul 2026",
     "Budgeting and variance analysis",
     "Building the cohort-wise cost sheet, comparing budgeted and actual "
     "heads, quantifying variances and identifying controllable overspends."),
    ("Week 5", "06 Jul - 11 Jul 2026",
     "Ratio analysis and performance interpretation",
     "Computation of liquidity, profitability, solvency and activity ratios "
     "for three years, trend charts and DuPont decomposition of return on "
     "equity."),
    ("Week 6", "13 Jul - 18 Jul 2026",
     "Cost control study and CVP analysis",
     "Segregation of fixed and variable costs, contribution and P/V ratio, "
     "break-even sales, margin of safety and leverage computation."),
    ("Week 7", "20 Jul - 21 Jul 2026",
     "Report compilation and presentation",
     "Consolidation of findings, drafting of suggestions, review with the "
     "company mentor and presentation of the concluding summary."),
]


# --------------------------------------------------------------- self-check ----
def self_check():
    """Raise AssertionError if any statement fails to tie out."""
    errs = []

    for i in range(3):
        if abs(balance_total()[i] - assets_total()[i]) > 0.005:
            errs.append("Balance sheet does not balance in %s: %.2f vs %.2f"
                        % (YEARS[i], balance_total()[i], assets_total()[i]))

    # Reserves must roll forward by retained profit.
    res = bs("Reserves & Surplus")
    for i in (1, 2):
        expect = round(res[i - 1] + pat()[i], 2)
        if abs(res[i] - expect) > 0.005:
            errs.append("Reserves roll-forward broken in %s: %.2f vs %.2f"
                        % (YEARS[i], res[i], expect))

    # CVP split must reproduce total expenses.
    if abs(variable_cost() + fixed_cost() - total_expenses()[2]) > 0.005:
        errs.append("Cost split %.2f + %.2f != total expenses %.2f"
                    % (variable_cost(), fixed_cost(), total_expenses()[2]))
    for head, var, fix in COST_SPLIT:
        if abs(var + fix - pl(head)[2]) > 0.005:
            errs.append("Cost split for %s does not equal P&L amount" % head)

    # Contribution less fixed cost plus other income must equal PBT.
    chk = round(contribution() - fixed_cost() + other_income()[2], 2)
    if abs(chk - pbt()[2]) > 0.005:
        errs.append("CVP reconciliation: %.2f != PBT %.2f" % (chk, pbt()[2]))

    # Revenue mix and quarterly revenue must both sum to turnover.
    if abs(sum(v for _l, v in REVENUE_MIX) - revenue()[2]) > 0.005:
        errs.append("Revenue mix does not sum to turnover")
    if abs(sum(v for _l, v in QUARTERLY) - revenue()[2]) > 0.005:
        errs.append("Quarterly revenue does not sum to turnover")

    # Budget actuals must agree with the P&L.
    for head, _bud, act, _lo in BUDGET:
        if abs(act - pl(head)[2]) > 0.005:
            errs.append("Budget actual for %s disagrees with P&L" % head)
    bt = budget_totals()
    if abs(bt["actual_pbt"] - pbt()[2]) > 0.005:
        errs.append("Budget actual PBT disagrees with P&L")

    # Cash flow must reconcile opening to closing cash.
    cf = cash_flow()
    if abs(cf["opening"] + cf["net_change"] - cf["closing"]) > 0.005:
        errs.append("Cash flow does not reconcile: %.2f + %.2f != %.2f"
                    % (cf["opening"], cf["net_change"], cf["closing"]))

    # DuPont must reproduce ROE within rounding tolerance.
    for i in range(3):
        d = dupont(i)
        if abs(d["roe_reconstructed"] - d["roe_direct"]) > 0.35:
            errs.append("DuPont mismatch in %s: %.2f vs %.2f"
                        % (YEARS[i], d["roe_reconstructed"], d["roe_direct"]))

    if errs:
        raise AssertionError("Financial model self-check failed:\n  - " +
                             "\n  - ".join(errs))
    return True


if __name__ == "__main__":
    self_check()
    print("Financial model self-check: PASSED\n")
    print("%-42s %9s %9s %9s" % ("Particulars", *YEARS_SHORT))
    print("-" * 72)
    for name, vals in [("Total Income", total_income()),
                       ("Total Expenses", total_expenses()),
                       ("EBITDA", ebitda()), ("EBIT", ebit()),
                       ("Profit Before Tax", pbt()), ("Profit After Tax", pat()),
                       ("Balance Sheet Total", balance_total()),
                       ("Shareholders' Funds", shareholders_funds()),
                       ("Working Capital", working_capital())]:
        print("%-42s %9.2f %9.2f %9.2f" % (name, *vals))
    print("-" * 72)
    for i in range(3):
        r = ratio_set(i)
        print("%s  current %.2f  net margin %.2f%%  ROCE %.2f%%  D/E %.2f"
              % (YEARS[i], r["current"], r["net_margin"], r["roce"],
                 r["debt_equity"]))
    print("\nCVP: contribution %.2f  P/V %.2f%%  BEP %.2f  MoS %.2f (%.2f%%)"
          % (contribution(), pv_ratio(), bep_sales(), margin_of_safety(),
             mos_ratio()))
    dol, ebit_op = operating_leverage()
    print("Leverage: operating %.2f  financial %.2f  combined %.2f"
          % (dol, financial_leverage(), round(dol * financial_leverage(), 2)))
    cf = cash_flow()
    print("Cash flow: operating %.2f  investing %.2f  financing %.2f  net %.2f"
          % (cf["net_op"], cf["net_inv"], cf["net_fin"], cf["net_change"]))
