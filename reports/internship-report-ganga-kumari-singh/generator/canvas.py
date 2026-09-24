"""
Minimal anti-aliased raster canvas with a pure-Python PNG encoder.

No third-party imaging library is available in this sandbox, so drawing is
implemented directly: shapes are described as polygons (curves are flattened),
rasterised with a scanline algorithm at 4x supersampling for smooth edges, and
composited with alpha onto an RGB byte buffer.
"""

import math
import struct
import zlib

SS = 4  # supersampling factor per axis for coverage estimation


class Canvas:
    def __init__(self, width, height, bg=(255, 255, 255)):
        self.w = int(width)
        self.h = int(height)
        self.buf = bytearray(self.w * self.h * 3)
        self.fill_all(bg)

    # ------------------------------------------------------------ pixels ----
    def fill_all(self, rgb):
        row = bytes(rgb) * self.w
        for y in range(self.h):
            self.buf[y * self.w * 3:(y + 1) * self.w * 3] = row

    def blend(self, x, y, rgb, alpha):
        if alpha <= 0.0 or x < 0 or y < 0 or x >= self.w or y >= self.h:
            return
        if alpha > 1.0:
            alpha = 1.0
        i = (y * self.w + x) * 3
        b = self.buf
        inv = 1.0 - alpha
        b[i] = int(b[i] * inv + rgb[0] * alpha + 0.5)
        b[i + 1] = int(b[i + 1] * inv + rgb[1] * alpha + 0.5)
        b[i + 2] = int(b[i + 2] * inv + rgb[2] * alpha + 0.5)

    # ---------------------------------------------------------- polygons ----
    def fill_polygon(self, pts, rgb, alpha=1.0, even_odd=False):
        """Fill one polygon (list of (x, y)) with anti-aliased edges."""
        self.fill_polygons([pts], rgb, alpha, even_odd)

    def fill_polygons(self, polys, rgb, alpha=1.0, even_odd=False):
        """Fill a set of sub-polygons as a single path (supports holes)."""
        edges = []
        min_y, max_y = 1e18, -1e18
        min_x, max_x = 1e18, -1e18
        for pts in polys:
            n = len(pts)
            if n < 3:
                continue
            for k in range(n):
                x0, y0 = pts[k]
                x1, y1 = pts[(k + 1) % n]
                if y0 == y1:
                    continue
                edges.append((x0, y0, x1, y1))
                if y0 < min_y: min_y = y0
                if y1 < min_y: min_y = y1
                if y0 > max_y: max_y = y0
                if y1 > max_y: max_y = y1
                if x0 < min_x: min_x = x0
                if x1 < min_x: min_x = x1
                if x0 > max_x: max_x = x0
                if x1 > max_x: max_x = x1
        if not edges:
            return

        y_start = max(0, int(math.floor(min_y)))
        y_end = min(self.h - 1, int(math.ceil(max_y)))
        x_start = max(0, int(math.floor(min_x)))
        x_end = min(self.w - 1, int(math.ceil(max_x)))
        if y_end < y_start or x_end < x_start:
            return

        row_w = x_end - x_start + 1
        step = 1.0 / SS
        half = step * 0.5

        for py in range(y_start, y_end + 1):
            cov = [0.0] * row_w
            hit = False
            for s in range(SS):
                sy = py + s * step + half
                xs = []
                for (x0, y0, x1, y1) in edges:
                    if (y0 <= sy < y1) or (y1 <= sy < y0):
                        t = (sy - y0) / (y1 - y0)
                        xs.append((x0 + t * (x1 - x0), 1 if y1 > y0 else -1))
                if not xs:
                    continue
                xs.sort()
                spans = []
                if even_odd:
                    for k in range(0, len(xs) - 1, 2):
                        spans.append((xs[k][0], xs[k + 1][0]))
                else:
                    wind = 0
                    open_x = 0.0
                    for (xv, d) in xs:
                        prev = wind
                        wind += d
                        if prev == 0 and wind != 0:
                            open_x = xv
                        elif prev != 0 and wind == 0:
                            spans.append((open_x, xv))
                for (sx0, sx1) in spans:
                    if sx1 <= sx0:
                        continue
                    a = max(sx0, x_start)
                    b = min(sx1, x_end + 1.0)
                    if b <= a:
                        continue
                    hit = True
                    ia = int(math.floor(a))
                    ib = int(math.ceil(b)) - 1
                    for px in range(ia, ib + 1):
                        left = px if px > a else a
                        right = (px + 1.0) if (px + 1.0) < b else b
                        frac = right - left
                        if frac > 0:
                            idx = px - x_start
                            if 0 <= idx < row_w:
                                cov[idx] += frac * step
            if not hit:
                continue
            for idx in range(row_w):
                c = cov[idx]
                if c > 0.002:
                    self.blend(x_start + idx, py, rgb, c * alpha)

    # ------------------------------------------------------------ strokes ----
    def stroke_polyline(self, pts, rgb, width=1.0, alpha=1.0, closed=False,
                        cap_round=True):
        """Stroke a polyline by emitting a quad per segment plus round joins."""
        if len(pts) < 2:
            return
        seq = list(pts)
        if closed:
            seq.append(seq[0])
        hw = width / 2.0
        quads = []
        for k in range(len(seq) - 1):
            x0, y0 = seq[k]
            x1, y1 = seq[k + 1]
            dx, dy = x1 - x0, y1 - y0
            ln = math.hypot(dx, dy)
            if ln < 1e-9:
                continue
            nx, ny = -dy / ln * hw, dx / ln * hw
            quads.append([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny),
                          (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)])
        if not quads:
            return
        self.fill_polygons(quads, rgb, alpha)
        if cap_round and width > 1.6:
            joins = seq[1:-1] if not closed else seq
            for (jx, jy) in joins:
                self.fill_polygon(_circle_pts(jx, jy, hw, 12), rgb, alpha)

    def line(self, x0, y0, x1, y1, rgb, width=1.0, alpha=1.0):
        self.stroke_polyline([(x0, y0), (x1, y1)], rgb, width, alpha,
                             cap_round=False)

    def rect(self, x, y, w, h, rgb, alpha=1.0):
        self.fill_polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                          rgb, alpha)

    def rect_outline(self, x, y, w, h, rgb, width=1.0, alpha=1.0):
        self.stroke_polyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                             rgb, width, alpha, closed=True, cap_round=False)

    def round_rect(self, x, y, w, h, r, rgb, alpha=1.0):
        self.fill_polygon(_round_rect_pts(x, y, w, h, r), rgb, alpha)

    def circle(self, cx, cy, r, rgb, alpha=1.0):
        self.fill_polygon(_circle_pts(cx, cy, r, max(18, int(r * 2.2))), rgb,
                          alpha)

    def ring(self, cx, cy, r_outer, r_inner, rgb, alpha=1.0):
        n = max(36, int(r_outer * 2.4))
        outer = _circle_pts(cx, cy, r_outer, n)
        inner = _circle_pts(cx, cy, r_inner, n)[::-1]
        self.fill_polygons([outer, inner], rgb, alpha)

    def wedge(self, cx, cy, r_outer, r_inner, a0, a1, rgb, alpha=1.0):
        """Annular wedge; angles in degrees, measured clockwise from 12 o'clock."""
        steps = max(3, int(abs(a1 - a0) / 2.2) + 3)
        pts = []
        for k in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * k / steps - 90.0)
            pts.append((cx + r_outer * math.cos(a), cy + r_outer * math.sin(a)))
        for k in range(steps, -1, -1):
            a = math.radians(a0 + (a1 - a0) * k / steps - 90.0)
            pts.append((cx + r_inner * math.cos(a), cy + r_inner * math.sin(a)))
        self.fill_polygon(pts, rgb, alpha)

    # ----------------------------------------------------------- gradient ----
    def linear_gradient(self, x, y, w, h, c0, c1, horizontal=True):
        from brand import mix
        x, y, w, h = int(x), int(y), int(w), int(h)
        if horizontal:
            for px in range(x, x + w):
                t = (px - x) / max(1.0, w - 1.0)
                col = mix(c0, c1, t)
                self.rect(px, y, 1, h, col)
        else:
            for py in range(y, y + h):
                t = (py - y) / max(1.0, h - 1.0)
                col = mix(c0, c1, t)
                self.rect(x, py, w, 1, col)

    # -------------------------------------------------------------- output ----
    @staticmethod
    def _chunk(tag, data):
        body = tag + data
        return (struct.pack(">I", len(data)) + body +
                struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))

    def to_png(self, indexed=False, max_colours=256):
        """
        Encode as PNG. `indexed=True` writes an 8-bit palette image, which is
        far smaller for flat artwork such as the charts.
        """
        chunk = self._chunk
        if indexed:
            import quant
            palette, idx, _exact = quant.index_image(bytes(self.buf), self.w,
                                                     self.h, max_colours)
            raw = bytearray()
            for y in range(self.h):
                raw.append(0)                     # filter type 0 (None)
                raw += idx[y * self.w:(y + 1) * self.w]
            plte = b"".join(bytes(c) for c in palette)
            ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 3, 0, 0, 0)
            return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
                    chunk(b"PLTE", plte) +
                    chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
                    chunk(b"IEND", b""))

        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)
            raw += self.buf[y * stride:(y + 1) * stride]
        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
                chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
                chunk(b"IEND", b""))

    def save(self, path, indexed=False):
        with open(path, "wb") as fh:
            fh.write(self.to_png(indexed=indexed))
        return path

    def rgb_bytes(self):
        return bytes(self.buf)


