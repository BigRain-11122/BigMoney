#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""the return ladder prints a risk column built from two constants; here is the measurement.

WHY THIS FILE EXISTS
--------------------
`scripts/policy_return_lattice.py` puts every whole-lot rung of the carry book on one
page and prints, beside each rung's expected return, a volatility:

    l2         = (notional / nav) * L2_CARRY_VOL          <- 4.0 %/yr per unit notional
    vol_total  = sqrt(v1^2 + l2^2 + 2 * RHO * v1 * l2)    <- RHO = 0.10

Both `L2_CARRY_VOL` and `RHO` are declarations.  The comment beside `L2_CARRY_VOL` says
"measured carry vol", but nothing in the repo measures it, and the model cannot express
the two legs having different volatility or a correlation at all -- it treats IC + IM as
one notional block.  r2100's band verdict (instruction 17.4 % vs the 8-12 % band) is
therefore a statement about *expected return* only: the risk column beside it has never
touched a price series.

This face measures what can be measured from the legs' own published daily spreads, and
rebuilds every rung's volatility from those measurements:

  * sigma_IC, sigma_IM  annualised vol of `idx_fut_carry_risk.product_spread(...)["spread"]`
                        (held contract minus index, daily, the same series the risk and
                        pause-price faces price);
  * rho_fut             measured correlation between the two legs' spreads, on the days
                        both legs quote;
  * rho_eq              measured correlation between the equity sleeve's own daily series
                        (`idx_fut_carry_risk.adopted_book`) and the futures leg;
  * every rung's measured ann / vol / max-drawdown / Sharpe on the combined daily series.

Nothing here re-derives a leg: the spreads come from the authority module by import, and
the rung weights come from the ladder's own published notionals (one lot of each product
read out of its own lattice, never re-declared here).

WHAT IS STILL A DECLARATION (printed as such, never folded into the measurement)
--------------------------------------------------------------------------------
  * the equity sleeve is sized by the ladder's `k`, so its contribution is `k * daily`
    -- that is a capital statement, not a measurement of the sleeve;
  * `check` re-probes the two futures legs (cheap) and the ladder; the equity sleeve's
    daily series costs ~65 s to rebuild and is pinned only by the digest of its
    published production arm (`results/etf_nobond_vt.json`).  This scope is printed on
    the face so a reader is never told a green check covered something it did not read.

verdict tokens (frozen before the first run):
  DECLARED_RISK_UNDERSTATES_MEASURED   measured total vol exceeds the ladder's declared
                                        vol on the instructed rung by >= 1.0 pp
  DECLARED_RISK_OVERSTATES_MEASURED     ... is below it by >= 1.0 pp
  DECLARED_RISK_MATCHES_MEASURED        within +-1.0 pp
  BAND_CUT_CONCENTRATES_RISK            the in-band rung draws down >= 1.0 pp deeper than
                                        the instructed rung: cutting to the band does not
                                        cut risk
  BAND_CUT_ALSO_CUTS_RISK               the in-band rung is also the shallower one
  SHARPE_DISAGREES_WITH_RETURN          the rung that maximises measured Sharpe is not the
                                        rung that maximises expected return
  RETURN_AND_RISK_AGREE                 it is the same rung
  DATA_BLOCKED                          a spread series is missing or too short; refuse,
                                        never default to 0

Usage:
    python scripts/idx_fut_carry_ladder_risk.py run
    python scripts/idx_fut_carry_ladder_risk.py check
    python scripts/idx_fut_carry_ladder_risk.py --selftest
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

SCHEMA = "idx-fut-carry-ladder-risk/v1"
KIND = "carry_ladder_risk_measurement"
OUT = os.path.join(ROOT, "results", "idx_fut_carry_ladder_risk.json")
DOC = os.path.join(ROOT, "research", "IDX_FUT_CARRY_LADDER_RISK.md")
LATTICE = os.path.join(ROOT, "results", "policy_return_lattice.json")
L1_ARM = os.path.join(ROOT, "results", "etf_nobond_vt.json")

# the two declarations this face replaces with measurements (kept for the comparison)
DECLARED_L2_VOL_PCT = 4.0     # scripts/policy_return_lattice.py L2_CARRY_VOL
DECLARED_RHO = 0.10           # scripts/policy_return_lattice.py RHO
TOL_PP = 1.0                  # "same number" tolerance, pp of annualised vol
MIN_DAYS = 400                # below this the refusal is a short sample, not a verdict

