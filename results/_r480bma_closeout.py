import io
import json
import datetime
import time

now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S") + time.strftime("%z")[:3] + ":" \
    + time.strftime("%z")[3:] if False else now.isoformat(timespec="seconds")

line = (
    f"{ts} | r480 | dept:engineering | WM=py_low_board_clear green (board open=0 all tickets claimed | RW-5 freeze pending 10-03 external review = legal idle whitelist | red=False healthy) | "
    "Receipt round: D-20260930-40 (16:18 new row later than r479) read + executed in same round = "
    "CN-C7 wired into PREREG_TEMPLATE (round-trip cost bp must declare a single comparable number + asset-class routing + minimum commission tier), "
    "cadence-shortening law honored (Q4 slimming + CN-C7 both one-edit items delivered in the same round) | "
    "What was done: (1)**RW-7 DONE (T-127 close-out, last remaining item of D-05 credibility repair ticket)** = "
    "live/gateway.py sole order exit refactor: RiskGateRejected exception class (reject=exception, no silent drop) + "
    "check() strict mode (position cap 0.10/total cap 0.80/trade count cap 10/invalid side/halted-day BUY all throw) + "
    "daily_loss_breaker wired into check (halted day blocks new opens, de-risk sells pass) + gate_orders() sole exit funnel + "
    "emit_order_sheet rejects ungated orders (RuntimeError) -> exit_rules priority ladder + circuit breaker layer = permanent machine-check face; "
    "smoke 39->47/47 (8 new assertions: P1>P2 / P2>P3 (trailing stop 110.88 vs tier-2 10% conflict construction) / P4>P5 (loss-hold domain swallowed by decay) / P6 terminal tier / breaker -3% boundary / x5 rejection cases / halted-sell pass / emit sole-exit guard) "
    "(2)**D-20260930-40 CN-C7 wired** = research/PREREG_TEMPLATE.md cost-caliber section adds mandatory field: round-trip cost bp (Face A=knowledge/cost_spec.py derived ETF 26.082bp constant-identity + stock-side fee_schedule_for routing buy-side/sell-side declared separately + "
    "notional tier (¥20k minimum commission critical) attached) -- existing-file content revision = legal under RW-5 freeze "
    "(3)**D-20260930-27 Q4 marks slimming implemented + evaluated** = probe _r480bma_q4_marks_slim_eval.py (3-day window 66 ticks, 62 suppressible=93.9%, today 62 ticks 97% -- same direction as audit 86% and heavier) -> "
    "writer landing scripts/update_intraday_marks.py _tick_redundant() write-before-disk gate (keep-set: first-tick/settle/state-change/any-trader >=5bp/unpriced face/--force; suppression=zero disk write + one stdout line + rc0 legitimate no-op) + "
    "selftest S10-S13 all PASS (fixture shallow-copy self-contamination caught in-round and fixed) + CEO face results/Q4_MARKS_SLIMMING_20260930.md (before/after reconciliation table per D-40 expression discipline) "
    "(4)S0.5 double scan: orders 127/127 zero unacknowledged + decisions only one new row D-40 (disposition as above) (5)S6 chain all green rc0: dualrun ZERO-DRIFT 51/3 | compute_audit flags=pool_starvation+supply_floor (RW-5 freeze legal idle) | WM probe py_low_board_clear | update_daily zero new rows (cutoff 2026-09-29 holds, pre-holiday source not out) -> live.paper/t35/t24 trio conditional block skipped entirely honest | "
    "regime trigger breadth 0.83>=65% rc0 | scorecard 6/28/7 | CALL ORANGE_COOL | collection family all no-op/spawn legitimate (lhb 30min guard / heat already collected / futures/repo/options/sina_mf cutoff covered / moneyflow rank pass / ths 24min throttle / ah spawn throttled / fundamental 4.9h fresh / blayer all gates pass) | "
    "lane guards bm-a honest no-op x5 (astock/etf/minute/rev_osc/alloc) + fund_premium bm-c no-op | aggr/grid/sysv1 marks idempotent no-op | t35_export 2026-09-29 regenerated | dscore/dreport(five faces)/ceo_live(ORANGE cap50 COOL 6 members)/build_status/token delta=0 all rc0 "
    "(6)attrition CLEAN (4 ledgers, 1 healed note recorded as-is) (7)self-heal trio: loop pin=8 no-op Running + watchdog Ready 16:50 + claw installed (8)inbox zero unread | "
    "Verification evidence: smoke 47/47 + marks selftest S1-S13 PASS + Q4 probe deterministic + S6 all rc0 + epoch int self-check pending | "
    "Current activity: 10-01 month-first trio (science_audit/monthly_briefing/self_review); Latest deliverable: live/gateway.py sole order exit + smoke 47 (8 RW-7 assertions) + results/Q4_MARKS_SLIMMING_20260930.md (16:3x this round); "
    "Next milestone: 10-01 month-first trio + RW-5 external review 10-03 (after unfreezing, supply lines restored) -> M1 prereg (D-30 true calendar), window <=48h | "
    "next: r481 = 10-01 month-first trio + Q4 first live-fire watch (first suppression face of next trading day's 2nd tick) + M1 true calendar prerequisite (10-03 gate) [via bm-a]\n"
)

with io.open("round_reports-bm-a.md", "a", encoding="utf-8") as fh:
    fh.write(line)

# heartbeat update
hp = r"fleet\machines\bm-a.json"
h = json.load(io.open(hp, encoding="utf-8"))
epoch = int(time.time())
assert isinstance(epoch, int)
h["last_seen"] = now.strftime("%Y-%m-%dT%H:%M:%S%z")[:19] + time.strftime("%z")[:3] + ":" + time.strftime("%z")[3:] if False else now.isoformat(timespec="seconds")
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now.isoformat(timespec="seconds")
h["current_task"] = ("10-01 month-first trio (science_audit/monthly_briefing/self_review) + "
                     "Q4 slimming first real-fire watch + M1 true-calendar prerequisite (10-03 gate)")
h["verdict"] = ("r480 done: RW-7 sole-order-exit landed (smoke 39->47, T-127 close-out), "
                "D-40 CN-C7 wired into prereg template, Q4 marks slimming landed (93.9% "
                "suppressible measured, keep-faces intact), S6 rc0, orders 127/127")
h["orders_ack"] = sorted(set(h.get("orders_ack", [])))
json.dump(h, io.open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# self-check epoch int
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("round report appended; heartbeat epoch int", chk["heartbeat_epoch_utc"],
      "clock", chk["clock_read"])
