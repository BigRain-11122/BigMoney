# -*- coding: utf-8 -*-
# r1114-continuation bm-c: clone the r1111 S6 light driver -> r1114 (count-asserted, same legs verbatim)
import io, py_compile

SRC = "results/_r1111bmc_s6_light.py"
DST = "results/_r1114bmc_s6_light.py"
t = io.open(SRC, encoding="utf-8", newline="").read()
R = [
 ('"""r1111 bm-c S6 Monday pre-market light chain driver (10 legs, r1096-r1109 canon', '"""r1114-continuation bm-c S6 Monday mid-morning light chain driver (10 legs, r1096-r1111 canon', 1, "d-hdr"),
 ('Log to results/_r1110bmc_s6_log.txt. MUST run under the SYSTEM python', 'Log to results/_r1114bmc_s6_log.txt. MUST run under the SYSTEM python', 1, "d-logdoc"),
 ('Monday\n~07:2x run -- bars cutoff 10-16 current (pre-15:30 honest: update_daily/papers', 'Monday\n~10:5x run -- bars cutoff 10-16 current (pre-15:30 honest: update_daily/papers', 1, "d-time"),
 ('r1111 window: W276 FULL CYCLE one-window (splice 354a645155 CLEAN-AT-BIRTH 9th\n+ engine self-burn 12/12 df7dedfd07+627c4e10f2 + sixgate PRE-FINALIZE 39th\n+ finalize one-pass ledger 1,029,335+2,200=1,031,535 / K 602,920+2,200=605,120\nEXACT + fivekeys 6/6 ALL PASS + sec.7/8 backfill zero-placeholder; bands A 622_501..624_500\n25th A-hop / B 624_501..624_700 26th above-own-A per seat receipt verbatim; r1111\ncloseout = this window."""',
  'r1114-continuation window: W277 FULL CYCLE one-window (splice 9e53371814 CLEAN-AT-BIRTH 10th\n+ engine self-burn 12/12 0df07c846b+644b4f8459 + sixgate PRE-FINALIZE 40th\n+ finalize one-pass ledger 1,031,535+2,200=1,033,735 / K 605,120+2,200=607,320\nEXACT + fivekeys 6/6 ALL PASS + sec.7/8 backfill zero-placeholder; bands A 624_701..626_700\n26th A-hop / B 626_701..626_900 27th above-own-A per seat receipt verbatim + W278 SEAT\nPUBLISHED b187aa6214 (A 626_901..628_900 27th A-hop / B 628_901..629_100 28th above-own-A);\nr1114-continuation closeout = this window."""', 1, "d-narr"),
 ('LOG = os.path.join(ROOT, "results", "_r1111bmc_s6_log.txt")', 'LOG = os.path.join(ROOT, "results", "_r1114bmc_s6_log.txt")', 1, "d-log"),
 ('log.write("r1111 bm-c S6 Monday pre-market light chain run %s legs=%d\\n"', 'log.write("r1114-continuation bm-c S6 Monday mid-morning light chain run %s legs=%d\\n"', 1, "d-logw"),
 ('print("r1111 S6 light chain start %s legs=%d"', 'print("r1114-continuation S6 light chain start %s legs=%d"', 1, "d-start"),
]
for old, new, expect, tag in R:
    n = t.count(old)
    assert n == expect, f"[{tag}] {n} != {expect}: {old[:80]!r}"
    t = t.replace(old, new)
io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
print("S6 DRIVER CLONE OK", DST, len(t.encode("utf-8")), "B")
