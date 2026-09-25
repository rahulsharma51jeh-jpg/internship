"""
raster.py -- tiny software rasterizer used to visually proof-read the PDF
pages produced by pdfengine.py.  It replays the page operator list directly
(no PDF parsing needed), extracts real glyph outlines from the embedded
TrueType fonts, fills/strokes paths with a scanline rasteriser, and writes a
PNG (pure zlib, no image libraries).
"""

import struct
import zlib

SS = 3  # supersampling factor


# --------------------------------------------------------------------------
# glyph outlines
# --------------------------------------------------------------------------
class GlyphSource(object):
    def __init__(self, ttf):
        self.f = ttf
        self.loca = self._loca()
        off, length = ttf.tables["glyf"]
        self.glyf = ttf.data[off:off + length]
        self.cache = {}

    def _loca(self):
        f = self.f
        off, length = f.tables["loca"]
        raw = f.data[off:off + length]
        if f.index_to_loc_format == 0:
            n = len(raw) // 2
            return [v * 2 for v in struct.unpack(">%dH" % n, raw[:n * 2])]
        n = len(raw) // 4
        return list(struct.unpack(">%dI" % n, raw[:n * 4]))

    def contours(self, gid, depth=0):
        """Return list of contours, each a list of (x, y) in font units."""
        if gid in self.cache:
            return self.cache[gid]
        if gid + 1 >= len(self.loca):
            return []
        start, end = self.loca[gid], self.loca[gid + 1]
        if end <= start:
            return []
        d = self.glyf[start:end]
        n_contours = struct.unpack(">h", d[0:2])[0]
        result = []
        if n_contours >= 0:
            ends = struct.unpack(">%dH" % n_contours, d[10:10 + n_contours * 2])
            pos = 10 + n_contours * 2
            ins_len = struct.unpack(">H", d[pos:pos + 2])[0]
            pos += 2 + ins_len
            n_pts = (ends[-1] + 1) if n_contours else 0
            flags = []
            while len(flags) < n_pts:
                fl = d[pos]
                fl = fl if isinstance(fl, int) else ord(fl)
                pos += 1
                flags.append(fl)
                if fl & 8:
                    rep = d[pos]
                    rep = rep if isinstance(rep, int) else ord(rep)
                    pos += 1
                    flags.extend([fl] * rep)
            flags = flags[:n_pts]
            xs, v = [], 0
            for fl in flags:
                if fl & 2:
                    dx = d[pos]
                    dx = dx if isinstance(dx, int) else ord(dx)
                    pos += 1
                    v += dx if (fl & 16) else -dx
                elif not (fl & 16):
                    v += struct.unpack(">h", d[pos:pos + 2])[0]
                    pos += 2
                xs.append(v)
            ys, v = [], 0
            for fl in flags:
                if fl & 4:
                    dy = d[pos]
                    dy = dy if isinstance(dy, int) else ord(dy)
                    pos += 1
                    v += dy if (fl & 32) else -dy
                elif not (fl & 32):
                    v += struct.unpack(">h", d[pos:pos + 2])[0]
                    pos += 2
                ys.append(v)
            s = 0
            for e in ends:
                pts = [(xs[i], ys[i], bool(flags[i] & 1)) for i in range(s, min(e + 1, n_pts))]
                s = e + 1
                if pts:
                    result.append(self._flatten(pts))
        elif depth < 4:
            pos = 10
            while True:
                flags_c, glyph_index = struct.unpack(">HH", d[pos:pos + 4])
                pos += 4
                if flags_c & 1:
                    a1, a2 = struct.unpack(">hh", d[pos:pos + 4])
                    pos += 4
                else:
                    a1, a2 = struct.unpack(">bb", d[pos:pos + 2])
                    pos += 2
                sx = sy = 1.0
                s01 = s10 = 0.0
                if flags_c & 8:
                    sx = sy = struct.unpack(">h", d[pos:pos + 2])[0] / 16384.0
                    pos += 2
                elif flags_c & 0x40:
                    sx = struct.unpack(">h", d[pos:pos + 2])[0] / 16384.0
                    sy = struct.unpack(">h", d[pos + 2:pos + 4])[0] / 16384.0
                    pos += 4
                elif flags_c & 0x80:
                    sx, s01, s10, sy = [x / 16384.0 for x in struct.unpack(">hhhh", d[pos:pos + 8])]
                    pos += 8
                dx, dy = (a1, a2) if (flags_c & 2) else (0, 0)
                for c in self.contours(glyph_index, depth + 1):
                    result.append([(x * sx + y * s10 + dx, x * s01 + y * sy + dy) for x, y in c])
                if not (flags_c & 0x20):
                    break
        self.cache[gid] = result
        return result

    @staticmethod
    def _flatten(pts, steps=6):
        """Convert TrueType quadratic contour points to a polyline."""
        # build full on-curve sequence
        seq = []
        n = len(pts)
        for i in range(n):
            x, y, on = pts[i]
            if on:
                seq.append((x, y, True))
            else:
                px, py, pon = pts[i - 1]
                if not pon:
                    seq.append(((x + px) / 2.0, (y + py) / 2.0, True))
                seq.append((x, y, False))
        if not seq:
            return []
        if not seq[0][2]:
            # rotate so we start on-curve
            for i, p in enumerate(seq):
                if p[2]:
                    seq = seq[i:] + seq[:i]
                    break
            else:
                return []
        out = [(seq[0][0], seq[0][1])]
        i = 1
        m = len(seq)
        while i <= m:
            cur = seq[i % m]
            if cur[2]:
                out.append((cur[0], cur[1]))
                i += 1
            else:
                nxt = seq[(i + 1) % m]
                end = (nxt[0], nxt[1]) if nxt[2] else ((cur[0] + nxt[0]) / 2.0, (cur[1] + nxt[1]) / 2.0)
                x0, y0 = out[-1]
                for s in range(1, steps + 1):
                    t = s / float(steps)
                    mt = 1 - t
                    out.append((mt * mt * x0 + 2 * mt * t * cur[0] + t * t * end[0],
                                mt * mt * y0 + 2 * mt * t * cur[1] + t * t * end[1]))
                i += 1 if nxt[2] else 1
        return out


