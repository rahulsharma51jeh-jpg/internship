# Summer Internship Project Report — Ganga Kumari Singh

Deliverables for the M.B.A. (Financial Management) summer internship report on
**Infinity Interns** (Infinitya1 Career Counselling Private Limited), Patna.

## Output

| File | Size | Notes |
|---|---|---|
| `output/Internship_Report_Ganga_Kumari_Singh.pdf` | 1.1 MB | 83 pages, A4, print-ready |
| `output/Internship_Report_Ganga_Kumari_Singh.docx` | 0.8 MB | Editable, opens in Word / Google Docs / LibreOffice |

The 20 chart images are embedded as 8-bit indexed-palette PNGs (`quant.py`),
which halves both file sizes with no visible loss on flat artwork. The PDF uses
an `/Indexed /DeviceRGB` colour space for them.

Both files are generated from one source, so their content is identical.

**In the DOCX:** select the Table of Contents and press **F9** (or right-click →
*Update Field*) to populate its page numbers. Word owns pagination in a `.docx`,
so the numbers cannot be baked in beforehand. The PDF already has correct page
numbers throughout.

## Contents

Cover, Certificate of Completion, Certificate of the Guide, Declaration,
Acknowledgement, Preface, Table of Contents, List of Tables, List of Figures,
Executive Summary, then ten chapters — Introduction, Company Profile,
Internship Tasks, Financial Management Analysis, Budgeting & Cost Control,
Ratio & Financial Analysis, Learning Outcomes, Challenges Faced, Findings &
Suggestions, Conclusion — followed by a Bibliography and nine Annexures.

**46 tables · 20 charts · ~15,400 words**

## Rebuilding

No third-party packages are used; the document engine, chart library, brand mark
and both file writers are pure-standard-library Python.

```bash
cd src
python3 build.py                 # writes both files to ../output
python3 validate.py              # structural checks on both files
python3 findata.py               # prints the financial model and its self-check
python3 pdfproof.py 1 12 23      # rasterise chosen PDF pages to ../build/proof
```

### Source layout

| Module | Responsibility |
|---|---|
| `findata.py` | The financial model — single source of truth, with a self-check that ties the P&L, balance sheet, cash flow, CVP and DuPont figures together |
| `content.py` | The report text as a list of layout blocks, with every figure interpolated from `findata` |
| `charts.py`, `exhibits.py` | The 20 chart exhibits |
| `logo.py`, `canvas.py`, `strokefont.py` | Brand mark and the raster/PNG engine behind the graphics |
| `pdfwriter.py`, `pdfdoc.py`, `afm.py` | PDF layout engine, object writer and base-14 font metrics |
| `docxwriter.py` | OOXML (`.docx`) writer |
| `validate.py`, `pdfproof.py` | Output verification |

## A note on the figures

The financial statements are **indicative management figures** compiled for
academic analysis, not audited statutory accounts. This is stated on the
Declaration page, in Section 1.8 (Limitations), in Section 6.1 and again in the
Annexures. `findata.self_check()` runs before every build and fails the build if
any statement stops reconciling.
