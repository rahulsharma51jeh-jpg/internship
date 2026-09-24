#!/usr/bin/env python3
"""
Builds the internship report.

    python3 build.py [output-directory]

Verifies the financial model, renders every exhibit, then writes the PDF and
the DOCX from the single block list in content.py.
"""

import os
import sys
import time

import brand
import content
import exhibits
import findata as fd

OUT_NAME = "Internship_Report_Ganga_Kumari_Singh"


def main(outdir):
    t0 = time.time()
    os.makedirs(outdir, exist_ok=True)

    print("  1/5  verifying the financial model ...", end=" ", flush=True)
    fd.self_check()
    print("tied out")

    print("  2/5  rendering exhibits ...", end=" ", flush=True)
    images, _canvases = exhibits.build_all()
    print("%d images" % len(images))

    print("  3/5  building the content model ...", end=" ", flush=True)
    blocks = content.build()
    counts, words = content.stats(blocks)
    print("%d blocks, ~%d words" % (len(blocks), words))

    meta = {
        "title": brand.REPORT_TITLE.title() + " \u2014 " + brand.REPORT_SUBJECT,
        "author": brand.STUDENT_NAME.title(),
        "subject": "%s, %s | %s" % (brand.DEGREE_SHORT, brand.SPECIALISATION,
                                    brand.UNIVERSITY),
    }

    print("  4/5  writing PDF ...", end=" ", flush=True)
    import pdfwriter
    pdf_bytes, pages = pdfwriter.build_pdf(blocks, images, meta)
    pdf_path = os.path.join(outdir, OUT_NAME + ".pdf")
    with open(pdf_path, "wb") as fh:
        fh.write(pdf_bytes)
    print("%d pages, %.1f KB" % (pages, len(pdf_bytes) / 1024.0))

    print("  5/5  writing DOCX ...", end=" ", flush=True)
    try:
        import docxwriter
        docx_bytes = docxwriter.build_docx(blocks, images, meta)
        docx_path = os.path.join(outdir, OUT_NAME + ".docx")
        with open(docx_path, "wb") as fh:
            fh.write(docx_bytes)
        print("%.1f KB" % (len(docx_bytes) / 1024.0))
    except ImportError:
        print("skipped (docxwriter not present yet)")

    print("\nDone in %.1fs. Output in %s" % (time.time() - t0, outdir))
    print("  tables: %d   figures: %d   PDF pages: %d"
          % (counts.get("table", 0), counts.get("figure", 0), pages))
    return pages


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/projects/sandbox/output"
    main(out)
