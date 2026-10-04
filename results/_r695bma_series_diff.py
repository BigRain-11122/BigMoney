# r695 bm-a: day-level series diff -- P2-time npy vs today's re-run (failing cell)
import io, json, os, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import refine_bench_rev_census as RC

CELL_NAME = "D-15|raw|base|time|h20"
p2_series = np.load(os.path.join(ROOT, "results", "refine_bench_stock",
                                 "rev_p2", "cells",
                                 CELL_NAME.replace("|", "_") + "_x1.npy"))
print("P2 series: shape=%s dtype=%s sum=%r" % (p2_series.shape, p2_series.dtype,
                                                float(p2_series.sum())))

# locate cell + rebuild today's series via census glue path (series retained
# by mirroring the accumulation manually -- reuse _rc-style but census math)
RC._init_worker()
cell = None
for c in RC.census_cells():
    if c["name"] == CELL_NAME:
        cell = c
        break

# census _cell_job drops the series; replicate its accumulation to keep series
P = RC._W["P"]
import rev_osc_stock_p1 as RV
cost = RV.COST_X1
tp_pct, sl_pct = RC._exit_pair(cell["exit"])
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
print("today series: shape=%s sum=%r" % (today.shape, float(today.sum())))

n = min(len(p2_series), len(today))
diff = np.asarray(today[:n]) - np.asarray(p2_series[:n], dtype=np.float64)
nz = np.flatnonzero(np.abs(diff) > 0)
print("days differing (|d|>0): %d / %d" % (len(nz), n))
print("days differing (|d|>1e-12): %d" % int((np.abs(diff) > 1e-12).sum()))
print("max|diff| = %.3e  sum|diff| = %.3e" % (float(np.abs(diff).max()),
                                              float(np.abs(diff).sum())))
if len(nz):
    print("first 20 diff days (idx, p2, today, delta):")
    for i in nz[:20]:
        print("  %5d  p2=%.10f today=%.10f d=%.3e" % (i, p2_series[i], today[i], diff[i]))
# dates for context
import pandas as pd
idx = pd.to_datetime(np.load(os.path.join(RV.CACHE, "dates.npy")), unit="us")
for i in nz[:20]:
    print("   date[%d]=%s" % (i, str(idx[i].date())))
# contiguous structure
if len(nz):
    print("diff day range: %s .. %s" % (nz[0], nz[-1]))
    # gap histogram
    gaps = np.diff(nz)
    print("n contiguous blocks:", int((gaps > 1).sum()) + 1)
print("PROBE_OK")
