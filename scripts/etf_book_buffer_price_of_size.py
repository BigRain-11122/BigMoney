"""The buffer's breakeven is quoted in basis points -- what capital does that actually mean?

r1347 published `results/etf_book_hysteresis_paths.json`: for every (book, phase, k) cell, the
per-side cost at which the incumbent buffer's turnover saving would pay for the return it gives
away. A breakeven in bp/side is only actionable if it can be read as a size, because the book
never pays a flat cost -- it pays the impact model.

The cost model already exists and is imported here, never restated:
`scripts.etf_book_capacity.ImpactCost` charges `base + k*sqrt(participation/1%)` per side. The
published capacity ladder records that cost at ONE reference NAV and the participation of every
decision at that NAV, so the whole curve follows from the sqrt law:

    cost(NAV) = base + (cost_ref - base) * sqrt(NAV / REF_NAV)

Inverting that per cell gives the capital above which that cell's saving covers its loss:

    NAV* = REF_NAV * ((breakeven_bp - base) / (cost_ref - base))**2

Three honest limits, stated before the numbers:

  * The cost curve is taken from the published capacity ladder, which prices the N5 book. The
    buffer grid is priced on wider cells (N8/N12/N20), and a wider book splits the same money
    over more names, so its participation per name is LOWER. Using the N5 curve therefore
    OVERSTATES what the wide book pays, which makes every crossing NAV here an optimistic
    bound -- if the buffer does not pay even at this cost, it does not pay at the real one.
  * The panel is one window of one regime, and the cells are phases inside one cycle, so NAV*
    inherits exactly the phase luck the parent face disclosed (its median phase IQR is printed
    next to the answer).
  * This is an exploratory re-reading of two published faces. No preregistration, no verdict
    booking, no config change: an arm that "pays at size" is a hypothesis for a prereg, and it
    still has to clear the frozen per-cell rule it failed in the parent face.

Usage:
    python scripts/etf_book_buffer_price_of_size.py run
    python scripts/etf_book_buffer_price_of_size.py --check
    python scripts/etf_book_buffer_price_of_size.py --selftest
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.etf_book_capacity import BASE_BP, IMPACT_BP_PER_PCT, REF_NAV  # noqa: E402

SCRIPT = "scripts/etf_book_buffer_price_of_size.py"
FACE = "results/etf_book_buffer_price_of_size.json"
OUT_JSON = ROOT / FACE
OUT_MD = ROOT / "research" / "ETF_BOOK_BUFFER_PRICE_OF_SIZE.md"
PARENT = ROOT / "results" / "etf_book_hysteresis_paths.json"
CAPACITY = ROOT / "results" / "etf_book_capacity.json"
CARD = ROOT / "results" / "etf_book_production" / "latest.json"

NAV_GRID = (1e6, 5e6, 1e7, 3e7, 5e7, 1e8)
# frozen before the first run: an arm counts as "pays at size S" only if this share of its
# cells have already crossed their breakeven by S. Same shape as the parent face's share rule,
# one number instead of five because there is only one thing being asserted here.
CROSS_SHARE_MIN = 0.80

CRITERIA = {
    "nav_grid": list(NAV_GRID),
    "ref_nav": REF_NAV,
    "base_bp": BASE_BP,
    "impact_bp_per_pct": IMPACT_BP_PER_PCT,
    "cost_law": "cost(NAV) = base + (cost_ref - base) * sqrt(NAV / REF_NAV)",
    "crossing_law": "NAV* = REF_NAV * ((breakeven_bp - base) / (cost_ref - base))**2",
    "cross_share_min": CROSS_SHARE_MIN,
    "frozen": "constants written before the first run; the gate refuses a face that echoes others",
}

UNITS = {
    "cost_bp_side": "basis points per side, the unit ImpactCost charges",
    "breakeven_bp_side": "per-side cost at which the cell's turnover saving equals its return loss",
    "crossing_nav_cny": "capital above which the cell's saving covers its loss (0 = at any size)",
    "share_crossed": "share of the arm's cells whose crossing NAV is <= the column's NAV",
}


# ---------------------------------------------------------------- the cost curve

def cost_bp(nav, cost_ref, base=BASE_BP, ref=REF_NAV):
    """Per-side cost at a given capital, from the published sqrt impact law."""
    if cost_ref is None or nav is None or nav <= 0:
        return None
    return base + max(0.0, cost_ref - base) * (float(nav) / float(ref)) ** 0.5


def crossing_nav(breakeven_bp, cost_ref, base=BASE_BP, ref=REF_NAV):
    """Capital above which `breakeven_bp` of per-side cost is actually being paid.

    Three states, not one number, because collapsing them is how a table lies:
      * breakeven <= 0        -> the arm GAINS return, so it needs no cost story: pays at any size
                                 (0.0), flagged in `reason`.
      * breakeven <= base     -> the book pays that much before any impact: pays at any size.
      * otherwise             -> invert the sqrt law; None if the reference cost is not above
                                 the base (no impact component = the threshold is unreachable).
    """
    if breakeven_bp is None:
        return None, "no breakeven on the face"
    if breakeven_bp <= 0:
        return 0.0, "arm gains return -- pays at any cost"
    if breakeven_bp <= base:
        return 0.0, "below the base cost -- pays at any size"
    if cost_ref is None or cost_ref <= base:
        return None, "reference cost is not above the base: no impact component to cross"
    ratio = (breakeven_bp - base) / (cost_ref - base)
    return round(ref * ratio * ratio, 1), "sqrt law inversion"


# ---------------------------------------------------------------- reading the faces

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def cost_reference(capacity):
    """The book's own per-side cost at one reference NAV, as a median over decisions.

    The capacity face records `rate_bp_per_side` for every decision it priced at REF_NAV.
    The median is preferred to the mean because a single thin name can carry the whole
    average, and the curve is then scaled by the sqrt law -- not re-fitted.
    """
    part = capacity.get("participation_at_ref_nav") or {}
    rows = [r.get("rate_bp_per_side") for r in part.get("rows") or []
            if r.get("rate_bp_per_side") is not None]
    if not rows:
        return None, None, part
    rows.sort()
    n = len(rows)
    med = rows[n // 2] if n % 2 else 0.5 * (rows[n // 2 - 1] + rows[n // 2])
    return round(float(med), 3), part.get("ref_nav") or REF_NAV, part


def arm_cells(parent, arm_k):
    for a in parent.get("arms") or []:
        if a.get("k") == arm_k:
            return a.get("cells") or []
    return []


def price_arm(cells, cost_ref):
    """Per-cell crossing NAVs, then the share that has crossed at each NAV in the grid."""
    out = []
    for c in cells:
        be = c.get("breakeven_cost_bp_side", c.get("breakeven_bp_side"))
        nav_star, why = crossing_nav(be, cost_ref)
        out.append({
            "n_hold": c.get("n_hold"), "rebal": c.get("rebal"), "phase": c.get("phase"),
            "breakeven_cost_bp_side": be, "crossing_nav_cny": nav_star,
            "crossing_reason": why,
        })
    known = [r["crossing_nav_cny"] for r in out if r["crossing_nav_cny"] is not None]
    share = {}
    for nav in NAV_GRID:
        hit = sum(1 for v in known if v <= nav)
        share[_nav_key(nav)] = round(hit / float(len(out)), 4) if out else None
    return {
        "n_cells": len(out),
        "n_known": len(known),
        "median_crossing_nav_cny": _median(known),
        "min_crossing_nav_cny": min(known) if known else None,
        "max_crossing_nav_cny": max(known) if known else None,
        "share_crossed": share,
        "pays_at": {_nav_key(nav): (share[_nav_key(nav)] is not None
                                    and share[_nav_key(nav)] >= CROSS_SHARE_MIN)
                    for nav in NAV_GRID},
        "cells": out,
    }


def _nav_key(nav):
    return "nav=%g" % float(nav)


def _median(vals):
    if not vals:
        return None
    v = sorted(vals)
    n = len(v)
    return round(float(v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2])), 1)


def family(cost_ref, capacity):
    """One sentence: at what size does ANY arm pay, and is that size even runnable?"""
    part = capacity.get("participation_at_ref_nav") or {}
    cap_nav = part.get("nav_where_p90_trade_is_1pct_adv")
    return {
        "nav_where_p90_trade_is_1pct_adv": cap_nav,
        "note": ("the p90 trade is already 1%% of ADV at about %.2fM of capital; a buffer that "
                 "only pays above that size cannot be used, because the book cannot be run "
                 "there without breaking the 1%% participation cap"
                 % ((cap_nav or 0) / 1e6)),
        "cost_at_ref_bp_side": cost_ref,
    }


# ---------------------------------------------------------------- build

def build():
    parent = load(PARENT)
    capacity = load(CAPACITY)
    cost_ref, ref_used, part = cost_reference(capacity)
    card_cutoff = None
    if CARD.exists():
        try:
            card_cutoff = load(CARD).get("priced_bar") or load(CARD).get("evidence_cutoff")
        except Exception:
            card_cutoff = None

    arms = []
    for a in parent.get("arms") or []:
        priced = price_arm(arm_cells(parent, a.get("k")), cost_ref)
        arms.append(dict({"k": a.get("k"), "parent_verdict": a.get("verdict"),
                          "parent_median_cagr_pp": a.get("median_delta_cagr_pp")}, **priced))

    payload = {
        "script": SCRIPT,
        "face": FACE,
        "evidence_cutoff": parent.get("evidence_cutoff"),
        "units": UNITS,
        "criteria": CRITERIA,
        "config": {
            "parent_face": str(PARENT.relative_to(ROOT)),
            "cost_face": str(CAPACITY.relative_to(ROOT)),
            "ref_nav_used": ref_used,
            "cost_curve": [{"nav": nav, "cost_bp_side": round(cost_bp(nav, cost_ref), 3)}
                           for nav in NAV_GRID],
            "absorption": "cost curve read from the published capacity ladder (the N5 book)",
        },
        "card_cutoff": card_cutoff,
        "family": family(cost_ref, capacity),
        "arms": arms,
        "caveats": [
            "the cost curve is the N5 book's, so the wide cells' real bill is LOWER and every "
            "crossing NAV here is an optimistic bound",
            "exploratory re-reading of two published faces: no preregistration, no verdict booking",
            "NAV* inherits the parent face's phase luck (see its median phase IQR)",
            "an arm that pays at size still failed the parent face's frozen per-cell rule",
        ],
    }
    return payload


def render_md(p):
    L = []
    L.append("# ETF book -- the buffer's breakeven, read as a size\n")
    L.append("Face: `%s` (parent cutoff **%s**)\n" % (FACE, p["evidence_cutoff"]))
    fam = p["family"]
    L.append("## Cost curve (published sqrt impact law)\n")
    L.append("- %s\n" % fam.get("note"))
    L.append("| NAV | per-side cost (bp) |")
    L.append("|---|---|")
    for row in p["config"]["cost_curve"]:
        L.append("| %.0fM | %.2f |" % (row["nav"] / 1e6, row["cost_bp_side"]))
    L.append("\n## Arms (median breakeven across cells, and the capital that implies)\n")
    L.append("| k | parent verdict | median breakeven (bp/side) | median crossing NAV | "
             "pays at 1M | 5M | 10M | 30M | 50M | 100M |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for a in p["arms"]:
        med = a["median_crossing_nav_cny"]
        L.append("| %.2f | %s | %s | %s | %s |"
                 % (a["k"], a["parent_verdict"],
                    "n/a" if not a["n_cells"] else "%.1f" % _median(
                        [c["breakeven_cost_bp_side"] for c in a["cells"]
                         if c["breakeven_cost_bp_side"] is not None] or [0]),
                    "n/a" if med is None else "%.2fM" % (med / 1e6),
                    " | ".join("yes" if a["pays_at"][_nav_key(n)] else "no" for n in NAV_GRID)))
    L.append("\n\"Pays at S\" = at least %.0f%% of the arm's cells have crossed their breakeven "
             "by S. A median crossing of 0.00M means more than half the arm's cells need no "
             "cost story at all -- the pays-at columns still apply the %.0f%% share rule, which "
             "is why an arm can have a zero median and still not pay.\n"
             % (100 * CROSS_SHARE_MIN, 100 * CROSS_SHARE_MIN))
    L.append("\n## Honest limits\n")
    for c in p["caveats"]:
        L.append("- %s" % c)
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- gate

def staleness(face_cutoff, card_cutoff):
    """r1346: 'behind the card' is a third state the runner pays a refresh for."""
    if not face_cutoff or not card_cutoff:
        return "unknown"
    return "stale" if str(face_cutoff) < str(card_cutoff) else "current"


def recompute(payload):
    """Re-derive every crossing and every pays-at flag from the stored inputs."""
    cost_ref = payload.get("family", {}).get("cost_at_ref_bp_side")
    problems = []
    for a in payload.get("arms") or []:
        cells = a.get("cells") or []
        rebuilt = price_arm(cells, cost_ref)
        for key in ("median_crossing_nav_cny", "min_crossing_nav_cny", "max_crossing_nav_cny",
                    "n_known"):
            if a.get(key) != rebuilt[key]:
                problems.append("arm k=%s %s published %r but recomputes to %r"
                                % (a.get("k"), key, a.get(key), rebuilt[key]))
        if a.get("share_crossed") != rebuilt["share_crossed"]:
            problems.append("arm k=%s share_crossed published %r but recomputes to %r"
                            % (a.get("k"), a.get("share_crossed"), rebuilt["share_crossed"]))
        if a.get("pays_at") != rebuilt["pays_at"]:
            problems.append("arm k=%s pays_at published %r but recomputes to %r"
                            % (a.get("k"), a.get("pays_at"), rebuilt["pays_at"]))
    return problems


def check():
    if not OUT_JSON.exists():
        print("CHECK FAIL: face absent %s" % OUT_JSON)
        return 2
    payload = load(OUT_JSON)
    state = staleness(payload.get("evidence_cutoff"), payload.get("card_cutoff"))
    if state == "stale":
        print("STALE: face priced on %s while the production card is on %s"
              % (payload.get("evidence_cutoff"), payload.get("card_cutoff")))
        return 2
    problems = []
    echo = payload.get("criteria") or {}
    for key, want in (("base_bp", BASE_BP), ("impact_bp_per_pct", IMPACT_BP_PER_PCT),
                      ("ref_nav", REF_NAV), ("cross_share_min", CROSS_SHARE_MIN)):
        if echo.get(key) != want:
            problems.append("criteria echo drifted at %s: %r vs %r" % (key, echo.get(key), want))
    if [float(x) for x in echo.get("nav_grid") or []] != [float(x) for x in NAV_GRID]:
        problems.append("nav grid echo drifted: %r" % (echo.get("nav_grid"),))
    cost_ref = payload.get("family", {}).get("cost_at_ref_bp_side")
    if cost_ref is None:
        problems.append("cost reference missing: the curve has no anchor")
    curve = {round(float(r["nav"])): r["cost_bp_side"]
             for r in payload.get("config", {}).get("cost_curve") or []}
    for nav in NAV_GRID:
        want = round(cost_bp(nav, cost_ref), 3) if cost_ref is not None else None
        if curve.get(round(float(nav))) != want:
            problems.append("cost curve at NAV %s published %r but the law gives %r"
                            % (nav, curve.get(round(float(nav))), want))
    problems.extend(recompute(payload))
    if problems:
        print("CHECK FAIL:\n  " + "\n  ".join(problems))
        return 2
    print("CHECK OK: %d arms, %d cells, cost_ref=%.2fbp at %gM"
          % (len(payload.get("arms") or []),
             sum(a.get("n_cells") or 0 for a in payload.get("arms") or []),
             cost_ref, REF_NAV / 1e6))
    return 0


# ---------------------------------------------------------------- selftest

def _eq(name, got, want, tol=1e-6):
    if isinstance(want, str) or isinstance(got, str):
        ok = got == want
    else:
        ok = (got is None and want is None) or (
            got is not None and want is not None and abs(float(got) - float(want)) <= tol)
    if not ok:
        raise AssertionError("%s: got %r want %r" % (name, got, want))
    print("  ok %s = %r" % (name, got))


def selftest():
    print("selftest: the sqrt cost law")
    cref = 30.0
    _eq("cost at the reference NAV == the reference cost", cost_bp(REF_NAV, cref), cref)
    _eq("cost at a quarter of the NAV removes half the impact",
        cost_bp(REF_NAV / 4, cref), BASE_BP + (cref - BASE_BP) / 2, 1e-9)
    _eq("cost is monotone in size",
        cost_bp(REF_NAV * 4, cref) > cost_bp(REF_NAV, cref), True)
    _eq("a reference at the base has no impact component",
        cost_bp(REF_NAV * 100, BASE_BP), BASE_BP, 1e-9)

    print("selftest: crossing NAV is the inverse of the curve")
    for be in (9.0, 12.0, 20.0, 44.5):
        nav = crossing_nav(be, cref)[0]
        _eq("crossing then cost round-trips at breakeven %.1fbp" % be,
            round(cost_bp(nav, cref), 9), be, 1e-3)

    print("selftest: three crossing states are not one number")
    _eq("a return-gaining arm crosses at zero", crossing_nav(-5.0, cref)[0], 0.0)
    _eq("its reason says so", crossing_nav(-5.0, cref)[1], "arm gains return -- pays at any cost")
    _eq("a breakeven under the base pays at any size", crossing_nav(BASE_BP / 2, cref)[0], 0.0)
    _eq("no breakeven on the face -> no crossing", crossing_nav(None, cref)[0], None)
    _eq("a reference at the base cannot be crossed",
        crossing_nav(20.0, BASE_BP)[0], None)

    print("selftest: the pays-at column reads shares, not one cell")
    cells = [{"n_hold": 12, "rebal": 20, "phase": "p%d" % i,
              "breakeven_cost_bp_side": be} for i, be in enumerate((9.0, 9.5, 10.0, 400.0))]
    priced = price_arm(cells, cref)
    _eq("4 cells priced", priced["n_cells"], 4)
    # cost at 1M is 8 + 22*sqrt(0.1) = 14.96bp, so the three cheap cells have crossed
    _eq("share crossed at 1M reads the curve, not the count of cells",
        priced["share_crossed"][_nav_key(1e6)], 0.75)
    _eq("the far cell has not crossed even at 100M",
        priced["share_crossed"][_nav_key(1e8)] < 1.0, True)
    _eq("pays_at needs the frozen share, not one survivor",
        priced["pays_at"][_nav_key(1e8)], False)

    print("selftest: the gate recomputes what it published")
    payload = {"family": {"cost_at_ref_bp_side": cref},
               "arms": [dict({"k": 0.05}, **price_arm(cells, cref))]}
    if recompute(payload):
        raise AssertionError("a fresh publish must rebuild clean: %r" % (recompute(payload),))
    print("  ok a fresh face rebuilds clean")
    tampered = json.loads(json.dumps(payload))
    tampered["arms"][0]["cells"][0]["breakeven_cost_bp_side"] = 9.9
    if not any("median_crossing" in p or "share_crossed" in p for p in recompute(tampered)):
        raise AssertionError("an edited cell breakeven was not caught")
    print("  ok a hand-edited cell breakeven is contradicted by the recompute")
    tampered2 = json.loads(json.dumps(payload))
    tampered2["arms"][0]["pays_at"][_nav_key(1e8)] = True
    if not any("pays_at" in p for p in recompute(tampered2)):
        raise AssertionError("an edited pays_at flag was not caught")
    print("  ok a hand-edited verdict flag is contradicted by the shares")

    print("selftest: behind-the-card is a third state (r1346)")
    _eq("stale when card advanced", staleness("2026-10-28", "2026-10-29"), "stale")
    _eq("current on the same bar", staleness("2026-10-29", "2026-10-29"), "current")
    _eq("unknown without a card", staleness("2026-10-29", None), "unknown")

    print("selftest PASS (24 legs)")
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest or a.cmd == "selftest":
        return selftest()
    if a.check or a.cmd == "check":
        return check()
    if a.cmd != "run":
        print("unknown command: %s" % a.cmd)
        return 2
    payload = build()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=1, ensure_ascii=False, default=float),
                        encoding="utf-8")
    OUT_MD.write_text(render_md(payload), encoding="utf-8")
    print("wrote %s (cutoff %s, cost_ref %.2fbp/side)" % (FACE, payload["evidence_cutoff"],
                                                         payload["family"]["cost_at_ref_bp_side"]))
    for arm in payload["arms"]:
        med = arm["median_crossing_nav_cny"]
        print("  k=%.2f %-15s median crossing %s  share@1M %.0f%%  share@100M %.0f%%"
              % (arm["k"], arm["parent_verdict"],
                 "n/a" if med is None else "%.2fM" % (med / 1e6),
                 100 * (arm["share_crossed"][_nav_key(1e6)] or 0),
                 100 * (arm["share_crossed"][_nav_key(1e8)] or 0)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))