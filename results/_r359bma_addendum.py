# -*- coding: utf-8 -*-
"""r359 bm-a storm addendum: round-report line + heartbeat/state refresh
after the two-pass push-storm resolution and successful push 1d707d2a."""
import json
import time

now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
now_epoch = int(time.time())

addendum = (
    "2026-09-27" + now_iso[10:] + " | R359 addendum bm-a | "
    "push-storm TWO passes resolved + PUSHED 1d707d2a (15c2770e..1d707d2a): "
    "pass-1 18-UU vs origin f84502d4 (bmc r110 batch-30 archival + bmb r344 fold chain) -- "
    "side-assert :2:=origin/:3:=mine per r351, sides sourced from COMMIT BLOBS (tick-immune, 22:10 tick window "
    "respected per r351 law-3 wait-85s); classifier 17 classified + 1 UNKNOWN (archive) fail-closed -> manual; "
    "recipes: snapshots x11 take-new hardened deep-probe ALL->MINE (my S6 22:02 fresher than origin-side 21:5x "
    "bmc-r110 chain; probe strip [_-]+^20..-shape+time-of-day gate per r100/R350), REPORT/dashboard twins "
    "same-side coupling (json probe decides, md/js whole-bytes copy same side), compute_audit history "
    "235+201->236 ts-key union zero-loss + snapshot MINE@22:02:02, regime_state union + state take-HEAD "
    "(date-only asof cannot feed wall-clock max), autofill_state launches composite-key union 48+48->48 "
    "(identical-dedupe, ASC sort, cap50) + last_tick take-ORIGIN@22:00:02 tie->HEAD; "
    "pool (git auto-merged, structural verify): 80 entries, W2B x1 = f5822d92 + bmb d8_receipt SUPERSET face "
    "(r322 field-superset law -- first-pass verbatim-adopt had wiped bmb's D8-receipt dep-1 marker, caught "
    "in-window and reversed before continue; d8_receipt = bmb received the 60.4MB npz, sha256 verified "
    "per their r344 close); W2A lane_owner=bm-b intact; "
    "CODELY.md memory-union both-sides-restructured face: origin r110 batch-30 structure as base "
    "(their 10-row fold-to-nothing = verbatim-in-29th-batch reliance, r342 wrapped-verbatim in their "
    "batch-30 section) + my batch renumbered 30->31 per r176 yield law (origin pushed first) with "
    "r109-fold (origin kept it hot, hard line binds, verbatim now in batch-31) + r359 pointer + batch-31 "
    "summary; 2 redundant r353-annotations trimmed; origin rows 23/23 covered; final 10,222B <= 10,240B "
    "hard line (shave ladder); archive: origin batch-30 kept verbatim + batch-31 section appended "
    "(r109/r342/r359 verbatim; r342 dual-record wrapped-30th/plain-31st = dual-record precedent); "
    "pass-2 = single tick-keepalive commit 15c2770e, rebase auto-merged 0-UU, tick-side 48 launch rows "
    "zero-loss verified post-push; pre-push amend fixed commit message (batch renumber + storm facts); "
    "resolver evidence results/_r359bma_resolve.py | "
    "verify: 18 UU -> 0 remaining, all json.loads-verified on write, push FAST (both passes), "
    "autofill tick-face zero-loss, pool d8_receipt preserved | "
    "next: unchanged -- Mon 09-28 09:15 T-91 s3 auto-fire; bm-b W2-A finalize + W2-B sequence "
    "(dep-1 D8 RECEIPT now stamped in pool row, dep-2 = W2-A finalize); council 09-29 12:00; 5x=R360 HANDOVER\n")

with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8", newline="\n") as fh:
    fh.write(addendum)

# heartbeat + state refresh (fresh timestamp law)
with open("fleet/machines/bm-a.json", encoding="utf-8") as fh:
    hb = json.load(fh)
hb["last_seen"] = now_iso
hb["heartbeat_epoch_utc"] = now_epoch
hb["clock_read"] = now_iso
hb["current_task"] = "r359 closed+pushed: W2B pool row restored (d8_receipt superset kept), CODELY batch-31, 2-pass storm resolved"
with open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
with open("fleet/machines/bm-a.json", encoding="utf-8") as fh:
    chk = json.load(fh)
assert isinstance(chk["heartbeat_epoch_utc"], int) and "T" in chk["clock_read"]

with open("state-bm-a.json", encoding="utf-8") as fh:
    st = json.load(fh)
st["current_task"] = hb["current_task"]
st["updated"] = now_iso
with open("state-bm-a.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)

print("addendum OK: report line + heartbeat (epoch", now_epoch, "int) + state refreshed")
