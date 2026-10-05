# -*- coding: utf-8 -*-
# r547 bm-c surgical fix: py_verdict misattribution (regex caught first
# "verdict" in S6 log = compute_audit FLAG:supply_gap face; true py_watermark
# verdict = py_low_board_clear). Fix state/hb/round-report row bytes-face
# with per-file count asserts (r710 law: python bytes; r503: assert before
# write). Idempotent: skips files already clean.
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
FIXES = [
    (ROOT + r"\state-bm-c.json",
     b"FLAG:supply_gap legal idle whitelist",
     b"py_low_board_clear legal idle whitelist",
     2),
    (ROOT + r"\fleet\machines\bm-c.json",
     b"WM green, FLAG:supply_gap legal idle",
     b"WM green, py_low_board_clear legal idle",
     1),
    (ROOT + r"\round_reports-bm-c.md",
     b"py_watermark probe rc0\xc2\xb7FLAG:supply_gap",
     b"py_watermark probe rc0\xc2\xb7py_low_board_clear",
     1),
]
for path, old, new, expect in FIXES:
    raw = open(path, 'rb').read()
    n = raw.count(old)
    if n == 0 and raw.count(new) >= expect:
        print("ALREADY-CLEAN %s" % path)
        continue
    if n != expect:
        sys.exit("COUNT-MISMATCH %s old=%d expect=%d" % (path, n, expect))
    open(path, 'wb').write(raw.replace(old, new))
    print("FIXED %s (%d occurrence(s))" % (path, n))
print("SURGICAL_FIX_DONE")
