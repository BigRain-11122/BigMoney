"""r1349 closeout: state-bm-b.json + fleet/machines/bm-b.json (round face only).

Writes only this machine's two faces.  Epoch is an int (F7), clock_read uses a T separator.
"""
import datetime
import io
import json
import subprocess

NOW = datetime.datetime.now().astimezone().replace(microsecond=0)
ISO = NOW.isoformat()
EPOCH = int(NOW.timestamp())

STATE = "state-bm-b.json"
HEART = "fleet/machines/bm-b.json"

round_block = {
    "round": 1349,
    "dept": "research+engineering",
    "study": "E329_two_vintage_binding",
    "face": "results/state_tilt/TWOVINTAGE-2026-11-01.json",
    "verdict": "the_stale_cut_loses_while_the_pointer_exists_and_no_fallback_rechecks_for_a_newer_cut",
    "finding": (
        "228 sources name a face and form 597 (source, family) pairs; 9 name two vintages of one "
        "stem (8 two dated cuts, 1 pointer pair) and only 2 have both cuts on disk. 2 pairs bind "
        "them to separately named roles (DEFAULT_ASOF/DEFAULT_FRESH, ca/cb) so nothing races; 1 is "
        "a real fallback chain -- e242's _face_file tries *_latest first and a pinned 2026-10-29 "
        "second -- and no leg covers that order. All 4 of its call-site stems are served from the "
        "pointer today (0 serve stale), but for 2 of them (owncross, sharediff) the pinned branch "
        "would serve a 2026-10-29 cut while a 2026-10-30 cut sits on disk."),
    "pit": (
        "(1) a stem is not case-stable on this disk -- OWNCROSS-2026-10-29.json sits beside "
        "owncross_latest.json, so an exact-case index reported the family as having no cuts and the "
        "exposure as zero. (2) an ordered container is not an order: a fixture loop over a tuple of "
        "face names has an order and decides nothing; the class ordered_list exists so a fixture is "
        "not credited with a resolution rule. (3) one assignment of a tuple of cuts is not a "
        "rebound -- NAMES = (a, b) was first read as the same target bound twice and printed a "
        "load-order winner for a tuple with no second assignment. (4) the study's own source had to "
        "join OWN_SOURCES or its fixture literals became rows on the next run (E319 family)."),
    "not_run": (
        "full 330+ leg smoke suite not re-run (~35 min); the new smoke leg was exec'd out of "
        "smoke_test.py standalone: PASS. GPU untouched (parked C-20261014-01); cloud untouched; "
        "nothing deleted, no quarantine action; bm-a/bm-c lane collectors honoured their guards."),
    "product": [
        "scripts/e329_two_vintage_binding.py (run / verify problems=[] / selftest 28/28)",
        "results/state_tilt/TWOVINTAGE-2026-11-01.json + twovintage_latest.json",
        "Tools/s6_chain_bmb.py leg two_vintage_binding (verify, ~7s)",
        "smoke_test.py leg (executed standalone: PASS)",
        "knowledge/METHODOLOGY_ASSETS.md card E329",
        "research/digests/DIGEST-20261101-r1349-e329-two-vintage.md",
        "results/runnable_pool.json E329 done with result_ref; E330 seeded ready",
    ],
    "pool": "E329 done with result_ref; E330-WHICH-FALLBACK-IS-UNCOVERED seeded ready (820 entries: 819 done / 1 ready)",
    "s1": "full suite not re-run this window; the new S6 leg ran verify problems=[] and the new smoke leg was exec'd standalone: PASS",
    "s6": ("orphan py_faces=7 orphans=0 residents=0 | dualrun ZERO-DRIFT 820 entries streak 51 | "
           "attrition CLEAN 4 ledgers (3 historical shrinks healed) | two_vintage_binding verify rc=0 "
           "~7s | sat engine rc=0 idle; compute_audit / py_watermark / lane collectors not re-run "
           "this window (stated plainly)"),
    "s7": ("schtasks table via zero-window wrapper: Bigmoney-IterationLoop / -LoopWatchdog / "
           "-SatEngine-bm-b / -Autofill all present; no drift observed"),
    "ts": ISO,
}

with io.open(STATE, encoding="utf-8") as fh:
    state = json.load(fh)
state["round_no"] = 1349
state["round"] = 1349
state["round_no_label"] = "r1349"
state["round_no_ts"] = ISO
state["ts"] = ISO
state["updated"] = ISO
state["updated_at"] = ISO
state["task"] = ("r1349 E329: 9 of 597 source-family pairs name two vintages of one stem; 1 is an "
                 "order-decided fallback chain whose order no leg covers")
state["task_short"] = "r1349 E329 two-vintage binding"
state["study"] = "E329_two_vintage_binding"
state["face"] = round_block["face"]
state["verdict"] = round_block["verdict"]
state["watermark_red"] = ("insufficient_history at open (1 ready card = E329, py idle); burned the "
                          "ready head E329 in-round and seeded E330")
state["watermark_note"] = round_block["s6"]
state["s1"] = round_block["s1"]
state["s6"] = round_block["s6"]
state["s7"] = round_block["s7"]
state["smoke"] = "leg E329 executed standalone: PASS (full suite not re-run this window)"
state["selftest"] = "e329_two_vintage_binding 28/28"
state["sat_engine"] = "rc=0 idle"
state["status"] = "green"
state["r1349"] = round_block

with io.open(STATE, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, indent=1, ensure_ascii=False)
    fh.write("\n")

with io.open(HEART, encoding="utf-8") as fh:
    heart = json.load(fh)
heart["round_no"] = 1349
heart["round"] = 1349
heart["last_seen"] = ISO
heart["ts"] = ISO
heart["clock_read"] = ISO
heart["heartbeat_epoch_utc"] = EPOCH
heart["task"] = state["task"]
heart["task_short"] = state["task_short"]
heart["study"] = "E329_two_vintage_binding"
heart["verdict"] = round_block["verdict"]
heart["work"] = "r1349 E329 two-vintage binding + delivery"
heart["watermark_red"] = state["watermark_red"]
heart["watermark_note"] = round_block["s6"]
heart["status"] = "green"
heart["s1"] = round_block["s1"]
heart["s6"] = round_block["s6"]
heart["s7"] = round_block["s7"]
heart["selftest"] = "e329_two_vintage_binding 28/28"
heart["smoke"] = state["smoke"]
heart["sat_engine"] = "rc=0 idle"
heart["agenda_starved"] = False
heart["r1349"] = {k: round_block[k] for k in ("dept", "face", "finding", "pit", "product", "verdict",
                                              "ts")}
with io.open(HEART, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(heart, fh, indent=1, ensure_ascii=False)
    fh.write("\n")

# re-read both faces and assert the types the readers pin
check = json.load(io.open(HEART, encoding="utf-8"))
assert isinstance(check["heartbeat_epoch_utc"], int), "epoch must be an int (F7)"
assert "T" in check["clock_read"] and "+" in check["clock_read"], "clock_read must be ISO with T"
json.load(io.open(STATE, encoding="utf-8"))
print("state + heartbeat written; round_no=%s epoch_type=%s clock=%s"
      % (check["round_no"], type(check["heartbeat_epoch_utc"]).__name__, check["clock_read"]))