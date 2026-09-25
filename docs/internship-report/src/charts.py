"""
charts.py -- vector chart library drawn with pdfengine primitives.
Every function has the signature f(d, x, y, w, h, ...) where (x, y) is the
bottom-left of the plot block.
"""

import math
from pdfengine import (NAVY, NAVY_D, BLUE, BLUE_M, BLUE_L, BLUE_XL, ORANGE, ORANGE_L, ORANGE_XL,
                       GREEN, GREEN_L, RED, RED_L, TEAL, PURPLE, GOLD, GREY_D, GREY, GREY_M,
                       GREY_L, GREY_XL, WHITE, SERIES)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def nice_max(v, ticks=5):
    if v <= 0:
        return 1.0
    raw = v / float(ticks)
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 1.5, 2, 2.5, 3, 4, 5, 7.5, 10):
        if raw <= m * mag:
            return m * mag * ticks
    return 10 * mag * ticks


def axes(d, x, y, w, h, ymax, ticks=5, ylabel=None, fmt=lambda v: "%g" % v,
         grid=True, ymin=0.0, tick_size=7.0, axis_color=GREY_M, label_color=GREY):
    """Draw y-axis grid + labels; return (plot_x, plot_w) of the data area."""
    lab_w = 0.0
    for i in range(ticks + 1):
        v = ymin + (ymax - ymin) * i / float(ticks)
        lab_w = max(lab_w, d.width(fmt(v), "regular", tick_size))
    pad_left = lab_w + 8 + (12 if ylabel else 0)
    px = x + pad_left
    pw = w - pad_left
    for i in range(ticks + 1):
        v = ymin + (ymax - ymin) * i / float(ticks)
        gy = y + h * (v - ymin) / float(ymax - ymin)
        if grid:
            d.line(px, gy, x + w, gy, GREY_L if i else axis_color, 0.55 if i else 0.9)
        d.text_right(px - 5, gy - tick_size * 0.34, fmt(v), "regular", tick_size, label_color)
    if ylabel:
        d.text_rot_center(x + 6, y + h / 2.0, ylabel, 90, "semibold", 7.6, GREY)
    return px, pw


def legend(d, x, y, items, size=7.8, gap=13.0, swatch=7.0, cols=None, row_h=11.0, marker="box",
           max_w=None):
    """items: list of (label, color)."""
    if cols is None:
        cx = x
        cy = y
        for lab, col in items:
            item_w = swatch + 8 + d.width(lab, "regular", size) + gap
            if max_w and cx > x and cx + item_w - gap > x + max_w:
                cx = x
                cy -= row_h
            if marker == "line":
                d.line(cx, cy + 3, cx + swatch + 2, cy + 3, col, 1.8)
                d.circle(cx + (swatch + 2) / 2.0, cy + 3, 2.0, fill=col)
            else:
                d.round_rect(cx, cy, swatch, swatch, 1.2, fill=col)
            d.text(cx + swatch + 4, cy + 0.6, lab, "regular", size, GREY_D)
            cx += item_w
        return
    per = cols
    for i, (lab, col) in enumerate(items):
        r, c = i // per, i % per
        cw = 150
        cx = x + c * cw
        cy = y - r * row_h
        d.round_rect(cx, cy, swatch, swatch, 1.2, fill=col)
        d.text(cx + swatch + 4, cy + 0.6, lab, "regular", size, GREY_D)


def _cat_labels(d, px, pw, labels, y, size=7.4, color=GREY_D, max_lines=2, rotate=False):
    n = len(labels)
    slot = pw / float(n)
    for i, lab in enumerate(labels):
        cx = px + slot * (i + 0.5)
        if rotate:
            d.text_rot(cx - 2.5, y - 2, lab, 38, "regular", size, color)
            continue
        lines = d.wrap(lab, slot - 3, "regular", size)[:max_lines]
        for j, ln in enumerate(lines):
            d.text_center(cx, y - j * (size + 1.4), ln, "regular", size, color)


# --------------------------------------------------------------------------
# bar charts
# --------------------------------------------------------------------------
def bar_v(d, x, y, w, h, labels, values, color=BLUE, ymax=None, fmt=lambda v: "%g" % v,
          value_labels=True, ylabel=None, bar_frac=0.56, colors=None, target=None,
          target_label=None, label_size=7.4, rotate_labels=False, tick_fmt=None, ticks=5):
    lab_h = 22 if not rotate_labels else 30
    ph = h - lab_h
    ymax = ymax or nice_max(max(values) * 1.12, ticks)
    px, pw = axes(d, x, y + lab_h, w, ph, ymax, ticks=ticks, ylabel=ylabel, fmt=tick_fmt or fmt)
    slot = pw / float(len(values))
    bw = slot * bar_frac
    for i, v in enumerate(values):
        bx = px + slot * i + (slot - bw) / 2.0
        bh = ph * v / float(ymax)
        col = (colors[i] if colors else color)
        d.rect(bx, y + lab_h, bw, max(bh, 0.4), fill=col)
        d.rect(bx, y + lab_h + max(bh, 0.4) - 2.2, bw, 2.2, fill=_shade(col, 0.82))
        if value_labels:
            d.text_center(bx + bw / 2.0, y + lab_h + bh + 3.4, fmt(v), "semibold", 7.3, GREY_D)
    if target is not None:
        ty = y + lab_h + ph * target / float(ymax)
        d.line(px, ty, x + w, ty, RED, 1.0, dash=(3, 2))
        if target_label:
            d.text_right(x + w, ty + 3, target_label, "semibold", 7.0, RED)
    _cat_labels(d, px, pw, labels, y + lab_h - 10, label_size, rotate=rotate_labels)


