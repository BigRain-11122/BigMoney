"""Which of the desk's year-axis refusals can see the next year at all?

r1441 tested ONE caliber -- Y4 (top-2 year share <= 0.70) -- and found it blind:
concentration computed on a finished window carries no information about the year
that follows it.  But the supply floor refuses candidates on FOUR year-axis checks
(Y1 positive-years share, Y2 median year, Y3 worst year, Y4 top-2 share), and all
four live candidates are currently refused on Y4 alone.  So the question that has
been open for forty rounds is not "is Y4 blind" (that is answered) but:

    of the checks the gate actually owns, which ones carry forward information,
    and does re-pointing the refusal onto those change what the floor refuses?

The assay is the same one r1441 froze, extended per check: price a frozen grid of
arms with the published engine (imported, never re-implemented), cut each arm into
fixed-length rolling windows, read each check's own statistic from the window's own
years (via candidate_year_gate.year_metrics -- the frozen implementation, not a
copy), and rank-correlate it with the return of the year that follows the window.

DIRECTION IS FROZEN BEFORE READING.  Three checks are "higher is a stronger book"
(Y1 share of positive years, Y2 median year, Y3 worst year), one is "higher is a
more concentrated book" (Y4 top-2 share).  The sign is declared per check and the
correlation is *aligned* to the gate's own semantics, so:

    CARRIES_FORWARD  aligned rho >= +0.35 and perm p < 0.10  -> refusing on the bad
                     side of this check has protected money
    BACKWARDS        aligned rho <= -0.35 and perm p < 0.10  -> the check refuses
                     books that go on to do better; worse than decorative
    BLIND            otherwise

A second, deliberately separate leg answers the operational question without
touching any line: read the four published candidate receipts and re-issue the
verdict with Y4 dropped from the refusal set (rule frozen below).  That leg is a
SCENARIO, printed as such -- it does not change the gate, and it only becomes an
option if the forward leg says Y4 is the blind one and something else is not.

Usage:
    python scripts/etf_book_gate_forward_content.py run
    python scripts/etf_book_gate_forward_content.py --check
    python scripts/etf_book_gate_forward_content.py --selftest
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import candidate_year_gate as G  # noqa: E402
import etf_book_ruler_forward as F  # noqa: E402
import etf_composite_pf as E  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import etf_robust_pf as R  # noqa: E402

OUT_DIR = os.path.join(ROOT, "results", "etf_book_gate_forward")
OUT = os.path.join(OUT_DIR, "GATE-FORWARD.json")

COST = 0.0010

# ---- frozen before any reading ------------------------------------------------
CRITERIA = {
    "assay": "each year-axis check's own statistic on a leading fixed-length window "
             "vs the NEXT calendar year's return of the same arm",
    "window_years": 3,
    "window_years_secondary": 4,
    "forward_years": 1,
    "signs": {
        "Y1_positive_years_share": +1,
        "Y2_median_positive": +1,
        "Y3_worst_year": +1,
        "Y4_top2_share": -1,
    },
    "sign_why": "aligned rho is computed in the gate's own direction: for Y1/Y2/Y3 a "
                "higher value is a stronger book, for Y4 a higher value is a more "
                "concentrated (worse) book; a refusal only protects money if the bad "
                "side of its statistic predicts a worse forward year",
    "decision": {
        "CARRIES_FORWARD": "aligned_rho >= +0.35 and perm_p < 0.10",
        "BACKWARDS": "aligned_rho <= -0.35 and perm_p < 0.10",
        "BLIND": "otherwise",
    },
    "severity_worst_first": ["BACKWARDS", "BLIND", "NOT_ASSESSED", "CARRIES_FORWARD"],
    "severity_why": "a backwards check is worse than a decorative one: it refuses the "
                    "books that then do better",
    "min_cells": 12,
    "permutations": 2000,
    "seed": 20261108,
    "partial_year_rule": "a cell whose leading window OR forward year touches a partial "
                         "year is published but excluded from the pooled reading",
    "repoint_rule": "SCENARIO ONLY, no gate is changed: with a check dropped from the "
                    "refusal set, ADMIT = every remaining check passes, CONDITIONAL = "
                    "exactly one remaining check fails, REFUSE = two or more fail; "
                    "capacity column is left exactly as published",
    "repoint_candidates": {
        "nobond_vt08_adopted": "results/etf_book_phase_gate.json",
        "nobond_base": "results/etf_book_phase_gate.json",
        "nobond_vt08_floor_050": "results/etf_book_phase_gate.json",
        "all_classes_published": "results/etf_book_year_gate/YEAR-GATE.json",
    },
    "grid": "full (width 3/5/8 x rebalance 10/20/40 x vol target on/off) -- the same "
            "family the desk runs, varying only width and rebalance",
}

YEAR_CHECKS = ["Y1_positive_years_share", "Y2_median_positive",
               "Y3_worst_year", "Y4_top2_share"]


# ---- pure helpers (every one has a selftest leg) ------------------------------
def window_metrics(table: dict, start: int, length: int) -> dict | None:
    """Gate metrics on one window, computed by the frozen gate implementation."""
    rows = []
    for y in range(start, start + length):
        if y not in table:
            return None
        blk = table[y]
        rows.append({"year": str(y), "net_pct": blk["net_pct"],
                     "cohorts": blk["cohorts"], "partial": blk["partial"]})
    return G.year_metrics(rows)


def stat_of(check: str, m: dict) -> float | None:
    if not m or m.get("years", 0) <= 0:
        return None
    if check == "Y1_positive_years_share":
        return m["positive_years"] / float(m["years"])
    if check == "Y2_median_positive":
        return m["median"]
    if check == "Y3_worst_year":
        return m["worst"]
    if check == "Y4_top2_share":
        return m["top2_share"]
    raise KeyError(check)


def aligned(rho: float | None, check: str) -> float | None:
    if rho is None:
        return None
    return rho * CRITERIA["signs"][check]


def word_of(aligned_rho: float | None, p: float | None, cells: int) -> str:
    if cells < CRITERIA["min_cells"] or aligned_rho is None or p is None:
        return "NOT_ASSESSED"
    if aligned_rho >= 0.35 and p < 0.10:
        return "CARRIES_FORWARD"
    if aligned_rho <= -0.35 and p < 0.10:
        return "BACKWARDS"
    return "BLIND"


def combine(a: str, b: str) -> dict:
    for word in CRITERIA["severity_worst_first"]:
        if word in (a, b):
            return {"windows": [a, b], "composite": word, "agree": a == b}
    return {"windows": [a, b], "composite": "NOT_ASSESSED", "agree": a == b}


def repoint(failing: list[str], dropped: str) -> dict:
    """Scenario verdict under CRITERIA['repoint_rule']; nothing is written back."""
    remaining = [c for c in failing if c != dropped and c in YEAR_CHECKS]
    if not remaining:
        verdict = "ADMIT"
    elif len(remaining) == 1:
        verdict = "CONDITIONAL"
    else:
        verdict = "REFUSE"
    return {"dropped": dropped, "failing_published": sorted(failing),
            "failing_remaining": sorted(remaining), "verdict": verdict,
            "changed": verdict != ("ADMIT" if not failing else
                                   ("CONDITIONAL" if len(failing) == 1 else "REFUSE"))}


# ---- the panel leg ------------------------------------------------------------
def build_grid(grid: list[dict], window_years: int) -> tuple[list[dict], dict, dict]:
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    score = E.build_score(close[cols], amt[cols], feats)

    cells: list[dict] = []
    panel = {"arms": [], "bars": int(len(close)),
             "from": str(close.index[0].date()), "to": str(close.index[-1].date()),
             "flips_repaired": int(n_flip)}
    per_arm: dict[str, dict] = {}
    for a in grid:
        name = F.arm_name(a)
        ser, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], score,
                                          a["rebal"], a["n_hold"], COST,
                                          vol_target=a["vol_target"])
        ser = ser.dropna()
        if len(ser) < 400:
            continue
        table = F.year_table(ser)
        arm_cells = F.cells_for_arm(name, table, window_years)
        gate_stats = []
        for c in arm_cells:
            start = int(c["window"].split("-")[0])
            m = window_metrics(table, start, window_years)
            if m is None:
                continue
            stats = {chk: stat_of(chk, m) for chk in YEAR_CHECKS}
            c["gate"] = stats
            c["leading_years"] = m["years"]
            gate_stats.append(stats)
            cells.append(c)
        per_arm[name] = {"turnover": round(float(turn), 4),
                         "years": {str(y): round(v["net_pct"], 4)
                                   for y, v in sorted(table.items())},
                         "partial_years": [str(y) for y, v in sorted(table.items())
                                           if v["partial"]],
                         "cells": len(arm_cells)}
        panel["arms"].append(name)
    return cells, panel, per_arm


def pooled_check(cells: list[dict], check: str) -> dict:
    use = [c for c in cells
           if not c["leading_partial"] and not c["forward_partial"]
           and c.get("gate", {}).get(check) is not None]
    xs = [float(c["gate"][check]) for c in use]
    ys = [float(c["forward_pct"]) for c in use]
    rho = F.spearman(xs, ys)
    p = F.perm_p(xs, ys, rho, CRITERIA["permutations"], CRITERIA["seed"])
    ar = aligned(rho, check)
    return {"check": check, "sign": CRITERIA["signs"][check],
            "cells": len(use), "cells_published": len(cells),
            "excluded_partial": len(cells) - len(use),
            "rho": None if rho is None else round(rho, 4),
            "aligned_rho": None if ar is None else round(ar, 4),
            "perm_p": None if p is None else round(p, 4),
            "verdict": word_of(ar, p, len(use))}


def receipts() -> dict:
    """Read the published refusals, one entry per PHASE, not one per book.

    A book's refusal is not one reading: the phase gate publishes the same book from
    several decision phases and the failing set moves between them (nobond_base fails
    nothing in 2 phases and fails two checks in 1).  Reporting only the first phase
    would print a clean verdict for a book whose phases disagree -- the r1325 lesson.
    """
    out = {}
    with io.open(os.path.join(ROOT, "results", "etf_book_phase_gate.json"),
                 encoding="utf-8") as f:
        ph = json.load(f)
    for b in ph.get("books", []):
        rows = b.get("phase_rows") or []
        if not rows:
            continue
        out[b["book"]] = {
            "source": "results/etf_book_phase_gate.json",
            "verdict_published": (b.get("adjudication") or {}).get("state")
                                 if isinstance(b.get("adjudication"), dict)
                                 else b.get("adjudication"),
            "refusal_survival": b.get("refusal_survival"),
            "phases": [{"start": r.get("start"),
                        "failing": list(r.get("failing_checks") or [])}
                       for r in rows]}
    ygp = os.path.join(ROOT, "results", "etf_book_year_gate", "YEAR-GATE.json")
    if os.path.exists(ygp):
        with io.open(ygp, encoding="utf-8") as f:
            yg = json.load(f)
        for b in yg.get("books", []):
            checks = b.get("checks") or {}
            failing = [k for k in YEAR_CHECKS if checks.get(k) is False]
            out[b.get("book")] = {"source": "results/etf_book_year_gate/YEAR-GATE.json",
                                  "verdict_published": b.get("verdict"),
                                  "phases": [{"start": yg.get("asof"),
                                              "failing": failing}]}
    return out


def refusal_provenance_leg() -> dict:
    """If Y4 is blind, the refusal is said to survive on a 'trusted' ruler. Which one?

    Read, never re-derived: results/etf_book_year_caliber.json publishes which calibers
    can adjudicate themselves and what each said; the phase receipt says a refusal
    "survives the trusted ruler".  Those two published facts are put side by side here
    so the second line of defence can be read without opening two files.
    """
    p = os.path.join(ROOT, "results", "etf_book_year_caliber.json")
    if not os.path.exists(p):
        return {"state": "unreadable", "why": "results/etf_book_year_caliber.json missing"}
    with io.open(p, encoding="utf-8") as f:
        d = json.load(f)
    trusted = d.get("trusted_calibers") or []
    verdicts = d.get("trusted_verdicts") or {}
    composite = d.get("composite_verdict")
    if not trusted or not verdicts:
        dec = d.get("decision") or {}
        trusted = trusted or (dec.get("trusted_calibers") or [])
        verdicts = verdicts or (dec.get("trusted_verdicts") or {})
        composite = composite or dec.get("composite_verdict")
    failing = [c for c in trusted if verdicts.get(c) == "FAIL"]
    surviving = []
    rests_on_unadjudicable = []
    for b in (results_phase_gate().get("books") or []):
        rs = b.get("refusal_survival") or {}
        states = rs.get("states") or {}
        refusing = [c for c, w in states.items() if w == "FAIL" and c in trusted]
        weak = [c for c in refusing if verdicts.get(c) == "FAIL"]
        surviving.append({"book": b.get("book"),
                          "word": rs.get("word"),
                          "trusted_states": states,
                          "trusted_refusing": refusing,
                          "refusing_calibers_that_fail_self_adjudication": weak})
        if refusing and len(weak) == len(refusing):
            rests_on_unadjudicable.append(b.get("book"))
    return {
        "caliber_receipt": "results/etf_book_year_caliber.json",
        "trusted_calibers": trusted,
        "trusted_self_adjudication": verdicts,
        "trusted_that_fail_self_adjudication": sorted(failing),
        "composite_verdict": composite,
        "phase_receipts": surviving,
        "refusal_rests_only_on_unadjudicable_calibers": sorted(rests_on_unadjudicable),
        "reading": (
            "the refusal survives only through calibers that fail their own "
            "self-adjudication (%s): the second line of defence is the same question "
            "asked twice" % ",".join(sorted(failing))
            if rests_on_unadjudicable and len(rests_on_unadjudicable) == len(surviving)
            else "at least one refusing caliber passes its own self-adjudication; the "
                 "refusal's second line stands on that one"),
    }


def results_phase_gate() -> dict:
    with io.open(os.path.join(ROOT, "results", "etf_book_phase_gate.json"),
                 encoding="utf-8") as f:
        return json.load(f)


def repoint_leg() -> dict:
    rp = receipts()
    rows = []
    for name, rec in sorted(rp.items()):
        per_phase = []
        for ph in rec["phases"]:
            a = repoint(ph["failing"], dropped=None)["verdict"]
            b = repoint(ph["failing"], dropped="Y4_top2_share")["verdict"]
            per_phase.append({"start": ph["start"], "failing": ph["failing"],
                              "as_published": a, "without_Y4": b, "flips": a != b})
        words_no_y4 = [p["without_Y4"] for p in per_phase]
        stable = len(set(words_no_y4)) == 1
        rows.append({"book": name, "source": rec["source"],
                     "verdict_published": rec["verdict_published"],
                     "phases": len(per_phase),
                     "phases_flipped": sum(1 for p in per_phase if p["flips"]),
                     "without_Y4_words": sorted(set(words_no_y4)),
                     "without_Y4_stable_across_phases": stable,
                     "detail": per_phase})
    return {"rule": CRITERIA["repoint_rule"], "candidates": rows,
            "books_all_phases_admit_without_Y4": [
                r["book"] for r in rows
                if r["without_Y4_words"] == ["ADMIT"] and r["phases_flipped"] > 0],
            "n_flipped": sum(1 for r in rows if r["phases_flipped"]),
            "note": "scenario only: no gate line is changed by this file, and a book "
                    "that only admits in some phases is printed as phase-unstable "
                    "(r1325/E188: adoption needs a path test, not one decision sequence)"}


def run() -> int:
    t0 = time.time()
    wy = CRITERIA["window_years"]
    wy2 = CRITERIA["window_years_secondary"]
    grid = [{"n_hold": n, "rebal": r, "vol_target": vt}
            for vt in (0.08, None) for n in (3, 5, 8) for r in (10, 20, 40)]

    cells, panel, per_arm = build_grid(grid, wy)
    cells2, panel2, _ = build_grid(grid, wy2)

    reads = {}
    for chk in YEAR_CHECKS:
        primary = pooled_check(cells, chk)
        secondary = pooled_check(cells2, chk)
        comp = combine(primary["verdict"], secondary["verdict"])
        reads[chk] = {"primary_3y": primary, "secondary_4y": secondary,
                      "windows": comp["windows"], "composite": comp["composite"],
                      "windows_agree": comp["agree"]}

    words = {k: v["composite"] for k, v in reads.items()}
    informed = [k for k, w in words.items() if w == "CARRIES_FORWARD"]
    dead = [k for k, w in words.items() if w == "BLIND"]
    backwards = [k for k, w in words.items() if w == "BACKWARDS"]

    rp = repoint_leg()
    rp["refusal_provenance"] = refusal_provenance_leg()
    if not informed:
        judgement = "NO_YEAR_CHECK_SEES_FORWARD"
        why = ("every check the year gate refuses on is blind to the next year; the "
               "supply floor is not a risk control, it is a shape filter")
    elif len(informed) < len(YEAR_CHECKS):
        judgement = "PARTIAL_REPOINT"
        why = ("only %s carries forward information; refusing on %s protects nothing"
               % (",".join(sorted(informed)), ",".join(sorted(dead))))
    else:
        judgement = "ALL_CHECKS_SEE_FORWARD"
        why = "the year gate's refusals are all forward-informative; the floor stands"

    payload = {
        "face": "etf_book_gate_forward_content",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": panel["to"],
        "question": "which of the year gate's four refusals can see the year after?",
        "criteria": CRITERIA,
        "panel": panel,
        "arms": per_arm,
        "cells": len(cells),
        "forward_relation": reads,
        "judgement": judgement,
        "judgement_why": why,
        "informed_checks": sorted(informed),
        "blind_checks": sorted(dead),
        "backwards_checks": sorted(backwards),
        "repoint": rp,
        "honest": {
            "one_family": "the arms are one ETF family; most cells share one bet, so "
                          "the cross-section is narrower than the cell count suggests",
            "decision_points": "at most three forward years per arm; this can settle "
                               "whether a check carries forward information, never a "
                               "strategy question (r1316 power floor)",
            "no_line_changed": "no gate line, no refusal set and no production book was "
                               "modified by this file",
            "arithmetic_floor": "on a 3-year window all-positive record, Y4 cannot go "
                                "below 0.667 and Y1 cannot reach 0.70 unless all three "
                                "years are positive -- part of 'never passes' is the "
                                "window's arithmetic, printed rather than netted out",
        },
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = OUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp, OUT)
    print(json.dumps({"judgement": judgement, "words": words,
                      "cells": len(cells), "repoint_flips": rp["n_flipped"],
                      "out": os.path.relpath(OUT, ROOT)}, ensure_ascii=False))
    print("  forward: " + " | ".join(
        "%s a3=%s p3=%s 4y=%s" % (k, v["primary_3y"]["aligned_rho"],
                                  v["primary_3y"]["perm_p"], v["composite"])
        for k, v in reads.items()))
    return 0


def check() -> int:
    """Fast structural check: criteria frozen, receipts readable, rule self-consistent."""
    bad = []
    if sorted(CRITERIA["signs"]) != sorted(YEAR_CHECKS):
        bad.append("signs must cover exactly the four year checks")
    if CRITERIA["signs"]["Y4_top2_share"] != -1:
        bad.append("Y4 must be signed negative (higher concentration = worse)")
    rp = repoint_leg()
    if len(rp["candidates"]) < 3:
        bad.append("fewer than three candidate receipts readable")
    for r in rp["candidates"]:
        if r["verdict_published"] not in ("ADMIT", "CONDITIONAL", "REFUSE",
                                          "UNADJUDICABLE_PHASE", "CAPACITY_LIMITED"):
            bad.append("unexpected published verdict for %s" % r["book"])
    print(json.dumps({"check": "ok" if not bad else "FAIL", "problems": bad,
                      "candidates": len(rp["candidates"]),
                      "flips_without_Y4": rp["n_flipped"]}, ensure_ascii=False))
    return 0 if not bad else 1


def selftest() -> int:
    legs = []

    def leg(name, fn):
        try:
            legs.append((name, bool(fn())))
        except Exception as exc:  # noqa: BLE001
            legs.append((name, "ERR:%s" % exc))

    leg("ranks ties share the average rank",
        lambda: F.ranks([1.0, 2.0, 2.0, 3.0]) == [1.0, 2.5, 2.5, 4.0])
    leg("spearman monotone = +1",
        lambda: abs(F.spearman([1, 2, 3, 4], [10, 20, 30, 40]) - 1.0) < 1e-12)
    leg("spearman reversed = -1",
        lambda: abs(F.spearman([1, 2, 3, 4], [40, 30, 20, 10]) + 1.0) < 1e-12)

    def aligned_sign_leg():
        # a check where higher is better, forward returns rising with it: aligned > 0
        rho = F.spearman([1, 2, 3, 4], [1, 2, 3, 4])
        return aligned(rho, "Y1_positive_years_share") > 0.99 and \
            aligned(rho, "Y4_top2_share") < -0.99
    leg("aligned rho flips sign for Y4 only", aligned_sign_leg)

    leg("word: carries forward needs strength AND significance",
        lambda: word_of(0.60, 0.01, 20) == "CARRIES_FORWARD"
        and word_of(0.60, 0.50, 20) == "BLIND"
        and word_of(-0.60, 0.01, 20) == "BACKWARDS")
    leg("word: too few cells is NOT_ASSESSED, never a pass",
        lambda: word_of(0.9, 0.001, 5) == "NOT_ASSESSED")
    leg("combine takes the worst word, never an average",
        lambda: combine("CARRIES_FORWARD", "BLIND")["composite"] == "BLIND"
        and combine("CARRIES_FORWARD", "BACKWARDS")["composite"] == "BACKWARDS")
    leg("severity order matches the frozen list",
        lambda: CRITERIA["severity_worst_first"][0] == "BACKWARDS"
        and CRITERIA["severity_worst_first"][-1] == "CARRIES_FORWARD")

    table = {2020: {"net_pct": 10.0, "cohorts": 4, "partial": False},
             2021: {"net_pct": 20.0, "cohorts": 4, "partial": False},
             2022: {"net_pct": -5.0, "cohorts": 4, "partial": False},
             2023: {"net_pct": 3.0, "cohorts": 1, "partial": True}}

    def window_uses_frozen_gate():
        m = window_metrics(table, 2020, 3)
        return (m["years"] == 3 and m["positive_years"] == 2
                and abs(stat_of("Y1_positive_years_share", m) - 2 / 3) < 1e-12
                and m["worst"] == -5.0 and m["median"] == 10.0)
    leg("window metrics come from candidate_year_gate.year_metrics", window_uses_frozen_gate)

    def y4_none_when_sum_nonpositive():
        m = G.year_metrics([{"year": "2020", "net_pct": -1.0, "cohorts": 4, "partial": False},
                            {"year": "2021", "net_pct": -2.0, "cohorts": 4, "partial": False}])
        return m["top2_share"] is None and stat_of("Y4_top2_share", m) is None
    leg("Y4 is None (excluded) when the annual sum is not positive", y4_none_when_sum_nonpositive)

    def repoint_rules():
        only_y4 = repoint(["Y4_top2_share"], "Y4_top2_share")["verdict"] == "ADMIT"
        y3y4 = repoint(["Y3_worst_year", "Y4_top2_share"], "Y4_top2_share")["verdict"] \
            == "CONDITIONAL"
        two = repoint(["Y1_positive_years_share", "Y3_worst_year",
                       "Y4_top2_share"], "Y4_top2_share")["verdict"] == "REFUSE"
        keep = repoint(["Y4_top2_share"], None)["verdict"] == "CONDITIONAL"
        return only_y4 and y3y4 and two and keep
    leg("repoint rule: 0 / 1 / 2 remaining failures map to ADMIT / CONDITIONAL / REFUSE",
        repoint_rules)

    def partial_exclusion():
        cells = [{"leading_partial": True, "forward_partial": False, "forward_pct": 5.0,
                  "gate": {"Y1_positive_years_share": 1.0}},
                 {"leading_partial": False, "forward_partial": False, "forward_pct": 5.0,
                  "gate": {"Y1_positive_years_share": 0.5}}]
        out = pooled_check(cells, "Y1_positive_years_share")
        return out["cells"] == 1 and out["excluded_partial"] == 1
    leg("partial-touching cells are excluded from the pooled reading", partial_exclusion)

    def degenerate_constant_check():
        cells = [{"leading_partial": False, "forward_partial": False, "forward_pct": 1.0 + i,
                  "gate": {"Y2_median_positive": 7.0}} for i in range(15)]
        out = pooled_check(cells, "Y2_median_positive")
        return out["rho"] is None and out["verdict"] == "NOT_ASSESSED"
    leg("a constant statistic yields NOT_ASSESSED, not a claim", degenerate_constant_check)

    def forward_year_is_the_next_one():
        c = F.cells_for_arm("x", table, 2)
        return bool(c) and all(x["forward_year"] == int(x["window"].split("-")[0]) + 2
                               for x in c)
    leg("the forward year is the one immediately after the window", forward_year_is_the_next_one)

    passed = sum(1 for _, ok in legs if ok is True)
    for name, ok in legs:
        print(("PASS  " if ok is True else "FAIL  ") + name +
              ("" if ok is True else " -> %r" % (ok,)))
    print("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def repoint_only() -> int:
    """Recompute the scenario leg on an existing receipt (the panel leg is expensive).

    The forward reading does not depend on the receipts and vice versa, so the cheap
    half can be re-derived without repricing 18 arms -- printed here so a reader can
    see the two legs were produced by one file.
    """
    if not os.path.exists(OUT):
        print("FATAL: run the panel leg first (%s missing)" % OUT)
        return 2
    with io.open(OUT, encoding="utf-8") as f:
        d = json.load(f)
    rp = repoint_leg()
    rp["refusal_provenance"] = refusal_provenance_leg()
    d["repoint"] = rp
    d["repoint_regenerated"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    tmp = OUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    os.replace(tmp, OUT)
    print(json.dumps({"repoint_flips": rp["n_flipped"],
                      "admit_in_every_phase_without_Y4":
                          rp["books_all_phases_admit_without_Y4"],
                      "refusal_provenance":
                          rp["refusal_provenance"].get("reading")}, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.check:
        return check()
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    if args.cmd == "repoint":
        return repoint_only()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())