"""P-1e probe (zoo #85/#92/#93 behavior-factor IC batch, pre-prereg face probe).

Prereg-input probe ONLY (no judgement numbers recorded): constructs the
frozen zoo cells (scripts/p1e_factors.py, selftest-gated) on the p1c_stock
cache panel, measures per-factor compute cost (the #93 freeze-card clause:
measured re-check of the 7.5e8-ops estimate), checks the turnover unit
convention, and runs the batch-design corr pre-check mandated by the zoo
rows / freeze digest:
  - pairwise among zoo mains (85 terrified / 85 STV / 92 coin_team / 93 ARC)
  - intra-#93 (ARC vs VRC/SRC/KRC variant legs)
  - zoo mains vs GTJA named neighbors 070/081 (zoo rows) + 042 (pool head)
ALL corr/coverage stats are computed on the IS window only (<= IS_END
2024-12-31) so the OOS face stays untouched by the probe. No IC means are
recorded anywhere (similarity inputs only).

Reuse (no rewrite): p1c_stock_ic_batch loaders + vendor loader +
_peak_ram_gb; shortline_p1_ic._ic_series_fast; composite_ic.IS_END;
constructors from p1e_factors (selftest-gated, ARC brute-force green).
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from composite_ic import IS_END                                    # noqa: E402
from shortline_p1_ic import _ic_series_fast                        # noqa: E402
import p1c_stock_ic_batch as P1C                                   # noqa: E402
from p1e_factors import (_xs_spearman_series, build_zoo85_stv,     # noqa: E402
                         build_zoo85_terrified, build_zoo92_coin_team,
                         build_zoo93_arc_family)

CACHE_DIR = P1C.CACHE_DIR
OUT_JSON = os.path.join(P1C.OUT_DIR, "p1e_probe.json")
GTJA_NEIGHBORS = ("alpha191_070", "alpha191_081", "alpha191_042")


def main():
    t_all = time.time()
    rep = {"meta": {
        "probe": "P-1e zoo behavior-factor IC batch face probe "
                 "(prereg-input, IS-only corr/coverage, zero judgement)",
        "run_at": time.strftime("%Y-%m-%d %H:%M"),
        "panel": "Money02/data/cache/p1c_stock (T=8792, N=5222, ok 5130)",
        "is_end": str(IS_END),
        "constructors": "scripts/p1e_factors.py selftest PASS "
                        "(ARC brute-force worst 1.18e-15)",
    }, "facts": {}, "timing": {}, "corr": {}, "coverage": {}}

    idx, syms, meta = P1C.load_universe()

    def _load(field, ffill=False):
        mm = np.load(os.path.join(CACHE_DIR, field + ".npy"), mmap_mode="r")
        arr = np.asarray(mm, dtype=np.float64)
        df = pd.DataFrame(arr, index=idx, columns=syms)
        if ffill:
            df = df.ffill()
        del mm, arr
        return df

    close = _load("close", ffill=True)
    open_ = _load("open", ffill=True)
    # turnover: the cache column is all-NaN except the final bar
    # (TURNOVER_DERIVATION.md) -> consume the r219 derived sidecar
    # (board-split frozen formula, 5-symbol reconciliation gated)
    tr_side = os.path.join(CACHE_DIR, "turnover_derived.npy")
    tr_meta_p = os.path.join(CACHE_DIR, "turnover_derived.meta.json")
    assert os.path.exists(tr_side) and os.path.exists(tr_meta_p), \
        "turnover_derived sidecar missing - run scripts/p1e_turnover_derive.py"
    tr_prov = json.load(open(tr_meta_p, encoding="utf-8"))
    assert tr_prov["shape"]["T"] == len(idx) and \
        tr_prov["shape"]["N"] == len(syms), "sidecar shape mismatch"
    tr_raw = _load("turnover_derived")
    rep["facts"]["turnover_source"] = {
        "sidecar": "Money02/data/cache/p1c_stock/turnover_derived.npy",
        "formula": tr_prov["formula"],
        "generated": tr_prov["generated"],
        "gates": tr_prov["gates"]["finalbar_recon"] is not None,
    }
    vwap = _load("vwap")
    pct_chg = _load("pct_chg")
    print(f"  primary panels loaded incl derived turnover "
          f"({time.strftime('%H:%M:%S')})", flush=True)

    rets = close / close.shift(1) - 1.0

    # --- face fact: turnover unit convention (derived panel is fraction)
    trv = tr_raw.values
    trv_finite = trv[np.isfinite(trv)]
    pcts = np.percentile(trv_finite, [1, 25, 50, 75, 99])
    tr_frac = tr_raw / 100.0 if pcts[2] > 3.0 else tr_raw
    rep["facts"]["turnover_unit"] = {
        "percentiles_1_25_50_75_99": [round(float(x), 4) for x in pcts],
        "convention": "percent -> /100 to fraction"
        if tr_frac is not tr_raw else "already fraction",
        "share_gt_1_raw": round(float((trv_finite > 1.0).mean()), 6),
    }
    # --- face fact: bars pct_chg is a PERCENT-scale column (source display
    # rounding 4dp); the batch freezes close-based fraction returns
    # (harness-consistent with fwd_rets); agreement reported after /100
    both = rets.notna() & pct_chg.notna()
    dd = (rets - pct_chg / 100.0).where(both).abs()
    rep["facts"]["bars_pctchg_unit"] = {
        "unit": "percent (p99 |value| ~ 9.99 = A-share limit cap)",
        "n_overlap_cells": int(both.sum().sum()),
        "share_agree_gt_1e_4_after_div100": round(
            float((dd <= 1e-4).sum().sum() / max(1, int(both.sum().sum()))), 6),
        "share_disagree_after_div100": round(
            float((dd > 1e-4).sum().sum() / max(1, int(both.sum().sum()))), 6),
        "note": "residual disagreement = suspension-gap days where the "
                "ffilled close ratio spans multiple sessions (single-day "
                "pct_chg cannot match); close-based is the frozen "
                "convention, pct_chg not consumed by the batch",
    }
    del pct_chg, trv, trv_finite, dd, both

    # --- zoo factor construction with timing
    zoo = {}
    t0 = time.time()
    zoo["zoo85_terrified"] = build_zoo85_terrified(rets)
    rep["timing"]["zoo85_terrified_s"] = round(time.time() - t0, 1)
    print(f"  zoo85_terrified {rep['timing']['zoo85_terrified_s']}s",
          flush=True)

    t0 = time.time()
    zoo["zoo85_stv"] = build_zoo85_stv(rets, tr_frac)
    rep["timing"]["zoo85_stv_s"] = round(time.time() - t0, 1)
    print(f"  zoo85_stv {rep['timing']['zoo85_stv_s']}s", flush=True)

    t0 = time.time()
    zoo["zoo92_coin_team"] = build_zoo92_coin_team(close, open_, tr_frac)
    rep["timing"]["zoo92_coin_team_s"] = round(time.time() - t0, 1)
    print(f"  zoo92_coin_team {rep['timing']['zoo92_coin_team_s']}s",
          flush=True)

    t0 = time.time()
    fam, n_bad = build_zoo93_arc_family(tr_frac, vwap, close)
    rep["timing"]["zoo93_arc_family_s"] = round(time.time() - t0, 1)
    rep["facts"]["zoo93_nonfinite_arc_cells"] = n_bad
    zoo.update(fam)
    print(f"  zoo93 family {rep['timing']['zoo93_arc_family_s']}s "
          f"(non-finite arc cells {n_bad})", flush=True)
    rep["facts"]["zoo93_estimate_recheck"] = {
        "freeze_card_claim": "~7.5e8 simple ops, numpy vectorized "
        "minutes-level; naive upper bound qlib 200-300min",
        "measured_wall_s": rep["timing"]["zoo93_arc_family_s"],
        "T_x_N": list(close.shape),
        "window_count_scale": int(np.prod(close.shape)),
        "note": "cumsum-factorized O(T*N) per power j (5 powers + validity)",
    }
    del open_, vwap, tr_raw, tr_frac, rets

    # --- GTJA named neighbors on the full vendor panel dict
    t0 = time.time()
    panels = {"close": close}
    for f in ("open", "high", "low", "volume", "amount", "turnover", "vwap"):
        panels[f] = _load(f, ffill=(f in ("open", "high", "low")))
    mod = P1C.load_alpha191_bigpanel()
    gtja = {}
    for nm in GTJA_NEIGHBORS:
        tc = time.time()
        gtja[nm] = getattr(mod, nm)(panels)
        rep["timing"][nm + "_s"] = round(time.time() - tc, 1)
        print(f"  {nm} {rep['timing'][nm + '_s']}s", flush=True)
    rep["timing"]["gtja_stage_s"] = round(time.time() - t0, 1)
    del panels

    # --- coverage (IS only) + corr pre-check (IS only, OOS untouched)
    is_rows = close.index <= IS_END
    allf = dict(zoo)
    allf.update(gtja)
    for nm, fdf in allf.items():
        fis = fdf.loc[is_rows]
        n_is = int(fis.notna().sum().sum())
        rep["coverage"][nm] = {
            "is_valid_cells": n_is,
            "is_valid_cell_share": round(n_is / float(np.prod(fis.shape)), 4),
        }

    fwd10 = close.shift(-10) / close - 1.0
    mains = ["zoo85_terrified", "zoo85_stv", "zoo92_coin_team", "zoo93_arc"]

    ic_is = {}
    for nm in mains:
        s = _ic_series_fast(zoo[nm], fwd10)
        ic_is[nm] = s[s.index <= IS_END]
        rep["coverage"][nm]["is_ic_periods"] = int(len(ic_is[nm]))

    pairs = [(mains[i], mains[j])
             for i in range(len(mains)) for j in range(i + 1, len(mains))]
    pairs += [("zoo93_arc", v) for v in ("zoo93_vrc", "zoo93_src",
                                         "zoo93_krc")]
    pairs += [(m, g) for m in mains for g in GTJA_NEIGHBORS]
    for a, b in pairs:
        t0 = time.time()
        sp = _xs_spearman_series(allf[a].loc[is_rows],
                                 allf[b].loc[is_rows])
        rep["corr"][f"{a}|{b}"] = {
            "xs_spearman_mean": round(float(sp.mean()), 4)
            if len(sp) else None,
            "n_dates": int(len(sp)),
        }
        print(f"  corr {a}|{b} -> "
              f"{rep['corr'][f'{a}|{b}']['xs_spearman_mean']} "
              f"({time.time() - t0:.0f}s)", flush=True)

    for i in range(len(mains)):
        for j in range(i + 1, len(mains)):
            a, b = mains[i], mains[j]
            s1, s2 = ic_is[a], ic_is[b]
            common = s1.index.intersection(s2.index)
            if len(common) > 30:
                c = float(np.corrcoef(s1[common].values,
                                      s2[common].values)[0, 1])
                rep["corr"][f"ic10_series|{a}|{b}"] = {
                    "pearson": round(c, 4), "n_common": int(len(common))}

    rep["facts"]["peak_ram_gb"] = P1C._peak_ram_gb()
    rep["meta"]["elapsed_s"] = round(time.time() - t_all, 1)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2, ensure_ascii=False)
    print(f"saved: {OUT_JSON} (elapsed {rep['meta']['elapsed_s']}s, "
          f"peak {rep['facts']['peak_ram_gb']}GB)", flush=True)
    print("turnover:", rep["facts"]["turnover_unit"]["convention"])
    for k, v in rep["corr"].items():
        print(f"  {k}: "
              f"{v['pearson'] if k.startswith('ic10') else v['xs_spearman_mean']}")


if __name__ == "__main__":
    main()
