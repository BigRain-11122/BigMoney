"""PA1_PREMIUM_IC batch (research/shortline/PA1_PREMIUM_IC.md pre-reg, frozen
r54; T-16 deliverable-6 / claim MSG-20260924-1436; order O-20260924-1155).

Factor-layer IC screening of ETF on/off-exchange premium factors on the
core48 panel built r53 (data/fund_premium/panel/panel.csv). Zero engine
runs -> strategy engine ledger N untouched; registers no traders
(IC != strategy). PASS only shelves premium_z as ETF-domain synthesis
material; strategy conversion needs its own prereg + G1' v2 chain.

Frozen factor definitions (panel-native, zero recompute; prereg SS3):
  primary      premium_z       per-day cross-sectional z of premium_adj
  sensitivity  premium_adj     raw level (same lineage, report-only)
  sensitivity  premium_chg_5d  5d change (same lineage, report-only)
Forward returns (frozen): dividend-inclusive
  (close[t+h] + sum of div_per_unit over (t, t+h]) / close[t] - 1,
cons windows excluded per (t, member) pair. h10 = sole gating horizon;
h5/h20 report columns computed only if primary passes V1 (snooping
discount, non-gating).

Frozen mask (SS3): premium_z finite AND close finite AND fwd_h10
computable AND no cons event in (t, t+h] -- the K=50 nulls share the
same mask (P-A lesson: narrow cross-sections need the same mask band).
Null seeds: 20260925+i, i=0..49 (SEED_REGISTRY["pa1_premium_ic"]).

Gates (SS4, frozen before the run, primary only):
  V1 |IS IC_mean| > max(0.02 floor, masked-null p95 |IC|)
  V2 |IS IC_IR| >= 0.30
  V3 OOS same sign AND |OOS IC_mean| >= 0.5 x |IS IC_mean|
  periods gate: IS n_periods >= 500

Equivalence gate first (PA_LHB paradigm): -60d momentum probe on the
close surface (zero contact with premium columns), seeded 400-day
subsample vs composite_ic.ic_series reference; max|diff| > 1e-6 -> abort
with no numbers produced.

Outputs: research/shortline/pa1_premium_ic_results.csv
         results/shortline/pa1_premium_ic.json (+ gate_attrition.json row)
"""
import json
import os
import subprocess
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from composite_ic import IS_END, ic_series, stats_block  # established methodology
import science_gates as sg  # cutoff_meta / append_ledger / ledger_head

PANEL_CSV = os.path.join(ROOT, "data", "fund_premium", "panel", "panel.csv")
PANEL_SUMMARY = os.path.join(ROOT, "results", "shortline", "fund_premium_panel.json")
RES_CSV = os.path.join(ROOT, "research", "shortline", "pa1_premium_ic_results.csv")
OUT_JSON = os.path.join(ROOT, "results", "shortline", "pa1_premium_ic.json")
ATTRITION_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

H_GATE = 10            # sole gating horizon (prereg SS3)
H_REPORT = [5, 20]     # report-only, computed for primary V1 passers only
N_NULLS = 50
SEED0 = 20260925       # SEED_REGISTRY["pa1_premium_ic"], date-style (prereg SS3)
V1_FLOOR = 0.02
V2_IR = 0.30
V3_RETAIN = 0.5
MIN_PERIODS = 500
IS_END_TS = pd.Timestamp(IS_END)
CUTOFF = "2026-09-23"  # panel evidence_cutoff (r53 build, forward lockbox D2)
EQUIV_TOL = 1e-6
EQUIV_N_DATES = 400
NAV_COV_MIN = 0.95
N_EFF_BASE = 53        # 1 primary + 2 sensitivity + 50 nulls (prereg SS0)
N_EFF_REPORT = 2       # +h5/h20 report columns if primary passes V1 (cap 55)


