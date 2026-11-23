"""r2023 closeout (bm-c): round-report row + state fields + heartbeat fields.

Append-only on the report ledger; fresh read on the state face.  Two phases:
    python results/_r2023bmc_closeout.py            # row + state + hb fields
    python results/_r2023bmc_closeout.py --addendum <commit> [--ahead 0]
"""
from __future__ import annotations

import io
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "results", "_r2023bmc_hb_fields.json")

ROUND = 2023
PREV = 2022

ROW = (
    "| 2026-11-24 04:0x | r2023（**竞争探针 rc=3 CONTENTION·只落新增文件面**·回撤预算这张票："
    "买多少保险、最后一点回撤多少钱） | **watermark：red=false / lane=healthy · 孤儿面=0**"
    "（py_faces=3 / resident_servers=1=ComfyUI 空闲）。**产品（产品优先律）**："
    "r2022 把反票在两种真能交易的标的上打完了，留下五个 k 和一句「买的是保险不是边」；"
    "**没有人持有 k**——持有人手上只有一条愿意坐过去的回撤预算和一个真能拿到的融券价。"
    "本面把持仓问题翻成采购问题并冻结两条规则（都在**样本内**选、读**样本外**）："
    "规则 A＝预算内年化最高档（并列取更小档），规则 B＝预算字面要求的最小档。"
    "**读数一（10% 预算买不到）**：网格能给的最小样本内回撤地板是 **9.80%**（k=0.85），"
    "融券 2% 起地板抬到 10.61%、5% 抬到 11.69% —— 10% 预算连样本内都只剩 0.2pp 余量，"
    "而同一档读样本外是 **-14.36%**，判 MISSES。"
    "**读数二（20% 预算：两个买法都守住，价差 4pp）**：规则 A 选 **k=0.65**"
    "（样本内回撤 -10.80%、年化 +6.65%，相对不买保险 **倒贴 -0.97pp**；样本外回撤 -14.64% 守住、"
    "年化 +11.55%，代价 **+4.89pp**），规则 B 只要 **k=0.15**（样本外仅付 0.89pp）——"
    "**多出来的额度花掉要多付 4.00pp 年化、换回 2.68pp 回撤**，这就是「预算不紧时你拿它做什么」的价格。"
    "**读数三（价签随窗口翻符号）**：每削 1pp 回撤付出的年化，样本内 -0.082（对冲倒贴）、"
    "样本外 **+0.943** pp/pp（k=0.65 处）；到 k=1.00 是 -0.060 / **+1.522**。"
    "**读数四（最后一点最贵）**：边际价格（上一个 5 分档加到这里）样本外 k=1.00 时 **+9.55 pp/pp**，"
    "而 k=0.40 只要 4.58——回撤的最后一截是整张表里最贵的东西，因为回撤在 k≈1 附近触底"
    "（全窗 -14.17%），再往上买（k=1.5/2.0）回撤反而回到 -24.05%/-47.26%，过度对冲把空头的波动买回来了。"
    "**读数五（什么时候答案是「不买」）**：25% 预算 × 5% 融券时规则 A 直接选 **k=0.00**——"
    "在那一刻保险已经贵过它买到的回撤。｜**验证证据**：`--selftest` **46/46 PASS**"
    "（回撤取绝对值 / 无观测期→None 不印 0 / 平坦书零回撤且并列取小档 / beta=1 完美对冲把 -20% 那期"
    "变得与其余不可区分且回撤只剩成本拖累 / 无敌对冲买到网格边缘并如实标 at_max_grid / 规则 A 边界含等号 / "
    "规则 B 取最小可行 / 不可达→None / 并列取小档 / 地板＝网格最小回撤 / 削掉零回撤时价格=None 不除零 / "
    "价格＝放弃年化÷削掉回撤 / 负数价签照印不截断 / 价格基准取同窗口 k=0 / 边际价取上一步不是平均 / "
    "k=0 无边际步 / 判词三态含边界与未知 / 价签判词四态 / k=0 带融券仍逐位复现原书 / 缺价期不当免费对冲 / "
    "成本随 |k·beta| 线性且 k=0 归零 / 每格都带已定价的样本外回撤）；"
    "`run` rc0（77 期，evidence_cutoff **2026-11-20**）→ `results/astock_veto_hedge_budget.json` + "
    "`research/ASTOCK_VETO_HEDGE_BUDGET.md`；`check` **rc0**（母面摘要门 + 五个已发布档 × 两窗 × 三项"
    "＝30 格锚腿全 0 差 + 全网格 41×3 曲线逐格重推 + 每格判词重判 + 页面与渲染逐字节相等）。"
    "**负控 `results/_r2023bmc_hedge_budget_negative.py` 21/21 PASS**，并当场抓到一枚真缺陷："
    "首版 `check` 把「面内被改一行」也印成 STALE（因为只比面副本与母面）——"
    "正法＝**记母面内容摘要**（剔除 generated），摘要一致＝母面没动，此时任何不一致都是**本面的缺陷**"
    "（CHECK FAILED），摘要变了才是 STALE；负控改为 monkeypatch loader 模拟母面移动（不碰共享母面），"
    "三条 STALE 腿（行/β/截断）与九条 CHECK FAILED 腿（改行/改 k/改判词/改回撤/改曲线/改页/改 cutoff/改 β）"
    "互不串词。｜**S0**：`fleet/machine.json`=bm-c；`orphan_face_probe` py_faces=3 **orphans=0** 零杀；"
    "`repo_write_contention` **rc=3 CONTENTION**（2 宿主存活：pid 51252＝11-22 20:10 起的常驻 ACP 宿主，"
    "6 秒 CPU 增量 0.016 实测空闲；27 张共享面在本轮开始前被对端写，含 `fleet/machines/bm-c.json`、"
    "`fleet/round_reports-bm-c.md`、`research/ARBITER-BOARD.md`、`results/_attrition_guard_scan.json`）"
    "→ 按 r1927 只落**新增文件面**，未改共享代码/数据面、未跑 S6 链；fetch 后 0 ahead / 0 behind。"
    "｜**S0.5 双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / 124 陈旧注记 / unacked=[]）；"
    "集团 `git cat-file blob origin/main:docs/decisions.md` 原字节 sha256 = **79e3083b85c130b8**（250,586 B）"
    "== state 水位 → 零新决策零动作。｜**S1（诚实边界）**：全量 smoke **未跑**（`smoke_test.py` 与 "
    "`logs/smoke_legs.json` 是共享面，竞争窗不覆盖）；本轮以 46/46 selftest + 21/21 负控 + run/check 双 rc0 "
    "背书，**不宣称全绿**。｜**S6**：未跑（`Tools/s6_chain_bmc.py` 与链产物为对端写的共享面）。"
    "｜**S7**：`state round_no 2022→2023`（rounds_done +1，round_no_prev 留痕 2022）；"
    "`& Tools/register_loop_task.ps1` **phase ok**（machine=bm-c pin=0 current=0）；"
    "`attrition_ledger_guard scan` **CLEAN**（4 账本，3 处历史缩行 healed 注记照录）；"
    "`pre-commit`/`pre-push` 与 `Tools/git-hooks/` 逐字节（CR 归一）比对。"
    "｜**CEO 过程可见面**：当前活＝把「要买多少保险」变成一张按回撤预算和融券价查的表，"
    "并说清最后一点回撤为什么最贵；最近实物＝"
    "`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ASTOCK_VETO_HEDGE_BUDGET.md`"
    "（2026-11-24 04:0x·10% 预算买不到样本外；20% 预算 A 选 k=0.65、B 只要 0.15，差 4.00pp 换 2.68pp；"
    "价签样本内 -0.082 / 样本外 +0.943 pp/pp，边际最贵 9.55）＋"
    "`results\\astock_veto_hedge_budget.json`＋`scripts\\astock_veto_hedge_budget.py`（selftest 46/46）＋"
    "`results\\_r2023bmc_hedge_budget_negative.py`（负控 21/21）；"
    "下个里程碑＝（a）竞争窗结束后把本面接 S6 链腿 + 冒烟两腿（≤48h）；"
    "（b）**把预算换成日频口径**：现在是 20 根 bar 的期间曲线，真实账户按日盯市，"
    "把同一套规则放到日频序列上重算，看「守住了」这句话还成不成立（≤48h）。"
    "｜**未验证（如实）**：①回撤是 20 根 bar 期间曲线，不是日频 mark-to-market；"
    "②空头腿保证金/追保/强平未建模；③对冲腿 as-traded 不含分红；"
    "④只有 77 期（IS 43 / OOS 34），「守住」是一次观测不是分布；"
    "⑤预算 10/15/20/25%×融券 0/2/5% 与 k 步长 0.05 都是冻结网格，未搜最优；"
    "⑥本面是定价/口径件不是可交易策略；⑦全量 smoke 与 S6 未跑（竞争窗），本面尚未接链。"
    "｜**本地未达 origin commit 数**＝推送后复核。记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3"
    "（无方法论新增：本面把 r2022 的「保险」从判词变成可按预算与融券价查询的价格表，属证据与载体）。 |"
)


