#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ETF BOOK CAPACITY FLOOR GAP -- the red the year gate cannot name.

`etf_book_year_gate` carries C1_capacity = (one-day capacity at 5% of ADV >=
20,000,000 CNY), and every candidate has failed it in every phase for weeks.
A check that fails identically in all phases is not a calendar question and
cannot be fixed by re-cutting the book window -- it is a level question the
gate never prints: *how far below the floor is the ceiling, and what would
close the gap?*

This face only reads receipts that already exist. It computes no returns and
imports no engine:

  adopted    results/etf_book_capacity_rule.json
             the live 5-name k=0.20/beta book's own capacity frontier by
             participation cap (this engine, this universe)
  card       results/etf_book_publish_decision.json
             the published 12-name vol-target card's ceiling per arm
  envelope   results/etf_capacity_frontier.json
             the priced width ladder N5..N20 (a second engine, its own
             universe) -- the only place a bigger number could live
  floor      candidate_year_gate.CAPACITY_FLOOR_CNY (single owner; never a
             second copy of 20,000,000 in this file)

Units: every capacity is CNY at a stated participation cap; cagr/maxdd are
fractions. Readings from different engines are labelled and never merged:
the envelope reading is quoted as the widest thing that has been PRICED, not
as this book's capacity.

Verdict (frozen before the first read):
  FLOOR_REACHABLE_ON_PRICE_ENVELOPE   some priced reading >= floor
  FLOOR_BEYOND_PRICED_ENVELOPE        every priced reading < floor; the gap
                                      and the width it would take are printed,
                                      and a width beyond the priced ladder is
                                      flagged OUTSIDE_PRICED_ENVELOPE
  UNKNOWN                             no reading could be read (r98: unknown
                                      is not empty, and never zero)

  python scripts/etf_book_capacity_floor_gap.py run
  python scripts/etf_book_capacity_floor_gap.py --check
  python scripts/etf_book_capacity_floor_gap.py --selftest
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "results", "etf_book_capacity_floor_gap.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_CAPACITY_FLOOR_GAP.json.md")

CAPACITY_RULE = "results/etf_book_capacity_rule.json"
CARD_RECEIPT = "results/etf_book_publish_decision.json"
ENVELOPE = "results/etf_capacity_frontier.json"
PRICED_WIDTH_MAX = 20  # the ladder the capacity engine prices (N5..N20)


def _load(rel, root=None):
    path = os.path.join(root or ROOT, rel)
    if not os.path.exists(path):
        return None, "missing"
    try:
        with io.open(path, encoding="utf-8") as f:
            return json.load(f), None
    except Exception as exc:  # a broken receipt is not an empty one
        return None, "unreadable: %s" % (exc,)


def floor_cny():
    """The floor has one owner: the gate that tests it."""
    sdir = os.path.join(ROOT, "scripts")
    if sdir not in sys.path:
        sys.path.insert(0, sdir)
    import candidate_year_gate as G
    return float(G.CAPACITY_FLOOR_CNY)


def _pct(x):
    return None if x is None else round(100.0 * x, 2)


def reading_adopted(payload):
    """The live 5-name sleeve: its own ladder by participation cap."""
    if not payload:
        return None
    row = payload.get("capacity_frontier_by_cap") or {}
    arms = row.get("rule") or []
    by_cap = {}
    for a in arms:
        cap = a.get("cap_p90_of_adv")
        if cap is None:
            continue
        by_cap["%.4f" % cap] = a
    get = lambda c: (by_cap.get("%.4f" % c) or {}).get("deployable_nav_cny")
    return {
        "reading": "adopted_5name_rule",
        "engine": payload.get("script"),
        "evidence_cutoff": payload.get("evidence_cutoff"),
        "capacity_1pct": get(0.01),
        "capacity_2pct": get(0.02),
        "capacity_5pct": get(0.05),
        "cagr_5pct": _pct((by_cap.get("0.0500") or {}).get("cagr")),
        "maxdd_5pct": _pct((by_cap.get("0.0500") or {}).get("maxdd")),
        "units": "CNY deployable at the stated participation cap (this book's own engine)",
    }


