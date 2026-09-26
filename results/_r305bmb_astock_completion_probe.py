# -*- coding: utf-8 -*-
"""r305 bm-b: T-87 astock_daily first-pull PASS-COMPLETION probe (new face,
explicitly queued since r301 'next' / r304 'next' pointers: the pass-completion
re-probe after the ETA window 06:40-09:30, distinct from the frozen mid-flight
health probe lineage #18 which stays the in-flight face).

Helpers (pid-alive / last-line / frozen fields) carried verbatim in spirit
from the frozen probe lineage (_r297bmb...->_r305bmb_astock_pass_probe.py);
the verdict face here is completion-oriented:

  lock dead + todo empty + coverage>=universe-quarantined -> pass_complete
  lock dead + todo nonempty                          -> ended_incomplete_todo_left
  lock alive                                          -> in_flight (rate face)

Read-only w.r.t. the pass. Dict-topped JSON (r276 law).
"""
import csv as _csv
import ctypes
import datetime as dt
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PER_DIR = os.path.join(ROOT, "data", "astock_daily", "per")
PROGRESS = os.path.join(ROOT, "data", "astock_daily", "_progress.json")
LOCK = os.path.join(ROOT, "data", "astock_daily", "_refresh.lock")
STATUS = os.path.join(ROOT, "results", "astock_daily_update_status.json")
OUT = os.path.join(ROOT, "results", "_r305bmb_astock_completion_probe.json")

FROZEN_FIELDS = ["date", "open", "high", "low", "close", "volume", "amount",
                 "outstanding_share", "turnover"]
CUTOFF_EXPECTED = "2026-09-24"   # status panel.cutoff (Thu bar; Fri=mkt holiday)
DEADLINE = dt.datetime(2026, 9, 28, 9, 15)   # Mon open: first live fire


def _pid_alive(pid):
    h = ctypes.windll.kernel32.OpenProcess(0x1000, False, int(pid))
    if not h:
        return False
    ctypes.windll.kernel32.CloseHandle(h)
    return True


def _last_line(path):
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - 4096))
        tail = f.read().decode("utf-8", "replace").rstrip("\n").splitlines()
    return tail[-1] if tail else ""


def main():
    now = dt.datetime.now()
    files = sorted(os.listdir(PER_DIR))
    files = [f for f in files if f.endswith(".csv")]
    n_done = len(files)

    status = json.load(io.open(STATUS, encoding="utf-8-sig"))
    panel = status.get("panel") or {}
    universe_n = int(panel.get("universe_n") or 0)
    prog = json.load(io.open(PROGRESS, encoding="utf-8-sig"))
    attempts = prog.get("attempts") or {}
    quarantined = sorted(c for c, n in attempts.items() if n >= 3)
    todo = prog.get("todo")
    todo_n = len(todo) if isinstance(todo, (list, dict)) else todo

    lock = json.load(io.open(LOCK, encoding="utf-8-sig")) if os.path.exists(LOCK) else None
    lock_alive = bool(lock) and _pid_alive(lock.get("pid", 0))

    # tail-date census + header spot-face (first/mid/last 3 samples like #18)
    tail_dates = {}
    header_bad = []
    paths = [os.path.join(PER_DIR, f) for f in files]
    for idx, p in enumerate(paths):
        with io.open(p, encoding="utf-8") as f:
            header = next(_csv.reader(f))
        if header != FROZEN_FIELDS and len(header_bad) < 20:
            header_bad.append(os.path.basename(p))
        if idx in (0, n_done // 2, n_done - 1):
            tdate = _last_line(p).split(",")[0]
            tail_dates[tdate] = tail_dates.get(tdate, 0) + 1
    at_cutoff_probe = sum(
        1 for p in paths if _last_line(p).split(",")[0] == CUTOFF_EXPECTED)

    coverage_ok = n_done >= (universe_n - len(quarantined))
    if lock_alive:
        verdict = "in_flight"
    elif (todo_n in (0, None)) and coverage_ok:
        verdict = "pass_complete"
    else:
        verdict = "ended_incomplete_todo_left"

    out = {
        "ts": now.isoformat(timespec="seconds"),
        "round": "r305",
        "machine": "bm-b",
        "lane": "T-87 astock_daily supply (bm-b)",
        "verdict": verdict,
        "pass_state": {
            "universe_n": universe_n,
            "per_files": n_done,
            "done_pct": round(100 * n_done / universe_n, 1) if universe_n else None,
            "lock": lock,
            "lock_alive": lock_alive,
            "todo_n": todo_n,
            "attempts_n": len(attempts),
            "quarantined": quarantined,
            "quarantined_n": len(quarantined),
        },
        "panel_face": {
            "status_panel_complete": bool(panel.get("complete")),
            "status_panel_cutoff": panel.get("cutoff"),
            "status_panel_per_files": panel.get("per_files"),
        },
        "shape_face": {
            "header_bad": header_bad,
            "header_bad_n_total_capped": len(header_bad),
            "files_at_expected_cutoff": at_cutoff_probe,
            "spot_tail_dates": tail_dates,
        },
        "monday_deadline": DEADLINE.isoformat(timespec="seconds"),
        "note": ("completion re-probe face (new, queued r301/r304 next-"
                 "pointers); mid-flight face stays with frozen probe lineage "
                 "#18 (_r305bmb_astock_pass_probe.py); self-heal law: todo "
                 "remnants re-fetch via file-derived todo on next gate spawn"),
    }
    with io.open(OUT, "w", encoding="utf-8", newline="") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({"ts": out["ts"], "verdict": verdict,
                      "per_files": n_done, "universe": universe_n,
                      "todo_n": todo_n, "quarantined_n": len(quarantined),
                      "lock_alive": lock_alive,
                      "at_cutoff": at_cutoff_probe},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
