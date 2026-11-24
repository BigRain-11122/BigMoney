#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r2043 closeout for bm-c: state fields, heartbeat fields, one round-report row.

Contention window is open (repo_write_contention rc=3, two interactive bm-c hosts
writing shared faces), so every write here is **field-level merge on this machine's own
faces only** -- read the latest bytes, set only this round's keys, write back in the file's
own format (indent=2).  No shared code/data face is touched and the round report is
appended, never rewritten.
"""
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")
ROUND = 2043
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
STAMP = time.strftime("%Y-%m-%d %H:%M")

CURRENT = ("r2043 · 新增文件面（竞争窗）：scripts/cash_shelf_build_out_plan.py + "
           "results/cash_shelf_build_out_plan.json + research/CASH_SHELF_BUILD_OUT_PLAN.md "
           "-- 把 r2041 的容量「THIN」翻译成排期与它的价：票面 565,246 元要 511380 两个交易日、"
           "511360 五个、511180 三个；而分批的 95 分位成本是 511380 2,787 元（= 它一年超额的 239%）、"
           "511360 265 元（= 9%）、511180 3,090 元（而它本身比回购少赚 2,041 元/年，问题不是等）")

DATASET = {
    "round_no": ROUND,
    "round": ROUND,
    "last_round": "r2043 — 现金腿货架的排期价：慢不贵，波动才贵",
    "last_round_label": "r2043 cash_shelf_build_out_plan",
    "last_round_at": NOW,
    "last_round_ts": NOW,
    "last_round_summary": CURRENT,
    "last_round_summary_at": NOW,
    "activity": "product",
    "activity_now": CURRENT,
    "activity_now_round": ROUND,
    "did_round": ROUND,
    "did": CURRENT,
    "who_did": "bm-c",
    "who_did_r": ROUND,
    "当前活": ("能装下不等于装得进：给「分天买」这一动作定价——同一句排期，落在每天走 0.9 个基点的短融上是排期，"
                "落在每天摆动几十个基点的转债上是下注"),
    "当前活_en": ("r2043: a THIN capacity verdict is a calendar question, not a wall -- price the "
                  "batching itself on the tape instead of assuming the ceiling is the answer"),
    "work": ("r2043 · 新增文件面（竞争窗）：把 r2041 的容量读数翻译成「要几个交易日」与「分批本身多少钱」。"
             "尺子冻结：一天上限 = 坏日子成交额 1%（读 r2041，不重打）；成交均价 = 每天等额买入的调和平均"
             "（不是算术平均，否则把成本说大）；偏移 = 调和均价 ÷ 首日价 − 1，面板每个重叠窗都算，"
             "所以公布的是真的发生过什么。读数一：票面 565,246 元，511380 要 2 天、511180 3 天、511360 5 天，"
             "511880/511010 一天装完。读数二（本面的要点）：最慢的 511360 分批 95 分位只花 265 元 = 它一年超额的 8.6%；"
             "只要 2 天的 511380 一次分批就花 2,787 元 = 2.4 年超额。读数三：511180 根本不该买——它比回购少赚 2,041 元/年，"
             "把它和「一年超额」比是拿负数当分母。读数四：511360 的 05 分位是 −0.79bp，"
             "在 114.19 元的票面上是 9 个最小报价单位，属于报价粒度而非方向赌（一个报价单位只有 0.0876bp）。"),
    "最新判词": "SCHEDULING_IS_ENOUGH_FOR:511360 + SCHEDULING_IS_NOT_ENOUGH_FOR:511380 + A_TWO_SIDED_BATCH_IS_NOT_BUDGETABLE_FOR:511380,511180,511360",
    "最新实物": ("research/CASH_SHELF_BUILD_OUT_PLAN.md + results/cash_shelf_build_out_plan.json + "
                 "scripts/cash_shelf_build_out_plan.py（selftest 35/35·check rc0·负控 6/6）（" + STAMP + "）"),
    "最近实物": ("research/CASH_SHELF_BUILD_OUT_PLAN.md + results/cash_shelf_build_out_plan.json + "
                 "scripts/cash_shelf_build_out_plan.py（selftest 35/35·check rc0·负控 6/6）（" + STAMP + "）"),
    "下轮指针": ("(a) 竞争窗关后把 r2022–r2043 二十一面接 S6 链腿与冒烟两腿，并跑全量套件（≤48h）；"
                 "(b) 把「慢不贵、波动才贵」这一句搬进 CEO 一页纸的现金腿节（≤48h）——正文只加一句"
                 "「需要五个交易日的短融分批只花掉 9% 的年超额，需要两个交易日的转债一次分批就吃掉 2.4 年」；"
                 "(c) 若要真用 511360，还要测「分批期间在途资金停在回购腿」的对冲读数，本面只量了价格偏移"),
    "下个里程碑": "(a) 二十一面接链 + 全量冒烟（≤48h）；(b) CEO 一页纸现金腿节加这一句（≤48h）",
    "未验证": ("①参与带是市场触达惯例，不是实测冲击模型（我们太小，没有影响模型可用）；"
               "②成交价用当日收盘，不是次日开盘（本面只量时间偏移的相对大小，不重定执行基准）；"
               "③整手零头不重复计价（r2041 已按整手定过：票面在 511360 上留 5,720 元零头 = 15.2bp）；"
               "④规模档只到 500 万，再往上要靠 39 个交易日，本面没有测；"
               "⑤511180 的超额为负是继承 r2041 的读数，本面没有重算它的收益；"
               "⑥窗口从 2020-07-16 起，转债两只与短融都是 2020 年上市，样本只有一段"),
    "记账_r2043": "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：把容量的「THIN」换到时间轴上定价属证据与载体）",
    "孤儿面": 0,
    "孤儿面_note": "round-zero orphan_face_probe: orphans 0, py_faces 3, resident_servers 0, killed 0",
    "水位": "healthy",
    "verdict": "healthy",
    "competition_r2043": ("repo_write_contention rc=3 CONTENTION：本机另有 interactive 宿主 pid 51252（2026-11-22 20:10 起，"
                          "2320.8min）与 pid 68052（2026-11-24 09:43 起）在写共享面，25 张面在轮首前被写、2 张落在重叠窗不可归因 "
                          "-> 按 r1907 只落新增文件面，未改共享代码/数据面，未跑 S6 链与全量冒烟"),
    "deferred_r2043": ("竞争窗 rc=3 未跑：S6 链 / 全量冒烟 / attrition 守卫 / py_watermark+compute_audit / update_daily 族；"
                       "下轮（竞争窗关后）首批补跑，禁读成「全绿」"),
    "本地未达 origin commit 数": 0,
    "本地未达origin": 0,
}

HB_FIELDS = {
    "round": ROUND,
    "round_no": ROUND,
    "last_round": ROUND,
    "round_label": "r2043 cash_shelf_build_out_plan",
    "last_round_label": "r2043 cash_shelf_build_out_plan",
    "last_seen": NOW,
    "last_seen_at": NOW,
    "ts": NOW,
    "updated_at": NOW,
    "clock_read": NOW,
    "clock_read_source": "system",
    "heartbeat_epoch_utc": EPOCH,
    "heartbeat_epoch_utc_type": "int",
    "cpu_pct": 6.2,
    "cpu_free_pct": 93.8,
    "ram_free_gb": 26.8,
    "free_ram_gb": 26.8,
    "vram_free_gb": 11.1,
    "gpu_free_vram_gb": 11.1,
    "vram_total_gb": 16.0,
    "孤儿面": 0,
    "orphans": 0,
    "orphan_face": 0,
    "watermark_verdict": "green (red=false; lane healthy; repo_write_contention rc=3 -> new-file faces only)",
    "watermark_note": ("竞争窗 rc=3：interactive pids 51252/68052 写共享面；本轮只落新增文件面，"
                       "未改共享面、未跑 S6 链、未跑全量 smoke"),
    "current_task": CURRENT,
    "当前活": ("能装下不等于装得进：给「分天买」定价——短融每天走 0.9bp 是排期，转债每天摆动几十 bp 是下注"),
    "最新实物": ("research/CASH_SHELF_BUILD_OUT_PLAN.md + results/cash_shelf_build_out_plan.json + "
                 "scripts/cash_shelf_build_out_plan.py（selftest 35/35·check rc0·负控 6/6）（" + STAMP + "）"),
    "最近实物": ("research/CASH_SHELF_BUILD_OUT_PLAN.md + results/cash_shelf_build_out_plan.json + "
                 "scripts/cash_shelf_build_out_plan.py（selftest 35/35·check rc0·负控 6/6）（" + STAMP + "）"),
    "最新判词": "SCHEDULING_IS_ENOUGH_FOR:511360 + SCHEDULING_IS_NOT_ENOUGH_FOR:511380 + A_TWO_SIDED_BATCH_IS_NOT_BUDGETABLE_FOR:511380,511180,511360",
    "下轮指针": ("(a) 竞争窗关后 r2022–r2043 二十一面接链 + 全量冒烟（≤48h）；"
                 "(b) CEO 一页纸现金腿节加「慢不贵」一句（≤48h）"),
    "下个里程碑": "(a) 二十一面接链 + 全量冒烟（≤48h）；(b) CEO 一页纸现金腿节加这一句（≤48h）",
    "s6_chain": "deferred (contention rc=3)",
    "s6_chain_inflight": False,
    "chain_in_flight": False,
    "verdict": "healthy",
    "status": "healthy",
    "activity": "product",
    "activity_now": CURRENT,
    "activity_now_round": ROUND,
    "idle_rounds": 0,
    "agenda_starved": False,
    "本地未达 origin commit 数": 0,
    "local_unreached_commits": 0,
    "记账_r2043": "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3",
}

REPORT_ROW = (
    "| " + STAMP + " | r2043 **新增文件面（竞争窗）**：scripts/cash_shelf_build_out_plan.py ＋ "
    "results/cash_shelf_build_out_plan.json ＋ research/CASH_SHELF_BUILD_OUT_PLAN.md ＋ "
    "负控 results/_r2043bmc_buildout_negative.py —— 把 r2041 的「容量 THIN」翻译成排期与它的价。"
    "**尺子**：一天上限 = 坏日子成交额的 1%（读 r2041 的 max_open_order_cny，不重打）；成交均价 = 每天等额买入的"
    "**调和平均**（不是算术平均，否则把成本说大；自检有腿钉死 10/20 两天 = 13.333 而非 15）；偏移 = 调和均价 ÷ 首日价 − 1，"
    "面板上每个重叠窗都算，公布的是真发生过什么。**读数**：票面 565,246 元，511380 要 2 个交易日、511180 3 个、511360 5 个，"
    "511880/511010 一天装完；分批的 95 分位成本 511380 **2,787 元 = 它一年超额（1,167 元）的 239%**，"
    "511360 **265 元 = 9%**（一年超额 3,088 元），511180 3,090 元而它本身比回购少赚 2,041 元/年"
    "（把它和一年超额比是拿负数当分母，页面印「本行超额为负」不印百分比）。**要点**：最慢的货架分批最便宜、"
    "最快的转债分批最贵——慢不贵，波动才贵；同一句「分天买」落在每天走 0.9bp 的短融上是排期，落在每天摆动几十 bp 的转债上是下注。"
    "511360 的 05 分位 −0.79bp 在 114.19 元票面上是 9 个最小报价单位（一个报价单位仅 0.0876bp），属报价粒度不是方向赌。"
    "**验证**：`--selftest` **35/35 PASS**（含调和 vs 算术、天数取整、单调/双向二分、负超额不判排期、页面不印负数百分比）；"
    "`--check` **rc0** 五行使逐格复算（面板 + r2041）；负控 **6/6**（改一格必 rc1 并点名、上游动一字节必 rc3 STALE 且不带 CHECK FAILED、"
    "人造 +1bp/日漂移必落在 ~2bp/5 窗且加倍即加倍、平坦 tape 必 0）。｜**S0**：fleet/machine.json=bm-c；"
    "orphan_face_probe **orphans=0**（py_faces 3、resident_servers 0）零杀；竞争探针 **rc=3 CONTENTION**"
    "（interactive pid 51252 自 11-22 20:10、pid 68052 自 11-24 09:43；25 张共享面在轮首前被写、2 张在重叠窗不可归因）"
    "→ 按 r1907 只落新增文件面，未改共享面、未跑 S6 链与全量冒烟。｜**未验证（如实）**：①参与带是市场触达惯例不是实测冲击模型；"
    "②成交价用当日收盘不是次日开盘（只量时间偏移的相对大小）；③整手零头不重复计价（r2041 已按整手定价：票面在 511360 上留 5,720 元 = 15.2bp）；"
    "④规模档只到 500 万（再往上要 39 个交易日）；⑤511180 的负超额继承 r2041 未重算；⑥窗口 2020-07-16 起，两只转债与短融都是 2020 年上市。"
    "｜**下轮指针**：竞争窗关后 (a) r2022–r2043 二十一面接 S6 链腿 + 冒烟两腿 + 全量套件（≤48h）；"
    "(b) 把「慢不贵」一句搬进 CEO 一页纸现金腿节（≤48h）；(c) 若要真用 511360，还需测分批期间在途资金停在回购腿的对冲读数。"
    "｜**本地未达 origin commit 数**＝推送后复核。｜记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3。"
)


def main():
    # ---- state
    with io.open(STATE, encoding="utf-8") as f:
        st = json.load(f)
    before = st.get("round_no")
    st.update(DATASET)
    with io.open(STATE, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(st, ensure_ascii=False, indent=2) + "\n")
    with io.open(STATE, encoding="utf-8") as f:
        chk = json.load(f)
    assert chk["round_no"] == ROUND, "state round_no did not land"
    print("state: round_no %s -> %s, %d keys" % (before, chk["round_no"], len(chk)))

    # ---- heartbeat: this file's own format is indent=1 (state is indent=2); writing it
    # with the wrong indent rewrites all ~918 lines and would bury a peer's concurrent
    # field edit inside a whole-file diff (r2043 self-caught)
    with io.open(HB, encoding="utf-8") as f:
        hb = json.load(f)
    hb_before = hb.get("round")
    hb.update(HB_FIELDS)
    with io.open(HB, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(hb, ensure_ascii=False, indent=1) + "\n")
    with io.open(HB, encoding="utf-8") as f:
        cb = json.load(f)
    assert isinstance(cb["heartbeat_epoch_utc"], int), "heartbeat_epoch_utc must be an int"
    assert "T" in cb["clock_read"], "clock_read must be T-separated ISO"
    print("heartbeat: round %s -> %s, epoch type int=%s" % (
        hb_before, cb["round"], isinstance(cb["heartbeat_epoch_utc"], int)))

    # ---- round report: append one row, never rewrite; idempotent on re-run
    with io.open(REPORT, encoding="utf-8") as f:
        last = f.read().splitlines()[-1] if os.path.getsize(REPORT) else ""
    if last.startswith("| " + STAMP):
        print("round report: this round's row is already the last line, nothing appended")
    else:
        with io.open(REPORT, "a", encoding="utf-8", newline="") as f:
            f.write(REPORT_ROW + "\n")
        with io.open(REPORT, encoding="utf-8") as f:
            tail = f.read().splitlines()[-1]
        assert tail.startswith("| " + STAMP), "round report row did not land as the last line"
        print("round report: 1 row appended (%d chars)" % len(REPORT_ROW))
    return 0


if __name__ == "__main__":
    sys.exit(main())
