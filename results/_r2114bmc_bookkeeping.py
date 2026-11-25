#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r2114 bookkeeping writer: one round-report row + state + heartbeat.

Written as a fresh read-modify-write per file (r109/r16: never replace a shared ledger in
place from a stale snapshot). Idempotent by construction: the round row is appended only if
its first field is not already present.
"""
from __future__ import print_function

import io
import json
import os
import time
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../quant/bigmoney
ROUND = 2114
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
CLOCK = NOW.strftime("%Y-%m-%dT%H:%M:%S%z")
CLOCK = CLOCK[:-2] + ":" + CLOCK[-2:]
EPOCH = int(time.time())
STAMP = NOW.strftime("%Y-%m-%dT%H:%M+08:00")

ROW = (
    "{stamp} | r{n} | bm-c | **单一宿主窗**（`results/_repo_write_contention.bm-c.json` rc0 **CLEAN**："
    "「fewer than two codely hosts alive」，对手 interactive 98008 已退出；但工作树仍脏 ~1,950 件"
    "（对端的 `Tools/page_fmt_guard_v2.py` 一族与 `data/daily` 面板未提交面）→ 按 r1907 仍只落**新增文件面**，"
    "不改 `Tools/s6_chain_bmc.py`/`smoke_test.py`/`data/`，不跑全量冒烟）。watermark verdict=**绿**"
    "（`results/watermark_red.json` red=false lane=healthy）。"
    "**PRODUCT**：把 r2113 那个「+0.208 夏普」的重配第一次拿去做可持有性检查——每套权重都有一条**下限**"
    "（每条期货腿能持有一整手的 NAV＝每手名义额÷权重）和一条**上限**（权益袖碰 1% ADV 线的 NAV＝容量线资本÷权益权重）。"
    "档 1/1 结果：**现在这套权重窗口开着 [1,000,000, 2,401,198]**（今日口径，中位 1,142,112／最差 784,076），"
    "而**等风险重配没有任何资本放得下**：两条期货腿的整手地板是 **2,789,167 元**（约束腿 IM：1,086,880÷0.389679），"
    "权益袖 1.000×NAV 在 **1,043,801 元** 就顶到线——下限是今日上限的 **2.67 倍**，缓冲是负的。"
    "三件要紧的：①**两端不是同一把尺子驱动的**——下限由每手名义额（IC 1,153,800／IM 1,086,880，2026-11-25 收盘）"
    "决定，上限由容量面 60 个 session 的成交额决定，同一套权重在两者之间被夹死，不是「市场不够深」也不是「资本不够」；"
    "②**慢的会是权益那一端**——权益袖的 1% ADV 线在 60 个 session 里从 34.1 万到 104.4 万（中位 49.6 万），"
    "「满仓权益」的容量是一个 3 倍宽的区间而不是一个数；③**把窗口打开的最小改动是 0.3742**——在同一资本（2,789,167）上"
    "把权益袖从 1.000 压到 ≤0.3742×NAV，重配的其它腿不用动。跨面对账：容量面摘要 vs 本面从 sessions 重算 "
    "**CROSS_FACE_MATCHES**（中位 496,476=496,476，最差 340,838=340,838）；`idx_fut_carry_open_capital` 的首档"
    "（IC 1,132,145／IM 1,161,161）是「每手波动÷8% 预算」那把尺子，与每手名义额比值 0.9812／1.0683 → "
    "**DIFFERENT_RULER_NAMED**，两个数不取平均。｜证据：`--selftest` **19/19**；`check` **CHECK_OK**"
    "（输入 sha 漂移说 STALE、同输入数字不符说 CHECK FAILED 且**不带 STALE**、页面不能从发布面重渲染也说 STALE）；"
    "负控 `python results/_r2114bmc_floor_negative.py` **25/25 ALL_CONTROLS_PASS**（手改窗口数字→CHECK FAILED 无 STALE／"
    "改输入 sha→STALE／改页面→STALE／复原→绿／页面无字面 `%%`／每手名义额与保证金面逐位相同／中位口径=上游的上中位／"
    "每档下限=各腿地板取大／上限=容量÷权益权重／0/1 档不许凭空长出一个重配）。面 "
    "`results/idx_fut_carry_rebudget_floor.json`、页面 `research/IDX_FUT_CARRY_REBUDGET_FLOOR.md`、"
    "QA `qa/rebudget-floor-r2114.md`。｜本轮自捕两枚：①中位数首版用「两中值平均」（492,295.89），"
    "而容量面用的是**上中位**（496,475.93）——同一批 60 个 session 两个估计量会印成两个答案（r1911 族），"
    "改成沿用上游定义并在源码注释里写清来历；②自检断言「页面报红时输出含 page」，实际文案是 "
    "「does not re-render from the published face」——断言写错不是判据错，改断言不放松判据。"
    "另记一枚工具坑：裸 `python -` 在 PowerShell 里会进交互式 stdin **挂死 5 分钟**被工具取消（本窗实测），"
    "一切探针一律落文件再跑，禁 `python -`。｜未做（如实）：①未接进 `Tools/s6_chain_bmc.py` 与 `smoke_test.py`"
    "（`Tools/s6_chain_bmc.py` 开工时已是对端未提交脏面 +45 行）；②未改 r2113 的重配权重（选择在那面）；"
    "③权益容量只覆盖容量面自己五个名字，更宽票池只声明方向不猜数值；④全量冒烟未跑。｜S0.5 双扫：fleet/orders "
    "**117 件** vs 心跳 orders_ack 归 **258** → **未回执 0**；集团 `origin/main:docs/decisions.md` 原生字节 "
    "**250,586 B sha256 79e3083b85c130b8…** == 自持水位 → **零新决策零动作**（`git cat-file blob` 直落字节、"
    "不带 2>&1、不经 PS 字符串往返）。｜S7：孤儿面=**0**（py_faces=4 / resident_servers=2，"
    "`results/_orphan_face_probe.bm-c.json`）；Bigmoney-IterationLoop 幂等 no-op（pin=0 current=0 PT5H）；"
    "Watchdog 重注册成功但 **S4U XML 翻转仍被拒（拒绝访问）**=需一次提权（carried，非本轮引入）；"
    "pre-commit / pre-push 两爪重装（LF 归一）；`attrition_ledger_guard scan` **CLEAN**（4 账本，2 处历史缩行 healed 照录）；"
    "静态闸 `Tools/page_fmt_guard.py scan` 对本轮新页**零命中**（仓内他人脚本那 31 处字面 `%%` 仍未修，属他人面）。"
    "｜**CEO 三行**：当前活＝把 r2113 那条「重配 +0.208 夏普」从纸面算术推进到「这套权重在哪个资本区间能被持有」"
    "｜最近实物=`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\IDX_FUT_CARRY_REBUDGET_FLOOR.md`"
    "（2026-11-26T02:1x·现在这套窗口 100 万→240 万开着·重配地板 279 万 > 权益线 104 万·把窗口打开的最小改动=权益权重 0.3742）"
    "｜下个里程碑＝把这面接进链与冒烟腿，并把 0.3742 这条「容量可行权重」与 8% 波动目标并排成一条可执行仓位规则（需独占窗，≤48h）"
    "| 记账：轮报告 1 处 + 页面 1 件（脚本渲染）+ QA 1 件 = 3"
).format(stamp=STAMP, n=ROUND)

# ---------------------------------------------------------------- round report
rr = os.path.join(ROOT, "round_reports-bm-c.md")
existing = ""
if os.path.exists(rr):
    with io.open(rr, "r", encoding="utf-8") as fh:
        existing = fh.read()
if ("| r{} |".format(ROUND) + " bm-c |") in existing or ("| r{} |".format(ROUND)) in existing:
    print("round row already present, not appended twice")
else:
    sep = "" if (not existing or existing.endswith("\n")) else "\n"
    with io.open(rr, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(sep + ROW + "\n")
    print("round row appended")

# ---------------------------------------------------------------- state
sp = os.path.join(ROOT, "state-bm-c.json")
with io.open(sp, "r", encoding="utf-8") as fh:
    st = json.load(fh)
prev_round = st.get("round_no")
st["round_no"] = ROUND
st["round_no_prev"] = prev_round
st["round_no_note"] = ("prev value was {} while the report rows had already reached r2113 "
                       "(shared state face written by concurrent hosts); set to the next free "
                       "number after the last report row instead of prev+1".format(prev_round))
st["ts"] = CLOCK
st["updated"] = STAMP
st["clock_read"] = CLOCK
st["heartbeat_epoch_utc"] = EPOCH
st["verdict"] = ("lane healthy: r2114 -- the equal-risk re-budget has no capital at which it "
                 "can be held (floor 2,789,167 vs equity ADV ceiling 1,043,801)")
st["当前活"] = ("把 r2113 的重配从纸面算术推进到可持有性：每条权重集的整手地板与 1% ADV 上限"
              "之间有没有资本窗口")
st["最近实物"] = ("research/IDX_FUT_CARRY_REBUDGET_FLOOR.md + results/idx_fut_carry_rebudget_floor.json"
                "（2026-11-26T02:1x：现在这套窗口 1.00M→2.40M 开着；重配地板 2.79M > 权益线 1.04M，2.67 倍）")
st["下个里程碑"] = ("把这面接进链与冒烟腿，并把「容量可行权重 0.3742」与 8% 波动目标并排成一条可执行仓位规则（需独占窗，≤48h）")
st["孤儿面"] = 0
st["孤儿面_note"] = "round-zero orphan_face_probe: orphans 0 (py_faces 4, resident_servers 2)"
st["watermark_verdict"] = "green red=false lane=healthy"
st["竞争_r2114"] = ("rc0 CLEAN（results/_repo_write_contention.bm-c.json：fewer than two codely hosts alive）；"
                   "工作树仍脏 ~1,950 件（对端未提交面）→ 仍只落新增文件面")
st["s05_r2114"] = ("orders 117 件 vs 心跳 orders_ack 258 → 未回执 0；origin/main:docs/decisions.md 原始字节 "
                   "250,586 B sha256 79e3083b85c130b8… == 水位 → 零新决策零动作")
st["s7_r2114"] = ("orphans 0；IterationLoop 幂等 no-op（pin0/PT5H）；Watchdog 重注册 OK 但 S4U XML 翻转被拒"
                  "（需提权，carried）；pre-commit/pre-push 重装 LF 归一；attrition CLEAN（4 账本 2 处历史缩行 healed）")
st["verify_r2114"] = ("selftest 19/19；check CHECK_OK；负控 25/25 ALL_CONTROLS_PASS；page_fmt_guard 对本页零命中；"
                      "跨面 capacity MEDIAN/WORST 逐位相同、open_capital 命名为 DIFFERENT_RULER_NAMED（0.9812/1.0683）")
st["记账_r2114"] = "轮报告 1 处 + 页面 1 件（脚本渲染）+ QA 1 件 = 3"
st["本轮"] = ("r2114：重配的资本窗口 = [整手地板 2,789,167, 权益 ADV 上限 1,043,801] → FLOOR_ABOVE_CAPACITY；"
            "现在这套 = [1,000,000, 2,401,198] WINDOW_OPEN；容量可行权益权重 0.3742")
st["未验证"] = ("①全量冒烟未跑（本窗时长），禁读成已全绿；②本面未接进链与冒烟腿（共享脏面）；"
               "③权益容量只覆盖容量面五个名字；④重配的夏普增益是历史分段算术，不是承诺")
st["本地未达 origin commit 数"] = 0
st["status"] = "healthy"

with io.open(sp, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps(st, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
print("state written round_no={}".format(st["round_no"]))

# ---------------------------------------------------------------- heartbeat
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with io.open(hp, "r", encoding="utf-8") as fh:
    hb = json.load(fh)
hb["last_seen"] = STAMP
hb["ts"] = CLOCK
hb["clock_read"] = CLOCK
hb["heartbeat_epoch_utc"] = int(EPOCH)
hb["task"] = "r2114 重配的资本窗口（整手地板 vs 1% ADV 上限）"
hb["verdict"] = ("lane healthy: r2114 -- re-budget floor 2,789,167 vs equity ADV ceiling 1,043,801 "
                 "(2.67x over); as-built window [1.00M, 2.40M] open")
hb["cpu核"] = 32
hb["空闲RAM"] = "25.4 GB free / 55.9 GB"
hb["GPU空闲VRAM"] = "14.0 GB free / 16.0 GB"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["did"] = ("r2114: results/idx_fut_carry_rebudget_floor.json + research/IDX_FUT_CARRY_REBUDGET_FLOOR.md "
             "+ qa/rebudget-floor-r2114.md (selftest 19/19, check OK, 25/25 controls)")
with io.open(hp, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps(hb, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
print("heartbeat written epoch_is_int={}".format(isinstance(hb["heartbeat_epoch_utc"], int)))
