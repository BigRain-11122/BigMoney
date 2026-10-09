# -*- coding: utf-8 -*-
import io
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
n1n = io.open(ROOT + r"\scripts\perpetual_faces_n1.py", encoding="utf-8",
              errors="replace", newline="").read().replace("\r\n", "\n")
pfn = io.open(ROOT + r"\scripts\perpetual_faces.py", encoding="utf-8",
              errors="replace", newline="").read().replace("\r\n", "\n")


def chunk(text, start, end):
    i = text.find(start)
    assert i >= 0, "start miss: " + start[:40]
    j = text.find(end, i)
    assert j > i, "end miss"
    return text[i:j + len(end)]


mat200 = chunk(n1n, "    # --- W200 materializer face", "    _set_wave(2)")
cfg200 = chunk(n1n, '    200: {"batch": "PERPETUAL-N1-W200",',
               '"engine_owner": "bm-a"},')
pf200 = chunk(pfn, "    # W200 (bm-a r921 freeze", '"engine_owner": "bm-a"},')
claim200 = chunk(n1n, '          "+ W200 materializer face [same guard set',
                 '"r921 bm-a] "')
for nm, frag in (("mat", mat200), ("cfg", cfg200), ("pf", pf200),
                 ("claim", claim200)):
    p = ROOT + r"\results\_r922bma_w201_faceprobe_" + nm + ".txt"
    io.open(p, "w", encoding="utf-8", newline="").write(frag)
    print(nm, len(frag), "B")
print("OK")
