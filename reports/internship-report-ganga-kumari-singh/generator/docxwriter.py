"""
A hand-built OOXML (.docx) writer.

A .docx is a ZIP of XML parts. This module writes the minimum set Word needs
(content types, relationships, styles, numbering, the document body, headers and
footers, and the embedded images) and maps the same block list used by the PDF
writer onto WordprocessingML, so the two files carry identical content and a
matching visual design.

Word paginates the flow itself, so there is no layout engine here: page breaks
come from the explicit pagebreak blocks, and the table of contents is emitted as
a real TOC field that Word populates on open, plus a static fallback list so the
document is readable even before the field is refreshed.
"""

import zipfile

import brand
import content as content_mod
import pdfdoc

# ---------------------------------------------------------------- constants ----
EMU_PER_PT = 12700
TWIP = 20                      # twentieths of a point
PAGE_W_TW = 11906              # A4 width in twips
PAGE_H_TW = 16838
MARG_L, MARG_R = 1247, 1041    # ~62pt / ~52pt, matching the PDF
MARG_T, MARG_B = 1280, 1240
HEADER_D, FOOTER_D = 620, 600
CONTENT_TW = PAGE_W_TW - MARG_L - MARG_R

SANS = brand.FONT_SANS_DOCX
SERIF = brand.FONT_SERIF_DOCX

NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/'
      'relationships" '
      'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/'
      'wordprocessingDrawing" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" '
      'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"')


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def hx(rgb):
    return brand.hex_of(rgb)


