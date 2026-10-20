"""FUND P2 burn progress face (r1072 bm-b).

Read-only aggregator: turns the two P2 plan faces + on-disk cell outputs into a
single machine-consumable progress record (results/fund_p2_burn_progress.json)
so the burn's state is visible without scraping runner logs.

Zero network, zero engine, zero judgment: done = cell file present on disk;
totals come from PLAN.json judged_cells. No gate verdict is computed here --
finalize stays the only place that judges.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(HERE, "results")
BATCHES = {
    "FUND-VALUE-P2": os.path.join(RES, "fund_value_p2"),
    "FUND-QUALITY-P2": os.path.join(RES, "fund_quality_p2"),
}
CN = timezone(timedelta(hours=8))


def load_json(path: str):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def cell_ids(plan: dict) -> list[str]:
    ids: list[str] = []
    for key in ("judged_cells", "judged_strategy_cells"):
        raw = plan.get(key)
        if not isinstance(raw, (list, tuple)):
            continue
        for item in raw:
            cid = item if isinstance(item, str) else (item.get("cell_id") or item.get("cell") or item.get("id"))
            if cid and cid not in ids:
                ids.append(cid)
    return ids


def batch_progress(name: str, path: str) -> dict:
    plan_path = os.path.join(path, "PLAN.json")
    out: dict = {"batch": name, "plan": os.path.relpath(plan_path, HERE).replace("\\", "/")}
    if not os.path.exists(plan_path):
        out.update({"status": "no_plan", "done": 0, "total": 0})
        return out
    plan = load_json(plan_path)
    ids = cell_ids(plan)
    cells_dir = os.path.join(path, "cells")
    present = set()
    if os.path.isdir(cells_dir):
        for fn in os.listdir(cells_dir):
            if fn.lower().endswith(".json"):
                present.add(os.path.splitext(fn)[0])
    stem = {i.replace("/", "-") for i in ids}
    done = [i for i in ids if i in present or i.replace("/", "-") in present]
    extra = sorted(p for p in present if p not in stem)
    runner = os.path.join(path, "runner.log")
    fresh = None
    if os.path.exists(runner):
        fresh = datetime.fromtimestamp(os.path.getmtime(runner), CN).isoformat(timespec="seconds")
    out.update(
        {
            "status": "complete" if ids and len(done) == len(ids) else "running",
            "done": len(done),
            "total": len(ids),
            "pct": round(100.0 * len(done) / len(ids), 1) if ids else 0.0,
            "missing": [i for i in ids if i not in done][:20],
            "extra_cell_files": extra[:20],
            "runner_log_mtime": fresh,
        }
    )
    return out


def build() -> dict:
    rows = []
    t_done = t_total = 0
    for name, path in BATCHES.items():
        row = batch_progress(name, path)
        t_done += int(row.get("done") or 0)
        t_total += int(row.get("total") or 0)
        rows.append(row)
    return {
        "generated": datetime.now(CN).isoformat(timespec="seconds"),
        "evidence_cutoff": datetime.now(CN).strftime("%Y-%m-%d"),
        "machine": "bm-b",
        "batches": rows,
        "total_done": t_done,
        "total_cells": t_total,
        "pct": round(100.0 * t_done / t_total, 1) if t_total else 0.0,
        "note": "read-only progress face; judgment belongs to finalize alone",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(RES, "fund_p2_burn_progress.json"))
    args = ap.parse_args()
    face = build()
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(json.dumps({k: face[k] for k in ("total_done", "total_cells", "pct")}, ensure_ascii=False))
    for row in face["batches"]:
        print(f"  {row['batch']}: {row.get('done')}/{row.get('total')} {row.get('status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())