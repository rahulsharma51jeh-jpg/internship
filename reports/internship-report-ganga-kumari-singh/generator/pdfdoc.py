"""
A minimal PDF 1.4 writer: object table, page tree, image XObjects, a Type3 font
for the rupee sign, document outline and a per-page drawing surface.

Layout decisions live in pdfwriter; this module only knows how to turn drawing
calls into a valid PDF file.
"""

import zlib

import afm
import brand

PT = 1.0
MM = 72.0 / 25.4
A4 = (595.276, 841.890)


def _num(v):
    """Compact fixed-point formatting for PDF operands."""
    if v == int(v):
        return str(int(v))
    return ("%.3f" % v).rstrip("0").rstrip(".")


class Surface:
    """Accumulates PDF content-stream operators for one page."""

    def __init__(self, doc, width, height):
        self.doc = doc
        self.w = width
        self.h = height
        self.ops = []
        self._fill = None
        self._stroke = None
        self._lw = None

    # -------------------------------------------------------- coordinates ----
    def _y(self, y):
        """Convert top-left origin (layout space) to PDF bottom-left."""
        return self.h - y

    # -------------------------------------------------------------- state ----
    def set_fill(self, rgb):
        if rgb != self._fill:
            r, g, b = brand.unit(rgb)
            self.ops.append("%s %s %s rg" % (_num(r), _num(g), _num(b)))
            self._fill = rgb

    def set_stroke(self, rgb):
        if rgb != self._stroke:
            r, g, b = brand.unit(rgb)
            self.ops.append("%s %s %s RG" % (_num(r), _num(g), _num(b)))
            self._stroke = rgb

    def set_width(self, w):
        if w != self._lw:
            self.ops.append("%s w" % _num(w))
            self._lw = w

    # ------------------------------------------------------------- shapes ----
    def rect(self, x, y, w, h, rgb):
        if w <= 0 or h <= 0:
            return
        self.set_fill(rgb)
        self.ops.append("%s %s %s %s re f" %
                        (_num(x), _num(self._y(y + h)), _num(w), _num(h)))

    def round_rect(self, x, y, w, h, r, rgb):
        if w <= 0 or h <= 0:
            return
        r = min(r, w / 2.0, h / 2.0)
        k = r * 0.5523
        y0 = self._y(y + h)
        y1 = self._y(y)
        self.set_fill(rgb)
        o = ["%s %s m" % (_num(x + r), _num(y0))]
        o.append("%s %s l" % (_num(x + w - r), _num(y0)))
        o.append("%s %s %s %s %s %s c" % (_num(x + w - r + k), _num(y0),
                                          _num(x + w), _num(y0 + r - k),
                                          _num(x + w), _num(y0 + r)))
        o.append("%s %s l" % (_num(x + w), _num(y1 - r)))
        o.append("%s %s %s %s %s %s c" % (_num(x + w), _num(y1 - r + k),
                                          _num(x + w - r + k), _num(y1),
                                          _num(x + w - r), _num(y1)))
        o.append("%s %s l" % (_num(x + r), _num(y1)))
        o.append("%s %s %s %s %s %s c" % (_num(x + r - k), _num(y1),
                                          _num(x), _num(y1 - r + k),
                                          _num(x), _num(y1 - r)))
        o.append("%s %s l" % (_num(x), _num(y0 + r)))
        o.append("%s %s %s %s %s %s c" % (_num(x), _num(y0 + r - k),
                                          _num(x + r - k), _num(y0),
                                          _num(x + r), _num(y0)))
        o.append("f")
        self.ops.append(" ".join(o))

    def line(self, x0, y0, x1, y1, rgb, width=0.6):
        self.set_stroke(rgb)
        self.set_width(width)
        self.ops.append("%s %s m %s %s l S" %
                        (_num(x0), _num(self._y(y0)),
                         _num(x1), _num(self._y(y1))))

    def hline(self, x0, x1, y, rgb, width=0.6):
        self.line(x0, y, x1, y, rgb, width)

    def circle(self, cx, cy, r, rgb):
        k = r * 0.5523
        cy = self._y(cy)
        self.set_fill(rgb)
        self.ops.append(
            "%s %s m %s %s %s %s %s %s c %s %s %s %s %s %s c "
            "%s %s %s %s %s %s c %s %s %s %s %s %s c f" % (
                _num(cx + r), _num(cy),
                _num(cx + r), _num(cy + k), _num(cx + k), _num(cy + r),
                _num(cx), _num(cy + r),
                _num(cx - k), _num(cy + r), _num(cx - r), _num(cy + k),
                _num(cx - r), _num(cy),
                _num(cx - r), _num(cy - k), _num(cx - k), _num(cy - r),
                _num(cx), _num(cy - r),
                _num(cx + k), _num(cy - r), _num(cx + r), _num(cy - k),
                _num(cx + r), _num(cy)))

    def polygon(self, pts, rgb):
        if len(pts) < 3:
            return
        self.set_fill(rgb)
        o = ["%s %s m" % (_num(pts[0][0]), _num(self._y(pts[0][1])))]
        for (px, py) in pts[1:]:
            o.append("%s %s l" % (_num(px), _num(self._y(py))))
        o.append("h f")
        self.ops.append(" ".join(o))

    # -------------------------------------------------------------- images ----
    def image(self, name, x, y, w, h):
        self.ops.append("q %s 0 0 %s %s %s cm /%s Do Q" %
                        (_num(w), _num(h), _num(x), _num(self._y(y + h)),
                         name))

    # ---------------------------------------------------------------- text ----
    def text(self, x, y, segments, rgb=None, char_space=0.0):
        """
        Draw text at baseline y.

        `segments` is a list of (face, size, string). A face of 'rupee' selects
        the Type3 rupee font, whose glyph is addressed by the single byte 'R'.
        """
        if not segments:
            return
        if rgb is not None:
            self.set_fill(rgb)
        o = ["BT"]
        if char_space:
            o.append("%s Tc" % _num(char_space))
        o.append("1 0 0 1 %s %s Tm" % (_num(x), _num(self._y(y))))
        for (face, size, s) in segments:
            if not s:
                continue
            if face == "rupee":
                res = self.doc.rupee_font_name()
                o.append("/%s %s Tf" % (res, _num(size)))
                o.append("(R) Tj")
            else:
                res = self.doc.font_name(face)
                o.append("/%s %s Tf" % (res, _num(size)))
                o.append("(%s) Tj" % afm.encode(s).decode("latin-1"))
        if char_space:
            o.append("0 Tc")
        o.append("ET")
        self.ops.append(" ".join(o))

    def simple_text(self, x, y, s, face, size, rgb, char_space=0.0):
        self.text(x, y, [(face, size, s)], rgb, char_space)

    # -------------------------------------------------------------- output ----
    def stream(self):
        return ("\n".join(self.ops)).encode("latin-1")


