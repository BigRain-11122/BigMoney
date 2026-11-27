# -*- coding: utf-8 -*-
"""lane_lag_attribution.py -- why a lane is late, not just that it is late.

WHY (r2169)
-----------
`results/data_lane_freshness.json` says *how late* each lane is and *who owns*
it.  It cannot say **who was supposed to move it**.  So a row can sit at
`stalled / tail 2026-11-20 / owner bm-c` for a week and every reader assumes
some other round is on it -- exactly the r1322 shape ("we have a leg" != "the
leg ran") one step earlier: **no leg at all never runs**.

This face reads the freshness face and answers one question per late lane:

    is there a driver, and if not, who has to create one?

Drivers are counted from three sources, all cheap and local:

  * ``chain``    -- the writer's script path appears in Tools/s6_chain_bmc.py
                    LEGS (the round-driven chain).
  * ``task``     -- a scheduled task name mentions the writer (schtasks query,
                    no window; evidence only, task names lie -- lane_hosts.json
                    exists because "SatEngine-bm-b registered on bm-a" proved
                    a name is not an owner).
  * ``register`` -- a Tools/register_*.ps1 mentions the writer script.

A lane with none of the three is `no_driver`: nobody will ever refresh it, and
that is a different defect from "the source is broken".

Read-only.  Writes only results/lane_lag_attribution.json.
"""
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FRESH = os.path.join(ROOT, "results", "data_lane_freshness.json")
CHAIN = os.path.join(ROOT, "Tools", "s6_chain_bmc.py")
OUT = os.path.join(ROOT, "results", "lane_lag_attribution.json")
TOOLS = os.path.join(ROOT, "Tools")

# lane -> state face its own gate writes (evidence for "blocked", not a driver)
GATE_FACES = {
    "ah_panel": os.path.join(ROOT, "results", "ah_panel_status.json"),
}

LATE = ("stalled", "behind_1d", "absent", "unreadable")


def chain_scripts(path=CHAIN):
    """Script paths named inside the chain's LEGS block, as basenames."""
    try:
        src = io.open(path, encoding="utf-8").read()
    except OSError:
        return set()
    m = re.search(r"^LEGS\s*=\s*\[", src, re.M)
    if not m:
        return set()
    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth:
        if src[i] == "[":
            depth += 1
        elif src[i] == "]":
            depth -= 1
        i += 1
    block = src[start:i]
    return {os.path.basename(p) for p in re.findall(r'"(?:scripts|Tools)/([\w\-]+\.py)"', block)}


def task_names():
    """Scheduled task names, or [] when schtasks is unavailable."""
    try:
        cp = subprocess.run(["schtasks", "/query", "/fo", "csv", "/nh"],
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            creationflags=0x08000000)  # CREATE_NO_WINDOW
        txt = cp.stdout.decode("utf-8", "replace")
    except OSError:
        return []
    names = []
    for line in txt.splitlines():
        line = line.strip()
        if not line.startswith('"'):
            continue
        names.append(line.split('","')[0].strip('"'))
    return names


