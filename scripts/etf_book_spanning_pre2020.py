"""Does the four-beta explanation survive OUTSIDE the ETF boom window?

r1310 asked whether the shipped book still has an intercept after the four liquid
exposures an account could hold instead (gold 518880 / Nasdaq QDII 513100 / CSI300
510300 / bond 511010), and r1311 asked the same of the staggered 6+6 book. Both answers
live in 2020-01..2026-10 -- the window in which the ETF panel grew from a handful of funds
to ~1,500 and in which the published book made its money. A regression that only holds in
the window it was fitted in is a description, not an edge, so the same test is run on the
pre-boom window the published work never looked at (2015-01-01..2019-12-31, the U_pre
universe of etf_book_pre2020).

Nothing is re-implemented. The panel, the universe mask, the truncation and both engines
are the published ones (etf_book_pre2020_wf's own call path); the regression is
etf_book_spanning.arm_from_returns, the single place a span regression is fitted in this
repo, called with `is_end` so the IS/OOS split is the window's own (2015-2017 / 2018-2019)
rather than the 2020+ face's 2023 split.

Control before any quotation (r1297 rule, third consumer): the single-sleeve arm priced
here must reproduce the published pre-2020 N12 overlay cell
(results/etf_book_pre2020_wf.json:full_window_arm_stats.fixed_n12_vt.cagr) within 0.5pp.
If it does not, this script is pricing a different book and every delta below is a code
difference rather than a period result -- so it exits 3 instead of quoting.

Readings published together, never one alone:
  (a) each arm's alpha / t / loadings / R^2 on the 2015-2019 window, with IS and OOS
  (b) the same four spans held as one equal-weight basket on the book's own decision grid
      and 10bp cost, so the intercept has a comparison a human could have bought
  (c) the eligible-name count per decision, because a top-12 choice out of 20 names is not
      a cross-section (etf_book_pre2020's own caveat, carried here)

Usage (cwd = repo root):
    python scripts/etf_book_spanning_pre2020.py run
    python scripts/etf_book_spanning_pre2020.py --selftest
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

import etf_book_production as P
import etf_book_pre2020 as W
import etf_book_pre2020_wf as WF
import etf_book_spanning as SP
import etf_book_stagger_publish as S
import etf_composite_pf as E
import etf_robust_pf as R

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
RESULT = os.path.join(P.E.PATHS.data_dir, "..", "results", "etf_book_spanning_pre2020.json")
PUB_WF = os.path.join(_REPO, "results", "etf_book_pre2020_wf.json")
PUB_STAGGER = os.path.join(_REPO, "results", "etf_book_stagger_publish.json")

START = "2015-01-01"
END = "2019-12-31"
IS_END = "2017-12-31"
REBAL = 20
N_HOLD = 12
COST = 0.0010
VT = 0.08
TOL_PP = 0.5          # control tolerance, pinned as in the two faces it borrows from


def pre_panel():
    """The published pre-2020 panel: production gate, U_pre mask, truncation, rebuilt score.

    Identical call path to etf_book_pre2020_wf.run -- the score is rebuilt on the 193
    surviving names rather than subset after ranking 1,499, otherwise the ranking itself is
    computed on funds that did not exist yet.
    """
    close, openp, amt, _score, _cls, n_flip = P.prep_panel()
    _c, _o, _a, feats = E.build_panel()
    pre = W.universe_pre(close)
    cols = [c for c in close.columns if c in set(pre)]
    c, o, a, f = W.truncate(
        [close[cols], openp[cols], amt[cols],
         {k: v.reindex(columns=cols) for k, v in feats.items() if hasattr(v, "columns")}],
        None, END)
    score = E.build_score(c, a, f)
    return c, o, a, score, len(pre), len(cols), int(n_flip)


def span_frames():
    """Span closes/opens, flip-repaired and truncated to the window's end."""
    _sc, so, flips = SP.load_span_frames()
    (so2,) = W.truncate([so], None, END)
    return so2, int(flips)