def _shade(c, f):
    return (min(1, c[0] * f), min(1, c[1] * f), min(1, c[2] * f))


def bar_grouped(d, x, y, w, h, labels, series, ymax=None, fmt=lambda v: "%g" % v,
                ylabel=None, legend_items=True, value_labels=True, tick_fmt=None,
                label_size=7.3, ticks=5):
    """series: list of (name, values, color)."""
    leg_h = 14 if legend_items else 0
    lab_h = 20
    ph = h - lab_h - leg_h
    allv = [v for _, vals, _ in series for v in vals]
    ymax = ymax or nice_max(max(allv) * 1.12, ticks)
    px, pw = axes(d, x, y + lab_h, w, ph, ymax, ticks=ticks, ylabel=ylabel, fmt=tick_fmt or fmt)
    slot = pw / float(len(labels))
    n = len(series)
    bw = slot * 0.66 / n
    for si, (name, vals, col) in enumerate(series):
        for i, v in enumerate(vals):
            bx = px + slot * i + slot * 0.17 + si * bw
            bh = ph * v / float(ymax)
            d.rect(bx, y + lab_h, bw, max(bh, 0.4), fill=col)
            if value_labels:
                d.text_center(bx + bw / 2.0, y + lab_h + bh + 2.6, fmt(v), "semibold", 6.3, GREY)
    _cat_labels(d, px, pw, labels, y + lab_h - 10, label_size)
    if legend_items:
        legend(d, px, y + h - 8, [(n, c) for n, _, c in series])


def bar_h(d, x, y, w, h, labels, values, colors=None, fmt=lambda v: "%g" % v,
          label_w=None, bar_h_frac=0.62, value_inside=False, xmax=None, note_col=None,
          size=7.8):
    label_w = label_w or min(150, max(d.width(l, "regular", size) for l in labels) + 8)
    px = x + label_w
    pw = w - label_w - 36
    xmax = xmax or nice_max(max(values) * 1.02, 4)
    n = len(values)
    slot = h / float(n)
    bh = slot * bar_h_frac
    for i, v in enumerate(values):
        by = y + h - slot * (i + 1) + (slot - bh) / 2.0
        bwid = pw * v / float(xmax)
        col = colors[i] if colors else SERIES[i % len(SERIES)]
        d.rect(px, by, max(bwid, 0.6), bh, fill=col)
        d.text_right(px - 6, by + bh / 2.0 - size * 0.34, labels[i], "regular", size, GREY_D)
        if value_inside and bwid > 40:
            d.text_right(px + bwid - 5, by + bh / 2.0 - 2.6, fmt(v), "semibold", 7.2, WHITE)
        else:
            d.text(px + bwid + 4, by + bh / 2.0 - 2.6, fmt(v), "semibold", 7.4, GREY_D)
    d.line(px, y, px, y + h, GREY_M, 0.8)


def bar_stacked(d, x, y, w, h, labels, series, ymax=None, fmt=lambda v: "%g" % v,
                ylabel=None, tick_fmt=None, show_total=True, bar_frac=0.5, pct=False,
                ticks=5):
    """series: list of (name, values, color) stacked bottom-up."""
    leg_h = 14
    lab_h = 20
    ph = h - lab_h - leg_h
    totals = [sum(s[1][i] for s in series) for i in range(len(labels))]
    if pct:
        ymax = 100.0
    else:
        ymax = ymax or nice_max(max(totals) * 1.1, ticks)
    px, pw = axes(d, x, y + lab_h, w, ph, ymax, ticks=ticks, ylabel=ylabel, fmt=tick_fmt or fmt)
    slot = pw / float(len(labels))
    bw = slot * bar_frac
    for i in range(len(labels)):
        base = 0.0
        bx = px + slot * i + (slot - bw) / 2.0
        for name, vals, col in series:
            v = vals[i]
            if pct:
                v = v / totals[i] * 100.0
            bh = ph * v / float(ymax)
            d.rect(bx, y + lab_h + ph * base / float(ymax), bw, bh, fill=col)
            if bh > 9:
                d.text_center(bx + bw / 2.0, y + lab_h + ph * base / float(ymax) + bh / 2.0 - 2.6,
                              ("%.0f%%" % v) if pct else fmt(vals[i]), "semibold", 6.6, WHITE)
            base += v
        if show_total and not pct:
            d.text_center(bx + bw / 2.0, y + lab_h + ph * base / float(ymax) + 3.2,
                          fmt(totals[i]), "bold", 7.2, NAVY)
    _cat_labels(d, px, pw, labels, y + lab_h - 10)
    legend(d, px, y + h - 8, [(n, c) for n, _, c in series])


