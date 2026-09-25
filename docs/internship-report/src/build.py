"""Two-pass build of the internship report."""
import sys
import pdfengine as pe
import content


def make(prev=None):
    d = pe.Document(pe.FONTS)
    content.build(d, prev)
    d.finish()
    return d


def main(out="/projects/sandbox/Internship_Report_Gunja_Kumari.pdf", passes=3):
    prev = None
    for p in range(passes):
        d = make(prev)
        prev = {"refs": dict(d._collect), "figures": list(d.figures),
                "tables": list(d.tables_list)}
        print("pass %d: %d pages, %d figures, %d tables"
              % (p + 1, len(d.pages), len(d.figures), len(d.tables_list)))
    pages, size = d.save(out, title="Internship Report on Financial Management Practices at "
                                    "Infinity Interns",
                         author="Gunja Kumari (Roll No. 35)",
                         subject="MBA Summer Internship Report, Session 2024-26")
    print("saved %s  (%d pages, %.2f MB)" % (out, pages, size / 1048576.0))
    return d


if __name__ == "__main__":
    main(*(sys.argv[1:] or []))
