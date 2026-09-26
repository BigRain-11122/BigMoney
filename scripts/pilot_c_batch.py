"""T-70 pilot C-arm batch orchestrator (MSG-20260926-0925-bm-a).

Sequential 01-10, checkpoint-resume (verdict.json present = task done =
skip), per-task ledger row appended to
results/local_coding_pilot/ledger.jsonl (append-only, zero edits to
existing rows), status mirror results/local_coding_pilot/C_batch_status.json
for supervision legs in later rounds. Resource gates per batch-1 prereg
section-1 terms (weekend window, board clear, pool empty, RAM free
> 30GB checked pre-spawn by the caller; NUM_PARALLEL=1 -> sequential).

Usage:
    python scripts/pilot_c_batch.py run       # full pass (resume-safe)
    python scripts/pilot_c_batch.py status   # print mirror
"""

import io
import json
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PILOT = os.path.join(REPO, "results", "local_coding_pilot")
LEDGER = os.path.join(PILOT, "ledger.jsonl")
MIRROR = os.path.join(PILOT, "C_batch_status.json")
TASKS = [f"{i:02d}" for i in range(1, 11)]


def _mirror(state):
    io.open(MIRROR, "w", encoding="utf-8").write(
        json.dumps(state, ensure_ascii=False, indent=1))


def _append_ledger(nn, v, gen_stats):
    row = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "task": nn,
        "arm": "C_selffix",
        "verify_cmd": f"python tasks/{nn}/C/<name>.py selftest "
                      "(frozen arm-placement form)",
        "arm_C_selffix": {
            "verdict": v["verdict"], "fix_rounds": v["fix_rounds"],
            "fix_rounds_label": v["fix_rounds_dist_label"],
            "attempts": v["attempts"],
            "gen": gen_stats,
        },
        "ledger_note": "C arm per MSG-20260926-0925-bm-a; batch-1 A/B rows "
                       "untouched; interpretation lines frozen in "
                       "R-20260926-bma-pilot-C-arm.md",
    }
    with io.open(LEDGER, "a", encoding="utf-8", newline="") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def run():
    state = {"mode": "running", "started": time.strftime("%Y-%m-%d %H:%M:%S"),
             "done": [], "failed_tasks": [], "current": None,
             "updated": time.strftime("%Y-%m-%d %H:%M:%S")}
    _mirror(state)
    for nn in TASKS:
        task_dir = os.path.join(PILOT, "tasks", nn)
        verdict_path = os.path.join(task_dir, "C", "verdict.json")
        if os.path.exists(verdict_path):
            v = json.load(io.open(verdict_path, encoding="utf-8"))
            state["done"].append({"task": nn, "verdict": v.get("verdict"),
                                  "fix_rounds": v.get("fix_rounds"),
                                  "resumed": True})
            _mirror(state)
            print(f"[batch] task {nn}: verdict.json present -> resume skip")
            continue
        state["current"] = nn
        state["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        _mirror(state)
        r = subprocess.run(
            [sys.executable, os.path.join(REPO, "scripts", "pilot_c_client.py"),
             task_dir], cwd=REPO)
        if r.returncode == 0 and os.path.exists(verdict_path):
            v = json.load(io.open(verdict_path, encoding="utf-8"))
            metrics = json.load(io.open(
                os.path.join(task_dir, "C", "metrics.json"),
                encoding="utf-8"))
            gen_stats = {
                "attempts": len(metrics),
                "total_s_sum": round(sum(m.get("total_s") or 0 for m in metrics), 1),
                "tok_s_last": metrics[-1].get("tok_s"),
                "eval_count_sum": sum(m.get("eval_count") or 0 for m in metrics),
            }
            _append_ledger(nn, v, gen_stats)
            state["done"].append({"task": nn, "verdict": v["verdict"],
                                  "fix_rounds": v["fix_rounds"]})
        else:
            state["failed_tasks"].append({"task": nn, "exit": r.returncode})
        state["current"] = None
        state["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        _mirror(state)
    passes = [d for d in state["done"] if d.get("verdict") == "PASS"]
    state["mode"] = "complete"
    state["summary"] = {
        "n_done": len(state["done"]), "n_pass": len(passes),
        "dist": {
            "0_single_shot": sum(1 for d in state["done"]
                                 if d.get("verdict") == "PASS" and d.get("fix_rounds") == 0),
            "1_3_rounds": sum(1 for d in state["done"]
                              if d.get("verdict") == "PASS" and 1 <= (d.get("fix_rounds") or 0) <= 3),
            "3_fail": sum(1 for d in state["done"] if d.get("verdict") == "FAIL"),
        },
    }
    state["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    _mirror(state)
    print("[batch] complete:", json.dumps(state["summary"], ensure_ascii=False))
    return 0


def status():
    if not os.path.exists(MIRROR):
        print("no C batch mirror yet")
        return 0
    print(io.open(MIRROR, encoding="utf-8").read())
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        sys.exit(run())
    sys.exit(status())
