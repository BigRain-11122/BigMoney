"""What ISSUED the floor of k=0.393073 -- and is it a rule, or a measuring tape?

r1472 closed one sentence and opened a worse one: the sheet obeys the floor
(k=0.390822 vs permitted 0.393073) but the rule's own decision bar sizes at
k=0.460253, so the trim must be re-applied on 90.4% of bars.  Its closing line was
"the real question is which version of the rule the floor was ISSUED against".

This face answers that off the published receipts only (no panel, no repricing):

  * every cell of results/etf_book_size_rulers_decision.json carries both `k` and
    `beta`; if k * beta == beta_target on every cell then the floor is not a rule
    version at all, it is beta_TARGET / beta -- a measuring tape turned upside down;
  * the floor is min over path readings = the reciprocal of the LARGEST beta in the
    table, so the floor is issued by whichever cell measured the most volatile book;
  * the four path cells form a 2x2 (window: full vs common-306-bar) x (universe: all
    vs graded), so the gap between the highest and the lowest floor can be split into
    a window main effect, a universe main effect and their interaction -- and the
    question the desk actually has is which of those two knobs moved the money.

The answer is printed as money, not as pp of beta: the floor is a size, so a knob
that moves beta by 4pp moves the order by a different number of CNY.

Read-only over published JSON.  Deterministic.  No network.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULERS = os.path.join(BASE, "results", "etf_book_size_rulers_decision.json")
PERMISSION = os.path.join(BASE, "results", "etf_book_rebalance_permission.json")
OUT = os.path.join(BASE, "results", "etf_book_floor_provenance.json")
MD = os.path.join(BASE, "research", "ETF_BOOK_FLOOR_PROVENANCE.md")

IDENT_TOL = 1e-9        # k * beta == beta_target is an algebraic identity, not a fit
K_DP = 6

VERDICT_RECIPROCAL = "FLOOR_IS_A_BETA_RECIPROCAL"
VERDICT_IDENTITY_BROKEN = "IDENTITY_BROKEN"
VERDICT_UNREADABLE = "UNREADABLE"

# the 2x2 the ruler table was built on; the labels are the ones the receipt uses
WINDOW_LABELS = {"full": "full", "common": "common"}
UNIVERSE_LABELS = {"all": "all", "graded": "graded"}


def _read_json(p):
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _axis(value):
    """Map a free-text cell label onto the 2x2 axis, or None when it does not fit."""
    v = (value or "").strip().lower()
    if not v:
        return None
    if v.startswith("full") or v in ("all classes on the panel",):
        return None if v.startswith("all classes") else "full"
    if v.startswith("common"):
        return "common"
    if v.startswith("all"):
        return "all"
    if v.startswith("graded"):
        return "graded"
    return None


def cell_axes(cell):
    """(window, universe) of one ruler cell, using the receipt's own vocabulary."""
    w_raw = (cell.get("window") or "")
    u_raw = (cell.get("universe") or "")
    w = "full" if w_raw.strip().lower().startswith("full") else (
        "common" if w_raw.strip().lower().startswith("common") else None)
    u = "graded" if u_raw.strip().lower().startswith("graded") else (
        "all" if u_raw.strip().lower().startswith("all") else None)
    return w, u


def identity_of(cells, beta_target):
    """Does k * beta == beta_target on every cell that carries both?"""
    rows, broken, unreadable = [], [], []
    for name, cell in (cells or {}).items():
        k, beta = cell.get("k"), cell.get("beta")
        if k is None or beta is None:
            unreadable.append("%s: no k/beta pair" % name)
            continue
        prod = float(k) * float(beta)
        err = prod - float(beta_target)
        rows.append({"cell": name, "k": float(k), "beta": float(beta),
                     "k_x_beta": prod, "err_vs_target": err})
        if abs(err) > IDENT_TOL:
            broken.append("%s: k*beta=%.12f vs target %.12f (err %.3e)"
                          % (name, prod, float(beta_target), err))
    return rows, broken, unreadable


