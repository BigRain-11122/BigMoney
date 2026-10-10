#!/usr/bin/env python
# r858 bm-b T23 census autofire watcher, SECOND GENERATION (re-arm).
# Lineage: r854 watcher (_r854bmb_t23_autofire.py) honestly timed out at
# 03:27:56 (receipt state=timeout, 90-min window, astock refresh incomplete
# 5219/5229 with 10 persistent structural failures quarantined at 3/3
# attempts). Per r857 readout design: timeout -> quarantine carryover check
# + re-arm (move stale receipt before re-spawn per single-flight law).
# Carryover verdict: the 10 quarantined codes are excluded from _todo_for,
# so the next refresh pass has remaining=0 -> panel flips complete; census
# universe = per-file intersection, drops the 10, disclosed in burn product.
# This clone keeps the r854 watcher logic verbatim with r858 identity and a
# belt-and-braces single-flight guard on the OLD receipt path too.
# Encoding: pure ASCII body (repo PS/py GBK decode law).
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNNER = os.path.join(ROOT, "scripts", "t23_random_grammar_census.py")
RECEIPT = os.path.join(ROOT, "results", "_r858bmb_t23_watch_receipt.json")
LEGACY_RECEIPT = os.path.join(ROOT, "results", "_r854bmb_t23_autofire_receipt.json")
WATCH_LOG = os.path.join(ROOT, "results", "_r858bmb_t23_watch.log")
RUN_LOG = os.path.join(ROOT, "logs", "t23_census_run.log")
POLL_S = 45
MAX_MIN = 90


def log(msg):
    line = "%s %s" % (time.strftime("%Y-%m-%dT%H:%M:%S"), msg)
    with open(WATCH_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def write_receipt(state, extra=None):
    doc = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "round": 858,
        "machine": "bm-b",
        "state": state,
        "poll_s": POLL_S,
        "max_min": MAX_MIN,
        "runner": "scripts/t23_random_grammar_census.py",
    }
    if extra:
        doc.update(extra)
    tmp = RECEIPT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, RECEIPT)


def gate_face():
    p = subprocess.run([sys.executable, RUNNER, "status"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=120)
    try:
        return json.loads(p.stdout), p.returncode
    except Exception:
        return None, p.returncode


def main():
    if os.path.exists(RECEIPT):
        log("receipt exists, refusing to start (single-flight law)")
        return 0
    if os.path.exists(LEGACY_RECEIPT):
        log("legacy r854 receipt still exists, refusing to start "
            "(single-flight law, belt-and-braces)")
        return 0
    write_receipt("watching")
    log("watcher up (r858 re-arm), polling gate every %ds (max %d min)"
        % (POLL_S, MAX_MIN))
    deadline = time.time() + MAX_MIN * 60
    last_face = None
    while time.time() < deadline:
        try:
            face, rc = gate_face()
        except Exception as e:
            log("gate probe error: %r" % (e,))
            time.sleep(POLL_S)
            continue
        last_face = face
        if face is not None and face.get("ready") is True:
            log("gate ready=true -> spawning detached burn")
            flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                     | subprocess.CREATE_NO_WINDOW)
            os.makedirs(os.path.dirname(RUN_LOG), exist_ok=True)
            with open(RUN_LOG, "a", encoding="utf-8") as lf:
                proc = subprocess.Popen(
                    [sys.executable, RUNNER, "run"],
                    stdout=lf, stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL, creationflags=flags,
                    close_fds=False, cwd=ROOT)
            write_receipt("fired", {"pid": proc.pid, "run_log": RUN_LOG,
                                    "gate_face": face})
            log("burn spawned pid=%s log=%s" % (proc.pid, RUN_LOG))
            return 0
        log("not ready (disk=%s status=%s mode=%s)"
            % (face.get("per_files_on_disk"), face.get("status_per_files"),
               face.get("mode")))
        time.sleep(POLL_S)
    write_receipt("timeout", {"gate_face": last_face})
    log("timeout after %d min, honest exit (next round re-fires)" % MAX_MIN)
    return 0


if __name__ == "__main__":
    sys.exit(main())