def price_arms(c, o, a, score, start=START):
    """Both arms through the published engines. Returns (single, staggered) curves."""
    single, _turns = R.open_to_open_equity(
        c, o, a, score, REBAL, N_HOLD, COST, vol_target=VT, start=start)
    cfg = stagger_config()
    st, _st_turns, _trades = S.run_staggered(
        c, o, a, score, rebal=cfg["rebal"], n_total=cfg["n_total"], cost=cfg["cost"],
        vol_target=cfg["vol_target"], start=start)
    return single, st, cfg


def stagger_config():
    """The published stagger rule, read off its own artefact (r1288: never a literal)."""
    try:
        with open(PUB_STAGGER, encoding="utf-8") as f:
            m = json.load(f)["machinery"]
        return {"n_total": int(m["n_total"]), "rebal": int(m["rebal"]),
                "vol_target": float(m["vol_target"]),
                "cost": float(m["cost_bp_per_side"]) / 1e4,
                "source": "results/etf_book_stagger_publish.json:machinery"}
    except Exception as e:                                       # noqa: BLE001
        return {"n_total": N_HOLD, "rebal": REBAL, "vol_target": VT, "cost": COST,
                "source": "fallback default (%s: %s)" % (type(e).__name__, e)}


def control(single_ser):
    """Assert this script prices the published pre-2020 book before quoting any alpha."""
    out = {"source": "results/etf_book_pre2020_wf.json:full_window_arm_stats.fixed_n12_vt",
           "tolerance_pp": TOL_PP}
    try:
        with open(PUB_WF, encoding="utf-8") as f:
            pub = json.load(f)["full_window_arm_stats"]["fixed_n12_vt"]["cagr"]
    except Exception as e:                                       # noqa: BLE001
        out.update({"status": "published arm unreadable", "error": type(e).__name__})
        return out
    got = (A_stats(single_ser) or {}).get("cagr")
    if got is None:
        out.update({"status": "arm not priced"})
        return out
    d = abs(got - pub) * 100.0
    out.update({"mine": round(got, 4), "published": round(float(pub), 4),
                "delta_pp": round(d, 3), "within_0p5pp": bool(d <= TOL_PP)})
    return out


def A_stats(ser):
    import etf_equity_alpha as A
    if ser is None or len(ser) < 40:
        return None
    return {k: A.stats2(ser, "arm").get(k)
            for k in ("cagr", "sharpe", "maxdd", "vol", "years")}


def regression(curve, sr, keys, is_end=IS_END):
    """One arm through the repo's single regression path, with this window's own split."""
    if curve is None or len(curve) < 60:
        return {"status": "arm_not_priced"}
    return SP.arm_from_returns(curve.pct_change().dropna(), sr, keys,
                               equity=curve, is_end=is_end)


def span_portfolios(span_open, keys, first_bar):
    """Each span arm and one equal-weight basket on the book's grid and cost."""
    out = {}
    for key, code, label in SP.SPAN:
        ser, turns = SP.basket(span_open, [code], REBAL, COST)
        row = {"code": code, "label": label,
               "turnover_total": round(turns, 3) if ser is not None else None}
        if ser is not None:
            row.update(SP._pstats(ser[ser.index >= first_bar], key) or {})
        out[key] = row
    sb, turns = SP.basket(span_open, keys, REBAL, COST)
    row = {"codes": list(keys), "turnover_total": round(turns, 3) if sb is not None else None}
    if sb is not None:
        row.update(SP._pstats(sb[sb.index >= first_bar], "ew") or {})
    out["equal_weight_basket"] = row
    return out


