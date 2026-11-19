#!/usr/bin/env python3
"""The same gate over every start in one rebalance block, not five weekly samples.

``etf_book_phase_admission`` prices the book at five weekly starts and found 4 ADMIT /
1 DENY (2020-01-22, OOS Sharpe 0.693 against a 0.70 line). It printed the honest limits of
that design itself: "five weekly starts are one rebalance block, not a sample of all
calendars; a sixth start would be a sixth coin toss, not new evidence".

This face closes that hole the only way it can be closed: it prices **every** start of the
decision grid inside one rebalance block (25 consecutive bar starts from 2020-01-01, which
covers the 20-bar rebalance period in full and still reaches the latest start the phase face
used, 2020-02-04). Nothing new is decided here:

* the per-start verdicts and the four-word aggregate are ``etf_book_phase_admission``'s own
  functions (imported, not retyped);
* the spread rule is ``etf_book_phase_admission.spread_state`` (itself pinned against
  ``candidate_year_gate_phases.adjudicate``);
* the three rulers are ``candidate_year_gate``'s thresholds (imported).

What is new is one reading the five-point face could not produce: **how far apart two
adjacent starts put the same ruler**. A refusal that sits 0.007 from the line, on a ruler
whose adjacent starts move by an order of magnitude more, is not a measurement of the book.
That comparison is a description of resolution, never an admission line -- the admission
lines remain YEAR-GATE's and the phase face's, and this face does not move them.

    python scripts/etf_book_start_grid.py run       # ~3-4 min (25 repricings)
    python scripts/etf_book_start_grid.py check     # re-derive + cross-face + freshness
    python scripts/etf_book_start_grid.py selftest  # fixtures only
"""

import argparse
import io
import json
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

import pandas as pd  # noqa: E402

import candidate_year_gate as G  # noqa: E402
import etf_book_phase_admission as PA  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402
import etf_equity_alpha as A  # noqa: E402

OUT = os.path.join(ROOT, "results", "etf_book_start_grid.json")
GATE = PA.GATE
PHASE_FACE = PA.OUT
BOOK = PA.BOOK
# The block start and the number of starts. 25 covers the 20-bar rebalance period in full
# and reaches 2020-02-04, the latest first_bar the phase face priced (2020-01-29 -> 02-04).
GRID_FROM = "2020-01-01"
GRID_STARTS = 25
REBAL_PERIOD = 20  # engine's own rebalance, asserted below against the grid width


def grid_starts(index, n=GRID_STARTS):
    """The first n bars on or after GRID_FROM -- a pure slice of the panel's own index."""
    cut = pd.Timestamp(GRID_FROM)
    return [d for d in index if d >= cut][:n]


def one_ruler(rows, key):
    """Per-start verdicts of ONE ruler, so 'these starts disagree' means that ruler did."""
    out = []
    for r in rows:
        v = (r.get("checks") or {}).get(key)
        out.append("INSUFFICIENT" if v is None else ("ADMIT" if v else "DENY"))
    return out


def _margins(rows, key, value_key, line):
    """Signed distance to the line for every readable row, in row order."""
    out = []
    for r in rows:
        v = r.get(value_key)
        if v is None:
            continue
        out.append({"start": r.get("start"), "verdict": r.get("verdict"),
                    "ruler": key, "value": round(float(v), 4),
                    "margin": round(float(v) - float(line), 4)})
    return out


