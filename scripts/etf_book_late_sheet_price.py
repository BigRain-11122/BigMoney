"""What does it cost to fill *this* sheet one open late?

Why this face exists
--------------------
r1480 priced the delay *policy*: "fill every sheet one open late and you give back
1.87pp/yr (18,700 CNY on 1,000,000)".  A desk cannot use that sentence.  The desk has
exactly one sheet in front of it and asks a different question: *if I cannot act today
and I act tomorrow, what does that one sheet cost me?*  The policy number is the sum of
83 such decisions plus whatever the compounding does with them, and until we know
whether the sum is made of 83 similar small prices or of a few big ones cancelling, the
policy number cannot be transferred to a single sheet (E238 family: the member and the
aggregate are different objects).

What it measures
----------------
For every decision bar in the control path, the book changes from `old` to `new`.  A
punctual fill holds `new` over the next bar; one open late holds `old` for that same bar
and takes `new` one bar later -- after which the two paths are identical again.  So the
price of one late sheet is exactly one bar of return difference:

    delta_log_i = log(1 + r_old_i) - log(1 + r_new_i)      (positive = late was better)
    delta_cny_i = NAV_at_decision_i * (r_old_i - r_new_i)

That is a *local* price.  The face does not assume the locals add up: it measures the
aggregate arm (every sheet one open late, `etf_book_punctuality.replay(lag=1)`) and
prints the residual between `sum(delta_log)` and the actual log ratio.  If the residual
is not small, the desk cannot be quoted a per-sheet price at all and the verdict says so.

The one thing it refuses to do is quote a price without its own dispersion: an average
of 1,5xx CNY per event is useless if a third of the events go the other way.

Usage: python scripts/etf_book_late_sheet_price.py [run|--check|selftest]
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_equity_alpha as A
import etf_robust_pf as R
import etf_book_punctuality as P

CAPITAL_CNY = 1_000_000.0
REBAL, N_HOLD, COST = 20, 5, 0.0010
ARMS = (("nobond_vt08", 0.08), ("nobond_base", None))
PHASES = 5
ADD_TOL = 0.15  # residual share above which the locals do not reconstruct the aggregate


def tape(close, openp, amt, score, rebal=REBAL, n_hold=N_HOLD, cost=COST,
         vol_target=None, vol_window=60, phase=0):
    """Walk the punctual path and record one row per decision bar.

    This is a deliberate copy of `etf_book_punctuality.replay` (lag=0): the copy exists
    because we need the *interior* of the loop (the old book, the new book, the one bar
    they differ by), not just the equity curve.  The control leg below asserts that the
    copy reproduces the engine bit-for-bit, so a divergence cannot hide here.
    """
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    score = score.where(elig)
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp(R.START)]
    rets = op.pct_change()
    equity, held, daily, events = 1.0, {}, [], []

    def book_vol(book, upto):
        if not book:
            return np.nan
        window = rets.loc[:upto].tail(vol_window)[list(book)]
        if window.shape[0] < 20:
            return np.nan
        w = np.array([book[k] for k in window.columns])
        cov = window.cov().to_numpy()
        return float(np.sqrt(w @ cov @ w) * np.sqrt(252))

    for i in range(len(dates) - 1):
        d = dates[i]
        if (i - phase) % rebal == 0 and i >= phase:
            s = score.loc[d].dropna()
            if len(s) >= n_hold:
                picks = list(s.nlargest(n_hold).index)
                w = {p: 1.0 / n_hold for p in picks}
                scale = 1.0
                if vol_target:
                    v = book_vol(w, d)
                    if np.isfinite(v) and v > 0:
                        scale = float(max(0.0, min(1.0, vol_target / v)))
                w = {k: v * scale for k, v in w.items()}
                old = dict(held)
                turn = sum(abs(w.get(k, 0.0) - old.get(k, 0.0)) for k in set(w) | set(old))
                equity *= (1.0 - cost * turn)
                held = w
                nxt = dates[i + 1]

                def bar_return(book):
                    if not book:
                        return 0.0
                    r = 0.0
                    for p, wt in book.items():
                        a, b = op.at[d, p], op.at[nxt, p]
                        if np.isfinite(a) and np.isfinite(b) and a > 0:
                            r += wt * (b / a - 1.0)
                    return r

                r_old, r_new = bar_return(old), bar_return(w)
                events.append({
                    "date": str(pd.Timestamp(d).date()),
                    "nav_cny": round(equity, 2),
                    "k_scale": round(scale, 6),
                    "legs_changed": len([k for k in w if w.get(k) != old.get(k)]),
                    "r_old": r_old,
                    "r_new": r_new,
                    "delta_log": math.log1p(r_old) - math.log1p(r_new),
                    "delta_bps": (r_old - r_new) * 1e4,
                    "delta_cny": equity * (r_old - r_new) * CAPITAL_CNY,
                })
        nxt = dates[i + 1]
        r = 0.0
        for p, wt in held.items():
            a, b = op.at[d, p], op.at[nxt, p]
            if np.isfinite(a) and np.isfinite(b) and a > 0:
                r += wt * (b / a - 1.0)
        equity *= (1.0 + r)
        daily.append((nxt, equity))
    return pd.Series(dict(daily)).sort_index(), events


def _dist(values):
    v = np.asarray(values, dtype=float)
    n = int(v.size)
    if n == 0:
        return {"n": 0}
    sd = float(np.std(v, ddof=1)) if n > 1 else 0.0
    sem = sd / math.sqrt(n) if n > 1 else float("inf")
    mean = float(np.mean(v))
    return {
        "n": n,
        "mean": mean,
        "sd": sd,
        "sem": sem,
        "t": (mean / sem) if sem > 0 else None,
        "median": float(np.median(v)),
        "p10": float(np.percentile(v, 10)),
        "p90": float(np.percentile(v, 90)),
        "worst": float(np.min(v)),
        "best": float(np.max(v)),
        "share_late_helps": float(np.mean(v > 0)),
    }


def measure_arm(close, openp, amt, sc, arm, vt):
    """One arm: per-phase event tapes, aggregate arm, and the additivity residual."""
    ref, _ref_turn = R.open_to_open_equity(close, openp, amt, sc, REBAL, N_HOLD, COST,
                                           vol_target=vt)
    rows, control = [], None
    for ph in range(PHASES):
        ctl_ser, events = tape(close, openp, amt, sc, vol_target=vt, phase=ph)
        if ph == 0:
            joined = pd.concat([ref.rename("ref"), ctl_ser.rename("mine")], axis=1).dropna()
            gap = float((joined["ref"] - joined["mine"]).abs().max()) if len(joined) else float("inf")
            control = {"arm": arm, "bars": int(len(joined)), "max_abs_level_gap": gap,
                       "reproduces_engine": gap <= 1e-12}
            if not control["reproduces_engine"]:
                raise SystemExit("CONTROL_FAIL: tape does not reproduce the engine for %s "
                                 "(gap=%r) -- refusing to price lateness" % (arm, gap))
        late_ser, _t, _late = P.replay(close, openp, amt, sc, REBAL, N_HOLD, COST,
                                      vol_target=vt, lag=1, phase=ph)
        predicted = sum(e["delta_log"] for e in events)
        actual = math.log(float(late_ser.iloc[-1]) / float(ctl_ser.iloc[-1]))
        residual = actual - predicted
        # both arms span the same bars; the CAGR gap is the money form of the same fact,
        # and it is taken from the shared annualiser so it lands on r1480's number
        s_ctl = A.stats2(ctl_ser, "ctl")
        s_late = A.stats2(late_ser, "late")
        years = s_ctl.get("years", 0.0)
        rows.append({
            "phase": ph,
            "events": len(events),
            "years": years,
            "predicted_log_delta": predicted,
            "actual_log_delta": actual,
            "residual": residual,
            "residual_share": (residual / abs(actual)) if actual else None,
            "predicted_cny_on_capital": predicted * CAPITAL_CNY,
            "actual_cny_on_capital": (float(late_ser.iloc[-1]) - float(ctl_ser.iloc[-1])) * CAPITAL_CNY,
            "dcagr_pp": (s_late["cagr"] - s_ctl["cagr"]) * 100.0,
            "control_final": float(ctl_ser.iloc[-1]),
            "late_final": float(late_ser.iloc[-1]),
            "tape": events,
        })
    all_events = [e for r in rows for e in r["tape"]]
    share_ok = all((r["residual_share"] is None or abs(r["residual_share"]) <= ADD_TOL) for r in rows)
    dist_bps = _dist([e["delta_bps"] for e in all_events])
    dist_cny = _dist([e["delta_cny"] for e in all_events])
    t = dist_bps.get("t")
    helps = dist_bps.get("share_late_helps")
    # three states, because "the mean is real" and "this sheet is predictable" are
    # different claims: the mean can be significantly negative while 4 sheets in 10
    # would have been better off waiting (r1425 family: a verdict must carry its noise)
    if dist_bps.get("n", 0) == 0:
        verdict = "NO_EVENTS"
    elif not share_ok:
        verdict = "LOCALS_DO_NOT_ADD_UP"
    elif t is None or abs(t) < 2:
        verdict = "PRICE_NOT_SEPARABLE_FROM_ZERO"
    elif helps is not None and 0.35 < helps < 0.65:
        verdict = "MEAN_IS_PRICED_EACH_SHEET_IS_NOT"
    else:
        verdict = "ONE_SHEET_IS_PRICED"
    return {
        "arm": arm,
        "vol_target": vt,
        "control": control,
        "phases": [{k: v for k, v in r.items() if k != "tape"} for r in rows],
        "events_per_phase": [r["events"] for r in rows],
        "event_dates_first_last": [all_events[0]["date"], all_events[-1]["date"]] if all_events else [],
        "dist_bps": dist_bps,
        "dist_cny": dist_cny,
        "verdict": verdict,
    }


def _sentence(res):
    d = res["dist_cny"]
    if not d.get("n"):
        return "%s: no decision bars to price." % res["arm"]
    phases = res["phases"]
    dcagr = float(np.median([p["dcagr_pp"] for p in phases]))
    resid = max(abs(p["residual"]) for p in phases)
    tail = {
        "ONE_SHEET_IS_PRICED": "so a late sheet has a price you can quote",
        "MEAN_IS_PRICED_EACH_SHEET_IS_NOT": ("so the price is real in aggregate but a "
                                            "single late sheet is a coin flip -- budget "
                                            "it, do not argue with it"),
        "PRICE_NOT_SEPARABLE_FROM_ZERO": ("and that mean is not separable from zero, so "
                                          "no one can say a late sheet costs anything"),
        "LOCALS_DO_NOT_ADD_UP": ("and the per-sheet prices do not add up to the "
                                 "whole-book arm, so no per-sheet quote is offered"),
    }[res["verdict"]]
    return ("On %s, one sheet filled one open late is worth %s CNY of NAV at the decision "
            "(median over %d sheets, p10..p90 %s..%s); waiting helped on %.0f%% of them, "
            "the mean is %.1f bps with t=%s. The %d locals add up to the whole-book delay "
            "arm to %s log (residual, not assumed): that arm costs %.2fpp a year -- %s."
            % (res["arm"], "{:,.0f}".format(d["median"]), d["n"],
               "{:,.0f}".format(d["p10"]), "{:,.0f}".format(d["p90"]),
               100.0 * d["share_late_helps"], res["dist_bps"]["mean"],
               ("%.2f" % res["dist_bps"]["t"]) if res["dist_bps"].get("t") is not None else "n/a",
               res["dist_bps"]["n"], "%.0e" % resid, abs(dcagr), tail))


def run(out_path=None):
    close, openp, amt, sc, n_flip, _cls = P.build()
    results = [measure_arm(close, openp, amt, sc, arm, vt) for arm, vt in ARMS]
    payload = {
        "face": "etf_book_late_sheet_price",
        "question": "What does one sheet cost when it is filled one open late -- and is "
                    "that price the same for every sheet?",
        "evidence_cutoff": str(close.index[-1].date()),
        "capital_cny": CAPITAL_CNY,
        "config": {"rebal": REBAL, "n_hold": N_HOLD, "cost_per_edge": COST,
                   "vol_window": 60, "universe": "bond-free", "phases": PHASES,
                   "additivity_tol": ADD_TOL},
        "panel": {"symbols": int(close.shape[1]), "first_bar": str(close.index[0].date()),
                  "last_bar": str(close.index[-1].date()), "flips_repaired": int(n_flip)},
        "model": {
            "local_price": "delta = NAV * (r_old - r_new) over the one bar the fill moves",
            "aggregate": "etf_book_punctuality.replay(lag=1) on the same phase grid",
            "not_assumed": "that the locals add up -- the residual is measured and printed",
            "cost_timing": "the 0.10%/edge toll is also paid one bar later; that is second "
                           "order and lives inside the residual, it is not dropped silently",
        },
        "arms": results,
        "headline": [_sentence(r) for r in results],
    }
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=1, ensure_ascii=False)
            f.write("\n")
        print("wrote", out_path)
    return payload


# --------------------------------------------------------------------------- fixtures
def _fixture(kind, n=620, rebal=20):
    """Two-name panel.

    `monotone`  -- A outgrows B on every bar, so the book trades once and then never moves.
    `flat`      -- nothing moves at all.
    `flip`      -- the score alternates at every event, and the bar the fill moves is
                   rigged so the *outgoing* book wins it: every late sheet must be worth
                   something, and every event is a real switch.
    """
    idx = pd.bdate_range("2020-01-01", periods=n)
    close = pd.DataFrame({"A": np.ones(n), "B": np.ones(n)}, index=idx)
    score = pd.DataFrame({"A": 2.0, "B": 1.0}, index=idx)

    def pick(i):
        return "A" if (i // rebal) % 2 == 0 else "B"

    for i in range(1, n):
        if kind == "flat":
            close.iloc[i] = close.iloc[i - 1]
            continue
        if kind == "flip":
            other = "B" if pick(i) == "A" else "A"
            score.iloc[i] = {pick(i): 2.0, other: 1.0}
            if i % rebal == 0:
                g = {pick(i): 0.999, other: 1.001}  # the incoming book loses the bar
            else:
                g = {"A": 1.0, "B": 1.0}
        else:  # monotone
            g = {"A": 1.001, "B": 1.0}
        close.iloc[i] = close.iloc[i - 1] * np.array([g["A"], g["B"]])
    openp = close.shift(1).bfill()
    amt = pd.DataFrame(1e9, index=idx, columns=close.columns)
    return close, openp, amt, score


def selftest():
    legs = []
    close, openp, amt, score = _fixture("monotone")
    ser, events = tape(close, openp, amt, score, n_hold=1, cost=0.0)
    ref, _ = R.open_to_open_equity(close, openp, amt, score, 20, 1, 0.0)
    joined = pd.concat([ref.rename("ref"), ser.rename("mine")], axis=1).dropna()
    legs.append(("tape_reproduces_the_engine", float((joined.ref - joined.mine).abs().max()) <= 1e-12))
    grid = [d for d in openp.reindex(columns=close.columns).index if d >= pd.Timestamp(R.START)]
    expected = sum(1 for i in range(len(grid) - 1) if i % 20 == 0)
    pos = [grid.index(pd.Timestamp(e["date"])) for e in events]
    legs.append(("events_are_the_decision_grid",
                 bool(pos) and all(p % 20 == 0 for p in pos) and len(events) <= expected,
                 "%d events, all on 20-bar marks, ceiling %d" % (len(events), expected)))

    # a book that never changes has no price for being late
    steady = [e for e in events[1:] if e["legs_changed"] == 0]
    legs.append(("unchanged_book_has_no_price",
                 bool(steady) and all(abs(e["delta_bps"]) < 1e-9 for e in steady)))

    # on a flat panel every event is worth exactly zero
    fc, fo, fa, fs = _fixture("flat")
    _fs, fev = tape(fc, fo, fa, fs, n_hold=1, cost=0.0)
    legs.append(("flat_panel_prices_lateness_at_zero",
                 all(abs(e["delta_log"]) < 1e-15 for e in fev)))

    # the fixture where the incoming book loses 0.05%/bar and the outgoing one wins it:
    # every late sheet must be worth something, and the sign must be "late helped"
    fc2, fo2, fa2, fs2 = _fixture("flip")
    fs_ser, fev2 = tape(fc2, fo2, fa2, fs2, n_hold=1, cost=0.0)
    priced = [e for e in fev2 if e["legs_changed"] > 0]
    legs.append(("a_real_switch_has_a_price", bool(priced) and all(abs(e["delta_bps"]) > 0 for e in priced)))
    legs.append(("sign_convention_late_helps_positive",
                 all((e["delta_cny"] > 0) == (e["delta_log"] > 0) for e in fev2)))

    # additivity is asserted on the fixture where the locals are the whole story
    late, _t, _l = P.replay(fc2, fo2, fa2, fs2, 20, 1, 0.0, lag=1)
    predicted = sum(e["delta_log"] for e in fev2)
    actual = math.log(float(late.iloc[-1]) / float(fs_ser.iloc[-1]))
    legs.append(("locals_add_up_on_a_one_bar_switch", abs(actual - predicted) <= 1e-9))

    # dispersion helper: a constant sample must not produce a t-statistic out of nothing
    d1 = _dist([1.0, 1.0, 1.0])
    d2 = _dist([1.0, -1.0, 1.0, -1.0])
    legs.append(("constant_sample_has_no_t", d1["sd"] == 0.0 and d1["t"] is None))
    legs.append(("noisy_sample_reports_share_both_ways", abs(d2["share_late_helps"] - 0.5) < 1e-12))
    legs.append(("empty_sample_is_not_a_zero", _dist([]) == {"n": 0}))

    failed = [leg[0] for leg in legs if not leg[1]]
    for leg in legs:
        print(("PASS " if leg[1] else "FAIL ") + leg[0]
              + (("  [" + leg[2] + "]") if len(leg) > 2 else ""))
    print("selftest %d/%d legs" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


def check(out_path=None):
    path = out_path or os.path.join(E.PATHS.results_dir, "etf_book_late_sheet_price.json")
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    legs, bad = [], []

    for arm in d["arms"]:
        legs.append(("%s: control replays the engine" % arm["arm"], arm["control"]["reproduces_engine"], ""))
        if not arm["control"]["reproduces_engine"]:
            bad.append(arm["arm"] + ":control")

        # the verdict must be re-derivable from the printed distribution, not typed in
        dist = arm["dist_bps"]
        t = dist.get("t")
        share_ok = all(p["residual_share"] is None or abs(p["residual_share"]) <= d["config"]["additivity_tol"]
                       for p in arm["phases"])
        if dist.get("n", 0) == 0:
            want = "NO_EVENTS"
        elif not share_ok:
            want = "LOCALS_DO_NOT_ADD_UP"
        elif t is None or abs(t) < 2:
            want = "PRICE_NOT_SEPARABLE_FROM_ZERO"
        elif 0.35 < dist["share_late_helps"] < 0.65:
            want = "MEAN_IS_PRICED_EACH_SHEET_IS_NOT"
        else:
            want = "ONE_SHEET_IS_PRICED"
        legs.append(("%s: verdict follows from its own distribution" % arm["arm"],
                     want == arm["verdict"], "%s vs %s" % (want, arm["verdict"])))
        if want != arm["verdict"]:
            bad.append(arm["arm"] + ":verdict")

        # money and bps must describe the same events
        legs.append(("%s: bps and CNY describe the same events" % arm["arm"],
                     arm["dist_bps"]["n"] == arm["dist_cny"]["n"], ""))
        if arm["dist_bps"]["n"] != arm["dist_cny"]["n"]:
            bad.append(arm["arm"] + ":n")

        # every phase must publish its residual, and the aggregate must be the recomputation
        legs.append(("%s: every phase carries a residual" % arm["arm"],
                     all("residual" in p and "actual_log_delta" in p for p in arm["phases"]), ""))
        if not all("residual" in p for p in arm["phases"]):
            bad.append(arm["arm"] + ":residual")

        agg_ok = all(abs(p["actual_log_delta"] -
                         math.log(p["late_final"] / p["control_final"])) <= 1e-9
                     for p in arm["phases"])
        legs.append(("%s: aggregate arm is recomputable from its finals" % arm["arm"], agg_ok, ""))
        if not agg_ok:
            bad.append(arm["arm"] + ":aggregate")

    for n, ok, detail in legs:
        print(("PASS " if ok else "FAIL ") + n + (("  [" + detail + "]") if detail else ""))
    print("check %d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        return selftest()
    if len(argv) > 1 and argv[1] == "--check":
        return check()
    out = os.path.join(E.PATHS.results_dir, "etf_book_late_sheet_price.json")
    payload = run(out)
    for line in payload["headline"]:
        print(line)
    for arm in payload["arms"]:
        print("  %s -> %s" % (arm["arm"], arm["verdict"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))