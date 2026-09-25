#!/usr/bin/env python3
"""board_aging.py -- fleet task-board aging report (status counts + claimed age).

T-70 local-coding pilot task 04. Loose-consumption scanner over a board
directory of ticket JSON files: status counts (open/claimed/done/other),
per-ticket claimed age in hours, stalled48h flag (>48h), max age. Stdlib
only, zero network, zero file writes.
"""

import json
import os
import sys
from datetime import datetime

DEFAULT_BOARD_DIR = "fleet/tasks"
USAGE = "usage: board_aging.py [selftest | <board_dir>] (default board_dir=fleet/tasks)"


def _parse_ticket(name, text):
    """Return ticket dict or None when the file face is unusable (parse_fail)."""
    if text.startswith("\ufeff"):  # BOM char surviving a plain-utf-8 read
        text = text[1:]
    try:
        obj = json.loads(text)
    except (ValueError, TypeError):
        return None
    if not isinstance(obj, dict):
        return None
    tid = obj.get("id")
    if not isinstance(tid, str) or not tid:
        tid = name[:-5] if name.endswith(".json") else name
    status = obj.get("status")
    if not isinstance(status, str) or not status:
        status = "unknown"
    claimed_at = obj.get("claimed_at")
    parsed_at = None
    if isinstance(claimed_at, str) and claimed_at:
        try:
            parsed_at = datetime.fromisoformat(claimed_at)
        except ValueError:
            parsed_at = None
        if parsed_at is not None and parsed_at.tzinfo is None:
            parsed_at = parsed_at.astimezone()  # spec 3b: attach local tz
    claimed_by = obj.get("claimed_by")
    if not isinstance(claimed_by, str):
        claimed_by = ""
    machine = claimed_by.split()[0] if claimed_by.split() else ""
    return {
        "id": tid,
        "status": status,
        "claimed_dt": parsed_at,
        "machine": machine,
    }


def digest(raw_items, now):
    """Core: list of (filename, raw_text) + timezone-aware now -> result dict."""
    counts = {"open": 0, "claimed": 0, "done": 0, "other": 0}
    parse_fail = 0
    claimed_rows = []  # (id, age_raw_float_or_None, machine)
    for name, text in raw_items:
        t = _parse_ticket(name, text)
        if t is None:
            parse_fail += 1
            continue
        st = t["status"]
        if st == "open":
            counts["open"] += 1
        elif st == "claimed":
            counts["claimed"] += 1
            age = None
            if t["claimed_dt"] is not None:
                age = (now - t["claimed_dt"]).total_seconds() / 3600.0
            claimed_rows.append((t["id"], age, t["machine"]))
        elif st == "done":
            counts["done"] += 1
        else:
            counts["other"] += 1
    stalled = sum(1 for _, a, _ in claimed_rows if a is not None and a > 48.0)
    valid_ages = [a for _, a, _ in claimed_rows if a is not None and a >= 0.0]
    max_age = max(valid_ages) if valid_ages else -1.0
    # sort: age desc (missing age = -1.0 sentinel for ordering), tie by id asc
    def sort_key(row):
        rid, age, _ = row
        return (-(age if age is not None else -1.0), rid)
    claimed_rows.sort(key=sort_key)
    return {
        "total": counts["open"] + counts["claimed"] + counts["done"] + counts["other"],
        "parse_fail": parse_fail,
        "open": counts["open"],
        "claimed": counts["claimed"],
        "done": counts["done"],
        "other": counts["other"],
        "stalled48h": stalled,
        "max_age_h": max_age,
        "claimed_rows": claimed_rows,
    }


def render(res):
    """ASCII stdout lines: one summary + one row per claimed ticket."""
    lines = [
        "BOARD total={total} parse_fail={pf} open={o} claimed={c} done={d} "
        "other={x} stalled48h={s} max_age_h={m:.1f}".format(
            total=res["total"], pf=res["parse_fail"], o=res["open"],
            c=res["claimed"], d=res["done"], x=res["other"],
            s=res["stalled48h"], m=res["max_age_h"])
    ]
    for rid, age, machine in res["claimed_rows"]:
        a = age if age is not None else -1.0
        lines.append("CLAIMED {i} age_h={a:.1f} by={m}".format(i=rid, a=a, m=machine))
    return lines