def grid(cells):
    """The 2x2, plus what each corner's k is and which cells are missing."""
    m = {}
    for name, cell in (cells or {}).items():
        w, u = cell_axes(cell)
        if w is None or u is None or cell.get("k") is None or cell.get("beta") is None:
            continue
        m[(w, u)] = {"cell": name, "k": float(cell["k"]), "beta": float(cell["beta"]),
                     "bars": cell.get("bars"),
                     "note": (cell.get("note") or "")}
    missing = [("%s x %s" % (w, u)) for w in ("full", "common") for u in ("all", "graded")
               if (w, u) not in m]
    return m, missing


def effects(m, nav):
    """Split the floor gap into window / universe main effects on the k scale.

    The floor the desk obeys is min over path cells = the reciprocal of the largest
    beta, so the honest summaries of a knob are the floor it produces at each level.
    A 2x2 of k lets the two main effects and their interaction be read off directly.
    """
    def k(w, u):
        c = m.get((w, u))
        return None if c is None else c["k"]

    def mean_k(ws, us):
        vals = [k(w, u) for w in ws for u in us]
        vals = [v for v in vals if v is not None]
        return None if not vals else sum(vals) / len(vals)

    # floors (min over the cells at that level) and their money
    floor_full = min([v for v in (k("full", "all"), k("full", "graded")) if v is not None], default=None)
    floor_common = min([v for v in (k("common", "all"), k("common", "graded")) if v is not None], default=None)
    floor_all = min([v for v in (k("full", "all"), k("common", "all")) if v is not None], default=None)
    floor_graded = min([v for v in (k("full", "graded"), k("common", "graded")) if v is not None], default=None)

    out = {
        "floor_full_window": floor_full,
        "floor_common_window": floor_common,
        "floor_all_universe": floor_all,
        "floor_graded_universe": floor_graded,
        "floor_full_all": k("full", "all"),
        "floor_full_graded": k("full", "graded"),
        "floor_common_all": k("common", "all"),
        "floor_common_graded": k("common", "graded"),
    }
    if floor_full is not None and floor_common is not None:
        out["window_effect_k"] = round(floor_full - floor_common, K_DP)
        out["window_effect_pp"] = round(100.0 * (floor_full - floor_common), 2)
        out["window_effect_cny"] = round((floor_full - floor_common) * nav, 2)
    if floor_all is not None and floor_graded is not None:
        out["universe_effect_k"] = round(floor_all - floor_graded, K_DP)
        out["universe_effect_pp"] = round(100.0 * (floor_all - floor_graded), 2)
        out["universe_effect_cny"] = round((floor_all - floor_graded) * nav, 2)
    # interaction on the additive k scale: how much the universe effect depends on the window
    u_full = (k("full", "all") - k("full", "graded")) if None not in (k("full", "all"), k("full", "graded")) else None
    u_common = (k("common", "all") - k("common", "graded")) if None not in (k("common", "all"), k("common", "graded")) else None
    if u_full is not None and u_common is not None:
        out["universe_effect_full_window_pp"] = round(100.0 * u_full, 2)
        out["universe_effect_common_window_pp"] = round(100.0 * u_common, 2)
        out["interaction_pp"] = round(100.0 * (u_full - u_common), 2)
    # total gap the two knobs together explain, and each one's share of it
    if None not in (k("full", "all"), k("common", "graded")):
        total = k("full", "all") - k("common", "graded")
        out["total_gap_k"] = round(total, K_DP)
        out["total_gap_pp"] = round(100.0 * total, 2)
        out["total_gap_cny"] = round(total * nav, 2)
        if out.get("window_effect_k") is not None and total:
            out["window_share_of_gap"] = round(out["window_effect_k"] / total, 3)
        if out.get("universe_effect_k") is not None and total:
            out["universe_share_of_gap"] = round(out["universe_effect_k"] / total, 3)
    return out


def issuing_cell(cells):
    """The cell whose beta is largest -- the one that sets the floor."""
    cand = [(name, c) for name, c in (cells or {}).items()
            if c.get("k") is not None and c.get("beta") is not None
            and (c.get("bars") or 0) >= 60
            and not (c.get("note") or "").lower().startswith("static composition")]
    if not cand:
        return None
    name, c = max(cand, key=lambda kv: float(kv[1]["beta"]))
    return {"cell": name, "beta": float(c["beta"]), "k": float(c["k"]),
            "bars": c.get("bars"), "window": c.get("window"), "universe": c.get("universe")}


