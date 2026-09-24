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


def _load_axis_prices(axis: str) -> dict:
    """Axis price source (r82 bm-a fix-forward, J18: implementation repair
    only, prereg s2 judgments untouched). legacy = core48 CSVs (load_core);
    deep = T-18 panel window (manifest frozen) with the T-19 adjusted view
    as the price source for the 19 consolidation-affected members -- GF
    law: return face fixed, raw face authoritative elsewhere. Caller must
    have run `scripts/t18_deep_axis.py build` locally (idempotent, sha gate).
    """
    from live.paper import load_core
    if axis == "legacy":
        return load_core()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    man_path = os.path.join(root, "results", "shortline",
                            "t18_deep_manifest.json")
    man = json.load(open(man_path, encoding="utf-8"))
    assert man.get("verdict") == "PASS", "T22-GATE: t18 manifest != PASS"
    bad = [c for c, m in man["members"].items() if not m.get("pass")]
    assert not bad, f"T22-GATE: t18 members fail: {bad}"
    lo = pd.Timestamp(man["panel_start"])
    hi = pd.Timestamp(man["evidence_cutoff"])
    ohlcv_dir = os.path.join(root, "Money02", "data", "cache",
                             "t18_deep_panel", "ohlcv")
    adj_dir = os.path.join(root, "data", "consolidation", "adjusted_view")
    prices, adj_used = {}, []
    for code in sorted(man["members"]):
        vpath = os.path.join(adj_dir, code + ".parquet")
        src = vpath if os.path.exists(vpath) else os.path.join(
            ohlcv_dir, code + ".parquet")
        df = pd.read_parquet(src)
        if "date" in df.columns:
            df = df.set_index("date")
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)   # twin face: string dates
        df = df.sort_index()
        df = df.loc[(df.index >= lo) & (df.index <= hi)]
        assert df.index.is_monotonic_increasing \
            and not df.index.duplicated().any()
        df = df[["open", "high", "low", "close", "volume"]].copy()
        # paper.py L135 canonical fallback (t18 cache carries no amount;
        # no in-register entry builder consumes amount -- disclosed proxy)
        df["amount"] = df["volume"] * df["close"]
        prices[code] = df
        if src == vpath:
            adj_used.append(code)
    assert len(adj_used) == 19, \
        f"T22-GATE: adjusted view {len(adj_used)}/19 -- GF hard gate"
    return prices


def _init_worker(axis: str, log_path: str):
    import psutil
    pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
    if pri is not None:
        try:
            psutil.Process().nice(pri)   # O-1136 full-load low-priority pool
        except Exception:
            pass
    from live.paper import (PAPER_LEVELS, SIGNAL_BUILDERS, build_panels)
    from firm.hr import TRADERS_DIR, load_trader
    prices = _load_axis_prices(axis)
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
            # r82 bm-a fix-forward (J18): CostPatch takes a MULTIPLIER
            # (G2 convention CostPatch(2), ce_transfer/combined_exit
            # precedent). COST_X2_RATE is the resulting stressed single-
            # side RATE (0.0026082), not the multiplier -- passing it here
            # multiplied all fee fields BY 0.0026 (near-zero fees), which
            # inverted the x2 stress face. Judgments unchanged (prereg s3).
            with CostPatch(2.0):
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

    P = build_panels(_load_axis_prices(args.axis))   # r82 fix: axis-aware
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

# ------------------------------------------------------------------ finalize

LEGACY_CUTOFF = "2026-09-23"   # prereg s2: legacy axis panel end at run time
BATCH_CUTOFF = "2026-09-22"    # binding cutoff (deep manifest, min of axes)
BOOTSTRAP_B = 2000             # prereg s4: binomial bootstrap, frozen
BOOTSTRAP_SEED = 20260924      # frozen seed, disclosed in output
SUBSAMPLE_STEP = 25            # prereg s4: 25td de-overlap subsample
WINDOWS = {"6m": W6M, "12m": W12M, "24m": W24M}
CANON_FILES = {
    ("legacy", "base"): ["cells_legacy_base_c1.jsonl"],
    ("legacy", "x2"): ["cells_legacy_x2_c1.jsonl"],
    ("deep", "base"): ["cells_deep_base_d-a1.jsonl",
                       "cells_deep_base_d-c1.jsonl"],
    ("deep", "x2"): ["cells_deep_x2_d-a1.jsonl",
                     "cells_deep_x2_d-c1.jsonl"],
}
REPRO_FILE = "cells_deep_base_dprobe.jsonl"   # 12 reproduction cells (r82 probe)
_COMPARE_FIELDS = ("ret_6m", "ret_12m", "ret_24m", "p_ret_6m", "p_ret_12m",
                   "p_ret_24m", "dd_6m", "dd_12m", "dd_24m", "sharpe_6m",
                   "sharpe_12m", "sharpe_24m", "trades_6m", "trades_12m",
                   "trades_24m", "beat_6m", "beat_12m", "beat_24m")


