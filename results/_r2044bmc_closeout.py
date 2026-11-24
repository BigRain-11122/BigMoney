#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r2044 closeout (bm-c): state face + heartbeat field dict + round-report row.

Kept as a file rather than an inline command so the exact fields this round wrote are
auditable after the fact, and so the state face is rewritten with ITS OWN indent (2) and
the heartbeat with ITS OWN indent (1) -- r2043's self-catch: a writer that borrows the other
file's indent rewrites every line of a 900-line face invisibly.
"""
import datetime as dt
import io
import json
import subprocess
import time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = ROOT + r"\state-bm-c.json"
HB_FIELDS = ROOT + r"\results\_r2044bmc_hb_fields.json"
REPORT = ROOT + r"\fleet\round_reports-bm-c.md"

ROUND = 2044
FACE = "research/CASH_SHELF_INFLIGHT_CARRY.md"
JSON_FACE = "results/cash_shelf_inflight_carry.json"
SCRIPT = "scripts/cash_shelf_inflight_carry.py"
NEG = "results/_r2044bmc_inflight_negative.py"

WORK = (
    "r2044 · 新增文件面（竞争窗）：把 r2043 的「等待」从价格偏移改成成本读数——"
    "分批期间在途资金停在已发布的现金腿（GC001，含 0.1bp/张进场佣金）能挣回多少。"
    "读数一：票面 565,246 元买 511360 要 5 个交易日，r2043 的 p95 等待 264.5 元，"
    "扣掉 carry 后净 166.6 元（-37%），中位只要 20.65 元（0.37bp）；挣回份额中位 78.6%。"
    "读数二（本面的骨架）：等额分批把「多等的天数」压成 (n-1)/2 个满仓日，滑点与 carry "
    "乘的是同一个天数，于是两个量只剩一场每日期望比赛——短融价格每天走 0.794bp、"
    "回购腿每天付 0.624bp（净 0.183bp/日）。读数三：排期拉长时佣金按张数线性涨"
    "（39 日窗口 1.90bp），仍被 carry 压住，511360 的 39 日净等待 2.46bp（份额 84.9%）。"
    "读数四：转债是两面的——511380 两个交易日的净等待中位 -9.68 元（分批反而便宜），"
    "但 p95 2,775 元，所以判词分开给（WAIT_IS_PAID_IN_FULL 与 WAIT_WALKS_FASTER_THAN_THE_REPO_LEG）。"
)

VERIFY = (
    "cash_shelf_inflight_carry selftest 24/24 PASS | run rc0（40s，1539 bar × 5 货架 × 5 档）"
    " | --check rc0 CHECK OK（5 货架 / 17 个有窗档位逐位复算）"
    " | 负控 results/_r2044bmc_inflight_negative.py 7/7 rc0（手改一个数 rc3 / 上游字节变 rc3 且说 STALE / "
    "佣金臂分离后 carry 差额 == 0.1bp×(n-1)/2 逐位相等）"
    " | 上游滑点不重打：用 r2043 的 batch_slippage_bp 重算，与面里印的 1.5883/4.68bp 逐位相同"
    " | 竞争探针 rc=3（对端 interactive pid 51252 存活 39h 但 20s 只用 0.06s CPU、重叠窗 0 次写入）→ "
    "按 r1907 只落新增文件面，未跑 S6 链、未跑全量冒烟、未改共享代码/数据面"
)

NEXT = (
    "(a) 竞争窗关后首批：把 r2022–r2044 这批面接 S6 链腿与冒烟两腿并跑全量套件（≤48h，禁读成已全绿）；"
    "(b) 把「等 5 天只花 20 元、等 39 天也只花 2.5bp」这一句搬进 CEO 一页纸的现金腿节（≤48h，需改共享面）；"
    "(c) 在途资金只测了 GC001，下一步可比「停 GC007/停货币 ETF」同一窗的 carry（同一模块换 name 即可）"
)


def main():
    now = dt.datetime.now().astimezone()
    ts = now.strftime("%Y-%m-%dT%H:%M:%S%z")
    clock = now.strftime("%Y-%m-%dT%H:%M:%S") + now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:]

    # ---- state face (its own indent = 2, round-trip verified before writing)
    raw = io.open(STATE, encoding="utf-8", newline="").read()
    st = json.loads(raw)
    assert json.dumps(st, ensure_ascii=False, indent=2) + "\n" == raw, "state indent changed"
    st["round_no"] = ROUND
    st["ts"] = ts
    st["clock_read"] = clock
    st["当前任务"] = WORK
    st["当前任务_en"] = ("r2044: the wait is not a price offset but a cost -- park the unspent "
                         "cash in the published cash leg and the five-session build-out nets "
                         "166.6 CNY at p95 instead of 264.5")
    st["当前活"] = ("两个量乘同一个 (n-1)/2 个满仓日：短融每天走 0.794bp、回购腿每天付 0.624bp，"
                    "所以「等」的净代价只有滑点的两成分之一")
    st["当前活_en"] = ("r2044: slip and carry share the same (n-1)/2 wait-days, so the whole "
                       "question collapses to one per-day race")
    st["最新判词"] = ("CARRY_PAYS_MOST_OF_THE_WAIT:17 + WAIT_WALKS_FASTER_THAN_THE_REPO_LEG:14"
                      " + WAIT_IS_PAID_IN_FULL:3 + ONE_SESSION_NO_WAIT:8")
    st["最新实物"] = "%s + %s + %s（selftest 24/24·check rc0·负控 7/7）（%s）" % (
        FACE, JSON_FACE, SCRIPT, now.strftime("%Y-%m-%d %H:%M"))
    st["最近实物"] = st["最新实物"]
    st["下个里程碑"] = "(a) 二十余面接链+全量冒烟（≤48h）；(b) CEO 一页纸现金腿节加这一句（≤48h）"
    st["下轮指针"] = NEXT
    st["未验证"] = ("①佣金按交易所牌价假设（1 天期 0.1bp/张），未逐券商核；②在途资金只测停 GC001；"
                    "③价格用收盘（r2043 口径），不是次日开盘；④价格指数是价格不是全收益——若窗口内分红，"
                    "本面净等待是下界（已用「单日跌破 -5bp 天数」披露：511360 在 1539 根里 12 天）；"
                    "⑤窗口 2020-07-16 起，只有一段样本；⑥净等待 p50 是逐窗配对差的中位，不等于两列中位相减")
    st["竞争_r2044"] = ("repo_write_contention rc=3 CONTENTION：对端 interactive pid 51252（2026-11-22 20:10 起）"
                        "仍存活但 20s 仅 0.06s CPU、重叠窗 0 次写入，pid 68052 已退出；"
                        "22 张共享面在轮首前被写、0 张落在重叠窗 -> 按 r1907 只落新增文件面")
    st["deferred_r2044"] = ("竞争窗 rc=3 未跑：S6 链 / 全量冒烟 / attrition 守卫 / py_watermark+compute_audit / "
                            "update_daily 族；下轮（竞争窗关后）首批补跑，禁读成「全绿」")
    st["孤儿面"] = 0
    st["孤儿面_note"] = "round-zero orphan_face_probe: orphans 0, py_faces 3, resident_servers 1, killed 0"
    st["本地未达 origin commit 数"] = 0
    st["本地未达origin"] = 0
    st["记账_r2044"] = "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：把 carry 这个减法做成可复核读数属证据与载体）"
    st["watermark_verdict"] = "green (red=false; lane healthy; repo_write_contention rc=3 -> new-file faces only)"
    st["通过_r2044"] = ("orders 116 文件 / 归一回执 257 / 未回执 0；decisions.md 字节 sha 79e3083b… 未变=零动作；"
                        "idle_trigger green_idle=true 且池空/板空 -> 本轮自驱产品件即工作，--worked 清零")
    io.open(STATE, "w", encoding="utf-8", newline="").write(
        json.dumps(st, ensure_ascii=False, indent=2) + "\n")

    # ---- heartbeat field dict (heartbeat_write.py applies it merge-only, indent 1)
    fields = {
        "ts": ts,
        "clock_read": clock,
        "last_seen": ts,
        "heartbeat_epoch_utc": int(time.time()),
        "round_no": ROUND,
        "round": ROUND,
        "verdict": "healthy",
        "machine_id": "bm-c",
        "当前任务": "r2044 · %s" % JSON_FACE,
        "当前活": ("等额分批把多等的天数压成 (n-1)/2 个满仓日，滑点与回购 carry 乘同一个天数；"
                    "短融 0.794bp/日 vs 回购 0.624bp/日"),
        "最近实物": st["最近实物"],
        "下个里程碑": st["下个里程碑"],
        "孤儿面": 0,
        "idle_rounds": 0,
        "agenda_starved": False,
        "本地未达 origin commit 数": 0,
        "lane": "cb-cash-shelf",
        "orders_ack_note": "orders 116 / 归一回执 257 / 未回执 0（本轮零新增令）",
        "watermark_verdict": "green",
    }
    io.open(HB_FIELDS, "w", encoding="utf-8", newline="").write(
        json.dumps(fields, ensure_ascii=False, indent=2) + "\n")

    # ---- round report row (append-only, one fixed-field line)
    row = "| %s | r%d | %s | %s | %s |\n" % (ts, ROUND, WORK, VERIFY, NEXT)
    with io.open(REPORT, "a", encoding="utf-8", newline="") as f:
        f.write(row)

    print("state round_no -> %d ; hb fields -> %s ; report appended %d chars"
          % (ROUND, HB_FIELDS, len(row)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
