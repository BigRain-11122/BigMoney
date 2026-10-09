# -*- coding: utf-8 -*-
"""r912 bm-a: dump the four live W195 fragments (physical faces, r776 law)
to results/_r912bma_w196_face_*.txt for the W196 freeze roll pairs.
Read-only; zero writes to the live scripts."""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N1P = os.path.join(ROOT, "scripts", "perpetual_faces_n1.py")
PFP = os.path.join(ROOT, "scripts", "perpetual_faces.py")


def chunk(text, start, end, stag):
    i = text.find(start)
    assert i >= 0, "start marker not found [%s]" % stag
    j = text.find(end, i)
    assert j > i, "end marker not found [%s]" % stag
    return text[i:j + len(end)]


def main():
    n1_raw = open(N1P, encoding="utf-8", errors="replace", newline="").read()
    pf_raw = open(PFP, encoding="utf-8", errors="replace", newline="").read()
    n1n = n1_raw.replace("\r\n", "\n")
    pfn = pf_raw.replace("\r\n", "\n")

    mat195 = chunk(n1n, "    # --- W195 materializer face", "    _set_wave(2)", "mat195")
    cfg195 = chunk(n1n, '    195: {"batch": "PERPETUAL-N1-W195",',
                   '"engine_owner": "bm-a"},', "cfg195")
    pf195 = chunk(pfn, "    # W195 (bm-a r909 freeze, seat MSG-2026-10-09-0844-bma-w195-seat",
                  '"engine_owner": "bm-a"},', "pf195")
    claim195 = chunk(n1n, '          "+ W195 materializer face [same guard set',
                     '"r909 bm-a] "', "claim195")

    for name, txt in (("mat195", mat195), ("cfg195", cfg195),
                      ("pf195", pf195), ("claim195", claim195)):
        out = os.path.join(ROOT, "results", "_r912bma_w196_face_%s.txt" % name)
        with open(out, "w", encoding="utf-8", newline="") as fh:
            fh.write(txt)
        print("dumped %s: %d B" % (name, len(txt)))
    print("uniqueness: cfg=%d claim=%d pf=%d"
          % (n1n.count(cfg195), n1n.count(claim195), pfn.count(pf195)))
    print("anchors: T141_after_mat=%d claim_T141_anchor=%d"
          % (n1n.find("    # --- T-141 s2 lane face",
                      n1n.find("    # --- W195 materializer face")),
             n1n.count(claim195 + '\n          "+ T-141 s2 "')))


if __name__ == "__main__":
    main()
