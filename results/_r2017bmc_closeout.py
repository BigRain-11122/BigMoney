"""r2017 closeout (bm-c): advance the round counter and stage the heartbeat fields.

Guard (r2015 precedent): the counter is advanced only if the face still reads the
predecessor round, so a re-run cannot double-count a round.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "results", "_r2017bmc_hb_fields.json")

PREV, NOW = 2016, 2017


def now_iso() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def main() -> int:
    with open(STATE, "r", encoding="utf-8") as fh:
        st = json.load(fh)

    if int(st.get("round_no", 0)) == PREV:
        st["round_no_prev"] = PREV
        st["round_no"] = NOW
        st["rounds_done"] = int(st.get("rounds_done", 0)) + 1
        st["last_round_at"] = now_iso()
        with open(STATE, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(st, fh, ensure_ascii=False, indent=1)
        print("state: round_no %d->%d rounds_done->%d" % (PREV, NOW, st["rounds_done"]))
    elif int(st.get("round_no", 0)) == NOW:
        print("state: already at %d (idempotent, no advance)" % NOW)
    else:
        print("state: UNEXPECTED round_no=%r (expected %d) -- not touched"
              % (st.get("round_no"), PREV))
        return 3

    ts = now_iso()
    fields = {
        "round": NOW,
        "round_no": NOW,
        "machine_id": "bm-c",
        "last_seen": ts,
        "clock_read": ts,
        "ts": ts,
        "heartbeat_epoch_utc": int(time.time()),
        "current_task": "r2017 turnover layers: is the book's churn the universe under it or names flapping across the veto edge?",
        "verdict": "healthy",
    }
    with open(HB, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fields, fh, ensure_ascii=False, indent=1)
    print("heartbeat fields -> %s" % os.path.relpath(HB, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
