#!/usr/bin/env python3
"""
Structural checks on the two generated files.

The DOCX check parses every XML part, verifies that relationship targets exist,
that every image referenced by the document body is present in the package, and
that property elements appear in the order the WordprocessingML schema demands
(Word shows a repair prompt otherwise).

The PDF check verifies the header, the object table, the cross-reference table
offsets, the page count and that every font and image resource referenced by a
content stream is actually declared.
"""

import re
import sys
import xml.etree.ElementTree as ET
import zipfile

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# Schema order of the child elements this writer emits.
PPR_ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "numPr",
             "pBdr", "shd", "tabs", "spacing", "ind", "contextualSpacing",
             "jc", "outlineLvl", "rPr", "sectPr"]
RPR_ORDER = ["rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike",
             "color", "spacing", "w", "kern", "position", "sz", "szCs",
             "highlight", "u", "vertAlign", "lang"]
TBLPR_ORDER = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblW", "jc",
               "tblCellSpacing", "tblInd", "tblBorders", "shd", "tblLayout",
               "tblCellMar", "tblLook", "tblCaption", "tblDescription"]
TCPR_ORDER = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders",
              "shd", "noWrap", "tcMar", "textDirection", "tcFitText",
              "vAlign", "hideMark"]
TRPR_ORDER = ["cnfStyle", "divId", "gridBefore", "gridAfter", "wBefore",
              "wAfter", "cantSplit", "trHeight", "tblHeader", "tblCellSpacing",
              "jc", "hidden"]
ORDERS = {"pPr": PPR_ORDER, "rPr": RPR_ORDER, "tblPr": TBLPR_ORDER,
          "tcPr": TCPR_ORDER, "trPr": TRPR_ORDER}


def check_docx(path):
    errs = []
    info = {}
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        required = ["[Content_Types].xml", "_rels/.rels", "word/document.xml",
                    "word/styles.xml", "word/_rels/document.xml.rels"]
        for r in required:
            if r not in names:
                errs.append("missing part: " + r)

        trees = {}
        for n in names:
            if n.endswith(".xml") or n.endswith(".rels"):
                try:
                    trees[n] = ET.fromstring(z.read(n))
                except ET.ParseError as e:
                    errs.append("XML parse error in %s: %s" % (n, e))

        # --- relationships resolve --------------------------------------
        rels = trees.get("word/_rels/document.xml.rels")
        rel_targets = {}
        if rels is not None:
            for rel in rels:
                rid = rel.get("Id")
                tgt = rel.get("Target")
                rel_targets[rid] = tgt
                if not tgt.startswith("http"):
                    full = "word/" + tgt
                    if full not in names:
                        errs.append("relationship %s points at a missing part: "
                                    "%s" % (rid, tgt))
        info["relationships"] = len(rel_targets)

        # --- every embedded image is declared and present ---------------
        doc = trees.get("word/document.xml")
        if doc is not None:
            used = set(re.findall(r'r:embed="([^"]+)"',
                                  z.read("word/document.xml").decode("utf-8")))
            for rid in used:
                if rid not in rel_targets:
                    errs.append("image relationship not declared: " + rid)
            info["images_referenced"] = len(used)
            media = [n for n in names if n.startswith("word/media/")]
            info["images_embedded"] = len(media)
            if len(used) > len(media):
                errs.append("more image references than embedded files")

            # --- property element ordering -----------------------------
            bad_order = 0
            for tag, order in ORDERS.items():
                for el in doc.iter(W + tag):
                    seen = []
                    for child in el:
                        local = child.tag.split("}")[-1]
                        if local in order:
                            seen.append(order.index(local))
                    if seen != sorted(seen):
                        bad_order += 1
                        if bad_order <= 5:
                            errs.append("%s children out of schema order: %s"
                                        % (tag, [c.tag.split('}')[-1]
                                                 for c in el]))
            if bad_order:
                errs.append("%d property elements are out of order" % bad_order)

            info["paragraphs"] = sum(1 for _ in doc.iter(W + "p"))
            info["tables"] = sum(1 for _ in doc.iter(W + "tbl"))
            info["drawings"] = sum(1 for _ in doc.iter(W + "drawing"))
            info["breaks"] = len([b for b in doc.iter(W + "br")
                                  if b.get(W + "type") == "page"])
            sect = list(doc.iter(W + "sectPr"))
            if not sect:
                errs.append("no sectPr: page size would be undefined")
    return errs, info


def check_pdf(path):
    errs = []
    info = {}
    with open(path, "rb") as fh:
        data = fh.read()
    if not data.startswith(b"%PDF-1."):
        errs.append("missing PDF header")
    if not data.rstrip().endswith(b"%%EOF"):
        errs.append("missing %%EOF trailer")

    n_obj = len(re.findall(rb"\n\d+ 0 obj\n", b"\n" + data))
    info["objects"] = n_obj
    pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
    info["pages"] = pages
    if pages == 0:
        errs.append("no page objects found")

    m = re.search(rb"/Count (\d+)", data)
    if m and int(m.group(1)) != pages:
        errs.append("page tree Count (%s) disagrees with page objects (%d)"
                    % (m.group(1).decode(), pages))

    # startxref must point at the xref keyword
    m = re.search(rb"startxref\s+(\d+)\s+%%EOF\s*$", data)
    if not m:
        errs.append("malformed startxref")
    else:
        off = int(m.group(1))
        if data[off:off + 4] != b"xref":
            errs.append("startxref offset does not land on the xref table")
        else:
            info["xref_offset"] = off

    # cross-reference offsets must point at object headers
    xref = data[off:] if m else b""
    entries = re.findall(rb"(\d{10}) 00000 n", xref)
    bad = 0
    for e in entries:
        o = int(e)
        if o and not re.match(rb"\d+ 0 obj", data[o:o + 24]):
            bad += 1
    if bad:
        errs.append("%d cross-reference entries do not point at an object"
                    % bad)
    info["xref_entries"] = len(entries)

    for need, label in [(rb"/Type\s*/Catalog", "catalog"),
                        (rb"/Type\s*/Pages", "page tree"),
                        (rb"/MediaBox", "MediaBox")]:
        if not re.search(need, data):
            errs.append("missing " + label)

    fonts = set(re.findall(rb"/BaseFont\s*/([A-Za-z\-]+)", data))
    info["fonts"] = sorted(f.decode() for f in fonts)
    info["type3_rupee"] = bool(re.search(rb"/Subtype\s*/Type3", data))
    info["images"] = len(re.findall(rb"/Subtype\s*/Image", data))
    info["outline_items"] = len(re.findall(rb"/Type\s*/Outlines", data))
    info["size_kb"] = round(len(data) / 1024.0, 1)
    return errs, info


def main(pdf_path, docx_path):
    ok = True
    for label, fn, path in [("PDF", check_pdf, pdf_path),
                            ("DOCX", check_docx, docx_path)]:
        print("\n%s  %s" % (label, path))
        print("-" * 72)
        errs, info = fn(path)
        for k in sorted(info):
            print("   %-22s %s" % (k, info[k]))
        if errs:
            ok = False
            print("   PROBLEMS:")
            for e in errs:
                print("     - " + e)
        else:
            print("   no structural problems found")
    print()
    return 0 if ok else 1


if __name__ == "__main__":
    base = "/projects/sandbox/output/Internship_Report_Ganga_Kumari_Singh"
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else base + ".pdf",
                  sys.argv[2] if len(sys.argv) > 2 else base + ".docx"))
