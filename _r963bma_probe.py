"""r963 probe: verify the three pending P0-matrix row streams against their
frozen sidecar/scan anchors BEFORE wiring them into the runner (fail-closed)."""
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

OUT = []


def rep(k, v):
    OUT.append((k, v))
    print(k, "=", v)


# ---------- 1) dip-rebound trio (refine_bench_stock rev_p2 raw|base x1) ----
CELLS_DIR = os.path.join(ROOT, "results", "refine_bench_stock", "rev_p2", "cells")
TRIO = ["D-15_raw_base_time_h20", "D-25_raw_base_time_h20", "Dtop10_raw_base_time_h20"]
dates_np = np.load(os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock",
                                "dates.npy"))
dates = [str(pd.Timestamp(x).date()) for x in pd.to_datetime(dates_np, unit="us")]
rep("stock panel T", len(dates))
rep("stock first/last", (dates[0], dates[-1]))


def stream_stats(rets, include_first=True):
    r = np.asarray(rets, dtype=float) if include_first else np.asarray(rets, dtype=float)[1:]
    sd = float(r.std(ddof=1))
    mean = float(r.mean())
    sharpe = mean / sd * np.sqrt(252.0) if sd > 0 else 0.0
    eq = np.cumprod(1.0 + r)
    years = len(r) / 252.0
    ann = float(eq[-1] ** (1.0 / years) - 1.0)
    maxdd = float((eq / np.maximum.accumulate(eq) - 1.0).min())
    return {"sharpe": round(sharpe, 4), "ann": round(ann, 6), "dd": round(maxdd, 6)}


for c in TRIO:
    a = np.load(os.path.join(CELLS_DIR, c + "_x1.npy"))
    side = json.load(open(os.path.join(CELLS_DIR, c + "_x1.json"), encoding="utf-8"))
    s_inc = stream_stats(a)
    s_exc = stream_stats(a, include_first=False)
    st = side["stats"]
    rep(c + " len", len(a))
    rep(c + " sidecar", (st["sharpe_full"], st["ann_ret"], st["max_dd"]))
    rep(c + " recompute[incl-first]", (s_inc["sharpe"], s_inc["ann"], s_inc["dd"]))
    rep(c + " recompute[drop-first]", (s_exc["sharpe"], s_exc["ann"], s_exc["dd"]))

# ---------- 2) six-members composite (member_reinforce cells x1) -----------
MR_CELLS = os.path.join(ROOT, "results", "member_reinforce", "cells")
MEMBERS = ["COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
           "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01"]
from live.paper import load_core, build_panels  # noqa: E402

_cut = pd.Timestamp("2026-09-22")
_pfull = load_core()
_pcut = {s: df[df.index <= _cut] for s, df in _pfull.items()}
P = build_panels(_pcut)
pidx = P["close"].index
rep("core48 joined bars", len(pidx))
for mbr in MEMBERS[:2]:
    a = np.load(os.path.join(MR_CELLS, mbr + "_x1.npy"))
    side = json.load(open(os.path.join(MR_CELLS, mbr + "_x1.json"), encoding="utf-8"))
    rep(mbr + " len/npy", len(a))
    idx = pidx[:len(a)]
    rep(mbr + " last-date", str(idx[-1].date()))
    s_inc = stream_stats(a)
    s_exc = stream_stats(a, include_first=False)
    rep(mbr + " sidecar", (side["sharpe_full"], side["ann_ret"], side["max_dd"]))
    rep(mbr + " recompute[incl]", (s_inc["sharpe"], s_inc["ann"], s_inc["dd"]))
    rep(mbr + " recompute[drop]", (s_exc["sharpe"], s_exc["ann"], s_exc["dd"]))

# ---------- 3) four-asset A-EQW replay (allocation_policy_scan engine) ------
from scripts import allocation_policy_scan as aps  # noqa: E402

aps._cost_check()
rep("COST_PER_SIDE set", aps.COST_PER_SIDE)
d4, r4, facts = aps.load_faces()
rep("four-asset panel n", len(d4))
rep("four-asset first/last", (str(d4[0]), str(d4[-1])))
targets = np.array([[0.25, 0.25, 0.25, 0.25]])
sim = aps.simulate_with_dates(d4, r4, targets, np.zeros(1, dtype=int),
                              "monthly", store_path=True)
path = sim["path"][0]
met = aps._path_metrics(path)
scan = json.load(open(os.path.join(ROOT, "results", "cross_start_robustness",
                                   "scan.json"), encoding="utf-8"))
ae = [x for x in scan["cells"] if x["cell_id"] == "A-EQW"][0]
rep("A-EQW n_reb replay/scan", (int(sim["n_reb"][0]), ae["n_rebalances"]))
for k in ("cagr", "vol", "sharpe", "maxdd"):
    rep("A-EQW " + k, (met[k], ae[k], abs(met[k] - ae[k])))
rep("PROBE DONE", True)