# ------------------------------------------------------------- run building ----
def runs_xml(text, face=SERIF, size=21, colour=brand.INK, bold=False,
             italic=False, caps=False, spacing=None, small=False):
    """
    Convert inline <b>/<i> markup into a sequence of w:r elements.

    `size` is in half-points, as WordprocessingML requires.
    """
    import pdfwriter
    out = []
    for (chunk, style) in pdfwriter.parse_runs(text):
        if chunk == "":
            continue
        b = bold or style in ("b", "bi")
        i = italic or style in ("i", "bi")
        props = ['<w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="%s"/>'
                 % (face, face, face)]
        if b:
            props.append("<w:b/>")
        if i:
            props.append("<w:i/>")
        if caps:
            props.append("<w:caps/>")
        props.append('<w:color w:val="%s"/>' % hx(colour))
        if spacing:
            props.append('<w:spacing w:val="%d"/>' % spacing)
        props.append('<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (size, size))
        out.append('<w:r><w:rPr>%s</w:rPr><w:t xml:space="preserve">%s</w:t>'
                   '</w:r>' % ("".join(props), esc(chunk)))
    return "".join(out)


def para(inner, align=None, before=0, after=100, line=None, ind_left=0,
         ind_right=0, ind_first=0, keep_next=False, shade=None, borders=None,
         style=None, tabs=None, contextual=False):
    """Assemble a w:p with the given paragraph properties."""
    # WordprocessingML requires pPr children in schema order:
    # pStyle, keepNext, keepLines, numPr, pBdr, shd, tabs, spacing, ind, jc.
    p = []
    if style:
        p.append('<w:pStyle w:val="%s"/>' % style)
    if keep_next:
        p.append("<w:keepNext/><w:keepLines/>")
    if borders:
        p.append(borders)
    if shade:
        p.append('<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % shade)
    if tabs:
        p.append(tabs)
    sp = '<w:spacing w:before="%d" w:after="%d"' % (before, after)
    if line:
        sp += ' w:line="%d" w:lineRule="auto"' % line
    sp += "/>"
    p.append(sp)
    if ind_left or ind_right or ind_first:
        if ind_first < 0:
            p.append('<w:ind w:left="%d" w:right="%d" w:hanging="%d"/>'
                     % (ind_left, ind_right, -ind_first))
        else:
            p.append('<w:ind w:left="%d" w:right="%d" w:firstLine="%d"/>'
                     % (ind_left, ind_right, ind_first))
    if contextual:
        p.append("<w:contextualSpacing/>")
    if align:
        p.append('<w:jc w:val="%s"/>' % align)
    pr = "<w:pPr>%s</w:pPr>" % "".join(p) if p else ""
    return "<w:p>%s%s</w:p>" % (pr, inner)


def bar(colour, size=8, space=0):
    return ('<w:pBdr><w:left w:val="single" w:sz="%d" w:space="%d" '
            'w:color="%s"/></w:pBdr>' % (size, space, hx(colour)))


def bottom_rule(colour, size=6):
    return ('<w:pBdr><w:bottom w:val="single" w:sz="%d" w:space="2" '
            'w:color="%s"/></w:pBdr>' % (size, hx(colour)))


def box_border(colour, size=6):
    return ('<w:pBdr>'
            '<w:top w:val="single" w:sz="%d" w:space="4" w:color="%s"/>'
            '<w:left w:val="single" w:sz="18" w:space="4" w:color="%s"/>'
            '<w:bottom w:val="single" w:sz="%d" w:space="4" w:color="%s"/>'
            '<w:right w:val="single" w:sz="%d" w:space="4" w:color="%s"/>'
            '</w:pBdr>' % (size, hx(colour), hx(colour), size, hx(colour),
                           size, hx(colour)))


def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def spacer(pts):
    return para('<w:r><w:rPr><w:sz w:val="%d"/></w:rPr><w:t></w:t></w:r>'
                % max(2, int(pts * 2)), after=0, before=0)


# ============================================================== the writer ====
class DocxWriter:
    def __init__(self, images, meta=None):
        self.images = images
        self.meta = meta or {}
        self.rels = []             # (id, target, type)
        self.media = {}            # filename -> bytes
        self.img_rel = {}          # logical name -> (rId, w_px, h_px)
        self.body = []
        self.fig_label = {}
        self.toc = []
        self.tables = []
        self.figures = []

    # ------------------------------------------------------------- images ----
    def _register(self, name):
        if name in self.img_rel:
            return self.img_rel[name]
        data = self.images[name]
        w, h = pdfdoc.png_dimensions(data)
        fn = "media/%s.png" % name
        rid = "rId%d" % (100 + len(self.img_rel))
        self.media[fn] = data
        self.rels.append((rid, fn,
                          "http://schemas.openxmlformats.org/officeDocument/"
                          "2006/relationships/image"))
        self.img_rel[name] = (rid, w, h)
        return self.img_rel[name]

    def drawing(self, name, width_pt, align="center"):
        rid, pw, ph = self._register(name)
        cx = int(width_pt * EMU_PER_PT)
        cy = int(width_pt * ph / pw * EMU_PER_PT)
        seq = len(self.img_rel)
        inner = (
            '<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" '
            'distR="0"><wp:extent cx="%d" cy="%d"/>'
            '<wp:docPr id="%d" name="Picture %d"/>'
            '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/'
            'drawingml/2006/picture"><pic:pic>'
            '<pic:nvPicPr><pic:cNvPr id="%d" name="%s.png"/><pic:cNvPicPr/>'
            '</pic:nvPicPr>'
            '<pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/>'
            '</a:stretch></pic:blipFill>'
            '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/>'
            '</a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            '</pic:spPr></pic:pic></a:graphicData></a:graphic>'
            '</wp:inline></w:drawing></w:r>'
            % (cx, cy, seq, seq, seq, name, rid, cx, cy))
        return para(inner, align=align, after=80, before=80)

    # ============================================================== render ====
    def render(self, blocks):
        import pdfwriter
        self.toc, self.tables, self.figures = pdfwriter.prescan(blocks)
        self.fig_label = {i: n for (n, _c, i) in self.figures}
        for idx, blk in enumerate(blocks):
            self._idx = idx
            fn = getattr(self, "_b_" + blk[0], None)
            if fn is None:
                raise ValueError("docx: unknown block " + blk[0])
            fn(*blk[1:])
        return self.package()

    def add(self, xml):
        self.body.append(xml)

    # ---------------------------------------------------------------- cover ----
    def _b_cover(self):
        a = self.add
        a(para(runs_xml(brand.COMPANY_BRAND.upper(), SANS, 40, brand.NAVY,
                        bold=True, spacing=90), align="center",
               before=240, after=60))
        a(para(runs_xml(brand.COMPANY_TAG, SANS, 17, brand.INK_SOFT),
               align="center", after=200))
        a(self.drawing("logo_mark", 190))
        a(para(runs_xml(brand.REPORT_TITLE, SANS, 30, brand.NAVY, bold=True,
                        spacing=60), align="center", before=160, after=60,
               borders=bottom_rule(brand.ORANGE, 12)))
        a(para(runs_xml("A STUDY ON", SANS, 17, brand.GREY, spacing=60),
               align="center", before=160, after=80))
        for ln in ["FINANCIAL MANAGEMENT PRACTICES, BUDGETARY CONTROL",
                   "AND FINANCIAL PERFORMANCE ANALYSIS"]:
            a(para(runs_xml(ln, SERIF, 33, brand.NAVY_MID, bold=True),
                   align="center", after=40))
        a(para(runs_xml("at", SERIF, 21, brand.GREY, italic=True),
               align="center", before=120, after=60))
        a(para(runs_xml(brand.COMPANY_LEGAL, SERIF, 25, brand.NAVY, bold=True),
               align="center", after=40))
        a(para(runs_xml(brand.COMPANY_ADDR1 + ", " + brand.COMPANY_ADDR2,
                        SERIF, 19, brand.INK_SOFT), align="center", after=200))
        a(para(runs_xml("Submitted in partial fulfilment of the requirements "
                        "for the award of the degree of", SERIF, 18,
                        brand.INK_SOFT, italic=True), align="center",
               after=60))
        a(para(runs_xml(brand.DEGREE.upper(), SANS, 24, brand.NAVY, bold=True,
                        spacing=30), align="center", after=40))
        a(para(runs_xml("Specialisation:  " + brand.COURSE, SERIF, 20,
                        brand.INK_SOFT), align="center", after=200))

        rows = [("Submitted by", brand.STUDENT_NAME.title()),
                ("Father's Name", "Shri " + brand.FATHER_NAME),
                ("Roll Number", brand.ROLL_NO),
                ("Registration Number", brand.REG_NO),
                ("Programme", brand.DEGREE_SHORT + "   |   " + brand.SEMESTER +
                 "   |   Session " + brand.SESSION)]
        a(self._plain_table(
            [(CONTENT_TW * 0.34, "l"), (CONTENT_TW * 0.66, "l")],
            [[(k, SANS, 16, brand.NAVY_MID, True),
              (v, SERIF, 20, brand.INK, True)] for (k, v) in rows],
            fill=hx(brand.BLUE_MIST), left_accent=hx(brand.ORANGE)))
        a(spacer(10))
        a(para(runs_xml(brand.UNIVERSITY_LN, SANS, 25, brand.NAVY, bold=True,
                        spacing=40), align="center", before=160, after=40))
        a(para(runs_xml("Department of Business Administration", SERIF, 19,
                        brand.INK_SOFT), align="center", after=100))
        a(para(runs_xml("Internship Period:  " + brand.INTERN_SPAN, SERIF, 19,
                        brand.ORANGE, italic=True), align="center", after=60))

    # ------------------------------------------------------------ structure ----
    def _b_pagebreak(self):
        self.add(page_break())

    def _b_spacer(self, pts):
        self.add(spacer(pts * 0.55))

    def _b_rule(self):
        self.add(para("", after=120, borders=bottom_rule(brand.GREY_LIGHT, 6)))

    def _b_chapter(self, number, title, standfirst):
        a = self.add
        a(self._banner(number, title))
        if standfirst:
            a(para(runs_xml(standfirst, SERIF, 21, brand.INK_SOFT,
                            italic=True), align="both", before=140, after=160,
                   line=280))

    def _banner(self, number, title):
        """Navy chapter banner rendered as a single-cell shaded table."""
        left = ""
        if number:
            left = (para(runs_xml("CHAPTER", SANS, 16, brand.BLUE_LIGHT,
                                  bold=True, spacing=60), after=20) +
                    para(runs_xml(number, SANS, 62, brand.ORANGE, bold=True),
                         after=0))
        else:
            left = para("", after=0)
        right = para(runs_xml(title, SANS, 38, brand.PAPER, bold=True),
                     after=0, before=60)
        w1 = int(CONTENT_TW * (0.18 if number else 0.02))
        w2 = CONTENT_TW - w1
        return (
            '<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/>'
            '<w:tblBorders>%s</w:tblBorders>'
            '<w:tblCellMar><w:top w:w="140" w:type="dxa"/>'
            '<w:left w:w="160" w:type="dxa"/>'
            '<w:bottom w:w="140" w:type="dxa"/>'
            '<w:right w:w="120" w:type="dxa"/></w:tblCellMar></w:tblPr>'
            '<w:tblGrid><w:gridCol w:w="%d"/><w:gridCol w:w="%d"/></w:tblGrid>'
            '<w:tr><w:trPr><w:cantSplit/></w:trPr>'
            '<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>'
            '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>'
            '<w:vAlign w:val="center"/></w:tcPr>%s</w:tc>'
            '<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>'
            '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>'
            '<w:vAlign w:val="center"/></w:tcPr>%s</w:tc>'
            '</w:tr></w:tbl>'
            % (CONTENT_TW, _no_borders(), w1, w2, w1, hx(brand.NAVY), left,
               w2, hx(brand.NAVY), right)
        ) + para("", after=0, before=0,
                 borders=bottom_rule(brand.ORANGE, 18))

    def _b_front(self, title, subtitle):
        a = self.add
        a(para(runs_xml(title, SANS, 33, brand.NAVY, bold=True, spacing=70),
               align="center", before=200, after=60,
               borders=bottom_rule(brand.ORANGE, 14)))
        if subtitle:
            a(para(runs_xml(subtitle, SERIF, 20, brand.INK_SOFT, italic=True),
                   align="center", before=100, after=200))
        else:
            a(spacer(8))

    def _b_front_sub(self, title):
        self.add(para(runs_xml(title, SANS, 26, brand.NAVY, bold=True,
                               spacing=50), align="center", before=260,
                      after=60, borders=bottom_rule(brand.ORANGE, 10)))

    # ------------------------------------------------------------- headings ----
    def _b_h2(self, text):
        self.add(para(runs_xml(text, SANS, 24, brand.NAVY, bold=True),
                      before=280, after=120, keep_next=True, ind_left=140,
                      borders=('<w:pBdr>'
                               '<w:left w:val="single" w:sz="18" w:space="6" '
                               'w:color="%s"/>'
                               '<w:bottom w:val="single" w:sz="4" w:space="3" '
                               'w:color="%s"/></w:pBdr>'
                               % (hx(brand.ORANGE), hx(brand.GREY_HAIR)))))

    def _b_h3(self, text):
        self.add(para(runs_xml(text, SANS, 21, brand.NAVY_MID, bold=True),
                      before=200, after=80, keep_next=True))

    # ---------------------------------------------------------------- text ----
    def _b_p(self, text):
        self.add(para(runs_xml(text, SERIF, 21, brand.INK), align="both",
                      after=130, line=264))

    def _b_lead(self, text):
        self.add(para(runs_xml(text, SERIF, 24, brand.NAVY_MID, italic=True),
                      after=180, before=120, line=288, ind_left=200,
                      borders=bar(brand.BLUE_LIGHT, 14, 8)))

    def _b_center(self, text):
        self.add(para(runs_xml(text, SERIF, 22, brand.NAVY), align="center",
                      after=160, before=80))

    def _b_small(self, text):
        self.add(para(runs_xml(text, SERIF, 18, brand.INK_SOFT, italic=True),
                      after=100))

    def _b_quote(self, text, attrib):
        self.add(para(runs_xml("\u201c" + text + "\u201d", SERIF, 24,
                               brand.NAVY, italic=True), after=60, before=140,
                      line=288, ind_left=420, ind_right=300,
                      borders=bar(brand.ORANGE, 18, 10)))
        if attrib:
            self.add(para(runs_xml("\u2014 " + attrib, SERIF, 19, brand.GREY),
                          after=160, ind_left=420))

    # --------------------------------------------------------------- lists ----
    def _b_bullets(self, items):
        for it in items:
            self.add(para(runs_xml(it, SERIF, 21, brand.INK), align="both",
                          after=90, line=264, ind_left=360, ind_first=-220,
                          style="ListBullet"))

    def _b_numbers(self, items):
        for i, it in enumerate(items):
            marker = runs_xml("%d." % (i + 1), SERIF, 21, brand.ORANGE,
                              bold=True)
            tabs = ('<w:tabs><w:tab w:val="left" w:pos="360"/></w:tabs>')
            inner = (marker + '<w:r><w:tab/></w:r>' +
                     runs_xml(it, SERIF, 21, brand.INK))
            self.add(para(inner, align="both", after=90, line=264,
                          ind_left=360, ind_first=-360, tabs=tabs))

    def _b_refs(self, items):
        for it in items:
            self.add(para(runs_xml(it, SERIF, 19, brand.INK), after=110,
                          line=250, ind_left=400, ind_first=-400))

    def _b_defs(self, items):
        for (term, body) in items:
            self.add(para(runs_xml(term, SANS, 19, brand.NAVY_MID, bold=True),
                          before=140, after=40, keep_next=True, ind_left=200,
                          borders=bar(brand.GREY_LIGHT, 8, 6)))
            self.add(para(runs_xml(body, SERIF, 21, brand.INK), align="both",
                          after=120, line=264, ind_left=200))

    # ------------------------------------------------------------- callout ----
    def _b_callout(self, kind, title, body):
        tint, accent = {
            "info": (brand.BLUE_MIST, brand.NAVY_MID),
            "note": (brand.ORANGE_PALE, brand.ORANGE),
            "warn": (brand.RED_PALE, brand.RED),
            "good": (brand.GREEN_PALE, brand.GREEN),
        }.get(kind, (brand.BLUE_MIST, brand.NAVY_MID))
        cells = [[(title, SANS, 20, accent, True)],
                 [(body, SERIF, 19, brand.INK, False)]]
        self.add(
            '<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/>'
            '<w:tblBorders>'
            '<w:top w:val="single" w:sz="4" w:space="0" w:color="%s"/>'
            '<w:left w:val="single" w:sz="24" w:space="0" w:color="%s"/>'
            '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="%s"/>'
            '<w:right w:val="single" w:sz="4" w:space="0" w:color="%s"/>'
            '</w:tblBorders>'
            '<w:tblCellMar><w:top w:w="120" w:type="dxa"/>'
            '<w:left w:w="180" w:type="dxa"/>'
            '<w:bottom w:w="120" w:type="dxa"/>'
            '<w:right w:w="160" w:type="dxa"/></w:tblCellMar></w:tblPr>'
            '<w:tblGrid><w:gridCol w:w="%d"/></w:tblGrid>'
            '<w:tr><w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>'
            '<w:shd w:val="clear" w:color="auto" w:fill="%s"/></w:tcPr>'
            '%s%s</w:tc></w:tr></w:tbl>'
            % (CONTENT_TW, hx(tint), hx(accent), hx(tint), hx(tint),
               CONTENT_TW, CONTENT_TW, hx(tint),
               para(runs_xml(title, SANS, 20, accent, bold=True), after=60),
               para(runs_xml(body, SERIF, 19, brand.INK), align="both",
                    after=0, line=250)))
        self.add(spacer(6))

    # ------------------------------------------------------------------ kpi ----
    def _b_kpi(self, items):
        n = len(items)
        w = CONTENT_TW // n
        tcs = []
        for i, (value, label, note) in enumerate(items):
            inner = (para(runs_xml(value, SANS, 30, brand.NAVY, bold=True),
                          align="center", after=40, before=60) +
                     para(runs_xml(label, SANS, 15, brand.INK_SOFT, bold=True),
                          align="center", after=30) +
                     para(runs_xml(note, SERIF, 14, brand.GREY, italic=True),
                          align="center", after=60))
            tcs.append(
                '<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>'
                '<w:tcBorders><w:top w:val="single" w:sz="24" w:space="0" '
                'w:color="%s"/></w:tcBorders>'
                '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>'
                '</w:tcPr>%s</w:tc>'
                % (w, hx(brand.SERIES[i % len(brand.SERIES)]),
                   hx(brand.BLUE_MIST), inner))
        self.add('<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/>'
                 '<w:tblBorders>%s</w:tblBorders>'
                 '<w:tblCellMar><w:left w:w="80" w:type="dxa"/>'
                 '<w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr>'
                 '<w:tblGrid>%s</w:tblGrid><w:tr>%s</w:tr></w:tbl>'
                 % (CONTENT_TW, _no_borders(),
                    "".join('<w:gridCol w:w="%d"/>' % w for _ in items),
                    "".join(tcs)))
        self.add(spacer(8))

    # ------------------------------------------------------------ signature ----
    def _b_signatures(self, items):
        n = len(items)
        w = CONTENT_TW // n
        tcs = []
        for (role, name) in items:
            inner = para("", after=0,
                         borders=bottom_rule(brand.INK_SOFT, 6))
            if role:
                inner += para(runs_xml(role, SANS, 17, brand.NAVY, bold=True),
                              align="center", after=20, before=60)
            if name:
                inner += para(runs_xml(name, SERIF, 17, brand.INK_SOFT),
                              align="center", after=40)
            tcs.append('<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/></w:tcPr>'
                       '%s</w:tc>' % (w, inner))
        self.add(spacer(16))
        self.add('<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/>'
                 '<w:tblBorders>%s</w:tblBorders>'
                 '<w:tblCellMar><w:left w:w="200" w:type="dxa"/>'
                 '<w:right w:w="200" w:type="dxa"/></w:tblCellMar></w:tblPr>'
                 '<w:tblGrid>%s</w:tblGrid><w:tr>%s</w:tr></w:tbl>'
                 % (CONTENT_TW, _no_borders(),
                    "".join('<w:gridCol w:w="%d"/>' % w for _ in items),
                    "".join(tcs)))
        self.add(spacer(10))

    # --------------------------------------------------------------- figures ----
    def _b_figure_inline(self, key, frac):
        self.add(self.drawing(key, 470 * frac))

    def _b_figure(self, key, caption, source):
        label = self.fig_label.get(self._idx, "Figure")
        self.add(self.drawing(key, 418))
        inner = (runs_xml(label + "  ", SANS, 18, brand.ORANGE, bold=True) +
                 runs_xml(caption, SANS, 18, brand.INK_SOFT))
        self.add(para(inner, align="center", after=40, before=20))
        if source:
            self.add(para(runs_xml(source, SERIF, 16, brand.GREY, italic=True),
                          align="center", after=180))
        else:
            self.add(spacer(8))

    # ---------------------------------------------------------------- tables ----
    def _b_table(self, spec):
        cols = spec["cols"]
        fs = int(round(18 * spec.get("font_scale", 1.0)))
        widths = [int(CONTENT_TW * c[1]) for c in cols]
        widths[-1] = CONTENT_TW - sum(widths[:-1])
        ncol = len(cols)

        cap = ("Table " + str(spec["number"])) if spec.get("number") else ""
        inner = (runs_xml(cap + "  ", SANS, 19, brand.ORANGE, bold=True) +
                 runs_xml(spec.get("title") or "", SANS, 19, brand.NAVY,
                          bold=True))
        self.add(para(inner, before=220, after=60, keep_next=True))

        align_map = {"l": "left", "c": "center", "r": "right"}
        rows_xml = []
        # header row, repeated on every page Word breaks the table across
        hcells = []
        for i, c in enumerate(cols):
            hcells.append(
                '<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>'
                '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>'
                '<w:vAlign w:val="center"/></w:tcPr>%s</w:tc>'
                % (widths[i], hx(brand.NAVY),
                   para(runs_xml(c[0], SANS, fs, brand.PAPER, bold=True),
                        align=align_map[c[2]], after=0, before=0)))
        rows_xml.append('<w:tr><w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>'
                        '%s</w:tr>' % "".join(hcells))

        band = 0
        for (cells, style) in spec["rows"]:
            cells = list(cells) + [""] * (ncol - len(cells))
            emph = style in ("total", "group")
            if style == "group":
                fill = hx(brand.NAVY_MID)
                colr = brand.PAPER
            elif style == "total":
                fill = hx(brand.BLUE_PALE)
                colr = brand.NAVY
            else:
                fill = hx(brand.PAPER_WARM) if band % 2 == 1 else "FFFFFF"
                colr = brand.INK
            face = SANS if emph else SERIF
            tcs = []
            for i, c in enumerate(cols):
                tcs.append(
                    '<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>'
                    '<w:tcBorders><w:bottom w:val="single" w:sz="2" '
                    'w:space="0" w:color="%s"/></w:tcBorders>'
                    '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>'
                    '</w:tcPr>%s</w:tc>'
                    % (widths[i], hx(brand.GREY_HAIR), fill,
                       para(runs_xml(cells[i], face, fs, colr, bold=emph),
                            align=align_map[c[2]], after=0, before=0,
                            line=250)))
            rows_xml.append('<w:tr><w:trPr><w:cantSplit/></w:trPr>%s</w:tr>'
                            % "".join(tcs))
            band += 1

        self.add(
            '<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/>'
            '<w:tblBorders>'
            '<w:top w:val="single" w:sz="8" w:space="0" w:color="%s"/>'
            '<w:bottom w:val="single" w:sz="8" w:space="0" w:color="%s"/>'
            '</w:tblBorders>'
            '<w:tblLayout w:type="fixed"/>'
            '<w:tblCellMar><w:top w:w="70" w:type="dxa"/>'
            '<w:left w:w="100" w:type="dxa"/>'
            '<w:bottom w:w="70" w:type="dxa"/>'
            '<w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr>'
            '<w:tblGrid>%s</w:tblGrid>%s</w:tbl>'
            % (CONTENT_TW, hx(brand.NAVY), hx(brand.NAVY),
               "".join('<w:gridCol w:w="%d"/>' % w for w in widths),
               "".join(rows_xml)))

        if spec.get("note"):
            inner = (runs_xml("Note:  ", SANS, 16, brand.GREY, bold=True) +
                     runs_xml(spec["note"], SERIF, 16, brand.GREY))
            self.add(para(inner, after=180, before=60, line=230))
        else:
            self.add(spacer(8))

    # ------------------------------------------ contents and list of items ----
    def _toc_field(self, levels):
        """A real Word TOC field, which Word fills in when the file opens."""
        return (
            '<w:p><w:pPr><w:spacing w:after="120"/></w:pPr>'
            '<w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
            '<w:r><w:instrText xml:space="preserve"> TOC \\o "1-%d" \\h \\z '
            '\\u </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>' % levels)

    def _toc_end(self):
        return ('<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>')

    def _dotted(self, level, text, style_hint=0):
        face = SANS if level == 0 else SERIF
        size = 20 if level == 0 else 19
        col = brand.NAVY if level == 0 else brand.INK
        tabs = ('<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="%d"/>'
                '</w:tabs>' % CONTENT_TW)
        inner = (runs_xml(text, face, size, col, bold=(level == 0)) +
                 '<w:r><w:tab/></w:r>' +
                 self._page_ref_placeholder())
        return para(inner, after=(60 if level == 0 else 30),
                    before=(80 if level == 0 else 0),
                    ind_left=(0 if level == 0 else 280), tabs=tabs)

    def _page_ref_placeholder(self):
        # Word recalculates the real numbers through the TOC field above; this
        # keeps the static fallback visually complete.
        return runs_xml("\u2013", SERIF, 18, brand.GREY_LIGHT)

    def _b_toc(self):
        self.add(self._toc_field(2))
        for (level, text, _idx) in self.toc:
            self.add(self._dotted(level, text))
        self.add(self._toc_end())
        self.add(para(runs_xml("Page numbers are inserted by Word: open the "
                               "document, select the contents above, then "
                               "press F9 (or right-click and choose Update "
                               "Field) to populate them.", SERIF, 16,
                               brand.GREY, italic=True), before=160,
                      after=60))

    def _b_lot(self):
        for (num, title, _idx) in self.tables:
            self.add(self._dotted(1, num + "   " + title))

    def _b_lof(self):
        for (num, caption, _idx) in self.figures:
            self.add(self._dotted(1, num + "   " + caption))

    # ------------------------------------------------------- helper tables ----
    def _plain_table(self, colspec, rows, fill=None, left_accent=None):
        widths = [int(w) for (w, _a) in colspec]
        widths[-1] = CONTENT_TW - sum(widths[:-1])
        align_map = {"l": "left", "c": "center", "r": "right"}
        out = []
        for r in rows:
            tcs = []
            for i, cell in enumerate(r):
                txt, face, size, colour, bold = cell
                borders = ""
                if left_accent and i == 0:
                    borders = ('<w:tcBorders><w:left w:val="single" w:sz="24" '
                               'w:space="0" w:color="%s"/></w:tcBorders>'
                               % left_accent)
                tcs.append(
                    '<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s%s'
                    '</w:tcPr>%s</w:tc>'
                    % (widths[i], borders,
                       ('<w:shd w:val="clear" w:color="auto" w:fill="%s"/>'
                        % fill) if fill else "",
                       para(runs_xml(txt, face, size, colour, bold=bold),
                            align=align_map[colspec[i][1]], after=30,
                            before=30)))
            out.append('<w:tr>%s</w:tr>' % "".join(tcs))
        return ('<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/>'
                '<w:tblBorders>%s</w:tblBorders>'
                '<w:tblCellMar><w:left w:w="200" w:type="dxa"/>'
                '<w:right w:w="160" w:type="dxa"/></w:tblCellMar></w:tblPr>'
                '<w:tblGrid>%s</w:tblGrid>%s</w:tbl>'
                % (CONTENT_TW, _no_borders(),
                   "".join('<w:gridCol w:w="%d"/>' % w for w in widths),
                   "".join(out)))

    # ============================================================= package ====
    def package(self):
        doc_xml = self._document_xml()
        parts = {
            "[Content_Types].xml": _content_types(self.media),
            "_rels/.rels": _root_rels(),
            "docProps/core.xml": _core_props(self.meta),
            "docProps/app.xml": _app_props(self.meta),
            "word/document.xml": doc_xml,
            "word/styles.xml": _styles_xml(),
            "word/numbering.xml": _numbering_xml(),
            "word/settings.xml": _settings_xml(),
            "word/header1.xml": _header_xml(),
            "word/footer1.xml": _footer_xml(),
            "word/_rels/document.xml.rels": self._doc_rels(),
        }
        import io
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for name, data in parts.items():
                z.writestr(name, data if isinstance(data, bytes)
                           else data.encode("utf-8"))
            for fn, data in self.media.items():
                z.writestr("word/" + fn, data)
        return buf.getvalue()

    def _doc_rels(self):
        base = [
            ("rId1", "styles.xml", "styles"),
            ("rId2", "numbering.xml", "numbering"),
            ("rId3", "settings.xml", "settings"),
            ("rId4", "header1.xml", "header"),
            ("rId5", "footer1.xml", "footer"),
        ]
        out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
               '<Relationships xmlns="http://schemas.openxmlformats.org/'
               'package/2006/relationships">']
        for (rid, target, kind) in base:
            out.append('<Relationship Id="%s" Type="http://schemas.'
                       'openxmlformats.org/officeDocument/2006/relationships/'
                       '%s" Target="%s"/>' % (rid, kind, target))
        for (rid, target, typ) in self.rels:
            out.append('<Relationship Id="%s" Type="%s" Target="%s"/>'
                       % (rid, typ, target))
        out.append("</Relationships>")
        return "".join(out)

    def _document_xml(self):
        sect = (
            '<w:sectPr>'
            '<w:headerReference r:id="rId4"/>'
            '<w:footerReference r:id="rId5"/>'
            '<w:pgSz w:w="%d" w:h="%d"/>'
            '<w:pgMar w:top="%d" w:right="%d" w:bottom="%d" w:left="%d" '
            'w:header="%d" w:footer="%d" w:gutter="0"/>'
            '<w:cols w:space="708"/><w:docGrid w:linePitch="360"/>'
            '</w:sectPr>' % (PAGE_W_TW, PAGE_H_TW, MARG_T, MARG_R, MARG_B,
                             MARG_L, HEADER_D, FOOTER_D))
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<w:document %s><w:body>%s%s</w:body></w:document>'
                % (NS, "".join(self.body), sect))


