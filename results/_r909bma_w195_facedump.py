# -*- coding: utf-8 -*-
"""r909 bm-a W195 five-face prep: physical face dumps of the current W194
fragments (r776 fragment-needle law: the freeze pair lists must be built
from the PHYSICAL probe-dumped shapes, never from memory). Zero writes to
the source files; dumps land in results/_r909bma_w195_face_*.txt."""
import io

N1 = "scripts/perpetual_faces_n1.py"
PF = "scripts/perpetual_faces.py"
NL = "\n"

n1n = io.open(N1, encoding="utf-8", newline="").read().replace("\r\n", "\n")
pfn = io.open(PF, encoding="utf-8", newline="").read().replace("\r\n", "\n")


def chunk(text, start, end, tag):
    i = text.find(start)
    assert i >= 0, "start not found: %s" % tag
    j = text.find(end, i)
    assert j > i, "end not found: %s" % tag
    return text[i:j + len(end)]


cfg = chunk(n1n, '    194: {"batch": "PERPETUAL-N1-W194",',
            '"engine_owner": "bm-a"},', "cfg194")
mat = chunk(n1n, "    # --- W194 materializer face",
            "    _set_wave(2)", "mat194")
pf = chunk(pfn, "    # W194 (bm-a r905 freeze, seat MSG-2026-10-09-0627-bma-w194-seat",
           '"engine_owner": "bm-a"},', "pf194")
claim = chunk(n1n, '          "+ W194 materializer face [same guard set',
              '"r905 bm-a] "', "claim194")

for name, txt in (("cfg", cfg), ("mat", mat), ("pf", pf), ("claim", claim)):
    io.open("results/_r909bma_w195_face_%s.txt" % name, "w",
            encoding="utf-8", newline="\n").write(txt)
    print("dumped %s: %d bytes, %d lines" % (name, len(txt), txt.count(NL)))
print("MAT TAIL:", repr(mat[-80:]))
print("PF ROW:", repr(pf[pf.rfind("194: {"):][:120]))
