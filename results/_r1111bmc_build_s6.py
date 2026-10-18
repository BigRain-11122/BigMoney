# -*- coding: utf-8 -*-
# r1111 bm-c: clone the r1110 S6 light driver -> r1111 (count-asserted, same legs verbatim)
import io, py_compile

SRC = "results/_r1110bmc_s6_light.py"
DST = "results/_r1111bmc_s6_light.py"
t = io.open(SRC, encoding="utf-8", newline="").read()
R = [
 ('r1110 bm-c S6 Monday pre-market light chain driver', 'r1111 bm-c S6 Monday pre-market light chain driver', 1, "d-hdr"),
 ('r1110 window: W276 PREREG DERIVED + FREEZE-PUSHED origin', 'r1111 window: W276 FULL CYCLE one-window (splice 354a645155 CLEAN-AT-BIRTH 9th', 1, "d-n1"),
 ('770a47fa1f first-try (research/PERPETUAL_N1_W276_PREREG.md 23,554B', '+ engine self-burn 12/12 df7dedfd07+627c4e10f2 + sixgate PRE-FINALIZE 39th', 1, "d-n2"),
 ('sha256_16 5352c7cf343fc5e5 BYTE-IDENTICAL to sim pre-flight; banned_direction', '+ finalize one-pass ledger 1,029,335+2,200=1,031,535 / K 602,920+2,200=605,120', 1, "d-n3"),
 ('gate ADMIT rc0; bands A 622_501..624_500 25th A-hop / B 624_501..624_700 26th', 'EXACT + fivekeys 6/6 ALL PASS + sec.7/8 backfill zero-placeholder; bands A 622_501..624_500', 1, "d-n4"),
 ('above-own-A per seat receipt 21b51a102 verbatim) + r1110 closeout = this', '25th A-hop / B 624_501..624_700 26th above-own-A per seat receipt verbatim; r1111', 1, "d-n5"),
 ('window."""', 'closeout = this window."""', 1, "d-n6"),
 ('LOG = os.path.join(ROOT, "results", "_r1110bmc_s6_log.txt")', 'LOG = os.path.join(ROOT, "results", "_r1111bmc_s6_log.txt")', 1, "d-log"),
 ('log.write("r1110 bm-c S6 Monday pre-market light chain run %s legs=%d\\n"', 'log.write("r1111 bm-c S6 Monday pre-market light chain run %s legs=%d\\n"', 1, "d-logw"),
 ('print("r1110 S6 light chain start %s legs=%d"', 'print("r1111 S6 light chain start %s legs=%d"', 1, "d-start"),
]
for old, new, expect, tag in R:
    n = t.count(old)
    assert n == expect, f"[{tag}] {n} != {expect}: {old[:80]!r}"
    t = t.replace(old, new)
io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
print("S6 DRIVER CLONE OK", DST, len(t.encode("utf-8")), "B")
