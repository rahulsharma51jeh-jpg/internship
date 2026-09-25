"""
diagrams.py -- vector business diagrams (org charts, flows, cycles, matrices,
trees, roadmaps) drawn with pdfengine primitives.
Signature: f(d, x, y, w, h, ...) with (x, y) the bottom-left of the block.
"""

import math
from pdfengine import (NAVY, NAVY_D, BLUE, BLUE_M, BLUE_L, BLUE_XL, ORANGE, ORANGE_L, ORANGE_XL,
                       GREEN, GREEN_L, RED, RED_L, TEAL, PURPLE, GOLD, GREY_D, GREY, GREY_M,
                       GREY_L, GREY_XL, WHITE, SERIES)


# --------------------------------------------------------------------------
# primitives
# --------------------------------------------------------------------------
def box(d, x, y, w, h, title, subtitle=None, fill=WHITE, stroke=GREY_M, tcolor=NAVY,
        size=8.4, sub_size=6.9, sub_color=GREY, r=3.0, lw=0.8, bar=None, title_font="semibold",
        pad=5.0, align="center"):
    d.round_rect(x, y, w, h, r, fill=fill, stroke=stroke, lw=lw)
    if bar:
        d.round_rect(x, y, 3.4, h, 1.6, fill=bar)
    lines = d.wrap(title, w - 2 * pad - (4 if bar else 0), title_font, size)
    sub_lines = d.wrap(subtitle, w - 2 * pad, "regular", sub_size) if subtitle else []
    total = len(lines) * (size + 2.0) + (len(sub_lines) * (sub_size + 1.6) + 2 if sub_lines else 0)
    ty = y + h / 2.0 + total / 2.0 - size
    for ln in lines:
        if align == "left":
            d.text(x + pad + (4 if bar else 0), ty, ln, title_font, size, tcolor)
        else:
            d.text_center(x + w / 2.0, ty, ln, title_font, size, tcolor)
        ty -= size + 2.0
    ty -= 1.5
    for ln in sub_lines:
        if align == "left":
            d.text(x + pad + (4 if bar else 0), ty, ln, "regular", sub_size, sub_color)
        else:
            d.text_center(x + w / 2.0, ty, ln, "regular", sub_size, sub_color)
        ty -= sub_size + 1.6


def chip(d, cx, cy, text, fill=NAVY, tcolor=WHITE, size=7.4, pad=6.0, h=14.0):
    w = d.width(text, "semibold", size) + 2 * pad
    d.round_rect(cx - w / 2.0, cy - h / 2.0, w, h, h / 2.0, fill=fill)
    d.text_center(cx, cy - size * 0.35, text, "semibold", size, tcolor)
    return w


def badge_num(d, cx, cy, n, r=8.0, fill=ORANGE, tcolor=WHITE, size=8.0):
    d.circle(cx, cy, r, fill=fill)
    d.text_center(cx, cy - size * 0.35, str(n), "bold", size, tcolor)


# --------------------------------------------------------------------------
# 1. organisation chart
# --------------------------------------------------------------------------
def org_chart(d, x, y, w, h, top, level2, level3=None):
    """top: (title, sub). level2/3: list of (title, sub, color)."""
    box_h = 30.0
    top_w = min(w * 0.44, 210)
    top_y = y + h - box_h
    box(d, x + (w - top_w) / 2.0, top_y, top_w, box_h, top[0], top[1], fill=NAVY, stroke=NAVY,
        tcolor=WHITE, sub_color=BLUE_L, size=9.4)
    n = len(level2)
    gap = 8.0
    cw = (w - gap * (n - 1)) / float(n)
    l2_y = top_y - 52
    bus_y = l2_y + box_h + 20
    d.line(x + w / 2.0, top_y, x + w / 2.0, bus_y, GREY_M, 0.9)
    centers = []
    for i, (t, s, col) in enumerate(level2):
        bx = x + i * (cw + gap)
        cx = bx + cw / 2.0
        centers.append((cx, bx))
        d.line(cx, bus_y, cx, l2_y + box_h, GREY_M, 0.9)
        box(d, bx, l2_y, cw, box_h, t, s, fill=BLUE_XL, stroke=BLUE_L, tcolor=NAVY, size=8.0,
            bar=col)
    xs = [c[0] for c in centers]
    d.line(min(xs), bus_y, max(xs), bus_y, GREY_M, 0.9)
    if level3:
        l3_y = l2_y - 46
        for i, (t, s, col) in enumerate(level3):
            cx, bx = centers[i]
            d.line(cx, l2_y, cx, l3_y + 28, GREY_L, 0.8, dash=(2, 2))
            box(d, bx + cw * 0.06, l3_y, cw * 0.88, 28, t, s, fill=GREY_XL, stroke=GREY_L,
                tcolor=GREY_D, size=7.4, sub_size=6.4)
        # highlight the finance branch
        cx, bx = centers[0]
        d.round_rect(bx - 4, l3_y - 6, cw + 8, (l2_y + box_h) - (l3_y - 6) + 6, 4,
                     stroke=ORANGE, lw=1.1)
        d.text(bx - 4, l3_y - 16, "Internship placement", "semibolditalic", 7.0, ORANGE)