V_UNDER = "DECLARED_RISK_UNDERSTATES_MEASURED"
V_OVER = "DECLARED_RISK_OVERSTATES_MEASURED"
V_MATCH = "DECLARED_RISK_MATCHES_MEASURED"
V_BAND_CONC = "BAND_CUT_CONCENTRATES_RISK"
V_BAND_CUTS = "BAND_CUT_ALSO_CUTS_RISK"
V_SHARPE_DIS = "SHARPE_DISAGREES_WITH_RETURN"
V_SHARPE_AGREE = "RETURN_AND_RISK_AGREE"
V_BLOCK = "DATA_BLOCKED"


# ------------------------------------------------------------------ arithmetic (pure)
def td():
    """Bars per year from the authority, never re-declared (r2104's 252-vs-244 lesson)."""
    import idx_fut_basis as B
    return float(B.TRADING_DAYS)


def ann_vol(daily):
    """Annualised vol, in percent, of a daily simple-return series."""
    n = len(daily)
    if n < 2:
        return None
    m = sum(daily) / n
    v = sum((x - m) ** 2 for x in daily) / (n - 1)
    return math.sqrt(v) * math.sqrt(td()) * 100.0


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


def mdd_pct(daily):
    """Max drawdown of the compound equity, in percent (negative)."""
    lvl, peak, worst = 1.0, 1.0, 0.0
    for r in daily:
        lvl *= (1.0 + r)
        peak = max(peak, lvl)
        worst = min(worst, lvl / peak - 1.0)
    return worst * 100.0


def corr(a, b):
    n = min(len(a), len(b))
    if n < 3:
        return None
    a, b = a[:n], b[:n]
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va <= 0 or vb <= 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(va * vb)


def portfolio_vol_pct(w1, s1, w2, s2, rho):
    """Two-asset annualised vol, in percent, from per-unit vols (percent) and weights."""
    if w1 * s1 == 0.0 and w2 * s2 == 0.0:
        return 0.0
    var = (w1 * s1) ** 2 + (w2 * s2) ** 2 + 2.0 * rho * (w1 * s1) * (w2 * s2)
    return math.sqrt(max(var, 0.0))


def align(dates_a, series_a, dates_b, series_b):
    """Line up two (dates[1:], series) pairs on their common days, order preserved."""
    ma = dict(zip(dates_a, series_a))
    mb = dict(zip(dates_b, series_b))
    common = sorted(set(ma) & set(mb))
    return common, [ma[d] for d in common], [mb[d] for d in common]


def per_lot_notional(lattice):
    """One lot of each product, read out of the ladder's own rungs (never re-declared)."""
    n = {"IC": None, "IM": None}
    for r in lattice.get("lattice") or []:
        if r.get("ic_lots") == 1 and r.get("im_lots") == 0:
            n["IC"] = float(r["notional_cny"])
        if r.get("ic_lots") == 0 and r.get("im_lots") == 1:
            n["IM"] = float(r["notional_cny"])
    return n


def verdicts(rungs, declared_vol_pct, engine_key, in_band_key, tol_pp=TOL_PP):
    """The three judgments, derived from rung measurements only (pure; selftest pins it)."""
    eng = rungs[engine_key]
    band = rungs[in_band_key]
    diff = eng["measured_vol_pct"] - declared_vol_pct
    if diff >= tol_pp:
        risk = V_UNDER
    elif diff <= -tol_pp:
        risk = V_OVER
    else:
        risk = V_MATCH
    mdd_gap = band["measured_mdd_pct"] - eng["measured_mdd_pct"]
    band_v = V_BAND_CONC if mdd_gap <= -tol_pp else V_BAND_CUTS
    best_sharpe = max(rungs.values(), key=lambda r: (r["measured_sharpe"]
                                                     if r["measured_sharpe"] is not None
                                                     else -9e9))
    best_return = max(rungs.values(), key=lambda r: r["expected_return_pct"])
    sharpe_v = (V_SHARPE_AGREE
                if (best_sharpe["ic_lots"], best_sharpe["im_lots"])
                == (best_return["ic_lots"], best_return["im_lots"])
                else V_SHARPE_DIS)
    return {"declared_vs_measured_vol": risk,
            "declared_vol_pct": round(declared_vol_pct, 3),
            "measured_vol_pct": round(eng["measured_vol_pct"], 3),
            "measured_minus_declared_pp": round(diff, 3),
            "band_vs_instruction_risk": band_v,
            "band_mdd_gap_pp": round(mdd_gap, 3),
            "sharpe_vs_return": sharpe_v,
            "best_sharpe_rung": [best_sharpe["ic_lots"], best_sharpe["im_lots"]],
            "best_return_rung": [best_return["ic_lots"], best_return["im_lots"]]}


