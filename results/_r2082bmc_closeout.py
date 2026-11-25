"""r2082 bm-c closeout: state + heartbeat + round-report line, one writer, idempotent.

The three faces are re-written from the same measured numbers so a rerun leaves them
byte-identical except for the clock fields (state/heartbeat are the only two allowed to
carry one -- D-20260930-18 content-addressed law is not violated by a bookkeeping file).
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CST = timezone(timedelta(hours=8))
NOW = datetime.now(CST)
ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
ROUND = 2082

ACTIVITY = (
    "r2082 · 水位绿 red=false · 竞争探针 CLEAN（单宿主）· 修复 CEO 一页纸 3 条红：" 
    "许可面把 baseline_published 判成 UNREADABLE，根因是它自己重判了一次恒等式（把「另一 bar 的相邻步进」"
    "当成恒等式破裂），而专门面 etf_book_k_identity_bar 早已判 IDENTITY_INTACT_LEG_READS_A_DIFFERENT_STEP；"
    "改为读该面结论（并只在票面同名+两数逐位相同时采信，L9/L10/L11 三条负控钉死），链条 "
    "UNREADABLE→ORDER_WITHIN_PERMISSION→NOTHING_OWED_TODAY→页面三行转绿；另修页面自检两腿的断言范围"
    "（把「金额不得出现在整页」收窄到溢价那一行：浮盈亏 ￥1,940 与溢价 ￥1,940 撞数导致假红）"
)

SAMPLES = {
    "CPU_load_pct": 9,
    "RAM_free_gb": 25.9,
    "RAM_total_gb": 55.9,
    "GPU_free_mib": 14073,
    "GPU_total_mib": 16384,
}

# ---- state ---------------------------------------------------------------
state_path = os.path.join(BASE, "state-bm-c.json")
with open(state_path, encoding="utf-8") as fh:
    state = json.load(fh)
state.update({
    "round_no": ROUND,
    "activity": "product",
    "activity_now": ACTIVITY,
    "activity_now_round": ROUND,
    "verdict": "healthy",
    "ahead_origin": 0,
    "behind_origin": 0,
    "agenda_starved": False,
    "idle_rounds": 0,
    "clock_read": ISO,
    "ts": ISO,
    "heartbeat_epoch_utc": EPOCH,
})
with open(state_path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, ensure_ascii=False, indent=1, sort_keys=True)
    fh.write("\n")

# ---- heartbeat -----------------------------------------------------------
hb_path = os.path.join(BASE, "fleet", "machines", "bm-c.json")
with open(hb_path, encoding="utf-8") as fh:
    hb = json.load(fh)
hd = hb if isinstance(hb, dict) else {}
hd.update({
    "machine_id": "bm-c",
    "verdict": "healthy",
    "activity": "product",
    "activity_now": ACTIVITY,
    "activity_now_round": str(ROUND),
    "last_seen": ISO,
    "ts": ISO,
    "clock_read": ISO,
    "heartbeat_epoch_utc": EPOCH,
    "CPU_load_pct": SAMPLES["CPU_load_pct"],
    "空闲RAM": "%.1f GB free / %.1f GB" % (SAMPLES["RAM_free_gb"], SAMPLES["RAM_total_gb"]),
    "GPU空闲VRAM": "%.1f GB free / %.0f GB" % (
        SAMPLES["GPU_free_mib"] / 1024.0, SAMPLES["GPU_total_mib"] / 1024.0),
    "idle_rounds": 0,
    "agenda_starved": False,
    "busy": False,
    "ahead_origin": "0",
    "behind_origin": "0",
    "batch": "none (wiring/repair round, no compute batch)",
    "artifacts": (
        "scripts/etf_book_rebalance_permission.py (selftest 11/11), "
        "scripts/ceo_live_usage.py (selftest ALL PASS), "
        "results/_r2082bmc_s6_chain.only-*.json (4/4 + 2/2 rc0), "
        "docs/live_usage/LIVE-2026-11-25.md"
    ),
    "carrier_debt_r2082": (
        "全量冒烟仍只到 logs/smoke_round2081b.log（跑至 capacity_rule 腿被杀，非红）；"
        "S6 全链本轮只跑受影响 6 腿；工作树 2,300+ 遗留脏件（11-23/11-24 bar 刷新 + 他机 lane 面 + "
        "上窗未提交研究件）本轮未吞并，只定向 add 本轮产出"
    ),
})
with open(hb_path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hd, fh, ensure_ascii=False, indent=1, sort_keys=True)
    fh.write("\n")

# ---- heartbeat self-check (smoke F7 is picky about the two clock fields) --
with open(hb_path, encoding="utf-8") as fh:
    back = json.load(fh)
assert isinstance(back["heartbeat_epoch_utc"], int), back["heartbeat_epoch_utc"]
assert "T" in back["clock_read"] and "+" in back["clock_read"], back["clock_read"]

# ---- round report --------------------------------------------------------
line = (
    "| %s | r%d | bm-c | **PRODUCT（S1 修红闭环）**：上一窗冒烟留下 3 条红（CEO 一页纸 "
    "`single-sheet coin flip` / `missing premium face` / `premium off another ticket`），根因不在页面而在上游："
    "`etf_book_rebalance_permission` 把 `baseline_published` 判成 UNREADABLE —— 它自己重判了 k 恒等式，"
    "把「同一张 schedule 的相邻两步」（票面 k_rule=0.458463 在 2026-11-20，cell k=0.460253 在 2026-10-23）"
    "当成「恒等式破裂」，而专门面 `etf_book_k_identity_bar` 早已判 "
    "`IDENTITY_INTACT_LEG_READS_A_DIFFERENT_STEP`。正法=读者读生产者的结论（r1852），但只在这张 receipt "
    "点名同一张票、且两个数与 cell/ticket 逐位相同（IDENT_TOL=1e-6）时才采信：新增 L8（采信→baseline 记为 path）、"
    "L9（receipt 点名另一张票→不采信）、L10（receipt 记的是另一对数→不采信）、L11（receipt 说 BROKEN→拒），"
    "原 L5「破恒等式必须拒」保留，selftest **11/11**。重跑链条：许可面 UNREADABLE→"
    "`KEEP_SUPPORTED_BY_INDEPENDENT_PATH`（permitted_k=0.435003，keep=True）→ 缺口面 `ORDER_WITHIN_PERMISSION`"
    "（无裁量）→ 时点面 `NOTHING_OWED_TODAY`（k=1 行 mean -1786 CNY / share_late_helps 41.4%）→ CEO 页三行转绿。"
    "第二枚（同窗自捕）：页面两条 r1820 腿把「溢价金额不得出现」断言在整个页面上，而页里另有一笔 **￥1,940** "
    "的持仓浮盈亏与溢价 ￥1,940 撞数 → 正确拒绝反被判红；正法=断言收窄到「这笔钱里有多少是溢价」那一行"
    "（新增 `_prem_line`），不删任何断言、不放宽判据。| 证据：scripts/etf_book_rebalance_permission.py（selftest "
    "**11/11**）+ results/etf_book_rebalance_permission.json（verdict/permitted_k/readings 全重生）+ "
    "scripts/ceo_live_usage.py（selftest **ALL PASS**）+ results/_r2082bmc_s6_chain.only-*.json"
    "（rebalance/cut_order_gap 4/4 rc0、do_or_wait+ceo_live_usage 2/2 rc0）+ docs/live_usage/LIVE-2026-11-25.md"
    "（state=RED/rung=RED/cap=20%/heat=COOL）| 未做（如实）：全量冒烟未重跑（上窗日志跑到 capacity_rule 腿被杀，"
    "该腿单独 selftest **19/19** PASS，非真红）；S6 全链只跑受影响 6 腿；工作树 2,300+ 遗留脏件未吞并 | "
    "S0.5 双扫：本轮未发现新增 @bm-c 令（fleet/orders 面与心跳 ack 差集由上窗实测 0 件未回执）| "
    "S7：orphan_face_probe（py_faces=3 / orphans=0 / resident_servers=2）；竞争探针 rc=0 CLEAN（单宿主 pid=84280）| "
    "**本地未达 origin commit 数**：commit 前实测 0/0 | 下轮指针：(a) 静窗后跑全量冒烟并把这 4 条新负控一并收编；"
    "(b) 把「哪张面读了哪张面的结论」写进 chain_writer_audit 的读边（receipt 消费者）；(c) 遗留 2,300+ 脏件按 lane "
    "归属分批提交或交还他机 | **CEO 三行**：当前活＝修好让 CEO 页每天能算「今天做还是分开做」的那条链（许可→缺口→时点）"
    "｜最近实物=`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\docs\\live_usage\\LIVE-2026-11-25.md`（"
    + NOW.strftime("%Y-%m-%dT%H:%M") + " 生成·selftest ALL PASS）"
    "｜下个里程碑＝全量冒烟补跑 + 遗留脏件分批归属（≤48h）| 记账：轮报告 1 + state 1 + 心跳 1 = 3（背账 3 处含轮报告）|"
)
line = line.replace("%s", ISO, 1).replace("%d", str(ROUND), 1)
rr_path = os.path.join(BASE, "round_reports-bm-c.md")
with open(rr_path, "a", encoding="utf-8", newline="\n") as fh:
    fh.write("\n" + line + "\n")

print("closeout ok:", ISO, "round", ROUND)
print("heartbeat epoch type:", type(back["heartbeat_epoch_utc"]).__name__)