def reading_card(payload, want="12@vol"):
    """The published card's ceiling, read from its own arm entry."""
    if not payload:
        return None
    for a in payload.get("arms") or []:
        if a.get("config") == want:
            return {
                "reading": "published_card_%s" % want,
                "engine": payload.get("script"),
                "evidence_cutoff": payload.get("evidence_cutoff"),
                "capacity_1pct": a.get("capacity_1pct"),
                "capacity_5pct": a.get("capacity_5pct"),
                "cagr_5pct": _pct(a.get("cagr")),
                "maxdd_5pct": _pct(a.get("maxdd")),
                "source": a.get("source"),
                "units": "CNY ceiling p90 participation at 1%/5% of ADV",
            }
    return None


def envelope_best(payload, cadence="R20"):
    """Widest PRICED ceiling: the ladder's own max aum_5pct at one cadence."""
    if not payload:
        return None, []
    cells = [c for c in (payload.get("cells") or [])
             if str(c.get("cell", "")).endswith("_" + cadence)]
    if not cells:
        return None, []
    best = max(cells, key=lambda c: c.get("aum_5pct") or 0.0)
    out = {
        "reading": "priced_envelope_%s" % cadence,
        "engine": "results/etf_capacity_frontier.json",
        "evidence_cutoff": None,
        "capacity_1pct": best.get("aum_1pct"),
        "capacity_5pct": best.get("aum_5pct"),
        "cagr_5pct": _pct(best.get("cagr")),
        "maxdd_5pct": _pct(best.get("maxdd")),
        "sharpe_5pct": best.get("sharpe"),
        "cell": best.get("cell"),
        "units": "CNY ceiling p90 participation at 1%/5% of ADV (a second engine, its own universe)",
    }
    return out, sorted(cells, key=lambda c: _names(c.get("cell")) or 0)


def _names(cell):
    """'N12_R20' -> 12.0 ; anything else -> None (never a guess)."""
    try:
        head = str(cell).split("_")[0]
        if not head.startswith("N"):
            return None
        return float(head[1:])
    except Exception:
        return None


def widen_plan(cells, floor):
    """How many names the ladder's own slope says the floor needs.

    Least squares on (names, aum_5pct) over the priced cells of one cadence.
    The answer is printed WITH the priced ceiling, because a width beyond the
    ladder is an extrapolation, not a measurement.
    """
    pts = [(_names(c.get("cell")), c.get("aum_5pct")) for c in cells or []]
    pts = [(n, v) for n, v in pts if n is not None and v]
    if len(pts) < 3:
        return {"state": "UNPRICED", "why": "fewer than three priced widths"}
    n = len(pts)
    sx = sum(p[0] for p in pts)
    sy = sum(p[1] for p in pts)
    sxx = sum(p[0] * p[0] for p in pts)
    sxy = sum(p[0] * p[1] for p in pts)
    den = n * sxx - sx * sx
    if not den:
        return {"state": "UNPRICED", "why": "degenerate width axis"}
    slope = (n * sxy - sx * sy) / den
    intercept = (sy - slope * sx) / n
    if slope <= 0:
        return {"state": "NO_SLOPE", "slope_cny_per_name": round(slope, 1),
                "why": "the ladder's own ceiling does not rise with width"}
    need = (floor - intercept) / slope
    priced_max = max(p[0] for p in pts)
    return {
        "state": "BELOW_PRICED_MAX" if need <= priced_max else "OUTSIDE_PRICED_ENVELOPE",
        "slope_cny_per_name": round(slope, 1),
        "intercept_cny": round(intercept, 1),
        "names_needed_for_floor": round(need, 1),
        "priced_width_max": priced_max,
        "widths_priced": [p[0] for p in sorted(pts)],
    }


