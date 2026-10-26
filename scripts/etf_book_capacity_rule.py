"""Capacity of the DELIVERED rule, not of the flat research book.

r1291 closed the width question: the card-vs-ticket gap is a risk-budget choice, and the
name count is a monotone risk knob. What it could not answer is the money question that
comes next -- every capacity number on the shelf (r1259 etf_book_capacity.py, r1247
frontier, r1260 stagger) prices the FULLY INVESTED equal-weight book at flat 8bp base
plus a square-root impact. The executable ticket is a different animal: it holds
`k = min(1, 0.20/beta)` of NAV in the top-N basket and parks the rest in GC001. Smaller
trades should carry more money. Does it?

The two arms here share ONE engine, ONE window and ONE cost model, so the answer is not
confounded by anything else (the r1290/r1291 lesson):

  rule   : w_i = k/n for the current picks, (1-k) in the repo cash leg, k from the
           expanding-beta schedule (BT.k_schedule, the production rule verbatim);
  flat   : the same picks, the same grid, k = 1 (no cash leg) -- the research book.

Cost model (reused, not re-stated): per-name traded weight x (8bp + K*sqrt(p/1%)),
p = traded notional / ADV20 known one bar before the fill (C.adv_at). A name without an
ADV is charged the punitive 100bp and counted, never silently filled at the base rate.
The traded weight is taken from the ACTUAL weight path -- a k move trades the whole
basket proportionally, a rebalance trades names -- so no fee is invented and none is
double-charged. The base-only path is pinned to `F.run_next_open(cost=F.COST)` to 1e-12
by leg 1 of the selftest, which is what makes every delta below attributable.

  python scripts/etf_book_capacity_rule.py run [--target=0.20] [--k-bp=10]
  python scripts/etf_book_capacity_rule.py --selftest

Outputs results/etf_book_capacity_rule.json and a printed ladder.
Each ladder row carries dollars two ways: `annual_profit_cny` (the earning RATE at that
NAV, which is what capacity is about) and `total_profit_cny` (what the window actually
made). `peak_dollar_profit_nav` and `peak_dollar_profit_cny` are a pair -- the NAV at the
peak and the money earned there; they must not be read as one number twice.
Exploratory: no preregistration, no verdict, no ledger booking.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from scripts import etf_composite_pf as F
from scripts import etf_phase_beta_target as BT
from scripts import etf_phase_beta_window as BW
from scripts import etf_book_capacity as C

REBAL = F.REBAL[1]
START = "2020-01-01"
TARGET_BETA = 0.20
REF_NAV = 1e7
NAV_GRID = (1e6, 5e6, 1e7, 3e7, 5e7, 1e8, 2e8, 5e8, 1e9)
EPS = 1e-12


class Recorder(object):
    """Zero-cost cost callable: records (fill bar, previous book, new book).

    The engine calls this once per rebalance with the books as {sym: weight}; it must
    return the per-side rate, so returning 0.0 leaves the curve GROSS and lets this
    script charge every basis point itself from the realised weight path.
    """

    def __init__(self):
        self.fills = []

    def __call__(self, prev, new, d):
        self.fills.append((pd.Timestamp(d), dict(prev), dict(new)))
        return 0.0


def _applied_k(sched, dates):
    """k in force for each bar's return: a decision on the close of d applies from d+1."""
    marks = pd.Series(np.nan, index=dates, dtype=float)
    for d, k, _b in sched:
        if d in marks.index:
            marks.loc[d] = float(k)
    return marks.shift(1).ffill()


