# -*- coding: utf-8 -*-
# r1121 bm-c estate-verify extractor: W278 derive script span/needle marker faces (heal(i) law:
# line-level verification against ACTUAL text). Read-only.
import io, sys
sys.stdout.reconfigure(encoding="utf-8")
t = io.open(r"results/_w278bmc_prereg_derive.py", encoding="utf-8", newline="").read().replace("\r\n", "\n")
lines = t.split("\n")
print("TOTAL_LINES", len(lines), "BYTES", len(t.encode("utf-8")))
markers = [
    "_blob_expect =",
    'SRC sha mismatch"',
    "chain-fact existence gates",
    "seat MSG not carried",
    "fivekeys receipt + results json",
    'fivekeys not all_pass"',
    "se_mu chain verify",
    "probe_receipt.json",
    "lands_inside",
    "live RAM honesty gate",
    "RAM face out of honest window",
    "VMAP_POST_LEGS = [",
    "VMAP = [",
    "VMAP_FLOORS = {",
    "def xf(t):",
    "NEW = {",
    "marker pairs:",
    "BLOCKS = [",
    "T2 = T1",
    "MUST = [",
    "MUST_NOT = [",
    "post gates",
    'io.open(OUT',
    "staircase affects A",
    "frozen_face.txt",
    "import io, os",
    "PSUTIL",
    "psutil",
]
for m in markers:
    hits = [(i + 1, l) for i, l in enumerate(lines) if m in l]
    for h in hits[:4]:
        print("%d | %s" % (h[0], h[1][:170]))
    print("--- %r hits=%d" % (m, len(hits)))
print("FIRSTLINE:", lines[0][:170])
print("HDR_END_CANDIDATES:")
for i, l in enumerate(lines[:120]):
    if "universe face rolls naturally" in l or "import io, os" in l:
        print(i + 1, "|", l[:170])
