# -*- coding: utf-8 -*-
"""r935 physical dump probe: extract live W202 fragments (cfg/pf/mat/claim)
from scripts/perpetual_faces_n1.py + scripts/perpetual_faces.py (r909 law:
rolling-pair old strings from PHYSICAL files via file dump, never
transcribed). Read-only, zero writes to the engine files."""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
N1P = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\scripts\perpetual_faces_n1.py"
PFP = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\scripts\perpetual_faces.py"
OUT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results\_r935bma_probe_fragdump.py"

n1 = open(N1P, encoding="utf-8", errors="replace", newline="").read()
pf = open(PFP, encoding="utf-8", errors="replace", newline="").read()
n1n = n1.replace("\r\n", "\n")
pfn = pf.replace("\r\n", "\n")


def chunk(text, start, end, stag):
    i = text.find(start)
    assert i >= 0, "start marker missing [%s]" % stag
    j = text.find(end, i)
    assert j > i, "end marker missing [%s]" % stag
    return text[i:j + len(end)]


cfg202 = chunk(n1n, '    202: {"batch": "PERPETUAL-N1-W202",',
               '"engine_owner": "bm-a"},', "cfg202")
mat202 = chunk(n1n, "    # --- W202 materializer face",
               "    _set_wave(2)", "mat202")
pf202 = chunk(pfn, "    # W202 (bm-a r927 freeze",
              '"engine_owner": "bm-a"},', "pf202")
claim202 = chunk(n1n, '          "+ W202 materializer face [same guard set',
                 '"r927 bm-a] "', "claim202")
frags = {"cfg202": cfg202, "mat202": mat202, "pf202": pf202,
         "claim202": claim202}
for nm, frag in frags.items():
    path = OUT.replace("fragdump.py", "frag_%s.txt" % nm)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(frag)
    print(nm, "len", len(frag), "->", path)
for nm in ("cfg202", "pf202"):
    print("=" * 20, nm, "=" * 20)
    print(frags[nm][:2400])
