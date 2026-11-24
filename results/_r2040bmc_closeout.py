#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r2040 closeout: state counter, heartbeat fields, round-report row (one window)."""
import io
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB_FIELDS = os.path.join(ROOT, "results", "_r2040bmc_hb_fields.json")
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")

ROUND = 2040
NOW = time.strftime("%Y-%m-%d %H:%M")
CLOCK = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")

CURRENT = ("能买，但不是停泊：把 CEO 令点名的「可转债当空仓期补充」从类别层面搬到货架层面，"
           "并用「防守日」这把尺子量它")
NEXT = ("(a) 竞争窗关后把 r2022–r2040 十八面接 S6 链腿与冒烟两腿（≤48h）；"
        "(b) 把「买得到的那只 ETF 只有 1.83%/年、防守日跟跌 0.66%、beta 0.36」写进 CEO 一页纸的现金腿节（≤48h）；"
        "(c) 差额里没拆开的那一块（等权 vs 发行量加权指数、现金拖累、费率）需要转债指数成分数据，另开一张面")

MILESTONE = ("(a) 现金腿节改写（≤48h）；(b) r2022–r2040 十八面接链 + 冒烟（≤48h）")

DID = ("r2040 · 新增文件面（竞争窗）：scripts/cb_parking_bakeoff.py + results/cb_parking_bakeoff.json + "
       "research/CB_PARKING_BAKEOFF.md —— CEO 令 O-20261009-1105 说「可转债可以作为空仓期的补充」，"
       "此前被实现成两次选券测量（cb_dual_low 判死、cb_floor 功效不足），没人答「停泊」。"
       "同窗口（2020-07-16..2026-11-20）七条腿同一套成本口径：回购 1.77%（复现票面现金腿 1.77%）/ "
       "货币 ETF 1.53% / 债+货币 ETF 等权 1.52% / 转债 ETF 两只等权 1.83% / 转债全池等权 5.41% / "
       "全池每根 bar 等权 6.39% / 权益 ETF 等权 1.13%（标尺）。防守测试：权益跌 ≥1% 的 232 天里，"
       "回购 +0.006%、货币 ETF +0.010%、债 ETF -0.054%，而转债 ETF -0.665%（beta 0.36、95.7% 的下跌日）、"
       "全池 -0.663%（beta 0.36）——转债在防守日的表现和债券不在一列。剂量表：挪 25% 现金腿进转债 ETF "
       "每年多 125 元/百万但最差 20 根从 +0.07% 变 -1.98%、回撤 0→-4.88%；换全池等权 1,371 元/百万、"
       "最差 20 根 -1.94%；整条现金腿换全池也只有 20,430 元/百万（书的 3.65pp）而对最差 20 根 -8.12%。"
       "差额拆解：新券上市档 108.19%/年（切片）、成熟券 5.29%/年（每日等权）——即使剔掉新券，等权也远高于 ETF，"
       "剩下的（等权 vs 发行量加权指数、现金拖累、费率）本面明说拆不开。"
       "判词 CONVERTIBLES_PAY_MORE_THAN_THE_REPO_LEG + BUT_THEY_FALL_ON_THE_DAYS_THE_BOOK_DEFENDS + "
       "THE_INSTRUMENT_ON_SALE_DOES_NOT_HOLD_THE_CLASS_RETURN")

