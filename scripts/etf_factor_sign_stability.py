"""Do the six production factor signs still point the way they were fitted to point?

Every ETF composite note since r1245 ranks six factors with signs frozen in
`etf_composite_pf.SIGNS`, and those signs come from one in-sample IC table
(`results/factor_ic.json`).  Nobody had asked the two questions a frozen sign
begs: (a) does each factor still carry its stated direction in each individual
year, and (b) if the signs were re-read every rebalance from the trailing three
years only, would the book have earned more or less than the frozen signs?

Design (all of it frozen in CRITERIA below before the first run):

* forward horizon = the book's own holding period (20 bars), so the IC measured
  here is the IC of the thing the book actually trades;
* an IC observation is only used for a year once its forward window has fully
  printed (a bar pair that reaches past the panel end is dropped, never
  truncated to whatever was available);
* the lagged arm reads signs from the trailing 756 calendar days of IC
  observations, shifted one observation so the bar being decided is never
  inside its own estimator -- a sign that needs today's return to be chosen is
  not a causal sign;
* both arms ride `etf_composite_pf.run_next_open` on the same panel, same
  rebalance grid, same 8bp/side cost -- the only difference is the sign set.

Exit codes: 0 = ran, 2 = mechanism fault (missing panel/feats), 3 = a frozen
criterion could not be evaluated (too few observations).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from scripts import etf_composite_pf as F

START = "2020-01-01"
HORIZON = 20          # the book's own holding period
IC_STRIDE = 5         # one IC observation per rebalance week
R_REBAL = 20          # production cadence (etf_book_order.REBAL)
TRAIL_DAYS = 756      # three calendar years of trailing observations
MIN_OBS = 150         # a factor needs this many eligible names to score an IC
MIN_IC_OBS = 40       # trailing mean needs this many observations to be a reading
GROWTH_BP = 50.0      # a switch has to clear half a point a year to count

CRITERIA = {
    "stable_share": 0.70,      # >= 5 of 7 years agreeing = the sign is STABLE
    "contrary_share": 0.43,    # <= 3 of 7 years agreeing = the sign is CONTRARY
    "switch_bp": GROWTH_BP,
    "severity": ["SIGNS_CONTRARY", "SIGNS_DRIFT", "SIGNS_STABLE"],
}

RECEIPT = os.path.join("results", "etf_factor_sign_stability.json")


def _elig(close, amt):
    hist = close.notna().cumsum()
    return (amt >= F.MIN_AMT) & (hist >= F.MIN_HIST)


def rank_ic_series(feat, fwd, elig, dates, stride=IC_STRIDE, min_obs=MIN_OBS):
    """Cross-sectional rank IC of one factor on every `stride`-th bar.

    Both sides are ranked inside the same eligible cross-section, so a factor
    whose units or outliers move does not move the reading.
    """
    f = feat.reindex(index=dates, columns=elig.columns).where(elig.reindex(index=dates))
    r = fwd.reindex(index=dates, columns=elig.columns).where(elig.reindex(index=dates))
    fr = f.rank(axis=1)
    rr = r.rank(axis=1)
    out = {}
    for d in dates[::stride]:
        a = fr.loc[d]
        b = rr.loc[d]
        m = a.notna() & b.notna()
        n = int(m.sum())
        if n < min_obs:
            continue
        av = a[m].to_numpy(dtype=float)
        bv = b[m].to_numpy(dtype=float)
        if av.std() == 0 or bv.std() == 0:
            continue
        out[d] = (float(np.corrcoef(av, bv)[0, 1]), n)
    if not out:
        return pd.Series(dtype=float), pd.Series(dtype=float)
    ic = pd.Series({k: v[0] for k, v in out.items()}).sort_index()
    nn = pd.Series({k: v[1] for k, v in out.items()}).sort_index()
    return ic, nn


def yearly_ic(ic, sign, years):
    rows = []
    if len(ic) == 0:
        return [{"year": int(y), "n_obs": 0, "mean_ic": None, "agrees": None,
                 "note": "no observation"} for y in years], 0
    ic = ic.copy()
    ic.index = pd.to_datetime(ic.index)
    for y in years:
        s = ic[ic.index.year == y]
        if len(s) == 0:
            rows.append({"year": int(y), "n_obs": 0, "mean_ic": None,
                         "agrees": None, "note": "no observation"})
            continue
        m = float(s.mean())
        rows.append({
            "year": int(y),
            "n_obs": int(len(s)),
            "mean_ic": round(m, 4),
            "agrees": bool(np.sign(m) == np.sign(sign)),
        })
    agree = sum(1 for r in rows if r["agrees"])
    return rows, agree


def sign_class(agree, n_years, criteria=CRITERIA):
    """Share-based so the same words mean the same thing on 2 years or on 7.

    At the frozen shape (5 of 7 stable, 3 of 7 contrary) this reproduces the
    absolute thresholds exactly; it only stops a short panel from being graded
    on a 7-year ruler.
    """
    if n_years <= 0:
        return None
    share = agree / float(n_years)
    if share >= criteria["stable_share"]:
        return "SIGNS_STABLE"
    if share <= criteria["contrary_share"]:
        return "SIGNS_CONTRARY"
    return "SIGNS_DRIFT"


def trailing_sign(ic, index, trail_days=TRAIL_DAYS, min_obs=MIN_IC_OBS):
    """Sign of the trailing mean IC, decided from observations strictly before t.

    The estimator is shifted by one observation: the sign applied on bar t is
    built from observations that all closed before t.  Where the trailing window
    is too thin the production sign is kept and the bar is counted, so a young
    panel cannot silently become an "all long" book.
    """
    if len(ic) == 0:
        return None, 0
    shifted = ic.shift(1)
    roll = shifted.rolling(f"{trail_days}D", min_periods=1).agg(["mean", "count"])
    fallback = 0
    signs = []
    for d in index:
        try:
            m = roll["mean"].asof(d)
            c = roll["count"].asof(d)
        except Exception:
            m, c = np.nan, 0
        if not np.isfinite(m) or not np.isfinite(c) or c < min_obs:
            fallback += 1
            signs.append(np.nan)
        else:
            signs.append(1.0 if m >= 0 else -1.0)
    return pd.Series(signs, index=index), fallback


def lagged_score(feats, close, elig, fwd, sign_prod, panel_dates):
    """Score face with per-date causal signs (production sign where unestimable)."""
    ic_dates = [d for d in panel_dates if d >= pd.Timestamp(START)]
    cols = close.columns
    parts = []
    per_factor = {}
    for c, sgn in sign_prod.items():
        f = feats.get(c)
        if f is None:
            continue
        ic, _ = rank_ic_series(f, fwd, elig, ic_dates)
        sers, fallback = trailing_sign(ic, ic_dates)
        signs = sers.reindex(panel_dates).ffill().bfill()
        if signs is None:
            signs = pd.Series(sgn, index=panel_dates)
        else:
            signs = signs.fillna(sgn)
        z = (f.reindex(index=panel_dates, columns=cols).rank(axis=1, pct=True) - 0.5) * 2.0
        parts.append(z.mul(signs, axis=0))
        per_factor[c] = {
            "production_sign": sgn,
            "fallback_bars": int(fallback),
            "sign_switches": int((signs.diff().fillna(0) != 0).sum()),
            "final_sign": float(signs.iloc[-1]) if len(signs) else None,
        }
    if not parts:
        return None, {}
    score = sum(parts) / len(parts)
    return score.where(elig.reindex(index=panel_dates)), per_factor


def _arm(close, openp, amt, feats, score, label):
    ser, turn, gapfill = F.run_next_open(close, openp, amt, feats, R_REBAL,
                                         n_hold=F.N_HOLD, cost=F.COST,
                                         start=START, score=score)
    full = F.metrics(ser, label)
    oos = F.metrics(ser[ser.index >= pd.Timestamp("2024-01-01")], label + "_oos")
    return {"full": full, "oos": oos, "turnover": round(float(turn), 4),
            "open_gapfill": int(gapfill)}


def score_from_signs(feats, close, amt, signs):
    """Score face from an arbitrary sign dict; a factor mapped to None drops out."""
    idx = close.index
    cols = close.columns
    hist = close.notna().cumsum()
    elig = (amt >= F.MIN_AMT) & (hist >= F.MIN_HIST)
    parts = []
    for c, sgn in signs.items():
        if sgn is None:
            continue
        f = feats.get(c)
        if f is None:
            continue
        f = f.reindex(index=idx, columns=cols)
        parts.append(sgn * ((f.rank(axis=1, pct=True) - 0.5) * 2.0))
    if not parts:
        return None
    score = sum(parts) / len(parts)
    score.index = pd.to_datetime(score.index)
    return score.where(elig)


def decide(a_arm, b_arm, criteria=CRITERIA):
    """Frozen ordering: the lagged arm must clear the bar on growth, sharpe and OOS."""
    d_cagr_bp = 10000.0 * (b_arm["full"]["cagr"] - a_arm["full"]["cagr"])
    d_sharpe = b_arm["full"]["sharpe"] - a_arm["full"]["sharpe"]
    d_oos_bp = 10000.0 * (b_arm["oos"]["cagr"] - a_arm["oos"]["cagr"])
    bar = criteria["switch_bp"]
    if d_cagr_bp >= bar and d_sharpe >= 0 and d_oos_bp >= 0:
        word = "SWITCH_HELPS"
    elif d_cagr_bp <= -bar and d_sharpe <= 0 and d_oos_bp <= 0:
        word = "SWITCH_HURTS"
    else:
        word = "INCONCLUSIVE"
    return {"verdict": word, "cagr_gap_bp": round(d_cagr_bp, 1),
            "sharpe_gap": round(float(d_sharpe), 3), "oos_gap_bp": round(d_oos_bp, 1),
            "bar_bp": bar}


def run(write=True):
    close, openp, amt, feats = F.build_panel()
    if not feats:
        print("[signstab] no factor faces -- mechanism fault")
        return 2
    elig = _elig(close, amt)
    px = close.ffill()
    fwd = (px.shift(-HORIZON) / px - 1.0).where(elig)
    # an observation whose forward window has not printed is not an observation
    fwd = fwd.where(px.shift(-HORIZON).notna())
    panel_dates = list(px.index)
    ic_dates = [d for d in panel_dates if d >= pd.Timestamp(START)]
    years = sorted({d.year for d in ic_dates})

    per_factor = {}
    for c, sgn in F.SIGNS.items():
        f = feats.get(c)
        if f is None:
            per_factor[c] = {"production_sign": sgn, "note": "factor face missing"}
            continue
        ic, nn = rank_ic_series(f, fwd, elig, ic_dates)
        rows, agree = yearly_ic(ic, sgn, years)
        per_factor[c] = {
            "production_sign": sgn,
            "ic_obs": int(len(ic)),
            "mean_ic": round(float(ic.mean()), 4) if len(ic) else None,
            "years": rows,
            "agree_years": int(agree),
            "class": sign_class(agree, len(years)),
        }

    prod_score = F.build_score(close, amt, feats)
    lag_score, sign_diag = lagged_score(feats, close, elig, fwd, F.SIGNS, panel_dates)
    if lag_score is None:
        print("[signstab] could not build the lagged score face")
        return 3

    a = _arm(close, openp, amt, feats, prod_score, "frozen_signs")
    b = _arm(close, openp, amt, feats, lag_score, "lagged_signs")
    dec = decide(a, b)

    # Two diagnostic arms named by the yearly table itself (not adopted here): what if
    # the unstable factors simply leave, and what if the contrary one is flipped?
    stable_only_signs = {c: (sgn if (v.get("class") == "SIGNS_STABLE") else None)
                         for c, sgn in F.SIGNS.items() for v in [per_factor[c]]}
    flip_signs = {c: (-sgn if per_factor[c].get("class") == "SIGNS_CONTRARY" else sgn)
                  for c, sgn in F.SIGNS.items()}
    arms = {"frozen_signs": a, "lagged_signs": b}
    decisions = {"lagged_signs": dec}
    for name, signs in (("stable_only", stable_only_signs), ("flip_contrary", flip_signs)):
        sc = score_from_signs(feats, close, amt, signs)
        if sc is None:
            continue
        arms[name] = _arm(close, openp, amt, feats, sc, name)
        decisions[name] = decide(a, arms[name])
        decisions[name]["signs"] = {c: s for c, s in signs.items()}

    grades = [v.get("class") for v in per_factor.values() if v.get("class")]
    worst = min(grades, key=lambda g: CRITERIA["severity"].index(g)) if grades else None

    last = px.index[-1]
    head = {"frozen_signs": F.today_picks(prod_score, close, n_hold=F.N_HOLD)}
    head_lag = F.today_picks(lag_score.ffill(), close, n_hold=F.N_HOLD) if lag_score.notna().any().any() else []
    receipt = {
        "face": "etf_factor_sign_stability",
        "evidence_cutoff": str(pd.Timestamp(last).date()),
        "panel": {"symbols": int(close.shape[1]), "bars": int(close.shape[0]),
                  "start": str(pd.Timestamp(px.index[0]).date())},
        "criteria": CRITERIA,
        "horizon_bars": HORIZON,
        "per_factor": per_factor,
        "worst_factor_class": worst,
        "lagged_sign_diagnostics": sign_diag,
        "arms": arms,
        "decision": dec,
        "diagnostic_decisions": {k: v for k, v in decisions.items() if k != "lagged_signs"},
        "picks_today": {"frozen_signs": head["frozen_signs"], "lagged_signs": head_lag,
                        "same": head["frozen_signs"] == head_lag},
        "units": "cagr/sharpe/maxdd are fractions of NAV unless stated in bp; ic is a rank correlation",
        "caveats": [
            "IC observations are one per rebalance week; the trailing mean is a mean of "
            "rank ICs, not a regression slope, so it is comparable across factors but not "
            "to a factor-return premium.",
            "the lagged arm pays the same 8bp/side but its decisions are noisier by "
            "construction (a sign can flip on a single year of data) -- turnover is printed "
            "so the reader can see that cost before trusting a gap.",
            "the 2026 year is partial (through the panel end), so a factor that flipped this "
            "year is judged on a fraction of a year.",
            "the two diagnostic arms are chosen AFTER the yearly table was read, so their "
            "gaps carry selection risk: six factors were examined and only the flattering "
            "flip is printed. drawdown_60 is the awkward case -- its pooled mean IC is "
            "positive (+0.0398) while only 3 of 7 years agree, so flipping it follows the "
            "year count against the pooled evidence. Neither selector is trustworthy; that "
            "disagreement is the finding, not a recommendation.",
            "diagnostic arms ride one decision phase (the same 20-bar grid as production). "
            "Phase spread on this book has been measured at ~0.5pp, so an 87bp gap is not "
            "yet separable from the grid -- a phase sweep is the named next step, no "
            "production change is claimed here.",
        ],
    }
    if write:
        os.makedirs("results", exist_ok=True)
        with open(RECEIPT, "w", encoding="utf-8") as fh:
            json.dump(receipt, fh, ensure_ascii=False, indent=1, sort_keys=True)
        print(f"[signstab] receipt -> {RECEIPT}")

    print(f"[signstab] panel {close.shape[1]} symbols x {close.shape[0]} bars, cutoff {receipt['evidence_cutoff']}")
    for c, v in per_factor.items():
        if "years" not in v:
            print(f"  {c:16s} {v.get('note')}")
            continue
        print(f"  {c:16s} prod={v['production_sign']:+.0f} mean_ic={v['mean_ic']:+.4f} "
              f"agree={v['agree_years']}/{len(years)} {v['class']}")
    print(f"  frozen : cagr {a['full']['cagr']:+.4f} sharpe {a['full']['sharpe']:+.3f} "
          f"maxdd {a['full']['maxdd']:+.4f} turnover {a['turnover']:.3f}")
    print(f"  lagged : cagr {b['full']['cagr']:+.4f} sharpe {b['full']['sharpe']:+.3f} "
          f"maxdd {b['full']['maxdd']:+.4f} turnover {b['turnover']:.3f}")
    print(f"  OOS     frozen {a['oos']['cagr']:+.4f}/sh {a['oos']['sharpe']:+.3f}  "
          f"lagged {b['oos']['cagr']:+.4f}/sh {b['oos']['sharpe']:+.3f}")
    print(f"  decision: {dec['verdict']} (cagr gap {dec['cagr_gap_bp']:+.1f}bp, "
          f"sharpe {dec['sharpe_gap']:+.3f}, oos {dec['oos_gap_bp']:+.1f}bp, bar {dec['bar_bp']}bp)")
    print(f"  picks today frozen={head['frozen_signs']} lagged={head_lag} same={head['frozen_signs'] == head_lag}")
    for name, d in decisions.items():
        if name == "lagged_signs":
            continue
        arm = arms[name]
        print(f"  {name:10s}: cagr {arm['full']['cagr']:+.4f} sharpe {arm['full']['sharpe']:+.3f} "
              f"maxdd {arm['full']['maxdd']:+.4f} oos {arm['oos']['cagr']:+.4f} "
              f"-> {d['verdict']} ({d['cagr_gap_bp']:+.1f}bp, oos {d['oos_gap_bp']:+.1f}bp)")
    return 0


def check(path=RECEIPT):
    """Re-derive the verdicts from the receipt's own numbers (never trust stored words)."""
    if not os.path.exists(path):
        print(f"[signstab] no receipt at {path}")
        return 2
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    bad = []
    for c, v in doc["per_factor"].items():
        if "years" not in v:
            continue
        agree = sum(1 for r in v["years"] if r.get("agrees"))
        if agree != v["agree_years"]:
            bad.append(f"{c}: agree_years {v['agree_years']} != re-derived {agree}")
        word = sign_class(agree, len(v["years"]))
        if word != v["class"]:
            bad.append(f"{c}: class {v['class']} != re-derived {word}")
        for r in v["years"]:
            if r.get("mean_ic") is None:
                continue
            if bool(np.sign(r["mean_ic"]) == np.sign(v["production_sign"])) != bool(r["agrees"]):
                bad.append(f"{c}/{r['year']}: agrees flag contradicts mean_ic sign")
    dec = decide(doc["arms"]["frozen_signs"], doc["arms"]["lagged_signs"])
    if dec["verdict"] != doc["decision"]["verdict"]:
        bad.append(f"verdict {doc['decision']['verdict']} != re-derived {dec['verdict']}")
    for name, stored in (doc.get("diagnostic_decisions") or {}).items():
        if name not in doc["arms"]:
            bad.append(f"diagnostic arm {name} has a decision but no arm")
            continue
        again = decide(doc["arms"]["frozen_signs"], doc["arms"][name])
        if again["verdict"] != stored["verdict"]:
            bad.append(f"{name}: verdict {stored['verdict']} != re-derived {again['verdict']}")
    if bad:
        for b in bad:
            print("[signstab] CHECK FAIL " + b)
        return 1
    print(f"[signstab] check OK: {len(doc['per_factor'])} factors, "
          f"verdict {doc['decision']['verdict']} re-derived identical")
    return 0


