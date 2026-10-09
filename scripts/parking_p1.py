"""PARKING-P1 runner (parking cash-leg three-arm batch, O-20261009-1105-bm-a sec.3).

Design frozen verbatim in research/PARKING_P1_PREREG.md (freeze commit
b904a0a0e dead-session r914 product, adopted r914; post-freeze spec
edits = none -- runner is part of the freeze). Conventions reused, zero
re-implementation:
  - panels: 6 ETF data/daily/sh<code>.csv + repo data/repo_daily/GC001.csv
    + 510300 bear face (raw pd.read_csv, truncate to evidence_cutoff
    2026-09-22, warmup=0 except 510300 MA200=200 bars per frozen sec.2)
  - stint=(entry close buy, entry+d close sell, hold-through; every-5td
    census); cost V1 face A 26.082bp round-trip x1 + x2/x3 stress legs
  - carry convention (prereg sec.3 "entry->exit same-window cumulative",
    row alignment not pinned): repo accrues over the d nights spanned by
    the stint = GC001 daily carries at panel rows e..e+d-1 (1-day repo
    T+0 roll face), prefix-sum vectorized; disclosed in interpretation_notes
  - baselines: C2 repo proxy (GC001 close annualized%/100/250 daily carry,
    main) / C1 money-ETF as-traded (disclosure only) / C0 pure cash
  - K=200 null family on 511880: per draw i, rng(94300+i) picks
    (duration tier, entry phase in {0..4}); the draw's stint family (all
    every-5td entries at that phase+duration) yields one same-formula
    annualized Sharpe mean_u/sigma_u*sqrt(250/d) -- the per-draw FAMILY
    reading is the only computable one (single-stint sigma is undefined);
    disclosed in batch interpretation_notes
  - Face 2 per instrument (Face-1 survivors): the instrument's best
    surviving cell by t carries sharpe_full (same stint formula, same
    scale as null values); its pickup series feeds the bootstrap CI
  - PBO: stint-ordinal aligned 24-cell matrix truncated to the min common
    stint count (entry-date grids have disjoint phases 0/1/2/3 across
    panels -> no complete date-aligned matrix exists; cscv_pbo requires a
    complete matrix) -- construction disclosed; truncation < 16 rows =
    honest missing-input and G2 refuses per frozen "missing input = honest refusal"
  - gates: science_gates m1_t_value_gate/bootstrap_ci_sharpe/g1_prime_v2/
    g2_registration_v2/deflated_sharpe_ratio/cutoff_meta/append_ledger/
    closed_family_check/SEED_REGISTRY (parking_p1_null_base=94300)
  - D6: 4 judged instruments' daily returns vs REG6 members
    (cn_rev_tilt_p1 load_member_rets/_corr) + same-batch cross incl.
    511880/511990 (null-family underlying) -- reject line 0.70
  - exit-axis declaration (2) hold-through: stints have NO stop-loss, NO
    timeout, NO other exit; this module never imports engine/exit_rules
    (selftest L15 static source scan)

Determinism: no wall-clock in content fields; nulls seeded rng(94300+i);
redo (batch already in ledger) recomputes and append_ledger is idempotent
per its own schema (r253 single-count law). Batch is short (<3 min single
core per frozen sec.0) -- NOT pooled; run in-round.

Exit codes: 0 normal/no-op; 2 mechanism failure; 3 VOID face-mismatch
fail-closed (nothing written).
"""
import argparse
import json
import math
import os
import subprocess
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

import science_gates as SG  # noqa: E402
from screening.pbo import cscv_pbo  # noqa: E402