def build_face(target=TARGET_BETA, start=START):
    """One engine pass (gross) + the production k schedule + repo cash leg."""
    close, openp, amt, feats = F.build_panel()
    score = F.build_score(close, amt, feats)
    rec = Recorder()
    gross, turn, gapfill = F.run_next_open(close, openp, amt, feats, REBAL,
                                           cost=rec, start=start, score=score)
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        raise SystemExit("FATAL: no 510300 column on the panel")
    mkt = close[mkt_col]
    idx = gross.index.intersection(mkt.index)
    # keep the engine's FIRST bar (it is the curve's start point, so its return is 0):
    # dropping it would silently lose that bar's fill cost and leg from every arm.
    rp = gross.reindex(idx).pct_change().fillna(0.0)
    rm = mkt.reindex(idx).pct_change().fillna(0.0)
    sched = BT.k_schedule(rp, rm, target)
    k_ser = _applied_k(sched, rp.index).reindex(rp.index)
    rf, rf_missing = BW.repo_daily_cash(rp.index, BW.load_repo_rates())
    rf = rf.reindex(rp.index).fillna(0.0)
    return {"close": close, "amt": amt, "idx": idx, "rp": rp, "rm": rm,
            "sched": sched, "k": k_ser, "rf": rf, "rf_missing": rf_missing,
            "fills": rec.fills, "rebal_turnover": turn, "gapfill": gapfill,
            "market": mkt, "mkt_col": mkt_col}


def weight_path(face, k_override=None):
    """[(bar, {sym: weight})] -- the book as actually held at each bar's start.

    Weights are k/n over the picks in force; the k series is the production schedule
    unless `k_override` pins it (k=1 gives the flat research book on this same engine).
    """
    fills = {d: new for d, _p, new in face["fills"]}
    book = {}
    out = []
    for d in face["idx"]:
        if d in fills:
            book = fills[d]
        k = float(k_override) if k_override is not None else face["k"].get(d, np.nan)
        if not np.isfinite(k):
            k = 1.0        # warm-up before the first beta estimate: fully invested
        n = len(book)
        w = {} if n == 0 else {s: k / n for s in book}
        # before the first fill there is no basket at all: everything is cash, whatever k says
        out.append((d, w, 1.0 - sum(w.values())))
    return out


def _cost_legs(prev, new, adv_row, nav, k_bp, base_bp, punitive_bp):
    """Per-name traded weight, participation and charged basis points for one bar."""
    legs = []
    for s in sorted(set(prev) | set(new)):
        dw = abs(new.get(s, 0.0) - prev.get(s, 0.0))
        if dw <= EPS:
            continue
        adv = np.nan if adv_row is None else float(adv_row.get(s, np.nan))
        if not np.isfinite(adv) or adv <= 0:
            legs.append({"sym": s, "dw": dw, "adv": None, "participation": None,
                         "bp": punitive_bp, "missing_adv": True, "notional": dw * nav})
            continue
        p = dw * nav / adv
        bp = base_bp + k_bp * np.sqrt(p / 0.01)
        legs.append({"sym": s, "dw": dw, "adv": adv, "participation": p, "bp": bp,
                     "missing_adv": False, "notional": dw * nav})
    return legs


def curve(face, nav, k_bp=C.IMPACT_BP_PER_PCT, base_bp=C.BASE_BP,
          k_override=None, path=None, trace=False):
    """Daily NAV series of one arm priced at `nav`, with per-name impact.

    Returns (level series, list of per-decision cost rows, counters).
    """
    if path is None:
        path = weight_path(face, k_override=k_override)
    amt = face["amt"]
    rp, rf = face["rp"], face["rf"]
    prev_w = {}
    equity = 1.0
    levels = []
    rows = []
    missing = 0
    nav_charged = 0.0
    for d, w, cash in path:
        k = 1.0 - cash
        legs = _cost_legs(prev_w, w, C.adv_at(amt, d, back=1), nav,
                          k_bp, base_bp, C.PUNITIVE_BP)
        cost = 0.0
        if legs:
            cost = sum(l["dw"] * l["bp"] for l in legs) / 1e4
            missing += sum(1 for l in legs if l["missing_adv"])
            nav_charged += 1
            if trace:
                ps = [l["participation"] for l in legs if l["participation"] is not None]
                rows.append({"date": str(d.date()),
                             "turnover": round(sum(l["dw"] for l in legs), 6),
                             "cost_bp_per_side": round(cost * 1e4 /
                                                       max(sum(l["dw"] for l in legs), EPS), 4),
                             "cost_frac": round(cost, 10),
                             "participation_max": round(max(ps), 6) if ps else None,
                             "missing_adv": sum(1 for l in legs if l["missing_adv"])})
        r = k * float(rp.get(d, 0.0)) + cash * float(rf.get(d, 0.0))
        # cost multiplies, never subtracts: it is charged on the traded notional at the
        # fill, exactly as `F.run_next_open` does, so the base-only k=1 arm is bit-equal.
        equity *= (1.0 + r) * (1.0 - cost)
        levels.append((d, equity))
        prev_w = w
    ser = pd.Series(dict(levels))
    return ser, rows, {"missing_adv_legs": missing, "bars_charged": nav_charged}


