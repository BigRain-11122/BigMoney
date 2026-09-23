"""P-1a GTJA191 factor IC screen (preregistered: research/shortline/P1_FACTOR_SCREEN.md).

Run:  python research/shortline/screening/p1_factor_screen.py [--selftest]

Universe core48 (bare-code CSVs, same semantics as scripts/composite_ic.py),
IS <= 2024-12-31, OOS >= 2025-01-01, cross-sectional Spearman IC (same
ic_series as composite_ic), horizons 5/10/20 with h10 primary. Nulls = 50
iid N(0,1) panels through the same pipeline (seed 20260923). Gates V1-V3 per
prereg §3. One shot: no post-run threshold edits, no reruns.
"""
import os, sys, json, time, types, warnings, importlib.util

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, _ROOT)
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from config import PATHS
import gtja191_ops as ops

EXTERNAL = os.path.join(_ROOT, "research", "shortline", "external")
IS_END = "2024-12-31"
HORIZONS = [5, 10, 20]
PRIMARY = 10
N_NULLS = 50
NULL_SEED = 20260923
LEDGER_PREV = 1073          # N=1073 per round-18 ledger (CODELY.md)
STATIC_EXCLUDED = {"alpha191_030", "alpha191_143"}   # unfinished=True in source
IC_FLOOR = 0.02
IR_FLOOR = 0.30
OOS_DECAY_MIN = 0.5         # |IC_OOS| >= 0.5 * |IC_IS|


# ---------------------------------------------------------------- universe
def load_core48() -> dict:
    daily = PATHS.daily_dir
    files = sorted(os.listdir(daily))
    bare = [f for f in files if f.endswith(".csv") and f[:-4].isdigit()]
    out = {}
    for f in bare:
        df = pd.read_csv(os.path.join(daily, f), parse_dates=["date"])
        df = df.set_index("date").sort_index()
        if len(df) < 60:
            continue
        out[f[:-4]] = df[["open", "high", "low", "close", "volume", "amount"]].copy()
    return out


def build_panels(univ: dict) -> dict:
    keys = ["open", "high", "low", "close", "volume", "amount"]
    panels = {k: pd.DataFrame({s: d[k] for s, d in univ.items()}).sort_index() for k in keys}
    vol = panels["volume"].where(panels["volume"] > 0)
    panels["vwap"] = panels["amount"] / vol
    return panels


def forward_returns(close: pd.DataFrame) -> dict:
    return {h: close.shift(-h) / close - 1 for h in HORIZONS}


# ---------------------------------------------------------------- IC (same estimator as composite_ic)
def ic_series(factor: pd.DataFrame, fwd_ret: pd.DataFrame) -> pd.Series:
    """Per-date cross-sectional Spearman IC, vectorized (= Pearson on average-ties
    ranks, identical estimator to the scipy.spearmanr loop in composite_ic;
    equivalence asserted in selftest S6b). Rows with <5 valid pairs or constant
    cross-section are skipped, matching composite_ic semantics."""
    common = factor.index.intersection(fwd_ret.index)
    if len(common) == 0:
        return pd.Series(dtype=float)
    f = factor.loc[common]
    r = fwd_ret.loc[common]
    valid = f.notna() & r.notna()
    n = valid.sum(axis=1)
    fr = f.where(valid).rank(axis=1)          # rank within valid pairs only (scipy semantics)
    rr = r.where(valid).rank(axis=1)
    mf = fr.mean(axis=1)
    mr = rr.mean(axis=1)
    fd = fr.sub(mf, axis=0)
    rd = rr.sub(mr, axis=0)
    cov = (fd * rd).mean(axis=1)
    sf = np.sqrt((fd * fd).mean(axis=1))
    sr = np.sqrt((rd * rd).mean(axis=1))
    corr = cov / (sf * sr)
    ok = (n >= 5) & np.isfinite(corr) & (corr.abs() <= 1 + 1e-12)
    return corr[ok]


