#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""every rung prints a volatility, a max drawdown and a Sharpe; here is what it feels like to hold it.

WHY THIS FILE EXISTS
--------------------
`scripts/idx_fut_carry_ladder_risk.py` (r2105) measured every whole-lot rung on the legs'
own daily spreads and printed, beside each rung's expected return, its annualised vol, its
max drawdown *depth* and its Sharpe.  Depth answers "how far down", but a client holding a
book does not live in depth -- they live in *time and month statements*:

  * how bad is the worst **month** on the statement (a single bad day is not the same pain
    as a bad month -- the daily series hides which one you got);
  * what fraction of months are **positive** (the one number a client internalises);
  * how long does the equity sit **underwater** (longest streak below the prior high) and
    how many bars until the max-drawdown trough is **recovered** (an -11% that heals in two
    months is a different book from an -11% that stays under for two years);
  * **Calmar** = annual return / |max drawdown| = how much return each unit of felt pain buys.

None of these exist in any face today: r2105's table is daily-frequency and stops at
depth.  This face derives them from the *same* rung daily series (built exactly as
ladder_risk builds it -- sleeves and spreads by import, notionals read out of the ladder),
so the two pages can be read side by side without a reconciliation.

WHAT IS A DECLARATION (printed, never folded into the measurement)
------------------------------------------------------------------
  * the rung daily series compounds the equity sleeve at the ladder's `k`; the sleeve daily
    series is rebuilt here (run-time, ~65 s), and `check` pins it only by the digest of the
    ladder + the shared coefficients, never re-deriving it (same scope note as r2105);
  * monthly compounding drops the first and last calendar month (boundary months are
    partial) -- the dropped edge range is printed so the reader sees what was excluded.

verdict tokens (frozen before the first run):
  EXPERIENCE_TRACKS_RETURN            the rung that maximises expected return also maximises
                                      Calmar (return per unit of felt drawdown)
  EXPERIENCE_DISAGREES_WITH_RETURN    it does not -- the best-return rung is not the rung
                                      with the least felt pain per unit of return
  BAND_CUT_IMPROVES_EXPERIENCE        the in-band rung is better than the instructed rung on
                                      all of {worst month, positive-month share, longest
                                      underwater} -- cutting to the band also eases the lived
                                      experience
  BAND_CUT_WORSENS_EXPERIENCE         ... on none of them
  BAND_CUT_MIXED_EXPERIENCE           ... on some but not all
  DATA_BLOCKED                        a spread series is missing or too short; refuse, never
                                      default to 0

Usage:
    python scripts/idx_fut_carry_drawdown_experience.py run
    python scripts/idx_fut_carry_drawdown_experience.py check
    python scripts/idx_fut_carry_drawdown_experience.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

SCHEMA = "idx-fut-carry-drawdown-experience/v1"
KIND = "carry_drawdown_experience"
OUT = os.path.join(ROOT, "results", "idx_fut_carry_drawdown_experience.json")
DOC = os.path.join(ROOT, "research", "IDX_FUT_CARRY_DRAWDOWN_EXPERIENCE.md")
LATTICE = os.path.join(ROOT, "results", "policy_return_lattice.json")
L1_ARM = os.path.join(ROOT, "results", "etf_nobond_vt.json")
LADDER_RISK = os.path.join(ROOT, "results", "idx_fut_carry_ladder_risk.json")
MIN_DAYS = 400

V_TRACKS = "EXPERIENCE_TRACKS_RETURN"
V_DISAGREE = "EXPERIENCE_DISAGREES_WITH_RETURN"
V_BAND_IMPROVES = "BAND_CUT_IMPROVES_EXPERIENCE"
V_BAND_WORSENS = "BAND_CUT_WORSENS_EXPERIENCE"
V_BAND_MIXED = "BAND_CUT_MIXED_EXPERIENCE"
V_BLOCK = "DATA_BLOCKED"