# --------------------------------------------------------------------------
# 2. horizontal chevron process
# --------------------------------------------------------------------------
def chevrons(d, x, y, w, h, steps, colors=None, size=8.0, sub_size=6.6, notch=9.0,
             numbered=True):
    """Horizontal chevron process band; sub-captions are dropped automatically
    when the available step width is too narrow to hold them legibly."""
    n = len(steps)
    gap = 3.0
    bw = (w - gap * (n - 1)) / float(n)
    bh = min(h, 46.0)
    by = y + (h - bh) / 2.0
    avail = bw - notch - 12
    if avail < 54:
        sub_size = 0            # no room: show titles only
    elif avail < 72:
        sub_size = min(sub_size, 6.0)
    if avail < 46:
        size = min(size, 7.2)
    for i, st in enumerate(steps):
        title = st[0]
        sub = (st[1] if len(st) > 1 else None) if sub_size else None
        col = (colors[i] if colors else _ramp(i, n))
        bx = x + i * (bw + gap)
        pts = [(bx, by), (bx + bw - notch, by), (bx + bw, by + bh / 2.0), (bx + bw - notch, by + bh),
               (bx, by + bh)]
        if i > 0:
            pts.append((bx + notch, by + bh / 2.0))
        d.polygon(pts, fill=col)
        tx = bx + (notch if i else 6) + 3
        title_lines = d.wrap(title, avail, "semibold", size)[:2]
        sub_lines = d.wrap(sub, avail, "regular", sub_size)[:2] if sub else []
        if numbered:
            d.text(tx, by + bh - 11, "STEP %d" % (i + 1), "bold", 5.8, WHITE)
        block = len(title_lines) * (size + 1.4) + len(sub_lines) * (sub_size + 1.2)
        top = by + bh / 2.0 + block / 2.0 - size - (3.0 if numbered else 0)
        ty = top
        for ln in title_lines:
            d.text(tx, ty, ln, "semibold", size, WHITE)
            ty -= size + 1.4
        for ln in sub_lines:
            d.text(tx, ty - 0.8, ln, "regular", sub_size, WHITE)
            ty -= sub_size + 1.2


def _ramp(i, n):
    t = i / float(max(n - 1, 1))
    c1, c2 = NAVY, BLUE_M
    return (c1[0] + (c2[0] - c1[0]) * t, c1[1] + (c2[1] - c1[1]) * t, c1[2] + (c2[2] - c1[2]) * t)


# --------------------------------------------------------------------------
# 3. vertical flowchart with decision diamonds
# --------------------------------------------------------------------------
def flowchart(d, x, y, w, h, nodes, col_w=205.0, gap=14.0, side_notes=None):
    """nodes: list of (kind, text) where kind in start|process|decision|end|doc."""
    n = len(nodes)
    total_gap = gap * (n - 1)
    nh = (h - total_gap) / float(n)
    nh = min(nh, 34.0)
    cx = x + col_w / 2.0 + 10
    top = y + h
    ys = []
    for i, (kind, text) in enumerate(nodes):
        ny = top - nh - i * (nh + gap)
        ys.append(ny)
        if kind == "decision":
            tw = d.width(text, "semibold", 7.2) + 34
            hw = max(col_w * 0.62, min(col_w * 1.05, tw))
            hh = nh * 1.18
            d.polygon([(cx, ny + nh / 2.0 + hh / 2.0), (cx + hw / 2.0, ny + nh / 2.0),
                       (cx, ny + nh / 2.0 - hh / 2.0), (cx - hw / 2.0, ny + nh / 2.0)],
                      fill=ORANGE_XL, stroke=ORANGE, lw=1.0)
            lines = d.wrap(text, hw * 0.62, "semibold", 7.2)[:2]
            for j, ln in enumerate(lines):
                d.text_center(cx, ny + nh / 2.0 + (len(lines) - 1) * 4.6 - j * 9.2 - 2.6,
                              ln, "semibold", 7.2, ORANGE)
        elif kind in ("start", "end"):
            bw = max(col_w * 0.60, min(col_w * 1.02, d.width(text, "bold", 8.0) + 26))
            d.round_rect(cx - bw / 2.0, ny + 4, bw, nh - 8, (nh - 8) / 2.0,
                         fill=NAVY if kind == "start" else GREEN, stroke=None)
            d.text_center(cx, ny + nh / 2.0 - 2.9, text, "bold", 8.0, WHITE)
        elif kind == "doc":
            bw = min(col_w * 1.02, max(col_w * 0.78, d.width(text, "regular", 7.6) + 26))
            bx = cx - bw / 2.0
            d.round_rect(bx, ny + 3, bw, nh - 6, 2.0, fill=BLUE_XL, stroke=BLUE_L, lw=0.9)
            d.line(bx + 6, ny + nh - 9, bx + bw - 6, ny + nh - 9, BLUE_L, 0.6)
            for j, ln in enumerate(d.wrap(text, bw - 12, "regular", 7.6)[:2]):
                d.text_center(cx, ny + nh / 2.0 + (2.6 if j == 0 else -5.4), ln, "regular", 7.6, NAVY)
        else:
            bw = min(col_w * 1.04, max(col_w * 0.80, d.width(text, "semibold", 7.8) + 26))
            box(d, cx - bw / 2.0, ny + 3, bw, nh - 6, text, None, fill=WHITE, stroke=BLUE_M,
                tcolor=NAVY_D, size=7.8, lw=0.9, bar=BLUE)
        if i:
            d.arrow(cx, ys[i - 1], cx, ny + nh, GREY, 0.9, 4.6)
    if side_notes:
        for idx, note, col in side_notes:
            ny = ys[idx]
            nx = cx + col_w * 0.5 + 16
            d.line(cx + col_w * 0.44, ny + nh / 2.0, nx - 4, ny + nh / 2.0, col, 0.7, dash=(2, 1.8))
            lines = d.wrap(note, (x + w) - nx - 4, "italic", 7.2)
            for j, ln in enumerate(lines):
                d.text(nx, ny + nh / 2.0 + (len(lines) - 1) * 4.4 - j * 9.0 - 2.4, ln,
                       "italic", 7.2, col)


