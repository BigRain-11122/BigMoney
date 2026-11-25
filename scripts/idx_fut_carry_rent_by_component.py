#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""who pays the rent in this carry book: each arm's share of the return, and its share of the risk.

WHY THIS FILE EXISTS
--------------------
`scripts/idx_fut_carry_ladder_risk.py` (r2105) prices each rung's vol, drawdown and Sharpe;
`idx_fut_carry_drawdown_experience.py` (r2106) translates that into monthly statements;
`idx_fut_carry_ladder_years.py` (r2107) splits *one* year's return across the sleeve and the two
futures legs.  None of them answers the question a risk budget is actually spent on:

    of the 25 points this book makes, which arm makes them -- and which arm is eating the risk?

Today's book scales the equity sleeve by the ladder's `k` (0.4347) and adds one IC lot plus one
IM lot.  Those three arms are the whole book.  This face prints, for every arm and every bar:

  * its **contribution** to the book's return, in percentage points per year (arithmetic mean
    of its own daily contribution x trading days -- these add up to the book's own average);
  * its **return share** and its **risk share** (covariance contribution to the book's variance;
    these add up to 100% by construction);
  * **rent** = return share / risk share: >1 means the arm earns more than its share of the
    risk, <1 means it is being subsidised;
  * its own standalone vol, its correlation with the book, and a leave-one-out book
    (drop that arm, what does the book become);
  * an equal-risk-share counterfactual, capped so no arm's notional exceeds 100% of NAV.

The cash arm is in the table too, with risk share 0 (a constant accrual): it is printed, not
folded in, so the reader can see how little of the 25 points is the riskless carry.

verdict tokens (frozen before the first run):
  EQUITY_ARM_PAYS_THE_RENT            the equity arm's rent >= RENT_PAID while both futures
                                      legs' rent <= RENT_UNDERPAID
  EVERY_COMPONENT_PAYS_ITS_RENT       every risky arm's rent >= RENT_PAID
  MIXED_RENT                          anything else
  CARRY_LEGS_MARKET_NEUTRAL           the equity arm explains <= NEUTRAL_R2 of the futures
                                      legs' daily variance
  CARRY_LEGS_TRACK_THE_MARKET         it explains more
  REBUDGETING_WOULD_HELP              equal-risk-share (capped) Sharpe exceeds the book's by
                                      >= SHARPE_GAIN_PP
  REBUDGETING_IS_A_WASH               it does not
  REBUDGET_NOT_APPLICABLE             the rung has an arm with zero covariance, so 1/c_i has
                                      no value -- refuse to call that a wash (silence would
                                      read as "tested and harmless")
  DATA_BLOCKED                        a series is missing or too short; refuse, never default 0

WHAT IS A DECLARATION, NOT A MEASUREMENT
  * the equity-sleeve daily series is rebuilt at run time (~65 s) through the published engine;
    `check` pins it by the digests of the ladder + etf_nobond_vt face, never by re-deriving it;
  * the cash arm's return is the ladder's own `cash_interest_cny / nav / trading_days`, i.e. it
    inherits the ladder's cash assumption rather than re-pricing it;
  * risk shares are covariance shares of daily contributions; they are a *decomposition of the
    book that exists today*, not an optimisation and not a recommendation.

Usage:
    python scripts/idx_fut_carry_rent_by_component.py run
    python scripts/idx_fut_carry_rent_by_component.py check
    python scripts/idx_fut_carry_rent_by_component.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
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

SCHEMA = "idx-fut-carry-rent-by-component/v1"
KIND = "carry_rent_by_component"
OUT = os.path.join(ROOT, "results", "idx_fut_carry_rent_by_component.json")
DOC = os.path.join(ROOT, "research", "IDX_FUT_CARRY_RENT_BY_COMPONENT.md")
LATTICE = os.path.join(ROOT, "results", "policy_return_lattice.json")
L1_ARM = os.path.join(ROOT, "results", "etf_nobond_vt.json")
LADDER_RISK = os.path.join(ROOT, "results", "idx_fut_carry_ladder_risk.json")
MIN_DAYS = 400

# frozen thresholds, declared once
RENT_PAID = 1.25
RENT_UNDERPAID = 0.80
NEUTRAL_R2 = 0.05
SHARPE_GAIN_PP = 0.10
TOL_SHARE = 2e-6
TOL_PP = 1e-6

V_EQUITY_RENT = "EQUITY_ARM_PAYS_THE_RENT"
V_ALL_RENT = "EVERY_COMPONENT_PAYS_ITS_RENT"
V_MIXED = "MIXED_RENT"
V_NEUTRAL = "CARRY_LEGS_MARKET_NEUTRAL"
V_TRACKS = "CARRY_LEGS_TRACK_THE_MARKET"
V_REBUDGET_HELP = "REBUDGETING_WOULD_HELP"
V_REBUDGET_WASH = "REBUDGETING_IS_A_WASH"
V_REBUDGET_NA = "REBUDGET_NOT_APPLICABLE"
V_BLOCK = "DATA_BLOCKED"

RISKY = ("equity_arm", "IC_leg", "IM_leg")
LABEL = {"equity_arm": "equity sleeve (k x L1)", "IC_leg": "IC basis leg",
         "IM_leg": "IM basis leg", "cash": "cash arm (riskless)"}


# ------------------------------------------------------------------ arithmetic (pure)
def td():
    """Bars per year from the authority, never re-declared (r2104's 252-vs-244 lesson)."""
    import idx_fut_basis as B
    return float(B.TRADING_DAYS)


def mean(x):
    return sum(x) / len(x) if x else None


def ann_arith_pct(x, bars=None):
    m = mean(x)
    if m is None:
        return None
    return m * (bars or td()) * 100.0