def _dd_date(ser):
    """The bar the worst drawdown bottomed on -- a drawdown without a date is unreadable."""
    s = ser.dropna()
    if len(s) < 3:
        return None
    dd = s / s.cummax() - 1.0
    return str(pd.Timestamp(dd.idxmin()).date())


def _peak_nav(ladder, field="annual_profit_cny"):
    """The NAV that earns the most dollars per year -- capacity is an interior peak,
    so the widest NAV on the grid is almost never the right answer."""
    pts = [(r["nav"], r[field]) for r in ladder if r.get(field) is not None]
    return max(pts, key=lambda t: t[1])[0] if pts else None


def _peak_dollar(ladder, field="annual_profit_cny"):
    """The dollar amount earned AT that peak NAV. Reporting the NAV under a field
    named `peak_dollar_profit_cny` was r1292's bug: the two numbers came out equal
    by construction and read as if the book made 200M a year."""
    pts = [(r["nav"], r[field]) for r in ladder if r.get(field) is not None]
    return max(pts, key=lambda t: t[1])[1] if pts else None


def _breakeven(ladder, field="excess_vs_ew_pp"):
    ok = [r["nav"] for r in ladder
          if r.get(field) is not None and r[field] > 0]
    return max(ok) if ok else None


def _ceiling_nav(ref_nav, p90_fraction, cap=0.01):
    """NAV at which the p90 decision's biggest leg first touches `cap` of ADV.
    Participation is a fraction of ADV, and it scales linearly in NAV, so one
    reference bar is enough -- but get the unit wrong and the answer is off by 100x."""
    if p90_fraction is None or p90_fraction <= 0:
        return None
    return round(cap * ref_nav / p90_fraction, 1)


