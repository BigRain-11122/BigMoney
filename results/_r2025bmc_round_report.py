"""Append the r2025 round-report line (fresh read-modify-write, utf-8, no BOM)."""

from __future__ import annotations

import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")

LINE = (
    "| 2026-11-24 04:4x | r2025（**竞争探针 rc=3 CONTENTION·只落新增文件面**·九条选档规则赛马："
    "谁活过了样本外） | **watermark：red=false / lane=healthy · 孤儿面=0**（py_faces=4 / "
    "resident_servers=1=ComfyUI 空闲）。**产品（产品优先律）**：r2023 从回撤预算挑了档位、r2024 把同一批预算"
    "换到日频尺上发现「规则 A 买过头」，但两轮都只是**一个**挑法，没人问「换一种挑法会不会一样」。本面把这个问题"
    "做成赛马：九条规则冻结在跑之前，全部只看 IS（date<=2023-12-31，43 期），全部只在 OOS（34 期 / 680 个盯市日）"
    "上读。**读数一（20% 预算：机械的一单位 beta 活，8 个拟合挑法里 5 个死）**：k=1.00 不挑不选，IS 回撤 12.25% / "
    "年化 8.32%，OOS **19.89%**（20% 预算内）/ 9.82%；同预算下拟合家族只有 A_PERIOD（k=0.65→18.74%/12.88%）、"
    "MID_DAILY 与 MAX_SHARPE（k=0.95→19.48%/10.30%）活，其余五个破 20%：A_DAILY（k=1.10→20.74%）、"
    "B_MARGIN（0.50→20.22%）、MIN_IS_DD（1.05→20.29%）、B_DAILY（0.35→21.71%）、B_PERIOD（0.15→23.72%）。"
    "**读数二（死的在两侧，不是单调）**：活的落在 k≈0.65–0.95 一带，死的在带下（0.15/0.35/0.50 全落在 20.2–23.7%，"
    "把预算当上限花光就是买得太少，而回撤是空头没削掉的那部分）和带上（1.05/1.10，空头自己的波动开始变成回撤）。"
    "**读数三（10% 与 15% 预算在样本外根本不存在）**：全网格 OOS 最浅 **18.07%**（k=0.75，事后挑），两档无论谁挑都"
    "判 NO_BUDGET_IS_HELD——比 r2024 的「日频地板 12.07%」更硬，那是 IS 地板，这是 OOS 地板。**读数四（25% 预算下"
    "拟合确实帮了忙）**：FITTING_HELPS，7/8 拟合挑法守住，其中 5 个比 k=1.00 的 9.82% 拿到更多年化。**读数五（给每条"
    "规则标价：34 期只是几次观测）**：圆形块自助（块=4 期/80 bar，600 抽，种子 20261124）下 20% 预算的守预算概率——"
    "k=1.00 **0.69**、MIN_IS_DD 0.69、MID_DAILY 0.68，而 r2023 的 A_PERIOD 只有 **0.34**（点读数更好但贴预算线，"
    "样本不确定性更大）；10% 预算下全场 ≤0.09。｜**验证证据**：`--selftest` **18/18 PASS**；`run` rc0（77 期 / IS 43 / "
    "OOS 34 / 680 盯市日，evidence_cutoff **2026-11-20**）→ `results/astock_veto_hedge_picker.json` + "
    "`research/ASTOCK_VETO_HEDGE_PICKER.md`；`check` **rc0**（9 挑法 × 4 预算逐格从 41 条已发布曲线重推 + "
    "survivors/breakers 覆盖性 + 判词重判 + 单调性不变量）；**锚腿**：k=0 的日频全窗回撤与父面逐位相等（gap **0.0**）、"
    "k=1.00 的 OOS 与父面逐位相等（gap **0.0**）、A_PERIOD 在 20% 预算重推出 r2023 的 **k=0.65**、k=0.65/1.00 两臂 "
    "154 期对父面 `arm_series` 最大缺口 **5.2e-15**。**负控 `results/_r2025bmc_picker_negative.py` 13/13 PASS**，"
    "并当场抓到一枚真缺陷：首版 `check` 在某条曲线缺 `daily_oos` 时直接 KeyError 崩掉——崩掉的自检等于没有自检，"
    "已修为「挑法指向的曲线缺读数=CHECK FAILED 并点名」。｜**S0**：`fleet/machine.json`=bm-c；`orphan_face_probe` "
    "py_faces=4 **orphans=0** 零杀；`repo_write_contention` **rc=3 CONTENTION**（2 宿主存活：pid 51252＝11-22 20:10 "
    "起的 interactive 常驻；20 张共享面在本轮开始前被对端写，重叠窗内 0 张）→ 按 r1927 只落**新增文件面**，未改共享"
    "代码/数据面、未跑 S6 链、未跑全量 smoke；fetch 后 0 ahead / 0 behind。｜**S0.5 双扫**：`Tools/orders_ack_scan.py` "
    "**CLEAN**（116 令 / 329 回执 / 124 陈旧注记 / unacked=[]）；集团 `git cat-file blob "
    "origin/main:docs/decisions.md` **原字节** sha256 = **79e3083b85c130b8**（250,586 B）== state 水位 → 零新决策零"
    "动作；fleet/inbox 0 件。｜**S1（诚实边界）**：全量 smoke **未跑**（`smoke_test.py` 与 `logs/smoke_legs.json` 是"
    "对端写的共享面，竞争窗不覆盖）；本轮以 18/18 selftest + 13/13 负控 + run/check 双 rc0 + 四条锚腿背书，**不宣称"
    "全绿**。｜**S6**：未跑（链腿与链产物为共享面）。｜**S7**：`state round_no 2024→2025`（rounds_done 1960→1961）；"
    "心跳经 `Tools/heartbeat_write.py apply` 合并写；`& Tools/register_loop_task.ps1` **phase ok**（machine=bm-c "
    "pin=0 current=0）；`attrition_ledger_guard scan` **CLEAN**（4 账本，2 处历史缩行 healed 注记照录）；"
    "`pre-commit`/`pre-push` 与 `Tools/git-hooks/` 逐字节（CR 归一）**MATCH**。｜**CEO 过程可见面**：当前活＝把"
    "「怎么选对冲档位」本身做成九条规则的赛马，并在同一批小样本上给每条规则标价｜最近实物＝"
    "`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ASTOCK_VETO_HEDGE_PICKER.md`（2026-11-24 04:4x·20% 预算"
    "下机械一单位 beta 活 19.89%、8 个拟合挑法死 5 个；活的是一带 0.65–0.95，死在带两侧；10%/15% 预算在样本外不"
    "存在，地板 18.07%）＋`results\\astock_veto_hedge_picker.json`＋`scripts\\astock_veto_hedge_picker.py`"
    "（selftest 18/18）＋`results\\_r2025bmc_picker_negative.py`（负控 13/13）｜下个里程碑＝（a）竞争窗结束后把本面"
    "接 S6 链腿 + 冒烟两腿（≤48h）；（b）把「一个单位 beta」写成默认档，并把九条规则的淘汰写成一条常设判断"
    "（≤48h）。｜**未验证（如实）**：①仍是 77 期（IS 43 / OOS 34），「活/死」是一次观测，自助只给不确定性不造新"
    "信息；②日频盯市仍是入场即等权、期内不调仓的固定股数篮子；③追保与强平未建模；④空头腿 as-traded 不含分红、"
    "成本只按 flat carry 计；⑤票池现存标的（幸存者偏差，父面同）；⑥全量 smoke 与 S6 未跑（竞争窗），本面尚未接链。"
    "｜**本地未达 origin commit 数**＝推送后复核。记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增："
    "「同一个决定有九种挑法」属证据与载体，不新立方法）。 |\n"
)


def main() -> int:
    with io.open(REPORT, "r", encoding="utf-8", newline="") as fh:
        text = fh.read()
    if not text.endswith("\n"):
        text += "\n"
    text += LINE
    with io.open(REPORT, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    print("appended %d chars to fleet/round_reports-bm-c.md" % len(LINE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
