"""Single machine-derived producer of the round's watermark red card.

Why this exists: results/watermark_red.json was written by a fresh ad-hoc
closeout script in every window (`_rNNNbmc_closeout.py`, one per round, kept
in scratch/tmp), so the face that decides whether a round opens with a P0
escalation was itself re-implemented by hand each time -- and every copy
inherited the same defect.

The defect (r1361 bm-c): a pool row that declares `blocked_by` but still
carries `status="ready"` was counted as "work waiting for you". Autofill cannot
launch it (verdict ghost_ready_no_shards: no shards, no cmd) and no round can
ever consume it, so the card stayed red on a phantom row for as long as the row
stayed blocked -- a permanently red gate, which is exactly the class that gets
"fixed" by relaxing the assertion (r1135 trap).

Law: a row that declares itself blocked is not work, it is a named debt. It is
reported on its own line (`pool_blocked_ids` + `blocked_reasons`) and never
counted as a work candidate.

Usage:
    python Tools/watermark_red.py write     # derive + write results/watermark_red.json
    python Tools/watermark_red.py show      # derive + print, no write
    python Tools/watermark_red.py selftest  # offline legs, no repo writes

Every number comes from a file on disk: the pool face, the board tickets, the
bandit faces and the watermark series. Nothing here judges science.
"""
import json
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import py_watermark as wm  # noqa: E402  (shared constants: never a second copy)

OUT = os.path.join(ROOT, "results", "watermark_red.json")
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
TASKS = os.path.join(ROOT, "fleet", "tasks")
LANE_POOL = "pool-batch-runnable-idle-low-cpu"


def _lane_owner_ok(entry, machine_id):
    lane = entry.get("lane_owner")
    return lane in (None, "", "ANY", "any") or lane == machine_id


def derive(pool_path=POOL, series_path=None, machine_id=None, tasks_dir=TASKS):
    """Return the red card as a dict. Pure function of files (no network)."""
    machine_id = machine_id or wm._machine_id()
    claimable, blocked = [], []
    try:
        with open(pool_path, encoding="utf-8") as f:
            entries = json.load(f).get("entries", [])
    except Exception:
        entries = []
    for e in entries:
        if not isinstance(e, dict) or e.get("status") != "ready":
            continue
        if not _lane_owner_ok(e, machine_id):
            continue
        if e.get("blocked_by"):
            blocked.append({"id": e.get("id") or "?",
                            "blocked_by": str(e.get("blocked_by"))[:160],
                            "blocked_at": e.get("blocked_at")})
        else:
            claimable.append(e)

    claimable.sort(key=lambda e: (e.get("priority") or 99, e.get("id") or ""))
    pool_ids = [e.get("id") or "?" for e in claimable]

    ticket_ids = wm._scan_tickets(tasks_dir) if tasks_dir else []
    board_inflight = wm._board_inflight(tasks_dir) if tasks_dir else []
    try:
        bandit_open = wm._bandit_open()
    except Exception:
        bandit_open = 0
    try:
        lock_lanes = wm._refresh_locks_alive()
    except Exception:
        lock_lanes = []

    series_path = series_path or os.path.join(ROOT, "results", "watermark.jsonl")
    tail, verdict, window = [], "insufficient_history", {}
    try:
        rows = []
        with open(series_path, encoding="utf-8") as f:
            for ln in f.read().splitlines():
                try:
                    rows.append(json.loads(ln))
                except Exception:
                    pass
        tail = [r.get("py_cpu_pct") for r in rows[-3:]]
        if rows:
            verdict = rows[-1].get("verdict") or verdict
            window = rows[-1].get("window") or {}
    except Exception:
        pass

    blockers = (len(pool_ids) + len(ticket_ids) + len(board_inflight)
                + int(bool(lock_lanes)) + int(bandit_open > 0))
    # py-low on the sustained window when one exists, else on the newest sample
    # (the card must not go silent just because the window has not filled yet).
    py_low = window.get("max_py_cpu_pct", 0.0) < wm.LOW_PY_LINE if window else (
        (tail[-1] if tail else 0.0) < wm.LOW_PY_LINE)
    red = bool(py_low and blockers > 0)

    if red:
        if pool_ids:
            lane = LANE_POOL
        elif ticket_ids or board_inflight or bandit_open:
            lane = "board-work-idle-low-cpu"
        else:
            lane = "local-batch-idle-low-cpu"
    else:
        lane = None if blockers else "board-clear-and-pool-empty"
        if blockers and not py_low:
            lane = "loaded-ok"

    reasons = []
    if pool_ids:
        reasons.append("{} claimable pool row(s): {}".format(
            len(pool_ids), ", ".join(pool_ids[:5])))
    if blocked:
        reasons.append("{} blocked row(s) excluded as debt: {}".format(
            len(blocked), ", ".join(b["id"] for b in blocked[:5])))
    if not blockers:
        reasons.append("no claimable pool row, no open/in-flight ticket, "
                       "no bandit pointer, no local batch")

    return {
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "machine": machine_id,
        "red": red,
        "lane": lane,
        "reason": "; ".join(reasons),
        "order_ref": "O-20260924-1626 R1/R2/R3",
        "py_series_tail": tail,
        "py_low": bool(py_low),
        "window": window,
        "verdict_src": verdict,
        "next_pick": pool_ids[0] if pool_ids else None,
        "pool_ready_ids": pool_ids,
        "pool_blocked_ids": [b["id"] for b in blocked],
        "blocked_reasons": {b["id"]: b["blocked_by"] for b in blocked},
        "board_inflight_ids": board_inflight,
        "open_ticket_ids": ticket_ids,
        "work_cand_buckets": {
            "pool_batch": len(pool_ids),
            "pool_blocked": len(blocked),
            "board_open": len(ticket_ids),
            "board_inflight": len(board_inflight),
            "local_batch": int(bool(lock_lanes)),
            "bandit_open": int(bandit_open),
        },
        "producer": "Tools/watermark_red.py",
    }


