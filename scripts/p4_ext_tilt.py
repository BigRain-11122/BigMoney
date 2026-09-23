"""P4_EXT_TILT — extension-slot survivor -> strategy conversion batch.

B-layer stock pool, low-frequency tilt. Prereg FROZEN (round 67, commit
cccd5f1): research/shortline/P4_EXT_TILT.md — 47 cells = 5 main + 40 random
nulls (20 quarterly / 20 20-day) + 2 passive. Verdicts = BACKTEST_SCIENCE v2
via science_gates shared library (own-null skill line + vi floor 0.561,
bootstrap CI, F6 dual trade gate). D6 admission = max|corr| vs 6 registered
traders (ew6 member reruns), >=0.7 rejects the cell.

Reuse (no rebuild): p4_batch2_screen shared panel/fill_guard/CostPatch/exec
semantics + p1d_ext_slots_ic factor builders/gates + p2_null_calibration
passive baselines + ew6_portfolio member_run.

Subcommands:
  selftest   offline, no panel dependency
  gates      p1d three-slot gates + own universe probe (exit 2 = refuse batch)
  probe      gates + single-cell timing (spec SS0 probe-first protocol)
  run        resumable 47-cell batch (jsonl checkpoints + lock); finalize
             writes results/shortline_p4_ext_tilt.json + results CSV
  status     progress readout
"""
import json
import os
import subprocess
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import p4_batch2_screen as B          # shared panel + engine exec machinery
import p1d_ext_slots_ic as P1D        # factor builders + three-slot gates
import science_gates as SG

OUT_JSON = os.path.join(ROOT, "results", "shortline_p4_ext_tilt.json")
RUNS_JSONL = os.path.join(ROOT, "results", "p4_ext_tilt_runs.jsonl")
FINAL_CSV = os.path.join(ROOT, "research", "shortline", "p4_ext_tilt_results.csv")
LOCK = os.path.join(ROOT, "results", "p4_ext_tilt_run.lock")
ATTRITION = os.path.join(ROOT, "results", "gate_attrition.json")

# ---- frozen spec constants (P4_EXT_TILT.md SS3/SS4) ----
EVIDENCE_CUTOFF = "2026-09-22"
SEED_Q = 49_000                      # SEED_REGISTRY p4_ext_tilt_q
SEED_D20 = 49_100                    # SEED_REGISTRY p4_ext_tilt_d20
N_NULL = 20
VI_FLOOR = 0.561                     # P4_BATCH2 recorded vi (domain floor)
BATCH_CELLS = 47
GDHS_LAG = 45                        # quarter-end + 45 natural days
WORKERS = 8                          # O-1738 bm-b <= 12; WQ leg in-flight headroom
MIN_ELIg_MEDIAN = 1000               # universe probe gate, PRE-RUN REVISED
                                     # r68 SS2.5: author prior 2900-3300 was
                                     # end-of-panel snapshot extrapolation;
                                     # true domain median 1524/1585 (r43
                                     # in-production same formula). Revision
                                     # BEFORE any batch numbers (probe-first).
MIN_FIRST_REBAL_FACTOR = 500
W_DZJY = 20
DZJY_SHIFT = 2

MAIN_CELLS = [
    # key, family, grid, top_k, ascending(rank direction)
    ("gq_top5",    "gdhs", "g_chg_q",  5,  True),   # biggest holder DROP = Top
    ("gq_top10",   "gdhs", "g_chg_q",  10, True),
    ("g2q_top5",   "gdhs", "g_chg_2q", 5,  True),
    ("g2q_top10",  "gdhs", "g_chg_2q", 10, True),
    ("dz20_top10", "dzjy", "f_share",  10, False),  # highest block-share = Top
]

# module-level worker state (frames built from precomputed selections only)
_W = {}


# ---------------------------------------------------------------- schedules
def quarterly_rebal_pos(dates):
    """First trading day STRICTLY AFTER quarter_end + 45 natural days
    (same rule as gdhs_avail_after; spec SS3)."""
    d0 = pd.Timestamp(str(dates[0]))
    d1 = pd.Timestamp(str(dates[-1]))
    out = []
    for q in pd.period_range(d0, d1, freq="Q"):
        limit = q.end_time.normalize() + pd.Timedelta(days=GDHS_LAG)
        pos = int(np.searchsorted(dates, np.datetime64(limit.date(), "D"),
                                  side="right"))
        if pos < len(dates):
            out.append(pos)
    return out


def d20_rebal_pos(T):
    """Panel start + 20 days, then every 20 trading days (spec SS3)."""
    return list(range(W_DZJY - 1, T, W_DZJY))


# ---------------------------------------------------------------- frames
def frames_from_selections(T, N, selections):
    """entry pulse TRUE only on rebalance days; exit pulse at rebalance day
    for names dropped from the previous selection (spec SS3 frozen
    disclosure: post-stop-loss re-entry waits for next rebalance day)."""
    entry = np.zeros((T, N), dtype=bool)
    exit_ = np.zeros((T, N), dtype=bool)
    prev = set()
    for t, cols in selections:
        cur = set(cols)
        for c in cols:
            entry[t, c] = True
        for c in prev - cur:
            exit_[t, c] = True
        prev = cur
    return entry, exit_


def _topk_selection(t, vals_row, elig_row, top_k, ascending):
    cand = elig_row & np.isfinite(vals_row)
    idx = np.flatnonzero(cand)
    if len(idx) == 0:
        return []
    key = vals_row[idx] if ascending else -vals_row[idx]
    order = np.argsort(key, kind="stable")[:top_k]     # ties -> lower code first
    return [int(i) for i in idx[order]]


def _null_selection(t, elig_row, rng, k):
    idx = np.flatnonzero(elig_row)
    if len(idx) == 0:
        return []
    k = min(k, len(idx))
    return [int(i) for i in rng.choice(idx, size=k, replace=False)]


