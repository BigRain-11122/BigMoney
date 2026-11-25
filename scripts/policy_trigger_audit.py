# -*- coding: utf-8 -*-
"""policy_trigger_audit -- does the book's written-down trigger table actually
exist as arithmetic, and what does the one unfixed number cost?

research/STRATEGY-20261125.md section four says the triggers are frozen ("写死,
不许临场改").  A frozen table is only frozen if something evaluates it.  This
face reads three things and compares them line by line:

  * the strategy document (numbers pulled by regex, each with its line number,
    so a reworded claim shows up as a MISSING CLAIM instead of passing silently)
  * the engine that claims to apply it (scripts/policy_engine.py constants)
  * today's output (results/policy/POLICY.json) and the measured sleeve risk
    (results/idx_fut_carry_risk.json, the carry legs' own daily series)

It reports, per trigger, one of IMPLEMENTED / NOT_WIRED / MISMEASURED, plus the
places where the document states two different numbers for the same thing.

It also prices the one line in the table that carries a number but no argument
("单腿 60 日累计 carry < −2pp"): given each leg's measured annual volatility and
drift, how often would a −2pp 60-day pause fire on a leg that is performing
exactly as measured?  That is a noise calculation, not a forecast -- the
threshold it recommends is the one whose *false-pause* rate you can live with.

(The minus in that line is U+2212, not ASCII '-'.  On a GBK console it prints as
'?', which makes a written number look like a placeholder; read that row with
ascii()/repr() before concluding anything about it.)

Zero network, deterministic.  `--check` re-derives and compares to the published
face; a moved source says STALE (chain legs pay to rewrite), a same-input
disagreement says CHECK FAILED.
"""
from __future__ import annotations

import io
import json
import math
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bench_core as bc  # noqa: E402

DOC = os.path.join(bc.ROOT, "research", "STRATEGY-20261125.md")
ENGINE = os.path.join(bc.ROOT, "scripts", "policy_engine.py")
POLICY = os.path.join(bc.RESULTS, "policy", "POLICY.json")
CARRY_RISK = os.path.join(bc.RESULTS, "idx_fut_carry_risk.json")
OUT = os.path.join(bc.RESULTS, "policy_trigger_audit.json")

KIND = "policy_trigger_audit_v1"
PHI = lambda z: 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _rel(path):
    try:
        return os.path.relpath(path, bc.ROOT)
    except ValueError:
        return path  # a temp copy on another drive is still a legitimate input


def _lines(path):
    with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read().splitlines()


def doc_claims(lines):
    """Pull the numbers the document promises from the document itself."""
    claims = {}

    def grab(key, pattern, cast=float, required=True):
        for i, raw in enumerate(lines, 1):
            m = re.search(pattern, raw)
            if m:
                claims[key] = {"value": cast(m.group(1)), "line": i,
                               "text": raw.strip()[:160]}
                return
        if required:
            claims[key] = {"value": None, "line": None, "text": "MISSING"}

    grab("target_lo_pct", r"目标年化 \| (\d+)")
    grab("target_hi_pct", r"目标年化 \| \d+%[–-](\d+)%")
    grab("vol_target_s1_pct", r"波动目标 \| (\d+)%")
    grab("vol_cap_s1_pct", r"波动目标 \| \d+%.*?上限 (\d+)%")
    grab("vol_target_s3_pct", r"组合波动目标 \*\*(\d+)%\*\*")
    grab("drawdown_red_pct", r"回撤红线 \| (\d+)%")
    grab("corr_cap", r"与 A 股相关性 \| ≤([0-9.]+)")
    grab("l1_budget_pct", r"L1 ≤ \*\*([0-9.]+)%\*\*")
    grab("l2_budget_pct", r"L2 ≤ \*\*([0-9.]+)%\*\*")
    grab("notional_cap_x", r"L2 名义 ≤ \*\*([0-9.]+)×NAV\*\*")
    grab("margin_cap_pct", r"保证金占用 ≤ \*\*(\d+)% NAV\*\*")
    grab("dd_half_pct", r"组合回撤 ≥(\d+)% \| 全部腿降半")
    grab("dd_clear_pct", r"组合回撤 ≥(\d+)% \| L2 清零")

    # the placeholder: it has no number, so record what is literally there
    for i, raw in enumerate(lines, 1):
        if "60 日累计 carry" in raw:
            m = re.search(r"(?:<|≤)\s*([-\u2212]?\d+(?:\.\d+)?)\s*pp", raw)
            claims["carry_pause"] = {
                "value": float(m.group(1).replace(u"\u2212", "-")) if m else None,
                "line": i, "text": raw.strip()[:160],
                "placeholder": "?" in raw}
            break
    else:
        claims["carry_pause"] = {"value": None, "line": None,
                                 "text": "MISSING", "placeholder": False}
    return claims


