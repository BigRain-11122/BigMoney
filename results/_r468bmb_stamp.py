"""_r468bmb_stamp.py -- heartbeat time-face stamp (R170/R178 epoch-int law).

Stamps bm-b heartbeat + state time faces with true UTC epoch (python int(time.time()))
and local ISO clock_read. Avoids the PS Get-Date -UFormat %s +8h double-count trap
observed r468 (1790780258 vs true ~1790751457). Idempotent; self-verifies isinstance(int).
"""
import json
import time

HB = r"fleet\machines\bm-b.json"
STATE = r"state.json"


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
    with open(HB, "w", encoding="utf-8") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
    with open(STATE, "r", encoding="utf-8") as f:
        st = json.load(f)
    st["last_round_at"] = now_iso
    st["last_round_ts"] = now_iso
    st["ts"] = now_iso
    st["updated"] = now_iso
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    with open(HB, "r", encoding="utf-8") as f:
        d2 = json.load(f)
    assert isinstance(d2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
    print("stamp OK epoch=%d clock=%s" % (d2["heartbeat_epoch_utc"], d2["clock_read"]))


if __name__ == "__main__":
    main()
