# -*- coding: utf-8 -*-
"""r360 bm-a S7 addendum: push-storm two-pass resolution record + state/heartbeat
refresh (r359 addendum pattern)."""
import datetime
import io
import json
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

RLINE = (
    NOW + " | R360 addendum bm-a | two-pass push-storm resolved + PUSHED b73296d6 (96deea98..b73296d6): "
    "pass-1 = 16-UU vs bmc-r111 (origin 605169e6, classifier 16/16 GREEN 0-UNKNOWN): 12 snapshots take-MINE "
    "deep-probe fresher (mine 22:20:48-22:22:11 vs origin 22:19:25-22:20:53, r100/R350 value-shape gate), "
    "REPORT json+md twins SAME-SIDE MINE (22:22:09>22:20:52, r327/r329 coupling), dash json+js pair SAME-SIDE "
    "MINE (R209 wrapper whole-bytes), autofill launches 48+48->48 identical-dedupe + last_tick origin 22:20:02 > "
    "mine 22:20:01, compute_audit history ts-key union, regime state take-mine 22:20:49; PASS-1 DEFECT "
    "SELF-CAUGHT pre-push: resolver cap bug truncated union 201+201->201 dropping oldest row 2026-09-26 20:01:54 "
    "vs canon |A∪B|=202 (r344 no-cap precedent 236-kept; r85 = anti-false-flag only, never licenses resolver "
    "truncation) -> row restored + amended in the pre-push window (r359 law: 推前窗=唯一修正期), resolver patched "
    "no-cap; pass-2 vs bmb-r345 (origin 96deea98, 3 union faces): autofill launches 47+48->48 (origin subset of "
    "mine) + last_tick tie 22:20:02->HEAD origin (r140/r344 same-tick precedent), compute_audit 238+202->239 "
    "distinct |A∪B| zero-loss audited, regime state mine 22:20:49 newer; r290 blocker live-fire: unstaged "
    "resolver patch (AM face) blocked rebase --continue with misleading 'You must edit all merge conflicts' -> "
    "targeted add per r290/r344 law, continue clean; HANDOVER automerge sanity = R360 promote + bmb r345 audit "
    "line both present zero markers (R210 anchor respected by construction: my L4 edit + their tail line "
    "non-overlapping); post-fold pool ID-set audit (r344 law): 80=80 zero-diff, W2A ready lane=bm-b + W2B "
    "waiting d8_receipt intact | verify: PARSE-VERIFY 16/16 + 3/3 r185, union asserts in-resolver, push FAST "
    "both passes, worktree clean post-push | next: unchanged -- Mon 09-28 09:15 T-91 s3 auto-fire; bm-b W2-A "
    "finalize + W2-B dep-2 sequence; council 09-29 12:00; next 5x=R365 HANDOVER")

with io.open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(RLINE + "\n")

sp = "state-bm-a.json"
st = json.load(io.open(sp, encoding="utf-8"))
st["current_task"] = ("r360 closed+pushed b73296d6: 5x HANDOVER R360 promote landed, two-pass push-storm "
                      "16-UU+3-UU resolved per canon (pool 80 zero-diff, audit union 239 no-cap)")
st["updated"] = NOW
io.open(sp, "w", encoding="utf-8", newline="\n").write(json.dumps(st, ensure_ascii=False, indent=1) + "\n")

hp = "fleet/machines/bm-a.json"
hb = json.load(io.open(hp, encoding="utf-8"))
hb["last_seen"] = NOW
hb["current_task"] = st["current_task"]
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
io.open(hp, "w", encoding="utf-8", newline="\n").write(json.dumps(hb, ensure_ascii=False, indent=1) + "\n")
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int) and "T" in chk["clock_read"]
print("addendum OK epoch=", EPOCH, NOW)