def _bootstrap_ci(k: int, n: int):
    """Binomial bootstrap 95% CI on the beat rate (prereg s4, B/seed frozen).
    Fresh seeded rng per cell -> each CI independently reproducible."""
    if n == 0:
        return None, None, None
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draws = rng.binomial(n, k / n, BOOTSTRAP_B) / n
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return round(float(lo), 4), round(float(hi), 4), round(float(hi - lo), 4)


def _agg(rows, wname):
    """One (trader, face, window) aggregate on the COMPLETE-window subset
    (prereg s3: partial windows flagged, main read on full-window subset;
    all-window face disclosed in parallel)."""
    pflag = {"6m": None, "12m": "partial_12m", "24m": "partial_24m"}[wname]
    full = [r for r in rows if pflag is None or not r.get(pflag)]
    partial_n = len(rows) - len(full)
    n, k, dds, trades = len(full), 0, [], 0
    seg = {}
    for r in full:
        k += int(bool(r[f"beat_{wname}"]))
        dds.append(float(r[f"dd_{wname}"]))
        trades += int(r[f"trades_{wname}"])
        s = r.get("regime", "na")
        b = seg.setdefault(s, {"n": 0, "k": 0, "dds": []})
        b["n"] += 1
        b["k"] += int(bool(r[f"beat_{wname}"]))
        b["dds"].append(float(r[f"dd_{wname}"]))
    rate = k / n if n else None
    min_dd = min(dds) if dds else None
    starts = sorted({r["start"] for r in full})
    covered_years = (round((pd.Timestamp(starts[-1])
                            - pd.Timestamp(starts[0])).days / 365.25, 2)
                     if starts else None)
    n_regime, last = 0, None
    for r in sorted(full, key=lambda r: (r["pos"], r["trader"])):
        s = r.get("regime", "na")
        if s != last:
            n_regime += 1
            last = s
    ci_lo, ci_hi, ci_w = _bootstrap_ci(k, n)
    all_dds = [float(r[f"dd_{wname}"]) for r in rows]
    all_k = sum(1 for r in rows if r[f"beat_{wname}"])
    segments = {s: {"n": b["n"], "beat_rate": round(b["k"] / b["n"], 4),
                    "min_dd": round(min(b["dds"]), 4)}
                for s, b in sorted(seg.items())}
    return {"n": n, "beats": k,
            "beat_rate": round(rate, 4) if rate is not None else None,
            "min_dd": round(min_dd, 4) if min_dd is not None else None,
            "mean_dd": round(sum(dds) / len(dds), 4) if dds else None,
            "oos_trades": trades, "covered_years": covered_years,
            "independent_regime_windows": n_regime,
            "ci95_lo": ci_lo, "ci95_hi": ci_hi, "ci95_width": ci_w,
            "partial_n": partial_n,
            "all_windows": {"n": len(rows),
                            "beat_rate": round(all_k / len(rows), 4)
                            if rows else None,
                            "min_dd": round(min(all_dds), 4)
                            if all_dds else None},
            "segments": segments,
            "verdict": (bool(rate is not None and rate >= BEAT_LINE
                             and min_dd is not None
                             and min_dd >= DD_RED_LINE) if n else None)}


def _pooled(rows, wname, keyfn):
    """Pooled beat rate by a row key (regime segment / start-year cohort)."""
    out = {}
    for r in rows:
        g = out.setdefault(keyfn(r), {"n": 0, "k": 0})
        g["n"] += 1
        g["k"] += int(bool(r[f"beat_{wname}"]))
    return {s: {"n": v["n"], "beat_rate": round(v["k"] / v["n"], 4)}
            for s, v in sorted(out.items())}


