#!/usr/bin/env python
# mem_pressure_report.py -- O-20261026-0735-bm-c sec.4.3 (RAM 空路) probe.
#
# Why this exists: every round has been reporting "RAM 97.8% / free 0.5GB" from
# Win32_OperatingSystem.FreePhysicalMemory, which counts ONLY the truly-free
# page list and therefore always reads ~0 on a warm Windows box (standby cache
# is excluded). The number that actually predicts allocation failure is the
# COMMIT charge vs the commit limit, and the number that says "a new batch can
# start" is Available MBytes. This tool reports all three and names the top
# commit-charge holders, so "release RAM" decisions are made on the right
# quantity instead of on a metric that is always ~0.
#
# Read-only. Never kills anything -- naming the holder is the report; the
# release decision belongs to whoever owns the session that started it.
#
# Usage:
#   python Tools/mem_pressure_report.py run        # measure + write json
#   python Tools/mem_pressure_report.py selftest   # offline classification legs
#
# Exit: 0 ok / 2 mechanism fault (probe unreadable) / 3 pressure CRITICAL
#       (verdict is a reported fact, not a blocker -- see law note below)

import json
import os
import subprocess
import sys
import time
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "results", "mem_pressure.bm-c.json")

# Thresholds are deliberately about COMMIT, not about free-page-list:
#   - commit headroom < 4 GB  -> a GPU/torch batch of normal size can fail to
#     allocate mid-run (torch reserves multi-GB at once)
#   - available < 1 GB        -> new OS allocations start paging hard
COMMIT_HEADROOM_CRIT_GB = 4.0
AVAIL_CRIT_MB = 1024.0


def classify(commit_headroom_gb, avail_mb):
    """Pure: pressure verdict from the two quantities that matter."""
    if commit_headroom_gb < COMMIT_HEADROOM_CRIT_GB:
        return "CRITICAL", "commit headroom %.2fGB < %.1fGB" % (
            commit_headroom_gb, COMMIT_HEADROOM_CRIT_GB)
    if avail_mb < AVAIL_CRIT_MB:
        return "TIGHT", "available %.0fMB < %.0fMB" % (avail_mb, AVAIL_CRIT_MB)
    return "OK", "commit headroom %.2fGB, available %.0fMB" % (
        commit_headroom_gb, avail_mb)


def _ps(script):
    p = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, timeout=120,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if p.returncode != 0:
        raise RuntimeError("powershell rc=%s: %s" % (p.returncode, p.stderr[:400]))
    return p.stdout


def measure():
    os_sql = (
        "Get-CimInstance Win32_OperatingSystem | ForEach-Object {"
        "'{0}|{1}|{2}' -f $_.FreePhysicalMemory,$_.TotalVisibleMemorySize,"
        "$_.TotalVirtualMemorySize};"
        "Get-CimInstance Win32_Process | Where-Object { $_.Name -match "
        "'python|node|ComfyUI|codely' } | ForEach-Object {"
        "'PROC|{0}|{1}|{2}' -f $_.ProcessId,$_.Name,$_.WorkingSetSize}"
    )
    out = _ps(os_sql)
    free_kb = total_kb = commit_limit_kb = None
    procs = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("PROC|"):
            _, pid, name, ws = line.split("|", 3)
            procs.append({"pid": int(pid), "name": name,
                          "ws_mb": round(int(ws) / 1048576.0)})
        else:
            a = line.split("|")
            if len(a) == 3:
                free_kb, total_kb, commit_limit_kb = (int(a[0]), int(a[1]), int(a[2]))

    perf = _ps(
        "$c = Get-Counter '\\Memory\\Available MBytes','\\Memory\\Committed Bytes'"
        " -ErrorAction Stop; $c.CounterSamples | ForEach-Object {"
        "'{0}|{1}' -f $_.Path,$_.CookedValue}"
    )
    avail_mb = committed = None
    for line in perf.splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        path, val = line.rsplit("|", 1)
        low = path.lower()
        if "available mbytes" in low:
            avail_mb = float(val)
        elif "committed bytes" in low:
            committed = float(val)

    if avail_mb is None or committed is None or commit_limit_kb is None:
        raise RuntimeError("probe incomplete: avail=%r committed=%r limit=%r"
                           % (avail_mb, committed, commit_limit_kb))

    commit_limit = commit_limit_kb * 1024.0
    return {
        "free_physical_mb": round(free_kb / 1024.0),
        "available_mb": round(avail_mb),
        "total_physical_gb": round(total_kb / 1048576.0, 2),
        "committed_gb": round(committed / 1073741824.0, 2),
        "commit_limit_gb": round(commit_limit / 1073741824.0, 2),
        "commit_headroom_gb": round((commit_limit - committed) / 1073741824.0, 2),
        "procs_top": sorted(procs, key=lambda p: -p["ws_mb"])[:8],
    }


