# -*- coding: utf-8 -*-
"""r668 bm-c rebase UU probe: per-file HEAD-vs-MINE ts + compute_audit structure."""
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = "K:/Fluxgroup/FluxGroup/quant/bigmoney/"
UU = [
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/daily_report/REPORT-2026-10-07.md",
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
PAT = re.compile(r"<<<<<<< HEAD\r?\n(.*?)\|\|\|\|\|\|\|.*?\r?\n(.*?)=======\r?\n(.*?)>>>>>>> [^\r\n]*\r?\n", re.S)
TSRE = re.compile(r"2026-10-07[ T]\d{1,2}:\d{2}(:\d{2})?(\.\d+)?")


def side_ts(blob):
    hits = TSRE.findall(blob)
    stamps = [m.group(0) for m in TSRE.finditer(blob)]
    best = None
    for s in stamps:
        try:
            t = s.replace("T", " ")
            hhmmss = t.split(" ")[1]
            if best is None or hhmmss > best.split(" ")[1]:
                best = t
        except Exception:
            pass
    return best


for f in UU:
    raw = open(R + f, "rb").read().decode("utf-8", errors="replace")
    hunks = PAT.findall(raw)
    if not hunks:
        print(f, "NO-HUNK-PARSE", raw.count("<<<<<<<"))
        continue
    head_all = "".join(h[0] for h in hunks)
    mine_all = "".join(h[2] for h in hunks)
    hts, mts = side_ts(head_all), side_ts(mine_all)
    winner = "MINE" if (mts and (not hts or mts > hts)) else ("HEAD" if hts else "?")
    print("%-46s hunks=%d HEAD=%s MINE=%s -> %s" % (f, len(hunks), hts, mts, winner))

# compute_audit structure probe
raw = open(R + "results/compute_audit.json", "rb").read().decode("utf-8", errors="replace")
print("\n== compute_audit structure ==")
print("markers:", raw.count("<<<<<<<"), raw.count("======="), raw.count(">>>>>>>"))
head_side = PAT.findall(raw)
for k in ("history", "runs", "samples", "rows", "audit", '"machine"', '"ts"'):
    print("  key", k, "present:", k in raw)
# first 3 lines of file
print("  head lines:", raw.splitlines()[:3])
