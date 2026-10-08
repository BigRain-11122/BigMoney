# -*- coding: utf-8 -*-
"""r901 bm-a W193 five-face prep: physical face dumps of the current W192
fragments (r776 fragment-needle law: the freeze pair lists must be built
from the PHYSICAL probe-dumped shapes, never from memory). Zero writes to
the source files; dumps land in results/_r901bma_w193_face_*.txt."""
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


cfg = chunk(n1n, '    192: {"batch": "PERPETUAL-N1-W192",',
            '"engine_owner": "bm-c"},', "cfg192")
mat = chunk(n1n, "    # --- W192 materializer face",
            "    _set_wave(2)", "mat192")
pf = chunk(pfn, "    # W192 (bm-c r787 freeze, seat MSG-20261008-2351-bmc-w192-seat",
           '"engine_owner": "bm-c"},', "pf192")
claim = chunk(n1n, '          "+ W192 materializer face [same guard set',
              '"r787 bm-c] "', "claim192")

for name, txt in (("cfg", cfg), ("mat", mat), ("pf", pf), ("claim", claim)):
    io.open("results/_r901bma_w193_face_%s.txt" % name, "w",
            encoding="utf-8", newline="\n").write(txt)
    print("dumped %s: %d bytes, %d lines" % (name, len(txt), txt.count(NL)))
print("MAT TAIL:", repr(mat[-80:]))
print("PF ROW:", repr(pf[pf.rfind("192: {"):][:120]))
