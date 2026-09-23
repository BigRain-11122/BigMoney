"""P-2 GTJA191 composite synthesis (preregistered: research/shortline/P2_GTJA191_SYNTH.md).

Run:  python -u research/shortline/screening/p2_gtja_synth.py

Recipe (all fixed before run, zero fitting):
  pool = bm-a in_pool 89 -> clean-room value panels (single implementation)
  -> orient by IS h10 IC sign (P-1a recorded constants)
  -> IS-segment Pearson corr on stacked oriented z -> complete-linkage
     hierarchical clustering, cut 1-corr <= 0.5
  -> representative per cluster = max IS |IC|; cap K_max=20 clusters
  -> composite = equal-weight mean of oriented rep z-panels (min_valid=min(3,K))
Factor gates h10: V1 vs nullA (random K from 183) + nullB (random K from 89)
n=50 each; V2 IR>=0.30; V3 OOS same-sign retention>=0.5.
Strategy G1': top-n in {3,5,8} rotation (20d rebal, 0.95/n sizing, engine
default exits, 13bp) + 20 random baselines (all-False exits, engine rules
only, same as P1); six clauses on recorded constants (i 0.352 / vi 0.4004).
Rail anchor: composite_top5 must reproduce strategy_rank.csv bit-exact
(0.4225/0.9727/707) else batch void.
G2 for survivors: neighborhood (n+/-1 @ rebal20, n @ rebal{10,40}) all green
+ OOS>=0.7284 + cost x2 survive (CostPatch self-test first, J10 lesson)
+ no crash year. One shot, no reruns.
"""
import os, sys, json, time, warnings

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))          # screening/
sys.path.insert(0, os.path.join(_ROOT, "scripts"))                       # ce_transfer

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

from config import PATHS
from p1_factor_screen import (IS_END, HORIZONS, run_selftests, load_alpha191,
                              load_core48, build_panels, ic_series, seg_stats)
from p1_strategy_screen import run_one as p1_run_one          # baselines (all-False exits)
import ce_transfer as ct
from strategies.composite_rotation import top_n_rotation

POOL_CSV = os.path.join(_ROOT, "research", "shortline", "gtja191_ic_results.csv")
MY_IC_CSV = os.path.join(_ROOT, "research", "shortline", "p1_factor_ic.csv")
T_CUT = 0.5                 # complete-linkage cut on distance = 1 - corr
K_MAX = 20                  # cluster cap
N_NULLS = 50                # per family (A and B)
NULL_SEED = 20260923
IC_FLOOR = 0.02
IR_FLOOR = 0.30
OOS_DECAY_MIN = 0.5
PRIMARY = 10
TOP_NS = (3, 5, 8)
REBAL = 20
N_BASELINES = 20
BASELINE_P = [0.02, 0.05]
MIN_TRADES = 30
MAX_DD = -0.35
I_BAR_EXP, VI_BAR_EXP, REF_OOS_EXP = 0.3521, 0.4004, 1.0405
ANCHOR_TOL = 0.002
DECAY_FLOOR = 0.70
CRASH_YEAR = -0.30
LEDGER_PREV = 1312          # after P-1a (+239), per P1_RECONCILIATION section 3

I_BAR = VI_BAR = None       # set from recorded constants in main


# ---------------------------------------------------------------- helpers
def xs_zscore(df: pd.DataFrame, min_n: int = 5) -> pd.DataFrame:
    mu = df.mean(axis=1)
    sd = df.std(axis=1, ddof=0)
    valid = df.notna().sum(axis=1) >= min_n
    z = df.sub(mu, axis=0).div(sd.replace(0, np.nan), axis=0)
    z[~valid] = np.nan
    return z