def _no_borders():
    return ('<w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
            '<w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
            '<w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
            '<w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
            '<w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
            '<w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>')


# --------------------------------------------------------------- static parts ----
def _content_types(media):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/'
            'content-types">'
            '<Default Extension="rels" ContentType="application/'
            'vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Default Extension="png" ContentType="image/png"/>'
            '<Override PartName="/word/document.xml" ContentType="application/'
            'vnd.openxmlformats-officedocument.wordprocessingml.document.'
            'main+xml"/>'
            '<Override PartName="/word/styles.xml" ContentType="application/'
            'vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
            '<Override PartName="/word/numbering.xml" ContentType="application/'
            'vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
            '<Override PartName="/word/settings.xml" ContentType="application/'
            'vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
            '<Override PartName="/word/header1.xml" ContentType="application/'
            'vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>'
            '<Override PartName="/word/footer1.xml" ContentType="application/'
            'vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
            '<Override PartName="/docProps/core.xml" ContentType="application/'
            'vnd.openxmlformats-package.core-properties+xml"/>'
            '<Override PartName="/docProps/app.xml" ContentType="application/'
            'vnd.openxmlformats-officedocument.extended-properties+xml"/>'
            '</Types>')


def _root_rels():
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/'
            '2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships/officeDocument" '
            'Target="word/document.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/'
            'package/2006/relationships/metadata/core-properties" '
            'Target="docProps/core.xml"/>'
            '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships/extended-properties" '
            'Target="docProps/app.xml"/>'
            '</Relationships>')