def combo_bar_line(d, x, y, w, h, labels, bars, line, bar_color=BLUE_M, line_color=ORANGE,
                   bar_name="", line_name="", fmt_bar=lambda v: "%g" % v,
                   fmt_line=lambda v: "%g" % v, ymax=None, y2max=None):
    leg_h, lab_h = 14, 20
    ph = h - lab_h - leg_h
    ymax = ymax or nice_max(max(bars) * 1.15)
    y2max = y2max or nice_max(max(line) * 1.3, 4)
    px, pw = axes(d, x, y + lab_h, w - 30, ph, ymax, fmt=fmt_bar)
    slot = pw / float(len(labels))
    bw = slot * 0.5
    for i, v in enumerate(bars):
        bx = px + slot * i + (slot - bw) / 2.0
        d.rect(bx, y + lab_h, bw, ph * v / ymax, fill=bar_color)
        d.text_center(bx + bw / 2.0, y + lab_h + ph * v / ymax + 3, fmt_bar(v), "semibold", 6.6, GREY_D)
    pts = []
    for i, v in enumerate(line):
        cx = px + slot * (i + 0.5)
        cy = y + lab_h + ph * v / y2max
        pts.append((cx, cy))
    d.polyline(pts, line_color, 1.6)
    for i, (cx, cy) in enumerate(pts):
        d.circle(cx, cy, 2.6, fill=WHITE, stroke=line_color, lw=1.3)
        d.text_center(cx, cy + 6, fmt_line(line[i]), "bold", 6.8, line_color)
    # right axis
    for i in range(5):
        v = y2max * i / 4.0
        gy = y + lab_h + ph * v / y2max
        d.text(x + w - 26, gy - 2.4, fmt_line(v), "regular", 6.8, line_color)
    d.line(x + w - 30, y + lab_h, x + w - 30, y + lab_h + ph, GREY_M, 0.7)
    _cat_labels(d, px, pw, labels, y + lab_h - 10)
    legend(d, px, y + h - 8, [(bar_name, bar_color)])
    legend(d, px + 120, y + h - 8, [(line_name, line_color)], marker="line")


# --------------------------------------------------------------------------
# line / area
# --------------------------------------------------------------------------
def line_chart(d, x, y, w, h, labels, series, ymax=None, ymin=0.0, fmt=lambda v: "%g" % v,
               ylabel=None, markers=True, value_labels=False, area=False, legend_on=True,
               tick_fmt=None, dashes=None, ticks=5, label_every=1, label_size=7.2):
    """series: list of (name, values, color)."""
    leg_h = 14 if legend_on else 0
    lab_h = 20
    ph = h - lab_h - leg_h
    allv = [v for _, vals, _ in series for v in vals]
    ymax = ymax or nice_max(max(allv) * 1.15, ticks)
    px, pw = axes(d, x, y + lab_h, w, ph, ymax, ticks=ticks, ylabel=ylabel,
                  fmt=tick_fmt or fmt, ymin=ymin)
    n = len(labels)
    step = pw / float(max(n - 1, 1)) if n > 1 else pw
    for si, (name, vals, col) in enumerate(series):
        pts = [(px + step * i, y + lab_h + ph * (v - ymin) / (ymax - ymin)) for i, v in enumerate(vals)]
        want_area = (area is True) or (area is not False and area == si)
        if want_area:
            poly = pts + [(pts[-1][0], y + lab_h), (pts[0][0], y + lab_h)]
            d.polygon(poly, fill=_tint(col, 0.16))
        d.polyline(pts, col, 1.7, dash=(dashes[si] if dashes else None))
        if markers:
            label_this = (value_labels is True) or (value_labels is not False
                                                   and value_labels is not None
                                                   and value_labels == si)
            for i, (cx, cy) in enumerate(pts):
                d.circle(cx, cy, 2.4, fill=WHITE, stroke=col, lw=1.3)
                if label_this:
                    d.text_center(cx, cy + 6.5, fmt(vals[i]), "semibold", 6.6, col)
    for i in range(n):
        if i % label_every == 0:
            d.text_center(px + step * i, y + lab_h - 10, labels[i], "regular", label_size, GREY_D)
    if legend_on:
        legend(d, px, y + h - 8, [(n_, c) for n_, _, c in series], marker="line")