def verdict(arms):
    """Word the period question from the two intercepts, not from what we hoped for."""
    def t_of(name):
        return ((arms.get(name) or {}).get("full") or {}).get("alpha_t")
    def a_of(name):
        return ((arms.get(name) or {}).get("full") or {}).get("alpha_annual")

    ts, tg = t_of("single"), t_of("staggered")
    if ts is None and tg is None:
        return "neither arm could be priced on this window"
    if (ts or 0) >= 2.0 and (tg or 0) >= 2.0:
        return ("both arms keep an intercept outside 2020-2026 (t %.2f single / %.2f "
                "staggered) -- the four exposures do not explain the book in either window"
                % (ts, tg))
    if (tg or 0) >= 2.0 > (ts or 0):
        return ("the staggered arm keeps an intercept where the single sleeve does not "
                "(t %.2f vs %.2f, %.2fpp/yr apart) on this window -- one window, one arm: a "
                "hypothesis, not a promotion" % (tg, ts,
                                                 ((a_of("staggered") or 0) - (a_of("single") or 0)) * 100))
    if (ts or 0) >= 2.0 > (tg or 0):
        return ("the single sleeve keeps an intercept here and the staggered arm does not "
                "(t %.2f vs %.2f) -- the split clock is the arm that needs the boom window"
                % (ts, tg))
    return ("no intercept survives outside 2020-2026 (t %.2f single / %.2f staggered): the "
            "published alpha is a property of the window, not of the book" % (ts, tg))


def build(c, o, a, score, span_open=None, single=None, stagger=None, cfg=None,
          universe=None):
    """Pure function of the priced arms: regressions, span comparisons, verdict."""
    keys = [code for _k, code, _l in SP.SPAN]
    if span_open is None:
        span_open, _flips = span_frames()
    if single is None or stagger is None:
        single, stagger, cfg = price_arms(c, o, a, score)
    sr = SP.span_returns(span_open, keys)
    arms = {"single": regression(single, sr, keys),
            "staggered": regression(stagger, sr, keys)}
    single_stats = A_stats(single)
    stagger_stats = A_stats(stagger)
    if single_stats:
        arms["single"]["stats"] = single_stats
    if stagger_stats:
        arms["staggered"]["stats"] = stagger_stats
    first = min([x["window"][0] for x in arms.values() if x.get("window")] or [START])
    out = {
        "schema": "etf_book_spanning_pre2020/v1",
        "question": ("do gold/Nasdaq/CSI300/bond explain the book outside the 2020-2026 "
                     "ETF-boom window?"),
        "window": [START, END],
        "is_end": IS_END,
        "config": {"n_hold": N_HOLD, "rebal": REBAL, "vol_target": VT,
                   "cost_bp_per_side": round(COST * 1e4, 2),
                   "stagger": {k: v for k, v in (cfg or {}).items() if k != "source"},
                   "stagger_source": (cfg or {}).get("source")},
        "universe": universe or {},
        "arms": arms,
        "span_portfolios": span_portfolios(span_open, keys, first),
        "control": control(single),
        "caveats": [
            "one window, one universe: U_pre is itself survival-filtered (dead funds are "
            "absent from the panel), so a pass here is weaker evidence than it looks and a "
            "failure is stronger",
            "the pre-2020 cross-section is small (eligible names per decision are published "
            "in the panel block); a top-12 pick out of 20 names is the universe, not a "
            "ranking",
            "daily OLS without HAC correction, same basis as results/etf_book_spanning.json",
            "span arms carry the same flip repair as the book's panel",
            "exploratory: no preregistration, no verdict booking, no member file touched",
        ],
    }
    out["verdict"] = verdict(arms)
    return out