def _core_props(meta):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<cp:coreProperties '
            'xmlns:cp="http://schemas.openxmlformats.org/package/2006/'
            'metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" '
            'xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            '<dc:title>%s</dc:title><dc:creator>%s</dc:creator>'
            '<dc:subject>%s</dc:subject>'
            '<cp:lastModifiedBy>%s</cp:lastModifiedBy>'
            '</cp:coreProperties>'
            % (esc(meta.get("title", "")), esc(meta.get("author", "")),
               esc(meta.get("subject", "")), esc(meta.get("author", ""))))


def _app_props(meta):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Properties xmlns="http://schemas.openxmlformats.org/'
            'officeDocument/2006/extended-properties" '
            'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/'
            'docPropsVTypes"><Application>Infinity Interns Report Engine'
            '</Application><Company>%s</Company></Properties>'
            % esc(brand.COMPANY_LEGAL))


def _settings_xml():
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:settings %s>'
            '<w:zoom w:percent="100"/>'
            '<w:defaultTabStop w:val="720"/>'
            '<w:characterSpacingControl w:val="doNotCompress"/>'
            '<w:updateFields w:val="true"/>'
            '<w:compat><w:compatSetting w:name="compatibilityMode" '
            'w:uri="http://schemas.microsoft.com/office/word" w:val="15"/>'
            '</w:compat></w:settings>' % NS)


