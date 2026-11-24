#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r2053 bm-c closeout: report row + state + heartbeat (single writer, no shared-face edits)."""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUND = 2053
NOW = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))

ROW = (
    "| 2026-11-24 20:4x | 2053 | **PRODUCT（产品优先律·watermark=green (red=false)·孤儿面=0）**："
    "把 r2048 的「多少倍自身 σ」这把尺子反过来量它自己——货币架上 plain σ / robust σ 中位 **5.9 倍**、"
    "最坏 **86.7 倍**（511970：plain 64.32bp vs robust 0.74bp），分子分母是同一批跳点；"
    "再把 621 根极端 bar 按「掉下去之后怎么回来」分类：SNAP（≤3 根）**358** / 恰按 accrual 时钟回补 **6** / "
    "不在时钟上（比 carry 能做的快）**190** / 走完 750 根也没回 **67**；"
    "**6 根 accrual-paced 全部是 511880 的年终份额整并（pace 0.67-1.38）**，"
    "36 只里只有 511360/511880 两只存在真正的 accrual 时钟（其余 34 只中位 bar <0.0133bp，价格自己不会爬）——"
    "所以「慢回复」不是一类现象，而是**只有一个标的拥有的现象**；"
    "另捕上游分类污染：census 的 money 类里 **20 只**是「现金流」权益 ETF（中位日收益 3.8-15.9bp），"
    "名字里的「现金流」被当成「现金」，本面已按 accrual 速度机械剔除并公布名单；"
    "记零规则两端：SNAP 段留下未赚到的反弹最多 **198.9 bp/年**、NEVER 段抹掉永不回来的水平 **373.0 bp/年**（均 511930，≈1-3.7% 面值/年）"
    " | scripts/money_residual_sigma_recovery.py（selftest **21 腿全过**·--check **rc0 CHECK OK 36 行**·"
    "三种红已验：改 σ→CHECK FAILED / 上游行数动→STALE / 窗口动→bars moved）+ "
    "results/money_residual_sigma_recovery.json + research/MONEY_RESIDUAL_SIGMA_RECOVERY.md + "
    "负控 results/_r2053bmc_residual_sigma_negative.py（**18 腿全过**：确定性 / 通胀是算出来的不是写死的 / "
    "权益速度机械可判 / 20bp 地板双向 / 80bp 在 0.5bp 时钟上必须读成 accrual-paced（诚实局限）/ "
    "估计器一换通胀就塌回 1 / 剔除名单口径自洽 / doc 必须印本面判词）；"
    "竞争窗 rc=3（对端 interactive pid 2276 19:54 起在写共享面，19 张面在轮首前被动过、重叠窗 0 张）→ 按 r1907 只落新增文件面"
    " | (a) 全量冒烟 + S6 链收口（≤48h，等竞争窗关闭）；(b) 把「accrual 时钟是否存在」做成货币读器的准入前置（≤48h）；"
    "(c) 上游 money 分类器加「现金流 ≠ 现金」闸（须他机属主或 GM 署名） |\n"
)


def _max_round(text: str) -> int:
    nums = [int(m) for m in re.findall(r"^\|\s*20\d\d-\d\d-\d\d[^|]*\|\s*r?(\d{3,4})\s*\|", text, re.M)]
    return max(nums) if nums else 0