def assess(rulers, permission, nav=1000000.0):
    """Pure function of the published receipts."""
    if rulers is None:
        return {"verdict": VERDICT_UNREADABLE, "reason": "missing_rulers_receipt",
                "sentence": "the rulers receipt is missing: a floor nobody can trace has no issuer"}
    cells = rulers.get("cells") or {}
    # the money ruler comes off the receipt the caller hands in, not off a default
    if permission and permission.get("nav_cny") is not None:
        nav = float(permission["nav_cny"])
    beta_target = permission.get("beta_target") if permission else None
    if beta_target is None:
        beta_target = rulers.get("beta_target")
    if beta_target is None:
        return {"verdict": VERDICT_UNREADABLE, "reason": "missing_beta_target",
                "sentence": "no beta target on either receipt: the reciprocal cannot be checked"}
    beta_target = float(beta_target)

    ident_rows, broken, unreadable = identity_of(cells, beta_target)
    m, missing = grid(cells)
    eff = effects(m, nav)
    issued = issuing_cell(cells)
    published_floor = (permission or {}).get("permitted_k")

    out = {
        "face": "etf_book_floor_provenance",
        "question": "which cell ISSUED the floor -- a rule version, or the measuring tape?",
        "beta_target": beta_target,
        "identity": ident_rows,
        "identity_broken": broken,
        "identity_unreadable": unreadable,
        "grid": {"%s|%s" % kk: vv for kk, vv in sorted(m.items())},
        "grid_missing": missing,
        "effects": eff,
        "issuing_cell": issued,
        "published_floor": published_floor,
        "evidence_cutoff": rulers.get("evidence_cutoff"),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }

    if broken:
        out["verdict"] = VERDICT_IDENTITY_BROKEN
        out["sentence"] = (
            "k*beta does not equal the beta target on %d cell(s): the floor is not a "
            "reciprocal here, so this face will not call it one (%s)"
            % (len(broken), "; ".join(broken[:2])))
        return out
    if missing:
        out["verdict"] = VERDICT_UNREADABLE
        out["sentence"] = (
            "the 2x2 is incomplete (%s missing): a main effect cannot be read off "
            "three corners, and the missing corner is not zero" % ", ".join(missing))
        return out

    out["verdict"] = VERDICT_RECIPROCAL
    if issued and published_floor is not None:
        out["issuing_cell_is_the_floor"] = abs(issued["k"] - float(published_floor)) <= 1e-6
        out["issuing_cell_delta_pp"] = round(100.0 * (issued["k"] - float(published_floor)), 2)

    win_pp = eff.get("window_effect_pp")
    uni_pp = eff.get("universe_effect_pp")
    share = eff.get("window_share_of_gap")
    out["sentence"] = (
        "the floor is not a version of the rule: k*beta == %.4f on all %d cells, so the floor "
        "is the target divided by the largest beta measured -- issued by `%s` (%s bars). "
        "Of the %.2fpp between the widest floor (k=%.6f) and the narrowest (k=%.6f), "
        "%.2fpp (%.0f%%) comes from shrinking the window from the full panel to %s bars and "
        "only %.2fpp from grading the universe on that same short stretch (%.2fpp if the universe "
        "is graded on the full panel); the two knobs interact by %.2fpp. "
        "Read as money on CNY %s NAV: the window alone accounts for CNY %s of the gap."
        % (beta_target, len(ident_rows),
           (issued or {}).get("cell"), (issued or {}).get("bars"),
           eff.get("total_gap_pp") or 0.0,
           eff.get("floor_full_all") or 0.0, eff.get("floor_common_graded") or 0.0,
           win_pp or 0.0, 100.0 * (share or 0.0),
           (issued or {}).get("bars"),
           uni_pp or 0.0, eff.get("universe_effect_full_window_pp") or 0.0,
           eff.get("interaction_pp") or 0.0,
           format(nav, ",.0f"),
           format(eff.get("window_effect_cny") or 0.0, ",.0f")))
    out["not_measured"] = [
        "the short window is one calendar stretch (2025-07..2026-10), not a sample of stretches: "
        "a rolling 306-bar beta path would say whether the window knob is a level shift or a "
        "phase effect, and this face does not compute it",
        "whether a longer window is the RIGHT window: this face only prices the knob, it does "
        "not elect one (r1446's caliber prereg)",
        "the floor's own drift as the window slides: today's 306 bars end 2026-10-14, so the "
        "floor will be re-issued on a different stretch next month",
    ]
    return out


