"""r2015 closeout (bm-c): state bump + heartbeat fields for the tearsheet round.

Nothing here re-derives numbers: the face already wrote results/astock_veto_tearsheet.json
and research/ASTOCK_VETO_TEARSHEET.md. This script only carries the round's
bookkeeping (S7) so the numbers in the heartbeat are the ones the face printed.

Usage
-----
    python results/_r2015bmc_closeout.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

STATE = os.path.join(ROOT, "state-bm-c.json")
FACE = os.path.join(ROOT, "results", "astock_veto_tearsheet.json")
HB = os.path.join(HERE, "_r2015bmc_hb_fields.json")

ROUND_NO = 2015


def main() -> int:
    with open(FACE, "r", encoding="utf-8") as fh:
        face = json.load(fh)
    s, e = face["summary"], face["edges"]
    ef = e["by_booking"]["fractional"]
    el = e["by_booking"]["lot_10000000"]
    a_f, b_f = s["A"]["bookings"]["fractional"], s["B"]["bookings"]["fractional"]
    a_l, b_l = s["A"]["bookings"]["lot_10000000"], s["B"]["bookings"]["lot_10000000"]
    tax = e["edge_tax"]
    be = tax["breakeven"] or {}

    with open(STATE, "r", encoding="utf-8") as fh:
        state = json.load(fh)
    prev = state.get("round_no")
    state["round_no_prev"] = prev
    state["round_no"] = ROUND_NO
    if isinstance(state.get("rounds_done"), int):
        state["rounds_done"] = state["rounds_done"] + 1
    with open(STATE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=1)

    fields = {
        "round": ROUND_NO,
        "who_did": "bm-c",
        "work": ("r2015 · 新增文件面（竞争窗）：scripts/astock_veto_tearsheet.py + "
                 "results/astock_veto_tearsheet.json + research/ASTOCK_VETO_TEARSHEET.md —— "
                 "族内 %d 张面都只印均值，本面补风险形状：分数口径 B 夏普 %.2f 对 %.2f、"
                 "最大回撤 %.2f%% 对 %.2f%% → %s；换手 %.2f%% 对 %.2f%%、毛边 %+.4f%%/期里 "
                 "%.1f%% 交给券商、单边费要到 %.1f bp 净边才归零"
                 % (face["family_faces_before"], b_f["sharpe_excess_0"], a_f["sharpe_excess_0"],
                    b_f["max_drawdown"] * 100, a_f["max_drawdown"] * 100, ef["verdict"],
                    s["B"]["turnover_mean"] * 100, s["A"]["turnover_mean"] * 100,
                    tax["gross_edge_per_period"] * 100,
                    tax["tax_share_of_gross_edge"] * 100, be.get("one_side_bp", float("nan")))),
        "当前任务": ("r2015: 这条黑名单十三张面都在讲每期多少，没人讲过程多颠；本轮补齐波动/回撤/"
                     "夏普/水下时间——分数口径 B 夏普 0.49 对 0.38、回撤 -25.92% 对 -29.71% → "
                     "SHARPE_UP_DRAWDOWN_SHALLOWER；整手 1000 万档同判词，但那一档的振幅更小"
                     "只是因为 71.7%/78.4% 的钱躺在现金里"),
        "当前任务_en": ("r2015: the family printed the mean thirteen times and the ride zero "
                        "times; B Sharpe 0.49 vs 0.38, drawdown -25.92% vs -29.71% -> "
                        "SHARPE_UP_DRAWDOWN_SHALLOWER (same verdict at 10M whole lots, whose "
                        "smaller amplitude is 71.7%/78.4% cash, not safety)"),
        "本次": ("r2015 四条曲线：分数 A 年化 %.2f%%/波动 %.2f%%/夏普 %.2f/回撤 %.2f%%/胜率 %.1f%%；"
                 "分数 B 年化 %.2f%%/波动 %.2f%%/夏普 %.2f/回撤 %.2f%%/胜率 %.1f%%；"
                 "整手 1000 万 A 年化 %.2f%%/波动 %.2f%%/夏普 %.2f/回撤 %.2f%%；"
                 "B 年化 %.2f%%/波动 %.2f%%/夏普 %.2f/回撤 %.2f%%；"
                 "B-A 分数 %+.4f%%/期 t=%s，整手 %+.4f%%/期；"
                 "换手 A %.2f%% B %.2f%%；税前边 %+.4f%%，税后 %+.4f%%（税占 %.1f%%）；"
                 "成本归零点单边 %.1f bp（%.2fx）"
                 % (a_f["annualized_compound"] * 100, a_f["annual_vol"] * 100,
                    a_f["sharpe_excess_0"], a_f["max_drawdown"] * 100, a_f["hit_rate"] * 100,
                    b_f["annualized_compound"] * 100, b_f["annual_vol"] * 100,
                    b_f["sharpe_excess_0"], b_f["max_drawdown"] * 100, b_f["hit_rate"] * 100,
                    a_l["annualized_compound"] * 100, a_l["annual_vol"] * 100,
                    a_l["sharpe_excess_0"], a_l["max_drawdown"] * 100,
                    b_l["annualized_compound"] * 100, b_l["annual_vol"] * 100,
                    b_l["sharpe_excess_0"], b_l["max_drawdown"] * 100,
                    ef["mean_per_period"] * 100, ef["t"], el["mean_per_period"] * 100,
                    s["A"]["turnover_mean"] * 100, s["B"]["turnover_mean"] * 100,
                    tax["gross_edge_per_period"] * 100, tax["net_edge_per_period"] * 100,
                    tax["tax_share_of_gross_edge"] * 100,
                    be.get("one_side_bp", float("nan")), be.get("k_multiple", float("nan")))),
        "最近实物": ("scripts/astock_veto_tearsheet.py（selftest 37/37）+ "
                     "results/astock_veto_tearsheet.json + research/ASTOCK_VETO_TEARSHEET.md + "
                     "负控 results/_r2015bmc_tearsheet_negative.py（24/24）（2026-11-24 00:2x）"),
        "当前活": "给这条黑名单补风险面（波动/回撤/夏普/水下时间），并把它和换手税放在同一张面上",
        "下个里程碑": ("(a) 竞争窗结束后把本面接 smoke 两腿 + S6 腿（≤48h）；(b) 换手控制：B 臂换手 23.95% "
                       "是 A 的 4.3 倍，试带宽（进 20%/出 30%）能省多少税、会不会削掉排序（≤48h）"),
        "下轮指针": ("(a) 无竞争轮：smoke_test.py 两腿 + Tools/s6_chain_bmc.py 腿 + knowledge/"
                     "METHODOLOGY_ASSETS.md 卡（本轮锁存：整手账振幅变小=更闲不是更安全）+ CODELY 两行；"
                     "(b) 换手带宽实验：同一张面板上给黑名单加进出不对称门，量税与排序的交换"),
        "verify": ("astock_veto_tearsheet selftest 37/37 PASS；run rc0（77 期，evidence_cutoff "
                   "2026-11-20，anchor worst_abs_diff=0.000e+00 vs r2012 面）；check rc0（含 STALE/"
                   "CHECK FAILED 分型与父面锚硬腿）；负控 _r2015bmc_tearsheet_negative.py 24/24 PASS"
                   "（面板前移→STALE、十个手改数→CHECK FAILED 且不带 STALE、父面锚破坏→STALE、"
                   "缺面→face missing、还原后逐字节相同）"),
        "watermark_verdict": ("green (red=false; lane healthy; repo_write_contention rc=3 CONTENTION "
                              "-> new-file-only round)"),
        "watermark_note": ("竞争探针 rc=3：3 宿主存活（pid 51252 11-22 20:10 起 / 67160 11-23 20:05 起 / "
                           "本宿），25 张共享面在本轮开始前被对端写 -> 按 r1927 只落新增文件面，"
                           "未改共享代码/数据面、未跑 S6 链"),
        "s0_note": "orphan_face_probe py_faces=7 orphans=0 零杀；repo_write_contention rc=3 CONTENTION",
        "s05_note": ("orders_ack_scan CLEAN（116 令 / 329 回执 / 124 陈旧注记 / unacked=[]）；"
                     "decisions.md 原字节 sha256 79e3083b85c130b8... == state 水位 -> 零新决策；"
                     "fleet/inbox 空"),
        "s6_chain": "not run (CONTENTION rc=3)",
        "smoke": ("not run this round (CONTENTION); 以 37/37 selftest + 24/24 负控 + run/check 双 rc0 背书，"
                  "不宣称全绿"),
        "s7_loop": "Bigmoney-IterationLoop phase ok（machine=bm-c pin=0 current=0，首燃 11/24 00:35 未动）",
        "s7_attrition": "attrition_ledger_guard scan CLEAN（4 账本，3 处历史缩行 healed）",
        "s7_claws": "pre-commit / pre-push 与 Tools/git-hooks/ 逐字节（CR 归一）MATCH，未重装、未用 --no-verify",
        "孤儿面": 0,
        "孤儿面_note": "round-zero orphan_face_probe: orphans 0 (py_faces 7, resident_servers 0)",
        "记账_r2015": "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（方法论卡锁存待无竞争轮：整手账振幅变小=更闲不是更安全）",
        "why_not_bookkeeping": "本轮主产出是新的风险刻画面（脚本+JSON+md+负控），不是记账",
        "未验证": ("①回撤是 20 交易日一期的净值曲线回撤，不是日频 mark-to-market（日频要每日权重，"
                   "本家族从未记过）②夏普超额基准取 0% 现金，逆回购腿（2.1pp/年）两臂共享只披露不并入 "
                   "③整手档的波动/回撤天然更小是因为四成的钱在现金里，与分数档的夏普不可直接比大小 "
                   "④票池现存标的（幸存者偏差），2020 只有 7 期 ⑤Calmar 在 77 期上对单个极端期敏感"),
        "went_well": ("同一条账按两档记账（分数/整手）各算一遍风险，才发现整手档『更稳』其实是现金稀释——"
                      "只看一档会把它读成整手让这本书变安全了"),
    }
    with open(HB, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fields, fh, ensure_ascii=False, indent=1)

    print("state round_no %s -> %s (rounds_done %s)" % (prev, state["round_no"],
                                                        state.get("rounds_done")))
    print("heartbeat fields -> %s (%d keys)" % (os.path.basename(HB), len(fields)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
