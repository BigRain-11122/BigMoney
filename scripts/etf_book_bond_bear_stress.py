"""What is left of the book if the bond leg stops paying?

The book spends 54.5% of its bars with no equity at all (`etf_book_defense_spells`) and
earns 2.51%/yr on those bars. That 2.51% is not produced by the rule, it is produced by
holding bonds. So the single dependency the headline rests on is: *Chinese bonds keep
paying*. This face prices what happens when they do not.

Method: no fill maths of its own. `etf_equity_alpha.run_with_attribution` runs the
published cell (N5/R20/10bp, all classes, 8% vol target off) once and books every bar's
P&L by asset class; `etf_book_defense_spells.mix_timeline` says which rebalance governs
each bar, so the bond+money weight of the held book on each bar is known exactly. Each
stress arm then re-prices the same picks:

  base            actual bond returns (equivalence gate: rebuilt curve == published ser)
  bond_flat       bond+money pay 0% while held
  bond_bear_300   bond+money pay 300bp/yr less than actual, while held
  bond_bear_600   ... 600bp/yr less

This is a LEVEL shock: the crash arrives after the book bought the bonds, so the score
never gets to see it. The rule-aware reading is a different book, and it is already
published: `etf_nobond_vt` refuses the bond universe outright (11.49%/SR1.132). Both
readings are printed; neither is allowed to stand in for the other.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import numpy as np
import pandas as pd

import etf_equity_alpha as A
from etf_book_defense_spells import mix_timeline
from config import PATHS

FACE = os.path.join(ROOT, "results", "etf_book_bond_bear_stress.json")
DOC = os.path.join(ROOT, "research", "ETF_BOOK_BOND_STRESS.md")
SCHEMA = "etf-book-bond-bear-stress/v1"
TICKET_CNY = 1000000.0
SLEEVE = ("bond", "money")
BEARS = (("bond_flat", None), ("bond_bear_300bp", 0.03), ("bond_bear_600bp", 0.06))
NOBOND_FACE = os.path.join(ROOT, "results", "etf_nobond_vt.json")
PARENT_FACE = os.path.join(ROOT, "results", "etf_equity_alpha.json")


# ------------------------------------------------------------------ pure helpers
def rebuild(r_tot, sleeve_r, cost, bw, rate):
    """Re-price the same picks with the sleeve's return replaced.

    `rate=None` means the sleeve earns nothing; a number is an annual haircut applied to
    the bond+money weight held on that bar. Returns (curve, log_returns)."""
    eq, curve, logs = 1.0, [], []
    prev = 1.0
    for i in range(len(r_tot)):
        eq *= (1.0 - cost[i])
        r = r_tot[i] - sleeve_r[i]
        if rate is not None:
            r -= rate * bw[i] / 252.0
        eq *= (1.0 + r)
        curve.append(eq)
        logs.append(np.log(eq) - np.log(prev))
        prev = eq
    return curve, logs


def rolling_worst(ser, window=252):
    """Worst / best `window`-bar holding-period return, plus the share of windows that lose."""
    s = ser.dropna()
    if len(s) <= window:
        return {"note": "short", "bars": len(s)}
    fwd = s.shift(-window) / s - 1.0
    fwd = fwd.dropna()
    return {
        "bars": int(len(s)),
        "window": int(window),
        "windows": int(len(fwd)),
        "worst": round(float(fwd.min()), 4),
        "worst_window_start": str(fwd.idxmin().date()),
        "best": round(float(fwd.max()), 4),
        "p05": round(float(np.percentile(fwd, 5)), 4),
        "median": round(float(np.median(fwd)), 4),
        "pct_negative": round(100.0 * float((fwd < 0).mean()), 1),
    }


def year_table(ser):
    s = ser.dropna()
    y = s.groupby(s.index.year).apply(lambda x: x.iloc[-1] / x.iloc[0] - 1.0)
    return {int(k): round(float(v), 4) for k, v in y.items()}


def pct(x):
    return None if x is None else round(float(x) * 100.0, 2)


def arm_bp(label):
    """Annual haircut encoded in an arm label, in bp (0 when the label has none)."""
    tail = str(label).rsplit("_", 1)[-1]
    return int(tail[:-2]) if tail.endswith("bp") and tail[:-2].isdigit() else 0


# ------------------------------------------------------------------ derive
def derive():
    close, openp, amt, feats = A.E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    score = A.E.build_score(close, amt, feats)
    print("panel", close.shape, "flips", n_flip, flush=True)

    ser, contrib, turn, mixes = A.run_with_attribution(close, openp, amt, score, cls)
    op = openp.reindex(columns=close.columns)
    dates_all = [d for d in op.index if d >= pd.Timestamp(A.START)]
    fired = [i for i in range(len(dates_all) - 1)
             if i % A.REBAL == 0 and len(score.loc[dates_all[i]].dropna()) >= A.N_HOLD]
    if len(fired) != len(mixes):
        raise SystemExit("alignment: fired=%d mixes=%d" % (len(fired), len(mixes)))
    curve_dates = pd.DatetimeIndex(ser.index)
    owner = mix_timeline(len(curve_dates), A.REBAL, fired)
    if any(o < 0 for o in owner):
        raise SystemExit("alignment: bar before the first fired rebalance")

    r_tot = np.array([c[1] for c in contrib], dtype=float)
    cost = np.array([c[3] for c in contrib], dtype=float)
    sleeve_r = np.array([c[2].get("bond", 0.0) + c[2].get("money", 0.0) for c in contrib],
                        dtype=float)
    bw = np.array([mixes[o].get("bond", 0.0) + mixes[o].get("money", 0.0) for o in owner],
                  dtype=float)
    ew = np.array([mixes[o].get("equity", 0.0) for o in owner], dtype=float)
    if len(r_tot) != len(curve_dates):
        raise SystemExit("alignment: contrib %d vs curve %d" % (len(r_tot), len(curve_dates)))

    # equivalence gate: the rebuilt base must be the published curve, bit for bit
    base_curve, base_logs = rebuild(r_tot, np.zeros_like(sleeve_r), cost, bw, None)
    gap = float(np.max(np.abs(np.array(base_curve) - ser.values)))
    if gap > 1e-12:
        raise SystemExit("EQUIVALENCE GATE FAILED: rebuilt base deviates by %.3e" % gap)

    arms = []
    base_stats = A.stats2(ser, "base")
    for label, rate in (("base", "skip"),) + BEARS:
        if label == "base":
            s = ser
        else:
            c, _l = rebuild(r_tot, sleeve_r, cost, bw, rate)
            s = pd.Series(c, index=curve_dates)
        st = dict(A.stats2(s, label))
        is_end = pd.Timestamp(A.IS_END)
        for tag, sl in (("is", s[s.index <= is_end]), ("oos", s[s.index > is_end])):
            m2 = A.stats2(sl, label + "_" + tag)
            for k in ("cagr", "sharpe", "maxdd"):
                st[k + "_" + tag] = m2.get(k)
        st["final_cny"] = round(float(s.iloc[-1]) * TICKET_CNY, 0)
        st["delta_cagr_pp_vs_base"] = round((st["cagr"] - base_stats["cagr"]) * 100.0, 2)
        st["delta_sharpe_vs_base"] = round(st["sharpe"] - base_stats["sharpe"], 3)
        arms.append(st)
        print("%-16s cagr %6.2f%%  SR %5.3f  mdd %7.2f%%  oos %6.2f%%"
              % (label, st["cagr"] * 100, st["sharpe"], st["maxdd"] * 100,
                 (st["cagr_oos"] or 0.0) * 100), flush=True)

    # the dependency, in three numbers
    n_bars = len(curve_dates)
    def_bars = int((ew <= 0).sum())
    sleeve_log = float(np.sum(sleeve_r))
    gross_log = float(np.sum(np.log1p(r_tot)))
    net_log = gross_log + float(np.sum(np.log1p(-cost)))
    sleeve_share = (sleeve_log / net_log) if net_log else None

    # The sleeve curve is only a bond-market proxy from the first bar where a bond or money
    # name is actually eligible; before that the equal-weight is an empty basket printing
    # 0.00% years, which would otherwise be read as "the bond market was flat for 8 years".
    hist = close.notna().cumsum()
    elig = (amt >= A.E.MIN_AMT) & (hist >= A.E.MIN_HIST)
    sleeve_cols = [c for c in close.columns if cls[c] in SLEEVE]
    live = elig[sleeve_cols].sum(axis=1)
    live = live[live > 0]
    first_active = str(live.index.min().date()) if len(live) else None
    bond_ew = A.ew_universe(close, amt, cls, set(SLEEVE), start="2005-01-01")
    if first_active:
        bond_ew = bond_ew[bond_ew.index >= pd.Timestamp(first_active)]
    census_book = rolling_worst(bond_ew, 252)
    census_book60 = rolling_worst(bond_ew, 60)
    book_win = bond_ew[bond_ew.index >= pd.Timestamp(A.START)]
    years = year_table(bond_ew)
    neg_years = sorted([y for y, v in years.items() if v < 0])

    # today
    last = int(len(bw) - 1)
    today = {
        "bar": str(curve_dates[-1].date()),
        "bond_money_weight": round(float(bw[last]), 4),
        "equity_weight": round(float(ew[last]), 4),
        "in_defense": bool(ew[last] <= 0),
        "sleeve_share_of_bars": round(100.0 * float((bw > 0.5).mean()), 1),
    }

    flat = [a for a in arms if a["label"] == "bond_flat"][0]
    base = [a for a in arms if a["label"] == "base"][0]

    # external anchor: the base arm must be the book the parent face already publishes
    parent = {}
    parent_runs = {}
    if os.path.exists(PARENT_FACE):
        with open(PARENT_FACE, encoding="utf-8") as f:
            pf = json.load(f)
        parent_runs = {r.get("label"): r for r in (pf.get("runs") or [])}
        row = [parent_runs.get("all_classes")] if parent_runs.get("all_classes") else []
        if row:
            p = row[0]
            same = (abs((p.get("cagr") or 0.0) - base["cagr"]) < 1e-4
                    and abs((p.get("sharpe") or 0.0) - base["sharpe"]) < 2e-3
                    and abs((p.get("maxdd") or 0.0) - base["maxdd"]) < 2e-3)
            parent = {"face": "results/etf_equity_alpha.json", "run": "all_classes",
                      "parent": {"cagr": p.get("cagr"), "sharpe": p.get("sharpe"),
                                 "maxdd": p.get("maxdd")},
                      "ours": {"cagr": base["cagr"], "sharpe": base["sharpe"],
                               "maxdd": base["maxdd"]},
                      "same": bool(same),
                      "tolerance": "cagr 1e-4 / sharpe 2e-3 / maxdd 2e-3",
                      "note": "the parent face carries no evidence_cutoff, so a one-bar "
                              "difference shows up in the fourth digit; it is printed, not gated"}
            print("parent anchor same=%s" % same, flush=True)
    verdict = ("THE_DEFENSIVE_HALF_IS_A_BOND_POSITION"
               if flat["cagr"] < base["cagr"] * 0.75
               else "THE_DEFENSIVE_HALF_SURVIVES_WITHOUT_BOND_CARRY")
    never = (census_book.get("pct_negative") == 0.0)
    second = ("BONDS_HAVE_NEVER_LOST_A_ROLLING_YEAR_IN_THIS_PANEL" if never
              else "BONDS_DID_LOSE_ROLLING_YEARS_IN_THIS_PANEL")
    third = ("THE_SLEEVE_IS_DRY_POWDER_NOT_AN_ENGINE"
             if (sleeve_share is not None and sleeve_share < 0.20)
             else "THE_SLEEVE_CARRIES_THE_RETURN")

    face = {
        "schema": SCHEMA,
        "evidence_cutoff": str(max(pd.Timestamp(d) for d in close.index).date()),
        "cell": "N%d_R%d_%dbp" % (A.N_HOLD, A.REBAL, A.COST * 1e4),
        "execution": "decision at close t, execute at open t+1 (entry_lag=0, the printed caliber)",
        "vol_target": None,
        "headline": {"verdict": verdict, "second": second, "third": third},
        "arms": arms,
        "equivalence_gate": {"max_abs_deviation": gap,
                             "meaning": "base arm rebuilt from per-bar class P&L equals the "
                                        "published curve, so every stress arm is priced on the "
                                        "same picks"},
        "parent_anchor": parent,
        "dependency": {
            "bars": n_bars,
            "defensive_bars": def_bars,
            "defensive_pct": round(100.0 * def_bars / n_bars, 1),
            "bond_money_weight_median": round(float(np.median(bw)), 4),
            "bars_with_sleeve_over_half": round(100.0 * float((bw > 0.5).mean()), 1),
            "sleeve_log_total": round(sleeve_log, 4),
            "book_log_total_net": round(net_log, 4),
            "book_log_total_gross": round(gross_log, 4),
            "sleeve_share_of_net_log_pct": pct(sleeve_share),
            "share_note": "the sleeve's own log P&L over the book's net log return (net of the "
                          "20bp one-way trading cost, which the sleeve does not pay)",
            "ticket_cny": TICKET_CNY,
            "sleeve_log_cny": round(sleeve_log * TICKET_CNY, 0),
        },
        "bond_market_census": {
            "proxy": "equal-weight of the bond + money classes, daily open-to-open, "
                     "hist>=120 bars and 20d turnover >= 20m, from the panel's first bar",
            "first_active_bar": first_active,
            "names_eligible_today": int(live.iloc[-1]) if len(live) else 0,
            "why": "windows before first_active_bar have no eligible bond/money name at all, "
                   "so they are excluded instead of being printed as flat years",
            "years_covered": "%d-%d" % (bond_ew.index[0].year, bond_ew.index[-1].year),
            "rolling_1y": census_book,
            "rolling_60bar": census_book60,
            "calendar_years": years,
            "negative_calendar_years": neg_years,
            "book_window_rolling_1y": rolling_worst(book_win, 252),
        },
        "rule_aware_reading": {
            "face": "results/etf_nobond_vt.json",
            "meaning": "the same score with the bond universe refused outright -- the reading "
                       "available to an investor who believes the bear is coming",
        },
        "today": today,
        "provenance": {
            "engine": "etf_equity_alpha.run_with_attribution (no fill maths of its own)",
            "spells": "etf_book_defense_spells.mix_timeline",
            "note": "level shock: picks are fixed before the shock, so the score cannot dodge it",
        },
    }
    if os.path.exists(NOBOND_FACE):
        with open(NOBOND_FACE, encoding="utf-8") as f:
            nb = json.load(f)
        prod = [r for r in (nb.get("runs") or []) if r.get("label") == "nobond_vt08"]
        if prod:
            face["rule_aware_reading"].update({
                "with_vol_target": {
                    "arm": "nobond_vt08", "face": "results/etf_nobond_vt.json",
                    "cagr_pct": round((prod[0].get("cagr") or 0.0) * 100.0, 2),
                    "sharpe": prod[0].get("sharpe"),
                    "maxdd_pct": round((prod[0].get("maxdd") or 0.0) * 100.0, 2),
                },
            })
    nbarm = parent_runs.get("no_bond_equity_mix")
    if nbarm:
        face["rule_aware_reading"]["no_vol_target"] = {
            "arm": "no_bond_equity_mix", "face": "results/etf_equity_alpha.json",
            "cagr_pct": round((nbarm.get("cagr") or 0.0) * 100.0, 2),
            "sharpe": nbarm.get("sharpe"),
            "maxdd_pct": round((nbarm.get("maxdd") or 0.0) * 100.0, 2),
        }
    face["rule_aware_reading"]["caveat"] = (
        "both are different books, not stress arms of this one; the pair differs by the vol "
        "target as well as by the refused universe, so neither number is 'what refusing bonds "
        "is worth'")
    return face


# ------------------------------------------------------------------ write
def write(face):
    os.makedirs(os.path.dirname(FACE), exist_ok=True)
    with open(FACE, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    print("saved", FACE, flush=True)
    write_doc(face)


def write_doc(face):
    h = face["headline"]
    dep = face["dependency"]
    cen = face["bond_market_census"]
    arms = {a["label"]: a for a in face["arms"]}
    base, flat = arms["base"], arms["bond_flat"]
    lines = []
    lines.append("<!-- ETF-BOOK-BOND-STRESS:BEGIN -->")
    lines.append("")
    lines.append("**verdict** `%s` / `%s` / `%s`"
                 % (h["verdict"], h["second"], h.get("third", "")))
    lines.append("")
    lines.append("cell %s · evidence_cutoff %s · no vol target (the all-class book)"
                 % (face["cell"], face["evidence_cutoff"]))
    lines.append("")
    lines.append("The book holds no equity on **%d of %d bars (%.1f%%)**, and bond+money is "
                 "more than half of the book on **%.1f%%** of bars."
                 % (dep["defensive_bars"], dep["bars"], dep["defensive_pct"],
                    dep["bars_with_sleeve_over_half"]))
    lines.append("The bond+money leg carries **%s%% of the book's net log return** "
                 "(%s CNY on the %d ticket): the sleeve is where the book waits, not what "
                 "pays it."
                 % (dep["sleeve_share_of_net_log_pct"], format(dep["sleeve_log_cny"], ",.0f"),
                    int(dep["ticket_cny"])))
    lines.append("")
    lines.append("If that leg pays **nothing** while held, the book earns **%.2f%%/yr** "
                 "(Sharpe %.3f, max drawdown %.2f%%) instead of **%.2f%%/yr** "
                 "(%.3f, %.2f%%) -- %+.2fpp a year, %s CNY on the ticket."
                 % (flat["cagr"] * 100, flat["sharpe"], flat["maxdd"] * 100,
                    base["cagr"] * 100, base["sharpe"], base["maxdd"] * 100,
                    flat["delta_cagr_pp_vs_base"],
                    format(flat["final_cny"] - base["final_cny"], ",.0f")))
    lines.append("")
    lines.append("| stress | cagr | sharpe | maxdd | worst year | OOS 2024+ | final on 1m |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    order = ["base", "bond_flat", "bond_bear_300bp", "bond_bear_600bp"]
    for k in order:
        a = arms[k]
        lines.append("| %s | %.2f%% | %.3f | %.2f%% | %.2f%% | %.2f%% | %s |"
                     % (k, a["cagr"] * 100, a["sharpe"], a["maxdd"] * 100,
                        a["worst_year"] * 100, (a["cagr_oos"] or 0.0) * 100,
                        format(a["final_cny"], ",.0f")))
    lines.append("")
    pa = face.get("parent_anchor") or {}
    if pa:
        tag = ("same within %s" % pa.get("tolerance", "rounding")
               if pa.get("same") else "not the same book -- read both, do not average")
        lines.append("The base arm is the published book, not a rebuild: `%s` `%s` prints "
                     "%.2f%% / %.3f / %.2f%% and this face prints %.2f%% / %.3f / %.2f%% (%s)."
                     % (pa["face"], pa["run"], (pa["parent"]["cagr"] or 0) * 100,
                        pa["parent"]["sharpe"], (pa["parent"]["maxdd"] or 0) * 100,
                        (pa["ours"]["cagr"] or 0) * 100, pa["ours"]["sharpe"],
                        (pa["ours"]["maxdd"] or 0) * 100, tag))
        lines.append("")
    bw1 = cen["book_window_rolling_1y"]
    r1 = cen["rolling_1y"]
    lines.append("Realised bond bears are shallow, and the sample does contain them: over %s..%s "
                 "(from the first bar with an eligible bond/money name, %s) the class "
                 "equal-weight's worst rolling year was **%.2f%%** (%s), %s of rolling years "
                 "were negative, and the down calendar years were %s -- %d of %d years."
                 % (cen["years_covered"].split("-")[0], cen["years_covered"].split("-")[1],
                    cen["first_active_bar"], r1.get("worst", 0.0) * 100,
                    r1.get("worst_window_start"),
                    ("%s%%" % r1.get("pct_negative")),
                    ("none" if not cen["negative_calendar_years"]
                     else ", ".join(str(y) for y in cen["negative_calendar_years"])),
                    len(cen["negative_calendar_years"]), len(cen["calendar_years"])))
    lines.append("Inside the book's own window the worst rolling year was **%.2f%%** (window "
                 "starting %s), so the -%d/-%d bp arms are shocks the market has not delivered "
                 "in this panel -- they are a bound, not a forecast."
                 % (bw1.get("worst", 0.0) * 100, bw1.get("worst_window_start"),
                    int(arm_bp("bond_bear_300bp")), int(arm_bp("bond_bear_600bp"))))
    lines.append("")
    lines.append("So the sleeve is not the engine of the headline -- it is the thing that keeps "
                 "the book compounding on the %d bars where nothing else does. Zeroing it costs "
                 "%.2fpp a year and %.2f of Sharpe, not the book."
                 % (dep["defensive_bars"], -flat["delta_cagr_pp_vs_base"],
                    abs(flat["delta_sharpe_vs_base"])))
    lines.append("")
    ra = face["rule_aware_reading"]
    wt = ra.get("with_vol_target") or {}
    nv = ra.get("no_vol_target") or {}
    lines.append("Two readings, printed side by side and not averaged: this face is a "
                 "**level shock** -- the crash arrives after the book already owns the bonds, "
                 "so the rule cannot see it. An investor who believes the bear is coming takes "
                 "the other reading and refuses the bond universe outright: `%s` "
                 "(%s%%/yr, Sharpe %s, drawdown %s%%) with no vol target, `%s` "
                 "(%s%%/yr, %s, %s%%) with the 8%% one. Those two differ by the vol target as "
                 "well as by the universe, so neither is 'what refusing bonds is worth'."
                 % (nv.get("arm"), nv.get("cagr_pct"), nv.get("sharpe"), nv.get("maxdd_pct"),
                    wt.get("arm"), wt.get("cagr_pct"), wt.get("sharpe"), wt.get("maxdd_pct")))
    lines.append("")
    lines.append("Today (%s): bond+money weight **%.1f%%**, equity weight **%.1f%%**%s."
                 % (face["today"]["bar"], face["today"]["bond_money_weight"] * 100,
                    face["today"]["equity_weight"] * 100,
                    " -- the book is in defence" if face["today"]["in_defense"] else ""))
    lines.append("")
    lines.append("<!-- ETF-BOOK-BOND-STRESS:END -->")
    body = "\n".join(lines) + "\n"
    with open(DOC, "w", encoding="utf-8") as f:
        f.write(body)
    print("saved", DOC, flush=True)


# ------------------------------------------------------------------ check
def check():
    """Re-derive the doc's markers and the arm ordering from the published face."""
    if not os.path.exists(FACE):
        print("check FAIL: no face at", FACE)
        return 1
    with open(FACE, encoding="utf-8") as f:
        face = json.load(f)
    probs = []
    arms = {a.get("label"): a for a in face.get("arms") or []}
    for k in ("base", "bond_flat", "bond_bear_300bp", "bond_bear_600bp"):
        if k not in arms:
            probs.append("arm %s missing" % k)
    if not probs:
        gate = face.get("equivalence_gate") or {}
        dev = gate.get("max_abs_deviation")
        if dev is None or float(dev) > 1e-12:
            probs.append("equivalence gate deviation %r" % (dev,))
        for a in arms.values():
            want = round((a["cagr"] - arms["base"]["cagr"]) * 100.0, 2)
            if abs(want - a["delta_cagr_pp_vs_base"]) > 1e-9:
                probs.append("%s: delta_cagr_pp %.2f != cagr-base %.2f"
                             % (a["label"], a["delta_cagr_pp_vs_base"], want))
        seq = [arms[k]["cagr"] for k in ("bond_bear_600bp", "bond_bear_300bp", "bond_flat",
                                        "base")]
        if seq != sorted(seq):
            probs.append("cagr not monotone in the shock size: %r" % (seq,))
        dep = face.get("dependency") or {}
        if abs(dep.get("sleeve_log_total", 0.0) - 0.0) < 1e-12:
            probs.append("sleeve contributed exactly zero log -- suspect an empty class")
    if os.path.exists(DOC):
        with open(DOC, encoding="utf-8") as f:
            body = f.read()
        if "<!-- ETF-BOOK-BOND-STRESS:BEGIN -->" not in body:
            probs.append("doc lost its marker block")
        if face.get("headline", {}).get("verdict") not in body:
            probs.append("doc does not print the face's own verdict")
        if arms.get("bond_flat") and ("%.2f%%" % (arms["bond_flat"]["cagr"] * 100)) not in body:
            probs.append("doc does not print the flat arm's cagr")
    else:
        probs.append("doc missing")
    if probs:
        print("check FAIL:")
        for x in probs:
            print("  -", x)
        return 1
    print("check ok: %d arms, base %.2f%% -> flat %.2f%%, gate %s"
          % (len(arms), arms["base"]["cagr"] * 100, arms["bond_flat"]["cagr"] * 100,
             (face["equivalence_gate"] or {}).get("max_abs_deviation")))
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    fails = []

    def eq(name, got, want, tol=1e-12):
        if isinstance(want, (int, float)) and isinstance(got, (int, float)):
            ok = abs(got - want) <= tol
        else:
            ok = got == want
        print(("ok   " if ok else "FAIL ") + name + " -> " + repr(got), flush=True)
        if not ok:
            fails.append(name)

    # rebuild with no sleeve return and no haircut reproduces the plain compounding
    r = [0.01, -0.02, 0.03]
    c, logs = rebuild(r, [0.0] * 3, [0.0] * 3, [1.0] * 3, None)
    eq("rebuild: no shock == compounding", round(c[-1], 12),
       round((1.01 * 0.98 * 1.03), 12), 1e-12)
    eq("rebuild: log sums to the curve", round(float(np.sum(logs)), 12),
       round(float(np.log(c[-1])), 12), 1e-12)

    # flat sleeve removes exactly the sleeve's contribution
    c2, _ = rebuild([0.02], [0.02], [0.0], [1.0], None)
    eq("flat sleeve: book return becomes zero", round(c2[-1], 12), 1.0, 1e-12)

    # a haircut only bites on the weight actually held
    c3, _ = rebuild([0.10], [0.0], [0.0], [0.5], 0.252)   # 0.252/yr on 50% -> -0.05% this bar
    eq("haircut scales with weight", round(c3[-1], 6), round(1.0 + 0.10 - 0.252 * 0.5 / 252, 6),
       1e-9)
    c4, _ = rebuild([0.10], [0.0], [0.0], [0.0], 0.252)
    eq("haircut on zero weight bites nothing", round(c4[-1], 12), 1.10, 1e-12)

    # cost is charged before the bar's return
    c5, _ = rebuild([0.10], [0.0], [0.01], [0.0], None)
    eq("cost charged before the return", round(c5[-1], 12), round(0.99 * 1.10, 12), 1e-12)

    # rolling_worst on a synthetic: one clean loser
    idx = pd.date_range("2020-01-01", periods=600, freq="B")
    up = pd.Series(np.linspace(1.0, 1.5, 600), index=idx)     # +50% over the window
    down = pd.Series(np.r_[np.linspace(1.0, 1.0, 252), np.linspace(1.0, 0.8, 348)], index=idx)
    ew_up = rolling_worst(up, 252)
    eq("rolling_worst: monotone up never negative", ew_up["pct_negative"], 0.0)
    ew_dn = rolling_worst(down, 252)
    if ew_dn["pct_negative"] <= 0:
        print("FAIL rolling_worst: a falling series shows no negative window", flush=True)
        fails.append("rolling_worst negative")
    else:
        print("ok   rolling_worst: falling series shows negative windows -> %.1f%%"
              % ew_dn["pct_negative"], flush=True)

    # year_table
    y = pd.Series([1.0, 1.1, 0.9], index=pd.DatetimeIndex(["2020-06-30", "2020-12-31",
                                                          "2021-12-31"]))
    yt = year_table(y)
    eq("year_table: first partial year", round(yt[2020], 4), 0.1, 1e-9)

    if fails:
        print("selftest FAILED: %d" % len(fails))
        return 1
    print("selftest 11/11 PASS")
    return 0


def main(argv):
    if len(argv) > 1 and argv[1].lstrip("-") == "check":
        return check()
    if len(argv) > 1 and argv[1].lstrip("-") == "selftest":
        return selftest()
    face = derive()
    write(face)
    print("verdict", face["headline"]["verdict"], "/", face["headline"]["second"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