def run(target=TARGET_BETA, k_bp=C.IMPACT_BP_PER_PCT, start=START):
    face = build_face(target=target, start=start)
    rp, rf = face["rp"], face["rf"]
    rule_path = weight_path(face)
    flat_path = weight_path(face, k_override=1.0)

    ew = F.run_ew(face["close"], face["amt"], REBAL, start=start)
    ew_m = F.metrics(ew, "pool equal weight")
    mkt_ser = face["market"].reindex(rp.index)
    mkt_m = F.metrics(mkt_ser, face["mkt_col"])

    rule_flat, _, _ = curve(face, 0.0, k_bp=0.0, base_bp=C.BASE_BP,
                            path=rule_path, trace=True)          # base-only, no size
    flat_flat, _, _ = curve(face, 0.0, k_bp=0.0, base_bp=C.BASE_BP, path=flat_path)
    rule_m0 = F.metrics(rule_flat, "rule @ 8bp, no size")
    flat_m0 = F.metrics(flat_flat, "flat @ 8bp, no size")

    ladders = {}
    traces = {}
    for arm, path in (("rule", rule_path), ("flat", flat_path)):
        rows = []
        for nav in NAV_GRID:
            ser, crows, cnt = curve(face, nav, k_bp=k_bp, path=path, trace=True)
            m = F.metrics(ser, "%s @ nav=%.0e" % (arm, nav))
            m.update({"nav": nav, "k_bp": k_bp, "dd_date": _dd_date(ser),
                      "turnover": round(float(sum(c["turnover"] for c in crows)), 4)
                      if crows else None,
                      "missing_adv_legs": cnt["missing_adv_legs"],
                      "bars_charged": cnt["bars_charged"]})
            if crows:
                ps = pd.Series([c["participation_max"] for c in crows
                                if c["participation_max"] is not None])
                m["participation_max_p90"] = round(float(ps.quantile(0.9)), 6) if len(ps) else None
                m["participation_worst"] = round(float(ps.max()), 6) if len(ps) else None
                m["cost_bp_avg_per_side"] = round(
                    float(np.average([c["cost_bp_per_side"] for c in crows],
                                     weights=[c["turnover"] for c in crows])), 3)
                traces[(arm, nav)] = crows
            if m.get("cagr") is not None:
                m["excess_vs_ew_pp"] = round(100.0 * (m["cagr"] - ew_m["cagr"]), 3)
                ref = rule_m0 if arm == "rule" else flat_m0
                m["excess_vs_own_8bp_pp"] = round(100.0 * (m["cagr"] - ref["cagr"]), 3)
                # dollars per year vs dollars over the window are different questions:
                # capacity is about the yearly earning rate, the ladder's headline is
                # what the whole 6.8 years actually made.
                m["annual_profit_cny"] = round(nav * m["cagr"], 0)
                m["total_profit_cny"] = round(nav * m["total_ret"], 0)
                m["annual_profit_vs_own_8bp_cny"] = round(
                    nav * (m["cagr"] - ref["cagr"]), 0)
            rows.append(m)
        ladders[arm] = rows

    # participation ceiling: the NAV where the p90 decision's biggest leg is 1% of ADV.
    # `participation_max` is a FRACTION of ADV (0.0655 == 6.55%), so the ceiling is
    # ref_nav * 0.01 / frac. Reading that fraction as a percentage shrinks the ceiling
    # by 100x -- exactly the r1292 bug that printed a 15k ceiling next to a 1.5M book.
    ceiling = {}
    for arm in ("rule", "flat"):
        rws = traces.get((arm, REF_NAV), [])
        ps = pd.Series([r["participation_max"] for r in rws
                        if r["participation_max"] is not None])
        p90 = float(ps.quantile(0.9)) if len(ps) else None
        ceiling[arm] = _ceiling_nav(REF_NAV, p90)
        ceiling[arm + "_at_ref_nav"] = {
            "ref_nav": REF_NAV, "decisions": int(len(ps)),
            "p50": round(float(ps.median()), 6) if len(ps) else None,
            "p90": round(p90, 6) if len(ps) else None,
            "units": "fraction of ADV (0.0655 == 6.55%)",
            "worst": round(float(ps.max()), 6) if len(ps) else None}

    out = {
        "ts": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_cutoff": str(pd.Timestamp(face["idx"][-1]).date()),
        "script": "scripts/etf_book_capacity_rule.py",
        "config": {"target_beta": target, "k_bp": k_bp, "base_bp": C.BASE_BP,
                   "rebal": REBAL, "n_hold": F.N_HOLD, "start": start,
                   "nav_grid": list(NAV_GRID), "ref_nav": REF_NAV,
                   "live_from": str(pd.Timestamp(face["k"].dropna().index[0]).date())
                   if len(face["k"].dropna()) else None},
        "rule_at_8bp_no_size": rule_m0,
        "flat_at_8bp_no_size": flat_m0,
        "pool_equal_weight": ew_m,
        "market": mkt_m,
        "ladder": ladders,
        "breakeven_nav_vs_ew": {a: _breakeven(ladders[a]) for a in ladders},
        "peak_dollar_profit_nav": {a: _peak_nav(ladders[a]) for a in ladders},
        "peak_dollar_profit_cny": {a: _peak_dollar(ladders[a]) for a in ladders},
        "participation_ceiling_1pct_adv": ceiling,
        "k_stats": _k_stats(face),
        "cash_leg": {"rf_mean_ann_pct": round(float(rf.mean()) * 252.0 * 100.0, 3),
                     "rf_missing_days": int(face["rf_missing"])},
        "engine": {"rebal_turnover": round(float(face["rebal_turnover"]), 4),
                   "open_gapfill": int(face["gapfill"])},
        "method_note": ("two arms, one engine, one window: rule (k=0.20/beta + repo cash) "
                        "vs flat (k=1) on the SAME picks and grid, both priced from the "
                        "realised weight path at 8bp + K*sqrt(p/1%) using ADV known one bar "
                        "before the fill"),
    }
    return out


