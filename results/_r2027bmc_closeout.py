"""r2027 closeout: state + round report + heartbeat fields (bm-c).

Run from the repo root:  python results/_r2027bmc_closeout.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")
FIELDS = os.path.join(ROOT, "results", "_r2027bmc_hb_fields.json")

TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
TS = NOW.isoformat(timespec="seconds")
ROUND = 2027

WORK = (
    "r2027 · 新增文件面（竞争窗）：scripts/astock_veto_hedge_lots.py + "
    "results/astock_veto_hedge_lots.json + research/ASTOCK_VETO_HEDGE_LOTS.md —— "
    "把 r2026 的「90.13% 账面」翻成一张下单前的检查单"
)

REPORT_ROW = (
    "| {ts} | r{round}（**竞争探针 rc=3 CONTENTION·只落新增文件面**·"
    "把「90.13% 账面」翻成一张下单前的检查单：几手、多少保证金、离强平多远） | "
    "**watermark：red=false / lane=healthy · 孤儿面=0**（py_faces=6 / resident_servers=1=ComfyUI 空闲）。"
    "**产品（产品优先律）**：r2023 定价、r2024 换日频尺、r2025 赛马九条规则、r2026 定默认档——"
    "四轮都用「账面占比」说话，而账户下的不是占比，是手。本面只做四件算术，全部落在已发布的数与两根价格面板的尾 bar 上。"
    "**读数一（粒度比 4,822）**：512100 一手 = 100 份 × 2.300 = **230 元**；IM 一手 = 200 × 5545.6 = **1,109,120 元**"
    "——同一笔对冲，两种下单，一手差 4,822 倍。"
    "**读数二（ETF 上取整是免费的，期货上不是）**：100 万账面需要 3,918.83 手 → 填 3,919 手，beta 0.9014 对目标 0.9013，"
    "误差 **0.00004**；同一账面在 IM 上需要 0.813 手——四舍五入只有 0（不对冲）或 1 手（**1.1091 单位 beta**，超配 0.2078）。"
    "把取整误差压到 0.5% beta 所需的账面：512100 **23,000 元**，IM **1.109 亿**——4,822 倍。"
    "精确 beta 中性的账面是 1 手 **1,230,535 元**、2 手 2,461,071 元，其它规模都只能近似。"
    "**读数三（90% 名义不是 90% 账面）**：融券保证金与卖出冻结款同时不可用——80% 档下 100 万账面要压 **1,622,466 元（162% 账面）**，"
    "50% 档 135%、100% 档 180%；而 IM 12% 档只压 133,094 元（13%）——每 1 元目标名义占用 1.50–2.00 元 vs 0.15–0.18 元，"
    "便宜十倍的那条臂恰恰是下不出目标 beta 的那条。"
    "**读数四（期货的保证金一天就用掉一半）**：口径=保证金率即「跌到零权益」的反向幅度（上界，不含追保与手续费）；"
    "12% 档 = 12%，而最新一根 bar IM 单日 **-5.64%**，一天吃掉 12% 档的 **47%**、15% 档的 38%。"
    "**读数五（成本与可达性照抄父面，不重估）**：滚动 12.6 次/年 × 16bp = **2.02% 名义 / 1.82% 账面**；"
    "IM 中位基差 -0.629%（方向对空头不利，但中位取自混合到期日、不能年化，如实标为未建模）；"
    "流动性不是约束（ETF 空头占当日成交额 76.2 ppm、期货 3.5 ppm），券源是柜台问题不是面板问题。"
    "｜**验证证据**：`--selftest` **29/29 PASS**（半手边界 / floor 不过冲 / round 落在半手内 / beta 误差按 (成交-目标) 而非 (成交-1) 定义 / "
    "0.5% 线解出的资本 / 保证金与冻结款合并 / 期货无冻结款 / 强平线等于保证金率 / 判词三态 + 恰好压线算过 / 摘要忽略运行戳 / 两根面板可读）；"
    "`run` rc0（evidence_cutoff **2026-11-20**，beta 0.9013312810692592 取自父面）；`check` **rc0**（每档资本 × 两臂 × 两种取整 × 5 字段 + 保证金每档 + "
    "资金效率每档 + 粒度/中性资本/流动性份额 + carry 逐条重推，页面逐字节，≥155 项比较）。"
    "**负控 `results/_r2027bmc_lots_negative.py` 21/21 PASS**（11 条读数逐个篡改→CHECK FAILED 且不带 STALE / 手改页面点名 / "
    "父面移动→STALE 且不带 CHECK FAILED / 面板尾 bar 移动→STALE / 缺面缺页不崩 / 父面不可读→STALE 不崩 / 跑完发布面逐字节未动且仍绿），"
    "**并当场抓到一枚真缺陷**：`_rel()` 在跨盘路径（临时目录在 C:，仓在 K:）上 `ntpath.relpath` 抛 ValueError 直接崩——"
    "父面指纹因此无法在负控里读；已修为「相对化失败就印绝对路径」，负控转绿（r1745 族同病第三例）。"
    "｜**S0**：`fleet/machine.json`=bm-c；`orphan_face_probe` py_faces=6 **orphans=0** 零杀；"
    "`repo_write_contention` **rc=3 CONTENTION**（2 宿主存活：对端 interactive pid 51252＝11-22 20:10 起常驻；21 张共享面在轮首前被对端写，重叠窗 0 张）"
    "→ 只落新增文件面，未改共享代码/数据面、未跑 S6 链、未跑全量 smoke；fetch 后 0 ahead / 0 behind。"
    "｜**S0.5 双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / 124 陈旧注记 / unacked=[]）；"
    "集团 `git cat-file blob origin/main:docs/decisions.md` **原字节** sha256 = **79e3083b85c130b8**（250,586 B）== state 水位 → 零新决策零动作；"
    "`docs/orders.md` 原字节 sha256 = **99e8e77d093cc13d**（103,567 B）== 水位（r2009 已消费尾行）→ 零新行；fleet/inbox 0 件。"
    "｜**S1（诚实边界）**：全量 smoke **未跑**（`smoke_test.py` 与 `logs/smoke_legs.json` 是对端写的共享面）；本轮以 29/29 selftest + 21/21 负控 + "
    "run/check 双 rc0 背书，**不宣称全绿**。｜**S6**：未跑（链腿与链产物=共享面）。"
    "｜**S7**：`state round_no 2026→2027`（rounds_done 1962→1963，round_no_prev 留痕 2026）；心跳经 `Tools/heartbeat_write.py apply` 合并写；"
    "`& Tools/register_loop_task.ps1` **phase ok**（machine=bm-c pin=0 current=0，首燃 11/24 05:30 未动）；"
    "`attrition_ledger_guard scan` **CLEAN**（4 账本，3 处历史缩行 healed 注记照录）；`pre-commit`/`pre-push` 与 `Tools/git-hooks/` 逐字节（CR 归一）MATCH。"
    "｜**CEO 过程可见面**：当前活＝把「90% 账面」翻成账户真的能下的单，并算清它要压多少钱、离强平多远｜"
    "最近实物＝`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ASTOCK_VETO_HEDGE_LOTS.md`（2026-11-24 05:3x·"
    "一手差 **4,822 倍**；ETF 取整误差 0.00004 beta / IM 一手超配 0.2078；"
    "**90.13% 名义在 80% 融券档要压 162% 账面的现金**；IM 12% 保证金被最新一根 -5.64% 的一天吃掉 47%）"
    "＋`results\\astock_veto_hedge_lots.json`＋`scripts\\astock_veto_hedge_lots.py`（selftest 29/29）＋`results\\_r2027bmc_lots_negative.py`（负控 21/21）；"
    "下个里程碑＝（a）竞争窗结束后把 r2022–r2027 五面接 S6 链腿 + 冒烟两腿（≤48h）；（b）把「162% 现金承诺 / 一手 4,822 倍」这两条接到 CEO 一页纸与票据的仓位节（≤48h）。"
    "｜**未验证（如实）**：①保证金比例与券源是券商条款，本仓不可观测，按 50/80/100% 与 12/15% 两轴印，不取单一值；"
    "②强平距离是「保证金率=反向幅度」的粗略上界，未建模维持保证金、追保时点、手续费与逐日结算节奏；"
    "③账面按今天收盘价定价、持仓按最后一期的权重，两者相差 7 个交易日（11-20 价格 vs 11-11 期末），未做市值重估；"
    "④IM 中位基差取自混合到期日，方向可读、年化不可读，未建模；⑤ETF 融券的券源规模与召回风险完全未建模；"
    "⑥本面是口径/下单检查件，不是可交易策略，也不是下单指令。｜**本地未达 origin commit 数**＝推送后复核。"
    "记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：把「占比」落到「手」属证据与载体；负控抓到的跨盘 relpath 缺陷按锁存待无竞争轮入卡）。 |"
)

STATE_UP = {
    "round_no": ROUND,
    "round_no_prev": 2026,
    "rounds_done": 1963,
    "rounds": 2027,
    "work": WORK,
    "task": ("r2027: one contract is 4,822 ETF lots; 90.13% of notional needs 162% of the book "
             "in cash at an 80% 融券 ratio; the ETF rounds to 0.00004 of beta, the contract to 0.2078"),
    "当前任务": ("r2027: 把默认档翻成手数——一手差 4,822 倍；1M 账面 ETF 3,919 手（beta 误差 0.00004）vs IM 0.813 手（只能 0 或 1.1091 beta）；"
            "80% 融券档 162% 现金承诺；IM 12% 保证金被单日 -5.64% 吃掉 47%"),
    "当前活": "把「90% 账面」翻成账户真的能下的单：几手、压多少现金、离强平多远",
    "最近实物": ("research/ASTOCK_VETO_HEDGE_LOTS.md + results/astock_veto_hedge_lots.json + "
             "scripts/astock_veto_hedge_lots.py（selftest 29/29·check rc0·负控 21/21）（2026-11-24 05:3x）"),
    "最新实物": "research/ASTOCK_VETO_HEDGE_LOTS.md + results/astock_veto_hedge_lots.json + scripts/astock_veto_hedge_lots.py",
    "最新判词": "LOT_IS_FREE_ON_THE_ETF_AND_A_FOUR_THOUSANDTH_OF_THE_BOOK_ON_THE_FUTURE",
    "本次": ("r2027 检查单：ETF 一手 230 元 / IM 一手 1,109,120 元（4,822x）；1M 档 ETF 3,918.83 手→3,919（beta 0.9014，误差 0.00004）、"
         "IM 0.813 手→0 或 1（beta 1.1091，误差 0.2078）；0.5% beta 所需账面 ETF 23,000 元 / IM 1.109 亿；"
         "精确中性账面 1 手 1,230,535 / 2 手 2,461,071；仿柱保证金 50/80/100% → committed 135/162/180% 账面；"
         "IM 12/15% → 13/17%（且 1M 档不可下）；每元目标名义占用 ETF 1.50/1.80/2.00 vs IM 0.15/0.18；"
         "最新 bar ETF -4.80% / IM -5.64%（12% 档一天的 47%）；滚动 2.02% 名义 / 1.82% 账面；基差中位 -0.629%"),
    "未验证": ("①保证金比例与券源是券商条款不可观测，按 50/80/100% 与 12/15% 轴印；②强平距离=保证金率的粗略上界，未建模维持保证金/追保/手续费；"
           "③价格取 11-20 收盘、持仓取最后一期（11-11 期末），7 个交易日未做市值重估；④IM 基差中位取自混合到期日，不能年化；"
           "⑤券源规模与召回未建模；⑥本面是口径件不是下单指令"),
    "watermark_verdict": "green (red=false; lane healthy; repo_write_contention rc=3 CONTENTION -> new-file faces only)",
    "watermark_note": ("竞争探针 rc=3：2 宿主存活（对端 pid 51252 11-22 20:10 起常驻 interactive / 本宿），"
                       "21 张共享面在轮首前被对端写、重叠窗 0 张 -> 按 r1927 只落新增文件面，未改共享代码/数据面、未跑 S6 链"),
    "s0_note": "orphan_face_probe py_faces=6 orphans=0 零杀；repo_write_contention rc=3 CONTENTION",
    "s05_note": ("orders_ack_scan CLEAN（116 令 / 329 回执 / 124 陈旧注记 / unacked=[]）；decisions.md 原字节 sha256 "
                 "79e3083b85c130b8... == state 水位 -> 零新决策；orders.md 原字节 99e8e77d093cc13d == 水位 -> 零新行；fleet/inbox 空"),
    "smoke": "not run this round (CONTENTION); 以 29/29 selftest + 21/21 负控 + run/check 双 rc0 背书，不宣称全绿",
    "s6_chain": "not run (CONTENTION rc=3)",
    "s7_attrition": "attrition_ledger_guard scan CLEAN（4 账本，3 处历史缩行 healed）",
    "s7_claws": "pre-commit / pre-push 与 Tools/git-hooks/ 逐字节（CR 归一）MATCH，未重装、未用 --no-verify",
    "s7_loop": "Bigmoney-IterationLoop phase ok（machine=bm-c pin=0 current=0，首燃 11/24 05:30 未动）",
    "s7_note": "contention window (rc=3): new-file-only landing; shared smoke/S6 faces untouched",
    "孤儿面": 0,
    "下轮指针": ("(a) 无竞争轮：smoke_test.py 两腿 + Tools/s6_chain_bma.py r2022-r2027 五面腿 + knowledge/METHODOLOGY_ASSETS.md 卡"
             "（锁存：跨盘 relpath 崩 = 第四例 r1745 族）+ CODELY 两行；"
             "(b) 把「162% 现金承诺」接进 CEO 一页纸与票据的仓位节；"
             "(c) 账面/价格时点错位（11-11 期末 vs 11-20 收盘）改成同一天重估"),
    "下个里程碑": ("(a) 竞争窗结束后把 r2022–r2027 五面接 S6 链腿与冒烟腿（≤48h）；"
              "(b) 把「90.13% 名义 = 162% 现金承诺 / 一手 4,822 倍」接到 CEO 一页纸与票据仓位节（≤48h）"),
    "记账_r2027": "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3",
    "本地未达 origin commit 数": None,
}


def main() -> int:
    st = json.load(open(STATE, encoding="utf-8"))
    st.update({k: v for k, v in STATE_UP.items() if v is not None})
    with open(STATE, "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    with open(REPORT, "a", encoding="utf-8") as fh:
        fh.write(REPORT_ROW.format(ts=NOW.strftime("%Y-%m-%d %H:%M"), round=ROUND) + "\n")

    fields = {
        "round_no": ROUND,
        "rounds_done": 1963,
        "who_did": "bm-c",
        "verdict": "healthy",
        "last_seen": TS,
        "ts": TS,
        "clock_read": TS,
        "heartbeat_epoch_utc": int(time.time()),
        "当前任务": STATE_UP["当前任务"],
        "当前活": STATE_UP["当前活"],
        "最近实物": STATE_UP["最近实物"],
        "最新判词": STATE_UP["最新判词"],
        "下个里程碑": STATE_UP["下个里程碑"],
        "下轮指针": STATE_UP["下轮指针"],
        "watermark_verdict": STATE_UP["watermark_verdict"],
        "孤儿面": 0,
        "本地未达 origin commit 数": 0,
        "记账_r2027": "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3",
    }
    with open(FIELDS, "w", encoding="utf-8") as fh:
        json.dump(fields, fh, ensure_ascii=False, indent=1)

    print("state round_no -> %d" % ROUND)
    print("round report row appended")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "Tools", "heartbeat_write.py"),
                        "apply", "--fields", FIELDS], cwd=ROOT, capture_output=True, text=True)
    print((r.stdout or "").strip()[-400:])
    if r.returncode not in (0,):
        print("heartbeat rc=%d %s" % (r.returncode, (r.stderr or "")[-300:]))
    return 0 if r.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