def widen_cost(cells):
    """What the widest priced cell costs against the narrowest, same cadence."""
    pts = [(c.get("cell"), _names(c.get("cell")), c) for c in cells or []]
    pts = [p for p in pts if p[1] is not None]
    if len(pts) < 2:
        return None
    lo = min(pts, key=lambda p: p[1])[2]
    hi = max(pts, key=lambda p: p[1])[2]
    if lo.get("cagr") is None or hi.get("cagr") is None:
        return None
    return {
        "from_cell": lo.get("cell"),
        "to_cell": hi.get("cell"),
        "cagr_from_pct": _pct(lo.get("cagr")),
        "cagr_to_pct": _pct(hi.get("cagr")),
        "cagr_cost_pp": round(100.0 * (lo["cagr"] - hi["cagr"]), 2),
        "maxdd_from_pct": _pct(lo.get("maxdd")),
        "maxdd_to_pct": _pct(hi.get("maxdd")),
        "maxdd_cost_pp": round(100.0 * (hi.get("maxdd", 0.0) - lo.get("maxdd", 0.0)), 2),
        "sharpe_from": lo.get("sharpe"),
        "sharpe_to": hi.get("sharpe"),
        "units": "pp of annualised return / pp of drawdown, same engine, same cadence",
    }


def build(root=None):
    root = root or ROOT
    errors = []
    cap_rule, err = _load(CAPACITY_RULE, root)
    if err:
        errors.append({"receipt": CAPACITY_RULE, "why": err})
    card, err = _load(CARD_RECEIPT, root)
    if err:
        errors.append({"receipt": CARD_RECEIPT, "why": err})
    env, err = _load(ENVELOPE, root)
    if err:
        errors.append({"receipt": ENVELOPE, "why": err})

    try:
        floor = floor_cny()
    except Exception as exc:
        floor = None
        errors.append({"receipt": "candidate_year_gate.CAPACITY_FLOOR_CNY",
                       "why": "unreadable: %s" % (exc,)})

    readings = []
    for r in (reading_adopted(cap_rule), reading_card(card)):
        if r and r.get("capacity_5pct"):
            readings.append(r)
    best_env, cells = envelope_best(env)
    if best_env and best_env.get("capacity_5pct"):
        readings.append(best_env)

    priced = [r for r in readings if r.get("capacity_5pct")]
    best = max(priced, key=lambda r: r["capacity_5pct"]) if priced else None
    gap_cny = None if (best is None or floor is None) else round(floor - best["capacity_5pct"], 1)
    share = None if (best is None or not floor) else round(best["capacity_5pct"] / floor, 6)

    plan = widen_plan(cells, floor) if (cells and floor) else {"state": "UNPRICED"}
    cost = widen_cost(cells)

    if floor is None or not priced:
        verdict = "UNKNOWN"
    elif best["capacity_5pct"] >= floor:
        verdict = "FLOOR_REACHABLE_ON_PRICE_ENVELOPE"
    else:
        verdict = "FLOOR_BEYOND_PRICED_ENVELOPE"

    return {
        "script": "scripts/etf_book_capacity_floor_gap.py",
        "question": ("C1_capacity fails in every phase -- how far below the floor "
                     "is the ceiling, and what would close the gap?"),
        "floor_cny": floor,
        "floor_owner": "scripts/candidate_year_gate.py::CAPACITY_FLOOR_CNY",
        "readings": readings,
        "best_reading": None if best is None else best["reading"],
        "best_capacity_5pct_cny": None if best is None else best["capacity_5pct"],
        "gap_to_floor_cny": gap_cny,
        "best_share_of_floor": share,
        "widen_plan": plan,
        "widen_cost": cost,
        "unreadable": errors,
        "verdict": verdict,
        "units": ("capacity_* are CNY; cagr/maxdd are printed in percent; "
                  "gap and share are CNY / fraction-of-floor"),
        "method_note": ("aggregation only -- every capacity number is copied from the "
                        "receipt named beside it, and readings from different engines "
                        "are labelled, never averaged"),
    }


def summary_line(face):
    best = face.get("best_capacity_5pct_cny")
    floor = face.get("floor_cny")
    gap = face.get("gap_to_floor_cny")
    if face["verdict"] == "UNKNOWN":
        return "UNKNOWN (no readable capacity receipt: %d errors)" % len(face["unreadable"])
    share = face.get("best_share_of_floor")
    plan = face.get("widen_plan") or {}
    bits = ["%s" % face["verdict"],
            "floor %.0f" % floor,
            "best %.0f (%s)" % (best, face["best_reading"]),
            "gap %.0f" % gap,
            "%.1f%% of floor" % (100.0 * share,)]
    if plan.get("names_needed_for_floor"):
        bits.append("needs ~%s names at R20 (%s)"
                    % (plan["names_needed_for_floor"], plan["state"]))
    cost = face.get("widen_cost") or {}
    if cost.get("cagr_cost_pp") is not None:
        bits.append("widest priced width costs %.2fpp cagr / %.2fpp dd"
                    % (cost["cagr_cost_pp"], cost["maxdd_cost_pp"]))
    return " | ".join(bits)