def _sub_rate(rows, wname):
    """Beat rate on the 25td-spaced start subsample (prereg s4 de-overlap
    robustness disclosure), complete-window subset only."""
    pflag = {"6m": None, "12m": "partial_12m", "24m": "partial_24m"}[wname]
    sub = [r for r in rows if r["pos"] % SUBSAMPLE_STEP == 0
           and (pflag is None or not r.get(pflag))]
    if not sub:
        return None
    return round(sum(1 for r in sub if r[f"beat_{wname}"]) / len(sub), 4)


def cmd_finalize(_) -> int:
    t0 = time.time()
    print("=== T-22 axis finalize (prereg s3/s6) ===")
    from live.paper import PAPER_LEVELS, build_panels, load_core
    from firm.hr import TRADERS_DIR, load_trader
    live_ids = set()
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        if t.get("level") in PAPER_LEVELS:
            live_ids.add(t["id"])

    # 1) load canonical cells; corrupt line anywhere = integrity abort
    cells, corrupt, dup_reports = {}, 0, []
    cells_audit = {"files": {}, "corrupt": corrupt}
    for (axis, face), names in sorted(CANON_FILES.items()):
        union, seen = [], set()
        for name in names:
            path = os.path.join(OUT_DIR, name)
            if not os.path.exists(path):
                print(f"finalize: missing shard {path} -- abort")
                return 2
            n_rows = 0
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        r = json.loads(line)
                    except json.JSONDecodeError:
                        corrupt += 1
                        continue
                    n_rows += 1
                    if r["key"] in seen:
                        dup_reports.append(r["key"])
                        continue
                    seen.add(r["key"])
                    union.append(r)
            cells_audit["files"][name] = n_rows
        cells[(axis, face)] = union
    if corrupt:
        print(f"finalize: {corrupt} corrupt line(s) -- abort")
        return 2
    if dup_reports:
        print(f"finalize: {len(dup_reports)} unexpected duplicate key(s) "
              f"inside canonical shards -- integrity abort")
        return 2

    # 2) reproduction gate: dprobe 12 rows must equal canonical deep-base
    repro_path = os.path.join(OUT_DIR, REPRO_FILE)
    repro_n, repro_match = 0, 0
    deep_base_idx = {r["key"]: r for r in cells[("deep", "base")]}
    repro_bad = []
    with open(repro_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rp = json.loads(line)
            repro_n += 1
            orig = deep_base_idx.get(rp["key"])
            if orig is None:
                repro_bad.append(f"{rp['key']}: no canonical counterpart")
                continue
            diff = [f for f in _COMPARE_FIELDS
                    if orig.get(f) != rp.get(f)]
            if diff:
                repro_bad.append(f"{rp['key']}: field drift {diff[:3]}")
            else:
                repro_match += 1
    cells_audit["reproductions"] = {"n": repro_n, "value_match": repro_match,
                                    "mismatches": repro_bad}
    if repro_n != repro_match:
        print(f"finalize: REPRODUCTION GATE FAIL ({repro_match}/{repro_n}) "
              f"-- pipeline nondeterminism or shard corruption, abort")
        return 2
    print(f"reproduction gate PASS: {repro_match}/{repro_n} bit-equal")

    # 3) census gate (r105 drift-gate law): live panel at the FROZEN cutoff
    #    must re-derive the exact start set the cells ran on
    machine = json.load(open("fleet/machine.json",
                             encoding="utf-8"))["machine_id"]
    axes_out, trials_cells, trials_passive = {}, 0, 0
    for axis in ("legacy", "deep"):
        if axis == "legacy":
            prices = load_core()
            hi = pd.Timestamp(LEGACY_CUTOFF)
            prices = {s: df[df.index <= hi] for s, df in prices.items()}
            cutoff = LEGACY_CUTOFF
        else:
            prices = _load_axis_prices(axis)
            cutoff = BATCH_CUTOFF
        P = build_panels(prices)
        listed = P["close"].notna().sum(axis=1)
        elig = enumerate_starts(len(P["close"].index), listed)
        elig_set = set(elig)
        rows_by_face = {f: cells[(axis, f)] for f in FACES}
        starts_by_face = {f: {r["pos"] for r in rows} for f, rows in
                          rows_by_face.items()}
        traders_seen = {r["trader"] for rows in rows_by_face.values()
                        for r in rows}
        ok = (traders_seen == live_ids
              and all(s == elig_set for s in starts_by_face.values()))
        n_starts = len(elig_set)
        if not ok:
            print(f"finalize: CENSUS/COVERAGE GATE FAIL on {axis} "
                  f"(starts={n_starts}, traders_ok="
                  f"{traders_seen == live_ids}) -- abort")
            return 2
        print(f"census gate PASS [{axis}]: {n_starts} starts x "
              f"{len(traders_seen)} traders x 2 faces, cutoff {cutoff}")
        trials_cells += sum(len(rows) for rows in rows_by_face.values())
        trials_passive += n_starts

        judgments = {tid: {} for tid in sorted(traders_seen)}
        for tid in judgments:
            for wname in WINDOWS:
                cell = {"window_td": WINDOWS[wname]}
                for face in FACES:
                    rows = [r for r in rows_by_face[face]
                            if r["trader"] == tid]
                    cell[face] = _agg(rows, wname)
                cell["verdict_base"] = cell["base"]["verdict"]
                cell["verdict_x2"] = cell["x2"]["verdict"]
                judgments[tid][wname] = cell
        base6 = [r for r in rows_by_face["base"]]
        axes_out[axis] = {
            "cutoff": cutoff, "n_starts": n_starts,
            "passive_windows": n_starts,
            "cells": {f: len(rows_by_face[f]) for f in FACES},
            "cells_total": sum(len(rows_by_face[f]) for f in FACES),
            "traders": sorted(traders_seen),
            "judgments": judgments,
            "segments_pooled_base_6m": _pooled(base6, "6m",
                                                lambda r: r.get("regime",
                                                                "na")),
            "start_year_cohorts_base_6m": _pooled(
                base6, "6m", lambda r: r["start"][:4]),
            "subsample_25td": {tid: {
                wname: {face: _sub_rate(
                    [r for r in rows_by_face[face] if r["trader"] == tid],
                    wname) for face in FACES} for wname in WINDOWS}
                for tid in sorted(traders_seen)},
        }

    # 4) x2 survival gate (prereg s4): any trader breaching on x2 -> flag
    x2_fail = [{"axis": ax, "trader": tid, "window": w}
               for ax in ("legacy", "deep")
               for tid, j in axes_out[ax]["judgments"].items()
               for w, cell in j.items() if cell["verdict_x2"] is False]

    # 5) predictions reconciliation (prereg s5, frozen pre-run)
    def _pooled_base6(ax):
        return round(sum(j["6m"]["base"]["beats"]
                         for j in axes_out[ax]["judgments"].values())
                     / sum(j["6m"]["base"]["n"]
                           for j in axes_out[ax]["judgments"].values()), 4)
    pooled = {ax: _pooled_base6(ax) for ax in ("legacy", "deep")}
    preds = []
    for ax in ("legacy", "deep"):
        seg = axes_out[ax]["segments_pooled_base_6m"]
        delta_x2 = {tid: round(
            (j["6m"]["x2"]["beat_rate"] or 0)
            - (j["6m"]["base"]["beat_rate"] or 0), 4)
            for tid, j in axes_out[ax]["judgments"].items()}
        cohorts = axes_out[ax]["start_year_cohorts_base_6m"]
        y25 = cohorts.get("2025", {}).get("beat_rate")
        y26 = cohorts.get("2026", {}).get("beat_rate")
        late = round((y25 + y26) / 2, 4) if y25 is not None \
            and y26 is not None else (y25 or y26)
        preds.append({
            "axis": ax,
            "p1_pooled_base_6m_in_[0.55,0.70]": bool(
                0.55 <= pooled[ax] <= 0.70),
            "p1_pooled": pooled[ax],
            "p1_majority_below_line": bool(sum(
                1 for j in axes_out[ax]["judgments"].values()
                if j["6m"]["base"]["beat_rate"] is not None
                and j["6m"]["base"]["beat_rate"] < BEAT_LINE)
                > len(axes_out[ax]["judgments"]) / 2),
            "p2_bear_gt_bull": bool(
                seg.get("bear", {}).get("beat_rate", -1)
                > seg.get("bull", {}).get("beat_rate", -1)),
            "p2_chop_weakest": bool(
                seg.get("chop", {}).get("beat_rate", 1)
                <= min([v["beat_rate"] for k, v in seg.items()
                        if k != "chop"] or [1])),
            "p3_x2_degradation_max_pp": max(
                (abs(v) for v in delta_x2.values()), default=0.0),
            "p3_cost_sensitivity_redflag": bool(any(
                v <= -0.10 for v in delta_x2.values())),
            "p4_2025plus_cohort_highest": bool(late is not None and late
                == max(v["beat_rate"] for v in cohorts.values())),
            "p4_2025plus_cohort": late,
            "cohorts": cohorts, "segments_pooled": seg,
            "x2_vs_base_delta_6m": delta_x2})

    # 6) ledger (F3): cells + passive windows, zero-assumption, no hand-copied
    #    prev; dprobe 12 reproductions NOT counted (P5C precedent)
    from science_gates import append_ledger, cutoff_meta
    batch_trials = trials_cells + trials_passive
    ledger = append_ledger(
        "T22_VIRTUAL_TIMEPOINTS", batch_trials,
        file_name="t22_virtual_timepoints.json",
        evidence_cutoff=BATCH_CUTOFF,
        note=(f"axis finalize: legacy c1 15,060 cells (bm-c canonical rerun, "
              f"dual-manifest transfer MSG-2032) + deep 18,072 unique cells "
              f"(d-c1 16,800 + d-a1 1,272, bm-a) + passive windows "
              f"{trials_passive} (1,255+1,506, P-5 per-start accounting); "
              f"dprobe 12 reproductions deduped; anchors verified at shard "
              f"run time not counted (prereg s0)"))

    # 7) outputs: JSON (top-level C2 key) + aggregated CSV (small, git)
    out_json = os.path.join("results", "t22_virtual_timepoints.json")
    out_csv = os.path.join("research", "shortline",
                           "t22_virtual_timepoints_results.csv")
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    n_csv = 0
    with open(out_csv, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("axis,trader,face,window,segment,n,beat_rate,min_dd,"
                 "mean_dd,oos_trades,ci95_width,verdict\n")
        for ax in ("legacy", "deep"):
            for tid, j in axes_out[ax]["judgments"].items():
                for w, cell in j.items():
                    for face in FACES:
                        a = cell[face]
                        rows = [("all", a["n"], a["beat_rate"], a["min_dd"],
                                 a["mean_dd"], a["oos_trades"],
                                 a["ci95_width"], a["verdict"])]
                        rows += [(s, v["n"], v["beat_rate"], v["min_dd"],
                                  None, None, None, None)
                                 for s, v in a["segments"].items()]
                        for s, n_, br, mdd, mddm, tr, ciw, vd in rows:
                            fh.write(f"{ax},{tid},{face},{w},{s},{n_},{br},"
                                     f"{mdd},{mddm},{tr},{ciw},{vd}\n")
                            n_csv += 1
    payload = {
        "batch": "T22_VIRTUAL_TIMEPOINTS",
        "evidence_cutoff": BATCH_CUTOFF,
        "cutoff_meta": cutoff_meta(BATCH_CUTOFF),
        "axis_cutoffs": {"legacy": LEGACY_CUTOFF, "deep": BATCH_CUTOFF},
        "evidence_cutoff_note": (
            "binding cutoff = deep manifest (2026-09-22); legacy axis cells "
            "ran on the 2026-09-23 panel (prereg s2 dual-cutoff disclosure)"),
        "judgment_rule": (
            "PASS iff beat_rate >= 0.70 AND min_dd >= -0.35 on the "
            "complete-window subset (P-5/P-5B frozen, prereg s4); primary "
            "read = base face 6m; x2 = survival gate; partial windows "
            "flagged, all-window face disclosed in parallel"),
        "bootstrap": {"B": BOOTSTRAP_B, "seed": BOOTSTRAP_SEED,
                      "method": "binomial percentile 95% CI"},
        "cells_audit": cells_audit,
        "axes": axes_out,
        "x2_survival_gate": {"fail_count": len(x2_fail), "fails": x2_fail},
        "predictions_vs_results": preds,
        "census_reconciliation": (
            "t22-canonical 1255 legacy starts vs p5c probe 1253 (exclusive "
            "upper bound n-1-126) vs P-5 archived 1254; both preregs frozen "
            "independently, boundary convention disclosed per P5C finalize"),
        "trials_ledger": ledger,
        "audit": {"runtime_sec": None, "machine": machine,
                  "finalize_ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                  "outputs": {"json": os.path.abspath(out_json),
                              "csv": os.path.abspath(out_csv),
                              "csv_rows": n_csv}},
    }
    payload["audit"]["runtime_sec"] = round(time.time() - t0, 1)
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False, default=bool)
    print(f"judgments: legacy pooled base 6m = {pooled['legacy']}, "
          f"deep pooled base 6m = {pooled['deep']}")
    print(f"trials: {trials_cells} cells + {trials_passive} passive "
          f"= {batch_trials}; ledger total -> {ledger['total']}")
    print(f"finalize DONE in {payload['audit']['runtime_sec']}s "
          f"-> {out_json} + {out_csv} ({n_csv} rows)")
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

    # S5b (r82 bm-a fix-forward regression): the x2 face must STRESS costs
    # strictly -- the stressed commission inside the patch == 2x base.
    # Catches the J14-adjacent trap of passing a RATE where a MULTIPLIER
    # is expected (near-zero fees = inverted stress face).
    base_fee = eb.FeeSchedule()
    with CostPatch(2.0):
        stressed_fee = eb.FeeSchedule()
        doubled = (stressed_fee.commission_rate == base_fee.commission_rate * 2
                   and stressed_fee.slippage_a == base_fee.slippage_a * 2)
    t("S5b CostPatch(2.0) doubles fee fields (direction gate)",
      doubled and eb.FeeSchedule().commission_rate == base_fee.commission_rate)

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

    # S8: finalize aggregation on synthetic rows (verdict + partial split
    # + segment buckets); 6m has no partial flag by construction
    rows = []
    for i, (beat, dd, reg) in enumerate([
            (True, -0.01, "bull"), (False, -0.50, "bear"),
            (True, -0.02, "bull"), (True, -0.03, "chop"),
            (False, -0.01, "bear"), (False, -0.02, "bull")]):
        rows.append({"key": f"T|{i}", "trader": "T", "pos": i,
                     "start": f"2021-01-0{i+1}", "face": "base",
                     "regime": reg, "beat_6m": beat, "dd_6m": dd,
                     "trades_6m": 3, "beat_12m": beat, "dd_12m": dd,
                     "trades_12m": 5, "partial_12m": False,
                     "beat_24m": beat, "dd_24m": dd, "trades_24m": 5,
                     "partial_24m": i >= 4})
    a = _agg(rows, "6m")
    t("S8 agg beat_rate/min_dd/verdict",
      a["n"] == 6 and a["beats"] == 3 and abs(a["beat_rate"] - 0.5) < 1e-9
      and a["min_dd"] == -0.5 and a["verdict"] is False
      and a["segments"]["bull"]["n"] == 3
      and a["segments"]["bear"]["beat_rate"] == 0.0)
    a12 = _agg(rows, "12m")
    t("S8b partial split (12m full / 24m drops 2)",
      a12["n"] == 6 and _agg(rows, "24m")["n"] == 4
      and _agg(rows, "24m")["partial_n"] == 2)
    t("S8c oos_trades + covered_years + regime runs",
      a["oos_trades"] == 18 and a["covered_years"] == 0.01
      and a["independent_regime_windows"] == 6)

    # S9: bootstrap CI determinism (frozen seed) + width sanity
    lo1, hi1, w1 = _bootstrap_ci(7, 10)
    lo2, hi2, w2 = _bootstrap_ci(7, 10)
    t("S9 bootstrap deterministic + sane width",
      (lo1, hi1) == (lo2, hi2) and 0 < w1 <= 1
      and _bootstrap_ci(0, 10)[0] == 0.0
      and _bootstrap_ci(10, 10)[1] == 1.0)

    # S10: pooled-by-key grouping
    pooled = _pooled(rows, "6m", lambda r: r["regime"])
    t("S10 pooled segment counts",
      pooled["bull"]["n"] == 3 and pooled["bull"]["beat_rate"] > 0
      and pooled["bear"]["beat_rate"] == 0.0
      and sum(v["n"] for v in pooled.values()) == 6)

    # S11: verdict gate semantics mirror P-5 frozen line
    t("S11 frozen judgment constants",
      BEAT_LINE == 0.70 and DD_RED_LINE == -0.35
      and WINDOWS == {"6m": 126, "12m": 252, "24m": 504}
      and SUBSAMPLE_STEP == 25 and BOOTSTRAP_B == 2000)

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
    sub.add_parser("finalize")
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "finalize":
        return cmd_finalize(args)
    return cmd_selftest(args)


if __name__ == "__main__":
    sys.exit(main())
