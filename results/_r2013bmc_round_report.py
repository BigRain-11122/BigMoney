# -*- coding: utf-8 -*-
"""r2013 round report line (append-only, S5)."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")

LINE = (
    "| 2026-11-23 23:4x | r2013（**竞争探针 rc=3 CONTENTION·只落新增文件面**·"
    "整手账里那 22.83% 没投出去的钱，夜里赚了多少） "
    "| **watermark：red=false / lane=healthy · 孤儿面=0**（py_faces 3 / resident_servers 1=ComfyUI 空闲）。"
    "**产品（产品优先律）**：r2012 把所有投不出去的现金记 **0%**，于是 1000 万的黑名单账上有 22.8% 的钱既不买股也不生息。"
    "真实 A 股账户收盘会把闲钱扫进**一天期逆回购（GC001）**。本轮把这条腿按真实 GC001 报价（`data/repo_daily/GC001.csv`，"
    "年化百分比 close，日收益 = close/365，节假日按最后一个报价前向填充、不按 0%）重新定价。"
    "**读数一（现金腿非对称）**：1000 万时 A 臂（全池 2,866 只）在场 **70.38%**、B 臂（黑名单）在场 **77.17%**——"
    "**黑名单臂反而更少现金**（差 **+6.79pp**），因为 r2012 已量过：买不起一手的名字是中位价 47 元的贵股票，它们更多落在全池里。"
    "**读数二（水平都涨，B 涨得少）**：B 净年化 **11.38% → 11.71%**（+0.33pp），A **8.84% → 9.26%**（+0.42pp）；"
    "同期 GC001 期间收益均值 **+0.1079%**、年化 **+1.37%**。"
    "**读数三（判词不变、比值更差）**：B−A 从 **+0.2074%/期**（t 3.04）掉到 **+0.2004%**（t 2.93），比值 **0.854 → 0.825**，"
    "仍判 `EDGE_DEGRADES_UNDER_ROUNDING`；50M 档 0.941→0.935 仍 `EDGE_SURVIVES_ROUNDING`，**「这本书要 5000 万才存在」这个门槛没被现金腿移动**。"
    "结论一句话：**等价的现金收益补不回整手税，它反而把两臂的差拉得更小——因为整手账里现金多的那一臂不是黑名单。**"
    "｜**验证证据**：`--selftest` **26/26 PASS**（日收益换算 / 两日复利 / 洞前向填充不是 0% / 面板日历对齐 / 首报价前 NaN / "
    "invested=100% 无红利 / invested=0% 全现金 / 半仓半红利 / **r_cash=0 逐位复现父面** / NaN share 不静默 / 判词三态六边界 / "
    "turnover 首期=全额入场 / 现金多的臂红利更大 / B 投更多则 B 红利更少）；`run` rc0 落 `results/astock_veto_cash_leg.json` + "
    "`research/ASTOCK_VETO_CASH_LEG.md`（evidence_cutoff 2026-11-20，77 期）；`check` **rc0**（含**父面锚硬腿**："
    "`invested_share_median` 与 `net_per_period_mean` 必须逐位复现 `astock_veto_lot_drag.json`，本次最大绝对差 **0.000e+00**）。"
    "**负控 `results/_r2013bmc_cash_leg_negative.py` 18/18 PASS**（原样 rc0 / 面板 cutoff 移动→rc3 带 STALE / "
    "手改 mean_n→rc3 CHECK FAILED 且**不带** STALE / 手改 net_with_cash→rc3 不带 STALE / 破坏父面锚→rc3 带 STALE / "
    "缺面→rc3 face missing 且不穿 STALE / 还原后 rc0 且两面 sha256 逐字节相同）。"
    "｜**S0**：`fleet/machine.json`=bm-c；`orphan_face_probe` py_faces=3 **orphans=0** 零杀；`repo_write_contention` "
    "**rc=3 CONTENTION**（3 宿主存活：pid 51252 为 11-22 20:10 起的 interactive、67160 为 11-23 20:05 起、本宿 67924；"
    "27 张共享面在本轮开始前被对端写，含 `fleet/machines/bm-c.json`、`fleet/round_reports-bm-c.md`、`research/ARBITER-BOARD.md`）"
    "→ 按 r1927 只落**新增文件面**，未改共享代码/数据面、未跑 S6 链；fetch 后 0 ahead / 0 behind。"
    "｜**S0.5 双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / 124 陈旧注记 / unacked=[]）；"
    "集团 `git cat-file blob origin/main:docs/decisions.md` **原字节** sha256 = **79e3083b85c130b8**（250,586 B）== state 水位 → "
    "零新决策零动作；fleet/inbox 无未处理件。"
    "｜**S1（诚实边界）**：全量 smoke **未跑**（`smoke_test.py` 与 `logs/smoke_legs.json` 是共享面，竞争窗不覆盖）；"
    "本轮以 26/26 selftest + 18/18 负控 + run/check 双 rc0 背书，**不宣称全绿**。"
    "｜**S6**：未跑（`Tools/s6_chain_bmc.py` 被对端写）。"
    "｜**S7**：`state round_no 2012→2013`（rounds_done 1950→1951，round_no_prev 留痕）；心跳经 `Tools/heartbeat_write.py apply` "
    "合并写（ack 329 未减）；`& Tools/register_loop_task.ps1` **phase ok**（machine=bm-c pin=0 current=0，首燃 11/23 23:45 未动）；"
    "`attrition_ledger_guard scan` **CLEAN**（4 账本，3 处历史缩行 healed 注记照录）；"
    "`pre-commit` / `pre-push` 与 `Tools/git-hooks/` 逐字节（CR 归一）**MATCH**，未重装、未用 --no-verify。"
    "｜**CEO 过程可见面**：当前活＝给整手账里那 22.83% 没投出去的钱按真实 GC001 逆回购定价，看现金腿帮的是哪一臂｜"
    "最近实物＝`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ASTOCK_VETO_CASH_LEG.md`"
    "（2026-11-23 23:4x·现金腿帮全池更多：B 11.38→11.71%/年、A 8.84→9.26%，B−A 比值 0.854→0.825，判词不变）＋"
    "`results\\astock_veto_cash_leg.json`＋`scripts\\astock_veto_cash_leg.py`（selftest 26/26）＋"
    "`results\\_r2013bmc_cash_leg_negative.py`（负控 18/18）｜"
    "下个里程碑＝（a）竞争窗结束后把本面接 S6 链腿 + 冒烟两腿（≤48h）；（b）现金腿的期限阶梯：GC001 之外接 GC007/GC014 的跨周末溢价，"
    "量出「保守口径」少算了多少（≤48h）。"
    "｜**未验证（如实）**：①现金腿只用 GC001（1 天期），未建模 7/14 天期阶梯（跨周末会更高，本面取保守）；"
    "②逆回购年化百分比按 `close/365` 折日收益、节假日前向填充，未处理真实申赎摩擦与额度；"
    "③记账口径是父面的 close(t)→close(t+20)，**没有**并进次日开盘的执行滞后（r2008/r2010 的面），两笔账分开算；"
    "④现金腿假设每期初全额扫入、期末全额赎回；⑤票池是现存标的（幸存者偏差，父面同），面板起于 2020-01-02；"
    "⑥本面是定价件，不是可交易策略：无仓位规则、无容量约束、无风控；⑦全量 smoke 与 S6 未跑（竞争窗）。"
    "｜**本地未达 origin commit 数**＝推送后复核。"
    "记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：给已有 family 加「现金腿」这条可执行性轴，属证据与载体）。|\n"
)

with io.open(P, "a", encoding="utf-8", newline="") as fh:
    fh.write(LINE)
print("appended %d chars -> %s" % (len(LINE), P))