def run():
    now = datetime.now().astimezone()
    try:
        m = measure()
    except Exception as exc:  # noqa: BLE001 -- reported, never masked
        print("MECHANISM-FAULT %s" % exc)
        return 2
    verdict, why = classify(m["commit_headroom_gb"], m["available_mb"])
    rec = {
        "tool": "mem_pressure_report",
        "machine_id": "bm-c",
        "generated": now.isoformat(timespec="seconds"),
        "generated_epoch": int(time.time()),
        "metric_note": ("free_physical_mb is the Win32 FreePhysicalMemory face "
                        "(excludes standby) and is ~0 on any warm box; judge "
                        "pressure by commit_headroom_gb + available_mb"),
        "verdict": verdict,
        "verdict_reason": why,
        "thresholds": {"commit_headroom_crit_gb": COMMIT_HEADROOM_CRIT_GB,
                       "available_crit_mb": AVAIL_CRIT_MB},
    }
    rec.update(m)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    os.replace(tmp, OUT)

    with open(OUT, "r", encoding="utf-8") as fh:
        back = json.load(fh)
    assert back["verdict"] == verdict and back["committed_gb"] == rec["committed_gb"]

    print("commit %.2f/%.2fGB (headroom %.2fGB) available %.0fMB free_phys %.0fMB"
          % (rec["committed_gb"], rec["commit_limit_gb"],
             rec["commit_headroom_gb"], rec["available_mb"],
             rec["free_physical_mb"]))
    print("VERDICT %s -- %s" % (verdict, why))
    for p in rec["procs_top"][:5]:
        print("  holder pid=%s %-10s ws=%sMB" % (p["pid"], p["name"], p["ws_mb"]))
    print("out %s" % OUT)
    return 0 if verdict != "CRITICAL" else 3


def selftest():
    legs = []
    # leg 1: commit starvation dominates even when available looks healthy --
    # this is the whole point of the tool (the old metric would say OK).
    legs.append(("commit-first", classify(1.9, 8000.0)[0] == "CRITICAL"))
    # leg 2: healthy commit but starved available -> TIGHT not CRITICAL
    legs.append(("avail-second", classify(20.0, 400.0)[0] == "TIGHT"))
    # leg 3: both healthy -> OK
    legs.append(("both-ok", classify(20.0, 8000.0)[0] == "OK"))
    # leg 4: boundary is strict (< threshold), not <=, so a value exactly at
    # the line must NOT be flagged -- catches an off-by-one that would make
    # every healthy box look critical.
    legs.append(("boundary-strict", classify(4.0, 1024.0)[0] == "OK"))
    # leg 5: reason string must carry the deciding quantity (a verdict with no
    # number is not auditable).
    legs.append(("reason-carries-number", "GB" in classify(1.0, 500.0)[1]))
    ok = 0
    for name, passed in legs:
        print(("PASS " if passed else "FAIL ") + name)
        ok += 1 if passed else 0
    print("selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(selftest())
    sys.exit(run())