def _k_stats(face):
    k = face["k"].dropna()
    if not len(k):
        return {}
    return {"bars": int(len(k)),
            "first": str(pd.Timestamp(k.index[0]).date()),
            "last": str(pd.Timestamp(k.index[-1]).date()),
            "mean": round(float(k.mean()), 4), "p50": round(float(k.median()), 4),
            "min": round(float(k.min()), 4), "max": round(float(k.max()), 4),
            "share_full_invest": round(float((k >= 0.999).mean()), 4),
            "decisions": int(len(face["sched"]))}


def _print(out):
    print("window %s -> %s | rule live from %s | k mean %.3f (min %.3f)"
          % (out["config"]["start"], out["evidence_cutoff"],
             out["config"]["live_from"], out["k_stats"].get("mean", float("nan")),
             out["k_stats"].get("min", float("nan"))))
    for arm in ("rule", "flat"):
        m = out["%s_at_8bp_no_size" % arm]
        print("%-5s @8bp no size : cagr %6.2f%%  vol %5.2f%%  sharpe %5.3f  maxdd %6.2f%%"
              % (arm, 100 * m["cagr"], 100 * m["vol"], m["sharpe"], 100 * m["maxdd"]))
    print("\n NAV        rule cagr  rule $/yr   rule $tot   flat cagr  flat $/yr   rule p90 part  cost bp")
    for r, f in zip(out["ladder"]["rule"], out["ladder"]["flat"]):
        print(" %-10.0f %8.2f%% %11.0f %11.0f %9.2f%% %10.0f %12s %9s"
              % (r["nav"], 100 * (r.get("cagr") or 0), r.get("annual_profit_cny") or 0,
                 r.get("total_profit_cny") or 0,
                 100 * (f.get("cagr") or 0), f.get("annual_profit_cny") or 0,
                 ("%.3f%%" % (100 * r["participation_max_p90"]))
                 if r.get("participation_max_p90") is not None else "-",
                 ("%.1f" % r["cost_bp_avg_per_side"])
                 if r.get("cost_bp_avg_per_side") is not None else "-"))
    print("\npeak $/yr: rule %s CNY at NAV %s | flat %s CNY at NAV %s"
          % (out["peak_dollar_profit_cny"]["rule"], out["peak_dollar_profit_nav"]["rule"],
             out["peak_dollar_profit_cny"]["flat"], out["peak_dollar_profit_nav"]["flat"]))
    print("1%% ADV ceiling (p90 trade): rule %s | flat %s"
          % (out["participation_ceiling_1pct_adv"]["rule"],
             out["participation_ceiling_1pct_adv"]["flat"]))


