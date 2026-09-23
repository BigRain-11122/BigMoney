"""P-A2 LHB survivor synthesis (research/shortline/PA2_LHB_SYNTH.md pre-reg).

O-1819 queue-never-empty lane (claim MSG-20260923-2030, before prereg commit).
Factor-layer IC synthesis of the three P-A survivor factors; zero engine
runs -> strategy engine ledger N untouched; registers no traders (IC !=
strategy). Stock-pool strategy runs stay behind the O-1820 R38 hard gate.

Frozen construction parity: helpers imported from scripts/pa_lhb_ic.py
(rolling_sum/shift1/rank_rows/ic_from_ranks/fwd_ret/seg_stats); panel and
event-grid loading copied verbatim from pa_lhb_ic.main(); copy fidelity is
adjudicated by the anchor gate (rounded equality vs registered P-A evidence
in results/shortline/pa_lhb_ic.json) BEFORE any batch number is produced.

Composites (SS3): COMP-A primary = z(-count_20)+z(share 0-fill) @ mask A;
COMP-C secondary = z(days_since)+z(share 0-fill) @ mask C. Structured nulls
(SS4): K=50 noise pairs, noise2 supported only on the B-support (replicates
the 0-fill tie-block structure), seeds 20260923+1000+k.

Outputs: research/shortline/pa2_lhb_synth_results.csv
         results/shortline/pa2_lhb_synth.json
"""
import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from pa_lhb_ic import (  # frozen construction, zero re-derivation
    BARS_DIR, CACHE_DIR, H_GATE, H_REPORT, IS_END_TS, LHB_PATH, MIN_PERIODS,
    SEED0, V1_FLOOR, V2_IR, V3_RETAIN, WIN_START, W_COUNT, W_DECAY, W_NETBUY,
    W_SHARE, fwd_ret, ic_from_ranks, rank_rows, rolling_sum, seg_stats, shift1,
)

RES_DIR = os.path.join(ROOT, "research", "shortline")
OUT_DIR = os.path.join(ROOT, "results", "shortline")
PA_JSON = os.path.join(OUT_DIR, "pa_lhb_ic.json")
N_NULLS = 50
SEED_OFFSET = 1000  # disjoint from P-A's +0..49 stream
ANCHOR_TOL_MEAN = 0.5e-4   # half of last kept digit (4dp registered evidence)
ANCHOR_TOL_IR = 0.5e-3     # 3dp registered evidence


def z_rows(mask, vals):
    """Per-date cross-sectional z-score inside mask (ddof=0; std=0 -> 0)."""
    v = np.where(mask, vals, np.nan)
    with np.errstate(invalid="ignore"):
        mu = np.nanmean(v, axis=1)
        sd = np.nanstd(v, axis=1)
    sd_safe = np.where(sd > 0, sd, 1.0)
    z = (v - mu[:, None]) / sd_safe[:, None]
    return np.where((sd > 0)[:, None], z, 0.0)


def ic_h(mask, vals, fwd, cal):
    """Masked rank IC at horizon `fwd` grid + full/is/oos stat blocks."""
    eff = mask & np.isfinite(vals) & np.isfinite(fwd)
    s = ic_from_ranks(rank_rows(eff, vals), rank_rows(eff, fwd), cal)
    return seg_stats(s)


