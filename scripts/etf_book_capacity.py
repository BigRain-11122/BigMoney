"""How much money can this ETF book actually carry, and does its edge survive the
impact of trading it at size?

Every round from r1249 to r1259 priced the book at a flat 8bp/side. That is a
spread-and-commission assumption, not a size assumption: it says nothing about how
much of a name you can buy before the trade moves the price. This script replaces
the flat rate with a participation-priced one and reports the NAV at which the
book stops beating its own equal weight.

What is reused, never rewritten:
  * selection, fill legs and turnover  = `F.run_next_open` (r1250 next-open basis);
    the only addition is a per-decision cost callable (`cost=` may be a function),
    which charges the same `rate * turnover` as before -- the scalar path is pinned
    bit-identical by leg 1 of the selftest;
  * the score face                     = `F.build_score` (no re-derivation);
  * the ADV face                       = `F.build_panel`'s `amt`, the 20-day MEDIAN
    of close*volume (the same liquidity face the 20M eligibility gate uses);
  * controls                           = `F.run_ew` (equal weight, same cadence) and
    510300 as the market.

Impact model (stated, not fitted -- the whole point is that it can be argued with):
  participation p = |delta weight| x NAV / ADV20
  extra_bp        = K x sqrt(p / 1%)          K = 10bp at 1% of ADV (default)
  per side rate   = (8bp + extra_bp) averaged over the traded weight
  a name with no ADV of its own is charged a punitive 100bp and counted, never
  silently filled at the flat rate.

Because p enters as a square root, the cost of size is concave: doubling NAV costs
1.41x the extra basis points, so the book does not fall off a cliff -- it decays.
The break-even NAV is reported, and K is swept (5/10/20bp) so the answer is a band.

Second face, unrelated to size: the pool is every ETF that still prints a bar today.
A name that stopped printing (liquidation) drops out of the cross-section, and when
the book already holds it, `leg()` skips the missing cell and averages the rest -- so
the position is silently retired at par. That is defensible ONLY if ETF liquidation
returns NAV to holders, which is exactly what it does in China. This script measures
how often it actually happens instead of assuming it away.

  python scripts/etf_book_capacity.py run [--k=10] [--out=...]
  python scripts/etf_book_capacity.py --selftest

Outputs results/etf_book_capacity.json and a printed table.
Exploratory: no preregistration, no verdict, no ledger booking.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from config import PATHS
from scripts import etf_composite_pf as F

BASE_BP = 8.0                 # the flat spread/commission assumption of r1249-r1259
IMPACT_BP_PER_PCT = 10.0      # K: basis points of impact at 1% ADV20 participation
PUNITIVE_BP = 100.0           # a traded name with no ADV of its own
NAV_GRID = (1e6, 5e6, 1e7, 3e7, 5e7, 1e8, 2e8, 5e8, 1e9)
K_GRID = (5.0, 10.0, 20.0)
REBAL = F.REBAL[1]            # 20 bars, the cadence every r1249+ result used
START = "2020-01-01"
REF_NAV = 1e7                 # the scale the participation table is printed at


def adv_at(amt, d, back=1):
    """The ADV face as it was KNOWN when the decision was taken.

    `d` is the fill bar; the decision was taken on the previous bar's close, so the
    row handed back is `back` bars before `d`. Never the fill bar itself.
    """
    idx = amt.index
    j = idx.searchsorted(pd.Timestamp(d)) - back
    if j < 0 or j >= len(idx):
        return None
    return amt.iloc[j]


class ImpactCost(object):
    """Per-decision cost rate = (base + square-root impact) averaged over traded weight.

    Instances are callable and ride `F.run_next_open(cost=obj)`. They also record
    every decision they priced, which is what the participation table is built from.
    """

    def __init__(self, amt, nav, k_bp=IMPACT_BP_PER_PCT, base_bp=BASE_BP,
                 punitive_bp=PUNITIVE_BP, trace=True):
        self.amt = amt
        self.nav = float(nav)
        self.k_bp = float(k_bp)
        self.base_bp = float(base_bp)
        self.punitive_bp = float(punitive_bp)
        self.trace = trace
        self.rows = []
        self.missing_names = 0

    def parts(self, prev, new, d):
        a = adv_at(self.amt, d)
        out = []
        for k in sorted(set(prev) | set(new)):
            dw = abs(new.get(k, 0.0) - prev.get(k, 0.0))
            if dw <= 0:
                continue
            notional = dw * self.nav
            adv = np.nan if a is None else float(a.get(k, np.nan))
            if not np.isfinite(adv) or adv <= 0:
                self.missing_names += 1
                out.append({"sym": k, "dw": dw, "notional": notional,
                            "adv": None, "participation": None,
                            "extra_bp": self.punitive_bp, "missing_adv": True})
                continue
            p = notional / adv
            out.append({"sym": k, "dw": dw, "notional": notional, "adv": adv,
                        "participation": p,
                        "extra_bp": self.k_bp * np.sqrt(p / 0.01),
                        "missing_adv": False})
        return out

    def __call__(self, prev, new, d):
        legs = self.parts(prev, new, d)
        if not legs:
            return 0.0
        den = sum(l["dw"] for l in legs)
        num = sum(l["dw"] * (self.base_bp + l["extra_bp"]) for l in legs)
        rate = (num / den) / 1e4
        if self.trace:
            ps = [l["participation"] for l in legs if l["participation"] is not None]
            self.rows.append({
                "date": str(pd.Timestamp(d).date()),
                "n_legs": len(legs),
                "turnover": round(den, 4),
                "rate_bp_per_side": round(rate * 1e4, 3),
                "extra_bp_avg": round(float(np.mean([l["extra_bp"] for l in legs])), 3),
                "participation_max": round(float(max(ps)), 6) if ps else None,
                "participation_median": round(float(np.median(ps)), 6) if ps else None,
                "missing_adv_legs": sum(1 for l in legs if l["missing_adv"]),
                "legs": [{"sym": l["sym"], "dw": round(l["dw"], 4),
                          "adv": None if l["adv"] is None else round(l["adv"], 1),
                          "participation": None if l["participation"] is None
                          else round(l["participation"], 6)} for l in legs],
            })
        return rate


def universe_health(close, min_gap=20):
    """Which names in the panel stopped printing, and what they did on the way out."""
    cutoff = close.index[-1]
    pos = {d: i for i, d in enumerate(close.index)}
    last = close.apply(lambda s: s.last_valid_index())
    dead = {}
    for sym, lb in last.items():
        if lb is None:
            continue
        gap = len(close.index) - 1 - pos[pd.Timestamp(lb)]
        if gap >= min_gap:
            ser = close[sym].dropna()
            tail = ser.iloc[-21:] if len(ser) > 21 else ser
            move = float(tail.iloc[-1] / tail.iloc[0] - 1.0) if len(tail) > 1 else None
            dead[sym] = {"last_bar": str(pd.Timestamp(lb).date()), "bars_since": int(gap),
                         "last20_move": None if move is None else round(move, 4)}
    alive = len(last) - len(dead)
    return {"panel_cutoff": str(pd.Timestamp(cutoff).date()), "n_names": int(len(last)),
            "n_alive": int(alive), "n_dead": int(len(dead)), "dead": dead}


def holding_deaths(close, decisions):
    """Was the book ever holding a name on the day it stopped printing?

    `decisions` = list of {"date":..., "held":[...]}. A death inside a holding window
    means the leg engine skipped that cell and averaged the survivors: the position
    left at par. Counting it is the only honest way to say how much that assumption
    is worth.
    """
    pos = {d: i for i, d in enumerate(close.index)}
    last = close.apply(lambda s: s.last_valid_index())
    out = []
    cutoff = pd.Timestamp(close.index[-1])
    for i, dec in enumerate(decisions):
        nxt = decisions[i + 1]["date"] if i + 1 < len(decisions) else \
            str(cutoff.date())
        a = pd.Timestamp(dec["date"])
        b = pd.Timestamp(nxt)
        for sym in dec["held"]:
            lb = last.get(sym)
            if lb is None:
                continue
            lb = pd.Timestamp(lb)
            if lb >= cutoff:
                continue          # still printing on the last bar: not known dead yet
            if a < lb <= b:
                out.append({"decision": dec["date"], "sym": sym,
                            "last_bar": str(lb.date()),
                            "bars_held_before_death": int(pos[lb] - pos[a])})
    return out


def run(k_bp=IMPACT_BP_PER_PCT, start=START):
    close, openp, amt, feats = F.build_panel()
    score = F.build_score(close, amt, feats)

    # the objective the capacity ladder is graded against: the same pool, equal weight
    ew = F.run_ew(close, amt, REBAL, start=start)
    ew_m = F.metrics(ew, "pool equal weight")
    mkt = F.bench_series(close, start)
    mkt_m = F.metrics(mkt, "510300") if mkt is not None else None

    flat_ser, flat_turn, flat_gap = F.run_next_open(
        close, openp, amt, feats, REBAL, cost=F.COST, start=start, score=score)

    ladder = []
    trace_by_nav = {}
    for nav in NAV_GRID:
        cm = ImpactCost(amt, nav, k_bp=k_bp)
        ser, turn, gpf = F.run_next_open(close, openp, amt, feats, REBAL,
                                         cost=cm, start=start, score=score)
        m = F.metrics(ser, "nav=%.0e" % nav)
        m.update({"nav": nav, "turnover": round(turn, 4),
                  "open_gapfill": gpf, "missing_adv_legs": cm.missing_names,
                  "excess_vs_ew_pp": (None if m.get("cagr") is None else
                                      round(100.0 * (m["cagr"] - ew_m["cagr"]), 3)),
                  "excess_vs_flat_pp": (None if m.get("cagr") is None else
                                        round(100.0 * (m["cagr"] - F.metrics(flat_ser, "f")["cagr"]), 3))})
        if m.get("cagr") is not None:
            p2 = pd.Series([r["participation_max"] for r in cm.rows
                            if r["participation_max"] is not None])
            m["participation_max_p90"] = round(float(p2.quantile(0.9)), 6) if len(p2) else None
            m["decisions_over_1pct"] = int((p2 > 0.01).sum()) if len(p2) else 0
        ladder.append(m)
        trace_by_nav[nav] = cm.rows

    # the same ladder at two other impact constants: the answer is a band, not a point
    band = {}
    for kk in K_GRID:
        row = []
        for nav in (1e7, 5e7, 1e8, 2e8, 5e8):
            cm = ImpactCost(amt, nav, k_bp=kk, trace=False)
            ser, _, _ = F.run_next_open(close, openp, amt, feats, REBAL, cost=cm,
                                        start=start, score=score)
            m = F.metrics(ser, "k=%g nav=%.0e" % (kk, nav))
            row.append({"nav": nav, "k_bp": kk,
                        "cagr": m.get("cagr"), "excess_vs_ew_pp":
                        None if m.get("cagr") is None else round(100.0 * (m["cagr"] - ew_m["cagr"]), 3)})
        band["k=%g" % kk] = row

    def _breakeven(rows):
        ok = [r for r in rows if r.get("excess_vs_ew_pp") is not None and r["excess_vs_ew_pp"] > 0]
        return max([r["nav"] for r in ok]) if ok else None

    # participation at a reference NAV, plus the NAV where the p90 trade hits 1% ADV
    ref_rows = trace_by_nav.get(REF_NAV, [])
    pmax = pd.Series([r["participation_max"] for r in ref_rows
                      if r["participation_max"] is not None])
    pmed = pd.Series([r["participation_median"] for r in ref_rows
                      if r["participation_median"] is not None])
    ceiling = None
    if len(pmax):
        p90_1pct = float(pmax.quantile(0.9))
        if p90_1pct > 0:
            ceiling = 0.01 * REF_NAV / p90_1pct

    decisions = [{"date": r["date"], "held": [l["sym"] for l in r["legs"]]} for r in ref_rows]
    uh = universe_health(close)
    deaths = holding_deaths(close, decisions)

    out = {
        "ts": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "script": "scripts/etf_book_capacity.py",
        "config": {"nav_grid": list(NAV_GRID), "k_bp": k_bp, "k_grid": list(K_GRID),
                   "base_bp": BASE_BP, "rebal": REBAL, "n_hold": F.N_HOLD,
                   "start": start, "min_amt": F.MIN_AMT, "min_hist": F.MIN_HIST},
        "flat_8bp_reference": F.metrics(flat_ser, "book @ flat 8bp"),
        "pool_equal_weight": ew_m,
        "market_510300": mkt_m,
        "capacity_ladder": ladder,
        "breakeven_nav_vs_ew": _breakeven(ladder),
        "impact_k_band": band,
        "participation_at_ref_nav": {
            "ref_nav": REF_NAV,
            "decisions": len(pmax),
            "max_participation_p50": round(float(pmax.median()), 6) if len(pmax) else None,
            "max_participation_p90": round(float(pmax.quantile(0.9)), 6) if len(pmax) else None,
            "max_participation_worst": round(float(pmax.max()), 6) if len(pmax) else None,
            "median_participation_p50": round(float(pmed.median()), 6) if len(pmed) else None,
            "nav_where_p90_trade_is_1pct_adv": None if ceiling is None else round(ceiling, 1),
            "rows": ref_rows,
        },
        "universe_health": uh,
        "holding_deaths_while_held": deaths,
    }
    return out, ladder, out["participation_at_ref_nav"]


def selftest():
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        print("[%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))
        ok = ok and bool(cond)

    # ---- 1) the scalar cost path is bit-identical -----------------------------
    idx = pd.to_datetime(["2021-01-04", "2021-01-05", "2021-01-06", "2021-01-07",
                          "2021-01-08", "2021-01-11", "2021-01-12", "2021-01-13"])
    close = pd.DataFrame({"AAA": [10.0, 10.2, 10.1, 10.4, 10.3, 10.6, 10.5, 10.8],
                          "BBB": [5.0, 5.1, 5.05, 5.2, 5.15, 5.3, 5.25, 5.4]}, index=idx)
    openp = close.shift(1).bfill()
    amt = pd.DataFrame(1e9, index=idx, columns=close.columns)
    feat = {}
    for c in F.SIGNS:
        feat[c] = close.pct_change().fillna(0.0)
    score = pd.DataFrame({"AAA": 1.0, "BBB": 0.0}, index=idx)

    a, ta, _ = F.run_next_open(close, openp, amt, feat, 2, cost=0.0008, start="2021-01-04",
                               score=score)
    cm = ImpactCost(amt, 1e6, k_bp=0.0, base_bp=8.0, trace=False)   # zero impact
    b, tb, _ = F.run_next_open(close, openp, amt, feat, 2, cost=cm, start="2021-01-04",
                               score=score)
    chk("callable cost path == scalar path", np.allclose(a.values, b.values, atol=1e-12),
        "max|d|=%.2e" % float(np.abs(a.values - b.values).max()))
    chk("turnover identical", abs(ta - tb) < 1e-12, "%.6f" % ta)

    # ---- 2) impact rate is exactly the stated formula -------------------------
    amt2 = pd.DataFrame({"AAA": [1e8, 1e8, 1e8], "BBB": [1e8, 1e8, 1e8]}, index=idx[:3])
    cm2 = ImpactCost(amt2, 1e6, k_bp=10.0, trace=True)
    rate = cm2(prev={}, new={"AAA": 0.5, "BBB": 0.5}, d=idx[1])
    # dw=0.5 each -> notional 5e5 / adv 1e8 = 0.5% -> extra 10*sqrt(0.5)=7.0711bp
    exp = (8.0 + 10.0 * np.sqrt(0.005 / 0.01)) / 1e4
    chk("impact formula exact", abs(rate - exp) < 1e-12, "%.8f vs %.8f" % (rate, exp))

    # ---- 3) cost rises with NAV, and only as a square root -------------------
    rates = []
    for nav in (1e6, 1e7, 1e8):
        c = ImpactCost(amt2, nav, k_bp=10.0, trace=False)
        rates.append(c({}, {"AAA": 0.5, "BBB": 0.5}, idx[1]))
    chk("cost monotone in NAV", rates[0] < rates[1] < rates[2], str([round(r * 1e4, 3) for r in rates]))
    # 100x NAV = 10x participation = sqrt(10)x the impact part
    base = 8.0 / 1e4
    ratio = (rates[2] - base) / (rates[0] - base)
    chk("square-root scaling", abs(ratio - np.sqrt(100.0)) < 1e-6, "ratio=%.6f" % ratio)

    # ---- 4) a missing ADV is punished and counted, never flat-priced ---------
    amt3 = pd.DataFrame({"AAA": [np.nan, np.nan, np.nan]}, index=idx[:3])
    c3 = ImpactCost(amt3, 1e6)
    r3 = c3({}, {"AAA": 1.0}, idx[1])
    chk("missing ADV -> punitive", abs(r3 - (PUNITIVE_BP + BASE_BP) / 1e4) < 1e-12,
        "%.4f" % (r3 * 1e4))
    chk("missing ADV counted", c3.missing_names == 1, str(c3.missing_names))

    # ---- 5) adv_at never reads the fill bar ----------------------------------
    amt4 = pd.DataFrame({"AAA": [1.0, 2.0, 3.0]}, index=idx[:3])
    chk("adv_at is one bar back", float(adv_at(amt4, idx[2]).iloc[0]) == 2.0,
        "%.1f" % float(adv_at(amt4, idx[2]).iloc[0]))
    chk("adv_at at the start is None", adv_at(amt4, idx[0]) is None, "")

    # ---- 6) dead-name detection --------------------------------------------
    c5 = close.copy()
    c5.loc[idx[4]:, "BBB"] = np.nan
    uh = universe_health(c5, min_gap=1)
    chk("dead name detected", uh["n_dead"] == 1 and "BBB" in uh["dead"], json.dumps(uh["dead"])[:80])
    chk("alive count", uh["n_alive"] == 1, str(uh["n_alive"]))

    # ---- 7) holding death inside a window -----------------------------------
    decs = [{"date": str(idx[2].date()), "held": ["BBB"]},
            {"date": str(idx[5].date()), "held": ["AAA"]}]
    dd = holding_deaths(c5, decs)
    chk("holding death detected", len(dd) == 1 and dd[0]["sym"] == "BBB", json.dumps(dd))

    # ---- 8) determinism -----------------------------------------------------
    a2, _, _ = F.run_next_open(close, openp, amt, feat, 2, cost=cm, start="2021-01-04",
                               score=score)
    chk("deterministic", np.allclose(b.values, a2.values, atol=0), "")

    print("\nselftest %s" % ("ALL PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--k", type=float, default=IMPACT_BP_PER_PCT)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out", default=os.path.join(PATHS.results_dir, "etf_book_capacity.json"))
    args = ap.parse_args(argv)

    if args.selftest or args.cmd == "selftest":
        return selftest()

    out, ladder, part = run(k_bp=args.k)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("evidence_cutoff=%s  k=%.1fbp/1%%" % (out["evidence_cutoff"], args.k))
    print("%-10s %8s %8s %8s %10s %10s" % ("NAV", "CAGR", "Sharpe", "MaxDD",
                                           "xEW(pp)", "p90 part"))
    for m in ladder:
        if m.get("cagr") is None:
            continue
        print("%-10.0e %7.2f%% %8.3f %7.2f%% %+10.2f %10s" % (
            m["nav"], 100 * m["cagr"], m["sharpe"], 100 * m["maxdd"],
            m["excess_vs_ew_pp"], "%.2f%%" % (100 * (m["participation_max_p90"] or 0))))
    print("pool EW CAGR %.2f%% | 510300 %.2f%% | flat-8bp book %.2f%%" % (
        100 * out["pool_equal_weight"]["cagr"],
        100 * out["market_510300"]["cagr"] if out["market_510300"] else float("nan"),
        100 * out["flat_8bp_reference"]["cagr"]))
    print("break-even NAV vs equal weight: %s | p90 1%%-ADV ceiling: %s" % (
        out["breakeven_nav_vs_ew"], part["nav_where_p90_trade_is_1pct_adv"]))
    print("universe: %d names, %d alive, %d stopped printing" % (
        out["universe_health"]["n_names"], out["universe_health"]["n_alive"],
        out["universe_health"]["n_dead"]))
    print("holding deaths while held: %d" % len(out["holding_deaths_while_held"]))
    print("wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))