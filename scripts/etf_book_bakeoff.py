"""Second book, round two: a bake-off of candidate mechanisms against the shipped book.

Why: r1296 closed short-horizon reversal as a second-book candidate -- it was shaped
right (0.25 OOS correlation, 7% name overlap) and still lost money. The capacity study
(r1280/r1295) says the shipped book's size is capped by participation, so the only lever
left is a *second, low-correlated, positive-expectancy* book. This script answers
"which mechanism, if any" in one run instead of one mechanism per round.

Rules this measurement obeys (each one was paid for by an earlier mistake):
  * the control arm must be THE SHIPPED BOOK -- built through
    `etf_book_production.prep_panel()` (class-restricted, split prints repaired) and
    asserted against the published `results/etf_book_production/latest.json` n12_vt08
    CAGR. r1296's first cut compared against a rebuilt panel and priced "book A" at
    6.74% where the shipped book does 9.49%.
  * every candidate runs on the same panel, the same open-to-open execution, the same
    10bp/side and the same 8% vol target; only the score and the cadence differ.
  * a seeded random-score book runs as the null control, and the number of candidates
    tested is published (multiple-comparisons honesty).
  * nothing here is a live face: no registry entry, no capital claim.

Outputs results/etf_book_bakeoff.json and a printed table.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
from config import PATHS

IS_END = "2023-12-31"
TARGET_VOL = 0.08
COST = 0.0010
CONTROL_TOL_PP = 0.50     # published vs computed CAGR, percentage points
CORR_MAX = 0.70           # "a different trade" threshold used for the verdict


def _mask(score, close, amt):
    """Same eligibility the shipped book uses: liquidity floor and enough history."""
    hist = close.notna().cumsum()
    elig = (amt.reindex_like(close) >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    out = score.where(elig)
    out.index = pd.to_datetime(out.index)
    return out


def _rank(raw, close, amt):
    """Cross-sectional percentile score in [-1, 1]; only data at or before each row."""
    return _mask((raw.rank(axis=1, pct=True) - 0.5) * 2.0, close, amt)


def vol60_score(close, amt):
    return _rank(-(close.pct_change().rolling(60).std() * np.sqrt(252)), close, amt)


def mom60_score(close, amt):
    return _rank(close.pct_change(60), close, amt)


def breakout_score(close, amt):
    return _rank(close / close.rolling(60).max() - 1.0, close, amt)


def rev5_score(close, amt):
    return _rank(-close.pct_change(5), close, amt)


def random_score(close, amt, seed=20261027):
    rs = np.random.RandomState(seed)
    raw = pd.DataFrame(rs.random_sample(close.shape), index=close.index, columns=close.columns)
    return _rank(raw, close, amt)


def daily_returns(ser):
    return ser.sort_index().pct_change().dropna()


def blend(series_list, weights):
    """Fixed-weight daily-rebalanced blend (paper composition, no extra cost)."""
    rets = [daily_returns(s) for s in series_list]
    idx = rets[0].index
    for r in rets[1:]:
        idx = idx.intersection(r.index)
    acc = None
    for w, r in zip(weights, rets):
        part = r.reindex(idx).fillna(0.0) * w
        acc = part if acc is None else acc + part
    eq = (1.0 + acc).cumprod()
    eq.index = idx
    return eq


def pair_corr(a, b):
    ra, rb = daily_returns(a), daily_returns(b)
    idx = ra.index.intersection(rb.index)
    if len(idx) < 20:
        return None
    return float(np.corrcoef(ra.reindex(idx).fillna(0.0), rb.reindex(idx).fillna(0.0))[0, 1])


def shared_name_pct(close, amt, score_a, score_b, n_a, n_b, rebal, start=R.START):
    """Share of book A's decision days where both books hold >=1 common name."""
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    sa, sb = score_a.where(elig), score_b.where(elig)
    dates = [d for d in close.index if d >= pd.Timestamp(start)]
    shared = days = 0
    for i in range(0, len(dates) - 1, rebal):
        d = dates[i]
        x, y = sa.loc[d].dropna(), sb.loc[d].dropna()
        if len(x) < n_a or len(y) < n_b:
            continue
        days += 1
        if set(x.nlargest(n_a).index) & set(y.nlargest(n_b).index):
            shared += 1
    return {"decision_days": days, "days_with_shared_name": shared,
            "shared_pct": round(shared / days, 4) if days else None}


def control_delta_pp(computed_cagr, published_cagr):
    """Signed difference in percentage points; None when either side is missing."""
    if computed_cagr is None or published_cagr is None:
        return None
    return round((float(computed_cagr) - float(published_cagr)) * 100.0, 3)


def verdict(row):
    """A second book has to earn its place: positive, additive to the blend, different."""
    if row.get("cagr") is None or row.get("blend_cagr") is None:
        return "unmeasured"
    if row["cagr"] <= 0:
        return "reject: loses money alone"
    if row.get("corr_full") is not None and row["corr_full"] >= CORR_MAX:
        return "reject: same trade (corr >= %.2f)" % CORR_MAX
    if row["blend_cagr"] <= row.get("control_cagr", 0.0):
        return "reject: blend does not beat the shipped book"
    return "candidate: pursue"