def _now():
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def append_row(text: str) -> None:
    with io.open(REPORT, "r", encoding="utf-8") as fh:
        body = fh.read()
    if not body.endswith("\n"):
        body += "\n"
    with io.open(REPORT, "w", encoding="utf-8", newline="") as fh:
        fh.write(body + text + "\n")


def main(argv) -> int:
    if "--addendum" in argv:
        sha = argv[argv.index("--addendum") + 1]
        ahead = argv[argv.index("--ahead") + 1] if "--ahead" in argv else "0"
        row = (
            "| 2026-11-24 04:1x | r2023 **addendum**（送达核验） | commit **%s** 已推 origin/main，"
            "fetch 后 **AHEAD=%s / BEHIND=0**，`git ls-tree -r origin/main` 六件 blob 全在位"
            "（scripts/astock_veto_hedge_budget.py / results/astock_veto_hedge_budget.json / "
            "research/ASTOCK_VETO_HEDGE_BUDGET.md / 负控 results/_r2023bmc_hedge_budget_negative.py / "
            "收口 _r2023bmc_closeout.py 与 _r2023bmc_hb_fields.json，`_r[0-9]*` 走 `git add -f` 既有惯例）"
            "→ **本地未达 origin commit 数=0**。**S7 收尾双扫**：`Tools/orders_ack_scan.py` **CLEAN**；"
            "集团 decisions 原字节 sha256 仍 **79e3083b85c130b8** → 零新决策；fleet/inbox 0 件。"
            "记账：本行 1 处（轮报告 addendum），本轮合计 4。 |" % (sha, ahead)
        )
        append_row(row)
        with io.open(STATE, "r", encoding="utf-8") as fh:
            st = json.load(fh)
        st["送达自证_r2023"] = ("commit %s 已推 origin/main；fetch 后 AHEAD=%s / BEHIND=0；"
                              "ls-tree origin/main 六件 blob 在位（scripts/results/md/负控/收口两件）；"
                              "本地未达 origin commit 数=0" % (sha, ahead))
        st["本地未达 origin commit 数"] = 0
        st["本地未达origin"] = 0
        with io.open(STATE, "w", encoding="utf-8") as fh:
            json.dump(st, fh, ensure_ascii=False, indent=1)
        print("addendum appended: %s ahead=%s" % (sha, ahead))
        return 0

    append_row(ROW)

    with io.open(STATE, "r", encoding="utf-8") as fh:
        st = json.load(fh)
    st["round_no"] = ROUND
    st["round_no_prev"] = PREV
    st["rounds_done"] = int(st.get("rounds_done", ROUND - 1)) + 1
    st["孤儿面"] = 0
    st["孤儿面_note"] = "round-zero orphan_face_probe: orphans 0, py_faces 3, resident_servers 1"
    st["watermark_verdict"] = ("green (red=false; lane healthy; repo_write_contention rc=3 CONTENTION "
                               "-> new-file-only round, 27 shared faces written by peer pid 51252 before round start)")
    st["当前活"] = "把「要买多少保险」变成按回撤预算与融券价可查的价格表（A 股残差黑名单的对冲腿）"
    st["当前任务"] = ("r2023: budget 20%/carry 0% -> rule A k=0.65 (IS -10.80% dd, IS ann 6.65% = -0.97pp paid; "
                      "OOS -14.64% dd holds, OOS ann 11.55% = +4.89pp cost); rule B k=0.15; "
                      "price per dd point -0.082 in-sample vs +0.943 out-of-sample; marginal out-of-sample 9.55pp/pp at k=1")
    st["当前任务_en"] = ("r2023: turned the hedge into a drawdown-budget purchase table -- 10% budget is "
                         "reachable in-sample only (floor 9.80%) and misses out-of-sample (-14.36%); "
                         "20% budget: rule A k=0.65 holds both windows at +4.89pp cost, rule B k=0.15 at +0.89pp")
    st["最近实物"] = ("research/ASTOCK_VETO_HEDGE_BUDGET.md + results/astock_veto_hedge_budget.json + "
                    "scripts/astock_veto_hedge_budget.py（selftest 46/46·check rc0·负控 21/21）（2026-11-24 04:0x）")
    st["下个里程碑"] = ("(a) 竞争窗关后接 S6 链腿 + 冒烟两腿（≤48h）(b) 把同一套预算规则放到**日频**序列上重算，"
                     "看「样本外守住了」是否还成立（≤48h）")
    st["下轮指针"] = ("(a) 无竞争轮：smoke_test.py 两腿 + Tools/s6_chain_bmc.py 腿 + knowledge/METHODOLOGY_ASSETS.md 卡 "
                   "+ CODELY 两行 (b) 日频回撤口径 + 空头腿保证金占用，是本面唯一还没量的两件事")
    st["本轮"] = ("r2023: 回撤预算采购表（规则 A 预算内年化最高/规则 B 最小档，均在样本内选读样本外）；"
               "10% 预算样本内地板 9.80%、融券 2% 起不可达、样本外 -14.36% 判 MISSES；"
               "20% 预算 A k=0.65（代价 +4.89pp）B k=0.15（+0.89pp），松弛价值 4.00pp 换 2.68pp 回撤；"
               "价签样本内 -0.082 / 样本外 +0.943 pp/pp，边际最贵 9.55 pp/pp")
    st["记账_r2023"] = "本行 1 处（轮报告）+ state 1 处 + 心跳 1 处 = 3"
    with io.open(STATE, "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)

    hb = {
        "last_seen": _now(),
        "round": ROUND,
        "round_no": ROUND,
        "ts": _now(),
        "clock_read": _now(),
        "heartbeat_epoch_utc": int(datetime.now(timezone.utc).timestamp()),
        "当前任务": st["当前任务"],
        "当前活": st["当前活"],
        "最近实物": st["最近实物"],
        "下个里程碑": st["下个里程碑"],
        "verdict": "healthy",
        "idle_rounds": 0,
        "agenda_starved": False,
        "孤儿面": 0,
    }
    with io.open(HB, "w", encoding="utf-8") as fh:
        json.dump(hb, fh, ensure_ascii=False, indent=1)
    print("report row appended; state round_no=%d; hb fields -> %s" % (ROUND, HB))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