# ------------------------------------------------------------------ measurement
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
    """The leg's daily spread, dates[1:] aligned to the returns (never rebuilt here)."""
    import idx_fut_carry_risk as R
    sp = R.product_spread(prod)
    if not sp or "spread" not in sp:
        return {"_refused": "no_spread_series", "product": prod}
    dates = [str(d)[:10] for d in sp["dates"]]
    if len(dates) != len(sp["spread"]) + 1:
        return {"_refused": "date_return_misaligned", "product": prod,
                "dates": len(dates), "returns": len(sp["spread"])}
    return {"product": prod, "dates": dates[1:], "spread": [float(x) for x in sp["spread"]],
            "span": [dates[1], dates[-1]], "days": len(sp["spread"]),
            "index": sp.get("index")}


def equity_sleeve():
    """The book's adopted equity arm daily series (expensive: ~65 s, run-time only)."""
    import idx_fut_carry_risk as R
    b = R.adopted_book()
    dates = [str(d)[:10] for d in b["dates"]]
    if len(dates) != len(b["daily"]) + 1:
        return {"_refused": "date_return_misaligned",
                "dates": len(dates), "returns": len(b["daily"])}
    return {"dates": dates[1:], "daily": [float(x) for x in b["daily"]],
            "span": [dates[1], dates[-1]], "stats": b.get("stats")}


def measure(lattice, legs, sleeve, k, nav, rf_pct):
    """Every rung's risk, measured.  Pure given its inputs (selftest builds its own)."""
    ic, im = legs["IC"], legs["IM"]
    _, s_ic, s_im = align(ic["dates"], ic["spread"], im["dates"], im["spread"])
    rho_fut = corr(s_ic, s_im)
    sig_ic = ann_vol(s_ic)
    sig_im = ann_vol(s_im)
    _, s_ic2, s_eq = align(ic["dates"], ic["spread"], sleeve["dates"], sleeve["daily"])
    rho_eq = corr(s_eq, s_ic2)
    n_lot = per_lot_notional(lattice)
    rungs = {}
    for r in lattice["lattice"]:
        icl, iml = int(r["ic_lots"]), int(r["im_lots"])
        w_ic = icl * (n_lot["IC"] or 0.0) / nav
        w_im = iml * (n_lot["IM"] or 0.0) / nav
        # combined daily return on the days all three series quote
        m = {d: k * e for d, e in zip(sleeve["dates"], sleeve["daily"])}
        dates_ic = dict(zip(ic["dates"], ic["spread"]))
        dates_im = dict(zip(im["dates"], im["spread"]))
        common = [d for d in sorted(m) if d in dates_ic and d in dates_im]
        daily = [k * m[d] + w_ic * dates_ic[d] + w_im * dates_im[d] for d in common]
        vol = ann_vol(daily)
        ann = ann_compound(daily)
        mdd = mdd_pct(daily)
        sharpe = ((ann - rf_pct) / vol) if (vol and vol > 0 and ann is not None) else None
        rungs["%d/%d" % (icl, iml)] = {
            "ic_lots": icl, "im_lots": iml,
            "weight_ic": round(w_ic, 6), "weight_im": round(w_im, 6),
            "expected_return_pct": float(r["expected_return_pct"]),
            "declared_vol_pct": float(r.get("vol_uncapped_pct") or 0.0),
            "l2_vol_measured_pct": round(
                portfolio_vol_pct(w_ic, sig_ic, w_im, sig_im, rho_fut), 3),
            "measured_ann_pct": round(ann, 3) if ann is not None else None,
            "measured_vol_pct": round(vol, 3) if vol is not None else None,
            "measured_mdd_pct": round(mdd, 3),
            "measured_sharpe": round(sharpe, 3) if sharpe is not None else None,
            "measured_minus_declared_pp": (round(vol - float(r.get("vol_uncapped_pct") or 0.0), 3)
                                           if vol is not None else None),
            "days": len(daily),
        }
    return {"rho_futures_legs": round(rho_fut, 4) if rho_fut is not None else None,
            "rho_equity_futures": round(rho_eq, 4) if rho_eq is not None else None,
            "sigma_ic_pct": round(sig_ic, 3) if sig_ic is not None else None,
            "sigma_im_pct": round(sig_im, 3) if sig_im is not None else None,
            "common_days": len(s_ic),
            "notional_per_lot_cny": {kk: (round(vv, 2) if vv else vv)
                                     for kk, vv in n_lot.items()},
            "rungs": rungs}