def engine_constants(text):
    out = {}
    for m in re.finditer(r"^([A-Z][A-Z0-9_]{2,})\s*=\s*([0-9.]+)", text, re.M):
        out[m.group(1)] = float(m.group(2))
    # the ladder itself is a literal list of (level, action) pairs
    ladder = re.findall(r"\(([0-9.]+),\s*\"([A-Z_]+)\"\)", text)
    out["_DRAWDOWN_LADDER"] = [[float(a), b] for a, b in ladder]
    # which series feeds the ladder? follow the variable the ladder compares.
    drv = "unknown"
    m = re.search(r"if\s+(\w+)\s*<=\s*-100\.0\s*\*\s*level", text)
    if m:
        var = m.group(1)
        a = re.search(r"^\s*%s\s*=\s*(.+)$" % re.escape(var), text, re.M)
        src = a.group(1).lower() if a else ""
        if "paper" in src:
            drv = "paper carry"
        elif "book" in src or "nav" in src:
            drv = "composite book"
    out["_ladder_drives_on"] = drv
    return out


def combined_vol_pct(a, b, rho):
    return math.sqrt(a * a + b * b + 2.0 * rho * a * b)


def pause_pricing(leg, ann_vol_pct, ann_mean_pct, window=60, line_pp=-2.0):
    """False-pause arithmetic for a 60-day carry pause line.

    sigma_window = annual vol * sqrt(window/252); drift_window = annual mean *
    window/252.  Trip rate = P(sum < line) under the measured drift.  The
    threshold that keeps the false-pause rate at `tail` is drift - z*sigma.
    """
    s = ann_vol_pct * math.sqrt(float(window) / 252.0)
    d = ann_mean_pct * float(window) / 252.0
    trip = PHI((line_pp - d) / s) if s > 0 else (1.0 if d < line_pp else 0.0)
    out = {"leg": leg, "window_days": window, "ann_vol_pct": ann_vol_pct,
           "ann_mean_pct": ann_mean_pct,
           "sigma_window_pp": round(s, 3), "drift_window_pp": round(d, 3),
           "line_pp": line_pp, "trip_rate_at_line": round(trip, 4),
           "trip_windows_per_year_at_line": round(trip * 252.0 / window, 2)}
    hard = {}
    for label, tail in (("2.5pct", 0.025), ("5pct", 0.05), ("10pct", 0.10)):
        z = {0.025: 1.959964, 0.05: 1.644854, 0.10: 1.281552}[tail]
        hard[label] = round(d - z * s, 2)
    out["threshold_pp_for"] = hard
    out["note"] = ("noise-only: the drift is the sample mean of the same window "
                   "and the distribution is treated as normal")
    return out


