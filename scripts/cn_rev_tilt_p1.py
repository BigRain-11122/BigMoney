# -*- coding: utf-8 -*-
"""CN-REV-TILT-P1 -- CN-REVERSAL-TILT combo model, s3 slice-1 batch runner
(T-2026-09-26-73, CEO order O-20260926-0926 "CN-native combo models").

Prereg FROZEN research/CN_REV_TILT_PREREG.md (R245 freeze, R246 zero-run
amendments: seed base 20260930 + s2 evidence_cutoff backfill); runner
contract frozen in ticket progress_r246. Zero threshold edits post-run;
s7/s8 backfill is the only sanctioned prereg edit (control-plane, not here).

Cells (prereg s0: judged grid = 4, K=50 nulls NOT in the skill grid):
  REV20_bare / REV60_bare     naked reversal sleeves (top-20 of top-10%
                              decile, equal weight, h10 rebalance, T+1)
  REV20_tilt / REV60_tilt     regime-tilted: trail>0 -> rev 0.9/cash 0.1,
                              else rev 0.1/cash 0.9 (prereg s3.3 constitutive
                              axis, s2 v2-fail empirical driver)
  Machinery (disclosure, not judged): MOM{20,60} mirror bare sleeves feed
  the 252d style-regime trail. Cost faces x1/x2/x3 = V1 13.041bp/side
  (alloc_backtest.V1_FLAT_SIDE single source) x {1,2,3} on turnover;
  x1 = judged face, x2/x3 = stress tracks (BACKTEST_PLAN iron law 3).
  Nulls: K=50 same-mask random-signal 20-name sleeves, seeds 20260930+k
  (science_gates.SEED_REGISTRY['cn_rev_tilt_p1'], R246 collision amendment).
  Baselines: census equal-weight same-rhythm sleeve + the random nulls;
  trial count N recorded (ledger trials = 4 cells + 50 nulls = 54).

Panel (prereg s2): P1C census close panel via the s2 slice-A loader
(t73_s2_reversal_momentum.load_close -- same cache, same ffill convention,
zero network). Data gates fail-closed exit 2: panel cutoff == 2026-09-22
AND T>=8000 AND N>=5000 (D2 forward lockbox; 09-23/24 bars excluded).

Accounting (close-only face, P1C has no ADV -> V1 flat cost, prereg s3.2):
  rebalance schedule = range(H-1, T-1, H) (p4_ext_tilt d20 semantics at
  H=10); signal at close of r, trades execute AT close of r+1 (T+1, close
  is the only price on this face); a rebalance with an EMPTY selection
  liquidates to cash (empty target face); cohort holds 10 close-to-close
  intervals; turnover cost = side_rate * sum|target_w - drifted_w| * V at
  each transition; cash leg zero-yield; full-timeline return series with
  out-days = 0 (div_lowvol s4 convention). Frozen-price ffill tails
  inherited from the P1C convention (s2 single-source; disclosed).

Gates (prereg s4, shared library only -- zero hand-copied lines, O-2250):
  G1'v2 = science_gates.g1_prime_v2(batch_cells=4, pool='core48',
  null_pool=batch-own {values, coverage}) ; G2 = g2_registration_v2 +
  DSR (deflated_sharpe_ratio, n_trials=line.n_eff, var_null_sr=sigma^2)
  + family PBO (screening/pbo.cscv_pbo CSCV-8 over the 4-cell x1 grid).
  D6 (s1): max|corr| of each judged cell vs the 6 registered traders
  (ew6 canon member_run) + same-batch cross-corr; >=0.7 vs REGISTERED
  members = reject. Descriptive clauses + hard-bound triad (median/p99.9
  + crisis windows 2015-06/07, 2016-01, 2024-01/02 with single-point
  exemption disclosure) are batch-level honesty, never gates.
  REGIME_GUARD v3 four-state series via the IMPORTED frozen deep-replay
  layer (regime_deep_replay.run_matrices -> v3 states, 2005-04-08+;
  pre-ETF era = structurally unavailable, honest None) = descriptive
  market-regime axis vs the style-regime (trail) axis, never a switch.

Products (prereg s6): results/cn_rev_tilt/p1_results.json (top-level
evidence_cutoff + science_gates.cutoff_meta + 4 cells x {x1,x2,x3} +
nulls + baselines + D6 corr table + regime columns) + cells_summary.csv;
ledger append single-shot at finalize (CN_REV_TILT_P1_REFINALIZE=1 is the
only redo path); per-unit .npz checkpoints under results/cn_rev_tilt/ckpt/
(gitignored binary, exact float64 -> resume is byte-identical to fresh).

Usage: run | selftest   (exit 0 ok; 2 = fail-closed gate/mechanism refusal)
"""
import argparse
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "screening"))

import numpy as np
import pandas as pd

import science_gates as sg
from pbo import cscv_pbo, align_returns
from alloc_backtest import V1_FLAT_SIDE
from composite_ic import IS_END

TICKET = "T-2026-09-26-73"
PREREG = os.path.join(ROOT, "research", "CN_REV_TILT_PREREG.md")
OUT_DIR = os.path.join(ROOT, "results", "cn_rev_tilt")
CKPT_DIR = os.path.join(OUT_DIR, "ckpt")
OUT_JSON = os.path.join(OUT_DIR, "p1_results.json")
OUT_CSV = os.path.join(OUT_DIR, "cells_summary.csv")
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")
LOG_PATH = os.path.join(OUT_DIR, "runner.log")

EVIDENCE_CUTOFF = "2026-09-22"     # prereg s2 (R246 same-source probe backfill)
EVIDENCE_CUTOFF_TS = pd.Timestamp(EVIDENCE_CUTOFF)
OOS_START = "2025-01-01"           # composite_ic shared split (IS_END+1)
SEED_BASE = 20_260_930             # SEED_REGISTRY['cn_rev_tilt_p1'] (R246)
K_NULLS = 50
BATCH_CELLS = 4                    # judged grid (prereg s0; nulls excluded)
LEDGER_TRIALS = 54                 # 4 cells + 50 nulls on the D1 bill
W_SET = (20, 60)                   # prereg s3.1 frozen windows
TOP_POOL_Q = 0.10                  # top-10% decile pool (s3.2)
TOP_K = 20                         # top-20 equal weight (s3.2)
H = 10                            # h10 rebalance rhythm (s3.2)
TRAIL_WIN = 252                    # style-regime trail window (s3.3)
TILT_HI, TILT_LO = 0.9, 0.1       # tilt weights (s3.3, no tuning face)
FACES = {"x1": 1.0, "x2": 2.0, "x3": 3.0}   # per-side multipliers on V1
MAXDD_LINE = -0.35                  # descriptive red line (s4)
CRASH_YEAR_LINE = -0.35             # "no crash year" definition (disclosed)
D6_REJECT = 0.7                     # s1 hard line
CRISIS_WINDOWS = [("2015-06-01", "2015-07-31"),
                  ("2016-01-01", "2016-01-31"),
                  ("2024-01-01", "2024-02-29")]   # s4 hard-bound triad
CRISIS_LOG_ABS_R = 0.05             # crisis-day log threshold (s4)
MIN_T, MIN_N = 8000, 5000           # s2 completeness gate
REG6 = ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
        "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01")
JUDGED_CELLS = ("REV20_bare", "REV60_bare", "REV20_tilt", "REV60_tilt")
PBP = 252.0


def _log(msg):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    print(f"[cn_rev_tilt] {msg}", flush=True)


# ---------------------------------------------------------------- panel