def main():
    t0 = time.time()

    # ---- panel slice (verbatim copy of pa_lhb_ic.main loading section) ----
    dates_all = np.load(os.path.join(CACHE_DIR, "dates.npy"))
    i0 = int(np.searchsorted(dates_all,
                             np.datetime64(WIN_START, "us").astype("int64")))
    cal = dates_all[i0:]
    T = len(cal)
    files = sorted(glob.glob(os.path.join(BARS_DIR, "*.parquet")))
    syms = [os.path.basename(p)[:-8] for p in files]
    N = len(syms)
    sym_col = {s: i for i, s in enumerate(syms)}
    close = np.asarray(np.load(os.path.join(CACHE_DIR, "close.npy"),
                               mmap_mode="r")[i0:], dtype=np.float64)
    amount = np.asarray(np.load(os.path.join(CACHE_DIR, "amount.npy"),
                                mmap_mode="r")[i0:], dtype=np.float64)
    print(f"panel slice: T={T} x N={N} ({time.time()-t0:.0f}s)", flush=True)

    # ---- LHB events: dedup per (code,date) = row with max LHB turnover ----
    lhb = pd.read_parquet(LHB_PATH)
    n_raw = len(lhb)
    lhb = lhb.sort_values(["龙虎榜成交额", "序号"], ascending=[True, False])
    ev = lhb.drop_duplicates(subset=["代码", "上榜日"], keep="last")
    n_events = len(ev)
    ev_us = (pd.to_datetime(ev["上榜日"]).values.astype("datetime64[us]")
             .astype("int64"))
    pos = np.searchsorted(cal, ev_us)
    in_cal = pos < T
    pos_safe = np.minimum(pos, T - 1)
    pos_ok = in_cal & (cal[pos_safe] == ev_us)
    cols = ev["代码"].map(sym_col)
    col_ok = cols.notna().values
    keep = pos_ok & col_ok
    r_idx = pos[keep]
    c_idx = cols.values[keep].astype(int)
    n_placed = int(keep.sum())
    print(f"events: raw={n_raw} dedup={n_events} placed={n_placed} "
          f"({time.time()-t0:.0f}s)", flush=True)

    # ---- event-time grids + shifts (verbatim P-A construction) ----
    ind = np.zeros((T, N))
    ind[r_idx, c_idx] = 1.0
    sh_grid = np.zeros((T, N))
    sh_grid[r_idx, c_idx] = ev["成交额占总成交比"].values[keep]
    count20 = rolling_sum(ind, W_COUNT)
    share20 = rolling_sum(sh_grid, W_SHARE)
    with np.errstate(invalid="ignore", divide="ignore"):
        amt_share20 = np.where(count20 > 0, share20 / count20, np.nan)
    ev_pos = np.where(ind > 0, np.arange(T)[:, None], -1.0)
    last_ev = np.maximum.accumulate(ev_pos, axis=0)
    days_since = np.arange(T)[:, None] - last_ev
    days_since[last_ev < 0] = np.nan
    days_capped = np.where(days_since <= W_DECAY, days_since, np.nan)

    count_s = shift1(count20, 0.0)
    days_s = shift1(days_capped)
    share_s = shift1(amt_share20)

    A = np.isfinite(close) & np.isfinite(amount)
    B = A & (count_s >= 1)
    C = A & np.isfinite(days_s)
    print(f"masks up ({time.time()-t0:.0f}s)", flush=True)

    # ---- 0-fill share leg: true value semantics (SS3), support recorded ----
    share0 = np.where(np.isfinite(share_s), share_s, 0.0)
    supp = B & np.isfinite(share_s)   # nonzero-firepower support (for nulls)

    fwd10 = fwd_ret(close, H_GATE)

    # ---- ANCHOR GATE: rounded equality vs registered P-A evidence ----
    pa = json.load(open(PA_JSON, encoding="utf-8"))
    anchors_spec = [
        ("lhb_count_20", count_s, A),
        ("lhb_days_since", days_s, C),
        ("lhb_amt_share_20", share_s, B),
    ]
    anchor_report = []
    anchor_ok = True
    for name, vals, mask in anchors_spec:
        _, bis, bos = ic_h(mask, vals, fwd10, cal)
        reg = next(r for r in pa["rows"] if r["factor"] == name)
        checks = {
            "is_ic": abs(bis["ic_mean"] - reg["h10_is_ic_mean"]) < ANCHOR_TOL_MEAN,
            "is_ir": abs(bis["ic_ir"] - reg["h10_is_ic_ir"]) < ANCHOR_TOL_IR,
            "is_n": bis["n_periods"] == reg["h10_is_n_periods"],
            "oos_ic": abs(bos["ic_mean"] - reg["h10_oos_ic_mean"]) < ANCHOR_TOL_MEAN,
            "oos_ir": abs(bos["ic_ir"] - reg["h10_oos_ic_ir"]) < ANCHOR_TOL_IR,
            "oos_n": bos["n_periods"] == reg["h10_oos_n_periods"],
        }
        ok = all(checks.values())
        anchor_ok &= ok
        anchor_report.append({"factor": name,
                              "reproduced_is_ic": bis["ic_mean"],
                              "registered_is_ic": reg["h10_is_ic_mean"],
                              "reproduced_oos_ic": bos["ic_mean"],
                              "registered_oos_ic": reg["h10_oos_ic_mean"],
                              "checks": checks, "ok": bool(ok)})
        print(f"anchor {name}: is_ic={bis['ic_mean']} vs {reg['h10_is_ic_mean']}"
              f" oos_ic={bos['ic_mean']} vs {reg['h10_oos_ic_mean']}"
              f" ok={ok}", flush=True)
    if not anchor_ok:
        print("ANCHOR GATE FAIL - aborting batch (no numbers produced)")
        sys.exit(1)
    print(f"anchor gate PASS 3/3 ({time.time()-t0:.0f}s)", flush=True)

    # ---- composites (SS3) ----
    composites = [
        ("COMP-A", A, supp, -count_s),
        ("COMP-C", C, supp & C, days_s),
    ]
    results = []
    null_p95 = {}
    for name, mask, support, leg1_raw in composites:
        t1 = time.time()
        comp = z_rows(mask, leg1_raw) + z_rows(mask, share0)
        blk_full, blk_is, blk_oos = ic_h(mask, comp, fwd10, cal)
        print(f"{name}: is_ic={blk_is.get('ic_mean')} "
              f"ir={blk_is.get('ic_ir')} oos_ic={blk_oos.get('ic_mean')} "
              f"({time.time()-t1:.0f}s)", flush=True)
        results.append({"composite": name, "mask": "A" if mask is A else "C",
                        "status": "ok",
                        "h10_full_ic": blk_full.get("ic_mean", ""),
                        "h10_is_ic": blk_is.get("ic_mean", ""),
                        "h10_is_ir": blk_is.get("ic_ir", ""),
                        "h10_is_n": blk_is.get("n_periods", ""),
                        "h10_oos_ic": blk_oos.get("ic_mean", ""),
                        "h10_oos_ir": blk_oos.get("ic_ir", ""),
                        "h10_oos_n": blk_oos.get("n_periods", "")})
        # structured nulls (SS4): noise2 supported only on `support`
        abs_ic = []
        eff_fwd = mask & np.isfinite(fwd10)
        R_fwd = rank_rows(eff_fwd, fwd10)
        t2 = time.time()
        for k in range(N_NULLS):
            rng = np.random.default_rng(SEED0 + SEED_OFFSET + k)
            n1 = rng.standard_normal((T, N))
            n2 = rng.standard_normal((T, N))
            n2 = np.where(support, n2, 0.0)
            cnull = z_rows(mask, n1) + z_rows(mask, n2)
            s = ic_from_ranks(rank_rows(eff_fwd, cnull), R_fwd, cal)
            blk = seg_stats(s)[1]
            if "ic_mean" in blk:
                abs_ic.append(abs(blk["ic_mean"]))
            if (k + 1) % 10 == 0:
                print(f"  null[{name}] {k+1}/{N_NULLS} "
                      f"({time.time()-t2:.0f}s)", flush=True)
        p95 = float(np.quantile(abs_ic, 0.95)) if abs_ic else 9.9
        null_p95[name] = {"p95_abs_ic": round(p95, 4),
                          "n_nulls": len(abs_ic)}
        print(f"  null[{name}] p95|ic|={p95:.4f} "
              f"({time.time()-t2:.0f}s)", flush=True)

    # ---- gates (SS4) ----
    for rec in results:
        if isinstance(rec.get("h10_is_ic"), float) and \
                isinstance(rec.get("h10_oos_ic"), float):
            thr = max(V1_FLOOR, null_p95[rec["composite"]]["p95_abs_ic"])
            v1 = abs(rec["h10_is_ic"]) > thr
            v2 = abs(rec["h10_is_ir"]) >= V2_IR
            v3 = ((rec["h10_oos_ic"] > 0) == (rec["h10_is_ic"] > 0)
                  and abs(rec["h10_oos_ic"]) >= V3_RETAIN
                  * abs(rec["h10_is_ic"]))
            pg = rec["h10_is_n"] >= MIN_PERIODS
            rec.update({"v1_thr": round(thr, 4), "v1": bool(v1),
                        "v2": bool(v2), "v3": bool(v3),
                        "period_gate": bool(pg),
                        "pass": bool(v1 and v2 and v3 and pg)})
            if rec["pass"]:  # report-only horizons for passers (non-gating)
                for h in H_REPORT:
                    fw = fwd_ret(close, h)
                    _, bis, bos = ic_h(
                        A if rec["mask"] == "A" else C,
                        z_rows(A, -count_s) + z_rows(A, share0)
                        if rec["mask"] == "A"
                        else z_rows(C, days_s) + z_rows(C, share0), fw, cal)
                    rec[f"h{h}_is_ic"] = bis.get("ic_mean", "")
                    rec[f"h{h}_oos_ic"] = bos.get("ic_mean", "")
        else:
            rec.update({"v1": False, "v2": False, "v3": False,
                        "period_gate": False, "pass": False})

    # ---- inter-leg mechanism readout (SS5): spearman(count,share) on B ----
    eff_c = B & np.isfinite(share_s)
    s_legs = ic_from_ranks(rank_rows(eff_c, count_s),
                           rank_rows(eff_c, share_s), cal)
    _, legs_is, _ = seg_stats(s_legs)
    leg_corr_is = legs_is.get("ic_mean", "")
    print(f"inter-leg corr (IS): {leg_corr_is}", flush=True)

    n_pass = int(sum(bool(r.get("pass")) for r in results))
    df = pd.DataFrame(results)
    df.to_csv(os.path.join(RES_DIR, "pa2_lhb_synth_results.csv"),
              index=False, encoding="utf-8")
    out = {
        "meta": {"batch": "P-A2 LHB survivor synthesis",
                 "pre_reg": "research/shortline/PA2_LHB_SYNTH.md",
                 "order": "O-20260923-1819 queue-never-empty refill",
                 "claim": "MSG-20260923-2030",
                 "date": time.strftime("%Y-%m-%d %H:%M"),
                 "gate_horizon": H_GATE, "n_nulls_per_composite": N_NULLS,
                 "seed0": SEED0 + SEED_OFFSET,
                 "is_end": str(IS_END_TS.date()),
                 "window": f"{WIN_START} -> cache cutoff",
                 "mirror_clause": "count/days_since split across composites",
                 "zero_fill_clause": "amt_share true-value 0 outside B",
                 "primary": "COMP-A", "secondary": "COMP-C (no promotion)",
                 "engine_runs": 0,
                 "ledger_note": "factor IC batch: strategy engine ledger N "
                                "untouched (P-A precedent); stock-pool "
                                "strategy runs stay behind O-1820 R38 gate",
                 "ic_computations": 3 + 2 + 2 * N_NULLS + 1},
        "anchor_gate": {"rows": anchor_report,
                        "tol_mean": ANCHOR_TOL_MEAN, "tol_ir": ANCHOR_TOL_IR,
                        "pass": bool(anchor_ok)},
        "events": {"raw_rows": n_raw, "dedup_stock_days": n_events,
                   "placed": n_placed},
        "panel": {"T": T, "N": N,
                  "start": str(cal[0].astype("datetime64[us]")),
                  "end": str(cal[-1].astype("datetime64[us]"))},
        "nulls": null_p95,
        "rows": results,
        "mechanism": {"leg_corr_count_vs_share_is": leg_corr_is,
                      "note": "positive corr = attention breeds firepower; "
                              "COMP-A leg-cancellation risk readout"},
        "counts": {"computed": 2, "pass": n_pass},
        "audit": {"elapsed_sec": round(time.time() - t0, 1), "workers": 1,
                  "cpu_cap_policy": "O-20260923-1738 (vectorized single-proc)"},
    }
    with open(os.path.join(OUT_DIR, "pa2_lhb_synth.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\n=== P-A2 synthesis: pass={n_pass}/2 "
          f"({time.time()-t0:.0f}s) ===", flush=True)


if __name__ == "__main__":
    main()