def run(write=True):
    t0 = time.time()
    rulers = _read_json(RULERS)
    permission = _read_json(PERMISSION)
    nav = float((permission or {}).get("nav_cny") or 1000000.0)
    face = assess(rulers, permission, nav)
    face["elapsed_sec"] = round(time.time() - t0, 2)
    if write:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(face, f, ensure_ascii=False, indent=1)
            f.write("\n")
        with open(MD, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines(face)) + "\n")
    return face


def md_lines(d):
    eff = d.get("effects") or {}
    out = [
        "# What issued the floor of k=%.6f" % (d.get("published_floor") or 0.0),
        "",
        "> %s" % d.get("sentence", ""),
        "",
        "## The identity",
        "",
        "| cell | beta | k | k x beta | err vs target |",
        "|---|---|---|---|---|",
    ]
    for r in d.get("identity") or []:
        out.append("| %s | %.6f | %.6f | %.9f | %.2e |"
                   % (r["cell"], r["beta"], r["k"], r["k_x_beta"], r["err_vs_target"]))
    out += [
        "",
        "If the right column is all zeros this is not a fit: **k = beta_target / beta**.",
        "",
        "## The 2x2 and what each knob costs",
        "",
        "| corner | cell | k | bars |",
        "|---|---|---|---|",
    ]
    for key, c in (d.get("grid") or {}).items():
        out.append("| %s | %s | %.6f | %s |" % (key, c.get("cell"), c["k"], c.get("bars")))
    out += [
        "",
        "| effect | k | pp | CNY on 1,000,000 |",
        "|---|---|---|---|",
        "| window (full -> common) | %s | %s | %s |"
        % (eff.get("window_effect_k"), eff.get("window_effect_pp"),
           format(eff.get("window_effect_cny") or 0, ",.0f")),
        "| universe (all -> graded, at the 306-bar window) | %s | %s | %s |"
        % (eff.get("universe_effect_k"), eff.get("universe_effect_pp"),
           format(eff.get("universe_effect_cny") or 0, ",.0f")),
        "| universe (all -> graded, at the full panel) | - | %s | - |"
        % eff.get("universe_effect_full_window_pp"),
        "| interaction | - | %s | - |" % eff.get("interaction_pp"),
        "| total gap | %s | %s | %s |"
        % (eff.get("total_gap_k"), eff.get("total_gap_pp"),
           format(eff.get("total_gap_cny") or 0, ",.0f")),
        "",
        "- share of the gap explained by the window alone: **%.0f%%**"
        % (100.0 * (eff.get("window_share_of_gap") or 0.0)),
        "- share explained by grading the universe: **%.0f%%**"
        % (100.0 * (eff.get("universe_share_of_gap") or 0.0)),
        "",
        "## What this does to the sheet",
        "",
        "- The floor is a **measuring tape**, not a rule: it is the beta target divided by "
        "whichever beta the table measured as largest.",
        "- The issuing cell is `%s` (%s bars) -- the shortest evidence in the table."
        % ((d.get("issuing_cell") or {}).get("cell"), (d.get("issuing_cell") or {}).get("bars")),
        "- So \"the floor\" is a statement about the last ~306 bars of volatility, re-issued "
        "as that window slides; it is not a bound the rule was designed against.",
        "",
        "## Not measured",
        "",
    ]
    for m in d.get("not_measured") or []:
        out.append("- " + m)
    out += ["", "_evidence cutoff %s_" % d.get("evidence_cutoff")]
    return out