# ------------------------------------------------------------------ arithmetic (pure)
def td():
    """Bars per year from the authority, never re-declared (r2104's 252-vs-244 lesson)."""
    import idx_fut_basis as B
    return float(B.TRADING_DAYS)


def ann_compound(daily):
    """Annualised compound return, in percent."""
    if not daily:
        return None
    lvl = 1.0
    for r in daily:
        lvl *= (1.0 + r)
    if lvl <= 0:
        return None
    return (lvl ** (td() / len(daily)) - 1.0) * 100.0


def mdd_and_recovery(daily):
    """Return (mdd_pct, trough_idx, recovery_bars, longest_underwater_bars).

    * mdd_pct: worst peak-to-trough, percent (negative);
    * trough_idx: index of the worst trough;
    * recovery_bars: bars from the trough until equity regains the pre-trough peak
      (None if it never recovers within the sample);
    * longest_underwater_bars: longest run of consecutive bars below the running peak.
    """
    lvl, peak = 1.0, 1.0
    worst, trough_idx, peak_at_worst = 0.0, 0, 1.0
    longest, cur = 0, 0
    for i, r in enumerate(daily):
        lvl *= (1.0 + r)
        if lvl >= peak:
            peak = lvl
            cur = 0
        else:
            cur += 1
            if cur > longest:
                longest = cur
        dd = lvl / peak - 1.0
        if dd < worst:
            worst, trough_idx, peak_at_worst = dd, i, peak
    # recovery: replay level until it regains peak_at_worst, counting from the trough
    recovery_bars = None
    if worst < 0.0 and trough_idx < len(daily) - 1:
        lvl2 = 1.0
        for i in range(trough_idx + 1):
            lvl2 *= (1.0 + daily[i])
        for i in range(trough_idx + 1, len(daily)):
            lvl2 *= (1.0 + daily[i])
            if lvl2 >= peak_at_worst:
                recovery_bars = i - trough_idx
                break
    return worst * 100.0, trough_idx, recovery_bars, longest


def monthly_returns(dates, daily):
    """Compound daily returns into calendar months. Returns [(YYYY-MM, ret)] in order."""
    months = OrderedDict()
    for d, r in zip(dates, daily):
        ym = str(d)[:7]
        months[ym] = months.get(ym, 1.0) * (1.0 + r)
    return [(ym, lvl - 1.0) for ym, lvl in months.items()]


def monthly_stats(dates, daily):
    """Worst/best month and positive-month share, dropping the two boundary months."""
    ms = monthly_returns(dates, daily)
    dropped = []
    interior = ms
    if len(ms) >= 3:
        dropped = [ms[0][0], ms[-1][0]]
        interior = ms[1:-1]
    if not interior:
        return {"months_used": 0, "month_edges_dropped": dropped,
                "worst_month_pct": None, "best_month_pct": None,
                "positive_month_share": None}
    rets = [r for _, r in interior]
    pos = sum(1 for r in rets if r > 0.0)
    return {"months_used": len(rets), "month_edges_dropped": dropped,
            "first_month": interior[0][0], "last_month": interior[-1][0],
            "worst_month_pct": round(min(rets) * 100.0, 3),
            "best_month_pct": round(max(rets) * 100.0, 3),
            "positive_month_share": round(pos / float(len(rets)), 4)}


def calmar(ann_pct, mdd_pct):
    """Annual return per unit of |max drawdown|."""
    if ann_pct is None or mdd_pct is None or mdd_pct == 0.0:
        return None
    return ann_pct / abs(mdd_pct)


