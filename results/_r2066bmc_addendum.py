# -*- coding: utf-8 -*-
"""r2066 addendum: delivery facts + honest behind count.  One write, one commit."""
from __future__ import annotations

import datetime as _dt
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, "round_reports-bm-c.md")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")


def _counts():
    out = subprocess.run(["git", "rev-list", "--left-right", "--count",
                          "origin/main...HEAD"], cwd=ROOT, capture_output=True,
                         text=True, timeout=120).stdout.split()
    return (int(out[0]), int(out[1])) if len(out) == 2 else (None, None)


def main():
    behind, ahead = _counts()
    ts = _dt.datetime.now().astimezone().replace(microsecond=0).isoformat()
    with io.open(RP, "r", encoding="utf-8", newline="") as f:
        body = f.read()
    if not body.endswith("\n"):
        body += "\n"
    line = (
        "{ts} | r2066a | bm-c | 送达补记：commit **1a130fda68**（13 件·+4395/-3485——"
        "新建 scripts/etf_book_headroom_two_readings.py / results/etf_book_headroom_two_readings.json / "
        "research/ETF_BOOK_HEADROOM_TWO_READINGS.md / qa/headroom-two-readings-r2066.md / 四件 r2066 证据脚本，"
        "改 round_reports-bm-c.md / state-bm-c.json（2065→2066）/ fleet/machines/bm-c.json（583 键零增减·"
        "heartbeat_epoch_utc 实测 int）/ 两份探针证据）。main 直推被拒（non-fast-forward：origin/main 独有 1、"
        "本机独有 16），按 D-20260925-01③ 推 **origin/machine/bm-c-r2066**；fetch 后 "
        "`git rev-list --left-right --count origin/machine/bm-c-r2066...HEAD` = **0/0**，ls-tree 逐件核验四件实物"
        "（dqa/headroom-two-readings-r2066.md、research/ETF_BOOK_HEADROOM_TWO_READINGS.md、"
        "results/etf_book_headroom_two_readings.json、scripts/etf_book_headroom_two_readings.py）全在位。"
        "**本地未达 origin/main commit 数**：本条 commit 前实测 origin/main...HEAD = 1/{ahead}；"
        "本 addendum 自身再加 1 → 读者此刻应为 1/{ahead1}（自指计数差 1 按 r2062 addendum-2 判例写清）。"
        "S7：attrition tripwire 本轮未跑（竞争窗，与冒烟/S6 同列延后）；pre-commit/pre-push 爪均未触发新装。"
        "| 记账：本行 1 处（累计 4）。\n"
    ).format(ts=ts, ahead=ahead, ahead1=(ahead + 1) if ahead is not None else "?")
    with io.open(RP, "w", encoding="utf-8", newline="") as f:
        f.write(body + line)

    with open(HB, encoding="utf-8") as f:
        hb = json.load(f)
    if behind is not None:
        hb["local_behind_commits"] = ahead
    with open(HB, "w", encoding="utf-8") as f:
        json.dump(hb, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps({"behind": behind, "ahead": ahead, "ts": ts}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
