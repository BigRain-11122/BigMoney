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
GPU_FIELDS = ("util", "free_gb")

# D-20261028-02 item 1 pins the six fields above; item 3 says a consumer must not
# read a face it cannot fully parse as healthy. Those two only bite together if
# the gate is field-level: on 2026-10-28 the face was a machine-keyed map and the
# gate said OK while two of the three entries carried no `cpu` at all and every
# entry carried a flat `gpu_free_gb` instead of the pinned `gpu` object. Shape-ok
# was being read as contract-ok, so the missing readings stayed invisible.
REQUIRED_PATHS = ("ts", "cpu", "ram_free_gb", "gpu", "gpu.util", "gpu.free_gb",
                  "util", "work")


def _looks_like_entry(v):
    """An entry is a mapping that carries a timestamp. Anything else -- including
    the {"value": ...} shells -- is not a row and must not be adopted."""
    return isinstance(v, dict) and isinstance(v.get("ts"), str) and bool(v.get("ts"))


def entry_gaps(entry):
    """-> list of canonical paths this entry does not actually carry.

    A field that is present but null is NOT a reading: the face says UNKNOWN by
    omission, and this list is how a reader learns which reading is the missing
    one instead of seeing a plausible-looking panel.
    """
    gaps = []
    if not isinstance(entry, dict):
        return list(REQUIRED_PATHS)
    for path in REQUIRED_PATHS:
        if "." in path:
            head, tail = path.split(".", 1)
            node = entry.get(head)
            if not isinstance(node, dict) or node.get(tail) is None:
                gaps.append(path)
        elif entry.get(path) is None:
            gaps.append(path)
    return gaps


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


def _heartbeat(machine, hb_dir=None):
    p = os.path.join(hb_dir or HEARTBEAT_DIR, machine + ".json")
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


def _first(hb, keys):
    """First non-None reading among spellings. `or` would be wrong here: a true
    reading of 0.0 (idle GPU, idle CPU) is falsy and would fall through to the
    next spelling and then to None, i.e. a busy-looking UNKNOWN."""
    for k in keys:
        v = hb.get(k)
        if v is not None:
            return v
    return None


def build_entry(machine, hb=None, now=None, hb_dir=None):
    """One canonical entry. Missing readings stay None -- the face says UNKNOWN
    by omission instead of inventing a plausible number."""
    hb = _heartbeat(machine, hb_dir) if hb is None else hb
    now = now or time.strftime("%Y-%m-%d %H:%M")
    gpu = {
        "util": _num(_first(hb, ("gpu_util_pct", "gpu_util"))),
        "free_gb": _num(_first(hb, ("free_vram_gb", "gpu_free_gb", "gpu_vram_free_gb"))),
    }
    return {
        "ts": str(hb.get("ts") or now)[:16],
        "cpu": _num(_first(hb, ("cpu_pct", "cpu_util_pct", "cpu_total_pct"))),
        "ram_free_gb": _num(_first(hb, ("free_ram_gb", "ram_free_gb"))),
        "gpu": gpu,
        "util": str(hb.get("status") or hb.get("verdict") or "")[:40] or None,
        "work": str(hb.get("current_task") or hb.get("task") or "")[:200] or None,
    }


def write_face(machine, path=FACE, hb_dir=None, heal=True):
    """Derive the local entry, then heal thin FOREIGN entries from their own
    heartbeats.

    `heal` exists because the hourly oversight writer is a second code face that
    emits a partial row (no `cpu`, no `gpu.util`), so a face that is complete now
    goes thin again one hour later. Healing keeps the view whole from the source
    of truth per machine instead of either relaxing the gate or letting a thin
    row sit there until someone reads it.
    """
    machines, status, _dropped = read_face(path)
    machines[machine] = build_entry(machine, hb_dir=hb_dir)
    healed = []
    if heal:
        for mid in list(machines):
            if mid == machine or not entry_gaps(machines[mid]):
                continue
            hb = _heartbeat(mid, hb_dir)
            if not hb:
                continue
            machines[mid] = build_entry(mid, hb=hb)
            healed.append(mid)
    _save(machines, path)
    return machines, {"was": status, "healed": healed}


def rebuild_face(path=FACE, hb_dir=None):
    """Re-derive EVERY machine entry from that machine's own heartbeat.

    `write` only refreshes the local machine, so a face rebuilt by it keeps
    whatever shape the last foreign writer emitted (that is exactly how bm-a and
    bm-b kept a flat `gpu_free_gb` while the pinned shape is a `gpu` object).
    Rebuild is the once-per-decision repair: every entry is derived, no entry is
    carried forward. A machine with no heartbeat keeps its row and reports gaps.
    """
    machines, status, _dropped = read_face(path)
    hb_dir = hb_dir or HEARTBEAT_DIR
    ids = set(machines)
    try:
        ids |= {f[:-5] for f in os.listdir(hb_dir) if f.endswith(".json")}
    except Exception:
        pass
    rebuilt, kept, gap_report = [], [], {}
    for mid in sorted(ids):
        hb = _heartbeat(mid, hb_dir)
        if hb:
            machines[mid] = build_entry(mid, hb=hb)
            rebuilt.append(mid)
        else:
            kept.append(mid)
        gaps = entry_gaps(machines[mid])
        if gaps:
            gap_report[mid] = gaps
    _save(machines, path)
    return machines, {"rebuilt": rebuilt, "kept": kept, "gaps": gap_report,
                      "was": status}


