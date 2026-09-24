"""
Renders the Infinity Interns brand mark.

The mark is a lemniscate ("figure of eight") ribbon whose half-width tapers
towards the central crossing and whose colour sweeps from ribbon blue through
accent orange, mirroring the logo supplied by the student. Because the raster
canvas has no alpha channel, the mark is baked onto a caller-supplied flat
background so it can be dropped onto white or navy areas without a visible box.
"""

import math

import brand
from canvas import Canvas

# Colour stops sampled along the path parameter u in [0, 1].
# u 0.00-0.50 traces the right lobe, u 0.50-1.00 the left lobe.
_STOPS = [
    (0.00, brand.BLUE),
    (0.10, brand.ORANGE_LT),
    (0.22, brand.ORANGE),
    (0.34, brand.mix(brand.ORANGE, brand.NAVY, 0.30)),
    (0.46, brand.NAVY_MID),
    (0.50, brand.NAVY),
    (0.58, brand.NAVY_MID),
    (0.70, brand.BLUE),
    (0.80, brand.BLUE_LIGHT),
    (0.90, brand.BLUE),
    (1.00, brand.NAVY_MID),
]

_WHITE = (255, 255, 255)

_STOPS_MONO = [
    (0.00, _WHITE),
    (0.14, brand.mix(brand.ORANGE_LT, _WHITE, 0.35)),
    (0.26, brand.ORANGE_LT),
    (0.40, brand.mix(brand.ORANGE_LT, _WHITE, 0.45)),
    (0.50, _WHITE),
    (0.64, brand.mix(brand.BLUE_LIGHT, _WHITE, 0.40)),
    (0.76, brand.BLUE_LIGHT),
    (0.90, brand.mix(brand.BLUE_LIGHT, _WHITE, 0.45)),
    (1.00, _WHITE),
]

# Canvas aspect ratio of the standalone mark (height / width).
MARK_RATIO = 0.42


def _colour_at(u, stops):
    u = min(1.0, max(0.0, u))
    for i in range(len(stops) - 1):
        u0, c0 = stops[i]
        u1, c1 = stops[i + 1]
        if u0 <= u <= u1:
            t = (u - u0) / (u1 - u0) if u1 > u0 else 0.0
            return brand.mix(c0, c1, t)
    return stops[-1][1]


def _point(t, a, b):
    """Lemniscate centreline: crosses itself once at the origin."""
    return (a * math.cos(t), -(b * 0.5) * math.sin(2 * t))


def _half_width(t, w_max):
    """Ribbon tapers to ~34% at the crossing and swells at the outer loops."""
    return w_max * (0.34 + 0.66 * abs(math.cos(t)))


def _ribbon_quads(cx, cy, a, b, w_max, samples):
    """Build (quad, u) pairs walking the centreline from u=0 to u=1."""
    t0 = -math.pi / 2.0
    pts = []
    for k in range(samples + 1):
        u = k / samples
        t = t0 + u * 2.0 * math.pi
        px, py = _point(t, a, b)
        pts.append((cx + px, cy + py, t, u))

    quads = []
    for k in range(samples):
        x0, y0, ta, ua = pts[k]
        x1, y1, tb, ub = pts[k + 1]
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy)
        if ln < 1e-9:
            continue
        # Extend each quad slightly along the path so neighbouring segments
        # overlap; this hides anti-aliasing seams between fills.
        ex, ey = dx / ln * (ln * 0.55), dy / ln * (ln * 0.55)
        nx, ny = -dy / ln, dx / ln
        ha = _half_width(ta, w_max)
        hb = _half_width(tb, w_max)
        quad = [(x0 - ex + nx * ha, y0 - ey + ny * ha),
                (x1 + ex + nx * hb, y1 + ey + ny * hb),
                (x1 + ex - nx * hb, y1 + ey - ny * hb),
                (x0 - ex - nx * ha, y0 - ey - ny * ha)]
        quads.append((quad, (ua + ub) * 0.5))
    return quads, pts


def _arrowhead(cv, pts, u_at, w_max, colour, scale=2.2, reverse=False):
    """Drop a triangular arrowhead on the centreline pointing along the tangent."""
    n = len(pts) - 1
    i = max(1, min(n - 1, int(round(u_at * n))))
    x0, y0, t, _ = pts[i]
    xp, yp = pts[i - 1][0], pts[i - 1][1]
    xn, yn = pts[i + 1][0], pts[i + 1][1]
    dx, dy = xn - xp, yn - yp
    if reverse:
        dx, dy = -dx, -dy
    ln = math.hypot(dx, dy) or 1.0
    dx, dy = dx / ln, dy / ln
    nx, ny = -dy, dx
    h = _half_width(t, w_max) * scale
    tip = (x0 + dx * h * 1.25, y0 + dy * h * 1.25)
    left = (x0 - dx * h * 0.35 + nx * h, y0 - dy * h * 0.35 + ny * h)
    right = (x0 - dx * h * 0.35 - nx * h, y0 - dy * h * 0.35 - ny * h)
    cv.fill_polygon([tip, left, right], colour)