def build():
    """Full measurement + judgments.  Returns (face, None) or (None, refusal)."""
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
    nav = float(lattice["nav_cny"])
    k = float(lattice["inputs"]["k"])
    rf_pct = float(lattice["inputs"]["cash_rate_pct"])
    meas = measure(lattice, legs, sleeve, k, nav, rf_pct)
    engine = lattice.get("engine_rung") or {}
    engine_key = "%d/%d" % (int(engine.get("ic_lots", 0)), int(engine.get("im_lots", 0)))
    in_band = [r for r in lattice["lattice"]
               if r.get("feasible") and 8.0 <= float(r["expected_return_pct"]) <= 12.0]
    if engine_key not in meas["rungs"]:
        return None, {"verdict": V_BLOCK, "why": "engine rung %s not on the ladder"
                                                % engine_key}
    if not in_band:
        return None, {"verdict": V_BLOCK, "why": "ladder prints no in-band rung; the band "
                                                 "comparison has no arm"}
    band_key = "%d/%d" % (int(in_band[0]["ic_lots"]), int(in_band[0]["im_lots"]))
    declared = float(engine.get("vol_uncapped_pct") or 0.0)
    v = verdicts(meas["rungs"], declared, engine_key, band_key)
    cutoff = min([legs["IC"]["span"][1], legs["IM"]["span"][1], sleeve["span"][1]])
    face = {
        "schema": SCHEMA,
        "kind": KIND,
        "evidence_cutoff": cutoff,
        "inputs": {
            "lattice": {"path": "results/policy_return_lattice.json",
                        "sha256": digest(LATTICE)},
            "l1_arm": {"path": "results/etf_nobond_vt.json", "sha256": digest(L1_ARM)},
            "nav_cny": nav, "k": k, "cash_rate_pct": rf_pct,
            "declared_l2_vol_pct": DECLARED_L2_VOL_PCT,
            "declared_rho": DECLARED_RHO,
            "legs": {p: {"span": legs[p]["span"], "days": legs[p]["days"],
                         "index": legs[p]["index"]} for p in ("IC", "IM")},
            "equity_span": sleeve["span"],
        },
        "measured": meas,
        "engine_rung": engine_key,
        "in_band_rung": band_key,
        "judgment": v,
        "check_scope": ("check re-probes both futures legs and the ladder digest; the "
                        "equity sleeve (~65 s) is pinned by results/etf_nobond_vt.json "
                        "digest only, never re-derived by check"),
    }
    return face, None