def panel_gates(idx, n):
    """s2 data gates, fail-closed."""
    cutoff_ok = str(idx[-1].date()) == EVIDENCE_CUTOFF
    return {"cutoff": str(idx[-1].date()), "cutoff_ok": bool(cutoff_ok),
            "T": int(len(idx)), "T_ok": bool(len(idx) >= MIN_T),
            "N": int(n), "N_ok": bool(n >= MIN_N),
            "all_ok": bool(cutoff_ok and len(idx) >= MIN_T and n >= MIN_N)}


def load_panel():
    """s2 slice-A loader thin-slice (same cache, same ffill, zero network)."""
    from t73_s2_reversal_momentum import load_close
    close, _meta = load_close()
    close = close[close.index <= EVIDENCE_CUTOFF_TS]     # lockbox, belt+braces
    return close


# ---------------------------------------------------------------- selection


def rebal_schedule(T):
    """h10 fixed-frequency schedule, p4_ext_tilt d20_rebal_pos semantics."""
    return list(range(H - 1, T - 1, H))


def signal_valid(close_arr, w):
    """Names with computable REV{w}/MOM{w} signal at each day (same mask)."""
    N = close_arr.shape[1]
    if close_arr.shape[0] <= w:
        return np.zeros_like(close_arr, dtype=bool)
    prev = np.vstack([np.full((w, N), np.nan), close_arr[:-w]])
    return np.isfinite(close_arr) & np.isfinite(prev)


def sig_matrix(close_arr, w, family):
    """REV{w} = -(C_t/C_{t-w} - 1); MOM = exact mirror (s3.1 frozen)."""
    N = close_arr.shape[1]
    if close_arr.shape[0] <= w:
        return np.full_like(close_arr, np.nan)
    mom = close_arr / np.vstack(
        [np.full((w, N), np.nan), close_arr[:-w]]) - 1.0
    return -mom if family == "rev" else mom


def topk_selections(sig, valid, sched):
    """Top-10% decile pool -> top-20 equal weight (s3.2). Ties -> lower
    column index first (np.lexsort secondary key; deterministic)."""
    sels = []
    for r in sched:
        cols = np.flatnonzero(valid[r])
        if cols.size == 0:
            sels.append((r, None))
            continue
        pool_n = max(1, int(math.ceil(cols.size * TOP_POOL_Q)))
        order = np.lexsort((cols, -sig[r, cols]))     # primary: signal desc
        k = min(TOP_K, pool_n)
        sels.append((r, cols[order[:k]]))
    return sels


def null_selections(valid, sched, seed):
    """Same-mask random-signal 20-name selections (s3.4). One rng per draw,
    consumed in schedule order (deterministic; wild_route/xstock canon)."""
    rng = np.random.default_rng(seed)
    sels = []
    for r in sched:
        cols = np.flatnonzero(valid[r])
        if cols.size == 0:
            sels.append((r, None))
            continue
        k = min(TOP_K, cols.size)
        pick = rng.choice(cols, size=k, replace=False)
        sels.append((r, np.sort(pick)))
    return sels


# ---------------------------------------------------------------- simulator


def simulate(close_arr, idx, sels, side_rate, weight_by_r=None):
    """Close-only value sim. sels=[(r, cols|None)]; trades at close of r+1
    (T+1); a rebalance whose selection is empty/None LIQUIDATES to cash.
    weight_by_r: r -> sleeve weight (1.0 bare; 0.9/0.1 tilt; 0.0 warmup).
    Full-timeline daily returns with out-days = 0 (div_lowvol s4 face)."""
    T, N = close_arr.shape
    vals = np.zeros(N)                # per-name yuan value
    cash = 1.0
    trans = {}                        # transition day -> target cols array
    for r, cols in sels:
        e = r + 1
        if e < T:
            trans[e] = (cols if cols is not None
                        else np.empty(0, dtype=np.int64))
    w_of = {r: (float(weight_by_r.get(r, 1.0)) if weight_by_r else 1.0)
            for r, _ in sels}
    n_sched = len(sels)
    rets = np.zeros(T)
    rets[0] = np.nan                  # day 0 has no interval
    v_prev = 1.0
    n_entries = n_trades = n_active = 0
    turnover_total = cost_total = 0.0
    k_list = []
    first_entry_day = None
    held = np.empty(0, dtype=np.int64)
    for t in range(1, T):
        if held.size:
            with np.errstate(invalid="ignore"):
                ratio = close_arr[t, held] / close_arr[t - 1, held]
            vals[held] *= np.where(np.isfinite(ratio), ratio, 1.0)
        v = cash + float(vals.sum())
        if t in trans:
            cols = trans[t]
            r = t - 1
            w = w_of.get(r, 1.0)
            k = int(cols.size)
            cur = np.zeros(N)
            if held.size and v > 0:
                cur[held] = vals[held] / v
            tgt = np.zeros(N)
            if w > 0.0 and k > 0:
                tgt[cols] = w / k
            delta = np.abs(tgt - cur)
            turnover = float(delta.sum())
            cost = side_rate * turnover * v
            v_after = v - cost
            n_trades += int((delta > 1e-12).sum())
            if k > 0 and w > 0.0:
                n_entries += int((tgt[cols] > cur[cols] + 1e-12).sum())
                n_active += 1
                k_list.append(k)
                if first_entry_day is None:
                    first_entry_day = t
            turnover_total += turnover
            cost_total += cost
            vals = tgt * v_after
            cash = v_after - float(vals.sum())
            held = np.flatnonzero(vals)
            v_final = v_after
        else:
            v_final = v
        rets[t] = v_final / v_prev - 1.0 if v_prev > 0 else 0.0
        v_prev = v_final
    truncated = bool(float(vals.sum()) > 0)   # window-end open cohort
    series = pd.Series(rets, index=idx)
    return {
        "returns": series,
        "n_entries": n_entries, "n_trades": n_trades,
        "n_rebal": int(len(trans)), "n_active_rebal": n_active,
        "k_min": min(k_list) if k_list else 0,
        "k_max": max(k_list) if k_list else 0,
        "turnover_total": round(turnover_total, 4),
        "cost_total": round(cost_total, 8),
        "first_entry_day": first_entry_day,
        "truncated": truncated,
        "inv_rebal_frac": round(n_active / n_sched, 4) if n_sched else 0.0,
    }


def metrics(rec):
    rets = rec["returns"]
    eq = (1.0 + rets.fillna(0.0)).cumprod()
    out = {
        "sharpe": _sharpe(rets), "ann_ret": _ann(rets), "max_dd": _max_dd(eq),
        "n_entries": rec["n_entries"], "n_trades": rec["n_trades"],
        "n_rebal": rec["n_rebal"],
        "n_active_rebal": rec.get("n_active_rebal"),
        "k_min": rec["k_min"], "k_max": rec["k_max"],
        "turnover_total": rec["turnover_total"],
        "cost_total": rec["cost_total"], "truncated": rec["truncated"],
        "inv_rebal_frac": rec["inv_rebal_frac"],
    }
    oos = rets[rets.index >= pd.Timestamp(OOS_START)]
    out["oos"] = {"sharpe": _sharpe(oos), "ann_ret": _ann(oos),
                  "n_days": int(len(oos))}
    out["yearly"] = {int(y): round(float(g.iloc[-1] / g.iloc[0] - 1.0), 4)
                     for y, g in eq.groupby(eq.index.year)}
    d1 = rets.iloc[1:]
    a = np.abs(d1.to_numpy())
    finite = np.isfinite(a)
    a_f = a[finite]
    argmax_day = str(d1.index[int(np.argmax(a))].date()) if len(a) else None
    out["d1_bounds"] = {
        "median": float(np.median(a_f)) if a_f.size else None,
        "p99_9": float(np.percentile(a_f, 99.9)) if a_f.size else None,
        "max": float(a_f.max()) if a_f.size else None,
        "argmax_day": argmax_day,
        "in_crisis_window": bool(any(
            s <= argmax_day <= e for s, e in CRISIS_WINDOWS))
        if argmax_day else False,
    }
    out["crisis_log"] = _crisis_log(rets)
    out["exempt_single_point"] = _exempt(rets, out["d1_bounds"])
    out["cost_stability"] = None      # filled at batch level (x1 face only)
    return out


