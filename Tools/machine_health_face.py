#!/usr/bin/env python
"""fleet/machine-health.json -- canonical face builder + tripwire (D-20261028-02).

WHY THIS EXISTS
---------------
The face had drifted into a shape no reader could use. Read it on 2026-10-27:

    json.load(...) -> list
    [{"value": [{"value": [{"value": [{"value": [{"value": " ", "Count": 2},
     ... "@{name=qwen3.8:4b; model=qwen3.8:4b; size=3711319408; ...}"

i.e. three shell layers of {"value": ...} wrapped around PowerShell hashtable
`.ToString()` strings. Two separate damages:

  1. THE CONTENT was never this face's (an ollama inventory was serialised into
     this path at some point).
  2. THE WRITER RE-READS ITS OWN OUTPUT before appending. Whatever it finds is
     carried forward verbatim, so one bad payload becomes a nesting generator:
     each hourly run wrapped the previous generation one level deeper.

A reader that only accepts `{machine: {...}}` therefore gets nothing, and a
reader that "fails soft" gets nothing *silently* -- monitor/build_status.py's
union helper returned {} and the panel showed blank machine rows rather than
UNKNOWN. That is the fail-open case D-20261028-02 item 3 forbids.

THIS TOOL
---------
`write`  rebuilds the face from live readings: the machine's own heartbeat
         (fleet/machines/<id>.json, written by this lane every round) plus the
         wall clock. Other machines' entries are carried over ONLY if they are
         well-formed; malformed entries are dropped rather than propagated.
`check`  validates the shape and says UNKNOWN out loud when it cannot read it.
`selftest` pins the three shapes that matter: canonical map kept, legacy hourly
         row array converted, {"value": ...} shell rejected (not carried).

Canonical shape (D-20261028-02 item 1, pinned):

    {"<machine>": {"ts": ..., "cpu": ..., "ram_free_gb": ...,
                   "gpu": {"util": ..., "free_gb": ...},
                   "util": ..., "work": ...}}

Usage:
    python Tools/machine_health_face.py check
    python Tools/machine_health_face.py write [--machine bm-b]
    python Tools/machine_health_face.py selftest
"""
import argparse
import json
import os
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE = os.path.join(ROOT, "fleet", "machine-health.json")
HEARTBEAT_DIR = os.path.join(ROOT, "fleet", "machines")

MACHINE_FIELDS = ("ts", "cpu", "ram_free_gb", "gpu", "util", "work")


def _looks_like_entry(v):
    """An entry is a mapping that carries a timestamp. Anything else -- including
    the {"value": ...} shells -- is not a row and must not be adopted."""
    return isinstance(v, dict) and isinstance(v.get("ts"), str) and bool(v.get("ts"))


def read_face(path=FACE):
    """-> (machines, status) with status in {ok, empty, missing, unreadable}.

    Accepts BOTH shapes on purpose: the canonical machine map, and the legacy
    hourly row array this face used to be. A later row for the same machine
    wins, which is what every consumer wanted in the first place.
    """
    if not os.path.exists(path):
        return {}, "missing", 0
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception:
        return {}, "unreadable", 0

    machines = {}
    if isinstance(data, dict):
        if _looks_like_entry(data):
            # a single legacy row: {ts, <machine>: {...}}
            for k, v in data.items():
                if k != "ts" and _looks_like_entry(v):
                    machines[str(k)] = v
        else:
            for k, v in data.items():
                if _looks_like_entry(v):
                    machines[str(k)] = v
    elif isinstance(data, list):
        for row in data:
            if not isinstance(row, dict):
                continue
            for k, v in row.items():
                if k != "ts" and _looks_like_entry(v):
                    machines[str(k)] = v
    dropped = 0
    if isinstance(data, list):
        dropped = sum(1 for r in data if not isinstance(r, dict))
    status = "ok" if machines else ("empty" if not data else "unreadable")
    return machines, status, dropped


