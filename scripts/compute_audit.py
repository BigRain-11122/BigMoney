"""Compute auditor (CEO order O-20260923-1810, charter research/COMPUTE_AUDIT.md).

Samples CPU / python-process load / GPU / batch-output freshness / fleet open
tasks / runnable-pool ready count each loop round (S6 tail). Flags:
blind_burn, idle_with_work, cap_violation, gpu_unauthorized, zombie_process,
single_core_hog, pool_starvation (seventh flag, COMPUTE_AUDIT v2.2 /
O-20260925-1137: ready-batches==0 AND py<70% sustained ~30min -- closes the
"empty pool = structurally green while CPUs idle" loophole).
v2.3 (O-20260926-2320, CEO 24h-saturation order): the starvation flag fires
on ANY calendar day -- the weekend/legal-idle whitelist exemption is
ABOLISHED; the only legal convergence is feeding the pool with real
historical batches. Quiet exit 0
unless flags fire; history appended to results/compute_audit.json for
two-source (sample+history) judgment.
v2.4 (O-20260928-1614 sec.5 + O-20260928-1625 P0 correction, standing
SATURATION MECHANISM law): supply-family legs --
  * supply_gap (eighth flag, the O-1625 miss-face): py<70% WITH claimable
    pool work (ready>0) sustained >=15min = flagged state; the 15:40 live
    case (py 11.6%, ready=1, verdict CLEAN) is the named leak this closes.
  * starvation sustained window tightened 30min -> 15min (O-1614 sec.5).
  * supply_floor (sec.1): pool ready below floor 3 while NOT burning.
  * ignition_sla (sec.2): a ready entry unclaimed (no shard owner) past
    60s = SLA breach (enforcement = any-machine force-claim). Line
    tightened 10min -> 1min in T-107 slice-3 (r179 bm-c): the D2
    resident dispatcher landed r175 (30s detect + 15s spacing + ~15s
    tick) and the r179 ladder-adoption slice closed the supply loop;
    the autofill C8 10-min tick remains as the backstop lane only.
  * supply_family_streak_min: escalation metadata (flag family unconverged
    15min -> auto-escalate to GM dispatch face).
O-20260928-1630/O-1640 architecture layer (T-108 D1-D7) complements this
mechanism layer; the two-pool sovereignty face (quant HIGH vs scavenger)
reports through the T-107 utilization face (daily_report).

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
sys.path.insert(0, ROOT)
from config.lane_io import (mirror_shared_if_changed,  # noqa: E402
                           write_lane)  # D-03(1) batch-1
SAMPLE_WINDOW_S = 3
CAP_POLICY = 0.80            # O-20260923-1738
CAP_TOLERANCE = 1.06         # 85% trip line
BLIND_BURN_PY_CPU = 60.0     # % of machine capacity
BLIND_BURN_STALE_MIN = 15.0
IDLE_CPU = 20.0
GPU_UTIL_TRIP = 10.0
ZOMBIE_AGE_MIN = 45.0
STARVATION_PY_CPU = 70.0     # O-20260925-1137 py line
STARVATION_SUSTAIN_MIN = 15.0   # v2.4: 30->15min tightened per O-1614 sec.5
STARVATION_MIN_SAMPLES = 3
SUPPLY_FLOOR_READY = 3        # O-20260928-1614 sec.1 supply floor
IGNITION_SLA_MIN = 1.0        # O-20260928-1614 sec.2 acceptance line:
                              # <=60s ignition once D2 went live (T-108
                              # r175) and the r179 ladder-adoption slice
                              # closed the supply loop; the autofill C8
                              # 10-min tick stays as the backstop lane
SUPPLY_GAP_SUSTAIN_MIN = 15.0  # O-20260928-1614 sec.5 P0 window
SUPPLY_FAMILY_FLAGS = ("supply_gap", "pool_starvation", "supply_floor",
                       "ignition_sla")
AUDIT_VERSION = "v2.4.2"     # v2.4 standing saturation mechanism;
                              # v2.4.1 r179 bm-c: ignition_sla 10min -> 60s
                              # acceptance line (D2 live r175 + ladder
                              # adoption slice r179; charter synced);
                              # v2.4.2 T-134 s4: parallel-efficiency row
                              # (core-seconds/wall-seconds per batch, law-2
                              # sampler aggregate -- observational, no flag)


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


def fleet_open_tasks(tasks_dir=None):
    """Open (unclaimed) ticket count -- claimed_by set (any machine) =
    claim lock per fleet/README sec.4, NOT an open work candidate (r528
    family residual: 18:51 audit flagged idle_with_work on the single
    open+claimed ticket while the watermark probe correctly said
    board-clear; r330 fix mirrors py_watermark._scan_tickets)."""
    if tasks_dir is None:
        tasks_dir = os.path.join(ROOT, "fleet", "tasks")
    n = 0
    for p in glob.glob(os.path.join(tasks_dir, "*.json")):
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            if d.get("status") == "open" and not d.get("claimed_by"):
                n += 1
        except Exception:
            pass
    return n


def _merged_pool(rdir):
    """T-116 s3 wave-1 flip (D-20260928-03(1) structural end-state): the
    audit's pool samples read the lane-merged view (shared + per-machine
    lanes, same merger recipes the S6 settle writes) -- dual-run zero-
    drift evidence 3/3/8 all-green 2026-09-29. Returns (view, None) or
    (None, reason) on read faults (fail-closed r98: corrupt source /
    identity contradiction -> unknown, never a silent bare read)."""
    try:
        sdir = os.path.join(ROOT, "scripts")
        if sdir not in sys.path:
            sys.path.insert(0, sdir)
        import merge_lane_views as _mlv
        shared = os.path.join(rdir, "runnable_pool.json")
        lanes = [os.path.join(rdir, "runnable_pool.%s.json" % m)
                 for m in _mlv.MACHINES]
        if not any(os.path.exists(p) for p in [shared] + lanes):
            return None, "missing everywhere (pre-flip missing-shared parity)"
        view = _mlv.face_view("runnable_pool", results_dir=rdir)
        return (view or {}).get("entries") or [], None
    except (Exception, SystemExit) as ex:
        return None, str(ex)


def pool_ready_count():
    """ready entries across the lane-merged pool view; None = unreadable.

    None (unknown) is deliberately distinct from 0 (known-empty): the
    starvation flag must not fire on a pool we could not read.
    """
    entries, _why = _merged_pool(os.path.join(ROOT, "results"))
    if entries is None:
        return None
    return sum(1 for e in entries if e.get("status") == "ready")


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


def supply_gap_decision(hist, now_epoch, cur_py, cur_ready, cur_ts):
    """v2.4 eighth flag (O-20260928-1614 sec.5 / O-20260928-1625 miss-face).

    Candidate = current sample py<70% WITH claimable pool work (ready>0).
    Full flag requires the trailing run of qualifying samples to span
    >= SUPPLY_GAP_SUSTAIN_MIN with >= STARVATION_MIN_SAMPLES samples --
    the pool-supply-gap load_state that previously audited verdict CLEAN
    (live case 2026-09-28 15:40: py 11.6%, ready=1, CLEAN = named leak).
    Returns (candidate, flag_fired, detail)."""
    if cur_ready is None or cur_py is None:
        return False, False, {"reason": "unknown_pool_or_py"}
    candidate = cur_py < STARVATION_PY_CPU and cur_ready > 0
    if not candidate:
        return False, False, {"reason": load_state(cur_py, cur_ready)}
    run = [cur_ts]
    for s in reversed(hist):
        py, rd = s.get("py_cpu_pct"), s.get("pool_ready_count")
        if py is None or rd is None:
            break
        if py < STARVATION_PY_CPU and rd > 0:
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
        if span_min is not None and span_min >= SUPPLY_GAP_SUSTAIN_MIN:
            return True, True, {"run_samples": len(run),
                                "span_min": round(span_min, 1)}
    return True, False, {"run_samples": len(run), "span_min": span_min}


def pool_ready_entries():
    """[(id, ready_since, claimed)] for status==ready entries; None =
    unreadable pool (r98 unknown-law: None != empty, never flag on None).
    ready_since = armed_at (r391 arming precedent) else entered_at;
    claimed = any shard carries a non-null owner (ignition in progress).
    T-116 s3 wave-1: reads the lane-merged view (see _merged_pool)."""
    entries, _why = _merged_pool(os.path.join(ROOT, "results"))
    if entries is None:
        return None
    out = []
    for e in entries:
        if e.get("status") != "ready":
            continue
        since = e.get("armed_at") or e.get("entered_at")
        claimed = any(s.get("owner") for s in (e.get("shards") or []))
        out.append((e.get("id"), since, claimed))
    return out


def ignition_sla_breaches(ready_entries, now_epoch):
    """v2.4 (O-20260928-1614 sec.2): a ready entry with no shard owner past
    IGNITION_SLA_MIN from ready-since = SLA breach. Unreadable pool (None)
    or missing timestamps never breach (honest unknown)."""
    if not ready_entries:
        return []
    out = []
    for eid, since, claimed in ready_entries:
        if claimed or not since:
            continue
        try:
            age_min = (now_epoch - time.mktime(time.strptime(
                since, "%Y-%m-%d %H:%M:%S"))) / 60.0
        except Exception:
            continue
        if age_min > IGNITION_SLA_MIN:
            out.append(eid)
    return out


def supply_family_streak_min(hist, cur_flags, now_epoch):
    """v2.4 escalation metadata (O-20260928-1614 sec.5): minutes the
    supply-family flags have fired in one continuous trailing run; the
    15min-unconverged auto-escalation to GM dispatch reads this face."""
    if not any(f in cur_flags for f in SUPPLY_FAMILY_FLAGS):
        return None
    run_ts = [time.strftime("%Y-%m-%d %H:%M:%S")]
    for s in reversed(hist):
        sflags = s.get("flags") or []
        if any(f in sflags for f in SUPPLY_FAMILY_FLAGS) and s.get("ts"):
            run_ts.append(s.get("ts"))
        else:
            break
    try:
        oldest = time.mktime(time.strptime(run_ts[-1], "%Y-%m-%d %H:%M:%S"))
        return round((now_epoch - oldest) / 60.0, 1)
    except Exception:
        return None


# ------------------------------------------------- s4 efficiency face (T-134)
CORE_SAMPLES_PATH = os.path.join(ROOT, "results", "pool_core_samples.jsonl")
PAR_EFF_WINDOW_MIN = 60.0    # trailing window for the per-batch aggregate


def parallel_efficiency_row(now_epoch, samples_path=None):
    """T-134 s4 (CEO order O-2026-09-30-2355): parallel-efficiency face =
    core-seconds / wall-seconds per batch, aggregated over the trailing
    window from the law-2 launch sampler (Tools/core_sampler.py ->
    results/pool_core_samples.jsonl, per-batch rows with verdicts).
    Pure aggregation, observational -- no new flag; missing/unreadable
    file -> honest zero-batch row (readable=False; the sampler fleet
    landed r496, per-machine lanes accrue as their launchers sample)."""
    path = samples_path or CORE_SAMPLES_PATH
    row = {"window_min": PAR_EFF_WINDOW_MIN, "batches_judged": 0,
           "core_seconds": 0.0, "wall_seconds": 0.0,
           "effective_cores": None, "multicore_burn": 0,
           "single_core_burn": 0, "too_short_to_sample": 0}
    if not os.path.exists(path):
        row["readable"] = False
        return row
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except Exception:
        row["readable"] = False
        return row
    cut = time.strftime("%Y-%m-%dT%H:%M",
                        time.localtime(now_epoch - PAR_EFF_WINDOW_MIN * 60))
    cpu_sum = wall_sum = 0.0
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        try:
            r = json.loads(ln)
        except Exception:
            continue
        if str(r.get("ts", ""))[:16] < cut:   # ISO prefix compare, minute precision
            continue
        v = r.get("verdict")
        if v == "too_short_to_sample":
            row["too_short_to_sample"] += 1
            continue
        if v in ("multicore_burn", "single_core_burn"):
            row["batches_judged"] += 1
            row[v] += 1
            cpu_sum += float(r.get("cpu_s") or 0.0)
            wall_sum += float(r.get("wall_s") or 0.0)
    row["core_seconds"] = round(cpu_sum, 2)
    row["wall_seconds"] = round(wall_sum, 2)
    if wall_sum > 0:
        row["effective_cores"] = round(cpu_sum / wall_sum, 2)
    row["readable"] = True
    return row


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

    # eighth flag + v2.4 supply-family legs (O-20260928-1614 sec.1/2/5):
    # supply_gap never-CLEAN family, supply floor, ignition SLA.
    gap_cand, gap_flag, gap_detail = supply_gap_decision(
        hist, time.time(), py_cpu_pct, ready,
        time.strftime("%Y-%m-%d %H:%M:%S"))
    if gap_flag:
        flags.append("supply_gap")
    ready_entries = pool_ready_entries()
    sla_ids = ignition_sla_breaches(ready_entries, time.time())
    if sla_ids:
        flags.append("ignition_sla")
    floor_breach = ready is not None and ready < SUPPLY_FLOOR_READY
    if floor_breach and py_cpu_pct is not None \
            and py_cpu_pct < STARVATION_PY_CPU:
        flags.append("supply_floor")
    streak_min = supply_family_streak_min(hist, flags, time.time())

    record = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "audit_version": AUDIT_VERSION,
        "cpu_total_pct": cpu_now,
        "py_cpu_pct": py_cpu_pct,
        "cores": cores,
        "py_procs": len(p2),
        "result_stale_min": None if stale is None else round(stale, 1),
        "fleet_open_tasks": open_tasks,
        "pool_ready_count": ready,
        "pool_ready_unclaimed": (None if ready_entries is None else
                                 sum(1 for _, _, c in ready_entries if not c)),
        "load_state": load_state(py_cpu_pct, ready),
        "pool_starvation_candidate": starve_cand,
        "pool_starvation_detail": starve_detail,
        "supply_gap_candidate": gap_cand,
        "supply_gap_detail": gap_detail,
        "supply_floor": {"ready": ready, "floor": SUPPLY_FLOOR_READY,
                         "breach": floor_breach},
        "ignition_sla_breach_ids": sla_ids,
        "supply_family_streak_min": streak_min,
        "gpu": gpu,
        "zombies": zombies,
        "single_core_hog_candidate": hog_candidate,
        "single_core_hog_detail": hog,
        "parallel_efficiency": parallel_efficiency_row(time.time()),
        "flags": flags,
        "verdict": "CLEAN" if not flags else "FLAG:" + ",".join(flags),
    }

    hist.append(record)
    payload = {"latest": record, "history": hist}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    # D-20260928-03(1) batch-1 writer dual-track: own lane alongside the
    # shared face (compat window -- shared stays authoritative; the
    # lane write never changes the audit exit contract).
    write_lane("compute_audit", payload, indent=2)
    # D-03(1) batch-1 scattered-writer faces: gate_attrition /
    # post_review_criteria writers are one-off batch runners (~40 live
    # sites and new ones appear with every prereg wave), so per-site
    # wiring decays structurally -- this every-round audit leg maintains
    # both lanes via churn-free mirrors instead (any snapshot ever
    # captured is lossless under merger union semantics).
    for _face in ("gate_attrition", "post_review_criteria"):
        mirror_shared_if_changed(_face)
    # runnable_pool leaves the one-way mirror family (debt-③ slice-5,
    # r385): the pool is the ONE face with BOTH a tick dual-track writer
    # (claim/keepalive/done write shared + own lane) and free-form
    # session writers (defer/flip one-off scripts touch ONLY the shared
    # file, r378 catch #4), so a shared->lane byte mirror is the r381
    # audit-③ stale-shared rollback shape in waiting -- the day the
    # tick goes lane-primary it would swallow a lane-only keepalive
    # (r288 double-burn family).  Merged-sync settles BOTH sides to
    # the same marker-law union consumers read, churn-free.
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from merge_lane_views import sync_face
        _sync = sync_face("runnable_pool")
        if _sync.get("status") not in ("settled", "unchanged"):
            print(f"compute_audit: runnable_pool merged-sync "
                  f"{_sync.get('status')} -- neither side written "
                  f"({_sync.get('notes')})", file=sys.stderr)
        elif _sync.get("status") == "settled":
            print("compute_audit: runnable_pool merged-sync settled "
                  + json.dumps({k: _sync.get(k) for k in
                                ("wrote_shared", "wrote_lane")},
                               ensure_ascii=False), file=sys.stderr)
    except (Exception, SystemExit) as _ex:
        print(f"compute_audit: runnable_pool merged-sync fault: {_ex} "
              "(fail-soft, mirrors stay authoritative)",
              file=sys.stderr)

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
    # (g) v2.3 any-calendar-day law (O-20260926-2320): Saturday timestamps
    # (2026-09-26 is a Saturday) with a sustained starved window still fire
    # the flag -- weekend exemption abolished; any future weekday branch
    # added to the decision path must turn this case red first.
    sat_now = time.mktime(time.strptime("2026-09-26 23:00:00",
                                        "%Y-%m-%d %H:%M:%S"))
    sat_hist = [
        {"ts": "2026-09-26 22:20:00", "py_cpu_pct": 0.2,
         "pool_ready_count": 0},
        {"ts": "2026-09-26 22:40:00", "py_cpu_pct": 8.0,
         "pool_ready_count": 0},
        {"ts": "2026-09-26 22:50:00", "py_cpu_pct": 0.2,
         "pool_ready_count": 0},
    ]
    import datetime as _dt
    check("2026-09-26 is Saturday (fixture validity)",
          _dt.date(2026, 9, 26).weekday(), 5)
    cand, flag, det = starvation_decision(
        sat_hist, sat_now, 0.2, 0, "2026-09-26 23:00:00")
    check("saturday starvation -> flag (v2.3 anyday)",
          (cand, flag), (True, True))
    # taxonomy sanity
    check("burning state", load_state(85.0, 0), "burning-healthy")
    check("starvation state", load_state(1.9, 0), "idle-starvation")

    # ---- v2.4 legs (O-20260928-1614 sec.1/2/5) ----
    # (h) supply_gap sustained: py<70 + ready>0 over ~30min -> candidate+flag
    hist_gap = [sample(30, 11.6, 1), sample(20, 9.0, 1), sample(10, 11.0, 1)]
    cand, flag, det = supply_gap_decision(
        hist_gap, now, 11.6, 1, ts_ago(0))
    check("v2.4 supply_gap sustained -> flag (15:40 miss-face closed)",
          (cand, flag), (True, True))
    # (h2) short span -> candidate only (SLA/fill window still open)
    cand, flag, _ = supply_gap_decision(
        [sample(10, 11.6, 1)], now, 11.6, 1, ts_ago(0))
    check("v2.4 supply_gap short span -> candidate only",
          (cand, flag), (True, False))
    # (h3) burning -> no candidate (healthy saturation)
    cand, flag, _ = supply_gap_decision(hist_gap, now, 85.0, 1, ts_ago(0))
    check("v2.4 supply_gap burning -> none", (cand, flag), (False, False))
    # (h4) ready==0 falls to starvation family, not gap
    cand, flag, _ = supply_gap_decision(hist, now, 1.9, 0, ts_ago(0))
    check("v2.4 ready==0 -> not gap (starvation owns)", (cand, flag),
          (False, False))
    # (i) ignition SLA: unclaimed past 10min = breach; claimed/fresh = none
    def _ts(min_ago):
        return time.strftime("%Y-%m-%d %H:%M:%S",
                             time.localtime(now - min_ago * 60))
    check("v2.4.1 sla unclaimed 12min -> breach",
          ignition_sla_breaches([("E-X", _ts(12), False)], now), ["E-X"])
    check("v2.4.1 sla claimed -> no breach",
          ignition_sla_breaches([("E-X", _ts(12), True)], now), [])
    check("v2.4.1 sla fresh 30s -> no breach",
          ignition_sla_breaches([("E-X", _ts(0.5), False)], now), [])
    check("v2.4.1 sla 5min unclaimed -> breach (line 60s, r179)",
          ignition_sla_breaches([("E-X", _ts(5), False)], now), ["E-X"])
    check("v2.4.1 sla unreadable pool -> never breach",
          ignition_sla_breaches(None, now), [])
    # (j) supply floor: below 3 while NOT burning = flag condition
    check("v2.4 floor breach recorded (ready 2 < 3)", (2 < SUPPLY_FLOOR_READY),
          True)
    check("v2.4 floor ok at 3", (3 < SUPPLY_FLOOR_READY), False)
    # (k) escalation streak: trailing family run spans from oldest carry
    streak = supply_family_streak_min(
        [{"ts": ts_ago(20), "flags": ["supply_gap"]},
         {"ts": ts_ago(10), "flags": ["supply_gap"]}], ["supply_gap"], now)
    check("v2.4 streak >= 20min from trailing run", streak is not None
          and streak >= 20.0, True)
    check("v2.4 no family flags -> streak None",
          supply_family_streak_min([], ["zombie_process"], now), None)

    # ---- T-134 s4 legs (O-2026-09-30-2355) ----
    # (l) parallel-efficiency aggregation: hermetic temp jsonl, window filter
    #     + weighted effective cores + verdict-class counts
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "cores.jsonl")
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%S")
        rows = [
            {"ts": now_iso, "machine_id": "bm-a", "entry": "A", "shard": "1",
             "wall_s": 30.0, "cpu_s": 300.0, "effective_cores": 10.0,
             "verdict": "multicore_burn"},
            {"ts": now_iso, "machine_id": "bm-a", "entry": "B", "shard": "2",
             "wall_s": 30.0, "cpu_s": 30.0, "effective_cores": 1.0,
             "verdict": "single_core_burn"},
            {"ts": now_iso, "machine_id": "bm-a", "entry": "C", "shard": "3",
             "wall_s": 5.0, "cpu_s": 4.0, "effective_cores": 0.8,
             "verdict": "too_short_to_sample"},
            {"ts": "2026-09-30T00:00:00", "machine_id": "bm-a",
             "entry": "OLD", "shard": "4", "wall_s": 30.0, "cpu_s": 300.0,
             "effective_cores": 10.0, "verdict": "multicore_burn"},
        ]
        with open(p, "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
        pe = parallel_efficiency_row(now, samples_path=p)
    check("s4 window filter keeps 2 judged", pe["batches_judged"], 2)
    check("s4 weighted cores 330/60=5.5", pe["effective_cores"], 5.5)
    check("s4 single_core count", pe["single_core_burn"], 1)
    check("s4 multicore count", pe["multicore_burn"], 1)
    check("s4 too_short counted not judged", pe["too_short_to_sample"], 1)
    check("s4 missing file -> unreadable",
          parallel_efficiency_row(
              now, samples_path=os.path.join("Z:\\no", "such.jsonl"))
          .get("readable"), False)

    # ---- r330 leg: fleet_open_tasks claim-lock exclusion (r528 family) --
    import tempfile
    with tempfile.TemporaryDirectory() as tmpd:
        td = os.path.join(tmpd, "tasks")
        os.makedirs(td)
        for tid, st_ in (("T-1", "open"), ("T-2", "done"),
                         ("T-3", "open"), ("T-4", "open")):
            d = {"id": tid, "status": st_}
            if tid == "T-4":
                # mirrors the live T-141 shape: status=open but claimed
                # by another machine -> claim lock, not open work (r528)
                d["claimed_by"] = "bm-b"
            with open(os.path.join(td, tid + ".json"), "w",
                      encoding="utf-8") as f:
                json.dump(d, f)
        check("fleet_open_tasks open+unclaimed only",
              fleet_open_tasks(td), 2)
        with open(os.path.join(td, "bad.json"), "w", encoding="utf-8") as f:
            f.write("{broken")
        check("fleet_open_tasks tolerates corrupt",
              fleet_open_tasks(td), 2)

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
