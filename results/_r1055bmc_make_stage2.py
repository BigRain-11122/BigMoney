# -*- coding: utf-8 -*-
"""r1055 absorb: stage editor before P5e-rcpt-semantics-A, diff needle vs t."""
import io

ED = r"results\_w254bmc_derive_editor.py"
OUT = r"results\_r1055bmc_editor_staged2.py"

t = io.open(ED, encoding="utf-8").read()

i = t.find("rep('\"A\": \"1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim in the probe receipt; the naive continuation 571_701..573_700 refused")
assert i > 0, "P5e-rcpt-semantics-A rep call not found"
staged = t[:i]
tail = '''

with io.open(r"results/_r1055bmc_staged2_t.txt", "w", encoding="utf-8", newline="") as f:
    f.write(t)
print("staged2 t len", len(t))
print('"A": "1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop count:', t.count('"A": "1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop'))
print("STAGE2 OK")
'''
io.open(OUT, "w", encoding="utf-8", newline="").write(staged + tail)
print("staged2 written, staged len", len(staged))
