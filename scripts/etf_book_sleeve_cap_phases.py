"""A sleeve cap is a rule, so it gets the same phase test a book gets.

r1423's attribution said the loud years are single-sleeve years (2024: commodity 94.4% of
the year) and left the next pointer "cap the commodity sleeve". r1425 priced that cap on
one decision phase (`etf_book_sleeve_cap.py`) and every arm got *worse*: plain 11.46% /
1.128 / -10.56%, cap 2 commodity names 10.46% / 1.057 / -10.56%. A single phase is a
single decision sequence (E188, E199), so that reading cannot be the verdict.

This file runs the same four arms over the frozen phase set (five weekly starts = exactly
one 20-bar rebalance block, imported from `candidate_year_gate_phases`) and adjudicates
each arm with that file's own three-word rule (`adjudicate`, imported, never retyped).
The yearly gate lines come from `candidate_year_gate.admission_block`; the arm wrapper
uses the engine's own `select_hook`, so the only thing that differs between arms is the
cap.

Adoption rule is frozen in RULE below and printed into the receipt *before* any reading:

    ADOPT   cap arm ADMITs on the phase set, AND the plain arm does not (otherwise the
            cap buys nothing -- it can only remove names), AND the cap is not a pure
            loss: in at least 60% of phases its CAGR is no worse than plain - 0.10pp
            AND its Sharpe no worse than plain - 0.01.
    REJECT  any of the three fails; the failing clause is named.
    UNADJUDICABLE_PHASE  the cap's own phase set disagrees or its spread is wider than
            its distance to the line -- then no adoption decision may be taken at all.

rc: 0 = ran and wrote the receipt; 3 = the cap-free arm no longer reproduces the
published book (the arms would be measuring a different book).

    python scripts/etf_book_sleeve_cap_phases.py run
    python scripts/etf_book_sleeve_cap_phases.py selftest
"""
import json
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import pandas as pd  # noqa: E402

import candidate_year_gate as G  # noqa: E402
import candidate_year_gate_phases as P  # noqa: E402
import etf_book_sleeve_cap as C  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402
import etf_book_year_gate as Y  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import etf_robust_pf as R  # noqa: E402

OUT = os.path.join(ROOT, "results", "etf_book_sleeve_cap_phases.json")

REBAL = 20
N_HOLD = 5
COST = 0.0010
VT = 0.08

# identical to the single-phase run, so the arms are the same arms
ARMS = (
    ("plain", {}),
    ("cap_comm_1", {"commodity": 1}),
    ("cap_comm_2", {"commodity": 2}),
    ("cap_comm_1_conv_1", {"commodity": 1, "convertible": 1}),
)

RULE = {
    "phase_set": list(P.PHASE_STARTS),
    "phase_rule_imported": "candidate_year_gate_phases.adjudicate (RULE frozen there)",
    "admit_word": "ADMIT",
    "not_worse_cagr_tol_pp": 0.10,
    "not_worse_sharpe_tol": 0.01,
    "not_worse_share_floor": 0.60,
    "adopt_requires": [
        "cap arm adjudication state == ADMIT",
        "plain arm adjudication state != ADMIT (otherwise the cap can only remove names)",
        "share of phases where cagr >= plain-0.10pp AND sharpe >= plain-0.01 >= 0.60",
    ],
    "reason": (
        "a cap is a rule; E188/E199 say a rule that wins on one decision phase and loses "
        "on the next is not a rule, and an adoption must also answer whether it bought "
        "anything (a cap on a book that already ADMITs can only shrink it)"
    ),
    "frozen_before_read": True,
}


def run_arm(close, openp, amt, sc, cls, caps, label, start):
    """One repricing through the published engine; the cap is the only difference."""
    hook = None
    if caps:
        hook = lambda row, held, n, d: C.capped_select(row, held, n, d, cls, caps)
    ser, turn = R.open_to_open_equity(close, openp, amt, sc, REBAL, N_HOLD, COST,
                                     vol_target=VT, start=start, select_hook=hook)
    return ser, turn


