#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""the ladder's 26.7 %/yr is one number over 1052 bars; which years made it?

WHY THIS FILE EXISTS
--------------------
`scripts/idx_fut_carry_ladder_risk.py` measured every rung's volatility, drawdown and
Sharpe over the whole sample as one block, and `idx_fut_carry_drawdown_experience`
translated the worst of it into a customer's units (worst month, longest run under
water, time to get back).  Neither answers the question a reader holding this book for
four years would ask first: **which years produced the money?**  A book that compounds
26.7 %/yr with one great year and three flat ones is a totally different object from a
book that earns the same number every year, and every face published so far would print
the same headline for both.

This face is also the first rung arithmetic written after r2106 caught the double-scaled
equity sleeve in `ladder_risk` (`m = k * sleeve` and then `daily = k * m`, i.e. k^2).
That face may not be rewritten in a contention window, so the corrected per-rung series
is published here and the deviation is recorded in `cross_face` -- a reader must never be
handed two annualised numbers for the same rung without being told why.

WHAT IT MEASURES
----------------
For every rung on `results/policy_return_lattice.json`:
  * the rung's daily return series, rebuilt from the same imported legs (`product_spread`)
    and the same imported sleeve (`adopted_book`) the sibling face uses, with the sleeve
    weighted by `k` exactly once;
  * per calendar year: the year's realised compound return, its own annualised vol, its
    own max drawdown inside the year, and the same return in CNY on the ladder's NAV;
  * the concentration readings: the best year, the share of total compounded growth that
    year produced, and the same book with the best year's bars removed (ex-one-year CAGR)
    together with what that year was worth in pp/yr.

judgment tokens (frozen before the first run, on the instructed rung):
  ONE_YEAR_CARRIES_THE_BOOK        removing the best year costs >= 50 % of the CAGR
  RETURN_IS_SPREAD_ACROSS_YEARS    removing it costs <= 25 % of the CAGR
  SOME_YEARS_CARRY_MORE_THAN_OTHERS  in between
  NO_NEGATIVE_YEAR_IN_SAMPLE       every calendar year of the sample compounded positive
  LOSS_YEARS_IN_SAMPLE             at least one did not (the years are printed)
  BAND_WORST_YEAR_BETTER_PER_RISK  the in-band rung's worst year, divided by its own vol,
                                   beats the instructed rung's by >= 0.10
  BAND_WORST_YEAR_NOT_BETTER       it does not
  DATA_BLOCKED                     a series is missing or too short; refuse, never 0