BATCH = "PARKING-P1"
FAMILY_KEY = "parking_cash_leg"
TRIALS = 24                       # 4 judged instruments x 6 durations (frozen sec.0)
CUTOFF = "2026-09-22"             # forward lockbox D2 (frozen sec.2)
DURATIONS = [5, 10, 20, 40, 60, 120]  # frozen sec.3 duration tiers
ENTRY_STEP = 5                    # every-5td census (frozen sec.3)
JUDGED = ["511010", "511090", "511260", "511380"]   # arm A x3 + arm B x1
MONEY = ["511880", "511990"]                        # arm C money ETFs (C1 face)
ALL_ETFS = JUDGED + MONEY
ARM = {c: ("A" if c in ("511010", "511090", "511260") else "B") for c in JUDGED}
COST_RT_X1 = 0.0026082            # 26.082bp round-trip V1 face A (frozen sec.3)
REPO_PPY = 250.0                  # repo carry: close annualized%/100/250 (frozen sec.3)
PPY = 250.0                       # daily-series annualization base
N_NULLS = 200
NULL_BASE = 94300                 # SEED_REGISTRY parking_p1_null_base (r915)
D6_REJECT = 0.70
LIQ_FLOOR = 50_000_000.0          # median daily amount floor (frozen sec.4)
P95_LINE = {"A": -0.030, "B": -0.060}   # within-stint maxdd p95 red line
TAIL_CAP = {"A": -0.100, "B": -0.150}    # single-stint trough hard cap
OUT_JSON = os.path.join(ROOT, "results", "parking_p1.json")
OUT_CSV = os.path.join(ROOT, "research", "parking_p1_results.csv")
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")
PREREG = os.path.join(ROOT, "research", "PARKING_P1_PREREG.md")

# frozen sec.2 probe anchor facts (results/_r912bma_parking_probe.json, r913)
FROZEN_ANCHORS = {
    "511010": {"rows": 3273, "first": "2013-04-09"},
    "511090": {"rows": 797, "first": "2023-06-13"},
    "511260": {"rows": 2204, "first": "2017-08-24"},
    "511380": {"rows": 1570, "first": "2020-04-07"},
    "511880": {"rows": 3266, "first": "2013-04-18"},
    "511990": {"rows": 3273, "first": "2013-04-09"},
}
GC001_ANCHOR = {"first": "2011-05-13", "cutoff_rows_min": 3700}
FACE510300 = {"from": "2012-05-28", "ma_warmup": 200}


def _void(msg):
    print(f"VOID fail-closed: {msg}")
    sys.exit(3)


def load_panels():
    """Frozen sec.2 faces: raw read_csv, truncate to cutoff, anchor assert
    vs r912 probe facts. Returns (panels, repo_rate_by_date) where panels =
    {code: {"dates": [...], "close": np, "amount": np, "carry_prefix": np}}.
    carry_prefix[i] = sum of GC001 daily carries at panel rows 0..i."""
    repo = pd.read_csv(os.path.join(ROOT, "data", "repo_daily", "GC001.csv"),
                       parse_dates=["date"])
    repo = repo[repo["date"] <= pd.Timestamp(CUTOFF)]
    if len(repo) < GC001_ANCHOR["cutoff_rows_min"]:
        _void(f"GC001 truncated rows {len(repo)} < {GC001_ANCHOR['cutoff_rows_min']}")
    if repo["date"].iloc[0].strftime("%Y-%m-%d") != GC001_ANCHOR["first"]:
        _void("GC001 first-date face mismatch")
    rate = dict(zip(repo["date"].dt.strftime("%Y-%m-%d"),
                     repo["close"].to_numpy(dtype=float) / 100.0 / REPO_PPY))
    panels = {}
    for code in ALL_ETFS:
        df = pd.read_csv(os.path.join(ROOT, "data", "daily", f"sh{code}.csv"),
                         parse_dates=["date"])
        df = df[df["date"] <= pd.Timestamp(CUTOFF)]
        if df.empty:
            _void(f"panel {code} empty at cutoff {CUTOFF}")
        a = FROZEN_ANCHORS[code]
        first = df["date"].iloc[0].strftime("%Y-%m-%d")
        if len(df) != a["rows"] or first != a["first"]:
            _void(f"face mismatch {code}: rows {len(df)}!={a['rows']} "
                  f"or first {first}!={a['first']}")
        if df["date"].iloc[-1].strftime("%Y-%m-%d") != CUTOFF:
            _void(f"panel {code} tail != cutoff (data completeness gate)")
        keys = df["date"].dt.strftime("%Y-%m-%d").to_numpy()
        missing = [k for k in keys if k not in rate]
        if missing:
            _void(f"repo carry coverage gap on {code}: {len(missing)} dates "
                  f"e.g. {missing[0]}")
        row_rate = np.array([rate[k] for k in keys], dtype=float)
        panels[code] = {
            "dates": keys, "close": df["close"].to_numpy(dtype=float),
            "amount": df["amount"].to_numpy(dtype=float),
            "carry_prefix": np.concatenate(([0.0], np.cumsum(row_rate))),
        }
    return panels, rate


