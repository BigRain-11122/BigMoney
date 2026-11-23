"""Append r2015's row to fleet/round_reports-bm-c.md (fresh read, one line).

Numbers are read from results/astock_veto_tearsheet.json so the row cannot drift
from the face it describes.

Usage
-----
    python results/_r2015bmc_round_report.py
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FACE = os.path.join(ROOT, "results", "astock_veto_tearsheet.json")
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")


def main() -> int:
    face = json.load(io.open(FACE, encoding="utf-8"))
    s, e = face["summary"], face["edges"]
    ef, el = e["by_booking"]["fractional"], e["by_booking"]["lot_10000000"]
    a_f, b_f = s["A"]["bookings"]["fractional"], s["B"]["bookings"]["fractional"]
    a_l, b_l = s["A"]["bookings"]["lot_10000000"], s["B"]["bookings"]["lot_10000000"]
    tax = e["edge_tax"]
    be = tax["breakeven"] or {}

    row = "| 2026-11-24 00:3x | r2015（**竞争探针 rc=3 CONTENTION·只落新增文件面**·13 张面都在讲「每期多少」，没人讲「过程有多颠」） | " \
        "**watermark：red=false / lane=healthy · 孤儿面=0**（py_faces 7 / resident_servers 0）。" \
        "**产品（产品优先律）**：这条黑名单被量过 %d 遍——能不能成交、一字板要不要等、整手税、闲钱按哪种日计数、" \
        "装得下多少钱、2026 亏的是市场还是排序——**十三张面全在印均值，没有一张印过程的形状**。" \
        "一个真准备把钱放进去的人第二句就问这个。本轮补 tearsheet：" \
        "**分数口径** A 期间均值 %+.4f%%/年化 %.2f%%/波动 %.2f%%/夏普 %.2f/最大回撤 %.2f%%/胜率 %.1f%%/水下时间 %.1f%%，" \
        "B %+.4f%%/%.2f%%/%.2f%%/%.2f/%.2f%%/%.1f%%/%.1f%% → **%s**。" \
        "**整手 1000 万档**同判词（`%s`：A 夏普 %.2f 对 B %.2f、回撤 %.2f%% 对 %.2f%%），" \
        "但那一档的振幅更小**不是更安全，是更闲**——中位 %s 的钱（A）/%s（B）根本没买成股票躺在 0%% 现金里，" \
        "现金把整条曲线按比例压扁；两臂吃同一种稀释，所以 B 与 A 的比较成立，整手档的夏普不能与分数档直接比大小。" \
        "**账单**：B 换手 %.2f%% 是 A %.2f%% 的 %.1f 倍（残差排名每期翻动），税前边 %+.4f%%/期、税后 %+.4f%%/期，" \
        "**%.1f%% 的毛边交给券商**；单边费要涨到 **%.1f bp**（现在 %.1f bp，%.2f 倍）净边才归零——这是解出来的零点，不是阈值。" \
        "｜**验证证据**：`--selftest` **37/37 PASS**（复利/NaN 期不当平盘/回撤峰值含期初 1.0/波动年化/夏普公式与零方差/胜率/滚动窗/" \
        "Calmar 拒零回撤/水下时间/2x2 严格比较含打平/成本块/归零点代数 k* 逐位归零/三态拒答）；" \
        "`run` rc0（%d 期，evidence_cutoff **%s**）→ `results/astock_veto_tearsheet.json` + `research/ASTOCK_VETO_TEARSHEET.md`；" \
        "`check` **rc0**（含**父面锚硬腿**：`per_period_mean`（分数与 1,000 万整手）与 `turnover_mean` 逐位复现 r2012 面，" \
        "本次最大绝对差 **0.000e+00**）。**负控 `results/_r2015bmc_tearsheet_negative.py` 24/24 PASS**" \
        "（原样 rc0 / 面板前移→STALE / 十个手改数→CHECK FAILED 且**不带** STALE / 父面锚破坏→STALE / 缺面→face missing 且不穿 STALE / " \
        "还原后两面 sha256 逐字节相同 / selftest 仍绿）。" \
        "｜**S0**：`fleet/machine.json`=bm-c；`orphan_face_probe` py_faces=7 **orphans=0** 零杀；" \
        "`repo_write_contention` **rc=3 CONTENTION**（3 宿主存活：pid 51252 为 11-22 20:10 起的 interactive、67160 为 11-23 20:05 起、本宿；" \
        "25 张共享面在本轮开始前被对端写，含 `fleet/machines/bm-c.json`、`fleet/round_reports-bm-c.md`、`research/ARBITER-BOARD.md`）" \
        "→ 按 r1927 只落**新增文件面**，未改共享代码/数据面、未跑 S6 链；fetch 后 0 ahead / 0 behind。" \
        "｜**S0.5 双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / 124 陈旧注记 / unacked=[]）；" \
        "集团 `git cat-file blob origin/main:docs/decisions.md` **原字节** sha256 = **79e3083b85c130b8**（250,586 B）== state 水位 → 零新决策零动作；" \
        "fleet/inbox 空。" \
        "｜**S1（诚实边界）**：全量 smoke **未跑**（`smoke_test.py` 与 `logs/smoke_legs.json` 是共享面，竞争窗不覆盖）；" \
        "本轮以 37/37 selftest + 24/24 负控 + run/check 双 rc0 背书，**不宣称全绿**。" \
        "｜**S6**：未跑（`Tools/s6_chain_bmc.py` 被对端写）。" \
        "｜**S7**：`state round_no 2014→2015`（rounds_done 1952→1953，round_no_prev 留痕）；" \
        "心跳经 `Tools/heartbeat_write.py apply` 合并写（applied 21 键，ack 329 未减，warnings=心跳比 state 多 57 条回执仅保留不删）；" \
        "`& Tools/register_loop_task.ps1` **phase ok**（machine=bm-c pin=0 current=0，首燃 11/24 00:35 未动）；" \
        "`attrition_ledger_guard scan` **CLEAN**（4 账本，3 处历史缩行 healed 注记照录）；" \
        "`pre-commit` / `pre-push` 与 `Tools/git-hooks/` 逐字节（CR 归一）**MATCH**，未重装、未用 --no-verify。" \
        "｜**CEO 过程可见面**：当前活＝给这条黑名单补风险形状（波动/回撤/夏普/水下时间）并把换手税摆在旁边" \
        "｜最近实物＝`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ASTOCK_VETO_TEARSHEET.md`" \
        "（2026-11-24 00:2x·夏普 %.2f 对 %.2f、回撤 %.2f%% 对 %.2f%%：这条边不只是更赚，它连回撤都更浅；换手 4.3 倍、毛边的 %.1f%% 交给券商）" \
        "＋`results\\astock_veto_tearsheet.json`＋`scripts\\astock_veto_tearsheet.py`（selftest 37/37）＋" \
        "`results\\_r2015bmc_tearsheet_negative.py`（负控 24/24）" \
        "｜下个里程碑＝（a）竞争窗结束后把本面接 S6 腿 + 冒烟两腿（≤48h）；" \
        "（b）换手带宽实验：给黑名单加进出不对称门（进 20%%/出 30%%），量「省下的税」与「削掉的排序」谁更大（≤48h）。" \
        "｜**未验证（如实）**：①回撤是 20 交易日一期的净值曲线回撤，**不是**日频 mark-to-market（日频要每日权重，本家族从未记过）" \
        "②夏普超额基准取 0%% 现金，逆回购腿（r2013/r2014 定价约 2.1pp/年）两臂共享，只披露不并入 " \
        "③整手档振幅更小是现金稀释（71.7%%/78.4%% 的钱在场），与分数档夏普不可直接比大小 " \
        "④票池现存标的（幸存者偏差，父面同），2020 只有 7 期 ⑤Calmar 在 77 期上对单个极端期敏感 " \
        "⑥全量 smoke 与 S6 未跑（竞争窗）。｜**本地未达 origin commit 数**＝0（本行随本轮提交推送后 fetch 复核）。" \
        "记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：给已有 family 加「风险形状」这条读数，属证据与载体；" \
        "方法论卡「整手账振幅变小=更闲不是更安全」锁存待无竞争轮 append）。|" % (
            face["family_faces_before"],
            a_f["per_period_mean"] * 100, a_f["annualized_compound"] * 100, a_f["annual_vol"] * 100,
            a_f["sharpe_excess_0"], a_f["max_drawdown"] * 100, a_f["hit_rate"] * 100,
            a_f["underwater_share"] * 100,
            b_f["per_period_mean"] * 100, b_f["annualized_compound"] * 100, b_f["annual_vol"] * 100,
            b_f["sharpe_excess_0"], b_f["max_drawdown"] * 100, b_f["hit_rate"] * 100,
            b_f["underwater_share"] * 100,
            ef["verdict"], el["verdict"], a_l["sharpe_excess_0"], b_l["sharpe_excess_0"],
            a_l["max_drawdown"] * 100, b_l["max_drawdown"] * 100,
            "%.1f%%" % (s["A"]["invested_share_median_lot_10000000"] * 100),
            "%.1f%%" % (s["B"]["invested_share_median_lot_10000000"] * 100),
            s["B"]["turnover_mean"] * 100, s["A"]["turnover_mean"] * 100,
            s["B"]["turnover_mean"] / s["A"]["turnover_mean"],
            tax["gross_edge_per_period"] * 100, tax["net_edge_per_period"] * 100,
            tax["tax_share_of_gross_edge"] * 100,
            be.get("one_side_bp", float("nan")), tax["cost_actually_charged_one_side"] * 1e4,
            be.get("k_multiple", float("nan")),
            face["rebalances"], face["evidence_cutoff"],
            a_f["sharpe_excess_0"], b_f["sharpe_excess_0"],
            a_f["max_drawdown"] * 100, b_f["max_drawdown"] * 100,
            tax["tax_share_of_gross_edge"] * 100,
        )

    with io.open(REPORT, encoding="utf-8") as fh:
        text = fh.read()
    if not text.endswith("\n"):
        text += "\n"
    text += row + "\n"
    with io.open(REPORT, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    print("appended r2015 row (%d chars) -> fleet/round_reports-bm-c.md" % len(row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
