# -*- coding: utf-8 -*-
# r709 bm-c close addendum: delivery-face correction (honesty law, no false
# claims). main push raced x2 (bm-a hot window d3b0737fe -> e069782f7c) ->
# machine/bm-c-r709 branch delivery VERIFIED (origin/machine/bm-c-r709 == HEAD
# 0163a0048); 2 commits unreached on main, S0 auto-carry next round (no
# force-push). Round-report addendum line + heartbeat/state claim surgery
# (r504 JSON-surgery-through-script law).
import json, datetime, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")

RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
line = (TS + " | r709 补记 | 送达面勘正（诚实律·禁假宣称）：main push 两拒（竞态窗：non-fast-forward→pull --rebase 到 d3b0737fe→再拒=origin 再进 e069782f7c·bm-a 热推窗）"
  "→按律 machine/bm-c-r709 分支代投 VERIFIED（origin/machine/bm-c-r709=0163a0048=HEAD）"
  "·本地未达 origin/main commit 数=2（churn absorb+closeout·下轮 S0 rebase 自动代投·禁 force-push 遵从）"
  " | 轮报告前段「本地未达 origin commit 数=0」声明以本行勘正为准 | 无其他改动\n")
with io.open(RR, "a", encoding="utf-8") as f:
    f.write(line)

FIXED_SUMMARY = ("r709: QDII premium watch landed (baseline 46/87, median -0.481%), D-20261007-07 consumed (no new duty), S6 38 rc0 streak 29, "
  "QA 5/5 det-30th, smoke 48/48, delivery: main push raced x2 (bm-a hot window) -> machine/bm-c-r709 branch VERIFIED, 2 unreached-main commits S0-carry next round.")

HP = os.path.join(ROOT, "state-bm-c.json")
st = json.load(io.open(HP, encoding="utf-8-sig"))
st["last_round_summary"] = FIXED_SUMMARY
st["last_action"] = FIXED_SUMMARY
st["note"] = (st.get("note", "") + " Delivery: main raced x2 -> machine/bm-c-r709 branch per fallback law (2 commits S0-carry).")
json.dump(st, io.open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(io.open(HB, encoding="utf-8-sig"))
hb["last_round_summary"] = FIXED_SUMMARY
hb["last_action"] = FIXED_SUMMARY
hb["health"] = ("alive (r709 QDII observation + decision-delta round clean: loop pin=5, watchdog registered, SAT alive rc0, QA 5/5 determinism 30th, "
  "smoke 48/48, S6 38/38 rc0 dualrun streak 29, orders double-sweep zero-delta unacked=0, DEC CHANGED->D-20261007-07 consumed, orphan face=1 ComfyUI "
  "no-kill documented, idle NOT-GREEN resident load idle_rounds=0 worked-declared, DELIVERY: main raced x2 -> machine/bm-c-r709 VERIFIED, 2 unreached-main commits S0-carry next round)")
hb["note"] = (hb.get("note", "") + " Delivery: main raced x2 (bm-a hot window) -> machine/bm-c-r709 branch per fallback law.")
json.dump(hb, io.open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("addendum ok: round-report line + state/heartbeat delivery claims corrected @ %s" % TS)