# ----------------------------------------------------------- geometry util ----
def _circle_pts(cx, cy, r, n=32):
    return [(cx + r * math.cos(2 * math.pi * k / n),
             cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def _round_rect_pts(x, y, w, h, r):
    r = min(r, w / 2.0, h / 2.0)
    pts = []
    corners = [(x + w - r, y + r, -90, 0), (x + w - r, y + h - r, 0, 90),
               (x + r, y + h - r, 90, 180), (x + r, y + r, 180, 270)]
    for (ccx, ccy, a0, a1) in corners:
        steps = 8
        for k in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * k / steps)
            pts.append((ccx + r * math.cos(a), ccy + r * math.sin(a)))
    return pts


def bezier_pts(p0, p1, p2, p3, steps=40):
    """Flatten a cubic Bezier into a point list."""
    out = []
    for k in range(steps + 1):
        t = k / steps
        mt = 1 - t
        a = mt * mt * mt
        b = 3 * mt * mt * t
        c = 3 * mt * t * t
        d = t * t * t
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def offset_path(pts, width_fn):
    """
    Build a closed ribbon polygon around a centreline where the half-width at
    each point is given by width_fn(index_fraction).
    """
    n = len(pts)
    left, right = [], []
    for i, (px, py) in enumerate(pts):
        if i == 0:
            dx, dy = pts[1][0] - px, pts[1][1] - py
        elif i == n - 1:
            dx, dy = px - pts[-2][0], py - pts[-2][1]
        else:
            dx = pts[i + 1][0] - pts[i - 1][0]
            dy = pts[i + 1][1] - pts[i - 1][1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        hw = width_fn(i / max(1, n - 1))
        left.append((px + nx * hw, py + ny * hw))
        right.append((px - nx * hw, py - ny * hw))
    return left + right[::-1]
