"""Supply truth for the research work bank (research/WORK-BANK.json).

Why this exists
---------------
`scripts/bench_refill.py` writes only one edge of the card's lifecycle: it
flips `open` -> `queued` when it takes a card into the bench queue. Nothing
ever writes the outcome back. So the 18 cards that the queue answered on
2026-11-24 still read `queued`, and every reader -- including
`bench_refill.py --status` and `block_board.probe_supply` -- has to guess
whether `queued` means "in flight" or "finished weeks ago".

The two guesses cost differently:
  * read as "in flight"  -> the line looks busy while it has actually run dry
                            (this is what happened: 18 queued, 0 real work left)
  * read as "answered"   -> the supply block stays red for the only honest
                            reason: nobody has authored card #21.

This module does the join and prints the three states a supply decision needs:
answered / in flight / never taken. Read-only: it never writes the bank.

Usage
-----
  python scripts/work_bank_supply_truth.py            # write json + page
  python scripts/work_bank_supply_truth.py --check    # selftest, offline
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, "research", "WORK-BANK.json")
QUEUE = os.path.join(ROOT, "research", "BENCH-QUEUE.json")
OUT_JSON = os.path.join(ROOT, "results", "work_bank_supply_truth.json")
OUT_MD = os.path.join(ROOT, "research", "WORK-BANK-SUPPLY.md")

ANSWERED = "ANSWERED"
IN_FLIGHT = "IN_FLIGHT"
UNTAKEN = "UNTAKEN"
BLOCKED = "BLOCKED"
STRANDED = "STRANDED"

IN_FLIGHT_CELL_STATES = ("pending", "running", "failed")
OPEN_BANK_STATES = ("open",)


def _load(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def classify(item, cell):
    """One card -> one state. The order matters: a done cell always wins,
    because that is the whole point -- a card cannot be 'in flight' once its
    cell has a verdict."""
    if cell is not None:
        st = (cell.get("status") or "").lower()
        if st == "done":
            return ANSWERED, cell.get("verdict")
        if st in IN_FLIGHT_CELL_STATES:
            return IN_FLIGHT, None
        return IN_FLIGHT, None  # unknown cell state: treat as still moving
    status = (item.get("status") or "").lower()
    if status in OPEN_BANK_STATES:
        return UNTAKEN, None
    if status == "blocked":
        return BLOCKED, None
    if status == "queued":
        # taken by refill, but its cell is gone -- not in flight, not answered
        return STRANDED, None
    return STRANDED, None


def build(bank, queue):
    cells = {c.get("id"): c for c in (queue.get("cells") or [])}
    rows = []
    for item in bank.get("items") or []:
        cid = item.get("id")
        cell = cells.get(cid)
        state, verdict = classify(item, cell)
        rows.append({
            "id": cid,
            "bank_status": item.get("status"),
            "cell_status": (cell or {}).get("status"),
            "state": state,
            "verdict": verdict if verdict is not None else (cell or {}).get("verdict"),
            "finished": (cell or {}).get("finished"),
            "result": (cell or {}).get("result"),
            "question": item.get("question") or item.get("title"),
        })

    bank_ids = {i.get("id") for i in bank.get("items") or []}
    off_bank = []
    for cell in queue.get("cells") or []:
        if cell.get("id") in bank_ids:
            continue
        off_bank.append({
            "id": cell.get("id"),
            "cell_status": cell.get("status"),
            "verdict": cell.get("verdict"),
            "finished": cell.get("finished"),
            "result": cell.get("result"),
        })

    counts = {}
    for r in rows:
        counts[r["state"]] = counts.get(r["state"], 0) + 1

    untaken = counts.get(UNTAKEN, 0)
    in_flight = counts.get(IN_FLIGHT, 0)
    finished = [r["finished"] for r in rows + off_bank if r.get("finished")]
    return {
        "schema": "work-bank-supply-truth/v1",
        "evidence_cutoff": max(finished)[:10] if finished else None,
        "generated": None,  # filled by caller
        "bank_items": len(rows),
        "queue_cells": len(cells),
        "counts": counts,
        "supply": {
            # same question the block board asks, but asked with honest words
            "has_work_to_take": untaken + in_flight > 0,
            "untaken": untaken,
            "in_flight": in_flight,
            "answered": counts.get(ANSWERED, 0),
            "read_as_in_flight_if_naive": counts.get(ANSWERED, 0) + counts.get(STRANDED, 0) + in_flight,
        },
        "rows": rows,
        "off_bank": off_bank,
    }


def render(report):
    s = report["supply"]
    c = report["counts"]
    lines = []
    lines.append("generated %s" % report["generated"])
    lines.append("evidence_cutoff %s" % report["evidence_cutoff"])
    lines.append("")
    lines.append("银行 %d 张卡 · 队列 %d 格 · 已答 %d / 在飞 %d / 未取 %d / 数据阻塞 %d / 悬空 %d"
                 % (report["bank_items"], report["queue_cells"], c.get(ANSWERED, 0),
                    c.get(IN_FLIGHT, 0), c.get(UNTAKEN, 0), c.get(BLOCKED, 0), c.get(STRANDED, 0)))
    lines.append("")
    if not s["has_work_to_take"]:
        lines.append("供给判词 = **无题可取**（未取 0 + 在飞 0）。红是真的红，但它的意思不是"
                     "「队列坏了」而是「没人写下第 %d 张卡」。" % (report["bank_items"] + 1))
    else:
        lines.append("供给判词 = 有题可取（未取 %d + 在飞 %d）。" % (s["untaken"], s["in_flight"]))
    lines.append("")
    lines.append("朴素读法会把 %d 张已答卡读成在飞（`queued` 一旦写下就再没人翻面），"
                 "差 %d 张。" % (s["read_as_in_flight_if_naive"], s["read_as_in_flight_if_naive"]))
    lines.append("")
    lines.append("| 卡 | 银行状态 | 格状态 | 判词 | 完成 |")
    lines.append("|---|---|---|---|---|")
    for r in report["rows"]:
        lines.append("| %s | %s | %s | %s | %s |" % (
            r["id"], r["bank_status"], r["cell_status"] or "-",
            (r["verdict"] if isinstance(r["verdict"], str) else json.dumps(r["verdict"], ensure_ascii=False))
            if r["verdict"] is not None else "-",
            (r["finished"] or "-")[:19]))
    lines.append("")
    lines.append("队列里不属于银行的格 %d 个——赚钱线（基差 carry/容量/时点）全在这一侧，"
                 "银行里一张都没有，所以银行答完 18 张也不等于研究面见底。" % len(report["off_bank"]))
    lines.append("")
    lines.append("| 格 | 状态 | 判词 | 完成 |")
    lines.append("|---|---|---|---|")
    for r in report["off_bank"]:
        v = r["verdict"]
        lines.append("| %s | %s | %s | %s |" % (
            r["id"], r["cell_status"],
            (v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)) if v is not None else "-",
            (r["finished"] or "-")[:19]))
    return "\n".join(lines) + "\n"


def _fixtures():
    bank = {"items": [
        {"id": "done_card", "status": "queued"},        # answered but still `queued`
        {"id": "flying", "status": "queued"},           # genuinely in flight
        {"id": "fresh", "status": "open"},              # never taken
        {"id": "blocked", "status": "blocked"},         # data blocked
        {"id": "lost", "status": "queued"},             # taken, cell gone
    ]}
    queue = {"cells": [
        {"id": "done_card", "status": "done", "verdict": "NO_EDGE", "finished": "2026-11-24T21:24:50+08:00"},
        {"id": "flying", "status": "pending"},
        {"id": "outsider", "status": "done", "verdict": "GO", "finished": "2026-11-24T21:43:53+08:00"},
    ]}
    return bank, queue


def selftest():
    bank, queue = _fixtures()
    rep = build(bank, queue)
    rows = {r["id"]: r for r in rep["rows"]}
    checks = []

    checks.append(("a done cell beats the stale `queued` word",
                   rows["done_card"]["state"] == ANSWERED))
    checks.append(("a pending cell is in flight",
                   rows["flying"]["state"] == IN_FLIGHT))
    checks.append(("an `open` card is untaken",
                   rows["fresh"]["state"] == UNTAKEN))
    checks.append(("a blocked card is blocked",
                   rows["blocked"]["state"] == BLOCKED))
    checks.append(("a queued card with no cell is stranded, not in flight",
                   rows["lost"]["state"] == STRANDED))
    checks.append(("answered count is 1, in flight is 1",
                   rep["counts"].get(ANSWERED) == 1 and rep["counts"].get(IN_FLIGHT) == 1))
    checks.append(("naive reader would see 3 in flight (answered+stranded+flying)",
                   rep["supply"]["read_as_in_flight_if_naive"] == 3))
    checks.append(("supply has work because one card is untaken",
                   rep["supply"]["has_work_to_take"] is True))
    checks.append(("cells outside the bank are reported, not silently dropped",
                   [r["id"] for r in rep["off_bank"]] == ["outsider"]))
    checks.append(("evidence_cutoff is the newest finishing date",
                   rep["evidence_cutoff"] == "2026-11-24"))

    # the negative control: take the untaken card away -> supply must flip red,
    # and it must flip red for the honest reason, not because a done card got
    # counted as flight.
    bank2 = {"items": [i for i in bank["items"] if i["id"] != "fresh"]}
    queue2 = {"cells": [c for c in queue["cells"] if c["id"] != "flying"]}
    rep2 = build(bank2, queue2)
    checks.append(("no untaken + nothing pending = no work to take",
                   rep2["supply"]["has_work_to_take"] is False))
    checks.append(("the red is not caused by the answered card",
                   rep2["counts"].get(ANSWERED) == 1))

    bad = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(("PASS " if ok else "FAIL ") + n)
    print("selftest %d/%d" % (len(checks) - len(bad), len(checks)))
    return 0 if not bad else 3


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    if a.check:
        return selftest()

    report = build(_load(BANK), _load(QUEUE))
    import datetime
    report["generated"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(report))

    if not a.quiet:
        s = report["supply"]
        print("bank %d · answered %d · in_flight %d · untaken %d · blocked %d · stranded %d · off_bank %d"
              % (report["bank_items"], s["answered"], s["in_flight"], s["untaken"],
                 report["counts"].get(BLOCKED, 0), report["counts"].get(STRANDED, 0),
                 len(report["off_bank"])))
        print("has_work_to_take=%s (naive reader would see %d in flight)"
              % (s["has_work_to_take"], s["read_as_in_flight_if_naive"]))
        print("-> %s" % os.path.relpath(OUT_JSON, ROOT))
        print("-> %s" % os.path.relpath(OUT_MD, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
