"""r2014 closeout: bump state-bm-c.json (round_no 2013 -> 2014)."""
import io
import json
import os
import time
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "state-bm-c.json")

s = json.load(io.open(P, encoding="utf-8"))
s["round_no_prev"] = s.get("round_no")
s["round_no"] = 2014
s["rounds_done"] = s.get("rounds_done", 1951) + 1

s["当前任务"] = (
    "r2014: 修正现金腿的日计数——r2013 按「交易日」给 GC001 计息（每步 1 天），"
    "而回购按自然日付息；20 个交易日实际占款 30.1 自然日，所以现金腿被低估 53%。"
    "改对后：GC001 年化 1.37→2.10pp（×1.531），1000 万档 B 11.71→11.88%、A 9.26→9.48%；"
    "期限阶梯（28 天期买定）只再多 +0.11pp——钱在日计数里，不在期限溢价里"
)
s["当前任务_en"] = (
    "r2014: the cash leg was paid per trading day, but repo accrues on natural days; "
    "20 trading days span 30.1 natural days, so r2013 under-stated the cash leg by 53%. "
    "Fixed: GC001 1.37 -> 2.10 pp/yr (x1.531); at 10M B 11.71 -> 11.88%, A 9.26 -> 9.48%; "
    "a 28-day ladder adds only +0.11pp more -- the money is in the day count, not the term premium"
)
s["当前活"] = "把没投出去的钱按自然日重新计息，看 r2013 保守口径少算了多少、期限阶梯值不值"
s["最近实物"] = (
    "scripts/astock_veto_cash_daycount.py（selftest 23/23）+ results/astock_veto_cash_daycount.json + "
    "research/ASTOCK_VETO_CASH_DAYCOUNT.md + 负控 results/_r2014bmc_daycount_negative.py（21/21）（2026-11-24 00:0x）"
)
s["下个里程碑"] = (
    "(a) 竞争窗结束后把本面接 smoke 两腿 + S6 腿（≤48h）"
    "(b) 把「现金腿日计数」做成通用检查项：任何涉及闲置现金的账面收益，先问它按哪种日计数计息（≤48h）"
)
s["下轮指针"] = (
    "(a) 无竞争轮：smoke_test.py 两腿 + Tools/s6_chain_bmc.py 腿 + knowledge/METHODOLOGY_ASSETS.md 卡 + CODELY 两行 "
    "(b) 现金腿已到 2.10pp/yr；若要再进一步，只剩「真实申赎摩擦与单笔门槛」，量级应远小于日计数"
)
s["本次"] = (
    "r2014: 日计数修正。trading 1.369pp/yr（复现 r2013 逐位）/ calendar 2.096（×1.531）/ ladder 2.209（自然日+28天期）；"
    "10M 档 A 9.26→9.48→9.51%、B 11.71→11.88→11.91%；B-A 0.2004→0.1968→0.1962%/期，"
    "比值 0.825→0.810→0.808，判词不变仍 EDGE_DEGRADES_UNDER_ROUNDING；父面锚 worst_abs_diff=0.0"
)

now = datetime.now(timezone(timedelta(hours=8)))
s["clock_read"] = now.isoformat(timespec="seconds")
io.open(P, "w", encoding="utf-8", newline="\n").write(
    json.dumps(s, ensure_ascii=False, indent=1) + "\n")

hb = {
    "last_seen": now.isoformat(timespec="seconds"),
    "ts": now.isoformat(timespec="seconds"),
    "clock_read": now.isoformat(timespec="seconds"),
    "heartbeat_epoch_utc": int(time.time()),
    "activity_now": "r2014 cash-leg day count corrected (trading-day vs natural-day interest), ladder priced",
    "activity_now_round": 2014,
    "verdict": "healthy",
    "idle_rounds": 0,
    "agenda_starved": False,
}
hb_path = os.path.join(ROOT, "results", "_r2014bmc_hb_fields.json")
io.open(hb_path, "w", encoding="utf-8", newline="\n").write(
    json.dumps(hb, ensure_ascii=False, indent=1) + "\n")
print("state round_no=%s rounds_done=%s prev=%s" % (
    s["round_no"], s["rounds_done"], s["round_no_prev"]))
print("hb fields -> %s" % hb_path)