def distribution(rows, s1_line, a1_line):
    """Describe the spread of one block of starts. Pure; no verdict is invented here.

    Two numbers matter for a reader of a refusal: the distance between the refusing start
    and the line, and the size of the step the same ruler takes when the start moves by one
    bar. If the first is smaller than the second, the refusal is inside the resolution of
    the start grid -- which is a statement about measurement, not about the book.
    """
    known = [r for r in rows if r.get("verdict") in ("ADMIT", "DENY", "INSUFFICIENT")]
    out = {"starts": len(known),
           "admit": sum(1 for r in known if r["verdict"] == "ADMIT"),
           "deny": sum(1 for r in known if r["verdict"] == "DENY"),
           "insufficient": sum(1 for r in known if r["verdict"] == "INSUFFICIENT")}
    if not known:
        out.update(state="CANNOT_VERIFY", reason="no start published a verdict")
        return out

    for key, value_key, line in (("S1_oos_sharpe", "oos_sharpe", s1_line),
                                 ("A1_cagr_after_cost", "cagr_pct", a1_line)):
        vals = [float(r[value_key]) for r in known if r.get(value_key) is not None]
        if not vals:
            out[key] = {"readable": 0}
            continue
        jumps = [round(abs(b - a), 4) for a, b in zip(vals, vals[1:])]
        block = {"readable": len(vals), "line": round(float(line), 4),
                 "min": round(min(vals), 4), "median": round(statistics.median(vals), 4),
                 "max": round(max(vals), 4), "spread": round(max(vals) - min(vals), 4),
                 "above_line": sum(1 for v in vals if v >= line),
                 "below_line": sum(1 for v in vals if v < line),
                 "neighbour_jump_median": round(statistics.median(jumps), 4) if jumps else None,
                 "neighbour_jump_max": round(max(jumps), 4) if jumps else None}
        margins = _margins(known, key, value_key, line)
        refusing = [m for m in margins if m["margin"] < 0]
        jm = block["neighbour_jump_median"]

        def place(m):
            """One refusal against the resolution of the grid."""
            if m is None:
                return None
            inside = jm is not None and abs(m["margin"]) < jm
            return {"start": m["start"], "value": m["value"], "margin": m["margin"],
                    "distance_to_line": round(abs(m["margin"]), 4),
                    "inside_start_noise": bool(inside),
                    "vs_one_bar_step": None if not jm else round(abs(m["margin"]) / jm, 4)}

        # "closest" and "worst" are two different questions and a reader needs both: the
        # closest refusal asks whether the line can be located at all, the worst asks how
        # bad a start can get. Printing only the closest would let a real refusal hide
        # behind a coin-flip one -- the "missing one member" shape this repo keeps meeting.
        block["refusals"] = [place(m) for m in refusing]
        block["closest_refusal"] = place(min(refusing, key=lambda m: abs(m["margin"]))) \
            if refusing else None
        block["worst_refusal"] = place(min(refusing, key=lambda m: m["margin"])) \
            if refusing else None
        block["refusal_inside_start_noise"] = (block["closest_refusal"] or {}).get(
            "inside_start_noise")
        block["any_refusal_outside_start_noise"] = any(
            r["inside_start_noise"] is False for r in block["refusals"])
        if not refusing:
            block["resolution_sentence"] = (
                "no start refuses on this ruler, so there is no refusal to place against "
                "the %.4f median one-bar step" % (jm or 0.0))
        else:
            cl, wo = block["closest_refusal"], block["worst_refusal"]
            block["resolution_sentence"] = (
                "the closest refusal (%s) sits %.4f from the %.2f line and the worst (%s) "
                "sits %.4f away, while moving the start by one bar moves this ruler by a "
                "median of %.4f: the closest refusal %s the grid's resolution and the worst "
                "one %s"
                % (cl["start"], cl["distance_to_line"], float(line),
                   wo["start"], wo["distance_to_line"], jm or 0.0,
                   "lies inside" if cl["inside_start_noise"] else "lies outside",
                   "lies inside" if wo["inside_start_noise"] else "lies outside"))
        out[key] = block
    return out


