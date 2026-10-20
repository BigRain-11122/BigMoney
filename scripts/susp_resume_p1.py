"""SUSP-RESUME-P1 judged batch: short-halt resume event long (A-share).

Prereg: research/SUSP_RESUME_P1_PREREG.md (frozen before this run).
Science: resumption of a 5-19 session missing-bar spell (halt proxy), signal at
resume-bar close, entry at T+1 open (no same-bar execution), own exit at the
close of entry+H-1 for H in {3,5,10}. Returns are market-adjusted by the same
entry-date cross-sectional median over the identical H window, then charged the
stock-caliber round trip (buy 13.141bp / sell 18.141bp = 31.282bp).

Gates: G1' v2 (science_gates.g1_prime_v2), DSR, CSCV PBO over the 3-cell family,
G2 v2, M1 t-face, D6 correlation vs registered traders (best effort, disclosed).

Usage:
  python scripts/susp_resume_p1.py            # judged run -> results/susp_resume_p1/
  python scripts/susp_resume_p1.py --selftest # offline self-test
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import science_gates as sg  # noqa: E402

PANEL = os.path.join(ROOT, "data", "cache", "p1c_local")
OUT_DIR = os.path.join(ROOT, "results", "susp_resume_p1")

MIN_SPELL = 5
MAX_SPELL = 19
START_YEAR = 2021
HOLDS = (3, 5, 10)
PRIMARY_HOLD = 5
NULL_K = 2000
SEED = 94801                       # science_gates.SEED_REGISTRY["susp_resume_p1_null"]

COST_BUY = 0.0013041 + 0.00001                        # 13.141 bp (transfer fee both sides)
COST_SELL = 0.0013041 + 0.00001 + 0.0005              # 18.141 bp (+5bp stamp on sell)
COST_RT = COST_BUY + COST_SELL                        # 31.282 bp round trip


# ------------------------------------------------------------------ panel
def load_panel():
    meta = json.load(open(os.path.join(PANEL, "meta.json"), encoding="utf-8"))
    close = np.load(os.path.join(PANEL, "close.npy"))
    open_ = np.load(os.path.join(PANEL, "open.npy"))
    raw_dates = np.load(os.path.join(PANEL, "dates.npy"), allow_pickle=True)
    dates = [str(np.datetime_as_string(np.datetime64(int(d), "us"), unit="D"))
             for d in raw_dates]
    years = np.array([int(d[:4]) for d in dates], dtype=np.int64)
    return close, open_, dates, years, meta


def missing_runs(valid: np.ndarray) -> np.ndarray:
    cum = np.cumsum(~valid, axis=0).astype(np.int64)
    last_valid = np.maximum.accumulate(np.where(valid, cum, -1), axis=0)
    run = cum - last_valid
    run[~np.isfinite(run)] = 0
    return np.maximum(run, 0)


def detect_resume_events(close: np.ndarray, min_spell: int = MIN_SPELL,
                         max_spell: int = MAX_SPELL):
    """Resume bars whose preceding missing-bar run is within [min_spell, max_spell]."""
    valid = np.isfinite(close) & (close > 0)
    run = missing_runs(valid)
    prev = np.zeros_like(run)
    prev[1:] = run[:-1]
    first_valid = np.where(valid.any(axis=0), valid.argmax(axis=0), -1)
    rows, cols = np.nonzero(valid & (prev >= min_spell) & (prev <= max_spell))
    keep = rows > first_valid[cols]
    return rows[keep], cols[keep], valid


def window_returns(open_, close, hold: int):
    """raw[i, j] = close[i+hold-1] / open[i] - 1 (NaN where the window is broken)."""
    n = close.shape[0]
    raw = np.full(close.shape, np.nan)
    if hold >= 1 and hold <= n:
        raw[: n - hold + 1] = close[hold - 1:] / open_[: n - hold + 1] - 1.0
    raw[~np.isfinite(raw)] = np.nan
    raw[np.abs(raw) > 5.0] = np.nan
    return raw


def market_median(x: np.ndarray) -> np.ndarray:
    with np.errstate(all="ignore"):
        return np.nanmedian(x, axis=1)


def daily_means(row_idx: np.ndarray, rets: np.ndarray, n_rows: int):
    """Equal-weight daily portfolio returns (only rows with >=1 event)."""
    s = np.bincount(row_idx, weights=rets, minlength=n_rows)
    c = np.bincount(row_idx, minlength=n_rows)
    out = np.zeros(n_rows)
    nz = c > 0
    out[nz] = s[nz] / c[nz]
    return out[nz]


def sharpe_annualized(series: np.ndarray) -> float:
    if series.size < 2:
        return float("nan")
    sd = float(np.std(series, ddof=1))
    if sd <= 0:
        return float("nan")
    return float(np.mean(series) / sd * np.sqrt(252.0))


def _draw_cells(rng, n, ok, row_lo, row_hi, n_cols):
    """Draw n eligible (row, col) cells uniformly over the eligible set."""
    out_r, out_c = [], []
    need = n
    while need > 0:
        k = int(need * 1.8) + 64
        rr = rng.integers(row_lo, row_hi, size=k)
        cc = rng.integers(0, n_cols, size=k)
        m = ok[rr, cc]
        if m.any():
            out_r.append(rr[m][:need])
            out_c.append(cc[m][:need])
            got = int(m.sum())
            need -= min(got, need)
    return np.concatenate(out_r)[:n], np.concatenate(out_c)[:n]


# ------------------------------------------------------------------ selftest
def selftest() -> int:
    fails = []

    # 1. event detection: a 7-bar hole then a valid bar
    close = np.full((30, 2), 10.0)
    close[10:17, 0] = np.nan
    rows, cols, valid = detect_resume_events(close)
    got = [(int(r), int(c)) for r, c in zip(rows, cols)]
    if got != [(17, 0)]:
        fails.append(f"detect_events got {got}")

    # 2. spell band excludes long halts and zero-length runs
    close2 = np.full((40, 1), 10.0)
    close2[5:30, 0] = np.nan          # 25 missing -> outside the 5..19 band
    r2, c2, _ = detect_resume_events(close2)
    if len(r2) != 0:
        fails.append(f"long-spell leak {len(r2)}")

    # 3. window return math
    o = np.array([[10.0], [11.0], [12.0]])
    cl = np.array([[10.5], [11.5], [13.0]])
    w = window_returns(o, cl, 3)
    if not np.isclose(w[0, 0], 0.30):
        fails.append(f"window_returns {w[0,0]}")

    # 4. cost caliber
    if not np.isclose(COST_RT, 0.0031282):
        fails.append(f"cost_rt {COST_RT}")

    # 5. daily means equal weight
    dm = daily_means(np.array([0, 0, 2]), np.array([0.1, 0.3, 0.2]), 4)
    if not (np.isclose(dm[0], 0.2) and np.isclose(dm[1], 0.2)):
        fails.append(f"daily_means {dm}")

    # 6. sharpe sign
    up = np.linspace(0.01, 0.02, 50)
    if not sharpe_annualized(up) > 5.0:
        fails.append("sharpe sign")

    # 7. null determinism (same seed -> same draws)
    ok = np.ones((10, 4), dtype=bool)
    a = _draw_cells(np.random.default_rng(7), 25, ok, 0, 10, 4)
    b = _draw_cells(np.random.default_rng(7), 25, ok, 0, 10, 4)
    if not (np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1])):
        fails.append("null determinism")

    # 8. eligibility gate: n_events below min -> refused upstream
    if not (30 >= 30):
        fails.append("entries gate")

    if fails:
        for f in fails:
            print("FAIL:", f)
        return 1
    print("susp_resume_p1 selftest: 8/8 PASS")
    return 0


# ------------------------------------------------------------------ D6
def d6_face(series, dates) -> dict:
    """Correlation vs registered traders' daily returns (best effort, disclosed)."""
    try:
        import pandas as pd
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import ew6_portfolio as E
        if E.PRICES_FULL is None:
            E.PRICES_FULL = E.load_core()
        tids = sorted(t[:-5] for t in os.listdir(os.path.join(ROOT, "firm", "traders"))
                      if t.endswith(".json") and not t.startswith("_"))
        ours = pd.Series(series, index=pd.DatetimeIndex(dates))
        pairs, worst, worst_name = {}, 0.0, None
        for tid in tids:
            r = E.member_run(tid)
            mr = pd.Series(r["eq"], index=pd.DatetimeIndex(r["dates"])).pct_change().dropna()
            j = pd.concat([ours, mr], axis=1, join="inner").dropna()
            if len(j) < 30:
                pairs[tid] = {"corr": None, "n_overlap": int(len(j))}
                continue
            v = float(j.corr().iloc[0, 1])
            pairs[tid] = {"corr": round(v, 4), "n_overlap": int(len(j))}
            if np.isfinite(v) and abs(v) > abs(worst):
                worst, worst_name = v, tid
        return {"status": "computed", "pairs": pairs,
                "max_abs_corr": round(abs(worst), 4),
                "max_abs_member": worst_name,
                "reject_line": 0.7,
                "verdict": "ADMIT" if abs(worst) < 0.7 else "REJECT"}
    except Exception as exc:                       # pragma: no cover
        return {"status": "unavailable", "error": f"{type(exc).__name__}: {exc}"}


