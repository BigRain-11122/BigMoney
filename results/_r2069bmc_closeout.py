# -*- coding: utf-8 -*-
"""r2069 closeout: state + heartbeat + round report row (single pass)."""
import datetime as dt
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HEART = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")

now = dt.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
utc_epoch = int(now.timestamp())


def ahead():
    try:
        out = subprocess.run(["git", "-C", ROOT, "rev-list", "--count", "origin/main..HEAD"],
                             capture_output=True, text=True, timeout=60)
        return out.stdout.strip() or "?"
    except Exception:
        return "?"


AHEAD = ahead()

WORK = ("r2069 · 新增文件面（竞争窗 rc=3）：把块看板的「落后」按官方交易日历重算，"
        "发现容差字段 holiday_allow_days 比的是**日历日**——同一个缺口按星期几跑红绿两色："
        "缺 3 个交易日时板算 3–5 天（周一周二绿、周三起红），缺 4 个交易日时 4–6 天。"
        "今天五条 dir_bar_fresh 里：D1/D4 当前、D2/D3 是源未发布（生产者自己写在 "
        "index_daily_update_status 里，r1852：读者别再判一遍）、D6 真落后——板印 5 天，"
        "日历事实 **2 个交易日**（11-23、11-24）。五条的日历差全都不是交易日差。")

UNVERIFIED = ("①只描述不修板（block_board.py 是共享面，补丁 PROVEN_NOT_APPLIED）；"
              "②未跑全量冒烟与 S6 链（竞争窗禁止项）；"
              "③index_daily 未登记进 data_lane_freshness 车道表（共享面）；"
              "④data/index_daily 四只仍停在 11-23，来源端未发布，本面只携带生产者原话不代抓")

NEXT = ("(a) 竞争窗关后按面里 patch.shape 把 block_board 的 expected/allow 改到交易日，"
        "再跑本面看 numbers_disagree 是否归零（≤48h）；"
        "(b) 给 index_daily 补一条 freshness 车道登记（共享面，静窗）；"
        "(c) 全量冒烟 + S6 分批补跑（连续第 14 轮未跑，≤48h）")

with io.open(STATE, encoding="utf-8") as fh:
    st = json.load(fh)
before_keys = len(st)

st["round_no"] = 2069
st["who_did"] = "bm-c"
st["who_did_r"] = 2069
st["当前任务"] = WORK
st["当前活"] = "把「这条车道落后几天」从日历日换成交易日，并证明容差本身会随时钟翻色"
st["最新判词"] = "TOLERANCE_IS_IN_THE_WRONG_UNIT"
st["最新实物"] = "research/LANE_LAG_UNIT_GUARD.md + results/lane_lag_unit_guard.json @%s" % ts
st["最近实物"] = ("scripts/lane_lag_unit_guard.py（selftest 28/28 · --check rc0 · 负控 15/15）"
               "+ research/LANE_LAG_UNIT_GUARD.md")
st["最近实物_update"] = "results/lane_lag_unit_guard.json @%s" % ts
st["未验证"] = UNVERIFIED
st["未验证_r2069"] = UNVERIFIED
st["下轮指针"] = NEXT
st["下个里程碑"] = "(a) 补丁落 block_board 后 numbers_disagree 归零；(b) 全量冒烟 + S6 收口（≤48h）"
st["本轮"] = WORK
st["孤儿面"] = "0"
st["孤儿面_note"] = "round-zero orphan_face_probe: orphans 0 (py_faces 4, resident_servers 2)"
st["竞争_r2069"] = ("repo_write_contention rc=3 CONTENTION：对端 interactive pid 79608"
                 "（codely.exe，2026-11-24T22:39 起、age 307.7m）在轮首前写过 15 张共享面、"
                 "重叠窗内不可归因 0 张 -> 按 r1907 只落新增文件面，未改共享面、未跑 S6 链、"
                 "未跑全量冒烟")
st["通过_r2069"] = ("orders 117 件 vs 心跳 orders_ack 331（state 面 273）-> 未回执 0；"
                  "face_divergence 已用 Tools/orders_ack_append.py 补齐"
                  "（O-20261124-2300-bm-c）后 rc0 CLEAN；origin/main:docs/decisions.md 原生字节 "
                  "250,586B sha256 79e3083b85c130b8… == 自持水位 -> 零新决策零动作；"
                  "attrition_ledger_guard CLEAN（4 件·三条历史缩行 healed 照录）")
st["记账_r2069"] = ("轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：把"
                  "「容差必须和数据同单位」做成可复核读数属证据与载体；方法论卡锁存待无竞争轮）")
st["本地未达 origin commit 数"] = AHEAD
st["本地未达origin"] = AHEAD
st["送达自证_r2069"] = "pending-push"

