# -*- coding: utf-8 -*-
"""r666 bm-c trio watch revival addendum (withdrawal face, r664 pattern)."""
import json
import os
import sys

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "_r666bmc_trio_watch.json")
with open(P, encoding="utf-8-sig") as fh:
    d = json.load(fh)
d["revival_addendum"] = {
    "ts": "2026-10-07T09:24:00+08:00",
    "verdict_update": "WITHDRAWN -- bm-b revived in the minutes right after the 09:15:34 verdict probe; escalation MSG RESOLVED note appended (r664 pattern); aging line lifted; ~10:30 next rung disarmed",
    "revival_evidence_origin": [
        "8d47a5427 09:15:11 r802 churn-absorb-4 (mid-rebase live lane window)",
        "477083d30 09:15:12 r802 churn-absorb-2 (autofill tick + Q claim face refresh, burn done)",
        "2c63b0585 09:15:58 r802 churn-absorb-3 (live lane tick window)",
        "09217e0cc 09:16:19 autofill keepalive fund-divlowvol-p1-nulls owner=bm-b",
    ],
    "counters_at_withdrawal": {
        "quality": "2000/2000 COMPLETE (mtime 09:21:47) -- first-to-2000 reached, r668 execution face = bm-b",
        "divlowvol": "1674/2000 advancing (mtime 09:21:47)",
        "value": "2000/2000 complete (unaffected)",
        "crash_fuse_active": {},
    },
    "honesty_note": "verdict probe fetch at 09:15:34 did not yet contain the revival commits (pushed after probe) -- verdict was legal on evidence visible at probe time; bm-b recovery actions started ~09:08 (status faces ts 09:08:10-09:08:15), near-simultaneous race with the aging line, not a false alarm",
    "hb_note": "bm-b hb still 06:40:15 at withdrawal = r802 mid-flight not yet closed, not a darkness signal",
}
with open(P, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
# whole-file re-validation (r504 law)
with open(P, encoding="utf-8-sig") as fh:
    chk = json.load(fh)
assert "revival_addendum" in chk
print("TRIO_WATCH_ADDENDUM_OK keys=%d" % len(chk))
