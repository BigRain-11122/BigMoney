# r695 bm-a: exact block boundaries + pick-set intersection to identify the stock
import io, os, sys
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
cell = [c for c in RC.census_cells() if c["name"] == CELL_NAME][0]
cost = RV.COST_X1
tp_pct, sl_pct = RC._exit_pair(cell["exit"])
idx = pd.to_datetime(np.load(os.path.join(RV.CACHE, "dates.npy")), unit="us")
syms = P["syms"]

p2 = np.load(os.path.join(ROOT, "results", "refine_bench_stock", "rev_p2",
                          "cells", CELL_NAME.replace("|", "_") + "_x1.npy"))

# rebuild today series (same as before)
b = [np.zeros(P["T"]), np.zeros(P["T"])]
for g, t in enumerate(RV.signal_grid()):
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
        b[bucket][t + 1:t + 1 + span] += float(w[i]) * float(net) / span
today = 0.5 * (b[0] + b[1])

diff = np.asarray(today) - np.asarray(p2, dtype=np.float64)
nz = np.flatnonzero(np.abs(diff) > 1e-12)
blocks = []
start = prev = nz[0]
for i in nz[1:]:
    if i != prev + 1:
        blocks.append((start, prev))
        start = i
    prev = i
blocks.append((start, prev))
print("blocks:", len(blocks))
for (s0, s1) in blocks:
    deltas = diff[s0:s1 + 1]
    print("block %5d..%5d (%s..%s) ndays=%d delta=%.6e const=%s"
          % (s0, s1, str(idx[s0].date()), str(idx[s1].date()), s1 - s0 + 1,
             float(deltas[0]), bool(np.allclose(deltas, deltas[0], atol=1e-15))))

# cohort pick sets for affected windows
def cohort_for_window(s0):
    # cohort t = s0 - 1 (entry day); find grid t with t+1 <= s0 <= t+1+span-1
    for g, t in enumerate(RV.signal_grid()):
        if t + 1 <= s0 <= t + 1 + 40:
            return g, t
    return None, None

sets = []
for (s0, s1) in blocks:
    g, t = cohort_for_window(s0)
    picks, why = RC._pick_axis(P, t, cell)
    if picks is None:
        print("block %d: cohort picks None (%s)" % (s0, why))
        continue
    syms_set = set(syms[int(x)] for x in picks)
    sets.append(syms_set)
    print("block %d -> cohort g=%d t=%d(%s) picks=%s" %
          (s0, g, t, str(idx[t].date()), sorted(syms_set)))
inter = set.intersection(*sets) if sets else set()
print("== pick-set intersection across blocks:", sorted(inter))
print("PROBE_OK")