def register_scripts(folder=TOOLS):
    """{basename of writer .py -> [register script basenames]} from Tools/register_*.ps1."""
    hits = {}
    try:
        files = [f for f in os.listdir(folder) if f.startswith("register_") and f.endswith(".ps1")]
    except OSError:
        return hits
    for f in files:
        try:
            src = io.open(os.path.join(folder, f), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for base in re.findall(r"([\w\-]+\.py)", src):
            hits.setdefault(base, []).append(f)
    return hits


def declared_hosts(path=None):
    """{writer: machine} from config/lane_hosts.json -- an assignment, not a driver."""
    path = path or os.path.join(ROOT, "config", "lane_hosts.json")
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(d.get("lane_hosts") or {})


def gate_state(lane):
    path = GATE_FACES.get(lane)
    if not path or not os.path.exists(path):
        return None
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return {"readable": False}
    return {"readable": True,
            "complete": d.get("complete"),
            "cutoff": d.get("cutoff"),
            "last_error": d.get("last_error") or d.get("error")}


def classify(row, chain, tasks, regs, hosts=None):
    """Return (cause, detail, can_fix_here).  Pure function -- selftestable."""
    hosts = hosts or {}
    lane = row["lane"]
    verdict = row.get("verdict")
    if verdict == "retired":
        return "retired_by_design", "lane retired; tail is historical", False
    if verdict == "in_sync":
        return "in_sync", "", False

    writer = (row.get("writer") or "").strip()
    declared = hosts.get(writer)
    script = (writer + ".py") if writer else ""
    in_chain = bool(script) and script in chain
    task_hits = [t for t in tasks if writer and writer.lower().replace("update_", "") in t.lower()]
    reg_hits = regs.get(script, []) if script else []
    drivers = {"chain": in_chain, "task": task_hits, "register": reg_hits}
    detail = "drivers: chain=%s task=%d register=%d declared_host=%s" % (
        in_chain, len(task_hits), len(reg_hits), declared)

    if not (in_chain or task_hits or reg_hits):
        if declared:
            return ("declared_host_without_driver",
                    detail + "; %s was assigned this lane but nothing runs it" % declared,
                    declared == "bm-c")
        return "no_driver", detail + "; nothing refreshes this lane and no machine claims it", True

    gate = gate_state(lane)
    if verdict == "absent":
        if gate and gate.get("readable") and not gate.get("complete"):
            return ("gate_blocked",
                    detail + "; gate face complete=%s cutoff=%s err=%s"
                    % (gate.get("complete"), gate.get("cutoff"), gate.get("last_error")),
                    True)
        return "absent_no_artifact", detail + "; no artifact and no gate explanation", True

    if row.get("host_alive") is False:
        if row.get("takeover_capable"):
            return ("host_dead_takeover_available",
                    detail + "; owner %s silent %.1fh, takeover allowed"
                    % (row.get("lane_host"), row.get("host_age_h") or 0.0), True)
        return ("host_dead_cannot_take_over",
                detail + "; owner %s silent %.1fh, takeover NOT allowed"
                % (row.get("lane_host"), row.get("host_age_h") or 0.0), False)

    if in_chain or task_hits:
        return "driven_but_late", detail + "; a driver exists but the tail did not move", True
    return "declared_only", detail + "; only a register script mentions it", True


def build(fresh_path=FRESH):
    fresh = json.load(io.open(fresh_path, encoding="utf-8"))
    chain = chain_scripts()
    tasks = task_names()
    regs = register_scripts()
    hosts = declared_hosts()
    rows, counts = [], {}
    for row in fresh.get("lanes", []):
        cause, detail, fixable = classify(row, chain, tasks, regs, hosts)
        counts[cause] = counts.get(cause, 0) + 1
        if cause == "in_sync":
            continue
        rows.append({
            "lane": row.get("lane"),
            "verdict": row.get("verdict"),
            "tail": row.get("tail"),
            "expected": row.get("expected"),
            "n_missing": row.get("n_missing"),
            "writer": row.get("writer"),
            "declared_host": hosts.get((row.get("writer") or "").strip()),
            "owner": row.get("owner"),
            "lane_host": row.get("lane_host"),
            "host_alive": row.get("host_alive"),
            "cause": cause,
            "detail": detail,
            "fix_owner": "bm-c" if fixable else "needs-human-or-owner",
            "can_fix_here": fixable,
        })
    rows.sort(key=lambda r: (not r["can_fix_here"], r["lane"]))
    return {
        "schema": "lane-lag-attribution/v1",
        "source": {"face": "results/data_lane_freshness.json",
                   "as_of": fresh.get("as_of"),
                   "expected_last_official_day": fresh.get("expected_last_official_day"),
                   "verdict": fresh.get("verdict")},
        "drivers": {"chain_scripts": len(chain), "tasks": len(tasks),
                    "register_scripts": len(regs)},
        "counts": counts,
        "n_rows": len(rows),
        "rows": rows,
    }


# ---------------------------------------------------------------- selftest
def selftest():
    ok = 0
    chain = {"update_heat.py"}
    regs = {"update_repo.py": ["register_repo.ps1"]}

    base = {"lane": "x", "verdict": "stalled", "tail": "2026-11-20",
            "expected": "2026-11-26", "n_missing": 4, "writer": "update_orphan",
            "owner": "bm-c", "lane_host": "bm-c", "host_alive": True,
            "takeover_capable": False, "host_age_h": 0.0}
    c, _, fix = classify(dict(base), chain, [], regs)
    assert (c, fix) == ("no_driver", True), (c, fix)
    print("[PASS] L1 a writer with no chain/task/register is no_driver")
    ok += 1

    c, _, _ = classify(dict(base, writer="update_heat", verdict="in_sync"), chain, [], regs)
    assert c == "in_sync", c
    print("[PASS] L2 in_sync rows are not attributed at all")
    ok += 1

    c, _, fix = classify(dict(base, writer="update_repo"), chain, [], regs,
                         {"update_repo": "bm-a"})
    assert c == "declared_only" and fix, (c, fix)
    print("[PASS] L3 a register script is a declaration, not a driver")
    ok += 1

    c, _, fix = classify(dict(base, writer="update_repo"), chain, ["Bigmoney-UpdateRepo"], regs)
    assert c == "driven_but_late" and fix, (c, fix)
    print("[PASS] L3b a live task name turns the same row into driven_but_late")
    ok += 1

    c, _, fix = classify(dict(base, writer="update_heat", host_alive=False,
                              takeover_capable=False), chain, [], regs)
    assert (c, fix) == ("host_dead_cannot_take_over", False), (c, fix)
    print("[PASS] L4 dead host without takeover is not ours to fix")
    ok += 1

    c, _, fix = classify(dict(base, writer="update_heat", host_alive=False,
                              takeover_capable=True), chain, [], regs)
    assert (c, fix) == ("host_dead_takeover_available", True), (c, fix)
    print("[PASS] L5 dead host with takeover is ours to fix")
    ok += 1

    c, _, _ = classify(dict(base, verdict="retired"), chain, [], regs, {})
    assert c == "retired_by_design", c
    print("[PASS] L6 retired lanes are not labelled late")
    ok += 1

    c, _, fix = classify(dict(base), chain, [], regs, {})
    assert c == "no_driver" and fix, (c, fix)
    c, _, fix = classify(dict(base), chain, [], regs, {"update_orphan": "bm-c"})
    assert (c, fix) == ("declared_host_without_driver", True), (c, fix)
    c, _, fix = classify(dict(base), chain, [], regs, {"update_orphan": "bm-b"})
    assert (c, fix) == ("declared_host_without_driver", False), (c, fix)
    print("[PASS] L6b an assignment without a driver is named as one (ours to fix only on bm-c)")
    ok += 1

    hits = chain_scripts()
    assert "update_heat.py" in hits, "chain parser lost update_heat"
    assert "s6_chain_bmc.py" not in hits
    print("[PASS] L7 chain parser reads LEGS only (%d scripts)" % len(hits))
    ok += 1
    print("selftest %d/%d ok" % (ok, ok))


def main(argv):
    if "--selftest" in argv:
        selftest()
        return 0
    rep = build()
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("LANE-LAG-ATTRIBUTION as_of=%s src=%s" % (
        rep["source"]["as_of"], rep["source"]["face"]))
    print("counts:", json.dumps(rep["counts"], ensure_ascii=False))
    for r in rep["rows"]:
        print("  %-14s %-11s tail=%-10s miss=%-2s %-28s %s" % (
            r["lane"], r["verdict"], r["tail"], r["n_missing"], r["cause"],
            "FIXABLE" if r["can_fix_here"] else r["fix_owner"]))
    print("-> results/lane_lag_attribution.json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
