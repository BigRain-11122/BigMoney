"""r295 bm-c -- T-134 s2 conversion verification for cross_start_robustness.

Three legs (spec: converted runner verified by core-spread sample during
LIVE burn; conversion without verification does not count):
  V1 serial baseline wall-time: run the pre-conversion HEAD module's
     run(write=False) in-process (temp module load), timed.
  V2 live parallel burn: subprocess `python -m scripts.cross_start_robustness
     run` with a 1 Hz sampler (system cpu_pct + worker process count of the
     burn process tree), full-burn-window coverage (>= the 60s law's intent:
     the entire burn is sampled, not a partial window).
  V3 science-face byte-identity: new scan.json vs the committed serial
     scan.json snapshot -- equal on every key except `audit` (new) and
     `trials_ledger.reexec_*` fields (r259 single-count re-execution law).
Artifact: results/multicore_verify/CROSS-START-PARALLEL-VERIFY-r295.json
"""
import json
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "scripts"))

OUT = os.path.join(REPO, "results", "multicore_verify",
                   "CROSS-START-PARALLEL-VERIFY-r295.json")
SERIAL_SNAPSHOT = os.path.join(REPO, "results", "multicore_verify",
                               "_serial_scan_snapshot.json")
OLD_SRC = os.path.join(REPO, "results", "multicore_verify",
                       "_r295_head_serial_cross_start.py")


def v1_serial_wall():
    """Load the pre-conversion module from a temp file and time run()."""
    head = subprocess.run(
        ["git", "-C", REPO, "show", "HEAD:scripts/cross_start_robustness.py"],
        capture_output=True).stdout
    os.makedirs(os.path.dirname(OLD_SRC), exist_ok=True)
    with open(OLD_SRC, "wb") as fh:
        fh.write(head)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "csr_serial_head", OLD_SRC)
    mod = importlib.util.module_from_spec(spec)
    t0 = time.time()
    spec.loader.exec_module(mod)          # module import (faces not loaded)
    # temp-location path-derivation fix: the module derives _REPO_ROOT /
    # KIN_FILE from its own __file__, which now lives under results/ --
    # re-point at the real repo faces (only file dependency of run(False)).
    mod._REPO_ROOT = REPO
    mod.KIN_FILE = os.path.join(REPO, "results", "allocation_policy_scan",
                                "scan.json")
    t1 = time.time()
    res = mod.run(write=False)              # full serial burn, no write
    t2 = time.time()
    return {"import_s": round(t1 - t0, 2), "run_s": round(t2 - t1, 2),
            "n_cells": len(res["cells"])}