def run():
    c, o, a, score, n_pre, n_cols, n_flip = pre_panel()
    print("panel U_pre=%d cols=%d shape=%s last=%s flips=%d"
          % (n_pre, n_cols, c.shape, c.index[-1].date(), n_flip), flush=True)
    single, stagger, cfg = price_arms(c, o, a, score)
    print("arms: single %d bars -> %.2f%%   staggered %d bars -> %.2f%%"
          % (len(single), (A_stats(single) or {}).get("cagr", 0) * 100,
             len(stagger), (A_stats(stagger) or {}).get("cagr", 0) * 100), flush=True)
    out = build(c, o, a, score, single=single, stagger=stagger, cfg=cfg,
                universe={"U_pre": n_pre, "cols": n_cols, "flips_repaired": n_flip,
                          "shape": list(c.shape),
                          "last_bar": str(c.index[-1].date())})
    print("control:", json.dumps(out["control"], sort_keys=True), flush=True)
    out["_control_ok"] = bool(out["control"].get("within_0p5pp"))
    if not out["_control_ok"]:
        print("CONTROL MISMATCH -- alphas are not quotable", flush=True)
    os.makedirs(os.path.dirname(RESULT), exist_ok=True)
    with open(RESULT, "w", encoding="utf-8", newline="\n") as f:
        json.dump({k: v for k, v in out.items() if not k.startswith("_")}, f,
                  indent=1, ensure_ascii=False)
    for name in ("single", "staggered"):
        arm = out["arms"][name]
        f_ = arm.get("full") or {}
        print("%-9s alpha %7.2f%%/yr t=%5.2f r2=%.2f resid_vol %5.2f%% "
              "(IS t=%5.2f / OOS t=%5.2f)"
              % (name, (f_.get("alpha_annual") or 0) * 100, f_.get("alpha_t") or 0,
                 f_.get("r2") or 0, (f_.get("resid_vol_annual") or 0) * 100,
                 (arm.get("is") or {}).get("alpha_t") or 0,
                 (arm.get("oos") or {}).get("alpha_t") or 0), flush=True)
    ew = (out["span_portfolios"].get("equal_weight_basket") or {}).get("cagr")
    print("equal-weight four-span basket on this window: %s"
          % ("%.2f%%/yr" % (ew * 100) if ew is not None else "not priced"), flush=True)
    print("verdict:", out["verdict"], flush=True)
    print("wrote", os.path.relpath(RESULT, _REPO), flush=True)
    return 0 if out["_control_ok"] else 3


# --------------------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------------------