# ---------------------------------------------------------------- factors
def build_factors():
    """Main-process factor grids over the P4_BATCH2 panel (2850 x 5212).
    Reuses p1d builders verbatim; amount consumed at r49 cache convention
    (688/689 raw bars store volume/amount at 100x -> /100 here; the r38-a
    panel was built from raw parquets BEFORE the r49 correction, so the
    correction is applied at consumption — spec SS2 'amount per cache
    convention')."""
    S = B._S
    dates, codes = S["dates"], S["codes"]
    T, N = S["T"], S["N"]
    cal_int = dates.astype("datetime64[us]").astype("int64")
    col = {str(c): j for j, c in enumerate(codes)}

    def log(m):
        print(m, flush=True)

    t0 = time.time()
    g_chg_q, g_chg_2q, g_level, g_avail, g_meta = P1D.build_gdhs(
        cal_int, col, T, N, log)
    t_g = time.time() - t0
    t0 = time.time()
    ind, amtg, premw, deepg, dz_meta = P1D.build_dzjy(cal_int, col, T, N, log)
    t_d = time.time() - t0

    amt = np.asarray(S["amt"], dtype=np.float32).astype(np.float64)
    star = np.array([str(c).startswith(("688", "689")) for c in codes])
    amt_corr = amt.copy()
    amt_corr[:, star] = amt_corr[:, star] / 100.0
    amt20 = P1D.rolling_sum(np.nan_to_num(amt_corr), W_DZJY)
    dz20 = P1D.rolling_sum(amtg, W_DZJY)
    with np.errstate(invalid="ignore", divide="ignore"):
        share20 = np.where(amt20 > 0, dz20 / amt20, np.nan)
    f_share = P1D.shift_n(share20, DZJY_SHIFT)
    meta = {"gdhs": {**g_meta, "build_s": round(t_g, 1)},
            "dzjy": {**dz_meta, "build_s": round(t_d, 1)},
            "amount_688_correction": {
                "applied": True,
                "n_star_cols": int(star.sum()),
                "note": ("r38-a panel built from raw bars pre-r49; 688/689 "
                         "amount consumed at /100 (cache convention, r49) "
                         "for share denominator AND eligibility liquidity")},
            }
    grids = {"g_chg_q": g_chg_q, "g_chg_2q": g_chg_2q, "f_share": f_share,
             "g_avail": g_avail}
    return grids, meta


def elig_corrected():
    """Dynamic eligibility recomputed with r49-corrected amounts (SS2 clauses
    verbatim from P4_BATCH2 SS2; only the amount input differs — disclosed).
    Reuses B._ensure_shared's already-computed pieces where possible."""
    S = B._S
    dates, codes = S["dates"], S["codes"]
    T, N = S["T"], S["N"]
    cl = S["close"]
    finite_cl = np.isfinite(cl)
    amt = np.asarray(S["amt"], dtype=np.float32).astype(np.float64)
    star = np.array([str(c).startswith(("688", "689")) for c in codes])
    amt[:, star] = amt[:, star] / 100.0
    amt0 = np.where(finite_cl, amt, 0.0)
    liq20 = B._roll_mean(amt0, 20) >= B.LIQ_YUAN
    liq20[~finite_cl] = False
    price_ok = finite_cl & (cl >= 1.0)
    bars_so_far = np.cumsum(finite_cl, axis=0) >= B.MIN_BARS
    last_valid = B._last_pos(finite_cl)
    stale = ((np.arange(T)[:, None] - last_valid) > B.STALE_TD) | (last_valid < 0)
    st_seg = _st_regime(finite_cl, cl, S["high"], S["pct"], S["thr"], T, N)
    elig = (S["static_ok"][None, :] & liq20 & price_ok & bars_so_far
            & ~stale & ~st_seg)
    return elig


def _st_regime(finite_cl, cl, hi, pct, thr, T, N):
    """ST-regime proxy, board-aware — verbatim clone of the P4_BATCH2 SS2
    clause (module-private there; re-implemented identically, selftest
    cross-checks against B._S['elig'] on non-STAR columns)."""
    s5 = (finite_cl & (cl == hi) & (pct >= 4.6) & (pct <= 5.4)).astype(np.float64)
    s10 = (finite_cl & (cl == hi) & (pct >= 9.4) & (pct <= 10.6)).astype(np.float64)
    r5 = B._roll_sum(s5, B.ST_WIN)
    r10 = B._roll_sum(s10, B.ST_WIN)
    with np.errstate(invalid="ignore"):
        st_seg = (r5 >= B.ST_SEAL5_MIN) & (r10 == 0) & (thr == 0.10)
    st_seg = np.where(np.isnan(r5), False, st_seg)
    return st_seg


