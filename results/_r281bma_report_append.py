# -*- coding: utf-8 -*-
"""R281 bm-a round-report append (r281 bm-b law: probe tail newline first;
fixed five-field line per fleet/README.md sec.6)."""
import datetime

P = "logs/iteration-loop/round_reports-bm-a.md"
raw = open(P, "rb").read()
if raw and not raw.endswith(b"\n"):
    with open(P, "ab") as fh:
        fh.write(b"\n")          # repair: two rounds had merged into one line
now = datetime.datetime.now()
ts = now.strftime("%Y-%m-%d %H:%M:%S")
line = (
    f"{ts} | R281 bm-a | CN_TREND_ETF_P1 runner built per R99 law "
    "(scripts/cn_trend_etf_p1.py: 23-ETF mechanical universe re-derive "
    "gate, 7 judged cells MA/DON/TRAIL event-driven engine, K=2000 "
    "weekly-Bernoulli nulls via parallel_runner workers=4, census+"
    "splits+robust, D6 REG6 reject face + prior-negative advisory) + "
    "pooled ready lane=ANY; rev_osc twin finalize landmines defused "
    "pre-relaunch (g2 pbo dict->float; ledger key->trials_ledger r252); "
    "rebase autofill_state union + post_review pair (jsonl union +36 "
    "lines, REPORT snapshot take-newer, jsonl EOL LF-normalized after "
    "resolver CRLF flip self-catch) | verify: selftest 21/21 + revosc "
    "15/15, py_compile x2, real-data gate probe GREEN (T=5248 N=23 "
    "sse_cover 0.9939, panel 15s), MA_BASE x2 probe sharpe 0.4516 in "
    "prereg s5 band 0.2-0.6, push 84c8b09d..463bde3a | next: autofill "
    "tick claims cntrend-0of1 + revosc relaunch (both ready in pool); "
    "T-87 s2 queue #2 runner follows after #1 judged; harvest/judgment "
    "next rounds\n"
)
with open(P, "ab") as fh:
    fh.write(line.encode("utf-8"))
print("appended R281 line;", P)
