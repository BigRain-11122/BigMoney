"""Tools/t36_drill_runner.py -- T-36 d3 stale-takeover real-fire drill runner
(O-20260924-2100 s2.4 acceptance injection: "stalled shard -> auto-released
and taken over by healthy machine").

One-shot drill payload launched by Tools/autofill.py C8 when a ready shard
owned by a >20-min-stale heartbeat is taken over by this machine. It is NOT
science compute: it proves the takeover path end-to-end by writing a
deterministic evidence file (results/t36_stale_takeover_drill.json) +
one checkpoint line, running the workers_plan burn (default 2 workers x
~6s busy loop, BelowNormal inherited from the autofill launch), exit 0.

Idempotent: evidence write is atomic (.tmp + os.replace); a second launch
post-exit simply rewrites the evidence (drill window is round-controlled).
Exit codes: 0 = drill complete, 2 = mechanism fault (never mask).
selftest = offline evidence/checkpoint write logic, no real burn.
"""
import json
import os
import sys
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE = os.path.join(ROOT, "results", "t36_stale_takeover_drill.json")
CHECKPOINT = os.path.join(ROOT, "results", "t36_drill_checkpoint.jsonl")
MACHINE_JSON = os.path.join(ROOT, "fleet", "machine.json")
DRILL_ID = "DRILL-T36-STALE-TAKEOVER"


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _machine_id():
    try:
        with open(MACHINE_JSON, encoding="utf-8") as fh:
            return json.load(fh).get("machine_id", "")
    except Exception:
        return ""


def _parent_cmd():
    try:
        import psutil
        return " ".join(psutil.Process(os.getppid()).cmdline() or [])[:300]
    except Exception:
        return "unavailable"


def _burn(seconds):
    """Busy-loop ~`seconds` wall time (single process, drill-scale burn)."""
    t0 = time.time()
    x = 0.0
    while time.time() - t0 < seconds:
        x += 1.0 / (x % 7.0 + 1.0)
    return round(time.time() - t0, 2)


def run(burn_s=6.0):
    ts_start = _now()
    t0 = time.time()
    try:
        burned = _burn(burn_s)
        os.makedirs(os.path.dirname(CHECKPOINT), exist_ok=True)
        with open(CHECKPOINT, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(
                {"ts": _now(), "pid": os.getpid(), "drill": DRILL_ID,
                 "phase": "drill_complete"}, ensure_ascii=False) + "\n")
        rec = {"drill": DRILL_ID,
               "verdict": "drill_complete",
               "ts_start": ts_start, "ts_end": _now(),
               "pid": os.getpid(),
               "machine_id": _machine_id(),
               "parent_cmd": _parent_cmd(),
               "burn_seconds_plan": burn_s,
               "burn_seconds_actual": burned,
               "wall_s": round(time.time() - t0, 2),
               "evidence_note": ("real-fire stale-takeover acceptance: "
                                 "launched by autofill C8 after >20min-stale "
                                 "shard-owner release (T-36 d3)")}
        tmp = EVIDENCE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, EVIDENCE)
        print(json.dumps({"ok": True, "evidence": EVIDENCE},
                         ensure_ascii=False))
        return 0
    except Exception as ex:
        print(f"drill mechanism fault: {ex}", file=sys.stderr)
        return 2


def selftest():
    global EVIDENCE, CHECKPOINT
    import tempfile
    ok_all = True

    def ok(name, cond):
        nonlocal ok_all
        ok_all &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    print("t36_drill_runner selftest:")
    with tempfile.TemporaryDirectory() as tmp:
        EVIDENCE = os.path.join(tmp, "evidence.json")
        CHECKPOINT = os.path.join(tmp, "ckpt.jsonl")
        rc = run(burn_s=0.1)
        ok("S1 run rc0", rc == 0)
        ev = json.load(open(EVIDENCE, encoding="utf-8"))
        ok("S2 evidence keys", ev["drill"] == DRILL_ID
           and ev["verdict"] == "drill_complete" and "pid" in ev)
        ok("S3 checkpoint line", "drill_complete" in open(
            CHECKPOINT, encoding="utf-8").read())
        rc2 = run(burn_s=0.1)
        ev2 = json.load(open(EVIDENCE, encoding="utf-8"))
        ok("S4 idempotent rerun rc0 + overwrite", rc2 == 0
           and ev2["verdict"] == "drill_complete")
    print("SELFTEST", "ALL PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


def main():
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(run())


if __name__ == "__main__":
    main()
