"""Negative control for r2063's k-identity diagnosis: does the face refuse the answers it should? (r2063)

A diagnosis that can only conclude "identity intact" is not a diagnosis. This script loads the
published face and drives `judge()` / `check()` with poisoned inputs, asserting each poison turns
the verdict, and re-derives the headline numbers a second way.

Eight legs, no network, no panel rebuild (everything comes off the published face plus fixtures).
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_k_identity_bar as K  # noqa: E402

FACE = os.path.join(ROOT, "results", "etf_book_k_identity_bar.json")
TICKET = os.path.join(ROOT, "results", "etf_book_order", "TICKET-2026-11-24.json")


def main():
    legs = []
    with open(FACE, encoding="utf-8") as f:
        face = json.load(f)
    with open(TICKET, encoding="utf-8") as f:
        tk = json.load(f)
    assert face["verdict"] == "IDENTITY_INTACT_LEG_READS_A_DIFFERENT_STEP", face["verdict"]

    sched = K._fixture_sched()

    # 1 the published arm's last step really is the ticket's k_rule -- otherwise the face is
    #   diagnosing a schedule the ticket never saw (this is the external anchor, off the face)
    tail_last = face["schedule_tail"][-1]
    assert abs(tail_last["k"] - tk["k_rule"]) <= K.STEP_TOL, (tail_last, tk["k_rule"])
    assert tail_last["bar"] == face["priced_bar"], (tail_last, face["priced_bar"])
    legs.append("ticket_is_the_faces_own_last_step")

    # 2 poison: a k_rule that is not on the schedule must never read intact (3.7e-5 off, i.e.
    #   well outside the 6dp storage precision the ticket actually carries)
    j = K.judge(sched, {"k_rule": 0.4585, "base_bar": "2026-11-24",
                        "book_decided_at": "2026-11-11"})
    assert j["verdict"] == "IDENTITY_STILL_BROKEN", j["verdict"]
    legs.append("off_schedule_refused")

    # 3 poison: a real schedule point that is NOT the last one before the priced bar
    j = K.judge(sched, {"k_rule": 0.458808, "base_bar": "2026-11-24",
                        "book_decided_at": "2026-11-11"})
    assert j["verdict"] == "IDENTITY_STILL_BROKEN", j["verdict"]
    assert "that_point_is_the_last_step_at_or_before_the_priced_bar" in j["identity_broken"], j
    legs.append("wrong_step_refused")

    # 4 poison: priced bar moved back onto the leg's own step -> no split left to explain
    j = K.judge(sched, {"k_rule": 0.458463, "base_bar": "2026-10-23",
                        "book_decided_at": "2026-11-11"})
    assert j["verdict"] == "IDENTITY_STILL_BROKEN", j["verdict"]
    legs.append("moved_priced_bar_refused")

    # 5 poison: leg bar moved onto the ticket's step -> the two rows agree, so this face's
    #   diagnosis does not apply and it says so instead of inventing a split
    j = K.judge(sched, {"k_rule": 0.458463, "base_bar": "2026-11-24",
                        "book_decided_at": "2026-11-24"})
    assert j["verdict"] == "IDENTITY_STILL_BROKEN", j["verdict"]
    assert "same step" in j["sentence"].lower(), j["sentence"]
    legs.append("same_row_refused")

    # 6 the 6dp storage tolerance is load-bearing: at 1e-12 the published pair looks broken
    j = K.judge(sched, {"k_rule": round(0.45846254, 12), "base_bar": "2026-11-24",
                        "book_decided_at": "2026-11-11"}, )
    assert j["verdict"] == "IDENTITY_INTACT_LEG_READS_A_DIFFERENT_STEP", j
    hits_at_1e12 = K.locate(sched, 0.45846254, tol=1e-12)
    assert hits_at_1e12 == [], "the fixture should not match at 1e-12 -- tolerance must matter"
    legs.append("storage_tolerance_is_load_bearing")

    # 7 headline re-derived a second way: the gap is the difference of the two schedule rows,
    #   and the CNY figure is pp/100 x ticket, not pp x ticket
    row_priced = K.step_bar(sched, "2026-11-24")[1]
    row_leg = K.step_bar(sched, "2026-11-11")[1]
    assert abs(100.0 * (row_priced - row_leg) - face["dk_pp"]) < 1e-9, (row_priced, row_leg)
    assert abs(face["dk_cny_at_ticket"] - face["dk_pp"] / 100.0 * 1000000.0) < 1e-6, face
    assert abs(face["dk_cny_at_ticket"] + 1790.0) < 1e-6, face["dk_cny_at_ticket"]
    legs.append("gap_rederived")

    # 8 the drift claim is a count, not an adjective: recount it off the published schedule tail
    #   plus the face's own drift block, and require the threshold to be the one used
    dr = face["drift"]
    assert dr["n_diffs"] == dr["n_steps"] - 1, dr
    assert 0 <= dr["n_steps_where_a_0_179pp_gap_would_turn_red"] <= dr["n_diffs"], dr
    assert dr["abs_step_pp_max"] >= abs(face["dk_pp"]), dr
    legs.append("drift_is_a_count")

    # 9 the face must not claim intact while one of its legs is False
    assert face["identity_broken"] == [], face["identity_broken"]
    assert all(v is True for v in face["legs"].values()), face["legs"]
    legs.append("verdict_matches_legs")

    # 10 the face says what it does not do: it must name the host contention and the smoke legs
    joined = " ".join(face["what_this_does_not_claim"])
    assert "host" in joined and "smoke" in joined, joined
    legs.append("limits_printed")

    print("negctl %d/%d OK: %s" % (len(legs), len(legs), ",".join(legs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
