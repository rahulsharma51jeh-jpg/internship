"""
Chart library for the internship report.

Every chart is rendered to a PNG on the shared raster canvas so the identical
image can be embedded in both the DOCX and the PDF. Charts share a common frame
(title block, plot area, gridlines, axes, legend and source note) drawn by
_Frame, which keeps the visual language consistent across all exhibits.
"""

import math

import brand
import strokefont as sf
from canvas import Canvas

W = 1200            # default render width in px
H = 900             # default render height in px


# --------------------------------------------------------------- utilities ----
def _xlines(categories):
    """How many label rows the category axis needs."""
    return max(1, max(len(str(c).split("\n")) for c in categories))


def _nice_step(rough):
    """Round a rough tick interval up to 1, 2, 2.5 or 5 x a power of ten."""
    if rough <= 0:
        return 1.0
    exp = math.floor(math.log10(rough))
    base = 10.0 ** exp
    for m in (1.0, 2.0, 2.5, 5.0, 10.0):
        if rough <= m * base * 1.0000001:
            return m * base
    return 10.0 * base


def _axis(vmin, vmax, target=5):
    """Return (lo, hi, step) spanning [vmin, vmax] on round numbers."""
    if vmax == vmin:
        vmax = vmin + 1.0
    step = _nice_step((vmax - vmin) / float(target))
    lo = math.floor(vmin / step) * step
    hi = math.ceil(vmax / step) * step
    # Guard against float dust producing a stray extra gridline.
    if hi - vmax < step * 0.02:
        pass
    return lo, hi, step


def _fmt(v, dec=None):
    """Format a number for an axis tick or a value label."""
    if dec is None:
        av = abs(v)
        if av >= 1000:
            dec = 0
        elif av >= 100:
            dec = 0 if abs(v - round(v)) < 1e-9 else 1
        elif av >= 10:
            dec = 0 if abs(v - round(v)) < 1e-9 else 1
        else:
            dec = 0 if abs(v - round(v)) < 1e-9 else 2
    s = ("%." + str(int(dec)) + "f") % v
    if s.startswith("-0") and float(s) == 0:
        s = s[1:]
    return s


def _wrap(text, size, maxw):
    """Greedy word wrap at the given cap height."""
    words = str(text).split()
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if cur and sf.text_width(trial, size) > maxw:
            lines.append(cur)
            cur = wd
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines or [""]


def _wrap_fit(text, size, maxw, max_lines=2):
    """Wrap `text`, shrinking the type until it fits within `max_lines`."""
    s = size
    for _ in range(18):
        lines = _wrap(text, s, maxw)
        if len(lines) <= max_lines:
            return lines, s
        s *= 0.94
    return _wrap(text, s, maxw)[:max_lines], s


def _fit(text, size, maxw):
    """Shrink a single line so it never exceeds maxw."""
    w = sf.text_width(text, size)
    return size * maxw / w if w > maxw else size