# --------------------------------------------------------------------------
# 4. circular cycle
# --------------------------------------------------------------------------
def cycle(d, x, y, w, h, stages, center_title=None, center_sub=None, colors=None,
          r_frac=0.36, size=7.6):
    cx = x + w / 2.0
    cy = y + h / 2.0
    R = min(w * 0.30, h * 0.42)
    n = len(stages)
    for i in range(n):
        a0 = 90 - 360.0 * i / n - 4
        a1 = 90 - 360.0 * (i + 1) / n + 4
        col = colors[i] if colors else _ramp(i, n)
        d.wedge(cx, cy, R, a0, a1, fill=col, r_inner=R * 0.60)
        mid = math.radians((a0 + a1) / 2.0)
        # arrow head at segment end
        ae = math.radians(a1 - 1)
        rr = R * 0.80
        d.polygon([(cx + math.cos(ae) * (rr + 5.5), cy + math.sin(ae) * (rr + 5.5)),
                   (cx + math.cos(ae - 0.055) * (rr - 4.5), cy + math.sin(ae - 0.055) * (rr - 4.5)),
                   (cx + math.cos(ae + 0.055) * (rr - 4.5), cy + math.sin(ae + 0.055) * (rr - 4.5))],
                  fill=WHITE)
        badge_num(d, cx + math.cos(mid) * R * 0.80, cy + math.sin(mid) * R * 0.80, i + 1,
                  r=7.0, fill=WHITE, tcolor=col, size=7.6)
        lx = cx + math.cos(mid) * (R + 12)
        ly = cy + math.sin(mid) * (R + 12)
        title = stages[i][0]
        sub = stages[i][1] if len(stages[i]) > 1 else None
        aw = max(60.0, min(120.0, (w / 2.0 - R - 16)))
        lines = d.wrap(title, aw, "semibold", size)
        sublines = d.wrap(sub, aw, "regular", 6.6)[:3] if sub else []
        block = len(lines) * (size + 1.6) + len(sublines) * 7.6
        ty = ly + block / 2.0 - size
        for ln in lines:
            if abs(math.cos(mid)) < 0.25:
                d.text_center(lx, ty, ln, "semibold", size, NAVY)
            elif math.cos(mid) > 0:
                d.text(lx + 2, ty, ln, "semibold", size, NAVY)
            else:
                d.text_right(lx - 2, ty, ln, "semibold", size, NAVY)
            ty -= size + 1.6
        for ln in sublines:
            if abs(math.cos(mid)) < 0.25:
                d.text_center(lx, ty, ln, "regular", 6.6, GREY)
            elif math.cos(mid) > 0:
                d.text(lx + 2, ty, ln, "regular", 6.6, GREY)
            else:
                d.text_right(lx - 2, ty, ln, "regular", 6.6, GREY)
            ty -= 7.6
    if center_title:
        for j, ln in enumerate(d.wrap(center_title, R * 1.0, "bold", 8.6)[:3]):
            d.text_center(cx, cy + 4 - j * 10, ln, "bold", 8.6, NAVY)
    if center_sub:
        d.text_center(cx, cy - 13, center_sub, "regular", 6.6, GREY)


# --------------------------------------------------------------------------
# 5. SWOT quadrants
# --------------------------------------------------------------------------
def swot(d, x, y, w, h, s, wk, o, t, size=7.3, head_h=17.0):
    gap = 7.0
    qw = (w - gap) / 2.0
    qh = (h - gap) / 2.0
    quads = [("STRENGTHS", s, NAVY, BLUE_XL, "S"), ("WEAKNESSES", wk, ORANGE, ORANGE_XL, "W"),
             ("OPPORTUNITIES", TEAL, GREEN_L, None, None), ("THREATS", None, None, None, None)]
    data = [("STRENGTHS", s, NAVY, BLUE_XL), ("WEAKNESSES", wk, ORANGE, ORANGE_XL),
            ("OPPORTUNITIES", o, TEAL, GREEN_L), ("THREATS", t, RED, RED_L)]
    pos = [(x, y + qh + gap), (x + qw + gap, y + qh + gap), (x, y), (x + qw + gap, y)]
    # shrink the body text until the longest quadrant fits inside its box
    avail = qh - head_h - 14
    for trial in (size, 7.0, 6.8, 6.5, 6.2, 6.0):
        need = 0
        for (_, items, _, _) in data:
            block = 0
            for it in items:
                block += len(d.wrap(it, qw - 24, "regular", trial)) * (trial + 2.2) + 2.4
            need = max(need, block)
        size = trial
        if need <= avail:
            break
    for (title, items, col, bg), (bx, by) in zip(data, pos):
        d.round_rect(bx, by, qw, qh, 3.0, fill=_soft(bg), stroke=col, lw=0.8)
        d.round_rect(bx, by + qh - head_h, qw, head_h, 3.0, fill=col)
        d.rect(bx, by + qh - head_h, qw, 3.0, fill=col)
        d.text(bx + 9, by + qh - head_h / 2.0 - 3.0, title, "bold", 8.0, WHITE, char_space=1.2)
        ty = by + qh - head_h - 9
        for it in items:
            lines = d.wrap(it, qw - 24, "regular", size)
            for j, ln in enumerate(lines):
                if j == 0:
                    d.circle(bx + 10, ty + size * 0.3, 1.6, fill=col)
                d.text(bx + 16, ty, ln, "regular", size, GREY_D)
                ty -= size + 2.2
            ty -= 2.4


def _soft(c, f=0.74):
    return (c[0] + (1 - c[0]) * f, c[1] + (1 - c[1]) * f, c[2] + (1 - c[2]) * f)


# --------------------------------------------------------------------------
# 6. pyramid
# --------------------------------------------------------------------------
def pyramid(d, x, y, w, h, layers, side_notes=True, size=8.0):
    """layers: list of (title, note, color) bottom-first."""
    n = len(layers)
    lh = h / float(n) - 4
    max_w = w * 0.56
    cx = x + max_w / 2.0 + 6
    for i, (title, note, col) in enumerate(layers):
        frac_b = 1.0 - i / float(n) * 0.72
        frac_t = 1.0 - (i + 1) / float(n) * 0.72
        by = y + i * (lh + 4)
        wb = max_w * frac_b
        wt = max_w * frac_t
        d.polygon([(cx - wb / 2.0, by), (cx + wb / 2.0, by), (cx + wt / 2.0, by + lh),
                   (cx - wt / 2.0, by + lh)], fill=col)
        d.text_center(cx, by + lh / 2.0 - 3.0, title, "semibold", size, WHITE)
        if side_notes and note:
            nx = x + max_w + 22
            d.line(cx + wb / 2.0 + 2, by + lh / 2.0, nx - 5, by + lh / 2.0, col, 0.7, dash=(2, 1.8))
            lines = d.wrap(note, (x + w) - nx, "regular", 7.2)
            for j, ln in enumerate(lines):
                d.text(nx, by + lh / 2.0 + (len(lines) - 1) * 4.4 - j * 8.8 - 2.4, ln,
                       "regular", 7.2, GREY_D)