def published_control_cagr(path=None):
    p = path or os.path.join(PATHS.results_dir, "etf_book_production", "latest.json")
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        return float(d["backtest"]["n12_vt08"]["full"]["cagr"])
    except Exception:
        return None


def selftest():
    ok = total = 0

    def chk(label, cond, detail=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print("[PASS]", label, "|", detail, flush=True)
        else:
            print("[FAIL]", label, "|", detail, flush=True)

    idx = pd.bdate_range("2021-01-01", periods=200)
    cols = ["sh510300", "sh510500", "sz159915", "sh518880"]
    rs = np.random.RandomState(7)
    close = pd.DataFrame(1.0 + rs.random_sample((len(idx), len(cols))).cumsum(0) * 0.01,
                         index=idx, columns=cols)
    amt = pd.DataFrame(1e9, index=idx, columns=cols)

    # L1 causality: each score at row t must equal the score computed from a panel
    # truncated at t (no lookahead in the rolling windows).
    for name, fn in (("vol60", vol60_score), ("mom60", mom60_score), ("breakout", breakout_score)):
        full = fn(close, amt)
        cut = fn(close.iloc[:120], amt.iloc[:120])
        v1, v2 = full.loc[idx[119]].dropna(), cut.loc[idx[119]].dropna()
        same = len(v1) > 0 and len(v1) == len(v2) and np.allclose(v1.sort_index(), v2.sort_index())
        chk("L1 %s is causal" % name, same, "row 120 identical under truncation")

    # L2 the null control is reproducible and not accidentally causal-free noise
    r1, r2 = random_score(close, amt), random_score(close, amt)
    chk("L2 random control deterministic", r1.equals(r2), "same seed -> identical scores")

    # L3 a blend of a leg with itself reproduces the leg (guards the "blend is a no-op"
    # and "blend hides a cost" failure modes)
    eq = pd.Series(np.linspace(1.0, 1.4, 120), index=idx[:120])
    b = blend([eq, eq], [0.5, 0.5])
    chk("L3 blend of identical legs == leg", np.allclose(b.values, daily_returns(eq).add(1).cumprod().values),
        "max diff %.2e" % float(np.max(np.abs(b.values - daily_returns(eq).add(1).cumprod().values))))

    # L4 the control assertion actually fires: a 1pp gap must exceed the tolerance
    chk("L4 control guard catches drift", abs(control_delta_pp(0.1049, 0.0949)) > CONTROL_TOL_PP,
        "delta %.2fpp vs tol %.2f" % (control_delta_pp(0.1049, 0.0949), CONTROL_TOL_PP))
    chk("L4b control guard passes the shipped number", abs(control_delta_pp(0.0949, 0.0949)) <= CONTROL_TOL_PP,
        "identical inputs")

    # L5 a losing leg can never be reported as a candidate
    chk("L5 negative CAGR is rejected",
        verdict({"cagr": -0.0367, "blend_cagr": 0.028, "corr_full": 0.46, "control_cagr": 0.0949})
        .startswith("reject"),
        "reversal book stays rejected")
    chk("L5b high correlation is rejected",
        verdict({"cagr": 0.12, "blend_cagr": 0.10, "corr_full": 0.85, "control_cagr": 0.0949})
        .startswith("reject"),
        "corr gate")
    chk("L5c positive, additive, different passes",
        verdict({"cagr": 0.12, "blend_cagr": 0.131, "corr_full": 0.30, "control_cagr": 0.0949})
        .startswith("candidate"),
        "all three gates open")

    print("\nselftest %d/%d" % (ok, total), flush=True)
    return 0 if ok == total else 1


def main(only=None):
    import etf_book_production as P
    close, openp, amt, score_a, cls, n_flip = P.prep_panel()
    print("panel names %d bars %d flips %d" % (close.shape[1], close.shape[0], n_flip), flush=True)

    # tag -> (score fn, n_hold, rebal, one-line mechanism)
    cands = {
        "lowvol_12": (vol60_score, 12, 20, "cross-sectional LOW volatility (short-horizon vol)"),
        "mom60_10": (mom60_score, 10, 10, "60-day cross-sectional momentum, faster cadence than A"),
        "breakout_12": (breakout_score, 12, 20, "distance to the 60d high (breakout strength)"),
        "rev5_10": (rev5_score, 10, 10, "5-day reversal (r1296 reference arm, expected to fail)"),
        "rand_12": (random_score, 12, 20, "seeded random scores (null control)"),
    }
    if only:
        cands = {k: v for k, v in cands.items() if k in only}

    out = {"evidence_cutoff": str(close.index[-1].date()),
           "execution": "decision at close t, execute at open t+1, vol target 8%%, cost 10bp/side",
           "panel": {"names": int(close.shape[1]), "flips_repaired": int(n_flip),
                     "classes": list(P.USE_CLASSES),
                     "why": "same panel the production card prices, so book A is the shipped book"},
           "note": "exploratory; not a live face, not registered, no capital claim",
           "n_candidates": len(cands), "books": {}, "vs_A": {}, "ranking": []}

    sum_a, turn_a = R.open_to_open_equity(close, openp, amt, score_a, 20, 12,
                                          COST, vol_target=TARGET_VOL)
    a_full = R.stats(sum_a, "A_trend_12_R20")
    a_full["turnover"] = round(turn_a, 2)
    a_is = R.stats(sum_a[sum_a.index <= IS_END], "A_is")
    a_oos = R.stats(sum_a[sum_a.index > IS_END], "A_oos")
    for k in ("cagr", "sharpe", "maxdd"):
        a_full[k + "_is"] = a_is.get(k)
        a_full[k + "_oos"] = a_oos.get(k)
    out["books"]["A_trend"] = a_full

    pub = published_control_cagr()
    delta = control_delta_pp(a_full.get("cagr"), pub)
    out["control_check"] = {"published_cagr": pub, "computed_cagr": a_full.get("cagr"),
                            "delta_pp": delta, "tolerance_pp": CONTROL_TOL_PP,
                            "matches": (delta is not None and abs(delta) <= CONTROL_TOL_PP)}
    print("control A: computed %.2f%% published %s delta %s pp"
          % (a_full["cagr"] * 100, ("%.2f%%" % (pub * 100)) if pub else "n/a", delta), flush=True)

    for tag, (fn, n_hold, rebal, why) in cands.items():
        score = fn(close, amt)
        ser, turn = R.open_to_open_equity(close, openp, amt, score, rebal, n_hold,
                                          COST, vol_target=TARGET_VOL)
        full = R.stats(ser, tag)
        full["turnover"] = round(turn, 2)
        full["n_hold"] = n_hold
        full["rebal"] = rebal
        full["mechanism"] = why
        is_s = R.stats(ser[ser.index <= IS_END], tag + "_is")
        oos = R.stats(ser[ser.index > IS_END], tag + "_oos")
        for k in ("cagr", "sharpe", "maxdd"):
            full[k + "_is"] = is_s.get(k)
            full[k + "_oos"] = oos.get(k)
        out["books"][tag] = full

        bl = blend([sum_a, ser], [0.5, 0.5])
        bl_st = R.stats(bl, tag + "_blend50")
        bl_is = R.stats(bl[bl.index <= IS_END], tag + "_blend_is")
        bl_oos = R.stats(bl[bl.index > IS_END], tag + "_blend_oos")
        for k in ("cagr", "sharpe", "maxdd"):
            bl_st[k + "_is"] = bl_is.get(k)
            bl_st[k + "_oos"] = bl_oos.get(k)

        corr = {}
        for w, sl in (("full", None), ("is", IS_END), ("oos", IS_END)):
            if w == "full":
                x, y = sum_a, ser
            elif w == "is":
                x, y = sum_a[sum_a.index <= IS_END], ser[ser.index <= IS_END]
            else:
                x, y = sum_a[sum_a.index > IS_END], ser[ser.index > IS_END]
            c = pair_corr(x, y)
            corr[w] = round(c, 3) if c is not None else None

        ov = shared_name_pct(close, amt, score_a, score, 12, n_hold, 20)
        row = {"tag": tag, "cagr": full.get("cagr"), "sharpe": full.get("sharpe"),
               "maxdd": full.get("maxdd"), "cagr_oos": full.get("cagr_oos"),
               "turnover": full.get("turnover"), "corr_full": corr["full"],
               "corr_oos": corr["oos"], "shared_pct": ov["shared_pct"],
               "blend_cagr": bl_st.get("cagr"), "blend_sharpe": bl_st.get("sharpe"),
               "blend_maxdd": bl_st.get("maxdd"), "control_cagr": a_full.get("cagr")}
        row["verdict"] = verdict(row)
        out["vs_A"][tag] = {"correlation": corr, "overlap": ov, "blend_50_50": bl_st,
                            "verdict": row["verdict"]}
        out["ranking"].append(row)
        print("%-12s cagr %7.2f%% SR %5.3f dd %6.2f%% oos %7.2f%% corr %5.3f shared %4.1f%% "
              "blend %7.2f%% -> %s"
              % (tag, (full.get("cagr") or 0) * 100, full.get("sharpe") or 0,
                 (full.get("maxdd") or 0) * 100, (full.get("cagr_oos") or 0) * 100,
                 corr["full"] if corr["full"] is not None else float("nan"),
                 (ov["shared_pct"] or 0) * 100, (bl_st.get("cagr") or 0) * 100,
                 row["verdict"]), flush=True)

    out["ranking"].sort(key=lambda r: (-(r["cagr"] or -9), -(r["blend_sharpe"] or -9)))
    p = os.path.join(PATHS.results_dir, "etf_book_bakeoff.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", p, flush=True)
    if not out["control_check"]["matches"]:
        print("CONTROL MISMATCH: computed book A is not the shipped book", flush=True)
        return 2
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--selftest" in args:
        sys.exit(selftest())
    only = None
    if "--only" in args:
        only = set(args[args.index("--only") + 1].split(","))
    sys.exit(main(only))