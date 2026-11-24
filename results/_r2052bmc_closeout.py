#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r2052 bm-c closeout: report row + state + heartbeat (single writer, no shared-face edits)."""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUND = 2052
NOW = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))

ROW = (
    "| 2026-11-24 19:3x | 2052 | **PRODUCT（产品优先律·watermark=green (red=false)·孤儿面=0）**："
    "把「印出来的收益」拆成 accrual + 价格水平两半，再用**截尾口径**证伪价格水平那一半——"
    "11 只货币 ETF 的 2.5-11.4pp/yr 价格水平在两侧各截 10% 后塌到 |0.0-0.33|pp，"
    "说明 r2050 印的「溢价」主体不是价格路径，而是复权把重置 bar 记零后**未修的回弹 bar**；"
    "反过来 511010/511880/511360 三只真 accrual（水平 0.01/0.09/0.38pp），"
    "可转债 ETF 的 23.9/51.4pp 是真实价格路径（截尾 13.6/31.8pp 留得住）"
    " | scripts/money_accrual_level_decomposition.py（selftest **25 腿全过**·--check **rc0 CHECK OK 16 行**）+ "
    "results/money_accrual_level_decomposition.json + research/MONEY_ACCRUAL_LEVEL_DECOMPOSITION.md + "
    "负控 results/_r2052bmc_accrual_negative.py（**10 腿全过**：纯 accrual 不被误判为假数字 / "
    "跳变串必被判假 / 多 bar 水平必须留得住 / 改一行必 rc1 且不得借 STALE 一词 / 未改必 rc0）；"
    "S6 链 r2049 在飞（pid 74392 跑 etf_book_width_return），本轮按 r1907 只落新增文件面、不重跑链、不改共享面"
    " | (a) r2049 链收口后跑全量冒烟；(b) 把「截尾水平」接进货币读器口径并重算 4 个依赖面（≤48h）；"
    "(c) 511930/511920 残余 σ 的形状（慢回复）单独一面 |\n"
)


def main() -> int:
    # 1. report row (append-only, bm-c's own file)
    p = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
    with io.open(p, "r", encoding="utf-8", newline="") as fh:
        text = fh.read()
    if "| 2026-11-24 19:3x | 2052 |" not in text:
        if not text.endswith("\n"):
            text += "\n"
        text += "\n" + ROW
        with io.open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        print("report row appended")
    else:
        print("report row already present")

    # 2. state (indent=2 per r2043 self-catch)
    sp = os.path.join(ROOT, "state-bm-c.json")
    with io.open(sp, "r", encoding="utf-8") as fh:
        st = json.load(fh)
    st["round_no"] = ROUND
    st["round_no_note"] = "r2052 收口（state 上轮停在 2050，2050/2051 两轮提交已上链但报告行缺失，本轮补齐 r2052 行）"
    st["当前活"] = ("把一只货币 ETF 印出来的收益拆成 accrual 与价格水平两半，并用截尾口径判定价格水平那半"
                  "是真路径还是复权规则印出来的假数字")
    st["当前活_en"] = ("r2052: split the printed return into accrual + price level, then use a trimmed "
                       "average to decide whether the level part is a path or a reset artifact")
    st["最近实物"] = ("scripts/money_accrual_level_decomposition.py + results/money_accrual_level_decomposition.json + "
                  "research/MONEY_ACCRUAL_LEVEL_DECOMPOSITION.md（selftest 25/25 · check rc0 · 负控 10/10）")
    st["最新判词"] = "THE_PRINTED_RETURN_IS_MOSTLY_PRICE | LEVEL_PART_IS_A_RESET_ARTIFACT | PREMIUMS_BLEED_BACK"
    st["下轮指针"] = ("(a) r2049 链收口后跑全量冒烟；(b) 把截尾水平接进货币读器口径并重算 4 个依赖面（≤48h）；"
                  "(c) 511930/511920 残余 σ 的慢回复形状单独一面")
    st["下个里程碑"] = "(a) 链收口 + 全量冒烟（≤48h）；(b) 截尾口径进货币读器（≤48h）"
    st["孤儿面"] = "0"
    st["孤儿面_note"] = "round-zero orphan_face_probe: orphans 0 (py_faces 7, resident_servers 1 = ComfyUI idle)"
    st["watermark_verdict"] = "green (red=false; lane healthy)"
    st["竞争_r2052"] = ("repo_write_contention rc=0 CLEAN（fewer than two codely hosts alive）；"
                     "但 S6 链 r2049 仍在飞（pid 74392 -> etf_book_width_return），故本轮只落新增文件面")
    st["未验证_r2052"] = ("①截尾口径只回答「这个数字是不是少数 bar 印的」，不是收益估计；"
                       "②accrual 六年一个数，政策利率变化与溢价同形，只有回归标签能分开；"
                       "③S6 链与全量冒烟未在本轮跑（链在飞），禁读成已全绿")
    st["记账_r2052"] = "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：把「截尾」做成可复核的证伪尺属证据与载体）"
    st["通过_r2052"] = "orders 116 文件 / 归一回执 329 / 未回执 0；decisions.md 未变零动作；smoke 本轮被 r2049 链在飞阻断（20 红全属面代差族）"
    with io.open(sp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("state updated round=%d" % ROUND)

    # 3. heartbeat (indent=1; epoch must be an int; clock_read ISO with T)
    hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    with io.open(hp, "r", encoding="utf-8") as fh:
        hb = json.load(fh)
    clock = NOW.isoformat(timespec="seconds")
    hb["machine_id"] = "bm-c"
    hb["last_seen"] = clock
    hb["ts"] = clock
    hb["clock_read"] = clock
    hb["heartbeat_epoch_utc"] = int(NOW.timestamp())
    hb["round_no"] = ROUND
    hb["last_round_no"] = ROUND
    hb["round"] = ROUND
    hb["current_task"] = ("r2052 · accrual 与价格水平的分解：11 只货币 ETF 的价格水平在截尾口径下塌到 "
                          "|0.0-0.33|pp，说明 r2050 的「溢价」主体是复权回弹 bar")
    hb["did"] = "new-file-only landing: script + results + page + negative control + report row + this heartbeat"
    hb["verdict"] = "healthy"
    hb["孤儿面"] = "0"
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    hb["chain_in_flight"] = "Tools/s6_chain_bmc.py 2049 (pid 74392 -> etf_book_width_return run) since 16:07; not restarted this round"
    hb["smoke"] = "not run to completion: 20 reds observed, all panel-staleness family (faces priced 2026-11-20, panel now 2026-11-24) while r2049's chain is in flight"
    with io.open(hp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(hb, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("heartbeat updated %s epoch=%d" % (clock, hb["heartbeat_epoch_utc"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