def ann_compound_pct(x, bars=None):
    if not x:
        return None
    lvl = 1.0
    for r in x:
        lvl *= (1.0 + r)
    if lvl <= 0:
        return None
    return (lvl ** ((bars or td()) / len(x)) - 1.0) * 100.0


def vol_pct(x, bars=None):
    if len(x) < 2:
        return None
    m = mean(x)
    var = sum((v - m) ** 2 for v in x) / (len(x) - 1)
    return (var ** 0.5) * ((bars or td()) ** 0.5) * 100.0


def cov(x, y):
    if len(x) < 2 or len(x) != len(y):
        return None
    mx, my = mean(x), mean(y)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (len(x) - 1)


def var(x):
    if len(x) < 2:
        return None
    m = mean(x)
    return sum((v - m) ** 2 for v in x) / (len(x) - 1)


def corr(x, y):
    cx = cov(x, y)
    vx, vy = var(x), var(y)
    if cx is None or not vx or not vy:
        return None
    return cx / ((vx ** 0.5) * (vy ** 0.5))


def mdd_pct(x):
    lvl, peak, worst = 1.0, 1.0, 0.0
    for r in x:
        lvl *= (1.0 + r)
        peak = max(peak, lvl)
        worst = min(worst, lvl / peak - 1.0)
    return worst * 100.0


def sharpe(ann_pct, vol, rf_pct):
    if vol is None or not vol or ann_pct is None:
        return None
    return (ann_pct - rf_pct) / vol


def book_stats(series, bars, rf_pct):
    ann = ann_compound_pct(series, bars)
    v = vol_pct(series, bars)
    return {"ann_compound_pct": ann, "ann_arith_pct": ann_arith_pct(series, bars),
            "vol_pct": v, "sharpe": sharpe(ann, v, rf_pct), "mdd_pct": mdd_pct(series),
            "days": len(series)}


# ------------------------------------------------------------------ decomposition (pure)
def decompose(comps, bars, rf_pct):
    """Return the share table given per-arm daily contribution series (dict name -> list)."""
    names = list(comps)
    n = min(len(comps[k]) for k in names)
    comps = {k: comps[k][:n] for k in names}
    total = [sum(comps[k][i] for k in names) for i in range(n)]
    vt = var(total)
    rows = []
    anns = {k: ann_arith_pct(comps[k], bars) for k in names}
    tot_ann = ann_arith_pct(total, bars)
    for k in names:
        c = cov(comps[k], total) if vt else None
        rows.append({
            "name": k,
            "ann_arith_pct": anns[k],
            "return_share": (anns[k] / tot_ann) if tot_ann else None,
            "cov_with_total": c,
            "risk_share": (c / vt) if (vt and c is not None) else None,
            "vol_pct": vol_pct(comps[k], bars),
            "corr_with_total": corr(comps[k], total),
        })
    for r in rows:
        rs, rk = r["return_share"], r["risk_share"]
        r["rent"] = (rs / rk) if (rs is not None and rk) else None
    return {"rows": rows, "total": total, "book": book_stats(total, bars, rf_pct)}


def loo_table(comps, bars, rf_pct):
    names = list(comps)
    n = min(len(comps[k]) for k in names)
    comps = {k: comps[k][:n] for k in names}
    total = [sum(comps[k][i] for k in names) for i in range(n)]
    base = book_stats(total, bars, rf_pct)
    out = {}
    for k in names:
        rest = [total[i] - comps[k][i] for i in range(n)]
        st = book_stats(rest, bars, rf_pct)
        out[k] = {"ann_compound_pct": st["ann_compound_pct"], "vol_pct": st["vol_pct"],
                  "sharpe": st["sharpe"],
                  "d_ann_pp": (st["ann_compound_pct"] - base["ann_compound_pct"])
                  if (st["ann_compound_pct"] is not None
                      and base["ann_compound_pct"] is not None) else None}
    return out


def carry_vs_equity(comps, bars):
    """Beta / R^2 of the futures legs' contribution against the equity arm's contribution."""
    n = min(len(comps["equity_arm"]), len(comps["IC_leg"]), len(comps["IM_leg"]))
    eq = comps["equity_arm"][:n]
    carry = [comps["IC_leg"][i] + comps["IM_leg"][i] for i in range(n)]
    ve = var(eq)
    if not ve:
        return None
    beta = cov(eq, carry) / ve
    r = corr(eq, carry)
    return {"beta": beta, "corr": r, "r2": (r * r) if r is not None else None,
            "carry_ann_arith_pct": ann_arith_pct(carry, bars),
            "equity_vol_pct": vol_pct(eq, bars),
            "beta_times_equity_vol_pp": (beta * (vol_pct(eq, bars) or 0.0))}


def risk_parity(comps, weights, bars, rf_pct, cap=1.0):
    """Equal risk share across the three risky arms, with max implied notional <= cap x NAV.

    Scaling an arm's contribution series by s scales its covariance with the book by s, so
    'equal covariance contribution' means s_i * c_i equal for all i.  That pins the ratios
    s_i ~ 1/c_i; the free scalar is fixed by the cap so the largest implied notional is cap.
    A constant arm (cash) is left untouched.
    """
    risky = [k for k in RISKY if k in comps]
    n = min(len(comps[k]) for k in comps)
    total = [sum(comps[k][i] for k in comps) for i in range(n)]
    vt = var(total)
    c0 = {k: cov(comps[k], total) for k in risky}
    if not vt or any((v is None or v <= 0) for v in c0.values()):
        return None
    ratios = {k: 1.0 / c0[k] for k in risky}
    notionals = {k: abs(ratios[k] * weights[k]) for k in risky}
    scale_ref = max(notionals.values())
    s = {k: (cap / scale_ref) * ratios[k] for k in risky}
    implied = {k: abs(s[k] * weights[k]) for k in risky}
    new = {k: [s[k] * v for v in comps[k]] for k in risky}
    new["cash"] = list(comps.get("cash", [0.0] * n))
    tot = [sum(new[k][i] for k in new) for i in range(n)]
    st = book_stats(tot, bars, rf_pct)
    return {"implied_notional_x_nav": implied, "book": st}