# --------------------------------------------------------------------------
# 7. DuPont / driver tree
# --------------------------------------------------------------------------
def driver_tree(d, x, y, w, h, root, level1, level2=None, op="x"):
    """root: (label, value). level1: list of (label, value, color).
       level2: list of list of (label, value) feeding each level1 node."""
    rw, rh = min(190.0, w * 0.42), 36.0
    rx = x + (w - rw) / 2.0
    ry = y + h - rh
    d.round_rect(rx, ry, rw, rh, 3.0, fill=NAVY, stroke=NAVY)
    d.text_center(rx + rw / 2.0, ry + rh - 14, root[0], "semibold", 8.4, WHITE)
    d.text_center(rx + rw / 2.0, ry + 7, root[1], "bold", 13.0, ORANGE_L)
    n = len(level1)
    gap = 16.0
    cw = (w - gap * (n - 1)) / float(n)
    l1_h = 40.0
    l1_y = ry - 64
    bus = l1_y + l1_h + 12
    d.line(x + w / 2.0, ry, x + w / 2.0, bus, GREY_M, 0.9)
    cxs = []
    for i, (lab, val, col) in enumerate(level1):
        bx = x + i * (cw + gap)
        cx = bx + cw / 2.0
        cxs.append((cx, bx))
        d.line(cx, bus, cx, l1_y + l1_h, GREY_M, 0.9)
        d.round_rect(bx, l1_y, cw, l1_h, 3.0, fill=WHITE, stroke=col, lw=1.1)
        d.rect(bx, l1_y, cw, 3.0, fill=col)
        for j, ln in enumerate(d.wrap(lab, cw - 10, "semibold", 7.8)[:2]):
            d.text_center(cx, l1_y + l1_h - 12 - j * 9, ln, "semibold", 7.8, NAVY)
        d.text_center(cx, l1_y + 7, val, "bold", 11.0, col)
        if i:
            px = (cxs[i - 1][0] + cx) / 2.0
            d.circle(px, bus, 7.0, fill=GREY_XL, stroke=GREY_M, lw=0.7)
            d.text_center(px, bus - 3.0, op, "bold", 8.6, GREY_D)
    d.line(cxs[0][0], bus, cxs[-1][0], bus, GREY_M, 0.9)
    if level2:
        l2_y = l1_y - 44
        for i, group in enumerate(level2):
            cx, bx = cxs[i]
            d.line(cx, l1_y, cx, l2_y + 30, GREY_L, 0.8, dash=(2, 2))
            m = len(group)
            sw = (cw - 6 * (m - 1)) / float(m)
            for k, (lab, val) in enumerate(group):
                sx = bx + k * (sw + 6)
                d.round_rect(sx, l2_y, sw, 30, 2.4, fill=GREY_XL, stroke=GREY_L, lw=0.7)
                for j, ln in enumerate(d.wrap(lab, sw - 8, "regular", 6.7)[:2]):
                    d.text_center(sx + sw / 2.0, l2_y + 20 - j * 7.6, ln, "regular", 6.7, GREY_D)
                d.text_center(sx + sw / 2.0, l2_y + 5, val, "bold", 7.6, NAVY)


# --------------------------------------------------------------------------
# 8. roadmap / timeline
# --------------------------------------------------------------------------
def roadmap(d, x, y, w, h, phases, size=8.0):
    """phases: list of (horizon, title, items, color).  Cards alternate above and
    below a central time band; card height adapts to the longest phase."""
    n = len(phases)
    cw = w / float(n)
    # height needed by the wordiest card
    needed = 0.0
    for (_, title, items, _) in phases:
        block = 15.0
        for it in items:
            block += len(d.wrap(it, cw - 30, "regular", 6.9)) * 8.4 + 1.6
        needed = max(needed, block + 10)
    bh = min(needed, (h - 34) / 2.0)
    band_y = y + bh + 14
    d.round_rect(x, band_y, w, 18, 9, fill=GREY_XL)
    d.polygon([(x + w, band_y - 5), (x + w + 10, band_y + 9), (x + w, band_y + 23)], fill=GREY_L)
    for i, (hz, title, items, col) in enumerate(phases):
        cx = x + cw * (i + 0.5)
        d.round_rect(x + cw * i + 3, band_y + 2, cw - 6, 14, 7, fill=col)
        d.text_center(cx, band_y + 5.4, hz, "bold", 7.4, WHITE)
        above = (i % 2 == 0)
        by = (band_y + 26) if above else (band_y - bh - 8)
        d.round_rect(x + cw * i + 6, by, cw - 12, bh, 3.0, fill=WHITE, stroke=col, lw=0.9)
        d.rect(x + cw * i + 6, by + (bh - 3 if above else 0), cw - 12, 3, fill=col)
        d.line(cx, band_y + (20 if above else -2), cx, by + (0 if above else bh), col, 0.8,
               dash=(2, 1.6))
        ty = by + bh - 13
        d.text(x + cw * i + 13, ty, title, "semibold", size, NAVY)
        ty -= 12
        for it in items:
            lines = d.wrap(it, cw - 30, "regular", 6.9)
            for j, ln in enumerate(lines):
                if j == 0:
                    d.circle(x + cw * i + 15, ty + 2.4, 1.4, fill=col)
                d.text(x + cw * i + 20, ty, ln, "regular", 6.9, GREY_D)
                ty -= 8.4
            ty -= 1.6