def main() -> int:
    rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
    with io.open(rp, "r", encoding="utf-8", newline="") as fh:
        text = fh.read()

    # 撞号让路：对端宿主可能已写更高的轮号，取 现在最大 +1，但不低于 2053
    round_no = max(_max_round(text), ROUND - 1) + 1
    row = ROW if round_no == ROUND else ROW.replace("| 2053 |", "| %d |" % round_no, 1)

    if "| %d |" % round_no not in text:
        if not text.endswith("\n"):
            text += "\n"
        text += "\n" + row
        with io.open(rp, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        print("report row appended round=%d" % round_no)
    else:
        print("report row already present round=%d" % round_no)

    sp = os.path.join(ROOT, "state-bm-c.json")
    with io.open(sp, "r", encoding="utf-8") as fh:
        st = json.load(fh)
    st["round_no"] = round_no
    st["当前活"] = ("用一把不许跳点投票的尺子重量货币架的极端 bar，并按「怎么回来」把它们分成快回、按 carry 回、回不来三类")
    st["当前活_en"] = ("r2053: re-measure each money extreme bar with a ruler the outliers cannot vote on, "
                       "then split them by how they come back -- snap, accrual-paced, or gone")
    st["最近实物"] = ("scripts/money_residual_sigma_recovery.py + results/money_residual_sigma_recovery.json + "
                  "research/MONEY_RESIDUAL_SIGMA_RECOVERY.md（selftest 21/21 · check rc0 · 负控 18/18）")
    st["最新判词"] = "THE_YARDSTICK_IS_MADE_OF_THE_OUTLIER | THREE_SHAPES_NOT_ONE | THE_ZERO_RULE_IS_RIGHT_FOR_ONE_SHAPE_ONLY"
    st["下轮指针"] = ("(a) 全量冒烟 + S6 链收口（≤48h，等竞争窗关闭）；(b) 「accrual 时钟是否存在」做成货币读器准入前置（≤48h）；"
                  "(c) 上游 money 分类器加「现金流 ≠ 现金」闸（他机属主或 GM 署名）")
    st["下个里程碑"] = "(a) 链收口 + 全量冒烟（≤48h）；(b) 时钟准入进货币读器（≤48h）"
    st["孤儿面"] = "0"
    st["孤儿面_note"] = "round-zero orphan_face_probe: orphans 0 (py_faces 4, resident_servers 1 = ComfyUI idle)"
    st["watermark_verdict"] = "green (red=false; lane healthy)"
    st["竞争_r2053"] = ("repo_write_contention rc=3 CONTENTION：对端 interactive pid 2276（19:54 起）在写共享面，"
                     "19 张面在轮首前被动过、重叠窗 0 张 -> 按 r1907 只落新增文件面，未跑 S6 链、未改共享面")
    st["未验证_r2053"] = ("①bars_to_half 只描述路径，不解释成因；②NEVER 仅指 750 根窗内没回来；"
                       "③34 只无时钟标的的两列 bp/年 是**面值水平吞掉/伪造量**，不是收益；"
                       "④全量冒烟与 S6 链本轮未跑（竞争窗），禁读成已全绿")
    st["记账_r2053"] = ("轮报告 1 处 + state 1 处 + 心跳 1 处 = 3"
                     "（无方法论新增：把『尺子不许跳点投票』与『回补是否在 accrual 时钟上』做成可复核读数属证据与载体）")
    st["通过_r2053"] = ("orders 117 文件 / 归一回执 329 / 未回执 0；decisions.md 字节 sha 79e3083b 未变=零动作；"
                     "orders.md 变（99e8e77d -> 6bd40fec）新增 1 行 = OB-20261122-223110-552 本地优先令，"
                     "本仓照做（本轮全部本地算力、零云端调用），回执随轮报告")
    with io.open(sp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("state updated round=%d" % round_no)

    hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    with io.open(hp, "r", encoding="utf-8") as fh:
        hb = json.load(fh)
    clock = NOW.isoformat(timespec="seconds")
    hb["machine_id"] = "bm-c"
    hb["last_seen"] = clock
    hb["ts"] = clock
    hb["clock_read"] = clock
    hb["heartbeat_epoch_utc"] = int(NOW.timestamp())
    hb["round_no"] = round_no
    hb["last_round_no"] = round_no
    hb["round"] = round_no
    hb["current_task"] = ("r2053 · 尺子自证：货币架 plain σ / robust σ 中位 5.9 倍、最坏 86.7 倍；"
                          "621 根极端 bar = 358 SNAP / 6 accrual-paced（全在 511880）/ 190 off-pace / 67 never")
    hb["did"] = "new-file-only landing: script + results + page + negative control + report row + this heartbeat"
    hb["verdict"] = "healthy"
    hb["孤儿面"] = "0"
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    hb["contention"] = "rc=3 CONTENTION (peer interactive pid 2276 since 19:54): new-file landing only, S6 chain not run"
    hb["smoke"] = "not run this round: contention window (r1907), and the face carries its own selftest 21/21 + check rc0 + 18 negative legs"
    with io.open(hp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(hb, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("heartbeat updated %s epoch=%d" % (clock, hb["heartbeat_epoch_utc"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