def _numbering_xml():
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:numbering %s>'
            '<w:abstractNum w:abstractNumId="1">'
            '<w:multiLevelType w:val="singleLevel"/>'
            '<w:lvl w:ilvl="0"><w:start w:val="1"/>'
            '<w:numFmt w:val="bullet"/><w:lvlText w:val="\u2022"/>'
            '<w:lvlJc w:val="left"/>'
            '<w:pPr><w:ind w:left="360" w:hanging="220"/></w:pPr>'
            '<w:rPr><w:rFonts w:ascii="%s" w:hAnsi="%s"/>'
            '<w:color w:val="%s"/></w:rPr></w:lvl></w:abstractNum>'
            '<w:num w:numId="1"><w:abstractNumId w:val="1"/></w:num>'
            '</w:numbering>' % (NS, SANS, SANS, hx(brand.ORANGE)))


def _styles_xml():
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:styles %s>'
            '<w:docDefaults><w:rPrDefault><w:rPr>'
            '<w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="%s"/>'
            '<w:sz w:val="21"/><w:szCs w:val="21"/>'
            '<w:lang w:val="en-IN"/></w:rPr></w:rPrDefault>'
            '<w:pPrDefault><w:pPr>'
            '<w:spacing w:after="130" w:line="264" w:lineRule="auto"/>'
            '</w:pPr></w:pPrDefault></w:docDefaults>'
            '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
            '<w:name w:val="Normal"/><w:qFormat/></w:style>'
            '<w:style w:type="paragraph" w:styleId="ListBullet">'
            '<w:name w:val="List Bullet"/><w:basedOn w:val="Normal"/>'
            '<w:pPr><w:numPr><w:numId w:val="1"/></w:numPr></w:pPr>'
            '</w:style>'
            '<w:style w:type="paragraph" w:styleId="Heading1">'
            '<w:name w:val="heading 1"/><w:basedOn w:val="Normal"/>'
            '<w:next w:val="Normal"/><w:qFormat/>'
            '<w:pPr><w:outlineLvl w:val="0"/><w:keepNext/>'
            '<w:spacing w:before="280" w:after="120"/></w:pPr>'
            '<w:rPr><w:rFonts w:ascii="%s" w:hAnsi="%s"/><w:b/>'
            '<w:color w:val="%s"/><w:sz w:val="30"/></w:rPr></w:style>'
            '<w:style w:type="paragraph" w:styleId="Heading2">'
            '<w:name w:val="heading 2"/><w:basedOn w:val="Normal"/>'
            '<w:next w:val="Normal"/><w:qFormat/>'
            '<w:pPr><w:outlineLvl w:val="1"/><w:keepNext/>'
            '<w:spacing w:before="240" w:after="100"/></w:pPr>'
            '<w:rPr><w:rFonts w:ascii="%s" w:hAnsi="%s"/><w:b/>'
            '<w:color w:val="%s"/><w:sz w:val="24"/></w:rPr></w:style>'
            '<w:style w:type="paragraph" w:styleId="TOC1">'
            '<w:name w:val="toc 1"/><w:basedOn w:val="Normal"/></w:style>'
            '<w:style w:type="paragraph" w:styleId="TOC2">'
            '<w:name w:val="toc 2"/><w:basedOn w:val="Normal"/>'
            '<w:pPr><w:ind w:left="280"/></w:pPr></w:style>'
            '<w:style w:type="character" w:styleId="Hyperlink">'
            '<w:name w:val="Hyperlink"/>'
            '<w:rPr><w:color w:val="%s"/></w:rPr></w:style>'
            '</w:styles>'
            % (NS, SERIF, SERIF, SERIF, SANS, SANS, hx(brand.NAVY),
               SANS, SANS, hx(brand.NAVY), hx(brand.NAVY_MID)))