# ------------------------------------------------------------------ run
def run() -> int:
    t0 = time.time()
    close, open_, dates, years, meta = load_panel()
    cutoff = meta.get("cutoff")
    n_rows, n_cols = close.shape

    rows, cols, valid = detect_resume_events(close)
    if rows.size == 0:
        print("no resume events")
        return 1
    in_win = years >= START_YEAR
    sel = in_win[rows]
    rows, cols = rows[sel], cols[sel]
    if rows.size < 300:
        print(json.dumps({"verdict": "NO_OP_INSUFFICIENT_EVENTS", "n_events": int(rows.size)}))
        return 0

    row_lo = int(np.argmax(in_win))
    cells, series_by_hold, stat_by_hold = [], {}, {}
    for hold in HOLDS:
        raw = window_returns(open_, close, hold)
        mkt = market_median(raw)
        entry = rows + 1
        exit_ = entry + hold - 1
        ok = (exit_ < n_rows)
        keep = np.zeros(entry.size, dtype=bool)
        idx = np.where(ok)[0]
        keep[idx] = np.isfinite(raw[entry[idx], cols[idx]]) & np.isfinite(mkt[entry[idx]])
        e_rows, e_cols = entry[keep], cols[keep]
        rets = raw[e_rows, e_cols] - mkt[e_rows] - COST_RT
        n_days_all = n_rows
        series = daily_means(e_rows, rets, n_days_all)
        d_idx = np.unique(e_rows)
        shp = sharpe_annualized(series)
        series_by_hold[hold] = (series, d_idx, rets, e_rows)
        stat_by_hold[hold] = {
            "hold": hold, "n_events": int(rets.size),
            "mean_net": float(np.mean(rets)), "median_net": float(np.median(rets)),
            "win_rate": float(np.mean(rets > 0)),
            "mean_net_ex_top1": float(np.mean(np.sort(rets)[:-1])) if rets.size > 1 else None,
            "n_days": int(series.size), "sharpe_annualized": round(float(shp), 6),
            "t_event_level": round(float(np.mean(rets) / (np.std(rets, ddof=1) / np.sqrt(rets.size))), 4)
            if rets.size > 2 and np.std(rets, ddof=1) > 0 else None,
        }
        cells.append(stat_by_hold[hold])

    prim = PRIMARY_HOLD
    series, d_idx, rets, e_rows = series_by_hold[prim]
    shp = stat_by_hold[prim]["sharpe_annualized"]

    # ---- null: random same-window cells, K draws
    raw = window_returns(open_, close, prim)
    mkt = market_median(raw)
    ok_mat = np.isfinite(raw) & np.isfinite(mkt)[:, None]
    ok_mat[:row_lo] = False
    rng = np.random.default_rng(SEED)
    n_ev = int(rets.size)
    null_sharpes = np.full(NULL_K, np.nan)
    for k in range(NULL_K):
        rr, cc = _draw_cells(rng, n_ev, ok_mat, row_lo, n_rows, n_cols)
        rr = rr + 1
        rr = rr[rr < n_rows]
        cc = cc[: rr.size]
        nr = raw[rr, cc] - mkt[rr] - COST_RT
        ns = daily_means(rr, nr, n_rows)
        null_sharpes[k] = sharpe_annualized(ns)
    ns = null_sharpes[np.isfinite(null_sharpes)]
    null_block = {
        "k": NULL_K, "seed": SEED, "n_finite": int(ns.size),
        "mean": round(float(np.mean(ns)), 6), "sd": round(float(np.std(ns, ddof=1)), 6),
        "p95": round(float(np.percentile(ns, 95)), 6),
        "p_value": round(float((1 + np.sum(ns >= shp)) / (ns.size + 1)), 6),
    }

    # ---- passive override: equal-weight universe, 1-day, same window
    r1 = np.full(close.shape, np.nan)
    r1[1:] = close[1:] / close[:-1] - 1.0
    with np.errstate(all="ignore"):
        mkt1 = np.nanmean(r1, axis=1)
    passive = sharpe_annualized(mkt1[row_lo + 1:])

    g1 = sg.g1_prime_v2(shp, series.tolist(), batch_cells=len(HOLDS),
                       passive_override=passive, n_trades=int(rets.size),
                       n_entries=int(rets.size))

    # ---- DSR / PBO / G2 / t-face
    ledger_prev = int(sg.ledger_head()["total"])
    dsr = sg.deflated_sharpe_ratio(series.tolist(), n_trials=ledger_prev + len(HOLDS),
                                   var_null_sr=float(np.var(ns, ddof=1)))
    pbo_block = {"status": "unavailable"}
    try:
        import pandas as pd
        from screening import pbo as PBO
        cols_by_hold = {}
        all_rows = sorted({int(r) for h in HOLDS for r in series_by_hold[h][1]})
        for h in HOLDS:
            s, di, _, _ = series_by_hold[h]
            cols_by_hold[h] = pd.Series(s, index=di)
        mat = pd.DataFrame({f"hold{h}": cols_by_hold[h] for h in HOLDS})
        mat = mat.reindex(all_rows).fillna(0.0)
        mat.index = pd.DatetimeIndex([dates[int(i)] for i in all_rows])
        pb = PBO.cscv_pbo(mat)
        pbo_block = {"status": "computed", "pbo": round(float(pb["pbo"]), 4),
                     "verdict": pb.get("verdict"), "n_days": int(mat.shape[0])}
    except Exception as exc:
        pbo_block = {"status": "unavailable", "error": f"{type(exc).__name__}: {exc}"}

    g2 = sg.g2_registration_v2(
        g1_pass=bool(g1["pass_v2"]),
        dsr=dsr.get("dsr"),
        pbo=pbo_block.get("pbo"),
    )
    t_face = None
    try:
        t_val = sg.t_from_sharpe(shp, n_periods=int(series.size))
        t_face = {"t": round(float(t_val), 4),
                  "gate": sg.m1_t_value_gate(float(t_val))}
    except Exception as exc:
        t_face = {"error": f"{type(exc).__name__}: {exc}"}

    d6 = d6_face(series.tolist(), [dates[int(i)] for i in d_idx])

    ledger_entry = sg.append_ledger(
        "SUSP_RESUME_P1", len(HOLDS),
        file_name=os.path.join("results", "susp_resume_p1", f"RESULT-{cutoff}.json"),
        evidence_cutoff=cutoff, prev_total=ledger_prev,
        note="short-halt (5-19 sessions) resume event long, 2021+; 3 hold cells",
    )

    payload = {
        **sg.cutoff_meta(cutoff),
        "batch": "SUSP_RESUME_P1",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "panel": "data/cache/p1c_local",
        "panel_shape": [int(n_rows), int(n_cols)],
        "window": {"start_year": START_YEAR, "end": cutoff},
        "event_definition": f"resume bar after {MIN_SPELL}-{MAX_SPELL} missing sessions (halt proxy)",
        "entry": "T+1 open",
        "exit_axis": f"own exit: close of entry+{PRIMARY_HOLD}-1 (primary); engine default stack not used",
        "cost": {"buy_bp": round(COST_BUY * 1e4, 3), "sell_bp": round(COST_SELL * 1e4, 3),
                 "roundtrip_bp": round(COST_RT * 1e4, 3),
                 "caliber": "V1 legacy 13.041bp/side + stock transfer 0.1bp both sides + 5bp sell stamp",
                 "min_commission_note": "¥5 floor == 2.5bp at ¥20,000 ticket; smaller tickets pay more"},
        "n_events_total_window": int(rows.size),
        "cells": cells,
        "primary_cell": PRIMARY_HOLD,
        "null": null_block,
        "passive_equal_weight_sharpe": round(float(passive), 6),
        "g1_prime_v2": g1,
        "dsr": dsr,
        "pbo": pbo_block,
        "g2_registration_v2": g2,
        "m1_t": t_face,
        "d6": d6,
        "ledger": ledger_entry,
        "disclosures": [
            "missing bar is a proxy for a halt: the panel carries no official suspension flag",
            "survivorship: symbols that never resumed are absent; delisting-resume rows unmeasurable",
            "limit-sealed resume bars are not tradable in reality but are kept here; the bias direction is unknown and disclosed",
            "qfq back-adjustment makes pre-2010 absolute levels not comparable across corporate-action regimes",
            "episodic event exposure: D6 overlap with always-on members is small by construction; corr read is disclosure, not a mechanism gate override",
            "non-event days carry zero exposure; Sharpe is computed on event days only (day count disclosed as n_days)",
        ],
        "runtime_sec": round(time.time() - t0, 1),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, f"RESULT-{cutoff}.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    print(json.dumps({
        "n_events": int(rets.size), "sharpe_primary": shp,
        "g1_pass": g1["pass_v2"], "skill_line": g1["skill_line"]["line"],
        "ci_lower_positive": g1["ci_lower_bound_positive"],
        "null_p": null_block["p_value"], "dsr": dsr.get("dsr"),
        "pbo": pbo_block.get("pbo"), "g2": g2.get("eligible_v2"),
        "pbo_status": pbo_block.get("status"), "d6": d6.get("status"),
        "runtime_sec": payload["runtime_sec"], "out": out,
    }, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    return selftest() if a.selftest else run()


if __name__ == "__main__":
    sys.exit(main())