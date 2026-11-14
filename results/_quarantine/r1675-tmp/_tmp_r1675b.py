import io
import json
import time

TS = "2026-11-14T18:13:00+08:00"

with io.open("round_reports-bm-c.md", "a", encoding="utf-8", newline="") as fh:
    fh.write(
        "| 2026-11-14 18:1x | 1675b | **ADDENDUM（收尾）**："
        "送达＝`793e0a0aff`（7ceec548bb..793e0a0aff，9 件 +174/‐42），fetch 后 **0 ahead / 0 behind**；"
        "S0.5 二扫 orders_delta=false／decisions_delta=false／unacked=[] rc0；"
        "S7＝loop pin=5 no-op（首次 18:10 未打）/ 看门狗在位但 **S4U XML 翻转第 27 次被拒**（落回默认 principal，"
        "LogonType 回归面待提权重跑）/ 两钩子 LF 归一重装 / attrition CLEAN（4 账本，2 历史缩行 healed）；"
        "孤儿面=1（集团 agent.py，非本司面）。**记账**：本行 1 处。"
        "本地未达 origin commit 数=0。 |\n"
    )

sp = "state-bm-c.json"
st = json.load(io.open(sp, encoding="utf-8"))
st["ts"] = TS
st["updated"] = TS
st["updated_at"] = TS
st["s7"] = ("loop pin=5 no-op (first fire 18:10) | watchdog in place, first fire 18:08 | "
            "pre-commit claw LF-normalized reinstall | pre-push claw LF-normalized reinstall | "
            "attrition CLEAN (4 ledgers, 2 historic shrinks healed)")
st["s7_notes"] = "watchdog S4U XML flip refused for the 27th time -> task left at default principal (needs manual S4U re-pass)"
st["s05_second_scan"] = "收尾复扫 0 未回执"
st["sync"] = {"ahead_origin": 0, "behind_origin": 0, "commit": "793e0a0aff"}
json.dump(st, io.open(sp, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)

hp = "fleet/machines/bm-c.json"
hb = json.load(io.open(hp, encoding="utf-8"))
hb["last_seen"] = TS
hb["ts"] = TS
hb["clock_read"] = TS
hb["heartbeat_epoch_utc"] = int(time.time())
hb["activity_now"] = "CEO 页票据句按票据自己的 bar 定词（今日债 1→0）"
hb["activity_now_round"] = 1675
hb["chain_verdict"] = "dualrun ZERO-DRIFT 51 + py_watermark py_low_with_work_cands + attrition CLEAN; full chain not run"
hb["s4u_note"] = "watchdog S4U flip refused 27th time (default principal)"
json.dump(hb, io.open(hp, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
assert isinstance(json.load(io.open(hp, encoding="utf-8"))["heartbeat_epoch_utc"], int)
print("closed")
