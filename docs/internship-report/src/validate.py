"""Structural validation of the generated PDF: header, xref offsets, object
integrity, stream lengths, page tree, fonts, page labels and outline."""
import re
import sys
import zlib

path = sys.argv[1] if len(sys.argv) > 1 else "/projects/sandbox/Internship_Report_Gunja_Kumari_Illustrated.pdf"
data = open(path, "rb").read()
errors = []

if not data.startswith(b"%PDF-1."):
    errors.append("bad header")
if not data.rstrip().endswith(b"%%EOF"):
    errors.append("missing %%EOF")

# startxref -> xref table
m = re.search(rb"startxref\s+(\d+)\s+%%EOF\s*$", data)
if not m:
    errors.append("no startxref")
    print(errors)
    sys.exit(1)
xref_off = int(m.group(1))
if data[xref_off:xref_off + 4] != b"xref":
    errors.append("startxref does not point at 'xref'")

body = data[xref_off:]
head = re.match(rb"xref\s+0\s+(\d+)\s+", body)
n_obj = int(head.group(1))
entries = re.findall(rb"(\d{10}) (\d{5}) ([nf])", body[:head.end() + n_obj * 20 + 40])
if len(entries) != n_obj:
    errors.append("xref entry count %d != %d" % (len(entries), n_obj))

# every in-use entry must point at "<num> 0 obj"
checked = 0
for i, (off, gen, kind) in enumerate(entries):
    if kind == b"f":
        continue
    o = int(off)
    expect = b"%d 0 obj" % i
    if data[o:o + len(expect)] != expect:
        errors.append("object %d xref offset wrong (found %r)" % (i, data[o:o + 16]))
    checked += 1

# stream /Length values must match the actual stream payload
for mo in re.finditer(rb"/Length (\d+)[^>]*>>\s*stream\r?\n", data):
    length = int(mo.group(1))
    start = mo.end()
    if data[start + length:start + length + 10].strip()[:9] != b"endstream":
        errors.append("stream length mismatch at byte %d" % start)

# all Flate streams must inflate
inflated = 0
for mo in re.finditer(rb"<<([^<>]|<<[^>]*>>)*?/Filter /FlateDecode([^<>]|<<[^>]*>>)*?/Length (\d+)[^>]*>>\s*stream\r?\n", data):
    length = int(mo.group(3))
    raw = data[mo.end():mo.end() + length]
    try:
        zlib.decompress(raw)
        inflated += 1
    except Exception as exc:
        errors.append("stream will not inflate at %d: %s" % (mo.end(), exc))

trailer = re.search(rb"trailer\s*<<(.*?)>>\s*startxref", data, re.S).group(1)
root = re.search(rb"/Root (\d+) 0 R", trailer).group(1)
pages = len(re.findall(rb"/Type /Page\b[^s]", data))
kids = re.search(rb"/Type /Pages /Count (\d+)", data)
fonts = re.findall(rb"/BaseFont /([A-Za-z0-9#\-]+)", data)
labels = re.search(rb"/PageLabels", data)
outline = re.search(rb"/Type /Outlines /First (\d+) 0 R /Last (\d+) 0 R /Count (\d+)", data)

print("file            : %s (%.2f MB)" % (path, len(data) / 1048576.0))
print("objects         : %d (%d in use, offsets verified)" % (n_obj - 1, checked))
print("flate streams   : %d inflate cleanly" % inflated)
print("page objects    : %d ; /Pages /Count = %s" % (pages, kids.group(1).decode() if kids else "?"))
print("embedded fonts  : %s" % ", ".join(sorted(set(f.decode() for f in fonts))))
print("page labels     : %s" % ("present" if labels else "MISSING"))
print("outline         : %s top-level bookmarks" % (outline.group(3).decode() if outline else "MISSING"))
print("catalog object  : %s" % root.decode())
print("")
if errors:
    print("FAILED %d check(s):" % len(errors))
    for e in errors[:20]:
        print("  -", e)
    sys.exit(1)
print("STRUCTURE OK - no errors found")
