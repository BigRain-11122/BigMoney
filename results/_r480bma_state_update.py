import json
import datetime

p = r'state-bm-a.json'
s = json.load(open(p, encoding='utf-8'))
s['round_no'] = 480
s['did'] = ("r480: RW-7 DONE (T-127 close-out): RiskGate.check strict reject=exception "
            "(RiskGateRejected on position/total/trade caps + invalid side + halted-day BUY; "
            "daily_loss_breaker wired into check; sells still pass on halted day) + "
            "gate_orders() sole-exit funnel + emit_order_sheet refuses ungated orders -> "
            "smoke 39->47 (8 new RW-7 assertions: P1>P2, P2>P3 trailing-stop-vs-tier-2, "
            "P4>P5 overlap dominance, P6 terminal tier, breaker boundary, rejections-raise x5, "
            "halted-sell pass, sole-exit emit guard) + D-20260930-40 CN-C7 wired into "
            "PREREG_TEMPLATE (round-trip cost bp mandatory single comparable number, "
            "per-asset-class face A derivation + min-commission notional tiers) + "
            "D-20260930-27 Q4 marks slimming landed (eval probe 93.9% suppressible 62/66 "
            "3-day window, today 97%; writer gate _tick_redundant: first-tick/settle/"
            "state-change/>=5bp/unpriced/force faces always kept; selftest S10-S13 PASS; "
            "CEO face results/Q4_MARKS_SLIMMING_20260930.md)")
s['verify'] = ("smoke 47/47 (2x: pre/post marks-writer change); update_intraday_marks "
               "selftest PASS (S1-S13); marks eval probe deterministic 66 ticks; "
               "S6 chain all legs rc0 (dualrun ZERO-DRIFT 51/3; compute_audit flags="
               "pool_starvation+supply_floor RW-5-freeze legal idle; WM py_low_board_clear; "
               "update_daily no new bar cutoff 2026-09-29 -> live.paper/t35/t24 trio "
               "conditional skip honest; scorecard 6/28/7; CALL ORANGE_COOL; REPORT/"
               "LIVE-2026-09-30 regenerated ORANGE cap50 COOL; lane guards honest no-op); "
               "attrition CLEAN; loop pin=8 no-op; watchdog Ready; claw installed; "
               "orders 127/127 diff empty; inbox zero unread")
s['next'] = ("r481: (1) 10-01 month-first trio (science_audit + monthly_briefing + "
             "self_review; REGIME_GUARD v3 date-gate hands-off); (2) M1 prereg prerequisite "
             "true trading calendar (D-30, post 10-03 external recheck gate); (3) Q4 slimming "
             "first real-fire watch (next trading day 2nd intraday tick); (4) RW-5 external "
             "recheck 10-03 -> supply line refill; (5) W14/REEVAL-18 bm-b/bm-c lanes watch")
s['last_round_at'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
s['updated'] = s['last_round_at']
s['current_task'] = ("10-01 month-first trio + M1 true-calendar prerequisite (D-30 post-10-03 "
                     "gate) + Q4 slimming first real-fire watch")
json.dump(s, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state written round_no=', s['round_no'])