def _sharpe(rets):
    r = rets.dropna()
    if len(r) < 20 or float(r.std()) == 0:
        return None
    return round(float(r.mean() / r.std() * math.sqrt(PBP)), 4)


def _ann(rets):
    r = rets.dropna()
    if len(r) < 20:
        return None
    total = float((1.0 + r).prod())
    return round(total ** (PBP / len(r)) - 1.0, 6)


def _max_dd(eq):
    if len(eq) < 2:
        return None
    return round(float((eq / eq.cummax() - 1.0).min()), 6)


def _crisis_log(rets):
    rows = []
    for day, v in rets.iloc[1:].items():
        if np.isfinite(v) and abs(v) >= CRISIS_LOG_ABS_R and any(
                s <= str(day.date()) <= e for s, e in CRISIS_WINDOWS):
            rows.append({"day": str(day.date()), "r1": round(float(v), 6)})
    return rows


def _exempt(rets, bounds):
    """Hard-bound triad (s4): max|d1| day in a crisis window -> single-point
    exemption column (stats ex-that-day), disclosure-only, never a gate."""
    if not bounds["in_crisis_window"]:
        return {"applied": False}
    d1 = rets.iloc[1:]
    drop = pd.Timestamp(bounds["argmax_day"])
    kept = d1[d1.index != drop]
    return {"applied": True, "exempted_day": bounds["argmax_day"],
            "sharpe_ex": _sharpe(kept), "ann_ret_ex": _ann(kept)}


# ---------------------------------------------------------------- checkpoints


def _ck_path(unit):
    return os.path.join(CKPT_DIR, unit + ".npz")


def _ck_save(unit, rec, series):
    os.makedirs(CKPT_DIR, exist_ok=True)
    r = {k: v for k, v in rec.items() if k != "returns"}
    np.savez(_ck_path(unit), meta=json.dumps(r),
             returns=np.asarray(series, dtype=np.float64),
             index=np.asarray([str(d.date()) for d in series.index]))


def _ck_load(unit, idx):
    """Exact resume only on date-window match; any drift -> recompute."""
    p = _ck_path(unit)
    if not os.path.exists(p):
        return None
    try:
        z = np.load(p, allow_pickle=False)
        meta = json.loads(str(z["meta"]))
        dates = [str(x) for x in z["index"]]
        if len(dates) != len(idx) or dates[0] != str(idx[0].date()) \
                or dates[-1] != str(idx[-1].date()):
            return None
        out = dict(meta)
        out["returns"] = pd.Series(z["returns"], index=idx)
        return out
    except Exception:
        return None


def _write_ckpt_gitignore():
    os.makedirs(CKPT_DIR, exist_ok=True)
    p = os.path.join(CKPT_DIR, ".gitignore")
    if not os.path.exists(p):
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("*\n!.gitignore\n")


# ---------------------------------------------------------------- regime axis


def regime_v3_column(idx):
    """Descriptive market-regime axis: REGIME_GUARD v3 four-state series via
    the IMPORTED frozen deep-replay layer (single source, zero rebuild).
    Pre-2005 ETF/index era = structurally unavailable -> None (honest)."""
    try:
        import regime_deep_replay as RDR
        bench = RDR.load_index_bench()
        mats, _ds, _br = RDR.run_matrices(bench)
        states = mats["v3"]["states"]
        col = pd.Series([states.get(d) for d in idx], index=idx,
                        dtype=object)
        per_year = {}
        for y, g in col.groupby(col.index.year):
            counts = {}
            for v in g:
                if isinstance(v, str):
                    counts[v] = counts.get(v, 0) + 1
            per_year[int(y)] = counts
        return {
            "series_states_per_year": per_year,
            "n_days_covered": int(sum(isinstance(v, str) for v in col)),
            "n_days_pre_era_none": int(sum(v is None for v in col)),
            "bench_start": str(bench.index[0].date()),
            "bench_end": str(bench.index[-1].date()),
            "source": "regime_deep_replay.run_matrices v3 (imported "
                      "frozen layer, REGIME_GUARD_DEEP_REPLAY_V2 lineage)",
            "note": "descriptive disclosure only, never a switch gate "
                    "(prereg s3.3); pre-2005-04-08 census days predate "
                    "the hs300 index face -> structurally None",
        }
    except Exception as exc:
        return {"status": "unavailable_error", "error": repr(exc)[:200]}


# ---------------------------------------------------------------- D6


def _corr(a, b, min_overlap=20):
    j = pd.concat([a, b], axis=1, join="inner").dropna()
    if len(j) < min_overlap:
        return None, int(len(j))
    v = float(np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1])
    return round(v, 4), int(len(j))


def d6_block(cell_rets, member_rets):
    """s1: reject face = max|corr| vs REGISTERED members (REG6, ew6 canon);
    same-batch + null family = disclosure faces."""
    out = {"reject_line": D6_REJECT, "members": list(REG6)}
    per_member = {}
    for tid, mr in member_rets.items():
        v, ov = _corr(cell_rets, mr)
        per_member[tid] = {"corr": v, "overlap_days": ov}
    finite = {t: v["corr"] for t, v in per_member.items()
              if v["corr"] is not None}
    argmax = max(finite, key=lambda k: abs(finite[k])) if finite else None
    out["member_face"] = {
        "per_member": per_member,
        "max_abs_corr": round(abs(finite[argmax]), 4) if argmax else None,
        "argmax_member": argmax,
        "reject": bool(argmax is not None
                       and abs(finite[argmax]) >= D6_REJECT),
    }
    return out


def load_member_rets():
    """Registered-trader daily returns via the ew6 canon (div_lowvol
    d6_block precedent; IDENTICAL code path to the live.paper anchor gate)."""
    import ew6_portfolio as E
    from live.paper import load_core
    if E.PRICES_FULL is None:
        E.PRICES_FULL = load_core()
    out, cutoffs = {}, {}
    for tid in REG6:
        r = E.member_run(tid)
        eq = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
        out[tid] = eq.pct_change().dropna()
        cutoffs[tid] = r.get("cutoff")
    return out, cutoffs


# ---------------------------------------------------------------- run / cli