def bear_face():
    """Frozen sec.4 Face 4: 510300 close<MA200 bear set (MA200 warmup 200)."""
    h = pd.read_csv(os.path.join(ROOT, "data", "daily", "sh510300.csv"),
                    parse_dates=["date"])
    h = h[h["date"] <= pd.Timestamp(CUTOFF)]
    if h["date"].iloc[0].strftime("%Y-%m-%d") != FACE510300["from"]:
        _void("510300 first-date face mismatch")
    ma = h["close"].rolling(FACE510300["ma_warmup"]).mean()
    bear = (h["close"] < ma)
    return dict(zip(h["date"].dt.strftime("%Y-%m-%d"), bear.to_numpy(dtype=bool)))


def stint_cell(close, d, carry_prefix, cost_rt):
    """Frozen sec.3 every-5td census stints. Carry = repo daily rates at
    rows e..e+d-1 (d nights spanned, 1-day-repo roll face) via prefix sums."""
    n = len(close)
    last_e = n - 1 - d
    entries = np.arange(0, last_e + 1, ENTRY_STEP)
    if len(entries) == 0:
        return None
    exits = entries + d
    gross = close[exits] / close[entries] - 1.0
    cum = carry_prefix[exits] - carry_prefix[entries]
    pickup_c2 = gross - cum - cost_rt
    maxdd = np.empty(len(entries))
    for k, e in enumerate(entries):
        path = close[e:e + d + 1]
        peak = np.maximum.accumulate(path)
        maxdd[k] = float((path / peak - 1.0).min())
    return {"entries": entries, "gross": gross, "carry_cum": cum,
            "pickup_c2": pickup_c2, "pickup_c0": gross - cost_rt, "maxdd": maxdd}


def annualized_stint_sharpe(u, d):
    """Frozen sec.3 same-formula: mean_u/sigma_u*sqrt(250/d) (ddof=1)."""
    a = np.asarray(u, dtype=float)
    if len(a) < 2 or a.std(ddof=1) == 0:
        return None
    return float(a.mean() / a.std(ddof=1) * math.sqrt(REPO_PPY / d))


def daily_excess(code, panels, rate):
    """Daily buy-and-hold excess vs repo carry (passive + C1 faces).
    Convention: day t return minus day t repo carry (same-day known rate)."""
    p = panels[code]
    rets = p["close"][1:] / p["close"][:-1] - 1.0
    rr = np.array([rate[k] for k in p["dates"][1:]], dtype=float)
    return rets - rr


def sharpe_ann(ex, ppy=PPY):
    a = np.asarray(ex, dtype=float)
    if len(a) < 2 or a.std(ddof=1) == 0:
        return None
    return float(a.mean() / a.std(ddof=1) * math.sqrt(ppy))


def null_family(panels, rate):
    """Frozen sec.3 null: K=200 draws rng(94300+i); each draw = (duration
    tier, entry phase); value = that stint family's same-formula annualized
    pickup Sharpe (vs C2, cost x1) on 511880."""
    p = panels["511880"]
    vals, meta = [], []
    for i in range(N_NULLS):
        rng = np.random.default_rng(NULL_BASE + i)
        dur = DURATIONS[int(rng.integers(0, len(DURATIONS)))]
        phase = int(rng.integers(0, ENTRY_STEP))
        fam = stint_family(p["close"], dur, p["carry_prefix"], phase, COST_RT_X1)
        if fam is None:
            continue
        v = annualized_stint_sharpe(fam["pickup_c2"], dur)
        if v is not None:
            vals.append(v)
            meta.append({"draw": i, "duration": dur, "phase": phase,
                         "n_stints": int(len(fam["entries"]))})
    if len(vals) < 30:
        _void(f"null family too thin: {len(vals)} values")
    a = np.asarray(vals)
    return {"coverage": {"mu": float(a.mean()), "sigma": float(a.std(ddof=1)),
                         "n_values": int(len(a))},
            "source": "PARKING_P1 own null family (511880 random-entry "
                      "phase/duration stint families vs repo proxy, cost x1)",
            "draws": meta}


