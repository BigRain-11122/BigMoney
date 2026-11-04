"""r1438 closeout: carry a dead window's E420 estate to the ledger, state, and heartbeat."""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

TS = "2026-11-04T21:05:00+08:00"
ROW = (
    "| 2026-11-04T21:05:00+08:00 | r1438 | bm-b | "
    "**watermark: red=false -- pool floor 3/3 ready at open (E413/E417/E420-no-writer); no card claimed this round** "
    "(the ready head E413 was NOT taken: the 19:52 window died mid-round leaving a complete, uncommitted E420 estate, "
    "and finishing it was cheaper than opening a new study). "
    "E420 (absorbed from the dead 19:52 window, verified end to end before claiming it): the only fields that move "
    "between an audit's `fresh_today` and a later re-derive are POPULATION COUNTS that grow with the corpus, so the "
    "frozen equality assertion in the E387 leg was unsatisfiable on an honest rebuild -- it reds on accretion and can "
    "never go green again. READINGS: 4 audited rows / 4 on disk, 2 flagged today, 0 flagged only by a corpus "
    "fingerprint, 2 rows where a published number moved, 0 numbers went DOWN, 0 verdicts moved, 1 row whose face "
    "agrees with its own pin file, **3 distinct pin vintages measured for one face inside one day**, corpus 2492 "
    "members, the current pin is not any recorded vintage. PRODUCT: `scripts/e420_corpus_pin_instability.py` "
    "(run / verify problems=0 / selftest PASS 10/10) + `results/state_tilt/PININSTABILITY-2026-11-04.json` "
    "(+`pininstability_latest.json`) + smoke_test.py E420 correction inside the E387 leg (3 hunks, all in that "
    "region) + card E420 (+40/-0) + `research/digests/DIGEST-20261104-r1438-e420-corpus-pin-gate.md`. "
    "VERIFIED: `python scripts\\run_e387_smoke_leg.py` -> leg 2/2 PASS with the new split (verdict move = red, "
    "number going down = red, accretion = green). "
    "S0/S0.5: machine id bm-b from `fleet/machine.json`; orders diff = 114 files / 115 acks / 0 unacked (no order to "
    "execute); `scripts/queue_head_collision_probe.py probe` -> CLEAR on both queues; no remote fetch/rebase attempted "
    "(the divergence wedge is unchanged, delivery is the machine branch). "
    "S6/S7: orphan probe py_faces=7 orphans=0 residents=0 | attrition guard CLEAN (4 ledgers, 2 historical shrinks "
    "healed) | saturation engine rc=0 idle | the rest of the S6 chain and the lane collectors were NOT re-run this "
    "window (wall budget, stated plainly). "
    "NOT RUN / NOT CLAIMED: the full ~319-leg smoke suite was not re-run, so 319/319 is not claimed; no GPU work "
    "(parked C-20261014-01); no cloud call; nothing deleted. 登记簿零命中 (no sweep/archive action). "
    "PIT: a dead window's estate must be re-verified from its own artefacts before it is adopted -- the face, "
    "selftest, verify and leg all had to pass on MY run, not on its last printed line. "
    "| 本地未达 origin main commit = 354 (fetch ok; delivered on the machine branch) |"
)

with io.open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="\n") as fh:
    fh.write(ROW + "\n")

