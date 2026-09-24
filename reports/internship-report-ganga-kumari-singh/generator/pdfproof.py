"""
A proof renderer for the PDF layout.

There is no PDF rasteriser available in this sandbox, so this module provides a
drop-in replacement for pdfdoc.Document whose Surface draws onto the raster
canvas instead of emitting PDF operators. Glyph *positions* are computed from
exactly the same AFM width tables used by the real writer, so line breaks,
justification, column alignment and page breaks are reproduced faithfully; only
the letterforms differ, because the proof draws with the stroke font.

It exists to catch overflows, collisions and pagination faults that would
otherwise be invisible.

    python3 pdfproof.py 1 7 23      # render those page numbers to build/proof
"""

import afm
import brand
import strokefont as sf
from canvas import Canvas
from pdfdoc import png_dimensions, _decode_png

SCALE = 1.7          # raster pixels per PDF point

# Cap-height as a fraction of em, per face, for sizing the stroke font.
_CAP = {
    "Times-Roman": 0.662, "Times-Bold": 0.676, "Times-Italic": 0.653,
    "Times-BoldItalic": 0.669, "Helvetica": 0.717, "Helvetica-Bold": 0.718,
    "Helvetica-Oblique": 0.717, "Helvetica-BoldOblique": 0.718,
    "rupee": 0.662,
}
_BOLD = ("Times-Bold", "Times-BoldItalic", "Helvetica-Bold",
         "Helvetica-BoldOblique")