def _tint(c, f):
    return (c[0] + (1 - c[0]) * (1 - f), c[1] + (1 - c[1]) * (1 - f), c[2] + (1 - c[2]) * (1 - f))


# --------------------------------------------------------------------------
# pie / donut
# --------------------------------------------------------------------------
def donut(d, x, y, w, h, values, labels, colors=None, inner=0.58, center_title=None,
          center_value=None, legend_side=True, pct=True, start=90.0, size=7.8):
    colors = colors or SERIES
    total = float(sum(values))
    if legend_side:
        r = min(h, w * 0.46) / 2.0 - 4
        cx = x + r + 8
    else:
        r = min(h * 0.62, w * 0.5) / 2.0
        cx = x + w / 2.0
    cy = y + h / 2.0 if legend_side else y + h * 0.42 + r * 0.1
    ang = start
    for i, v in enumerate(values):
        sweep = -360.0 * v / total
        col = colors[i % len(colors)]
        d.wedge(cx, cy, r, ang, ang + sweep, fill=col, r_inner=r * inner,
                stroke=WHITE, lw=1.1)
        mid = math.radians(ang + sweep / 2.0)
        if v / total > 0.055:
            lx = cx + math.cos(mid) * r * (inner + (1 - inner) / 2.0)
            ly = cy + math.sin(mid) * r * (inner + (1 - inner) / 2.0)
            d.text_center(lx, ly - 2.6, "%.0f%%" % (v / total * 100), "bold", 7.2, WHITE)
        ang += sweep
    if center_value:
        d.text_center(cx, cy + 1, center_value, "bold", 13.5, NAVY)
    if center_title:
        d.text_center(cx, cy - 10, center_title, "regular", 6.9, GREY)
    if legend_side:
        lx = cx + r + 18
        n = len(values)
        row = 15.0
        top = cy + (n - 1) * row / 2.0
        pct_w = 30.0 if pct else 0.0
        avail = (x + w) - (lx + 12) - pct_w - 6
        for i, lab in enumerate(labels):
            ly = top - i * row
            d.round_rect(lx, ly - 2.4, 7.5, 7.5, 1.4, fill=colors[i % len(colors)])
            txt = lab
            while d.width(txt, "regular", size) > avail and len(txt) > 6:
                txt = txt[:-1]
            if txt != lab:
                txt = txt[:-1] + "\u2026"
            d.text(lx + 12, ly, txt, "regular", size, GREY_D)
            if pct:
                d.text_right(x + w, ly, "%.1f%%" % (values[i] / total * 100), "semibold", size, NAVY)
    else:
        legend(d, x + 4, y + 2, [(labels[i], colors[i % len(colors)]) for i in range(len(labels))],
               cols=3, row_h=11)


def pie(d, x, y, w, h, values, labels, colors=None, **kw):
    donut(d, x, y, w, h, values, labels, colors=colors, inner=0.0, **kw)


# --------------------------------------------------------------------------
# radar
# --------------------------------------------------------------------------
def radar(d, x, y, w, h, axes_labels, series, maxv=100.0, rings=4, legend_on=True,
          label_size=7.2):
    """series: list of (name, values, color)."""
    leg_h = 14 if legend_on else 0
    cx = x + w / 2.0
    cy = y + (h - leg_h) / 2.0 + leg_h * 0.2
    r = min(w * 0.38, (h - leg_h) * 0.42)
    n = len(axes_labels)
    def pt(i, frac):
        a = math.pi / 2 + 2 * math.pi * i / n
        return (cx + math.cos(a) * r * frac, cy + math.sin(a) * r * frac)
    for k in range(1, rings + 1):
        poly = [pt(i, k / float(rings)) for i in range(n)]
        d.polygon(poly, stroke=GREY_L, lw=0.6)
    for i in range(n):
        p = pt(i, 1.0)
        d.line(cx, cy, p[0], p[1], GREY_L, 0.6)
        lp = pt(i, 1.17)
        a = math.pi / 2 + 2 * math.pi * i / n
        lines = d.wrap(axes_labels[i], 76, "regular", label_size)
        for j, ln in enumerate(lines):
            ly = lp[1] - j * (label_size + 1)
            if abs(math.cos(a)) < 0.3:
                d.text_center(lp[0], ly - (3 if math.sin(a) < 0 else 0), ln, "regular", label_size, GREY_D)
            elif math.cos(a) > 0:
                d.text(lp[0] - 2, ly - 2.4, ln, "regular", label_size, GREY_D)
            else:
                d.text_right(lp[0] + 2, ly - 2.4, ln, "regular", label_size, GREY_D)
    for name, vals, col in series:
        poly = [pt(i, min(vals[i] / maxv, 1.08)) for i in range(n)]
        d.polygon(poly, fill=_tint(col, 0.22), stroke=col, lw=1.5)
        for p in poly:
            d.circle(p[0], p[1], 2.1, fill=col)
    if legend_on:
        legend(d, x + 6, y + 2, [(n_, c) for n_, _, c in series])


