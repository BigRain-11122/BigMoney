"""r2038 closeout: bump the round number, refresh the state face, stage the heartbeat fields.

The round number lives in the state face and the heartbeat is merge-only, so both are written
from one script and the ack list is never rebuilt from scratch (r1052 family).

Usage
    python results/_r2038bmc_closeout.py
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB_FIELDS = os.path.join(ROOT, "results", "_r2038bmc_hb_fields.json")

TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ).isoformat(timespec="seconds")
EPOCH = int(time.time())
ROUND = 2038

VERDICT = "WAITING_IS_THE_EXPENSIVE_INSURANCE+THE_BETA_ERROR_IS_CHEAPER_THAN_THE_WAIT_IT_AVOIDS"

LATEST = ("research/ASTOCK_VETO_HEDGE_DEPLOY_WAIT.md + results/astock_veto_hedge_deploy_wait.json + "
          "scripts/astock_veto_hedge_deploy_wait.py（selftest 28/28·check rc0·负控 12/12）（2026-11-24 08:5x）")

FIELDS = {
    "round": ROUND,
    "round_no": ROUND,
    "last_seen": NOW,
    "clock_read": NOW,
    "ts": NOW,
    "heartbeat_epoch_utc": EPOCH,
    "verdict": "healthy",
    "idle_rounds": 0,
    "agenda_starved": False,
    "vcpu": 32,
    "vram_free_gb": 14.3,
    "vram_total_gb": 16.0,
    "latest_work": "r2038 astock_veto_hedge_deploy_wait (selftest 28/28, negative 12/12)",
    "当前活": "在 sizing 块上给「现在部署 vs 等带宽变窄」开一张价签：等待期每年到底在付什么",
    "当前任务": ("r2038: band 面印了 924 手带宽却把「部署 vs 等待」留在桌上。本面给等待定价——"
                 "带宽减半要四倍期数（43→172 期 = 再等 10.24 年），等待期账本裸着每年多扛 16.580pp，"
                 "等满共付 169.8pp（每百万 1,697,504 元），换来的残差天花板只有 0.124pp（1,242 元）"
                 "→ 等待是它买到保险的 1367 倍；反过来部署的风险上界只有 0.054pp（538 元），"
                 "是等一年 16.580pp 的 1/308"),
    "最新实物": LATEST,
    "最近实物": LATEST,
    "当前活_en": ("r2038: price the wait the sizing block left on the table -- halving the 924-lot band needs "
                  "four times the periods (10.24 more years), the unhedged book carries 16.580pp a year, "
                  "the wait's ceiling benefit is 0.124pp, so the wait costs 1367x what it insures; being "
                  "wrong about the beta costs 0.054pp, 1/308 of one year of waiting"),
    "最新判词": VERDICT,
    "下轮指针": (
        "(a) 无竞争轮：smoke_test.py 两腿 + Tools/s6_chain_bmc.py r2038 腿 + knowledge/METHODOLOGY_ASSETS.md 卡"
        "（锁存：等待的价格要用「未对冲暴露」而不是「放弃的收益」来标——对冲是减风险的，"
        "等待期付的是风险不是收益；把「等待期是裸的」这个前提写成显式口径）+ CODELY 一行；"
        "(b) 把「1367 倍 / 308 倍」这两个除数写进 CEO 一页纸的仓位节，替掉只印 924 手带宽的写法（≤48h）；"
        "(c) BUDGET 面规则 A 的 k=0.65 是本面的一个天然对照——部分对冲的等待费更小，"
        "下一面把「完全不对冲」与「部分对冲」两条等待曲线画在一张图上"),
    "下个里程碑": (
        "(a) 竞争窗关后把 r2022–r2038 十六面接 S6 链腿与冒烟两腿（≤48h）；"
        "(b) 把「等待 1367 倍 / 部署错 1/308」写进 CEO 一页纸仓位节（≤48h）"),
    "本次": (
        "三臂（每百万镜头）：deploy_now beta=0.9013 → 3,919 手、残差 10.763%、95% 带 3,457..4,381；"
        "wait_for_half_band 目标 462 手（半宽）、10.238 年后、等待期年付 16.580pp（165,803 元）、"
        "总付 169.75pp（1,697,504 元）、天花板收益 0.124pp（1,242 元）、倍率 1366.55；"
        "deploy_and_be_wrong 用 0.9013 而真值 1.0263（差 0.1249 = 13.86%）→ 残差差 0.0538pp（538 元）、"
        "是等一年的 1/308"),
    "孤儿面": 0,
    "孤儿面_note": "round-zero orphan_face_probe: orphans 0 (py_faces 3, resident_servers 1 = ComfyUI idle)",
    "watermark_note": ("竞争探针 rc=3 CONTENTION：对端 interactive pid 51252 常驻 36.6h、"
                       "24 张共享面在轮首前被写、重叠窗 0 张 → 按 r1907 只落新增文件面，"
                       "未改共享面、未跑 S6 链、未跑全量 smoke"),
    "watermark_verdict": "green (red=false; lane healthy; repo_write_contention rc=3 CONTENTION -> new-file faces only)",
    "记账_r2038": ("轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：等待的价格是"
                   "「未对冲暴露 − 已对冲残差」这个减法，属证据与载体；方法论卡锁存待无竞争轮）"),
    "why_not_bookkeeping": ("本轮主产出是一张把「等待」定价成「每年付多少波动换多少残差降低」的价签"
                            "（脚本 + JSON + 页面 + 负控），不是记账"),
    "went_well": ("把一个所有面都印了却没人选的交易（924 手带宽要不要等）变成一个分母清晰的倍率，"
                  "并且用「等待期是裸的」这个物理前提把等待费从抽象概念落成每年 165,803 元"),
    "when_well": ("本面只读父面、不重算 beta，所以「部署的风险上界」用的是家族自己的样本外估计，"
                  "不是另造一条曲线"),
    "未验证": (
        "①「等待 = 完全不对冲」是本面的定价前提，跑部分对冲（如 k=0.65）的读者付得更少；"
        "②10.24 年这个数字假设 beta 标准误按 1/√n 收窄，而 band 面的滚动拟合范围 0.885..1.280 说明 "
        "beta 本身在动，带宽收窄不一定带来更准的 beta；"
        "③52 期是否代表未来 regime 未证（r2037 已明说符号稳不等于样本公平），本面沿用；"
        "④16.580pp 是波动差，不是可实现的收益差——本面没有给波动定价（那是 BUDGET 面的活）；"
        "⑤只切 k=1、全额抵押、最便宜租金这一个参考格；"
        "⑥「等待期每年付 16.580pp」是按常数波动算的，如果等待期正好是低波 regime，实际等待费更低；"
        "⑦本面不宣称这个对冲值得做，只宣称「等」比「做」贵"),
}

# The state face carries the same fields; keep its own bookkeeping keys untouched.
STATE_FIELDS = dict(FIELDS)
STATE_FIELDS["本地未达 origin commit 数"] = 0
STATE_FIELDS["本地未达origin"] = 0
STATE_FIELDS["ˮλ"] = "healthy"


def main() -> int:
    with open(STATE, "r", encoding="utf-8") as fh:
        state = json.load(fh)
    prev = state.get("round_no")
    state["round_no_prev"] = prev
    state.update(STATE_FIELDS)
    state["next_pick"] = {
        "candidate": ("the two wait curves on one chart: fully unhedged vs BUDGET rule-A's "
                      "k=0.65 partial hedge"),
        "status": "open",
    }
    with open(STATE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    with open(HB_FIELDS, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(FIELDS, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    print("state round_no %s -> %s" % (prev, state.get("round_no")))
    print("heartbeat fields -> %s" % os.path.relpath(HB_FIELDS, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
