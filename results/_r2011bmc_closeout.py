#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r2011 bm-c closeout: state face + round report line + heartbeat fields.

Kept as a file (not an inline heredoc) because the round-report line is long
CJK text and PowerShell here-strings mangle it (r1005 family).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MACHINE = "bm-c"
ROUND = 2011

ACTIVITY = ("r2011: 这本书在盘口上装得下 28.7 亿，但 100 万时 92% 的名字一手都买不起 "
            "-- liquidity never binds at the sizes we can trade; whole lots do, "
            "so the book's real floor is ~50M CNY")

REPORT = (
    "| 2026-11-23 23:0x | r2011（**竞争探针 rc=3 CONTENTION·只落新增文件面**·"
    "这本书在盘口上装得下多少钱，以及谁先把它卡住） | "
    "**watermark：red=false / lane=healthy · 孤儿面=0**（py_faces 8 / resident_servers 1=ComfyUI 空闲）。"
    "**产品（产品优先律）**：r2005-r2010 这一族回答了每一次「买得到吗」，唯独没回答「买得到多少」——"
    "而这本书是 2,866 只等权，规模完全由这个数决定。本轮把它量出来：按 **5% 的 ADV 参与率**、"
    "用决策日（t）自己的 20 日均成交额（无前视），每期算每只的**可吸收金额**，再除以它的等权槽位。"
    "**读数一（流动性不是问题）**：臂 B 每只的 20 日均额中位 **0.774 亿元**，5% 即 387 万元容量——"
    "而 10,000,000 元资本的槽位只有 **3,489 元**，所以 77 期里 **100.00%** 的名字都装得下（最差期也是 1.0000），"
    "参与率放大到 10% 或缩到 2% 结论不变。整本书的严格等权上限（最薄那只成员决定）中位 **28.71 亿元**、"
    "最差期 19.57 亿；允许 10% 的名字装不下时 39.74 亿。**读数二（整手才是墙）**：同一批名字按一手（100 股）"
    "向下取整后，每槽的实际投入离等权差多少——100 万资本下 **92.4% 的名字一手都买不起**、平均偏离 93.9%；"
    "500 万 26.6%/40.96%；1000 万 **7.7%/21.63%**；5000 万 0.15%/4.50%；1 亿 0%/2.19%；5 亿 0.44%。"
    "**判词 CAPACITY_NOT_BINDING_AT_10M**（规则在跑批前写死：中位可满载比例 ≥0.99）——"
    "它排除的是一个嫌疑，不是给出一个新 alpha：**我们买不到这本书的原因从来不是盘口，而是 2,866 份等权在 100 万规模上根本不成立**。"
    "这条与黑名单无关：任何 2,866 只等权组合在 100 万上都长这样。｜"
    "**验证证据**：`--selftest` **24/24 PASS**（ADV 窗只平均交易日 / 无成交窗口必为 NaN 不静默归零 / "
    "非有限 ADV 记 0 容量而不跳过 / 槽位边界 / 最薄成员把严格上限拉到 0 / 参与率线性 / 判词三档与 0.99·0.90 两个边界逐条钉死 / "
    "空集合不返回 1.0 / 一手取整三例含「买不起一手记 100% 偏离」）；`run` rc0 落 "
    "`results/astock_veto_adv_capacity.json` + `research/ASTOCK_VETO_ADV_CAPACITY.md`（evidence_cutoff 2026-11-20，77 期）；"
    "`check` **rc0**（含**父面锚硬腿**：臂 B 每期成员数必须逐位复现 `astock_veto_executable.json` 的 `research_arms.B.mean_size`，"
    "本次绝对差 **0.0e+00**）。**负控 `results/_r2011bmc_adv_negative.py` 8/8 PASS**（原样 rc0 / 面板 cutoff 移动→rc3 带 STALE / "
    "mean_n 手改→rc3 CHECK FAILED 且**不带** STALE / 单档资本中位手改→rc3 不带 STALE / 缺面→rc3 face missing / "
    "父面不可读→rc3 带 STALE / 臂 A 漂移同样被抓 / 还原后 rc0）。｜"
    "**S0**：`fleet/machine.json`=bm-c；`orphan_face_probe` py_faces=8 **orphans=0** 零杀；"
    "`repo_write_contention` **rc=3 CONTENTION**（3 宿主：pid 51252 为 11-22 20:10 起的 interactive、pid 67160 为 11-23 20:05 起的 interactive、本宿 55300；"
    "18 张共享面在本轮开始前被对端写，含 `fleet/machines/bm-c.json`、`fleet/round_reports-bm-c.md`、`research/ARBITER-BOARD.md`、`research/QUANT-BLOCK-BOARD.md`）"
    "→ 按 r1927 只落**新增文件面**，未改任何共享代码/数据面、未跑 S6 链；fetch 后 0 ahead / 0 behind。｜"
    "**S0.5 双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / unacked=[]）；集团 "
    "`git cat-file blob origin/main:docs/decisions.md` **原字节** sha256 = **79e3083b85c130b8** == state 水位 → 零新决策零动作；"
    "fleet/inbox 无未处理件。｜**S1（诚实边界）**：全量 smoke **未跑**（`smoke_test.py` 与 `logs/smoke_legs.json` 是共享面，竞争窗不覆盖）；"
    "本轮以 24/24 selftest + 8/8 负控 + run/check 双 rc0 背书，**不宣称全绿**。｜**S6**：未跑（`Tools/s6_chain_bmc.py` 被对端写）。｜"
    "**S7**：`state round_no 2010→2011`（rounds_done 1948→1949，round_no_prev 留痕）；心跳经 `Tools/heartbeat_write.py apply` 合并写；"
    "`attrition_ledger_guard scan` **CLEAN**（4 账本，历史缩行 healed 注记照录）；`& Tools/register_loop_task.ps1` 见下条实况；"
    "`pre-commit`/`pre-push` 与 `Tools/git-hooks/` 逐字节（CR 归一）比对见下条。｜"
    "**CEO 过程可见面**：当前活＝量这本书在盘口上装得下多少钱、以及什么先把钱卡住｜"
    "最近实物＝`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ASTOCK_VETO_ADV_CAPACITY.md`"
    "（2026-11-23 23:0x·流动性到 28.7 亿才绑；100 万时 92.4% 的名字一手都买不起）"
    "＋`results\\astock_veto_adv_capacity.json`＋`scripts\\astock_veto_adv_capacity.py`（selftest 24/24）"
    "＋`results\\_r2011bmc_adv_negative.py`（负控 8/8）｜"
    "下个里程碑＝（a）竞争窗结束后把本面接 S6 链腿 + 冒烟两腿（≤48h）；"
    "（b）把这套「槽位÷一手」的诊断做成通用件，让任何等权广度策略在立项时就能算出自己需要多少资本才成立（≤48h）。｜"
    "**未验证（如实）**：①5% 的 ADV 是假设不实测，真实冲击要看盘口与下单方式；②ADV 用决策日收盘窗，不预测次日成交；"
    "③没有把「停下等一天」的延迟成本并进来（那是 r2010 的面）；④一手取整只按 100 股/手，未处理科创板/创业板不同的最小申报与他们各自的整手规则；"
    "⑤票池是现存标的（幸存者偏差，父面同），面板起于 2020-01-02；⑥本面是容量/排除性归因件，不是可交易策略：无仓位规则、无容量约束、无风控；"
    "⑦全量 smoke 与 S6 未跑（竞争窗）。｜**本地未达 origin commit 数**＝推送后复核。"
    "记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：本轮给已有 family 加「容量」这一条排除性诊断轴，属证据与载体）。|\n"
)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def main() -> int:
    # --- state face
    spath = os.path.join(ROOT, "state-%s.json" % MACHINE)
    with open(spath, "r", encoding="utf-8") as fh:
        state = json.load(fh)
    prev_round = state.get("round_no")
    state["round_no"] = ROUND
    state["round_no_prev"] = prev_round
    state["rounds_done"] = int(state.get("rounds_done") or 0) + 1
    state["activity"] = "product"
    state["activity_now"] = ACTIVITY
    state["activity_now_round"] = ROUND
    state["last_seen"] = now_iso()
    with open(spath, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=1, sort_keys=True)

    # --- round report line (append, never rewrite: other hosts append too)
    rpath = os.path.join(ROOT, "fleet", "round_reports-%s.md" % MACHINE)
    with open(rpath, "r", encoding="utf-8") as fh:
        body = fh.read()
    if "r2011（**竞争探针" in body:
        print("round report already holds r2011 line, refusing to duplicate")
    else:
        # append-only: another host may be appending this same file (r1927);
        # read-modify-write would silently drop its line.
        with open(rpath, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(REPORT)

    # --- heartbeat fields (merge-only writer owns the file)
    fields = {
        "last_seen": now_iso(),
        "current": ACTIVITY,
        "round_no": ROUND,
        "rounds_done": state["rounds_done"],
        "verdict": "healthy",
        "heartbeat_epoch_utc": int(time.time()),
        "clock_read": now_iso(),
        "ts": now_iso(),
        "agenda_starved": False,
    }
    fpath = os.path.join(ROOT, "results", "_r2011bmc_hb_fields.json")
    with open(fpath, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fields, fh, ensure_ascii=False, indent=1)
    rc = subprocess.call([sys.executable, os.path.join(ROOT, "Tools", "heartbeat_write.py"),
                          "apply", "--fields", fpath])
    print("heartbeat_write rc=%s" % rc)
    print("state round_no=%s rounds_done=%s prev=%s" % (state["round_no"], state["rounds_done"], prev_round))
    return rc


if __name__ == "__main__":
    sys.exit(main())
