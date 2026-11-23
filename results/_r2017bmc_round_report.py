"""r2017 round report append (bm-c).  Append-only: one row, never a rewrite."""
from __future__ import annotations

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")

ROW = (
    "| 2026-11-24 01:3x | r2017（**竞争探针 rc=3 CONTENTION·只落新增文件面**·23.95% 的换手是哪一层来的） | "
    "**watermark：red=false / lane=healthy · 孤儿面=0**（py_faces=3 / resident_servers=1=ComfyUI 空闲）。"
    "**产品（产品优先律）**：r2015 说这份账单是换手 23.95%/期、毛边的 10.8% 交给券商；r2016 试着用滞回带把税买回来——"
    "**证伪**，每期只省 0.02 bp。本轮退回更基础的一步：**这 23.95% 到底是谁在动？**答案只有两种，而且指向完全不同的做法——"
    "成分池在账下面动（新股进来/老股掉出可交易面板），或名字在否决边界上翻动（q==4 ↔ q<4）。"
    "本面用本账自己的换手定义（`1-|cur∩prev|/|cur|`，只有新进来的名字被计费）做**逐期恒等式拆分**，不做模型："
    "每一个新进账的名字，不是「上期不在池内」（U），就是「上期在池内=上期被否决」（V）。"
    "**读数一（结论翻转了下一步该做什么）**：可归因 22.95%/期里 **U 只占 3.64%（15.8%）**、**V 占 19.32%（84.2%）**——"
    "换手主要来自边界，不是池子。所以 r2016 的失败是结构性的：带子只改「被踢出的名字何时回来」，而它要抵的税 84.2% 是进来的名字自己造成的。"
    "**读数二（两张面独立对上）**：按本面量到边界税 **3.09 bp/期**，r2016 的带子实际省下 0.02 bp/期 = **0.5%**——不是转述，是同一次核对。"
    "**读数三（翻动是「一片人」不是几只票）**：76 期共 82,076 次边界穿越、落在 4,392 只名字上（每期约 1,080 只 ≈ 账上持仓的 38%），"
    "翻过 3 次及以上的有 4,337 只、最多的翻 40 次，**前 10% 的名字只占 16.1% 的穿越**——集中惩罚个别名字没用，要压就得压整片中段的分数。"
    "**读数四（税买的是差名字）**：进来的名字下一期真实收益 U +1.4845% / V **+0.4531%**，留下来的 +1.1069%——V 那批明显低于账面；"
    "U 虽最高但只占换手 15.8%，且 2025/2026 已掉到 0.89%/0.57%（池子稳了）。"
    "**读数五（池子的底不能直读）**：全池（A 臂）自身换手 4.30%/期，不能直接当 U——本账持仓只有 80.0%，同一绝对流量落在 1.25 倍小分母上，"
    "且进池的名字只有 67.8% 落在账上（其余一进来就是 q==4，不产生换手），U 的 3.64% 正是这两件事的合成。"
    "**零点不是方案**：若边界从不翻动，可归因期净额从 +0.9662%/期 到 +0.9971%/期（差 3.09 bp/期）；边界就是信号，去掉边界=换一本更笨的书。"
    "**下一个实验应该做平滑排名，不是更多带子参数**（本面把这一条写成判据，而不是猜测）。｜"
    "**验证证据**：`--selftest` **37/37 PASS**（父面换手定义含首期全额 / 一进来就被否决的名字不产生换手 / 释放=V 与真新码=U 分开 / "
    "只掉出不买不计费 / 穿越只算留在池内换边（离开再回来不算）/ 空账份额是 NaN 不是 0 / 池臂换手=纯成分流动 / net=mean-2c·turnover / "
    "三态判词严格 / 首期不入归因但入账面 / compound 拒 NaN / by_year 跳首期 / 跨盘路径打印不崩 / t 统计需两点）；"
    "`run` rc0（77 期，evidence_cutoff **2026-11-20**）→ `results/astock_veto_turnover_layers.json` + `research/ASTOCK_VETO_TURNOVER_LAYERS.md`，"
    "恒等式最大残差 **5.6e-17**；`check` **rc0**（含**父面锚硬腿**：A/B 两臂逐期 turnover 对 r2012 面逐位复现，最大绝对差 **0.000e+00**）。"
    "**负控 `results/_r2017bmc_turnover_layers_negative.py` 22/22 PASS**（原样 rc0 / cutoff 移动→STALE / 面板前移→STALE / "
    "十项手改数→CHECK FAILED 且**不带** STALE / 判词翻转→CHECK FAILED / 缺块→block missing / 逐期 turnover 改造→STALE / "
    "父面锚破坏→STALE parent anchor / 缺面→face missing 且不穿 STALE / 还原后两面 sha256 逐字节相同 / selftest 仍绿）。｜"
    "**S0**：`fleet/machine.json`=bm-c；`orphan_face_probe` py_faces=3 **orphans=0** 零杀；`repo_write_contention` **rc=3 CONTENTION**"
    "（2 宿主存活：pid 51252 为 11-22 20:10 起的 interactive、本宿 72992；20 张共享面在本轮开始前被对端写，含 `fleet/machines/bm-c.json`、"
    "`fleet/round_reports-bm-c.md`、`research/ARBITER-BOARD.md`、`results/_attrition_guard_scan.json`）→ 按 r1927 只落**新增文件面**，"
    "未改共享代码/数据面、未跑 S6 链；fetch 后 0 ahead / 0 behind。｜"
    "**S0.5 双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / 124 陈旧注记 / unacked=[]）；"
    "集团 `git cat-file blob origin/main:docs/decisions.md` **原字节** sha256 = **79e3083b85c130b8**（250,586 B）== state 水位 → 零新决策零动作；fleet/inbox 空。｜"
    "**S1（诚实边界）**：全量 smoke **未跑**（`smoke_test.py` 与 `logs/smoke_legs.json` 是共享面，竞争窗不覆盖）；"
    "本轮以 37/37 selftest + 22/22 负控 + run/check 双 rc0 背书，**不宣称全绿**。｜"
    "**S6**：未跑（`Tools/s6_chain_bmc.py` 与链产物为对端写的共享面）。｜"
    "**S7**：`state round_no 2016→2017`（rounds_done 1954→1955，带 predecessor 守卫防重复计数）；"
    "心跳经 `Tools/heartbeat_write.py apply` 合并写（applied 7 键，ack 329 未减，warnings=心跳比 state 多 57 条回执仅保留不删）；"
    "`& Tools/register_loop_task.ps1` **phase ok**（machine=bm-c pin=0 current=0，首燃 11/24 01:25 未动）；"
    "`attrition_ledger_guard scan` **CLEAN**（4 账本，3 处历史缩行 healed 注记照录）；"
    "`pre-commit` / `pre-push` 与 `Tools/git-hooks/` 逐字节（CR 归一）**MATCH**，未重装、未用 --no-verify。｜"
    "**CEO 过程可见面**：当前活＝把这条黑名单 23.95% 的换手拆成「池子流动」与「否决边界翻动」两层，看哪一个才是真能改的｜"
    "最近实物＝`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ASTOCK_VETO_TURNOVER_LAYERS.md`"
    "（2026-11-24 01:3x·84.2% 的换手来自否决边界、只有 15.8% 来自成分池；边界税 3.09 bp/期，r2016 的带子只买到 0.5%；"
    "翻动摊在 4,392 只名字上，前 10% 只占 16.1%）＋`results\\astock_veto_turnover_layers.json`"
    "＋`scripts\\astock_veto_turnover_layers.py`（selftest 37/37）＋`results\\_r2017bmc_turnover_layers_negative.py`（负控 22/22）｜"
    "下个里程碑＝（a）竞争窗结束后把本面接 S6 链腿 + 冒烟两腿（≤48h）；"
    "（b）**平滑排名实验**：残差排名先做 2-3 期平滑再取分位，量「降下来的换手」与「削掉的排序」谁大——本面已把方向定死在分数层，不再加带子参数（≤48h）。｜"
    "**未验证（如实）**：①换手仍按父面定义（名单集合差），同一只名字的权重变化不算交易；"
    "②U 不区分新上市/退市/长期停牌复牌/面板缺数据——数据层缺口会被算成成分池流动；"
    "③穿越按「留在池内且换边」计，离开池再回来不计（它没有做决定），「否决状态翻转」口径本面没印；"
    "④进来的名字收益是等权均值（与分数记账一致），整手口径不一致而整手不在射程；"
    "⑤年化是 77 期复利外推，2020 只有 6 期，逐年列只看方向；⑥票池现存标的（幸存者偏差，父面同），面板起于 2020-01-02；"
    "⑦本面是定价/口径件，不是可交易策略：无仓位规则、无容量约束、无风控；"
    "⑧全量 smoke 与 S6 未跑（竞争窗），本面尚未接 smoke 两腿与 S6 腿。｜"
    "**本地未达 origin commit 数**＝推送后复核。记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3"
    "（无方法论新增：本轮判据指向「平滑排名」这条待验证实验，属证据与载体，未成法）。|\n"
)


def main() -> int:
    with open(RP, "rb") as fh:
        raw = fh.read()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    with open(RP, "w", encoding="utf-8", newline="") as fh:
        fh.write(text + ROW.replace("\n", "\r\n" if crlf else "\n"))
    print("appended %d chars (eol=%s) -> fleet/round_reports-bm-c.md"
          % (len(ROW), "CRLF" if crlf else "LF"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