# --------------------------------------------------------------------------
# 9. fishbone (Ishikawa)
# --------------------------------------------------------------------------
def fishbone(d, x, y, w, h, effect, bones, size=7.4):
    """bones: list of (category, [causes]) -- alternates above/below the spine."""
    spine_y = y + h / 2.0
    head_w = 96.0
    sx = x + 14
    ex = x + w - head_w - 8
    d.polyline([(sx, spine_y), (ex, spine_y)], NAVY, 1.6)
    d.polygon([(ex, spine_y + 5), (ex + 9, spine_y), (ex, spine_y - 5)], fill=NAVY)
    d.round_rect(ex + 10, spine_y - 20, head_w, 40, 4.0, fill=NAVY, stroke=NAVY)
    for j, ln in enumerate(d.wrap(effect, head_w - 12, "bold", 8.0)[:4]):
        d.text_center(ex + 10 + head_w / 2.0, spine_y + 8 - j * 9.6, ln, "bold", 8.0, WHITE)
    n = len(bones)
    span = (ex - sx)
    pairs = (n + 1) // 2
    for i, (cat, causes) in enumerate(bones):
        up = (i % 2 == 0)
        bx = sx + span * (0.12 + 0.50 * (i // 2) / float(max(pairs - 1, 1)))
        rise = (h / 2.0) * 0.74
        tipx = bx + rise * 0.52
        tipy = spine_y + (rise if up else -rise)
        col = SERIES[i % len(SERIES)]
        d.polyline([(bx, spine_y), (tipx, tipy)], col, 1.2)
        d.round_rect(tipx - 34, tipy + (2 if up else -15), 68, 13, 6.5, fill=col)
        d.text_center(tipx, tipy + (5.4 if up else -11.6), cat, "bold", 6.8, WHITE)
        for k, cause in enumerate(causes[:3]):
            t = 0.30 + 0.24 * k
            px = bx + (tipx - bx) * t
            py = spine_y + (tipy - spine_y) * t
            d.line(px, py, px + 22, py, GREY_M, 0.6)
            for j, ln in enumerate(d.wrap(cause, 92, "regular", 6.5)[:2]):
                d.text(px + 25, py - 2.2 - j * 7.2, ln, "regular", 6.5, GREY_D)


# --------------------------------------------------------------------------
# 10. 2x2 matrix with plotted items
# --------------------------------------------------------------------------
def matrix_2x2(d, x, y, w, h, xlabel, ylabel, quads, items, size=7.2):
    """quads: list of 4 (label, color) for TL, TR, BL, BR.
       items: list of (text, fx, fy, color) in 0..1 fractions."""
    px, py = x + 30, y + 26
    pw, ph = w - 36, h - 34
    tl, tr, bl, br = quads
    d.rect(px, py + ph / 2.0, pw / 2.0, ph / 2.0, fill=_soft(tl[1]))
    d.rect(px + pw / 2.0, py + ph / 2.0, pw / 2.0, ph / 2.0, fill=_soft(tr[1]))
    d.rect(px, py, pw / 2.0, ph / 2.0, fill=_soft(bl[1]))
    d.rect(px + pw / 2.0, py, pw / 2.0, ph / 2.0, fill=_soft(br[1]))
    d.rect(px, py, pw, ph, stroke=GREY_M, lw=0.8)
    d.line(px + pw / 2.0, py, px + pw / 2.0, py + ph, WHITE, 1.4)
    d.line(px, py + ph / 2.0, px + pw, py + ph / 2.0, WHITE, 1.4)
    for (lab, col), (qx, qy) in zip([tl, tr, bl, br],
                                    [(px + 6, py + ph - 11), (px + pw / 2.0 + 6, py + ph - 11),
                                     (px + 6, py + ph / 2.0 - 11), (px + pw / 2.0 + 6, py + ph / 2.0 - 11)]):
        d.text(qx, qy, lab.upper(), "bold", 6.6, col, char_space=0.8)
    for (text, fx, fy, col) in items:
        cx = px + pw * fx
        cy = py + ph * fy
        d.circle(cx, cy, 4.2, fill=col, stroke=WHITE, lw=1.0)
        lines = d.wrap(text, 96, "regular", size)
        flip = (cx + 10 + d.width(text, "regular", size) > px + pw - 4)
        for j, ln in enumerate(lines):
            ly = cy + (len(lines) - 1) * 4.2 - j * 8.2 - 2.4
            if flip:
                d.text_right(cx - 7, ly, ln, "regular", size, NAVY_D)
            else:
                d.text(cx + 7, ly, ln, "regular", size, NAVY_D)
    d.text_center(px + pw / 2.0, y + 2, xlabel, "semibold", 7.6, GREY)
    d.text_rot_center(x + 8, py + ph / 2.0, ylabel, 90, "semibold", 7.6, GREY)
    d.arrow(px, py - 8, px + pw, py - 8, GREY_M, 0.8, 4)
    d.arrow(px - 9, py, px - 9, py + ph, GREY_M, 0.8, 4)


# --------------------------------------------------------------------------
# 11. value chain
# --------------------------------------------------------------------------
def value_chain(d, x, y, w, h, primary, support, size=7.6):
    sup_h = 22.0
    chev_h = min(46.0, h - sup_h * len(support) - 16)
    chevrons(d, x, y + h - chev_h, w, chev_h, primary, numbered=False, size=7.8, sub_size=6.4)
    ty = y + h - chev_h - 10
    for i, (title, note) in enumerate(support):
        by = ty - sup_h - i * (sup_h + 5)
        d.round_rect(x, by, w, sup_h, 3.0, fill=GREY_XL, stroke=GREY_L, lw=0.7)
        d.rect(x, by, 3.4, sup_h, fill=ORANGE)
        d.text(x + 12, by + sup_h / 2.0 - 3.0, title, "semibold", 7.6, NAVY)
        wlab = d.width(title, "semibold", 7.6)
        d.text(x + 20 + wlab, by + sup_h / 2.0 - 2.8, note, "regular", 7.0, GREY)
    d.text(x, y + 2, "Margin is earned where the primary activities above are delivered at a cost "
                     "below the fee charged.", "italic", 6.9, GREY_M)


# --------------------------------------------------------------------------
# 12. funnel
# --------------------------------------------------------------------------
def funnel(d, x, y, w, h, stages, fmt=lambda v: "%g" % v, size=8.0):
    """stages: list of (label, value, color)."""
    n = len(stages)
    top_w = w * 0.60
    lh = (h - 6) / float(n)
    cx = x + top_w / 2.0 + 10
    maxv = float(stages[0][1])
    for i, (lab, val, col) in enumerate(stages):
        frac_t = max(0.22, val / maxv)
        frac_b = max(0.18, (stages[i + 1][1] / maxv) if i + 1 < n else frac_t * 0.62)
        by = y + h - (i + 1) * lh
        wt = top_w * frac_t
        wb = top_w * frac_b
        d.polygon([(cx - wt / 2.0, by + lh - 2), (cx + wt / 2.0, by + lh - 2),
                   (cx + wb / 2.0, by), (cx - wb / 2.0, by)], fill=col)
        d.text_center(cx, by + lh / 2.0 - 3.6, fmt(val), "bold", size + 1, WHITE)
        nx = x + top_w + 24
        d.line(cx + wt / 2.0 + 2, by + lh * 0.6, nx - 6, by + lh * 0.6, col, 0.7, dash=(2, 1.6))
        d.text(nx, by + lh * 0.6 - 2.8, lab, "semibold", size, NAVY)
        if i + 1 < n:
            conv = stages[i + 1][1] / float(val) * 100.0
            d.text(nx, by + lh * 0.6 - 12.4, "conversion to next stage: %.0f%%" % conv,
                   "regular", 6.8, GREY)


# --------------------------------------------------------------------------
# 13. flow of funds (simple sankey-like)
# --------------------------------------------------------------------------
def fund_flow(d, x, y, w, h, sources, uses, hub_label="Pool of funds", fmt=lambda v: "%g" % v,
              size=7.4):
    cap_h = 14.0
    y = y + cap_h
    h = h - cap_h
    hub_w = 78.0
    hub_x = x + (w - hub_w) / 2.0
    hub_h = h * 0.46
    hub_y = y + (h - hub_h) / 2.0
    col_w = (w - hub_w) / 2.0 - 30
    total_s = float(sum(s[1] for s in sources))
    total_u = float(sum(u[1] for u in uses))

    def draw_side(items, total, left):
        n = len(items)
        gap = 5.0
        avail = h - gap * (n - 1)
        min_h = 14.0
        # proportional heights, but never below min_h: the deficit is taken from
        # the blocks that are above the minimum
        raw = [avail * v / total for (_, v, _) in items]
        heights = [max(min_h, r) for r in raw]
        excess = sum(heights) - avail
        if excess > 0.01:
            flex = [i for i, hh in enumerate(heights) if hh > min_h + 0.5]
            flex_total = sum(heights[i] - min_h for i in flex) or 1.0
            for i in flex:
                heights[i] -= excess * (heights[i] - min_h) / flex_total
        cy = y + h
        out = []
        for idx, (lab, val, col) in enumerate(items):
            bh = heights[idx]
            cy -= bh
            bx = x if left else x + w - col_w
            d.round_rect(bx, cy, col_w, bh, 2.4, fill=_soft(col, 0.80), stroke=col, lw=0.7)
            amt = fmt(val)
            amt_w = d.width(amt, "semibold", size)
            txt = lab
            while d.width(txt, "regular", size) > col_w - amt_w - 20 and len(txt) > 8:
                txt = txt[:-1]
            if txt != lab:
                txt = txt[:-1] + "\u2026"
            d.text(bx + 7, cy + bh / 2.0 - 2.6, txt, "regular", size, NAVY_D)
            d.text_right(bx + col_w - 6, cy + bh / 2.0 - 2.6, amt, "semibold", size, col)
            out.append((cy + bh / 2.0, bh, col))
            cy -= gap
        return out

    ls = draw_side(sources, total_s, True)
    rs = draw_side(uses, total_u, False)
    for (cy, bh, col) in ls:
        _ribbon(d, x + col_w, cy, bh * 0.66, hub_x, hub_y + hub_h / 2.0, hub_h * 0.5, col)
    for (cy, bh, col) in rs:
        _ribbon(d, hub_x + hub_w, hub_y + hub_h / 2.0, hub_h * 0.5, x + w - col_w, cy, bh * 0.66, col)
    d.round_rect(hub_x, hub_y, hub_w, hub_h, 4.0, fill=NAVY, stroke=NAVY)
    for j, ln in enumerate(d.wrap(hub_label, hub_w - 12, "bold", 8.0)[:3]):
        d.text_center(hub_x + hub_w / 2.0, hub_y + hub_h / 2.0 + 6 - j * 9.6, ln, "bold", 8.0, WHITE)
    d.text_center(hub_x + hub_w / 2.0, hub_y + hub_h / 2.0 - 16, fmt(total_s), "bold", 9.0, ORANGE_L)
    d.text_center(x + col_w / 2.0, y - cap_h + 2, "SOURCES OF FUNDS", "bold", 7.2, GREY,
                  char_space=1.4)
    d.text_center(x + w - col_w / 2.0, y - cap_h + 2, "APPLICATION OF FUNDS", "bold", 7.2, GREY,
                  char_space=1.4)


def _ribbon(d, x1, y1, t1, x2, y2, t2, col):
    mid = (x1 + x2) / 2.0
    top = [(x1, y1 + t1 / 2.0)]
    bot = [(x1, y1 - t1 / 2.0)]
    steps = 14
    for i in range(steps + 1):
        t = i / float(steps)
        # cubic ease
        e = t * t * (3 - 2 * t)
        xx = x1 + (x2 - x1) * t
        yy = y1 + (y2 - y1) * e
        tt = t1 + (t2 - t1) * t
        top.append((xx, yy + tt / 2.0))
        bot.append((xx, yy - tt / 2.0))
    d.polygon(top + list(reversed(bot)), fill=_tint(col, 0.30))


def _tint(c, f):
    return (c[0] + (1 - c[0]) * (1 - f), c[1] + (1 - c[1]) * (1 - f), c[2] + (1 - c[2]) * (1 - f))


# --------------------------------------------------------------------------
# 14. hub and spokes
# --------------------------------------------------------------------------
def hub_spokes(d, x, y, w, h, hub, spokes, size=7.4, hub_r=40.0):
    cx, cy = x + w / 2.0, y + h / 2.0
    n = len(spokes)
    R = min(w * 0.36, h * 0.40)
    bw, bh = 118.0, 30.0
    for i, sp in enumerate(spokes):
        a = math.pi / 2 - 2 * math.pi * i / n
        px = cx + math.cos(a) * (R + bw * 0.34)
        py = cy + math.sin(a) * (R + bh * 0.62)
        px = max(x + bw / 2.0, min(x + w - bw / 2.0, px))
        py = max(y + bh / 2.0, min(y + h - bh / 2.0, py))
        col = SERIES[i % len(SERIES)]
        d.line(cx + math.cos(a) * hub_r, cy + math.sin(a) * hub_r,
               px - math.cos(a) * 6, py - math.sin(a) * 6, GREY_M, 0.8, dash=(2.4, 1.8))
        title = sp[0]
        sub = sp[1] if len(sp) > 1 else None
        box(d, px - bw / 2.0, py - bh / 2.0, bw, bh, title, sub, fill=WHITE, stroke=col,
            lw=0.9, tcolor=NAVY, size=7.4, sub_size=6.3, bar=col)
    d.circle(cx, cy, hub_r, fill=NAVY)
    d.circle(cx, cy, hub_r - 4, stroke=BLUE_M, lw=0.8)
    for j, ln in enumerate(d.wrap(hub, hub_r * 1.5, "bold", 8.2)[:3]):
        d.text_center(cx, cy + 6 - j * 9.6, ln, "bold", 8.2, WHITE)


# --------------------------------------------------------------------------
# 15. bridge (theory -> practice)
# --------------------------------------------------------------------------
def bridge(d, x, y, w, h, left_title, left_items, right_title, right_items, pillars,
           size=7.2, caption="progressive exposure over the seven weeks"):
    """Two knowledge columns joined by an arrow 'bridge' resting on stage pillars."""
    card_w = w * 0.30
    card_h = h * 0.66
    card_y = y + h - card_h
    mid_x0 = x + card_w + 16
    mid_x1 = x + w - card_w - 16
    cy = card_y + card_h * 0.30
    for (title, items, bx, col) in [(left_title, left_items, x, BLUE),
                                    (right_title, right_items, x + w - card_w, ORANGE)]:
        d.round_rect(bx, card_y, card_w, card_h, 3.0, fill=WHITE, stroke=col, lw=0.9)
        d.round_rect(bx, card_y + card_h - 17, card_w, 17, 3.0, fill=col)
        d.rect(bx, card_y + card_h - 17, card_w, 3.0, fill=col)
        d.text_center(bx + card_w / 2.0, card_y + card_h - 12, title, "bold", 7.8, WHITE,
                      char_space=0.8)
        ty = card_y + card_h - 29
        for it in items:
            for j, ln in enumerate(d.wrap(it, card_w - 20, "regular", size)):
                if j == 0:
                    d.circle(bx + 9, ty + 2.4, 1.5, fill=col)
                d.text(bx + 15, ty, ln, "regular", size, GREY_D)
                ty -= size + 2.4
            ty -= 2.2
    # the bridge deck
    d.round_rect(mid_x0, cy - 7, mid_x1 - mid_x0, 14, 7, fill=NAVY)
    d.text_center((mid_x0 + mid_x1) / 2.0, cy + 12, "THE INTERNSHIP BRIDGE", "bold", 7.6, NAVY,
                  char_space=1.5)
    d.arrow(mid_x0 + 10, cy, mid_x1 - 8, cy, ORANGE_L, 1.6, 7.5)
    # supporting stages, stacked under the deck
    n = len(pillars)
    mid_c = (mid_x0 + mid_x1) / 2.0
    top = cy - 16
    avail = top - (y + 14)
    step = avail / float(n)
    d.line(mid_c, cy - 8, mid_c, top - step * (n - 1) - 3, GREY_M, 0.7, dash=(2, 1.8))
    for i, p in enumerate(pillars):
        py = top - step * i
        cw = min(mid_x1 - mid_x0 - 4, d.width(p, "semibold", 6.9) + 20)
        d.round_rect(mid_c - cw / 2.0, py - 7, cw, 14, 7.0, fill=BLUE_XL, stroke=BLUE_M, lw=0.7)
        d.text_center(mid_c, py - 2.4, p, "semibold", 6.9, NAVY)
    d.text_center((mid_x0 + mid_x1) / 2.0, y + 3, caption, "italic", 6.8, GREY_M)


# --------------------------------------------------------------------------
# 16. layered stack (report structure)
# --------------------------------------------------------------------------
def stack(d, x, y, w, h, layers, size=8.0, numbered=True):
    n = len(layers)
    lh = (h - (n - 1) * 4.0) / float(n)
    for i, (title, note, col) in enumerate(layers):
        by = y + h - (i + 1) * lh - i * 4.0
        d.round_rect(x, by, w, lh, 3.0, fill=_soft(col), stroke=col, lw=0.8)
        d.round_rect(x, by, 4.0, lh, 2.0, fill=col)
        tx = x + 14
        if numbered:
            badge_num(d, x + 22, by + lh / 2.0, i + 1, r=8.4, fill=col, size=7.8)
            tx = x + 38
        d.text(tx, by + lh / 2.0 + (3.2 if note else -3.0), title, "semibold", size, NAVY)
        if note:
            d.text(tx, by + lh / 2.0 - 7.6, note, "regular", 6.9, GREY)


# --------------------------------------------------------------------------
# 17. mapping / linkage columns
# --------------------------------------------------------------------------
def mapping(d, x, y, w, h, left, right, links, left_title="", right_title="", size=7.3):
    col_w = w * 0.40
    lh = 24.0
    n_l, n_r = len(left), len(right)
    def col(items, bx, col_c, title):
        ys = []
        span = h - 18
        step = span / float(len(items))
        for i, it in enumerate(items):
            by = y + h - 18 - (i + 1) * step + (step - lh) / 2.0
            d.round_rect(bx, by, col_w, lh, 2.6, fill=WHITE, stroke=col_c, lw=0.8)
            d.rect(bx, by, 3.0, lh, fill=col_c)
            lines = d.wrap(it, col_w - 14, "regular", size)[:2]
            for j, ln in enumerate(lines):
                d.text(bx + 9, by + lh / 2.0 + (len(lines) - 1) * 4.0 - j * 8.2 - 2.6, ln,
                       "regular", size, GREY_D)
            ys.append(by + lh / 2.0)
        d.text(bx, y + h - 10, title.upper(), "bold", 7.0, col_c, char_space=1.2)
        return ys
    ly = col(left, x, BLUE, left_title)
    ry = col(right, x + w - col_w, GREEN, right_title)
    for (li, ri) in links:
        x1 = x + col_w
        x2 = x + w - col_w
        y1, y2 = ly[li], ry[ri]
        mid = (x1 + x2) / 2.0
        pts = [(x1, y1)]
        for k in range(1, 13):
            t = k / 12.0
            e = t * t * (3 - 2 * t)
            pts.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * e))
        d.polyline(pts, GREY_M, 0.7)
        d.polygon([(x2, y2), (x2 - 4.6, y2 + 2.4), (x2 - 4.6, y2 - 2.4)], fill=GREY_M)