def _fixture(n_sym=24, n_bars=460, seed=11):
    """Synthetic panel: enough history for MIN_HIST, drifting names, liquid amounts."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2015-01-05", periods=n_bars)
    cols = ["s%02d" % i for i in range(n_sym)]
    drift = np.linspace(0.0006, -0.0002, n_sym)
    rets = drift + rng.normal(0.0, 0.010, size=(n_bars, n_sym))
    close = pd.DataFrame(100.0 * np.cumprod(1.0 + rets, axis=0), index=dates, columns=cols)
    openp = close.shift(1).fillna(close.iloc[0])
    amt = pd.DataFrame(5.0e8, index=dates, columns=cols)
    score = pd.DataFrame(rng.normal(size=(n_bars, n_sym)), index=dates, columns=cols)
    return close, openp, amt, score


def selftest():
    ok = 0
    total = 0

    def chk(label, cond, detail=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print("[PASS] %s%s" % (label, (" | " + detail if detail else "")))
        else:
            print("[FAIL] %s%s" % (label, (" | " + detail if detail else "")))

    import etf_equity_alpha as A

    # L1 alpha recovered from a constructed series: y = c + 0.5*x1, x2..x4 noise-free zero
    idx = pd.bdate_range("2015-01-05", periods=800)
    x1 = pd.Series(np.random.default_rng(3).normal(0, 0.01, 800), index=idx)
    span = pd.DataFrame({"a": x1, "b": 0.0, "c": 0.0, "d": 0.0})
    # zero-variance regressors would be refused by ols(); give them tiny independent noise
    rng = np.random.default_rng(4)
    for k in ("b", "c", "d"):
        span[k] = rng.normal(0, 0.01, 800)
    y = 0.0002 + 0.5 * span["a"]
    fit = SP.arm_from_returns(y, span.set_index(idx), ["a", "b", "c", "d"],
                              is_end=IS_END)
    chk("regression recovers a planted intercept", abs(fit["full"]["alpha_annual"] - 0.0504) < 0.01,
        "alpha %.4f" % fit["full"]["alpha_annual"])
    chk("regression recovers the planted loading", abs(fit["full"]["betas"]["a"] - 0.5) < 1e-6,
        "beta %.6f" % fit["full"]["betas"]["a"])

    # L2 the IS/OOS split follows is_end, not the 2020-face default
    chk("is_end honoured on the split", fit["obs"]["is"] + fit["obs"]["oos"] == fit["obs"]["full"],
        "is=%d oos=%d" % (fit["obs"]["is"], fit["obs"]["oos"]))
    early = SP.arm_from_returns(y, span.set_index(idx), ["a", "b", "c", "d"], is_end="2016-03-01")
    chk("a different is_end moves the split",
        early["obs"]["oos"] > fit["obs"]["oos"],
        "oos %d > %d" % (early["obs"]["oos"], fit["obs"]["oos"]))

    # L3 identity control: y == the span itself leaves no intercept
    ident = SP.arm_from_returns(span["a"], span.set_index(idx), ["a", "b", "c", "d"],
                                is_end=IS_END)
    chk("identity control: no residual intercept", abs(ident["full"]["alpha_annual"]) < 1e-9,
        "alpha %.2e" % ident["full"]["alpha_annual"])

    # L4 short overlap refused rather than fitted
    short = SP.arm_from_returns(y.iloc[:20], span.set_index(idx).iloc[:20],
                                ["a", "b", "c", "d"], is_end=IS_END)
    chk("short overlap refused", short.get("status") == "insufficient_overlap",
        str(short.get("status")))

    # L5 both arms really are priced, and the stagger clock changes the curve
    close, openp, amt, score = _fixture()
    single, stagger, cfg = price_arms(close, openp, amt, score, start="2015-01-05")
    chk("single arm produced a moving curve", len(single) > 100 and single.iloc[-1] != single.iloc[0],
        "bars=%d end=%.5f" % (len(single), float(single.iloc[-1])))
    chk("stagger arm produced a moving curve",
        len(stagger) > 100 and stagger.iloc[-1] != stagger.iloc[0],
        "bars=%d end=%.5f" % (len(stagger), float(stagger.iloc[-1])))

    # L6 control: an in-tolerance price passes, a planted 2pp drift is refused
    class _Fake:
        def __init__(self, cagr):
            self.cagr = cagr
    real = control.__globals__
    try:
        with open(PUB_WF, encoding="utf-8") as f:
            pub = json.load(f)["full_window_arm_stats"]["fixed_n12_vt"]["cagr"]
    except Exception:                                            # noqa: BLE001
        pub = 0.0497
    ser = pd.Series(np.linspace(1.0, (1.0 + pub) ** 2.0, 500),
                    index=pd.bdate_range("2015-01-05", periods=500))
    good = control(ser)
    chk("control passes a matching arm", good.get("within_0p5pp") is True,
        "delta_pp %s" % good.get("delta_pp"))
    ser2 = pd.Series(np.linspace(1.0, (1.0 + pub + 0.04) ** 2.0, 500),
                     index=pd.bdate_range("2015-01-05", periods=500))
    bad = control(ser2)
    chk("control refuses a 4pp drift", bad.get("within_0p5pp") is False,
        "delta_pp %s" % bad.get("delta_pp"))

    # L7 verdict is read off the numbers, in all four states
    def arm(t):
        return {"full": {"alpha_t": t, "alpha_annual": 0.05 if t > 0 else -0.01}}
    chk("verdict: both survive", "both arms keep an intercept" in
        verdict({"single": arm(2.5), "staggered": arm(2.1)}))
    chk("verdict: only staggered", "staggered arm keeps an intercept" in
        verdict({"single": arm(1.1), "staggered": arm(2.4)}))
    chk("verdict: only single", "single sleeve keeps an intercept" in
        verdict({"single": arm(2.4), "staggered": arm(0.9)}))
    chk("verdict: neither", "no intercept survives" in
        verdict({"single": arm(1.1), "staggered": arm(1.0)}))

    # L8 stagger configuration is read from the artefact, never defaulted in silence
    cfg2 = stagger_config()
    chk("stagger rule read off its artefact",
        cfg2["source"].startswith("results/etf_book_stagger_publish.json"),
        cfg2["source"])

    print("%d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lstrip("-")
    if cmd == "selftest":
        return selftest()
    if cmd in ("run", "go"):
        return run()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))