# --------------------------------------------------------------------------
# gauges
# --------------------------------------------------------------------------
def gauge_row(d, x, y, w, h, items, size=8.0):
    """items: list of (label, value, max, display, color, benchmark or None)."""
    n = len(items)
    cw = w / float(n)
    for i, it in enumerate(items):
        lab, val, mx, disp, col = it[:5]
        bench = it[5] if len(it) > 5 else None
        cx = x + cw * (i + 0.5)
        r = min(cw * 0.36, h * 0.44)
        cy = y + h * 0.40
        d.wedge(cx, cy, r, 180, 0, fill=GREY_L, r_inner=r * 0.62)
        frac = max(0.0, min(1.0, val / float(mx)))
        d.wedge(cx, cy, r, 180, 180 - 180 * frac, fill=col, r_inner=r * 0.62)
        if bench is not None:
            a = math.radians(180 - 180 * max(0.0, min(1.0, bench / float(mx))))
            d.line(cx + math.cos(a) * r * 0.58, cy + math.sin(a) * r * 0.58,
                   cx + math.cos(a) * r * 1.04, cy + math.sin(a) * r * 1.04, NAVY_D, 1.2)
        d.text_center(cx, cy + 4, disp, "bold", 11.5, NAVY)
        for j, ln in enumerate(d.wrap(lab, cw - 8, "regular", size)[:2]):
            d.text_center(cx, cy - 12 - j * 9.6, ln, "regular", size, GREY)


# --------------------------------------------------------------------------
# waterfall
# --------------------------------------------------------------------------
def waterfall(d, x, y, w, h, items, fmt=lambda v: "%g" % v, ylabel=None):
    """items: list of (label, delta, kind) kind in {'start','pos','neg','total'}"""
    lab_h = 26
    ph = h - lab_h
    run = 0.0
    tops = []
    for lab, delta, kind in items:
        if kind in ("start", "total"):
            tops.append((max(run, delta), min(run, delta) if kind == "total" else 0.0))
            run = delta if kind == "start" else run
        else:
            nxt = run + delta
            tops.append((max(run, nxt), min(run, nxt)))
            run = nxt
    peak = max(t[0] for t in tops)
    ymax = nice_max(peak * 1.12)
    px, pw = axes(d, x, y + lab_h, w, ph, ymax, ylabel=ylabel, fmt=fmt)
    slot = pw / float(len(items))
    bw = slot * 0.56
    run = 0.0
    prev_top = None
    for i, (lab, delta, kind) in enumerate(items):
        bx = px + slot * i + (slot - bw) / 2.0
        if kind == "start":
            lo, hi = 0.0, delta
            col = NAVY
            run = delta
        elif kind == "total":
            lo, hi = 0.0, delta
            col = GREEN
        elif delta >= 0:
            lo, hi = run, run + delta
            col = BLUE_M
            run += delta
        else:
            lo, hi = run + delta, run
            col = ORANGE
            run += delta
        y0 = y + lab_h + ph * lo / ymax
        y1 = y + lab_h + ph * hi / ymax
        d.rect(bx, y0, bw, max(y1 - y0, 0.8), fill=col)
        d.text_center(bx + bw / 2.0, y1 + 3.2, ("" if kind in ("start", "total") else
                                                ("+" if delta > 0 else "-")) + fmt(abs(delta)),
                      "semibold", 6.9, GREY_D if kind not in ("start", "total") else NAVY)
        if prev_top is not None and kind not in ("start", "total"):
            d.line(prev_top[0], prev_top[1], bx, prev_top[1], GREY_M, 0.6, dash=(2, 1.6))
        prev_top = (bx + bw, y1 if delta >= 0 else y0)
        if kind == "start":
            prev_top = (bx + bw, y1)
    _cat_labels(d, px, pw, [i[0] for i in items], y + lab_h - 10, 6.9, max_lines=3)