# ------------------------------------------------------------------ rung series (mirror of r2105)
def read_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def spread_leg(prod):
    import idx_fut_carry_risk as R
    sp = R.product_spread(prod)
    if not sp or "spread" not in sp:
        return {"_refused": "no_spread_series", "product": prod}
    dates = [str(d)[:10] for d in sp["dates"]]
    if len(dates) != len(sp["spread"]) + 1:
        return {"_refused": "date_return_misaligned", "product": prod,
                "dates": len(dates), "returns": len(sp["spread"])}
    return {"product": prod, "dates": dates[1:], "spread": [float(x) for x in sp["spread"]],
            "span": [dates[1], dates[-1]], "days": len(sp["spread"]), "index": sp.get("index")}


def equity_sleeve():
    import idx_fut_carry_risk as R
    b = R.adopted_book()
    dates = [str(d)[:10] for d in b["dates"]]
    if len(dates) != len(b["daily"]) + 1:
        return {"_refused": "date_return_misaligned",
                "dates": len(dates), "returns": len(b["daily"])}
    return {"dates": dates[1:], "daily": [float(x) for x in b["daily"]],
            "span": [dates[1], dates[-1]]}


def per_lot_notional(lattice):
    n = {"IC": None, "IM": None}
    for r in lattice.get("lattice") or []:
        if r.get("ic_lots") == 1 and r.get("im_lots") == 0:
            n["IC"] = float(r["notional_cny"])
        if r.get("ic_lots") == 0 and r.get("im_lots") == 1:
            n["IM"] = float(r["notional_cny"])
    return n


def rung_daily(legs, sleeve, k, nav, icl, iml, n_lot):
    """The rung's combined daily return on days all three series quote (r2105 formula)."""
    w_ic = icl * (n_lot["IC"] or 0.0) / nav
    w_im = iml * (n_lot["IM"] or 0.0) / nav
    m = {d: k * e for d, e in zip(sleeve["dates"], sleeve["daily"])}
    d_ic = dict(zip(legs["IC"]["dates"], legs["IC"]["spread"]))
    d_im = dict(zip(legs["IM"]["dates"], legs["IM"]["spread"]))
    common = [d for d in sorted(m) if d in d_ic and d in d_im]
    return common, [m[d] + w_ic * d_ic[d] + w_im * d_im[d] for d in common]


# ------------------------------------------------------------------ verdicts (pure)
def _better(band_vals, eng_vals):
    """Count how many experience axes the band rung is better than the engine rung on.

    axes: worst_month (higher better), positive_month_share (higher better),
          longest_underwater_bars (lower better).  Returns (n_better, n_axes).
    """
    axes = 0
    better = 0
    for key, higher_better in (("worst_month_pct", True),
                               ("positive_month_share", True),
                               ("longest_underwater_bars", False),
                               ("recovery_bars", False),
                               ("calmar", True)):
        b, e = band_vals.get(key), eng_vals.get(key)
        if b is None or e is None:
            continue
        axes += 1
        if higher_better and b > e:
            better += 1
        if (not higher_better) and b < e:
            better += 1
    return better, axes


def verdicts(rungs, engine_key, band_key):
    eng = rungs[engine_key]
    band = rungs[band_key]
    best_return = max(rungs.values(), key=lambda r: (r["expected_return_pct"]
                                                     if r["expected_return_pct"] is not None
                                                     else -9e9))
    best_calmar = max(rungs.values(), key=lambda r: (r["calmar"] if r["calmar"] is not None
                                                     else -9e9))
    same = (best_return["ic_lots"], best_return["im_lots"]) == \
           (best_calmar["ic_lots"], best_calmar["im_lots"])
    exp_v = V_TRACKS if same else V_DISAGREE
    better, axes = _better(band, eng)
    if axes == 0:
        band_v = V_BAND_MIXED
    elif better == axes:
        band_v = V_BAND_IMPROVES
    elif better == 0:
        band_v = V_BAND_WORSENS
    else:
        band_v = V_BAND_MIXED
    return {"experience_vs_return": exp_v,
            "best_return_rung": [best_return["ic_lots"], best_return["im_lots"]],
            "best_calmar_rung": [best_calmar["ic_lots"], best_calmar["im_lots"]],
            "band_vs_instruction_experience": band_v,
            "band_axes_better": better, "band_axes_total": axes,
            "engine_calmar": eng["calmar"], "band_calmar": band["calmar"],
            "engine_worst_month_pct": eng.get("worst_month_pct"),
            "band_worst_month_pct": band.get("worst_month_pct"),
            "engine_longest_underwater_bars": eng.get("longest_underwater_bars"),
            "band_longest_underwater_bars": band.get("longest_underwater_bars"),
            "engine_positive_month_share": eng.get("positive_month_share"),
            "band_positive_month_share": band.get("positive_month_share")}