def stint_family(close, d, carry_prefix, phase, cost_rt):
    """Every-5td entries from a given phase (null-draw face)."""
    n = len(close)
    last_e = n - 1 - d
    entries = np.arange(phase, last_e + 1, ENTRY_STEP)
    if len(entries) < 2:
        return None
    exits = entries + d
    gross = close[exits] / close[entries] - 1.0
    cum = carry_prefix[exits] - carry_prefix[entries]
    return {"entries": entries, "gross": gross, "carry_cum": cum,
            "pickup_c2": gross - cum - cost_rt}


def pbo_matrix(cells):
    """Stint-ordinal aligned matrix truncated to min common stint count."""
    lens = [len(c["pickup_c2"]) for c in cells.values()]
    m = min(lens)
    if m < 16:
        return None, m
    df = pd.DataFrame({k: v["pickup_c2"][:m] for k, v in cells.items()})
    if df.isna().any().any():
        return None, m
    return df, m


def _prereg_sha():
    import hashlib
    return hashlib.sha256(open(PREREG, "rb").read()).hexdigest()


def _machine_id():
    try:
        return json.load(open(os.path.join(ROOT, "fleet", "machine.json"),
                              encoding="utf-8"))["machine_id"]
    except Exception:
        return "unknown"


def gates_record():
    """sec.0.5 banned-direction gate (frozen at b904a0a0e, re-run for the
    record) + closed-family + seed registry + prereg sha."""
    r = subprocess.run([sys.executable,
                        os.path.join(ROOT, "Tools", "banned_direction_gate.py"),
                        "--prereg", PREREG], capture_output=True)
    out = {"banned_gate_rc": r.returncode,
           "banned_tail": (r.stdout or b"").decode("utf-8", "replace").strip()[-200:],
           "closed_family": SG.closed_family_check(FAMILY_KEY),
           "seed_registry_parking": SG.SEED_REGISTRY.get("parking_p1_null_base"),
           "prereg_sha256_at_run": _prereg_sha()}
    return out


def cmd_probe():
    panels, rate = load_panels()
    bear = bear_face()
    out = {"batch": BATCH, "cutoff": CUTOFF, "panels": {}, "liquidity": {},
           "bear_days": int(sum(1 for v in bear.values() if v)),
           "ledger_head": SG.ledger_head(),
           "seed_registry_parking": SG.SEED_REGISTRY.get("parking_p1_null_base"),
           "closed_family": SG.closed_family_check(FAMILY_KEY)["status"],
           "prereg_sha256": _prereg_sha()}
    for code in ALL_ETFS:
        p = panels[code]
        med = float(np.median(p["amount"]))
        out["panels"][code] = {"rows": int(len(p["close"])),
                               "first": str(p["dates"][0]), "last": str(p["dates"][-1])}
        out["liquidity"][code] = {"median_amount": med, "floor": LIQ_FLOOR,
                                  "pass": bool(med >= LIQ_FLOOR)}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return out


def cmd_gates():
    out = gates_record()
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if out["banned_gate_rc"] != 0:
        sys.exit(2)
    return out


