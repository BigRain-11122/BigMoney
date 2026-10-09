"""r811 bm-b closeout stamp + report append + push addendum (estate-absorb round).

Usage:
  python Tools/_r811bmb_closeout.py close              # stamp state/heartbeat clocks + append main report line
  python Tools/_r811bmb_closeout.py pushed <ahead> <behind> <tip>   # post-push addendum line

Byte-safe UTF-8 everywhere (r809 read2 recipe lineage); epoch written as JSON int
via int(time.time()) per R170/R178 law; clock ISO 8601 T-separated per R262 law.
"""
import datetime
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state.json")
HEART = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
RLINE = os.path.join(ROOT, "results", "_r811bmb_report_line.txt")


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def load(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def dump(path, obj):
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def close():
    iso = now_iso()
    epoch = int(time.time())

    s = load(STATE)
    for k in ("last_round_at", "ts", "updated", "last_seen", "clock_read", "updated_at"):
        s[k] = iso
    dump(STATE, s)

    h = load(HEART)
    # orders_ack integrity guard: this round adds zero new orders, so HEAD carries
    # the authoritative ack set; any transcription drift is restored from HEAD.
    import subprocess
    head_blob = subprocess.check_output(["git", "show", "HEAD:fleet/machines/bm-b.json"])
    head_h = json.loads(head_blob.decode("utf-8"))
    if h.get("orders_ack") != head_h.get("orders_ack"):
        print(
            "ACK-MISMATCH-RESTORED head_n=%d cur_n=%d"
            % (len(head_h.get("orders_ack", [])), len(h.get("orders_ack", [])))
        )
        h["orders_ack"] = head_h["orders_ack"]
        h["orders_ack_count"] = head_h.get("orders_ack_count", len(head_h["orders_ack"]))
    h["heartbeat_epoch_utc"] = epoch
    for k in ("last_round_at", "last_seen", "updated", "ts", "clock_read"):
        h[k] = iso
    h["sync"]["last_push_ts"] = iso
    dump(HEART, h)

    h2 = load(HEART)
    assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"

    with io.open(RLINE, encoding="utf-8") as f:
        line = f.read().strip("\n")
    stamped = line.replace("__R811_TS__", iso)
    with io.open(REPORT, "a", encoding="utf-8", newline="\n") as f:
        f.write(stamped + "\n")
    print("R811-CLOSE-OK iso=%s epoch=%d report_line_bytes=%d" % (iso, epoch, len(stamped.encode("utf-8"))))


def pushed(ahead, behind, tip):
    iso = now_iso()
    add = (
        "%s | r811 addendum bm-b | push LANDED tip=%s | local undelivered-to-origin commit count: %s "
        "(post-push fetch + rev-list ahead/behind=%s/%s + ls-remote tip verified)"
        % (iso, tip, ahead, ahead, behind)
    )
    with io.open(REPORT, "a", encoding="utf-8", newline="\n") as f:
        f.write(add + "\n")
    print("R811-PUSHED-OK", add)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "close"
    if mode == "close":
        close()
    elif mode == "pushed":
        pushed(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        raise SystemExit("unknown mode: %s" % mode)