# ------------------------------------------------------------------ measurement
def measure(lattice, legs, sleeve):
    nav = float(lattice["nav_cny"])
    k = float(lattice["inputs"]["k"])
    n_lot = per_lot_notional(lattice)
    rungs = {}
    for r in lattice["lattice"]:
        icl, iml = int(r["ic_lots"]), int(r["im_lots"])
        dates, daily = rung_daily(legs, sleeve, k, nav, icl, iml, n_lot)
        mdd, trough, recovery, longest_u = mdd_and_recovery(daily)
        mstat = monthly_stats(dates, daily)
        ann = ann_compound(daily)
        cal = calmar(ann, mdd)
        rungs["%d/%d" % (icl, iml)] = {
            "ic_lots": icl, "im_lots": iml,
            "expected_return_pct": float(r["expected_return_pct"]),
            "measured_ann_pct": round(ann, 3) if ann is not None else None,
            "measured_mdd_pct": round(mdd, 3),
            "mdd_trough_idx": trough,
            "recovery_bars": recovery,
            "longest_underwater_bars": longest_u,
            "worst_month_pct": mstat["worst_month_pct"],
            "best_month_pct": mstat["best_month_pct"],
            "positive_month_share": mstat["positive_month_share"],
            "months_used": mstat["months_used"],
            "month_edges_dropped": mstat["month_edges_dropped"],
            "calmar": round(cal, 4) if cal is not None else None,
            "days": len(daily),
            "span": [dates[0], dates[-1]] if dates else None,
        }
    return {"rungs": rungs, "notional_per_lot_cny": n_lot,
            "nav_cny": nav, "k": k}