def render_mark(width=900, bg=brand.PAPER, mono=False, shadow=True):
    """
    Render the infinity mark. Returns a Canvas sized width x (width * 0.46).

    mono=True produces the light-on-dark treatment for navy panels.
    """
    w = int(width)
    h = int(round(width * MARK_RATIO))
    cv = Canvas(w, h, bg)

    # Extents are chosen so the ribbon (centreline +/- w_max) plus the drop
    # shadow always sit inside the canvas: the widest point of a lobe is at
    # cx +/- (a + w_max) and the top of a lobe at cy +/- (b / 2 + w_max).
    cx, cy = w / 2.0, h / 2.0
    w_max = h * 0.135      # maximum ribbon half-width
    a = w * 0.390          # horizontal reach of each lobe
    b = h * 0.660          # vertical span of the lobes
    samples = 320

    stops = _STOPS_MONO if mono else _STOPS
    quads, pts = _ribbon_quads(cx, cy, a, b, w_max, samples)

    if shadow and not mono:
        shade = brand.mix(bg, brand.NAVY, 0.16)
        for quad, _u in quads:
            cv.fill_polygon([(px + w * 0.010, py + h * 0.022)
                             for (px, py) in quad], shade)

    # Base pass in a neutral mid tone fills any sub-pixel gaps, then the
    # gradient pass paints the ribbon in path order so the lobes weave.
    base = brand.mix(bg, brand.NAVY_MID, 0.9) if not mono else brand.BLUE_LIGHT
    for quad, _u in quads:
        cv.fill_polygon(quad, base)
    for quad, u in quads:
        cv.fill_polygon(quad, _colour_at(u, stops))

    # Two chevrons on the diagonal through the crossing: one sweeping up to the
    # right, one down to the left, echoing the arrows in the supplied logo.
    arrow = brand.BLUE_LIGHT if not mono else (255, 255, 255)
    _arrowhead(cv, pts, 0.455, w_max, arrow, reverse=True)
    _arrowhead(cv, pts, 0.545, w_max, arrow)
    return cv


def render_seal(size=520, bg=brand.PAPER):
    """
    A circular emblem: the mark inside a double ring with the company initials.
    Used on the cover and the certificate page.
    """
    import strokefont as sf

    s = int(size)
    cv = Canvas(s, s, bg)
    c = s / 2.0
    cv.circle(c, c, c * 0.97, brand.NAVY)
    cv.circle(c, c, c * 0.93, bg)
    cv.ring(c, c, c * 0.89, c * 0.875, brand.ORANGE)

    mark = render_mark(int(s * 0.74), bg=bg)
    _paste(cv, mark, int(c - mark.w / 2.0), int(c - mark.h / 2.0 - s * 0.070))

    size, trk = sf.fit_size("INFINITY INTERNS", s * 0.64, tracking_ratio=0.10)
    sf.draw_text(cv, "INFINITY INTERNS", c, c + s * 0.255, size, brand.NAVY,
                 align="center", tracking=trk, weight=size * 0.165)
    size2, trk2 = sf.fit_size("PATNA \u2022 BIHAR", s * 0.34, tracking_ratio=0.12)
    sf.draw_text(cv, "PATNA \u2022 BIHAR", c, c + s * 0.345, size2, brand.ORANGE,
                 align="center", tracking=trk2, weight=size2 * 0.15)
    return cv


def _paste(dst, src, x, y):
    """Copy one canvas onto another (opaque)."""
    for row in range(src.h):
        ty = y + row
        if ty < 0 or ty >= dst.h:
            continue
        sx0 = max(0, -x)
        sx1 = min(src.w, dst.w - x)
        if sx1 <= sx0:
            continue
        s_off = (row * src.w + sx0) * 3
        d_off = (ty * dst.w + (x + sx0)) * 3
        n = (sx1 - sx0) * 3
        dst.buf[d_off:d_off + n] = src.buf[s_off:s_off + n]


def render_lockup(width=1200, bg=brand.PAPER, mono=False):
    """
    Full horizontal lockup: mark above the wordmark and tagline, matching the
    proportions of the supplied logo. Used where a single image is convenient.
    """
    import strokefont as sf

    w = int(width)
    h = int(round(width * 0.52))
    cv = Canvas(w, h, bg)

    mark = render_mark(int(w * 0.64), bg=bg, mono=mono)
    _paste(cv, mark, int((w - mark.w) / 2.0), int(h * 0.05))

    ink = brand.NAVY if not mono else (255, 255, 255)
    sub = brand.INK_SOFT if not mono else brand.BLUE_PALE

    word = "INFINITY INTERNS"
    size, trk = sf.fit_size(word, w * 0.88, tracking_ratio=0.085)
    sf.draw_text(cv, word, w / 2.0, h * 0.79, size, ink, align="center",
                 tracking=trk, weight=size * 0.165)

    tag = brand.COMPANY_TAG
    t_size, _ = sf.fit_size(tag, w * 0.86, max_size=w * 0.030)
    sf.draw_text(cv, tag, w / 2.0, h * 0.955, t_size, sub, align="center",
                 weight=t_size * 0.115)
    return cv


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "/projects/sandbox/build"
    render_mark(900).save(out + "/logo_mark.png")
    render_mark(900, bg=brand.NAVY_DEEP, mono=True).save(out + "/logo_mark_mono.png")
    render_lockup(1100).save(out + "/logo_lockup.png")
    render_seal(520).save(out + "/logo_seal.png")
    print("logo assets written to", out)
