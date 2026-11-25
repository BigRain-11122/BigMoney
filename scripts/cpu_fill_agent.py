"""CPU-fill agent: a standing worker that keeps real work running, not one cell per tick.

Why this exists
---------------
The bench tick ran one cell every twenty minutes and most cells finish in one to
nine seconds. Duty cycle under one percent -- which reads, correctly, as idle
machinery. This agent is the opposite shape: it runs for a bounded window
(default 280s of every 5-minute slot), takes work from a catalog, and keeps
several units in flight at once so the cores are actually used.

What counts as work here
------------------------
Only units that produce an artefact a reader can use:
  * data audits in shards (find poisoned bars before they poison a backtest);
  * statistical refinements of the one GO (bootstrap with more resamples);
  * heavier censuses, gated on RAM and on the media line being quiet.
Nothing is invented to make a number look busy: if the catalog is empty and the
audits are complete, the agent reports STARVED and exits -- that is information
for the person who owes the next question, not a reason to spin.

Interlocks
----------
* Singleton lock (one agent per machine; a crashed agent's lock is reclaimed).
* Arbiter: every unit asks for a class before running, so the media line keeps
  its claim on GPU/RAM and the agent waits instead of competing.
* Time budget: the agent exits when its window closes, so the scheduled task can
  restart it cleanly every slot (no long-lived process to leak).
"""
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import silent_run  # noqa: E402

CATALOG = os.path.join(ROOT, "research", "CPU-WORK.json")
OUT_DIR = os.path.join(ROOT, "results", "cpu_fill")
STATE = os.path.join(OUT_DIR, "STATE.json")
LEDGER = os.path.join(OUT_DIR, "LEDGER.jsonl")
LOCK = os.path.join(OUT_DIR, ".agent.lock")
AUDIT_DIR = os.path.join(ROOT, "results", "audit")
TZ = timezone(timedelta(hours=8))

LANE_FILES = {
    "astock": os.path.join(ROOT, "data", "astock_daily", "per"),
    "etf": os.path.join(ROOT, "data", "daily"),
    "cb": os.path.join(ROOT, "data", "cb_daily"),
    "moneyflow": os.path.join(ROOT, "data", "moneyflow"),
}
SHARD = 250


def now():
    return datetime.now(TZ)


def read_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def ledger(row):
    os.makedirs(OUT_DIR, exist_ok=True)
    row = dict(row)
    row.setdefault("ts", now().isoformat(timespec="seconds"))
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def acquire_lock():
    os.makedirs(OUT_DIR, exist_ok=True)
    if os.path.exists(LOCK):
        try:
            age = time.time() - os.path.getmtime(LOCK)
            pid = int(open(LOCK, encoding="ascii").read().strip() or 0)
        except Exception:
            age, pid = 1e9, 0
        alive = False
        if pid:
            try:
                import psutil
                alive = psutil.pid_exists(pid)
            except Exception:
                alive = age < 3600
        if alive and age < 3600:
            return False
        try:
            os.remove(LOCK)
        except OSError:
            pass
    with open(LOCK, "w", encoding="ascii") as f:
        f.write(str(os.getpid()))
    return True


def release_lock():
    try:
        os.remove(LOCK)
    except OSError:
        pass


# --------------------------------------------------------------------------
# work supply
# --------------------------------------------------------------------------
def audit_progress():
    """How many shards of each lane already exist, and how many files each lane has."""
    done = {}
    if os.path.isdir(AUDIT_DIR):
        for f in os.listdir(AUDIT_DIR):
            if f.endswith(".json") and "-" in f:
                lane = f.split("-")[0]
                done[lane] = done.get(lane, 0) + 1
    out = {}
    for lane, path in LANE_FILES.items():
        if not os.path.isdir(path):
            continue
        files = len([f for f in os.listdir(path) if f.endswith(".csv")])
        shards = (files + SHARD - 1) // SHARD
        out[lane] = {"files": files, "shards": shards,
                     "done": done.get(lane, 0),
                     "next_start": done.get(lane, 0) * SHARD}
    return out


def next_catalog_unit():
    cat = read_json(CATALOG, {"units": []}) or {"units": []}
    for u in cat.get("units", []):
        if u.get("status") == "open":
            return u
    return None


def mark_catalog_unit(uid, status, seconds):
    cat = read_json(CATALOG, {"units": []}) or {"units": []}
    for u in cat.get("units", []):
        if u.get("id") == uid:
            u["status"] = status
            u["finished"] = now().isoformat(timespec="seconds")
            u["seconds"] = round(seconds, 1)
    write_json(CATALOG, cat)


def next_audit_unit():
    prog = audit_progress()
    for lane, v in sorted(prog.items(), key=lambda kv: -(kv[1]["shards"] - kv[1]["done"])):
        if v["done"] < v["shards"]:
            return {"id": f"audit:{lane}:{v['next_start']}",
                    "cmd": [sys.executable, os.path.join(ROOT, "scripts", "data_audit.py"),
                            "--lane", lane, "--start", str(v["next_start"]),
                            "--count", str(SHARD)],
                    "class": "cpu_light", "est_s": 6, "purpose": "data audit shard",
                    "lane": lane}
    return None