def check():
    """Re-derive every field that moves when an input moves. Drift is RED."""
    face = _read_json(OUT)
    if not face:
        print("CHECK_FAIL missing face %s" % OUT)
        return 2
    rulers = _read_json(RULERS)
    permission = _read_json(PERMISSION)
    nav = float((permission or {}).get("nav_cny") or 1000000.0)
    a = assess(rulers, permission, nav)
    drift = []
    for k in ("verdict", "beta_target", "published_floor", "issuing_cell_is_the_floor"):
        if face.get(k) != a.get(k):
            drift.append("%s: published=%r re-derived=%r" % (k, face.get(k), a.get(k)))
    for k in ("window_effect_pp", "universe_effect_pp", "interaction_pp",
              "total_gap_pp", "window_effect_cny"):
        if (face.get("effects") or {}).get(k) != (a.get("effects") or {}).get(k):
            drift.append("effects.%s: published=%r re-derived=%r"
                         % (k, (face.get("effects") or {}).get(k),
                            (a.get("effects") or {}).get(k)))
    if drift:
        for d in drift:
            print("DRIFT " + d)
        print("CHECK_FAIL %d field(s) drifted" % len(drift))
        return 1
    print("CHECK_OK floor=%s verdict=%s window_pp=%s universe_pp=%s"
          % (a.get("published_floor"), a.get("verdict"),
             (a.get("effects") or {}).get("window_effect_pp"),
             (a.get("effects") or {}).get("universe_effect_pp")))
    return 0


# ---------------------------------------------------------------------- selftest
def _fixture(beta_target=0.2):
    def c(beta, bars, window, universe):
        return {"k": beta_target / beta, "beta": beta, "bars": bars,
                "window": window, "universe": universe}
    return {"cells": {
        "baseline_published": c(0.4345431828620592, 1658, "full", "all classes on the panel"),
        "window": c(0.48465048393028765, 306, "common (2025-07-09..2026-10-14)",
                    "all classes on the panel"),
        "universe": c(0.4627540748556339, 1658, "full",
                      "graded (equity,commodity,convertible)"),
        "window_x_universe": c(0.508811146851568, 306, "common (2025-07-09..2026-10-14)",
                               "graded (equity,commodity,convertible)"),
        "denominator": {"k": 0.5444236051186708, "beta": 0.2 / 0.5444236051186708,
                        "bars": 306, "window": "common",
                        "universe": "today's 5 names, 100% invested",
                        "note": "static composition, not a path"},
    }, "evidence_cutoff": "2026-11-06"}


