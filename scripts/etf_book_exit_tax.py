#!/usr/bin/env python
"""ETF book: what does being OUT of the book cost? (r1387 bm-c, reading + ruler)

r1386 measured a candidate timing rule (zoo90 alligator) and the number that outlived the
verdict was the null it was judged against: a random-phase exposure with the SAME in-market
share as the rule still lost 4.11%/yr on a diversified basket. That is a hurdle, and no face
in this repo publishes it -- so every future "should the book be out of the market sometimes"
question starts by re-deriving the same ruler.

This face publishes the ruler for the book that is actually in force. Take the production
book's own daily net return series (bond-free, 8% vol target, next-open fill, 10bp a side --
the same call the published book is built from, not a re-implementation), and for each
exposure share s in {0.95, 0.85, 0.70, 0.50, 0.30} draw 200 random exposure masks that are
in market exactly s of the time with the same persistence, and measure the CAGR each one
gives up against never leaving. The mean of that distribution is the return a timing rule
with that share must EARN before it is even allowed to be compared to holding.

Two readings fall out, and both are the point:

  1. the tax is not proportional to the time spent out (a mask is daily, so a 50% exposure
     book loses more than half its edge only if the book's returns are clustered in the days
     the shuffle happens to miss) -- printing the proportional prediction beside the measured
     one shows which regime this book is in;
  2. the persistence matters: the same share held in long blocks is a different question from
     the same share flipped daily, so the ruler is computed at the persistence the candidates
     actually use (mean run ~20 bars, one rebalance cycle).

What this is NOT: no candidate, no verdict, no preregistration, no trial ledger booking, and
no costs of its own (a mask that switches daily would pay turnover -- this is a ruler, not a
rule; the cost of a real rule belongs on its own ticket). It cannot remove survivorship.

  python scripts/etf_book_exit_tax.py run       # write results/etf_book_exit_tax.json
  python scripts/etf_book_exit_tax.py --selftest
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_equity_alpha as A
import etf_robust_pf as R

OUT = "etf_book_exit_tax.json"
REBAL, N_HOLD, COST, VOL_TARGET = 20, 5, 0.0010, 0.08
SHARES = (0.95, 0.85, 0.70, 0.50, 0.30)
DRAWS = 200
MEAN_RUN = 20          # persistence of the exposure blocks the null draws
SEED = 20261107
BARS_PER_YEAR = 252


def cagr(rets):
    rets = np.asarray(rets, dtype=float)
    if rets.size == 0:
        return None
    growth = float(np.prod(1.0 + rets))
    if growth <= 0:
        return None
    return growth ** (BARS_PER_YEAR / rets.size) - 1.0


def masks(n, share, draws, mean_run, seed):
    """Boolean in-market masks with exactly `share` on average and mean run ~mean_run.

    A Markov chain with p_stay tuned so the stationary share is `share` and the expected run
    length is `mean_run`. Seeded, so the distribution is reproducible; the draws differ in
    both phase and pattern, which is what "same share and persistence, not that path" means.
    """
    if n <= 0:
        raise ValueError("no bars")
    if not 0.0 < share <= 1.0:
        raise ValueError("share must be in (0, 1]")
    if share == 1.0:
        return [np.ones(n, dtype=bool) for _ in range(draws)]
    rng = np.random.default_rng(seed)
    p_stay = 1.0 - 1.0 / max(1.0, mean_run)
    # stationary P(on) = p_off2on / (p_off2on + 1 - p_stay); solve p_off2on for `share`
    p_up = share * (1.0 - p_stay) / (1.0 - share)
    p_up = min(max(p_up, 0.0), 1.0)
    out = []
    for _ in range(draws):
        m = np.empty(n, dtype=bool)
        m[0] = rng.random() < share
        u = rng.random(n - 1)
        for i in range(1, n):
            m[i] = (u[i - 1] < p_stay) if m[i - 1] else (u[i - 1] < p_up)
        out.append(m)
    return out


MAX_BAR_RET = 0.35     # a daily book return above this is a level series, not a return


def tax_distribution(rets, share, draws=DRAWS, mean_run=MEAN_RUN, seed=SEED):
    """Excess CAGR of each random exposure mask against never leaving. None = unmeasured."""
    rets = np.asarray(rets, dtype=float)
    if rets.size < BARS_PER_YEAR // 2 or not np.isfinite(rets).all():
        return None
    if np.abs(rets).max() > MAX_BAR_RET:
        # the walk hands back LEVELS; masking a level series measures nothing and compounds
        # to inf. Refusing here is why a caller cannot pass the wrong series by accident.
        return None
    base = cagr(rets)
    if base is None:
        return None
    excess, used = [], []
    for m in masks(rets.size, share, draws, mean_run, seed):
        got = cagr(np.where(m, rets, 0.0))
        if got is None:
            continue
        excess.append(got - base)
        used.append(float(m.mean()))
    if not excess:
        return None
    ex = np.asarray(excess, dtype=float)
    return {
        "share_requested": share,
        "share_realized": round(float(np.mean(used)), 4),
        "draws": len(ex),
        "base_cagr": round(float(base), 6),
        "excess_mean": round(float(ex.mean()), 6),
        "excess_sd": round(float(ex.std(ddof=1)) if ex.size > 1 else 0.0, 6),
        "excess_worst": round(float(ex.min()), 6),
        "excess_best": round(float(ex.max()), 6),
        # the hurdle is stated positively: what a rule must earn to break even with holding
        "hurdle_pp_per_yr": round(float(-ex.mean()) * 100.0, 3),
        # a mask that is out (1-share) of the time loses share*base if the book's returns were
        # spread evenly; the gap between this and the measurement is the clustering effect
        "proportional_pp_per_yr": round(float((1.0 - np.mean(used)) * base) * 100.0, 3),
    }


def build_book():
    """The book in force: the published bond-free 8% vol-target walk, unchanged call."""
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cls = A.classify(close.columns, A.load_class_map(), close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)
    ser, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc,
                                      REBAL, N_HOLD, COST, vol_target=VOL_TARGET)
    # the walk returns NAV levels; every number on this face is about daily returns
    ser = ser.dropna()
    rets = ser.pct_change().dropna()
    return ser, rets, turn, n_flip, len(cols), str(ser.index[-1].date())


def control_arm(levels):
    """The book this ruler sits on must reproduce the published book at the published cutoff.

    Without this, a silent change in the walk (a different universe, a dropped repair) would
    move the hurdle while every leg still passed -- the ruler would be measuring another book.
    The comparison uses the published face's OWN statistics call (`stats2`, calendar-year
    CAGR), because reproducing a number means reproducing its口径, not a nearby one.
    """
    p = os.path.join("results", "etf_nobond_vt.json")
    try:
        with open(p, encoding="utf-8-sig") as fh:
            pub = json.load(fh)
        row = [r for r in pub.get("runs", []) if r.get("label") == "nobond_vt08"][0]
        cut = pub.get("live_picks", {}).get("as_of")
    except Exception as e:
        return {"ok": False, "why": "published face unreadable: %s" % e}
    sl = levels[levels.index <= pd.Timestamp(cut)]
    got = A.stats2(sl, "control").get("cagr")
    if got is None:
        return {"ok": False, "why": "truncated series unmeasurable", "cutoff": cut}
    tol = 0.0010
    return {"ok": bool(abs(got - row["cagr"]) <= tol),
            "published_cagr": row["cagr"], "recomputed_cagr": round(float(got), 6),
            "cutoff": cut, "bars": int(sl.size), "tolerance": tol}


def run():
    levels, rets_ser, turn, n_flip, n_univ, cutoff = build_book()
    ctrl = control_arm(levels)
    rets = rets_ser.to_numpy(dtype=float)
    rows = [tax_distribution(rets, s) for s in SHARES]
    rows = [r for r in rows if r]
    out = {
        "schema": "etf_book_exit_tax/v1",
        "evidence_cutoff": cutoff,
        "book": {"rule": "bond-free composite score, top %d, rebalance %d bars, %.2f%%/side,"
                         " vol target %.0f%%" % (N_HOLD, REBAL, COST * 100, VOL_TARGET * 100),
                 "universe": n_univ, "flip_repairs": n_flip, "turnover_per_rebal": round(turn, 3),
                 "bars": int(rets.size),
                 "bars_per_year": BARS_PER_YEAR},
        "ruler": {"draws": DRAWS, "mean_run_bars": MEAN_RUN, "seed": SEED,
                  "costs_of_the_mask": "none -- a ruler, not a rule"},
        "rows": rows,
        "control_arm": ctrl,
        "what_this_is_not": [
            "not a candidate and not a verdict: it publishes the hurdle a candidate must clear",
            "no turnover cost for the mask itself; a real timing rule pays its own switching",
            "panel is today's listed set: survivorship is unchanged by this face",
        ],
    }
    p = os.path.join("results", OUT)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    for r in rows:
        print("[exit-tax] share %.2f realized %.3f | hurdle %+.3f pp/yr (prop %+.3f) "
              "mean %+.4f sd %.4f worst %+.4f"
              % (r["share_requested"], r["share_realized"], r["hurdle_pp_per_yr"],
                 r["proportional_pp_per_yr"], r["excess_mean"], r["excess_sd"],
                 r["excess_worst"]), flush=True)
    print("[exit-tax] book cagr %.4f bars %d cutoff %s"
          % (rows[0]["base_cagr"] if rows else float("nan"), rets.size,
             out["evidence_cutoff"]), flush=True)
    print("[exit-tax] receipt", p, flush=True)
    print("[exit-tax] control arm: %s" % json.dumps(ctrl, ensure_ascii=False), flush=True)
    return 0 if ctrl.get("ok") else 2


def selftest():
    n = 1200
    drift = 0.0004            # constant daily drift: the analytic case
    const = np.full(n, drift)
    cagr_theory = (1.0 + drift) ** BARS_PER_YEAR - 1.0

    def leg(name, ok, detail=""):
        print("[%s] %s %s" % ("PASS" if ok else "FAIL", name, detail), flush=True)
        return bool(ok)

    res = []
    # L1 a mask that is always in market must give exactly zero excess, every draw
    full = tax_distribution(const, 1.0, draws=3)
    res.append(leg("L1 share 1.0 is exactly zero excess",
                   full and full["excess_mean"] == 0.0 and full["excess_worst"] == 0.0
                   and full["share_realized"] == 1.0, str(full and full["excess_mean"])))
    # L2 the masks realize the share they were asked for
    for s in (0.9, 0.5, 0.3):
        r = tax_distribution(const, s, draws=40)
        res.append(leg("L2 share %.1f realized within 0.02" % s,
                       r and abs(r["share_realized"] - s) <= 0.02, str(r and r["share_realized"])))
    # L3 on constant drift the measured tax matches the analytic one (log-space compounding)
    r = tax_distribution(const, 0.5, draws=60)
    analytic = (1.0 - r["share_realized"]) * cagr_theory if r else None
    res.append(leg("L3 constant drift: measured tax tracks (1-share)*cagr",
                   r and abs(-r["excess_mean"] - analytic) < 0.004,
                   "measured %+.4f analytic %+.4f" % (r["excess_mean"], -analytic)))
    # L4 a flat series has nothing to lose: tax is zero and the ruler still answers
    flat = tax_distribution(np.zeros(n), 0.5, draws=20)
    res.append(leg("L4 flat series: zero tax, measured not absent",
                   flat is not None and abs(flat["excess_mean"]) < 1e-12
                   and flat["draws"] == 20, str(flat and flat["excess_mean"])))
    # L5 less exposure is a bigger tax on a drifting series (analytic, not a tautology about data)
    hi = tax_distribution(const, 0.9, draws=40)
    lo = tax_distribution(const, 0.4, draws=40)
    res.append(leg("L5 exposure 0.4 taxes more than 0.9",
                   hi and lo and lo["hurdle_pp_per_yr"] > hi["hurdle_pp_per_yr"],
                   "%s vs %s" % (hi and hi["hurdle_pp_per_yr"], lo and lo["hurdle_pp_per_yr"])))
    # L6 deterministic: the seeded ruler repeats byte-for-byte
    a1 = tax_distribution(const, 0.7, draws=25)
    a2 = tax_distribution(const, 0.7, draws=25)
    res.append(leg("L6 seeded ruler is deterministic", a1 == a2, str(a1 == a2)))
    # L7 a series too short to annualize is UNMEASURED, never a zero
    res.append(leg("L7 short series returns None, not zero",
                   tax_distribution(np.full(10, 0.001), 0.5) is None, ""))
    # L8 a non-finite bar poisons the measurement and must be refused
    bad = const.copy()
    bad[7] = np.nan
    res.append(leg("L8 NaN bar refuses the measurement", tax_distribution(bad, 0.5) is None, ""))
    # L9 the realized share is published beside the requested one (a mask that misses is visible)
    r = tax_distribution(const, 0.25, draws=30)
    res.append(leg("L9 requested and realized share both published",
                   r and "share_requested" in r and "share_realized" in r
                   and r["share_requested"] == 0.25, str(r and r["share_realized"])))

    # L10 the walk hands back LEVELS: passing one must be refused, not compounded to inf
    levels = np.cumprod(1.0 + np.full(600, 0.001))
    res.append(leg("L10 a NAV level series is refused (levels are not returns)",
                   tax_distribution(levels, 0.5) is None, "max bar %.3f" % levels.max()))

    print("selftest: %d/%d PASS" % (sum(res), len(res)), flush=True)
    return 0 if all(res) else 1


def check():
    """Re-derive the published table from its own rows: a hand-edited hurdle reads red."""
    p = os.path.join("results", OUT)
    try:
        with open(p, encoding="utf-8-sig") as fh:
            d = json.load(fh)
    except Exception as e:
        print("[check] FAIL unreadable payload:", e)
        return 1
    rows = d.get("rows") or []
    bad = []
    if not rows:
        bad.append("no rows")
    seen = set()
    for r in rows:
        seen.add(r.get("share_requested"))
        want = round(-r["excess_mean"] * 100.0, 3)
        if r.get("hurdle_pp_per_yr") != want:
            bad.append("share %s hurdle %s != %s" % (r.get("share_requested"),
                                                     r.get("hurdle_pp_per_yr"), want))
        if not (abs(r["share_realized"] - r["share_requested"]) <= 0.03):
            bad.append("share %s realized %s off" % (r.get("share_requested"),
                                                     r.get("share_realized")))
        if r.get("draws") != d.get("ruler", {}).get("draws"):
            bad.append("share %s draws %s != ruler draws" % (r.get("share_requested"),
                                                             r.get("draws")))
    if seen != set(SHARES):
        bad.append("shares %s != %s" % (sorted(seen), sorted(SHARES)))
    if not d.get("evidence_cutoff"):
        bad.append("no evidence_cutoff")
    ctrl = d.get("control_arm") or {}
    if not ctrl.get("ok"):
        bad.append("control arm does not reproduce the published book: %s"
                   % json.dumps(ctrl, ensure_ascii=False))
    print("[check] %s" % ("PASS" if not bad else "FAIL " + "; ".join(bad)))
    return 0 if not bad else 1


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "run"
    if arg in ("--selftest", "selftest"):
        sys.exit(selftest())
    if arg in ("--check", "check"):
        sys.exit(check())
    sys.exit(run())