#!/usr/bin/env python
"""O-20260930-2355 law-2 launch-verification sampler (T-134 s3).

CEO direct order 2026-09-30 ~23:5x: "我是多核CPU！你写的玩意不是只
烧一个核一个线程！...解决好！" -- the launcher must sample the core
distribution of every burn within 60s of launch; a single-core burn is
a red flag (瞎跑 face), not "ran = worked".

Contract (spawned detached by Tools/autofill.py right after the runner
Popen):

    python Tools/core_sampler.py <pid> <entry_id> <shard_key> [max_s]

Samples the runner process tree (parent + children -- ProcessPool
workers are children) cpu-times every SAMPLE_S until the process exits
or max_s (default 60) elapses, then appends ONE JSON line to
results/pool_core_samples.jsonl:

    {"ts", "machine_id", "pid", "entry", "shard", "wall_s", "cpu_s",
     "samples", "effective_cores", "verdict"}

verdict:
  multicore_burn        effective_cores >= MULTICORE_MIN (real spread)
  single_core_burn      effective_cores < MULTICORE_MIN and wall >=
                        MIN_SAMPLE_WALL_S (the CEO red-flag face)
  too_short_to_sample   process ended before MIN_SAMPLE_WALL_S (honest:
                        fast deterministic burns are not core-spread
                        judgeable)
  process_missing       pid never observed alive (instant-exit family --
                        the crash-fuse face owns that classification)

Exit 0 always (a sampler fault must never kill a burn); selftest
subcommand is offline/hermetic per house law.
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES_PATH = os.path.join(ROOT, "results", "pool_core_samples.jsonl")
SAMPLE_S = 5.0
MULTICORE_MIN = 1.5      # avg cores over the sampled window
MIN_SAMPLE_WALL_S = 10.0


def _machine_id():
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"),
                  encoding="utf-8") as fh:
            mid = json.load(fh).get("machine_id")
        return str(mid) if mid else "unknown"
    except Exception:
        return "unknown"


def _tree_cpu(pid):
    """cpu-seconds of the process tree, or None when pid is gone."""
    try:
        import psutil
        try:
            pr = psutil.Process(pid)
            total = sum(pr.cpu_times()[:2])
        except Exception:
            return None
        for ch in pr.children(recursive=True):
            try:
                total += sum(ch.cpu_times()[:2])
            except Exception:
                pass
        return total
    except Exception:
        return None


def _verdict(wall_s, effective_cores):
    if wall_s < MIN_SAMPLE_WALL_S:
        return "too_short_to_sample"
    if effective_cores is not None and effective_cores >= MULTICORE_MIN:
        return "multicore_burn"
    return "single_core_burn"


def run(pid, entry, shard, max_s=60.0, samples_path=SAMPLES_PATH):
    import datetime
    pid = int(pid)
    t0 = time.time()
    first = _tree_cpu(pid)
    if first is None:
        rec = {"ts": datetime.datetime.now().astimezone().isoformat(
                   timespec="seconds"),
               "machine_id": _machine_id(), "pid": pid, "entry": entry,
               "shard": shard, "wall_s": 0.0, "cpu_s": 0.0,
               "samples": 0, "effective_cores": None,
               "verdict": "process_missing"}
        _append(samples_path, rec)
        return 0
    cpu0, samples = first, 0
    while time.time() - t0 < max_s:
        time.sleep(SAMPLE_S)
        cur = _tree_cpu(pid)
        if cur is None:
            break
        cpu0 = max(cpu0, cur)
        samples += 1
    wall = time.time() - t0
    cpu_s = cpu0 - first
    eff = round(cpu_s / wall, 2) if wall > 0 else None
    rec = {"ts": datetime.datetime.now().astimezone().isoformat(
               timespec="seconds"),
           "machine_id": _machine_id(), "pid": pid, "entry": entry,
           "shard": shard, "wall_s": round(wall, 1),
           "cpu_s": round(cpu_s, 2), "samples": samples,
           "effective_cores": eff, "verdict": _verdict(wall, eff)}
    _append(samples_path, rec)
    return 0


def _append(path, rec):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def selftest():
    """Offline hermetic self-check: verdict boundaries + append format."""
    fails = []

    def check(name, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            fails.append(name)

    check("V1_multicore", _verdict(30.0, 12.0) == "multicore_burn")
    check("V2_single_core", _verdict(30.0, 1.0) == "single_core_burn")
    check("V3_boundary_below", _verdict(30.0, 1.49) == "single_core_burn")
    check("V4_boundary_at", _verdict(30.0, 1.5) == "multicore_burn")
    check("V5_too_short", _verdict(9.0, 1.0) == "too_short_to_sample")
    check("V6_short_even_wide", _verdict(5.0, 8.0) == "too_short_to_sample")
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "s.jsonl")
        _append(p, {"a": 1})
        _append(p, {"a": 2})
        lines = [json.loads(l) for l in open(p, encoding="utf-8")]
        check("V7_append_jsonl", len(lines) == 2 and lines[1]["a"] == 2)
    print(f"selftest: {len(fails)} FAIL" if fails else "selftest: ALL PASS")
    return 1 if fails else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "selftest":
        return selftest()
    if len(argv) < 3:
        print("usage: core_sampler.py <pid> <entry> <shard> [max_s]")
        return 2
    max_s = float(argv[3]) if len(argv) > 3 else 60.0
    try:
        return run(argv[0], argv[1], argv[2], max_s)
    except Exception as ex:            # never kill the burn's window
        print(f"sampler fault (honest, burn unaffected): {ex}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
