"""Compute auditor (CEO order O-20260923-1810, charter research/COMPUTE_AUDIT.md).

Samples CPU / python-process load / GPU / batch-output freshness / fleet open
tasks each loop round (S6 tail). Flags: blind_burn, idle_with_work,
cap_violation, gpu_unauthorized, zombie_process. Quiet exit 0 unless flags fire;
history appended to results/compute_audit.json for two-source (sample+history)
judgment.
"""
import glob
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "compute_audit.json")
SAMPLE_WINDOW_S = 3
CAP_POLICY = 0.80            # O-20260923-1738
CAP_TOLERANCE = 1.06         # 85% trip line
BLIND_BURN_PY_CPU = 60.0     # % of machine capacity
BLIND_BURN_STALE_MIN = 15.0
IDLE_CPU = 20.0
GPU_UTIL_TRIP = 10.0
ZOMBIE_AGE_MIN = 45.0


def cpu_total():
    import csv as _csv
    import io
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-CimInstance Win32_Processor | Measure-Object "
         "-Property LoadPercentage -Average).Average"],
        capture_output=True, text=True, timeout=30)
    try:
        return float(out.stdout.strip())
    except Exception:
        return None


def core_count():
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-CimInstance Win32_Processor | Measure-Object "
         "-Property NumberOfLogicalProcessors -Sum).Sum"],
        capture_output=True, text=True, timeout=30)
    try:
        return int(out.stdout.strip())
    except Exception:
        return 8


def python_procs():
    """[(pid, name, cpu_seconds, age_min)] snapshot for python/pythonw/codely."""
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "Get-Process | Where-Object { $_.Name -match 'python|codely' } | "
         "Select-Object Id,Name,CPU,StartTime | "
         "ConvertTo-Json -Compress"],
        capture_output=True, text=True, timeout=30)
    try:
        rows = json.loads(out.stdout)
    except Exception:
        return []
    if isinstance(rows, dict):
        rows = [rows]
    procs = []
    now = time.time()
    for r in rows:
        try:
            cpu_s = float(r.get("CPU") or 0)
            st = r.get("StartTime")
            age = None
            if st:
                try:
                    st = st.replace("Z", "UTC") if isinstance(st, str) else st
                    age = (now - time.mktime(time.strptime(
                        str(st)[:19], "%Y-%m-%dT%H:%M:%S"))) / 60.0
                except Exception:
                    age = None
            procs.append((int(r["Id"]), str(r["Name"]), cpu_s, age))
        except Exception:
            continue
    return procs


def gpu_sample():
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=15)
        if out.returncode != 0 or not out.stdout.strip():
            return {"present": False}
        util, mem = [x.strip() for x in out.stdout.strip().split(",")[:2]]
        info = {"present": True, "util_pct": float(util),
                "mem_used_mb": float(mem)}
        # compute apps: whitelist ollama (authorized standing J13 service)
        apps = subprocess.run(
            ["nvidia-smi", "--query-compute-apps=pid,process_name",
             "--format=csv,noheader"],
            capture_output=True, text=True, timeout=15)
        names = []
        for line in apps.stdout.strip().splitlines():
            if "," in line:
                names.append(line.split(",", 1)[1].strip().lower())
        info["compute_apps_count"] = len(names)
        # rogue = OUR batch processes touching GPU (python*) — desktop apps
        # and whitelisted services (ollama) are other tenants, out of scope.
        # TENANT_PY_PATHS: other-tenant standing services that happen to be
        # python.exe -- the user's ComfyUI mini-game asset production line
        # (machine-level standing authorization, same class as the ollama
        # whitelist; inert on machines without it).
        tenant_py = ("comfyui", "python_embeded")
        info["rogue_apps"] = [n for n in names
                              if "python" in n
                              and not any(t in n for t in tenant_py)]
        return info
    except Exception:
        return {"present": False}


def newest_result_age_min():
    newest, now = 0.0, time.time()
    for p in glob.glob(os.path.join(ROOT, "results", "*.json")):
        m = os.path.getmtime(p)
        if m > newest:
            newest = m
    return (now - newest) / 60.0 if newest else None


def fleet_open_tasks():
    n = 0
    for p in glob.glob(os.path.join(ROOT, "fleet", "tasks", "*.json")):
        try:
            with open(p, encoding="utf-8") as f:
                if json.load(f).get("status") == "open":
                    n += 1
        except Exception:
            pass
    return n


def main():
    cores = core_count()
    p1 = {pid: (name, cpu_s, age) for pid, name, cpu_s, age in python_procs()}
    cpu_a = cpu_total()
    time.sleep(SAMPLE_WINDOW_S)
    p2 = {pid: (name, cpu_s, age) for pid, name, cpu_s, age in python_procs()}
    cpu_b = cpu_total()

    delta_total = 0.0
    zombies = []
    for pid, (name, cpu2, age) in p2.items():
        cpu1 = p1.get(pid, (name, 0.0, age))[1]
        d = max(0.0, cpu2 - cpu1)
        delta_total += d
        if name.startswith("python") and age is not None and age > ZOMBIE_AGE_MIN:
            zombies.append({"pid": pid, "age_min": round(age, 1)})
    py_cpu_pct = round(min(100.0, (delta_total / (SAMPLE_WINDOW_S * cores))
                           * 100), 1)
    cpu_now = cpu_b if cpu_b is not None else cpu_a
    stale = newest_result_age_min()
    open_tasks = fleet_open_tasks()
    gpu = gpu_sample()

    flags = []
    if py_cpu_pct > BLIND_BURN_PY_CPU and (stale is None or
                                           stale > BLIND_BURN_STALE_MIN):
        flags.append("blind_burn")
    if open_tasks > 0 and cpu_now is not None and cpu_now < IDLE_CPU:
        flags.append("idle_with_work")
    if cpu_now is not None and cpu_now > CAP_POLICY * 100 * CAP_TOLERANCE:
        flags.append("cap_violation")
    if gpu.get("present") and gpu.get("rogue_apps"):
        flags.append("gpu_unauthorized")
    if zombies:
        flags.append("zombie_process")

    record = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_total_pct": cpu_now,
        "py_cpu_pct": py_cpu_pct,
        "cores": cores,
        "py_procs": len(p2),
        "result_stale_min": None if stale is None else round(stale, 1),
        "fleet_open_tasks": open_tasks,
        "gpu": gpu,
        "zombies": zombies,
        "flags": flags,
        "verdict": "CLEAN" if not flags else "FLAG:" + ",".join(flags),
    }

    hist = []
    if os.path.exists(OUT):
        try:
            with open(OUT, encoding="utf-8") as f:
                hist = json.load(f).get("history", [])[-200:]
        except Exception:
            hist = []
    hist.append(record)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"latest": record, "history": hist}, f, indent=2,
                  ensure_ascii=False)

    print(json.dumps(record, ensure_ascii=False))
    # exit 0 always: audit is observational; loop reports flags only
    return 0


if __name__ == "__main__":
    sys.exit(main())
