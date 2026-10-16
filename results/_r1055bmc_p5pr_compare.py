# -*- coding: utf-8 -*-
"""r1055 absorb: compare W253-editor P5e-pr chunk vs W254-editor clone + source reality."""
import io

ED253 = r"results\_w253bmc_derive_editor.py"
ED254 = r"results\_w254bmc_derive_editor.py"
SRC = r"results\_w253bmc_freeze_edits.py"

t = io.open(SRC, encoding="utf-8").read()
e253 = io.open(ED253, encoding="utf-8").read()


def chunk_at(ed, tag):
    i1 = ed.find('"%s")' % tag)
    if i1 < 0:
        return None, None
    i0 = ed.rfind("chunk('''", 0, i1)
    region = ed[i0:i1 + len('"%s")' % tag)]
    parts = region.split("'''")
    return parts[1], parts[3]


s253, d253 = chunk_at(e253, "P5e-pr")
print("=== W253-editor P5e-pr SRC (was needle for W252 freeze_edits) ===")
print(s253)
print("=== W253-editor P5e-pr DST (=> landed in W253 freeze_edits) ===")
print(d253)
print("=== does current source contain W253 dst verbatim? ===", t.count(d253))
print("=== source contains 'A=1-HOP STAIRCASE-AFFECTS-A walk'? ===", t.count("A=1-HOP STAIRCASE-AFFECTS-A walk"))
print("=== source contains 'chain-order splice from the'? ===", t.count("chain-order splice from the"))
