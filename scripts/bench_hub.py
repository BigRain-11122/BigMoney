"""24/7 driver for the strategy bench: one pending cell per tick, ledgered.

Why a queue instead of "run everything"
--------------------------------------
A cell is only worth running when its question is still open. The queue file
(research/BENCH-QUEUE.json) is the single place that says which questions are
open, in what order, and what each one's verdict was. The driver does not think:
every 20 minutes a scheduled tick takes the first `pending` cell whose script
exists, runs it in a child python process, and writes the outcome to a ledger.
If the queue is empty the tick exits in milliseconds.

Guards (learned from this fleet's failures)
-------------------------------------------
* RAM guard: cells marked heavy are skipped while the machine has < 2.0 GB
  available, with a printed reason. A skipped cell stays pending; it is not a
  failure and it never records a verdict.
* Attempts: a cell that fails twice is marked `blocked` (with the reason), so
  one broken script cannot eat the night.
* Staleness: every cell declares the data lane it reads; if the newest bar in
  that lane is older than `max_bar_age_days`, the cell is reported
  DATA-BLOCKED instead of silently producing a result on stale bars. On a
  weekend/holiday this is the normal state (the bar is from the last session).
* One writer: a lock file keeps two concurrent ticks from running the same cell.

Usage
-----
  python scripts/bench_hub.py --status
  python scripts/bench_hub.py --next
  python scripts/bench_hub.py --cell fut_trend
  python scripts/bench_hub.py --selftest
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import silent_run  # noqa: E402  (children must never open a console window)

QUEUE = os.path.join(ROOT, "research", "BENCH-QUEUE.json")
BENCH = os.path.join(ROOT, "results", "bench")
LEDGER = os.path.join(BENCH, "LEDGER.jsonl")
STATE = os.path.join(BENCH, "HUB-STATE.json")
LOCK = os.path.join(BENCH, ".hub.lock")
STATUS_MD = os.path.join(ROOT, "research", "BENCH-STATUS.md")

TZ = timezone(timedelta(hours=8))
RAM_FLOOR_GB = 2.0
MAX_ATTEMPTS = 2
CELL_TIMEOUT_S = 3600
BAR_LANES = {
    "futures": os.path.join(ROOT, "data", "futures_daily"),
    "index": os.path.join(ROOT, "data", "index_daily"),
    "etf": os.path.join(ROOT, "data", "daily"),
    "cb": os.path.join(ROOT, "data", "cb_daily"),
    "astock": os.path.join(ROOT, "data", "astock_daily"),
    "repo": os.path.join(ROOT, "data", "repo_daily"),
}


def now():
    return datetime.now(TZ)


def load_queue():
    with open(QUEUE, encoding="utf-8") as f:
        return json.load(f)


def save_queue(q):
    q["updated"] = now().isoformat(timespec="seconds")
    tmp = QUEUE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(q, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, QUEUE)


def ram_gb():
    try:
        import psutil
        return psutil.virtual_memory().available / (1024 ** 3)
    except Exception:
        return None


def lane_bar_date(lane):
    """Newest date string found in the lane's files (cheap: newest file wins).

    Parquet/CSV lanes are dated by the last line's first column elsewhere; here
    we only need "is the lane recent", so file mtime + the last bar of the newest
    csv is enough and costs no full scan.
    """
    d = BAR_LANES.get(lane)
    if not d or not os.path.isdir(d):
        return None
    files = [f for f in os.listdir(d) if f.endswith(".csv")]
    if not files:
        return None
    files.sort(key=lambda f: os.path.getmtime(os.path.join(d, f)), reverse=True)
    newest = os.path.join(d, files[0])
    try:
        ts = datetime.fromtimestamp(os.path.getmtime(newest), TZ)
    except OSError:
        return None
    return ts.date()


def bar_age_days(cell):
    lane = cell.get("lane")
    if not lane:
        return None
    d = lane_bar_date(lane)
    if d is None:
        return None
    # mtime is the write time; on a weekend the newest bar is Friday's, so the
    # caller compares against max_bar_age_days which itself allows the weekend.
    return (now().date() - d).days


def is_recurring_due(cell):
    """A recurring cell (e.g. re-validation) becomes due again after its window."""
    if not cell.get("recurring"):
        return False
    last = cell.get("last_run")
    if not last:
        return True
    try:
        t = datetime.fromisoformat(last)
    except ValueError:
        return True
    if t.tzinfo is None:
        t = t.replace(tzinfo=TZ)
    return (now() - t) >= timedelta(hours=float(cell.get("recur_hours", 12)))


def pick_next(q):
    for cell in q.get("cells", []):
        status = cell.get("status")
        due = status in ("pending", "failed") or (status == "done" and is_recurring_due(cell))
        if not due:
            continue
        if int(cell.get("attempts", 0)) >= MAX_ATTEMPTS:
            continue
        if not os.path.exists(os.path.join(ROOT, cell.get("script", ""))):
            continue
        return cell
    return None


def arbiter_ask(cell):
    """Ask the shared arbiter before starting; a denial is a wait, not a failure."""
    try:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import line_arbiter as la  # noqa: WPS433
        cls = "cpu_heavy" if cell.get("heavy") else "cpu_light"
        return cls, la.ask("quant_bench", cls, cell)
    except Exception as e:
        return None, {"allow": True, "reason": f"ARBITER_UNAVAILABLE({e})", "cls": None}


def arbiter_release(cls):
    if not cls:
        return
    try:
        import line_arbiter as la  # noqa: F811
        la.release(cls)
    except Exception:
        pass


def run_cell(cell):
    script = os.path.join(ROOT, cell["script"])
    if not os.path.exists(script):
        return {"rc": 127, "reason": "script missing", "seconds": 0.0}

    age = bar_age_days(cell)
    limit = int(cell.get("max_bar_age_days", 6))
    if age is not None and age > limit:
        return {"rc": 0, "skipped": "DATA-BLOCKED",
                "reason": f"newest bar write is {age}d old (limit {limit}d)",
                "seconds": 0.0}

    avail = ram_gb()
    if cell.get("heavy") and avail is not None and avail < RAM_FLOOR_GB:
        return {"rc": 0, "skipped": "RAM-GUARD",
                "reason": f"available {avail:.1f}GB < {RAM_FLOOR_GB}GB",
                "seconds": 0.0}

    cls, grant = arbiter_ask(cell)
    if not grant.get("allow", True):
        ledger_append({"ts": now().isoformat(timespec="seconds"), "cell": cell["id"],
                       "skipped": "WAIT_RESOURCE", "reason": grant.get("reason"),
                       "evidence": grant.get("evidence")})
        return {"rc": 0, "skipped": "WAIT_RESOURCE",
                "reason": f"{grant.get('reason')}: {grant.get('evidence')}", "seconds": 0.0}

    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["OMP_NUM_THREADS"] = str(cell.get("threads", 4))
    env["OPENBLAS_NUM_THREADS"] = str(cell.get("threads", 4))
    env["MKL_NUM_THREADS"] = str(cell.get("threads", 4))
    t0 = time.time()
    try:
        p = silent_run.run([sys.executable, script], cwd=ROOT, env=env,
                           timeout=CELL_TIMEOUT_S)
        secs = round(time.time() - t0, 1)
        tail = (p.stdout or "")[-4000:]
        err = (p.stderr or "")[-2000:]
        return {"rc": p.returncode, "seconds": secs, "stdout_tail": tail,
                "stderr_tail": err}
    except subprocess.TimeoutExpired:
        return {"rc": 124, "seconds": round(time.time() - t0, 1),
                "reason": f"timeout {CELL_TIMEOUT_S}s"}
    finally:
        arbiter_release(cls)


def read_verdict(cell):
    path = cell.get("result")
    if not path:
        return None
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return None
    try:
        with open(full, encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        return None
    v = d.get("verdict")
    if isinstance(v, dict):
        return v
    return v


def ledger_append(row):
    os.makedirs(BENCH, exist_ok=True)
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def acquire_lock():
    os.makedirs(BENCH, exist_ok=True)
    if os.path.exists(LOCK):
        try:
            age = time.time() - os.path.getmtime(LOCK)
        except OSError:
            age = 1e9
        if age < CELL_TIMEOUT_S:      # a live tick owns it
            return False
        os.remove(LOCK)               # stale lock from a killed tick
    with open(LOCK, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
    return True


def release_lock():
    try:
        os.remove(LOCK)
    except OSError:
        pass


def attach_power(cell):
    """After a run, attach the arm's minimum detectable edge (MDE) to the cell.

    A negative is only evidence if the sample could have seen the edge we care
    about. If every arm in the cell sits inside its own noise, the verdict is
    downgraded to UNINFORMATIVE_AT_TARGET -- "not seen" is not "not there".
    """
    script = os.path.join(ROOT, "scripts", "bench_power.py")
    if not os.path.exists(script):
        return None
    try:
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        silent_run.run([sys.executable, script], cwd=ROOT, env=env, timeout=300)
        with open(os.path.join(ROOT, "results", "bench_power.json"), encoding="utf-8") as f:
            p = json.load(f)
    except Exception:
        return None
    rows = [r for r in p.get("rows", []) if r.get("cell") == cell["id"]]
    if not rows:
        return None
    unpowered = [r for r in rows if r.get("reading") == "UNPOWERED_AT_OWN_NOISE"]
    summary = {
        "target_edge_pp": p.get("target_edge_pp"),
        "arms": len(rows),
        "unpowered": len(unpowered),
        "mde_pp_range": [min(r["mde_pp"] for r in rows if r.get("mde_pp") is not None),
                         max(r["mde_pp"] for r in rows if r.get("mde_pp") is not None)]
        if any(r.get("mde_pp") is not None for r in rows) else None,
    }
    if rows and len(unpowered) == len(rows):
        summary["verdict_downgraded"] = "UNINFORMATIVE_AT_TARGET"
    return summary


def run_one(cell_id=None):
    if not acquire_lock():
        print(json.dumps({"ok": True, "skipped": "LOCKED", "reason": "another tick owns the hub"}))
        return 0
    try:
        q = load_queue()
        cell = None
        if cell_id:
            cell = next((c for c in q["cells"] if c["id"] == cell_id), None)
            if cell is None:
                print(json.dumps({"ok": False, "error": f"unknown cell {cell_id}"}))
                return 2
        else:
            cell = pick_next(q)
            if cell is None:
                print(json.dumps({"ok": True, "skipped": "NO_PENDING"}, ensure_ascii=False))
                return 0

        res = run_cell(cell)
        stamp = now().isoformat(timespec="seconds")
        if res.get("skipped"):
            print(json.dumps({"ok": True, "cell": cell["id"], "skipped": res["skipped"],
                              "reason": res.get("reason")}, ensure_ascii=False))
            ledger_append({"ts": stamp, "cell": cell["id"], "skipped": res["skipped"],
                           "reason": res.get("reason")})
            return 0

        verdict = read_verdict(cell)
        ok = res["rc"] == 0
        cell["runs"] = int(cell.get("runs", 0)) + 1
        cell["last_run"] = stamp
        cell["last_seconds"] = res["seconds"]
        if ok:
            cell["status"] = "done"
            cell["verdict"] = verdict
            cell["finished"] = stamp
            cell["attempts"] = 0
            power = attach_power(cell)
            if power:
                cell["power"] = power
            if cell.get("recurring"):
                cell["next_due"] = (now() + timedelta(hours=float(cell.get("recur_hours", 12)))
                                    ).isoformat(timespec="seconds")
        else:
            cell["attempts"] = int(cell.get("attempts", 0)) + 1
            cell["status"] = "failed" if cell["attempts"] < MAX_ATTEMPTS else "blocked"
            cell["last_error"] = (res.get("reason") or res.get("stderr_tail") or "")[-500:]
        save_queue(q)

        state = {"tick": stamp, "cell": cell["id"], "rc": res["rc"],
                 "verdict": verdict, "seconds": res["seconds"]}
        os.makedirs(BENCH, exist_ok=True)
        with open(STATE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=1)
        ledger_append({"ts": stamp, "cell": cell["id"], "rc": res["rc"],
                       "seconds": res["seconds"], "verdict": verdict})
        render_status(q)
        print(json.dumps({"ok": ok, "cell": cell["id"], "rc": res["rc"],
                          "verdict": verdict, "seconds": res["seconds"]},
                         ensure_ascii=False, indent=1))
        if not ok:
            print((res.get("stderr_tail") or res.get("reason") or "")[-1200:], file=sys.stderr)
        return 0 if ok else 1
    finally:
        release_lock()


def render_status(q=None):
    q = q or load_queue()
    lines = ["# 策略试验场状态（bench hub）", "",
             f"updated {q.get('updated')} | 细胞数 {len(q.get('cells', []))}", "",
             "| id | 状态 | 判决 | 最近跑 | 秒 | 问题 |",
             "|---|---|---|---|---|---|"]
    for c in q.get("cells", []):
        v = c.get("verdict")
        if isinstance(v, dict):
            v = ", ".join(f"{k}={x}" for k, x in v.items())[:120]
        lines.append(f"| {c['id']} | {c.get('status')} | {v or '—'} | "
                     f"{c.get('last_run', '—')} | {c.get('last_seconds', '—')} | "
                     f"{c.get('question', '')[:60]} |")
    lines += ["", "## 队列规则", "",
              "- 每 20 分钟一次静默 tick，只跑第一条 pending；队列空则毫秒退出。",
              "- 新格必须先写脚本 + 在 BENCH-QUEUE.json 登记（问题、判据、数据车道、时限）。",
              "- 判负的格子保留脚本与结果，不删；重开要新 id，禁改旧结论。",
              "- 判据在跑之前写死在脚本顶部；改判据要留痕。"]
    with open(STATUS_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def selftest():
    checks = []
    q = load_queue()
    checks.append(("queue has cells", bool(q.get("cells"))))
    checks.append(("ids unique", len({c["id"] for c in q["cells"]}) == len(q["cells"])))
    checks.append(("every cell has a question", all(c.get("question") for c in q["cells"])))
    checks.append(("every cell declares a script", all(c.get("script") for c in q["cells"])))
    missing = [c["id"] for c in q["cells"]
               if c.get("status") in ("pending", "failed")
               and not os.path.exists(os.path.join(ROOT, c.get("script", "")))]
    checks.append(("pending cells have scripts", not missing))
    for name, ok in checks:
        print(("PASS " if ok else "FAIL ") + name)
    if missing:
        print("  missing:", missing)
    return 0 if all(ok for _, ok in checks) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--next", action="store_true")
    ap.add_argument("--cell")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.status:
        render_status()
        print(open(STATUS_MD, encoding="utf-8").read())
        return 0
    if a.cell or a.next:
        return run_one(a.cell)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
