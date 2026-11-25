# -*- coding: utf-8 -*-
"""Append the r2103 delivery self-proof to the round reports (idempotent)."""
from __future__ import annotations

import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = [os.path.join(ROOT, "round_reports-bm-c.md"),
           os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")]
TAG = "| r2103-delivered |"

LINE = (
    "2026-11-25T22:4x+08:00 | r2103-delivered | bm-c | 送达补记：commit "
    "**e67a46eb39** 已直推 origin/main（90e3b175ea..e67a46eb39，非 FF 未发生）；"
    "fetch 后 `git rev-list --left-right --count origin/main...HEAD` = **0/0**；"
    "`git ls-tree -r --name-only origin/main` 核验 **6/6** 件在位"
    "（scripts/policy_trigger_audit.py、results/policy_trigger_audit.json、"
    "research/POLICY_TRIGGER_AUDIT.md、qa/policy-trigger-audit-r2103.md、"
    "results/_r2103bmc_trigger_audit_negative.py、results/_r2103bmc_round_report.py）"
    "→ **本地未达 origin commit 数=0**。"
    "本窗按竞争窗纪律未动 state/心跳两面（对端 21:5x 仍持有，r1907 同树多宿主律），"
    "round_no 与心跳由下一个拿到独占窗的执行体推进；本轮记账=轮报告 2 处（正文+本行）。"
)


def main():
    wrote = []
    for path in TARGETS:
        if not os.path.exists(path):
            continue
        text = io.open(path, "r", encoding="utf-8").read()
        if TAG in text:
            print("SKIP already tagged: %s" % os.path.relpath(path, ROOT))
            continue
        with io.open(path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(("\n" if not text.endswith("\n") else "") + LINE + "\n")
        wrote.append(os.path.relpath(path, ROOT))
    print("appended: %s" % (", ".join(wrote) if wrote else "nothing"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