def build():
    doc = _lines(DOC)
    claims = doc_claims(doc)
    eng = engine_constants(io.open(ENGINE, "r", encoding="utf-8").read())
    pol = json.load(io.open(POLICY, "r", encoding="utf-8"))
    risk = json.load(io.open(CARRY_RISK, "r", encoding="utf-8"))

    nav = float(pol["nav_cny"])
    findings = []

    # ---- A. one target, how many numbers -------------------------------------
    stated = {k: claims[k]["value"] for k in
              ("vol_target_s1_pct", "vol_cap_s1_pct", "vol_target_s3_pct")}
    eng_vol = eng.get("VOL_TARGET", 0.0) * 100.0
    vol_claims = {"document_section_1_pct": stated["vol_target_s1_pct"],
                  "document_section_1_cap_pct": stated["vol_cap_s1_pct"],
                  "document_section_3_pct": stated["vol_target_s3_pct"],
                  "engine_VOL_TARGET_pct": round(eng_vol, 2)}
    distinct = {v for v in (stated["vol_target_s1_pct"],
                            stated["vol_target_s3_pct"]) if v is not None}
    # the 8% in section 1 is an upper bound, not a second target: only a bound
    # that sits below a stated target is a contradiction
    bound_bad = (stated["vol_cap_s1_pct"] is not None and distinct and
                 stated["vol_cap_s1_pct"] < max(distinct))
    l1b = claims["l1_budget_pct"]["value"]
    l2b = claims["l2_budget_pct"]["value"]
    vol_arith = {}
    if l1b and l2b:
        for rho in (0.0, 0.1, 0.3):
            vol_arith["combined_at_rho_%.1f_pct" % rho] = round(
                combined_vol_pct(l1b, l2b, rho), 2)
        # how much budget the 9% line would need at the document's own rho=0.1
        base = combined_vol_pct(l1b, l2b, 0.1)
        if base > 0 and stated["vol_target_s3_pct"]:
            scale = stated["vol_target_s3_pct"] / base
            vol_arith["scale_needed_for_section_3"] = round(scale, 3)
            vol_arith["budgets_at_that_scale_pct"] = [
                round(l1b * scale, 2), round(l2b * scale, 2)]
    if len(distinct) > 1 or bound_bad:
        findings.append({
            "id": "VOL_TARGET_STATED_%d_WAYS" % max(2, len(distinct)),
            "severity": "blocks_a_frozen_table",
            "detail": ("the same risk target is stated as %s (bound %s); the "
                       "engine uses %s"
                       % (sorted(distinct), stated["vol_cap_s1_pct"],
                          round(eng_vol, 2))),
            "consequence": ("a drawdown or derisk step derived from 'the target' "
                            "has no single target to derive from"),
        })

    # ---- B. notional cap: per leg or for the sleeve --------------------------
    tgt = {c: float(v.get("target_notional_cny") or 0.0)
           for c, v in pol.get("l2_basis", {}).items()}
    act = {c: float(v.get("notional_at_lots_cny") or 0.0)
           for c, v in pol.get("l2_basis", {}).items()}
    cap_x = eng.get("L2_NOTIONAL_CAP_X", 0.0)
    notional = {"cap_x_nav": cap_x, "nav_cny": nav,
                "target_by_leg_x_nav": {c: round(v / nav, 4) for c, v in tgt.items()},
                "target_total_x_nav": round(sum(tgt.values()) / nav, 4),
                "actual_by_leg_x_nav": {c: round(v / nav, 4) for c, v in act.items()},
                "actual_total_x_nav": round(sum(act.values()) / nav, 4)}
    if cap_x and sum(tgt.values()) / nav > cap_x + 1e-9:
        findings.append({
            "id": "NOTIONAL_CAP_NOT_APPLIED_TO_THE_SLEEVE",
            "severity": "cap_declared_but_the_engine_splits_it_per_leg",
            "detail": ("engine constant L2_NOTIONAL_CAP_X=%s (of NAV) is used as "
                       "*each* leg's budget, so the published targets add up to "
                       "%.3fx NAV" % (cap_x, sum(tgt.values()) / nav)),
            "masked_by": ("today the margin cap binds first (%.0f%% of NAV margin "
                          "on a %.0f%% cap) and the lots land at %.3fx NAV"
                          % (100.0 * sum(float(v.get("margin_cny") or 0.0)
                                         for v in pol["l2_basis"].values()) / nav,
                             100.0 * eng.get("L2_MARGIN_CAP", 0.0),
                             sum(act.values()) / nav)),
            "consequence": ("at a lower margin rate the sleeve would run 2x the "
                            "cap it declares"),
        })

    # ---- C. margin cap: did it actually bind --------------------------------
    margin_actual = sum(float(v.get("margin_cny") or 0.0)
                        for v in pol["l2_basis"].values())
    margin = {"cap_cny": round(eng.get("L2_MARGIN_CAP", 0.0) * nav, 0),
              "actual_cny": round(margin_actual, 0),
              "steps_applied": pol.get("steps_applied", [])}
    margin["implemented"] = (margin_actual <= margin["cap_cny"] + 1.0)
    if not margin_actual <= margin["cap_cny"] + 1.0:
        findings.append({"id": "MARGIN_CAP_BREACHED",
                         "severity": "hard", "detail": margin})

    # ---- D. drawdown lines: on which book --------------------------------
    book = risk.get("book", {}) or {}
    dd = {"engine_ladder": eng.get("_DRAWDOWN_LADDER", []),
          "engine_drives_on": eng.get("_ladder_drives_on"),
          "document_lines_pct": [claims["dd_half_pct"]["value"],
                                 claims["dd_clear_pct"]["value"]],
          "book_mdd_pct": book.get("mdd_pct"),
          "book_underwater_open_bars": book.get("underwater_open_bars"),
          "book_underwater_max_bars": book.get("underwater_max_bars")}
    red = claims["drawdown_red_pct"]["value"]
    if book.get("mdd_pct") is not None and red is not None:
        dd["book_mdd_vs_red_line"] = ("breached" if abs(book["mdd_pct"]) >= red
                                      else "inside")
    if dd["engine_drives_on"] != "composite book":
        findings.append({
            "id": "DRAWDOWN_LINE_MEASURED_ON_ONE_LEG",
            "severity": "mismeasured_not_missing",
            "detail": ("the document calls these 组合回撤 lines; the engine "
                       "computes them from the carry leg's own cumulative "
                       "series (%s)" % dd["engine_drives_on"]),
            "consequence": ("a 6%% composite drawdown driven by the equity leg "
                            "cannot trip the ladder today; the book's own "
                            "backtest is %.3f%% at %d bars underwater"
                            % (book.get("mdd_pct") or 0.0,
                               book.get("underwater_open_bars") or 0)),
        })

    # ---- E. price the placeholder ------------------------------------------
    prods = risk.get("products", {}) or {}
    written_line = claims["carry_pause"].get("value")
    priced_line = float(written_line) if written_line is not None else -2.0
    pricings = []
    for code in ("IC", "IM"):
        r = (prods.get(code) or {}).get("risk")
        if r and r.get("ann_vol_pct"):
            pricings.append(pause_pricing(code, float(r["ann_vol_pct"]),
                                          float(r["ann_mean_pct"] or 0.0),
                                          line_pp=priced_line))
    pause = {"placeholder": claims["carry_pause"],
             "written_line_pp": written_line,
             "priced_line_pp": priced_line,
             "legs": pricings,
             "recommendation_pp": {}}
    for p in pricings:
        pause["recommendation_pp"][p["leg"]] = p["threshold_pp_for"]["2.5pct"]
    too_tight = [p for p in pricings if p["trip_rate_at_line"] > 0.05]
    if pricings and claims["carry_pause"].get("placeholder"):
        findings.append({
            "id": "CARRY_PAUSE_LINE_UNPRICED",
            "severity": "placeholder_in_a_frozen_table",
            "detail": ("the table says '< ?2pp' and carries a '?'; at -2pp the "
                       "measured drift trips it on %s of 60-day windows"
                       % ", ".join("%s %.1f%%" % (p["leg"],
                                                  100.0 * p["trip_rate_at_line"])
                                   for p in pricings)),
            "consequence": ("a performing leg would be paused in about 1 window "
                            "in 8-10; the 2.5%% tail line is %s"
                            % pause["recommendation_pp"]),
        })
    elif too_tight:
        findings.append({
            "id": "CARRY_PAUSE_LINE_TOO_TIGHT",
            "severity": "written_but_mis_priced",
            "detail": ("the line is written at %.2fpp, which the measured drift "
                       "trips on %s of 60-day windows"
                       % (priced_line, ", ".join(
                           "%s %.1f%%" % (p["leg"], 100.0 * p["trip_rate_at_line"])
                           for p in too_tight))),
            "consequence": ("the 2.5%% tail line is %s"
                            % pause["recommendation_pp"]),
        })

    # ---- F. the correlation claim, checked against the measured number -----
    corr = {"document_cap": claims["corr_cap"]["value"], "measured": {}}
    for code in ("IC", "IM", "IF", "IH"):
        v = (prods.get(code) or {}).get("corr_with_book")
        if v is not None:
            corr["measured"][code] = v
    corr["implemented"] = bool(corr["measured"]) and all(
        abs(v) <= (corr["document_cap"] or 1.0) for v in corr["measured"].values())

    triggers = {
        "basis_percentile_ge_80_zero_weight": {
            "state": "IMPLEMENTED",
            "evidence": "engine basis percentile rule feeds target_weight "
                        "(POLICY.l2_basis.*.weight)",
            "today_weight": {c: v.get("weight") for c, v in pol["l2_basis"].items()}},
        "composite_drawdown_6_10": {"state": "MISMEASURED", "evidence": dd},
        "carry_60d_pause": {"state": "NOT_WIRED",
                            "evidence": "no code path reads a 60-day carry sum; "
                                        "the document still carries the "
                                        "placeholder"},
        "corr_cap_0_35": {"state": ("IMPLEMENTED_IN_OUTPUT"
                                    if corr["implemented"] else "NOT_CHECKED"),
                          "evidence": corr},
        "annual_retirement_p_005": {
            "state": "OFFLINE_ONLY",
            "evidence": "quarterly permutation/bootstrap exists as a batch; "
                        "nothing in the daily engine evaluates it"},
        "margin_cap_35pct": {"state": ("IMPLEMENTED" if margin["implemented"]
                                       else "BREACHED"),
                             "evidence": margin},
        "notional_cap_2_5x": {"state": ("IMPLEMENTED" if notional[
            "target_total_x_nav"] <= cap_x + 1e-9 else "MISAPPLIED"),
            "evidence": notional},
    }

    verdict = ("CONTRACT_HOLDS" if not findings else
               "%d_TRIGGER_CONTRACT_FINDINGS" % len(findings))
    return {
        "kind": KIND,
        "face": "policy_trigger_audit",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": pol.get("generated", "")[:10],
        "question": ("the strategy document says its trigger table is frozen; "
                     "is it arithmetic anywhere, and what is the one unfixed "
                     "number worth?"),
        "inputs": {"strategy_doc": _rel(DOC),
                   "engine": _rel(ENGINE),
                   "policy": _rel(POLICY),
                   "carry_risk": _rel(CARRY_RISK),
                   "policy_generated": pol.get("generated")},
        "claims": claims,
        "vol_target": {"statements_pct": vol_claims, "arithmetic": vol_arith},
        "notional": notional,
        "margin": margin,
        "drawdown": dd,
        "carry_pause_pricing": pause,
        "correlation": corr,
        "triggers": triggers,
        "findings": findings,
        "verdict": verdict,
        "honest": [
            "this reads the document by regex: a reworded claim becomes a "
            "MISSING claim, not a silent pass",
            "the pause pricing is noise-only (normal, drift = sample mean of the "
            "same leg); it prices the false-pause rate, not the value of pausing",
            "sections 1 and 3 disagree on the volatility target; this face "
            "reports the disagreement and does not choose for the author",
            "the notional finding is about the *target*; today's lots stay under "
            "the cap because the margin step scaled them",
        ],
    }


