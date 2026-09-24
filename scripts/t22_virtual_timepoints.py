"""T-22 rolling-all-startpoints virtual-timepoint mass validation (CEO order
O-20260924-1532 history-as-virtual-timepoints; GM dispatch O-20260924-1730
s3.1 shard takeover, claimant bm-b stalled -> bm-c starts shards).

Preregistered in research/shortline/T22_VIRTUAL_TIMEPOINTS.md BEFORE the run
(frozen pre-run commit; no threshold/seed changes after results). Scales the
P-5/P-5B K=50 random-start inspection (frozen 0.70 beat-passive caliber) to
ALL eligible startpoints on (a) the legacy 2020-anchored core48 axis (control
batch, no GF dependency, spec deliverable-5 may start first) and (b) the
T-18 deep axis (growing-membership 2013 panel, GF gate resolved by T-19
stage-3 r59). Same per-cell pipeline as P-5 (anchor gate -> causal entry
signals on full panel -> engine forward run with real T+1/13bp/exits ->
same-window EW passive benchmark), windows extended to {6m, 12m, 24m}, both
cost faces (base V1 legacy + x2 stress via science_gates.CostPatch).

Cross-round discipline (R41): detached background run, per-cell JSONL
checkpoint under results/t22/, resume = skip recorded cell keys, shard
split by enumerated-position range (identical enumeration on every machine
-> no coordination math). Workers = parallel_runner.worker_cap() (floor
cores x 0.8, RAM-guarded) at BelowNormal priority per O-1136 full-load pool.

Ledger + aggregation happen in `finalize` (separate step once shards
complete): every window x trader x startpoint cell is a counted trial;
append_ledger with actual counts only, no hand-copied prev totals.

Usage:
  python scripts/t22_virtual_timepoints.py run --axis legacy --shard c1 \
      [--pos-from N --pos-to M] [--faces base,x2] [--limit K] [--workers N]
  python scripts/t22_virtual_timepoints.py status
  python scripts/t22_virtual_timepoints.py selftest                (offline)
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

WARMUP_TD = 252          # P-5 caliber: signal warmup bars before a startpoint
W6M, W12M, W24M = 126, 252, 504
MIN_LISTED = 24          # P-5 caliber
BEAT_LINE = 0.70         # P-5/P-5B frozen beat-passive line (prereg s4)
DD_RED_LINE = -0.35      # P-5 frozen dd red line (prereg s4)
FACES = ("base", "x2")
OUT_DIR = os.path.join("results", "t22")
TICKET = "T-2026-09-24-22"

# ---------------------------------------------------------------- enumeration

def enumerate_starts(idx_len: int, listed: pd.Series):
    """All eligible startpoint panel positions, deterministic order.
    Eligible (P-5 s2 caliber, full-enumeration variant): pos >= WARMUP_TD,
    at least W6M bars ahead, listed member count >= MIN_LISTED at pos."""
    return [p for p in range(WARMUP_TD, idx_len - W6M + 1)
            if int(listed.iloc[p]) >= MIN_LISTED]


def regime_proxy(close_sym: pd.Series) -> pd.Series:
    """Frozen 3-way regime proxy (prereg s3): 510300 close vs MA200.
    bear = close < MA200; chop = close >= MA200 and MA200 <= its value 20
    bars ago; bull = close >= MA200 and MA200 rising. Warmup NaN = 'na'.
    This is a disclosed PROXY, distinct from REGIME_GUARD v3 replay (2020+
    only) -- used purely as a reporting segment, never as a gate."""
    ma200 = close_sym.rolling(200).mean()
    prev = ma200.shift(20)
    state = pd.Series("na", index=close_sym.index, dtype=object)
    valid = ma200.notna() & prev.notna()
    bear = valid & (close_sym < ma200)
    chop = valid & (close_sym >= ma200) & (ma200 <= prev)
    bull = valid & (close_sym >= ma200) & (ma200 > prev)
    state[bear] = "bear"
    state[chop] = "chop"
    state[bull] = "bull"
    return state

# ------------------------------------------------------------------ checkpoint

def shard_path(axis: str, face: str, shard: str) -> str:
    return os.path.join(OUT_DIR, f"cells_{axis}_{face}_{shard}.jsonl")


def load_done_keys(path: str) -> set:
    """Cell keys already recorded; tolerates a truncated trailing line
    (crash mid-append) by ignoring an unparseable last line."""
    keys = set()
    if not os.path.exists(path):
        return keys
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    for i, ln in enumerate(lines):
        if not ln.strip():
            continue
        try:
            keys.add(json.loads(ln)["key"])
        except (json.JSONDecodeError, KeyError):
            if i == len(lines) - 1:
                continue  # truncated tail from a crash: skip honestly
            raise  # corrupt mid-file = data integrity problem, do not hide
    return keys

# ------------------------------------------------------------ worker machinery

_G = {}  # per-worker globals, built once by _init_worker


def _init_worker(axis: str, log_path: str):
    import psutil
    pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
    if pri is not None:
        try:
            psutil.Process().nice(pri)   # O-1136 full-load low-priority pool
        except Exception:
            pass
    from live.paper import (PAPER_LEVELS, SIGNAL_BUILDERS, build_panels,
                            load_core)
    from firm.hr import TRADERS_DIR, load_trader
    prices = load_core()
    P = build_panels(prices)
    close = P["close"]
    traders = []
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        if t.get("level") in PAPER_LEVELS:
            traders.append(t)
    entries, params_by_id, exits_by_id = {}, {}, {}
    for t in traders:
        entries[t["id"]] = SIGNAL_BUILDERS[t["params"]["entry"]](P)
        params_by_id[t["id"]] = {k: v for k, v in t["params"].items()
                                 if k != "entry"}
        exits_by_id[t["id"]] = t.get("exit_overrides")
    reg = None
    if "510300" in close.columns:
        reg = regime_proxy(close["510300"])
    _G.update(prices=prices, close=close, idx=close.index,
              traders=[t["id"] for t in traders], entries=entries,
              params_by_id=params_by_id, exits_by_id=exits_by_id, regime=reg)


def _slice_metrics(eq: pd.Series, trades: list, k: int) -> dict:
    from engine.metrics import max_drawdown, sharpe
    seg = eq.iloc[:min(k, len(eq))]
    if len(seg) < 2:
        return {"ret": 0.0, "sharpe": 0.0, "dd": 0.0, "trades": 0,
                "n_bars": len(seg)}
    end = seg.index[-1]
    return {"ret": round(float(seg.iloc[-1] / seg.iloc[0] - 1), 6),
            "sharpe": round(float(sharpe(seg)), 4),
            "dd": round(float(max_drawdown(seg)), 4),
            "trades": sum(1 for tr in trades
                          if pd.Timestamp(tr["date"]) <= end),
            "n_bars": int(len(seg))}


def _run_cell(trader_id: str, pos: int, face: str) -> dict:
    """One (trader, startpoint, cost-face) cell. Runs the LONGEST window once
    (24m) and slices 6m/12m/24m metrics off the same equity curve (P-5
    pattern); passive = EW buy&hold of members listed at the start over the
    identical span. Returns a plain-dict row (small, picklable)."""
    from engine import run_backtest
    from live.paper import ExitPatch
    from science_gates import COST_X2_RATE, CostPatch
    prices = _G["prices"]
    close = _G["close"]
    idx = _G["idx"]
    entry = _G["entries"][trader_id]
    exit_sig = entry <= 0
    params = _G["params_by_id"][trader_id]
    sdate = idx[pos]
    e = idx[min(pos + W24M - 1, len(idx) - 1)]
    window = {s: df[(df.index >= sdate) & (df.index <= e)]
              for s, df in prices.items()}
    with ExitPatch(_G["exits_by_id"][trader_id]):
        if face == "x2":
            with CostPatch(COST_X2_RATE):
                res = run_backtest(window, params, entry_signal=entry,
                                   exit_signal=exit_sig)
        else:
            res = run_backtest(window, params, entry_signal=entry,
                               exit_signal=exit_sig)
    widx = idx[pos:pos + W24M][:len(res["equity_curve"])]
    eq = pd.Series(res["equity_curve"], index=widx)
    m6 = _slice_metrics(eq, res["trades"], W6M)
    m12 = _slice_metrics(eq, res["trades"], W12M)
    m24 = _slice_metrics(eq, res["trades"], W24M)
    syms = close.columns[close.loc[sdate].notna()]
    base = close.loc[sdate, syms]
    rel = (close.loc[sdate:e, syms] / base).mean(axis=1)
    p6 = _slice_metrics(rel, [], W6M)
    p12 = _slice_metrics(rel, [], W12M)
    p24 = _slice_metrics(rel, [], W24M)
    reg = "na"
    if _G["regime"] is not None:
        reg = str(_G["regime"].loc[sdate])
    return {"key": f"{trader_id}|{pos}", "trader": trader_id, "pos": pos,
            "start": str(sdate.date()), "face": face, "regime": reg,
            "n_listed": int(len(syms)),
            "partial_12m": m12["n_bars"] < W12M,
            "partial_24m": m24["n_bars"] < W24M,
            "ret_6m": m6["ret"], "ret_12m": m12["ret"], "ret_24m": m24["ret"],
            "p_ret_6m": p6["ret"], "p_ret_12m": p12["ret"],
            "p_ret_24m": p24["ret"],
            "dd_6m": m6["dd"], "dd_12m": m12["dd"], "dd_24m": m24["dd"],
            "sharpe_6m": m6["sharpe"], "sharpe_12m": m12["sharpe"],
            "sharpe_24m": m24["sharpe"],
            "trades_6m": m6["trades"], "trades_12m": m12["trades"],
            "trades_24m": m24["trades"],
            "beat_6m": m6["ret"] > p6["ret"],
            "beat_12m": m12["ret"] > p12["ret"],
            "beat_24m": m24["ret"] > p24["ret"]}

# ------------------------------------------------------------------- run mode

def _log(log_path: str, msg: str):
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(f"{stamp} {msg}\n")


def cmd_run(args) -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUT_DIR, "logs"), exist_ok=True)
    log_path = os.path.join(OUT_DIR, "logs", f"{args.axis}_{args.shard}.log")
    if os.environ.get("T22_DETACHED") == "1":
        sys.stdout = open(log_path, "a", buffering=1, encoding="utf-8")
        sys.stderr = sys.stdout
    t0 = time.time()
    _log(log_path, f"[{args.shard}] T-22 run start axis={args.axis} "
                   f"faces={args.faces} pos=[{args.pos_from},{args.pos_to})")
    # anchor gate first (P-5 caliber: any drift = batch void, exit 3)
    from live.paper import PAPER_LEVELS, anchor_gate, build_panels, load_core
    from firm.hr import TRADERS_DIR, load_trader
    prices = load_core()
    n_anchor_fail = 0
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        if t.get("level") not in PAPER_LEVELS:
            continue
        a = anchor_gate(t, prices)
        _log(log_path, f"anchor {t['id']}: {'PASS' if a['ok'] else 'FAIL'}")
        if not a["ok"]:
            n_anchor_fail += 1
    if n_anchor_fail:
        _log(log_path, f"ANCHOR-GATE FAIL x{n_anchor_fail} -- batch void "
                       f"(trader JSONs untouched)")
        return 3
    del prices

    P = build_panels(load_core())
    close = P["close"]
    idx = close.index
    listed = close.notna().sum(axis=1)
    eligible = enumerate_starts(len(idx), listed)
    n_elig = len(eligible)
    shard = eligible[args.pos_from:args.pos_to]
    if args.limit:
        shard = shard[:args.limit]
    if not shard:
        _log(log_path, "nothing to do (empty shard range)")
        return 0
    _log(log_path, f"panel {idx[0].date()}->{idx[-1].date()} "
                   f"eligible={n_elig} shard_positions={len(shard)} "
                   f"first={idx[shard[0]].date()} last={idx[shard[-1]].date()}")
    traders = []
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        if t.get("level") in PAPER_LEVELS:
            traders.append(t["id"])
    faces = [f.strip() for f in args.faces.split(",") if f.strip() in FACES]
    jobs = []
    paths = {}
    for face in faces:
        p = shard_path(args.axis, face, args.shard)
        paths[face] = p
        done = load_done_keys(p)
        for pos in shard:
            for tid in traders:
                if f"{tid}|{pos}" in done:
                    continue
                jobs.append((tid, pos, face))
    _log(log_path, f"cells todo={len(jobs)} (resume-skipped="
                   f"{len(shard) * len(traders) * len(faces) - len(jobs)})")
    if not jobs:
        _log(log_path, "all cells already checkpointed -- no-op")
        return 0

    import psutil
    pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
    if pri is not None:
        try:
            psutil.Process().nice(pri)
        except Exception:
            pass
    from parallel_runner import worker_cap
    workers = args.workers or worker_cap()
    from concurrent.futures import ProcessPoolExecutor, as_completed
    done_ct, t_last = 0, time.time()
    handles = {face: open(paths[face], "a", encoding="utf-8")
               for face in faces}
    try:
        with ProcessPoolExecutor(max_workers=workers,
                                 initializer=_init_worker,
                                 initargs=(args.axis, log_path)) as pool:
            futs = {pool.submit(_run_cell, tid, pos, face): (tid, pos, face)
                    for tid, pos, face in jobs}
            for fut in as_completed(futs):
                row = fut.result()
                fh = handles[row["face"]]
                fh.write(json.dumps(row, default=bool) + "\n")
                fh.flush()
                done_ct += 1
                if time.time() - t_last > 30:
                    _log(log_path, f"progress {done_ct}/{len(jobs)} cells")
                    t_last = time.time()
    finally:
        for fh in handles.values():
            fh.close()
    runtime = round(time.time() - t0, 1)
    marker = {"shard": args.shard, "axis": args.axis, "faces": faces,
              "cells_written": done_ct, "cells_total": len(jobs),
              "n_eligible": n_elig, "workers": workers,
              "runtime_sec": runtime,
              "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
              "ticket": TICKET}
    with open(os.path.join(OUT_DIR, f"done_{args.axis}_{args.shard}.json"),
              "w", encoding="utf-8") as fh:
        json.dump(marker, fh, indent=2)
    _log(log_path, f"DONE {done_ct}/{len(jobs)} cells in {runtime}s "
                   f"workers={workers}")
    return 0


def cmd_status(_) -> int:
    if not os.path.isdir(OUT_DIR):
        print("no results/t22 yet")
        return 0
    for name in sorted(os.listdir(OUT_DIR)):
        path = os.path.join(OUT_DIR, name)
        if name.startswith("cells_") and name.endswith(".jsonl"):
            n = sum(1 for _ in open(path, encoding="utf-8"))
            print(f"{name}: {n} cells")
        elif name.startswith("done_"):
            print(f"{name}: {open(path, encoding='utf-8').read()[:200]}")
    return 0

# ----------------------------------------------------------------- selftest

def cmd_selftest(_) -> int:
    """Offline selftest (no engine run, no network, no real panel):
    enumeration rules, regime proxy, checkpoint resume, CostPatch restore,
    metric slicing."""
    fails = []

    def t(name, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            fails.append(name)

    # S1/S2: enumeration determinism + eligibility rules on synthetic panel
    idx_len = 900
    listed = pd.Series(48, index=range(idx_len))
    e1 = enumerate_starts(idx_len, listed)
    e2 = enumerate_starts(idx_len, listed)
    t("S1 enumerate deterministic + range",
      e1 == e2 and e1[0] == WARMUP_TD and e1[-1] == idx_len - W6M)
    listed2 = pd.Series(10, index=range(idx_len))
    t("S2 MIN_LISTED filter excludes",
      enumerate_starts(idx_len, listed2) == [])
    listed3 = pd.Series(10, index=range(idx_len))
    listed3.iloc[:600] = 100
    e3 = enumerate_starts(idx_len, listed3)
    t("S2b listed gate boundary",
      e3 == [p for p in range(WARMUP_TD, idx_len - W6M + 1)
             if listed3.iloc[p] >= MIN_LISTED])

    # S3: regime proxy 3-way on crafted series
    up = pd.Series(np.linspace(100, 300, 600))
    dn = pd.Series(np.linspace(300, 100, 600))
    st_up = regime_proxy(up)
    st_dn = regime_proxy(dn)
    t("S3 regime warmup na + bull on rising",
      (st_up == "na").sum() == 219 and (st_up.iloc[250:] == "bull").all())
    t("S3b regime bear on close<MA200",
      (st_dn.iloc[250:] == "bear").all())
    flat = pd.Series(100.0, index=range(600))
    st_flat = regime_proxy(flat)
    t("S3c flat MA200 = chop (ma<=prev20)",
      (st_flat.iloc[250:] == "chop").all())

    # S4: checkpoint resume incl. truncated tail tolerance
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "_selftest_ckpt.jsonl")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"key": "A|1"}) + "\n")
        fh.write(json.dumps({"key": "A|2"}) + "\n")
        fh.write(json.dumps({"key": "A|3"}) + "\n")
        fh.write('{"key": "A|4", "trun')      # crash mid-line
    keys = load_done_keys(tmp)
    t("S4 resume keys skip truncated tail",
      keys == {"A|1", "A|2", "A|3"})
    os.remove(tmp)

    # S5: CostPatch restores engine.backtester.FeeSchedule identity
    import engine.backtester as eb
    from science_gates import COST_X2_RATE, CostPatch
    before = eb.FeeSchedule
    with CostPatch(COST_X2_RATE):
        inside = eb.FeeSchedule
    t("S5 CostPatch swaps inside + restores",
      inside is not before and eb.FeeSchedule is before)

    # S6: metric slicing sanity on synthetic equity
    eq = pd.Series(np.linspace(100, 120, 300),
                   index=pd.bdate_range("2020-01-01", periods=300))
    m = _slice_metrics(eq, [], 126)
    expect_ret = float(eq.iloc[125] / eq.iloc[0] - 1)
    t("S6 slice metrics monotonic-up",
      abs(m["ret"] - expect_ret) < 1e-6 and m["dd"] == 0.0
      and m["n_bars"] == 126)

    # S7: faces constant
    t("S7 faces tuple", FACES == ("base", "x2") and COST_X2_RATE > 0)

    print(f"\nselftest: {'ALL PASS' if not fails else 'FAIL x' + str(len(fails))}")
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--axis", choices=["legacy", "deep"], required=True)
    r.add_argument("--shard", required=True)
    r.add_argument("--pos-from", type=int, default=0)
    r.add_argument("--pos-to", type=int, default=10**9)
    r.add_argument("--faces", default="base,x2")
    r.add_argument("--limit", type=int, default=0)
    r.add_argument("--workers", type=int, default=0)
    sub.add_parser("status")
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "status":
        return cmd_status(args)
    return cmd_selftest(args)


if __name__ == "__main__":
    sys.exit(main())