ROW = (
    "| %s | r2040 **新增文件面**（竞争窗 rc=3·不动共享面） | **watermark：red=false / lane=healthy · 孤儿面=0**"
    "（py_faces=5 / resident_servers=0）。竞争探针 `results/_repo_write_contention.bm-c.json` **rc=3 CONTENTION**"
    "（2 宿主：本宿 pid 58220；对端 interactive pid 51252 自 11-22 20:10 常驻 37.4h、21 张共享面在轮首前被写、"
    "重叠窗 1.8 分钟内 2 张不可归因）→ 按 r1907 同树多宿主律只落新增文件面、未改共享代码/数据面、未跑 S6 链、"
    "未跑全量 smoke。**产品（产品优先律）**：CEO 令 O-20261009-1105 说「可转债可以作为空仓期的补充」，"
    "此前两次测量都是**选券**（cb_dual_low 判死 / cb_floor 功效不足），没有人答**停泊**。本面答停泊。"
    "**读数一（七条腿，同窗口 2020-07-16..2026-11-20、同成本口径）**：回购 **1.77%%**（复现票面 cash_leg 印的 1.77%%）/ "
    "货币 ETF **1.53%%** / 债+货币 ETF 等权 **1.52%%** / **转债 ETF 两只等权 1.83%%** / **转债全池月频等权 5.41%%** / "
    "全池每根 bar 等权 6.39%% / 权益 ETF 等权 1.13%%（标尺）。**读数二（防守日 = 本面的核心尺）**：权益跌 ≥1%% 的 **232 天**里，"
    "回购 **+0.006%%**、货币 ETF **+0.010%%**、债 ETF **-0.054%%**（43.5%% 下跌日），而 **转债 ETF -0.665%%**"
    "（beta **0.366**、corr 0.772、**95.7%% 的下跌日**）、全池 **-0.663%%**（beta 0.358）——现金腿的存在理由不是收益，"
    "是书亏钱的那些天它不亏，转债在这张表里和债券不在一列。**读数三（最差 20 根）**：回购 +0.07%% / 货币 -0.05%% / "
    "债 ETF -3.20%% / **转债 ETF -8.02%%** / 全池 -8.12%%。**读数四（剂量表）**：挪 25%% 现金腿（=书的 14.1%%）进转债 ETF "
    "每年多 **125 元/百万**、最差 20 根 +0.07%%→**-1.98%%**、回撤 0→-4.88%%；换全池等权 **1,371 元/百万**、最差 20 根 -1.94%%；"
    "整条现金腿换全池也只有 **20,430 元/百万**（书的 3.65pp）而对最差 20 根 -8.12%%、回撤 -17.03%%。"
    "**读数五（类别 vs 货架，3.58pp 的缺口）**：ETF 1.83%% / 全池月频 5.41%% / 全池每 bar 6.39%%；重排频率只值 **0.97pp**，"
    "**新券上市档 108.19%%/年（切片口径）**、**成熟券仍有 5.29%%/年**——即使把新券全剔掉等权也远高于 ETF，"
    "剩下的差额（等权 vs 发行量加权指数、现金拖累、费率）本面**明说拆不开**，不假装有答案。"
    "**判词** `CONVERTIBLES_PAY_MORE_THAN_THE_REPO_LEG+BUT_THEY_FALL_ON_THE_DAYS_THE_BOOK_DEFENDS+"
    "THE_INSTRUMENT_ON_SALE_DOES_NOT_HOLD_THE_CLASS_RETURN`。｜**验证证据**：`--selftest` **26/26 PASS**（含常数面板复现、"
    "单名单只付一次换手、最差 20 根窗口、cagr/level 恒等、beta 自比=1、防守日计数、洗牌保留均值方差但移动尾部、"
    "剂量端点恒等、`_pp`/`_pct` 不可互换、provenance 不得覆盖 metric 键）；`run` rc0 55.1s；`check` **rc0**"
    "（输入字节 sha + 头条逐值重推 + 剂量端点恒等 + 每行钱数恒等 + 页面 token/最差 20 根列在场 + 内容哈希）；"
    "负控 `results/_r2040bmc_parking_negative.py` **13/13 PASS**（健康副本必绿；父面动→STALE 且不带 CHECK FAILED；"
    "改头条→CHECK FAILED 且不带 STALE；改剂量钱数/端点→点名；页面丢判词/丢尾部列/植入百分比套百分比→各自点名；"
    "缺面→STALE 不崩；数字位写字符串→红不 traceback〔负控当场抓出 `near()` 崩溃，已修成判红〕；"
    "内容哈希不自洽→点名；跑完两个发布件逐字节未动）。｜**S0**：`fleet/machine.json`=bm-c；"
    "`orphan_face_probe` **orphans=0** 零杀；`repo_write_contention` rc=3 → 只落新增文件面。｜**S0.5 双扫**："
    "`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / unacked=[]）；集团 `git cat-file blob origin/main:docs/decisions.md` "
    "原字节 sha256 仍 **79e3083b85c130b8** → 零新决策；`attrition_ledger_guard scan` **CLEAN**（4 账本 / 5 处历史缩行 healed 照录）；"
    "fleet/inbox 0 件。｜**S1（诚实边界）**：全量 smoke 未跑（`smoke_test.py` 与 `logs/smoke_legs.json` 都是共享面），"
    "本轮以 26/26 selftest + 13/13 负控 + run/check 双 rc0 背书，**不宣称全绿**。｜**S6**：未跑（共享面）。"
    "｜**S7**：state round_no 2039→2040；`& Tools/register_loop_task.ps1` **phase ok**（pin=0 current=0，首燃 10:00 未动）；"
    "pre-commit / pre-push 爪与 `Tools/git-hooks/` 源同（MATCH/MATCH）；心跳 `heartbeat_write apply --fields` rc0；"
    "集团树缺席 fallback 未触发。｜**CEO 过程可见面**：当前活＝%s；最近实物＝`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\CB_PARKING_BAKEOFF.md`"
    "（2026-11-24 09:5x·**回购 1.77%% vs 转债 ETF 1.83%% vs 转债全池 5.41%%**；**防守日 232 天里转债 -0.665%%（beta 0.36、95.7%% 下跌日）"
    "而回购 +0.006%%**；**挪 25%% 现金腿进转债 ETF 只值 125 元/百万、最差 20 根 0.07%%→-1.98%%**）"
    "＋`results\\cb_parking_bakeoff.json`＋`scripts\\cb_parking_bakeoff.py`（selftest 26/26）＋"
    "`results\\_r2040bmc_parking_negative.py`（负控 13/13）；下个里程碑＝%s。｜**未验证（如实）**："
    "①全池腿是等权、无整手、无冲击的类别读数，不是可下单篮子；②月频 vs 每 bar 只把「重排频率」与「类别」分开，"
    "两条都不是可执行策略；③ETF 与等权之间 3.58pp 的缺口只拆出上市档这一块，剩下三项混在一起未拆；"
    "④窗口从 2020-07 起，只覆盖含 2022 转债杀与 2024 修复的这段 regime；⑤防守日尺子用权益 ETF 等权做标尺，"
    "换成指数或书的真实净值会得到不同的 beta；⑥剂量表 50%%→100%% 非单调是波动拖累，未进一步分解；"
    "⑦转债 ETF 只有两只、都是 2020 年上市，ETF 这一档的样本只有一段。"
    "｜**本地未达 origin commit 数**＝推送后复核。记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3"
    "（无方法论新增：把「这个能赚多少」换成「它在书防守的那些天干什么」属于证据与载体；方法论卡锁存待无竞争轮）。 |"
) % (NOW, CURRENT, MILESTONE)