def write_md(face, path):
    L = []
    L.append("# ETF book -- capacity floor gap")
    L.append("")
    L.append("_Generated by `scripts/etf_book_capacity_floor_gap.py` from published "
             "receipts only. Every number below is copied, not computed._")
    L.append("")
    L.append("The year gate's `C1_capacity` has failed in every phase, which makes it "
             "unreadable: a calendar cannot close a level gap. This face prints the "
             "level gap and what would close it.")
    L.append("")
    L.append("- floor: **%.0f CNY** (owner: `%s`)" % (face["floor_cny"], face["floor_owner"]))
    L.append("- verdict: **%s**" % face["verdict"])
    L.append("")
    L.append("| reading | 1%% ADV | 2%% ADV | 5%% ADV | cagr @5%% | maxdd @5%% |")
    L.append("|---|---|---|---|---|---|")
    for r in face["readings"]:
        L.append("| %s | %s | %s | %s | %s | %s |" % (
            r["reading"],
            _cny(r.get("capacity_1pct")), _cny(r.get("capacity_2pct")),
            _cny(r.get("capacity_5pct")),
            "-" if r.get("cagr_5pct") is None else "%.2f%%" % r["cagr_5pct"],
            "-" if r.get("maxdd_5pct") is None else "%.2f%%" % r["maxdd_5pct"]))
    L.append("")
    if face["gap_to_floor_cny"] is not None:
        L.append("Best priced ceiling: **%s CNY** (%s) = **%.1f%%** of the floor; "
                 "gap **%s CNY**." % (
                     _cny(face["best_capacity_5pct_cny"]), face["best_reading"],
                     100.0 * face["best_share_of_floor"], _cny(face["gap_to_floor_cny"])))
        L.append("")
    plan = face.get("widen_plan") or {}
    if plan.get("names_needed_for_floor"):
        L.append("Width needed at R20 on the ladder's own slope: **%s names** "
                 "(%.0f CNY per extra name); priced widths go to %s -> **%s**." % (
                     plan["names_needed_for_floor"], plan["slope_cny_per_name"],
                     plan.get("priced_width_max"), plan["state"]))
        L.append("")
    cost = face.get("widen_cost") or {}
    if cost.get("cagr_cost_pp") is not None:
        L.append("Cost of that width, same engine and cadence (%s -> %s): cagr %.2f%% -> "
                 "%.2f%% (**%+.2fpp**), maxdd %.2f%% -> %.2f%% (**%+.2fpp**), sharpe %s -> %s." % (
                     cost["from_cell"], cost["to_cell"], cost["cagr_from_pct"],
                     cost["cagr_to_pct"], -cost["cagr_cost_pp"], cost["maxdd_from_pct"],
                     cost["maxdd_to_pct"], cost["maxdd_cost_pp"],
                     cost["sharpe_from"], cost["sharpe_to"]))
        L.append("")
    if face["unreadable"]:
        L.append("Unreadable inputs (unknown, not zero): " +
                 "; ".join("%s (%s)" % (e["receipt"], e["why"]) for e in face["unreadable"]))
        L.append("")
    L.append("Readings come from different engines and are never averaged: the "
             "`adopted_5name_rule` and `published_card` rows are this desk's own "
             "capacity faces, the `priced_envelope` row is the width ladder's second "
             "engine on its own universe.")
    L.append("")
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")


def _cny(v):
    return "n/a" if v is None else "%.0f" % v


