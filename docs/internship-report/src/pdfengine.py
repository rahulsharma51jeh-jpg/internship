"""
pdfengine.py -- a small, dependency-free PDF generation engine.

Written for the Infinity Interns internship report because the sandbox has no
network access (so no reportlab / matplotlib / weasyprint).  It supports:

  * TrueType font embedding (Identity-H CID fonts) with real metrics read
    from the font's cmap/hmtx tables, so text measurement is exact and
    Unicode (including the rupee sign) works.
  * Vector drawing primitives: lines, rectangles, rounded rectangles,
    polygons, circles, arcs, bezier paths, clipping.
  * A flowing layout engine: justified paragraphs, headings, bullet lists,
    tables that break across pages, and "keep-together" figure blocks.
  * Running headers/footers, roman/arabic page labels, PDF outline
    (bookmarks) and a two-pass mechanism so the table of contents, list of
    figures and list of tables can carry real page numbers.
"""

import os
import struct
import zlib

# --------------------------------------------------------------------------
# palette
# --------------------------------------------------------------------------
NAVY = (0.086, 0.180, 0.365)
NAVY_D = (0.047, 0.110, 0.235)
BLUE = (0.106, 0.412, 0.729)
BLUE_M = (0.235, 0.549, 0.831)
BLUE_L = (0.639, 0.784, 0.914)
BLUE_XL = (0.882, 0.929, 0.973)
ORANGE = (0.910, 0.475, 0.082)
ORANGE_L = (0.988, 0.796, 0.596)
ORANGE_XL = (0.996, 0.925, 0.855)
GREEN = (0.106, 0.545, 0.375)
GREEN_L = (0.647, 0.847, 0.776)
RED = (0.769, 0.196, 0.196)
RED_L = (0.957, 0.792, 0.792)
TEAL = (0.086, 0.518, 0.580)
PURPLE = (0.373, 0.278, 0.596)
GOLD = (0.839, 0.655, 0.141)
GREY_D = (0.251, 0.267, 0.298)
GREY = (0.451, 0.471, 0.502)
GREY_M = (0.678, 0.698, 0.722)
GREY_L = (0.878, 0.890, 0.902)
GREY_XL = (0.957, 0.961, 0.969)
WHITE = (1.0, 1.0, 1.0)
BLACK = (0.0, 0.0, 0.0)

SERIES = [BLUE, ORANGE, TEAL, PURPLE, GOLD, GREEN, RED, BLUE_L]


# --------------------------------------------------------------------------
# TrueType parsing
# --------------------------------------------------------------------------
class TrueTypeFont(object):
    """Minimal TrueType reader: cmap (format 4/12), hmtx, head, hhea, OS/2."""

    def __init__(self, path, name):
        self.path = path
        self.name = name
        with open(path, "rb") as fh:
            self.data = fh.read()
        self.tables = {}
        self._parse_directory()
        self._parse_head()
        self._parse_hhea()
        self._parse_maxp()
        self._parse_hmtx()
        self._parse_cmap()
        self._parse_os2()
        self.used = {}  # gid -> codepoint

    # -- table plumbing ----------------------------------------------------
    def _parse_directory(self):
        (tag,) = struct.unpack(">I", self.data[0:4])
        offset = 0
        if tag == 0x74746366:  # 'ttcf'
            offset = struct.unpack(">I", self.data[12:16])[0]
        num_tables = struct.unpack(">H", self.data[offset + 4:offset + 6])[0]
        pos = offset + 12
        for _ in range(num_tables):
            tg = self.data[pos:pos + 4].decode("latin-1")
            off, length = struct.unpack(">II", self.data[pos + 8:pos + 16])
            self.tables[tg] = (off, length)
            pos += 16

    def _table(self, tag):
        if tag not in self.tables:
            return None
        off, length = self.tables[tag]
        return self.data[off:off + length]

    def _parse_head(self):
        head = self._table("head")
        self.units_per_em = struct.unpack(">H", head[18:20])[0]
        self.xmin, self.ymin, self.xmax, self.ymax = struct.unpack(">hhhh", head[36:44])
        self.index_to_loc_format = struct.unpack(">h", head[50:52])[0]

    def _parse_hhea(self):
        hhea = self._table("hhea")
        self.ascent = struct.unpack(">h", hhea[4:6])[0]
        self.descent = struct.unpack(">h", hhea[6:8])[0]
        self.num_h_metrics = struct.unpack(">H", hhea[34:36])[0]

    def _parse_maxp(self):
        maxp = self._table("maxp")
        self.num_glyphs = struct.unpack(">H", maxp[4:6])[0]

    def _parse_os2(self):
        os2 = self._table("OS/2")
        self.cap_height = int(0.72 * self.units_per_em)
        self.italic_angle = 0
        self.weight = 400
        if os2 and len(os2) >= 90:
            ver = struct.unpack(">H", os2[0:2])[0]
            self.weight = struct.unpack(">H", os2[4:6])[0]
            if ver >= 2 and len(os2) >= 90:
                ch = struct.unpack(">h", os2[88:90])[0]
                if ch:
                    self.cap_height = ch
        post = self._table("post")
        if post and len(post) >= 12:
            raw = struct.unpack(">i", post[4:8])[0]
            self.italic_angle = raw / 65536.0

    def _parse_hmtx(self):
        hmtx = self._table("hmtx")
        self.advances = []
        pos = 0
        last = 0
        for _ in range(self.num_h_metrics):
            if pos + 4 > len(hmtx):
                break
            last = struct.unpack(">H", hmtx[pos:pos + 2])[0]
            self.advances.append(last)
            pos += 4
        while len(self.advances) < self.num_glyphs:
            self.advances.append(last)

    def _parse_cmap(self):
        cmap = self._table("cmap")
        n = struct.unpack(">H", cmap[2:4])[0]
        best = None
        best_score = -1
        for i in range(n):
            pid, eid, off = struct.unpack(">HHI", cmap[4 + i * 8:12 + i * 8])
            score = {(3, 10): 5, (3, 1): 4, (0, 4): 3, (0, 3): 3, (0, 6): 3, (0, 0): 2}.get((pid, eid), 0)
            if score > best_score:
                best_score, best = score, off
        self.cmap = {}
        if best is None:
            return
        sub = cmap[best:]
        fmt = struct.unpack(">H", sub[0:2])[0]
        if fmt == 4:
            segx2 = struct.unpack(">H", sub[6:8])[0]
            seg = segx2 // 2
            ends = struct.unpack(">%dH" % seg, sub[14:14 + segx2])
            sp = 14 + segx2 + 2
            starts = struct.unpack(">%dH" % seg, sub[sp:sp + segx2])
            dp = sp + segx2
            deltas = struct.unpack(">%dh" % seg, sub[dp:dp + segx2])
            rp = dp + segx2
            ranges = struct.unpack(">%dH" % seg, sub[rp:rp + segx2])
            for i in range(seg):
                for cp in range(starts[i], min(ends[i], 0xFFFF) + 1):
                    if ranges[i] == 0:
                        gid = (cp + deltas[i]) & 0xFFFF
                    else:
                        gp = rp + i * 2 + ranges[i] + (cp - starts[i]) * 2
                        if gp + 2 > len(sub):
                            continue
                        gid = struct.unpack(">H", sub[gp:gp + 2])[0]
                        if gid:
                            gid = (gid + deltas[i]) & 0xFFFF
                    if gid:
                        self.cmap[cp] = gid
        elif fmt == 12:
            ngroups = struct.unpack(">I", sub[12:16])[0]
            for g in range(ngroups):
                s, e, sg = struct.unpack(">III", sub[16 + g * 12:28 + g * 12])
                for cp in range(s, e + 1):
                    self.cmap[cp] = sg + (cp - s)

    # -- public API --------------------------------------------------------
    def gid(self, ch):
        cp = ord(ch)
        g = self.cmap.get(cp)
        if g is None:
            g = self.cmap.get(ord("?"), 0)
            cp = ord("?")
        self.used[g] = cp
        return g

    def glyphs(self, text):
        return [self.gid(c) for c in text]

    def width(self, text, size):
        total = 0
        for c in text:
            cp = ord(c)
            g = self.cmap.get(cp)
            if g is None:
                g = self.cmap.get(ord("?"), 0)
            total += self.advances[g] if g < len(self.advances) else 0
        return total * size / float(self.units_per_em)

    def hexstr(self, text):
        return "".join("%04X" % g for g in self.glyphs(text))

    def scaled(self, v):
        return int(round(v * 1000.0 / self.units_per_em))