with io.open(STATE, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
print("state: round_no=%s keys %d->%d ahead=%s" % (st["round_no"], before_keys, len(st), AHEAD))

with io.open(HEART, encoding="utf-8") as fh:
    hb = json.load(fh)
hb["machine_id"] = "bm-c"
hb["last_seen"] = ts
hb["ts"] = ts
hb["clock_read"] = ts
hb["heartbeat_epoch_utc"] = utc_epoch
hb["当前任务"] = WORK
hb["current_task"] = WORK
hb["round_no"] = 2069
hb["verdict"] = "healthy"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphans"] = 0
hb["orders_ack"] = sorted(set(hb.get("orders_ack") or []) | {"O-20261124-2300-bm-c.md"})
hb["did"] = ("r2069: recomputed every dir_bar_fresh block in trading days; the board's "
             "holiday_allow_days tolerance is compared against calendar days, so a 3-day "
             "outage reads green on Mon/Tue and red from Wed; D6 prints 5d, the calendar "
             "says 2 trading days")

with io.open(HEART, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
assert isinstance(json.load(io.open(HEART, encoding="utf-8"))["heartbeat_epoch_utc"], int)
print("heartbeat: ack=%d epoch=%d" % (len(hb["orders_ack"]), utc_epoch))

row = (
    "%s | r2069 | bm-c | **PRODUCT（产品优先律·watermark 绿（red=false·lane=healthy·"
    "next_pick 他机 claimed）·孤儿面=0（py_faces=4 / orphans=0 / resident_servers=2）·"
    "竞争窗 rc=3 CONTENTION〔对端 codely.exe pid 79608 自 2026-11-24T22:39 起 307.7min、"
    "15 张共享面在轮首前被动过、重叠窗内不可归因 0 张，证据 "
    "results/_repo_write_contention.bm-c.json〕→ 按 r1907/r1927 只落新增文件面："
    "未改共享面、未重跑 S6 链、未跑全量冒烟）**：块看板判断「这条车道落后几天」用的容差叫 "
    "`holiday_allow_days`，比的却是**日历日**——于是同一个缺口按星期几跑红绿两色："
    "缺 3 个交易日时板算 3–5 天（周一周二绿、周三起红），缺 4 个交易日时 4–6 天，"
    "**一个死了三天的车道有 40%% 的时间显示绿色**。今天五条 dir_bar_fresh 逐条重算："
    "D1 期货（tail 11-24）、D4 A股（11-24）当前；D2 指数、D3 ETF（tail 11-23）是"
    "**源还没发布**——D2 的生产者自己在 `results/index_daily_update_status.json` 里写了 "
    "`reason=\"vendor has not published past 2026-11-23\"`，按 r1852 读者不再自己判一遍，"
    "转合法第三态 PENDING；D6 回购真落后：**板印 5 天，日历事实 2 个交易日（11-23、11-24）**，"
    "五条的日历差全都不是交易日差。"
    "| scripts/lane_lag_unit_guard.py（selftest **28/28 OK**·run rc0 verdict="
    "TOLERANCE_IS_IN_THE_WRONG_UNIT·--check **CHECK OK** rc0·负控 "
    "results/_r2069bmc_lane_lag_negative.py **15/15 OK**：改一格→rc3 且句含 CHECK FAILED "
    "且**不含** STALE／动 inputs_digest→rc3 且含 STALE 且不含 CHECK FAILED／页面 marker 块"
    "被改→rc3／每次复原 sha256 逐字节相同且回 rc0／classify 四方向是函数不是常量）"
    "+ results/lane_lag_unit_guard.json + research/LANE_LAG_UNIT_GUARD.md + "
    "qa/lane-lag-unit-guard-r2069.md。**自捕**：首版把「源还没发布」也算 LATE，D2/D3 被判 "
    "GREEN_IS_PREMATURE（假红）——正法不是放宽腿，是读生产者自己写的那句话，改三态后转 "
    "AGREE_PENDING；另有一条自检腿把 2026-11-21（周六）当尾巴，红的断言错不是代码错。"
    "**未做（如实）**：block_board.py 零改动（共享面·补丁 PROVEN_NOT_APPLIED 形状写进面）；"
    "全量冒烟连续第 14 轮未跑；S6 链连续第 14 轮未跑；index_daily 未登记进 freshness 车道表。"
    "| S0.5 双扫：fleet/orders 117 件、本机回执 331 条（state 面 273）、**未回执 0 件**；"
    "face_divergence 用 Tools/orders_ack_append.py 补齐后 rc0 CLEAN；"
    "origin/main:docs/decisions.md 原生字节 250,586B sha256 79e3083b85c130b8… **== 自持水位**"
    "（零新决策零动作）；fleet/inbox 空。"
    "| S7：attrition tripwire **CLEAN**（4 件·三条历史缩行 healed 照录）；"
    "schtasks 自愈本轮未触碰（对端在飞，重注册会打断在飞轮）。"
    "| **本地未达 origin commit 数**：commit 前实测 origin/main...HEAD = %s。"
    "| 下轮指针：%s。"
    "| **CEO 三行**：当前活＝把「这条车道落后几天」从日历日换成交易日，并证明容差本身会"
    "随时钟翻色｜最近实物=K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\"
    "LANE_LAG_UNIT_GUARD.md（%s·selftest 28/28·负控 15/15·--check rc0）｜"
    "下个里程碑＝补丁落 block_board 后 numbers_disagree 归零 + 全量冒烟收口（≤48h）。"
    "| 记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3。\n"
) % (ts, AHEAD, NEXT, ts)

with io.open(REPORT, "a", encoding="utf-8", newline="\n") as fh:
    fh.write("\n" + row)
print("report row written")