# --------------------------------------------------------------------------
# canvas
# --------------------------------------------------------------------------
class Canvas(object):
    def __init__(self, w_px, h_px):
        self.w = w_px
        self.h = h_px
        self.buf = bytearray(b"\xff" * (w_px * h_px * 3))

    def fill_path(self, contours, color, clip=None):
        """contours: list of point lists in device px (y down). Nonzero winding."""
        if not contours:
            return
        ss = SS
        edges = []
        miny, maxy = 1e18, -1e18
        for c in contours:
            if len(c) < 2:
                continue
            for i in range(len(c)):
                x0, y0 = c[i]
                x1, y1 = c[(i + 1) % len(c)]
                if y0 == y1:
                    continue
                edges.append((x0 * ss, y0 * ss, x1 * ss, y1 * ss))
                miny = min(miny, y0, y1)
                maxy = max(maxy, y0, y1)
        if not edges:
            return
        y_start = max(0, int(miny))
        y_end = min(self.h - 1, int(maxy) + 1)
        if clip:
            cx0, cy0, cx1, cy1 = clip
            y_start = max(y_start, int(cy0))
            y_end = min(y_end, int(cy1) + 1)
        r, g, b = [int(round(255 * v)) for v in color]
        cov_row = [0.0] * self.w
        for py in range(y_start, y_end + 1):
            for i in range(self.w):
                cov_row[i] = 0.0
            hit = False
            for sub in range(ss):
                sy = py * ss + sub + 0.5
                xs = []
                for (x0, y0, x1, y1) in edges:
                    if (y0 <= sy < y1) or (y1 <= sy < y0):
                        t = (sy - y0) / (y1 - y0)
                        xs.append((x0 + t * (x1 - x0), 1 if y1 > y0 else -1))
                if not xs:
                    continue
                xs.sort()
                wind = 0
                spans = []
                for i in range(len(xs) - 1):
                    wind += xs[i][1]
                    if wind != 0:
                        spans.append((xs[i][0], xs[i + 1][0]))
                for (sx0, sx1) in spans:
                    if clip:
                        sx0 = max(sx0, clip[0] * ss)
                        sx1 = min(sx1, clip[2] * ss)
                    if sx1 <= sx0:
                        continue
                    a = sx0 / ss
                    bnd = sx1 / ss
                    ia, ib = int(a), int(bnd)
                    if ia == ib:
                        if 0 <= ia < self.w:
                            cov_row[ia] += (bnd - a) / ss
                            hit = True
                        continue
                    if 0 <= ia < self.w:
                        cov_row[ia] += (ia + 1 - a) / ss
                    for px in range(max(0, ia + 1), min(self.w, ib)):
                        cov_row[px] += 1.0 / ss
                    if 0 <= ib < self.w:
                        cov_row[ib] += (bnd - ib) / ss
                    hit = True
            if not hit:
                continue
            base = py * self.w * 3
            for px in range(self.w):
                cv = cov_row[px]
                if cv <= 0.002:
                    continue
                if cv > 1:
                    cv = 1.0
                o = base + px * 3
                self.buf[o] = int(self.buf[o] * (1 - cv) + r * cv)
                self.buf[o + 1] = int(self.buf[o + 1] * (1 - cv) + g * cv)
                self.buf[o + 2] = int(self.buf[o + 2] * (1 - cv) + b * cv)

    def png(self, path):
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)
            raw += self.buf[y * stride:(y + 1) * stride]
        comp = zlib.compress(bytes(raw), 6)

        def chunk(tag, data):
            c = struct.pack(">I", len(data)) + tag + data
            return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0))
        png += chunk(b"IDAT", comp)
        png += chunk(b"IEND", b"")
        with open(path, "wb") as fh:
            fh.write(png)