def ic_series_scipy(factor: pd.DataFrame, fwd_ret: pd.DataFrame) -> pd.Series:
    """Reference loop (composite_ic verbatim); selftest-only equivalence anchor."""
    common = factor.index.intersection(fwd_ret.index)
    ics = []
    f_loc = factor.loc[common]
    r_loc = fwd_ret.loc[common]
    for dt in f_loc.index:
        f = f_loc.loc[dt].dropna()
        if len(f) < 5:
            continue
        r = r_loc.loc[dt].dropna()
        both = f.index.intersection(r.index)
        if len(both) < 5:
            continue
        ic, _ = spearmanr(f[both], r[both])
        if not np.isnan(ic):
            ics.append((dt, ic))
    return pd.Series(dict(ics)).sort_index()


def seg_stats(s: pd.Series, is_end: str = IS_END) -> dict:
    is_s = s[s.index <= is_end]
    oos_s = s[s.index > is_end]
    def blk(x):
        if len(x) < 30:
            return {"n": int(len(x)), "mean": np.nan, "std": np.nan, "ir": np.nan, "pos_pct": np.nan}
        sd = x.std()
        return {"n": int(len(x)), "mean": round(float(x.mean()), 4), "std": round(float(sd), 4),
                "ir": round(float(x.mean() / sd), 3) if sd > 0 else 0.0,
                "pos_pct": round(float((x > 0).mean()), 3)}
    return {"is": blk(is_s), "oos": blk(oos_s)}


# ---------------------------------------------------------------- alpha191 loading
def _exec_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_alpha191():
    for pkg in ["lib", "lib.ops", "lib.utils"]:
        m = types.ModuleType(pkg)
        m.__path__ = []
        sys.modules[pkg] = m
    _exec_module(os.path.join(EXTERNAL, "gtja191_lib_base.py"), "lib.base")
    _exec_module(os.path.join(EXTERNAL, "gtja191_lib_method_attrs.py"), "lib.utils.method_attrs")
    sys.modules["lib.ops.factor_ops"] = ops          # clean-room ops under expected import name
    buf = sys.stdout
    sys.stdout = types.SimpleNamespace(write=lambda *a: None, flush=lambda *a: None)  # swallow qlib ImportError print
    try:
        alpha191 = _exec_module(os.path.join(EXTERNAL, "gtja191_alpha191.py"), "gtja191_alpha191")
    finally:
        sys.stdout = buf
    for name in ["MIN", "REGRESI", "WMA", "rolling_slope", "rolling_rsquare"]:
        setattr(alpha191, name, getattr(ops, name))
    return alpha191


