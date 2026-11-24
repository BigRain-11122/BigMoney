"""Refill the bench queue from the pre-registered work bank.

Why
---
An empty queue stops the machine, and "no pending cells" was being reported as
legitimate idle. It is not: the bank already holds questions whose design,
criteria and detectable-effect check were written before any number was read.
Refill materialises the next one as a config + a queue cell; the generic runner
then executes it like any other cell.

Guards
------
* Only items marked `open` are taken; a taken item becomes `queued` with a stamp,
  so the same question is never run twice by accident.
* At most `--limit` items per call (default 1) and at most MAX_PER_DAY cells per
  calendar day, so a bug cannot flood the queue with work.
* Nothing is invented here: if the bank is empty, refill reports EMPTY and the
  hub goes idle honestly instead of manufacturing a filler cell.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, "research", "WORK-BANK.json")
QUEUE = os.path.join(ROOT, "research", "BENCH-QUEUE.json")
CELLS = os.path.join(ROOT, "research", "cells")
STATE = os.path.join(ROOT, "results", "bench", "REFILL-STATE.json")
TZ = timezone(timedelta(hours=8))
MAX_PER_DAY = 48


def now():
    return datetime.now(TZ)


def read_json(p, default=None):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def write_json(p, payload):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, p)


def refill(limit=1):
    bank = read_json(BANK) or {}
    items = bank.get("items") or []
    state = read_json(STATE) or {"date": now().date().isoformat(), "taken": 0}
    if state.get("date") != now().date().isoformat():
        state = {"date": now().date().isoformat(), "taken": 0}
    if state["taken"] >= MAX_PER_DAY:
        return {"ok": False, "state": "DAILY_CAP", "taken": state["taken"]}

    open_items = [i for i in items if i.get("status") == "open"]
    if not open_items:
        return {"ok": False, "state": "EMPTY", "taken": state["taken"]}

    queue = read_json(QUEUE) or {"cells": []}
    existing = {c["id"] for c in queue["cells"]}
    made = []
    for item in open_items[:max(1, limit)]:
        if item["id"] in existing:
            item["status"] = "queued"
            continue
        cfg = {k: v for k, v in item.items()
               if k not in ("status", "decides", "question")}
        os.makedirs(CELLS, exist_ok=True)
        cfg_path = os.path.join(CELLS, item["id"] + ".json")
        write_json(cfg_path, cfg)
        if item.get("script"):
            script = item["script"]
            args = list(item.get("args") or [])
            result = item.get("result") or f"results/{item['id']}.json"
            page = item.get("page") or f"research/{item['id'].upper()}.md"
        else:
            script = "scripts/bench_generic.py"
            args = ["--config", os.path.relpath(cfg_path, ROOT).replace("\\", "/")]
            result = f"results/bench_{item['id']}.json"
            page = f"research/BENCH-{item['id'].upper()}.md"
        queue["cells"].append({
            "id": item["id"],
            "title": item["id"],
            "question": item.get("question"),
            "script": script,
            "args": args,
            "result": result,
            "page": page,
            "lane": item.get("lane", "futures"),
            "max_bar_age_days": 8,
            "threads": item.get("threads", 3),
            "status": "pending",
            "attempts": 0,
            "recurring": bool(item.get("recurring", False)),
            "recur_hours": item.get("recur_hours", 24),
            "decides": item.get("decides"),
            "target_edge_pp": item.get("target_edge_pp"),
        })
        item["status"] = "queued"
        item["queued_at"] = now().isoformat(timespec="seconds")
        made.append(item["id"])

    write_json(QUEUE, queue)
    write_json(BANK, bank)
    state["taken"] += len(made)
    write_json(STATE, state)
    return {"ok": True, "state": "REFILLED", "made": made, "taken_today": state["taken"]}


def status():
    bank = read_json(BANK) or {}
    items = bank.get("items") or []
    counts = {}
    for i in items:
        counts[i.get("status", "?")] = counts.get(i.get("status", "?"), 0) + 1
    return {"items": len(items), "by_status": counts,
            "open": [i["id"] for i in items if i.get("status") == "open"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=1)
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()
    if a.status:
        print(json.dumps(status(), ensure_ascii=False, indent=1))
        return 0
    r = refill(a.limit)
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0 if r.get("ok") else 0


if __name__ == "__main__":
    sys.exit(main())