class _Frame:
    """Shared chart chrome: title block, plot rectangle, gridlines, legend."""

    def __init__(self, title, subtitle=None, width=W, height=H,
                 legend=None, note=None, y_title=None, bg=brand.PAPER,
                 pad_left=None, pad_right=None, x_lines=1):
        self.cv = Canvas(width, height, bg)
        self.w, self.h = width, height
        self.title = title
        self.subtitle = subtitle
        self.legend = legend or []
        self.note = note
        self.y_title = y_title

        u = width / 1500.0          # global scale factor
        self.u = u
        self.fs_title = 34 * u
        self.fs_sub = 22 * u
        self.fs_tick = 21 * u
        self.fs_label = 21 * u
        self.fs_val = 21 * u
        self.fs_note = 18 * u
        self.fs_leg = 21 * u

        self.x0 = (pad_left if pad_left is not None else 122) * u
        self.x1 = width - (pad_right if pad_right is not None else 48) * u

        self.x_lines = x_lines
        self._header()
        self.y0 = self.header_bottom + (60 if y_title else 42) * u
        bottom = 92 * u + (x_lines - 1) * 30 * u
        if self.legend:
            bottom += 54 * u
        if self.note:
            bottom += 44 * u
        self.y1 = height - bottom              # baseline of plot area

    # ------------------------------------------------------------ chrome ----
    def _header(self):
        cv, u = self.cv, self.u
        cv.rect(0, 0, self.w, 9 * u, brand.NAVY)
        cv.rect(0, 9 * u, self.w, 3 * u, brand.ORANGE)
        maxw = self.w - 92 * u

        t_size = _fit(self.title, self.fs_title, maxw)
        y = 64 * u
        sf.draw_text(cv, self.title, 44 * u, y, t_size, brand.NAVY,
                     weight=t_size * 0.135)

        if self.subtitle:
            lines, s = _wrap_fit(self.subtitle, self.fs_sub, maxw, 2)
            y += 34 * u
            for i, ln in enumerate(lines):
                sf.draw_text(cv, ln, 44 * u, y, s, brand.INK_SOFT,
                             weight=s * 0.115)
                if i < len(lines) - 1:
                    y += s * 1.42
        self.header_bottom = y

    def footer(self):
        cv, u = self.cv, self.u
        y = self.y1 + 74 * u + (self.x_lines - 1) * 30 * u
        if self.legend:
            self._legend(y)
            y += 50 * u
        if self.note:
            maxw = self.w - 92 * u
            lines, s = _wrap_fit(self.note, self.fs_note, maxw, 2)
            ny = self.h - 26 * u - (len(lines) - 1) * s * 1.45
            for ln in lines:
                sf.draw_text(cv, ln, 44 * u, ny, s, brand.GREY,
                             weight=s * 0.11)
                ny += s * 1.45
        return self.cv

    def _legend(self, y):
        cv, u = self.cv, self.u
        gap = 26 * u
        sw = 30 * u
        items = [(lbl, col) for (lbl, col) in self.legend]
        total = 0.0
        for lbl, _c in items:
            total += sw + 12 * u + sf.text_width(lbl, self.fs_leg) + gap
        total -= gap
        x = (self.x0 + self.x1) / 2.0 - total / 2.0
        for lbl, col in items:
            cv.round_rect(x, y - 15 * u, sw, 17 * u, 4 * u, col)
            x += sw + 12 * u
            sf.draw_text(cv, lbl, x, y, self.fs_leg, brand.INK_SOFT,
                         weight=self.fs_leg * 0.11)
            x += sf.text_width(lbl, self.fs_leg) + gap

    def y_grid(self, lo, hi, step, dec=None, currency=False):
        """Draw horizontal gridlines and the y-axis tick labels."""
        cv, u = self.cv, self.u
        self.lo, self.hi = lo, hi
        n = int(round((hi - lo) / step))
        for k in range(n + 1):
            v = lo + k * step
            y = self.vy(v)
            is_zero = abs(v) < 1e-9 and lo < 0
            cv.line(self.x0, y, self.x1, y,
                    brand.GREY_LIGHT if is_zero else brand.GREY_HAIR,
                    2.4 * u if is_zero else 1.6 * u)
            txt = _fmt(v, dec)
            sf.draw_text(cv, txt, self.x0 - 14 * u, y + self.fs_tick * 0.36,
                         self.fs_tick, brand.INK_SOFT, align="right",
                         weight=self.fs_tick * 0.11)
        cv.line(self.x0, self.y0 - 6 * u, self.x0, self.y1, brand.GREY_LIGHT,
                2.0 * u)
        cv.line(self.x0, self.y1, self.x1, self.y1, brand.INK_SOFT, 2.6 * u)
        if self.y_title:
            sf.draw_text(cv, self.y_title, self.x0 - 14 * u,
                         self.y0 - 26 * u, self.fs_tick * 0.92, brand.GREY,
                         align="right", weight=self.fs_tick * 0.10)

    def vy(self, v):
        """Value -> canvas y."""
        t = (v - self.lo) / float(self.hi - self.lo)
        return self.y1 - t * (self.y1 - self.y0)

    def x_labels(self, labels, centres, two_line=True):
        cv, u = self.cv, self.u
        for lbl, cxx in zip(labels, centres):
            parts = [lbl]
            if two_line and "\n" in lbl:
                parts = lbl.split("\n")
            yy = self.y1 + 34 * u
            for p in parts:
                size = self.fs_label
                maxw = (self.x1 - self.x0) / max(1, len(centres)) * 0.92
                if sf.text_width(p, size) > maxw:
                    size = size * maxw / sf.text_width(p, size)
                sf.draw_text(cv, p, cxx, yy, size, brand.INK, align="center",
                             weight=size * 0.115)
                yy += 27 * u