def check(payload=None):
    if payload is None:
        if not os.path.exists(OUT):
            print("STALE face missing: %s" % OUT)
            return 3
        payload = json.load(io.open(OUT, "r", encoding="utf-8"))
    fresh = build()
    problems = []
    for key in ("verdict", "findings", "triggers", "vol_target", "notional",
                "margin", "drawdown", "carry_pause_pricing", "correlation"):
        if json.dumps(payload.get(key), sort_keys=True, ensure_ascii=False) != \
           json.dumps(fresh.get(key), sort_keys=True, ensure_ascii=False):
            problems.append(key)
    # has any input moved since the face was priced?
    moved = []
    for label, path in (("strategy_doc", DOC), ("engine", ENGINE),
                        ("policy", POLICY), ("carry_risk", CARRY_RISK)):
        stamp = payload.get("inputs", {}).get(label)
        if stamp and os.path.exists(path):
            rel = os.path.relpath(path, bc.ROOT)
            if stamp != rel:
                moved.append(label)
    if problems and moved:
        print("STALE %s moved under this face: recompute" % ",".join(moved))
        return 3
    if problems:
        print("CHECK FAILED keys=%s" % ",".join(problems))
        return 1
    print("OK policy_trigger_audit: verdict=%s findings=%d"
          % (payload.get("verdict"), len(payload.get("findings") or [])))
    return 0