# ---------------------------------------------------------------- selftest
def _fixture(cap5=7_647_131.0, card5=9_123_940.0, env5=13_794_151.0,
             cells=None, floor=20_000_000.0):
    cap = {"script": "capacit_rule", "evidence_cutoff": "2026-11-17",
           "capacity_frontier_by_cap": {"rule": [
               {"cap_p90_of_adv": 0.01, "deployable_nav_cny": cap5 / 5.0, "cagr": 0.0713},
               {"cap_p90_of_adv": 0.02, "deployable_nav_cny": cap5 / 2.5},
               {"cap_p90_of_adv": 0.05, "deployable_nav_cny": cap5, "cagr": 0.0649,
                "maxdd": -0.1339}]}}
    card = {"script": "publish", "arms": [
        {"config": "12@vol", "capacity_1pct": 1_824_788.0, "capacity_5pct": card5,
         "cagr": 0.0962, "maxdd": -0.1177, "source": "fixture"}]}
    if cells is None:
        cells = [
            {"cell": "N5_R20", "aum_1pct": 856_075.0, "aum_5pct": 4_280_374.0,
             "cagr": 0.1556, "sharpe": 1.002, "maxdd": -0.1604},
            {"cell": "N8_R20", "aum_1pct": 1_252_211.0, "aum_5pct": 6_261_053.0,
             "cagr": 0.1500, "sharpe": 0.995, "maxdd": -0.1678},
            {"cell": "N12_R20", "aum_1pct": 1_824_788.0, "aum_5pct": 9_123_940.0,
             "cagr": 0.1403, "sharpe": 0.970, "maxdd": -0.1588},
            {"cell": "N20_R20", "aum_1pct": 2_758_830.0, "aum_5pct": env5,
             "cagr": 0.1264, "sharpe": 0.910, "maxdd": -0.2201},
        ]
    env = {"cells": cells, "universe": 1499}
    return cap, card, env, floor


def _selftest():
    ok = []

    def leg(name, cond):
        ok.append((name, bool(cond)))

    cap, card, env, floor = _fixture()
    best_env, cells = envelope_best(env)
    leg("L1 the widest priced ceiling is the ladder's own max aum_5pct",
        best_env["capacity_5pct"] == 13_794_151.0 and best_env["cell"] == "N20_R20")
    leg("L2 the narrowest cell does not win by its 1% column",
        max(cells, key=lambda c: c["aum_5pct"])["cell"] == "N20_R20")
    plan = widen_plan(cells, floor)
    leg("L3 the width the floor needs is solved from the ladder's own slope",
        abs(plan["slope_cny_per_name"] - 634_643.1) < 5.0 and
        plan["names_needed_for_floor"] > 20)
    leg("L4 a width past the priced ladder is flagged, not claimed",
        plan["state"] == "OUTSIDE_PRICED_ENVELOPE")
    plan_low = widen_plan(cells, 6_000_000.0)
    leg("L5 a floor inside the ladder reads BELOW_PRICED_MAX",
        plan_low["state"] == "BELOW_PRICED_MAX")
    leg("L6 the priced ceiling does not rise with width -> NO_SLOPE",
        widen_plan([{"cell": "N5_R20", "aum_5pct": 5.0},
                    {"cell": "N8_R20", "aum_5pct": 5.0},
                    {"cell": "N12_R20", "aum_5pct": 5.0}], floor)["state"] == "NO_SLOPE")
    cost = widen_cost(cells)
    leg("L7 widening costs cagr and drawdown on the same engine",
        abs(cost["cagr_cost_pp"] - 2.92) < 0.01 and abs(cost["maxdd_cost_pp"] + 5.97) < 0.01)
    adopted = reading_adopted(cap)
    leg("L8 the adopted sleeve reads its own 5% column verbatim",
        adopted["capacity_5pct"] == 7_647_131.0 and adopted["capacity_1pct"] == 1_529_426.2)
    leg("L9 percent helper is a real percent (100x guard, r1775 family)",
        _pct(0.0689) == 6.89 and _pct(None) is None)
    leg("L10 a cell name that is not N<n>_... yields no width instead of a guess",
        _names("R20_only") is None and _names("N12_R20") == 12.0)

    # end-to-end over fixtures: unknown is not zero, and the gap is arithmetic
    import tempfile
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "results"), exist_ok=True)
    for rel, obj in ((CAPACITY_RULE, cap), (CARD_RECEIPT, card), (ENVELOPE, env)):
        with io.open(os.path.join(tmp, rel), "w", encoding="utf-8", newline="\n") as f:
            json.dump(obj, f)
    face = build(root=tmp)
    leg("L11 the floor is the gate's own constant, not a copy",
        face["floor_cny"] == floor_cny() == 20_000_000.0)
    leg("L12 gap = floor - best priced ceiling, share = best/floor",
        abs(face["gap_to_floor_cny"] - 6_205_849.0) < 1.0 and
        abs(face["best_share_of_floor"] - 0.689708) < 1e-5)
    leg("L13 three readings are kept apart and labelled by engine",
        len(face["readings"]) == 3 and
        len(set(r["reading"] for r in face["readings"])) == 3)
    leg("L14 every candidate below the floor reads FLOOR_BEYOND_PRICED_ENVELOPE",
        face["verdict"] == "FLOOR_BEYOND_PRICED_ENVELOPE")

    tmp2 = tempfile.mkdtemp()
    face2 = build(root=tmp2)
    leg("L15 no receipts at all is UNKNOWN, never 0 and never REACHABLE",
        face2["verdict"] == "UNKNOWN" and face2["best_capacity_5pct_cny"] is None
        and face2["gap_to_floor_cny"] is None and len(face2["unreadable"]) == 3)

    tmp3 = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp3, "results"), exist_ok=True)
    for rel, obj in ((CAPACITY_RULE, cap), (CARD_RECEIPT, card), (ENVELOPE, env)):
        with io.open(os.path.join(tmp3, rel), "w", encoding="utf-8", newline="\n") as f:
            json.dump(obj, f)
    high = {"cells": [dict(env["cells"][-1], aum_5pct=25_000_000.0)] + env["cells"][:3]}
    with io.open(os.path.join(tmp3, ENVELOPE), "w", encoding="utf-8", newline="\n") as f:
        json.dump(high, f)
    face3 = build(root=tmp3)
    leg("L16 a ceiling above the floor flips the verdict to REACHABLE",
        face3["verdict"] == "FLOOR_REACHABLE_ON_PRICE_ENVELOPE" and
        face3["gap_to_floor_cny"] < 0)

    bad = [(n, c) for n, c in ok if not c]
    for n, c in ok:
        print("[%s] %s" % ("PASS" if c else "FAIL", n))
    print("selftest %d/%d %s" % (len(ok) - len(bad), len(ok),
                                 "PASS" if not bad else "FAIL"))
    return 0 if not bad else 1


