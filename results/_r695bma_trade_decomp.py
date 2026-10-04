# r695 bm-a: per-cohort per-pick decomposition to identify the changed trade(s)
import io, json, os, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import refine_bench_rev_census as RC
import rev_osc_stock_p1 as RV
import pandas as pd

CELL_NAME = "D-15|raw|base|time|h20"
RC._init_worker()
P = RC._W["P"]
cell = None
for c in RC.census_cells():
    if c["name"] == CELL_NAME:
        cell = c
        break
cost = RV.COST_X1
tp_pct, sl_pct = RC._exit_pair(cell["exit"])

idx = pd.to_datetime(np.load(os.path.join(RV.CACHE, "dates.npy")), unit="us")
syms = P["syms"]

# decompose cohorts overlapping the diff era [7136..8325]
records = []   # (g, t, s, sym, net, exit_d, span, bucket, w, window)
for g, t in enumerate(RV.signal_grid()):
    if t + 1 + 25 < 7136 or t + 1 > 8325:
        continue
    picks, why = RC._pick_axis(P, t, cell)
    if picks is None:
        continue
    w = np.ones(len(picks)) / len(picks)
    bucket = g % 2
    for i, s in enumerate(picks):
        net, exit_d, tag = RC._sim_axis(P, int(s), t, cell["H"], tp_pct, sl_pct, cost)
        if net is None:
            continue
        span = max(1, exit_d - (t + 1))
        records.append(dict(g=g, t=t, s=int(s), sym=syms[int(s)], net=float(net),
                            exit_d=int(exit_d), span=int(span), bucket=bucket,
                            w=float(w[i]), tag=tag))
print("cohort trades in era: %d" % len(records))
# delta signature: daily delta = w * dnet / span = -3.884e-04 -> dnet = -3.884e-04*span/w
cands = [r for r in records if abs(r["w"] * (-0.07768) / r["span"] - (-3.884e-04)) < 2e-6
         or abs(r["w"] * (-0.0777) / r["span"] + 3.884e-04) < 2e-6]
# too strict; instead: find trades whose daily-contribution magnitude could produce
# constant delta if their net shifted: any trade with span such that w*1/span*0.0777 ~ 3.884e-4
# i.e. span ~ w*0.0777/3.884e-4
for r in records:
    implied_span = r["w"] * 0.0777 / 3.884e-04
    r["span_match"] = abs(implied_span - r["span"]) < 1.5
n_match = sum(1 for r in records if r["span_match"])
print("trades with matching span signature:", n_match)
# which stocks appear in matching trades?
from collections import Counter
cnt = Counter(r["sym"] for r in records if r["span_match"])
print("top syms among span-matching trades:", cnt.most_common(8))
# show sample matching records
for r in [r for r in records if r["span_match"]][:10]:
    print("g=%d t=%d(%s) %s net=%.6f exit=%d(%s) span=%d tag=%s bucket=%d"
          % (r["g"], r["t"], str(idx[r["t"]].date()), r["sym"], r["net"],
             r["exit_d"], str(idx[r["exit_d"]].date()), r["span"], r["tag"], r["bucket"]))
print("PROBE_OK")