def live(board_dir):
    if not os.path.isdir(board_dir):
        print("board dir not found: " + board_dir, file=sys.stderr)
        return 2
    names = sorted(n for n in os.listdir(board_dir) if n.endswith(".json"))
    if not names:
        print("no *.json tickets under " + board_dir, file=sys.stderr)
        return 2
    raw_items = []
    for n in names:
        with open(os.path.join(board_dir, n), encoding="utf-8-sig") as f:
            raw_items.append((n, f.read()))
    res = digest(raw_items, datetime.now().astimezone())
    for line in render(res):
        print(line)
    return 1 if res["stalled48h"] >= 1 else 0


def _selftest():
    """Offline assertions: no repo file reads, no writes (frozen samples)."""
    now = datetime.fromisoformat("2026-09-26T12:00:00+08:00")
    checks = []

    def check(name, cond):
        checks.append((name, bool(cond)))

    # valid 1: mixed statuses incl one parse_fail and unknown -> other
    mixed = [
        ("a.json", '{"id":"A1","status":"open"}'),
        ("b.json", '{"id":"B1","status":"claimed","claimed_at":"2026-09-26T09:30:00+08:00","claimed_by":"bm-a (OS iteration loop, round 1)"}'),
        ("c.json", '{"id":"C1","status":"done"}'),
        ("d.json", '{"id":"D1"}'),  # missing status -> unknown -> other
        ("e.json", 'not-json{'),  # parse_fail
        ("f.json", '[1,2,3]'),  # top-level list -> parse_fail
    ]
    r1 = digest(mixed, now)
    check("mixed counts", r1["total"] == 4 and r1["open"] == 1
          and r1["claimed"] == 1 and r1["done"] == 1 and r1["other"] == 1
          and r1["parse_fail"] == 2)
    # valid 2: exact aging math 2.5h
    check("age 2.5h", abs(r1["claimed_rows"][0][1] - 2.5) < 1e-9)
    # boundary: machine first token
    check("machine token", r1["claimed_rows"][0][2] == "bm-a")
    # boundary: missing claimed_at -> -1.0, not stalled, max ignores
    r2 = digest([("x.json", '{"id":"X1","status":"claimed"}')], now)
    check("missing claimed_at", r2["claimed_rows"][0][1] is None
          and r2["stalled48h"] == 0 and r2["max_age_h"] == -1.0)
    # boundary: stalled 100h -> stalled48h=1, max=100.0
    r3 = digest([("old.json", json.dumps({
        "id": "OLD1", "status": "claimed",
        "claimed_at": "2026-09-22T08:00:00+08:00",
        "claimed_by": "bm-c"})), (
        "tie1.json", json.dumps({
            "id": "T1", "status": "claimed",
            "claimed_at": "2026-09-26T07:00:00+08:00",
            "claimed_by": "bm-b"})), (
        "tie2.json", json.dumps({
            "id": "T0", "status": "claimed",
            "claimed_at": "2026-09-26T07:00:00+08:00",
            "claimed_by": "bm-b"}))], now)
    check("stalled 100h", r3["stalled48h"] == 1 and abs(r3["max_age_h"] - 100.0) < 1e-9)
    # boundary: sort oldest first, tie by id asc
    order = [row[0] for row in r3["claimed_rows"]]
    check("sort order", order == ["OLD1", "T0", "T1"])
    # boundary: unknown keys ignored (loose face)
    r4 = digest([("u.json", '{"id":"U1","status":"claimed","claimed_at":"2026-09-26T11:00:00+08:00","claimed_by":"bm-a zz","extra_key":[1,2],"n":5}')], now)
    check("unknown keys ignored", r4["claimed"] == 1 and abs(r4["claimed_rows"][0][1] - 1.0) < 1e-9)
    # boundary: BOM-tolerant utf-8-sig face (BOM char present in raw text)
    bom_text = '﻿{"id":"B1","status":"open"}'
    r5 = digest([("bom.json", bom_text)], now)
    check("bom tolerant", r5["open"] == 1 and r5["parse_fail"] == 0)
    # boundary: render line shape (ASCII summary)
    lines = render(r3)
    check("render summary", lines[0].startswith("BOARD total=3 parse_fail=0 open=0 claimed=3 done=0 other=0 stalled48h=1 max_age_h=100.0"))
    check("render rows", lines[1] == "CLAIMED OLD1 age_h=100.0 by=bm-c" and len(lines) == 4)

    failed = [n for n, ok in checks if not ok]
    if failed:
        for n in failed:
            print("selftest FAIL: " + n)
        return 1
    print("selftest: {} assertions ALL PASS".format(len(checks)))
    return 0


def main(argv):
    if len(argv) < 2:
        print(USAGE)
        return 2
    if argv[1] == "selftest":
        return _selftest()
    return live(argv[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