# ---------------------------------------------------------------- check
def check_published(path=None):
    path = path or OUT_JSON
    if not os.path.exists(path):
        print("etf_book_capacity_floor_gap: no published face (run first)")
        return 2
    with io.open(path, encoding="utf-8") as f:
        got = json.load(f)
    want = build()
    problems = []
    for key in ("floor_cny", "verdict", "best_reading", "best_capacity_5pct_cny",
                "gap_to_floor_cny", "best_share_of_floor"):
        if got.get(key) != want.get(key):
            problems.append("%s %r != %r" % (key, got.get(key), want.get(key)))
    if [r["reading"] for r in got.get("readings") or []] != [r["reading"] for r in want["readings"]]:
        problems.append("readings set moved")
    for a, b in zip(got.get("readings") or [], want["readings"]):
        for k in ("capacity_1pct", "capacity_5pct"):
            if a.get(k) != b.get(k):
                problems.append("%s.%s %r != %r" % (a["reading"], k, a.get(k), b.get(k)))
    if (got.get("widen_plan") or {}).get("names_needed_for_floor") != \
            want["widen_plan"].get("names_needed_for_floor"):
        problems.append("widen plan moved")
    if problems:
        print("etf_book_capacity_floor_gap: FAIL " + "; ".join(problems))
        return 1
    print("etf_book_capacity_floor_gap: check OK (%s)" % summarize_want(want))
    return 0


def summarize_want(face):
    return "floor %.0f best %.0f gap %s %s" % (
        face["floor_cny"], face["best_capacity_5pct_cny"] or 0,
        face["gap_to_floor_cny"], face["verdict"])


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    if "--check" in argv:
        return check_published()
    if "run" in argv or len(argv) <= 1:
        face = build()
        import time
        face["generated"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
            json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")
        write_md(face, os.path.join(ROOT, "research", "ETF_BOOK_CAPACITY_FLOOR_GAP.md"))
        print("etf_book_capacity_floor_gap: %s" % summary_line(face))
        return 0
    print(__doc__.strip().splitlines()[0])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