def run() -> int:
    t0 = time.time()
    close, openp, amt, sc, n_flip = S.nobond_universe()
    picks, advs, adv_weakest = PA.live_picks(sc, amt)
    starts = grid_starts(openp.index)
    rows = []
    for start in starts:
        label = str(pd.Timestamp(start).date())
        ser, turn = PA.P.arm(close, openp, amt, sc, 0.08, 0.0, label)
        osr = G.oos_sharpe(ser)
        cagr = A.stats2(ser, BOOK).get("cagr")
        cagr_pct = None if cagr is None else round(float(cagr) * 100.0, 4)
        blk = G.decision_block(osr, cagr_pct, adv_weakest, len(picks) or None)
        rows.append({"start": label, "verdict": blk["verdict"], "oos_sharpe": osr,
                     "cagr_pct": cagr_pct, "checks": blk["checks"],
                     "failed_checks": blk["failed_checks"],
                     "bars": int(len(ser.dropna())),
                     "first_bar": str(pd.Timestamp(ser.dropna().index[0]).date()),
                     "last_bar": str(pd.Timestamp(ser.dropna().index[-1]).date()),
                     "turnover_per_side": round(float(turn), 3)})
        print("  %s -> %-12s oos_sharpe %s cagr %s"
              % (label, blk["verdict"], osr, cagr_pct), flush=True)

    agg = PA.aggregate(rows)
    print("%s over %d starts -> %s (%s)"
          % (BOOK, len(rows), agg["state"], agg.get("reason")), flush=True)

    spread = {
        "rule_source": "etf_book_phase_admission.spread_state (pinned against "
                       "candidate_year_gate_phases.adjudicate)",
        "S1": PA.spread_state([r.get("oos_sharpe") for r in rows],
                              one_ruler(rows, "S1_oos_sharpe"), G.GATE_OOS_SHARPE_MIN),
        "A1": PA.spread_state([r.get("cagr_pct") for r in rows],
                              one_ruler(rows, "A1_cagr_after_cost"), G.GATE_CAGR_MIN_PCT),
    }
    spread["S1"]["ruler"] = "S1_oos_sharpe"
    spread["A1"]["ruler"] = "A1_cagr_after_cost"

    dist = distribution(rows, G.GATE_OOS_SHARPE_MIN, G.GATE_CAGR_MIN_PCT)
    print(json.dumps({k: v for k, v in dist.items() if k.startswith(("S1", "A1"))},
                     ensure_ascii=False)[:600], flush=True)

    # cross-face: the phase face priced five of these starts; the two faces must agree on
    # the ones they share, otherwise this grid is priced by a different engine.
    cross = {"phase_face": None, "compared": [], "disagreements": []}
    try:
        with io.open(PHASE_FACE, encoding="utf-8") as f:
            pf = json.load(f)
        cross["phase_face"] = {"asof": pf.get("asof"), "evidence_cutoff": pf.get("evidence_cutoff"),
                               "state": (pf.get("adjudication") or {}).get("state"),
                               "phases": len(pf.get("phase_rows") or [])}
        by_first = {r["first_bar"]: r for r in rows}
        for pr in pf.get("phase_rows") or []:
            fb = pr.get("first_bar")
            mine = by_first.get(fb)
            if not mine:
                cross["disagreements"].append(
                    {"phase_start": pr.get("start"), "first_bar": fb,
                     "why": "this start is not inside the grid; not compared"})
                continue
            ds = None if (pr.get("oos_sharpe") is None or mine.get("oos_sharpe") is None) \
                else round(float(mine["oos_sharpe"]) - float(pr["oos_sharpe"]), 6)
            dc = None if (pr.get("cagr_pct") is None or mine.get("cagr_pct") is None) \
                else round(float(mine["cagr_pct"]) - float(pr["cagr_pct"]), 6)
            same = (mine.get("verdict") == pr.get("verdict")
                    and ds is not None and abs(ds) <= 1e-6
                    and dc is not None and abs(dc) <= 1e-6)
            cross["compared"].append({"phase_start": pr.get("start"), "first_bar": fb,
                                      "verdict": mine.get("verdict"),
                                      "delta_oos_sharpe": ds, "delta_cagr_pp": dc,
                                      "reproduces": same})
            if not same:
                cross["disagreements"].append(
                    {"phase_start": pr.get("start"), "first_bar": fb,
                     "why": "priced differently here", "mine": mine.get("verdict"),
                     "theirs": pr.get("verdict"), "delta_oos_sharpe": ds,
                     "delta_cagr_pp": dc})
    except Exception as exc:                                     # noqa: BLE001
        cross["disagreements"].append({"why": "phase face unreadable: %s" % exc})

    gate_decision = None
    try:
        with io.open(GATE, encoding="utf-8") as f:
            gj = json.load(f)
        gate_decision = {"asof": gj.get("asof"),
                         "data_last": (gj.get("data") or {}).get("last"),
                         "verdict": (gj.get("decision") or {}).get("verdict")}
    except Exception:                                            # noqa: BLE001
        gate_decision = {"verdict": None, "why": "YEAR-GATE.json is not readable"}

    out = {
        "artifact": "etf_book_start_grid",
        "face": "etf_book_start_grid",
        "asof": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "question": ("the five-point phase face found 4 ADMIT / 1 DENY and said it could not "
                     "tell a book property from a calendar property; price every start of "
                     "one rebalance block instead of five weekly samples"),
        "book": BOOK,
        "grid": {"from": GRID_FROM, "starts": len(rows),
                 "first_start": rows[0]["start"] if rows else None,
                 "last_start": rows[-1]["start"] if rows else None,
                 "rebalance_period": REBAL_PERIOD,
                 "covers_rebalance_block": bool(len(rows) > REBAL_PERIOD),
                 "why_25": "one 20-bar rebalance period in full, plus enough bars to reach "
                           "2020-02-04, the latest first_bar the five-point phase face priced"},
        "gate_lines_imported": {
            "oos_sharpe_min": G.GATE_OOS_SHARPE_MIN,
            "oos_start": G.GATE_OOS_START,
            "cagr_min_pct": G.GATE_CAGR_MIN_PCT,
            "impact_max_pct_of_adv": G.GATE_IMPACT_MAX * 100.0,
            "capacity_lens": [t for _c, t in G.GATE_CAPITALS_CNY]},
        "data": {"bars": int(len(close.index)),
                 "first": str(pd.Timestamp(close.index[0]).date()),
                 "last": str(pd.Timestamp(close.index[-1]).date()),
                 "flips_repaired": int(n_flip),
                 "bond_free_universe": int(len(close.columns)),
                 "live_picks": picks,
                 "live_picks_asof": str(pd.Timestamp(sc.index[-1]).date()),
                 "adv_median_by_slot": {k: round(v, 0) for k, v in advs.items()},
                 "adv_weakest_cny": None if adv_weakest is None else round(adv_weakest, 0)},
        "start_rows": rows,
        "adjudication": agg,
        "distribution": dist,
        "spread_reading": spread,
        "cross_face_vs_phase_admission": cross,
        "gate_face": gate_decision,
        "honest": [
            "every start here is one bar apart, so these 25 rows are 25 views of the same "
            "price series, not 25 independent trials; the median one-bar step is quoted as "
            "a resolution, never as a standard error",
            "the resolution comparison (refusal margin vs one-bar step) describes how finely "
            "the start grid can locate the line; it is not an admission rule and it moves no "
            "gate -- YEAR-GATE and the phase face keep their printed verdicts",
            "K1 is a reading of today's tape and is therefore identical at every start by "
            "construction; only S1 and A1 can move with the grid",
            "the verdicts and the aggregate are etf_book_phase_admission's own functions; "
            "this face adds no threshold",
            "no broker fills are involved: every number is arithmetic on a published panel",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    print(json.dumps({"state": agg["state"], "starts": len(rows),
                      "deny": dist.get("deny"), "insufficient": dist.get("insufficient"),
                      "cross_face_disagreements": len(cross["disagreements"]),
                      "elapsed_sec": out["elapsed_sec"]}, ensure_ascii=False))
    print("saved", OUT)
    return 0


def check() -> int:
    """Re-derive the aggregate and the description from the published rows."""
    if not os.path.exists(OUT):
        print("FACE MISSING: %s" % OUT)
        return 3
    with io.open(OUT, encoding="utf-8") as f:
        face = json.load(f)
    problems = []
    rows = face.get("start_rows") or []
    if not rows:
        problems.append("FACE EMPTY: no start rows")
    agg = PA.aggregate(rows) if rows else {"state": "CANNOT_VERIFY", "reason": "no rows"}
    pub = face.get("adjudication") or {}
    if pub.get("state") != agg["state"]:
        problems.append("VERDICT DRIFT: published %s, re-derived %s"
                        % (pub.get("state"), agg["state"]))
    for key in ("admit_phases", "deny_phases", "insufficient_phases",
                "oos_sharpe_spread", "cagr_spread_pp"):
        if agg.get(key) != pub.get(key):
            problems.append("NUMBER DRIFT %s: published %r, re-derived %r"
                            % (key, pub.get(key), agg.get(key)))
    dist = distribution(rows, G.GATE_OOS_SHARPE_MIN, G.GATE_CAGR_MIN_PCT) if rows else {}
    pdist = face.get("distribution") or {}
    for key in ("starts", "admit", "deny", "insufficient"):
        if dist.get(key) != pdist.get(key):
            problems.append("DISTRIBUTION DRIFT %s: published %r, re-derived %r"
                            % (key, pdist.get(key), dist.get(key)))
    for ruler in ("S1_oos_sharpe", "A1_cagr_after_cost"):
        for field in ("closest_refusal", "worst_refusal"):
            a = (dist.get(ruler) or {}).get(field)
            b = (pdist.get(ruler) or {}).get(field)
            if (a or {}).get("start") != (b or {}).get("start"):
                problems.append("%s DRIFT %s: published %r, re-derived %r"
                                % (field.upper().replace("_", " "), ruler,
                                   (b or {}).get("start"), (a or {}).get("start")))
            if (a or {}).get("inside_start_noise") != (b or {}).get("inside_start_noise"):
                problems.append("%s PLACEMENT DRIFT %s: published %r, re-derived %r"
                                % (field.upper().replace("_", " "), ruler,
                                   (b or {}).get("inside_start_noise"),
                                   (a or {}).get("inside_start_noise")))
        na = (dist.get(ruler) or {}).get("refusals")
        nb = (pdist.get(ruler) or {}).get("refusals")
        if [x.get("start") for x in (na or [])] != [x.get("start") for x in (nb or [])]:
            problems.append("REFUSAL LIST DRIFT %s: published %r, re-derived %r"
                            % (ruler, [x.get("start") for x in (nb or [])],
                               [x.get("start") for x in (na or [])]))
        ja = (dist.get(ruler) or {}).get("neighbour_jump_median")
        jb = (pdist.get(ruler) or {}).get("neighbour_jump_median")
        if ja != jb:
            problems.append("JUMP DRIFT %s: published %r, re-derived %r" % (ruler, jb, ja))
        oa = (dist.get(ruler) or {}).get("any_refusal_outside_start_noise")
        ob = (pdist.get(ruler) or {}).get("any_refusal_outside_start_noise")
        if oa != ob:
            problems.append("OUTSIDE-NOISE FLAG DRIFT %s: published %r, re-derived %r"
                            % (ruler, ob, oa))
    cross = face.get("cross_face_vs_phase_admission") or {}
    if (cross.get("disagreements") or []):
        problems.append("CROSS FACE: %d disagreement(s) with the phase face: %s"
                        % (len(cross["disagreements"]),
                           json.dumps(cross["disagreements"][:2], ensure_ascii=False)))
    if not (cross.get("compared") or []):
        problems.append("CROSS FACE: nothing was compared against the phase face")
    cut = face.get("evidence_cutoff")
    if not cut:
        problems.append("NO CUTOFF: the face does not say which bar it priced")
    # r1850: a face whose own check re-derives from its own rows is always self-consistent,
    # so freshness must be asked of an EXTERNAL anchor.
    try:
        with io.open(GATE, encoding="utf-8") as f:
            gate_last = ((json.load(f) or {}).get("data") or {}).get("last")
        if cut and gate_last and str(cut) < str(gate_last):
            problems.append("STALE FACE_BEHIND_GATE: this face priced %s, the gate's panel "
                            "is %s" % (cut, gate_last))
    except Exception:                                            # noqa: BLE001
        problems.append("UNREADABLE GATE: cannot check freshness against %s" % GATE)
    if problems:
        print(json.dumps({"ok": False, "problems": problems}, ensure_ascii=False, indent=1))
        return 3
    print(json.dumps({"ok": True, "state": agg["state"], "starts": len(rows),
                      "evidence_cutoff": cut}, ensure_ascii=False))
    return 0


def selftest() -> int:
    """Fixtures only -- the description must be able to say both things, both ways."""
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:
            legs.append((name, False, str(exc)))

    def r(start, verdict, sharpe=1.0, cagr=10.0, failed=None):
        return {"start": start, "verdict": verdict, "oos_sharpe": sharpe, "cagr_pct": cagr,
                "failed_checks": failed or [],
                "checks": {"S1_oos_sharpe": verdict != "DENY" if verdict != "INSUFFICIENT" else None,
                           "A1_cagr_after_cost": True,
                           "K1_capacity_1pct_adv": True}}

    def L1_counts():
        rows = [r("s%d" % i, "ADMIT") for i in range(4)] + [r("s4", "DENY", sharpe=0.69)]
        d = distribution(rows, 0.70, 6.0)
        assert (d["starts"], d["admit"], d["deny"], d["insufficient"]) == (5, 4, 1, 0), d

    def L2_margin_is_signed_against_the_line():
        rows = [r("s0", "ADMIT", sharpe=1.79), r("s1", "DENY", sharpe=0.693)]
        d = distribution(rows, 0.70, 6.0)
        cr = d["S1_oos_sharpe"]["closest_refusal"]
        assert cr["start"] == "s1" and abs(cr["margin"] + 0.007) < 1e-6, cr

    def L3_one_bar_step_is_the_median_of_adjacent_gaps():
        rows = [r("s%d" % i, "ADMIT", sharpe=v) for i, v in enumerate([1.79, 1.61, 1.23, 0.69])]
        d = distribution(rows, 0.70, 6.0)
        jumps = sorted([abs(1.61 - 1.79), abs(1.23 - 1.61), abs(0.69 - 1.23)])
        assert abs(d["S1_oos_sharpe"]["neighbour_jump_median"] - statistics.median(jumps)) < 1e-9, d
        assert abs(d["S1_oos_sharpe"]["neighbour_jump_max"] - max(jumps)) < 1e-9, d

    def L4_refusal_inside_noise_when_step_is_bigger():
        # 0.007 from the line, but adjacent starts move 0.38 -> inside the grid's resolution
        rows = [r("s0", "ADMIT", sharpe=1.23), r("s1", "DENY", sharpe=0.693),
                r("s2", "ADMIT", sharpe=1.07)]
        d = distribution(rows, 0.70, 6.0)
        assert d["S1_oos_sharpe"]["refusal_inside_start_noise"] is True, d
        assert "lies inside" in d["S1_oos_sharpe"]["resolution_sentence"], d

    def L5_refusal_outside_noise_when_the_neighbourhood_is_flat():
        # the mirror case must be reachable, otherwise the sentence only ever says one
        # thing. A lone refusal inside a flat neighbourhood is a location, not a coin:
        # the three passing starts sit 0.0001 apart, so the 0.007 gap is not start noise.
        rows = [r("s0", "ADMIT", sharpe=0.7005), r("s1", "DENY", sharpe=0.6930),
                r("s2", "ADMIT", sharpe=0.7005), r("s3", "ADMIT", sharpe=0.7006),
                r("s4", "ADMIT", sharpe=0.7007)]
        d = distribution(rows, 0.70, 6.0)
        assert d["S1_oos_sharpe"]["refusal_inside_start_noise"] is False, d
        assert "lies outside" in d["S1_oos_sharpe"]["resolution_sentence"], d

    def L6_a_coin_flip_refusal_may_not_hide_a_real_one():
        # the defect this leg exists for: printing only the closest refusal lets a refusal
        # that sits a full step from the line disappear behind one that sits 0.007 away.
        # s1 is closest (0.007, one-bar step ~0.31 -> inside); s3 is the worst (1.40 away
        # from the line, far outside any step this grid takes).
        rows = [r("s0", "ADMIT", sharpe=0.71), r("s1", "DENY", sharpe=0.693),
                r("s2", "ADMIT", sharpe=1.00), r("s3", "DENY", sharpe=-0.70),
                r("s4", "ADMIT", sharpe=1.02)]
        d = distribution(rows, 0.70, 6.0)["S1_oos_sharpe"]
        assert d["closest_refusal"]["start"] == "s1", d
        assert d["worst_refusal"]["start"] == "s3", d
        assert d["refusal_inside_start_noise"] is True, d
        assert d["any_refusal_outside_start_noise"] is True, d
        assert "lies inside" in d["resolution_sentence"] and \
               "lies outside" in d["resolution_sentence"], d
        assert len(d["refusals"]) == 2, d

    def L7_no_refusal_says_so_instead_of_printing_zero():
        rows = [r("s%d" % i, "ADMIT", sharpe=1.5) for i in range(3)]
        d = distribution(rows, 0.70, 6.0)["S1_oos_sharpe"]
        assert d["closest_refusal"] is None and d["worst_refusal"] is None, d
        assert d["refusals"] == [], d
        assert d["any_refusal_outside_start_noise"] is False, d
        assert "no start refuses" in d["resolution_sentence"], d

    def L7_unreadable_is_counted_not_passed():
        rows = [r("s0", "INSUFFICIENT", sharpe=None, cagr=None)] + \
               [r("s%d" % i, "ADMIT") for i in range(1, 3)]
        d = distribution(rows, 0.70, 6.0)
        assert d["insufficient"] == 1, d
        assert d["S1_oos_sharpe"]["readable"] == 2, d

    def L8_empty_is_cannot_verify():
        d = distribution([], 0.70, 6.0)
        assert d["state"] == "CANNOT_VERIFY", d

    def L9_grid_is_a_contiguous_slice_and_wider_than_the_rebalance_period():
        idx = pd.bdate_range("2019-12-01", periods=200)
        st = grid_starts(idx, n=25)
        assert len(st) == 25, len(st)
        assert all(st[i] < st[i + 1] for i in range(len(st) - 1)), "starts must be ordered"
        assert st[0] >= pd.Timestamp(GRID_FROM), st[0]
        assert len(st) > REBAL_PERIOD, "a grid no wider than the rebalance cannot cover a block"

    def L10_aggregate_comes_from_the_phase_face_not_from_here():
        rows = [r("s%d" % i, "ADMIT") for i in range(3)] + [r("s3", "DENY", sharpe=0.4)]
        a = PA.aggregate(rows)
        assert a["state"] == "REFUSED_AT_SOME_PHASE", a
        assert a["deny_phases"] == 1, a
        # and the spread rule is the imported one
        sp = PA.spread_state([1.70, 1.71, 1.72], ["ADMIT"] * 3, 0.70)
        assert sp["state"] == "ADMIT", sp

    for name, fn in [
        ("L1 计数=四态各自数量", L1_counts),
        ("L2 refusal margin 相对线带符号", L2_margin_is_signed_against_the_line),
        ("L3 一格步长=相邻差的中位与最大", L3_one_bar_step_is_the_median_of_adjacent_gaps),
        ("L4 步长大于距线 → 落在分辨率内", L4_refusal_inside_noise_when_step_is_bigger),
        ("L5 反向可达 → 落在分辨率外", L5_refusal_outside_noise_when_the_neighbourhood_is_flat),
        ("L6 硬币拒绝不得盖住真实拒绝", L6_a_coin_flip_refusal_may_not_hide_a_real_one),
        ("L7 无拒绝时印句子而非 0", L7_no_refusal_says_so_instead_of_printing_zero),
        ("L7b 读不出单独计数（r98）", L7_unreadable_is_counted_not_passed),
        ("L8 空面=CANNOT_VERIFY", L8_empty_is_cannot_verify),
        ("L9 起点是连续切片且宽于换仓周期", L9_grid_is_a_contiguous_slice_and_wider_than_the_rebalance_period),
        ("L10 判词与 spread 均来自相位面", L10_aggregate_comes_from_the_phase_face_not_from_here),
    ]:
        leg(name, fn)

    passed = sum(1 for _n, ok, _m in legs if ok)
    for n, ok, msg in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", n, "" if ok else "  <- " + msg))
    print("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return selftest()
    if args.check or args.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
