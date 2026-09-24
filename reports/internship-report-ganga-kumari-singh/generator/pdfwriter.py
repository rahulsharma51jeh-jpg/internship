"""
The PDF layout engine.

Consumes the block list from content.py and paginates it onto A4.

Pagination runs in two passes. Before either pass, `prescan` walks the block
list and derives the complete contents, table and figure lists, keying every
entry to the *index of its block*, which is stable across passes. Pass one lays
the document out with placeholder page labels; pass two repeats it with the real
labels. Since a leader-dot row has the same height whatever label it carries,
both passes paginate identically and the printed page numbers are correct.
"""

import afm
import brand
import pdfdoc
from pdfdoc import A4, Document

# ------------------------------------------------------------------ metrics ----
PAGE_W, PAGE_H = A4
M_LEFT, M_RIGHT = 62.0, 52.0
M_TOP, M_BOT = 64.0, 62.0
CONTENT_W = PAGE_W - M_LEFT - M_RIGHT
BODY_TOP = M_TOP + 18.0                 # first baseline band below the header
BODY_BOT = PAGE_H - M_BOT - 20.0        # last band above the footer

SERIF = "Times-Roman"
SERIF_B = "Times-Bold"
SERIF_I = "Times-Italic"
SERIF_BI = "Times-BoldItalic"
SANS = "Helvetica"
SANS_B = "Helvetica-Bold"
SANS_I = "Helvetica-Oblique"

BODY_SIZE = 10.6
BODY_LEAD = 15.0
SMALL_SIZE = 9.2
PLACEHOLDER = "00"

_FACE = {("serif", "r"): SERIF, ("serif", "b"): SERIF_B,
         ("serif", "i"): SERIF_I, ("serif", "bi"): SERIF_BI,
         ("sans", "r"): SANS, ("sans", "b"): SANS_B,
         ("sans", "i"): SANS_I, ("sans", "bi"): SANS_B}


# ----------------------------------------------------------- inline markup ----
def parse_runs(text):
    """'a <b>b</b> c' -> [('a ', 'r'), ('b', 'b'), (' c', 'r')]"""
    runs = []
    bold = ital = False
    buf = []
    i, n = 0, len(text)
    while i < n:
        if text[i] == "<":
            close = text.find(">", i)
            if close != -1:
                tag = text[i + 1:close].strip().lower()
                if tag in ("b", "/b", "i", "/i", "strong", "/strong",
                           "em", "/em"):
                    if buf:
                        runs.append(("".join(buf), _style(bold, ital)))
                        buf = []
                    if tag in ("b", "strong"):
                        bold = True
                    elif tag in ("/b", "/strong"):
                        bold = False
                    elif tag in ("i", "em"):
                        ital = True
                    else:
                        ital = False
                    i = close + 1
                    continue
        buf.append(text[i])
        i += 1
    if buf:
        runs.append(("".join(buf), _style(bold, ital)))
    return runs or [("", "r")]


def _style(bold, ital):
    if bold and ital:
        return "bi"
    return "b" if bold else ("i" if ital else "r")


def _merge(base, s):
    if base == "i":
        return {"r": "i", "b": "bi", "i": "i", "bi": "bi"}[s]
    if base == "b":
        return {"r": "b", "b": "b", "i": "bi", "bi": "bi"}[s]
    return s


def _restyle(runs, base):
    return [(t, _merge(base, s)) for (t, s) in runs] if base != "r" else runs


def _segments(word, style, family, size):
    """Split a word into (face, size, text) segments, isolating the rupee."""
    face = _FACE[(family, style)]
    out, buf = [], []
    for ch in word:
        if ch == afm.RUPEE:
            if buf:
                out.append((face, size, "".join(buf)))
                buf = []
            out.append(("rupee", size, afm.RUPEE))
        else:
            buf.append(ch)
    if buf:
        out.append((face, size, "".join(buf)))
    return out


def wrap_runs(runs, width, family, size):
    """Break styled runs into lines of [word, style, width] that fit `width`."""
    words = []
    for (txt, style) in runs:
        for part in txt.split(" "):
            if part:
                words.append([part, style,
                              afm.text_width(part, _FACE[(family, style)],
                                             size)])
    space_w = afm.text_width(" ", _FACE[(family, "r")], size)
    lines, cur, cur_w = [], [], 0.0
    for w in words:
        add = w[2] if not cur else space_w + w[2]
        if cur and cur_w + add > width:
            lines.append(cur)
            cur, cur_w = [w], w[2]
        else:
            cur.append(w)
            cur_w += add
    if cur:
        lines.append(cur)
    return lines or [[]]


def line_width(line, family, size):
    if not line:
        return 0.0
    space_w = afm.text_width(" ", _FACE[(family, "r")], size)
    return sum(w[2] for w in line) + space_w * (len(line) - 1)


def plain(line):
    return " ".join(w[0] for w in line)


