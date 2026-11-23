# -*- coding: utf-8 -*-
"""r2007 closeout: append one round-report row + bump state-bm-c.json. Refuses to run twice."""
import io, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")
STATE = os.path.join(ROOT, "state-bm-c.json")
MARK = "r2007（**竞争探针 rc=3 CONTENTION·只落新增文件面**"

ROW = (
"| 2026-11-23 20:1x | " + MARK + "·整数对冲到底是量出来的还是窗口量出来的） | "
"**watermark：red=false / lane=healthy · 孤儿面=0**（py_faces 5 / resident_servers 1=ComfyUI 空闲）。"
"**产品（产品优先律）**：r2006 给 IC 一手多头配了 beta=1.5567 手 IF 的空头，然后不得不买整数手——印成 2 手、资本 3,150,916.73 元（精确 beta 只要 2,826,641.50）。"
"两件事压在那个数下面：这个 beta 是某一个 242 天窗口量出来的，换一批 242 天还是不是它？而且一手不可拆，1.5567 你只能买 1 手（少空 36%）或 2 手（多空 28%），两种错的价钱从没人印过。"
"**读数（同一 roll walk·1961 个对齐交易日 2018-10-23..2026-11-20）**：IC/IF 全样本 beta **0.9466**，去年窗口 **1.5567**；"
"242 日滚动窗（344 个窗·步长 5）**0.426 / p10 0.605 / 中位 0.944 / p90 1.363 / 最大 1.548**，"
"**70.3% 的窗口会印 1 手而不是 2 手**——台面用的 1.5567 落在八年分布的顶端，不在中位。"
"IC/IH 更极端：242 日窗的整数手 **{1,2,3}** 三种都出现过（1.790 的跨度）。"
"**四十九条手臂里三条（IC×IM、IM×IC、IM×IF）也在 1/2 手之间来回**；IH 作多头时三条臂稳定在 1 手。"
"**取整到底值多少钱（去年窗·一手多头）**：精确 beta 净 95,884 元、残差 σ 225,664；买 2 手净 **143,280 元**、σ 251,552、资本 3,144,400；beta=1 净仅 36,360、σ 265,558。"
"即取整多出来的 **+0.4433 手空头去年赚了 47,396 元**——**但这不是省下的钱，是押在对冲腿自己 carry 上的仓**（去年 IF 贴水为负、做空在收钱）；对冲腿 carry 转正那天它会原样还回去，页面把这句话印在数字旁边。"
"**验证证据**：`--selftest` **14/14 PASS**（含「一张忘了写 state 的表格行会被判词静默跳过」这条真事故腿——首版确实跑出了 table 说 {1,2} 而 verdict 说 STABLE，是靠数据自相矛盾才抓出来的）；"
"`run` rc0 落 `results/idx_fut_carry_hedge_beta_lots.json` + `research/IDX_FUT_CARRY_HEDGE_BETA_LOTS.md`（evidence_cutoff 2026-11-20）；`check` rc0。"
"**跨面锚**：去年窗 beta 逐条复现 r2006 已发布读数（IC/IF 1.556717 vs 1.5567、IC/IM 1.005620 vs 1.0056、IM/IF 1.393872 vs 1.3939、IM/IH 1.898686 vs 1.8987，偏差 ≤2.8e-5）——不是第二套算法，是同一 roll walk 的另一种切法。"
"**负控** `results/_r2007bmc_beta_lots_negative.py` **17/17 PASS**（每腿自己写字节调真 check、不继承上腿）：一刀切掉 cutoff→rc3 带 STALE；改 input digest→rc3 带 STALE；"
"**手翻 verdict / 改 beta_full 却不动输入→rc3 且不带 STALE 字样**（首版这里把真缺陷印成「STALE face drifted」，负控当场抓出，已把 check 拆成漂移/自相矛盾两路——r1934 律）；删整张表→rc3；原样→rc0。"
"｜**S0**：`fleet/machine.json`=bm-c；`orphan_face_probe` py_faces=5 **orphans=0** 零杀；`repo_write_contention` **rc=3 CONTENTION**（2 宿主：pid 51252 为 11-22 20:10 起的 interactive + 本宿；16 张共享面在本轮开始前被对端写，含 `fleet/machines/bm-c.json`、`research/ARBITER-BOARD.md`、`results/host_contention` 族）→ 按 r1927 只落**新增文件面**，未改任何共享代码/数据面、未跑 S6 链；fetch 后 0 ahead / 0 behind（基座 d27d962ff0）。"
"｜**S0.5 双扫**：`Tools/orders_ack_scan.py` CLEAN（116 令 / 329 回执 / unacked=[]）；集团 `cat-file blob origin/main:docs/decisions.md` 原字节 sha256 == state 水位 79e3083b85c130b8 → 零新决策零动作；fleet/inbox 本轮无新增。"
"｜**S1（诚实边界）**：全量 smoke **未跑**（`smoke_test.py` 与 `logs/smoke_legs.json` 是共享面，竞争窗不覆盖）；本轮以 14/14 selftest + 17/17 负控 + run/check 双 rc0 背书，**不宣称全绿**。"
"｜**S6**：未跑（`Tools/s6_chain_bmc.py` 被对端写）。"
"｜**S7**：`state round_no 2005→2007`（rounds_done 1944→1945；r2006 由对端提交且未碰 state，故取 2006 之上下一个号并留此注）；"
"心跳经 `Tools/heartbeat_write.py apply` 合并写；`attrition_ledger_guard scan` CLEAN；`pre-commit`/`pre-push` 与 `Tools/git-hooks/` 逐字节 MATCH，未重装、未用 --no-verify。"
"｜**CEO 过程可见面**：当前活＝查整数对冲是不是窗口产物、取整在去年到底值多少钱｜"
"最近实物＝`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\IDX_FUT_CARRY_HEDGE_BETA_LOTS.md`（2026-11-23 20:1x·IC/IF 242 日窗 70.3% 会说 1 手）＋`results\\idx_fut_carry_hedge_beta_lots.json`＋`scripts\\idx_fut_carry_hedge_beta_lots.py`（selftest 14/14）｜"
"下个里程碑＝（a）竞争窗结束后把本面接 S6 链腿 + 冒烟两腿（≤48h）；（b）把「对冲腿 carry 转正就还回去」做成逐日的对冲 carry 符号面，让读者看到这 47,396 元的到期日（≤48h）。"
"｜**未验证（如实）**：①全量 smoke 与 S6 未跑（竞争窗）；②整数手只用 ceil/round 两读，交易所分级保证金下的逐档手数未拆；③样本是单一 roll walk，跨品种 roll 规则若变结论要重算；④「多 0.44 手赚 47,396」是去年一年的毛口径，未计多一手带来的保证金占用与追缴风险；⑤票池/合约宇宙为现存标的（幸存者偏差，父面同）。"
"｜**本地未达 origin commit 数**＝推送后复核。记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3。 |\n"
)

def main():
    old = io.open(REPORT, encoding="utf-8").read()
    if MARK in old:
        print("already appended; refusing to double-write")
        return 3
    if not old.endswith("\n"):
        old += "\n"
    io.open(REPORT, "w", encoding="utf-8", newline="").write(old + ROW)

    st = json.load(io.open(STATE, encoding="utf-8"))
    st["round_no"] = 2007
    st["rounds_done"] = int(st.get("rounds_done") or 0) + 1
    st["last_decisions_sha"] = "79e3083b85c130b8b57363d1ce4850520704cfbdf3fc41b8277e7e5ee39d6e16"
    st["activity_now"] = "r2007: beta stability of the integer hedge (70.3% of 242d windows say 1 lot)"
    st["activity_now_round"] = 2007
    with io.open(STATE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print("report row appended; state round_no=2007 rounds_done=%d" % st["rounds_done"])
    return 0

if __name__ == "__main__":
    sys.exit(main())