# --------------------------------------------------------------------------
# 18. card grid
# --------------------------------------------------------------------------
def card_grid(d, x, y, w, h, cards, cols=3, size=7.9, gap=8.0, icon_num=True):
    """cards: list of (title, body, color)."""
    rows = (len(cards) + cols - 1) // cols
    cw = (w - gap * (cols - 1)) / float(cols)
    chh = (h - gap * (rows - 1)) / float(rows)
    for i, (title, body, col) in enumerate(cards):
        r, c = i // cols, i % cols
        bx = x + c * (cw + gap)
        by = y + h - (r + 1) * chh - r * gap
        d.round_rect(bx, by, cw, chh, 3.0, fill=WHITE, stroke=GREY_L, lw=0.7)
        d.round_rect(bx, by + chh - 3.2, cw, 3.2, 1.4, fill=col)
        ty = by + chh - 16
        tx = bx + 9
        if icon_num:
            badge_num(d, bx + 15, ty + 2.6, i + 1, r=8.0, fill=col, size=7.6)
            tx = bx + 28
        for ln in d.wrap(title, cw - (tx - bx) - 8, "semibold", size)[:2]:
            d.text(tx, ty, ln, "semibold", size, NAVY)
            ty -= size + 1.8
        ty -= 3.0
        for ln in d.wrap(body, cw - 18, "regular", 6.9):
            d.text(bx + 9, ty, ln, "regular", 6.9, GREY_D)
            ty -= 8.2