class ProofSurface:
    def __init__(self, doc, width, height):
        self.doc = doc
        self.w = width
        self.h = height
        self.cv = Canvas(int(width * SCALE), int(height * SCALE), brand.PAPER)

    # ------------------------------------------------------------- helpers ----
    def _p(self, v):
        return v * SCALE

    # -------------------------------------------------------------- shapes ----
    def rect(self, x, y, w, h, rgb):
        if w <= 0 or h <= 0:
            return
        self.cv.rect(self._p(x), self._p(y), self._p(w), self._p(h), rgb)

    def round_rect(self, x, y, w, h, r, rgb):
        if w <= 0 or h <= 0:
            return
        self.cv.round_rect(self._p(x), self._p(y), self._p(w), self._p(h),
                           self._p(r), rgb)

    def line(self, x0, y0, x1, y1, rgb, width=0.6):
        self.cv.line(self._p(x0), self._p(y0), self._p(x1), self._p(y1), rgb,
                     max(1.0, self._p(width)))

    def hline(self, x0, x1, y, rgb, width=0.6):
        self.line(x0, y, x1, y, rgb, width)

    def circle(self, cx, cy, r, rgb):
        self.cv.circle(self._p(cx), self._p(cy), self._p(r), rgb)

    def polygon(self, pts, rgb):
        self.cv.fill_polygon([(self._p(x), self._p(y)) for (x, y) in pts], rgb)

    # -------------------------------------------------------------- images ----
    def image(self, res_name, x, y, w, h):
        src = self.doc.res_images.get(res_name)
        if src is None:
            self.rect(x, y, w, h, brand.GREY_LIGHT)
            return
        iw, ih, rgb = src
        dw, dh = int(self._p(w)), int(self._p(h))
        if dw <= 0 or dh <= 0:
            return
        ox, oy = int(self._p(x)), int(self._p(y))
        cv = self.cv
        stride = iw * 3
        for row in range(dh):
            ty = oy + row
            if ty < 0 or ty >= cv.h:
                continue
            sy = min(ih - 1, row * ih // dh)
            base = sy * stride
            drow = (ty * cv.w) * 3
            for cx in range(dw):
                tx = ox + cx
                if tx < 0 or tx >= cv.w:
                    continue
                sx = min(iw - 1, cx * iw // dw)
                si = base + sx * 3
                di = drow + tx * 3
                cv.buf[di:di + 3] = rgb[si:si + 3]

    # ---------------------------------------------------------------- text ----
    def text(self, x, y, segments, rgb=None, char_space=0.0):
        rgb = rgb if rgb is not None else brand.INK
        pen = x
        for (face, size, s) in segments:
            if not s:
                continue
            cap = _CAP.get(face, 0.66) * size
            weight = max(1.0, self._p(size) * (0.105 if face in _BOLD
                                               else 0.072))
            for ch in s:
                w = afm.char_width(ch, face, size) if face != "rupee" \
                    else afm.RUPEE_WIDTH * size / 1000.0
                if ch not in (" ", "\u00a0"):
                    glyph = afm.RUPEE if face == "rupee" else ch
                    sf.draw_text(self.cv, glyph, self._p(pen), self._p(y),
                                 self._p(cap), rgb, weight=weight)
                pen += w + char_space

    def simple_text(self, x, y, s, face, size, rgb, char_space=0.0):
        self.text(x, y, [(face, size, s)], rgb, char_space)

    def stream(self):
        return b""


class NullSurface:
    """Discards every drawing call, for pages the caller did not ask for."""

    def __init__(self, doc, width, height):
        self.doc = doc
        self.w = width
        self.h = height
        self.cv = None

    def _noop(self, *a, **k):
        return None

    rect = round_rect = line = hline = circle = polygon = _noop
    image = text = simple_text = _noop

    def stream(self):
        return b""


class ProofDocument:
    """Mimics pdfdoc.Document but keeps raster pages."""

    def __init__(self, page_size=None, title="", author="", subject="",
                 only_pages=None):
        from pdfdoc import A4
        self.page_w, self.page_h = page_size or A4
        self.pages = []
        self.images = {}          # logical name -> (res_name, ref)
        self.res_images = {}      # res_name -> (w, h, rgb bytes)
        self._seq = 0
        self.outline = []
        self.only = only_pages

    def new_page(self):
        n = len(self.pages) + 1
        if self.only is None or n in self.only:
            s = ProofSurface(self, self.page_w, self.page_h)
        else:
            s = NullSurface(self, self.page_w, self.page_h)
        self.pages.append(s)
        return s

    def add_image(self, name, png_bytes):
        if name in self.images:
            return self.images[name][0]
        self._seq += 1
        res = "Im%d" % self._seq
        self.images[name] = (res, self._seq)
        if self.only:
            # Decoding every chart is slow; only decode when rasterising.
            self.res_images[res] = _decode_png(png_bytes)
        return res

    def font_name(self, face):
        return face

    def rupee_font_name(self):
        return "rupee"

    def build(self):
        return b""


def render(blocks, images, pages, meta=None, outdir="/projects/sandbox/build/proof"):
    """Lay the document out and save the requested 1-based page numbers."""
    import os
    import pdfwriter

    os.makedirs(outdir, exist_ok=True)
    want = set(pages)

    state = {"final": False}

    def factory(**kw):
        return ProofDocument(only_pages=(want if state["final"] else set()),
                             **kw)

    class ProofWriter(pdfwriter.Writer):
        def _pass(self, blks, final):
            state["final"] = final
            return super()._pass(blks, final)

    orig = pdfwriter.Document
    pdfwriter.Document = factory
    try:
        doc = ProofWriter(images, meta).render(blocks)
    finally:
        pdfwriter.Document = orig

    written = []
    for n in sorted(want):
        if 1 <= n <= len(doc.pages):
            path = os.path.join(outdir, "page_%03d.png" % n)
            doc.pages[n - 1].cv.save(path)
            written.append(path)
    return written, len(doc.pages)


if __name__ == "__main__":
    import sys

    import content
    import exhibits

    nums = [int(a) for a in sys.argv[1:]] or [1, 2, 9, 14, 20]
    imgs, _ = exhibits.build_all()
    blocks = content.build()
    paths, total = render(blocks, imgs, nums)
    print("total pages: %d" % total)
    for p in paths:
        print("  " + p)