def cmd_write():
    card = derive()
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(card, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    print(json.dumps(card, ensure_ascii=False))
    return 0


def cmd_show():
    print(json.dumps(derive(), ensure_ascii=False, indent=1))
    return 0


def selftest():
    import shutil
    import tempfile

    ok = [True]

    def check(name, cond):
        if not cond:
            ok[0] = False
            print("FAIL:", name)
        else:
            print("PASS:", name)

    tmpd = tempfile.mkdtemp(prefix="wmred_")

    def pool(rows):
        p = os.path.join(tmpd, "pool.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"entries": rows}, f)
        return p

    _n = [0]

    def series(pys, verdict="py_low_with_work_cands", window=None):
        # one file per fixture: reusing a single name lets a later fixture
        # silently shadow an earlier one, which reads as "the reader disagrees"
        # when it is only the fixture aliasing itself (r1261 family).
        _n[0] += 1
        p = os.path.join(tmpd, "s{}.jsonl".format(_n[0]))
        with open(p, "w", encoding="utf-8") as f:
            for i, py in enumerate(pys):
                rec = {"epoch": 1000 + i, "py_cpu_pct": py, "verdict": verdict}
                if window is not None:
                    rec["window"] = window
                f.write(json.dumps(rec) + "\n")
        return p

    low = series([0.1, 0.2, 0.1])
    high = series([95.0, 92.0], verdict="loaded_ok")
    idle_win = {"n": 5, "span_min": 16.0, "max_py_cpu_pct": 0.4,
                "avg_py_cpu_pct": 0.2}

    # 1) the bug this tool exists for: a ready-but-blocked row is not work
    p1 = pool([{"id": "P-BLOCKED", "status": "ready",
                "blocked_by": "runner-import-missing:x"}])
    c = derive(p1, low, "bm-c", tasks_dir=None)
    check("ready-but-blocked row is not a work candidate",
          c["pool_ready_ids"] == [] and c["red"] is False)
    check("ready-but-blocked row is named as debt",
          c["pool_blocked_ids"] == ["P-BLOCKED"]
          and "runner-import-missing" in c["blocked_reasons"]["P-BLOCKED"])

    # 2) a genuinely claimable row still goes red when py is low
    p2 = pool([{"id": "P-ANY", "status": "ready", "priority": 1},
               {"id": "P-BLOCKED", "status": "ready", "blocked_by": "y"}])
    c = derive(p2, low, "bm-c", tasks_dir=None)
    check("claimable row keeps the red alive",
          c["red"] is True and c["lane"] == LANE_POOL
          and c["next_pick"] == "P-ANY"
          and c["pool_blocked_ids"] == ["P-BLOCKED"])

    # 3) claimable row + high py is not a red (machine is working)
    c = derive(p2, high, "bm-c", tasks_dir=None)
    check("high py suppresses the red", c["red"] is False)

    # 4) sustained-window verdict wins over a single newest sample
    c = derive(p2, series([0.2], window=idle_win), "bm-c", tasks_dir=None)
    check("sustained window drives the py-low read",
          c["py_low"] is True and c["red"] is True)
    busy = {"n": 5, "span_min": 16.0, "max_py_cpu_pct": 88.0}
    c = derive(p2, series([0.2], window=busy), "bm-c", tasks_dir=None)
    check("a busy window is not overridden by the last sample",
          c["py_low"] is False and c["red"] is False)

    # 5) lane ownership: another machine's row is neither work nor debt
    p5 = pool([{"id": "P-OTHER", "status": "ready", "lane_owner": "bm-a"}])
    c = derive(p5, low, "bm-c", tasks_dir=None)
    check("another machine's row is not claimable here",
          c["pool_ready_ids"] == [] and c["pool_blocked_ids"] == [])

    # 6) done rows never count
    p6 = pool([{"id": "P-DONE", "status": "done"}])
    c = derive(p6, low, "bm-c", tasks_dir=None)
    check("done rows never count as work", c["red"] is False)

    # 7) missing/corrupt pool is honest, not a crash
    c = derive(os.path.join(tmpd, "nope.json"), low, "bm-c", tasks_dir=None)
    check("missing pool -> empty board, not an exception",
          c["pool_ready_ids"] == [] and c["red"] is False)

    # 8) empty board with a low py is legal idle, named as such
    p8 = pool([])
    c = derive(p8, low, "bm-c", tasks_dir=None)
    check("empty board names the legal idle", c["red"] is False
          and c["lane"] == "board-clear-and-pool-empty")

    # 9) next_pick follows declared priority, not file order
    p9 = pool([{"id": "P-LOW", "status": "ready", "priority": 3},
               {"id": "P-HIGH", "status": "ready", "priority": 1}])
    c = derive(p9, low, "bm-c", tasks_dir=None)
    check("next_pick is the highest priority row", c["next_pick"] == "P-HIGH")

    # 10) Card is JSON-serialisable and self-names its producer
    c = derive(p9, low, "bm-c", tasks_dir=None)
    check("card serialises and names its producer",
          json.loads(json.dumps(c))["producer"] == "Tools/watermark_red.py")

    shutil.rmtree(tmpd, ignore_errors=True)
    print("\nselftest: {} legs, {}".format(
        12, "ALL PASS" if ok[0] else "FAILURES"))
    return 0 if ok[0] else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "show").lower()
    if cmd == "write":
        return cmd_write()
    if cmd == "show":
        return cmd_show()
    if cmd == "selftest":
        return selftest()
    print("usage: python Tools/watermark_red.py [write|show|selftest]",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))