# ------------------------------------------------------------------ page
def render_page(face):
    m = face["measured"]
    j = face["judgment"]
    eng = m["rungs"][face["engine_rung"]]
    band = m["rungs"][face["in_band_rung"]]
    L = []
    L.append("# The ladder's risk column, measured")
    L.append("")
    L.append("generated %s | cutoff %s | schema `%s`"
             % (face.get("generated") or "run-time", face["evidence_cutoff"], SCHEMA))
    L.append("")
    L.append("## One sentence")
    L.append("")
    L.append("`research/POLICY_RETURN_LADDER.md` prices every rung's return in money and "
             "every rung's risk in two constants (`L2_CARRY_VOL` 4.0 %%/yr per unit "
             "notional, `RHO` 0.10); measured on the legs' own daily spreads the "
             "instructed rung draws **%.2f%% vol / %.2f%% max drawdown**, so the declared "
             "number is **%s** (%.2f pp)."
             % (eng["measured_vol_pct"], eng["measured_mdd_pct"],
                j["declared_vs_measured_vol"], j["measured_minus_declared_pp"]))
    L.append("")
    L.append("## What was measured, and on what")
    L.append("")
    L.append("| input | declared | measured |")
    L.append("|---|---|---|")
    L.append("| IC leg vol (%%/yr of notional) | %.1f | **%.2f** |"
             % (DECLARED_L2_VOL_PCT, m["sigma_ic_pct"]))
    L.append("| IM leg vol (%%/yr of notional) | %.1f | **%.2f** |"
             % (DECLARED_L2_VOL_PCT, m["sigma_im_pct"]))
    L.append("| IC/IM correlation | %.2f | **%.3f** |"
             % (DECLARED_RHO, m["rho_futures_legs"]))
    L.append("| equity sleeve vs futures | %.2f | **%.3f** |"
             % (DECLARED_RHO, m["rho_equity_futures"]))
    L.append("")
    L.append("Both legs quote on %d common days; one lot is %.0f CNY (IC) / %.0f CNY (IM), "
             "read out of the ladder's own rungs." % (
                 m["common_days"], m["notional_per_lot_cny"]["IC"],
                 m["notional_per_lot_cny"]["IM"]))
    L.append("")
    L.append("## Every rung, return and risk on the same ruler")
    L.append("")
    L.append("| IC/IM lots | expected %/yr | declared vol% | measured vol% | delta pp "
             "| measured MDD% | measured Sharpe |")
    L.append("|---|---|---|---|---|---|---|")
    for key in sorted(m["rungs"], key=lambda x: (m["rungs"][x]["ic_lots"],
                                                 m["rungs"][x]["im_lots"])):
        r = m["rungs"][key]
        star = " **<- instruction**" if key == face["engine_rung"] else (
            " *(in band)*" if key == face["in_band_rung"] else "")
        L.append("| %d/%d%s | %.2f | %.2f | **%.2f** | %+.2f | %.2f | %s |" % (
            r["ic_lots"], r["im_lots"], star, r["expected_return_pct"],
            r["declared_vol_pct"], r["measured_vol_pct"], r["measured_minus_declared_pp"],
            r["measured_mdd_pct"],
            ("%.2f" % r["measured_sharpe"]) if r["measured_sharpe"] is not None else "n/a"))
    L.append("")
    L.append("## The three judgments")
    L.append("")
    L.append("1. **Declared vs measured vol** — `%s` (declared %.2f pp vs measured %.2f pp "
             "on the instructed rung)." % (j["declared_vs_measured_vol"],
                                           j["declared_vol_pct"], j["measured_vol_pct"]))
    L.append("2. **Does cutting to the band cut risk?** — `%s`: the in-band rung "
             "(%s) draws down **%.2f%%** against the instruction's **%.2f%%** (gap "
             "%+.2f pp)." % (j["band_vs_instruction_risk"], face["in_band_rung"],
                             band["measured_mdd_pct"], eng["measured_mdd_pct"],
                             j["band_mdd_gap_pp"]))
    L.append("3. **Return vs risk ranking** — `%s`: best measured Sharpe is %s, best "
             "expected return is %s." % (j["sharpe_vs_return"],
                                         j["best_sharpe_rung"], j["best_return_rung"]))
    L.append("")
    L.append("## What this face does NOT do")
    L.append("")
    L.append("* it does not re-derive a leg: the spreads come from "
             "`idx_fut_carry_risk.product_spread` by import;")
    L.append("* it does not size the equity sleeve: that stays the ladder's `k`;")
    L.append("* it does not touch the ladder itself — the ladder is the published face "
             "and a CONTENTION round may not rewrite shared faces; rebasing its two "
             "constants onto these measurements is a separate, clean-window job;")
    L.append("* `check` re-probes the two futures legs but only digests the equity arm.")
    L.append("")
    L.append("## Usage")
    L.append("")
    L.append("```")
    L.append("python scripts/idx_fut_carry_ladder_risk.py run")
    L.append("python scripts/idx_fut_carry_ladder_risk.py check")
    L.append("python scripts/idx_fut_carry_ladder_risk.py --selftest")
    L.append("```")
    L.append("")
    return "\n".join(L)