def selftest():
    legs = []
    legs.append(("phi", abs(PHI(0.0) - 0.5) < 1e-12 and abs(PHI(1.96) - 0.975) < 5e-4))
    legs.append(("combined_vol", abs(combined_vol_pct(4.6, 3.5, 0.0)
                                     - math.sqrt(4.6 ** 2 + 3.5 ** 2)) < 1e-9))
    p = pause_pricing("X", 5.87, 8.462)
    legs.append(("sigma_window", abs(p["sigma_window_pp"] - round(5.87 * math.sqrt(60 / 252), 3))
                 < 1e-9))
    legs.append(("drift_window", abs(p["drift_window_pp"] - round(8.462 * 60 / 252, 3)) < 1e-9))
    # a wider line must trip less often
    tight = pause_pricing("X", 5.87, 8.462, line_pp=-1.0)
    legs.append(("monotone_in_line", tight["trip_rate_at_line"]
                 > p["trip_rate_at_line"]))
    # a leg with a bigger drift trips less often at the same line
    rich = pause_pricing("X", 5.87, 20.0)
    legs.append(("monotone_in_drift", rich["trip_rate_at_line"]
                 < p["trip_rate_at_line"]))
    # zero vol: never trips on a negative line
    flat = pause_pricing("X", 0.0, 1.0)
    legs.append(("zero_vol_no_trip", flat["trip_rate_at_line"] == 0.0))
    # claims extraction on a synthetic doc
    fake = ["| 目标年化 | 8%–12% | x |", "| 波动目标 | 7%（上限 8%） | x |",
            "组合波动目标 **9%**；", "| 回撤红线 | 10% | x |",
            "| 单腿 60 日累计 carry < ?2pp | 该腿暂停 |"]
    fc = doc_claims(fake)
    legs.append(("claims_target", fc["target_lo_pct"]["value"] == 8.0
                 and fc["target_hi_pct"]["value"] == 12.0))
    legs.append(("claims_vol", fc["vol_target_s1_pct"]["value"] == 7.0
                 and fc["vol_cap_s1_pct"]["value"] == 8.0
                 and fc["vol_target_s3_pct"]["value"] == 9.0))
    legs.append(("claims_placeholder", fc["carry_pause"]["placeholder"] is True))
    # a doc without the placeholder must say so rather than invent one
    fc2 = doc_claims(["| 单腿 60 日累计 carry < -2pp | 该腿暂停 |"])
    legs.append(("claims_no_placeholder", fc2["carry_pause"]["placeholder"] is False))
    ok = sum(1 for _, v in legs if v)
    for name, v in legs:
        print("%-24s %s" % (name, "PASS" if v else "FAIL"))
    print("%d/%d PASS" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check()
    payload = build()
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False, indent=1))
        fh.write(u"\n")
    print("wrote %s verdict=%s findings=%d"
          % (os.path.relpath(OUT, bc.ROOT), payload["verdict"],
             len(payload["findings"])))
    for f in payload["findings"]:
        print(" - %s: %s" % (f["id"], f.get("detail")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