the worst-year comparison is run per unit of risk (return / the rung's own vol), because
the two rungs are different-sized books: a smaller book earning a smaller number is not a
worse year.  The first draft compared raw returns and said "not better" for a book that was
in fact better per unit of risk -- fixed before the first run.

nothing here re-derives a leg, a sleeve, a weight or a notional: all of them come from
the published modules and faces by import/read.  `check` re-probes the two futures legs
and the digest of both upstream faces; the sleeve's own daily series (~65 s) is pinned
by digest only, and that scope is printed on the face.

Usage:
    python scripts/idx_fut_carry_ladder_years.py run [--write-doc]
    python scripts/idx_fut_carry_ladder_years.py check
    python scripts/idx_fut_carry_ladder_years.py --selftest
"""
from __future__ import annotations

import argparse
import io
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

SCHEMA = "idx-fut-carry-ladder-years/v1"
KIND = "carry_ladder_year_arithmetic"
OUT = os.path.join(ROOT, "results", "idx_fut_carry_ladder_years.json")
DOC = os.path.join(ROOT, "research", "IDX_FUT_CARRY_LADDER_YEARS.md")
LATTICE = os.path.join(ROOT, "results", "policy_return_lattice.json")
L1_ARM = os.path.join(ROOT, "results", "etf_nobond_vt.json")
RISK_FACE = os.path.join(ROOT, "results", "idx_fut_carry_ladder_risk.json")

MIN_DAYS = 400
TOL_RATIO = 0.10            # "the worst year is better per unit of risk" tolerance, return/vol
CONCENTRATED = 0.50          # ex-best cost >= this share of CAGR = one year carries it
SPREAD = 0.25                # <= this share = the return is spread out

V_ONE = "ONE_YEAR_CARRIES_THE_BOOK"
V_SPREAD = "RETURN_IS_SPREAD_ACROSS_YEARS"
V_MIXED = "SOME_YEARS_CARRY_MORE_THAN_OTHERS"
V_NO_NEG = "NO_NEGATIVE_YEAR_IN_SAMPLE"
V_NEG = "LOSS_YEARS_IN_SAMPLE"
V_SHAPE_CUTS = "BAND_WORST_YEAR_BETTER_PER_RISK"
V_SHAPE_NOT = "BAND_WORST_YEAR_NOT_BETTER"
V_BLOCK = "DATA_BLOCKED"
V_OK = "CHECK_OK"
V_STALE = "STALE"
V_FAIL = "CHECK FAILED"

RC_OK, RC_STALE, RC_FAIL = 0, 3, 4


# ---------------------------------------------------------------- arithmetic (pure)
def year_key(date):
    return str(date)[:4]


def group_by_year(dates, series):
    """{year: [daily returns in date order]} -- no reordering, no gap filling."""
    out = {}
    for d, r in zip(dates, series):
        out.setdefault(year_key(d), []).append(float(r))
    return out


def compound_pct(returns):
    """The actual compound return of a slice, in percent (not annualised)."""
    lvl = 1.0
    for r in returns:
        lvl *= (1.0 + r)
    return (lvl - 1.0) * 100.0


def per_year(dates, series, nav, stats):
    """Per calendar year: realised return, own vol, own drawdown inside the year, money."""
    rows = {}
    for y, rets in sorted(group_by_year(dates, series).items()):
        ret = compound_pct(rets)
        rows[y] = {"days": len(rets),
                   "return_pct": round(ret, 3),
                   "ann_vol_pct": _round(stats["ann_vol"](rets), 3),
                   "mdd_pct": round(stats["mdd"](rets), 3),
                   "money_cny": round(ret / 100.0 * nav, 2)}
    return rows


def drop_year(dates, series, year):
    """The same series without one year's bars (the days go too, not just the returns)."""
    keep = [(d, r) for d, r in zip(dates, series) if year_key(d) != year]
    return [d for d, _ in keep], [r for _, r in keep]


def concentration(dates, series, stats):
    """The best year, its share of compounded growth, and the ex-best-year CAGR."""
    rows = per_year(dates, series, 1.0, stats)
    if not rows:
        return None
    best = max(rows, key=lambda y: rows[y]["return_pct"])
    full_lvl = 1.0
    for r in series:
        full_lvl *= (1.0 + r)
    best_lvl = 1.0 + rows[best]["return_pct"] / 100.0
    share = None
    if full_lvl > 0 and best_lvl > 0 and full_lvl != 1.0:
        share = math.log(best_lvl) / math.log(full_lvl)
    rest_d, rest_s = drop_year(dates, series, best)
    cagr_all = stats["ann_compound"](series)
    cagr_ex = stats["ann_compound"](rest_s) if rest_s else None
    cost = None
    if cagr_all is not None and cagr_ex is not None:
        cost = cagr_all - cagr_ex
    return {"best_year": best,
            "best_year_return_pct": rows[best]["return_pct"],
            "best_year_share_of_growth": _round(share, 4),
            "cagr_pct": _round(cagr_all, 3),
            "cagr_ex_best_pct": _round(cagr_ex, 3),
            "best_year_cost_pp": _round(cost, 3),
            "cagr_ex_best_days": len(rest_s),
            "worst_year": min(rows, key=lambda y: rows[y]["return_pct"]),
            "negative_years": [y for y in sorted(rows) if rows[y]["return_pct"] < 0.0]}


def _round(x, n):
    return None if x is None else round(x, n)


def loss_years(rung):
    """Years whose own compound was negative -- read off the year table, not a stored list."""
    years = rung.get("years") or {}
    if years:
        return [y for y in sorted(years) if float(years[y]["return_pct"]) < 0.0]
    return list((rung.get("concentration") or {}).get("negative_years") or [])


def worst_year_per_risk(rung):
    """The rung's worst year divided by the rung's own full-period vol (scale-free)."""
    c = rung["concentration"]
    vol = (rung.get("full") or {}).get("ann_vol_pct")
    if not vol or vol <= 0:
        return None
    return rung["years"][c["worst_year"]]["return_pct"] / vol


def calibration(rung):
    """How often a year cleared the ladder's expected-return column (not annualised)."""
    exp = rung.get("expected_return_pct")
    years = rung["years"]
    if exp is None:
        return None
    above = [y for y in sorted(years) if years[y]["return_pct"] >= exp]
    return {"expected_pct": round(float(exp), 3),
            "years_above_expected": len(above),
            "years_below_expected": len(years) - len(above),
            "below": [y for y in sorted(years) if years[y]["return_pct"] < exp]}


def judge(rungs, engine_key, band_key, concentrated=CONCENTRATED,
          spread=SPREAD, tol_ratio=TOL_RATIO):
    """The year-shape verdicts, derived from the published numbers only (pure)."""
    eng = rungs[engine_key]
    band = rungs[band_key]
    cagr = eng["concentration"]["cagr_pct"]
    cost = eng["concentration"]["best_year_cost_pp"]
    share = cost / cagr if (cagr and cagr > 0 and cost is not None) else None
    if share is None:
        token = V_BLOCK
    elif share >= concentrated:
        token = V_ONE
    elif share <= spread:
        token = V_SPREAD
    else:
        token = V_MIXED
    neg = loss_years(eng)
    sign = V_NEG if neg else V_NO_NEG
    eng_ratio = worst_year_per_risk(eng)
    band_ratio = worst_year_per_risk(band)
    if eng_ratio is None or band_ratio is None:
        shape, delta = V_BLOCK, None
    else:
        delta = band_ratio - eng_ratio
        shape = V_SHAPE_CUTS if delta >= tol_ratio else V_SHAPE_NOT
    return {"year_concentration": token,
            "best_year_cost_share_of_cagr": _round(share, 4),
            "year_sign": sign,
            "loss_years": neg,
            "engine_worst_year": eng["concentration"]["worst_year"],
            "engine_worst_year_pct": round(
                eng["years"][eng["concentration"]["worst_year"]]["return_pct"], 3),
            "engine_worst_year_per_vol": _round(eng_ratio, 4),
            "band_worst_year_pct": round(
                band["years"][band["concentration"]["worst_year"]]["return_pct"], 3),
            "band_worst_year_per_vol": _round(band_ratio, 4),
            "band_minus_engine_per_vol": _round(delta, 4),
            "worst_year_shape": shape}


# ---------------------------------------------------------------- measurement
def _lr():
    """The sibling face's own arithmetic and readers -- imported, never re-implemented."""
    import idx_fut_carry_ladder_risk as LR
    return LR


def stats():
    LR = _lr()
    return {"ann_vol": LR.ann_vol, "ann_compound": LR.ann_compound, "mdd": LR.mdd_pct}


def attribution(dates, comps):
    """Per year, what each piece contributed, as sums of daily contributions in pp.

    The three pieces add exactly to the year's *summed daily return*; compounding makes the
    year's compound figure a little different, so both are printed and neither is guessed.
    """
    rows = {}
    for i, d in enumerate(dates):
        y = year_key(d)
        row = rows.setdefault(y, {"sleeve_pp": 0.0, "ic_pp": 0.0, "im_pp": 0.0, "days": 0})
        row["sleeve_pp"] += comps["sleeve"][i] * 100.0
        row["ic_pp"] += comps["ic"][i] * 100.0
        row["im_pp"] += comps["im"][i] * 100.0
        row["days"] += 1
    for y, row in rows.items():
        row["sum_pp"] = row["sleeve_pp"] + row["ic_pp"] + row["im_pp"]
        for k2 in ("sleeve_pp", "ic_pp", "im_pp", "sum_pp"):
            row[k2] = round(row[k2], 3)
    return rows


def rung_series(lattice, legs, sleeve, k, ic_lots, im_lots):
    """The rung's daily returns on days all three series quote; sleeve weighted by k once."""
    LR = _lr()
    n_lot = LR.per_lot_notional(lattice)
    nav = float(lattice["nav_cny"])
    w_ic = ic_lots * (n_lot["IC"] or 0.0) / nav
    w_im = im_lots * (n_lot["IM"] or 0.0) / nav
    sleeve_d = dict(zip(sleeve["dates"], sleeve["daily"]))
    ic_d = dict(zip(legs["IC"]["dates"], legs["IC"]["spread"]))
    im_d = dict(zip(legs["IM"]["dates"], legs["IM"]["spread"]))
    common = [d for d in sorted(sleeve_d) if d in ic_d and d in im_d]
    # k * sleeve, and the legs at their notional weight: k appears exactly once (r2106)
    comps = {"sleeve": [k * sleeve_d[d] for d in common],
             "ic": [w_ic * ic_d[d] for d in common],
             "im": [w_im * im_d[d] for d in common]}
    daily = [comps["sleeve"][i] + comps["ic"][i] + comps["im"][i]
             for i in range(len(common))]
    return {"dates": common, "daily": daily, "comps": comps,
            "weight_ic": w_ic, "weight_im": w_im, "days": len(daily)}


def build():
    """Full measurement.  Returns (face, None) or None plus a refusal dict."""
    LR = _lr()
    if not os.path.exists(LATTICE):
        return None, {"verdict": V_BLOCK, "why": "ladder face missing: %s" % LATTICE}
    lattice = LR.read_json(LATTICE)
    legs = {p: LR.spread_leg(p) for p in ("IC", "IM")}
    for p, leg in legs.items():
        if "_refused" in leg:
            return None, {"verdict": V_BLOCK, "why": "leg %s refused: %s" % (p, leg["_refused"])}
        if leg["days"] < MIN_DAYS:
            return None, {"verdict": V_BLOCK,
                          "why": "leg %s has %d days, need %d" % (p, leg["days"], MIN_DAYS)}
    sleeve = LR.equity_sleeve()
    if "_refused" in sleeve:
        return None, {"verdict": V_BLOCK, "why": "equity sleeve refused: %s" % sleeve["_refused"]}
    cfg = stats()
    nav = float(lattice["nav_cny"])
    k = float(lattice["inputs"]["k"])

    rungs = {}
    for r in lattice["lattice"]:
        icl, iml = int(r["ic_lots"]), int(r["im_lots"])
        ser = rung_series(lattice, legs, sleeve, k, icl, iml)
        if ser["days"] < MIN_DAYS:
            return None, {"verdict": V_BLOCK,
                          "why": "rung %d/%d has %d common days" % (icl, iml, ser["days"])}
        conc = concentration(ser["dates"], ser["daily"], cfg)
        entry = {
            "ic_lots": icl, "im_lots": iml,
            "weight_ic": round(ser["weight_ic"], 6),
            "weight_im": round(ser["weight_im"], 6),
            "expected_return_pct": float(r["expected_return_pct"]),
            "days": ser["days"],
            "full": {"cagr_pct": _round(cfg["ann_compound"](ser["daily"]), 3),
                     "ann_vol_pct": _round(cfg["ann_vol"](ser["daily"]), 3),
                     "mdd_pct": round(cfg["mdd"](ser["daily"]), 3)},
            "years": per_year(ser["dates"], ser["daily"], nav, cfg),
            "attribution": attribution(ser["dates"], ser["comps"]),
            "concentration": conc,
        }
        entry["calibration"] = calibration(entry)
        rungs["%d/%d" % (icl, iml)] = entry

    engine = lattice.get("engine_rung") or {}
    engine_key = "%d/%d" % (int(engine.get("ic_lots", 0)), int(engine.get("im_lots", 0)))
    in_band = [r for r in lattice["lattice"]
               if r.get("feasible") and 8.0 <= float(r["expected_return_pct"]) <= 12.0]
    if engine_key not in rungs:
        return None, {"verdict": V_BLOCK, "why": "engine rung %s not on the ladder" % engine_key}
    if not in_band:
        return None, {"verdict": V_BLOCK,
                      "why": "ladder prints no in-band rung; the shape comparison has no arm"}
    band_key = "%d/%d" % (int(in_band[0]["ic_lots"]), int(in_band[0]["im_lots"]))

    cross = {}
    if os.path.exists(RISK_FACE):
        prev = LR.read_json(RISK_FACE)
        pub = (((prev.get("measured") or {}).get("rungs") or {}).get(engine_key) or {})
        here = rungs[engine_key]["full"]["cagr_pct"]
        published = pub.get("measured_ann_pct")
        cross = {"face": "results/idx_fut_carry_ladder_risk.json",
                 "face_sha256": LR.digest(RISK_FACE),
                 "rung": engine_key,
                 "published_ann_pct": published,
                 "here_ann_pct": here,
                 "gap_pp": _round(here - published, 3) if (here is not None
                                                           and published is not None) else None,
                 "reading": ("the published face weights the equity sleeve by k twice "
                             "(m = k*sleeve, then daily = k*m); this face weights it once. "
                             "The futures legs are identical in both, so the whole gap is the "
                             "sleeve's k^2 - k. Recorded, not repaired: that face is a shared "
                             "face and this is a contention window (r2106 cross_face).")}
    face = {
        "schema": SCHEMA,
        "kind": KIND,
        "evidence_cutoff": min([legs["IC"]["span"][1], legs["IM"]["span"][1],
                                sleeve["span"][1]]),
        "inputs": {
            "lattice": {"path": "results/policy_return_lattice.json", "sha256": LR.digest(LATTICE)},
            "l1_arm": {"path": "results/etf_nobond_vt.json",
                       "sha256": LR.digest(L1_ARM) if os.path.exists(L1_ARM) else None},
            "nav_cny": nav, "k": k, "trading_days": cfg_year_days(),
            "legs": {p: {"span": legs[p]["span"], "days": legs[p]["days"], "index": legs[p]["index"]}
                     for p in ("IC", "IM")},
            "equity_span": sleeve["span"],
        },
        "measured": {"rungs": rungs,
                     "years": sorted({y for r in rungs.values() for y in r["years"]})},
        "engine_rung": engine_key,
        "in_band_rung": band_key,
        "judgment": judge(rungs, engine_key, band_key),
        "cross_face": cross,
        "check_scope": ("check re-probes both futures legs (spread series) and the digest of the "
                        "ladder and the L1 arm; the equity sleeve's daily series (~65 s) is never "
                        "re-derived by check -- it is pinned by the L1 arm digest only. Nothing "
                        "is read from another face's numbers: the rung series are rebuilt here."),
    }
    return face, None


def cfg_year_days():
    import idx_fut_basis as B
    return float(B.TRADING_DAYS)


# ---------------------------------------------------------------- page
def _pct(x, n=2):
    return "--" if x is None else ("{:.%df}%%" % n).format(x)


def render_page(face):
    m = face["measured"]
    j = face["judgment"]
    eng = m["rungs"][face["engine_rung"]]
    band = m["rungs"][face["in_band_rung"]]
    years = m["years"]
    L = []
    L.append("# Which years made the ladder's return")
    L.append("")
    L.append("generated %s | cutoff %s | schema `%s`"
             % (face["generated"] if "generated" in face else "--",
                face["evidence_cutoff"], face["schema"]))
    L.append("")
    L.append("## One sentence")
    L.append("")
    L.append("The instructed rung (%s) compounds **%s**/yr over %d bars, but its best year "
             "(**%s**, %s) supplies **%s** of the compounded growth; take that year's bars out "
             "and the same book earns **%s**/yr -- so **%s**."
             % (face["engine_rung"], _pct(eng["full"]["cagr_pct"]), eng["days"],
                eng["concentration"]["best_year"],
                _pct(eng["concentration"]["best_year_return_pct"]),
                _pct(100.0 * (eng["concentration"]["best_year_share_of_growth"] or 0.0), 1),
                _pct(eng["concentration"]["cagr_ex_best_pct"]),
                j["year_concentration"]))
    L.append("")
    L.append("## Every rung, year by year (realised return, %)")
    L.append("")
    head = "| IC/IM lots | expected %/yr | " + " | ".join(years) + " | full CAGR | vol | MDD |"
    L.append(head)
    L.append("|" + "---|" * (len(years) + 5))
    for key in sorted(m["rungs"], key=lambda x: (m["rungs"][x]["ic_lots"],
                                                 m["rungs"][x]["im_lots"])):
        r = m["rungs"][key]
        cells = [_pct(r["years"][y]["return_pct"]) if y in r["years"] else "--" for y in years]
        tag = ""
        if key == face["engine_rung"]:
            tag = " **<- instruction**"
        elif key == face["in_band_rung"]:
            tag = " *(in band)*"
        L.append("| %s%s | %s | %s | %s | %s | %s |"
                 % (key, tag, _pct(r["expected_return_pct"]), " | ".join(cells),
                    _pct(r["full"]["cagr_pct"]), _pct(r["full"]["ann_vol_pct"]),
                    _pct(r["full"]["mdd_pct"])))
    L.append("")
    L.append("## What the best year is worth, rung by rung")
    L.append("")
    L.append("| IC/IM lots | best year | its return | share of growth | CAGR without it | cost pp/yr | worst year |")
    L.append("|---|---|---|---|---|---|---|")
    for key in sorted(m["rungs"], key=lambda x: (m["rungs"][x]["ic_lots"],
                                                 m["rungs"][x]["im_lots"])):
        c = m["rungs"][key]["concentration"]
        L.append("| %s | %s | %s | %s | %s | %s | %s (%s) |"
                 % (key, c["best_year"], _pct(c["best_year_return_pct"]),
                    _pct(100.0 * (c["best_year_share_of_growth"] or 0.0), 1),
                    _pct(c["cagr_ex_best_pct"]), _pct(c["best_year_cost_pp"]),
                    c["worst_year"],
                    _pct(m["rungs"][key]["years"][c["worst_year"]]["return_pct"])))
    L.append("")
    L.append("## The three readings")
    L.append("")
    L.append("1. **Is the return concentrated in one year?** — `%s`: the best year (%s) is worth "
             "%s of the CAGR, so removing its bars leaves **%s**/yr instead of %s."
             % (j["year_concentration"], eng["concentration"]["best_year"],
                _pct(100.0 * (j["best_year_cost_share_of_cagr"] or 0.0), 1),
                _pct(eng["concentration"]["cagr_ex_best_pct"]),
                _pct(eng["concentration"]["cagr_pct"])))
    L.append("2. **Did any year lose money?** — `%s`: %s. The instructed rung's worst year is "
             "**%s %s**; the in-band rung's is %s %s."
             % (j["year_sign"], ("years down: " + ", ".join(j["loss_years"]))
                if j["loss_years"] else "every calendar year of the sample compounded positive",
                j["engine_worst_year"], _pct(j["engine_worst_year_pct"]),
                band["concentration"]["worst_year"], _pct(j["band_worst_year_pct"])))
    L.append("3. **Is the in-band rung's worst year better per unit of risk?** — `%s`: "
             "return/vol %s vs %s (%+0.3f). Different-sized books, so the raw pp of #2 is not a "
             "risk comparison."
             % (j["worst_year_shape"],
                "--" if j["band_worst_year_per_vol"] is None else "%.3f" % j["band_worst_year_per_vol"],
                "--" if j["engine_worst_year_per_vol"] is None
                else "%.3f" % j["engine_worst_year_per_vol"],
                0.0 if j["band_minus_engine_per_vol"] is None else j["band_minus_engine_per_vol"]))
    L.append("")
    L.append("## Where each year's return came from (instructed rung %s, pp of NAV)"
             % face["engine_rung"])
    L.append("")
    L.append("| year | days | equity sleeve | IC leg | IM leg | sum of daily pp | that year's compound |")
    L.append("|---|---|---|---|---|---|---|")
    for y in years:
        a = eng["attribution"].get(y) or {}
        comp = (eng["years"].get(y) or {}).get("return_pct")
        L.append("| %s | %s | %s | %s | %s | %s | %s |"
                 % (y, a.get("days"),
                    "--" if a.get("sleeve_pp") is None else "%+0.2f" % a["sleeve_pp"],
                    "--" if a.get("ic_pp") is None else "%+0.2f" % a["ic_pp"],
                    "--" if a.get("im_pp") is None else "%+0.2f" % a["im_pp"],
                    _pct(a.get("sum_pp")), _pct(comp)))
    L.append("")
    best_y = eng["concentration"]["best_year"]
    ba = eng["attribution"].get(best_y) or {}
    legs_pp = (ba.get("ic_pp") or 0.0) + (ba.get("im_pp") or 0.0)
    L.append("The three pieces add exactly to the year's summed daily return; the last column "
             "compounds those days, so it differs from the sum -- and in a strongly trending "
             "year the compound can exceed it (all rungs' %s does). This table is the one that "
             "stops a %s-shaped year from being read as one thing: of the year's %s pp summed, "
             "the equity sleeve supplied %s pp and the two legs %s pp -- the sleeve is the piece "
             "every rung shares, the lot count is what varies."
             % (best_y, best_y,
                "%.2f" % (ba.get("sum_pp") or 0.0),
                "%.2f" % (ba.get("sleeve_pp") or 0.0), "%.2f" % legs_pp))
    L.append("")
    L.append("## Is the ladder's expected column a promise?")
    L.append("")
    L.append("| IC/IM lots | expected %/yr | years above it | years below it | below |")
    L.append("|---|---|---|---|---|")
    for key in sorted(m["rungs"], key=lambda x: (m["rungs"][x]["ic_lots"],
                                                 m["rungs"][x]["im_lots"])):
        c = m["rungs"][key].get("calibration") or {}
        L.append("| %s | %s | %s | %s | %s |"
                 % (key, _pct(c.get("expected_pct")), c.get("years_above_expected"),
                    c.get("years_below_expected"), ", ".join(c.get("below") or []) or "--"))
    L.append("")
    L.append("A year's return here is that year's own compound, so a partial year (the first "
             "and the last) is not comparable to a full one; the counts are printed, not scored.")
    L.append("")
    if face["cross_face"]:
        c = face["cross_face"]
        L.append("## Same rung, two annualised numbers")
        L.append("")
        L.append("`%s` publishes %s as **%s**/yr for rung %s; this face rebuilds the same rung "
                 "as **%s**/yr (gap %s pp). The published face weights the equity sleeve by `k` "
                 "twice; the legs are identical in both, so the gap is the sleeve's k^2-k. "
                 "Recorded here, not repaired there: that face is a shared face."
                 % (c["face"], c["rung"], _pct(c["published_ann_pct"]), c["rung"],
                    _pct(c["here_ann_pct"]),
                    "--" if c["gap_pp"] is None else "%.2f" % c["gap_pp"]))
        L.append("")
    L.append("## What this face does NOT do")
    L.append("")
    L.append("* it does not re-derive a leg or the sleeve: both are imported from the same "
             "authority modules the risk face uses;")
    L.append("* it does not rewrite `idx_fut_carry_ladder_risk` (shared face, contention window);")
    L.append("* every reading is in-sample over %d bars; a year's return is that year's own "
             "compound, never annualised from a partial year." % eng["days"])
    L.append("")
    L.append("## Usage")
    L.append("")
    L.append("```")
    L.append("python scripts/idx_fut_carry_ladder_years.py run --write-doc")
    L.append("python scripts/idx_fut_carry_ladder_years.py check")
    L.append("python scripts/idx_fut_carry_ladder_years.py --selftest")
    L.append("```")
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------- check
def check(face_path=OUT, probe_upstream=True):
    """rc, lines.  STALE only for upstream drift; CHECK FAILED never carries the word."""
    LR = _lr()
    if not os.path.exists(face_path):
        return RC_STALE, ["%s face missing: %s" % (V_STALE, face_path)]
    face = LR.read_json(face_path)
    lines = []
    drift = []
    if probe_upstream:
        if not os.path.exists(LATTICE):
            drift.append("ladder face missing: %s" % LATTICE)
        elif LR.digest(LATTICE) != ((face.get("inputs") or {}).get("lattice") or {}).get("sha256"):
            drift.append("ladder digest moved")
        l1 = ((face.get("inputs") or {}).get("l1_arm") or {}).get("sha256")
        if l1 and os.path.exists(L1_ARM) and LR.digest(L1_ARM) != l1:
            drift.append("L1 arm digest moved")
        for p in ("IC", "IM"):
            leg = LR.spread_leg(p)
            if "_refused" in leg:
                drift.append("leg %s refused now: %s" % (p, leg["_refused"]))
                continue
            was = (((face.get("inputs") or {}).get("legs") or {}).get(p) or {})
            if list(leg["span"]) != list(was.get("span") or []):
                drift.append("leg %s span moved %s -> %s" % (p, was.get("span"), leg["span"]))
            elif int(leg["days"]) != int(was.get("days") or -1):
                drift.append("leg %s days moved %s -> %s" % (p, was.get("days"), leg["days"]))
    if drift:
        return RC_STALE, ["%s upstream moved: %s" % (V_STALE, "; ".join(drift))]

    problems = []
    nav = float((face.get("inputs") or {}).get("nav_cny") or 0.0)
    rungs = (face.get("measured") or {}).get("rungs") or {}
    for key, r in sorted(rungs.items()):
        full = r.get("full") or {}
        growth = 1.0 + (full.get("cagr_pct") or 0.0) / 100.0
        lvl, days = 1.0, 0
        for y, row in sorted((r.get("years") or {}).items()):
            lvl *= (1.0 + float(row["return_pct"]) / 100.0)
            days += int(row["days"])
        if days != int(r.get("days") or -1):
            problems.append("%s year bars %d != rung days %s" % (key, days, r.get("days")))
        # the years' compound and the full-period CAGR must describe the same growth path
        expect = (lvl ** (cfg_year_days() / days) - 1.0) * 100.0 if days else None
        if expect is not None and full.get("cagr_pct") is not None:
            if abs(expect - float(full["cagr_pct"])) > 0.05:
                problems.append("%s years compound to %.3f but full CAGR says %.3f"
                                % (key, expect, float(full["cagr_pct"])))
        for y, row in sorted((r.get("years") or {}).items()):
            want = float(row["return_pct"]) / 100.0 * nav
            # the tolerance is the face's own publishing precision: return_pct is printed to
            # 3 decimals, so half an ulp is 0.0005 % of NAV (= 5 CNY on 1M), plus the 2 dp of
            # the money column itself.  A tighter number here would red a correct face.
            tol = nav * 5e-6 + 0.02
            if abs(want - float(row["money_cny"])) > tol:
                problems.append("%s %s money %.2f != return*nav %.2f (tol %.2f)"
                                % (key, y, float(row["money_cny"]), want, tol))
            if float(row["mdd_pct"]) > 0.0:
                problems.append("%s %s max drawdown is positive" % (key, y))
        c = r.get("concentration") or {}
        rest = [y for y in sorted(r.get("years") or {}) if y != c.get("best_year")]
        if len(rest) + 1 != len(r.get("years") or {}):
            problems.append("%s best year %s is not in its own year table"
                            % (key, c.get("best_year")))
        got = sum(int(r["years"][y]["days"]) for y in rest)
        if got != int(c.get("cagr_ex_best_days") or -1):
            problems.append("%s ex-best days %s != table %d"
                            % (key, c.get("cagr_ex_best_days"), got))
        if list(c.get("negative_years") or []) != loss_years(r):
            problems.append("%s stored loss years %s but the year table says %s"
                            % (key, c.get("negative_years"), loss_years(r)))
        attr = r.get("attribution") or {}
        if sorted(attr) != sorted(r.get("years") or {}):
            problems.append("%s attribution years %s != year table %s"
                            % (key, sorted(attr), sorted(r.get("years") or {})))
        for y, a in sorted(attr.items()):
            piece_sum = (float(a.get("sleeve_pp") or 0.0) + float(a.get("ic_pp") or 0.0)
                         + float(a.get("im_pp") or 0.0))
            if abs(piece_sum - float(a.get("sum_pp") or 0.0)) > 0.01:
                problems.append("%s %s pieces add to %.3f but sum_pp says %.3f"
                                % (key, y, piece_sum, float(a.get("sum_pp") or 0.0)))
            if int(a.get("days") or -1) != int(((r.get("years") or {}).get(y) or {}).get("days") or -2):
                problems.append("%s %s attribution days %s != year days %s"
                                % (key, y, a.get("days"),
                                   ((r.get("years") or {}).get(y) or {}).get("days")))
    j = face.get("judgment") or {}
    if rungs:
        again = judge(rungs, face.get("engine_rung"), face.get("in_band_rung"))
        for k2 in ("year_concentration", "worst_year_shape"):
            if again.get(k2) != j.get(k2):
                problems.append("judgment %s says %s, numbers say %s"
                                % (k2, j.get(k2), again.get(k2)))
    if problems:
        return RC_FAIL, ["%s: %s" % (V_FAIL, "; ".join(problems[:6]))]
    lines.append("%s %d rungs, %d years, engine %s, band %s -- every year table compounds to "
                 "its own full-period CAGR"
                 % (V_OK, len(rungs), len((face.get("measured") or {}).get("years") or []),
                    face.get("engine_rung"), face.get("in_band_rung")))
    return RC_OK, lines


# ---------------------------------------------------------------- commands
def cmd_run(args):
    face, refusal = build()
    if refusal:
        print(json.dumps(refusal, ensure_ascii=False))
        return 2
    import datetime
    face["generated"] = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
    LR = _lr()
    LR.write_json(OUT, face)
    if args.write_doc:
        with io.open(DOC, "w", encoding="utf-8", newline="\n") as f:
            f.write(render_page(face))
            f.write("\n")
    eng = face["measured"]["rungs"][face["engine_rung"]]
    print(json.dumps({"ok": True, "face": OUT, "doc": DOC if args.write_doc else None,
                      "judgment": face["judgment"],
                      "engine_cagr_pct": eng["full"]["cagr_pct"],
                      "engine_best_year": eng["concentration"]["best_year"],
                      "engine_cagr_ex_best_pct": eng["concentration"]["cagr_ex_best_pct"]},
                     ensure_ascii=False))
    return 0


def cmd_check(_args):
    rc, lines = check()
    print("\n".join(lines))
    return rc


def cmd_selftest(_args):
    cfg = stats()
    fails = []
    seen = [0]

    def ok(name, cond):
        seen[0] += 1
        if not cond:
            fails.append(name)

    # a toy two-year series with a known shape
    dates = ["2023-12-28", "2023-12-29", "2024-01-02", "2024-01-03", "2025-01-02"]
    series = [0.01, -0.005, 0.02, 0.015, 0.004]

    # L1 per-year grouping keeps date order and does not invent days
    g = group_by_year(dates, series)
    ok("L1 years", list(g) == ["2023", "2024", "2025"])
    ok("L1 bars", [len(v) for v in g.values()] == [2, 2, 1])
    ok("L1 order", g["2024"] == [0.02, 0.015])

    # L2 the years' compound is the full compound (an identity, not a coincidence)
    lvl = 1.0
    for y in sorted(g):
        lvl *= 1.0 + compound_pct(g[y]) / 100.0
    full = 1.0
    for r in series:
        full *= 1.0 + r
    ok("L2 identity", abs(lvl - full) < 1e-12)

    # L3 dropping a year drops exactly its bars
    d2, s2 = drop_year(dates, series, "2024")
    ok("L3 dropped", len(s2) == 3 and d2 == ["2023-12-28", "2023-12-29", "2025-01-02"])

    # L4 concentration names the best year and its share is inside the unit interval
    c = concentration(dates, series, cfg)
    ok("L4 best", c["best_year"] == "2024")
    ok("L4 share", 0.0 < c["best_year_share_of_growth"] < 1.0)
    ok("L4 cost", c["best_year_cost_pp"] > 0.0)

    # L5 drawdown inside a year is never positive, and a losing slice is negative
    rows = per_year(dates, series, 1000.0, cfg)
    ok("L5 mdd sign", all(rows[y]["mdd_pct"] <= 0.0 for y in rows))
    ok("L5 money", abs(rows["2025"]["money_cny"] - 4.0) < 1e-9)

    # L6 the judge flips on numbers alone, both directions, and names the tokens
    def rung(cagr, cost, worst, vol=10.0, exp=5.0):
        return {"years": {y: {"return_pct": worst if y == "Y0" else 1.0} for y in ("Y0", "Y1")},
                "full": {"ann_vol_pct": vol},
                "expected_return_pct": exp,
                "concentration": {"cagr_pct": cagr, "best_year_cost_pp": cost,
                                  "worst_year": "Y0"}}
    a = judge({"E": rung(20.0, 12.0, -6.0), "B": rung(12.0, 3.0, -2.0)}, "E", "B")
    b = judge({"E": rung(20.0, 2.0, -6.0), "B": rung(12.0, 3.0, -2.0)}, "E", "B")
    m = judge({"E": rung(20.0, 8.0, -6.0), "B": rung(12.0, 3.0, -2.0)}, "E", "B")
    ok("L6 one", a["year_concentration"] == V_ONE)
    ok("L6 spread", b["year_concentration"] == V_SPREAD)
    ok("L6 mixed", m["year_concentration"] == V_MIXED)
    ok("L6 loss years", a["year_sign"] == V_NEG and a["loss_years"] == ["Y0"])
    ok("L6 no loss", judge({"E": rung(20.0, 12.0, 3.0), "B": rung(12.0, 3.0, 1.0)},
                           "E", "B")["year_sign"] == V_NO_NEG)
    # per unit of risk, not raw pp: the small book earns less but loses less per unit of vol
    ok("L6 shape", judge({"E": rung(20.0, 12.0, 4.0, vol=10.0),
                          "B": rung(12.0, 3.0, 4.0, vol=4.0)}, "E", "B")
       ["worst_year_shape"] == V_SHAPE_CUTS)
    ok("L6 no shape", judge({"E": rung(20.0, 12.0, 4.0, vol=4.0),
                             "B": rung(12.0, 3.0, 4.0, vol=10.0)}, "E", "B")
       ["worst_year_shape"] == V_SHAPE_NOT)

    # L7 a zero CAGR cannot divide: refuse instead of inventing a share
    ok("L7 refuse", judge({"E": rung(0.0, 0.0, -1.0), "B": rung(1.0, 0.1, -1.0)},
                          "E", "B")["year_concentration"] == V_BLOCK)

    # L8 calibration counts years against the expected column, and a missing one is None
    cal = calibration({"expected_return_pct": 5.0,
                       "years": {"Y0": {"return_pct": 9.0}, "Y1": {"return_pct": 1.0}}})
    ok("L8 calibration", cal["years_above_expected"] == 1 and cal["below"] == ["Y1"])
    ok("L8 no expectation", calibration({"years": {"Y0": {"return_pct": 1.0}}}) is None)

    # L9 the pieces add to the total, day by day and year by year (an identity)
    comps = {"sleeve": [0.001, 0.0, -0.002], "ic": [0.0, 0.003, 0.0], "im": [0.0, 0.0, 0.004]}
    att = attribution(["2024-01-02", "2024-01-03", "2025-01-02"], comps)
    ok("L9 pieces", abs(att["2024"]["sum_pp"] - 0.4) < 1e-9)
    ok("L9 years", sorted(att) == ["2024", "2025"])
    ok("L9 days", att["2024"]["days"] == 2 and att["2025"]["days"] == 1)
    ok("L9 identity", abs(sum(v["sum_pp"] for v in att.values())
                          - sum(sum(comps[k2]) for k2 in comps) * 100.0) < 1e-9)

    # L9 the check's word discipline: a missing face is STALE, never a silent pass
    rc, lines = check(os.path.join(ROOT, "results", "_r2107bmc_no_such_face.json"),
                      probe_upstream=False)
    ok("L9 missing", rc == RC_STALE and "missing" in lines[0])

    if fails:
        print("SELFTEST FAILED: " + ", ".join(fails))
        return 1
    print("SELFTEST OK %d/%d" % (seen[0], seen[0]))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check", "selftest"))
    ap.add_argument("--write-doc", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        args.cmd = "selftest"
    return {"run": cmd_run, "check": cmd_check, "selftest": cmd_selftest}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