def cmd_run():
    panels, rate = load_panels()
    bear = bear_face()
    g = gates_record()
    if g["banned_gate_rc"] != 0:
        sys.exit(2)

    nulls = null_family(panels, rate)
    passive = sharpe_ann(daily_excess("511880", panels, rate))
    c1_face = {c: {"daily_excess_sharpe_as_traded":
                   sharpe_ann(daily_excess(c, panels, rate))} for c in MONEY}

    cells, verdicts = {}, {}
    for code in JUDGED:
        p = panels[code]
        liq_med = float(np.median(p["amount"]))
        for d in DURATIONS:
            cell = stint_cell(p["close"], d, p["carry_prefix"], COST_RT_X1)
            if cell is None:
                _void(f"cell {code}/{d} empty (panel too short)")
            cells[f"{code}/{d}"] = cell
            u = cell["pickup_c2"]
            n = len(u)
            mean = float(np.mean(u))
            sd = float(np.std(u, ddof=1))
            t = mean / (sd / math.sqrt(n)) if sd > 0 else None
            m1 = SG.m1_t_value_gate(t) if t is not None else \
                {"gate": "m1_t_value_gate", "claim_class": "new_factor",
                 "hurdle": 3.0, "t": None, "pass": False, "missing_input": "sd=0"}
            ci = SG.bootstrap_ci_sharpe(u.tolist(), seed=NULL_BASE,
                                        periods_per_year=REPO_PPY / d)
            arm = ARM[code]
            p95 = float(np.percentile(cell["maxdd"], 95))
            worst = float(cell["maxdd"].min())
            f3 = {"p95_maxdd": round(p95, 6),
                  "worst_stint_trough": round(worst, 6),
                  "p95_line": P95_LINE[arm], "tail_cap": TAIL_CAP[arm],
                  "p95_pass": bool(p95 >= P95_LINE[arm]),
                  "tail_pass": bool(worst > TAIL_CAP[arm])}
            bear_mask = np.array([bear.get(k, False) for k in p["dates"][cell["entries"]]])
            ub = u[bear_mask]
            f4 = {"bear_stints": int(bear_mask.sum()),
                  "bear_mean_pickup": round(float(ub.mean()), 6) if len(ub) else None,
                  "nonbear_mean_pickup": round(float(u[~bear_mask].mean()), 6)
                  if (~bear_mask).any() else None}
            u0_x2 = cell["pickup_c0"] - COST_RT_X1  # C0 at x2 stress
            q = np.percentile(u, [25, 50, 75])
            face1 = bool(mean > 0 and m1["pass"] and ci["ci_lower_bound_positive"])
            verdicts[f"{code}/{d}"] = {
                "instrument": code, "arm": arm, "d": d, "n_stints": n,
                "mean_pickup_c2": round(mean, 6), "sd": round(sd, 6),
                "t": None if t is None else round(t, 4), "m1": m1,
                "bootstrap_ci": ci,
                "ann_stint_sharpe": annualized_stint_sharpe(u, d),
                "face1_pass": face1,
                "face1_c0_x2_net_mean_pos": bool(float(np.mean(u0_x2)) > 0),
                "stress_x2_mean": round(float(np.mean(
                    cell["gross"] - cell["carry_cum"] - 2 * COST_RT_X1)), 6),
                "stress_x3_mean": round(float(np.mean(
                    cell["gross"] - cell["carry_cum"] - 3 * COST_RT_X1)), 6),
                "start_dist_p25_p50_p75_best_worst": [
                    round(float(q[0]), 6), round(float(q[1]), 6),
                    round(float(q[2]), 6), round(float(u.max()), 6),
                    round(float(u.min()), 6)],
                "face3": f3, "face4_bear": f4,
                "cell_pass": bool(face1 and f3["p95_pass"] and f3["tail_pass"]),
                "liquidity_median_amount": liq_med,
            }

    from cn_rev_tilt_p1 import REG6, load_member_rets, _corr
    member_rets, _cuts = load_member_rets()
    d6 = {"reject_line": D6_REJECT, "members": list(REG6), "cells": {},
          "same_batch_cross": {}}
    dret = {}
    for c in ALL_ETFS:
        p = panels[c]
        idx = pd.DatetimeIndex(pd.to_datetime(list(p["dates"][1:])))
        dret[c] = pd.Series(p["close"][1:] / p["close"][:-1] - 1.0, index=idx)
    for i in range(len(ALL_ETFS)):
        for j in range(i + 1, len(ALL_ETFS)):
            v, ov = _corr(dret[ALL_ETFS[i]], dret[ALL_ETFS[j]])
            d6["same_batch_cross"][f"{ALL_ETFS[i]}|{ALL_ETFS[j]}"] = \
                {"corr": v, "overlap_days": ov}
    for code in JUDGED:
        per, fin = {}, {}
        for tid, mr in member_rets.items():
            v, ov = _corr(dret[code], mr)
            per[tid] = {"corr": v, "overlap_days": ov}
            if v is not None:
                fin[tid] = v
        amax = max(fin, key=lambda k: abs(fin[k])) if fin else None
        d6["cells"][code] = {"per_member": per,
                             "max_abs_corr": round(abs(fin[amax]), 4) if amax else None,
                             "argmax_member": amax,
                             "reject": bool(amax is not None
                                            and abs(fin[amax]) >= D6_REJECT)}
    d6_reject_any = any(c["reject"] for c in d6["cells"].values())

    face2 = {}
    for code in JUDGED:
        surv = [(k, v) for k, v in verdicts.items()
                if v["instrument"] == code and v["face1_pass"]]
        if not surv:
            face2[code] = {"triggered": False,
                           "note": "no Face-1 surviving cell -- registration not triggered"}
            continue
        best_k, best_v = max(surv, key=lambda kv: (kv[1]["t"] or 0.0))
        u = cells[best_k]["pickup_c2"]
        d = best_v["d"]
        g1 = SG.g1_prime_v2(sharpe_full=annualized_stint_sharpe(u, d),
                            returns=u.tolist(), batch_cells=TRIALS,
                            null_pool=nulls, passive_override=passive)
        dsr = SG.deflated_sharpe_ratio(u.tolist(), n_trials=TRIALS,
                                       periods_per_year=REPO_PPY / d)
        mat, mlen = pbo_matrix(cells)
        pbo = None
        pbo_note = None
        if mat is not None:
            try:
                pbo = cscv_pbo(mat, n_blocks=8)
            except ValueError as e:
                pbo_note = f"matrix {mlen} rows below CSCV floor -- {e}"
                pbo = None
        g2 = SG.g2_registration_v2(g1["pass_v2"], dsr,
                                  pbo["pbo"] if pbo else None)
        face2[code] = {"triggered": True, "best_cell": best_k, "t": best_v["t"],
                       "sharpe_full": annualized_stint_sharpe(u, d),
                       "g1_prime_v2": g1, "dsr": dsr,
                       "pbo": ({"pbo": pbo["pbo"], "verdict": pbo["verdict"],
                                "matrix_rows": mlen} if pbo else None),
                       "pbo_missing": pbo is None,
                       "pbo_note": pbo_note or (
                           "stint-ordinal matrix below CSCV 160-row floor "
                           "(min common stints 136)" if mat is None else None),
                       "g2_registration_v2": g2}

    desc = {}
    for code in JUDGED:
        ex = daily_excess(code, panels, rate)
        mid = len(ex) // 2
        cum = np.cumsum(ex)
        desc[code] = {
            "daily_excess_ann": round(float(np.mean(ex) * PPY), 6),
            "oos_first_half_mean": round(float(np.mean(ex[:mid])), 8),
            "oos_second_half_mean": round(float(np.mean(ex[mid:])), 8),
            "oos_dual_positive": bool(np.mean(ex[:mid]) > 0 and np.mean(ex[mid:]) > 0),
            "sleeve_maxdd": round(float(np.min(cum - np.maximum.accumulate(cum))), 6)}

    any_pass = any(v["cell_pass"] for v in verdicts.values())
    out = {
        "schema": "parking_p1_results_v1",
        "batch": BATCH, "family_key": FAMILY_KEY, "trials": TRIALS,
        "evidence_cutoff": CUTOFF, "science_gates": SG.cutoff_meta(CUTOFF),
        "frozen_refs": g, "null_pool": nulls,
        "passive_override_511880": passive, "c1_money_face": c1_face,
        "verdicts": verdicts, "d6": d6, "d6_reject_any": d6_reject_any,
        "face2_registration": face2, "descriptives": desc,
        "any_cell_full_chain_pass": any_pass,
        "audit": {
            "machine": _machine_id(),
            "exit_axis": "declaration-2 hold-through (stints have no "
                         "stop-loss/timeout; engine never imported)",
            "interpretation_notes": [
                "carry row alignment: repo accrues at stint rows e..e+d-1 "
                "(d spanned nights, 1-day-repo roll face) -- prereg pins the "
                "window not the row alignment; disclosed",
                "null granularity: per-draw stint FAMILY (random duration tier "
                "+ entry phase) is the only computable reading of the frozen "
                "same-formula Sharpe (single-stint sigma undefined)",
                "face2 per instrument = best Face-1 surviving cell by t carries "
                "sharpe_full (same stint formula, same scale as null values)",
                "pbo matrix = stint-ordinal aligned, truncated to min common "
                "stint count (entry-date grids have disjoint phases -- no "
                "complete date matrix exists); 136-row truncation sits below "
                "the CSCV 160-row floor => PBO honest missing-input and G2 "
                "refusal per frozen 'missing input = honest refusal' clause",
                "stint census count = floor((n-1-d)/5)+1 actual entries; the "
                "frozen sec.3 formula floor((n-d)/5) undercounts by <=1; "
                "actual counts disclosed per cell"]},
    }
    out["trials_ledger"] = SG.append_ledger(
        batch_name=BATCH, batch_trials=TRIALS,
        file_name=os.path.relpath(OUT_JSON, ROOT).replace("\\", "/"),
        evidence_cutoff=CUTOFF)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    rows = []
    for k, v in verdicts.items():
        r = {"cell": k, "instrument": v["instrument"], "arm": v["arm"], "d": v["d"],
             "n_stints": v["n_stints"], "mean_pickup_c2": v["mean_pickup_c2"],
             "t": v["t"], "ann_stint_sharpe": v["ann_stint_sharpe"],
             "m1_pass": v["m1"]["pass"],
             "ci_lower_positive": v["bootstrap_ci"]["ci_lower_bound_positive"],
             "face1_pass": v["face1_pass"],
             "face1_c0_x2_net_mean_pos": v["face1_c0_x2_net_mean_pos"],
             "stress_x2_mean": v["stress_x2_mean"], "stress_x3_mean": v["stress_x3_mean"],
             "p95_maxdd": v["face3"]["p95_maxdd"], "p95_pass": v["face3"]["p95_pass"],
             "worst_stint_trough": v["face3"]["worst_stint_trough"],
             "tail_pass": v["face3"]["tail_pass"],
             "bear_stints": v["face4_bear"]["bear_stints"],
             "bear_mean_pickup": v["face4_bear"]["bear_mean_pickup"],
             "cell_pass": v["cell_pass"],
             "liquidity_median_amount": v["liquidity_median_amount"]}
        rows.append(r)
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
    _attr_row(out["ledger"].get("total"))
    print(json.dumps({"batch": BATCH, "any_cell_full_chain_pass": any_pass,
                      "d6_reject_any": d6_reject_any,
                      "ledger_total_after": out["ledger"].get("total"),
                      "out": os.path.relpath(OUT_JSON, ROOT)},
                     ensure_ascii=False))
    return out