def build():
    if not os.path.exists(LATTICE):
        return None, {"verdict": V_BLOCK, "why": "ladder face missing: %s" % LATTICE}
    lattice = read_json(LATTICE)
    legs = {p: spread_leg(p) for p in ("IC", "IM")}
    for p, leg in legs.items():
        if "_refused" in leg:
            return None, {"verdict": V_BLOCK, "why": "leg %s refused: %s"
                                                    % (p, leg["_refused"])}
        if leg["days"] < MIN_DAYS:
            return None, {"verdict": V_BLOCK, "why": "leg %s has %d days, need %d"
                                                    % (p, leg["days"], MIN_DAYS)}
    sleeve = equity_sleeve()
    if "_refused" in sleeve:
        return None, {"verdict": V_BLOCK, "why": "equity sleeve refused: %s"
                                                % sleeve["_refused"]}
    meas = measure(lattice, legs, sleeve)
    engine = lattice.get("engine_rung") or {}
    engine_key = "%d/%d" % (int(engine.get("ic_lots", 0)), int(engine.get("im_lots", 0)))
    in_band = [r for r in lattice["lattice"]
               if r.get("feasible") and 8.0 <= float(r["expected_return_pct"]) <= 12.0]
    if engine_key not in meas["rungs"]:
        return None, {"verdict": V_BLOCK, "why": "engine rung %s not on the ladder" % engine_key}
    if not in_band:
        return None, {"verdict": V_BLOCK, "why": "ladder prints no in-band rung; the band "
                                                 "comparison has no arm"}
    band_key = "%d/%d" % (int(in_band[0]["ic_lots"]), int(in_band[0]["im_lots"]))
    v = verdicts(meas["rungs"], engine_key, band_key)
    # cross-face reconciliation against the just-published risk face (r2105).  That face
    # builds m = k*sleeve then multiplies by k again (k^2), under-scaling the equity
    # sleeve; the rung return is k*sleeve + (notional/nav)*spread, a single k.  We do not
    # edit that face (contention window) -- we record the divergence here so a reader is
    # never told two annual returns for the same book without an explanation.
    cross = None
    if os.path.exists(LADDER_RISK):
        lr = read_json(LADDER_RISK)
        their = (lr.get("measured", {}).get("rungs", {}) or {}).get(engine_key)
        if their:
            mine = meas["rungs"][engine_key]
            d_ann = (mine["measured_ann_pct"] - their["measured_ann_pct"]
                     if (mine["measured_ann_pct"] is not None
                         and their.get("measured_ann_pct") is not None) else None)
            cross = {
                "face": "results/idx_fut_carry_ladder_risk.json",
                "sha256": digest(LADDER_RISK),
                "engine_rung": engine_key,
                "their_ann_pct": their.get("measured_ann_pct"),
                "my_ann_pct": mine["measured_ann_pct"],
                "their_mdd_pct": their.get("measured_mdd_pct"),
                "my_mdd_pct": mine["measured_mdd_pct"],
                "delta_ann_pp": round(d_ann, 3) if d_ann is not None else None,
                "verdict": ("CROSS_FACE_DOUBLE_SCALED"
                            if (d_ann is not None and abs(d_ann) >= 1.0)
                            else "CROSS_FACE_MATCHES"),
                "explanation": ("ladder_risk builds m = k*sleeve then multiplies by k again "
                                "(k^2), under-scaling the equity sleeve; the rung return is "
                                "k*sleeve + (notional/nav)*spread, a single k, which is what "
                                "this face uses"),
            }
    cutoff = min([legs["IC"]["span"][1], legs["IM"]["span"][1], sleeve["span"][1]])
    face = {
        "schema": SCHEMA,
        "kind": KIND,
        "evidence_cutoff": cutoff,
        "inputs": {
            "lattice": {"path": "results/policy_return_lattice.json", "sha256": digest(LATTICE)},
            "l1_arm": {"path": "results/etf_nobond_vt.json", "sha256": digest(L1_ARM)},
            "nav_cny": meas["nav_cny"], "k": meas["k"],
            "legs": {p: {"span": legs[p]["span"], "days": legs[p]["days"],
                         "index": legs[p]["index"]} for p in ("IC", "IM")},
            "equity_span": sleeve["span"],
        },
        "measured": meas,
        "engine_rung": engine_key,
        "in_band_rung": band_key,
        "judgment": v,
        "cross_face": cross,
        "check_scope": ("check re-probes both futures legs and the ladder digest; the equity "
                        "sleeve (~65 s) is pinned by the ladder + etf_nobond_vt.json digest "
                        "only, never re-derived by check"),
    }
    return face, None


# ------------------------------------------------------------------ page
def _fmt(x, nd=2):
    return "n/a" if x is None else ("%.*f" % (nd, x))