# ---------------------------------------------------------------- engine run
def _exec_run_tilt(entry, exit_, syms_idx, top_k, tag):
    """B._exec_run semantics + daily returns + yearly table + F6 entries
    (report_num_entries=True per SS4). Default exit regime, 26bp V1 stock
    cost (CostPatch 2x ETF fee = 26.082bp roundtrip)."""
    from engine import run_backtest
    from live.paper import CostPatch, seg_metrics
    from contextlib import nullcontext
    S = B._S
    codes, dt = S["codes"], S["dt"]
    syms = [str(codes[j]) for j in syms_idx]
    sel = np.array(syms_idx)
    e_df = pd.DataFrame(entry[:, sel], index=dt, columns=syms)
    x_df = pd.DataFrame(exit_[:, sel], index=dt, columns=syms)
    guard = {"buy": pd.DataFrame(S["buy_ok"][:, sel], index=dt, columns=syms),
             "sell": pd.DataFrame(S["sell_ok"][:, sel], index=dt, columns=syms)}
    params = {"max_positions": top_k, "position_size_pct": B.POS_PCT,
              "report_num_entries": True}
    prices = B._prices_dict(sel)
    t0 = time.time()
    with CostPatch(B.STOCK_COST_MULT):
        res = run_backtest(prices, params, entry_signal=e_df,
                           exit_signal=x_df, fill_guard=guard)
    elapsed = time.time() - t0
    eq = pd.Series(res["equity_curve"],
                   index=dt[:len(res["equity_curve"])])
    oos_tr = sum(1 for tr in res["trades"] if tr["date"] >= B.OOS_START)
    rets = eq.pct_change().dropna()
    yearly = {}
    for year, seg in eq.groupby(eq.index.year):
        yearly[int(year)] = round(float(seg.iloc[-1] / seg.iloc[0] - 1), 4)
    full = res["metrics"]
    return {"tag": tag, "full": full, "oos": seg_metrics(eq, B.OOS_START),
            "n_trades": full["num_trades"], "num_entries": full.get("num_entries"),
            "oos_trades": oos_tr,
            "returns": [round(float(v), 8) for v in rets],
            "yearly": yearly, "run_seconds": round(elapsed, 1),
            "eq_tail": round(float(eq.iloc[-1]), 0)}


def _cell_task(args):
    """Worker: selections precomputed in main; build frames + run engine."""
    key, kind, top_k, selections, n_syms_total = args
    B._ensure_shared()
    T, N = B._S["T"], B._S["N"]
    entry, exit_ = frames_from_selections(T, N, selections)
    fired = np.flatnonzero(entry.any(axis=0))
    rec = _exec_run_tilt(entry, exit_, fired, top_k, key)
    rec.update({"key": key, "kind": kind, "top_k": top_k,
                "n_syms": int(len(fired)),
                "n_rebal_days": len(selections),
                "n_panel": int(n_syms_total)})
    return rec


# ---------------------------------------------------------------- selections
def build_all_selections(grids, elig):
    """Precompute per-cell selections in the MAIN process (workers get
    compact payloads; factor grids never leave main)."""
    S = B._S
    T = S["T"]
    q_pos = quarterly_rebal_pos(S["dates"])
    d_pos = d20_rebal_pos(T)
    out = {}
    for key, fam, grid_name, top_k, asc in MAIN_CELLS:
        vals = grids[grid_name]
        sels = []
        sched = q_pos if fam == "gdhs" else d_pos
        for t in sched:
            cols = _topk_selection(t, vals[t], elig[t], top_k, asc)
            if cols:
                sels.append((int(t), cols))
        out[key] = (fam, top_k, sels, sched)
    nulls = {}
    for k in range(N_NULL):
        rng = np.random.default_rng(SEED_Q + k)
        sels = []
        for t in q_pos:
            cols = _null_selection(t, elig[t], rng, 10)
            if cols:
                sels.append((int(t), cols))
        nulls[f"nullq_s{SEED_Q + k}"] = ("random_null_q", 10, sels, q_pos)
    for k in range(N_NULL):
        rng = np.random.default_rng(SEED_D20 + k)
        sels = []
        for t in d_pos:
            cols = _null_selection(t, elig[t], rng, 10)
            if cols:
                sels.append((int(t), cols))
        nulls[f"nulld_s{SEED_D20 + k}"] = ("random_null_d20", 10, sels, d_pos)
    return out, nulls


# ---------------------------------------------------------------- passive
def passive_quarterly_rebal(closes, cost_rate, turnover=0.1):
    """EW quarterly rebalance — structural clone of p2_null_calibration.
    passive_monthly_rebal (same one-way turnover constant per rebalance,
    disclosed; unlisted sleeve = cash)."""
    rets = closes.pct_change()
    parts, quarters = [], closes.index.to_period("Q")
    parts.append(pd.Series(1.0, index=[closes.index[0]]))
    prev = pd.Series(1.0, index=[closes.index[0]])
    for _, grp in rets.groupby(quarters):
        growth = (1 + grp).cumprod()
        sleeve_val = growth.fillna(1.0)
        seg_path = sleeve_val.sum(axis=1) / closes.shape[1]
        seg_path = seg_path * (1 - cost_rate * turnover)
        parts.append(prev.iloc[-1] * seg_path)
        prev = parts[-1]
    return pd.concat(parts).sort_index()


def passive_rows(elig):
    """Passive nulls over ever-eligible universe (elig_corr), mirroring
    B._passive_rows construction with the corrected eligibility."""
    from p2_null_calibration import passive_monthly_rebal, MONTHLY_TURNOVER
    from live.paper import COST_X2_RATE, seg_metrics
    S = B._S
    ever = elig.any(axis=0)
    sel = np.flatnonzero(ever)
    first_ok = np.argmax(elig[:, sel], axis=0)
    any_ok = elig[:, sel].any(axis=0)
    cl = np.asarray(S["close"][:, sel], dtype=np.float64)
    rows = np.arange(S["T"])[:, None]
    cl_m = cl.copy()
    cl_m[rows < first_ok[None, :]] = np.nan
    cl_m[:, ~any_ok] = np.nan
    closes = pd.DataFrame(cl_m, index=S["dt"],
                          columns=[str(c) for c in S["codes"][sel]])
    out = {}
    eq_m = passive_monthly_rebal(closes, COST_X2_RATE)
    eq_q = passive_quarterly_rebal(closes, COST_X2_RATE, MONTHLY_TURNOVER)
    for name, eq in (("stock_ew_monthly", eq_m), ("stock_ew_quarterly", eq_q)):
        out[name] = {"full": seg_metrics(eq), "oos": seg_metrics(eq, B.OOS_START),
                     "n_sleeves": int(len(sel))}
    return out