def run() -> int:
    t0 = time.time()
    if os.environ.get("CN_REV_TILT_P1_REFINALIZE") != "1" \
            and os.path.exists(OUT_JSON):
        try:
            j = json.load(open(OUT_JSON, encoding="utf-8"))
            if j.get("ledger"):
                print("idempotent fast path: results/cn_rev_tilt/"
                      "p1_results.json already finalized (ledger block "
                      "present); CN_REV_TILT_P1_REFINALIZE=1 = only redo")
                return 0
        except Exception:
            pass
    if sg.SEED_REGISTRY.get("cn_rev_tilt_p1") != SEED_BASE:
        print("VOID: seed base cn_rev_tilt_p1 not registered in "
              "science_gates.SEED_REGISTRY (prereg s3.4: register BEFORE "
              "run)")
        return 2

    close = load_panel()
    idx = close.index
    gates = panel_gates(idx, close.shape[1])
    if not gates["all_ok"]:
        print("VOID: panel gate FAILED (cutoff/T/N):", json.dumps(gates))
        return 2
    _write_ckpt_gitignore()
    _log(f"panel gates OK: T={gates['T']} N={gates['N']} "
         f"cutoff={gates['cutoff']}")

    close_arr = close.to_numpy(dtype=np.float64)
    T = close_arr.shape[0]
    sched = rebal_schedule(T)
    sigs, valids, sels = {}, {}, {}
    for w in W_SET:
        sigs[("rev", w)] = sig_matrix(close_arr, w, "rev")
        sigs[("mom", w)] = sig_matrix(close_arr, w, "mom")
        valids[w] = signal_valid(close_arr, w)
        sels[("rev", w)] = topk_selections(sigs[("rev", w)], valids[w],
                                           sched)
        sels[("mom", w)] = topk_selections(sigs[("mom", w)], valids[w],
                                           sched)
    _log(f"signals built; schedule={len(sched)} rebalance days")

    resumed = []
    cell_recs = {}

    def run_cell(unit, s, rate, weight_by_r=None):
        ck = _ck_load(unit, idx)
        if ck is not None and "returns" in ck:
            resumed.append(unit)
            return ck
        rec = simulate(close_arr, idx, s, rate, weight_by_r)
        _ck_save(unit, rec, rec["returns"])
        return rec

    # -- judged bare cells x3 faces (REV bare x1 doubles as trail input)
    for w in W_SET:
        cell = f"REV{w}_bare"
        for face, mult in FACES.items():
            cell_recs[(cell, face)] = run_cell(
                f"cell_{cell}_{face}", sels[("rev", w)],
                V1_FLAT_SIDE * mult)
        _log(f"cell {cell}: x1 sharpe="
             f"{_sharpe(cell_recs[(cell, 'x1')]['returns'])} "
             f"entries={cell_recs[(cell, 'x1')]['n_entries']}")

    # -- machinery: MOM mirror bare sleeves at x1 (trail inputs, disclosure)
    mom_x1 = {}
    for w in W_SET:
        mom_x1[w] = run_cell(f"mach_mom{w}_x1", sels[("mom", w)],
                             V1_FLAT_SIDE)
        _log(f"mach_mom{w}_x1: sharpe={_sharpe(mom_x1[w]['returns'])} "
             f"entries={mom_x1[w]['n_entries']}")

    # sanity face (R240 law): never-invested sleeve = panel sickness
    for cell in ("REV20_bare", "REV60_bare"):
        rec = cell_recs[(cell, "x1")]
        if rec["n_entries"] == 0 or rec["inv_rebal_frac"] == 0.0:
            print(f"VOID: {cell} never invested -- all-cash panel "
                  "sickness, refusing verdict")
            return 2
    for w in W_SET:
        if mom_x1[w]["inv_rebal_frac"] == 0.0:
            print(f"VOID: MOM{w} mirror never invested -- refusing verdict")
            return 2

    # -- style-regime trail (s3.3): 252d trailing REV-bare minus MOM-bare
    #    net cum; decision at close r (shift(1) causal), effective r+1
    trail_by_w, tilt_w_by_w = {}, {}
    for w in W_SET:
        rv = cell_recs[(f"REV{w}_bare", "x1")]["returns"].fillna(0.0)
        mm = mom_x1[w]["returns"].fillna(0.0)
        cum_r = (1.0 + rv).cumprod().to_numpy()
        cum_m = (1.0 + mm).cumprod().to_numpy()
        e0 = cell_recs[(f"REV{w}_bare", "x1")]["first_entry_day"]
        pos = np.arange(T)
        win_ok = (pos >= (e0 + TRAIL_WIN)) if e0 is not None \
            else np.zeros(T, dtype=bool)
        cr = cum_r / np.concatenate(
            [np.full(TRAIL_WIN, np.nan), cum_r[:-TRAIL_WIN]])
        cm = cum_m / np.concatenate(
            [np.full(TRAIL_WIN, np.nan), cum_m[:-TRAIL_WIN]])
        trail_vals = cr - cm
        trail_vals[~win_ok] = np.nan
        tw = {}
        for r in sched:
            tv = trail_vals[r]
            tw[r] = 0.0 if not np.isfinite(tv) else \
                (TILT_HI if tv > 0 else TILT_LO)
        trail_by_w[w] = {
            "first_active_rebalance": next(
                (r for r in sched if tw[r] > 0), None),
            "warmup_rebalances": int(sum(1 for r in sched if tw[r] == 0.0)),
            "n_rev_regime": int(sum(1 for r in sched if tw[r] == TILT_HI)),
            "n_mom_regime": int(sum(1 for r in sched if tw[r] == TILT_LO)),
        }
        tilt_w_by_w[w] = tw
    _log(f"trail built: {json.dumps(trail_by_w, default=str)[:220]}")

    # -- judged tilt cells x3 faces (tilt weight series frozen at x1-caliber
    #    trail; faces differ ONLY in rate -- pure cost stress)
    for w in W_SET:
        cell = f"REV{w}_tilt"
        for face, mult in FACES.items():
            cell_recs[(cell, face)] = run_cell(
                f"cell_{cell}_{face}", sels[("rev", w)],
                V1_FLAT_SIDE * mult, tilt_w_by_w[w])
        _log(f"cell {cell}: x1 sharpe="
             f"{_sharpe(cell_recs[(cell, 'x1')]['returns'])}")

    # -- census equal-weight baseline, same rhythm (s3.4 passive)
    ew_sels = []
    for r in sched:
        cols = np.flatnonzero(np.isfinite(close_arr[r]))
        ew_sels.append((r, cols if cols.size else None))
    ew_rec = run_cell("baseline_census_ew", ew_sels, V1_FLAT_SIDE)

    # -- K=50 same-mask nulls on the judged x1 face (s3.4; wild_route canon)
    null_recs = []
    for k in range(K_NULLS):
        ns = null_selections(valids[20], sched, SEED_BASE + k)
        null_recs.append(run_cell(f"null_{k:02d}", ns, V1_FLAT_SIDE))
    null_vals = [(_sharpe(r["returns"]) or 0.0) for r in null_recs]
    mu, sigma = float(np.mean(null_vals)), float(np.std(null_vals, ddof=1))
    null_pool = {
        "values": [round(v, 6) for v in null_vals],
        "coverage": {"n_values": len(null_vals), "mu": mu, "sigma": sigma,
                     "schemas_parsed": [f"cn_rev_tilt_p1: {K_NULLS} "
                                        f"same-mask random-signal 20-name "
                                        f"h10 sleeves (seeds 20260930+i)"],
                     "known_unparsed": []},
    }
    _log(f"nulls: K={K_NULLS} mu={mu:.4f} sigma={sigma:.4f}")

    # census gate (r188 law): every unit computed before finalize
    units_expected = (2 * len(FACES)              # REV bare cells
                      + len(W_SET)                # MOM machinery
                      + 2 * len(FACES)            # REV tilt cells
                      + 1 + K_NULLS)              # baseline + nulls
    units_have = len(cell_recs) + len(mom_x1) + 1 + len(null_recs)
    if units_have < units_expected:
        print(f"finalize census gate: {units_have}/{units_expected} units "
              "-- premature finalize refused, no artifact written")
        return 2

    # -- gates (shared library, zero hand-copied lines; prereg s4)
    line = sg.skill_line_v2(batch_cells=BATCH_CELLS, pool="core48",
                            null_pool=null_pool)
    g1, dsr, g2 = {}, {}, {}
    judged_series = {}
    for cell in JUDGED_CELLS:
        rec = cell_recs[(cell, "x1")]
        rets = rec["returns"].iloc[1:]        # drop NaN head interval
        judged_series[cell] = rets
        g1[cell] = sg.g1_prime_v2(
            sharpe_full=_sharpe(rets), returns=rets,
            batch_cells=BATCH_CELLS, pool="core48", null_pool=null_pool,
            n_trades=rec["n_trades"], n_entries=rec["n_entries"])
        dsr[cell] = sg.deflated_sharpe_ratio(
            rets, n_trials=line["n_eff"], var_null_sr=sigma ** 2)
    fam_pbo = cscv_pbo(align_returns(judged_series))
    for cell in JUDGED_CELLS:
        g2[cell] = sg.g2_registration_v2(
            g1_pass=bool(g1[cell]["pass_v2"]), dsr=dsr[cell],
            pbo=fam_pbo["pbo"])

    # fail-closed (r119/r204 family): errored gate verdicts never read 0-pass
    g1_errs = {c: v.get("error") for c, v in g1.items()
               if isinstance(v, dict) and "error" in v}
    if g1_errs:
        first = next(iter(g1_errs.items()))
        print(f"finalize FAIL-CLOSED: g1 errored for {len(g1_errs)}/"
              f"{len(g1)} cells (first: {first[0]} -> "
              f"{str(first[1])[:120]}) -- no artifact written")
        return 2

    # -- D6 (registered members + same-batch disclosure)
    try:
        member_rets, member_cutoffs = load_member_rets()
        d6 = {c: d6_block(judged_series[c], member_rets)
              for c in JUDGED_CELLS}
        d6["member_cutoffs"] = member_cutoffs
    except Exception as exc:
        d6 = {"status": "pending_error", "error": repr(exc)[:200]}
    same_batch = {}
    for a in JUDGED_CELLS:
        row = {}
        for b in JUDGED_CELLS:
            if a == b:
                continue
            v, ov = _corr(judged_series[a], judged_series[b])
            row[b] = {"corr": v, "overlap_days": ov}
        same_batch[a] = row

    # -- descriptive clauses + cost stability (s4; disclosure, never gates)
    descriptive = {}
    for cell in JUDGED_CELLS:
        x1m = metrics(cell_recs[(cell, "x1")])
        yr1 = x1m["yearly"]
        stable = {}
        for face in ("x2", "x3"):
            yf = metrics(cell_recs[(cell, face)])["yearly"]
            common = [y for y in yr1 if y in yf]
            stable[face] = {
                "sign_match_years": int(sum(
                    1 for y in common if (yr1[y] > 0) == (yf[y] > 0))),
                "n_common_years": len(common),
            }
        x1m["cost_stability"] = stable
        descriptive[cell] = {
            "full_ann_positive": bool((x1m["ann_ret"] or 0) > 0),
            "oos_dual_positive": bool((x1m["oos"]["sharpe"] or 0) > 0
                                      and (x1m["oos"]["ann_ret"] or 0) > 0),
            "max_dd_line_pass": bool((x1m["max_dd"] or 0) >= MAXDD_LINE),
            "no_crash_year": bool(all(
                v > CRASH_YEAR_LINE for v in yr1.values())),
            "crash_year_line": CRASH_YEAR_LINE,
            "x2_x3_yearly_stability": stable,
        }

    # -- regime descriptive columns (market v3 axis vs style axis)
    reg_col = regime_v3_column(idx)
    style_axis = {}
    for w in W_SET:
        tw = tilt_w_by_w[w]
        per_year = {}
        for r in sched:
            y = int(idx[r].year)
            per_year.setdefault(y, {"rev": 0, "mom": 0, "warmup": 0})
            v = tw[r]
            key = "warmup" if v == 0.0 else ("rev" if v == TILT_HI
                                             else "mom")
            per_year[y][key] += 1
        style_axis[f"REV{w}_tilt"] = {
            "per_year_rebalance_counts": per_year,
            "trail_summary": trail_by_w[w],
        }

    # -- cells block (series stripped from per-face records)
    cells_out = {}
    for cell in JUDGED_CELLS:
        per_face = {}
        for face in FACES:
            mrec = metrics(cell_recs[(cell, face)])
            if face == "x1":
                mrec["cost_stability"] = descriptive[cell][
                    "x2_x3_yearly_stability"]
            per_face[face] = mrec
        cells_out[cell] = per_face
    mach_out = {f"mom{w}_bare_x1": metrics(mom_x1[w]) for w in W_SET}
    judged_returns_audit = {
        cell: [round(float(v), 6) for v in judged_series[cell].tolist()]
        for cell in JUDGED_CELLS}

    nulls_out = {
        "config": {"base": SEED_BASE, "registered": "cn_rev_tilt_p1",
                   "draws": K_NULLS, "face": "x1_judged",
                   "mask": "REV20 signal-valid mask (primary law face, "
                           "s2 slice-A lineage)",
                   "selection": "uniform 20 of valid per rebalance "
                                "(same rhythm, same universe)"},
        "n_values": len(null_vals),
        "values_rounded": null_pool["values"],
        "coverage": null_pool["coverage"],
    }
    baseline_out = {
        "census_ew": metrics(ew_rec),
        "note": "passive = census equal-weight same-rhythm sleeve "
                "(s3.4); skill-line passive anchor = core48 pool via "
                "the shared library (s4)",
    }

    led = sg.append_ledger(
        "CN-REV-TILT-P1", LEDGER_TRIALS,
        file_name="results/cn_rev_tilt/p1_results.json",
        evidence_cutoff=EVIDENCE_CUTOFF,
        note="4 judged cells REV{20,60} x {bare,regime-tilt} + K50 "
             "same-mask random nulls (seeds 20260930+i, registered "
             "cn_rev_tilt_p1); prereg research/CN_REV_TILT_PREREG.md "
             "frozen R245/R246; T-2026-09-26-73 s3 slice-1")

    att = json.load(open(ATT_JSON, encoding="utf-8"))
    d6_rejects = ({c: ((d6.get(c) or {}).get("member_face", {})
                       .get("reject")) for c in JUDGED_CELLS}
                  if d6.get("status") != "pending_error" else None)
    att["entries"].append({
        "batch": "CN-REV-TILT-P1",
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kind": "measurement",
        "cells_ledger_delta": LEDGER_TRIALS,
        "ledger_total_after": led["total"],
        "gates": {
            "panel_pass": True,
            "g1_prime_pass": {c: bool(g1[c]["pass_v2"])
                              for c in JUDGED_CELLS},
            "g2_eligible": {c: bool(g2[c]["eligible_v2"])
                            for c in JUDGED_CELLS},
            "d6_reject": d6_rejects,
        },
        "eliminated": LEDGER_TRIALS - sum(
            1 for c in JUDGED_CELLS if g2[c]["eligible_v2"]),
        "refs": {"prereg": "research/CN_REV_TILT_PREREG.md",
                 "ticket": TICKET},
    })

    import hashlib
    prereg_sha = hashlib.sha256(
        open(PREREG, "rb").read().replace(b"\r\n", b"\n")).hexdigest()

    payload = {
        **sg.cutoff_meta(EVIDENCE_CUTOFF),
        "meta": {
            "batch": "CN-REV-TILT-P1", "ticket": TICKET,
            "prereg": "research/CN_REV_TILT_PREREG.md",
            "prereg_sha256_lf_normalized": prereg_sha,
            "judge_face": "x1 (V1 13.041bp/side flat, alloc_backtest "
                          "single source); x2/x3 stress tracks",
            "seed_base_registered": "cn_rev_tilt_p1=20260930",
            "cost_basis": f"V1_FLAT_SIDE={V1_FLAT_SIDE} per side on "
                          "turnover; close-only face (no ADV -> V2 "
                          "uncomputable, honest per prereg s3.2)",
            "accounting": "signal close r -> trade close r+1 (T+1); "
                          "cohort holds 10 close-to-close intervals; "
                          "empty-selection rebalance liquidates to cash; "
                          "out-days = 0; ffill frozen-tail convention "
                          "inherited from P1C close (s2 single-source)",
            "machine": _machine_id(),
        },
        "panel_gates": gates,
        "cells": cells_out,
        "machinery_mom_mirror_bare": mach_out,
        "trail_axis": {"per_w": {str(k): v for k, v in trail_by_w.items()}},
        "nulls": nulls_out,
        "baselines": baseline_out,
        "skill_line": line,
        "g1_prime_v2": g1,
        "g2_registration_v2": g2,
        "family_pbo": {k: fam_pbo[k] for k in
                       ("pbo", "n_blocks", "n_trials", "n_rows",
                        "n_combinations") if k in fam_pbo},
        "dsr": dsr,
        "d6_correlation": d6,
        "same_batch_corr": same_batch,
        "descriptive": descriptive,
        "regime_columns": {
            "market_v3_axis": reg_col,
            "style_tilt_axis": style_axis,
        },
        "judged_x1_returns_6dp_audit": judged_returns_audit,
        "n_trials": LEDGER_TRIALS,
        "audit": {
            "elapsed_sec": round(time.time() - t0, 1),
            "workers": 1,
            "units_expected": units_expected,
            "units_fresh_this_run": units_expected - len(resumed),
            "units_resumed_from_checkpoint": len(resumed),
            "resumed_units_head": resumed[:80],
            "blind_run_flags": {
                "deterministic_sim": "no wall-clock inside sim outputs; "
                                     "double-run byte identity via selftest",
                "cost_faces_same_trades": "selections + tilt weights "
                                          "frozen at x1-caliber layer; "
                                          "faces differ only in rate",
            },
        },
        "ledger": led,
    }
    json.loads(json.dumps(payload, default=str))     # validate before write
    tmp = OUT_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, default=str)
    os.replace(tmp, OUT_JSON)
    tmp = ATT_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(att, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, ATT_JSON)
    _write_csv(cells_out, g1, g2, d6)
    _log(f"finalize: ledger total={led['total']} | g1="
         f"{ {c: g1[c]['pass_v2'] for c in JUDGED_CELLS} } g2="
         f"{ {c: g2[c]['eligible_v2'] for c in JUDGED_CELLS} } | "
         f"elapsed={round(time.time() - t0, 1)}s")
    print(f"[cn_rev_tilt] written {OUT_JSON}; g1="
          f"{ {c: g1[c]['pass_v2'] for c in JUDGED_CELLS} }")
    return 0