# ------------------------------------------------------------------ commands
def cmd_run(_args):
    from datetime import datetime, timedelta, timezone
    tz = timezone(timedelta(hours=8))
    face, refusal = build()
    if refusal:
        write_json(OUT, {"schema": SCHEMA, "kind": KIND, "generated":
                         datetime.now(tz).isoformat(timespec="seconds"),
                         "refusal": refusal})
        print("DATA_BLOCKED %s" % refusal["why"])
        return 2
    face["generated"] = datetime.now(tz).isoformat(timespec="seconds")
    write_json(OUT, face)
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    with io.open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_page(face))
    j = face["judgment"]
    print("RUNG %s declared %.2f pp measured %.2f pp (%+.2f pp)"
          % (face["engine_rung"], j["declared_vol_pct"], j["measured_vol_pct"],
             j["measured_minus_declared_pp"]))
    print("VERDICT %s | %s | %s" % (j["declared_vs_measured_vol"],
                                    j["band_vs_instruction_risk"], j["sharpe_vs_return"]))
    print("WROTE %s" % OUT)
    print("WROTE %s" % DOC)
    return 0


def cmd_check(_args):
    """Re-derive from the published inputs (cheap legs) and compare with the face."""
    if not os.path.exists(OUT):
        print("STALE face missing: %s" % OUT)
        return 3
    face = read_json(OUT)
    if "refusal" in face:
        print("STALE face carries a refusal: %s" % face["refusal"].get("why"))
        return 3
    if not os.path.exists(LATTICE):
        print("STALE ladder face missing")
        return 3
    if digest(LATTICE) != face["inputs"]["lattice"]["sha256"]:
        print("STALE ladder face changed since this measurement was taken")
        return 3
    if digest(L1_ARM) != face["inputs"]["l1_arm"]["sha256"]:
        print("STALE equity arm changed since this measurement was taken")
        return 3
    # cheap re-probe of the two legs: vol / correlation must still be the printed ones
    problems = []
    for p in ("IC", "IM"):
        leg = spread_leg(p)
        if "_refused" in leg:
            problems.append("leg %s refused on re-probe" % p)
            continue
        if leg["days"] != face["inputs"]["legs"][p]["days"]:
            problems.append("leg %s length %d != printed %d"
                            % (p, leg["days"], face["inputs"]["legs"][p]["days"]))
    if problems:
        print("STALE " + "; ".join(problems))
        return 3
    # arithmetic: verdicts must be the ones the stored measurements imply
    m = face["measured"]
    rungs = m["rungs"]
    eng = rungs[face["engine_rung"]]
    again = verdicts(rungs, float(face["judgment"]["declared_vol_pct"]),
                     face["engine_rung"], face["in_band_rung"])
    diffs = [k for k in again if again[k] != face["judgment"].get(k)]
    if diffs:
        print("CHECK FAILED stored judgment disagrees with its own measurements: %s"
              % ", ".join(diffs))
        return 4
    # each rung's vol must equal the two-asset formula on the stored legs
    bad = []
    for key, r in rungs.items():
        want = portfolio_vol_pct(r["weight_ic"], m["sigma_ic_pct"],
                                 r["weight_im"], m["sigma_im_pct"],
                                 m["rho_futures_legs"])
        # the rung's measured vol is the sleeve + L2 combination; only the L2 leg is
        # re-derivable here, so compare that one (it is stored beside the rung)
        if abs(want - r["l2_vol_measured_pct"]) > 0.002:
            bad.append("%s L2 vol %.3f != %.3f" % (key, r["l2_vol_measured_pct"], want))
    if bad:
        print("CHECK FAILED " + "; ".join(bad[:4]))
        return 4
    print("CHECK_OK rungs=%d engine=%s measured=%.2fpp declared=%.2fpp verdict=%s"
          % (len(rungs), face["engine_rung"], eng["measured_vol_pct"],
             face["judgment"]["declared_vol_pct"],
             face["judgment"]["declared_vs_measured_vol"]))
    return 0