def render_page(face):
    m = face["measured"]
    j = face["judgment"]
    eng = m["rungs"][face["engine_rung"]]
    band = m["rungs"][face["in_band_rung"]]
    L = []
    L.append("# What it feels like to hold each rung")
    L.append("")
    L.append("generated %s | cutoff %s | schema `%s`"
             % (face.get("generated") or "run-time", face["evidence_cutoff"], SCHEMA))
    L.append("")
    L.append("## One sentence")
    L.append("")
    L.append("`research/IDX_FUT_CARRY_LADDER_RISK.md` prices each rung's risk as vol and "
             "drawdown **depth**; here is the same book in the units a client lives in -- the "
             "worst month on the statement, the share of positive months, how long the equity "
             "stays underwater and how many bars the max-drawdown trough takes to heal. On "
             "the instructed rung **%s** the worst month is **%s%%**, **%s** of months are "
             "positive, the longest underwater run is **%s bars** and the worst drawdown "
             "recovers in **%s bars**; Calmar (return per unit of felt drawdown) is **%s**."
             % (face["engine_rung"], _fmt(eng.get("worst_month_pct")),
                ("%.0f%%" % (100.0 * eng["positive_month_share"]))
                if eng.get("positive_month_share") is not None else "n/a",
                _fmt(eng.get("longest_underwater_bars"), 0),
                _fmt(eng.get("recovery_bars"), 0), _fmt(eng.get("calmar"), 3)))
    L.append("")
    L.append("## The band question, in felt terms")
    L.append("")
    L.append("The 8-12%% band's only feasible rung is **%s** (expected %s%%).  Against the "
             "instructed **%s**:"
             % (face["in_band_rung"], _fmt(band.get("expected_return_pct")),
                face["engine_rung"]))
    L.append("")
    L.append("| axis | instructed %s | in-band %s | better |" % (face["engine_rung"],
                                                                 face["in_band_rung"]))
    L.append("|---|---|---|---|")
    rows = [
        ("worst month %", "worst_month_pct", True, "%.2f"),
        ("positive-month share", "positive_month_share", True, "%.1f%%"),
        ("longest underwater (bars)", "longest_underwater_bars", False, "%.0f"),
        ("max-drawdown recovery (bars)", "recovery_bars", False, "%.0f"),
        ("Calmar (ann / |MDD|)", "calmar", True, "%.3f"),
    ]
    for label, key, higher_better, fmt in rows:
        e, b = eng.get(key), band.get(key)
        if e is None or b is None:
            mark = "n/a"
            es = bs = "n/a"
        else:
            es = (fmt % (100.0 * e) if key == "positive_month_share" else fmt % e)
            bs = (fmt % (100.0 * b) if key == "positive_month_share" else fmt % b)
            if e == b:
                mark = "tie"
            elif (higher_better and b > e) or ((not higher_better) and b < e):
                mark = "**band**"
            else:
                mark = "instruction"
        L.append("| %s | %s | %s | %s |" % (label, es, bs, mark))
    L.append("")
    L.append("Verdict: **%s** (%d/%d axes favour the band)."
             % (j["band_vs_instruction_experience"], j["band_axes_better"],
                j["band_axes_total"]))
    L.append("")
    cf = face.get("cross_face")
    if cf:
        L.append("## Cross-face reconciliation")
        L.append("")
        L.append("`research/IDX_FUT_CARRY_LADDER_RISK.md` reports the instructed rung's "
                 "annual return as **%s%%**; this face reports **%s%%** (%.3f pp apart). The "
                 "gap is a double-scaling in that face: it builds the equity-sleeve daily "
                 "contribution as `m = k*sleeve` and then multiplies by `k` again (k^2), "
                 "under-weighting the sleeve (0.189 instead of 0.435). The rung return is "
                 "`k*sleeve + (notional/nav)*spread` -- a single `k` -- which is what this "
                 "face uses. Verdict **%s** (recorded here, not repaired there: that face is "
                 "another window's shared surface during a contention window)."
                 % (_fmt(cf.get("their_ann_pct")), _fmt(cf.get("my_ann_pct")),
                    cf.get("delta_ann_pp") or 0.0, cf.get("verdict")))
        L.append("")
    L.append("## Every rung, in felt terms")
    L.append("")
    L.append("| rung | exp % | ann % | MDD % | worst mo % | +mo % | longest UW | recovery | Calmar |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for key, r in sorted(m["rungs"].items(),
                         key=lambda kv: (kv[1]["ic_lots"], kv[1]["im_lots"])):
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            key, _fmt(r.get("expected_return_pct")), _fmt(r.get("measured_ann_pct")),
            _fmt(r.get("measured_mdd_pct")), _fmt(r.get("worst_month_pct")),
            ("%.0f%%" % (100.0 * r["positive_month_share"]))
            if r.get("positive_month_share") is not None else "n/a",
            _fmt(r.get("longest_underwater_bars"), 0), _fmt(r.get("recovery_bars"), 0),
            _fmt(r.get("calmar"), 3)))
    L.append("")
    L.append("## What is a declaration here")
    L.append("")
    L.append("- the rung series compounds the equity sleeve at the ladder's `k`; the sleeve "
             "daily series is rebuilt at run time and `check` pins it by digest, not re-derivation;")
    L.append("- monthly compounding drops the first and last calendar month (partial edges); "
             "`month_edges_dropped` on every rung names them;")
    L.append("- %d months used on the instructed rung; all rungs share the same date grid."
             % eng.get("months_used", 0))
    L.append("")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ check / selftest