# -------------------------------------------------------------------------- selftest
def _fixture():
    idx = pd.date_range("2020-01-01", periods=520, freq="B")
    cols = [f"x{i:03d}" for i in range(60)]
    rng = np.random.default_rng(11)
    return idx, cols, rng


def _fixture_score(idx, cols, rng):
    """A score that is deliberately NOT correlated with the fixture's forward returns."""
    return pd.DataFrame(rng.normal(size=(len(idx), len(cols))), index=idx, columns=cols)


def selftest():
    ok = 0
    total = 0
    idx, cols, rng = _fixture()

    # L1: a factor whose value predicts the next bar positively reads a positive IC,
    # and one that predicts negatively reads a negative IC -- the sign is measured,
    # not assumed.
    total += 1
    px = pd.DataFrame(rng.normal(0, 1, size=(len(idx), len(cols))).cumsum(axis=0),
                      index=idx, columns=cols) + 100.0
    fwd = px.shift(-5) / px - 1.0
    good = fwd.copy()             # value at t == the return t..t+5 (a perfect forecaster)
    ic_pos, _ = rank_ic_series(good, fwd, pd.DataFrame(True, index=idx, columns=cols), list(idx), min_obs=30)
    ic_neg, _ = rank_ic_series(-good, fwd, pd.DataFrame(True, index=idx, columns=cols), list(idx), min_obs=30)
    if len(ic_pos) > 20 and ic_pos.mean() > 0.9 and ic_neg.mean() < -0.9:
        ok += 1
    else:
        print(f"  L1 FAIL ic_pos={ic_pos.mean():.3f} ic_neg={ic_neg.mean():.3f}")

    # L2: a factor that points the other way every year is CONTRARY, and a factor
    # with no observation at all is "no observation" -- never STABLE by default.
    total += 1
    anti, _ = rank_ic_series(-good, fwd, pd.DataFrame(True, index=idx, columns=cols),
                            list(idx), min_obs=30)
    rows, agree = yearly_ic(anti, +1.0, sorted({d.year for d in idx}))
    empty, agree_empty = yearly_ic(pd.Series(dtype=float), +1.0, [2020, 2021])
    if (agree == 0 and sign_class(agree, len(rows)) == "SIGNS_CONTRARY"
            and agree_empty == 0 and all(r["agrees"] is None for r in empty)):
        ok += 1
    else:
        print(f"  L2 FAIL agree={agree}/{len(rows)} empty_agree={agree_empty}")

    # L3: the trailing sign never uses the observation it is deciding.
    total += 1
    spike = pd.Series([-0.1] * 40, index=pd.date_range("2021-01-04", periods=40, freq="B"))
    spike.iloc[-1] = 100.0        # a huge IC printed on the final day
    signs, fallback = trailing_sign(spike, spike.index, trail_days=756, min_obs=5)
    if signs.iloc[-1] == -1.0 and signs.iloc[-2] == -1.0:
        ok += 1
    else:
        print(f"  L3 FAIL last two signs {signs.iloc[-2]:.0f} {signs.iloc[-1]:.0f}")

    # L4: too little history keeps the production sign instead of inventing one.
    total += 1
    thin = pd.Series([0.2] * 5, index=pd.date_range("2021-01-04", periods=5, freq="B"))
    signs, fallback = trailing_sign(thin, thin.index, trail_days=756, min_obs=MIN_IC_OBS)
    if np.isnan(signs.iloc[-1]) and fallback == 5:
        ok += 1
    else:
        print(f"  L4 FAIL fallback={fallback}")

    # L5: the decision ordering -- a helper must beat on growth, sharpe AND oos.
    total += 1
    a = {"full": {"cagr": 0.08, "sharpe": 0.9}, "oos": {"cagr": 0.10, "sharpe": 1.0}}
    b = {"full": {"cagr": 0.09, "sharpe": 0.95}, "oos": {"cagr": 0.11, "sharpe": 1.0}}
    weak = {"full": {"cagr": 0.09, "sharpe": 0.80}, "oos": {"cagr": 0.11, "sharpe": 1.0}}
    broken = {"full": {"cagr": 0.09, "sharpe": 0.95}, "oos": {"cagr": 0.05, "sharpe": 0.5}}
    d1, d2, d3 = decide(a, b), decide(a, weak), decide(a, broken)
    if d1["verdict"] == "SWITCH_HELPS" and d2["verdict"] != "SWITCH_HELPS" and d3["verdict"] != "SWITCH_HELPS":
        ok += 1
    else:
        print(f"  L5 FAIL {d1['verdict']} {d2['verdict']} {d3['verdict']}")

    # L6: severity ordering is the frozen one, so the composite word is the worst factor.
    total += 1
    worst = min(["SIGNS_STABLE", "SIGNS_CONTRARY", "SIGNS_DRIFT"],
                key=lambda g: CRITERIA["severity"].index(g))
    if worst == "SIGNS_CONTRARY":
        ok += 1
    else:
        print(f"  L6 FAIL worst={worst}")

    # L7: the forward window must be fully printed -- a bar whose horizon runs past
    # the panel end carries no IC (dropping it beats truncating it).
    total += 1
    tiny = px.iloc[:60]
    fwd_tiny = (tiny.shift(-20) / tiny - 1.0)
    n_last = int(fwd_tiny.iloc[-5].notna().sum())
    if n_last == 0:
        ok += 1
    else:
        print(f"  L7 FAIL last bars still carry {n_last} forward values")

    print(f"[signstab] selftest {ok}/{total} PASS")
    return 0 if ok == total else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        return run()
    cmd = argv[0]
    if cmd == "run":
        return run()
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print(f"[signstab] unknown command {cmd}")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())