# ------------------------------------------------------------- bar charts ----
def grouped_bars(title, categories, series, subtitle=None, note=None,
                 y_title=None, value_dec=None, width=W, height=H,
                 show_values=True, colours=None):
    """
    series: list of (label, [values...]) - one entry per legend item.
    """
    colours = colours or brand.SERIES
    legend = [(lbl, colours[i % len(colours)])
              for i, (lbl, _v) in enumerate(series)] if len(series) > 1 else []
    f = _Frame(title, subtitle, width, height, legend=legend, note=note,
               y_title=y_title, x_lines=_xlines(categories))
    u = f.u
    cv = f.cv

    flat = [v for _l, vals in series for v in vals]
    lo, hi, step = _axis(min(0.0, min(flat)), max(flat) * 1.14, 5)
    f.y_grid(lo, hi, step, value_dec)

    n_cat = len(categories)
    n_ser = len(series)
    slot = (f.x1 - f.x0) / n_cat
    group_w = slot * 0.70
    bar_w = group_w / n_ser
    centres = []
    for ci in range(n_cat):
        c = f.x0 + slot * (ci + 0.5)
        centres.append(c)
        for si, (_lbl, vals) in enumerate(series):
            v = vals[ci]
            bx = c - group_w / 2.0 + si * bar_w
            col = colours[si % len(colours)]
            y_top = f.vy(max(v, 0.0))
            y_base = f.vy(0.0 if lo <= 0 else lo)
            hgt = abs(y_base - y_top)
            if hgt < 1.2:
                hgt = 1.2
            cv.rect(bx + bar_w * 0.09, y_top, bar_w * 0.82, hgt, col)
            # hairline top highlight for a touch of depth
            cv.rect(bx + bar_w * 0.09, y_top, bar_w * 0.82,
                    min(3.2 * u, hgt), brand.lighten(col, 0.34))
            if show_values:
                sf.draw_text(cv, _fmt(v, value_dec), bx + bar_w * 0.5,
                             y_top - 12 * u, f.fs_val, brand.darken(col, 0.15),
                             align="center", weight=f.fs_val * 0.125)
    f.x_labels(categories, centres)
    return f.footer()


def h_bars(title, labels, values, subtitle=None, note=None, width=W, height=H,
           value_dec=None, colours=None, suffix="", sort=False):
    """Horizontal bars - used for revenue mix and cost structure rankings."""
    colours = colours or brand.SERIES
    pairs = list(zip(labels, values))
    if sort:
        pairs.sort(key=lambda p: -p[1])
    labels = [p[0] for p in pairs]
    values = [p[1] for p in pairs]

    f = _Frame(title, subtitle, width, height, note=note, pad_left=430)
    u, cv = f.u, f.cv
    vmax = max(values) * 1.20
    n = len(values)
    slot = (f.y1 - f.y0) / n
    bar_h = slot * 0.58

    for k in range(4 + 1):
        gx = f.x0 + (f.x1 - f.x0) * k / 4.0
        cv.line(gx, f.y0 - 6 * u, gx, f.y1 + 6 * u, brand.GREY_HAIR, 1.6 * u)

    for i, (lbl, v) in enumerate(zip(labels, values)):
        cy = f.y0 + slot * (i + 0.5)
        col = colours[i % len(colours)]
        bw = (f.x1 - f.x0) * (v / vmax)
        cv.rect(f.x0, cy - bar_h / 2.0, bw, bar_h, col)
        cv.rect(f.x0, cy - bar_h / 2.0, min(6 * u, bw), bar_h,
                brand.darken(col, 0.22))
        size = f.fs_label
        if sf.text_width(lbl, size) > 380 * u:
            size = size * 380 * u / sf.text_width(lbl, size)
        sf.draw_text(cv, lbl, f.x0 - 18 * u, cy + size * 0.36, size, brand.INK,
                     align="right", weight=size * 0.115)
        sf.draw_text(cv, _fmt(v, value_dec) + suffix, f.x0 + bw + 14 * u,
                     cy + f.fs_val * 0.36, f.fs_val, brand.darken(col, 0.15),
                     weight=f.fs_val * 0.125)
    cv.line(f.x0, f.y0 - 6 * u, f.x0, f.y1 + 6 * u, brand.INK_SOFT, 2.6 * u)
    return f.footer()