def _write_csv(cells_out, g1, g2, d6):
    import csv as _csv
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as fh:
        w = _csv.writer(fh)
        w.writerow(["cell", "face", "sharpe", "ann_ret", "max_dd",
                    "oos_sharpe", "oos_ann", "n_entries", "n_trades",
                    "n_rebal", "n_active_rebal", "k_min", "k_max",
                    "turnover", "cost_total", "g1_pass", "g2_eligible",
                    "d6_max_abs_corr"])
        for cell, per_face in cells_out.items():
            for face, m in per_face.items():
                mf = ((d6.get(cell) or {}).get("member_face", {})
                      if face == "x1" else {})
                w.writerow([cell, face, m["sharpe"], m["ann_ret"],
                            m["max_dd"], m["oos"]["sharpe"],
                            m["oos"]["ann_ret"], m["n_entries"],
                            m["n_trades"], m["n_rebal"],
                            m.get("n_active_rebal"), m["k_min"],
                            m["k_max"], m["turnover_total"],
                            m["cost_total"],
                            g1[cell]["pass_v2"] if face == "x1" else "",
                            g2[cell]["eligible_v2"] if face == "x1" else "",
                            mf.get("max_abs_corr", "")])


def _machine_id():
    try:
        return json.load(open(os.path.join(ROOT, "fleet", "machine.json"),
                              encoding="utf-8-sig"))["machine_id"]
    except Exception:
        return os.environ.get("COMPUTERNAME", "unknown")


