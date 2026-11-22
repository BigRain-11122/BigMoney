"""Bench cell 0 (recurring): re-validate every finished cell on the newest bars.

Why this cell exists
--------------------
A verdict is a statement about a sample. When new bars land, the sample changes,
and a conclusion that was true on 2026-11-20 is not automatically true on
2026-12-20. Re-running each finished cell on fresh bars is the cheapest form of
continuous science: no new hypotheses, no new faces -- just "does the published
answer still hold".

What it does
------------
For every finished cell in BENCH-QUEUE.json:
  * compare the cell's own `result` file evidence_cutoff with the newest bar its
    lane currently holds;
  * if the lane has newer bars, re-run the cell's script (one at a time);
  * compare the verdict map before and after;
  * a CHANGED verdict is an alarm and is written to the ledger with the old and
    new values. An unchanged verdict is recorded as REVALIDATED.
Cells whose lane has no newer bar are SKIPPED_STALE (nothing to do).

Never: it does not edit the other cells' result files beyond re-running their
scripts (the scripts own their own output), and it does not create new
hypotheses. The verdict comparison is the only thing it writes.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(ROOT, "research", "BENCH-QUEUE.json")
OUT = os.path.join(ROOT, "results", "bench_revalidate.json")
BENCH = os.path.join(ROOT, "results", "bench")
TZ = timezone(timedelta(hours=8))
LANES = {
    "futures": os.path.join(ROOT, "data", "futures_daily"),
    "index": os.path.join(ROOT, "data", "index_daily"),
    "etf": os.path.join(ROOT, "data", "daily"),
    "cb": os.path.join(ROOT, "data", "cb_daily"),
    "astock": os.path.join(ROOT, "data", "astock_daily", "per"),
}
TIMEOUT = 1800


def now():
    return datetime.now(TZ)


def bar_date(lane):
    d = LANES.get(lane)
    if not d or not os.path.isdir(d):
        return None
    best = None
    for f in os.listdir(d):
        if not f.endswith(".csv"):
            continue
        p = os.path.join(d, f)
        try:
            with open(p, "rb") as fh:
                fh.seek(0, os.SEEK_END)
                size = fh.tell()
                fh.seek(max(0, size - 400))
                tail = fh.read().decode("utf-8", "ignore").strip().splitlines()
        except OSError:
            continue
        for line in reversed(tail):
            head = line.split(",")[0].strip()
            if len(head) >= 8 and head[:4].isdigit():
                best = head[:10] if best is None else max(best, head[:10])
                break
    return best


def verdict_of_result(path):
    p = os.path.join(ROOT, path)
    if not os.path.exists(p):
        return None
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        return None
    return d.get("verdict")


def main():
    q = json.load(open(QUEUE, encoding="utf-8"))
    reports = []
    for cell in q.get("cells", []):
        if cell.get("status") != "done" or not cell.get("result"):
            continue
        if cell.get("id") == "revalidate" or cell.get("revalidate") is False:
            continue
        lane = cell.get("lane")
        newest = bar_date(lane) if lane else None
        p = os.path.join(ROOT, cell["result"])
        if not os.path.exists(p):
            reports.append({"cell": cell["id"], "state": "RESULT_MISSING"})
            continue
        try:
            res = json.load(open(p, encoding="utf-8"))
        except Exception as e:
            reports.append({"cell": cell["id"], "state": "RESULT_UNREADABLE", "error": str(e)})
            continue
        cutoff = str(res.get("evidence_cutoff") or "")
        if not newest:
            reports.append({"cell": cell["id"], "state": "LANE_UNREADABLE", "lane": lane})
            continue
        if cutoff and newest <= cutoff:
            reports.append({"cell": cell["id"], "state": "SKIPPED_STALE",
                            "cutoff": cutoff, "newest": newest})
            continue

        before = res.get("verdict")
        script = os.path.join(ROOT, cell["script"])
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        env["OMP_NUM_THREADS"] = str(cell.get("threads", 4))
        try:
            r = subprocess.run([sys.executable, script], cwd=ROOT, env=env,
                               capture_output=True, text=True, timeout=TIMEOUT)
            rc = r.returncode
        except subprocess.TimeoutExpired:
            reports.append({"cell": cell["id"], "state": "TIMEOUT"})
            continue
        after = verdict_of_result(cell["result"])
        if rc != 0:
            reports.append({"cell": cell["id"], "state": "SCRIPT_FAILED", "rc": rc,
                            "stderr": (r.stderr or "")[-400:]})
            continue
        changed = before != after
        reports.append({
            "cell": cell["id"],
            "state": "VERDICT_CHANGED" if changed else "REVALIDATED",
            "cutoff_before": cutoff, "newest_bar": newest,
            "verdict_before": before, "verdict_after": after,
        })

    changed = [x for x in reports if x["state"] == "VERDICT_CHANGED"]
    payload = {
        "cell": "revalidate",
        "generated": now().isoformat(timespec="seconds"),
        "evidence_cutoff": max([x.get("newest_bar", "") for x in reports], default=""),
        "n_checked": len(reports),
        "n_changed": len(changed),
        "verdict": "ALARM_VERDICT_CHANGED" if changed else "ALL_HOLD",
        "reports": reports,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT + ".tmp", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(OUT + ".tmp", OUT)

    led = os.path.join(BENCH, "LEDGER.jsonl")
    os.makedirs(BENCH, exist_ok=True)
    with open(led, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": payload["generated"], "cell": "revalidate",
                            "verdict": payload["verdict"], "changed": changed},
                           ensure_ascii=False) + "\n")

    print(json.dumps({"ok": True, "verdict": payload["verdict"],
                      "checked": len(reports), "changed": len(changed),
                      "states": sorted({x["state"] for x in reports})},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