# --------------------------------------------------------------------------
# break-even (CVP)
# --------------------------------------------------------------------------
def breakeven(d, x, y, w, h, fixed, var_per_unit, price, units_max, fmt=lambda v: "%g" % v,
              unit_label="Number of students enrolled", bep=None):
    lab_h, leg_h = 24, 14
    ph = h - lab_h - leg_h
    rev_max = price * units_max
    ymax = nice_max(rev_max * 1.06)
    px, pw = axes(d, x, y + lab_h, w, ph, ymax, fmt=fmt, ylabel=u"Revenue / Cost (\u20b9)")

    def P(u, v):
        return (px + pw * u / float(units_max), y + lab_h + ph * v / ymax)

    bep_u = fixed / float(price - var_per_unit)
    # shaded loss and profit areas
    d.polygon([P(0, 0), P(bep_u, price * bep_u), P(0, fixed)], fill=RED_L)
    d.polygon([P(bep_u, price * bep_u), P(units_max, price * units_max),
               P(units_max, fixed + var_per_unit * units_max)], fill=GREEN_L)
    # lines
    d.polyline([P(0, fixed), P(units_max, fixed)], PURPLE, 1.2, dash=(4, 2.5))
    d.polyline([P(0, fixed), P(units_max, fixed + var_per_unit * units_max)], ORANGE, 1.9)
    d.polyline([P(0, 0), P(units_max, price * units_max)], BLUE, 1.9)
    # BEP marker
    bp = P(bep_u, price * bep_u)
    d.line(bp[0], y + lab_h, bp[0], bp[1], GREY_D, 0.8, dash=(2.5, 2))
    d.circle(bp[0], bp[1], 3.6, fill=WHITE, stroke=NAVY, lw=1.6)
    bx_lab = bp[0] + 8
    d.round_rect(bx_lab, bp[1] - 6, 120, 25, 2.5, fill=WHITE, stroke=NAVY, lw=0.8)
    d.text(bx_lab + 6, bp[1] + 10, "Break-even point", "bold", 7.4, NAVY)
    d.text(bx_lab + 6, bp[1] + 1, "%d students  |  %s" % (bep or int(math.ceil(bep_u)),
                                                          fmt(price * bep_u)), "regular", 7.2, GREY_D)
    # x axis
    ticks = 6
    for i in range(ticks + 1):
        u = units_max * i / float(ticks)
        p = P(u, 0)
        d.line(p[0], y + lab_h, p[0], y + lab_h - 3, GREY_M, 0.7)
        d.text_center(p[0], y + lab_h - 12, "%d" % u, "regular", 7.2, GREY_D)
    d.text_center(px + pw / 2.0, y + 2, unit_label, "semibold", 7.6, GREY)
    legend(d, px, y + h - 8, [("Total revenue", BLUE), ("Total cost", ORANGE),
                              ("Fixed cost", PURPLE), ("Loss", RED_L), ("Profit", GREEN_L)])


# --------------------------------------------------------------------------
# tornado / variance
# --------------------------------------------------------------------------
def tornado(d, x, y, w, h, labels, values, fmt=lambda v: "%+g" % v, fav_color=GREEN,
            adv_color=RED, size=7.6, note_fav="Favourable", note_adv="Adverse"):
    label_w = min(140, max(d.width(l, "regular", size) for l in labels) + 10)
    px = x + label_w
    pw = w - label_w - 10
    mx = max(abs(v) for v in values) * 1.25
    zero = px + pw / 2.0
    n = len(values)
    slot = (h - 16) / float(n)
    bh = slot * 0.56
    d.line(zero, y, zero, y + h - 16, GREY_M, 0.9)
    for i, v in enumerate(values):
        by = y + h - 16 - slot * (i + 1) + (slot - bh) / 2.0
        length = (pw / 2.0) * abs(v) / mx
        col = fav_color if v >= 0 else adv_color
        if v >= 0:
            d.rect(zero, by, length, bh, fill=col)
            d.text(zero + length + 4, by + bh / 2.0 - 2.6, fmt(v), "semibold", 7.2, col)
        else:
            d.rect(zero - length, by, length, bh, fill=col)
            d.text_right(zero - length - 4, by + bh / 2.0 - 2.6, fmt(v), "semibold", 7.2, col)
        d.text_right(px - 8, by + bh / 2.0 - 2.6, labels[i], "regular", size, GREY_D)
    d.text_center(zero + pw / 4.0, y + h - 10, note_fav, "bold", 7.2, fav_color)
    d.text_center(zero - pw / 4.0, y + h - 10, note_adv, "bold", 7.2, adv_color)