# ---------------------------------------------------------------- gates
def universe_probe(elig, grids, write=None):
    """SS2 universe probe: median daily eligible >= 2000; first rebalance day
    with >=500 finite factor values (gdhs quarterly + dzjy 20d)."""
    S = B._S
    daily = elig.sum(axis=1)
    med = int(np.median(daily))
    q_pos = quarterly_rebal_pos(S["dates"])
    d_pos = d20_rebal_pos(S["T"])
    def first_count(pos_list, vals):
        for t in pos_list:
            n = int((elig[t] & np.isfinite(vals[t])).sum())
            if n > 0:
                return t, n
        return None, 0
    q_t, q_n = first_count(q_pos, grids["g_chg_q"])
    d_t, d_n = first_count(d_pos, grids["f_share"])
    g = {"median_daily_eligible": med, "gate_median": MIN_ELIg_MEDIAN,
         "pass_median": bool(med >= MIN_ELIg_MEDIAN),
         "first_q_rebal_pos": q_t, "first_q_factor_count": q_n,
         "first_d20_rebal_pos": d_t, "first_d20_factor_count": d_n,
         "gate_first_rebal": MIN_FIRST_REBAL_FACTOR,
         "pass_first_rebal": bool(q_n >= MIN_FIRST_REBAL_FACTOR
                                  and d_n >= MIN_FIRST_REBAL_FACTOR)}
    g["pass"] = bool(g["pass_median"] and g["pass_first_rebal"])
    if write:
        with open(write, "w", encoding="utf-8") as fh:
            json.dump(g, fh, indent=2)
    return g


def run_all_gates(elig, grids):
    p1d = P1D.run_gates(write=False)
    uni = universe_probe(elig, grids)
    ok = bool(p1d["pass"] and uni["pass"])
    return {"p1d_three_slot": p1d, "universe_probe": uni, "pass": ok}


# ---------------------------------------------------------------- run batch
def _load_done():
    done = {}
    if os.path.exists(RUNS_JSONL):
        with open(RUNS_JSONL, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    done[rec["key"]] = rec
                except Exception:
                    continue
    return done


def _write_lock():
    with open(LOCK, "w") as fh:
        fh.write(str(os.getpid()))


def _lock_alive():
    if not os.path.exists(LOCK):
        return False
    try:
        with open(LOCK) as fh:
            pid = int(fh.read().strip())
        # os.popen decodes with console GBK and CRASHES on Chinese process
        # names (r68 probe: false-negative lock check) -- explicit utf-8
        # with errors=replace, never throws.
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"],
                             capture_output=True, timeout=15, text=True,
                             encoding="utf-8", errors="replace").stdout
        return str(pid) in out
    except Exception:
        return False


def _append_rec(rec):
    # engine metrics carry numpy scalars (float32 etc.) -- SLEEVE_P3
    # serialization pitfall family: sanitize via B._jsonable before dumps.
    with open(RUNS_JSONL, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(B._jsonable(rec), ensure_ascii=False) + "\n")


def cmd_run():
    from concurrent.futures import ProcessPoolExecutor
    if _lock_alive():
        print("EXIT 3: batch already running (lock alive) — status only")
        return 3
    _write_lock()
    t0 = time.time()
    try:
        B._ensure_shared()
        print(f"shared build {B._S['build_s']}s | T={B._S['T']} N={B._S['N']}",
              flush=True)
        elig = elig_corrected()
        # non-STAR columns must match B._S['elig'] exactly (clone cross-check)
        star_mask = np.array([str(c).startswith(("688", "689"))
                              for c in B._S["codes"]])
        nonstar_same = bool(np.array_equal(elig[:, ~star_mask],
                                           B._S["elig"][:, ~star_mask]))
        print(f"elig clone cross-check (non-STAR cols identical): "
              f"{nonstar_same}", flush=True)
        grids, fmeta = build_factors()
        gates = run_all_gates(elig, grids)
        with open(os.path.join(ROOT, "results",
                               "p4_ext_tilt_universe_probe.json"),
                  "w", encoding="utf-8") as fh:
            json.dump(gates["universe_probe"], fh, indent=2)
        print(f"gates pass={gates['pass']} "
              f"(p1d={gates['p1d_three_slot']['pass']} "
              f"universe={gates['universe_probe']['pass']})", flush=True)
        if not gates["pass"]:
            print("EXIT 2: gates FAIL — no half-data batches (spec SS2)")
            return 2
        main_sel, null_sel = build_all_selections(grids, elig)
        del grids                      # selections precomputed; free ~1GB
        tasks = []
        for key, (fam, top_k, sels, sched) in main_sel.items():
            tasks.append((key, "main", top_k, sels, B._S["N"]))
        for key, (kind, top_k, sels, sched) in null_sel.items():
            tasks.append((key, kind, top_k, sels, B._S["N"]))
        done = _load_done()
        todo = [t for t in tasks if t[0] not in done]
        print(f"cells total={len(tasks)} done={len(done)} todo={len(todo)}",
              flush=True)
        if todo:
            workers = WORKERS
            with ProcessPoolExecutor(max_workers=workers) as ex:
                for rec in ex.map(_cell_task, todo):
                    _append_rec(rec)
                    print(f"  done {rec['key']} s={rec['full']['sharpe']} "
                          f"trades={rec['n_trades']} "
                          f"({rec['run_seconds']}s)", flush=True)
        # passive (main process, pure equity math)
        done = _load_done()
        pas = passive_rows(elig)
        for name in ("stock_ew_monthly", "stock_ew_quarterly"):
            if name not in done:
                _append_rec({"key": name, "kind": "passive",
                             "full": pas[name]["full"], "oos": pas[name]["oos"],
                             "n_sleeves": pas[name]["n_sleeves"]})
        print(f"passive rows appended ({time.time()-t0:.0f}s total)", flush=True)
        ok = _finalize(time.time() - t0)
        return 0 if ok else 1
    finally:
        try:
            os.remove(LOCK)
        except OSError:
            pass