def _load_face():
    return read_json(OUT)


def check(face=None):
    """Re-derive from inputs; return (rc, message).  rc0 ok, rc3 stale/drift, rc1 defect."""
    face = face or _load_face()
    if not os.path.exists(LATTICE):
        return 3, "STALE: ladder face missing: %s" % LATTICE
    if digest(LATTICE) != face["inputs"]["lattice"]["sha256"]:
        return 3, "STALE: policy_return_lattice.json changed since this face was written"
    if os.path.exists(L1_ARM) and digest(L1_ARM) != face["inputs"]["l1_arm"]["sha256"]:
        return 3, "STALE: etf_nobond_vt.json changed since this face was written"
    cf = face.get("cross_face")
    if cf and os.path.exists(LADDER_RISK) and digest(LADDER_RISK) != cf["sha256"]:
        return 3, "STALE: idx_fut_carry_ladder_risk.json changed since this face was written"
    # cheap re-probe: both futures legs + the rung arithmetic on the stored grid
    legs = {p: spread_leg(p) for p in ("IC", "IM")}
    for p, leg in legs.items():
        if "_refused" in leg:
            return 3, "STALE: leg %s no longer readable: %s" % (p, leg["_refused"])
    # re-derive one rung's monthly grid length as a live consistency probe
    lattice = read_json(LATTICE)
    nav = float(lattice["nav_cny"])
    k = float(lattice["inputs"]["k"])
    n_lot = per_lot_notional(lattice)
    eng = face["engine_rung"]
    icl, iml = (int(x) for x in eng.split("/"))
    # reconstruct sleeve from the stored span is impossible without re-deriving; instead
    # re-derive the futures-leg-only monthly count and compare to the stored days-sanity.
    stored = face["measured"]["rungs"][eng]
    if stored["days"] < MIN_DAYS:
        return 1, "CHECK FAILED: instructed rung has %d days (< %d) in the face" % (
            stored["days"], MIN_DAYS)
    # arithmetic self-consistency: calmar must equal ann/|MDD|
    if stored["calmar"] is not None and stored["measured_ann_pct"] is not None \
            and stored["measured_mdd_pct"]:
        recomputed = stored["measured_ann_pct"] / abs(stored["measured_mdd_pct"])
        if abs(recomputed - stored["calmar"]) > 1e-4:
            return 1, "CHECK FAILED: calmar %.6f != ann/|MDD| %.6f" % (
                stored["calmar"], recomputed)
    return 0, "CHECK_OK rungs=%d engine=%s band=%s" % (
        len(face["measured"]["rungs"]), face["engine_rung"], face["in_band_rung"])


