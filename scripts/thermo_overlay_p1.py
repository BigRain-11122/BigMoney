"""THERMO-OVERLAY-P1 runner (T-2026-10-10-181-P1 slice-2, O-20261009-2340 sec.2.4).

Universe-EW risk on/off overlay judgment batch on the Money02 full-stock
panel. Design frozen verbatim in research/THERMO-OVERLAY-P1.md (freeze
commit 5c332d987 precedes this run; post-freeze spec edits = none --
runner is part of the freeze). Conventions reused, zero re-implementation:
  - faces: results/regime_thermo/thermo_daily.csv (state axis, 7,216 rows)
    + Money02/data/bars 5,222 parquets (return face; bm-a hosted lane)
  - T+1 lag execution, cost 13bp/side x1 + 26bp/side x2 stress (frozen sec.3)
  - K=200 circular-shift structure-preserving mask nulls, rng(94500+i) i<200
    (SEED_REGISTRY thermo_overlay_p1_nulls; 94_001..94_999 pocket, never
    climbs the 95_000+ N1 staircase)
  - g1_prime_v2/g2_registration_v2/t_from_sharpe/m1/cutoff_meta/append_ledger/
    deflated_sharpe_ratio/closed_family_check: science_gates
  - PBO: screening.pbo.cscv_pbo CSCV-8 (same-family 6-cell grid)
  - D6 member face: cn_rev_tilt_p1 REG6/load_member_rets/_corr (ew6 canon)
  - exit-axis declaration (2) hold-through: this runner has NO stop-loss,
    NO timeout, NO other exit stack -- the overlay mask is the ONLY risk
    exit mechanism (hard assert in run(); engine default exits never load)

Determinism: no wall-clock in content fields; nulls seeded rng(94500+i);
redo (batch already in ledger) recomputes with batch_cells=0 and skips
append (r253 single-count law). Lane guard: bars panel is bm-a-hosted;
other machines probe fail-closed (exit 3, no burn).

Exit codes: 0 normal/no-op; 2 mechanism failure; 3 VOID face-mismatch /
lane refusal (fail-closed, honest message, nothing written).
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

import science_gates as SG  # noqa: E402
from screening.pbo import cscv_pbo  # noqa: E402
from parallel_runner import run_cells_parallel, worker_cap  # noqa: E402  # O-20260930-2355 law-1: workers_plan is CODE

BATCH = "THERMO-OVERLAY-P1"
TRIALS_JUDGED = 6
N_NULLS = 200
BATCH_CELLS = TRIALS_JUDGED + 6 * N_NULLS  # 1,206 (frozen sec.0)
CUTOFF = "2026-09-22"                      # P-5C frozen face, fleet-wide
VALID_FROM = "1996-12-16"                  # limit-board system restoration day
COST_SIDE_X1 = 0.0013                      # 13bp/side V1 legacy stress calibre
COST_SIDE_X2 = 0.0026                      # 26bp/side x2 cost-stress leg (frozen)
NULL_BASE = 94500                          # SEED_REGISTRY thermo_overlay_p1_nulls
PPY = 252.0
D6_REJECT = 0.70
CRASH_YEAR = -0.30                         # descriptive: no year sum <= -30%
MAXDD_LINE = -0.35                         # descriptive: maxdd >= -35%
BARS = os.path.join(ROOT, "Money02", "data", "bars")
THERMO_CSV = os.path.join(ROOT, "results", "regime_thermo", "thermo_daily.csv")
OUT_DIR = os.path.join(ROOT, "results", "thermo_overlay_p1")
OUT = os.path.join(OUT_DIR, "thermo_overlay_p1_results.json")
NULLS_CSV = os.path.join(OUT_DIR, "nulls_detail.csv")
PROBE_RC = os.path.join(ROOT, "results", "_r939bma_thermo_overlay_p1_probe.json")
SELFTEST_RC = os.path.join(ROOT, "results", "_r939bma_thermo_overlay_p1_selftest.json")
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

# frozen sec.2 probe facts (mask marginals -- face misconfiguration tripwire)
FROZEN_MASK_FACTS = {
    "P100":  {"rule": "n_sealed_down(t) >= 100", "off_days": 145, "segments": 109},
    "P500":  {"rule": "n_sealed_down(t) >= 500", "off_days": 46,  "segments": 36},
    "P1000": {"rule": "n_sealed_down(t) >= 1000", "off_days": 20, "segments": 17},
    "H12":   {"rule": "max_height(t) >= 12", "off_days": 1019, "segments": 166},
    "H16":   {"rule": "max_height(t) >= 16", "off_days": 443,  "segments": 91},
    "PH":    {"rule": "(n_sealed_down(t) >= 500) OR (max_height(t) >= 12)",
              "off_days": 1050, "segments": 183},
}
FROZEN_FACE1 = {"rows": 7216, "cols": 13, "first": VALID_FROM, "last": CUTOFF}
FROZEN_FACE2_FILES = 5222


def _void(msg):
    print(f"VOID fail-closed: {msg}")
    sys.exit(3)


def lane_guard():
    """R31 lane law: Money02 bars panel is bm-a-hosted. Other machines =
    probe fail-closed refuse-to-burn (frozen sec.6), honest stdout, no writes."""
    if not os.path.isdir(BARS) or not glob_parquets():
        print("lane guard: Money02 bars panel absent on this machine "
              "(bm-a-hosted lane) -- probe fail-closed refuse-to-burn, nothing written")
        sys.exit(3)


def glob_parquets():
    import glob as _g
    return sorted(_g.glob(os.path.join(BARS, "*.parquet")))


# pool harvest handshake (O-20260930-2355 window; r942 gap fix): the
# worker-side half mirrors lowamp_p1._pool_claim verbatim -- on a
# successful burn (incl. the idempotent fast path) write the closed+ok
# claim so the autofill harvest flip lands the shard done; without it
# a completed burn reads as a crash to the fuse (r496 live family,
# hit once on this runner 2026-10-10 -- claim backfilled by r942).
POOL_ENTRY = "THERMO-OVERLAY-P1-BURN"
POOL_SHARD = "thermo-overlay-p1-burn-0of1"
_CLAIM_STARTED = ""


def _machine_id() -> str:
    try:
        return json.load(open(os.path.join(ROOT, "fleet", "machine.json"),
                              encoding="utf-8"))["machine_id"]
    except Exception:
        return "unknown"


def _now_iso() -> str:
    import datetime
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _pool_claim(detail: str) -> None:
    d = os.path.join(ROOT, "results", "pool_claims",
                     POOL_ENTRY.replace("/", "_"))
    os.makedirs(d, exist_ok=True)
    fp = os.path.join(d, f"{POOL_SHARD}.{_machine_id()}.json")
    now = _now_iso()
    with open(fp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"machine_id": _machine_id(), "state": "closed",
                   "pid": os.getpid(), "heartbeat": now, "outcome": "ok",
                   "exit_code": 0, "started": _CLAIM_STARTED,
                   "closed_at": now, "result_ref": detail}, fh,
                  ensure_ascii=False, indent=2, sort_keys=True)
    print("pool claim closed:", os.path.basename(fp))


# ------------------------------------------------------------------ data faces

def load_faces(quiet=False):
    """Both frozen faces + hard completeness gates (frozen sec.2).

    Face 1: thermo_daily.csv state axis. Face 2: bars return face.
    Axis identity asserted (thermo axis == bars union axis in window).
    Returns (dates_index, r_u ndarray, masks dict, audit dict).
    """
    th = pd.read_csv(THERMO_CSV)
    if list(th.columns) != ["date", "n_trade", "n_sealed", "n_touched", "n_sealed_down",
                            "n_broke", "seal_rate", "n_firstboard", "n_lianban2",
                            "n_lianban3", "n_lianban4p", "max_height", "pct_sealed"]:
        _void(f"face1 column schema drift: {len(th.columns)} cols")
    if len(th) != FROZEN_FACE1["rows"]:
        _void(f"face1 rows {len(th)} != frozen {FROZEN_FACE1['rows']}")
    th["date"] = pd.to_datetime(th["date"])
    if str(th["date"].iloc[0].date()) != FROZEN_FACE1["first"] \
            or str(th["date"].iloc[-1].date()) != FROZEN_FACE1["last"]:
        _void(f"face1 window drift: {th['date'].iloc[0].date()}..{th['date'].iloc[-1].date()}")
    if not np.isfinite(th["n_sealed_down"].values).all() \
            or not np.isfinite(th["max_height"].values.astype(float)).all():
        _void("face1 state columns contain NaN (builder invariant broken)")

    nsd = th["n_sealed_down"].values.astype(float)
    mh = th["max_height"].values.astype(float)
    masks = {
        "P100": nsd >= 100,
        "P500": nsd >= 500,
        "P1000": nsd >= 1000,
        "H12": mh >= 12,
        "H16": mh >= 16,
        "PH": (nsd >= 500) | (mh >= 12),
    }
    mask_probe = {}
    for name, m in masks.items():
        m = np.asarray(m, dtype=bool)
        days = int(m.sum())
        segs = int(np.sum(m[1:] & ~m[:-1])) + (1 if m[0] else 0)
        f = FROZEN_MASK_FACTS[name]
        if days != f["off_days"] or segs != f["segments"]:
            _void(f"mask marginal drift cell {name}: {days}/{segs} != frozen "
                  f"{f['off_days']}/{f['segments']} (face misconfiguration)")
        mask_probe[name] = {"off_days": days, "segments": segs, "rule": f["rule"]}

    files = glob_parquets()
    if len(files) != FROZEN_FACE2_FILES:
        _void(f"face2 parquet count {len(files)} != frozen {FROZEN_FACE2_FILES}")
    lo, hi = pd.Timestamp(VALID_FROM), pd.Timestamp(CUTOFF)
    frames, rows_raw, rows_win, rows_valid = [], 0, 0, 0
    sample_info = None
    for i, fp in enumerate(files):
        df = pd.read_parquet(fp, columns=["date", "close", "high", "preclose"])
        if i == 0:
            sample_info = {"file": os.path.basename(fp), "cols": list(df.columns)}
        rows_raw += len(df)
        df = df.drop(columns=["high"])  # declared read face only; unused downstream
        df = df[(df["date"] >= lo) & (df["date"] <= hi)]
        rows_win += len(df)
        df = df.dropna(subset=["close", "preclose"])
        df = df[df["preclose"] >= 1.0]  # penny-row guard (frozen sec.3)
        rows_valid += len(df)
        frames.append(df)
        if not quiet and (i + 1) % 1000 == 0:
            print(f"  loaded {i + 1}/{len(files)}", flush=True)
    panel = pd.concat(frames, ignore_index=True)
    del frames
    panel["r"] = panel["close"] / panel["preclose"] - 1.0

    # axis identity gate: thermo axis == bars union axis (both in window)
    bars_axis = np.sort(panel["date"].unique())
    thermo_axis = th["date"].values
    if len(bars_axis) != len(thermo_axis) or not (bars_axis == thermo_axis).all():
        _void(f"date-axis identity broken: bars union {len(bars_axis)} vs "
              f"thermo {len(thermo_axis)} (first mismatch "
              f"{next((str(pd.Timestamp(a).date()) for a, b in zip(bars_axis, thermo_axis) if a != b), 'n/a')})")

    g = panel.groupby("date")["r"]
    r_u_df = g.mean()
    n_valid_df = g.size()
    r_u = r_u_df.reindex(pd.DatetimeIndex(thermo_axis)).values
    n_valid = n_valid_df.reindex(pd.DatetimeIndex(thermo_axis)).values
    if not np.isfinite(r_u).all():
        _void("EW return face has NaN days (valid-row count zero on some day)")
    audit = {
        "face1": {"rows": len(th), "cols": len(th.columns),
                  "first": str(th["date"].iloc[0].date()),
                  "last": str(th["date"].iloc[-1].date())},
        "face2": {"files": len(files), "rows_raw": rows_raw, "rows_window": rows_win,
                  "rows_valid": rows_valid, "sample": sample_info,
                  "min_valid_rows_per_day": int(n_valid.min()),
                  "valid_guard": "preclose notna AND preclose >= 1.0 (penny rows out)"},
        "mask_probe": mask_probe,
        "axis_identity": "thermo_daily date axis == bars panel union axis (bit-equal)",
    }
    return pd.DatetimeIndex(thermo_axis), r_u, masks, audit


# ------------------------------------------------------------------ engine

def overlay_stream(r_u, off, cost_side):
    """Frozen sec.3 execution: pos(0)=1 (t0 fully invested, no entry cost);
    pos(t+1) = 0 if off(t) else 1 (T+1 lag, no future data);
    r_ov(t) = pos(t)*r_u(t) - cost_side*1[pos(t)!=pos(t-1)] for t>=1."""
    T = len(r_u)
    pos = np.ones(T)
    pos[1:] = np.where(np.asarray(off, dtype=bool)[:-1], 0.0, 1.0)
    cost = np.zeros(T)
    cost[1:] = cost_side * (pos[1:] != pos[:-1])
    return pos * r_u - cost


def count_segments(off):
    m = np.asarray(off, dtype=bool)
    return int(np.sum(m[1:] & ~m[:-1])) + (1 if m[0] else 0)


def _sharpe(vals):
    a = np.asarray(vals, dtype=float)
    if len(a) < 2 or a.std(ddof=1) == 0 or not np.all(np.isfinite(a)):
        return None
    return float(a.mean() / a.std(ddof=1) * math.sqrt(PPY))


def stats_block(vals):
    a = np.asarray(vals, dtype=float)
    sr = _sharpe(a)
    cum = np.cumsum(a)
    dd = float(np.min(cum - np.maximum.accumulate(cum))) if len(cum) else None
    return {"n": int(len(a)),
            "sharpe": None if sr is None else round(sr, 4),
            "ann_ret": round(float(a.mean() * PPY), 6) if len(a) else None,
            "sum": round(float(a.sum()), 6) if len(a) else None,
            "maxdd": None if dd is None else round(dd, 6)}


def null_shifts(T):
    """Frozen sec.3 null law: s_i ~ Uniform{1..T-1}, rng(94500+i), i<200.
    Structure-preserving phase randomization (marginal + segment-length
    distribution + autocorrelation all preserved; only phase re-randomized
    = the correct null for 'does the thermo timing carry information')."""
    return [int(np.random.default_rng(NULL_BASE + i).integers(1, T))
            for i in range(N_NULLS)]


def monthly_virtual_starts(dates):
    """Frozen sec.4: first trading day of each month 1997-01..2026-06
    (~354 starts). Returns integer start indices into the axis."""
    starts = []
    y, m = 1997, 1
    while (y, m) <= (2026, 6):
        ts = pd.Timestamp(year=y, month=m, day=1)
        loc = dates.searchsorted(ts)
        if loc < len(dates):
            starts.append(int(loc))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return starts


def rolling_worst_sharpe(a, win_days):
    """Worst annualized Sharpe over all rolling windows of win_days length
    (prefix-sum vectorization; ddof=1)."""
    a = np.asarray(a, dtype=float)
    n = len(a) - win_days
    if n < 1:
        return None
    s1 = np.concatenate(([0.0], np.cumsum(a)))
    s2 = np.concatenate(([0.0], np.cumsum(a * a)))
    seg1 = s1[win_days:] - s1[:-win_days]
    seg2 = s2[win_days:] - s2[:-win_days]
    mean = seg1 / win_days
    var_pop = seg2 / win_days - mean * mean
    var_pop = np.maximum(var_pop, 0.0)
    var_ddof1 = var_pop * win_days / (win_days - 1)
    sd = np.sqrt(var_ddof1)
    ok = sd > 0
    if not ok.any():
        return None
    sr = np.where(ok, mean / np.where(ok, sd, 1.0) * math.sqrt(PPY), np.inf)
    return round(float(sr[ok].min()), 4)


def d6_block(cell_series, reject_line=D6_REJECT):
    """Per-cell member face vs REG6 registered traders (ew6 canon) +
    same-batch cross-cell disclosure. Machinery reused verbatim from
    cn_rev_tilt_p1 (load_member_rets/_corr)."""
    from cn_rev_tilt_p1 import REG6, load_member_rets, _corr
    member_rets, _cuts = load_member_rets()
    names = list(cell_series)
    out = {"reject_line": reject_line, "members": list(REG6), "cells": {},
           "same_batch_cross": {}}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            v, ov = _corr(cell_series[names[i]], cell_series[names[j]])
            out["same_batch_cross"][f"{names[i]}|{names[j]}"] = \
                {"corr": v, "overlap_days": ov}
    for name, s in cell_series.items():
        per, fin = {}, {}
        for tid, mr in member_rets.items():
            v, ov = _corr(s, mr)
            per[tid] = {"corr": v, "overlap_days": ov}
            if v is not None:
                fin[tid] = v
        amax = max(fin, key=lambda k: abs(fin[k])) if fin else None
        out["cells"][name] = {
            "per_member": per,
            "max_abs_corr": round(abs(fin[amax]), 4) if amax else None,
            "argmax_member": amax,
            "reject": bool(amax is not None and abs(fin[amax]) >= reject_line),
        }
    return out


def _attr_row(kind, delta, total, gates, entries):
    d = json.load(open(ATT_JSON, encoding="utf-8"))
    row = {"batch": BATCH, "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
           "kind": kind, "cells_ledger_delta": delta,
           "ledger_total_after": total, "gates": gates, "entries": entries}
    own = [i for i, e in enumerate(d["entries"])
           if e.get("batch") == BATCH and e.get("kind") == kind]
    if own:
        d["entries"][own[-1]] = row
    else:
        d["entries"].append(row)
    with open(ATT_JSON, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    return row


def _pre_burn_checks():
    """Seed-registry + closed-family receipts (frozen sec.3/sec.6)."""
    got = SG.SEED_REGISTRY.get("thermo_overlay_p1_nulls")
    if got != NULL_BASE:
        _void(f"seed base thermo_overlay_p1_nulls not registered in "
              f"science_gates.SEED_REGISTRY (got {got}, want {NULL_BASE})")
    cfam = SG.closed_family_check("thermo_overlay_p1")
    if cfam.get("status") == "rejected":
        _void(f"closed-family gate: thermo_overlay_p1 is closed ({cfam})")
    return cfam


def _exit_axis_assert():
    """Frozen sec.3 exit-axis declaration (2) hold-through: the overlay mask
    is the ONLY exit mechanism. Hard code-level assertion: this module defines
    no stop-loss/timeout/trailing engine exit, and the engine exit stack is
    never imported (engine/exit_rules.py absent from sys.modules)."""
    loaded = [m for m in sys.modules if m.startswith("engine") or "exit_rules" in m]
    if loaded:
        _void(f"exit-axis violation: engine exit stack loaded ({loaded}) -- "
              f"hold-through declaration forbids any default exit stack")
    return {"declaration": "2-hold-through",
            "engine_exit_stack_loaded": False,
            "note": "overlay mask = sole risk exit; no stop/timeout/trailing "
                    "anywhere in this module; engine never imported"}


# ------------------------------------------------------------------ probe

def cmd_probe(_):
    lane_guard()
    t0 = time.time()
    cfam = _pre_burn_checks()
    dates, r_u, masks, audit = load_faces()
    passive = stats_block(r_u)
    est = {"panel_rows": audit["face2"]["rows_window"],
           "burn_estimate_min": "10-25 (5,222 parquet read + 6 cell replays + "
                                "1,200 null replays, pure vectorized numpy)",
           "ram_peak_est_gb": round(audit["face2"]["rows_window"] * 8 * 3 / 1e9, 2)}
    rc = {"batch": BATCH, "probe": "GREEN_PROBE_READY",
          "lane": "bm-a (Money02 bars panel hosted)",
          "closed_family": cfam, "seed_registry": {"thermo_overlay_p1_nulls": NULL_BASE},
          "face_audit": audit, "passive_face": passive,
          "estimate": est,
          "runtime_sec": round(time.time() - t0, 2),
          "generated_by": "bm-a r939 scripts/thermo_overlay_p1.py probe"}
    with open(PROBE_RC, "w", encoding="utf-8") as fh:
        json.dump(rc, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"probe": rc["probe"], "passive_sr": passive["sharpe"],
                      "mask_cells": {k: (v["off_days"], v["segments"])
                                     for k, v in audit["mask_probe"].items()},
                      "out": PROBE_RC}, ensure_ascii=False))
    return 0


# ------------------------------------------------------------------ run

def _cell_compute(name, r_u, off, years, shifts, passive_sr, passive_sum):
    """ProcessPool worker body for ONE judgment cell (r941 multicore retrofit
    per O-20260930-2355 law-1). Math identical to the frozen serial design:
    same overlay_stream/stats_block/_sharpe calls, same null law (shifts are
    precomputed in the parent from rng(94500+i); workers only consume them),
    same roundings. Parent reassembles in original mask-iteration order ->
    payload byte-identical to the serial burn. Returns plain types only
    (picklable across the wire)."""
    T = len(r_u)
    off = np.asarray(off, dtype=bool)
    segs = count_segments(off)
    x1 = overlay_stream(r_u, off, COST_SIDE_X1)
    x2 = overlay_stream(r_u, off, COST_SIDE_X2)
    year_labels = sorted(set(int(y) for y in years))
    yr_x1 = {int(y): round(float(x1[years == y].sum()), 6) for y in year_labels}
    yr_x2 = {int(y): round(float(x2[years == y].sum()), 6) for y in year_labels}
    sign_agree = sum(1 for y in year_labels
                     if (yr_x1[y] > 0) == (yr_x2[y] > 0))
    null_rows, null_stress, sh = [], {}, []
    for i, s in enumerate(shifts):
        nm = off[(np.arange(T) + s) % T]
        nv = overlay_stream(r_u, nm, COST_SIDE_X1)
        nsr = _sharpe(nv)
        null_rows.append((name, i, NULL_BASE + i, s, nsr))
        if nsr is not None:
            sh.append(nsr)
        if i < 3:  # x2 stress face on first three nulls (disclosure)
            nv2 = overlay_stream(r_u, nm, COST_SIDE_X2)
            null_stress[f"{name}|null{i}"] = {
                "shift": s, "x1": _sharpe(nv), "x2": _sharpe(nv2)}
    a = np.asarray(sh, dtype=float)
    null_cov = ({"n_values": int(len(a)), "mu": float(a.mean()),
                 "sigma": float(a.std(ddof=1))} if len(a) >= 30 else None)
    return {"segs": segs, "x1": x1.tolist(),
            "x1_stats": stats_block(x1), "x2_stats": stats_block(x2),
            "yearly_x1": yr_x1, "yearly_x2": yr_x2, "sign_agree": sign_agree,
            "passive_diff": {"x1_minus_passive_sum":
                             round(float(x1.sum() - passive_sum), 6),
                             "x1_sr_minus_passive_sr":
                             round(float((stats_block(x1)["sharpe"] or 0.0)
                                         - passive_sr), 4)},
            "sub_first_half": stats_block(x1[:T // 2]),
            "sub_second_half": stats_block(x1[T // 2:]),
            "null_rows": null_rows, "null_stress": null_stress,
            "null_cov_raw": null_cov, "n_null_valid": int(len(sh))}


def cmd_run(_):
    global _CLAIM_STARTED
    _CLAIM_STARTED = _now_iso()
    t0 = time.time()
    lane_guard()
    # idempotent fast path (cn_rev_tilt precedent; env override = re-finalize only)
    if os.environ.get("THERMO_OVERLAY_P1_REFINALIZE") != "1" and os.path.exists(OUT):
        try:
            j = json.load(open(OUT, encoding="utf-8"))
            if j.get("trials_ledger"):
                print("idempotent fast path: results/thermo_overlay_p1/"
                      "thermo_overlay_p1_results.json already finalized "
                      "(ledger block present); THERMO_OVERLAY_P1_REFINALIZE=1 "
                      "= only redo")
                _pool_claim("idempotent fast path no-op: " + OUT
                            + " already finalized (r942 claim-leg fix)")
                return 0
        except Exception:
            pass
    cfam = _pre_burn_checks()
    exit_axis = _exit_axis_assert()
    dates, r_u, masks, audit = load_faces()
    T = len(r_u)

    # passive face: pos==1 universe EW hold, zero cost (frozen sec.3)
    passive = stats_block(r_u)
    passive_sr = passive["sharpe"]
    if passive_sr is None:
        print("mechanism failure: passive face undefined")
        return 2

    # null shifts shared across cells (seed law rng(94500+i), one shift per i)
    shifts = null_shifts(T)

    cells, cell_series = {}, {}
    null_rows = []          # (cell, i, seed, shift, sharpe)
    null_cov = {}
    null_stress = {}
    half = T // 2
    years = dates.year.values
    year_labels = sorted(set(int(y) for y in years))

    # r941 multicore retrofit (O-20260930-2355 law-1): per-cell compute over
    # the house ProcessPool; frozen quantities (masks/costs/nulls/seeds/
    # gates/ledger) untouched; assembly below iterates masks in the SAME
    # order as the serial design -> identical payload and CSV faces.
    jobs = [(name, _cell_compute,
             (name, np.asarray(r_u, dtype=float), np.asarray(off, dtype=bool),
              years, shifts, passive_sr, float(np.asarray(r_u).sum())))
            for name, off in masks.items()]
    par = run_cells_parallel(jobs, workers=min(len(jobs), worker_cap()),
                             desc="thermo cells")
    workers_used = int(par.pop("__workers__", 1))

    for name, off in masks.items():
        res = par[name]
        f = FROZEN_MASK_FACTS[name]
        if res["segs"] != f["segments"]:
            _void(f"segment recount drift cell {name}: {res['segs']} != frozen {f['segments']}")
        if res["null_cov_raw"] is None:
            _void(f"null family too thin for cell {name}: {res['n_null_valid']} values")
        x1 = np.asarray(res["x1"], dtype=float)
        cell_series[name] = pd.Series(x1, index=dates)
        cells[name] = {
            "params": {"rule": f["rule"], "cost_side_x1": COST_SIDE_X1,
                       "cost_side_x2": COST_SIDE_X2},
            "mask": {"off_days": int(np.asarray(off, dtype=bool).sum()),
                     "segments": res["segs"],
                     "n_trades": 2 * res["segs"], "n_entries": res["segs"]},
            "x1": res["x1_stats"], "x2": res["x2_stats"],
            "passive_diff": res["passive_diff"],
            "yearly_x1": res["yearly_x1"], "yearly_x2": res["yearly_x2"],
            "yearly_sign_agreement": f"{res['sign_agree']}/{len(year_labels)}",
            "crash_year": bool(any(v <= CRASH_YEAR
                                   for v in res["yearly_x1"].values())),
            "sub_first_half": res["sub_first_half"],
            "sub_second_half": res["sub_second_half"],
        }
        null_rows.extend(res["null_rows"])
        null_stress.update(res["null_stress"])
        null_cov[name] = res["null_cov_raw"]

    # family PBO: same-family 6-cell grid, CSCV-8 (frozen sec.4)
    in_df = pd.DataFrame({nm: cell_series[nm].values for nm in cell_series},
                         index=dates)
    pbo = cscv_pbo(in_df, n_blocks=8)

    # fresh/redo face (r253 single-count law)
    fresh = True
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT, encoding="utf-8"))
            if old.get("trials_ledger", {}).get("batch") == BATCH:
                fresh = False
        except Exception:
            fresh = True
    batch_cells_arg = BATCH_CELLS if fresh else 0

    # per-cell gates (frozen sec.4)
    gate_rows = {}
    for name in masks:
        sr = cells[name]["x1"]["sharpe"]
        cov = null_cov[name]
        npool = {"coverage": cov,
                 "source": f"{BATCH} cell {name} batch-own circular-shift "
                           f"mask nulls (K={N_NULLS}, rng seeds "
                           f"{NULL_BASE}+i, i<{N_NULLS})"}
        g1 = SG.g1_prime_v2(sharpe_full=sr,
                            returns=np.asarray(cell_series[name].values,
                                               dtype=float),
                            batch_cells=batch_cells_arg,
                            n_trades=2 * FROZEN_MASK_FACTS[name]["segments"],
                            n_entries=FROZEN_MASK_FACTS[name]["segments"],
                            null_pool=npool, passive_override=passive_sr)
        tstat = SG.t_from_sharpe(sr, n_periods=T) if sr is not None else None
        m1 = SG.m1_t_value_gate(tstat) if tstat is not None else \
            {"gate": "m1_t_value", "pass": False, "missing_input": "sharpe"}
        dsr = SG.deflated_sharpe_ratio(
            pd.Series(cell_series[name].values),
            n_trials=g1["skill_line"]["n_eff"])
        g2 = SG.g2_registration_v2(g1["pass_v2"], dsr, pbo["pbo"])
        gate_rows[name] = {"g1_prime_v2": g1, "m1": m1, "dsr": dsr, "g2": g2}

    # D6 member correlation face (reject line 0.70, cn_rev_tilt machinery)
    d6 = d6_block(cell_series, D6_REJECT)
    for name in gate_rows:
        gate_rows[name]["d6"] = d6["cells"][name]

    # virtual-start + rolling-worst descriptive faces (frozen sec.4)
    starts = monthly_virtual_starts(dates)
    if len(starts) != 354:
        _void(f"monthly virtual-start grid {len(starts)} != 354 (1997-01..2026-06)")
    vstarts = {"n_starts": len(starts), "start_first": str(dates[starts[0]].date()),
               "start_last": str(dates[starts[-1]].date()), "cells": {}}
    for name in masks:
        a = cell_series[name].values
        srs = [_sharpe(a[st:]) for st in starts]
        srs = [x for x in srs if x is not None]
        vstarts["cells"][name] = {
            "best": round(max(srs), 4), "worst": round(min(srs), 4),
            "p25": round(float(np.percentile(srs, 25)), 4),
            "median": round(float(np.median(srs)), 4),
            "p75": round(float(np.percentile(srs, 75)), 4),
            "rolling_worst_3y": rolling_worst_sharpe(a, 756),
            "rolling_worst_5y": rolling_worst_sharpe(a, 1260),
            "rolling_worst_10y": rolling_worst_sharpe(a, 2520),
        }

    # descriptive clauses (frozen sec.4, batch-level disclosure, NOT the gate)
    descriptive = {}
    for name in masks:
        c = cells[name]
        descriptive[name] = {
            "full_ann_positive": bool((c["x1"]["ann_ret"] or 0.0) > 0),
            "sub_faces_both_positive": bool(
                (c["sub_first_half"]["ann_ret"] or 0.0) > 0
                and (c["sub_second_half"]["ann_ret"] or 0.0) > 0),
            "sub_face_note": "two chronological halves = IS sub-faces; the "
                             "2025-01-01+ window is burned IS2 per "
                             "BACKTEST_SCIENCE s5 ruling -- no OOS claim made",
            "maxdd_ok": bool((c["x1"]["maxdd"] or 0.0) >= MAXDD_LINE),
            "no_crash_year": bool(not c["crash_year"]),
            "x2_yearly_sign_agreement": c["yearly_sign_agreement"],
        }

    def _cell_pass(name):
        g = gate_rows[name]
        return bool(g["g1_prime_v2"]["pass_v2"] and g["m1"].get("pass")
                    and g["g2"].get("eligible_v2") and not g["d6"]["reject"])

    passing = [nm for nm in gate_rows if _cell_pass(nm)]
    verdict = {
        "batch": BATCH,
        "any_cell_full_chain_pass": bool(passing),
        "passing_cells": passing,
        "g1_pass_cells": [nm for nm in gate_rows
                          if gate_rows[nm]["g1_prime_v2"]["pass_v2"]],
        "best_cell_by_sharpe": max(
            masks, key=lambda nm: cells[nm]["x1"]["sharpe"] or -9),
        "notes": "full chain = g1_prime_v2 pass_v2 (batch-own circular-shift "
                 "null_pool + passive_override + F6 dual trade gate) AND M1 "
                 "t>=3.0 AND g2_registration_v2 eligible_v2 AND D6 "
                 "no-reject; mechanism-judgment batch, multi-cell negative "
                 "is an honest expected outcome per frozen sec.5",
    }

    # trials ledger (single-count law; dict schema embedded in payload)
    if fresh:
        led = SG.append_ledger(batch_name=BATCH, batch_trials=BATCH_CELLS,
                               file_name="results/thermo_overlay_p1/"
                                         "thermo_overlay_p1_results.json",
                               evidence_cutoff=CUTOFF)
    else:
        led = json.load(open(OUT, encoding="utf-8"))["trials_ledger"]

    gates_summary = {
        "g1_pass_cells": verdict["g1_pass_cells"],
        "g2_eligible_cells": [nm for nm in gate_rows
                               if gate_rows[nm]["g2"].get("eligible_v2")],
        "m1_pass_cells": [nm for nm in gate_rows
                          if gate_rows[nm]["m1"].get("pass")],
        "d6_reject_cells": [nm for nm in gate_rows
                            if gate_rows[nm]["d6"]["reject"]],
        "full_chain_cells": passing}
    _attr_row("judgment", BATCH_CELLS if fresh else 0, led["total"],
              gates_summary,
              [f"{nm}: x1 SR {cells[nm]['x1']['sharpe']}" for nm in cells])

    payload = {
        **SG.cutoff_meta(CUTOFF),
        "schema": "thermo_overlay_p1_results_v1",
        "batch": BATCH,
        "ticket": "T-2026-10-10-181-P1 slice-2 (O-20261009-2340 sec.2.4 @bm-a)",
        "machine": "bm-a", "round": "r939",
        "frozen_refs": {
            "prereg": "research/THERMO-OVERLAY-P1.md (FROZEN 5c332d987 "
                      "precedes run; sec.7/8 backfill only)",
            "banned_gate": "BAN-05 new_mechanism+new_data exception ADMITTED "
                           "rc0 at freeze commit (r938 receipt)",
            "seed_registry": f"thermo_overlay_p1_nulls={NULL_BASE} (one-step "
                             f"R250, same-commit registration)",
            "cost": f"x1 {COST_SIDE_X1}/side x2 {COST_SIDE_X2}/side "
                    f"(V1 legacy stress calibre, 26/52 bp round-trip)",
        },
        "face_audit": audit,
        "exit_axis": exit_axis,
        "closed_family": cfam,
        "passive_face": {"construction": "universe EW hold pos==1, zero cost "
                                         "(frozen sec.3 passive baseline)",
                         "stats": passive},
        "null_face": {"construction": "K=200 circular random-shift mask nulls "
                                      "per cell, s_i~U{1..T-1}, rng(94500+i) "
                                      "i<200; shifts shared across cells "
                                      "(one shift per seed; structure-preserving "
                                      "phase randomization)",
                      "per_cell_coverage": {k: {"n_values": v["n_values"],
                                               "mu": round(v["mu"], 6),
                                               "sigma": round(v["sigma"], 6)}
                                           for k, v in null_cov.items()},
                      "null_stress_x2_sample": null_stress,
                      "n_nulls_per_cell": N_NULLS},
        "cells": cells,
        "gates": gate_rows,
        "pbo": pbo,
        "d6": d6,
        "virtual_starts": vstarts,
        "descriptive": descriptive,
        "verdict": verdict,
        "trials_ledger": led,
        "audit": {"runtime_sec": round(time.time() - t0, 2),
                  "python": sys.version.split()[0],
                  "numpy": np.__version__, "pandas": pd.__version__,
                  "determinism": "nulls seeded rng(94500+i) i<200; no other "
                                 "RNG; no wall-clock in content fields",
                  "engine_used": False,
                  "fresh_ledger_append": fresh,
                  "workers": workers_used,
                  "parallel": "house parallel_runner ProcessPool over 6 "
                              "judgment cells (r941 retrofit, "
                              "O-20260930-2355 law-1; per-cell math identical "
                              "to frozen serial design)",
                  "generated_by": "bm-a r939 scripts/thermo_overlay_p1.py "
                                  "(r941 multicore retrofit; science faces "
                                  "frozen-identical)"},
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    # per-cell CSV faces + null detail (frozen sec.6 products)
    for name, off in masks.items():
        x1 = overlay_stream(r_u, off, COST_SIDE_X1)
        pos = np.ones(T)
        pos[1:] = np.where(np.asarray(off, dtype=bool)[:-1], 0.0, 1.0)
        cdf = pd.DataFrame({"date": dates.astype(str), "r_u": r_u,
                            "off": np.asarray(off, dtype=int), "pos": pos,
                            "r_ov_x1": x1})
        cdf.to_csv(os.path.join(OUT_DIR, f"cells_{name}.csv"), index=False)
    nd = pd.DataFrame(null_rows, columns=["cell", "null_idx", "seed", "shift",
                                          "sharpe_x1"])
    nd.to_csv(NULLS_CSV, index=False)

    _pool_claim(OUT + " (verdict any_cell_full_chain_pass="
                + str(verdict["any_cell_full_chain_pass"])
                + "; trials_ledger total " + str(led["total"]) + ")")

    print(json.dumps({"out": OUT, "verdict": verdict,
                      "ledger_total": led["total"], "passive_sr": passive_sr,
                      "null_mu_sigma": {k: (round(v["mu"], 4),
                                            round(v["sigma"], 4))
                                        for k, v in null_cov.items()},
                      "runtime_sec": payload["audit"]["runtime_sec"]},
                     ensure_ascii=False, indent=1))
    return 0


# ------------------------------------------------------------------ selftest

def _selftest(_=None):
    ok_all = True
    legs = []

    def leg(name, ok, detail=""):
        nonlocal ok_all
        ok_all &= bool(ok)
        legs.append({"leg": name, "ok": bool(ok), "detail": str(detail)[:140]})

    # L1: overlay execution convention on a synthetic 8-day fixture
    # off on day 2 only -> pos [1,1,1,0,1,1,1,1]; sell cost day 3, buy cost day 4
    r_u = np.array([0.01, 0.02, -0.01, 0.03, -0.02, 0.01, 0.005, -0.005])
    off = np.array([False, False, True, False, False, False, False, False])
    c = 0.0013
    x = overlay_stream(r_u, off, c)
    exp = np.array([0.01, 0.02, -0.01, -c, -0.02 - c, 0.01, 0.005, -0.005])
    exp_pos = np.array([1, 1, 1, 0, 1, 1, 1, 1], dtype=float)
    leg("overlay_t_plus_1_lag", np.allclose(x, exp),
        f"got {np.round(x, 6).tolist()}")
    leg("overlay_pos_seq", np.allclose(
        np.concatenate(([1.0], np.where(off[:-1], 0.0, 1.0))), exp_pos))
    leg("overlay_t0_no_entry_cost", x[0] == r_u[0])
    # day3: pos=0 -> day-3 return NOT earned, sell cost charged;
    # day4: pos=1 -> day-4 return earned minus re-entry buy cost
    leg("overlay_exit_costs_two_sides",
        abs(x[3] - (0.0 - c)) < 1e-12 and abs(x[4] - (r_u[4] - c)) < 1e-12,
        f"x3={x[3]} x4={x[4]}")

    # L2: circular shift preserves structure (marginal + segment counts)
    m = np.zeros(30, dtype=bool)
    m[3:6] = True
    m[20:23] = True
    s = 11
    nm = m[(np.arange(30) + s) % 30]

    def _segs(a):
        a = np.asarray(a, dtype=bool)
        return int(np.sum(a[1:] & ~a[:-1])) + (1 if a[0] else 0)

    leg("circshift_marginal", nm.sum() == m.sum())
    leg("circshift_segments", _segs(nm) == _segs(m), f"{_segs(nm)} vs {_segs(m)}")
    leg("circshift_phase_differs", not np.array_equal(nm, m))

    # L3: seed determinism + band + non-crawl
    sh1 = null_shifts(7216)
    sh2 = null_shifts(7216)
    leg("null_shifts_deterministic", sh1 == sh2)
    leg("null_shifts_in_range", all(1 <= s <= 7215 for s in sh1))
    leg("seed_band_94xxx", 94001 <= NULL_BASE <= 94999,
        f"base {NULL_BASE} in 94_001..94_999 pocket; 95_000+ never touched")

    # L4: segment counting edges
    leg("seg_all_off", count_segments(np.ones(5, dtype=bool)) == 1)
    leg("seg_first_day", count_segments(
        np.array([True, False, False])) == 1)
    leg("seg_last_day", count_segments(
        np.array([False, False, True])) == 1)
    leg("seg_none", count_segments(np.zeros(5, dtype=bool)) == 0)

    # L5: skill_line_v2 plumbing with synthetic null_pool + passive_override
    line = SG.skill_line_v2(batch_cells=6,
                            null_pool={"coverage": {"mu": 0.1, "sigma": 0.2,
                                                    "n_values": 200}},
                            passive_override=0.35)
    leg("skill_line_plumbing", line["passive_source"] == "batch_own_per_cell"
        and abs(line["passive_term"] - 0.45) < 1e-9,
        f"line={line['line']}")

    # L6: stats helpers on a known fixture
    st = stats_block(np.full(252, 0.01))  # degenerate zero-var -> sharpe None
    leg("sharpe_degenerate_none", st["sharpe"] is None)
    st2 = stats_block(np.array([0.01, -0.01] * 126))
    leg("maxdd_known", abs(st2["maxdd"] - (-0.01)) < 1e-9, f"dd={st2['maxdd']}")

    # L7: monthly virtual-start grid on a synthetic business-day axis
    # (real-axis count gate lives in run(); here: shape + boundary months;
    #  bdate axis must SPAN past 2026-06 for the full 354-month grid)
    dates = pd.bdate_range("1996-12-16", "2026-09-22")
    starts = monthly_virtual_starts(dates)
    leg("vstarts_354", len(starts) == 354,
        f"n={len(starts)} first={dates[starts[0]].date()} "
        f"last={dates[starts[-1]].date()}")
    leg("vstarts_bounds", (dates[starts[0]].year, dates[starts[0]].month)
        == (1997, 1) and (dates[starts[-1]].year, dates[starts[-1]].month)
        == (2026, 6))

    # L8: rolling worst vectorization vs direct loop (small fixture)
    a = np.random.default_rng(7).normal(0.0005, 0.01, 600)
    rw = rolling_worst_sharpe(a, 250)
    direct = []
    for i in range(len(a) - 250 + 1):
        w = a[i:i + 250]
        direct.append(w.mean() / w.std(ddof=1) * math.sqrt(PPY))
    leg("rolling_worst_matches_loop", rw == round(min(direct), 4),
        f"vec={rw} loop={round(min(direct), 4)}")

    # L9: exit-axis declaration holds in this module
    ea = _exit_axis_assert()
    leg("exit_axis_hold_through", ea["declaration"] == "2-hold-through"
        and ea["engine_exit_stack_loaded"] is False)

    rc = {"selftest": "PASS" if ok_all else "FAIL", "legs": legs,
          "batch": BATCH, "generated_by": "bm-a r939"}
    with open(SELFTEST_RC, "w", encoding="utf-8") as fh:
        json.dump(rc, fh, ensure_ascii=False, indent=1)
    print(json.dumps(rc, ensure_ascii=False, indent=1))
    return 0 if ok_all else 2


# ------------------------------------------------------------------ cli

def main(argv=None):
    ap = argparse.ArgumentParser(description=BATCH)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run")
    sub.add_parser("probe")
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    return {"run": cmd_run, "probe": cmd_probe,
            "selftest": _selftest}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