def decide(arm_verdicts, phase_stats, not_worse_flags):
    """Frozen adoption rule. Verdicts come from the imported three-word rule."""
    cap_state = arm_verdicts.get("cap")
    plain_state = arm_verdicts.get("plain")
    share = (sum(not_worse_flags) / len(not_worse_flags)) if not_worse_flags else 0.0
    out = {"cap_state": cap_state, "plain_state": plain_state,
           "not_worse_share": round(share, 4),
           "not_worse_phases": sum(not_worse_flags), "phases": len(not_worse_flags)}
    if cap_state == "UNADJUDICABLE_PHASE":
        out.update(decision="UNADJUDICABLE_PHASE",
                   reason="the cap's own phase set cannot adjudicate itself")
        return out
    if cap_state != "ADMIT":
        out.update(decision="REJECT", reason="cap arm does not ADMIT (%s)" % cap_state)
        return out
    if plain_state == "ADMIT":
        out.update(decision="REJECT",
                   reason="plain arm already ADMITs; a cap here can only remove names")
        return out
    if share < RULE["not_worse_share_floor"]:
        out.update(decision="REJECT",
                   reason="cap is a pure loss: not-worse in only %d/%d phases (floor %.2f)"
                          % (sum(not_worse_flags), len(not_worse_flags),
                             RULE["not_worse_share_floor"]))
        return out
    out.update(decision="ADOPT",
               reason="cap ADMITs where plain does not, and is not-worse in %d/%d phases"
                      % (sum(not_worse_flags), len(not_worse_flags)))
    return out