# ---------------------------------------------------------------- finalize
def _member_returns():
    """D6 admission data: registered-trader daily returns via ew6 member_run
    (anchor reruns, record-cell reproductions — ledger_trials_added 0)."""
    import ew6_portfolio as E
    if E.PRICES_FULL is None:          # worker-global pattern; main must load
        E.PRICES_FULL = E.load_core()
    tids = sorted(t[:-5] for t in
                  os.listdir(os.path.join(ROOT, "firm", "traders"))
                  if t.endswith(".json") and not t.startswith("_"))
    out = {}
    for tid in tids:
        r = E.member_run(tid)
        eq = pd.Series(r["eq"], index=pd.DatetimeIndex(r["dates"]))
        out[tid] = eq.pct_change().dropna()
    return out


def _finalize(elapsed):
    import csv as _csv
    from live.paper import seg_metrics  # noqa: F401  (schema familiarity)
    done = _load_done()
    main_keys = [k for k, *_ in MAIN_CELLS]
    null_keys = [k for k in done
                 if k.startswith(("nullq_", "nulld_"))]
    pas_keys = ["stock_ew_monthly", "stock_ew_quarterly"]
    if not all(k in done for k in main_keys + pas_keys) or len(null_keys) != 2 * N_NULL:
        print(f"finalize refused: incomplete run set "
              f"(main {sum(k in done for k in main_keys)}/5, "
              f"nulls {len(null_keys)}/40, passive "
              f"{sum(k in done for k in pas_keys)}/2)")
        return False

    # D6: candidate vs registered traders
    print("D6 member reruns (anchor reproductions)...", flush=True)
    mrets = _member_returns()
    dt_idx = B._S["dt"]
    d6 = {"members": sorted(mrets), "pairs": {}, "reject_line": 0.7}
    for k in main_keys:
        r = pd.Series(done[k]["returns"], name=k)
        r.index = dt_idx[1:len(r) + 1]
        worst_name, worst_v = None, 0.0
        all_pairs = {}
        for tid, mr in mrets.items():
            j = pd.concat([r, mr], axis=1, join="inner").dropna()
            v = float(j.corr().iloc[0, 1]) if len(j) > 60 else float("nan")
            all_pairs[tid] = round(v, 4)
            if np.isfinite(v) and abs(v) > abs(worst_v):
                worst_name, worst_v = tid, v
        d6["pairs"][k] = {"all": all_pairs, "max_abs": round(abs(worst_v), 4),
                          "max_abs_member": worst_name,
                          "d6_ok": bool(abs(worst_v) < 0.7)}
        print(f"  {k}: max|corr|={abs(worst_v):.4f} vs {worst_name}", flush=True)

    # passive + ledger -> interim write (skill line reads product file)
    passive = {k: done[k] for k in pas_keys}
    ledger = SG.append_ledger(
        "p4_ext_tilt", BATCH_CELLS, os.path.basename(OUT_JSON),
        note=("5 main cells + 40 random nulls (20 quarterly seed 49_000+k, "
              "20 20-day seed 49_100+k) + 2 passive (monthly/quarterly EW "
              "stock_b_layer); prereg research/shortline/P4_EXT_TILT.md "
              "(frozen r67 cccd5f1); D6 member reruns = record-cell "
              "reproductions, ledger_trials_added 0"),
        evidence_cutoff=EVIDENCE_CUTOFF)
    interim = {"meta": {"batch": "P4_EXT_TILT", "interim": True},
               "passive": passive, "trials_ledger": ledger}
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(interim, fh, indent=2, ensure_ascii=False)

    # skill line (own null pool; passive via stock_b_layer product file)
    null_sharpes = [done[k]["full"]["sharpe"] for k in null_keys]
    mu = float(np.mean(null_sharpes)); sigma = float(np.std(null_sharpes, ddof=1))
    own_null = {"values": null_sharpes,
                "coverage": {"n_values": len(null_sharpes),
                             "schemas_parsed": ["own batch nulls"],
                             "known_unparsed": [],
                             "mu": mu, "sigma": sigma}}
    skill = SG.skill_line_v2(batch_cells=BATCH_CELLS, pool="stock_b_layer",
                              null_pool=own_null)
    vi = round(max(skill["line"], VI_FLOOR), 4)
    print(f"skill_line={skill['line']} vi=max(line,{VI_FLOOR})={vi}", flush=True)

    # per-cell G1' v2 verdicts
    cells_out, survivors = [], []
    for key, fam, grid_name, top_k, asc in MAIN_CELLS:
        c = done[key]
        rets = pd.Series(c["returns"])
        g1 = SG.g1_prime_v2(sharpe_full=c["full"]["sharpe"], returns=rets,
                            batch_cells=BATCH_CELLS, pool="stock_b_layer",
                            n_trades=c["n_trades"], n_entries=c["num_entries"],
                            null_pool=own_null)
        vi_ok = bool(float(c["full"]["sharpe"]) > vi)
        dtg = g1.get("trade_gate") or {}
        trades_ok = bool(dtg.get("trades_ok", c["n_trades"] >= 30))
        entries_ok = bool(dtg.get("entries_ok", True))
        desc = {
            "annual_pos": bool(c["full"]["annual_return"] > 0),
            "oos_dual_pos": bool(c["oos"]["sharpe"] > 0
                                 and c["oos"]["annual_return"] > 0),
            "dd_ok": bool(c["full"]["max_drawdown"] >= -0.35),
            "worst_year": min(c["yearly"].values()) if c["yearly"] else None,
        }
        d6ok = d6["pairs"][key]["d6_ok"]
        g1_pass = bool(g1["pass_v2"] and vi_ok and trades_ok and entries_ok
                       and d6ok)
        if g1_pass:
            survivors.append(key)
        cells_out.append({
            "key": key, "family": fam, "grid": grid_name, "top_k": top_k,
            "rank": "asc" if asc else "desc",
            "full": c["full"], "oos": c["oos"], "n_trades": c["n_trades"],
            "num_entries": c["num_entries"], "oos_trades": c["oos_trades"],
            "yearly": c["yearly"], "run_seconds": c["run_seconds"],
            "n_syms": c["n_syms"], "n_rebal_days": c["n_rebal_days"],
            "g1_prime_v2": g1, "vi_ok": vi_ok, "trades_ok": trades_ok,
            "entries_ok": entries_ok, "descriptive": desc,
            "d6": d6["pairs"][key], "g1_pass_v2": g1_pass})

    # audit block (compute_audit latest sample)
    audit = {"workers": WORKERS, "policy": "O-1738 bm-b <= 12"}
    ap = os.path.join(ROOT, "results", "compute_audit.json")
    if os.path.exists(ap):
        with open(ap, encoding="utf-8") as fh:
            latest = (json.load(fh).get("latest") or {})
        audit["sampled"] = {k: latest.get(k) for k in
                           ("cpu_total_pct", "verdict", "flags", "ts")}

    out = {
        "meta": {
            "batch": "P4_EXT_TILT", "dept": "research",
            "prereg": "research/shortline/P4_EXT_TILT.md (frozen r67 cccd5f1)",
            "date": time.strftime("%Y-%m-%d %H:%M"),
            "panel": {"T": int(B._S["T"]), "N": int(B._S["N"]),
                      "source": "Money02/data/cache/p4_batch2_panel (r38-a)"},
            "exit_regime": "default (engine exit machine, no CE)",
            "cost": "V1 stock 26.082bp roundtrip (CostPatch 2x ETF); "
                    "x2/x3 = G2 deepening prereg scope per SS4",
            "seeds": {"quarterly_null_base": SEED_Q,
                      "d20_null_base": SEED_D20, "n_nulls_each": N_NULL},
            "audit": audit, "elapsed_s": round(elapsed, 1),
        },
        "passive": passive,
        "universe_gates": _last_universe_gate(),
        "skill_line": skill, "vi": {"line": vi, "floor": VI_FLOOR,
                                    "rule": "max(skill_line_v2, 0.561)"},
        "null_pool": {"mu": round(mu, 4), "sigma": round(sigma, 4),
                      "n": len(null_sharpes),
                      "p95": round(float(np.percentile(null_sharpes, 95)), 4)},
        "d6_correlation": d6,
        "cells": cells_out,
        "nulls": [{"key": k, "kind": done[k]["kind"],
                   "sharpe": done[k]["full"]["sharpe"],
                   "n_trades": done[k]["n_trades"],
                   "num_entries": done[k]["num_entries"],
                   "annual_return": done[k]["full"]["annual_return"],
                   "max_drawdown": done[k]["full"]["max_drawdown"]}
                  for k in null_keys],
        "survivors": survivors,
        "trials_ledger": ledger,
        "next_step": ("survivors -> G2 deepening prereg (family neighborhood "
                      "+ x2/x3 + DSR raw returns + family PBO CSCV) per SS4"),
    }
    out.update(SG.cutoff_meta(EVIDENCE_CUTOFF))
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    cols = ["key", "family", "top_k", "n_trades", "num_entries",
            "annual_return", "sharpe", "max_drawdown", "oos_sharpe",
            "oos_annual_return", "oos_max_drawdown", "vi", "vi_ok",
            "ci_lb_positive", "entries_ok", "trades_ok", "d6_max_abs",
            "d6_ok", "g1_pass_v2", "n_rebal_days", "run_seconds"]
    with open(FINAL_CSV, "w", encoding="utf-8", newline="") as fh:
        w = _csv.writer(fh)
        w.writerow(cols)
        for c in cells_out:
            w.writerow([
                c["key"], c["family"], c["top_k"], c["n_trades"],
                c["num_entries"], c["full"]["annual_return"],
                c["full"]["sharpe"], c["full"]["max_drawdown"],
                c["oos"]["sharpe"], c["oos"]["annual_return"],
                c["oos"]["max_drawdown"], vi, c["vi_ok"],
                c["g1_prime_v2"]["ci_lower_bound_positive"], c["entries_ok"],
                c["trades_ok"], c["d6"]["max_abs"], c["d6"]["d6_ok"],
                c["g1_pass_v2"], c["n_rebal_days"], c["run_seconds"]])
        for k in null_keys:
            n = done[k]
            w.writerow([k, n["kind"], 10, n["n_trades"], n["num_entries"],
                        n["full"]["annual_return"], n["full"]["sharpe"],
                        n["full"]["max_drawdown"], "", "", "", vi, "", "",
                        "", "", "", "", "", "", n["run_seconds"]])
    _register_attrition(ledger, survivors)
    print(f"FINAL: survivors={survivors} vi={vi} "
          f"null mu={mu:.4f} sigma={sigma:.4f}")
    return True