# --------------------------------------------------------------------------
# scatter / bubble
# --------------------------------------------------------------------------
def bubble(d, x, y, w, h, points, xlabel, ylabel, xmax=100, ymax=100,
           quadrant_labels=None, size=7.6):
    lab_h = 22
    ph = h - lab_h - 4
    px = x + 34
    pw = w - 40
    py = y + lab_h
    d.rect(px, py, pw, ph, fill=GREY_XL, stroke=GREY_L, lw=0.6)
    d.line(px + pw / 2.0, py, px + pw / 2.0, py + ph, GREY_M, 0.7, dash=(3, 2))
    d.line(px, py + ph / 2.0, px + pw, py + ph / 2.0, GREY_M, 0.7, dash=(3, 2))
    if quadrant_labels:
        pos = [(px + pw * 0.25, py + ph * 0.93), (px + pw * 0.75, py + ph * 0.93),
               (px + pw * 0.25, py + ph * 0.06), (px + pw * 0.75, py + ph * 0.06)]
        for (qx, qy), lab in zip(pos, quadrant_labels):
            d.text_center(qx, qy, lab, "bold", 6.8, GREY_M)
    for pnt in points:
        name, vx, vy, r, col, highlight = pnt[:6]
        place = pnt[6] if len(pnt) > 6 else "below"
        cx = px + pw * vx / float(xmax)
        cy = py + ph * vy / float(ymax)
        d.circle(cx, cy, r, fill=_tint(col, 0.55 if not highlight else 0.9),
                 stroke=col, lw=1.4 if highlight else 0.8)
        fnt = "bold" if highlight else "regular"
        col_t = NAVY if highlight else GREY_D
        lines = d.wrap(name, 96, fnt, size)
        if place == "above":
            for j, ln in enumerate(lines):
                d.text_center(cx, cy + r + 5 + (len(lines) - 1 - j) * 8.6, ln, fnt, size, col_t)
        elif place == "right":
            for j, ln in enumerate(lines):
                d.text(cx + r + 5, cy + (len(lines) - 1) * 4.3 - j * 8.6 - 2.4, ln, fnt, size, col_t)
        elif place == "left":
            for j, ln in enumerate(lines):
                d.text_right(cx - r - 5, cy + (len(lines) - 1) * 4.3 - j * 8.6 - 2.4, ln, fnt, size, col_t)
        else:
            for j, ln in enumerate(lines):
                d.text_center(cx, cy - r - 9 - j * 8.6, ln, fnt, size, col_t)
    d.text_center(px + pw / 2.0, y + 2, xlabel, "semibold", 7.6, GREY)
    d.text_rot_center(x + 8, py + ph / 2.0, ylabel, 90, "semibold", 7.6, GREY)
    d.arrow(px, py - 6, px + pw, py - 6, GREY_M, 0.8, 4)
    d.arrow(px - 8, py, px - 8, py + ph, GREY_M, 0.8, 4)


# --------------------------------------------------------------------------
# scorecard heat table
# --------------------------------------------------------------------------
def scorecard(d, x, y, w, h, rows, headers, col_w=None, size=7.7):
    """rows: list of (label, [ (text, color_or_None), ... ])"""
    n_cols = len(headers)
    lab_w = w * 0.34
    cw = (w - lab_w) / float(n_cols)
    rh = h / float(len(rows) + 1)
    d.rect(x, y + h - rh, w, rh, fill=NAVY)
    d.text(x + 6, y + h - rh / 2.0 - 3, "Indicator", "bold", size, WHITE)
    for i, hd in enumerate(headers):
        d.text_center(x + lab_w + cw * (i + 0.5), y + h - rh / 2.0 - 3, hd, "bold", size, WHITE)
    for ri, (lab, cells) in enumerate(rows):
        ry = y + h - rh * (ri + 2)
        if ri % 2:
            d.rect(x, ry, w, rh, fill=GREY_XL)
        d.text(x + 6, ry + rh / 2.0 - 3, lab, "regular", size, GREY_D)
        for ci, (txt, col) in enumerate(cells):
            cx = x + lab_w + cw * ci
            if col:
                d.round_rect(cx + 4, ry + 2.4, cw - 8, rh - 4.8, 2.0, fill=col)
                d.text_center(cx + cw / 2.0, ry + rh / 2.0 - 3, txt, "bold", size, WHITE)
            else:
                d.text_center(cx + cw / 2.0, ry + rh / 2.0 - 3, txt, "regular", size, GREY_D)
        d.line(x, ry, x + w, ry, GREY_L, 0.5)
    d.rect(x, y, w, h, stroke=GREY_L, lw=0.7)


# --------------------------------------------------------------------------
# progress / target bars
# --------------------------------------------------------------------------
def progress_bars(d, x, y, w, h, items, size=8.0, show_target=True):
    """items: list of (label, value, max, display, color, target|None)"""
    n = len(items)
    slot = h / float(n)
    lab_w = w * 0.34
    px = x + lab_w
    pw = w - lab_w - 44
    for i, it in enumerate(items):
        lab, val, mx, disp, col = it[:5]
        tgt = it[5] if len(it) > 5 else None
        by = y + h - slot * (i + 1) + slot * 0.30
        bh = slot * 0.40
        d.round_rect(px, by, pw, bh, bh / 2.0, fill=GREY_L)
        fw = pw * max(0.0, min(1.0, val / float(mx)))
        d.round_rect(px, by, max(fw, bh), bh, bh / 2.0, fill=col)
        d.text_right(px - 8, by + bh / 2.0 - size * 0.35, lab, "regular", size, GREY_D)
        d.text(px + pw + 6, by + bh / 2.0 - size * 0.35, disp, "bold", size, col)
        if tgt is not None and show_target:
            tx = px + pw * max(0.0, min(1.0, tgt / float(mx)))
            d.line(tx, by - 2.6, tx, by + bh + 2.6, NAVY_D, 1.1)


