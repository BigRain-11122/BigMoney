"""r2030 closeout: state bump + heartbeat fields + round-report line (new file).

Only bm-c's own files are touched: state-bm-c.json, results/_r2030bmc_hb_fields.json and
fleet/round_reports-bm-c.md (append).  The heartbeat itself is written by
Tools/heartbeat_write.py (merge-only) from the fields file produced here.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "results", "_r2030bmc_hb_fields.json")
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")

ROUND = 2030
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
EPOCH = int(datetime.now(timezone.utc).timestamp())

ACTIVITY = (
    "r2030: held honestly (beta refitted before each period on prior rows only), the "
    "hedge still removes 61.9% of the book's volatility (29.89% -> 11.38%) while the "
    "look-ahead beta buys only 0.23pp more; beta = 1.00 ties the refit (0.22pp, and "
    "actually ends higher: 67.45% vs 60.68% cumulative); the de-lever control splits the "
    "claim -- at equal volatility the hedge earns 11.17% against 5.23% (0.98 vs 0.46 per "
    "unit of vol) but draws down 3.65pp deeper (-13.39% vs -9.74%)"
)

TASK = ("r2030: does the hedge still work when the beta cannot see the future "
        "(walk-forward), and is it more than leverage")

ARTIFACTS = ("scripts/astock_veto_hedge_walkforward.py (selftest 40/40); "
             "results/astock_veto_hedge_walkforward.json; "
             "research/ASTOCK_VETO_HEDGE_WALKFORWARD.md; "
             "results/_r2030bmc_walkforward_negative.py (14/14)")

REPORT_LINE = """| 2026-11-24 06:2x | r2030 **新增文件面**（竞争窗 rc=3·不动共享面） | **拿着过去的 beta 才对冲，风险还减不减**：`scripts/astock_veto_hedge_walkforward.py` + `results/astock_veto_hedge_walkforward.json` + `research/ASTOCK_VETO_HEDGE_WALKFORWARD.md`。r2022–r2029 七面都用「一个 beta 读全窗」，而那个「风险减了 60%」里含了拟合自己看过的那 43 期。本面把 beta 改成**每期只用当期的前面几期重拟**（预热 20 期），六个臂放在同一段 57 期上比较，另加一条**去杠杆对照**：同一本书缩到同等波动、完全不对冲。**读数一（诚实臂站得住）**：年化波动 29.89% → **11.38%（减 61.9%）**，判词 `HONEST_BETA_KEEPS_ITS_REMOVAL`。**读数二（偷看未来几乎不值钱）**：全窗 beta 减 62.69%，只多 **0.23pp** → 前几轮那 60% 不是拟合出来的假象。**读数三（但重拟也不值钱）**：beta=1.00 与逐期重拟相差 **0.22pp**（判 `ONE_UNIT_TIES_THE_FITTED_BETA`），而且**累计收益更高**：67.45% vs 60.68%，最差一期 -8.22% vs -9.09% —— 逐期重拟交的是信息费，拿不回。**读数四（重拟的 beta 不是常数的抖动）**：57 次重拟 **0.8644..1.0121**，其中 **9 次落在 r2029 印的 95% 带（0.7950..1.0076）之外** —— 那张带描述的是「冻结 beta 的抽样误差」，不是「beta 会跑到哪」。**读数五（去杠杆对照把claims 拆开）**：同等波动下不对冲的账本年化 **5.23%**（每单位波动 0.46），对冲 **11.17%**（0.98）——**对冲不是纯杠杆，它把每单位风险的收益翻了一倍**；但最深的坑是对冲更浅还是更深？**对冲 -13.39% vs 不对冲 -9.74%，深 3.65pp** → 判词 `HEDGE_TRADES_DRAWDOWN_FOR_RETURN`：**它对冲掉的是波动，不是回撤**。这条与 r2026「10%/15% 预算谁都守不住」、r2023「买回撤」正面冲突，必须往上呈。**读数六（逐期）**：57 期里 **82.5%** 的期数上对冲确实把单期幅度压小了。｜**验证证据**：`--selftest` **40/40 PASS**（斜率三腿含 nan 丢弃 / 前瞻性钉死四腿：毒化第 25 期后「该期及以前」的 beta 一位不动、「之后」每个都动、预热窗尊重、训练行数=期号 / 回撤四腿含复原情形 / 臂统计五腿含 ddof 与复利 / 判词阶梯逐条单因子十腿：去杠杆新增「深坑但多赚=交易」「深坑且不多赚=更小的书赢」「两轴皆平=只是杠杆」三态 / 活面七腿：同一样本、无对冲不removal、对照波动逐位相等、判词在冻结词表内）；`run` rc0（evidence_cutoff **2026-11-20**，末期为 2026-11-11）→ 双件落盘；`check` **rc0**（3 张父面 content_sha + 6 臂 × 8 字段 + 8 条读数 + 样本块 + beta 序列长度 + 6 个判词 + 页面三词逐项重推）。**负控 `results/_r2030bmc_walkforward_negative.py` 14/14 PASS**（毒臂波动/毒读数/翻头条/翻去杠杆判词/页面丢词 → CHECK FAILED 且**不带** STALE；父面移动 → STALE 且**不带** CHECK FAILED；缺面/缺页 → STALE；全跑完发布面逐字节未动且仍绿）。｜**S0**：`fleet/machine.json`=bm-c；`orphan_face_probe` py_faces=6 **orphans=0** 零杀；`repo_write_contention` **rc=3 CONTENTION**（2 宿主：本宿 pid 77488；对端 interactive pid 51252＝11-22 20:10 起常驻，23 张共享面在轮首前被写、重叠窗 0 张）→ 只落新增文件面、未改共享代码/数据面、未跑 S6 链、未跑全量 smoke。｜**S0.5 双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / 124 陈旧注记 / unacked=[]）；集团 `git cat-file blob origin/main:docs/decisions.md` **原字节** sha256 = **79e3083b85c130b8** == 水位 → 零新决策零动作；fleet/inbox 0 件。｜**S1（诚实边界）**：全量 smoke 在本窗启动（后台）**尚未返回**且写共享面 `logs/smoke_legs.json` → 本轮**不宣称全绿**；本面以 40/40 selftest + 14/14 负控 + run/check 双 rc0 背书。｜**S6**：未跑（共享面）。｜**S7**：`state round_no 2029→2030`（rounds_done 1964→1965，round_no_prev 留痕）；心跳经 `Tools/heartbeat_write.py apply` 合并写；`& Tools/register_loop_task.ps1` **phase ok**（machine=bm-c pin=0 current=0，首燃 06:30 未动）；`attrition_ledger_guard scan` **CLEAN**（4 账本，1 处历史缩行 healed 注记照录）；fetch 后 0 ahead / 0 behind。｜**CEO 过程可见面**：当前活＝把「拿着过去才知道的 beta 才对冲」这条路走一遍，看风险减得真不真｜最近实物＝`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ASTOCK_VETO_HEDGE_WALKFORWARD.md`（2026-11-24 06:2x·**诚实减 61.9%、偷看未来只多 0.23pp**；**beta=1 与重拟打平且累计收益更高**；**对冲把每单位风险收益翻倍但回撤深 3.65pp**）＋`results\\astock_veto_hedge_walkforward.json`＋`scripts\\astock_veto_hedge_walkforward.py`（selftest 40/40）＋`results\\_r2030bmc_walkforward_negative.py`（负控 14/14）；下个里程碑＝（a）竞争窗结束后把 r2022–r2030 八面接 S6 链腿 + 冒烟两腿（≤48h）；（b）把「对冲换波动不换回撤」这条接到 CEO 一页纸与票据（≤48h）——它现在的仓位节只说 3,919 手，没说这手数买到的坑比「少买一半」深。｜**未验证（如实）**：①重拟按每期 20 根、20 根一隔的不重叠窗，期数少（57）抽样误差本身未单独量化；②账面仍停在 2026-11-11 的 mark，价格晚 7 天（r2028 的欠账未在本面修）；③重拟没计换手成本，真实账户每期重设对冲要付钱，本面只说明「信息不值钱」，没说「免费」；④只走了 ETF 腿（512100），IM 腿按 r2027 的结论（小资本配不出 beta）不重复；⑤回撤比较用的是同一段 57 期，不同窗口下 3.65pp 会变，本面不宣称它是常数；⑥本面是口径/证据件，不是可交易策略。｜**本地未达 origin commit 数**＝推送后复核。记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：把「一个 beta 读全窗」改成「前期只能看前期」，属证据与载体）。 |
"""


def main() -> int:
    # ---- state
    with open(STATE, encoding="utf-8") as fh:
        state = json.load(fh)
    prev = state.get("round_no")
    state["round_no"] = ROUND
    state["round_no_prev"] = prev
    state["rounds_done"] = int(state.get("rounds_done") or 0) + 1
    state["last_round_utc"] = NOW
    with open(STATE, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("state: round_no %s -> %d, rounds_done=%d"
          % (prev, ROUND, state["rounds_done"]))

    # ---- heartbeat fields
    hb = {
        "machine_id": "bm-c",
        "round_no": ROUND,
        "activity": "product",
        "activity_now": ACTIVITY,
        "activity_now_round": ROUND,
        "task": TASK,
        "artifacts": ARTIFACTS,
        "verdict": "healthy",
        "last_seen": NOW,
        "ts": NOW,
        "clock_read": NOW,
        "heartbeat_epoch_utc": EPOCH,
        "idle_rounds": 0,
        "agenda_starved": False,
        "ahead_origin": 0,
        "behind_origin": 0,
        "batch": "none this round (contention rc=3: new-file faces only)",
        "chain": "S6 chain NOT run this round (Tools/s6_chain_bmc.py is a peer-written shared face)",
        "chain_verdict": "unchanged this round; r2029's chain state stands",
        "carrier_debt_r2030": (
            "the hedge family (r2022-r2030) still has no S6 leg and no smoke leg -- both "
            "files are peer-written shared faces, so the debt waits for a contention-free "
            "window"),
    }
    assert isinstance(hb["heartbeat_epoch_utc"], int)
    with open(HB, "w", encoding="utf-8") as fh:
        json.dump(hb, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print("heartbeat fields ->", os.path.relpath(HB, ROOT).replace(os.sep, "/"))

    # ---- round report (append only; own per-machine file)
    with open(REPORT, "a", encoding="utf-8") as fh:
        fh.write(REPORT_LINE)
    print("round report line appended")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