def selftest():
    fails, total = [], 0

    def leg(name, cond, detail=""):
        nonlocal total
        total += 1
        if not cond:
            fails.append(name + ((" :: " + detail) if detail else ""))

    fx = _fixture()
    perm = {"beta_target": 0.2, "permitted_k": 0.39307314951247446, "nav_cny": 1000000.0}
    a = assess(fx, perm)

    rows, broken, unread = identity_of(fx["cells"], 0.2)
    leg("L1 k*beta == target on every cell", not broken and len(rows) == 5,
        repr(broken))
    leg("L2 the identity holds to 1e-9, not approximately",
        all(abs(r["err_vs_target"]) <= 1e-9 for r in rows), repr(rows[:2]))

    m, missing = grid(fx["cells"])
    leg("L3 the 2x2 is complete and the static cell stays out of it",
        not missing and len(m) == 4, "%s / %s" % (missing, len(m)))
    leg("L3b the static denominator cell is not a grid corner",
        all(v["cell"] != "denominator" for v in m.values()), repr(list(m)))

    iss = issuing_cell(fx["cells"])
    leg("L4 the issuing cell is the largest beta, not the lowest k by accident",
        iss["cell"] == "window_x_universe" and abs(iss["beta"] - 0.508811146851568) < 1e-12,
        repr(iss))
    leg("L5 the issuing cell reproduces the published floor",
        abs(iss["k"] - 0.39307314951247446) <= 1e-9, repr(iss["k"]))

    eff = a["effects"]
    leg("L6 window and universe both lower the floor, and the window moves it more",
        eff["window_effect_pp"] > 0 and eff["universe_effect_pp"] > 0
        and eff["window_effect_pp"] > eff["universe_effect_pp"], repr(eff))
    leg("L7 the gap decomposition adds up: full/all - common/graded == total",
        abs((eff["floor_full_all"] - eff["floor_common_graded"]) - eff["total_gap_k"]) <= 1e-6,
        "%r vs %r" % (eff.get("total_gap_k"),
                      eff.get("floor_full_all", 0) - eff.get("floor_common_graded", 0)))
    # a step path: grade the universe first, then shrink the window (or the reverse);
    # the two shares must add to the total or one of the corners was read wrong
    leg("L8 universe-at-full-window plus window-at-graded reconstructs the total gap",
        abs((eff["universe_effect_full_window_pp"] + eff["window_effect_pp"])
            - eff["total_gap_pp"]) <= 0.02,
        "%r vs %r" % (eff["universe_effect_full_window_pp"] + eff["window_effect_pp"],
                      eff["total_gap_pp"]))

    # 9. a broken identity is refused, not computed away
    bad = _fixture()
    bad["cells"]["window"]["k"] = 0.5
    a2 = assess(bad, perm)
    leg("L9 a cell whose k*beta is not the target makes the face refuse to call it a reciprocal",
        a2["verdict"] == VERDICT_IDENTITY_BROKEN, repr(a2["verdict"]))

    # 10. an incomplete 2x2 is unreadable -- the missing corner is not zero
    miss = _fixture()
    del miss["cells"]["universe"]
    a3 = assess(miss, perm)
    leg("L10 a missing corner reads as unreadable, not as a smaller effect",
        a3["verdict"] == VERDICT_UNREADABLE and a3.get("effects") is not None,
        repr(a3["verdict"]))

    # 11. missing receipts
    leg("L11 no rulers receipt is UNREADABLE", assess(None, perm)["verdict"] == VERDICT_UNREADABLE, "")
    leg("L12 no beta target on either receipt is UNREADABLE",
        assess(fx, {})["verdict"] == VERDICT_UNREADABLE, "")

    # 13. the reciprocal is the tape, not the rule: double the beta, halve the k
    def c2(beta):
        return {"k": 0.2 / beta, "beta": beta, "bars": 500, "window": "full",
                "universe": "graded"}
    fx2 = {"cells": {"baseline_published": c2(0.4), "window": c2(0.4),
                     "universe": c2(0.4), "window_x_universe": c2(0.8)}}
    a4 = assess(fx2, perm)
    leg("L13 doubling the largest beta halves the issued size",
        abs(a4["issuing_cell"]["k"] - 0.25) < 1e-9, repr(a4["issuing_cell"]))

    # 14. money is reported on the ticket's own NAV, not a hard-coded million
    perm2 = dict(perm, nav_cny=2_000_000.0)
    a5 = assess(fx, perm2)
    leg("L14 effects are priced on the NAV handed in",
        abs(a5["effects"]["window_effect_cny"] - 2 * a["effects"]["window_effect_cny"]) <= 1e-2,
        "%r vs %r" % (a5["effects"]["window_effect_cny"], a["effects"]["window_effect_cny"]))

    # 15. a bar-poor cell must not issue the floor
    thin = _fixture()
    thin["cells"]["window_x_universe"]["bars"] = 12
    a6 = assess(thin, perm)
    leg("L15 a 12-bar cell is not allowed to issue the floor",
        a6["issuing_cell"]["cell"] != "window_x_universe", repr(a6.get("issuing_cell")))

    # 16. the sentence always names the issuing cell and its bar count
    leg("L16 the sentence names the issuing cell and its bars",
        "window_x_universe" in a["sentence"] and "306" in a["sentence"], a["sentence"])

    if fails:
        for f in fails:
            print("FAIL " + f)
        print("selftest %d/%d" % (total - len(fails), total))
        return 1
    print("selftest %d/%d" % (total, total))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "check", "selftest", "md"])
    a = ap.parse_args(argv)
    if a.mode == "selftest":
        return selftest()
    if a.mode == "check":
        return check()
    if a.mode == "md":
        face = run(write=False)
        print("\n".join(md_lines(face)))
        return 0
    face = run(write=True)
    print(json.dumps(face.get("effects"), ensure_ascii=False))
    print(face.get("sentence"))
    return 0


if __name__ == "__main__":
    sys.exit(main())