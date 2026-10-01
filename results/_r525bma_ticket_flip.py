"""r525 bm-a surgical ticket done-flips (T-125 W13 furnace arc, T-127 RW-1~7 close-out).
Byte-level anchored replacements, CRLF/LF preserved per file, json.loads roundtrip
validated before write (r504 law: JSON ticket edits must re-parse same round).
"""
import json
import sys

FLIPS = [
    {
        "file": "fleet/tasks/T-2026-09-30-125-P1.json",
        "nl": "\r\n",
        "status_old": ' "status": "claimed",',
        "status_new": ' "status": "done",',
        "ref_line": ' "result_ref": "results/trial_labor_w13/w13_judge.json + docs/trial_labor/CEO-REPORT-WAVE13-20260930.md (full arc on origin: GENERATE/SCREEN/JUDGE pool entries done, judge verdict = ledger head at r470, CEO report 09-30; 0 eligible = closed-family verdict per canon D-20260930-41)",',
        "anchor_status": ' "claimed_by": "bm-a",',
        "note_anchor": '-> intake -> CEO-REPORT-WAVE13 48h face"',
        "note_new": ('-> intake -> CEO-REPORT-WAVE13 48h face. '
                     '|| r525 bm-a DONE-FLIP: W13 furnace arc complete on origin '
                     '(GENERATE/SCREEN/JUDGE done; w13_judge.json ledger head r470; '
                     'CEO-REPORT-WAVE13-20260930.md delivered; 0 eligible per canon '
                     'D-20260930-41 closed-family; r464 surgeon-skeleton next-pointer '
                     'was stale per r302 three-check -- all slices already landed)"'),
    },
    {
        "file": "fleet/tasks/T-2026-09-30-127-P1.json",
        "nl": "\n",
        "status_old": ' "status": "claimed",',
        "status_new": ' "status": "done",',
        "ref_line": ' "result_ref": "results/RW6_FINAL_TABLE_20260930.md + results/RW1_MEMBER_DIFF_20260930.md + knowledge/panel_gate.py + live/gateway.py RW-7 sole-order-exit (close-out commit 0dc1bf5e7; conflict-copies cleanup r472 875ca03c4; RW-1~4 all-green verdict r476; 10-03 external audit = independent confirmation face per frozen criteria)",',
        "anchor_status": ' "claimed_by": "bm-a",',
        "note_anchor": '= science-face decision, not taken"',
        "note_new": ('= science-face decision, not taken. '
                     '|| r525 bm-a DONE-FLIP: RW-1~RW-7 all landed in the r472-r480 '
                     'close-out window per HANDOVER (RW-1 r472 / RW-2 in-storm / RW-3 r475 / '
                     'RW-4 r476 all-green verdict / RW-6 r477 / RW-7 r480 0dc1bf5e7 + '
                     'conflict-copies cleanup r472); ticket status now matches the '
                     'r480 close-out commit message)"'),
    },
]

for fl in FLIPS:
    path = fl["file"]
    raw = open(path, "rb").read().decode("utf-8")
    for needle in (fl["status_old"], fl["anchor_status"], fl["note_anchor"]):
        if raw.count(needle) != 1:
            print(f"FAIL {path}: anchor not unique: {needle[:50]!r} count={raw.count(needle)}")
            sys.exit(1)
    raw = raw.replace(fl["status_old"], fl["status_new"], 1)
    raw = raw.replace(fl["anchor_status"], fl["ref_line"] + fl["nl"] + fl["anchor_status"], 1)
    raw = raw.replace(fl["note_anchor"], fl["note_new"], 1)
    obj = json.loads(raw)  # roundtrip validation (r504 law)
    assert obj["status"] == "done" and "result_ref" in obj, path
    assert "\r\n" not in raw if fl["nl"] == "\n" else True, "LF-file CRLF contamination"
    open(path, "wb").write(raw.encode("utf-8"))
    print(f"OK {path}: status=done result_ref landed, json.loads roundtrip PASS")
print("ALL FLIPS DONE")