def stacked_bars(title, categories, series, subtitle=None, note=None,
                 y_title=None, width=W, height=H, colours=None,
                 value_dec=None, show_total=True):
    """series: list of (label, [values...]) stacked bottom-up."""
    colours = colours or brand.SERIES
    legend = [(lbl, colours[i % len(colours)])
              for i, (lbl, _v) in enumerate(series)]
    f = _Frame(title, subtitle, width, height, legend=legend, note=note,
               y_title=y_title, x_lines=_xlines(categories))
    u, cv = f.u, f.cv

    totals = [sum(vals[i] for _l, vals in series)
              for i in range(len(categories))]
    lo, hi, step = _axis(0, max(totals) * 1.14, 5)
    f.y_grid(lo, hi, step, value_dec)

    slot = (f.x1 - f.x0) / len(categories)
    bar_w = slot * 0.46
    centres = []
    for ci in range(len(categories)):
        c = f.x0 + slot * (ci + 0.5)
        centres.append(c)
        running = 0.0
        for si, (_lbl, vals) in enumerate(series):
            v = vals[ci]
            y_top = f.vy(running + v)
            y_bot = f.vy(running)
            col = colours[si % len(colours)]
            cv.rect(c - bar_w / 2.0, y_top, bar_w, y_bot - y_top, col)
            if (y_bot - y_top) > f.fs_val * 1.7:
                sf.draw_text(cv, _fmt(v, value_dec), c,
                             (y_top + y_bot) / 2.0 + f.fs_val * 0.36,
                             f.fs_val, brand.PAPER, align="center",
                             weight=f.fs_val * 0.13)
            running += v
        if show_total:
            sf.draw_text(cv, _fmt(totals[ci], value_dec), c,
                         f.vy(totals[ci]) - 14 * u, f.fs_val * 1.05,
                         brand.NAVY, align="center", weight=f.fs_val * 0.14)
    f.x_labels(categories, centres)
    return f.footer()


# ------------------------------------------------------------- line / combo ----
def line_chart(title, categories, series, subtitle=None, note=None,
               y_title=None, width=W, height=H, value_dec=None,
               colours=None, suffix="", show_values=True, area=False):
    colours = colours or [brand.NAVY, brand.ORANGE, brand.TEAL, brand.PURPLE]
    legend = [(lbl, colours[i % len(colours)])
              for i, (lbl, _v) in enumerate(series)] if len(series) > 1 else []
    f = _Frame(title, subtitle, width, height, legend=legend, note=note,
               y_title=y_title, x_lines=_xlines(categories))
    u, cv = f.u, f.cv

    flat = [v for _l, vals in series for v in vals]
    pad = (max(flat) - min(flat)) * 0.28 or max(flat) * 0.2
    lo, hi, step = _axis(min(flat) - pad, max(flat) + pad, 5)
    f.y_grid(lo, hi, step, value_dec)

    slot = (f.x1 - f.x0) / len(categories)
    centres = [f.x0 + slot * (i + 0.5) for i in range(len(categories))]

    for si, (_lbl, vals) in enumerate(series):
        col = colours[si % len(colours)]
        pts = [(centres[i], f.vy(vals[i])) for i in range(len(vals))]
        if area and len(series) == 1:
            poly = pts + [(centres[-1], f.vy(f.lo)), (centres[0], f.vy(f.lo))]
            cv.fill_polygon(poly, brand.lighten(col, 0.80))
        cv.stroke_polyline(pts, col, 5.0 * u)
        for i, (px, py) in enumerate(pts):
            cv.circle(px, py, 9.5 * u, brand.PAPER)
            cv.circle(px, py, 7.0 * u, col)
            if show_values:
                sf.draw_text(cv, _fmt(vals[i], value_dec) + suffix, px,
                             py - 22 * u, f.fs_val, brand.darken(col, 0.12),
                             align="center", weight=f.fs_val * 0.125)
    f.x_labels(categories, centres)
    return f.footer()