def dumbbell(d, x, y, w, h, labels, before, after, c_before=GREY_M, c_after=BLUE,
             fmt=lambda v: "%g" % v, size=7.8, legend_labels=("Before", "After"), maxv=10.0):
    lab_w = w * 0.38
    px = x + lab_w
    pw = w - lab_w - 26
    n = len(labels)
    slot = (h - 14) / float(n)
    for i in range(n):
        cy = y + h - 14 - slot * (i + 0.5)
        x1 = px + pw * before[i] / maxv
        x2 = px + pw * after[i] / maxv
        d.line(px, cy, px + pw, cy, GREY_L, 0.6, dash=(1.6, 1.8))
        d.line(x1, cy, x2, cy, BLUE_L, 3.2)
        d.circle(x1, cy, 3.4, fill=WHITE, stroke=c_before, lw=1.4)
        d.circle(x2, cy, 3.9, fill=c_after)
        d.text_right(px - 8, cy - size * 0.35, labels[i], "regular", size, GREY_D)
        d.text(px + pw + 6, cy - size * 0.35, fmt(after[i]), "bold", size, c_after)
    legend(d, px, y + h - 10, [(legend_labels[0], c_before), (legend_labels[1], c_after)])


# --------------------------------------------------------------------------
# treemap-ish composition bar
# --------------------------------------------------------------------------
def composition_bars(d, x, y, w, h, groups, fmt=lambda v: "%g" % v, size=7.4, bar_h=30.0,
                     gap=26.0, legends=False):
    """groups: list of (title, [(label, value, color), ...]) -> 100% wide bars"""
    n = len(groups)
    total_h = n * bar_h + (n - 1) * gap
    top = y + (h - total_h) / 2.0 + total_h
    for gi, (title, segs) in enumerate(groups):
        by = top - bar_h - gi * (bar_h + gap)
        tot = float(sum(s[1] for s in segs))
        d.text(x, by + bar_h + 6, title, "semibold", 8.4, NAVY)
        d.text_right(x + w, by + bar_h + 6, fmt(tot), "bold", 8.4, GREY_D)
        cx = x
        for (lab, v, col) in segs:
            sw = w * v / tot
            d.rect(cx, by, sw, bar_h, fill=col)
            if sw > 26:
                d.text_center(cx + sw / 2.0, by + bar_h / 2.0 + 1.5, "%.0f%%" % (v / tot * 100),
                              "bold", 7.0, WHITE)
            if sw > 46:
                lines = d.wrap(lab, sw - 5, "regular", 6.3)[:1]
                d.text_center(cx + sw / 2.0, by + bar_h / 2.0 - 7.5, lines[0], "regular", 6.3, WHITE)
            cx += sw
        d.rect(x, by, w, bar_h, stroke=WHITE, lw=0.8)
        if legends:
            legend(d, x, by - 12, [(s[0], s[2]) for s in segs], size=6.8, gap=8, swatch=6,
                   max_w=w, row_h=9.5)


def gantt(d, x, y, w, h, tasks, n_slots, slot_labels, size=7.6, bar_colors=None):
    """tasks: list of (label, start_slot, span, detail)"""
    lab_w = w * 0.30
    px = x + lab_w
    pw = w - lab_w
    head_h = 16.0
    n = len(tasks)
    slot_w = pw / float(n_slots)
    rows_h = h - head_h
    rh = rows_h / float(n)
    for i in range(n_slots):
        cx = px + slot_w * i
        d.rect(cx, y, slot_w, rows_h, fill=GREY_XL if i % 2 == 0 else WHITE)
        d.text_center(cx + slot_w / 2.0, y + rows_h + 5, slot_labels[i], "semibold", 7.0, GREY)
    for i, (lab, s, span, detail) in enumerate(tasks):
        by = y + rows_h - rh * (i + 1)
        col = (bar_colors[i] if bar_colors else SERIES[i % len(SERIES)])
        bx = px + slot_w * s
        bwid = slot_w * span
        d.round_rect(bx + 1.5, by + rh * 0.22, bwid - 3, rh * 0.56, 2.2, fill=col)
        d.text(x, by + rh / 2.0 - size * 0.35, lab, "semibold", size, NAVY)
        if detail:
            txt = detail
            while txt and d.width(txt, "regular", 6.6) > bwid - 10:
                txt = txt[:-1]
            if len(txt) >= 4:
                d.text_center(bx + bwid / 2.0, by + rh / 2.0 - 2.6, txt, "regular", 6.6, WHITE)
        d.line(x, by, x + w, by, GREY_L, 0.45)
    d.rect(px, y, pw, rows_h, stroke=GREY_L, lw=0.7)