class Document:
    def __init__(self, page_size=A4, title="", author="", subject=""):
        self.page_w, self.page_h = page_size
        self.objects = [None]          # 1-based; index 0 unused
        self.pages = []                # list of Surface
        self.images = {}               # logical name -> (res_name, ref)
        self._img_seq = 0
        self._fonts = {}               # face -> resource name
        self._font_refs = {}
        self._rupee = None
        self.outline = []              # (title, page_index, level)
        self.title = title
        self.author = author
        self.subject = subject

    # ------------------------------------------------------------ objects ----
    def _add(self, body):
        self.objects.append(body)
        return len(self.objects) - 1

    def _add_stream(self, extra, data, compress=True):
        if compress:
            data = zlib.compress(data, 9)
            extra = dict(extra)
            extra["Filter"] = "/FlateDecode"
        parts = " ".join("/%s %s" % (k, v) for k, v in extra.items())
        obj = ("<< %s /Length %d >>\nstream\n" % (parts, len(data))).encode(
            "latin-1") + data + b"\nendstream"
        return self._add(obj)

    # -------------------------------------------------------------- pages ----
    def new_page(self):
        s = Surface(self, self.page_w, self.page_h)
        self.pages.append(s)
        return s

    # -------------------------------------------------------------- fonts ----
    def font_name(self, face):
        if face not in self._fonts:
            self._fonts[face] = "F%d" % (len(self._fonts) + 1)
        return self._fonts[face]

    def rupee_font_name(self):
        if self._rupee is None:
            self._rupee = "FR"
        return self._rupee

    def _rupee_charproc(self):
        """
        Build the rupee glyph as a Type3 CharProc.

        The outline is taken from the stroke font used for the charts, scaled
        from its 14-unit cap height to the 1000-unit glyph space of a Type3
        font, so the rupee sign in the PDF matches the one in the exhibits.
        """
        import strokefont as sf

        scale = 662.0 / sf.CAP          # match the Times cap height
        polys = sf._FLAT[afm.RUPEE][1]
        ops = ["%d 0 d0" % afm.RUPEE_WIDTH, "62 w 1 J 1 j"]
        for poly in polys:
            pts = [(px * scale, py * scale) for (px, py) in poly]
            ops.append("%s %s m" % (_num(pts[0][0]), _num(pts[0][1])))
            for (px, py) in pts[1:]:
                ops.append("%s %s l" % (_num(px), _num(py)))
            ops.append("S")
        return "\n".join(ops).encode("latin-1")

    # ------------------------------------------------------------- images ----
    def add_image(self, name, png_bytes):
        """Register a PNG. Returns the page resource name."""
        if name in self.images:
            return self.images[name][0]
        img = decode_png(png_bytes)
        self._img_seq += 1
        res = "Im%d" % self._img_seq
        if img["kind"] == "indexed":
            pal = "".join("%02X%02X%02X" % c for c in img["palette"])
            cs = "[/Indexed /DeviceRGB %d <%s>]" % (len(img["palette"]) - 1,
                                                    pal)
        else:
            cs = "/DeviceRGB"
        ref = self._add_stream({
            "Type": "/XObject", "Subtype": "/Image",
            "Width": img["w"], "Height": img["h"],
            "ColorSpace": cs, "BitsPerComponent": 8,
        }, img["data"])
        self.images[name] = (res, ref)
        return res

    # ------------------------------------------------------------- output ----
    def build(self):
        font_refs = {}
        for face in self._fonts:
            font_refs[face] = self._add(
                ("<< /Type /Font /Subtype /Type1 /BaseFont /%s "
                 "/Encoding /WinAnsiEncoding >>" % face).encode("latin-1"))
        rupee_ref = None
        if self._rupee:
            proc = self._add_stream({}, self._rupee_charproc())
            rupee_ref = self._add((
                "<< /Type /Font /Subtype /Type3 "
                "/FontBBox [0 -20 %d 700] "
                "/FontMatrix [0.001 0 0 0.001 0 0] "
                "/CharProcs << /rupee %d 0 R >> "
                "/Encoding << /Type /Encoding /Differences [82 /rupee] >> "
                "/FirstChar 82 /LastChar 82 /Widths [%d] "
                "/Resources << >> >>" %
                (afm.RUPEE_WIDTH, proc, afm.RUPEE_WIDTH)).encode("latin-1"))

        res_parts = []
        if font_refs or rupee_ref:
            fonts = " ".join("/%s %d 0 R" % (self._fonts[f], font_refs[f])
                             for f in self._fonts)
            if rupee_ref:
                fonts += " /%s %d 0 R" % (self._rupee, rupee_ref)
            res_parts.append("/Font << %s >>" % fonts)
        if self.images:
            xo = " ".join("/%s %d 0 R" % (r, ref)
                          for (r, ref) in self.images.values())
            res_parts.append("/XObject << %s >>" % xo)
        resources = self._add(("<< %s >>" % " ".join(res_parts)).encode(
            "latin-1"))

        pages_ref = len(self.objects)          # reserved below
        self.objects.append(None)

        page_refs = []
        for surf in self.pages:
            content = self._add_stream({}, surf.stream())
            page_refs.append(self._add((
                "<< /Type /Page /Parent %d 0 R "
                "/MediaBox [0 0 %s %s] /Resources %d 0 R /Contents %d 0 R >>"
                % (pages_ref, _num(self.page_w), _num(self.page_h),
                   resources, content)).encode("latin-1")))

        self.objects[pages_ref] = (
            "<< /Type /Pages /Count %d /Kids [%s] >>" %
            (len(page_refs), " ".join("%d 0 R" % r for r in page_refs))
        ).encode("latin-1")

        # ------------------------------------------------------- outline ----
        outlines_ref = None
        if self.outline:
            outlines_ref = len(self.objects)
            self.objects.append(None)
            items = []
            for _t, _p, _l in self.outline:
                items.append(len(self.objects))
                self.objects.append(None)
            for i, (t, pidx, _lvl) in enumerate(self.outline):
                parts = ["/Title (%s)" % afm.encode(t).decode("latin-1"),
                         "/Parent %d 0 R" % outlines_ref,
                         "/Dest [%d 0 R /XYZ 0 %s 0]" %
                         (page_refs[min(pidx, len(page_refs) - 1)],
                          _num(self.page_h))]
                if i > 0:
                    parts.append("/Prev %d 0 R" % items[i - 1])
                if i < len(items) - 1:
                    parts.append("/Next %d 0 R" % items[i + 1])
                self.objects[items[i]] = ("<< %s >>" % " ".join(
                    parts)).encode("latin-1")
            self.objects[outlines_ref] = (
                "<< /Type /Outlines /Count %d /First %d 0 R /Last %d 0 R >>"
                % (len(items), items[0], items[-1])).encode("latin-1")

        info = self._add((
            "<< /Title (%s) /Author (%s) /Subject (%s) /Creator (%s) "
            "/Producer (%s) >>" % (
                afm.encode(self.title).decode("latin-1"),
                afm.encode(self.author).decode("latin-1"),
                afm.encode(self.subject).decode("latin-1"),
                afm.encode("Infinity Interns Report Engine").decode("latin-1"),
                afm.encode("Pure-Python PDF writer").decode("latin-1"),
            )).encode("latin-1"))

        cat_parts = ["/Type /Catalog", "/Pages %d 0 R" % pages_ref]
        if outlines_ref:
            cat_parts += ["/Outlines %d 0 R" % outlines_ref,
                          "/PageMode /UseOutlines"]
        catalog = self._add(("<< %s >>" % " ".join(cat_parts)).encode("latin-1"))

        # ----------------------------------------------------- serialise ----
        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0] * len(self.objects)
        for i in range(1, len(self.objects)):
            offsets[i] = len(out)
            out += ("%d 0 obj\n" % i).encode("latin-1")
            out += self.objects[i]
            out += b"\nendobj\n"
        xref = len(out)
        out += ("xref\n0 %d\n" % len(self.objects)).encode("latin-1")
        out += b"0000000000 65535 f \n"
        for i in range(1, len(self.objects)):
            out += ("%010d 00000 n \n" % offsets[i]).encode("latin-1")
        out += ("trailer\n<< /Size %d /Root %d 0 R /Info %d 0 R >>\n"
                "startxref\n%d\n%%%%EOF\n" %
                (len(self.objects), catalog, info, xref)).encode("latin-1")
        return bytes(out)