def _save(machines, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(machines, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def check(path=FACE):
    machines, status, dropped = read_face(path)
    if status != "ok":
        print("machine-health: UNKNOWN (%s) -- a reader must not treat this as healthy" % status)
        return 2
    gaps = {m: entry_gaps(e) for m, e in machines.items()}
    gaps = {m: g for m, g in gaps.items() if g}
    if gaps:
        detail = ";".join("%s:%s" % (m, ",".join(g)) for m, g in sorted(gaps.items()))
        print("machine-health: INCOMPLETE machines=%d dropped_junk=%d missing[%s] "
              "-- shape is readable but the pinned fields are not all there"
              % (len(machines), dropped, detail))
        return 2
    print("machine-health: OK machines=%d dropped_junk=%d fields=8/8 %s"
          % (len(machines), dropped, ",".join(sorted(machines))))
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

    machines, _wmeta = write_face("bm-b", merged)
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

    # The gate must be field-level, not shape-level (the 2026-10-28 miss: a clean
    # machine-keyed map whose entries had no `cpu` was reported OK).
    thin = {"ts": "2026-10-28 02:00", "util": "red", "work": "x",
            "ram_free_gb": 0.7, "gpu": {"free_gb": 14.6}}
    leg("a thin entry is reported field-by-field, not as OK",
        entry_gaps(thin) == ["cpu", "gpu.util"], str(entry_gaps(thin)))
    thin_path = os.path.join(d, "thin.json")
    with open(thin_path, "w", encoding="utf-8") as fh:
        json.dump({"bm-c": thin}, fh)
    leg("check refuses to call a thin face healthy", check(thin_path) == 2, "")

    # 0.0 is a reading (idle GPU / idle CPU), not a missing value.
    leg("a zero reading survives instead of falling through to UNKNOWN",
        build_entry("bm-z", hb={"ts": "2026-10-28 02:00", "cpu_pct": 0,
                                "free_ram_gb": 0, "free_vram_gb": 0,
                                "gpu_util_pct": 0, "status": "green",
                                "current_task": "idle"})["gpu"]["util"] == 0.0, "")

    hbdir = os.path.join(d, "hb")
    os.makedirs(hbdir)
    for mid in ("bm-a", "bm-b"):
        with open(os.path.join(hbdir, mid + ".json"), "w", encoding="utf-8") as fh:
            json.dump({"ts": "2026-10-28 02:0" + ("1" if mid == "bm-a" else "2"),
                       "cpu_pct": 11, "free_ram_gb": 9, "free_vram_gb": 4,
                       "gpu_util_pct": 0, "status": "green",
                       "current_task": "r1 " + mid}, fh)
    reb = os.path.join(d, "rebuild.json")
    with open(reb, "w", encoding="utf-8") as fh:
        json.dump({"bm-a": thin, "bm-b": thin, "bm-c": {"ts": "2026-10-28 02:00"}}, fh)
    machines, rep = rebuild_face(reb, hb_dir=hbdir)
    leg("rebuild re-derives every entry that has a heartbeat",
        rep["rebuilt"] == ["bm-a", "bm-b"] and set(rep["gaps"]) <= {"bm-c"}, str(rep))
    leg("rebuild keeps a heartbeat-less entry and reports its gaps",
        rep["kept"] == ["bm-c"] and "bm-c" in rep["gaps"], str(rep["gaps"]))
    leg("rebuild makes the previously thin entries complete",
        all(entry_gaps(machines[m]) == [] for m in ("bm-a", "bm-b")),
        str({m: entry_gaps(machines[m]) for m in machines}))

    # A thin FOREIGN row is healed from that machine's own heartbeat, so the hourly
    # oversight writer (a second code face that emits a partial row) cannot leave the
    # panel thin for a whole period between rounds.
    healp = os.path.join(d, "heal.json")
    with open(healp, "w", encoding="utf-8") as fh:
        json.dump({"bm-a": thin, "bm-c": thin}, fh)
    machines, meta = write_face("bm-b", healp, hb_dir=hbdir)
    leg("write heals a thin foreign entry from that machine's heartbeat",
        meta["healed"] == ["bm-a"] and entry_gaps(machines["bm-a"]) == [], str(meta))
    leg("write does not invent fields for a machine with no heartbeat",
        "bm-c" in {m for m, e in machines.items() if entry_gaps(e)}, str(rep))

    passed = sum(1 for _, c, _ in ok if c)
    for name, c, detail in ok:
        print("[%s] %s%s" % ("PASS" if c else "FAIL", name, ("  " + detail) if detail else ""))
    print("selftest: %d/%d PASS" % (passed, len(ok)))
    return 0 if passed == len(ok) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["check", "write", "rebuild", "selftest"])
    ap.add_argument("--machine", default=None)
    ap.add_argument("--path", default=FACE)
    a = ap.parse_args(argv)

    if a.cmd == "selftest":
        return _selftest()
    if a.cmd == "check":
        return check(a.path)
    if a.cmd == "rebuild":
        machines, rep = rebuild_face(a.path)
        print("machine-health: rebuilt %d entries (was=%s) kept=%s gaps=%s"
              % (len(rep["rebuilt"]), rep["was"], ",".join(rep["kept"]) or "-",
                 rep["gaps"] or "-"))
        return 0 if not rep["gaps"] else 1
    machine = a.machine
    if machine is None:
        try:
            with open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8") as fh:
                machine = json.load(fh)["machine_id"]
        except Exception:
            print("machine-health: cannot resolve machine_id -- refusing to write a guess")
            return 2
    machines, meta = write_face(machine, a.path)
    print("machine-health: rebuilt from live readings (was=%s) machines=%s healed=%s gaps=%s"
          % (meta["was"], ",".join(sorted(machines)), ",".join(meta["healed"]) or "-",
             entry_gaps(machines[machine]) or "-"))
    return 0


if __name__ == "__main__":
    sys.exit(main())