# ---------------------------------------------------------------- helpers
def rank_rows(eff, values):
    """Mask-first then rank (J7 pitfall family): average ties, NaN outside
    eff. eff = pairwise-complete mask for the (factor, fwd) pair."""
    return pd.DataFrame(np.where(eff, values, np.nan)).rank(axis=1).values


def ic_from_ranks(F, R, dates):
    """Spearman IC per date from rank arrays with identical support.

    n = pairwise count; >=5 names; zero-variance -> NaN. Index = dates."""
    with np.errstate(invalid="ignore"):
        fm = np.nanmean(F, axis=1)
        rm = np.nanmean(R, axis=1)
        dF = F - fm[:, None]
        dR = R - rm[:, None]
        cov = np.nansum(dF * dR, axis=1)
        sf = np.sqrt(np.nansum(dF * dF, axis=1))
        sr = np.sqrt(np.nansum(dR * dR, axis=1))
        ic = cov / (sf * sr)
    n = (np.isfinite(F) & np.isfinite(R)).sum(axis=1)
    ok = np.isfinite(ic) & (sf > 0) & (sr > 0) & (n >= 5)
    idx = pd.DatetimeIndex(dates[ok])
    return pd.Series(ic[ok], index=idx).dropna()


def fwd_ret_div(close, div, h):
    """Dividend-inclusive forward return (prereg SS3):
    (close[t+h] + sum_{t<d<=t+h} div_per_unit[d]) / close[t] - 1.
    div must be NaN->0 upstream; rows with t+h beyond the panel -> NaN."""
    cs = np.cumsum(div, axis=0)
    out = np.full_like(close, np.nan)
    out[:-h] = (close[h:] + (cs[h:] - cs[:-h])) / close[:-h] - 1.0
    return out


def cons_in_window(cons, h):
    """True where any cons_flag=1 day falls in (t, t+h] for that member."""
    cs = np.cumsum(cons, axis=0)
    out = np.zeros(cons.shape, dtype=bool)
    out[:-h] = (cs[h:] - cs[:-h]) > 0
    return out


def seg_stats(s):
    return (stats_block(s), stats_block(s[s.index <= IS_END_TS]),
            stats_block(s[s.index > IS_END_TS]))


def wide(pan, col):
    return pan.pivot(index="date", columns="code", values=col).values