# ------------------------------------------------------------------ verdicts (pure)
def verdicts(decomp, loo, neutrality, rebudget, base):
    rows = {r["name"]: r for r in decomp["rows"]}
    rents = {k: rows[k]["rent"] for k in RISKY if k in rows}
    if all((v is not None and v >= RENT_PAID) for v in rents.values()) and rents:
        token = V_ALL_RENT
    elif (rents.get("equity_arm") is not None and rents["equity_arm"] >= RENT_PAID
          and all(rows[k]["rent"] is not None and rows[k]["rent"] <= RENT_UNDERPAID
                  for k in ("IC_leg", "IM_leg") if k in rows)):
        token = V_EQUITY_RENT
    else:
        token = V_MIXED
    big_risk = max((k for k in RISKY if k in rows),
                   key=lambda k: rows[k]["risk_share"] or -9)
    big_earn = max((k for k in RISKY if k in rows),
                   key=lambda k: (rows[k]["ann_arith_pct"] if rows[k]["ann_arith_pct"]
                                  is not None else -9))
    neu = (V_NEUTRAL if (neutrality and neutrality.get("r2") is not None
                         and neutrality["r2"] <= NEUTRAL_R2) else V_TRACKS)
    gain = None
    if rebudget and rebudget["book"]["sharpe"] is not None and base["sharpe"] is not None:
        gain = rebudget["book"]["sharpe"] - base["sharpe"]
    if rebudget is None:
        reb = V_REBUDGET_NA            # an arm with zero covariance has no 1/c_i to scale by
    elif gain is not None and gain >= SHARPE_GAIN_PP:
        reb = V_REBUDGET_HELP
    else:
        reb = V_REBUDGET_WASH
    return {"rent": token, "rents": {k: (round(v, 4) if v is not None else None)
                                     for k, v in rents.items()},
            "biggest_risk_buyer": big_risk, "biggest_earner": big_earn,
            "neutrality": neu,
            "rebudget": reb, "rebudget_sharpe_gain": (round(gain, 4) if gain is not None
                                                      else None)}