# ================================================================= prescan ====
def prescan(blocks):
    """
    Derive the contents, table and figure lists from the block list.

    Entries are keyed by block index, which is identical on both layout passes.
    Figures are numbered by chapter.
    """
    toc, tables, figures = [], [], []
    chap = None
    fig_n = 0
    for idx, blk in enumerate(blocks):
        kind = blk[0]
        if kind == "chapter":
            chap = blk[1]
            fig_n = 0
            label = ("CHAPTER " + blk[1] + "   " + blk[2]) if blk[1] else blk[2]
            toc.append((0, label, idx))
        elif kind == "front":
            toc.append((0, blk[1], idx))
        elif kind == "h2":
            toc.append((1, blk[1], idx))
        elif kind == "table":
            spec = blk[1]
            tables.append(("Table " + str(spec.get("number", "")),
                           spec.get("title", ""), idx))
        elif kind == "figure":
            fig_n += 1
            num = ("%s.%d" % (chap, fig_n)) if chap else str(fig_n)
            figures.append(("Figure " + num, blk[2], idx))
    return toc, tables, figures


# ================================================================== engine ====
class Writer:
    def __init__(self, images, meta=None):
        self.images = images
        self.meta = meta or {}

    def render(self, blocks):
        self.toc, self.tables, self.figures = prescan(blocks)
        self.fig_label = {idx: num for (num, _c, idx) in self.figures}
        self.labels = {}
        self._pass(blocks, final=False)
        return self._pass(blocks, final=True)

    # --------------------------------------------------------------- passes ----
    def _pass(self, blocks, final):
        self.final = final
        self.doc = Document(title=self.meta.get("title", ""),
                            author=self.meta.get("author", ""),
                            subject=self.meta.get("subject", ""))
        for name, data in self.images.items():
            self.doc.add_image(name, data)

        self.body_mode = False
        self.front_no = 0
        self.body_no = 0
        self.chapter_title = ""
        self.page_labels = []
        self.surf = None
        self.outline = []
        self.y = BODY_TOP

        self._new_page(plain=True)          # the cover
        for idx, blk in enumerate(blocks):
            self._emit(blk, idx)
        self._finish_page()

        for (title, pidx) in self.outline:
            self.doc.outline.append((title, pidx, 0))
        return self.doc

    # -------------------------------------------------------------- paging ----
    def _new_page(self, plain=False):
        if self.surf is not None:
            self._finish_page()
        self.surf = self.doc.new_page()
        self._plain = plain
        if plain:
            label = ""
        elif self.body_mode:
            self.body_no += 1
            label = str(self.body_no)
        else:
            self.front_no += 1
            label = _roman(self.front_no)
        self.page_labels.append(label)
        self.y = BODY_TOP

    def _finish_page(self):
        # The header and footer are drawn when the page is closed, so the
        # running head names the section the page actually belongs to.
        if self.surf is not None and not self._plain:
            self._draw_header()
            self._draw_footer()

    def _page_index(self):
        return len(self.doc.pages) - 1

    def _label(self):
        return self.page_labels[-1] if self.page_labels else ""

    def _space(self, need):
        if self.y + need > BODY_BOT:
            self._new_page()
            return True
        return False

    def _mark(self, idx):
        """Record the page on which block `idx` was laid out."""
        if not self.final:
            self.labels[idx] = self._label()

    def _page_of(self, idx):
        return self.labels.get(idx, PLACEHOLDER) if self.final else PLACEHOLDER

    # ----------------------------------------------------------- furniture ----
    def _draw_header(self):
        s = self.surf
        y = M_TOP - 26
        s.simple_text(M_LEFT, y, "SUMMER INTERNSHIP PROJECT REPORT", SANS_B,
                      6.6, brand.NAVY, char_space=1.05)
        right = self.chapter_title.upper()
        if right:
            w = afm.text_width(right, SANS, 6.6) + 1.05 * max(0, len(right) - 1)
            if w < CONTENT_W * 0.55:
                s.simple_text(M_LEFT + CONTENT_W - w, y, right, SANS, 6.6,
                              brand.GREY, char_space=1.05)
        s.hline(M_LEFT, M_LEFT + CONTENT_W, M_TOP - 18, brand.GREY_HAIR, 0.6)
        s.rect(M_LEFT, M_TOP - 19.0, 44, 1.5, brand.ORANGE)

    def _draw_footer(self):
        s = self.surf
        y = PAGE_H - M_BOT + 6
        s.hline(M_LEFT, M_LEFT + CONTENT_W, y - 11, brand.GREY_HAIR, 0.6)
        left = brand.STUDENT_NAME.title() + "  |  Roll No. " + brand.ROLL_NO
        s.simple_text(M_LEFT, y + 2, left, SERIF_I, 7.4, brand.GREY)
        right = brand.COMPANY_BRAND + ", Patna"
        s.simple_text(M_LEFT + CONTENT_W - afm.text_width(right, SERIF_I, 7.4),
                      y + 2, right, SERIF_I, 7.4, brand.GREY)
        label = self._label()
        if label:
            cx = M_LEFT + CONTENT_W / 2.0
            s.round_rect(cx - 17, y - 6.5, 34, 13.5, 6.75, brand.NAVY)
            lw = afm.text_width(label, SANS_B, 7.8)
            s.simple_text(cx - lw / 2.0, y + 3.0, label, SANS_B, 7.8,
                          brand.PAPER)

    # ============================================================ dispatch ====
    def _emit(self, blk, idx):
        fn = getattr(self, "_b_" + blk[0], None)
        if fn is None:
            raise ValueError("unknown block: " + blk[0])
        self._idx = idx
        fn(*blk[1:])

    # ---------------------------------------------------------------- cover ----
    def _b_cover(self):
        s = self.surf
        s.rect(0, 0, PAGE_W, 198, brand.NAVY_DEEP)
        s.rect(0, 198, PAGE_W, 5.5, brand.ORANGE)
        key = "logo_mark_mono"
        if key in self.doc.images:
            iw, ih = pdfdoc.png_dimensions(self.images[key])
            w = 168.0
            h = w * ih / iw
            s.image(self.doc.images[key][0], (PAGE_W - w) / 2.0, 26, w, h)
        self._centre(s, 152, brand.COMPANY_BRAND.upper(), SANS_B, 19.5,
                     brand.PAPER, 4.4)
        self._centre(s, 175, brand.COMPANY_TAG, SANS, 8.0, brand.BLUE_PALE, 0.5)

        y = 252
        self._centre(s, y, brand.REPORT_TITLE, SANS_B, 15.0, brand.NAVY, 3.0)
        y += 16
        s.rect((PAGE_W - 116) / 2.0, y, 116, 2.2, brand.ORANGE)
        y += 30
        self._centre(s, y, "A STUDY ON", SANS, 8.2, brand.GREY, 2.8)
        y += 25
        for ln in ["FINANCIAL MANAGEMENT PRACTICES,",
                   "BUDGETARY CONTROL AND FINANCIAL",
                   "PERFORMANCE ANALYSIS"]:
            self._centre(s, y, ln, SERIF_B, 16.6, brand.NAVY_MID, 0.6)
            y += 22
        y += 8
        self._centre(s, y, "at", SERIF_I, 10.6, brand.GREY)
        y += 19
        self._centre(s, y, brand.COMPANY_LEGAL, SERIF_B, 12.2, brand.NAVY)
        y += 15
        self._centre(s, y, brand.COMPANY_ADDR1 + ", " + brand.COMPANY_ADDR2,
                     SERIF, 9.6, brand.INK_SOFT)

        y += 32
        s.hline(M_LEFT + 66, PAGE_W - M_RIGHT - 66, y, brand.GREY_LIGHT, 0.7)
        y += 22
        self._centre(s, y, "Submitted in partial fulfilment of the "
                     "requirements for the award of the degree of",
                     SERIF_I, 9.2, brand.INK_SOFT)
        y += 19
        self._centre(s, y, brand.DEGREE.upper(), SANS_B, 11.8, brand.NAVY, 1.6)
        y += 14
        self._centre(s, y, "Specialisation:  " + brand.COURSE, SERIF, 9.8,
                     brand.INK_SOFT)

        y += 28
        panel_h = 112
        s.round_rect(M_LEFT + 30, y, CONTENT_W - 60, panel_h, 7,
                     brand.BLUE_MIST)
        s.rect(M_LEFT + 30, y, 3.4, panel_h, brand.ORANGE)
        rows = [("Submitted by", brand.STUDENT_NAME.title()),
                ("Father's Name", "Shri " + brand.FATHER_NAME),
                ("Roll Number", brand.ROLL_NO),
                ("Registration Number", brand.REG_NO),
                ("Programme", brand.DEGREE_SHORT + "   |   " + brand.SEMESTER +
                 "   |   Session " + brand.SESSION)]
        ry = y + 22
        lx = M_LEFT + 52
        for (k, v) in rows:
            s.simple_text(lx, ry, k, SANS_B, 7.8, brand.NAVY_MID)
            s.simple_text(lx + 126, ry, v, SERIF_B, 10.0, brand.INK)
            ry += 18.4
        y += panel_h + 30

        self._centre(s, y, brand.UNIVERSITY_LN, SANS_B, 12.4, brand.NAVY, 2.2)
        y += 16
        self._centre(s, y, "Department of Business Administration", SERIF,
                     9.6, brand.INK_SOFT)
        y += 24
        self._centre(s, y, "Internship Period:  " + brand.INTERN_SPAN,
                     SERIF_I, 9.4, brand.ORANGE)

        s.rect(0, PAGE_H - 27, PAGE_W, 27, brand.NAVY_DEEP)
        s.rect(0, PAGE_H - 30.5, PAGE_W, 3.5, brand.ORANGE)
        self._centre(s, PAGE_H - 10, brand.COMPANY_BRAND.upper() +
                     "     \u2022     B-HUB, MAURYA LOK COMPLEX, PATNA",
                     SANS, 7.2, brand.BLUE_PALE, 1.8)
        self.y = BODY_BOT + 500        # nothing else belongs on the cover

    def _centre(self, s, y, text, face, size, rgb, tracking=0.0):
        w = afm.text_width(text, face, size) + tracking * max(0, len(text) - 1)
        s.simple_text((PAGE_W - w) / 2.0, y, text, face, size, rgb,
                      char_space=tracking)

    # ------------------------------------------------------------ structure ----
    def _b_pagebreak(self):
        self._new_page()

    def _b_spacer(self, pts):
        self.y += pts

    def _b_rule(self):
        self._space(12)
        self.surf.hline(M_LEFT, M_LEFT + CONTENT_W, self.y + 5,
                        brand.GREY_LIGHT, 0.7)
        self.y += 13

    def _b_chapter(self, number, title, standfirst):
        if number == "1":
            self.body_mode = True
            self.body_no = 0
        if self.y > BODY_TOP + 1:
            self._new_page()
        self.chapter_title = title
        self._mark(self._idx)
        self.outline.append((("Chapter " + number + " \u2014 " + title)
                             if number else title, self._page_index()))
        s = self.surf
        y = self.y + 14
        band_h = 94.0
        s.rect(M_LEFT, y, CONTENT_W, band_h, brand.NAVY)
        s.rect(M_LEFT, y + band_h, CONTENT_W, 4, brand.ORANGE)
        tx = M_LEFT + 24
        if number:
            s.simple_text(tx, y + 38, "CHAPTER", SANS_B, 8.0,
                          brand.BLUE_LIGHT, char_space=2.8)
            s.simple_text(tx, y + 76, number, SANS_B, 33, brand.ORANGE)
            tx += max(46.0, afm.text_width(number, SANS_B, 33) + 26)
        avail = CONTENT_W - (tx - M_LEFT) - 24
        size = 19.0
        lines = wrap_runs([(title, "r")], avail, "sans", size)
        while len(lines) > 2 and size > 13:
            size -= 1.0
            lines = wrap_runs([(title, "r")], avail, "sans", size)
        ty = y + (46 if len(lines) > 1 else 57)
        for ln in lines[:2]:
            s.simple_text(tx, ty, plain(ln), SANS_B, size, brand.PAPER,
                          char_space=0.5)
            ty += size * 1.16
        self.y = y + band_h + 22
        if standfirst:
            self._para(standfirst, SERIF_I, 10.6, 15.2, brand.INK_SOFT,
                       justify=False)
            self.y += 6

    def _b_front(self, title, subtitle):
        if self.y > BODY_TOP + 1:
            self._new_page()
        self.chapter_title = title
        self._mark(self._idx)
        self.outline.append((title, self._page_index()))
        s = self.surf
        y = self.y + 20
        self._centre(s, y, title, SANS_B, 16.5, brand.NAVY, 3.4)
        y += 11
        s.rect((PAGE_W - 92) / 2.0, y, 92, 2.4, brand.ORANGE)
        if subtitle:
            y += 19
            self._centre(s, y, subtitle, SERIF_I, 10.2, brand.INK_SOFT)
        self.y = y + 24

    def _b_front_sub(self, title):
        self._space(50)
        self.chapter_title = title
        s = self.surf
        y = self.y + 14
        self._centre(s, y, title, SANS_B, 13.2, brand.NAVY, 2.6)
        y += 9
        s.rect((PAGE_W - 72) / 2.0, y, 72, 2.0, brand.ORANGE)
        self.y = y + 18

    # ------------------------------------------------------------- headings ----
    def _b_h2(self, text):
        self._space(44)
        self._mark(self._idx)
        s = self.surf
        y = self.y + 15
        lines = wrap_runs(parse_runs(text), CONTENT_W - 13, "sans", 12.0)
        bar_top = y - 9.5
        for ln in lines:
            s.simple_text(M_LEFT + 11, y, plain(ln), SANS_B, 12.0, brand.NAVY)
            y += 14.6
        s.rect(M_LEFT, bar_top, 3.2, (y - 14.6) - bar_top + 12, brand.ORANGE)
        s.hline(M_LEFT, M_LEFT + CONTENT_W, y - 5, brand.GREY_HAIR, 0.6)
        self.y = y + 4

    def _b_h3(self, text):
        self._space(32)
        y = self.y + 13
        for ln in wrap_runs(parse_runs(text), CONTENT_W, "sans", 10.3):
            self.surf.simple_text(M_LEFT, y, plain(ln), SANS_B, 10.3,
                                  brand.NAVY_MID)
            y += 13
        self.y = y + 1

    # ---------------------------------------------------------------- text ----
    def _para(self, text, face, size, lead, rgb, justify=True,
              indent_left=0.0, indent_right=0.0, align="left"):
        family = "sans" if face in (SANS, SANS_B, SANS_I) else "serif"
        base = "i" if face in (SERIF_I, SANS_I) else (
            "b" if face in (SERIF_B, SANS_B) else "r")
        runs = _restyle(parse_runs(text), base)
        avail = CONTENT_W - indent_left - indent_right
        lines = wrap_runs(runs, avail, family, size)
        pages = []
        for i, ln in enumerate(lines):
            self._space(lead)
            y = self.y + size * 0.86
            last = (i == len(lines) - 1)
            self._draw_line(ln, M_LEFT + indent_left, y, avail, family, size,
                            rgb, justify and not last, align)
            pages.append(self._page_index())
            self.y += lead
        return pages

    def _draw_line(self, line, x, y, avail, family, size, rgb, justify, align):
        if not line:
            return
        space_w = afm.text_width(" ", _FACE[(family, "r")], size)
        total = sum(w[2] for w in line)
        gaps = len(line) - 1
        if justify and gaps > 0:
            gap = max(space_w, min((avail - total) / gaps, space_w * 3.4))
        else:
            gap = space_w
        natural = total + gap * gaps
        if align == "center":
            x += (avail - natural) / 2.0
        elif align == "right":
            x += (avail - natural)
        pen = x
        for k, (word, style, w) in enumerate(line):
            self.surf.text(pen, y, _segments(word, style, family, size), rgb)
            pen += w + (gap if k < gaps else 0)

    def _b_p(self, text):
        self._para(text, SERIF, BODY_SIZE, BODY_LEAD, brand.INK)
        self.y += 4.8

    def _b_lead(self, text):
        self._space(36)
        p0 = self._page_index()
        top = self.y + 3
        pages = self._para(text, SERIF_I, 11.9, 16.4, brand.NAVY_MID,
                           justify=False, indent_left=15)
        if pages and pages[-1] == p0:
            self.surf.rect(M_LEFT, top, 2.6, self.y - top - 3,
                           brand.BLUE_LIGHT)
        self.y += 8

    def _b_center(self, text):
        self._para(text, SERIF, BODY_SIZE + 0.5, BODY_LEAD + 1, brand.NAVY,
                   justify=False, align="center")
        self.y += 6

    def _b_small(self, text):
        self._para(text, SERIF_I, SMALL_SIZE, 12.6, brand.INK_SOFT,
                   justify=False)
        self.y += 4

    def _b_quote(self, text, attrib):
        self._space(56)
        p0 = self._page_index()
        top = self.y + 5
        self._para("\u201c" + text + "\u201d", SERIF_I, 12.0, 16.6,
                   brand.NAVY, justify=False, indent_left=28, indent_right=22)
        if attrib:
            self.y += 2
            self._para("\u2014 " + attrib, SERIF, 9.5, 13, brand.GREY,
                       justify=False, indent_left=28)
        if self._page_index() == p0:
            self.surf.rect(M_LEFT + 8, top, 3.0, self.y - top - 3,
                           brand.ORANGE)
        self.y += 8

    # --------------------------------------------------------------- lists ----
    def _list(self, items, marker_fn, gap=4.6):
        for i, it in enumerate(items):
            marker = marker_fn(i)
            mw = afm.text_width(marker, SERIF_B, BODY_SIZE)
            indent = max(17.0, mw + 7.0)
            lines = wrap_runs(parse_runs(it), CONTENT_W - indent, "serif",
                              BODY_SIZE)
            self._space(min(len(lines), 2) * BODY_LEAD)
            first = True
            for k, ln in enumerate(lines):
                self._space(BODY_LEAD)
                y = self.y + BODY_SIZE * 0.86
                if first:
                    self.surf.simple_text(M_LEFT + 2, y, marker, SERIF_B,
                                          BODY_SIZE, brand.ORANGE)
                    first = False
                self._draw_line(ln, M_LEFT + indent, y, CONTENT_W - indent,
                                "serif", BODY_SIZE, brand.INK,
                                k < len(lines) - 1, "left")
                self.y += BODY_LEAD
            self.y += gap

    def _b_bullets(self, items):
        self.y += 2
        self._list(items, lambda i: "\u2022")
        self.y += 3

    def _b_numbers(self, items):
        self.y += 2
        self._list(items, lambda i: "%d." % (i + 1))
        self.y += 3

    def _b_refs(self, items):
        self.y += 2
        for it in items:
            lines = wrap_runs(parse_runs(it), CONTENT_W - 20, "serif", 9.8)
            self._space(min(len(lines), 2) * 13.2)
            for k, ln in enumerate(lines):
                self._space(13.2)
                y = self.y + 8.4
                x = M_LEFT if k == 0 else M_LEFT + 20
                w = CONTENT_W if k == 0 else CONTENT_W - 20
                self._draw_line(ln, x, y, w, "serif", 9.8, brand.INK, False,
                                "left")
                self.y += 13.2
            self.y += 4.4
        self.y += 2

    def _b_defs(self, items):
        self.y += 3
        for (term, body) in items:
            t_lines = wrap_runs(_restyle(parse_runs(term), "b"),
                                CONTENT_W - 10, "sans", 9.7)
            self._space(len(t_lines) * 12.8 + BODY_LEAD * 2)
            p0 = self._page_index()
            top = self.y
            for ln in t_lines:
                self._space(12.8)
                y = self.y + 8.3
                self.surf.simple_text(M_LEFT + 10, y, plain(ln), SANS_B, 9.7,
                                      brand.NAVY_MID)
                self.y += 12.8
            self._para(body, SERIF, BODY_SIZE, BODY_LEAD, brand.INK,
                       indent_left=10)
            if self._page_index() == p0:
                self.surf.rect(M_LEFT, top + 1, 1.8, self.y - top - 4,
                               brand.GREY_LIGHT)
            self.y += 7
        self.y += 2

    # ------------------------------------------------------------- callout ----
    def _b_callout(self, kind, title, body):
        tint, accent = {
            "info": (brand.BLUE_MIST, brand.NAVY_MID),
            "note": (brand.ORANGE_PALE, brand.ORANGE),
            "warn": (brand.RED_PALE, brand.RED),
            "good": (brand.GREEN_PALE, brand.GREEN),
        }.get(kind, (brand.BLUE_MIST, brand.NAVY_MID))

        pad = 11.0
        inner = CONTENT_W - 2 * pad - 8
        t_lines = wrap_runs(_restyle(parse_runs(title), "b"), inner, "sans",
                            9.9)
        b_lines = wrap_runs(parse_runs(body), inner, "serif", 9.8)
        h = pad + len(t_lines) * 13.0 + 3 + len(b_lines) * 13.4 + pad - 3
        if self.y + h > BODY_BOT:
            self._new_page()
        self.y += 8
        top = self.y
        s = self.surf
        s.round_rect(M_LEFT, top, CONTENT_W, h, 5, tint)
        s.rect(M_LEFT, top, 3.6, h, accent)
        y = top + pad + 2
        for ln in t_lines:
            s.simple_text(M_LEFT + pad + 8, y, plain(ln), SANS_B, 9.9, accent)
            y += 13.0
        y += 3
        for k, ln in enumerate(b_lines):
            self._draw_line(ln, M_LEFT + pad + 8, y, inner, "serif", 9.8,
                            brand.INK, k < len(b_lines) - 1, "left")
            y += 13.4
        self.y = top + h + 12

    # ------------------------------------------------------------------ kpi ----
    def _b_kpi(self, items):
        n = len(items)
        gap = 9.0
        w = (CONTENT_W - gap * (n - 1)) / n
        h = 60.0
        self._space(h + 16)
        self.y += 6
        top = self.y
        s = self.surf
        for i, (value, label, note) in enumerate(items):
            x = M_LEFT + i * (w + gap)
            s.round_rect(x, top, w, h, 5, brand.BLUE_MIST)
            s.rect(x, top, w, 2.8, brand.SERIES[i % len(brand.SERIES)])
            size = 15.0
            while afm.text_width(value, SANS_B, size) > w - 12 and size > 8:
                size -= 0.5
            vw = afm.text_width(value, SANS_B, size)
            s.simple_text(x + (w - vw) / 2.0, top + 27, value, SANS_B, size,
                          brand.NAVY)
            yy = top + 39
            for (txt, face, fsz, col, maxl) in [
                    (label, SANS_B, 7.1, brand.INK_SOFT, 1),
                    (note, SERIF_I, 6.9, brand.GREY, 2)]:
                for ln in wrap_runs([(txt, "r")], w - 10,
                                    "sans" if face == SANS_B else "serif",
                                    fsz)[:maxl]:
                    t = plain(ln)
                    tw = afm.text_width(t, face, fsz)
                    s.simple_text(x + (w - tw) / 2.0, yy, t, face, fsz, col)
                    yy += 8.6
        self.y = top + h + 14

    # ------------------------------------------------------------ signature ----
    def _b_signatures(self, items):
        self._space(62)
        self.y += 16
        s = self.surf
        n = len(items)
        w = CONTENT_W / n
        base = self.y
        for i, (role, name) in enumerate(items):
            cx = M_LEFT + i * w + w / 2.0
            s.hline(cx - 70, cx + 70, base, brand.INK_SOFT, 0.7)
            y = base + 12
            if role:
                tw = afm.text_width(role, SANS_B, 8.7)
                s.simple_text(cx - tw / 2.0, y, role, SANS_B, 8.7, brand.NAVY)
                y += 11.4
            if name:
                for ln in wrap_runs([(name, "r")], w - 14, "serif", 8.7):
                    t = plain(ln)
                    tw = afm.text_width(t, SERIF, 8.7)
                    s.simple_text(cx - tw / 2.0, y, t, SERIF, 8.7,
                                  brand.INK_SOFT)
                    y += 10.8
        self.y = base + 40

    # --------------------------------------------------------------- figures ----
    def _b_figure_inline(self, key, frac):
        data = self.images.get(key)
        if data is None:
            return
        iw, ih = pdfdoc.png_dimensions(data)
        w = CONTENT_W * frac
        h = w * ih / iw
        self._space(h + 12)
        self.surf.image(self.doc.images[key][0],
                        M_LEFT + (CONTENT_W - w) / 2.0, self.y + 4, w, h)
        self.y += h + 12

    def _b_figure(self, key, caption, source):
        data = self.images.get(key)
        if data is None:
            return
        iw, ih = pdfdoc.png_dimensions(data)
        w = CONTENT_W * 0.88
        h = w * ih / iw
        fx = M_LEFT + (CONTENT_W - w) / 2.0
        label = self.fig_label.get(self._idx, "Figure")
        lw = afm.text_width(label, SANS_B, 9.0)
        cap_lines = wrap_runs([(caption, "r")], CONTENT_W - lw - 70, "sans",
                              9.0)
        need = h + 14 + len(cap_lines) * 12 + (12 if source else 0) + 10
        if self.y + need > BODY_BOT:
            self._new_page()
        self.y += 8
        self._mark(self._idx)
        s = self.surf
        s.image(self.doc.images[key][0], fx, self.y, w, h)
        s.line(fx, self.y, fx + w, self.y, brand.GREY_HAIR, 0.5)
        s.line(fx, self.y + h, fx + w, self.y + h, brand.GREY_HAIR, 0.5)
        self.y += h + 11
        first = True
        for ln in cap_lines:
            t = plain(ln)
            tw = afm.text_width(t, SANS, 9.0)
            total = (lw + 6 + tw) if first else tw
            x = M_LEFT + (CONTENT_W - total) / 2.0
            if first:
                s.simple_text(x, self.y + 7, label, SANS_B, 9.0, brand.ORANGE)
                x += lw + 6
                first = False
            s.simple_text(x, self.y + 7, t, SANS, 9.0, brand.INK_SOFT)
            self.y += 12
        if source:
            tw = afm.text_width(source, SERIF_I, 8.0)
            s.simple_text(M_LEFT + (CONTENT_W - tw) / 2.0, self.y + 6, source,
                          SERIF_I, 8.0, brand.GREY)
            self.y += 12
        self.y += 8

    # ---------------------------------------------------------------- tables ----
    def _b_table(self, spec):
        cols = spec["cols"]
        fs = 9.0 * spec.get("font_scale", 1.0)
        lead = fs * 1.30
        pad_x, pad_y = 5.0, 4.2
        widths = [CONTENT_W * c[1] for c in cols]
        ncol = len(cols)

        def wrap_cell(txt, ci, family, base):
            avail = max(widths[ci] - 2 * pad_x, 12)
            return wrap_runs(_restyle(parse_runs(str(txt)), base), avail,
                             family, fs)

        head_lines = [wrap_cell(c[0], i, "sans", "b")
                      for i, c in enumerate(cols)]
        head_h = max(len(l) for l in head_lines) * (fs * 1.26) + 2 * pad_y

        body = []
        for (cells, style) in spec["rows"]:
            cells = list(cells) + [""] * (ncol - len(cells))
            emph = style in ("total", "group")
            fam = "sans" if emph else "serif"
            base = "b" if emph else "r"
            wrapped = [wrap_cell(cells[i], i, fam, base) for i in range(ncol)]
            h = max(len(l) for l in wrapped) * lead + 2 * pad_y - 1
            body.append((wrapped, style, h, fam))

        cap = ("Table " + str(spec["number"])) if spec.get("number") else ""
        cap_w = afm.text_width(cap, SANS_B, 9.2) + 6 if cap else 0
        cap_lines = wrap_runs([(spec.get("title") or "", "r")],
                              CONTENT_W - cap_w, "sans", 9.2)
        note_lines = (wrap_runs(parse_runs(spec["note"]), CONTENT_W - 26,
                                "serif", 8.2) if spec.get("note") else [])

        cap_h = len(cap_lines) * 12.4 + 3
        keep = cap_h + head_h + sum(r[2] for r in body[:2]) + 8
        if self.y + keep > BODY_BOT:
            self._new_page()
        self.y += 9
        self._mark(self._idx)

        # --- caption ------------------------------------------------------
        s = self.surf
        for i, ln in enumerate(cap_lines):
            y = self.y + 8.6
            x = M_LEFT
            if i == 0 and cap:
                s.simple_text(x, y, cap, SANS_B, 9.2, brand.ORANGE)
                x += cap_w
            s.simple_text(x, y, plain(ln), SANS_B, 9.2, brand.NAVY)
            self.y += 12.4
        self.y += 2.5

        # --- header band --------------------------------------------------
        def draw_header(top):
            s2 = self.surf
            s2.rect(M_LEFT, top, CONTENT_W, head_h, brand.NAVY)
            cx = M_LEFT
            for i, c in enumerate(cols):
                yy = top + pad_y + fs * 0.92
                for ln in head_lines[i]:
                    t = plain(ln)
                    tw = afm.text_width(t, SANS_B, fs)
                    tx = (cx + widths[i] - pad_x - tw if c[2] == "r"
                          else (cx + (widths[i] - tw) / 2.0 if c[2] == "c"
                                else cx + pad_x))
                    s2.simple_text(tx, yy, t, SANS_B, fs, brand.PAPER)
                    yy += fs * 1.26
                cx += widths[i]
            return top + head_h

        y = draw_header(self.y)
        band = 0
        for (wrapped, style, h, fam) in body:
            if y + h > BODY_BOT:
                self.surf.hline(M_LEFT, M_LEFT + CONTENT_W, y, brand.NAVY, 0.9)
                self._new_page()
                self.y += 2
                y = draw_header(self.y)
                band = 0
            s = self.surf
            if style == "group":
                s.rect(M_LEFT, y, CONTENT_W, h, brand.NAVY_MID)
            elif style == "total":
                s.rect(M_LEFT, y, CONTENT_W, h, brand.BLUE_PALE)
            elif band % 2 == 1:
                s.rect(M_LEFT, y, CONTENT_W, h, brand.PAPER_WARM)
            emph = style in ("total", "group")
            col = (brand.PAPER if style == "group"
                   else (brand.NAVY if style == "total" else brand.INK))
            cx = M_LEFT
            for i, c in enumerate(cols):
                yy = y + pad_y + fs * 0.90
                for ln in wrapped[i]:
                    if not ln:
                        yy += lead
                        continue
                    tw = line_width(ln, fam, fs)
                    tx = (cx + widths[i] - pad_x - tw if c[2] == "r"
                          else (cx + (widths[i] - tw) / 2.0 if c[2] == "c"
                                else cx + pad_x))
                    self._draw_line(ln, tx, yy, tw, fam, fs, col, False,
                                    "left")
                    yy += lead
                cx += widths[i]
            if style != "group":
                s.hline(M_LEFT, M_LEFT + CONTENT_W, y + h, brand.GREY_HAIR,
                        0.4)
            y += h
            band += 1
        self.surf.hline(M_LEFT, M_LEFT + CONTENT_W, y, brand.NAVY, 0.9)
        self.y = y + 4

        for k, ln in enumerate(note_lines):
            self._space(11.4)
            yy = self.y + 7.6
            if k == 0:
                self.surf.simple_text(M_LEFT, yy, "Note:", SANS_B, 8.2,
                                      brand.GREY)
            self._draw_line(ln, M_LEFT + 26, yy, CONTENT_W - 26, "serif", 8.2,
                            brand.GREY, False, "left")
            self.y += 11.4
        self.y += 10

    # ------------------------------------------- contents and list of items ----
    def _dotted(self, level, text, label, size=9.7):
        indent = 0.0 if level == 0 else 18.0
        face = SANS_B if level == 0 else SERIF
        col = brand.NAVY if level == 0 else brand.INK
        lead = 15.4 if level == 0 else 13.4
        self._space(lead + (4 if level == 0 else 0))
        if level == 0:
            self.y += 4
        y = self.y + size * 0.86
        s = self.surf
        lab_face = SANS_B if level == 0 else SERIF
        lw = afm.text_width(label, lab_face, size)
        avail = CONTENT_W - indent - lw - 16
        t = text
        if afm.text_width(t, face, size) > avail:
            while len(t) > 6 and afm.text_width(t + "\u2026", face,
                                                size) > avail:
                t = t[:-1]
            t = t.rstrip(" ,;:-") + "\u2026"
        tw = afm.text_width(t, face, size)
        x = M_LEFT + indent
        s.simple_text(x, y, t, face, size, col)
        d0 = x + tw + 5
        d1 = M_LEFT + CONTENT_W - lw - 5
        if d1 > d0 + 6:
            step = afm.text_width(".", SERIF, size) * 2.4
            count = int((d1 - d0) / step)
            if count > 0:
                s.simple_text(d0, y, "." * count, SERIF, size,
                              brand.GREY_LIGHT,
                              char_space=step - afm.text_width(".", SERIF,
                                                               size))
        s.simple_text(M_LEFT + CONTENT_W - lw, y, label, lab_face, size,
                      brand.NAVY if level == 0 else brand.INK_SOFT)
        self.y += lead

    def _b_toc(self):
        self.y += 4
        for (level, text, idx) in self.toc:
            self._dotted(level, text, self._page_of(idx))

    def _b_lot(self):
        self.y += 4
        for (num, title, idx) in self.tables:
            self._dotted(1, num + "   " + title, self._page_of(idx), 9.1)

    def _b_lof(self):
        self.y += 4
        for (num, caption, idx) in self.figures:
            self._dotted(1, num + "   " + caption, self._page_of(idx), 9.1)


def _roman(n):
    vals = [(1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"),
            (90, "xc"), (50, "l"), (40, "xl"), (10, "x"), (9, "ix"),
            (5, "v"), (4, "iv"), (1, "i")]
    out = []
    for (v, sym) in vals:
        while n >= v:
            out.append(sym)
            n -= v
    return "".join(out)


def build_pdf(blocks, images, meta=None):
    w = Writer(images, meta)
    doc = w.render(blocks)
    return doc.build(), len(doc.pages)