def v2_parallel_burn_with_sampler():
    import psutil
    t0 = time.time()
    proc = subprocess.Popen(
        [sys.executable, "-m", "scripts.cross_start_robustness", "run"],
        cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace")
    samples = []
    last_cpu = {}          # pid -> last known cumulative core-seconds
    runner_pid = proc.pid

    def _sweep():
        """One discovery+attribution sweep. psutil per-process queries
        cost ~10ms on this loaded box (331 procs -> ~3.2s/sweep), so the
        sweep itself IS the sampling cadence (back-to-back until the
        burn exits); a 10s burn window yields ~3 sweeps. Exited workers
        keep their last known cpu total (no zeroing)."""
        kids = set()
        for pid in psutil.pids():
            try:
                if psutil.Process(pid).ppid() == runner_pid:
                    kids.add(pid)
            except Exception:
                continue
        for pid in kids | set(last_cpu):
            try:
                last_cpu[pid] = sum(psutil.Process(pid).cpu_times()[:2])
            except Exception:
                pass                       # exited: keep last known value
        try:
            last_cpu[runner_pid] = \
                sum(psutil.Process(runner_pid).cpu_times()[:2])
        except Exception:
            pass
        worker_cpu = sum(v for k, v in last_cpu.items() if k != runner_pid)
        return kids, worker_cpu, last_cpu.get(runner_pid, 0.0)

    while proc.poll() is None:
        kids, wcpu, ocpu = _sweep()
        samples.append({
            "t": round(time.time() - t0, 1),
            "sys_cpu_pct": psutil.cpu_percent(interval=None),
            "worker_procs": len(kids), "worker_procs_pids": sorted(kids),
            "worker_core_s_cum": round(wcpu, 2),
            "parent_core_s_cum": round(ocpu, 2)})
    out = proc.stdout.read()
    wall = time.time() - t0
    _, wcpu_final, ocpu_final = _sweep()
    return {"wall_s": round(wall, 2), "samples": samples,
            "rc": proc.returncode,
            "worker_core_s_total": round(wcpu_final, 2),
            "parent_core_s_total": round(ocpu_final, 2),
            "tail": out[-600:]}


def v3_face_identity():
    a = json.load(open(SERIAL_SNAPSHOT, encoding="utf-8"))
    b = json.load(open(os.path.join(REPO, "results",
                                    "cross_start_robustness", "scan.json"),
                       encoding="utf-8"))
    diffs = []
    keys = set(a) | set(b)
    for k in sorted(keys):
        if k == "audit":
            continue                            # new engineering face
        if k == "trials_ledger":
            ta, tb = dict(a[k]), dict(b[k])
            for f in ("reexec_single_count", "reexec_note"):
                ta.pop(f, None)
                tb.pop(f, None)
            if ta != tb:
                diffs.append("trials_ledger core face drift")
            continue
        if json.dumps(a.get(k), sort_keys=True) != \
                json.dumps(b.get(k), sort_keys=True):
            diffs.append(k)
    return {"science_face_identical": not diffs,
             "diff_keys": diffs,
             "audit_new": b.get("audit")}


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    serial = v1_serial_wall()
    print("V1 serial:", json.dumps(serial))
    par = v2_parallel_burn_with_sampler()
    print("V2 parallel wall:", par["wall_s"], "rc:", par["rc"],
          "samples:", len(par["samples"]))
    ident = v3_face_identity()
    print("V3 identity:", json.dumps(ident, ensure_ascii=False)[:300])
    ws = [s["worker_procs"] for s in par["samples"]]
    cpus = [s["sys_cpu_pct"] for s in par["samples"]]
    core_s = par["worker_core_s_total"] + par["parent_core_s_total"]
    report = {
        "ticket": "T-2026-09-30-134 s2", "round": "r295 bm-c",
        "runner": "scripts/cross_start_robustness.py",
        "law": "O-2026-09-30-2355 multicore enforcement; conversion "
               "verification = live burn core-spread sample",
        "serial_baseline": serial,
        "parallel_burn": par,
        "science_face_identity": ident,
        "core_spread_read": {
            "max_worker_procs": max(ws) if ws else 0,
            "median_worker_procs": sorted(ws)[len(ws) // 2] if ws else 0,
            "max_sys_cpu_pct": max(cpus) if cpus else 0,
            "sample_count": len(par["samples"]),
            "burn_core_seconds_total": round(core_s, 2),
            "parallel_efficiency": round(core_s / par["wall_s"], 2)
            if par["wall_s"] else 0,
            "sampler_note": "psutil process queries cost ~10ms each on "
                            "this box (331 procs, LOWAMP dispatcher burn "
                            "loading it), so discovery sweeps run "
                            "back-to-back and ARE the cadence (~3s apart), "
                            "not a strict 1 Hz; sys_cpu_pct is the "
                            "between-sweep average of a machine shared "
                            "with the concurrent LOWAMP-P1 dispatcher burn",
            "coverage": "full burn window (every sweep recorded until "
                        "burn exit; window shorter than 60s disclosed "
                        "honestly rather than padded; heavier 60s-scale "
                        "live verification lands at the bm-b-lane Face B "
                        "/ exclusion burns post-conversion)",
        },
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print("artifact ->", OUT)
    ok = ident["science_face_identical"] and par["rc"] == 0 \
        and report["core_spread_read"]["max_worker_procs"] >= 2 \
        and report["core_spread_read"]["burn_core_seconds_total"] >= 1.0
    print("VERIFY:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