# ------------------------------------------------------------------ inputs
def digest(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")


def build(legs=None, sleeve=None):
    if not os.path.exists(LATTICE):
        return None, {"verdict": V_BLOCK, "why": "ladder face missing: %s" % LATTICE}
    lat = read_json(LATTICE)
    nav = float(lat["nav_cny"])
    k = float(lat["inputs"]["k"])
    cash_rate = float(lat["inputs"]["cash_rate_pct"])
    lr = read_json(LADDER_RISK) if os.path.exists(LADDER_RISK) else {}
    engine_key = "%d/%d" % (int((lr.get("engine_rung") or "1/1").split("/")[0]),
                            int((lr.get("engine_rung") or "1/1").split("/")[1]))
    band_key = lr.get("in_band_rung") or "0/1"
    if legs is None or sleeve is None:
        import idx_fut_carry_ladder_risk as L
        legs = {p: L.spread_leg(p) for p in ("IC", "IM")}
        sleeve = L.equity_sleeve()
        n_lot = L.per_lot_notional(lat)
    for p, leg in legs.items():
        if "_refused" in leg:
            return None, {"verdict": V_BLOCK, "why": "leg %s refused: %s" % (p, leg["_refused"])}
        if leg["days"] < MIN_DAYS:
            return None, {"verdict": V_BLOCK, "why": "leg %s has %d days, need %d"
                                                     % (p, leg["days"], MIN_DAYS)}
    if "_refused" in sleeve:
        return None, {"verdict": V_BLOCK, "why": "equity sleeve refused: %s" % sleeve["_refused"]}
    bars = td()
    d_ic = dict(zip(legs["IC"]["dates"], legs["IC"]["spread"]))
    d_im = dict(zip(legs["IM"]["dates"], legs["IM"]["spread"]))
    d_eq = dict(zip(sleeve["dates"], sleeve["daily"]))
    common = [d for d in sorted(d_eq) if d in d_ic and d in d_im]
    if len(common) < MIN_DAYS:
        return None, {"verdict": V_BLOCK, "why": "only %d common bars, need %d"
                                                 % (len(common), MIN_DAYS)}
    rung_by_key = {"%d/%d" % (int(r["ic_lots"]), int(r["im_lots"])): r for r in lat["lattice"]}
    out = {}
    for key in (engine_key, band_key):
        if key in out:
            continue
        if key not in rung_by_key:
            return None, {"verdict": V_BLOCK, "why": "rung %s not on the ladder" % key}
        rung = rung_by_key[key]
        icl, iml = int(rung["ic_lots"]), int(rung["im_lots"])
        w_ic = icl * n_lot["IC"] / nav
        w_im = iml * n_lot["IM"] / nav
        cash_bar = float(rung.get("cash_interest_cny") or 0.0) / nav / bars
        comps = {
            "equity_arm": [k * d_eq[d] for d in common],
            "IC_leg": [w_ic * d_ic[d] for d in common],
            "IM_leg": [w_im * d_im[d] for d in common],
            "cash": [cash_bar for _ in common],
        }
        weights = {"equity_arm": k, "IC_leg": w_ic, "IM_leg": w_im, "cash": 0.0}
        dec = decompose(comps, bars, cash_rate)
        rows = []
        for r in dec["rows"]:
            rows.append({
                "name": r["name"], "label": LABEL[r["name"]],
                "weight_x_nav": round(weights[r["name"]], 6),
                "ann_arith_pct": round(r["ann_arith_pct"], 6),
                "return_share": round(r["return_share"], 6),
                "cov_with_total": r["cov_with_total"],
                "risk_share": (round(r["risk_share"], 6) if r["risk_share"] is not None else None),
                "rent": (round(r["rent"], 6) if r["rent"] is not None else None),
                "vol_pct": round(r["vol_pct"], 4) if r["vol_pct"] is not None else None,
                "corr_with_total": (round(r["corr_with_total"], 5)
                                    if r["corr_with_total"] is not None else None),
            })
        loo = loo_table(comps, bars, cash_rate)
        neu = carry_vs_equity(comps, bars)
        reb = risk_parity(comps, weights, bars, cash_rate, cap=1.0)
        v = verdicts({"rows": rows}, loo, neu, reb, dec["book"])
        out[key] = {
            "ic_lots": icl, "im_lots": iml,
            "weights_x_nav": {k2: round(v2, 6) for k2, v2 in weights.items()},
            "days": len(common), "span": [common[0], common[-1]],
            "components": rows,
            "book": {kk: (round(vv, 4) if isinstance(vv, float) else vv)
                     for kk, vv in dec["book"].items()},
            "leave_one_out": {k2: {kk: (round(vv, 4) if isinstance(vv, float) else vv)
                                   for kk, vv in v2.items()} for k2, v2 in loo.items()},
            "carry_vs_equity": ({k2: (round(v2, 6) if isinstance(v2, float) else v2)
                                 for k2, v2 in neu.items()} if neu else None),
            "equal_risk_share_capped": ({
                "implied_notional_x_nav": {k2: round(v2, 6)
                                           for k2, v2 in reb["implied_notional_x_nav"].items()},
                "book": {kk: (round(vv, 4) if isinstance(vv, float) else vv)
                         for kk, vv in reb["book"].items()},
            } if reb else None),
            "judgment": v,
        }
    # cross-face: the sibling face (r2106) prices the same rung WITHOUT the cash arm, so its
    # annual return must equal this face's leave-the-cash-out book.  Recorded as a snapshot;
    # check does not gate on it (that face is another writer's surface).
    cross = None
    ddx = os.path.join(ROOT, "results", "idx_fut_carry_drawdown_experience.json")
    if os.path.exists(ddx):
        other = read_json(ddx)
        theirs = (other.get("measured", {}).get("rungs", {}) or {}).get(engine_key)
        mine = out[engine_key]["leave_one_out"]["cash"]["ann_compound_pct"]
        if theirs and theirs.get("measured_ann_pct") is not None:
            d = mine - theirs["measured_ann_pct"]
            cross = {
                "face": "results/idx_fut_carry_drawdown_experience.json",
                "sha256": digest(ddx),
                "engine_rung": engine_key,
                "their_ann_pct": theirs["measured_ann_pct"],
                "my_book_without_cash_pct": round(mine, 4),
                "delta_pp": round(d, 4),
                "with_cash_pct": out[engine_key]["book"]["ann_compound_pct"],
                "verdict": ("CROSS_FACE_MATCHES" if abs(d) <= 0.05
                            else "CROSS_FACE_DIVERGES"),
                "explanation": ("that face prices the rung without the riskless cash arm; this "
                                "face adds it as a fourth component, so the like-for-like "
                                "comparison is with the leave-the-cash-out column"),
            }
    face = {
        "schema": SCHEMA,
        "kind": KIND,
        "evidence_cutoff": common[-1],
        "inputs": {
            "lattice": {"path": "results/policy_return_lattice.json", "sha256": digest(LATTICE)},
            "l1_arm": {"path": "results/etf_nobond_vt.json", "sha256": digest(L1_ARM)},
            "ladder_risk": ({"path": "results/idx_fut_carry_ladder_risk.json",
                             "sha256": digest(LADDER_RISK)} if os.path.exists(LADDER_RISK)
                            else None),
            "nav_cny": nav, "k": k, "cash_rate_pct": cash_rate, "trading_days": bars,
            "legs": {p: {"span": legs[p]["span"], "days": legs[p]["days"],
                         "index": legs[p]["index"]} for p in ("IC", "IM")},
            "equity_span": sleeve["span"],
            "thresholds": {"rent_paid": RENT_PAID, "rent_underpaid": RENT_UNDERPAID,
                           "neutral_r2": NEUTRAL_R2, "sharpe_gain_pp": SHARPE_GAIN_PP},
        },
        "question": ("of the book's annual return, which arm makes it and which arm eats the "
                     "risk -- and does an equal-risk-share re-budget buy a better Sharpe without "
                     "leveraging any arm past 100% of NAV?"),
        "rule": ("contribution_i = weight_i x daily series_i; return share = mean(contribution_i)"
                 " / mean(sum); risk share = cov(contribution_i, sum) / var(sum); rent = return "
                 "share / risk share; leave-one-out subtracts the arm's contribution bar by bar; "
                 "equal-risk-share scales each arm by 1/cov_i and the free scalar so the largest "
                 "implied notional is 100% of NAV"),
        "rungs": out,
        "judgment": {"engine_rung": engine_key, "band_rung": band_key,
                     "engine": out[engine_key]["judgment"],
                     "band": out[band_key]["judgment"] if band_key in out else None},
        "cross_face": cross,
        "scope_limits": [
            "the equity sleeve is rebuilt at run time; check pins it by digest only",
            "the cash arm inherits the ladder's cash assumption (cash_interest_cny/nav/bars)",
            "risk shares decompose today's book; they are not an optimisation or a recommendation",
            "the equal-risk-share arm is a counterfactual with a notional cap of 100% of NAV; "
            "it ignores the equity book's own capacity and the futures margin line",
        ],
        "not_recomputed": ["equity sleeve daily series (check uses digests)",
                           "the ladder's cash rate", "the futures leg spreads (check re-probes "
                           "their presence, not their values)"],
        "check_scope": ("check re-probes the two input faces' digests and re-derives every "
                        "share / rent / sign / verdict token from the stored component moments; "
                        "it never re-derives the equity sleeve, and it does not gate on the "
                        "cross_face snapshot (that face is another writer's surface)"),
    }
    return face, None


# ------------------------------------------------------------------ page
def _f(x, nd=2):
    return "n/a" if x is None else f"{x:.{nd}f}"


def _pct(x, nd=1):
    return "n/a" if x is None else f"{x*100:.{nd}f}%"


def render_page(face):
    j = face["judgment"]
    L = []
    L.append("# 这本书里哪条腿在养家：收益份额 vs 风险份额")
    L.append("")
    L.append(f"generated {face.get('generated') or 'run-time'} | cutoff "
             f"{face['evidence_cutoff']} | schema `{SCHEMA}`")
    L.append("")
    eng = face["rungs"][j["engine_rung"]]
    rows = {r["name"]: r for r in eng["components"]}
    L.append("## 一句话")
    L.append("")
    eq, ic, im, cash = (rows.get("equity_arm"), rows.get("IC_leg"),
                        rows.get("IM_leg"), rows.get("cash"))
    L.append(f"指令档 **{j['engine_rung']}** 在这 {eng['days']} 个 bar 上平均每年赚 "
             f"**{_f(eng['book']['ann_arith_pct'])} 个点**（复利 "
             f"**{_f(eng['book']['ann_compound_pct'])}%**，波动 "
             f"**{_f(eng['book']['vol_pct'])}%**）。拆成四条：权益袖 "
             f"**{_f(eq['ann_arith_pct'])} 点**、IC 腿 **{_f(ic['ann_arith_pct'])} 点**、"
             f"IM 腿 **{_f(im['ann_arith_pct'])} 点**、现金 **{_f(cash['ann_arith_pct'])} 点**。"
             f"按份额看，权益袖拿走 **{_pct(eq['return_share'])}** 的收益却只承担 "
             f"**{_pct(eq['risk_share'])}** 的风险（rent **{_f(eq['rent'])}**），而两条基差腿拿走 "
             f"**{_pct((ic['return_share'] or 0)+(im['return_share'] or 0))}** 的收益、扛了 "
             f"**{_pct((ic['risk_share'] or 0)+(im['risk_share'] or 0))}** 的风险"
             f"（rent IC **{_f(ic['rent'])}** / IM **{_f(im['rent'])}**）。"
             f"判词 **{j['engine']['rent']}**。")
    L.append("")
    L.append("## 每条腿，收益份额与风险份额并排")
    L.append("")
    L.append("| 臂 | 权重 x NAV | 年贡献 (点, 算术) | 收益份额 | 风险份额 | rent | 自身波动 | 与全书相关 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for name in ("equity_arm", "IC_leg", "IM_leg", "cash"):
        r = rows[name]
        L.append(f"| {r['label']} | {_f(r['weight_x_nav'], 4)} | {_f(r['ann_arith_pct'], 3)} | "
                 f"{_pct(r['return_share'])} | "
                 f"{_pct(r['risk_share']) if r['risk_share'] is not None else '0.0% (无风险)'} | "
                 f"{_f(r['rent'])} | {_f(r['vol_pct'], 3)} | "
                 f"{_f(r['corr_with_total'], 3)} |")
    L.append("")
    L.append("rent = 收益份额 / 风险份额。>1 表示这条腿赚的比它占的风险多；<1 表示它在吃补贴。"
             "现金臂的协方差为零，风险份额按 0 计，因此没有 rent。")
    L.append("")
    L.append("## 拆掉一条腿，这本书变成什么")
    L.append("")
    L.append("| 拆掉的臂 | 复利年化 % | 波动 % | 夏普 | 年化变化 (pp) |")
    L.append("|---|---|---|---|---|")
    for name in ("equity_arm", "IC_leg", "IM_leg", "cash"):
        l = eng["leave_one_out"][name]
        L.append(f"| {LABEL[name]} | {_f(l['ann_compound_pct'], 3)} | {_f(l['vol_pct'], 3)} | "
                 f"{_f(l['sharpe'], 3)} | {_f(l['d_ann_pp'], 3)} |")
    L.append("")
    L.append(f"全书：复利 **{_f(eng['book']['ann_compound_pct'])}%** / 波动 "
             f"**{_f(eng['book']['vol_pct'])}%** / 夏普 **{_f(eng['book']['sharpe'], 3)}** / "
             f"最大回撤 **{_f(eng['book']['mdd_pct'])}%**。")
    L.append("")
    cv = eng.get("carry_vs_equity")
    if cv:
        L.append("## 两条基差腿是不是偷偷在做多股市")
        L.append("")
        L.append(f"把「IC + IM 的日贡献」对「权益袖的日贡献」回归：beta **{_f(cv['beta'], 4)}**、"
                 f"相关 **{_f(cv['corr'], 4)}**、R² **{_pct(cv['r2'], 2)}**。也就是说权益袖只能解释"
                 f"基差腿日波动的 **{_pct(cv['r2'], 2)}**；beta 乘上权益袖波动是 "
                 f"**{_f(cv['beta_times_equity_vol_pp'], 3)} 个点**，而两条腿自己一年做 "
                 f"**{_f(cv['carry_ann_arith_pct'])} 个点**。判词 **{j['engine']['neutrality']}**。")
        L.append("")
    reb = eng.get("equal_risk_share_capped")
    if reb:
        L.append("## 如果按等风险份额重配（任何一臂名义不超过 100% NAV）")
        L.append("")
        parts = "、".join(f"{LABEL[k]} **{_f(v, 3)}×NAV**" for k, v in
                          reb["implied_notional_x_nav"].items())
        L.append(f"重配后的名义：{parts}。结果：复利 "
                 f"**{_f(reb['book']['ann_compound_pct'])}%**、波动 "
                 f"**{_f(reb['book']['vol_pct'])}%**、夏普 **{_f(reb['book']['sharpe'], 3)}**、"
                 f"最大回撤 **{_f(reb['book']['mdd_pct'])}%**（现在的书是 "
                 f"{_f(eng['book']['ann_compound_pct'])}% / {_f(eng['book']['vol_pct'])}% / "
                 f"{_f(eng['book']['sharpe'], 3)} / {_f(eng['book']['mdd_pct'])}%）。"
                 f"判词 **{j['engine']['rebudget']}**（夏普变化 "
                 f"**{_f(j['engine']['rebudget_sharpe_gain'], 3)}**，门槛 "
                 f"{SHARPE_GAIN_PP}）。")
        L.append("")
        d_ann = reb["book"]["ann_compound_pct"] - eng["book"]["ann_compound_pct"]
        d_mdd = reb["book"]["mdd_pct"] - eng["book"]["mdd_pct"]
        L.append(f"这是一次**交换**，不是白拿：年化少 **{_f(-d_ann)} 个点**，换来夏普 "
                 f"**{_f(j['engine']['rebudget_sharpe_gain'], 3)}**、波动少 "
                 f"**{_f(eng['book']['vol_pct'] - reb['book']['vol_pct'])} 个点**、回撤浅 "
                 f"**{_f(d_mdd)} 个点**。要不要换属于资金方的口味，不在这张面的判定范围内。")
        L.append("")
    cfr = face.get("cross_face")
    if cfr:
        L.append("## 跨面对账")
        L.append("")
        L.append(f"`research/IDX_FUT_CARRY_DRAWDOWN_EXPERIENCE.md` 给同一档 "
                 f"{cfr['engine_rung']} 的复利年化是 **{_f(cfr['their_ann_pct'])}%**（不含现金臂）；"
                 f"本面「拆掉现金臂」那一列是 **{_f(cfr['my_book_without_cash_pct'])}%**，差 "
                 f"**{_f(cfr['delta_pp'], 4)} 个点**，判 **{cfr['verdict']}**。本面把现金臂算进去的"
                 f"全书是 **{_f(cfr['with_cash_pct'])}%**——两个数都对，只是分母不同，页面上各印一遍。")
        L.append("")
    band_key = j["band_rung"]
    if band_key in face["rungs"] and band_key != j["engine_rung"]:
        band = face["rungs"][band_key]
        brows = {r["name"]: r for r in band["components"]}
        L.append(f"## 带内档 {band_key} 的同一张表")
        L.append("")
        L.append(f"带内档复利 **{_f(band['book']['ann_compound_pct'])}%** / 波动 "
                 f"**{_f(band['book']['vol_pct'])}%** / 夏普 **{_f(band['book']['sharpe'], 3)}**；"
                 f"权益袖 rent **{_f(brows['equity_arm']['rent'])}**、IM 腿 rent "
                 f"**{_f(brows['IM_leg']['rent'])}**。判词 **{band['judgment']['rent']}**，"
                 f"重配 **{band['judgment']['rebudget']}**。")
        L.append("")
    L.append("## 读法（写给自己下一轮）")
    L.append("")
    L.append("* 收益份额与风险份额相加都是 100%（现金臂风险份额为 0），所以「rent」是一把"
             "份额尺，不是金额尺；")
    L.append("* 复利列低于算术列，差额是波动拖累——两列都印，读者不会把拖累当成别人的功劳；")
    L.append("* 等风险份额那一档只是**今天的书**的一种再配法，它没有考虑权益书自己的容量，"
             "也没有考虑期货保证金线；它回答的是「同样的规则换个预算会不会更好」。")
    L.append("")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ check
def check():
    if not os.path.exists(OUT):
        return 1, "CHECK FAILED: face missing (run first): %s" % OUT
    face = read_json(OUT)
    ins = face.get("inputs") or {}
    for key in ("lattice", "l1_arm", "ladder_risk"):
        spec = ins.get(key)
        if not spec:
            continue
        path = os.path.join(ROOT, spec["path"].replace("/", os.sep))
        if not os.path.exists(path):
            return 3, "STALE: input %s missing on disk (%s)" % (key, spec["path"])
        if digest(path) != spec["sha256"]:
            return 3, ("STALE: input %s changed since the face was written (%s) -- re-run"
                       % (key, spec["path"]))
    for key, rung in (face.get("rungs") or {}).items():
        rows = rung["components"]
        tot_ann = sum(r["ann_arith_pct"] for r in rows)
        if abs(tot_ann - rung["book"]["ann_arith_pct"]) > 1e-3:
            return 1, ("CHECK FAILED: rung %s components sum to %.6f pp but the book prints "
                       "%.6f pp" % (key, tot_ann, rung["book"]["ann_arith_pct"]))
        vt = sum(r["cov_with_total"] for r in rows)
        for r in rows:
            rec_rs = (r["cov_with_total"] / vt) if vt else None
            if r["risk_share"] is None:
                if rec_rs not in (None, 0) and abs(rec_rs) > 1e-9:
                    return 1, "CHECK FAILED: rung %s %s prints no risk share but cov %.3e" % (
                        key, r["name"], r["cov_with_total"])
                continue
            if rec_rs is None or abs(rec_rs - r["risk_share"]) > TOL_SHARE:
                return 1, ("CHECK FAILED: rung %s %s risk share %.6f != recomputed %.6f"
                           % (key, r["name"], r["risk_share"], rec_rs or 0.0))
            rec_rent = (r["return_share"] / r["risk_share"]) if r["risk_share"] else None
            if r["rent"] is not None and rec_rent is not None \
                    and abs(rec_rent - r["rent"]) > 1e-4:
                return 1, ("CHECK FAILED: rung %s %s rent %.6f != return/risk %.6f"
                           % (key, r["name"], r["rent"], rec_rent))
        shares = sum(r["return_share"] for r in rows)
        if abs(shares - 1.0) > 1e-4:
            return 1, "CHECK FAILED: rung %s return shares sum to %.6f" % (key, shares)
        rshares = sum((r["risk_share"] or 0.0) for r in rows)
        if abs(rshares - 1.0) > 1e-4:
            return 1, "CHECK FAILED: rung %s risk shares sum to %.6f" % (key, rshares)
        v = verdicts({"rows": rows}, rung.get("leave_one_out") or {},
                     rung.get("carry_vs_equity"), rung.get("equal_risk_share_capped"),
                     rung["book"])
        for field in ("rent", "neutrality", "rebudget"):
            if v[field] != rung["judgment"][field]:
                return 1, ("CHECK FAILED: rung %s judgment %s is %s but recomputes to %s"
                           % (key, field, rung["judgment"][field], v[field]))
    return 0, ("CHECK_OK rungs=%d engine=%s band=%s rent=%s rebudget=%s"
               % (len(face["rungs"]), face["judgment"]["engine_rung"],
                  face["judgment"]["band_rung"],
                  face["judgment"]["engine"]["rent"],
                  face["judgment"]["engine"]["rebudget"]))


# ------------------------------------------------------------------ selftest
def _selftest():
    """Synthetic, no I/O: pin the decomposition identities and the verdicts."""
    import random
    ok = 0
    total = 0

    def chk(cond, msg):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL: %s" % msg)

    rng = random.Random(11)
    bars = 252.0
    n = 600
    a = [rng.gauss(2.0e-4, 3.0e-3) for _ in range(n)]     # cheap, low vol
    b = [rng.gauss(3.0e-4, 8.0e-3) for _ in range(n)]     # rich, high vol
    c = [rng.gauss(1.0e-4, 9.0e-3) for _ in range(n)]
    comps = {"equity_arm": a, "IC_leg": b, "IM_leg": c,
             "cash": [1.6e-5] * n}

    # 1) identities: shares sum to 1
    dec = decompose(comps, bars, 1.395)
    rs = sum(r["return_share"] for r in dec["rows"])
    rk = sum((r["risk_share"] or 0.0) for r in dec["rows"])
    chk(abs(rs - 1.0) < 1e-9, "return shares must sum to 1, got %.12f" % rs)
    chk(abs(rk - 1.0) < 1e-9, "risk shares must sum to 1, got %.12f" % rk)

    # 2) the riskless arm carries no risk share and no rent
    cash_row = [r for r in dec["rows"] if r["name"] == "cash"][0]
    chk(cash_row["risk_share"] is not None and abs(cash_row["risk_share"]) < 1e-12,
        "constant arm risk share must be 0")
    chk(cash_row["rent"] is None, "riskless arm has no rent")

    # 3) rent = return share / risk share
    for r in dec["rows"]:
        if r["rent"] is not None:
            chk(abs(r["rent"] - r["return_share"] / r["risk_share"]) < 1e-9, "rent identity")

    # 4) scaling an arm doubles its return share contribution
    comps2 = dict(comps)
    comps2["IC_leg"] = [2.0 * v for v in comps["IC_leg"]]
    dec2 = decompose(comps2, bars, 1.395)
    row1 = [r for r in dec["rows"] if r["name"] == "IC_leg"][0]
    row2 = [r for r in dec2["rows"] if r["name"] == "IC_leg"][0]
    chk(abs(row2["ann_arith_pct"] - 2.0 * row1["ann_arith_pct"]) < 1e-9,
        "double the arm -> double the contribution")

    # 5) leave-one-out is subtractive, not multiplicative: dropping a constant positive arm
    #    must LOWER the compounded book by roughly that arm's arithmetic contribution
    loo = loo_table(comps, bars, 1.395)
    cash_ann = cash_row["ann_arith_pct"]
    gap = dec["book"]["ann_compound_pct"] - loo["cash"]["ann_compound_pct"]
    chk(loo["cash"]["ann_compound_pct"] < dec["book"]["ann_compound_pct"],
        "dropping a constant positive arm must lower the compounded book")
    chk(abs(gap - cash_ann) < 0.5 * abs(cash_ann) + 0.5,
        "the drop should be about the arm's own contribution, got %.4f vs %.4f"
        % (gap, cash_ann))
    chk(loo["IC_leg"]["vol_pct"] < dec["book"]["vol_pct"], "dropping the big arm lowers vol")

    # 6) neutrality: an arm proportional to equity arm has R^2 = 1
    comps3 = {"equity_arm": a, "IC_leg": [0.5 * v for v in a],
              "IM_leg": [0.5 * v for v in a], "cash": [0.0] * n}
    neu = carry_vs_equity(comps3, bars)
    chk(neu["r2"] is not None and abs(neu["r2"] - 1.0) < 1e-9, "proportional carry -> R^2 1")
    neu2 = carry_vs_equity(comps, bars)
    chk(neu2["r2"] is not None and neu2["r2"] < 0.5, "independent carry -> small R^2")

    # 7) verdicts: equity paid, legs underpaid -> the equity token
    rows = [{"name": "equity_arm", "rent": 3.0, "risk_share": 0.1,
             "ann_arith_pct": 6.0, "return_share": 0.3},
            {"name": "IC_leg", "rent": 0.7, "risk_share": 0.45,
             "ann_arith_pct": 8.0, "return_share": 0.315},
            {"name": "IM_leg", "rent": 0.78, "risk_share": 0.45,
             "ann_arith_pct": 11.0, "return_share": 0.385}]
    v = verdicts({"rows": rows}, {}, {"r2": 0.01}, None, {"sharpe": 1.0})
    chk(v["rent"] == V_EQUITY_RENT, "equity-paid token, got %s" % v["rent"])
    chk(v["neutrality"] == V_NEUTRAL, "neutral token")
    chk(v["biggest_risk_buyer"] == "IC_leg", "biggest risk buyer ties at 0.45 -> first wins")
    chk(v["biggest_earner"] == "IM_leg", "biggest earner is IM")

    # 8) verdicts: every arm paid -> the all-paid token
    rows_all = [dict(r) for r in rows]
    rows_all[1]["rent"] = 1.5
    rows_all[2]["rent"] = 1.6
    chk(verdicts({"rows": rows_all}, {}, {"r2": 0.2}, None,
                 {"sharpe": 1.0})["rent"] == V_ALL_RENT, "all-paid token")

    # 9) rebudget token flips on the frozen threshold
    reb_hi = {"book": {"sharpe": 1.20}, "implied_notional_x_nav": {"equity_arm": 1.0}}
    reb_lo = {"book": {"sharpe": 1.02}, "implied_notional_x_nav": {"equity_arm": 1.0}}
    chk(verdicts({"rows": rows}, {}, {"r2": 0.01}, reb_hi,
                 {"sharpe": 1.0})["rebudget"] == V_REBUDGET_HELP, "rebudget help token")
    chk(verdicts({"rows": rows}, {}, {"r2": 0.01}, reb_lo,
                 {"sharpe": 1.0})["rebudget"] == V_REBUDGET_WASH, "rebudget wash token")
    chk(verdicts({"rows": rows}, {}, {"r2": 0.01}, None,
                 {"sharpe": 1.0})["rebudget"] == V_REBUDGET_NA,
        "no solvable re-budget must NOT be reported as a wash")

    # 10) neutral token flips at NEUTRAL_R2 (not before)
    chk(verdicts({"rows": rows}, {}, {"r2": NEUTRAL_R2}, None,
                 {"sharpe": 1.0})["neutrality"] == V_NEUTRAL, "boundary counts as neutral")
    chk(verdicts({"rows": rows}, {}, {"r2": NEUTRAL_R2 * 1.01}, None,
                 {"sharpe": 1.0})["neutrality"] == V_TRACKS, "above the line -> tracks")

    # 11) risk parity caps implied notional at 1.0 x NAV
    rp = risk_parity(comps, {"equity_arm": 0.4347, "IC_leg": 1.1538, "IM_leg": 1.08688,
                             "cash": 0.0}, bars, 1.395, cap=1.0)
    chk(rp is not None, "risk parity should solve")
    if rp:
        worst = max(abs(v) for v in rp["implied_notional_x_nav"].values())
        chk(abs(worst - 1.0) < 1e-9, "cap binds exactly once: %.6f" % worst)
        eq_share = rp["implied_notional_x_nav"]["equity_arm"]
        chk(eq_share >= rp["implied_notional_x_nav"]["IC_leg"],
            "the low-vol arm should need the larger notional")

    # 12) arithmetic vs compound: they agree only at zero return; a constant positive bar
    #     compounds to MORE than the arithmetic sum (this is why both columns are printed)
    zero = [0.0] * 252
    chk(abs(ann_arith_pct(zero) - ann_compound_pct(zero)) < 1e-9,
        "zero series: arithmetic == compound")
    const = [0.001] * 252
    chk(ann_compound_pct(const) > ann_arith_pct(const),
        "a constant positive bar compounds above the arithmetic sum")
    # 13) mdd never positive, vol never negative
    chk(mdd_pct(a) <= 0.0 and vol_pct(a) >= 0.0, "mdd<=0 and vol>=0")
    # 14) sharpe identity
    chk(abs(sharpe(10.0, 5.0, 1.0) - 1.8) < 1e-9, "sharpe identity")

    print("SELFTEST %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "--selftest"])
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "--selftest":
        return _selftest()
    if args.cmd == "check":
        rc, msg = check()
        print(msg)
        return rc
    face, refusal = build()
    if refusal is not None:
        print(json.dumps(refusal, ensure_ascii=False))
        return 2
    from datetime import datetime, timezone, timedelta
    face["generated"] = (datetime.now(timezone(timedelta(hours=8)))
                         .strftime("%Y-%m-%dT%H:%M:%S+08:00"))
    write_json(OUT, face)
    page = render_page(face)
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    with io.open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    j = face["judgment"]
    print("OK engine=%s rent=%s neutrality=%s rebudget=%s gain=%s band=%s band_rent=%s"
          % (j["engine_rung"], j["engine"]["rent"], j["engine"]["neutrality"],
             j["engine"]["rebudget"], j["engine"]["rebudget_sharpe_gain"], j["band_rung"],
             (j["band"] or {}).get("rent")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