# --------------------------------------------------------------------------
# 19. timeline (vertical, week log)
# --------------------------------------------------------------------------
def timeline_v(d, x, y, w, h, events, size=7.8):
    """events: list of (period, title, detail, color)."""
    n = len(events)
    axis_x = x + 74
    step = h / float(n)
    d.line(axis_x, y + 6, axis_x, y + h - 6, GREY_L, 1.6)
    for i, (period, title, detail, col) in enumerate(events):
        cy = y + h - step * (i + 0.5)
        d.circle(axis_x, cy, 5.2, fill=WHITE, stroke=col, lw=1.6)
        d.circle(axis_x, cy, 2.2, fill=col)
        d.text_right(axis_x - 12, cy - 2.8, period, "bold", 7.4, col)
        d.round_rect(axis_x + 12, cy - step * 0.36, w - (axis_x - x) - 14, step * 0.72, 2.6,
                     fill=GREY_XL, stroke=GREY_L, lw=0.6)
        d.text(axis_x + 20, cy + 3.0, title, "semibold", size, NAVY)
        if detail:
            d.text(axis_x + 20, cy - 6.4, detail, "regular", 6.8, GREY)


# --------------------------------------------------------------------------
# 20. concentric control rings
# --------------------------------------------------------------------------
def rings(d, x, y, w, h, layers, size=7.4):
    """layers: list of (label, color) outermost first."""
    cx = x + w * 0.34
    cy = y + h / 2.0
    R = min(w * 0.30, h * 0.46)
    n = len(layers)
    for i, (lab, col) in enumerate(layers):
        r = R * (1 - i / float(n) * 0.78)
        d.circle(cx, cy, r, fill=col if i == n - 1 else None, stroke=col, lw=1.4)
        if i < n - 1:
            d.wedge(cx, cy, r, 90, -270, fill=_tint(col, 0.10), r_inner=R * (1 - (i + 1) / float(n) * 0.78))
        lx = cx + R + 26
        ly = cy + R - i * (2 * R / float(n)) - R / float(n)
        d.line(cx, cy + r - (R / float(n)) * 0.5, lx - 8, ly, col, 0.7, dash=(2, 1.6))
        d.round_rect(lx - 6, ly - 8, w - (lx - x) + 4, 16, 2.4, fill=_soft(col))
        d.text(lx, ly - 2.8, lab, "semibold", size, NAVY)
    d.text_center(cx, cy - 3, "ASSETS", "bold", 6.6, WHITE, char_space=0.8)