# --------------------------------------------------------------------------
# operator replay
# --------------------------------------------------------------------------
def render(doc, page_index, path, dpi=105):
    page = doc.pages[page_index]
    scale = dpi / 72.0
    W = int(page.width * scale)
    H = int(page.height * scale)
    cv = Canvas(W, H)
    glyphsrc = {a: GlyphSource(f) for a, f in doc.fonts.items()}
    alias_to_font = {v: doc.fonts[k] for k, v in doc.font_alias.items()}
    alias_to_src = {v: glyphsrc[k] for k, v in doc.font_alias.items()}

    def dev(x, y):
        return (x * scale, (page.height - y) * scale)

    tokens = " ".join(page.ops).replace("<", " <").replace(">", "> ").split()
    fill = (0, 0, 0)
    stroke = (0, 0, 0)
    lw = 1.0
    path_pts = []      # current subpath
    subpaths = []
    stack = []
    clip = None
    pending_clip = False
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    # text state
    in_text = False
    tf = None
    tsize = 10.0
    tx = ty = 0.0
    tm = None
    tc = 0.0
    nums = []

    def flush_sub():
        if len(path_pts) > 1:
            subpaths.append(list(path_pts))

    def do_fill():
        flush_sub()
        cv.fill_path(subpaths, fill, clip)

    def thick(p0, p1, w):
        import math
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        ln = math.hypot(dx, dy)
        if ln < 1e-9:
            return None
        nx, ny = -dy / ln * w / 2.0, dx / ln * w / 2.0
        return [(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny),
                (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny)]

    def do_stroke():
        flush_sub()
        w = max(lw * scale, 0.9)
        polys = []
        for sp in subpaths:
            for i in range(len(sp) - 1):
                q = thick(sp[i], sp[i + 1], w)
                if q:
                    polys.append(q)
            if w > 1.6:
                for (px, py) in sp:
                    r = w / 2.0
                    polys.append([(px - r, py - r), (px + r, py - r), (px + r, py + r), (px - r, py + r)])
        for q in polys:
            cv.fill_path([q], stroke, clip)

    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        if t.startswith("<") and t.endswith(">"):
            nums.append(("hex", t[1:-1]))
            i += 1
            continue
        try:
            nums.append(("num", float(t)))
            i += 1
            continue
        except ValueError:
            pass
        if t in ("[", "]"):
            i += 1
            continue
        op = t
        vals = [v for k, v in nums if k == "num"]
        hexes = [v for k, v in nums if k == "hex"]
        if op == "rg":
            fill = tuple(vals[-3:])
        elif op == "RG":
            stroke = tuple(vals[-3:])
        elif op == "w":
            lw = vals[-1] if vals else 1.0
        elif op == "m":
            flush_sub()
            cur = dev(vals[-2], vals[-1])
            start = cur
            path_pts = [cur]
        elif op == "l":
            cur = dev(vals[-2], vals[-1])
            path_pts.append(cur)
        elif op == "c":
            p0 = cur
            c1 = dev(vals[-6], vals[-5])
            c2 = dev(vals[-4], vals[-3])
            p3 = dev(vals[-2], vals[-1])
            for s in range(1, 13):
                tt = s / 12.0
                mt = 1 - tt
                path_pts.append((mt ** 3 * p0[0] + 3 * mt * mt * tt * c1[0] + 3 * mt * tt * tt * c2[0] + tt ** 3 * p3[0],
                                 mt ** 3 * p0[1] + 3 * mt * mt * tt * c1[1] + 3 * mt * tt * tt * c2[1] + tt ** 3 * p3[1]))
            cur = p3
        elif op == "re":
            flush_sub()
            x, y, w_, h_ = vals[-4:]
            p1 = dev(x, y)
            p2 = dev(x + w_, y + h_)
            subpaths.append([(p1[0], p1[1]), (p2[0], p1[1]), (p2[0], p2[1]), (p1[0], p2[1])])
            path_pts = []
            cur = p1
        elif op == "h":
            if path_pts:
                path_pts.append(start)
        elif op in ("f", "f*"):
            do_fill()
            subpaths, path_pts = [], []
        elif op == "S":
            do_stroke()
            subpaths, path_pts = [], []
        elif op in ("B", "B*"):
            do_fill()
            do_stroke()
            subpaths, path_pts = [], []
        elif op == "W":
            pending_clip = True
        elif op == "n":
            if pending_clip:
                flush_sub()
                xs = [p[0] for sp in subpaths for p in sp]
                ys = [p[1] for sp in subpaths for p in sp]
                if xs:
                    nc = (min(xs), min(ys), max(xs), max(ys))
                    clip = nc if clip is None else (max(clip[0], nc[0]), max(clip[1], nc[1]),
                                                   min(clip[2], nc[2]), min(clip[3], nc[3]))
                pending_clip = False
            subpaths, path_pts = [], []
        elif op == "q":
            stack.append((fill, stroke, lw, clip))
        elif op == "Q":
            if stack:
                fill, stroke, lw, clip = stack.pop()
        elif op == "BT":
            in_text = True
            tm = None
        elif op == "ET":
            in_text = False
        elif op == "Tf":
            tsize = vals[-1]
        elif op == "Tc":
            tc = vals[-1]
        elif op == "Td":
            tx, ty = vals[-2], vals[-1]
            tm = None
        elif op == "Tm":
            tm = vals[-6:]
            tx, ty = tm[4], tm[5]
        elif op in ("Tj", "TJ"):
            # find font alias from the most recent /Fx token
            alias = None
            for j in range(i, -1, -1):
                if tokens[j].startswith("/F"):
                    alias = tokens[j][1:]
                    break
            fnt = alias_to_font.get(alias)
            src = alias_to_src.get(alias)
            if fnt and src:
                pen = 0.0
                seq = []
                for kind, val in nums:
                    seq.append((kind, val))
                for kind, val in seq:
                    if kind == "num" and op == "TJ":
                        pen -= val / 1000.0 * tsize
                    elif kind == "hex":
                        gids = [int(val[k:k + 4], 16) for k in range(0, len(val), 4)]
                        for gid in gids:
                            outl = src.contours(gid)
                            upm = float(fnt.units_per_em)
                            polys = []
                            for c in outl:
                                pc = []
                                for (gx, gy) in c:
                                    ux = gx * tsize / upm
                                    uy = gy * tsize / upm
                                    if tm:
                                        px = tm[0] * ux + tm[2] * uy + tx + pen * tm[0]
                                        py = tm[1] * ux + tm[3] * uy + ty + pen * tm[1]
                                    else:
                                        px, py = tx + ux + pen, ty + uy
                                    pc.append(dev(px, py))
                                if pc:
                                    polys.append(pc)
                            if polys:
                                cv.fill_path(polys, fill, clip)
                            pen += fnt.advances[gid] * tsize / upm + tc
        elif op == "d":
            pass
        nums = []
        i += 1
    cv.png(path)
    return W, H