def combo_bar_line(title, categories, bar_label, bar_values, line_label,
                   line_values, subtitle=None, note=None, width=W, height=H,
                   bar_dec=None, line_dec=1, line_suffix="%",
                   bar_colour=None, line_colour=None, y_title=None,
                   y2_title=None):
    """Bars on the left axis with a percentage line on a secondary right axis."""
    bar_colour = bar_colour or brand.NAVY
    line_colour = line_colour or brand.ORANGE
    f = _Frame(title, subtitle, width, height,
               legend=[(bar_label, bar_colour), (line_label, line_colour)],
               note=note, y_title=y_title, pad_right=132,
               x_lines=_xlines(categories))
    u, cv = f.u, f.cv

    lo, hi, step = _axis(0, max(bar_values) * 1.16, 5)
    f.y_grid(lo, hi, step, bar_dec)

    slot = (f.x1 - f.x0) / len(categories)
    centres = [f.x0 + slot * (i + 0.5) for i in range(len(categories))]
    bar_w = slot * 0.44
    for i, v in enumerate(bar_values):
        y_top = f.vy(v)
        cv.rect(centres[i] - bar_w / 2.0, y_top, bar_w, f.y1 - y_top,
                bar_colour)
        cv.rect(centres[i] - bar_w / 2.0, y_top, bar_w, 3.2 * u,
                brand.lighten(bar_colour, 0.34))
        sf.draw_text(cv, _fmt(v, bar_dec), centres[i], y_top - 12 * u,
                     f.fs_val, brand.NAVY, align="center",
                     weight=f.fs_val * 0.125)

    l2, h2, s2 = _axis(min(line_values) * 0.55, max(line_values) * 1.30, 4)

    def vy2(v):
        t = (v - l2) / float(h2 - l2)
        return f.y1 - t * (f.y1 - f.y0)

    n2 = int(round((h2 - l2) / s2))
    for k in range(n2 + 1):
        v = l2 + k * s2
        sf.draw_text(cv, _fmt(v, line_dec) + line_suffix, f.x1 + 14 * u,
                     vy2(v) + f.fs_tick * 0.36, f.fs_tick, line_colour,
                     weight=f.fs_tick * 0.11)
    cv.line(f.x1, f.y0 - 6 * u, f.x1, f.y1, brand.lighten(line_colour, 0.45),
            2.0 * u)
    if y2_title:
        sf.draw_text(cv, y2_title, f.x1 + 14 * u, f.y0 - 22 * u,
                     f.fs_tick * 0.95, brand.lighten(line_colour, 0.2),
                     weight=f.fs_tick * 0.10)

    pts = [(centres[i], vy2(line_values[i])) for i in range(len(line_values))]
    cv.stroke_polyline(pts, line_colour, 5.2 * u)
    for i, (px, py) in enumerate(pts):
        cv.circle(px, py, 10.0 * u, brand.PAPER)
        cv.circle(px, py, 7.2 * u, line_colour)
        sf.draw_text(cv, _fmt(line_values[i], line_dec) + line_suffix, px,
                     py - 22 * u, f.fs_val, brand.darken(line_colour, 0.12),
                     align="center", weight=f.fs_val * 0.125)
    f.x_labels(categories, centres)
    return f.footer()


# ------------------------------------------------------------------ donut ----
def donut(title, labels, values, subtitle=None, note=None, width=W, height=H,
          colours=None, unit_label="", value_dec=None, centre_label=None,
          centre_value=None):
    colours = colours or brand.SERIES
    f = _Frame(title, subtitle, width, height, note=note)
    u, cv = f.u, f.cv

    total = float(sum(values))
    cx = f.x0 + (f.x1 - f.x0) * 0.27
    cy = (f.y0 + f.y1) / 2.0
    r_out = min((f.y1 - f.y0) * 0.48, (f.x1 - f.x0) * 0.23)
    r_in = r_out * 0.58

    ang = 0.0
    for i, v in enumerate(values):
        sweep = 360.0 * v / total
        col = colours[i % len(colours)]
        cv.wedge(cx, cy, r_out, r_in, ang + 0.45, ang + sweep - 0.45, col)
        mid = math.radians(ang + sweep / 2.0 - 90.0)
        pct = 100.0 * v / total
        if pct >= 6.0:
            lr = (r_out + r_in) / 2.0
            sf.draw_text(cv, _fmt(pct, 1) + "%", cx + lr * math.cos(mid),
                         cy + lr * math.sin(mid) + f.fs_val * 0.36,
                         f.fs_val, brand.PAPER, align="center",
                         weight=f.fs_val * 0.14)
        ang += sweep

    if centre_label:
        sf.draw_text(cv, centre_label, cx, cy - 18 * u, f.fs_sub * 0.80,
                     brand.GREY, align="center", weight=f.fs_sub * 0.10,
                     tracking=2.2 * u)
    if centre_value:
        sf.draw_text(cv, centre_value, cx, cy + 26 * u, f.fs_title * 0.90,
                     brand.NAVY, align="center", weight=f.fs_title * 0.14)

    # Right-hand key with values, aligned as a small table
    lx = cx + r_out + 74 * u
    n = len(values)
    row = min(62 * u, (f.y1 - f.y0) / max(1, n))
    ty = cy - row * (n - 1) / 2.0
    for i, (lbl, v) in enumerate(zip(labels, values)):
        col = colours[i % len(colours)]
        cv.round_rect(lx, ty - 15 * u, 28 * u, 18 * u, 4 * u, col)
        size = f.fs_leg
        avail = f.x1 - (lx + 40 * u) - 170 * u
        if sf.text_width(lbl, size) > avail:
            size = size * avail / sf.text_width(lbl, size)
        sf.draw_text(cv, lbl, lx + 40 * u, ty, size, brand.INK,
                     weight=size * 0.115)
        sf.draw_text(cv, _fmt(v, value_dec) + unit_label, f.x1, ty,
                     f.fs_leg, brand.NAVY, align="right",
                     weight=f.fs_leg * 0.135)
        ty += row
    return f.footer()