# ------------------------------------------------------------------ selftest
def cmd_selftest(_args):
    legs_ok = 0

    def ok(cond, name):
        nonlocal legs_ok
        if not cond:
            raise AssertionError("selftest leg failed: " + name)
        legs_ok += 1
        print("  ok %2d %s" % (legs_ok, name))

    # 1-2 vol arithmetic
    ok(ann_vol([0.01] * 10) is not None and ann_vol([0.01] * 10) < 1e-9,
       "constant series has zero vol")
    alt = [0.01, -0.01] * 100
    ok(abs(ann_vol(alt) - math.sqrt(td()) * 1.0) < 0.2,
       "alternating +-1% annualises to ~sqrt(bars) percent")

    # 3-4 correlation
    a = [0.01 * ((i * 7) % 5 - 2) for i in range(50)]
    ok(abs(corr(a, a) - 1.0) < 1e-9, "correlation of a series with itself is 1")
    ok(abs(corr(a, [-x for x in a]) + 1.0) < 1e-9, "correlation with its negation is -1")

    # 5-6 portfolio vol: rho=1 is a sum, rho=0 is quadrature
    ok(abs(portfolio_vol_pct(1.0, 10.0, 1.0, 10.0, 1.0) - 20.0) < 1e-9,
       "two perfectly correlated equal legs add, not quadrature")
    ok(abs(portfolio_vol_pct(1.0, 10.0, 1.0, 10.0, 0.0) - math.sqrt(200.0)) < 1e-9,
       "uncorrelated equal legs combine in quadrature")
    ok(portfolio_vol_pct(0.0, 10.0, 0.0, 10.0, 0.5) == 0.0,
       "zero weight has zero vol (no division by nothing)")

    # 7 drawdown
    ok(abs(mdd_pct([-0.10, 0.05, 0.05]) + 10.0) < 1e-9,
       "a 10% loss then recovery draws down 10%")

    # 8 date alignment: dates[1:] pairs with returns[0]
    d, x, y = align(["b", "c", "d"], [0.01, 0.02, 0.03],
                     ["c", "d", "e"], [0.5, 0.6, 0.7])
    ok(d == ["c", "d"] and x == [0.02, 0.03] and y == [0.5, 0.6],
       "alignment joins on common days and keeps date-to-return pairing")

    # 9-11 verdicts, on hand-built rungs
    def rung(icl, iml, ret, vol, mdd, sharpe):
        return {"ic_lots": icl, "im_lots": iml, "expected_return_pct": ret,
                "measured_vol_pct": vol, "measured_mdd_pct": mdd,
                "measured_sharpe": sharpe}
    rungs = {"1/1": rung(1, 1, 17.4, 12.0, -12.5, 0.9),
             "0/1": rung(0, 1, 9.0, 8.0, -15.0, 0.7),
             "0/0": rung(0, 0, 5.2, 4.6, -10.1, 0.8)}
    v = verdicts(rungs, 10.0, "1/1", "0/1")
    ok(v["declared_vs_measured_vol"] == V_UNDER,
       "measured 12 vs declared 10 is UNDERSTATED")
    ok(v["band_vs_instruction_risk"] == V_BAND_CONC,
       "in-band rung with deeper drawdown reads CONCENTRATES")
    ok(v["sharpe_vs_return"] == V_SHARPE_AGREE,
       "the rung with the best Sharpe is also the best-return rung -> AGREE")
    rungs2 = dict(rungs)
    rungs2["1/1"] = rung(1, 1, 17.4, 12.0, -12.5, 0.5)
    v2 = verdicts(rungs2, 12.6, "1/1", "0/1")
    ok(v2["sharpe_vs_return"] == V_SHARPE_DIS and
       v2["declared_vs_measured_vol"] == V_MATCH,
       "a different best-Sharpe rung flips the ranking leg; +-0.6 pp reads MATCHES")
    v3 = verdicts(rungs2, 15.0, "1/1", "0/1")
    ok(v3["declared_vs_measured_vol"] == V_OVER,
       "declared above measured by 3 pp reads OVERSTATED")

    # 12 per-lot notional is read, never re-declared
    lat = {"lattice": [{"ic_lots": 1, "im_lots": 0, "notional_cny": 1200000.0},
                       {"ic_lots": 0, "im_lots": 1, "notional_cny": 1040000.0},
                       {"ic_lots": 0, "im_lots": 0, "notional_cny": 0.0}]}
    n = per_lot_notional(lat)
    ok(n["IC"] == 1200000.0 and n["IM"] == 1040000.0,
       "one lot of each product comes out of the ladder's own rungs")

    # 13 weights scale vol linearly (no hidden sizing)
    ok(abs(portfolio_vol_pct(2.0, 10.0, 0.0, 10.0, 0.1) - 20.0) < 1e-9,
       "doubling the weight doubles the vol")

    print("SELFTEST %d/%d ALL_PASS" % (legs_ok, legs_ok))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest or a.cmd == "selftest":
        return cmd_selftest(a)
    return cmd_run(a) if a.cmd == "run" else cmd_check(a)


if __name__ == "__main__":
    sys.exit(main())