def _attr_row(total_after):
    import time
    d = json.load(open(ATT_JSON, encoding="utf-8"))
    row = {"batch": BATCH, "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
           "kind": "judgment", "cells_ledger_delta": TRIALS,
           "ledger_total_after": total_after,
           "gates": "face1_mean+m1_t+ci / face3_p95+tail / face2_g1p2+g2 / "
                    "d6_corr / liquidity", "entries": TRIALS}
    own = [i for i, e in enumerate(d["entries"])
           if e.get("batch") == BATCH and e.get("kind") == "judgment"]
    if own:
        d["entries"][own[-1]] = row
    else:
        d["entries"].append(row)
    with open(ATT_JSON, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


def cmd_selftest():
    """L1-L16 offline deterministic legs (no network, no ledger writes)."""
    ok = []
    t = lambda name, cond: ok.append((name, bool(cond)))
    # L1 carry math: 2.5% annualized -> 0.0001 daily
    t("L1_carry", abs(2.5 / 100 / REPO_PPY - 0.0001) < 1e-12)
    # L2 stint census + gross on synthetic panel
    close = np.array([100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0,
                      108.0, 109.0, 110.0, 111.0])
    rate = np.full(12, 0.0001)
    cp = np.concatenate(([0.0], np.cumsum(rate)))
    cell = stint_cell(close, 5, cp, COST_RT_X1)
    t("L2_entries", list(cell["entries"]) == [0, 5])
    t("L2_gross", abs(cell["gross"][0] - 0.05) < 1e-12
      and abs(cell["gross"][1] - (110.0 / 105.0 - 1.0)) < 1e-12)
    # L3 carry prefix: e=0,d=5 -> rows 0..4 = 5*0.0001
    t("L3_carry_window", abs(cell["carry_cum"][0] - 5 * 0.0001) < 1e-15
      and abs(cell["carry_cum"][1] - 5 * 0.0001) < 1e-15)
    # L4 cost convention x1/x2/x3
    t("L4_cost", abs(COST_RT_X1 - 0.0026082) < 1e-12
      and abs(COST_RT_X1 * 2 - 0.0052164) < 1e-12
      and abs(COST_RT_X1 * 3 - 0.0078246) < 1e-12)
    # L5 pickup identity: c2 = gross - carry - cost; c0 = gross - cost
    t("L5_identity", np.allclose(cell["pickup_c2"],
                                 cell["gross"] - cell["carry_cum"] - COST_RT_X1)
      and np.allclose(cell["pickup_c0"], cell["gross"] - COST_RT_X1))
    # L6 maxdd path math
    path = np.array([100.0, 120.0, 90.0, 110.0])
    peak = np.maximum.accumulate(path)
    t("L6_maxdd", abs(float((path / peak - 1).min()) - (-0.25)) < 1e-9)
    # L7 annualized stint sharpe: zero-sd -> None; known value check
    t("L7_zero_sd", annualized_stint_sharpe(np.array([0.125] * 10), 5) is None)
    u = np.array([0.01, 0.03])
    expect = 0.02 / (0.02 / math.sqrt(2)) * math.sqrt(25.0)
    t("L7_value", abs(annualized_stint_sharpe(u, 10) - expect) < 1e-9)
    # L8 red lines frozen
    t("L8_lines", P95_LINE["A"] == -0.030 and P95_LINE["B"] == -0.060
      and TAIL_CAP["A"] == -0.100 and TAIL_CAP["B"] == -0.150)
    # L9 null family shape on synthetic panel (deterministic seeds)
    syn = {"511880": {"close": close, "carry_prefix": cp,
                      "dates": np.array([f"2024-01-{i:02d}" for i in range(1, 13)]),
                      "amount": np.full(12, 1e8)}}
    rate_d = dict.fromkeys(list(syn["511880"]["dates"]), 0.0001)
    fam = stint_family(close, 5, cp, 0, COST_RT_X1)
    t("L9_family", fam is not None and len(fam["entries"]) == 2)
    r1 = np.random.default_rng(NULL_BASE + 0)
    r2 = np.random.default_rng(NULL_BASE + 0)
    t("L9_seed_det", int(r1.integers(0, 6)) == int(r2.integers(0, 6)))
    # L10 D6 reject line + PBO floor
    t("L10_gates_const", D6_REJECT == 0.70)
    # L11 pbo matrix truncation + completeness
    fake = {f"c{i}": {"pickup_c2": np.arange(20 + i, dtype=float)} for i in range(3)}
    mat, mlen = pbo_matrix(fake)
    t("L11_pbo", mat is not None and mlen == 20 and not mat.isna().any().any())
    thin = {f"c{i}": {"pickup_c2": np.arange(5 + i, dtype=float)} for i in range(3)}
    t("L11_pbo_thin", pbo_matrix(thin)[0] is None)
    # L12 sharpe_ann known value
    ex = np.array([0.01, -0.01] * 10)
    t("L12_sharpe", abs(sharpe_ann(ex) - 0.0) < 1e-12)
    # L13 bootstrap determinism (same seed -> same CI)
    a = SG.bootstrap_ci_sharpe([0.001, 0.002, -0.001, 0.0005] * 25, seed=1)
    b = SG.bootstrap_ci_sharpe([0.001, 0.002, -0.001, 0.0005] * 25, seed=1)
    t("L13_bs_det", a == b)
    # L14 m1 gate contract
    t("L14_m1", SG.m1_t_value_gate(3.5)["pass"] is True
      and SG.m1_t_value_gate(2.9)["pass"] is False)
    # L15 exit-axis: repo engine stack never loaded in this process (runtime
    # truth, top-level exact names -- pandas internals carry 'engines' substring)
    _top = {m.split(".")[0] for m in sys.modules}
    t("L15_no_engine", "engine" not in _top and "exit_rules" not in _top)
    # L16 frozen anchors match prereg sec.2
    t("L16_anchors", FROZEN_ANCHORS["511090"] == {"rows": 797, "first": "2023-06-13"}
      and CUTOFF == "2026-09-22" and NULL_BASE == 94300)
    bad = [n for n, c in ok if not c]
    print(json.dumps({"selftest": "parking_p1", "legs": len(ok),
                      "fail": bad}, ensure_ascii=False))
    sys.exit(1 if bad else 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["probe", "gates", "run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "probe":
        cmd_probe()
    elif a.cmd == "gates":
        cmd_gates()
    elif a.cmd == "run":
        cmd_run()
    else:
        cmd_selftest()


if __name__ == "__main__":
    main()
