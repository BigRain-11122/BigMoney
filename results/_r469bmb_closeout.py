"""_r469bmb_closeout.py -- r469 round close-out faces (heartbeat + state).

r468 stamp-helper lineage: epoch via python int(time.time()) (R170/R178 law),
clock_read ISO with T separator + UTC offset (R262 law), self-verifies isinstance(int).
"""
import json
import time

HB = r"fleet\machines\bm-b.json"
STATE = r"state.json"

CURRENT = ("r469 unfreeze-transition round closed: S6 38-leg all rc0, "
           "32-UU stash-pop canon-resolved zero-loss, RW-5 unfreeze condition met "
           "(bm-a r476 086e6f584) -- pool shards watch on")

VERDICT = ("unfreeze-transition: RW-1~4 ALL GREEN (bm-a r476 RW-4 panel-gate done) -> "
           "RW-5 unfreeze condition met, supply lines legal from next rounds; "
           "RW-6 recompute = bm-a r477 next (anti-dup held, bm-b waits pool shards) "
           "| CURRENT: r469 closed -- S6 38-leg all rc0 NON-GREEN=NONE "
           "| LAST-ARTIFACT: docs/live_usage/LIVE-2026-09-30.md (ORANGE cap50) + "
           "REPORT-2026-09-30 faces=5 + marks-20260930.jsonl 62-line zero-loss union + "
           "minute_feed +93rows/5syms @15:04 "
           "| NEXT: >=15:35 round (~15:42) fires 09-30 post-close unlock legs "
           "(live.paper/t35/prospect accrue, bm-b etf_daily lane); 2026-10-01 "
           "month-first trio + REGIME_GUARD v3 date-gate auto; RW-6 shards appear -> bm-b claims")

STATE_NOTE = ("r469 unfreeze-transition round: S0 FF-pull landed bm-a r476 (RW-4 done -> "
              "RW-1~4 all green -> RW-5 unfreeze condition met) + bm-c r275; stash-pop 32-UU "
              "same-family batch canon-resolved via _r469bmb_resolve.py (r467 lineage: "
              "snapshots take-s3 mine-newer 15:04-05 vs 14:59-15:01, marks 61+59->62 union, "
              "x2_watch 1980+1980->1986, compute_audit history 206+201->207, regime identity 3+3->3, "
              "twins same-side forced); S6 38-leg all rc0 NON-GREEN=NONE (dualrun ZERO-DRIFT 51/3 "
              "@139, marks tick settle-recorded, regime ORANGE breadth 0.83, minute_feed +93 rows, "
              "cutoff 09-29 pre-15:30 legal no-op); orders 127/127 zero-unacked both scans; board 0 "
              "open pool 139/139 done (RW-6 recompute shards not yet submitted -- bm-a r477 next); "
              "NEXT: >=15:35 round = 09-30 post-close unlock legs; 2026-10-01 month-first trio + "
              "REGIME_GUARD v3 date-gate; RW-6 shards -> claim")


def iso_now():
    return time.strftime("%Y-%m-%dT%H:%M:%S") + time.strftime("%z")[:3] + ":" + time.strftime("%z")[3:]


def main():
    now_iso = iso_now()
    epoch = int(time.time())
    with open(HB, "r", encoding="utf-8") as f:
        hb = json.load(f)
    hb["heartbeat_epoch_utc"] = epoch
    hb["last_seen"] = now_iso
    hb["clock_read"] = now_iso
    hb["last_round_at"] = now_iso
    hb["round_no"] = 469
    hb["round"] = 469
    hb["loop_round"] = 469
    hb["current_task"] = CURRENT
    hb["verdict"] = VERDICT
    with open(HB, "w", encoding="utf-8") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
    with open(STATE, "r", encoding="utf-8") as f:
        st = json.load(f)
    st["round_no"] = 469
    st["note"] = STATE_NOTE
    st["last_round_at"] = now_iso
    st["last_round_ts"] = now_iso
    st["ts"] = now_iso
    st["updated"] = now_iso
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    with open(HB, "r", encoding="utf-8") as f:
        d2 = json.load(f)
    assert isinstance(d2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
    assert "T" in d2["clock_read"], "clock_read must be T-separated"
    print("closeout OK epoch=%d clock=%s round=%d" % (
        d2["heartbeat_epoch_utc"], d2["clock_read"], d2["round_no"]))


if __name__ == "__main__":
    main()