# ---------------------------------------------------------------- selftests (prereg §4)
def run_selftests(panels=None, univ=None) -> bool:
    rng = np.random.default_rng(7)
    # S1 SMA anchor == ewm(alpha=m/n) + na_map (vendored semantics)
    df = pd.DataFrame(rng.normal(size=(30, 3)))
    df.iloc[3, 0] = np.nan
    ref = df.ewm(alpha=1 / 5, ignore_na=True).mean() + df.isna().astype(float).replace(1., np.nan)
    pd.testing.assert_frame_equal(ops.SMA(df, 5, 1), ref)
    # S2 DECAYLINEAR manual window
    a = pd.DataFrame({"x": [1.0, 2.0, 3.0]})
    d = ops.DECAYLINEAR(a, 2)
    assert abs(d["x"].iloc[1] - (1 * (2 * 1 / 6) + 2 * (2 * 2 / 6))) < 1e-12
    assert abs(d["x"].iloc[2] - (2 * (2 * 1 / 6) + 3 * (2 * 2 / 6))) < 1e-12
    assert abs(sum([2 * i / (3 * 4) for i in range(1, 4)]) - 1.0) < 1e-12  # weights sum=1
    # S3 HIGHDAY semantics: days since N-day max
    A = pd.DataFrame({"x": [3.0, 1.0, 2.0, 5.0, 4.0]})
    h = ops.HIGHDAY(A, 3)["x"]
    assert np.isnan(h.iloc[0]) and np.isnan(h.iloc[1])
    assert h.iloc[2] == 2 and h.iloc[3] == 0 and h.iloc[4] == 1
    # S4 rolling_slope == np.polyfit slope
    x = pd.DataFrame({"x": rng.normal(size=30)})
    rs = ops.rolling_slope(x, 7)["x"]
    for t in range(6, 30):
        pf = np.polyfit(np.arange(7.0), x["x"].values[t - 6:t + 1], 1)[0]
        assert abs(rs.iloc[t] - pf) < 1e-9
    # S5 alpha191_002 hand replication on synthetic OHLC panel
    n_sym, n_day = 2, 6
    o = pd.DataFrame(rng.uniform(10, 11, (n_day, n_sym)), columns=["s1", "s2"])
    c = o + rng.uniform(-0.2, 0.2, (n_day, n_sym))
    h_ = c + np.abs(rng.uniform(0, 0.3, (n_day, n_sym)))
    l_ = c - np.abs(rng.uniform(0, 0.3, (n_day, n_sym)))
    data = {"open": o, "high": h_, "low": l_, "close": c,
            "volume": pd.DataFrame(rng.uniform(1e6, 2e6, (n_day, n_sym)), columns=["s1", "s2"]),
            "amount": pd.DataFrame(rng.uniform(1e7, 2e7, (n_day, n_sym)), columns=["s1", "s2"]),
            "vwap": (pd.DataFrame(rng.uniform(1e7, 2e7, (n_day, n_sym)), columns=["s1", "s2"])
                     / pd.DataFrame(rng.uniform(1e6, 2e6, (n_day, n_sym)), columns=["s1", "s2"]))}
    alpha191 = load_alpha191()
    got = alpha191.alpha191_002(data)
    hand = -((((c - l_) - (h_ - c)) / (h_ - l_)).diff(1))
    pd.testing.assert_frame_equal(got, hand)
    # S6 IC pipeline monotonic anchor (dates inside real IS range per P3 lesson)
    #    6 symbols (not 3: ic_series enforces min-5 cross-section, company convention)
    dates = pd.bdate_range("2021-01-04", periods=40)
    rets = [0.001, 0.002, 0.003, 0.004, 0.005, 0.006]
    px = pd.DataFrame({f"s{i}": 100.0 * np.power(1 + r, np.arange(1, 41)) for i, r in enumerate(rets)}, index=dates)
    fwd10 = px.shift(-10) / px - 1
    ics = ic_series(px, fwd10)
    assert len(ics) == 30 and abs(ics.mean() - 1.0) < 1e-9
    # S6b vectorized IC == composite_ic scipy loop (equivalence anchor, NaN+ties panel)
    dts2 = pd.bdate_range("2021-01-04", periods=120)
    cols = [f"e{i}" for i in range(12)]
    f2 = pd.DataFrame(rng.normal(size=(120, 12)), index=dts2, columns=cols)
    r2 = pd.DataFrame(rng.normal(size=(120, 12)), index=dts2, columns=cols)
    f2.iloc[10, 2] = np.nan
    f2.iloc[80, 4] = np.nan
    r2.iloc[5, 7] = np.nan
    f2.iloc[20, 0] = f2.iloc[20, 1]          # ties -> average ranks
    va, vb = ic_series(f2, r2), ic_series_scipy(f2, r2)
    assert va.index.equals(vb.index), "equivalence: index mismatch"
    assert np.allclose(va.values, vb.values, atol=1e-9), "equivalence: value mismatch"
    # S7 random-walk null sanity |mean IC| < 0.3 on 48 syms x 200 days
    dts = pd.bdate_range("2021-01-04", periods=200)
    walk = pd.DataFrame(rng.normal(size=(200, 48)), index=dts)
    walk = (1 + walk * 0.01).cumprod()
    icn = ic_series(walk, walk.shift(-10) / walk - 1)
    assert abs(icn.mean()) < 0.3
    # S8 universe anchor
    if univ is None:
        univ = load_core48()
    assert len(univ) == 48, f"universe={len(univ)} != 48"
    assert "510300" in univ
    assert all("amount" in d.columns and d["amount"].notna().any() for d in univ.values())
    print("[selftest] 9/9 PASS (ops anchors + alpha002 hand-replication + IC pipeline + vectorized==scipy equivalence + universe)")
    return True


