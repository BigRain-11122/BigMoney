# -*- coding: utf-8 -*-
"""r885 bm-a W186 sec7/sec8 backfill defect heal pass: U+2212 display minus
for the displayed mu values (r833 law 3) + bold-marker placement + anchor
char typo (U+952A -> U+951A, 2 sites) + mutual-exclusion char typo
(U+65A7 -> U+655A... actually U+65A7 axe -> U+65A5 expel)."""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PF = "research/PERPETUAL_N1_W186_PREREG.md"
src = io.open(PF, encoding="utf-8", newline="").read()

FIXES = [
    ("merged mu **-0.092905\uff08\u673a\u8bfb -0.09290459\uff09/ w-only mu **-0.102515\uff08\u673a\u8bfb -0.10251500\uff09",
     "merged mu **\u22120.092905**\uff08\u673a\u8bfb -0.09290459\uff09/ w-only mu **\u22120.102515**\uff08\u673a\u8bfb -0.10251500\uff09",
     1),
    ("W185 \u952a 0.3066", "W185 \u951a 0.3066", 2),
    ("\u540c\u7a97\u4e92\u65a7 leg2", "\u540c\u7a97\u4e92\u65a5 leg2", 1),
]
for old, new, exp in FIXES:
    n = src.count(old)
    assert n == exp, "fix target count=%d expect=%d: %r" % (n, exp, old[:60])
    src = src.replace(old, new)
assert "\u952a" not in src, "stray U+952A remains"
assert "\u4e92\u65a7" not in src, "stray axe char remains"
assert "\u22120.092905**" in src and "\u22120.102515**" in src, "U+2212 faces missing"
io.open(PF, "w", encoding="utf-8", newline="").write(src)
chk = io.open(PF, encoding="utf-8", newline="").read()
assert chk == src, "roundtrip drift"
print("heal pass rc0: U+2212 faces + anchor x2 + mutual-exclusion char fixed, bytes=%d" % len(chk.encode("utf-8")))