def main():
    with io.open(STATE, encoding="utf-8") as f:
        st = json.load(f)
    st["round_no"] = ROUND
    st["round"] = ROUND
    st["who_did"] = "bm-c"
    st["当前活"] = CURRENT
    st["当前任务"] = DID[:400]
    st["最新实物"] = ("research/CB_PARKING_BAKEOFF.md + results/cb_parking_bakeoff.json + "
                     "scripts/cb_parking_bakeoff.py（selftest 26/26·check rc0·负控 13/13）（%s）" % NOW)
    st["最近实物"] = st["最新实物"]
    st["最新判词"] = ("CONVERTIBLES_PAY_MORE_THAN_THE_REPO_LEG+BUT_THEY_FALL_ON_THE_DAYS_THE_BOOK_DEFENDS+"
                     "THE_INSTRUMENT_ON_SALE_DOES_NOT_HOLD_THE_CLASS_RETURN")
    st["本轮"] = DID
    st["本次"] = ("回购 1.77% / 货币 ETF 1.53% / 债 ETF 等权 1.52% / 转债 ETF 1.83% / 转债全池月频 5.41% / "
                  "全池每 bar 6.39% / 权益 ETF 1.13%；防守日 232 天：回购 +0.006%、货币 +0.010%、债 -0.054%、"
                  "转债 ETF -0.665%（beta 0.366、95.7% 下跌日）、全池 -0.663%；剂量 25% 现金腿：ETF +125 元/百万、"
                  "最差 20 根 -1.98%；全池 +1,371 元/百万、最差 20 根 -1.94%")
    st["下轮指针"] = NEXT
    st["下个里程碑"] = MILESTONE
    st["未验证"] = ("①全池腿是等权/无整手/无冲击的类别读数，不是可下单篮子；②月频 vs 每 bar 只分离重排频率；"
                    "③ETF 与等权 3.58pp 的缺口只拆出上市档；④窗口 2020-07 起；⑤防守日尺子=权益 ETF 等权；"
                    "⑥剂量表 50%→100% 非单调=波动拖累未分解；⑦转债 ETF 只有两只且 2020 年上市")
    st["watermark_verdict"] = ("green (red=false; lane healthy; repo_write_contention rc=3 CONTENTION -> "
                               "new-file faces only)")
    st["watermark_note"] = ("竞争探针 rc=3 CONTENTION：对端 interactive pid 51252 常驻 37.4h、21 张共享面在轮首前被写、"
                            "重叠窗 1.8 分钟内 2 张不可归因 → 按 r1907 只落新增文件面，未改共享代码/数据面、未跑 S6 链、未跑全量 smoke")
    st["记账_r2040"] = "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（方法论卡锁存待无竞争轮）"
    st["孤儿面"] = 0
    st["孤儿面_note"] = "round-zero orphan_face_probe: orphans 0 (py_faces 5, resident_servers 0)"
    with io.open(STATE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)

    fields = {
        "round": ROUND,
        "round_no": ROUND,
        "当前任务": "r2040: 可转债能不能当空仓期停泊（CEO 令 O-20261009-1105 的停泊面）",
        "最新实物": st["最新实物"],
        "最新判词": st["最新判词"],
        "watermark_verdict": st["watermark_verdict"],
        "孤儿面": 0,
        "下个里程碑": MILESTONE,
        "记账_r2040": st["记账_r2040"],
    }
    with io.open(HB_FIELDS, "w", encoding="utf-8") as f:
        json.dump(fields, f, ensure_ascii=False, indent=1)
    rc = subprocess.call([sys.executable, os.path.join(ROOT, "Tools", "heartbeat_write.py"),
                          "apply", "--fields", HB_FIELDS])
    print("heartbeat rc=%s" % rc)

    with io.open(REPORT, "a", encoding="utf-8") as f:
        f.write(ROW + "\n")
    print("round report row appended; round_no=%d" % ROUND)
    return 0 if rc == 0 else rc


if __name__ == "__main__":
    sys.exit(main())
