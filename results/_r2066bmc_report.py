# -*- coding: utf-8 -*-
"""Append one round-report line.  Read-modify-write in one process (r1005: never `replace`
on a multi-writer ledger)."""
from __future__ import annotations

import datetime as _dt
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, "round_reports-bm-c.md")

LINE = (
    "{ts} | r2066 | bm-c | "
    "**PRODUCT（产品优先律·watermark 绿（red=false·lane=healthy·next_pick 已被他机 claimed）"
    "·孤儿面=0（py_faces=4 / orphans=0 / resident_servers=2）"
    "·竞争窗 rc=3 CONTENTION〔对端 interactive pid 79608 自 2026-11-24T22:39 起 222min、"
    "8+ 张共享面在轮首前被动过、重叠 1.3min 内不可归因 0 张，证据 "
    "results/_repo_write_contention.bm-c.json〕→ 按 r1907/r1927 只落新增文件面："
    "未改共享面、未重跑 S6 链、未跑全量冒烟）**："
    "同一张 permission 收据上印着两个「许可边界」，差 **63.4 倍**——`permitted_k = min(paths)` "
    "（印成 *the permitting floor*）与 `keep_allowed = any(path >= k_now - tol)`（判词真正用的那条）。"
    "在册票面 k=0.435003 / 100 万元：严格读法只允许再加 **0.50pp ≈ 5,000 元**（因为它就是最严那条 "
    "universe=0.435003），宽松读法允许再加 **31.7083pp ≈ 317,083 元**（window=0.747086 撑腰）；"
    "两侧都加上面自带的 size_tol 0.50pp 后再减在册尺寸，因为 keep_allowed 本身就是这么写的。"
    "判词 `TWO_READINGS_DIFFER`，并**用真 decide() 逐 0.05pp 扫出翻转点 k=0.752503**（高于在册 "
    "31.75pp）——不是读代码推的，是调函数测的：翻转点之下一格真 decide() 仍 keep、点上不再 keep（selftest 双腿钉死）。"
    "另一条实测：k 变小永远不会失去许可（`any` 判据对下跌天然免疫），所以严格那个数是**加仓的天花板，不是割肉的扳机**——"
    "r2064 把它读成「零余量＝明天要卖」是把天花板当扳机，本面把这个误读就地挡住。"
    "| scripts/etf_book_headroom_two_readings.py（selftest **19/19 OK**·write rc0·--check **CHECK OK** rc0·"
    "负控 results/_r2066bmc_headroom_negctl.py **7/7 OK**：改一格→rc1 且句含 CHECK FAILED 且**不含**链的重建词／"
    "删面→rc3 且含 STALE／还原逐字节相同后转绿）"
    "+ results/etf_book_headroom_two_readings.json + research/ETF_BOOK_HEADROOM_TWO_READINGS.md + qa/headroom-two-readings-r2066.md。"
    "**负控抓出本面自己的缺陷（自捕）**：首版 check 文案写「(no STALE prefix: ...)」，字面自带链的重建词→"
    "每次真分歧都会让链白跑一次重建（r1850）；负控第三条腿当场判红，改写为「(same inputs, different numbers -- "
    "a disagreement, not drift)」后转绿，已记入 qa。"
    "**未做（如实）**：共享面零改动（permission/rulers/腿未碰）；r2063 一行补丁仍未落地，本面的读数是**打过该补丁之后**的语义"
    "（补丁只在内存里，base bar 2026-11-20 / k=0.458463422）；未重跑全量冒烟（连续第 12 轮，读数仍是 2026-11-24T20:12:28 那份）；"
    "S6 链连续第 12 轮未跑；本面未接冒烟腿/S6 腿（欠账入下轮指针）。"
    "| S0.5 双扫：fleet/orders 117 件、本机回执 331 条、**11 月令 3 件全部已回执（涉本机未回执 0 件）**；"
    "10 月及更早 34 件触及本机字面但均属跨机广播/已实质执行（未逐令补 ack，避免 34 条记账超预算，如实记）；"
    "集团 origin/main:docs/decisions.md 原生字节 250,586B sha256 79e3083b85c130b8… **== 自持水位**（零新决策零动作）；fleet/inbox 空。"
    "| S7：GPU 面走 Tools/gpu_face.py apply 一次探针写全 33 键（util 1% / used 1958 MiB / free 14426 MiB，audit findings=[]）；"
    "schtasks 自愈本轮未触碰（对端在飞，重注册会打断在飞轮）；attrition tripwire 未跑（竞争窗，与冒烟/S6 同列延后）。"
    "| **本地未达 origin commit 数**：本条 commit 前实测 origin/main...HEAD = 1/16（本行 commit 后再 +1，读者此刻应为 1/17；"
    "自指计数差 1 按 r2062 addendum-2 判例写清）。"
    "| 下轮指针：(a) 静窗后落地 r2063 一行补丁 → 再 run 本面 → 看严格/宽松两读是否变（预期不变，变的是面本身从 UNREADABLE 转可读）；"
    "(b) 把本面接一条冒烟腿（判据=两读差 >0.5pp 时必须印出 keep_allowed 走的是哪条 path）；"
    "(c) 全量冒烟 + S6 分批补跑（≤48h）。"
    "| **CEO 三行**：当前活＝把「这本书还能加多少钱」的两个答案摆在一起——同一份收据印出 5,000 元和 317,083 元，"
    "并指明判词实际用的是后者｜最近实物=K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ETF_BOOK_HEADROOM_TWO_READINGS.md"
    "（2026-11-25T02:36+08:00·selftest 19/19·负控 7/7）｜下个里程碑＝静窗落地 r2063 补丁后复验两读+接冒烟腿（≤48h）。"
    "| 记账：轮报告 1 处 + state 1 + 心跳 1 = 3。\n"
)


def main():
    ts = _dt.datetime.now().astimezone().replace(microsecond=0).isoformat()
    line = LINE.format(ts=ts)
    with io.open(RP, "r", encoding="utf-8", newline="") as f:
        body = f.read()
    if not body.endswith("\n"):
        body += "\n"
    with io.open(RP, "w", encoding="utf-8", newline="") as f:
        f.write(body + line)
    print(json_safe({"appended_bytes": len(line.encode("utf-8")), "ts": ts}))
    return 0


def json_safe(d):
    import json
    return json.dumps(d, ensure_ascii=False)


if __name__ == "__main__":
    sys.exit(main())