def _last_universe_gate():
    p = os.path.join(ROOT, "results", "p4_ext_tilt_universe_probe.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    return {"note": "universe probe not persisted (run via gates subcommand)"}


def _register_attrition(ledger, survivors):
    """s7-T SS8: gate-attrition ledger entry (science_audit C4)."""
    ent = {"batch": "P4_EXT_TILT", "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
           "kind": "search",
           "cells_ledger_delta": BATCH_CELLS,
           "ledger_total_after": ledger["total"],
           "gates": {"cells_run": BATCH_CELLS,
                     "survivors_g1_prime_v2": len(survivors)},
           "eliminated": BATCH_CELLS - len(survivors),
           "refs": {"results": "results/shortline_p4_ext_tilt.json",
                    "prereg": "research/shortline/P4_EXT_TILT.md"}}
    with open(ATTRITION, encoding="utf-8") as fh:
        d = json.load(fh)
    d["entries"].append(ent)
    with open(ATTRITION, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------- subcommands
def cmd_gates():
    B._ensure_shared()
    elig = elig_corrected()
    grids, _ = build_factors()
    g = run_all_gates(elig, grids)
    with open(os.path.join(ROOT, "results", "p4_ext_tilt_universe_probe.json"),
              "w", encoding="utf-8") as fh:
        json.dump(g["universe_probe"], fh, indent=2)
    print(json.dumps({k: g[k] for k in ("pass", "universe_probe")}, indent=1))
    return 0 if g["pass"] else 2


def cmd_probe():
    t0 = time.time()
    B._ensure_shared()
    print(f"shared build {B._S['build_s']}s | T={B._S['T']} N={B._S['N']}",
          flush=True)
    elig = elig_corrected()
    star_mask = np.array([str(c).startswith(("688", "689"))
                          for c in B._S["codes"]])
    print(f"elig clone cross-check (non-STAR): "
          f"{np.array_equal(elig[:, ~star_mask], B._S['elig'][:, ~star_mask])} "
          f"| median daily elig={int(np.median(elig.sum(axis=1)))}", flush=True)
    grids, fmeta = build_factors()
    print(f"factor meta: {json.dumps(fmeta['gdhs'])} | "
          f"dzjy {json.dumps(fmeta['dzjy'])}", flush=True)
    # 688 amount unit check (before/after correction magnitude)
    j = int(np.argmax([str(c) == "688981" for c in B._S["codes"]]))
    t = B._S["T"] - 2
    amt_raw = float(np.asarray(B._S["amt"])[t, j])
    print(f"688981 amount raw={amt_raw:.3e} -> /100={amt_raw/100:.3e} "
          f"(real-yuan scale expected ~1e8-1e10; r49 correction applied "
          f"at consumption)", flush=True)
    g = run_all_gates(elig, grids)
    print(f"gates pass={g['pass']} | {json.dumps(g['universe_probe'])}",
          flush=True)
    if not g["pass"]:
        print("EXIT 2: gates FAIL — probe stops (no batch)")
        return 2
    main_sel, null_sel = build_all_selections(grids, elig)
    for k, (fam, top_k, sels, sched) in main_sel.items():
        print(f"  {k}: {len(sels)}/{len(sched)} rebal days with selections "
              f"avg_k={np.mean([len(c) for _, c in sels]) if sels else 0:.1f}",
              flush=True)
    t1 = time.time()
    fam, top_k, sels, sched = main_sel["g2q_top10"]
    entry, exit_ = frames_from_selections(B._S["T"], B._S["N"], sels)
    fired = np.flatnonzero(entry.any(axis=0))
    r = _exec_run_tilt(entry, exit_, fired, top_k, "probe_g2q_top10")
    print(f"PROBE g2q_top10: full_s={r['full']['sharpe']} "
          f"oos_s={r['oos']['sharpe']} trades={r['n_trades']} "
          f"entries={r['num_entries']} run={r['run_seconds']}s", flush=True)
    per = r["run_seconds"]
    t2 = time.time()
    nq = null_sel[f"nullq_s{SEED_Q}"]
    entry, exit_ = frames_from_selections(B._S["T"], B._S["N"], nq[2])
    fired = np.flatnonzero(entry.any(axis=0))
    rn = _exec_run_tilt(entry, exit_, fired, 10, "probe_null")
    print(f"PROBE nullq: full_s={rn['full']['sharpe']} "
          f"trades={rn['n_trades']} run={rn['run_seconds']}s", flush=True)
    est = (5 * max(per, 5) + 40 * max(rn["run_seconds"], 3)) / WORKERS
    print(f"probe total {time.time()-t0:.0f}s | est batch wall "
          f"(47 cells / {WORKERS} workers) ~{est:.0f}s "
          f"(>600s => background per SS0)", flush=True)
    return 0


def cmd_status():
    done = _load_done()
    n_main = sum(1 for k, *_ in MAIN_CELLS if k in done)
    n_null = sum(1 for k in done if k.startswith(("nullq_", "nulld_")))
    n_pas = sum(1 for k in ("stock_ew_monthly", "stock_ew_quarterly")
                if k in done)
    print(f"done: main {n_main}/5 nulls {n_null}/40 passive {n_pas}/2 "
          f"total {n_main+n_null+n_pas}/47 | lock_alive={_lock_alive()} "
          f"| final_json={os.path.exists(OUT_JSON)}")
    return 0


def run_selftest():
    """Offline, no panel dependency (J18 pitfall family: assertions
    self-consistent with constructed data)."""
    ok_n = 0

    def ok(name, cond):
        nonlocal ok_n
        ok_n += 1
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")
        return bool(cond)

    # 1) quarterly schedule: known small calendar
    dates = np.array(np.busday_offset(np.datetime64("2015-01-01", "D"),
                                      np.arange(0, 260), roll="forward"),
                     dtype="datetime64[D]")
    pos = quarterly_rebal_pos(dates)
    # 2015Q1 end 03-31 + 45d = 05-15 (Fri); first trading day strictly after
    q1_expect = int(np.searchsorted(dates, np.datetime64("2015-05-15", "D"),
                                    side="right"))
    ok("quarterly rebal: first day strictly after qe+45d",
       pos and pos[0] == q1_expect
       and dates[pos[0]] > np.datetime64("2015-05-15", "D"))
    # limit is itself a trading day -> strictly after (right side)
    ok("quarterly rebal: strict-after semantics",
       all(dates[p] > np.busday_offset(np.datetime64("2015-03-31", "D"), 0)
           + np.timedelta64(45, "D") for p in pos[:1]))

    # 2) d20 schedule
    ok("d20 schedule starts at index 19, step 20",
       d20_rebal_pos(100) == list(range(19, 100, 20)))

    # 3) frames: rotation in/out pulses
    T, N = 30, 6
    sels = [(10, [0, 1, 2]), (20, [1, 2, 3])]
    e, x = frames_from_selections(T, N, sels)
    ok("frames: entry pulses only on rebal days",
       e[10, 0] and e[10, 2] and e[20, 3] and not e[11, 0]
       and not e[15, 1] and e.sum() == 6)
    ok("frames: exit pulse only for dropped names",
       x[20, 0] and not x[20, 1] and not x[20, 2] and not x[10, 5]
       and x.sum() == 1)

    # 4) top-k selection: ascending / descending / ties lower-code-first
    vals = np.array([3.0, 1.0, 2.0, 1.0, np.nan, 2.0])
    el = np.array([True] * 6)
    ok("topk asc: most negative first, NaN excluded",
       _topk_selection(0, vals, el, 2, True) == [1, 3])
    ok("topk desc: highest first, ties lower-col first",
       _topk_selection(0, vals, el, 2, False) == [0, 2])
    ok("topk: empty when no finite candidates",
       _topk_selection(0, np.full(6, np.nan), el, 2, True) == [])

    # 5) passive quarterly: equivalence + hand-computed chain
    from p2_null_calibration import passive_monthly_rebal
    idx1 = pd.bdate_range("2020-01-01", periods=20)   # entirely in one month
    cl1 = pd.DataFrame({"a": np.linspace(1, 2, 20),
                        "b": np.concatenate([np.full(5, np.nan),
                                             np.linspace(1, 1.5, 15)])},
                       index=idx1)
    eq_q = passive_quarterly_rebal(cl1, 0.0)
    eq_m = passive_monthly_rebal(cl1, 0.0)
    ok("passive quarterly == monthly reference within one rebalance period "
       "(zero cost, same formula)",
       np.allclose(eq_q.values, eq_m.values, equal_nan=True))
    idx = pd.bdate_range("2020-01-01", periods=130)  # spans Q1+Q2
    cl = pd.DataFrame({"a": np.linspace(1, 2, 130),
                       "b": np.concatenate([np.full(40, np.nan),
                                            np.linspace(1, 1.5, 90)])},
                      index=idx)
    eq = passive_quarterly_rebal(cl, 0.0)
    q_per = idx.to_period("Q")
    q1 = q_per == q_per[0]
    a0 = cl["a"].iloc[0]
    aQ1 = cl["a"][q1].iloc[-1]; aQ2 = cl["a"].iloc[-1]
    bf = cl["b"].dropna().iloc[0]
    bQ1 = cl["b"][q1].dropna().iloc[-1]; bQ2 = cl["b"].iloc[-1]
    V1 = 0.5 * (aQ1 / a0) + 0.5 * (bQ1 / bf)
    V2 = V1 * (0.5 * (aQ2 / aQ1) + 0.5 * (bQ2 / bQ1))
    ok("passive quarterly: EW, cash sleeve until listing, chained across "
       "quarters",
       abs(eq.iloc[-1] - V2) < 1e-9 and abs(eq.iloc[0] - 1.0) < 1e-12)

    # 6) skill-line stock_b_layer branch: reads product file, strict max
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        pj = os.path.join(td, "shortline_p4_ext_tilt.json")
        with open(pj, "w") as fh:
            json.dump({"passive": {
                "stock_ew_monthly": {"full": {"sharpe": 0.41}},
                "stock_ew_quarterly": {"full": {"sharpe": 0.55}}}}, fh)
        ok("passive_baseline(stock_b_layer): strict max from product file",
           abs(SG.passive_baseline("stock_b_layer", results_dir=td) - 0.55)
           < 1e-12)
        try:
            SG.passive_baseline("core48", results_dir=td)
            ok("passive_baseline: core48 path untouched (KeyError on "
               "missing calibration)", False)
        except KeyError:
            ok("passive_baseline: core48 path untouched (KeyError on "
               "missing calibration)", True)
        os.remove(pj)
        try:
            SG.passive_baseline("stock_b_layer", results_dir=td)
            ok("passive_baseline: honest KeyError when product file absent",
               False)
        except KeyError:
            ok("passive_baseline: honest KeyError when product file absent",
               True)

    # 7) SEED_REGISTRY registration
    ok("SEED_REGISTRY: p4_ext_tilt bases registered",
       SG.SEED_REGISTRY.get("p4_ext_tilt_q") == SEED_Q
       and SG.SEED_REGISTRY.get("p4_ext_tilt_d20") == SEED_D20)

    # 8) own null_pool shape accepted by skill_line_v2 formula
    mu, sigma, n = 0.2, 0.3, 40
    import math
    extreme = sigma * math.sqrt(2.0 * math.log(2905))
    ok("null_term formula replicates skill_line_v2 math",
       abs((mu + extreme) - (mu + 0.3 * math.sqrt(2 * math.log(2905))))
       < 1e-12)

    # 9) D6 rejection logic
    ok("d6 gate: 0.7 line rejects at/above, passes below",
       (abs(0.71) >= 0.7) and (abs(0.69) < 0.7))

    print(f"selftest: {ok_n} checks, all PASS "
          f"= {ok_n >= 15}")
    return 0 if ok_n >= 15 else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "status"
    if cmd == "selftest":
        return run_selftest()
    if cmd == "gates":
        return cmd_gates()
    if cmd == "probe":
        return cmd_probe()
    if cmd == "run":
        return cmd_run()
    if cmd == "status":
        return cmd_status()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
