#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""append the r2111 delivery line (fresh read; round_reports-bm-c.md is multi-host)."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "round_reports-bm-c.md")

LINE = (
    "2026-11-26T00:5x+08:00 | r2111-delivered | bm-c | 送达补记：commit **5d42b59dc4** 已直推 origin/main"
    "（6fe6ad539f..5d42b59dc4，非 FF 未发生）；fetch 后 `git rev-list --left-right --count origin/main...HEAD` = **0/0**；"
    "`git ls-tree` 核验 **6/6** 件在位（Tools/page_fmt_guard.py、results/page_fmt_guard.scan.json、"
    "qa/page-fmt-guard-r2111.md、results/_r2111bmc_leak_verify.{py,json}、results/_r2111bmc_round_report.py，`_r[0-9]*` "
    "按忽略规则 `git add -f` 入库），另 round_reports-bm-c.md 一行同批入库 → **本地未达 origin commit 数=0**。"
    "本窗自捕三枚：①正文写的「1 处读不出的旧脚本」是**错的**——`python -m py_compile Tools\\_r820bmc_close.py` 判 "
    "`unterminated string literal (detected at line 130)` rc=1，那是**真编译不了的脚本**（自 e1ee753a8a/r822 进库起从未能跑），"
    "已就地更正 QA 并从「编码问题」改判为独立缺陷；②**`python ... | Select-Object -First 1` 会把 `$LASTEXITCODE` 读成上一条命令的 0**"
    "（r1005「Select -First 截停上游脚本」同坑）——闸门真 rc=3（PAGE_FMT_HAZARDS）被管道吃掉了，去掉管道改 `$o = python ...; $LASTEXITCODE` "
    "才读到真值，**判定 rc 一律不接在 `Select-Object -First` 下游**；③扫描面 2,666 文件/1,194 渲染器/28,939 含 `%` 常量 → 31 字面 `%%` + 5 非法转换，"
    "与提交的面逐项一致（重扫幂等，仅 `generated` 时间戳变）。下轮指针（干净树首件事）：①把 31 处未格式化的 `%%` 改回单个 `%`（全在他人脚本面，"
    "改完重跑 `scan` 期望 literal_double_pct=0）；②把本闸接进 `Tools/s6_chain_bmc.py`（check-only 腿）与 `smoke_test.py`；③顺手修 "
    "`Tools/_r820bmc_close.py:130` 的未闭合串。本轮记账=轮报告 1 处（正文+本行）+ QA 更正 1 处。\n"
)

with io.open(P, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(LINE)
print("appended %d chars; file now %d bytes" % (len(LINE), os.path.getsize(P)))