# -------------------------------------------------------------- waterfall ----
def waterfall(title, labels, deltas, subtitle=None, note=None, width=W,
              height=H, value_dec=1, start_label=None, start_value=0.0,
              end_label=None, y_title=None):
    """
    Cash-flow style bridge. `deltas` are signed movements; pass start/end labels
    to pin the opening and closing totals as solid columns.
    """
    f = _Frame(title, subtitle, width, height, note=note, y_title=y_title,
               legend=[("Increase", brand.GREEN), ("Decrease", brand.RED),
                       ("Total", brand.NAVY)],
               x_lines=_xlines(list(labels) + [start_label or "", end_label or ""]))
    u, cv = f.u, f.cv

    cats, kinds, tops, bots = [], [], [], []
    run = start_value
    if start_label:
        cats.append(start_label)
        kinds.append("total")
        tops.append(max(0.0, run))
        bots.append(min(0.0, run))
    for lbl, d in zip(labels, deltas):
        cats.append(lbl)
        kinds.append("up" if d >= 0 else "down")
        tops.append(max(run, run + d))
        bots.append(min(run, run + d))
        run += d
    if end_label:
        cats.append(end_label)
        kinds.append("total")
        tops.append(max(0.0, run))
        bots.append(min(0.0, run))

    vmax = max(tops + [0.0])
    vmin = min(bots + [0.0])
    lo, hi, step = _axis(vmin - abs(vmax) * 0.04, vmax * 1.16, 5)
    f.y_grid(lo, hi, step, value_dec)

    slot = (f.x1 - f.x0) / len(cats)
    bar_w = slot * 0.54
    centres = []
    prev_x = None
    for i, lbl in enumerate(cats):
        c = f.x0 + slot * (i + 0.5)
        centres.append(c)
        col = {"up": brand.GREEN, "down": brand.RED,
               "total": brand.NAVY}[kinds[i]]
        yt, yb = f.vy(tops[i]), f.vy(bots[i])
        if yb - yt < 2.0:
            yt, yb = yt - 1.0, yt + 1.0
        cv.rect(c - bar_w / 2.0, yt, bar_w, yb - yt, col)
        val = tops[i] if kinds[i] == "total" else (tops[i] - bots[i])
        if kinds[i] == "down":
            val = -val
        txt = ("+" if (kinds[i] == "up") else "") + _fmt(val, value_dec)
        sf.draw_text(cv, txt, c, yt - 13 * u, f.fs_val,
                     brand.darken(col, 0.12), align="center",
                     weight=f.fs_val * 0.125)
        if prev_x is not None:
            link_y = f.vy(tops[i] if kinds[i] == "up" else bots[i])
            if kinds[i] == "total":
                link_y = f.vy(tops[i])
            cv.line(prev_x, link_y, c - bar_w / 2.0, link_y, brand.GREY,
                    1.8 * u)
        prev_x = c + bar_w / 2.0
    f.x_labels(cats, centres)
    return f.footer()


