# Illustrated internship report — build notes

`Internship_Report_Gunja_Kumari_Illustrated.pdf` (94 physical pages: cover + 13
preliminary pages numbered i–xiii + 80 numbered body pages) is generated from
source by these scripts. The sandbox has no PDF libraries and no network access,
so everything — PDF writing, font embedding, charts and diagrams — is implemented
here in pure Python.

## Files

| File | What it does |
|---|---|
| `pdfengine.py` | Minimal PDF writer: TrueType parsing (cmap/hmtx/glyf), Identity-H CID font embedding, vector primitives, justified text flow, headings, bullet lists, tables that break across pages with a repeated header, figure blocks, callouts, stat cards, running header/footer, roman/arabic page labels, PDF outline (bookmarks). |
| `charts.py` | 20 chart types: vertical/grouped/stacked/horizontal bars, line and area, donut and pie, radar, gauges, waterfall, break-even (CVP), tornado variance, bubble, scorecard, progress bars, dumbbell, composition bars, Gantt, combo bar+line. |
| `diagrams.py` | 20 diagram types: organisation chart, chevron process, flowchart with decision diamonds, cycle, SWOT, pyramid, driver (DuPont) tree, roadmap, fishbone, 2×2 matrix, value chain, funnel, fund-flow ribbons, hub-and-spokes, bridge, layered stack, mapping, card grid, vertical timeline, rings. |
| `content.py` | The whole report: front matter, Chapters 1–10, bibliography, Annexures A–K, plus all figure/table data. |
| `build.py` | Runs the build three times so the table of contents, list of figures and list of tables carry real page numbers (pass 2 onwards is stable). |
| `raster.py` | Software rasteriser that replays the page operators and writes PNGs — used to proof-read every page visually, since no PDF viewer is available here. |
| `renderall.py` | Renders page images into `../preview/pages/`. |
| `validate.py` | Checks the produced PDF: header/EOF, xref offsets, object integrity, stream lengths, Flate streams, page tree, fonts, page labels, outline. |

## Rebuild

```bash
cd report
python3 build.py ../Internship_Report_Gunja_Kumari_Illustrated.pdf   # 3-pass build
python3 validate.py ../Internship_Report_Gunja_Kumari_Illustrated.pdf
python3 renderall.py 1 94        # optional: PNG preview of every page
```

## Editing content

* Text, tables and figure data all live in `content.py`; each chapter is one
  function (`chapter1` … `chapter10`, `bibliography`, `annexures`) listed in
  `CHAPTER_NAMES`.
* Shared figures such as the profit and loss, balance sheet, batch budget,
  variance table and three-year trend are defined once as module-level constants
  near the top of `content.py`, so a change there flows through every chart,
  table and ratio that uses them.
* Every figure is a small `draw(d, x, y, w, h)` function passed to `d.figure(...)`,
  which handles keep-together behaviour, the frame, numbering and the caption,
  and registers the entry in the List of Figures.

## Data note

Financial figures are illustrative, as in the original report: they preserve the
structure and proportions described there (revenue ₹48,00,000; net margin 18.5%;
current ratio 1.92:1; debt-equity 0.24:1; batch break-even at 17 students) and are
labelled *observed*, *illustrative* or *indicative* throughout.
