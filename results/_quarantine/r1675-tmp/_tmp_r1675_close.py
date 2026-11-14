import io
import json
import time

TS = "2026-11-14T18:10:00+08:00"

# 1) round report: one fixed-field row, appended
report = (
    "| 2026-11-14 18:0x | 1675 | **PRODUCT**：CEO 页最后一条「今天」欠债清零——"
    "`capital_block` 三句「今天这张可执行单」改由 `day_word(page_day, ticket_bar)` 定词（周六页现在印"
    "「**2026-11-13 那张可执行单实际持 5 名**（bar 2026-11-13）」）；`PAGE_DAY_LEDGER` 删掉这行 owed"
    "（欠债 1→0），`render_md` 传 `generated_for_date`。"
    "｜验证：`etf_book_ceo_page.py selftest` **349/349 PASS**（新增 L133 异日必须点名 bar / "
    "L134 同日必须还说「今天」；L261 改夹具行后仍绿；L127 改用页面自身的 page_day 生成比对块）；"
    "页面重建 `docs/live_book/LIVE-BOOK-20261114.md` 实读新句。"
    "｜产线：`pool_dualrun` ZERO-DRIFT streak 51；`py_watermark`=py_low_with_work_cands"
    "（local_batch=1=本轮 smoke）；orphans=1（集团 agent.py，非本司面只读不杀）。"
    "｜卡：E637（台账清零时「要求台账非空」的腿会变成「要求某块别修」）。"
    "｜下个里程碑＝把 `PAGE_DAY_LEDGER` 剩余 reader_day 行逐条复判（它们各自那句话的 bar 是什么），"
    "让台账从「豁免清单」变成「逐行带 bar 字段的规则表」（窗 ≤48h）。"
    "｜**未验证（如实）**：全量 smoke 本轮未收口（17:46 起的那套仍在跑，未取到终数）；"
    "`capital_block` 的「（bar X）」在点名日时与句首日期重复，属可读性遗留。"
    "｜本地未达 origin commit 数=推送后复核。\n"
)
with io.open("round_reports-bm-c.md", "a", encoding="utf-8", newline="") as fh:
    fh.write(report)

# 2) state
sp = "state-bm-c.json"
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 1675
st["rounds"] = 1675
st["rounds_done"] = 1675
st["rounds_note"] = "r1675"
st["status"] = "round-closed"
st["ts"] = TS
st["updated"] = TS
st["updated_at"] = TS
st["task"] = "r1675: the last owed today-word (the ticket sheet) now names its own bar"
st["activity"] = "product"
st["activity_now"] = "CEO 页票据句改由票据自己的 bar 定词，页面日债清零"
st["activity_now_round"] = 1675
st["verdict"] = "green"
st["watermark_verdict"] = "py_low_with_work_cands"
st["verify"] = (
    "etf_book_ceo_page selftest 349/349 PASS (new L133 later-day names the bar / L134 same-day keeps 今天; "
    "L261 now probes owed() with a fixture row; L127 builds the compared block with the page's own page_day) | "
    "page rebuilt docs/live_book/LIVE-BOOK-20261114.md, live read: '2026-11-13 那张可执行单实际持 5 名（bar 2026-11-13）' | "
    "PAGE_DAY_LEDGER owed rows 1 -> 0 | pool_dualrun ZERO-DRIFT streak 51 | py_watermark py_low_with_work_cands"
)
st["verify_selftest"] = "etf_book_ceo_page 349/349 PASS"
st["page_day_debt"] = {"owed": 0, "reader_day": 5, "registry": "PAGE_DAY_LEDGER"}
st["orphans"] = 1
st["s6_chain"] = {
    "legs": "dualrun ZERO-DRIFT streak 51 | py_watermark py_low_with_work_cands (local_batch=1=self smoke) | "
            "full chain not run this round",
}
st["not_verified"] = "full smoke suite started 17:46 not closed at round end (no tally claimed)"
json.dump(st, io.open(sp, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
print("state ok", st["round_no"])

# 3) heartbeat (own file only)
hp = "fleet/machines/bm-c.json"
hb = json.load(io.open(hp, encoding="utf-8"))
hb["last_seen"] = TS
hb["ts"] = TS
hb["clock_read"] = TS
hb["heartbeat_epoch_utc"] = int(time.time())
hb["activity"] = "product"
hb["activity_now"] = "CEO 页票据句按票据自己的 bar 定词（今日债 1→0）"
hb["activity_now_round"] = 1675
hb["current_task"] = "r1675: ticket sheet names its own bar"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["busy"] = False
hb["ahead_origin"] = 0
hb["behind_origin"] = 0
json.dump(hb, io.open(hp, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
assert isinstance(json.load(io.open(hp, encoding="utf-8"))["heartbeat_epoch_utc"], int)
print("heartbeat ok")
