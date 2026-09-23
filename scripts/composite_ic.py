"""J6 composite factor IC validation.

Composite = 0.3*(-z(vol_60)) + 0.3*(-z(intraday_range))
          + 0.2*z(mom_12_1)  + 0.2*z(price_position)

Each component is cross-sectionally z-scored per date before weighting
(rank IC is scale-invariant per component, but z-scoring is required
for a *weighted sum* to be well-defined).

Universes:
  core = bare-code CSVs in data/daily (the original 48-ETF research pool,
         matches smoke_test "no-prefix" definition). Gates evaluated HERE.
  all  = core + prefixed (sh/sz) files, deduped by numeric code (bare
         wins over prefixed duplicate). Info-only robustness check; the
         expanded pool is J9 territory and not gate-worthy yet.

Split per PLAN §4.3: IS = dates <= 2024-12-31, OOS = dates >= 2025-01-01.

Pass gates (on core universe, h20 composite):
  G1 |IC_h20| > 0.06   (>= best single factor vol_60's 0.064)
  G2 IC_IR_h20 > 0.3
  G3 OOS IC same sign as IS and |IC| decay < 30%
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from config import PATHS
from engine.factors import FACTORS

WEIGHTS = {
    "vol_60": -0.3,
    "intraday_range": -0.3,
    "mom_12_1": +0.2,
    "price_position": +0.2,
}
HORIZONS = [5, 10, 20]
IS_END = "2024-12-31"   # OOS starts 2025-01-01


def load_universe(mode: str, min_listing_days: int = 60) -> dict:
    """mode 'core': bare-code CSVs only. 'all': dedup by numeric code, bare wins."""
    out = {}
    daily = PATHS.daily_dir
    # bare files first so they win dedup
    files = sorted(os.listdir(daily))
    bare = [f for f in files if f.endswith(".csv") and f[:-4].isdigit()]
    if mode == "core":
        chosen = bare
    else:
        prefixed = {}
        for f in files:
            if not f.endswith(".csv"):
                continue
            code = f[:-4]
            if code.isdigit():
                continue
            num = code.lstrip("abcdefghijklmnopqrstuvwxyz")
            prefixed.setdefault(num, f)
        chosen = bare + [f for num, f in prefixed.items() if num not in
                         {b[:-4] for b in bare}]
    for f in chosen:
        df = pd.read_csv(os.path.join(daily, f), parse_dates=["date"])
        df = df.set_index("date").sort_index()
        if len(df) < min_listing_days:
            continue
        if "open" not in df.columns:
            df["open"] = df["close"]
        out[f[:-4]] = df[["open", "high", "low", "close", "volume"]].copy()
    return out


def ic_series(factor: pd.DataFrame, fwd_ret: pd.DataFrame) -> pd.Series:
    """Cross-sectional Spearman IC per date (same method as factor_ic.py)."""
    common = factor.index.intersection(fwd_ret.index)
    ics = []
    for dt in common:
        f = factor.loc[dt].dropna()
        r = fwd_ret.loc[dt].dropna()
        both = f.index.intersection(r.index)
        if len(both) < 5:
            continue
        ic, _ = spearmanr(f[both], r[both])
        if not np.isnan(ic):
            ics.append((dt, ic))
    return pd.Series(dict(ics)).sort_index()


def xs_zscore(df: pd.DataFrame, min_n: int = 5) -> pd.DataFrame:
    """Cross-sectional z-score per date; dates with < min_n valid rows -> NaN."""
    mu = df.mean(axis=1)
    sd = df.std(axis=1, ddof=0)
    valid = df.notna().sum(axis=1) >= min_n
    z = df.sub(mu, axis=0).div(sd.replace(0, np.nan), axis=0)
    z[~valid] = np.nan
    return z


def stats_block(s: pd.Series) -> dict:
    if len(s) < 30:
        return {"n_periods": int(len(s)), "skip": "insufficient periods"}
    sd = s.std()
    return {
        "ic_mean": round(float(s.mean()), 4),
        "ic_std": round(float(sd), 4),
        "ic_ir": round(float(s.mean() / sd), 3) if sd > 0 else 0,
        "ic_pos_pct": round(float((s > 0).mean()), 3),
        "n_periods": int(len(s)),
    }


def run_universe(prices: dict) -> dict:
    panel = {f: pd.DataFrame({sym: p[f] for sym, p in prices.items()})
             .sort_index().ffill()
             for f in ["high", "low", "close"]}
    d = {"high": panel["high"], "low": panel["low"], "close": panel["close"]}
    comps = {name: FACTORS[name](d) for name in WEIGHTS}
    z = {name: xs_zscore(c) for name, c in comps.items()}
    composite = None
    for name, w in WEIGHTS.items():
        composite = w * z[name] if composite is None else composite + w * z[name]

    close = panel["close"]
    res = {"n_syms": len(prices), "horizons": {}}
    for h in HORIZONS:
        fwd = close.shift(-h) / close - 1
        hres = {"composite": {}, "components": {}}
        for name, fac in [("composite", composite)] + list(z.items()):
            s_all = ic_series(fac, fwd)
            blk = {"full": stats_block(s_all),
                   "is": stats_block(s_all[s_all.index <= IS_END]),
                   "oos": stats_block(s_all[s_all.index > IS_END])}
            if name == "composite" and "ic_mean" in blk["is"] and "ic_mean" in blk["oos"]:
                is_ic, oos_ic = blk["is"]["ic_mean"], blk["oos"]["ic_mean"]
                blk["same_sign_is_oos"] = bool((is_ic > 0) == (oos_ic > 0))
                decay = (1 - abs(oos_ic) / abs(is_ic)) if is_ic != 0 else 1.0
                blk["ic_decay_pct"] = round(float(max(0.0, decay)), 3)
            if name == "composite":
                hres["composite"] = blk
            else:
                hres["components"][name] = blk
        c_full = hres["composite"]["full"]
        gate = {
            "g1_abs_ic_gt_006": bool(abs(c_full.get("ic_mean", 0)) > 0.06),
            "g2_ic_ir_gt_03": bool(c_full.get("ic_ir", 0) > 0.3),
            "g3_oos_stable": bool(
                hres["composite"].get("same_sign_is_oos", False)
                and hres["composite"].get("ic_decay_pct", 1.0) < 0.30),
        }
        gate["pass"] = bool(all(gate.values()))
        hres["gates"] = gate
        res["horizons"][f"h{h}"] = hres
    return res


def main():
    out = {"weights": WEIGHTS, "is_end": IS_END}

    print("loading core universe (bare-code files)...")
    core = load_universe("core")
    print(f"  {len(core)} ETFs")
    out["core"] = run_universe(core)

    print("loading all universe (deduped)...")
    allu = load_universe("all")
    print(f"  {len(allu)} ETFs (deduped)")
    out["all_universe_info_only"] = run_universe(allu)

    for uni_name, uni in [("CORE (gates)", out["core"]),
                          ("ALL deduped (info)", out["all_universe_info_only"])]:
        print(f"\n===== {uni_name} | n_syms={uni['n_syms']} =====")
        print(f"{'factor':<18} {'seg':<5} {'IC':>8} {'IR':>7} {'pos%':>6} {'n':>5}")
        for h in HORIZONS:
            hres = uni["horizons"][f"h{h}"]
            print(f"--- horizon {h}d ---")
            for name, blk in [("composite", hres["composite"])] + \
                    [(k, v) for k, v in hres["components"].items()]:
                for seg in ["full", "is", "oos"]:
                    b = blk[seg]
                    if "ic_mean" in b:
                        print(f"{name:<18} {seg:<5} {b['ic_mean']:>8.4f} "
                              f"{b['ic_ir']:>7.3f} {b['ic_pos_pct']:>6.2f} "
                              f"{b['n_periods']:>5}")
            g = hres["gates"]
            print(f"  gates: G1={g['g1_abs_ic_gt_006']} G2={g['g2_ic_ir_gt_03']} "
                  f"G3={g['g3_oos_stable']} -> {'PASS' if g['pass'] else 'FAIL'}")

    out_path = os.path.join(PATHS.results_dir, "composite_ic.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    verdict = out["core"]["horizons"]["h20"]["gates"]["pass"]
    print(f"\nsaved: {out_path}")
    print(f"verdict core h20: {'PASS' if verdict else 'FAIL'}")


if __name__ == "__main__":
    main()
