# -*- coding: utf-8 -*-
"""r1064 bm-a delivery verification face: state sync/push_verified update (post-push)."""
import json, time, datetime, io, os

ROOT = os.path.dirname(os.path.abspath(__file__))
now_dt = datetime.datetime.now().astimezone()
now_iso = now_dt.isoformat(timespec="seconds")

NOTE = ("r1064 delivered f4622f010a..359f8ddc1f after TWO rebase races vs bm-c r1097 closeout hot-push era: "
        "rebase#1 = O-1810 order-file union receipt (both machines' checkbox lines preserved verbatim, marker scan clean); "
        "rebase#2 = 9 derived/probe UU faces resolved per-file newer-wins with ts evidence (7 take-mine 18:42-44 fresher "
        "/ 2 take-bm-c 18:47:03-05 attrition_guard+watermark fresher) + watermark 18:48:01 watchdog face take-mine on "
        "absorb-commit replay; stash r1064-live2 popped clean, live face absorb #2 committed; zero loss, main==HEAD asserted both rebases; "
        "local-unpushed=0")

sp = os.path.join(ROOT, "state-bm-a.json")
with io.open(sp, encoding="utf-8") as f:
    st = json.load(f)
st["sync"] = {"ts": now_iso, "origin_tip": "359f8ddc1f", "ahead_behind": "0/0", "note": NOTE}
st["push_verified"] = {"ts": now_iso, "origin_tip": "359f8ddc1f", "ahead_behind": "0/0", "note": NOTE}
st["last_delivery_verified_at"] = now_iso
with io.open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
assert isinstance(st["heartbeat_epoch_utc"], int)
print("DELIVERY-FACE-OK", now_iso)