# --------------------------------------------------------------------------
# PDF object plumbing
# --------------------------------------------------------------------------
class Ref(object):
    __slots__ = ("num",)

    def __init__(self, num):
        self.num = num

    def __str__(self):
        return "%d 0 R" % self.num


class Page(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ops = []

    def out(self, s):
        self.ops.append(s)


def esc_name(s):
    return s.replace(" ", "#20")


def pdf_text_string(s):
    """UTF-16BE string literal for outlines / metadata."""
    b = s.encode("utf-16-be")
    out = ["\xfe\xff"]
    for byte in b:
        c = chr(byte) if isinstance(byte, int) else byte
        if c in "()\\":
            out.append("\\" + c)
        elif ord(c) < 32:
            out.append("\\%03o" % ord(c))
        else:
            out.append(c)
    return "(" + "".join(out) + ")"


# --------------------------------------------------------------------------
# Document
# --------------------------------------------------------------------------
class Document(object):
    A4 = (595.276, 841.890)

    def __init__(self, fonts, page_size=A4, margins=(64, 64, 58, 62)):
        """fonts: dict alias -> path. margins: left, right, top, bottom."""
        self.page_w, self.page_h = page_size
        self.ml, self.mr, self.mt, self.mb = margins
        self.fonts = {}
        self.font_alias = {}
        for i, (alias, path) in enumerate(sorted(fonts.items())):
            # use the font's real name (e.g. NotoSans-Bold) as the PostScript
            # BaseFont so viewers and text extractors report it correctly
            ps_name = os.path.splitext(os.path.basename(path))[0]
            self.fonts[alias] = TrueTypeFont(path, ps_name)
            self.font_alias[alias] = "F%d" % (i + 1)
        self.pages = []
        self.page = None
        self.y = 0.0
        self.outline = []          # (level, title, page_index, y)
        self.page_kind = []        # 'cover' | 'front' | 'body'
        self.suppress_furniture = set()
        self._fig_no = 0
        self._tab_no = 0
        self.figures = []          # (number, caption, page_label)
        self.tables_list = []
        self.refs = {}             # heading key -> page label (filled pass 2)
        self._collect = {}         # heading key -> page label (pass output)
        self.chapter_title = ""
        self.total_body_pages = 0

    # ---------------- geometry helpers ----------------
    @property
    def content_w(self):
        return self.page_w - self.ml - self.mr

    @property
    def x0(self):
        return self.ml

    @property
    def x1(self):
        return self.page_w - self.mr

    @property
    def bottom(self):
        return self.mb + 16

    # ---------------- page handling ----------------
    def new_page(self, kind=None, furniture=True):
        # an implicit page break (from space()/table()/figure()) keeps the kind of
        # the page it continues, so front-matter overflow stays front matter
        if kind is None:
            kind = self.page_kind[-1] if self.page_kind else "body"
            if kind == "cover":     # a break on the cover starts the front matter
                kind = "front"
        self.page = Page(self.page_w, self.page_h)
        self.pages.append(self.page)
        self.page_kind.append(kind)
        if not furniture:
            self.suppress_furniture.add(len(self.pages) - 1)
        self.y = self.page_h - self.mt
        return self.page

    def page_index(self):
        return len(self.pages) - 1

    def page_label(self, index=None):
        if index is None:
            index = self.page_index()
        kind = self.page_kind[index]
        if kind == "cover":
            return ""
        if kind == "front":
            n = sum(1 for k in self.page_kind[:index + 1] if k == "front")
            return roman(n)
        n = sum(1 for k in self.page_kind[:index + 1] if k == "body")
        return str(n)

    def space(self, need):
        """Ensure `need` points of vertical space; page-break if not."""
        if self.y - need < self.bottom:
            self.new_page()
            return True
        return False

    def gap(self, h):
        self.y -= h

    # ---------------- raw drawing ----------------
    def out(self, s):
        self.page.out(s)

    def _col(self, c, stroke=False):
        op = "RG" if stroke else "rg"
        return "%.4f %.4f %.4f %s" % (c[0], c[1], c[2], op)

    def set_fill(self, c):
        self.out(self._col(c))

    def set_stroke(self, c):
        self.out(self._col(c, True))

    def line(self, x1, y1, x2, y2, color=GREY, w=0.7, dash=None):
        self.out("q %s %.3f w" % (self._col(color, True), w))
        if dash:
            self.out("[%s] 0 d" % " ".join("%.2f" % d for d in dash))
        self.out("%.3f %.3f m %.3f %.3f l S Q" % (x1, y1, x2, y2))

    def rect(self, x, y, w, h, fill=None, stroke=None, lw=0.7, dash=None):
        if fill is None and stroke is None:
            return
        self.out("q")
        if dash:
            self.out("[%s] 0 d" % " ".join("%.2f" % d for d in dash))
        if fill:
            self.out(self._col(fill))
        if stroke:
            self.out("%s %.3f w" % (self._col(stroke, True), lw))
        self.out("%.3f %.3f %.3f %.3f re" % (x, y, w, h))
        self.out("B" if (fill and stroke) else ("f" if fill else "S"))
        self.out("Q")

    def round_rect(self, x, y, w, h, r=4, fill=None, stroke=None, lw=0.7):
        k = 0.5523 * r
        p = []
        p.append("%.3f %.3f m" % (x + r, y))
        p.append("%.3f %.3f l" % (x + w - r, y))
        p.append("%.3f %.3f %.3f %.3f %.3f %.3f c" % (x + w - r + k, y, x + w, y + r - k, x + w, y + r))
        p.append("%.3f %.3f l" % (x + w, y + h - r))
        p.append("%.3f %.3f %.3f %.3f %.3f %.3f c" % (x + w, y + h - r + k, x + w - r + k, y + h, x + w - r, y + h))
        p.append("%.3f %.3f l" % (x + r, y + h))
        p.append("%.3f %.3f %.3f %.3f %.3f %.3f c" % (x + r - k, y + h, x, y + h - r + k, x, y + h - r))
        p.append("%.3f %.3f l" % (x, y + r))
        p.append("%.3f %.3f %.3f %.3f %.3f %.3f c" % (x, y + r - k, x + r - k, y, x + r, y))
        self.out("q")
        if fill:
            self.out(self._col(fill))
        if stroke:
            self.out("%s %.3f w" % (self._col(stroke, True), lw))
        self.out(" ".join(p) + " h")
        self.out("B" if (fill and stroke) else ("f" if fill else "S"))
        self.out("Q")

    def circle(self, cx, cy, r, fill=None, stroke=None, lw=0.7):
        k = 0.5523 * r
        self.out("q")
        if fill:
            self.out(self._col(fill))
        if stroke:
            self.out("%s %.3f w" % (self._col(stroke, True), lw))
        self.out("%.3f %.3f m" % (cx + r, cy))
        self.out("%.3f %.3f %.3f %.3f %.3f %.3f c" % (cx + r, cy + k, cx + k, cy + r, cx, cy + r))
        self.out("%.3f %.3f %.3f %.3f %.3f %.3f c" % (cx - k, cy + r, cx - r, cy + k, cx - r, cy))
        self.out("%.3f %.3f %.3f %.3f %.3f %.3f c" % (cx - r, cy - k, cx - k, cy - r, cx, cy - r))
        self.out("%.3f %.3f %.3f %.3f %.3f %.3f c" % (cx + k, cy - r, cx + r, cy - k, cx + r, cy))
        self.out("h " + ("B" if (fill and stroke) else ("f" if fill else "S")))
        self.out("Q")

    def polygon(self, pts, fill=None, stroke=None, lw=0.7, close=True):
        if not pts:
            return
        self.out("q")
        if fill:
            self.out(self._col(fill))
        if stroke:
            self.out("%s %.3f w 1 J 1 j" % (self._col(stroke, True), lw))
        self.out("%.3f %.3f m" % pts[0])
        for p in pts[1:]:
            self.out("%.3f %.3f l" % p)
        if close:
            self.out("h")
        self.out("B" if (fill and stroke) else ("f" if fill else "S"))
        self.out("Q")

    def polyline(self, pts, color=BLUE, lw=1.2, dash=None):
        if len(pts) < 2:
            return
        self.out("q %s %.3f w 1 J 1 j" % (self._col(color, True), lw))
        if dash:
            self.out("[%s] 0 d" % " ".join("%.2f" % d for d in dash))
        self.out("%.3f %.3f m" % pts[0])
        for p in pts[1:]:
            self.out("%.3f %.3f l" % p)
        self.out("S Q")

    def wedge(self, cx, cy, r, a0, a1, fill=None, stroke=None, lw=0.7, r_inner=0.0):
        """Pie/donut wedge; angles in degrees, counter-clockwise from +x."""
        import math
        steps = max(2, int(abs(a1 - a0) / 6) + 2)
        pts_out = []
        for i in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * i / float(steps))
            pts_out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        pts_in = []
        if r_inner > 0:
            for i in range(steps + 1):
                a = math.radians(a1 + (a0 - a1) * i / float(steps))
                pts_in.append((cx + r_inner * math.cos(a), cy + r_inner * math.sin(a)))
            pts = pts_out + pts_in
        else:
            pts = [(cx, cy)] + pts_out
        self.polygon(pts, fill=fill, stroke=stroke, lw=lw)

    def arrow(self, x1, y1, x2, y2, color=NAVY, lw=1.1, head=5.0, dash=None):
        import math
        ang = math.atan2(y2 - y1, x2 - x1)
        bx = x2 - head * 0.92 * math.cos(ang)
        by = y2 - head * 0.92 * math.sin(ang)
        self.polyline([(x1, y1), (bx, by)], color=color, lw=lw, dash=dash)
        p1 = (x2, y2)
        p2 = (x2 - head * math.cos(ang - 0.42), y2 - head * math.sin(ang - 0.42))
        p3 = (x2 - head * math.cos(ang + 0.42), y2 - head * math.sin(ang + 0.42))
        self.polygon([p1, p2, p3], fill=color)

    def elbow_arrow(self, x1, y1, x2, y2, color=NAVY, lw=1.0, vfirst=True, head=5.0):
        if vfirst:
            mid = (x1, y2)
        else:
            mid = (x2, y1)
        self.polyline([(x1, y1), mid], color=color, lw=lw)
        self.arrow(mid[0], mid[1], x2, y2, color=color, lw=lw, head=head)

    def clip_rect(self, x, y, w, h):
        self.out("q %.3f %.3f %.3f %.3f re W n" % (x, y, w, h))

    def clip_end(self):
        self.out("Q")

    def linear_band(self, x, y, w, h, c1, c2, steps=48, vertical=True):
        """Approximate gradient using thin bands (no shading dicts needed)."""
        for i in range(steps):
            t = i / float(steps - 1)
            c = (c1[0] + (c2[0] - c1[0]) * t, c1[1] + (c2[1] - c1[1]) * t, c1[2] + (c2[2] - c1[2]) * t)
            if vertical:
                bh = h / float(steps)
                self.rect(x, y + i * bh, w, bh * 1.04, fill=c)
            else:
                bw = w / float(steps)
                self.rect(x + i * bw, y, bw * 1.04, h, fill=c)

    # ---------------- text ----------------
    def text(self, x, y, s, font="regular", size=10, color=BLACK, char_space=None):
        if s is None or s == "":
            return 0.0
        f = self.fonts[font]
        self.out("BT %s /%s %.2f Tf" % (self._col(color), self.font_alias[font], size))
        # Tc is part of the persistent text state -- always set it explicitly so
        # a spaced-out heading cannot leak into later text objects.
        self.out("%.3f Tc" % (char_space or 0.0))
        self.out("%.3f %.3f Td <%s> Tj ET" % (x, y, f.hexstr(s)))
        w = f.width(s, size)
        if char_space:
            w += char_space * len(s)
        return w

    def text_center(self, cx, y, s, font="regular", size=10, color=BLACK, char_space=None):
        f = self.fonts[font]
        w = f.width(s, size) + (char_space * len(s) if char_space else 0)
        self.text(cx - w / 2.0, y, s, font, size, color, char_space)
        return w

    def text_right(self, rx, y, s, font="regular", size=10, color=BLACK, char_space=None):
        f = self.fonts[font]
        w = f.width(s, size) + (char_space * len(s) if char_space else 0)
        self.text(rx - w, y, s, font, size, color, char_space)
        return w

    def text_rot(self, x, y, s, angle=90, font="regular", size=9, color=BLACK):
        import math
        a = math.radians(angle)
        ca, sa = math.cos(a), math.sin(a)
        f = self.fonts[font]
        self.out("BT %s /%s %.2f Tf 0 Tc" % (self._col(color), self.font_alias[font], size))
        self.out("%.4f %.4f %.4f %.4f %.3f %.3f Tm <%s> Tj ET" % (ca, sa, -sa, ca, x, y, f.hexstr(s)))

    def text_rot_center(self, cx, cy, s, angle=90, font="regular", size=9, color=BLACK):
        import math
        f = self.fonts[font]
        w = f.width(s, size)
        a = math.radians(angle)
        x = cx - (w / 2.0) * math.cos(a)
        y = cy - (w / 2.0) * math.sin(a)
        self.text_rot(x, y, s, angle, font, size, color)

    def width(self, s, font="regular", size=10):
        return self.fonts[font].width(s, size)

    # ---------------- text flow ----------------
    def wrap(self, s, w, font="regular", size=10):
        words = s.split()
        lines, cur = [], []
        f = self.fonts[font]
        for word in words:
            trial = (" ".join(cur + [word]))
            if f.width(trial, size) <= w or not cur:
                cur.append(word)
            else:
                lines.append(" ".join(cur))
                cur = [word]
        if cur:
            lines.append(" ".join(cur))
        return lines

    def _show_justified(self, x, y, words, font, size, color, target_w):
        f = self.fonts[font]
        if len(words) == 1:
            self.text(x, y, words[0], font, size, color)
            return
        natural = sum(f.width(w, size) for w in words)
        space_w = f.width(" ", size)
        gaps = len(words) - 1
        extra = (target_w - natural - space_w * gaps) / float(gaps)
        adj = -(extra + space_w) * 1000.0 / size  # TJ units are 1/1000 em, subtractive
        parts = []
        for i, w in enumerate(words):
            parts.append("<%s>" % f.hexstr(w))
            if i != len(words) - 1:
                parts.append("%.2f" % adj)
        self.out("BT %s /%s %.2f Tf 0 Tc %.3f %.3f Td [%s] TJ ET"
                 % (self._col(color), self.font_alias[font], size, x, y, " ".join(parts)))

    def para(self, s, font="regular", size=10.2, leading=15.4, color=GREY_D,
             justify=True, indent=0.0, space_after=8.0, x=None, w=None, first_indent=0.0):
        x = self.x0 if x is None else x
        w = (self.content_w - indent) if w is None else w
        x += indent
        lines = []
        # honour a first-line indent while wrapping
        words = s.split()
        f = self.fonts[font]
        cur = []
        avail = w - first_indent
        for word in words:
            trial = " ".join(cur + [word])
            if f.width(trial, size) <= avail or not cur:
                cur.append(word)
            else:
                lines.append(cur)
                cur = [word]
                avail = w
        if cur:
            lines.append(cur)
        for i, line_words in enumerate(lines):
            self.space(leading + 2)
            self.y -= leading
            lx = x + (first_indent if i == 0 else 0)
            lw = w - (first_indent if i == 0 else 0)
            last = (i == len(lines) - 1)
            if justify and not last and len(line_words) > 1:
                self._show_justified(lx, self.y, line_words, font, size, color, lw)
            else:
                self.text(lx, self.y, " ".join(line_words), font, size, color)
        self.y -= space_after

    def bullets(self, items, font="regular", size=10.1, leading=14.6, color=GREY_D,
                indent=14.0, bullet_color=ORANGE, space_after=9.0, gap=5.0,
                marker="dot", bold_lead=True):
        for n, item in enumerate(items):
            lead, rest = None, item
            if bold_lead and ":" in item[:70]:
                head, tail = item.split(":", 1)
                if len(head.split()) <= 9:
                    lead, rest = head + ":", tail.strip()
            x = self.x0 + indent
            w = self.content_w - indent - 2
            f = self.fonts[font]
            fb = self.fonts["bold"]
            words = []
            if lead:
                words = [("bold", t) for t in lead.split()] + [("regular", t) for t in rest.split()]
            else:
                words = [("regular", t) for t in rest.split()]
            # wrap mixed-style words
            lines, cur, cw = [], [], 0.0
            space = f.width(" ", size)
            for st, tok in words:
                tw = (fb if st == "bold" else f).width(tok, size)
                if cur and cw + space + tw > w:
                    lines.append(cur)
                    cur, cw = [(st, tok)], tw
                else:
                    if cur:
                        cw += space
                    cur.append((st, tok))
                    cw += tw
            if cur:
                lines.append(cur)
            need = leading * len(lines) + gap
            if self.y - need < self.bottom and len(lines) <= 4:
                self.new_page()
            for i, line in enumerate(lines):
                self.space(leading + 2)
                self.y -= leading
                if i == 0:
                    if marker == "dot":
                        self.circle(self.x0 + 5.0, self.y + size * 0.30, 1.9, fill=bullet_color)
                    elif marker == "square":
                        self.rect(self.x0 + 3.2, self.y + size * 0.20, 3.4, 3.4, fill=bullet_color)
                    elif marker == "number":
                        self.text(self.x0 + 1.0, self.y, "%d." % (n + 1), "bold", size, bullet_color)
                    elif marker == "check":
                        self.check_mark(self.x0 + 3.0, self.y + size * 0.26, 4.0, bullet_color)
                cx = x
                for st, tok in line:
                    cx += self.text(cx, self.y, tok, st, size, NAVY_D if st == "bold" else color)
                    cx += space
            self.y -= gap
        self.y -= space_after - gap

    def check_mark(self, cx, cy, s, color=GREEN, lw=1.5):
        self.polyline([(cx - s * 0.5, cy), (cx - s * 0.1, cy - s * 0.45), (cx + s * 0.6, cy + s * 0.55)],
                      color=color, lw=lw)

    # ---------------- headings ----------------
    def chapter(self, number, title, key=None, kicker=None):
        self.new_page("body")
        self.chapter_title = "Chapter %s: %s" % (number, title) if number else title
        top = self.y
        self.rect(self.x0, top - 4, 46, 3.4, fill=ORANGE)
        y = top - 34
        if number:
            self.text(self.x0, y, "CHAPTER %s" % number, "bold", 10.5, BLUE, char_space=2.4)
            y -= 30
        else:
            y -= 4
        lines = self.wrap(title.upper(), self.content_w - 4, "bold", 21)
        for ln in lines:
            self.text(self.x0, y, ln, "bold", 21, NAVY)
            y -= 26
        y += 8
        self.line(self.x0, y, self.x1, y, NAVY, 1.4)
        self.line(self.x0, y - 3.2, self.x0 + 120, y - 3.2, ORANGE, 1.4)
        self.y = y - 26
        if kicker:
            self.para(kicker, font="italic", size=10.4, leading=15.2, color=GREY, justify=True,
                      space_after=12)
        self._register(key or ("ch%s" % number))
        self.outline.append((0, self.chapter_title, self.page_index(), self.page_h - self.mt))

    def section(self, title, key=None, space_before=14.0, size=13.0):
        self.space(size + 34)
        self.y -= space_before
        self.y -= size + 2
        self.rect(self.x0, self.y - 2.4, 3.0, size + 3.0, fill=ORANGE)
        self.text(self.x0 + 9.0, self.y, title, "bold", size, NAVY)
        self.y -= 9.0
        self._register(key or title)
        self.outline.append((1, title, self.page_index(), self.y + size + 14))

    def subsection(self, title, size=11.2, space_before=10.0):
        self.space(size + 26)
        self.y -= space_before
        self.y -= size
        self.text(self.x0, self.y, title, "semibold", size, BLUE)
        self.y -= 7.0

    def minihead(self, title, size=9.6, color=NAVY, space_before=8.0, space_after=5.0):
        self.space(size + 20)
        self.y -= space_before + size
        self.text(self.x0, self.y, title.upper(), "bold", size, color, char_space=1.1)
        self.y -= space_after

    def _register(self, key):
        self._collect[key] = self.page_label()

    def ref(self, key):
        return self.refs.get(key, "--")

    # ---------------- callouts ----------------
    def callout(self, title, body, color=BLUE, bg=BLUE_XL, icon="i", size=9.8, leading=13.6):
        pad = 10.0
        tw = self.content_w - 2 * pad - 6
        lines = self.wrap(body, tw, "regular", size)
        h = pad * 2 + (14 if title else 0) + leading * len(lines)
        self.space(h + 14)
        self.y -= h + 6
        y = self.y
        self.round_rect(self.x0, y, self.content_w, h, 3.5, fill=bg)
        self.rect(self.x0, y, 3.4, h, fill=color)
        ty = y + h - pad - 2
        if title:
            self.text(self.x0 + pad + 4, ty - 6, title.upper(), "bold", 9.0, color, char_space=1.2)
            ty -= 16
        for ln in lines:
            ty -= leading
            self.text(self.x0 + pad + 4, ty + 3, ln, "regular", size, GREY_D)
        self.y -= 8

    def stat_cards(self, cards, h=54.0, gap=9.0, cols=None):
        """cards: list of (value, label, color)"""
        cols = cols or len(cards)
        rows = (len(cards) + cols - 1) // cols
        self.space(rows * (h + gap) + 8)
        cw = (self.content_w - gap * (cols - 1)) / float(cols)
        for r in range(rows):
            self.y -= h
            row = cards[r * cols:(r + 1) * cols]
            for i, (val, lab, col) in enumerate(row):
                x = self.x0 + i * (cw + gap)
                self.round_rect(x, self.y, cw, h, 4, fill=GREY_XL, stroke=GREY_L, lw=0.6)
                self.rect(x, self.y, cw, 3.0, fill=col)
                size = 19 if len(val) <= 7 else (15.5 if len(val) <= 10 else 13)
                self.text_center(x + cw / 2.0, self.y + h - 25, val, "bold", size, col)
                lsize = 7.8
                lines = self.wrap(lab, cw - 10, "regular", lsize)
                if len(lines) > 2:
                    lsize = 7.0
                    lines = self.wrap(lab, cw - 8, "regular", lsize)
                for j, ln in enumerate(lines[:3]):
                    self.text_center(x + cw / 2.0, self.y + h - 36 - j * (lsize + 1.5), ln,
                                     "regular", lsize, GREY)
            self.y -= gap
        self.y -= 4

    # ---------------- tables ----------------
    def table(self, headers, rows, widths, aligns=None, size=8.9, header_size=8.9,
              pad=5.2, line_h=11.6, header_bg=NAVY, header_fg=WHITE, zebra=GREY_XL,
              grid=GREY_L, caption=None, note=None, col_colors=None, bold_rows=None,
              row_colors=None, fonts_col=None, min_row_h=None, header_align=None,
              number=True, space_after=10.0, cell_font="regular"):
        total = float(sum(widths))
        ws = [w / total * self.content_w for w in widths]
        aligns = aligns or ["left"] * len(widths)
        header_align = header_align or ["center"] * len(widths)
        bold_rows = bold_rows or []
        row_colors = row_colors or {}

        if caption:
            # keep the caption with at least the header and the first rows of the table
            self.space(126)
            if number:
                self._tab_no += 1
                cap = "Table %s: %s" % (self._table_label(), caption)
            else:
                cap = caption
            self.y -= 14
            self.text(self.x0, self.y, cap, "semibolditalic" if "semibolditalic" in self.fonts else "bold",
                      9.2, BLUE)
            if number:
                self.tables_list.append((self._table_label(), caption, self.page_label()))
            self.y -= 6

        def draw_header(y):
            hlines = []
            for i, htxt in enumerate(headers):
                hlines.append(self.wrap(str(htxt), ws[i] - 2 * pad, "bold", header_size))
            hh = max(len(l) for l in hlines) * (line_h - 0.6) + 2 * pad - 2
            self.rect(self.x0, y - hh, self.content_w, hh, fill=header_bg)
            x = self.x0
            for i, lines in enumerate(hlines):
                ty = y - pad - header_size * 0.92
                for ln in lines:
                    if header_align[i] == "center":
                        self.text_center(x + ws[i] / 2.0, ty, ln, "bold", header_size, header_fg)
                    elif header_align[i] == "right":
                        self.text_right(x + ws[i] - pad, ty, ln, "bold", header_size, header_fg)
                    else:
                        self.text(x + pad, ty, ln, "bold", header_size, header_fg)
                    ty -= line_h - 0.6
                x += ws[i]
            return y - hh

        self.space(92)
        y = self.y
        y = draw_header(y)
        top_of_block = y

        for ri, row in enumerate(rows):
            cell_lines = []
            for i, cell in enumerate(row):
                fnt = "bold" if (ri in bold_rows or (fonts_col and fonts_col.get(i) == "bold")) else cell_font
                cell_lines.append(self.wrap(str(cell), ws[i] - 2 * pad, fnt, size))
            rh = max(len(l) for l in cell_lines) * line_h + 2 * pad - 3.5
            if min_row_h:
                rh = max(rh, min_row_h)
            if y - rh < self.bottom:
                # close current block and continue on a new page
                self._table_frame(top_of_block, y, ws, grid)
                self.new_page()
                y = self.y
                y = draw_header(y)
                top_of_block = y
            bg = row_colors.get(ri)
            if bg is None and zebra and ri % 2 == 1:
                bg = zebra
            if ri in bold_rows and bg is None:
                bg = BLUE_XL
            if bg:
                self.rect(self.x0, y - rh, self.content_w, rh, fill=bg)
            x = self.x0
            for i, lines in enumerate(cell_lines):
                fnt = "bold" if (ri in bold_rows or (fonts_col and fonts_col.get(i) == "bold")) else cell_font
                col = NAVY_D if fnt == "bold" else GREY_D
                if col_colors and col_colors.get(i):
                    col = col_colors[i]
                ty = y - pad - size * 0.95
                for ln in lines:
                    if aligns[i] == "center":
                        self.text_center(x + ws[i] / 2.0, ty, ln, fnt, size, col)
                    elif aligns[i] == "right":
                        self.text_right(x + ws[i] - pad, ty, ln, fnt, size, col)
                    else:
                        self.text(x + pad, ty, ln, fnt, size, col)
                    ty -= line_h
                x += ws[i]
            self.line(self.x0, y - rh, self.x1, y - rh, grid, 0.5)
            y -= rh
        self._table_frame(top_of_block, y, ws, grid)
        self.y = y
        if note:
            self.y -= 12
            self.text(self.x0, self.y, note, "italic", 7.8, GREY)
        self.y -= space_after

    def _table_frame(self, top, bottom, ws, grid):
        self.rect(self.x0, bottom, self.content_w, top - bottom, stroke=grid, lw=0.6)
        x = self.x0
        for w in ws[:-1]:
            x += w
            self.line(x, bottom, x, top, grid, 0.5)

    def _table_label(self):
        return "%s.%d" % (self._chapter_no(), self._tab_no)

    def _chapter_no(self):
        t = self.chapter_title
        if t.startswith("Chapter "):
            return t.split()[1].rstrip(":")
        return "A"

    def reset_counters(self):
        self._fig_no = 0
        self._tab_no = 0

    # ---------------- figures ----------------
    def figure(self, height, draw, caption, note=None, frame=True, pad_top=12.0,
               space_after=12.0, bg=None, title=None, label=None):
        cap_h = 26.0
        need = height + cap_h + pad_top
        if self.y - need < self.bottom:
            self.new_page()
        self.y -= pad_top
        self._fig_no += 1
        label = label or ("Figure %s.%d" % (self._chapter_no(), self._fig_no))
        y = self.y - height
        if frame:
            self.round_rect(self.x0, y, self.content_w, height, 3.0,
                            fill=bg or WHITE, stroke=GREY_L, lw=0.6)
        elif bg:
            self.round_rect(self.x0, y, self.content_w, height, 3.0, fill=bg)
        inner_pad = 12.0
        if title:
            self.text(self.x0 + inner_pad, y + height - 16, title, "semibold", 9.6, NAVY)
            draw(self, self.x0 + inner_pad, y + inner_pad * 0.7,
                 self.content_w - 2 * inner_pad, height - inner_pad * 1.7 - 20)
        else:
            draw(self, self.x0 + inner_pad, y + inner_pad * 0.7,
                 self.content_w - 2 * inner_pad, height - inner_pad * 1.4)
        self.y = y - 13
        cap_lines = self.wrap("%s: %s" % (label, caption), self.content_w - 20, "italic", 8.6)
        for ln in cap_lines:
            self.text_center(self.page_w / 2.0, self.y, ln, "italic", 8.6, GREY)
            self.y -= 11
        if note:
            for ln in self.wrap(note, self.content_w - 40, "italic", 7.6):
                self.text_center(self.page_w / 2.0, self.y, ln, "italic", 7.6, GREY_M)
                self.y -= 9.6
        self.figures.append((label, caption, self.page_label()))
        self.y -= space_after

    # ---------------- furniture ----------------
    def finish(self):
        """Draw running headers/footers on every eligible page."""
        n_body = sum(1 for k in self.page_kind if k == "body")
        saved_page = self.page
        for idx, page in enumerate(self.pages):
            if idx in self.suppress_furniture or self.page_kind[idx] == "cover":
                continue
            self.page = page
            label = self.page_label(idx)
            # header
            self.line(self.ml, self.page_h - self.mt + 22, self.x1, self.page_h - self.mt + 22,
                      GREY_L, 0.6)
            self.text(self.ml, self.page_h - self.mt + 28,
                      "Internship Report  |  Financial Management Practices", "italic", 7.8, GREY_M)
            self.text_right(self.x1, self.page_h - self.mt + 28, "Infinity Interns, Patna",
                            "italic", 7.8, GREY_M)
            # footer
            fy = self.mb - 16
            self.line(self.ml, fy + 16, self.x1, fy + 16, GREY_L, 0.6)
            self.text(self.ml, fy + 5, "Gunja Kumari  |  Roll No. 35  |  MBA (Financial Management)",
                      "regular", 7.6, GREY_M)
            if self.page_kind[idx] == "body":
                self.text_right(self.x1, fy + 5, "Page %s of %d" % (label, n_body), "semibold", 7.8, GREY)
            else:
                self.text_right(self.x1, fy + 5, label, "semibold", 7.8, GREY)
        self.page = saved_page
        self.total_body_pages = n_body

    # ---------------- output ----------------
    def save(self, path, title="Internship Report", author="Gunja Kumari", subject=""):
        objs = []

        def add(body):
            objs.append(body)
            return Ref(len(objs))

        # fonts
        font_refs = {}
        for alias, f in self.fonts.items():
            file_ref = add(None)  # placeholder, filled below
            objs[file_ref.num - 1] = ("stream", {
                "Length1": len(f.data),
                "Filter": "/FlateDecode",
            }, zlib.compress(f.data, 9))
            desc = add("<< /Type /FontDescriptor /FontName /%s /Flags %d "
                       "/FontBBox [%d %d %d %d] /ItalicAngle %.1f /Ascent %d /Descent %d "
                       "/CapHeight %d /StemV 80 /FontFile2 %s >>"
                       % (esc_name(f.name), 4 if f.italic_angle == 0 else 68,
                          f.scaled(f.xmin), f.scaled(f.ymin), f.scaled(f.xmax), f.scaled(f.ymax),
                          f.italic_angle, f.scaled(f.ascent), f.scaled(f.descent),
                          f.scaled(f.cap_height), file_ref))
            gids = sorted(f.used.keys())
            w_parts = []
            i = 0
            while i < len(gids):
                run = [gids[i]]
                while i + 1 < len(gids) and gids[i + 1] == gids[i] + 1:
                    i += 1
                    run.append(gids[i])
                widths = " ".join(str(f.scaled(f.advances[g])) for g in run)
                w_parts.append("%d [%s]" % (run[0], widths))
                i += 1
            # ToUnicode CMap
            entries = ["<%04X> <%s>" % (g, "".join("%04X" % cp for cp in [f.used[g]])) for g in gids]
            chunks = []
            for j in range(0, len(entries), 100):
                part = entries[j:j + 100]
                chunks.append("%d beginbfchar\n%s\nendbfchar" % (len(part), "\n".join(part)))
            cmap = ("/CIDInit /ProcSet findresource begin\n12 dict begin\nbegincmap\n"
                    "/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n"
                    "/CMapName /Adobe-Identity-UCS def\n/CMapType 2 def\n"
                    "1 begincodespacerange\n<0000> <FFFF>\nendcodespacerange\n"
                    + "\n".join(chunks) +
                    "\nendcmap\nCMapName currentdict /CMap defineresource pop\nend\nend")
            tou = add(("stream", {"Filter": "/FlateDecode"}, zlib.compress(cmap.encode("latin-1"), 9)))
            cid = add("<< /Type /Font /Subtype /CIDFontType2 /BaseFont /%s "
                      "/CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> "
                      "/FontDescriptor %s /DW 500 /W [%s] /CIDToGIDMap /Identity >>"
                      % (esc_name(f.name), desc, " ".join(w_parts)))
            font_refs[alias] = add("<< /Type /Font /Subtype /Type0 /BaseFont /%s "
                                   "/Encoding /Identity-H /DescendantFonts [%s] /ToUnicode %s >>"
                                   % (esc_name(f.name), cid, tou))

        res = "<< /Font << %s >> /ProcSet [/PDF /Text] >>" % " ".join(
            "/%s %s" % (self.font_alias[a], font_refs[a]) for a in self.fonts)
        res_ref = add(res)

        pages_ref = Ref(0)  # patched later
        page_refs = []
        for page in self.pages:
            content = "\n".join(page.ops).encode("latin-1")
            cref = add(("stream", {"Filter": "/FlateDecode"}, zlib.compress(content, 9)))
            pref = add("<< /Type /Page /Parent {PAGES} /MediaBox [0 0 %.3f %.3f] "
                       "/Resources %s /Contents %s >>" % (page.width, page.height, res_ref, cref))
            page_refs.append(pref)

        kids = " ".join(str(p) for p in page_refs)
        pages_obj = add("<< /Type /Pages /Count %d /Kids [%s] >>" % (len(page_refs), kids))

        # outline
        outline_ref = None
        if self.outline:
            items = []
            # build a 2-level tree
            tree = []
            for level, title, pidx, y in self.outline:
                if level == 0 or not tree:
                    tree.append([(title, pidx, y), []])
                else:
                    tree[-1][1].append((title, pidx, y))
            root = add(None)
            top_refs = []
            for (t, pidx, y), children in tree:
                node = add(None)
                child_refs = []
                for ct, cp, cy in children:
                    child_refs.append(add(None))
                for i, cref in enumerate(child_refs):
                    ct, cp, cy = children[i]
                    prev = ("/Prev %s " % child_refs[i - 1]) if i > 0 else ""
                    nxt = ("/Next %s " % child_refs[i + 1]) if i < len(child_refs) - 1 else ""
                    objs[cref.num - 1] = ("<< /Title %s /Parent %s %s%s/Dest [%s /XYZ 0 %.1f 0] >>"
                                          % (pdf_text_string(ct), node, prev, nxt, page_refs[cp], cy))
                first_last = ""
                if child_refs:
                    first_last = "/First %s /Last %s /Count %d " % (child_refs[0], child_refs[-1],
                                                                    -len(child_refs))
                objs[node.num - 1] = ("<< /Title %s /Parent %s %s/Dest [%s /XYZ 0 %.1f 0] >>"
                                      % (pdf_text_string(t), root, first_last, page_refs[pidx], y))
                top_refs.append((node, first_last))
            for i, (node, fl) in enumerate(top_refs):
                body = objs[node.num - 1]
                extra = ""
                if i > 0:
                    extra += " /Prev %s" % top_refs[i - 1][0]
                if i < len(top_refs) - 1:
                    extra += " /Next %s" % top_refs[i + 1][0]
                objs[node.num - 1] = body[:-2] + extra + " >>"
            objs[root.num - 1] = ("<< /Type /Outlines /First %s /Last %s /Count %d >>"
                                  % (top_refs[0][0], top_refs[-1][0], len(top_refs)))
            outline_ref = root

        # page labels
        nums = []
        prev_kind = None
        front_start = 1
        for i, kind in enumerate(self.page_kind):
            if kind != prev_kind:
                if kind == "cover":
                    nums.append("%d << /S /D /St 1 >>" % i)
                elif kind == "front":
                    nums.append("%d << /S /r /St 1 >>" % i)
                else:
                    nums.append("%d << /S /D /St 1 >>" % i)
                prev_kind = kind
        labels = add("<< /Nums [%s] >>" % " ".join(nums))

        info = add("<< /Title %s /Author %s /Subject %s /Creator %s /Producer %s >>"
                   % (pdf_text_string(title), pdf_text_string(author), pdf_text_string(subject),
                      pdf_text_string("Custom vector PDF engine"), pdf_text_string("pdfengine.py")))
        catalog = add("<< /Type /Catalog /Pages %s /PageLabels %s %s "
                      "/ViewerPreferences << /DisplayDocTitle true >> /PageMode /UseOutlines >>"
                      % (pages_obj, labels, ("/Outlines %s" % outline_ref) if outline_ref else ""))

        # serialise
        out = bytearray()
        out += b"%PDF-1.5\n%\xe2\xe3\xcf\xd3\n"
        offsets = [0] * (len(objs) + 1)
        for i, body in enumerate(objs, start=1):
            offsets[i] = len(out)
            out += ("%d 0 obj\n" % i).encode("latin-1")
            if isinstance(body, tuple) and body[0] == "stream":
                _, extra, data = body
                d = dict(extra)
                d["Length"] = len(data)
                dic = "<< " + " ".join("/%s %s" % (k, v) for k, v in sorted(d.items())) + " >>"
                out += dic.encode("latin-1") + b"\nstream\n" + data + b"\nendstream"
            else:
                body = body.replace("{PAGES}", str(pages_obj))
                out += body.encode("latin-1")
            out += b"\nendobj\n"
        xref = len(out)
        out += ("xref\n0 %d\n" % (len(objs) + 1)).encode("latin-1")
        out += b"0000000000 65535 f \n"
        for i in range(1, len(objs) + 1):
            out += ("%010d 00000 n \n" % offsets[i]).encode("latin-1")
        out += ("trailer\n<< /Size %d /Root %s /Info %s >>\nstartxref\n%d\n%%%%EOF\n"
                % (len(objs) + 1, catalog, info, xref)).encode("latin-1")
        with open(path, "wb") as fh:
            fh.write(out)
        return len(self.pages), len(out)


def roman(n):
    vals = [(1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"),
            (50, "l"), (40, "xl"), (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    out = []
    for v, s in vals:
        while n >= v:
            out.append(s)
            n -= v
    return "".join(out)


FONT_DIR = "/usr/share/fonts/google-noto"
FONTS = {
    "regular": os.path.join(FONT_DIR, "NotoSans-Regular.ttf"),
    "bold": os.path.join(FONT_DIR, "NotoSans-Bold.ttf"),
    "italic": os.path.join(FONT_DIR, "NotoSans-Italic.ttf"),
    "semibold": os.path.join(FONT_DIR, "NotoSans-SemiBold.ttf"),
    "light": os.path.join(FONT_DIR, "NotoSans-Light.ttf"),
    "semibolditalic": os.path.join(FONT_DIR, "NotoSans-SemiBoldItalic.ttf"),
}


def fmt_inr(n, prefix="Rs. "):
    """Indian digit grouping."""
    neg = n < 0
    n = abs(int(round(n)))
    s = str(n)
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts) + "," + tail
    return ("-" if neg else "") + prefix + s
