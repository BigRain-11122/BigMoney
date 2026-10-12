# -*- coding: utf-8 -*-
# r923 absorb-window surgical fix: the r922 dead session wrote the prereg
# freeze-window token as "r922 freeze 窗·2026-10-12 10:5x" (its own planned
# window). r922 died pre-splice (estate = prereg + derive + subverify only,
# zero commits). The freeze splice actually lands in the r923 absorb window
# -> correct the provenance token to r923 (count==1 asserts both sides).
# The "live-read r922" face stays verbatim (factual: the r922 derive did
# that live read).
import sys
sys.stdout.reconfigure(encoding="utf-8")
P = r"research\PERPETUAL_N1_W220_PREREG.md"
t = open(P, encoding="utf-8").read()

FIND = "【bm-c 循环班 r922 freeze 窗·2026-10-12 10:5x·CEO 填载令 standing+"
REPL = "【bm-c 循环班 r923 freeze 窗（absorb r922 freeze-prep estate）·2026-10-12 11:4x·CEO 填载令 standing+"
assert t.count(FIND) == 1, f"freeze-window token count {t.count(FIND)} != 1"
t = t.replace(FIND, REPL, 1)

# second token already correct-face (r922 live read factual) -- verify present
assert t.count("live-read r922") == 1, "r922 live-read face drifted"
assert t.count("r923 freeze 窗") == 1 and t.count("r922 freeze 窗") == 0
open(P, "w", encoding="utf-8", newline="").write(t)
print("prereg freeze-window token fixed: r922 10:5x -> r923 11:4x (absorb r922 estate)")
