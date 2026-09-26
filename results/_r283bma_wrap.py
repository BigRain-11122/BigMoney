"""R283 bm-a wrap: round report line + state + heartbeat update (single now() source, R271 law)."""
import json
import time
from datetime import datetime

now = datetime.now().astimezone()
now_iso = now.isoformat(timespec="seconds")          # T-separated (R262 law)
now_s = now.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())                              # JSON int (R170/R178 law)

REPORT_LINE = (
    f"{now_s} | R283 bm-a | WM=GREEN insufficient_history(n=2 span 11.9m legal; board: 32 tickets all claimed, "
    f"pool shard owned bm-b, supply line active) | S0.5 orders full-scan 89/89 acked zero unacked (round-start + wrap double-scan); "
    f"decisions receipt D-20260927-04 (post_review hot-ticket anchor law: BigMoney self-corrected r256/r264 already closed, maintain) + "
    f"D-20260927-05 (orders full-file scan = existing S0.5 design since R13, compliant, maintain); "
    f"S3 T-87 s2 queue #2 CN_SOE_ETF_P1 prereg FROZEN ba54b43f (R99 law freeze>build>run): 8-member thin-sleeve SOE universe "
    f"(name-face re-derive + first<=2021-12-31 + rows>=1100 + MED_AMT20>=5e6 batch gate -- family 5e7 would zero the whole face, "
    f"capacity honesty: 1M-paper-scale only; 2023+ pure-SOE cohort IS-depth excluded forward-observation-only), 5 judged cells "
    f"(HOLD/HOLD_MA200/LEGMA200/REPAIR/LOWVOL3 folklore frozen), K=2000 duty-cycle nulls dual-method + census + RANDOM_LARGE_SAMPLE_LAW, "
    f"seed cn_soe_etf_p1=20272301 registered same commit (band 20272301-20274300 rg zero hits), science_gates selftest 37/37, "
    f"F-04 MSG declared, SCHOOL_SUPPLY_S1 sec.4 queue ledger opened; runner build = next-round exact continuation point; "
    f"rebase conflict autofill_state UU (bm-b r286 tick-tail same-window double-push) resolved per skill recipe: launches union 52->cap50 newest->ts asc, "
    f"last_tick same-second tie->HEAD, CRLF mirror, resolver results/_r283bma_resolve.py; post_review latest YES zero NO; smoke 25/25; "
    f"S6 22 legs rc=0 (audit CLEAN v2.3 pool-supply-gap, update_daily no-op weekend cutoff 09-24, regime ORANGE breadth 0.77 shadow, "
    f"scorecard 6/28/7, clock CALL-2026-09-24 ORANGE_COOL 4 sleeves 0 activated, t35 PASS 0 pending, prospect 22/22 drift 0, "
    f"promotion 0/22, aggr/grid idempotent no-op, export+daily cards+report regenerated, ah_panel spawned detached refresh first-run-incomplete self-heal); "
    f"CN-TREND cntrend-0of1 in-flight on bm-b (first-fire double crash root-fixed their side, checkpoints, zero overlap my lane) [via bm-a]"
)

# 1) round report append (probe trailing newline first, r281 law)
p = "logs/iteration-loop/round_reports-bm-a.md"
b = open(p, "rb").read()
nl = b"\r\n" if b.count(b"\r\n") > b.count(b"\n") - b.count(b"\r\n") else b"\n"
if not b.endswith(b"\n"):
    open(p, "ab").write(nl)
with open(p, "ab") as f:
    f.write(REPORT_LINE.encode("utf-8") + nl)

# 2) state file
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8-sig"))
st.update({
    "round_no": 283,
    "did": ("R283: CN_SOE_ETF_P1 prereg frozen ba54b43f (T-87 s2 queue #2 zhongtegu SOE sleeve: 8-member thin gate 5e6, "
            "5 judged cells, 2000 nulls, seed 20272301, sg selftest 37/37) + autofill_state rebase UU resolved (union cap50 skill recipe) "
            "+ S6 22 legs rc=0"),
    "verdict": "ok",
    "next": ("CN_SOE_ETF_P1 runner build per frozen prereg (scripts/cn_soe_etf_p1.py + selftest all green pre-pool r263 law) -> pool entry; "
             "CN-TREND judgment lands on bm-b; moneyflow IC batch parked source-blocked"),
    "ts": now_iso, "last_round_ts": now_s, "updated_at": now_s,
    "current_task": "R283 done: CN_SOE_ETF_P1 prereg frozen (queue #2); awaiting runner build round",
    "last_run": now_s, "last_round_at": now_s, "last_round": 282, "updated": now_s, "last_seen": now_iso,
})
open(sp, "w", encoding="utf-8", newline="\n").write(json.dumps(st, ensure_ascii=False, indent=1))

# 3) heartbeat
hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8-sig"))
hb.update({
    "machine_id": "bm-a",
    "last_seen": now_iso,
    "current_task": "R283 done: CN_SOE_ETF_P1 prereg frozen (queue #2); runner build next",
    "cpu_cores": 32, "cores": 32,
    "heartbeat_epoch_utc": epoch,        # int type (R170/R178)
    "clock_read": now_iso,               # T-separated (R262)
    "round_no": 283,
})
d = json.loads(open(hp, encoding="utf-8-sig").read()); hb["orders_ack"] = d["orders_ack"]  # unchanged, no new orders
json.dumps(hb)
open(hp, "w", encoding="utf-8", newline="\n").write(json.dumps(hb, ensure_ascii=False, indent=1))

# verify epoch int (R170/R178 law)
back = json.load(open(hp, encoding="utf-8-sig"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in back["clock_read"], "clock_read must be T-separated ISO"
print("wrap files written; epoch:", back["heartbeat_epoch_utc"], "clock:", back["clock_read"])