# ------------------------------------------------------------- PNG decoding ----
def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def decode_png(data):
    """
    Decode the PNG variants canvas.py produces: 8-bit truecolour or 8-bit
    indexed, no interlacing.

    Returns a dict with w, h, kind ('rgb' or 'indexed'), data and, for indexed
    images, palette as a list of (r, g, b).
    """
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    pos = 8
    width = height = 0
    ctype = 2
    idat = bytearray()
    plte = b""
    while pos < len(data):
        ln = int.from_bytes(data[pos:pos + 4], "big")
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        if tag == b"IHDR":
            width = int.from_bytes(body[0:4], "big")
            height = int.from_bytes(body[4:8], "big")
            depth, ctype = body[8], body[9]
            assert depth == 8 and ctype in (2, 3), "unsupported PNG variant"
        elif tag == b"PLTE":
            plte = body
        elif tag == b"IDAT":
            idat += body
        elif tag == b"IEND":
            break
        pos += 12 + ln

    raw = zlib.decompress(bytes(idat))
    bpp = 3 if ctype == 2 else 1
    stride = width * bpp
    rows = _unfilter(raw, width, height, stride, bpp)
    if ctype == 3:
        palette = [(plte[i], plte[i + 1], plte[i + 2])
                   for i in range(0, len(plte), 3)]
        return {"w": width, "h": height, "kind": "indexed", "data": rows,
                "palette": palette}
    return {"w": width, "h": height, "kind": "rgb", "data": rows,
            "palette": None}


def _decode_png(data):
    """Backwards-compatible helper returning (width, height, RGB bytes)."""
    img = decode_png(data)
    if img["kind"] == "rgb":
        return img["w"], img["h"], img["data"]
    pal = img["palette"]
    out = bytearray(img["w"] * img["h"] * 3)
    for i, ix in enumerate(img["data"]):
        out[i * 3:i * 3 + 3] = bytes(pal[ix])
    return img["w"], img["h"], bytes(out)


def _unfilter(raw, width, height, stride, bpp):
    """Reverse the PNG per-row filters."""
    out = bytearray(height * stride)
    prev = bytearray(stride)
    p = 0
    for y in range(height):
        ft = raw[p]
        p += 1
        line = bytearray(raw[p:p + stride])
        p += stride
        if ft == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif ft == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif ft == 3:
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 0xFF
        elif ft == 4:
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                ul = prev[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + _paeth(left, prev[i], ul)) & 0xFF
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return bytes(out)


def png_dimensions(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    return (int.from_bytes(data[16:20], "big"),
            int.from_bytes(data[20:24], "big"))