# ---------------------------------------------------------------- batch
def run_batch():
    t0 = time.time()
    univ = load_core48()
    panels = build_panels(univ)
    close = panels["close"]
    fwd = forward_returns(close)
    alpha191 = load_alpha191()

    names = sorted(n for n in dir(alpha191)
                   if n.startswith("alpha191_") and n[-3:].isdigit() and callable(getattr(alpha191, n)))
    run_names = [n for n in names if n not in STATIC_EXCLUDED
                 and not getattr(getattr(alpha191, n), "unfinished", False)]
    print(f"[batch] universe={len(univ)} alphas total={len(names)} static-excluded={len(names)-len(run_names)} run={len(run_names)}")

    rows, errors = [], {}
    null_t0 = time.time()
    for i, name in enumerate(run_names):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                fn = getattr(alpha191, name)
                panel = fn({k: panels[k] for k in ["open", "high", "low", "close", "volume", "amount", "vwap"]})
            if not isinstance(panel, pd.DataFrame):
                raise TypeError(f"return {type(panel).__name__} not DataFrame")
            panel = panel.reindex(index=close.index, columns=close.columns)
            row = {"alpha": name, "ret_type": getattr(fn, "return_type", "")}
            ics = {}
            for h in HORIZONS:
                s = ic_series(panel, fwd[h])
                ics[h] = s
                st = seg_stats(s)
                for seg in ["is", "oos"]:
                    for k, v in st[seg].items():
                        row[f"ic_{seg}_h{h}_{k}"] = v
            covered = panel.notna().sum(axis=1)
            row["coverage_days"] = int((covered >= 5).sum())
            is_m = row["ic_is_h10_mean"]
            oos_m = row["ic_oos_h10_mean"]
            is_ir = row["ic_is_h10_ir"]
            row["_is_abs_mean"] = abs(is_m) if np.isfinite(is_m) else np.nan
            row["_is_ir"] = is_ir
            row["_is_mean"] = is_m
            row["_oos_mean"] = oos_m
            rows.append(row)
        except Exception as e:  # noqa: BLE001  # excluded-with-error per prereg §1, no retry
            errors[name] = f"{type(e).__name__}: {e}"
        if (i + 1) % 25 == 0:
            print(f"[batch] {i+1}/{len(run_names)} elapsed={time.time()-null_t0:.0f}s errors={len(errors)}")

    # nulls: 50 iid panels through same pipeline (h10 primary)
    rng = np.random.default_rng(NULL_SEED)
    null_is_means = []
    for j in range(N_NULLS):
        panel = pd.DataFrame(rng.normal(size=close.shape), index=close.index, columns=close.columns)
        s = ic_series(panel, fwd[PRIMARY])
        is_s = s[s.index <= IS_END]
        if len(is_s) >= 30:
            null_is_means.append(float(is_s.mean()))
    null_abs = np.abs(np.array(null_is_means))
    null_p95 = float(np.quantile(null_abs, 0.95)) if len(null_abs) else 0.0
    null_p99 = float(np.quantile(null_abs, 0.99)) if len(null_abs) else 0.0
    v1_bar = max(IC_FLOOR, null_p95)
    print(f"[null] n={len(null_abs)} p95={null_p95:.4f} p99={null_p99:.4f} v1_bar={v1_bar:.4f}")

    for row in rows:
        is_m, oos_m = row.pop("_is_mean"), row.pop("_oos_mean")
        is_abs, is_ir = row.pop("_is_abs_mean"), row.pop("_is_ir")
        row["v1_bar"] = round(v1_bar, 4)
        row["v1"] = bool(np.isfinite(is_abs) and is_abs > v1_bar)
        row["v2"] = bool(np.isfinite(is_ir) and is_ir >= IR_FLOOR)
        row["v3"] = bool(np.isfinite(is_m) and np.isfinite(oos_m)
                         and np.sign(oos_m) == np.sign(is_m)
                         and abs(oos_m) >= OOS_DECAY_MIN * abs(is_m))
        row["pass"] = bool(row["v1"] and row["v2"] and row["v3"])
        row["direction"] = "+" if (np.isfinite(is_m) and is_m > 0) else "-"

    df = pd.DataFrame(rows).sort_values("ic_is_h10_mean", key=lambda s: s.abs(), ascending=False)
    out_csv = os.path.join(_ROOT, "research", "shortline", "p1_factor_ic.csv")
    df.to_csv(out_csv, index=False)

    survivors = df[df["pass"] == True]  # noqa: E712
    survivors = survivors.sort_values("ic_is_h10_mean", key=lambda s: s.abs(), ascending=False)
    ledger = {"prev_total": LEDGER_PREV,
              "batch_trials": len(run_names) + len(null_is_means),
              "total": LEDGER_PREV + len(run_names) + len(null_is_means)}
    payload = {
        "batch": "P1a-gtja191-factor-screen",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/shortline/P1_FACTOR_SCREEN.md (written before run)",
        "universe": {"pool": "core48-bare", "n": len(univ), "min_listing_days": 60,
                     "oos_start": "2025-01-01", "member_cutoff": str(close.index.max().date())},
        "horizons": HORIZONS, "primary": PRIMARY,
        "static_excluded": sorted(STATIC_EXCLUDED),
        "runtime_errors": errors,
        "null": {"n": int(len(null_abs)), "p95": round(null_p95, 4), "p99": round(null_p99, 4),
                 "seed": NULL_SEED},
        "gate_bars": {"v1_bar": round(v1_bar, 4), "v2_ir_min": IR_FLOOR, "v3_oos_retention_min": OOS_DECAY_MIN},
        "n_run": len(run_names), "n_computed": len(rows), "n_errors": len(errors),
        "n_pass": int(len(survivors)),
        "survivors": survivors[["alpha", "direction", "ic_is_h10_mean", "ic_is_h10_ir",
                                "ic_oos_h10_mean", "ic_oos_h10_ir", "coverage_days"]].to_dict("records"),
        "top20_is": df.head(20)[["alpha", "ic_is_h10_mean", "ic_is_h10_ir",
                                 "ic_oos_h10_mean", "pass"]].to_dict("records"),
        "ledger": ledger,
        "elapsed_sec": round(time.time() - t0, 1),
    }
    out_json = os.path.join(_ROOT, "results", "shortline_p1_factor.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    print(f"[done] computed={len(rows)} errors={len(errors)} pass={len(survivors)} "
          f"ledger N: {ledger['prev_total']}+{ledger['batch_trials']}={ledger['total']} elapsed={payload['elapsed_sec']}s")
    print("[survivors]")
    for r in payload["survivors"]:
        print(f"  {r['alpha']} dir={r['direction']} IS={r['ic_is_h10_mean']} IR={r['ic_is_h10_ir']} "
              f"OOS={r['ic_oos_h10_mean']} cover={r['coverage_days']}")
    if errors:
        print(f"[errors] {len(errors)}: " + "; ".join(f"{k}={v[:60]}" for k, v in list(errors.items())[:5]))
    return payload


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        run_selftests()
        sys.exit(0)
    run_selftests()
    run_batch()