def zmean(mats: list, min_valid: int) -> pd.DataFrame:
    """Equal-weight per-date mean over oriented z-panels; <min_valid valid -> NaN."""
    arr = np.stack([m.values for m in mats])
    cnt = np.isfinite(arr).sum(axis=0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        mean = np.nanmean(arr, axis=0)
    mean[cnt < min_valid] = np.nan
    return pd.DataFrame(mean, index=mats[0].index, columns=mats[0].columns)


def cluster_oriented(z_is: dict) -> tuple:
    """Complete-linkage clustering on distance 1-corr (stacked date,symbol),
    cut at T_CUT. Returns (labels dict name->cluster_id, corr matrix)."""
    long_df = pd.DataFrame({n: z.stack() for n, z in z_is.items()})
    corr = long_df.corr()
    dist = (1.0 - corr).fillna(1.0)
    condensed = squareform(dist.values, checks=False)
    Z = linkage(condensed, method="complete")
    labels = fcluster(Z, t=T_CUT, criterion="distance")
    return {n: int(l) for n, l in zip(corr.index, labels)}, corr


def pick_reps(labels: dict, is_ic: dict) -> tuple:
    """Representative per cluster = max IS |IC|. Cap K_MAX by rep |IC|."""
    clusters = {}
    for n, c in labels.items():
        clusters.setdefault(c, []).append(n)
    reps = []
    for c, members in clusters.items():
        rep = max(members, key=lambda m: abs(is_ic[m]))
        reps.append((rep, abs(is_ic[rep]), sorted(members)))
    reps.sort(key=lambda t: t[1], reverse=True)
    kept = reps[:K_MAX]
    return [r[0] for r in kept], [{"rep": r[0], "rep_abs_is_ic": round(r[1], 4),
                                   "members": r[2]} for r in reps]


def rotation_from_score(score: pd.DataFrame, top_n: int, rebal_days: int = 20) -> pd.DataFrame:
    ranks = score.rank(axis=1, ascending=False)
    in_set = ranks <= top_n
    held = in_set.iloc[::rebal_days].reindex(in_set.index).ffill()
    return held.fillna(False).astype(int)


def g1_clauses(r) -> dict:
    f_, o_ = r["full"], r["oos"]
    return {
        "i_rand_bar": bool(f_["sharpe"] > I_BAR),
        "ii_ann_pos": bool(f_["annual_return"] > 0),
        "iii_dd_ok": bool(f_["max_drawdown"] >= MAX_DD),
        "iv_trades": bool(r["n_trades"] >= MIN_TRADES),
        "v_oos_double_pos": bool(o_["sharpe"] > 0 and o_["annual_return"] > 0),
        "vi_skill_bar": bool(f_["sharpe"] > VI_BAR),
    }


# ---------------------------------------------------------------- selftests (prereg section 8)
def run_selftests_gate() -> None:
    print("[selftest] p1_factor_screen 9/9 ...")
    run_selftests()                                   # gate 1 (asserts inside)
    rng = np.random.default_rng(11)
    idx = pd.bdate_range("2020-01-01", periods=300)
    # gate 2: two duplicate pairs + 1 independent -> 3 clusters, reps by |IC|
    def mkdf():
        return pd.DataFrame(rng.normal(size=(300, 10)), index=idx)
    a, d, c = mkdf(), mkdf(), mkdf()
    panels = {"f_a": a, "f_b": a.copy(), "f_c": c,
              "f_d": d, "f_e": d.copy()}    # pairs {a,b} {d,e} + lone c = 3 clusters
    z_is = {n: xs_zscore(p) for n, p in panels.items()}
    z_is = {n: z.loc[z.index <= "2020-08-31"] for n, z in z_is.items()}
    labels, _ = cluster_oriented(z_is)
    fake_ic = {"f_a": 0.05, "f_b": 0.08, "f_c": 0.03, "f_d": 0.06, "f_e": 0.02}
    reps, _ = pick_reps(labels, fake_ic)
    assert len(set(labels.values())) == 3, f"clusters={len(set(labels.values()))}"
    assert sorted(reps) == ["f_b", "f_c", "f_d"], f"reps={reps}"
    assert labels["f_a"] == labels["f_b"] and labels["f_d"] == labels["f_e"]
    # gate 3: recipe anchor -- monotonic panel x3 (one warmup-delayed) -> IC=+1
    rets = [0.001 * (i + 1) for i in range(6)]
    px = pd.DataFrame({f"s{i}": 100.0 * np.power(1 + r, np.arange(1, 301))
                       for i, r in enumerate(rets)}, index=idx)
    m1 = m2 = xs_zscore(px)
    m3 = xs_zscore(px)
    m3.iloc[:30] = np.nan                                   # warmup NaN head
    comp = zmean([m1, m2, m3], min_valid=3)                 # head dates die
    fwd10 = px.shift(-10) / px - 1
    ics = ic_series(comp, fwd10)
    assert len(ics) > 0 and abs(ics.mean() - 1.0) < 1e-9, f"recipe anchor ic={ics.mean()}"
    assert comp.iloc[:30].isna().all().all(), "min_valid gate not enforced"
    # gate 4: null recipe -- random composite through same pipeline, finite
    zpop = {f"g{i}": xs_zscore(pd.DataFrame(rng.normal(size=(300, 6)), index=idx,
                                            columns=px.columns))
            for i in range(10)}
    nz = zmean(list(zpop.values())[:3], min_valid=3)
    nic = ic_series(nz, px.shift(-10) / px - 1)
    assert len(nic) > 0 and np.isfinite(nic.mean())
    # gates 5+6 (recorded constants + rail anchor) run in main on real data
    print("[selftest] clustering semantics + recipe + null-recipe: PASS")


def load_constants() -> dict:
    with open(os.path.join(PATHS.results_dir, "p2_calibration.json"), encoding="utf-8") as fh:
        g = json.load(fh)["g1_prime_gate"]
    with open(os.path.join(PATHS.results_dir, "p2_survivors.json"), encoding="utf-8") as fh:
        ref = json.load(fh)["constants"]["ref_oos_composite"]
    assert abs(g["i_full_sharpe_gt"] - I_BAR_EXP) < 1e-9, f"i_bar={g['i_full_sharpe_gt']}"
    assert abs(g["vi_full_sharpe_gt"] - VI_BAR_EXP) < 1e-9, f"vi_bar={g['vi_full_sharpe_gt']}"
    assert abs(ref - REF_OOS_EXP) < 1e-9, f"ref_oos={ref}"
    return {"i_bar": g["i_full_sharpe_gt"], "vi_bar": g["vi_full_sharpe_gt"],
            "ref_oos": ref, "oos_bar": round(DECAY_FLOOR * ref, 4)}


# ---------------------------------------------------------------- main
def main():
    global I_BAR, VI_BAR
    t0 = time.time()
    print("=== P-2 GTJA191 composite synthesis (preregistered) ===")
    consts = load_constants()
    I_BAR, VI_BAR = consts["i_bar"], consts["vi_bar"]
    oos_bar = consts["oos_bar"]
    print(f"recorded constants: i>{I_BAR} vi>{VI_BAR} ref_oos={consts['ref_oos']} "
          f"oos_bar={oos_bar}")

    # ---- universe + factor panels (clean-room, single implementation)
    univ = load_core48()
    panels = build_panels(univ)
    close_f = panels["close"]
    fwd = {h: close_f.shift(-h) / close_f - 1 for h in HORIZONS}
    alpha191 = load_alpha191()
    my_ic = pd.read_csv(MY_IC_CSV)
    finite = my_ic[np.isfinite(my_ic["ic_is_h10_mean"])]
    is_ic = dict(zip(finite["alpha"], finite["ic_is_h10_mean"]))
    sign = {n: (1 if v > 0 else -1) for n, v in is_ic.items()}
    pool = pd.read_csv(POOL_CSV)
    pool89 = sorted(pool.loc[pool["in_pool"] == True, "factor"].tolist())   # noqa: E712
    assert len(pool89) == 89 and all(n in is_ic for n in pool89), "pool integrity"
    all_names = sorted(n for n in is_ic
                       if getattr(getattr(alpha191, n), "unfinished", False) is False)
    print(f"pool=89 (all oriented) computable-population={len(all_names)}")

    t1 = time.time()
    z_cache, errors, sanitized = {}, {}, []

    def sanitize(panel: pd.DataFrame, name: str) -> pd.DataFrame:
        """Uniform value hygiene (batch-wide, zero gate impact): object/int
        dtypes coerced to float64 (numeric), +/-inf -> NaN."""
        p = panel.apply(pd.to_numeric, errors="coerce").astype("float64")
        p = p.replace([np.inf, -np.inf], np.nan)
        if not p.equals(panel):
            sanitized.append(name)
        return p

    for i, name in enumerate(all_names):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                fn = getattr(alpha191, name)
                panel = fn({k: panels[k] for k in
                            ["open", "high", "low", "close", "volume", "amount", "vwap"]})
            if not isinstance(panel, pd.DataFrame):
                raise TypeError("non-DataFrame return")
            panel = sanitize(panel.reindex(index=close_f.index, columns=close_f.columns),
                             name)
            z_cache[name] = xs_zscore(panel) * sign[name]
        except Exception as e:  # noqa: BLE001 -- excluded-with-error, no retry
            errors[name] = f"{type(e).__name__}: {e}"
        if (i + 1) % 50 == 0:
            print(f"  panels {i+1}/{len(all_names)} errors={len(errors)} "
                  f"({time.time()-t1:.0f}s)")
    n_ok = len(z_cache)
    assert n_ok >= 170, f"determinism guard: only {n_ok} panels (P-1a had 183)"
    print(f"panels computed={n_ok} errors={len(errors)} sanitized={len(sanitized)} "
          f"({time.time()-t1:.0f}s)")
    if sanitized:
        print(f"  sanitized (dtype/inf hygiene): {', '.join(sanitized)}")

    # ---- clustering (IS segment only)
    z_is = {n: z_cache[n].loc[z_cache[n].index <= IS_END] for n in pool89}
    labels, corr = cluster_oriented(z_is)
    reps, cluster_table = pick_reps(labels, is_ic)
    K = len(reps)
    min_valid = min(3, K)
    n_clusters_raw = len(set(labels.values()))
    print(f"clustering: raw clusters={n_clusters_raw} -> K={K} (cap {K_MAX}) "
          f"min_valid={min_valid}")
    print("representatives:", ", ".join(
        f"{r['rep']}({r['rep_abs_is_ic']},n={len(r['members'])})"
        for r in cluster_table[:K]))

    # ---- composite + factor gates
    comp = zmean([z_cache[n] for n in reps], min_valid=min_valid)
    nullA, nullB = [], []
    rng = np.random.default_rng(NULL_SEED)
    popA = sorted(z_cache)
    popB = [n for n in pool89 if n in z_cache]
    K_eff = min(K, len(popA), len(popB))
    for pop, store in ((popA, nullA), (popB, nullB)):
        for _ in range(N_NULLS):
            draw = rng.choice(pop, size=K_eff, replace=False)
            nz = zmean([z_cache[n] for n in draw], min_valid=min_valid)
            s = ic_series(nz, fwd[PRIMARY])
            is_s = s[s.index <= IS_END]
            if len(is_s) >= 30:
                store.append(float(is_s.mean()))
    p95A = float(np.quantile(np.abs(nullA), 0.95)) if nullA else 0.0
    p95B = float(np.quantile(np.abs(nullB), 0.95)) if nullB else 0.0
    v1_bar = round(max(IC_FLOOR, p95A, p95B), 4)
    print(f"nulls: A n={len(nullA)} p95={p95A:.4f} | B n={len(nullB)} p95={p95B:.4f} "
          f"-> V1 bar={v1_bar}")

    fac = {f"h{h}": seg_stats(ic_series(comp, fwd[h])) for h in HORIZONS}
    fi, fo = fac[f"h{PRIMARY}"]["is"], fac[f"h{PRIMARY}"]["oos"]
    v1 = bool(abs(fi["mean"]) > v1_bar)
    v2 = bool(fi["ir"] >= IR_FLOOR)
    v3 = bool(np.sign(fo["mean"]) == np.sign(fi["mean"])
              and abs(fo["mean"]) >= OOS_DECAY_MIN * abs(fi["mean"]))
    print(f"composite IC h{PRIMARY}: IS {fi['mean']}/{fi['ir']} "
          f"OOS {fo['mean']}/{fo['ir']} -> V1={v1} V2={v2} V3={v3}")
    factor_pass = bool(v1 and v2 and v3)
    comp_row = {"kind": "composite", "name": "gtja_composite",
                "h10_is_ic": fi["mean"], "h10_is_ir": fi["ir"],
                "h10_oos_ic": fo["mean"], "h10_oos_ir": fo["ir"],
                "v1_bar": v1_bar, "v1": v1, "v2": v2, "v3": v3,
                "factor_pass": factor_pass, "k_reps": K}
    for h in HORIZONS:
        for seg in ("is", "oos"):
            comp_row[f"h{h}_{seg}_ic"] = fac[f"h{h}"][seg].get("mean")
            comp_row[f"h{h}_{seg}_ir"] = fac[f"h{h}"][seg].get("ir")

    # ---- strategy rails: anchor + candidates + baselines
    print("loading engine universe (bare codes)...")
    prices = ct.load_core()
    P = ct.panels(prices)
    close, high, low = P["close"], P["high"], P["low"]
    idx = close.index
    data_end = str(idx[-1].date())
    print(f"  {len(prices)} ETFs, data through {data_end}")

    w5 = top_n_rotation(high, low, close, top_n=5, rebal_days=REBAL)
    r = ct.run_one(prices, idx, w5, {"max_positions": 5,
                                     "position_size_pct": round(0.95 / 5, 4)})
    anchor = {"expected": (0.4225, 0.9727, 707),
              "got": (r["full"]["sharpe"], r["oos"]["sharpe"], r["n_trades"]),
              "ok": bool(abs(r["full"]["sharpe"] - 0.4225) < ANCHOR_TOL
                         and abs(r["oos"]["sharpe"] - 0.9727) < ANCHOR_TOL
                         and r["n_trades"] == 707)}
    print(f"rail anchor composite_top5: got {anchor['got']} ok={anchor['ok']}")
    if not anchor["ok"]:
        print("RAIL ANCHOR BROKEN -- batch void, no verdict")
        void_exit(anchor, data_end, errors, n_clusters_raw, K, comp_row)
        return

    comp_e = comp.reindex(index=idx, columns=close.columns)
    rows, runs, n_runs = [], {}, 1          # n_runs counts the anchor
    for n in TOP_NS:
        w = rotation_from_score(comp_e, n, REBAL)
        params = {"max_positions": n, "position_size_pct": round(0.95 / n, 4)}
        r = ct.run_one(prices, idx, w, params)
        n_runs += 1
        cl = g1_clauses(r)
        green = all(cl.values())
        runs[f"gtja_top{n}"] = {"full": r["full"], "oos": r["oos"],
                                "n_trades": r["n_trades"], "clauses": cl,
                                "green": green, "equity": r["equity"]}
        rows.append({"role": "candidate", "point": f"gtja_top{n}_r{REBAL}",
                     "cost_mult": 1, "full_sharpe": r["full"]["sharpe"],
                     "full_ann": r["full"]["annual_return"],
                     "full_dd": r["full"]["max_drawdown"], "n_trades": r["n_trades"],
                     "oos_sharpe": r["oos"]["sharpe"], "oos_ann": r["oos"]["annual_return"],
                     "green": green, **{f"c_{k}": v for k, v in cl.items()}})
        print(f"  gtja_top{n}  full={r['full']['sharpe']:>7.3f} "
              f"oos={r['oos']['sharpe']:>7.3f} trades={r['n_trades']:<5} "
              f"{'GREEN' if green else 'red'}")

    print(f"running {N_BASELINES} random baselines (ledger discipline)...")
    syms = list(close.columns)
    for k in range(N_BASELINES):
        p = BASELINE_P[k // 10]
        rg = np.random.default_rng(NULL_SEED + k)
        entry = pd.DataFrame((rg.random((len(idx), len(syms))) < p).astype(int),
                             index=idx, columns=syms)
        exit_ = pd.DataFrame(False, index=idx, columns=syms)   # engine rules only
        r = p1_run_one(prices, idx, entry, exit_, {}, f"rand_p{p}_s{k % 10}")
        n_runs += 1
        rows.append({"role": "baseline", "point": f"rand_p{p}_s{k % 10}",
                     "cost_mult": 1, "full_sharpe": r["full"]["sharpe"],
                     "full_ann": r["full"]["annual_return"],
                     "full_dd": r["full"]["max_drawdown"], "n_trades": r["n_trades"],
                     "oos_sharpe": r["oos"]["sharpe"], "oos_ann": r["oos"]["annual_return"],
                     "green": ""})
    bl = [x for x in rows if x["role"] == "baseline"]
    b_p95 = round(float(np.percentile([x["oos_sharpe"] for x in bl], 95)), 4)
    b_p95f = round(float(np.percentile([x["full_sharpe"] for x in bl], 95)), 4)
    print(f"  baselines: full p95={b_p95f} oos p95={b_p95} (recorded i-line {I_BAR} stands)")

    # ---- G2 for G1' survivors
    g2, survivors = {}, [f"gtja_top{n}" for n in TOP_NS if runs[f"gtja_top{n}"]["green"]]
    if survivors:
        ct.self_test_patches()                     # J10 lesson: patch must bite first
    for key in survivors:
        n = int(key.split("top")[1])
        r = runs[key]
        decay_ok = bool(r["oos"]["sharpe"] >= oos_bar)
        pts = []
        n_var = [nn for nn in (n - 1, n + 1) if 2 <= nn <= 10]
        pts_def = [(nn, REBAL) for nn in n_var] + [(n, 10), (n, 40)]
        for nn, rb in pts_def:
            w = rotation_from_score(comp_e, nn, rb)
            rr = ct.run_one(prices, idx, w, {"max_positions": nn,
                                             "position_size_pct": round(0.95 / nn, 4)})
            n_runs += 1
            cl = g1_clauses(rr)
            g = all(cl.values())
            pts.append({"point": f"n{nn}_r{rb}", "full_sharpe": rr["full"]["sharpe"],
                        "oos_sharpe": rr["oos"]["sharpe"], "n_trades": rr["n_trades"],
                        "clauses": cl, "green": g})
            rows.append({"role": "nbhd", "point": f"gtja_top{nn}_r{rb}",
                         "cost_mult": 1, "full_sharpe": rr["full"]["sharpe"],
                         "full_ann": rr["full"]["annual_return"],
                         "full_dd": rr["full"]["max_drawdown"],
                         "n_trades": rr["n_trades"],
                         "oos_sharpe": rr["oos"]["sharpe"],
                         "oos_ann": rr["oos"]["annual_return"], "green": g})
            print(f"  nbhd {key} n{nn}_r{rb}: full={rr['full']['sharpe']:.3f} "
                  f"{'GREEN' if g else 'RED'}")
        nb_all = bool(pts) and all(p["green"] for p in pts)
        cost_runs = {}
        for m in (2, 3):
            w = rotation_from_score(comp_e, n, REBAL)
            params = {"max_positions": n, "position_size_pct": round(0.95 / n, 4)}
            rx = ct.run_one(prices, idx, w, params, cost_mult=m)
            n_runs += 1
            survive = bool(m == 2 and rx["full"]["sharpe"] > VI_BAR
                           and rx["oos"]["sharpe"] >= oos_bar)
            cost_runs[f"x{m}"] = {"full_sharpe": rx["full"]["sharpe"],
                                  "oos_sharpe": rx["oos"]["sharpe"],
                                  "n_trades": rx["n_trades"], "survive": survive}
            rows.append({"role": "cost", "point": f"gtja_top{n}_r{REBAL}",
                         "cost_mult": m, "full_sharpe": rx["full"]["sharpe"],
                         "full_ann": rx["full"]["annual_return"],
                         "full_dd": rx["full"]["max_drawdown"],
                         "n_trades": rx["n_trades"],
                         "oos_sharpe": rx["oos"]["sharpe"],
                         "oos_ann": rx["oos"]["annual_return"],
                         "green": survive if m == 2 else ""})
            print(f"  cost {key} x{m}: full={rx['full']['sharpe']:.3f} "
                  f"oos={rx['oos']['sharpe']:.3f} survive={survive}")
        yearly = ct.yearly_returns(r["equity"])
        worst = min(yearly.values())
        g2_pass = bool(decay_ok and nb_all and cost_runs["x2"]["survive"]
                       and worst > CRASH_YEAR)
        g2[key] = {"decay_ok": decay_ok, "neighborhood_all_green": nb_all,
                   "neighborhood": pts, "cost": cost_runs,
                   "yearly_returns": yearly, "worst_year": worst,
                   "g2_pass": g2_pass, "n": n}
        print(f"G2 {key}: decay={decay_ok} nb_all={nb_all} "
              f"x2={cost_runs['x2']['survive']} worst_year={worst} "
              f"-> {'PASS' if g2_pass else 'FAIL'}")

    # ---- ledger + products
    g2_runs = sum(len(g["neighborhood"]) + len(g["cost"]) for g in g2.values())
    trials = 2 * N_NULLS + len(TOP_NS) + N_BASELINES + g2_runs
    ledger = {"prev_total": LEDGER_PREV, "batch_trials": trials,
              "note": f"100 null composites + {len(TOP_NS)} candidates + "
                      f"{N_BASELINES} baselines + {g2_runs} G2 runs; "
                      f"engine_runs={n_runs} (incl. rail anchor, not a trial)",
              "total": LEDGER_PREV + trials}
    write_products(comp_row, rows, runs, g2, survivors, cluster_table, K, reps,
                   min_valid, factor_pass, anchor, consts, oos_bar, errors,
                   ledger, data_end, t0, n_clusters_raw, n_runs, sanitized)
    print(f"\nverdict: factor_pass={factor_pass} G1' survivors={len(survivors)} "
          f"G2 pass={[k for k, v in g2.items() if v['g2_pass']]}")
    print(f"ledger N: {LEDGER_PREV}+{trials}={ledger['total']} "
          f"elapsed={time.time()-t0:.0f}s")


def void_exit(anchor, data_end, errors, n_clusters_raw, K, comp_row):
    payload = {"batch": "P2-gtja191-synthesis", "void": True,
               "reason": "rail anchor broken", "anchor": anchor,
               "clusters_raw": n_clusters_raw, "k": K,
               "factor_row": comp_row, "runtime_errors": errors,
               "data_cutoff": data_end,
               "generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(os.path.join(PATHS.results_dir, "shortline_p2_synth.json"), "w",
              encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, default=str)
    print("void payload saved; no verdict, no registration")


def write_products(comp_row, rows, runs, g2, survivors, cluster_table, K, reps,
                   min_valid, factor_pass, anchor, consts, oos_bar, errors,
                   ledger, data_end, t0, n_clusters_raw, n_runs, sanitized):
    csv1 = os.path.join(_ROOT, "research", "shortline", "p2_gtja_composite.csv")
    pd.DataFrame([comp_row]).to_csv(csv1, index=False)
    csv2 = os.path.join(_ROOT, "research", "shortline", "p2_gtja_runs.csv")
    pd.DataFrame(rows).to_csv(csv2, index=False)
    payload = {
        "batch": "P2-gtja191-synthesis",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/shortline/P2_GTJA191_SYNTH.md (written before run)",
        "universe": {"pool": "core48-bare", "oos_start": "2025-01-01",
                     "data_cutoff": data_end},
        "pool_source": "bm-a gtja191_ic_results.csv in_pool=89 (GM ruling, P-2 = bm-b)",
        "clustering": {"raw_clusters": n_clusters_raw, "k_after_cap": K,
                       "cut": T_CUT, "linkage": "complete", "min_valid": min_valid,
                       "reps": reps, "clusters": cluster_table},
        "factor_gates": {"composite": comp_row, "factor_pass": factor_pass},
        "strategy": {k: {"full": v["full"], "oos": v["oos"],
                         "n_trades": v["n_trades"], "clauses": v["clauses"],
                         "green": v["green"]} for k, v in runs.items()},
        "g2": g2, "survivors_g1": survivors,
        "g2_pass": [k for k, v in g2.items() if v["g2_pass"]],
        "rail_anchor": anchor, "recorded_constants": consts,
        "runtime_errors": errors, "trials_ledger": ledger,
        "engine_runs": n_runs, "sanitized_panels": sanitized,
        "population_note": "population A = 182 (183 minus alpha191_064: "
                            "coverage 0, NaN IS IC, cannot orient, prereg S1 "
                            "'finite IS IC only' clause)",
        "elapsed_sec": round(time.time() - t0, 1),
    }
    with open(os.path.join(PATHS.results_dir, "shortline_p2_synth.json"), "w",
              encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, default=str)
    print(f"saved: {csv1}\nsaved: {csv2}")
    print("saved: results/shortline_p2_synth.json")

    # registration clause (prereg section 6): single slot on G2 PASS
    passed = [k for k, v in g2.items() if v["g2_pass"]]
    if passed:
        best = max(passed, key=lambda k: runs[k]["full"]["sharpe"])
        n = g2[best]["n"]
        reg = {
            "id": "GTJA-COMPOSITE-01", "name": "研报合成一号",
            "school": "composite", "author": "researcher-p2",
            "created": time.strftime("%Y-%m-%d"),
            "evidence_cutoff": data_end,
            "level": "INTERN",
            "params": ["entry", "max_positions", "position_size_pct"],
            "entry_builder": {"type": "gtja191_composite",
                              "reps": reps, "min_valid": min_valid,
                              "top_n": n, "rebal_days": REBAL},
            "repro": {"script": "research/shortline/screening/p2_gtja_synth.py",
                      "note": "clean-room gtja191_ops; pool=bm-a in_pool 89; "
                              "orientation=P-1a IS h10 signs; z-equal-weight reps"},
            "backtest": {"in_sample": runs[best]["full"],
                         "out_sample": runs[best]["oos"],
                         "cost_x2": g2[best]["cost"]["x2"]},
            "paper": {"months_tracked": 0, "monthly_returns": [],
                      "current_dd": 0.0, "as_of": None, "cutoff": None},
            "live": {"months_tracked": 0, "allocation_pct": 0, "pnl": []},
            "status_history": [{"date": time.strftime("%Y-%m-%d"), "from": None,
                                "to": "INTERN",
                                "note": f"P-2 GTJA191 synthesis one-shot G2 pass: "
                                        f"six G1' + OOS>={oos_bar} + nbhd green + "
                                        f"x2 survive + no crash year. Ledger N="
                                        f"{ledger['total']}"}],
            "notes": "cluster-representative z-composite of GTJA191 wide-screen "
                     "pool (89), engine default exits; SIGNAL_BUILDERS wiring "
                     "next round (no paper wiring = no accrual, hr gate intact)",
        }
        path = os.path.join(_ROOT, "firm", "traders", "GTJA-COMPOSITE-01.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(reg, f, ensure_ascii=False, indent=2)
        print(f"REGISTERED: GTJA-COMPOSITE-01 (from {best}) -> {path}")


if __name__ == "__main__":
    run_selftests_gate()
    main()