# ---------------------------------------------------------------- selftest

def _mk_panel(T=420, N=12, seed=20260926):
    """Hermetic synthetic close panel (no real data; R99-safe)."""
    idx = pd.bdate_range("2020-01-01", periods=T)
    syms = [f"{600000 + j:06d}" for j in range(N)]
    rng = np.random.default_rng(seed)
    base = 10.0 + np.cumsum(rng.normal(0, 0.02, (T, N)), axis=0)
    base = np.maximum(base, 2.0)
    close = pd.DataFrame(base, index=idx, columns=syms)
    close.iloc[:30, 5] = np.nan          # late-listed col (NaN head)
    if N > 7 and T > 100:
        close.iloc[100, 7] = np.nan       # one raw-NaN cell (ffill face)
    return close.ffill(), idx


def selftest() -> int:
    fails = []

    def ok(fid, cond, detail=""):
        print(f"  [{'PASS' if cond else 'FAIL'}] {fid} {detail}")
        if not cond:
            fails.append(fid)

    # frozen constants drift guards (prereg numbers)
    ok("[C1] frozen constants", all([
        SEED_BASE == 20_260_930 and
        sg.SEED_REGISTRY.get("cn_rev_tilt_p1") == SEED_BASE,
        K_NULLS == 50, BATCH_CELLS == 4, LEDGER_TRIALS == 54,
        TOP_POOL_Q == 0.10 and TOP_K == 20, H == 10 and TRAIL_WIN == 252,
        TILT_HI == 0.9 and TILT_LO == 0.1, D6_REJECT == 0.7,
        abs(V1_FLAT_SIDE - 0.0013041) < 1e-12,
        EVIDENCE_CUTOFF == "2026-09-22" and OOS_START == "2025-01-01",
        MIN_T == 8000 and MIN_N == 5000,
        IS_END == "2024-12-31",
    ]))

    # [C2] panel gate: wrong cutoff / short panel refused
    idx_bad = pd.bdate_range("2020-01-01", periods=100)
    idx_ok = pd.DatetimeIndex(
        list(pd.bdate_range("2019-01-01", periods=8000))
        + [EVIDENCE_CUTOFF_TS])
    ok("[C2] panel gate fail-closed",
       (not panel_gates(idx_bad, 6000)["all_ok"])
       and panel_gates(idx_ok, 5000)["all_ok"])

    # [F1] schedule + T+1 + close-only accounting hand math
    T, N = 60, 6
    idx = pd.bdate_range("2020-01-02", periods=T)
    cl = np.ones((T, N)) * 10.0
    for t in (11, 12, 13):
        cl[t, 0] = cl[t - 1, 0] * 1.10      # name0 +10% on days 11-13
    sels = [(9, np.array([0, 1])), (19, None), (29, np.array([2])),
            (39, np.array([0])), (49, None)]
    rec = simulate(cl, idx, sels, 0.0)      # zero cost first
    r = rec["returns"]
    # entry at close of day 10 (r=9): day-10 return still cash = 0;
    # first sleeve interval = day 11: half the sleeve grew +10% -> +5%
    ok("[F1] T+1 entry timing (first interval day 11)",
       float(r.iloc[10]) == 0.0 and abs(float(r.iloc[11]) - 0.05) < 1e-12,
       f"r10={r.iloc[10]} r11={r.iloc[11]}")
    ok("[F1] bookkeeping + empty-selection liquidation",
       rec["n_entries"] == 4 and rec["first_entry_day"] == 10
       and rec["k_max"] == 2 and rec["truncated"] is False
       and rec["n_active_rebal"] == 3,
       f"entries={rec['n_entries']} active={rec['n_active_rebal']}")
    sels2 = [(49, np.array([0]))]
    rec2 = simulate(cl, idx, sels2, 0.0)
    ok("[F1] window-end truncation flag", rec2["truncated"] is True)

    # [F2] turnover cost math incl. tilt weight change (flat px, no drift)
    cl_flat = np.ones((60, 4)) * 10.0
    sels_t = [(rr, np.array([0, 1])) for rr in (9, 19, 29, 39, 49)]
    w_hi = {9: 0.9, 19: 0.9, 29: 0.1, 39: 0.1, 49: 0.9}
    rate = 0.0013041
    rec3 = simulate(cl_flat, idx, sels_t, rate, w_hi)
    # e=10 buy 0.9; e=20 flat hold (0); e=30 shift 0.8; e=40 flat; e=50
    # buy 0.8; each cost compounds against the shrunken account value
    v_exp, cost_exp = 1.0, 0.0
    for to in (0.9, 0.0, 0.8, 0.0, 0.8):
        c = rate * to * v_exp
        cost_exp += c
        v_exp -= c
    ok("[F2] turnover cost math (0.9 buy + 0.8 + 0.8 shifts, compounded)",
       abs(rec3["cost_total"] - round(cost_exp, 8)) < 1e-12,
       f"cost={rec3['cost_total']} exp={cost_exp}")
    r3 = rec3["returns"]
    ok("[F2] cost booked on transition day",
       abs(float(r3.iloc[10]) + 0.9 * rate) < 1e-9
       and float(r3.iloc[11]) == 0.0, f"r10={r3.iloc[10]}")

    # [F3] drifted-weight turnover: hold-drift then reset to equal
    cl_dr = np.ones((40, 2)) * 10.0
    for t in range(10, 20):
        cl_dr[t, 0] = cl_dr[t - 1, 0] * 1.01      # name0 grows in period
    cl_dr[20:, 0] = cl_dr[19, 0]                  # carry flat after growth
    sels_dr = [(9, np.array([0, 1])), (19, np.array([0, 1]))]
    rec4 = simulate(cl_dr, idx[:40], sels_dr, 0.0)
    # growth close[10] -> close[20] for name0 = 1.01^9 (steps at t=11..19,
    # t=20 flat); e=10 initial buy turnover 1.0; e=20 reset drift
    g = 1.01 ** 9
    w0 = g / (g + 1.0)
    exp_to = 1.0 + 2 * abs(w0 - 0.5)
    ok("[F3] drifted-weight reset turnover",
       abs(rec4["turnover_total"] - round(exp_to, 4)) < 1e-12,
       f"to={rec4['turnover_total']} exp={exp_to:.6f}")

    # [F4] decile pool + top-k + tie determinism
    T5, N5 = 120, 250
    idx5 = pd.bdate_range("2020-01-02", periods=T5)
    cl5 = np.ones((T5, N5)) * 10.0
    cl5[29:, 0:25] = 5.0                # 25 crashed names -> tied strongest
    sig = sig_matrix(cl5, 20, "rev")
    val = signal_valid(cl5, 20)
    sched5 = rebal_schedule(T5)          # 9,19,...,119? no: range(9,119,10)
    sels5 = topk_selections(sig, val, sched5)
    r39 = dict(sels5)[39]
    ok("[F4] top-decile -> top-20, crashed lead, tie order frozen",
       r39 is not None and len(r39) == TOP_K
       and list(r39) == list(range(20)),
       f"sel_head={list(r39)[:6] if r39 is not None else None}...")
    cl6 = np.ones((120, 8)) * 10.0
    cl6[29:, 0] = 5.0
    sig6 = sig_matrix(cl6, 20, "rev")
    val6 = signal_valid(cl6, 20)
    sels6 = topk_selections(sig6, val6, sched5)
    r6 = dict(sels6)[39]
    ok("[F4] k = min(TOP_K, pool) on tiny universe",
       r6 is not None and len(r6) == 1 and 0 in r6)

    # [F5] MOM mirror = rank mirror of REV
    a = np.abs(sig_matrix(cl5, 20, "rev")
               - (-sig_matrix(cl5, 20, "mom")))
    ok("[F5] MOM = exact mirror of REV", bool(np.nanmax(a) == 0.0))
    sel_rev = dict(topk_selections(sig_matrix(cl5, 20, "rev"), val,
                                   sched5))[39]
    sel_mom = dict(topk_selections(sig_matrix(cl5, 20, "mom"), val,
                                   sched5))[39]
    ok("[F5] mirror sleeve picks top gainers (disjoint)",
       0 not in sel_mom and len(set(sel_rev) & set(sel_mom)) == 0)

    # [F6] trail warmup + sign rule + shift(1) causality
    Tt = 300
    idxt = pd.bdate_range("2020-01-02", periods=Tt)
    rev_ret = np.zeros(Tt)
    mom_ret = np.zeros(Tt)
    e0 = 30
    rev_ret[e0 + 1:] = 0.01
    cum_r = np.cumprod(1.0 + rev_ret)
    cum_m = np.cumprod(1.0 + mom_ret)

    def _trail_fn(r, cum):
        if r - TRAIL_WIN + 1 < e0 + 1 or r - TRAIL_WIN < 0:
            return None
        w0i = r - TRAIL_WIN
        return (cum[r] / cum[w0i]) - (cum_m[r] / cum_m[w0i])

    sched_t = rebal_schedule(Tt)
    ws = {}
    for rr in sched_t:
        tv = _trail_fn(rr, cum_r)
        ws[rr] = 0.0 if tv is None or not np.isfinite(tv) else \
            (TILT_HI if tv > 0 else TILT_LO)
    ok("[F6] warmup cash before e0+252, then rev regime",
       all(ws[rr] == 0.0 for rr in sched_t if rr < e0 + TRAIL_WIN)
       and ws[sched_t[-1]] == TILT_HI)
    rev_ret2 = rev_ret.copy()
    rev_ret2[-1] = 0.5                       # wild FUTURE-day move
    cum_r2 = np.cumprod(1.0 + rev_ret2)
    probe_r = sched_t[-1]                     # active decision point
    ok("[F6] shift(1) causality (future-day perturbation inert at r)",
       abs((_trail_fn(probe_r, cum_r) or 0.0)
           - (_trail_fn(probe_r, cum_r2) or 0.0)) < 1e-12)

    # [F7] nulls: determinism + same-mask + divergence
    v7 = signal_valid(cl5, 20)
    n1 = null_selections(v7, sched5, SEED_BASE)
    n2 = null_selections(v7, sched5, SEED_BASE)
    n3 = null_selections(v7, sched5, SEED_BASE + 1)
    ok("[F7] null same-seed identical",
       all((a2 is None) == (b2 is None) and
           (a2 is None or np.array_equal(a2, b2))
           for (_ra, a2), (_rb, b2) in zip(n1, n2)))
    ok("[F7] null diff-seed diverges + mask respected",
       any(not np.array_equal(a2, b2)
           for (_ra, a2), (_rb, b2) in zip(n1, n3))
       and all(cols is None or
               set(cols.tolist()) <= set(np.flatnonzero(v7[rr]).tolist())
               for rr, cols in n1))

    # [F8] gates wiring: coverage-carrying pool (r217 law) + real verdicts
    fake_nulls = [0.01 * ((k * 37) % 23 - 11) for k in range(50)]
    pool = {"values": fake_nulls,
            "coverage": {"n_values": 50, "mu": float(np.mean(fake_nulls)),
                         "sigma": float(np.std(fake_nulls, ddof=1)),
                         "schemas_parsed": ["selftest"],
                         "known_unparsed": []}}
    rets8 = pd.Series([0.001 * ((k * 53) % 17 - 8) for k in range(300)],
                      index=pd.bdate_range("2020-01-02", periods=300))
    v8 = sg.g1_prime_v2(sharpe_full=0.3, returns=rets8, batch_cells=4,
                        pool="core48", n_trades=99, n_entries=99,
                        null_pool=pool)
    ok("[F8] g1 verdict real fields (no error)",
       "pass_v2" in v8 and "skill_line" in v8 and "bootstrap_ci" in v8
       and "error" not in v8)
    try:
        sg.g1_prime_v2(sharpe_full=0.3, returns=rets8, batch_cells=4,
                       pool="core48", null_pool={"values": fake_nulls})
        ok("[F8] values-only pool raises KeyError (r217 proof)", False)
    except KeyError:
        ok("[F8] values-only pool raises KeyError (r217 proof)", True)
    g2v = sg.g2_registration_v2(g1_pass=True, dsr={"dsr": 0.97}, pbo=0.10)
    ok("[F8] g2 verdict columns",
       g2v["eligible_v2"] is True and g2v["dsr_ok"] and g2v["pbo_ok"])
    g2m = sg.g2_registration_v2(g1_pass=False, dsr={"dsr": 0.99}, pbo=0.0)
    ok("[F8] g2 fail-closed on g1 miss",
       g2m["eligible_v2"] is False and "g1_prime_v2" in g2m["missing_inputs"])

    # [F9] family PBO wiring over 4 synthetic cells
    fam = {f"c{i}": pd.Series(
        np.random.default_rng(i).normal(0.0005 * (i + 1), 0.01, 400),
        index=pd.bdate_range("2020-01-02", periods=400)) for i in range(4)}
    pbo = cscv_pbo(align_returns(fam))
    ok("[F9] cscv 8 blocks over 4-cell grid",
       pbo["n_blocks"] == 8 and pbo["n_trials"] == 4
       and 0.0 <= pbo["pbo"] <= 1.0)

    # [F10] crisis exemption logic + hard-bound columns
    rets_c = pd.Series(np.zeros(300),
                       index=pd.bdate_range("2014-06-02", periods=300))
    big_day = pd.Timestamp("2015-07-08")
    # pandas 3.x: s[int] = v is LABEL-based and appends an int-labeled row
    # on a datetime index (len+1, object dtype) -- positional via .iloc only
    rets_c.iloc[rets_c.index.get_loc(big_day)] = -0.092
    bnd = {"argmax_day": str(big_day.date()), "in_crisis_window": True,
           "median": 0.0, "p99_9": 0.0, "max": 0.092}
    ex = _exempt(rets_c, bnd)
    ok("[F10] crisis-window single-point exemption",
       ex["applied"] is True and ex["exempted_day"] == "2015-07-08")
    ok("[F10] crisis log captures >=5% crisis-day",
       len(_crisis_log(rets_c)) == 1)
    nb = {"argmax_day": "2019-03-08", "in_crisis_window": False,
          "median": 0.0, "p99_9": 0.0, "max": 0.092}
    ok("[F10] out-of-window max -> no exemption",
       _exempt(rets_c, nb)["applied"] is False)

    # [F11] full mini-pipeline determinism (double-run byte identity)
    def _mini():
        cl_m, idx_m = _mk_panel(T=420, N=12)
        arr = cl_m.to_numpy(dtype=np.float64)
        sch = rebal_schedule(arr.shape[0])
        out = {}
        for fam2 in ("rev", "mom"):
            sg_m = sig_matrix(arr, 20, fam2)
            vv = signal_valid(arr, 20)
            ss = topk_selections(sg_m, vv, sch)
            rr = simulate(arr, idx_m, ss, V1_FLAT_SIDE)
            out[fam2] = {"sharpe": _sharpe(rr["returns"]),
                         "entries": rr["n_entries"],
                         "to": rr["turnover_total"],
                         "rets": [round(float(x), 8) for x in
                                  rr["returns"].tolist()]}
        return json.dumps(out, sort_keys=True)

    a11, b11 = _mini(), _mini()
    ok("[F11] mini-pipeline double-run byte identity", a11 == b11)

    # [F12] census EW baseline: equal-weight + same rhythm
    cl_e = np.ones((60, 3)) * 10.0
    for t in range(1, 60):
        cl_e[t, 0] = cl_e[t - 1, 0] * 1.01
    ew_sels = [(rr, np.array([0, 1, 2])) for rr in rebal_schedule(60)]
    rec_e = simulate(cl_e, idx, ew_sels, 0.0)
    ok("[F12] census EW: first interval = mean of member rets",
       abs(float(rec_e["returns"].iloc[11]) - (0.01 + 0.0 + 0.0) / 3)
       < 1e-12, f"r11={rec_e['returns'].iloc[11]}")

    # [F13] checkpoint round-trip: save -> load -> exact returns
    import tempfile
    global CKPT_DIR
    saved = CKPT_DIR
    CKPT_DIR = os.path.join(tempfile.gettempdir(), "cnrev_selftest_ckpt")
    try:
        cl_p, idx_p = _mk_panel(T=200, N=6)
        arrp = cl_p.to_numpy(dtype=np.float64)
        ssp = topk_selections(sig_matrix(arrp, 20, "rev"),
                              signal_valid(arrp, 20),
                              rebal_schedule(200))
        recp = simulate(arrp, idx_p, ssp, V1_FLAT_SIDE)
        _ck_save("selftest_unit", recp, recp["returns"])
        lod = _ck_load("selftest_unit", idx_p)
        ok("[F13] ckpt round-trip exact + date-drift refusal",
           lod is not None and np.array_equal(
               np.asarray(recp["returns"]), np.asarray(lod["returns"]),
               equal_nan=True)
           and lod["n_entries"] == recp["n_entries"]
           and _ck_load("selftest_unit", idx_p[:-1]) is None)
    finally:
        CKPT_DIR = saved
        import shutil
        shutil.rmtree(os.path.join(tempfile.gettempdir(),
                                   "cnrev_selftest_ckpt"),
                      ignore_errors=True)

    # [F14] metrics block: OOS split + yearly + d1 bounds
    mret = pd.Series(
        np.random.default_rng(11).normal(0.001, 0.01, 800),
        index=pd.bdate_range("2022-01-03", periods=800))
    mm = {"returns": mret, "n_entries": 40, "n_trades": 80, "n_rebal": 79,
          "n_active_rebal": 79, "k_min": 20, "k_max": 20,
          "turnover_total": 12.0, "cost_total": 0.015, "truncated": False,
          "inv_rebal_frac": 1.0}
    m = metrics(mm)
    ok("[F14] metrics: oos window + yearly keys + d1 bounds",
       m["oos"]["n_days"] == int(
           (mret.index >= pd.Timestamp(OOS_START)).sum())
       and 2022 in m["yearly"] and m["d1_bounds"]["max"] is not None
       and m["sharpe"] is not None)

    # [F15] empty-selection liquidation face (prereg s3.2 exit-to-cash)
    cl_l = np.ones((40, 2)) * 10.0
    sels_l = [(9, np.array([0, 1])), (19, None)]
    rec_l = simulate(cl_l, idx[:40], sels_l, 0.0)
    ok("[F15] empty-selection rebalance liquidates",
       rec_l["truncated"] is False and rec_l["n_active_rebal"] == 1
       and float(rec_l["returns"].iloc[21]) == 0.0)

    print(f"cn_rev_tilt_p1 selftest: {len(fails)} FAIL")
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
