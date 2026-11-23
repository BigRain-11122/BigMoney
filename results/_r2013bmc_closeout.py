"""r2013 closeout: bump state-bm-c.json (round_no 2012 -> 2013)."""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "state-bm-c.json")

s = json.load(io.open(P, encoding="utf-8"))
s["round_no_prev"] = s.get("round_no")
s["round_no"] = 2013
s["rounds_done"] = s.get("rounds_done", 1950) + 1

s["当前任务"] = (
    "r2013: 整手取整的账上那 22.83% 没投出去的钱（1000 万档）如果收盘扫进 GC001，"
    "整手账从 11.38% 涨到 11.71%/年（+0.33pp），全池臂从 8.84% 涨到 9.26%（+0.42pp）——"
    "现金腿帮全池更多，B-A 从 +0.2074% 掉到 +0.2004%/期（比 0.854→0.825），判词不变仍 EDGE_DEGRADES"
)
s["当前任务_en"] = (
    "r2013: the 22.83% cash leg at 10M earns GC001; the black-list arm goes 11.38 -> 11.71%/yr, "
    "the full pool 8.84 -> 9.26%/yr -- cash helps the full pool more, B-A 0.2074 -> 0.2004%/period "
    "(ratio 0.854 -> 0.825), verdict unchanged"
)
s["当前活"] = "给整手账里那 22.83% 没投出去的钱按真实 GC001 逆回购定价，看现金腿帮的是哪一臂"
s["最近实物"] = (
    "scripts/astock_veto_cash_leg.py（selftest 26/26）+ results/astock_veto_cash_leg.json + "
    "research/ASTOCK_VETO_CASH_LEG.md + 负控 results/_r2013bmc_cash_leg_negative.py（18/18）（2026-11-23 23:4x）"
)
s["下个里程碑"] = (
    "(a) 竞争窗结束后把本面接 smoke 两腿 + S6 腿（≤48h）"
    "(b) 把「整手把书换成另一本书」做成通用件：任何等权广度策略立项时先算价格倾斜与在场比例（≤48h）"
)
s["下轮指针"] = (
    "(a) 无竞争轮：smoke_test.py 两腿 + Tools/s6_chain_bmc.py 腿 + knowledge/METHODOLOGY_ASSETS.md 卡 + CODELY 两行 "
    "(b) 现金腿的期限阶梯：GC001 之外接 GC007/GC014 的跨周末溢价，看保守口径少算了多少"
)
s["本次"] = (
    "r2013: 1000 万档 A 臂在场 70.38%/现金 29.62%，B 臂在场 77.17%/现金 22.83%（差 +6.79pp）；"
    "GC001 期间收益均值 +0.1079%（年化 +1.37%）；net 0%→真 A 8.84→9.26，B 11.38→11.71；"
    "B-A 0.2074→0.2004%/期（t 3.04→2.93），比值 0.854→0.825；50M 档 0.941→0.935 仍 EDGE_SURVIVES"
)
s["本轮"] = s["本次"]
s["记账_r2013"] = (
    "本行 1 处（轮报告）+ state 1 处 + 心跳 1 处 = 3（无方法论新增：给已有 family 加「现金腿」这条可执行性轴，属证据与载体）"
)
s["watermark_verdict"] = "green (red=false; lane healthy; repo_write_contention rc=3 CONTENTION -> new-file-only round)"
s["watermark_note"] = (
    "竞争探针 rc=3：3 宿主存活（pid 51252 11-22 20:10 起 / 67160 11-23 20:05 起 / 本宿），"
    "27 张共享面在本轮开始前被对端写，含 fleet/machines/bm-c.json、fleet/round_reports-bm-c.md、research/ARBITER-BOARD.md "
    "-> 按 r1927 只落新增文件面，未改共享代码/数据面、未跑 S6 链"
)
s["孤儿面"] = 0

io.open(P, "w", encoding="utf-8", newline="").write(json.dumps(s, ensure_ascii=False, indent=1))
print("state round_no %s rounds_done %s" % (s["round_no"], s["rounds_done"]))
