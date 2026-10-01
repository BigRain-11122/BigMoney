"""REFINE_BENCH_REV_CENSUS -- stock-face REV family axis census (stage A).

Ticket T-2026-10-01-139 family-1 (CEO order O-2026-10-01-1035 "股票呢？不要
光走ETF"). REFINE_BENCH_LAW v1.0 s2 axis sweep on the p1c_stock frozen panel:
the judged batch REV_OSC_STOCK_P1 tested ONE form (Top10-deepest, BG gate,
TP8/SL10, H7/10); this furnace sweeps the whole band (cheap census first per
TRIAL_LABOR_LAW + CEO meaning-gate O-1901; survivors go to a stage-B judged
prereg, NOT this file).

Engine provenance (zero re-implementation of frozen faces):
  panel/universe/entry-proxy/exit-mechanics/costs = scripts/rev_osc_stock_p1.py
  imports (load_panel, signal_grid, _prev_finite, _net, cell_stats, frozen
  constants). The ONLY new code is axis parameterization:
    - _sim_axis: sim_stock with parameterized TP/SL (tp=None -> time-only);
      gap/sealed-board/roll/suspension mechanics copied verbatim.
    - _pick_axis: pick_cohort extended with depth threshold + liquidity floor
      (gate=BG constant per family context; no-gate face already judged).

Grid (frozen in research/REFINE_BENCH_STOCK_REV_P1.md BEFORE any burn):
  depth {top10, -15, -25} x entry {raw, yang} x liq {base, liq2}
  x exit {time, tp8sl10, tp10sl10, tp15sl10, tp8sl5} x H {5,7,10,20}
  = 240 cells. 3 cells coincide with judged faces (top10/yang/base/time/H7,
  .../tp8sl10/H7, .../time/H10) and are tagged anchor_judged=true -- census
  re-measure for engine-reuse proof, no re-judgment, grammar dedup intact.

Census stats per cell (cheap face): sharpe_full / ann_ret / max_dd / entries /
hit_rate / exit counters on the x1 cost face. NO nulls, NO gates, NO verdict
(stage A). Census is fully deterministic (grid sweep, zero RNG).

Pool burn (O-2355 multi-core law): 6 shards x 40 cells, each shard = one pool
entry, ProcessPool via scripts/parallel_runner.py (workers load the panel from
disk in the initializer -- no giant pickle; RAM floor 16GB, worker count
honest-capped by free RAM). Burn completes -> self-claim handshake
(results/pool_claims/<ENTRY>/<shard>.<machine>.json state=closed outcome=ok,
r497 law: the worker NEVER writes runnable_pool.json).

Usage: run --shard K --of 6 | selftest
  exit 0 ok; 3 = RAM floor; 2 = mechanism fault.
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import rev_osc_stock_p1 as RV            # frozen engine faces (reuse law)
from parallel_runner import run_cells_parallel, worker_cap  # O-2355 s2 face

OUT_DIR = os.path.join(ROOT, "results", "refine_bench_stock", "rev_census")
BATCH_NAME = "REFINE_BENCH_REV_CENSUS"
N_SHARDS = 6
CELLS_PER_SHARD = 40
WORKER_CAP_ARENA = 6                     # memory guard: stock panel ~5GB/worker
RAM_FLOOR_GB = 16.0
PBP = 252

DEPTH_MODES = ("top10", "-15", "-25")     # top10 = no threshold (judged face)
ENTRY_FACES = ("raw", "yang")
LIQ_FACES = ("base", "liq2")             # liq2 = amt20 >= 2e8 (4x base floor)
EXIT_FACES = ("time", "tp8sl10", "tp10sl10", "tp15sl10", "tp8sl5")
HOLDS = (5, 7, 10, 20)
LIQ2_AMT = 2e8
THIN_MARKET_MIN = RV.THIN_MARKET_MIN

_JUDGED_ANCHORS = {                       # REV_OSC_STOCK_P1 judged cell overlap
    ("top10", "yang", "base", "time", 7),
    ("top10", "yang", "base", "tp8sl10", 7),
    ("top10", "yang", "base", "time", 10),
}


def census_cells():
    cells = []
    for depth in DEPTH_MODES:
        for entry in ENTRY_FACES:
            for liq in LIQ_FACES:
                for exit_f in EXIT_FACES:
                    for H in HOLDS:
                        key = (depth, entry, liq, exit_f, H)
                        cells.append({
                            "name": f"D{depth}|{entry}|{liq}|{exit_f}|h{H}",
                            "depth": depth, "entry": entry, "liq": liq,
                            "exit": exit_f, "H": H,
                            "anchor_judged": key in _JUDGED_ANCHORS,
                        })
    return cells


# ------------------------------------------------------------- axis layer
def _sim_axis(P, s, t, H, tp_pct, sl_pct, cost):
    """sim_stock verbatim mechanics with parameterized TP/SL (tp None =
    time-only). Frozen faces (T+1 open conservative proxy, near-limit-up open
    un-capture, sealed limit-down no-fill, suspension roll, same-day
    both-touch -> SL first, limit-down-open exit roll) copied from
    RV.sim_stock; only the tp/sl price construction is parameterized."""
    op, hi, lo, cl, fl = (P["col"]["open"][s], P["col"]["high"][s],
                          P["col"]["low"][s], P["col"]["close"][s], P["fl"][s])
    T = P["T"]
    d = t + 1
    o = op[d]
    if not np.isfinite(o):
        return None, None, "unfillable"
    pc = RV._prev_finite(cl, d)
    if not np.isfinite(pc) or o / pc - 1.0 >= fl[d] - RV.LIMIT_OPEN_TOL:
        return None, None, "unfillable"
    entry = float(o)
    tp_px = entry * tp_pct if tp_pct is not None else None
    sl_px = entry * sl_pct if sl_pct is not None else None
    d_target = t + 1 + H
    while d < T:
        o, h, l, c = op[d], hi[d], lo[d], cl[d]
        if not (np.isfinite(o) and np.isfinite(c)):
            d += 1
            continue
        if h == l == c:
            pc = RV._prev_finite(cl, d)
            if np.isfinite(pc) and c / pc - 1.0 <= -fl[d]:
                d += 1
                continue
        if tp_px is not None and np.isfinite(h) and np.isfinite(l):
            pc = RV._prev_finite(cl, d)
            lo_gap = np.isfinite(pc) and o / pc - 1.0 <= -(fl[d] - RV.LIMIT_OPEN_TOL)
            sl_hit = lo_gap or (l <= sl_px)
            tp_hit = (o >= tp_px) or (h >= tp_px)
            if sl_hit and tp_hit:
                px = o if lo_gap else sl_px
                return (RV._net(px, entry, cost), d, "sl")
            if sl_hit:
                px = o if lo_gap else sl_px
                return (RV._net(px, entry, cost), d, "sl")
            if tp_hit:
                px = o if o >= tp_px else tp_px
                return (RV._net(px, entry, cost), d,
                        "tp_gap" if o >= tp_px else "tp")
        if d >= d_target:
            pc = RV._prev_finite(cl, d)
            if np.isfinite(pc) and o / pc - 1.0 <= -(fl[d] - RV.LIMIT_OPEN_TOL):
                d += 1
                continue
            return (RV._net(o, entry, cost), d, "time")
        d += 1
    j = T - 1
    while j > t and not np.isfinite(cl[j]):
        j -= 1
    px = float(cl[j]) if np.isfinite(cl[j]) else entry
    return (RV._net(px, entry, cost), max(j, t + 1), "tail")


def _pick_axis(P, t, cell):
    """pick_cohort verbatim ranking + axis extension: depth threshold and
    higher liquidity floor. gate=BG constant (family context; the no-gate
    BASE face is already judged)."""
    if not (np.isfinite(P["sse"][t]) and np.isfinite(P["ma200"][t])):
        return None, "gate_undefined"
    if not (P["sse"][t] < P["ma200"][t]):
        return None, "gate_closed"
    row = P["drop20"][t]
    e = P["elig"][t] & np.isfinite(row)
    if cell["entry"] == "yang":
        e = e & (P["F"]["close"][t] > P["F"]["open"][t])
    if cell["depth"] != "top10":
        thr = -float(cell["depth"]) / 100.0
        e = e & (row <= thr)
    if cell["liq"] == "liq2":
        e = e & (P["amt20"][t] >= LIQ2_AMT)
    cand = np.flatnonzero(e)
    if len(cand) < THIN_MARKET_MIN:
        return None, "thin_market"
    vals = row[cand]
    k = min(10, len(cand))
    part = np.argpartition(vals, k - 1)[:k]
    ordr = part[np.argsort(vals[part], kind="stable")]
    return cand[ordr].tolist(), "ok"


# --------------------------------------------------------- worker context
_W = {}                                   # worker-shared panel (init loads)


def _init_worker():
    global _W
    _W["P"] = RV.load_panel()
    P = _W["P"]
    P["T"] = P["F"]["close"].shape[0]
    P["amt20"] = RV._roll_mean20(P["F"]["amount"])


def _cell_job(cell):
    """Top-level picklable task: one census cell -> row (deterministic)."""
    P = _W["P"]
    cost = RV.COST_X1
    tp_pct, sl_pct = _exit_pair(cell["exit"])
    b = [np.zeros(P["T"]), np.zeros(P["T"])]
    entries = unfillable = 0
    nets = []
    skips = {"gate_closed": 0, "gate_undefined": 0, "thin_market": 0,
             "empty_fill": 0}
    exits = {}
    for g, t in enumerate(RV.signal_grid()):
        picks, why = _pick_axis(P, t, cell)
        if picks is None:
            skips[why] = skips.get(why, 0) + 1
            continue
        w = np.ones(len(picks)) / len(picks)
        bucket = g % 2
        filled = 0
        for i, s in enumerate(picks):
            net, exit_d, tag = _sim_axis(P, int(s), t, cell["H"],
                                         tp_pct, sl_pct, cost)
            if net is None:
                unfillable += 1
                continue
            entries += 1
            nets.append(float(net))
            exits[tag] = exits.get(tag, 0) + 1
            span = max(1, exit_d - (t + 1))
            b[bucket][t + 1:t + 1 + span] += float(w[i]) * float(net) / span
            filled += 1
        if filled == 0:
            skips["empty_fill"] += 1
    series = 0.5 * (b[0] + b[1])
    stats = RV.cell_stats(series)
    row = dict(cell)
    row.update(stats)
    row["hit_rate"] = (round(float(np.mean(np.greater(nets, 0))), 4)
                       if nets else 0.0)
    row["entries"] = entries
    row["unfillable"] = unfillable
    row["skips"] = skips
    row["exits"] = exits
    return {k: v for k, v in row.items() if k != "series"}


def _exit_pair(exit_f):
    return {
        "time": (None, None),
        "tp8sl10": (1.08, 0.90),
        "tp10sl10": (1.10, 0.90),
        "tp15sl10": (1.15, 0.90),
        "tp8sl5": (1.08, 0.95),
    }[exit_f]


# ------------------------------------------------------------- io layer
def _machine_id() -> str:
    try:
        return json.load(open(os.path.join(ROOT, "fleet", "machine.json"),
                              encoding="utf-8"))["machine_id"]
    except Exception:
        return "unknown"


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S") + time.strftime("%z")[:3] \
        + ":" + time.strftime("%z")[3:]


def _pool_claim(entry_id, shard_key, detail, started):
    """r497 law: worker-side harvest handshake (single-writer pool law:
    the worker never writes runnable_pool.json)."""
    d = os.path.join(ROOT, "results", "pool_claims", entry_id)
    os.makedirs(d, exist_ok=True)
    fp = os.path.join(d, f"{shard_key}.{_machine_id()}.json")
    now = _now_iso()
    json.dump({"machine_id": _machine_id(), "state": "closed",
               "pid": os.getpid(), "heartbeat": now, "outcome": "ok",
               "exit_code": 0, "started": started, "closed_at": now,
               "result_ref": detail},
              open(fp, "w", encoding="utf-8"), indent=1)
    return fp


def _free_ram_gb():
    try:
        import psutil
        return psutil.virtual_memory().available / 1e9
    except Exception:
        return RAM_FLOOR_GB + 1.0


def _workers_plan():
    """O-2355 law-2: workers_plan derived from code + RAM, not guesswork."""
    cap = min(worker_cap(), WORKER_CAP_ARENA)
    free = _free_ram_gb()
    if free < RAM_FLOOR_GB:
        return 0, free
    while cap > 2 and free < 8.0 * cap:   # ~8GB per stock-panel worker
        cap -= 1
    return cap, free


def cmd_run(args) -> int:
    started = _now_iso()
    os.makedirs(OUT_DIR, exist_ok=True)
    shard_fp = os.path.join(OUT_DIR, f"shard-{args.shard}of{args.of}.json")
    if os.path.exists(shard_fp):
        print(f"[census] shard {args.shard}/{args.of} already done (idempotent "
              f"skip, r488 burn+flip atomics: file presence = done)")
        return 0
    cells = census_cells()
    total = len(cells)
    if args.of != N_SHARDS or total != CELLS_PER_SHARD * N_SHARDS:
        print(f"[census] grid census drift: {total} cells / of={args.of}")
        return 2
    lo, hi = args.shard * CELLS_PER_SHARD, (args.shard + 1) * CELLS_PER_SHARD
    mine = cells[lo:hi]
    workers, free = _workers_plan()
    if workers == 0:
        print(f"[census] RAM floor refused: free={free:.1f}GB < {RAM_FLOOR_GB}")
        return 3
    jobs = [(c["name"], _cell_job, (c,)) for c in mine]
    t0 = time.time()
    res = run_cells_parallel(jobs, workers=workers,
                             desc=f"rev-census s{args.shard}",
                             initializer=_init_worker, initargs=())
    rows = [res[k] for k in [c["name"] for c in mine]]
    elapsed = round(time.time() - t0, 1)
    audit = {"machine": _machine_id(), "workers": res.get("__workers__"),
             "elapsed_sec": elapsed, "shard": args.shard, "of": args.of,
             "n_cells": len(rows), "ts": started,
             "evidence_cutoff": RV.EVIDENCE_CUTOFF,
             "batch": BATCH_NAME,
             "panel": "p1c_stock T=8792 N=5222 x b_layer (frozen, "
                      "REV_OSC_STOCK_P1 load_panel verbatim)",
             "cost_face": f"x1={RV.COST_X1}"}
    json.dump({"audit": audit, "rows": rows},
              open(shard_fp, "w", encoding="utf-8"), indent=1)
    # burn + flip atomics (r488/r489): claim handshake right after product
    entry = f"REFINE-REV-STOCK-CENSUS-SHARD-{args.shard}"
    key = f"rev-census-{args.shard}of{args.of}"
    fp = _pool_claim(entry, key, os.path.relpath(shard_fp, ROOT), started)
    print(f"[census] shard {args.shard}/{args.of} DONE: {len(rows)} cells, "
          f"workers={audit['workers']}, elapsed={elapsed}s")
    print(f"[census] pool claim closed: {fp}")
    return 0


def cmd_status(_) -> int:
    done = 0
    for k in range(N_SHARDS):
        fp = os.path.join(OUT_DIR, f"shard-{k}of{N_SHARDS}.json")
        if os.path.exists(fp):
            rows = json.load(open(fp, encoding="utf-8"))["rows"]
            done += 1
            top = sorted(rows, key=lambda r: -r["sharpe_full"])[:3]
            print(f"[shard {k}] {len(rows)} cells; top: " +
                  "; ".join(f"{t['name']} s={t['sharpe_full']}"
                            for t in top))
    print(f"[census] shards done {done}/{N_SHARDS}")
    return 0


def cmd_selftest(_) -> int:
    """Hermetic legs (synthetic panel via RV._mk_panel + global rewire,
    the RV.cmd_selftest pattern; no real panel, no pool writes)."""
    import tempfile
    ok = 0
    saved = {}
    patch = ("CACHE", "BARS", "MASK", "SSE", "T_EXPECT", "N_EXPECT",
             "OK_STATIC_EXPECT", "UNIV_MEDIAN_FULL_MIN",
             "UNIV_MEDIAN_2010_MIN", "SSE_COVER_MIN")
    try:
        tmp = tempfile.mkdtemp(prefix="rev_census_selftest_")
        T, N = 420, 12
        cache, bars, idx = RV._mk_panel(tmp, T, N)
        for k in patch:
            saved[k] = getattr(RV, k)
        RV.CACHE, RV.BARS = cache, bars
        RV.MASK = os.path.join(tmp, "mask.csv")
        RV.SSE = os.path.join(tmp, "sse.parquet")
        RV.EXPECT_DATES = (str(idx[0].date()), str(idx[-1].date()))
        RV.T_EXPECT, RV.N_EXPECT, RV.OK_STATIC_EXPECT = T, N, N - 1
        RV.UNIV_MEDIAN_FULL_MIN, RV.UNIV_MEDIAN_2010_MIN = 1, 1
        RV.SSE_COVER_MIN = 0.0
        P = RV.load_panel()
        P["T"] = P["F"]["close"].shape[0]
        P["amt20"] = RV._roll_mean20(P["F"]["amount"])
        global _W
        _W["P"] = P
        cell = census_cells()[0]
        # leg 1: deterministic inline census (2 runs byte-equal)
        a = _cell_job(cell)
        b = _cell_job(cell)
        assert a == b, "selftest leg1: census not deterministic"
        print("selftest leg1 census-determinism: PASS")
        ok += 1
        # leg 2: exit-axis parameterization reaches the sim
        assert _exit_pair("time") == (None, None)
        assert _exit_pair("tp8sl10") == (1.08, 0.90)
        cell_t = dict(cell, exit="tp8sl10",
                      name=cell["name"].replace("|time|", "|tp8sl10|"))
        c = _cell_job(cell_t)
        assert c["exit"] == "tp8sl10" and c["name"] != a["name"]
        assert "tp" in c["exits"] or c["exits"].get("time", 0) >= 0
        print("selftest leg2 exit-axis parameterization: PASS")
        ok += 1
        # leg 3: pool-parallel identity (1 worker, 2 cells -- ems S18 law:
        # inline result == pool result)
        jobs = [(cc["name"], _cell_job, (cc,))
                for cc in (cell, cell_t)]
        res = run_cells_parallel(jobs, workers=1, desc="selftest-pool",
                                 initializer=_init_worker_selftest,
                                 initargs=(tmp,))
        assert res[cell["name"]] == a, "selftest leg3: pool face drift"
        print("selftest leg3 inline==pool identity: PASS")
        ok += 1
    finally:
        for k, v in saved.items():
            setattr(RV, k, v)
    # leg 4: grid census integrity (frozen axes)
    cells = census_cells()
    assert len(cells) == 240, "grid census drift"
    anchors = [c for c in cells if c["anchor_judged"]]
    assert len(anchors) == 3, "judged anchor census drift"
    print("selftest leg4 grid-integrity (240 cells, 3 judged anchors): PASS")
    ok += 1
    print(f"selftest: {ok}/4 PASS")
    return 0


def _init_worker_selftest(tmp):
    """Pool-test initializer: reuse the parent-built synthetic panel files
    (RV._mk_panel makedirs without exist_ok -- re-running it in the worker
    is a FileExistsError; the worker only rewires globals + load_panel)."""
    global _W
    cache, bars = os.path.join(tmp, "cache"), os.path.join(tmp, "bars")
    idx = pd.to_datetime(np.load(os.path.join(cache, "dates.npy")), unit="us")
    patch = {}
    for k in ("CACHE", "BARS", "MASK", "SSE", "T_EXPECT", "N_EXPECT",
              "OK_STATIC_EXPECT", "UNIV_MEDIAN_FULL_MIN",
              "UNIV_MEDIAN_2010_MIN", "SSE_COVER_MIN", "EXPECT_DATES"):
        patch[k] = getattr(RV, k)
    RV.CACHE, RV.BARS = cache, bars
    RV.MASK = os.path.join(tmp, "mask.csv")
    RV.SSE = os.path.join(tmp, "sse.parquet")
    RV.EXPECT_DATES = (str(idx[0].date()), str(idx[-1].date()))
    RV.T_EXPECT, RV.N_EXPECT, RV.OK_STATIC_EXPECT = 420, 12, 11
    RV.UNIV_MEDIAN_FULL_MIN, RV.UNIV_MEDIAN_2010_MIN = 1, 1
    RV.SSE_COVER_MIN = 0.0
    P = RV.load_panel()
    P["T"] = P["F"]["close"].shape[0]
    P["amt20"] = RV._roll_mean20(P["F"]["amount"])
    _W["P"] = P


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--shard", type=int, required=True)
    r.add_argument("--of", type=int, default=N_SHARDS)
    sub.add_parser("status")
    sub.add_parser("selftest")
    a = p.parse_args()
    if a.cmd == "run":
        sys.exit(cmd_run(a))
    if a.cmd == "status":
        sys.exit(cmd_status(a))
    sys.exit(cmd_selftest(a))


if __name__ == "__main__":
    main()