def _heartbeat(machine):
    p = os.path.join(HEARTBEAT_DIR, machine + ".json")
    try:
        with open(p, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def _num(v):
    try:
        return round(float(v), 2)
    except Exception:
        return None


def build_entry(machine, hb=None, now=None):
    """One canonical entry. Missing readings stay None -- the face says UNKNOWN
    by omission instead of inventing a plausible number."""
    hb = _heartbeat(machine) if hb is None else hb
    now = now or time.strftime("%Y-%m-%d %H:%M")
    gpu = {
        "util": _num(hb.get("gpu_util_pct") or hb.get("gpu_util")),
        "free_gb": _num(hb.get("free_vram_gb") or hb.get("gpu_free_gb")),
    }
    return {
        "ts": str(hb.get("ts") or now)[:16],
        "cpu": _num(hb.get("cpu_pct") or hb.get("cpu_util_pct")),
        "ram_free_gb": _num(hb.get("free_ram_gb")),
        "gpu": gpu,
        "util": str(hb.get("status") or hb.get("verdict") or "")[:40] or None,
        "work": str(hb.get("current_task") or hb.get("task") or "")[:200] or None,
    }


def write_face(machine, path=FACE):
    machines, status, _dropped = read_face(path)
    machines[machine] = build_entry(machine)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(machines, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)
    return machines, status


def check(path=FACE):
    machines, status, dropped = read_face(path)
    if status != "ok":
        print("machine-health: UNKNOWN (%s) -- a reader must not treat this as healthy" % status)
        return 2
    blank = [m for m, e in machines.items() if not e.get("ts")]
    print("machine-health: OK machines=%d dropped_junk=%d blank=%d %s"
          % (len(machines), dropped, len(blank), ",".join(sorted(machines))))
    return 0


def _selftest():
    ok = []

    def leg(name, cond, detail=""):
        ok.append((name, bool(cond), detail))

    d = tempfile.mkdtemp(prefix="mhface_")
    canonical = os.path.join(d, "canonical.json")
    with open(canonical, "w", encoding="utf-8") as fh:
        json.dump({"bm-a": {"ts": "2026-10-27 22:00", "cpu": 12.0, "util": "green"}}, fh)

    m, s, _ = read_face(canonical)
    leg("canonical map is read as machine-keyed", s == "ok" and list(m) == ["bm-a"], str(m))

    legacy = os.path.join(d, "legacy.json")
    with open(legacy, "w", encoding="utf-8") as fh:
        json.dump([{"ts": "2026-10-27 21:00", "bm-b": {"ts": "2026-10-27 21:00", "util": "green"}},
                   {"ts": "2026-10-27 22:00", "bm-b": {"ts": "2026-10-27 22:00", "util": "amber"}},
                   {"ts": "2026-10-27 22:00", "bm-c": {"ts": "2026-10-27 22:00", "util": "green"}}], fh)

    m, s, _ = read_face(legacy)
    leg("legacy hourly array is converted (newest row per machine wins)",
        s == "ok" and m["bm-b"]["util"] == "amber" and set(m) == {"bm-b", "bm-c"}, str(m))

    shell = os.path.join(d, "shell.json")
    with open(shell, "w", encoding="utf-8") as fh:
        json.dump([{"value": [{"value": "@{name=qwen3.8:4b; size=1}", "Count": 2}]}], fh)

    m, s, dropped = read_face(shell)
    leg("the {\"value\": ...} shells are rejected, not carried forward",
        s != "ok" and m == {}, "status=%s machines=%s" % (s, m))
    leg("a reader gets rc!=0 instead of a silent empty panel", check(shell) == 2, "")

    merged = os.path.join(d, "merged.json")
    with open(merged, "w", encoding="utf-8") as fh:
        json.dump({"bm-a": {"ts": "2026-10-27 22:00", "util": "green"},
                   "bm-junk": {"value": "nope"}}, fh)

    machines, _ = write_face("bm-b", merged)
    leg("write keeps a well-formed foreign entry", "bm-a" in machines, str(sorted(machines)))
    leg("write drops a malformed foreign entry", "bm-junk" not in machines, str(sorted(machines)))
    leg("write lands the canonical fields",
        all(k in machines["bm-b"] for k in ("ts", "cpu", "ram_free_gb", "gpu", "util", "work")),
        str(sorted(machines["bm-b"])))
    leg("write is a map, so json.load gives a dict",
        isinstance(json.load(open(merged, encoding="utf-8")), dict), "")

    bad = os.path.join(d, "bad.json")
    with open(bad, "w", encoding="utf-8") as fh:
        fh.write("not json at all")
    m, s, _ = read_face(bad)
    leg("unparsable bytes read as UNKNOWN, not as empty-and-fine", s == "unreadable", s)

    passed = sum(1 for _, c, _ in ok if c)
    for name, c, detail in ok:
        print("[%s] %s%s" % ("PASS" if c else "FAIL", name, ("  " + detail) if detail else ""))
    print("selftest: %d/%d PASS" % (passed, len(ok)))
    return 0 if passed == len(ok) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["check", "write", "selftest"])
    ap.add_argument("--machine", default=None)
    ap.add_argument("--path", default=FACE)
    a = ap.parse_args(argv)

    if a.cmd == "selftest":
        return _selftest()
    if a.cmd == "check":
        return check(a.path)
    machine = a.machine
    if machine is None:
        try:
            with open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8") as fh:
                machine = json.load(fh)["machine_id"]
        except Exception:
            print("machine-health: cannot resolve machine_id -- refusing to write a guess")
            return 2
    machines, was = write_face(machine, a.path)
    print("machine-health: rebuilt from live readings (was=%s) machines=%s"
          % (was, ",".join(sorted(machines))))
    return 0


if __name__ == "__main__":
    sys.exit(main())