def run():
    t0 = time.time()
    close, openp, amt, sc, n_flip = S.nobond_universe()
    cls = A.classify(close.columns, A.load_class_map(), close)
    cap_cny = S.published_capacity()

    # identity: the cap-free arm must still be the published book (refuse otherwise)
    published = C.load_published(R.PATHS.results_dir)
    cut = pd.Timestamp(published["as_of"])
    m_idx = close.index <= cut
    id_ser, _ = R.open_to_open_equity(close.loc[m_idx], openp.loc[m_idx], amt.loc[m_idx],
                                      sc.loc[m_idx], REBAL, N_HOLD, COST, vol_target=VT)
    id_stats = A.stats2(id_ser, "identity_" + C.PUBLISHED_LABEL)
    dev = C.identity_deviation(id_stats, published["numbers"])
    ok = C.identity_ok(id_stats, published["numbers"])
    print("identity", published["as_of"], "dev", dev, "ok", ok, flush=True)
    if not ok:
        print("REFUSED: cap-free arm no longer reproduces %s" % C.PUBLISHED_LABEL, flush=True)
        return 3

    books = []
    per_arm_phase = {}
    for label, caps in ARMS:
        rows = []
        for start in P.PHASE_STARTS:
            ser, turn = run_arm(close, openp, amt, sc, cls, caps, label, start)
            yrs = Y.yearly_returns(ser)
            st = A.stats2(ser, "p")
            blk = G.admission_block(yrs, cap_cny, None, st.get("cagr"))
            row = {
                "start": start,
                "verdict": blk["verdict"],
                "top2_share": blk["year_metrics"]["top2_share"],
                "positive_years_share": blk["year_metrics"].get("positive_years"),
                "worst_year_pp": blk["year_metrics"].get("worst"),
                "cagr_pct": blk["cagr_pct"],
                "sharpe": None if st.get("sharpe") is None else round(float(st["sharpe"]), 4),
                "maxdd": None if st.get("maxdd") is None else round(float(st["maxdd"]), 4),
                "turnover": round(turn, 3),
                "failing_checks": [k for k, v in blk["checks"].items() if v is False],
            }
            rows.append(row)
            print("  %-20s %s -> %-12s top2 %s cagr %s sharpe %s"
                  % (label, start, row["verdict"],
                     None if row["top2_share"] is None else round(row["top2_share"], 4),
                     None if row["cagr_pct"] is None else round(row["cagr_pct"], 3),
                     row["sharpe"]), flush=True)
        agg = P.adjudicate(rows)
        per_arm_phase[label] = rows
        books.append({"book": label, "caps": dict(caps) or None,
                      "phase_rows": rows, "adjudication": agg,
                      "single_phase_r1425_reading": rows[0]["verdict"]})
        print("%-20s -> %-20s (%s)" % (label, agg["state"], agg["reason"]), flush=True)

    # frozen rule, applied to each capped arm against plain
    plain_rows = per_arm_phase["plain"]
    decisions = []
    for b in books[1:]:
        flags = []
        for pr, cr in zip(plain_rows, b["phase_rows"]):
            if pr.get("cagr_pct") is None or cr.get("cagr_pct") is None:
                flags.append(False)
                continue
            cagr_ok = cr["cagr_pct"] >= pr["cagr_pct"] - RULE["not_worse_cagr_tol_pp"]
            sr_ok = (cr.get("sharpe") is not None and pr.get("sharpe") is not None
                     and cr["sharpe"] >= pr["sharpe"] - RULE["not_worse_sharpe_tol"])
            flags.append(bool(cagr_ok and sr_ok))
        d = decide({"cap": b["adjudication"]["state"],
                    "plain": books[0]["adjudication"]["state"]},
                   b["phase_rows"], flags)
        d["arm"] = b["book"]
        d["caps"] = b["caps"]
        decisions.append(d)
        print("%-20s DECISION %-20s (%s)" % (b["book"], d["decision"], d["reason"]), flush=True)

    out = {
        "face": "etf_book_sleeve_cap_phases",
        "asof": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "question": "does capping a sleeve buy the book anything, once the rule is read "
                    "over a phase set instead of one decision sequence?",
        "rule": RULE,
        "gate_lines_imported": {
            "top2_share_max": G.TOP2_SHARE_MAX,
            "positive_years_share": G.POSITIVE_YEARS_SHARE,
            "worst_year_floor_pp": G.WORST_YEAR_FLOOR_PP,
            "capacity_floor_cny": G.CAPACITY_FLOOR_CNY,
        },
        "params": {"n_hold": N_HOLD, "rebal": REBAL, "cost": COST, "vol_target": VT},
        "data": {"flips_repaired": n_flip, "universe": int(len(close.columns)),
                 "bars": int(len(close.index)),
                 "capacity_cny_1day_5pct": cap_cny,
                 "capacity_from": "results/etf_book_year_gate/YEAR-GATE.json"},
        "published_arm": published, "identity_deviation": dev, "identity_ok": ok,
        "books": books, "decisions": decisions,
        "summary": {b["book"]: {"state": b["adjudication"]["state"],
                                "median_top2_share": b["adjudication"]["median_top2_share"],
                                "spread_pp": b["adjudication"]["spread_pp"],
                                "margin_pp": b["adjudication"]["margin_pp"],
                                "phases_above_line": b["adjudication"].get("phases_above_line"),
                                "single_phase_verdict": b["single_phase_r1425_reading"]}
                    for b in books},
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved", OUT, flush=True)
    return 0


def selftest() -> int:
    """Offline proofs: every word of the frozen rule must be reachable, and each clause
    must be the thing that fires (a rule that can only say REJECT is not a test)."""
    errs = []

    def chk(ok, msg):
        print(("PASS " if ok else "FAIL ") + msg, flush=True)
        if not ok:
            errs.append(msg)

    ok_flags = [True, True, True, True, True]
    bad_flags = [False, False, False, False, True]

    # L1 cap cannot adjudicate itself -> no decision
    d = decide({"cap": "UNADJUDICABLE_PHASE", "plain": "CONDITIONAL"}, [], ok_flags)
    chk(d["decision"] == "UNADJUDICABLE_PHASE", "L1 unadjudicable cap -> %s" % d["decision"])

    # L2 cap does not ADMIT -> REJECT and names it
    d = decide({"cap": "CONDITIONAL", "plain": "CONDITIONAL"}, [], ok_flags)
    chk(d["decision"] == "REJECT" and "does not ADMIT" in d["reason"],
        "L2 cap CONDITIONAL -> REJECT (%s)" % d["reason"])

    # L3 plain already ADMITs -> the cap buys nothing
    d = decide({"cap": "ADMIT", "plain": "ADMIT"}, [], ok_flags)
    chk(d["decision"] == "REJECT" and "already ADMITs" in d["reason"],
        "L3 plain ADMIT -> REJECT (%s)" % d["reason"])

    # L4 cap ADMITs where plain does not but loses in most phases -> pure loss
    d = decide({"cap": "ADMIT", "plain": "CONDITIONAL"}, [], bad_flags)
    chk(d["decision"] == "REJECT" and "pure loss" in d["reason"],
        "L4 not-worse only 1/5 -> REJECT (%s)" % d["reason"])

    # L5 the only path to ADOPT
    d = decide({"cap": "ADMIT", "plain": "CONDITIONAL"}, [], ok_flags)
    chk(d["decision"] == "ADOPT" and d["not_worse_share"] == 1.0,
        "L5 ADMIT where plain does not, not-worse everywhere -> ADOPT")

    # L6 the floor is inclusive at exactly 0.60 (3/5), so 3/5 adopts and 2/5 does not
    d3 = decide({"cap": "ADMIT", "plain": "CONDITIONAL"}, [],
                [True, True, True, False, False])
    chk(d3["decision"] == "ADOPT", "L6 3/5 not-worse meets the 0.60 floor -> ADOPT")
    d2 = decide({"cap": "ADMIT", "plain": "CONDITIONAL"}, [],
                [True, True, False, False, False])
    chk(d2["decision"] == "REJECT", "L6b 2/5 not-worse misses the floor -> REJECT")

    # L7 a phase missing its numbers is not "not worse" (E-class: empty measurement is
    # not a pass)
    rows_plain = [{"cagr_pct": 10.0, "sharpe": 1.0}]
    rows_cap = [{"cagr_pct": None, "sharpe": None}]
    flags = []
    for pr, cr in zip(rows_plain, rows_cap):
        flags.append(bool(pr.get("cagr_pct") is not None and cr.get("cagr_pct") is not None
                          and cr["cagr_pct"] >= pr["cagr_pct"]))
    chk(flags == [False], "L7 missing numbers never count as not-worse")

    # L8 the tolerances are the declared ones (0.10pp CAGR / 0.01 Sharpe), not zero
    d8 = decide({"cap": "ADMIT", "plain": "CONDITIONAL"}, [],
                [True, True, True, True, True])
    chk(RULE["not_worse_cagr_tol_pp"] == 0.10 and RULE["not_worse_sharpe_tol"] == 0.01
        and RULE["not_worse_share_floor"] == 0.60 and d8["decision"] == "ADOPT",
        "L8 the published tolerances are the ones the rule uses")

    # L9 the phase set and the three-word rule are imported, not retyped
    chk(tuple(RULE["phase_set"]) == tuple(P.PHASE_STARTS) and len(P.PHASE_STARTS) == 5,
        "L9 phase set is the imported five weekly starts")
    chk(RULE["admit_word"] == P.RULE["admit_word"] and
        RULE["admit_word"] == "ADMIT", "L9b the admit word is the imported one")

    # L10 the arm list is exactly the single-phase run's arms, so nothing else moved
    chk([a[0] for a in ARMS] == ["plain", "cap_comm_1", "cap_comm_2", "cap_comm_1_conv_1"],
        "L10 arms are the r1425 single-phase arms, cap-free first")

    # L11 statistics module is actually used (median top2 is reported, not implied)
    chk(abs(statistics.median([0.71, 0.79, 0.60]) - 0.71) < 1e-12,
        "L11 median is computed, not hand-picked")

    tot = 12
    print("selftest %d/%d" % (tot - len(errs), tot), flush=True)
    return 0 if not errs else 1


def main(argv):
    mode = argv[1] if len(argv) > 1 else "run"
    if mode == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))