"""r671 T-166 closure: flip ticket to done with evidence, preserve all existing fields."""
import json, io, datetime

P = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\fleet\tasks\T-2026-10-04-166-P1.json"
j = json.load(open(P, encoding="utf-8"))
assert j.get("status") == "claimed" and j.get("claimed_by") == "bm-a", "lane guard: not my claimed ticket"

now = "2026-10-04T10:4x+08:00"
j["status"] = "done"
j["done_at"] = now
j["result_ref"] = ("results/fund_statement_update_status.json (complete=true, 86/86 periods, cutoff 20260630, rows_total 1,038,171, zero_row_periods=[])"
                   " + data/fund_statement_export/{cashflow,balance,income}_faces.parquet (292,537/283,955/461,679 rows, 86 periods each, PIT avail_date col)"
                   " + spec research/shortline/FUND_STATEMENT_PANEL.md + closure probe results/_r671bma_t166_close.py (CLOSURE GATE PASS)")
j["progress_r671"] = ("r671 closure (bm-a): backfill relaunched 07:44 (adopt note) completed ~09:53 -- status face mode='no-op: all 86 periods done', "
                      "complete=true, requests_used=251, zero_row_periods=[], faces re-assembled cashflow 292,537 / balance 283,955 / income 461,679 rows. "
                      "Closure verification: selftest ALL-PASS rc0 + parquet read-back 86/86 periods x 3 faces + TTM helper ttm_from_cumulative importable + "
                      "income face carries per-share CFO col (piece-4 accrual-wedge supply face). UNLOCKED per ticket purpose: piece-4 (candidate A CFO-NI wedge, "
                      "DIGEST-20261004-fund-domain-recheck sec.4) + piece-5 reserve legs (FFScore partial dROA/d_leverage) + census gross_profitability flip "
                      "candidate (income face now present; flip decision routed to GM/fund-domain consensus -- NOT flipped unilaterally this round). "
                      "Consumption routing honored: piece-4 prereg drafting stays gated on trio judged finalize (DIGEST sec.4: zero prereg/burn this window, "
                      "D6 corr vs VALUE family measurable only post-judged-face).")
json.dump(j, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
# write-back self-check
back = json.load(open(P, encoding="utf-8"))
assert back["status"] == "done" and back.get("result_ref")
print("T-166 closed, json reparse OK, fields:", len(back))