def _header_xml():
    tabs = ('<w:tabs><w:tab w:val="right" w:pos="%d"/></w:tabs>' % CONTENT_TW)
    inner = (runs_xml("SUMMER INTERNSHIP PROJECT REPORT", SANS, 13,
                      brand.NAVY, bold=True, spacing=24) +
             '<w:r><w:tab/></w:r>' +
             runs_xml(brand.COMPANY_BRAND + ", Patna", SANS, 13, brand.GREY,
                      spacing=20))
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:hdr %s>%s</w:hdr>'
            % (NS, para(inner, after=0, tabs=tabs,
                        borders=bottom_rule(brand.ORANGE, 8))))


def _footer_xml():
    tabs = ('<w:tabs><w:tab w:val="center" w:pos="%d"/>'
            '<w:tab w:val="right" w:pos="%d"/></w:tabs>'
            % (CONTENT_TW // 2, CONTENT_TW))
    page_field = (
        '<w:r><w:rPr><w:rFonts w:ascii="%s" w:hAnsi="%s"/><w:b/>'
        '<w:color w:val="%s"/><w:sz w:val="16"/></w:rPr>'
        '<w:fldChar w:fldCharType="begin"/></w:r>'
        '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="end"/></w:r>' % (SANS, SANS,
                                                        hx(brand.NAVY)))
    inner = (runs_xml(brand.STUDENT_NAME.title() + "  |  Roll No. " +
                      brand.ROLL_NO, SERIF, 15, brand.GREY, italic=True) +
             '<w:r><w:tab/></w:r>' + page_field +
             '<w:r><w:tab/></w:r>' +
             runs_xml(brand.UNIVERSITY, SERIF, 15, brand.GREY, italic=True))
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:ftr %s>%s</w:ftr>'
            % (NS, para(inner, after=0, tabs=tabs,
                        borders=('<w:pBdr><w:top w:val="single" w:sz="4" '
                                 'w:space="4" w:color="%s"/></w:pBdr>'
                                 % hx(brand.GREY_HAIR)))))


def build_docx(blocks, images, meta=None):
    return DocxWriter(images, meta).render(blocks)