# ---------------------------------------------------------------------------- selftest
def selftest():
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        print("[%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))
        ok = ok and bool(cond)

    # ---- 1) base-only, k=1 path reproduces the engine's own flat-cost curve -----
    close, openp, amt, feats = F.build_panel()
    score = F.build_score(close, amt, feats)
    rec = Recorder()
    gross, turn, _ = F.run_next_open(close, openp, amt, feats, REBAL, cost=rec,
                                     start="2024-01-01", score=score)
    rp = gross.pct_change().fillna(0.0)
    face = {"close": close, "amt": amt, "idx": rp.index, "rp": rp,
            "rf": pd.Series(0.0, index=rp.index), "k": pd.Series(1.0, index=rp.index),
            "fills": rec.fills, "market": close[next(c for c in BT.MKT if c in close.columns)]}
    mine, crows, cnt = curve(face, 0.0, k_bp=0.0, base_bp=F.COST * 1e4 * 1.0,
                             k_override=1.0, trace=True)
    ref, _, _ = F.run_next_open(close, openp, amt, feats, REBAL, cost=F.COST,
                                start="2024-01-01", score=score)
    common = mine.index.intersection(ref.index)
    d = float(np.abs(mine.reindex(common).values /
                     mine.reindex(common).values[0] -
                     ref.reindex(common).values / ref.reindex(common).values[0]).max())
    chk("base-only k=1 == engine flat path", d < 1e-12, "max|d|=%.2e" % d)
    chk("activity: trades actually happened",
        bool(crows) and sum(c["turnover"] for c in crows) > 0.5,
        "sum turnover %.3f over %d bars" % (sum(c["turnover"] for c in crows), len(crows)))

    # ---- 2) the weight path is a partition of NAV ------------------------------
    face2 = dict(face)
    face2["k"] = pd.Series(np.linspace(1.0, 0.2, len(rp)), index=rp.index)
    path = weight_path(face2)
    worst = max(abs(sum(w.values()) + cash - 1.0) for _d, w, cash in path)
    chk("weights + cash == 1 every bar", worst < 1e-12, "worst %.2e" % worst)
    chk("k series drives the book weight",
        abs(sum(path[-1][1].values()) - 0.2) < 1e-12 and abs(path[-1][2] - 0.8) < 1e-12,
        "last book %.2f cash %.2f" % (sum(path[-1][1].values()), path[-1][2]))

    # ---- 3) impact formula is exactly the stated one ---------------------------
    adv = pd.Series({"AAA": 1e8}, index=pd.to_datetime(["2021-01-05"]))
    amt2 = pd.DataFrame({"AAA": [1e8, 1e8, 1e8]},
                        index=pd.to_datetime(["2021-01-04", "2021-01-05", "2021-01-06"]))
    legs = _cost_legs({}, {"AAA": 0.5}, C.adv_at(amt2, "2021-01-05", back=1), 1e6,
                      10.0, 8.0, 100.0)
    exp = 8.0 + 10.0 * np.sqrt(0.005 / 0.01)
    chk("impact bp exact", abs(legs[0]["bp"] - exp) < 1e-12,
        "%.6f vs %.6f bp" % (legs[0]["bp"], exp))

    # ---- 4) square-root shape and monotonicity in NAV --------------------------
    lo = _cost_legs({}, {"AAA": 0.5}, C.adv_at(amt2, "2021-01-05", back=1), 2e6,
                    10.0, 8.0, 100.0)[0]["bp"]
    hi = _cost_legs({}, {"AAA": 0.5}, C.adv_at(amt2, "2021-01-05", back=1), 8e6,
                    10.0, 8.0, 100.0)[0]["bp"]
    chk("4x NAV -> 2x the impact part",
        abs((hi - 8.0) / (lo - 8.0) - 2.0) < 1e-9, "ratio %.6f" % ((hi - 8.0) / (lo - 8.0)))

    # ---- 5) a name with no ADV is charged punitively, never the base rate ------
    amt3 = pd.DataFrame({"AAA": [np.nan, np.nan, np.nan]},
                        index=pd.to_datetime(["2021-01-04", "2021-01-05", "2021-01-06"]))
    lg = _cost_legs({}, {"AAA": 0.5}, C.adv_at(amt3, "2021-01-05", back=1), 1e6,
                    10.0, 8.0, 100.0)
    chk("missing ADV -> punitive, counted",
        lg[0]["missing_adv"] and abs(lg[0]["bp"] - 100.0) < 1e-12, "bp %.1f" % lg[0]["bp"])

    # ---- 6) a k move is charged once, at the k it lands on ---------------------
    prev = {"AAA": 0.5, "BBB": 0.5}
    new = {"AAA": 0.25, "BBB": 0.25}
    lg2 = _cost_legs(prev, new, C.adv_at(amt2, "2021-01-05", back=1), 1e6, 10.0, 8.0, 100.0)
    chk("k move trades the basket proportionally",
        abs(sum(l["dw"] for l in lg2) - 0.5) < 1e-12,
        "traded weight %.4f" % sum(l["dw"] for l in lg2))
    chk("exiting a name is charged its full old weight",
        abs(_cost_legs({"AAA": 0.5}, {}, C.adv_at(amt2, "2021-01-05", back=1), 1e6,
                       10.0, 8.0, 100.0)[0]["dw"] - 0.5) < 1e-12)

    # ---- 7) k=0 parks everything in cash: only the repo leg accrues ------------
    rpz = pd.Series(0.01, index=pd.to_datetime(["2021-01-04", "2021-01-05", "2021-01-06"]))
    facez = {"close": close, "amt": amt2, "idx": rpz.index, "rp": rpz,
             "rf": pd.Series(0.0001, index=rpz.index),
             "k": pd.Series(0.0, index=rpz.index), "fills": [], "market": rpz}
    z, _zr, _zc = curve(facez, 1e6, k_bp=10.0)
    chk("k=0 -> cash only, no book return",
        abs(float(z.iloc[-1]) - (1.0001 ** 3)) < 1e-12, "nav %.8f" % float(z.iloc[-1]))

    # ---- 8) the ladder's dollar-profit picker finds the interior peak ----------
    lad = [{"nav": n, "annual_profit_cny": v} for n, v in
           ((1e6, 9e4), (5e6, 4e5), (1e7, 7e5), (1e8, 3e5))]
    chk("peak $/yr is interior, not the widest NAV", _peak_nav(lad) == 1e7,
        "picked %.0f" % _peak_nav(lad))
    chk("peak $/yr reports the money, not the NAV again",
        _peak_dollar(lad) == 7e5, "reported %.0f" % _peak_dollar(lad))
    chk("breakeven takes the LAST NAV still beating EW",
        _breakeven([{"nav": 1e6, "excess_vs_ew_pp": 2.0},
                    {"nav": 1e7, "excess_vs_ew_pp": 0.5},
                    {"nav": 1e8, "excess_vs_ew_pp": -1.0}]) == 1e7)
    chk("a ladder with no profit column yields no peak, not zero",
        _peak_nav([{"nav": 1e6}]) is None and _peak_dollar([{"nav": 1e6}]) is None)
    # ---- 8b) the ceiling divides by a FRACTION, and is 100x the percent misread ---
    chk("ceiling reads participation as a fraction",
        abs(_ceiling_nav(1e7, 0.0655) - 1526717.6) < 1.0,
        "%.1f" % _ceiling_nav(1e7, 0.0655))
    chk("reading 6.55 as a percent shrinks the ceiling 100x",
        abs(_ceiling_nav(1e7, 6.55) * 100.0 / _ceiling_nav(1e7, 0.0655) - 1.0) < 1e-5)

    # ---- 9) no lookahead: k in force lags its own decision --------------------
    sched = [(pd.Timestamp("2021-01-06"), 0.4, 0.5)]
    ser = _applied_k(sched, pd.to_datetime(["2021-01-04", "2021-01-05",
                                            "2021-01-06", "2021-01-07"]))
    chk("k decision applies from the NEXT bar",
        np.isnan(ser.loc["2021-01-05"]) and np.isnan(ser.loc["2021-01-06"])
        and abs(ser.loc["2021-01-07"] - 0.4) < 1e-12, str(list(ser.values)))

    print("\n%d/%d" % (17 if ok else 0, 17))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--target", type=float, default=TARGET_BETA)
    ap.add_argument("--k-bp", type=float, default=C.IMPACT_BP_PER_PCT)
    ap.add_argument("--start", default=START)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    if args.cmd == "--selftest" or args.cmd == "selftest":
        return selftest()
    out = run(target=args.target, k_bp=args.k_bp, start=args.start)
    dest = args.out or os.path.join(F.PATHS.results_dir, "etf_book_capacity_rule.json")
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=float)
    _print(out)
    print("\nwrote %s" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())