# ---------------------------------------------------------------- main
def main():
    t0 = time.time()
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)

    # ---- panel load (long -> wide; native columns only, zero recompute)
    pan = pd.read_csv(PANEL_CSV, parse_dates=["date"])
    codes = sorted(pan["code"].unique())
    cal = pd.DatetimeIndex(np.sort(pan["date"].unique()))
    T, N = len(cal), len(codes)
    close = np.asarray(wide(pan, "close"), dtype=np.float64)
    pz = np.asarray(wide(pan, "premium_z"), dtype=np.float64)
    pa = np.asarray(wide(pan, "premium_adj"), dtype=np.float64)
    pchg = np.asarray(wide(pan, "premium_chg_5d"), dtype=np.float64)
    nav = np.asarray(wide(pan, "nav"), dtype=np.float64)
    div = np.nan_to_num(np.asarray(wide(pan, "div_per_unit"), dtype=np.float64))
    cons = np.nan_to_num(np.asarray(wide(pan, "cons_flag"), dtype=np.float64))
    print(f"panel: T={T} ({cal[0].date()}..{cal[-1].date()}) x N={N} "
          f"({time.time()-t0:.0f}s)", flush=True)

    # ---- data-completeness gates (prereg SS2; fail -> abort, no numbers)
    # Row-wise convention (r52/r53 gate scope): quality of panel ROWS that
    # exist. Rectangular completeness (fund,date) gaps from later listings
    # are the mask's job (isfinite), not a data defect.
    nav_cov = float(pan["nav"].notna().mean())
    pa_nan = int(pan["premium_adj"].isna().sum())
    rect_gap = int(close.size - np.isfinite(close).sum())
    summ = json.load(open(PANEL_SUMMARY, encoding="utf-8-sig"))
    summ_gates = summ.get("gates", {})
    g1 = nav_cov >= NAV_COV_MIN
    g2 = (summ_gates.get("verdict") == "PASS"
          and summ.get("evidence_cutoff") == CUTOFF
          and int(summ.get("members", 0)) == N)
    g3 = pa_nan == 0
    print(f"data gates: nav_cov={nav_cov:.4f} (>= {NAV_COV_MIN}: {g1}) "
          f"row-wise | panel summary verdict={summ_gates.get('verdict')} "
          f"cutoff={summ.get('evidence_cutoff')} ({g2}) | "
          f"premium_adj_nan={pa_nan} ({g3}) | rect_gap={rect_gap} "
          f"(later-listing cells, mask-handled)", flush=True)
    if not (g1 and g2 and g3):
        print("DATA GATE FAIL - aborting batch (no numbers produced)")
        sys.exit(1)

    # ---- forward returns + frozen mask (SS3), gating horizon
    fwd10 = fwd_ret_div(close, div, H_GATE)
    cons10 = cons_in_window(cons, H_GATE)
    mask10 = (np.isfinite(pz) & np.isfinite(close) & np.isfinite(fwd10)
              & ~cons10)
    n_cons_excl = int((cons10 & np.isfinite(pz) & np.isfinite(close)
                       & np.isfinite(fwd10)).sum())
    row_n = mask10.sum(axis=1)
    xs_med = int(np.median(row_n[row_n > 0]))
    print(f"mask10: median cross-section={xs_med} members, "
          f"cells={int(mask10.sum())}, cons-excluded cells={n_cons_excl} "
          f"({time.time()-t0:.0f}s)", flush=True)

    # ---- equivalence gate: fast path vs composite_ic.ic_series reference
    # probe = -60d momentum on the close surface, ZERO contact with premium
    print("equivalence gate: fast IC vs reference on -60d momentum probe...",
          flush=True)
    p60 = np.full_like(close, np.nan)
    p60[60:] = close[60:] / close[:-60] - 1.0
    probe = -p60
    rng_dates = np.random.default_rng(SEED0)
    sub = np.sort(rng_dates.choice(T, size=min(EQUIV_N_DATES, T),
                                   replace=False))
    sub_idx = pd.DatetimeIndex(cal[sub])
    probe_df = pd.DataFrame(probe[sub], index=sub_idx, columns=codes)
    fwd_df = pd.DataFrame(fwd10[sub], index=sub_idx, columns=codes)
    ref = ic_series(probe_df, fwd_df)
    eff = np.isfinite(probe[sub]) & np.isfinite(fwd10[sub])
    F = rank_rows(eff, probe[sub])
    R = rank_rows(eff, fwd10[sub])
    fast = ic_from_ranks(F, R, cal[sub])
    common = ref.index.intersection(fast.index)
    worst = float((ref[common] - fast[common]).abs().max()) if len(common) \
        else 9.9
    print(f"  n_ref={len(ref)} n_fast={len(fast)} common={len(common)} "
          f"max|diff|={worst:.2e}", flush=True)
    if worst > EQUIV_TOL or len(ref) != len(fast):
        print("EQUIVALENCE FAIL - aborting batch (no numbers produced)")
        sys.exit(1)

    # ---- null baselines (K=50 white noise, same frozen mask, IS segment)
    t1 = time.time()
    abs_ic, abs_ir = [], []
    R_fwd = rank_rows(mask10, fwd10)
    for k in range(N_NULLS):
        rng = np.random.default_rng(SEED0 + k)
        noise = rng.standard_normal((T, N))
        F = rank_rows(mask10, noise)
        s = ic_from_ranks(F, R_fwd, cal)
        blk = stats_block(s[s.index <= IS_END_TS])
        if "ic_mean" in blk:
            abs_ic.append(abs(blk["ic_mean"]))
            abs_ir.append(abs(blk["ic_ir"]))
        if (k + 1) % 10 == 0:
            print(f"  null {k+1}/{N_NULLS} ({time.time()-t1:.0f}s)",
                  flush=True)
    thr = {
        "p95_abs_ic": round(float(np.quantile(abs_ic, 0.95)), 4),
        "p95_abs_ir": round(float(np.quantile(abs_ir, 0.95)), 4),
        "n_nulls": len(abs_ic),
        "median_cross_section": xs_med,
    }
    print(f"  nulls: p95|ic|={thr['p95_abs_ic']} p95|ir|={thr['p95_abs_ir']} "
          f"({time.time()-t1:.0f}s)", flush=True)
    v1_thr = max(V1_FLOOR, thr["p95_abs_ic"])

    # ---- factor batch at the gating horizon (mask-first, same mask band)
    factors = [
        ("premium_z", pz, True),
        ("premium_adj", pa, False),
        ("premium_chg_5d", pchg, False),
    ]
    rows = []
    primary_pass, primary_v1 = False, False
    for name, vals, is_primary in factors:
        t2 = time.time()
        eff_f = mask10 & np.isfinite(vals)
        s = ic_from_ranks(rank_rows(eff_f, vals), rank_rows(eff_f, fwd10),
                          cal)
        blk_full, blk_is, blk_oos = seg_stats(s)
        rec = {"factor": name, "role": "primary" if is_primary
               else "sensitivity", "mask": "frozen_h10",
               "status": "ok", "v1_thr": v1_thr}
        for seg, blk in [("full", blk_full), ("is", blk_is),
                         ("oos", blk_oos)]:
            for k in ("ic_mean", "ic_ir", "n_periods"):
                rec[f"h{H_GATE}_{seg}_{k}"] = blk.get(k, "")
        if is_primary:
            if "ic_mean" in blk_is and "ic_mean" in blk_oos:
                v1 = abs(blk_is["ic_mean"]) > v1_thr
                v2 = abs(blk_is["ic_ir"]) >= V2_IR
                v3 = ((blk_oos["ic_mean"] > 0) == (blk_is["ic_mean"] > 0)
                      and abs(blk_oos["ic_mean"]) >= V3_RETAIN
                      * abs(blk_is["ic_mean"]))
                pg = blk_is["n_periods"] >= MIN_PERIODS
                rec.update({"v1": bool(v1), "v2": bool(v2), "v3": bool(v3),
                            "period_gate": bool(pg),
                            "pass": bool(v1 and v2 and v3 and pg)})
                primary_pass, primary_v1 = rec["pass"], bool(v1)
            else:
                rec.update({"v1": False, "v2": False, "v3": False,
                            "period_gate": False, "pass": False})
            print(f"  {name}[primary] is_ic={rec.get('h10_is_ic_mean')} "
                  f"ir={rec.get('h10_is_ic_ir')} oos_ic="
                  f"{rec.get('h10_oos_ic_mean')} pass={rec['pass']}",
                  flush=True)
        else:
            rec.update({"v1": "", "v2": "", "v3": "", "period_gate": "",
                        "pass": ""})  # report-only, not judged (SS4)
            print(f"  {name}[sensitivity] is_ic={rec.get('h10_is_ic_mean')} "
                  f"(report-only)", flush=True)
        rec["compute_s"] = round(time.time() - t2, 1)
        rows.append(rec)

    # ---- report horizons h5/h20 (primary V1 passer only, non-gating)
    report_done = False
    if primary_v1:
        for h in H_REPORT:
            fw = fwd_ret_div(close, div, h)
            eff_h = (np.isfinite(pz) & np.isfinite(close) & np.isfinite(fw)
                     & ~cons_in_window(cons, h))
            sh_ = ic_from_ranks(rank_rows(eff_h, pz), rank_rows(eff_h, fw),
                                cal)
            _, bis, bos = seg_stats(sh_)
            rows[0][f"h{h}_is_ic"] = bis.get("ic_mean", "")
            rows[0][f"h{h}_oos_ic"] = bos.get("ic_mean", "")
        report_done = True
        print(f"  report horizons h5/h20 computed for primary V1 passer "
              f"(snooping-discount, non-gating)", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(RES_CSV, index=False, encoding="utf-8")

    # ---- trials ledger (factor line: prev = max across BOTH dirs, r60
    # one-chain convention; zero engine runs -> engine N untouched)
    n_cells = N_EFF_BASE + (N_EFF_REPORT if report_done else 0)
    prev = max(int(sg.ledger_head(os.path.join(ROOT, "results"))["total"]),
               int(sg.ledger_head(os.path.dirname(OUT_JSON))["total"]))
    ledger = sg.append_ledger(
        "pa1_premium_ic", n_cells, "results/shortline/pa1_premium_ic.json",
        evidence_cutoff=CUTOFF, prev_total=prev,
        note=("1 primary premium_z + 2 sensitivity (same premium_adj "
              "lineage, report-only) + 50 matched-mask nulls (seed "
              "20260925+i); zero engine runs, factor-layer IC batch "
              "(PA1_PREMIUM_IC.md frozen r54, claim MSG-20260924-1436)"))

    # ---- audit segment (compute_audit in-batch, prereg SS0: no audit
    # section -> results not ledgered; here embedded in the payload)
    audit_seg = {}
    try:
        subprocess.run([sys.executable,
                        os.path.join("scripts", "compute_audit.py")],
                       cwd=ROOT, capture_output=True, text=True, timeout=120)
    except Exception as exc:  # noqa: BLE001
        print(f"[pa1] compute_audit in-batch run failed: {exc}", flush=True)
    apath = os.path.join(ROOT, "results", "compute_audit.json")
    if os.path.exists(apath):
        with open(apath, encoding="utf-8") as fh:
            aj = json.load(fh)
        latest = aj.get("history", [{}])[-1] if aj.get("history") else aj
        audit_seg = {"source": "results/compute_audit.json (in-batch run, "
                               "latest)",
                     "verdict": latest.get("verdict"), "ts": latest.get("ts"),
                     "cpu_pct": latest.get("cpu_pct"),
                     "flags": latest.get("flags")}
    audit_seg.update({"elapsed_sec": round(time.time() - t0, 1),
                      "workers": 1,
                      "cpu_cap_policy": "vectorized single-proc, "
                                        "memory-bound rank ops "
                                        "(O-20260923-1738)"})

    out = {
        **sg.cutoff_meta(CUTOFF),  # C2-legal top-level key (T-02 7/7)
        "meta": {"batch": "PA1_PREMIUM_IC (ETF premium factor IC)",
                 "pre_reg": "research/shortline/PA1_PREMIUM_IC.md",
                 "order": "O-20260924-1155", "claim": "MSG-20260924-1436",
                 "task": "T-16 deliverable-6/7", "dept": "data+research",
                 "date": time.strftime("%Y-%m-%d %H:%M"),
                 "is_end": IS_END, "gate_horizon": H_GATE,
                 "n_nulls": N_NULLS, "seed0": SEED0,
                 "seed_registry": sg.SEED_REGISTRY.get("pa1_premium_ic"),
                 "window": f"{cal[0].date()}..{cal[-1].date()} "
                           f"(panel r53, cutoff {CUTOFF})",
                 "factors_frozen": "panel-native columns, zero recompute",
                 "fwd_ret": "dividend-inclusive (close[t+h]+sum div in "
                            "(t,t+h])/close[t]-1, cons windows excluded",
                 "mask_frozen": "premium_z finite & close finite & fwd_h10 "
                                "computable & no cons in (t,t+h]; nulls "
                                "same mask",
                 "availability_convention": "as-of NAV (nav_date<close_date "
                                            "per-fund latest), no uniform "
                                            "T-1 (frozen r54)",
                 "engine_runs": 0,
                 "ledger_note": "factor-layer IC batch: strategy engine "
                                "ledger N untouched (P-4-2a/PA_LHB "
                                "precedent); PASS -> shelf only, no trader "
                                "registration",
                 "ic_computations": 1 + N_NULLS + len(factors)
                                    + (len(H_REPORT) if report_done else 0)},
        "data_gates": {"nav_coverage": round(nav_cov, 4),
                       "nav_cov_min": NAV_COV_MIN, "g1": bool(g1),
                       "gate_scope": "row-wise (panel rows that exist)",
                       "panel_summary_verdict": summ_gates.get("verdict"),
                       "panel_summary_cutoff": summ.get("evidence_cutoff"),
                       "g2": bool(g2), "premium_adj_nan": pa_nan,
                       "g3": bool(g3),
                       "rect_gap_cells": rect_gap,
                       "rect_gap_note": "later-listing (fund,date) cells "
                                        "absent from the long panel; handled "
                                        "by the frozen mask, not a data "
                                        "defect"},
        "mask_stats": {"median_cross_section": xs_med,
                       "cells": int(mask10.sum()),
                       "cons_excluded_cells": n_cons_excl,
                       "T": T, "N": N},
        "equivalence": {"probe": "-60d momentum @ core48 close surface",
                        "max_abs_diff": worst, "n_common": int(len(common)),
                        "tol": EQUIV_TOL, "pass": worst <= EQUIV_TOL},
        "thresholds": {"h10": thr, "v1_floor": V1_FLOOR, "v1_thr": v1_thr},
        "counts": {"computed": len(factors),
                   "report_horizons_computed": report_done,
                   "pass": int(primary_pass)},
        "rows": rows,
        "trials_ledger": ledger,
        "audit": audit_seg,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    # ---- gate_attrition entry (measurement batch: gate outcomes, s7-T)
    try:
        with open(ATTRITION_JSON, encoding="utf-8-sig") as fh:
            attr = json.load(fh)
        prim = rows[0]
        attr["entries"].append({
            "batch": "PA1_PREMIUM_IC",
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "measurement",
            "cells_ledger_delta": n_cells,
            "ledger_total_after": ledger.get("total"),
            "gates": {"v1_floor": V1_FLOOR,
                      "null_is_p95_abs_ic": thr["p95_abs_ic"],
                      "v1_thr": v1_thr,
                      "primary_v1": bool(prim.get("v1")),
                      "primary_v2": bool(prim.get("v2")),
                      "primary_v3": bool(prim.get("v3")),
                      "period_gate": bool(prim.get("period_gate")),
                      "pass": bool(primary_pass),
                      "void": False},
            "eliminated": None,
            "refs": {"results": "results/shortline/pa1_premium_ic.json",
                     "prereg": "research/shortline/PA1_PREMIUM_IC.md"},
        })
        with open(ATTRITION_JSON, "w", encoding="utf-8") as fh:
            json.dump(attr, fh, ensure_ascii=False, indent=1)
    except Exception as exc:  # noqa: BLE001
        print(f"[pa1] gate_attrition append failed: {exc}", flush=True)

    print(f"\n=== PA1_PREMIUM_IC: computed={len(factors)} "
          f"primary_pass={primary_pass} cells={n_cells} "
          f"ledger_total={ledger['total']} "
          f"({time.time()-t0:.0f}s) ===", flush=True)
    if primary_pass:
        print("verdict: premium_z shelved as ETF-domain synthesis material "
              "(conversion = separate prereg)", flush=True)
    else:
        print("verdict: P-A1 factor judged negative - honest close "
              "(panel data asset retained for P-A2/P-B1)", flush=True)


if __name__ == "__main__":
    main()