# ----------------------------------------------------------- variance bars ----
def variance_bars(title, labels, values, subtitle=None, note=None, width=W,
                  height=H, value_dec=2, suffix="%", y_title=None):
    """Diverging horizontal bars: favourable right in green, adverse left in red."""
    f = _Frame(title, subtitle, width, height, note=note, pad_left=430,
               legend=[("Favourable", brand.GREEN), ("Adverse", brand.RED)])
    u, cv = f.u, f.cv
    span = max(abs(min(values)), abs(max(values))) * 1.32
    zx = (f.x0 + f.x1) / 2.0
    half = (f.x1 - f.x0) / 2.0
    n = len(values)
    slot = (f.y1 - f.y0) / n
    bar_h = slot * 0.56

    for k in (-1.0, -0.5, 0.5, 1.0):
        gx = zx + half * k
        cv.line(gx, f.y0 - 6 * u, gx, f.y1 + 6 * u, brand.GREY_HAIR, 1.6 * u)
        sf.draw_text(cv, _fmt(span * k, 0) + suffix, gx, f.y1 + 34 * u,
                     f.fs_tick * 0.92, brand.GREY, align="center",
                     weight=f.fs_tick * 0.10)

    for i, (lbl, v) in enumerate(zip(labels, values)):
        cy = f.y0 + slot * (i + 0.5)
        col = brand.GREEN if v >= 0 else brand.RED
        bw = half * (abs(v) / span)
        x = zx if v >= 0 else zx - bw
        cv.rect(x, cy - bar_h / 2.0, bw, bar_h, col)
        size = f.fs_label
        if sf.text_width(lbl, size) > 380 * u:
            size = size * 380 * u / sf.text_width(lbl, size)
        sf.draw_text(cv, lbl, f.x0 - 18 * u, cy + size * 0.36, size,
                     brand.INK, align="right", weight=size * 0.115)
        txt = ("+" if v >= 0 else "") + _fmt(v, value_dec) + suffix
        tx = zx + bw + 14 * u if v >= 0 else zx - bw - 14 * u
        sf.draw_text(cv, txt, tx, cy + f.fs_val * 0.36, f.fs_val,
                     brand.darken(col, 0.12),
                     align="left" if v >= 0 else "right",
                     weight=f.fs_val * 0.125)
    cv.line(zx, f.y0 - 6 * u, zx, f.y1 + 6 * u, brand.INK_SOFT, 2.8 * u)
    return f.footer()


