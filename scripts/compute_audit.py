"""Compute auditor (CEO order O-20260923-1810, charter research/COMPUTE_AUDIT.md).

Samples CPU / python-process load / GPU / batch-output freshness / fleet open
tasks / runnable-pool ready count each loop round (S6 tail). Flags:
blind_burn, idle_with_work, cap_violation, gpu_unauthorized, zombie_process,
single_core_hog, pool_starvation (seventh flag, COMPUTE_AUDIT v2.2 /
O-20260925-1137: ready-batches==0 AND py<70% sustained ~30min -- closes the
"empty pool = structurally green while CPUs idle" loophole). Quiet exit 0
unless flags fire; history appended to results/compute_audit.json for
two-source (sample+history) judgment.

Subcommands:
    (no args)  live sample
    selftest   hermetic offline scenarios for the starvation flag (exit 0/1)
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
STARVATION_PY_CPU = 70.0     # O-20260925-1137 py line
STARVATION_SUSTAIN_MIN = 25.0   # 30min intent; ~10min sample cadence tolerance
STARVATION_MIN_SAMPLES = 3


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


def pool_ready_count():
    """ready entries in results/runnable_pool.json; None = unreadable/missing.

    None (unknown) is deliberately distinct from 0 (known-empty): the
    starvation flag must not fire on a pool file we could not read.
    """
    try:
        with open(os.path.join(ROOT, "results", "runnable_pool.json"),
                  encoding="utf-8-sig") as f:
            entries = (json.load(f) or {}).get("entries") or []
        return sum(1 for e in entries if e.get("status") == "ready")
    except Exception:
        return None


def load_state(py_cpu_pct, ready):
    """Per-sample load taxonomy (COMPUTE_AUDIT v2.2, T-55): burning-healthy /
    idle-starvation / pool-supply-gap / unknown."""
    if ready is None or py_cpu_pct is None:
        return "unknown"
    if py_cpu_pct >= STARVATION_PY_CPU:
        return "burning-healthy"
    return "idle-starvation" if ready == 0 else "pool-supply-gap"


def starvation_decision(hist, now_epoch, cur_py, cur_ready, cur_ts):
    """Seventh-flag sustained-window decision (pure function, T-55).

    Candidate = current sample in idle-starvation state. Full flag requires
    the trailing run of qualifying samples (py<70 AND ready==0) to span
    >= STARVATION_SUSTAIN_MIN with >= STARVATION_MIN_SAMPLES samples.
    History samples missing pool_ready_count (pre-v2.2 legacy) cannot
    credit the window -- the run stops there (honest insufficient history).
    Returns (candidate, flag_fired, detail).
    """
    if cur_ready is None or cur_py is None:
        return False, False, {"reason": "unknown_pool_or_py"}
    candidate = cur_py < STARVATION_PY_CPU and cur_ready == 0
    if not candidate:
        return False, False, {"reason": load_state(cur_py, cur_ready)}
    run = [cur_ts]
    for s in reversed(hist):
        py, rd = s.get("py_cpu_pct"), s.get("pool_ready_count")
        if py is None or rd is None:
            break
        if py < STARVATION_PY_CPU and rd == 0:
            run.append(s.get("ts"))
        else:
            break
    span_min = None
    if len(run) >= STARVATION_MIN_SAMPLES:
        try:
            oldest = time.mktime(time.strptime(run[-1], "%Y-%m-%d %H:%M:%S"))
            span_min = (now_epoch - oldest) / 60.0
        except Exception:
            span_min = None
        if span_min is not None and span_min >= STARVATION_SUSTAIN_MIN:
            return True, True, {"run_samples": len(run),
                                "span_min": round(span_min, 1)}
    return True, False, {"run_samples": len(run), "span_min": span_min}


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
    ready = pool_ready_count()
    gpu = gpu_sample()

    # sixth flag candidate (O-20260924-2130 s1.3): single-core hog on a
    # multi-core machine -- ONE python process burning ~1 core while the
    # rest of the py load is idle. Shape candidate now; the FLAG requires
    # the previous audit sample (>=10min old) to carry the same candidate
    # (sustained window; class verification/disposal = watchdog C7 lanes).
    hog = None
    if cores >= 8:
        dom_pid, dom_d = None, 0.0
        for pid, (name, cpu2, age) in p2.items():
            cpu1 = p1.get(pid, (name, 0.0, age))[1]
            d = max(0.0, cpu2 - cpu1)
            if d > dom_d:
                dom_pid, dom_d = pid, d
        if (dom_d >= 0.8 and dom_d <= 1.5
                and delta_total <= dom_d * 1.7 and dom_pid is not None):
            hog = {"pid": dom_pid, "cores_used": round(dom_d, 2)}
    hog_candidate = hog is not None

    # history is read BEFORE flagging (sustained-window check needs it)
    hist = []
    if os.path.exists(OUT):
        try:
            with open(OUT, encoding="utf-8") as f:
                hist = json.load(f).get("history", [])[-200:]
        except Exception:
            hist = []

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
    if hog_candidate:
        prev = hist[-1] if hist else None
        prev_cand = bool(prev and prev.get("single_core_hog_candidate"))
        prev_age_min = None
        if prev:
            try:
                prev_age_min = (time.time() - time.mktime(time.strptime(
                    prev["ts"], "%Y-%m-%d %H:%M:%S"))) / 60.0
            except Exception:
                prev_age_min = None
        if prev_cand and prev_age_min is not None and prev_age_min >= 10:
            flags.append("single_core_hog")

    # seventh flag (O-20260925-1137 / COMPUTE_AUDIT v2.2): pool starvation.
    # Fires when ready==0 AND py<70% sustained ~30min -- the empty-pool
    # loophole in the red-card condition ("has runnable batch AND py<70%")
    # let idle CPUs audit green; this flag makes 池饿 a visible violation
    # state. Response is SUPPLY (real batches), never fabricated burn.
    starve_cand, starve_flag, starve_detail = starvation_decision(
        hist, time.time(), py_cpu_pct, ready,
        time.strftime("%Y-%m-%d %H:%M:%S"))
    if starve_flag:
        flags.append("pool_starvation")

    record = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_total_pct": cpu_now,
        "py_cpu_pct": py_cpu_pct,
        "cores": cores,
        "py_procs": len(p2),
        "result_stale_min": None if stale is None else round(stale, 1),
        "fleet_open_tasks": open_tasks,
        "pool_ready_count": ready,
        "load_state": load_state(py_cpu_pct, ready),
        "pool_starvation_candidate": starve_cand,
        "pool_starvation_detail": starve_detail,
        "gpu": gpu,
        "zombies": zombies,
        "single_core_hog_candidate": hog_candidate,
        "single_core_hog_detail": hog,
        "flags": flags,
        "verdict": "CLEAN" if not flags else "FLAG:" + ",".join(flags),
    }

    hist.append(record)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"latest": record, "history": hist}, f, indent=2,
                  ensure_ascii=False)

    print(json.dumps(record, ensure_ascii=False))
    # exit 0 always: audit is observational; loop reports flags only
    return 0


def _selftest():
    """Hermetic offline scenarios for the seventh flag (T-55 acceptance a/b).

    Pure-function level: the production decision path
    (starvation_decision/load_state) is exercised directly with synthetic
    samples; no PS sampling, no writes, no network.
    """
    now = time.time()

    def ts_ago(min_ago):
        return time.strftime("%Y-%m-%d %H:%M:%S",
                            time.localtime(now - min_ago * 60))

    def sample(min_ago, py, ready):
        return {"ts": ts_ago(min_ago), "py_cpu_pct": py,
                "pool_ready_count": ready}

    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    # (a) injected starvation: ready=0 + synthetic py<70% series over ~30min
    # -> candidate AND full flag fire
    hist = [sample(30, 1.9, 0), sample(20, 3.1, 0), sample(10, 2.4, 0)]
    cand, flag, det = starvation_decision(
        hist, now, 1.9, 0, ts_ago(0))
    check("starvation sustained -> flag", (cand, flag), (True, True))
    # (b) healthy burning at the 95%-core-hour state -> no flag, no candidate
    cand, flag, _ = starvation_decision(hist, now, 85.0, 0, ts_ago(0))
    check("burning-healthy no flag", (cand, flag), (False, False))
    # (b2) pool-fed idle: ready>0, py low -> supply-gap state, no starvation
    hist_fed = [sample(30, 2.0, 3), sample(20, 2.0, 2), sample(10, 2.0, 1)]
    cand, flag, _ = starvation_decision(hist_fed, now, 1.9, 2, ts_ago(0))
    check("pool-fed no starvation flag", (cand, flag), (False, False))
    check("pool-fed state", load_state(1.9, 2), "pool-supply-gap")
    # (c) legacy history (pre-v2.2 samples lack pool_ready_count) cannot
    # credit the window -> candidate only, honest no-flag
    hist_legacy = [
        {"ts": ts_ago(30), "py_cpu_pct": 2.0},
        {"ts": ts_ago(20), "py_cpu_pct": 2.0},
        {"ts": ts_ago(10), "py_cpu_pct": 2.0},
    ]
    cand, flag, _ = starvation_decision(hist_legacy, now, 1.9, 0, ts_ago(0))
    check("legacy history -> candidate only", (cand, flag), (True, False))
    # (d) insufficient span (2 samples, ~10min) -> candidate only
    hist_short = [sample(10, 1.9, 0)]
    cand, flag, _ = starvation_decision(hist_short, now, 1.9, 0, ts_ago(0))
    check("short span -> candidate only", (cand, flag), (True, False))
    # (e) pool unreadable -> unknown, never flags
    cand, flag, _ = starvation_decision(hist, now, 1.9, None, ts_ago(0))
    check("unreadable pool -> no candidate", (cand, flag), (False, False))
    check("unreadable pool state", load_state(1.9, None), "unknown")
    # (f) a fed sample inside the window breaks the trailing run -> no flag
    hist_break = [sample(30, 1.9, 0), sample(20, 2.0, 4), sample(10, 1.9, 0)]
    cand, flag, _ = starvation_decision(hist_break, now, 1.9, 0, ts_ago(0))
    check("fed sample breaks run", (cand, flag), (True, False))
    # taxonomy sanity
    check("burning state", load_state(85.0, 0), "burning-healthy")
    check("starvation state", load_state(1.9, 0), "idle-starvation")

    n_pass = sum(1 for _, ok, _, _ in cases if ok)
    print(f"compute_audit selftest: {n_pass}/{len(cases)} PASS")
    for name, ok, got, want in cases:
        if not ok:
            print(f"  FAIL {name}: got={got} want={want}")
    return 0 if n_pass == len(cases) else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(_selftest())
    sys.exit(main())