def pick_unit():
    u = next_catalog_unit()
    if u:
        cmd = u["cmd"]
        if isinstance(cmd, str):
            cmd = [cmd]
        first, rest = cmd[0], list(cmd[1:])
        if first.lower().endswith(".py"):
            cmd = [sys.executable, first if os.path.isabs(first) else os.path.join(ROOT, first)] + rest
        return {"id": u["id"], "cmd": cmd, "class": u.get("class", "cpu_light"),
                "est_s": u.get("est_s", 30), "purpose": u.get("purpose", ""),
                "source": "catalog"}
    u = next_audit_unit()
    return dict(u, source="audit") if u else None


# --------------------------------------------------------------------------
# execution
# --------------------------------------------------------------------------
def ask_arbiter(cls):
    try:
        import line_arbiter as la
        d = la.ask("cpu_fill", cls)
        return d
    except Exception as e:
        return {"allow": True, "reason": f"ARBITER_UNAVAILABLE({e})", "cls": cls}


def release_arbiter(cls):
    try:
        import line_arbiter as la
        la.release(cls)
    except Exception:
        pass


def run_unit(u, deadline):
    remaining = max(5, int(deadline - time.time()))
    grant = ask_arbiter(u["class"])
    if not grant.get("allow"):
        return {"id": u["id"], "state": "WAIT_RESOURCE", "reason": grant.get("reason"),
                "seconds": 0.0}
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["OMP_NUM_THREADS"] = str(u.get("threads", 1))
    t0 = time.time()
    try:
        p = silent_run.run(u["cmd"], cwd=ROOT, env=env, timeout=remaining)
        secs = round(time.time() - t0, 1)
        ok = p.returncode == 0
        return {"id": u["id"], "state": "DONE" if ok else "FAILED",
                "rc": p.returncode, "seconds": secs,
                "tail": (p.stderr or "")[-200:] if not ok else None}
    except subprocess.TimeoutExpired:
        return {"id": u["id"], "state": "TIMEOUT", "seconds": round(time.time() - t0, 1)}
    finally:
        release_arbiter(u["class"])


def sample_cpu():
    try:
        import psutil
        return round(psutil.cpu_percent(interval=None), 1)
    except Exception:
        return None


def run(budget=280, procs=4):
    if not acquire_lock():
        print(json.dumps({"ok": True, "state": "LOCKED", "reason": "another agent is running"}))
        return 0
    t_start = time.time()
    deadline = t_start + budget
    done, waiting, busy_seconds = [], [], 0.0
    try:
        while time.time() < deadline:
            batch = []
            while len(batch) < procs and time.time() < deadline:
                u = pick_unit()
                if not u:
                    break
                batch.append(u)
            if not batch:
                break
            with ThreadPoolExecutor(max_workers=len(batch)) as ex:
                futs = {ex.submit(run_unit, u, deadline): u for u in batch}
                for f in as_completed(futs):
                    u = futs[f]
                    try:
                        r = f.result()
                    except Exception as e:
                        r = {"id": u["id"], "state": "ERROR", "reason": str(e)}
                    r["purpose"] = u.get("purpose")
                    r["source"] = u.get("source")
                    if r["state"] in ("DONE", "FAILED", "TIMEOUT"):
                        busy_seconds += r.get("seconds") or 0
                        done.append(r)
                        if u.get("source") == "catalog":
                            mark_catalog_unit(u["id"], r["state"].lower(), r.get("seconds") or 0)
                    else:
                        waiting.append(r)
                    ledger(r)
            if waiting and not done:
                break          # arbiter refused everything: stop, do not spin
        elapsed = round(time.time() - t_start, 1)
        duty = round(100.0 * min(busy_seconds, elapsed * procs) / max(elapsed * procs, 1e-9), 1)
        state = {
            "generated": now().isoformat(timespec="seconds"),
            "budget_s": budget, "procs": procs, "elapsed_s": elapsed,
            "units_done": len(done), "units_waiting": len(waiting),
            "busy_seconds_sum": round(busy_seconds, 1),
            "duty_pct_of_slots": duty,
            "cpu_sample_pct": sample_cpu(),
            "audit_progress": audit_progress(),
            "last_units": done[-8:],
            "verdict": ("SATURATED" if duty >= 60 else
                        ("STARVED" if not done else "PARTIAL")),
        }
        write_json(STATE, state)
        print(json.dumps({"ok": True, "verdict": state["verdict"],
                          "units": len(done), "duty_pct": duty,
                          "elapsed_s": elapsed,
                          "waiting": len(waiting)}, ensure_ascii=False))
        return 0
    finally:
        release_lock()


def status():
    s = read_json(STATE, {}) or {}
    s["audit_progress"] = audit_progress()
    cat = read_json(CATALOG, {"units": []}) or {"units": []}
    s["catalog_open"] = sum(1 for u in cat.get("units", []) if u.get("status") == "open")
    print(json.dumps(s, ensure_ascii=False, indent=1))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=280)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()
    if a.status:
        return status()
    return run(a.budget, a.procs)


if __name__ == "__main__":
    sys.exit(main())