# ------------------------------------------------------------- break-even ----
def breakeven(title, sales_max, fixed, pv_ratio, actual_sales,
              subtitle=None, note=None, width=W, height=H, unit="\u20b9 Lakh"):
    """Classic cost-volume-profit chart with the break-even point annotated."""
    f = _Frame(title, subtitle, width, height, y_title=unit, note=note,
               x_lines=2,
               legend=[("Total Sales", brand.NAVY),
                       ("Total Cost", brand.ORANGE),
                       ("Fixed Cost", brand.GREY)])
    u, cv = f.u, f.cv
    vc_rate = 1.0 - pv_ratio
    top = sales_max * 1.06
    lo, hi, step = _axis(0, top, 5)
    f.y_grid(lo, hi, step, 0)

    def vx(s):
        return f.x0 + (f.x1 - f.x0) * (s / sales_max)

    x_step = _nice_step(sales_max / 5.0)
    k = 0
    while k * x_step <= sales_max + 1e-9:
        gx = vx(k * x_step)
        cv.line(gx, f.y0 - 6 * u, gx, f.y1, brand.GREY_HAIR, 1.6 * u)
        sf.draw_text(cv, _fmt(k * x_step, 0), gx, f.y1 + 32 * u,
                     f.fs_tick * 0.92, brand.INK_SOFT, align="center",
                     weight=f.fs_tick * 0.10)
        k += 1

    bep = fixed / pv_ratio

    # shaded loss / profit wedges
    cv.fill_polygon([(vx(0), f.vy(0)), (vx(bep), f.vy(bep)),
                     (vx(0), f.vy(fixed))], brand.RED_PALE)
    cv.fill_polygon([(vx(bep), f.vy(bep)), (vx(sales_max), f.vy(sales_max)),
                     (vx(sales_max), f.vy(fixed + vc_rate * sales_max))],
                    brand.GREEN_PALE)

    cv.stroke_polyline([(vx(0), f.vy(fixed)), (vx(sales_max), f.vy(fixed))],
                       brand.GREY, 4.0 * u)
    cv.stroke_polyline([(vx(0), f.vy(fixed)),
                        (vx(sales_max), f.vy(fixed + vc_rate * sales_max))],
                       brand.ORANGE, 5.0 * u)
    cv.stroke_polyline([(vx(0), f.vy(0)), (vx(sales_max), f.vy(sales_max))],
                       brand.NAVY, 5.0 * u)

    # break-even marker
    bx, by = vx(bep), f.vy(bep)
    for yy in range(int(by), int(f.y1), int(max(6, 14 * u))):
        cv.line(bx, yy, bx, min(yy + 7 * u, f.y1), brand.NAVY_MID, 2.2 * u)
    cv.circle(bx, by, 13 * u, brand.PAPER)
    cv.circle(bx, by, 9 * u, brand.NAVY)
    sf.draw_text(cv, "BREAK-EVEN  " + _fmt(bep, 2), bx + 22 * u,
                 by + 40 * u, f.fs_val * 1.02, brand.NAVY,
                 weight=f.fs_val * 0.14)

    ax = vx(actual_sales)
    cv.line(ax, f.y0 - 4 * u, ax, f.y1, brand.TEAL, 2.6 * u)
    sf.draw_text(cv, "Actual  " + _fmt(actual_sales, 2), ax - 16 * u,
                 f.y0 + 22 * u, f.fs_val, brand.TEAL, align="right",
                 weight=f.fs_val * 0.13)
    sf.draw_text(cv, "MARGIN OF SAFETY", (bx + ax) / 2.0, f.y1 - 18 * u,
                 f.fs_val * 0.92, brand.darken(brand.GREEN, 0.1),
                 align="center", weight=f.fs_val * 0.11)
    sf.draw_text(cv, "Sales (" + unit + ")", (f.x0 + f.x1) / 2.0,
                 f.y1 + 66 * u, f.fs_label, brand.INK, align="center",
                 weight=f.fs_label * 0.115)
    return f.footer()


# ------------------------------------------------------------ radar / gauge ----
def gauge_row(title, items, subtitle=None, note=None, width=W, height=None,
              unit=""):
    """
    A row of dial gauges - used to show headline ratios at a glance.
    items: list of (label, value, vmin, vmax, benchmark or None, decimals)
    """
    height = height or int(width * 0.27)
    f = _Frame(title, subtitle, width, height, note=note)
    u, cv = f.u, f.cv
    n = len(items)
    slot = (f.x1 - f.x0) / n
    r = max(30 * u, min(slot * 0.33, (f.y1 - f.y0) - 46 * u))
    cy = f.y0 + r + 6 * u

    for i, (lbl, val, vmin, vmax, bench, dec) in enumerate(items):
        cx = f.x0 + slot * (i + 0.5)
        cv.wedge(cx, cy, r, r * 0.68, -90, 90, brand.GREY_HAIR)
        frac = (val - vmin) / float(vmax - vmin)
        frac = max(0.0, min(1.0, frac))
        col = brand.SERIES[i % len(brand.SERIES)]
        cv.wedge(cx, cy, r, r * 0.68, -90, -90 + 180.0 * frac, col)
        if bench is not None:
            bf = max(0.0, min(1.0, (bench - vmin) / float(vmax - vmin)))
            a = math.radians(-90 + 180.0 * bf - 90.0)
            cv.stroke_polyline([(cx + r * 0.62 * math.cos(a),
                                 cy + r * 0.62 * math.sin(a)),
                                (cx + r * 1.06 * math.cos(a),
                                 cy + r * 1.06 * math.sin(a))],
                               brand.INK, 3.2 * u)
        sf.draw_text(cv, _fmt(val, dec) + unit, cx, cy - 4 * u,
                     f.fs_title * 0.86, brand.NAVY, align="center",
                     weight=f.fs_title * 0.14)
        size = f.fs_leg
        if sf.text_width(lbl, size) > slot * 0.94:
            size = size * slot * 0.94 / sf.text_width(lbl, size)
        sf.draw_text(cv, lbl, cx, cy + 34 * u, size, brand.INK_SOFT,
                     align="center", weight=size * 0.115)
    return f.footer()