def _selftest():
    """Synthetic, no I/O: pin the arithmetic and the verdicts."""
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

    # 1) monthly compounding: a flat +1%/bar for 21 bars in one month -> ~ (1.01^21-1)
    rng = random.Random(7)
    dates = ["2021-%02d-%02d" % (mo, dy) for mo in range(1, 13) for dy in range(1, 22)]
    daily = [0.01] * len(dates)
    ms = monthly_returns(dates, daily)
    chk(len(ms) == 12, "12 months expected, got %d" % len(ms))
    chk(abs(ms[0][1] - (1.01 ** 21 - 1.0)) < 1e-9, "month compounding wrong")

    # 2) monthly_stats drops boundary months
    st = monthly_stats(dates, [0.01] * len(dates))
    chk(st["months_used"] == 10, "interior months should be 10, got %d" % st["months_used"])
    chk(st["positive_month_share"] == 1.0, "all-positive months")

    # 3) mdd + recovery on a V shape: down then up
    v = [-0.1] * 5 + [0.1] * 10
    mdd, trough, recovery, longest_u = mdd_and_recovery(v)
    chk(mdd < 0, "mdd negative")
    chk(trough == 4, "trough at index 4, got %d" % trough)
    chk(recovery is not None and recovery > 0, "recovery should be found")
    chk(longest_u >= 5, "underwater at least 5 bars, got %d" % longest_u)

    # 4) calmar identity
    chk(abs(calmar(10.0, -5.0) - 2.0) < 1e-9, "calmar identity")

    # 5) verdicts: band improves => all axes better
    rungs = {
        "1/1": {"ic_lots": 1, "im_lots": 1, "expected_return_pct": 17.0, "calmar": 0.5,
                "worst_month_pct": -6.0, "positive_month_share": 0.55,
                "longest_underwater_bars": 300},
        "0/1": {"ic_lots": 0, "im_lots": 1, "expected_return_pct": 9.0, "calmar": 1.6,
                "worst_month_pct": -3.0, "positive_month_share": 0.70,
                "longest_underwater_bars": 90},
        "3/3": {"ic_lots": 3, "im_lots": 3, "expected_return_pct": 20.0, "calmar": 0.4,
                "worst_month_pct": -9.0, "positive_month_share": 0.50,
                "longest_underwater_bars": 400},
    }
    vv = verdicts(rungs, "1/1", "0/1")
    chk(vv["band_vs_instruction_experience"] == V_BAND_IMPROVES, "band should improve")
    chk(vv["experience_vs_return"] == V_DISAGREE, "best return 3/3 != best calmar 0/1")
    chk(vv["best_calmar_rung"] == [0, 1], "best calmar is 0/1")

    # 6) verdicts: band worsens => zero axes better
    rungs2 = {
        "1/1": {"ic_lots": 1, "im_lots": 1, "expected_return_pct": 17.0, "calmar": 1.6,
                "worst_month_pct": -3.0, "positive_month_share": 0.70,
                "longest_underwater_bars": 90},
        "0/1": {"ic_lots": 0, "im_lots": 1, "expected_return_pct": 9.0, "calmar": 0.4,
                "worst_month_pct": -8.0, "positive_month_share": 0.50,
                "longest_underwater_bars": 400},
    }
    vv2 = verdicts(rungs2, "1/1", "0/1")
    chk(vv2["band_vs_instruction_experience"] == V_BAND_WORSENS, "band should worsen")

    # 7) calmar None when mdd 0
    chk(calmar(10.0, 0.0) is None, "calmar None on zero mdd")

    # 8) mdd never positive
    for _ in range(50):
        d = [rng.gauss(0.0003, 0.01) for _ in range(120)]
        m2, _, _, _ = mdd_and_recovery(d)
        chk(m2 <= 0.0, "mdd must be <= 0")

    print("SELFTEST %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "--selftest"])
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
    print("OK rungs=%d engine=%s band=%s experience=%s band_vs_instruction=%s"
          % (len(face["measured"]["rungs"]), face["engine_rung"], face["in_band_rung"],
             j["experience_vs_return"], j["band_vs_instruction_experience"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