st = json.load(io.open("state-bm-b.json", encoding="utf-8"))
st.update({
    "round_no": 1438,
    "round": 1438,
    "seq": 1438,
    "round_no_label": "r1438",
    "round_no_ts": TS,
    "ts": TS,
    "timestamp": TS,
    "updated": TS,
    "updated_at": TS,
    "clock_read": TS,
    "status": "ok",
    "task": "r1438 E420: the corpus-pin equality gate was unsatisfiable -- price accretion, not equality",
    "task_short": "r1438 E420 corpus pin gate",
    "study": "E420_corpus_pin_instability",
    "face": "results/state_tilt/PININSTABILITY-2026-11-04.json",
    "verdict": "the_only_fields_that_moved_are_population_counts_that_grew_with_the_corpus_so_an_equality_assertion_on_them_is_unsatisfiable_on_an_honest_rebuild",
    "selftest": "e420_corpus_pin_instability 10/10; verify problems=0; E387 leg 2/2 PASS",
    "smoke": "E387 leg extracted verbatim and run standalone with the E420 split: PASS (2/2)",
    "s1": "the full ~319-leg suite was not re-run this window; the corrected E387 leg was executed verbatim from smoke_test.py (scripts/run_e387_smoke_leg.py, 2/2 PASS)",
    "s6": "orphan probe py_faces=7 orphans=0 residents=0 | attrition guard CLEAN (4 ledgers, 2 historical shrinks healed) | saturation engine rc=0 idle | dualrun, compute_audit, py_watermark and the lane collectors were NOT re-run this window (wall budget, stated plainly)",
    "s7": "orders 114 files / 115 acks / 0 unacked | queue head collision probe CLEAR on tech+explore | round took a dead window's E420 estate instead of the ready head E413 (cheaper, disclosed) | loop task / watchdog / claws not re-registered this window (their own ticks cover the gap; stated plainly)",
    "watermark_red": "pool floor 3/3 ready at open (E413/E417/E420-no-writer); none claimed -- the round finished a dead window's E420 estate instead",
    "watermark_verdict": "pool floor 3/3 met at open; no card consumed, floor unchanged",
    "absorb": "the 19:52 window wrote the E420 script, face, smoke correction, digest and card, then died before any closeout; every artefact was re-verified on this run (selftest 10/10, verify 0 problems, leg 2/2) before the number 1438 was carried",
    "not_run": "full smoke suite, rest of the S6 chain, dualrun/compute_audit/py_watermark, lane collectors, GPU (parked), cloud",
    "product": [
        "scripts/e420_corpus_pin_instability.py (selftest 10/10, verify problems=0)",
        "results/state_tilt/PININSTABILITY-2026-11-04.json + pininstability_latest.json",
        "smoke_test.py E420 correction (3 hunks, E387 leg only)",
        "knowledge/METHODOLOGY_ASSETS.md card E420",
        "research/digests/DIGEST-20261104-r1438-e420-corpus-pin-gate.md",
    ],
    "three_line_current": "E420: the corpus-pin equality gate reds on growth and can never go green -- it now prices accretion, a downward number, and self-agreement with the face's own pin",
    "three_line_artifact": "results/state_tilt/PININSTABILITY-2026-11-04.json @ 2026-11-04T21:05+08:00",
    "three_line_next": "E413 strong-basis names resolved to no file (ready, cpu-only) or E417 shadow faces -- due <=48h",
    "recent_artifact": "results/state_tilt/PININSTABILITY-2026-11-04.json",
    "sync": {"ahead": 354, "behind": 288, "peer": "origin", "branch": "machine/bm-b-r1438"},
})
with io.open("state-bm-b.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1, sort_keys=True)
    fh.write("\n")

mirror = json.load(io.open("state.json", encoding="utf-8"))
mirror["round_no"] = 1438
mirror["round"] = 1438
mirror["seq"] = 1438
mirror["ts"] = TS
mirror["updated"] = TS
mirror["state_face_note"] = "mirror; authoritative face is state-bm-b.json"
with io.open("state.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(mirror, fh, ensure_ascii=False, indent=1, sort_keys=True)
    fh.write("\n")

hb_path = "fleet/machines/bm-b.json"
hb = json.load(io.open(hb_path, encoding="utf-8"))
hb.update({
    "machine_id": "bm-b",
    "round_no": 1438,
    "last_seen": TS,
    "clock_read": TS,
    "ts": TS,
    "status": "ok",
    "task": "E420 corpus-pin gate closed (accretion, not equality); E413/E417 ready",
    "idle_rounds": 0,
    "agenda_starved": False,
})
with io.open(hb_path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1, sort_keys=True)
    fh.write("\n")

chk = json.load(io.open(hb_path, encoding="utf-8"))
print("round_reports row appended; state 1438; heartbeat round_no=%s orders_ack=%d"
      % (chk["round_no"], len(chk.get("orders_ack") or [])))