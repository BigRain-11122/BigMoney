# -*- coding: utf-8 -*-
"""r867 bm-a close bookkeeping (fresh read-modify-write per r862 law):
state file round 867->868 + r866 state-write-loss heal note (r841 family),
heartbeat epoch-int + fields, round report row. Zero cross-file staleness:
every file read fresh in-process at write time."""
import io
import json
import time

TS = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# ---- state file (repo ROOT state-bm-a.json) --------------------------------
st = json.load(open("state-bm-a.json", encoding="utf-8"))
prev_epoch = st.get("heartbeat_epoch_utc")
notes_add = ("r867: r866 session's state write was LOST in its own rebase storm "
             "(commit 11df6b757 message claims 'bookkeeping (state r866)' but the committed "
             "blob still showed r865-close content; r841 family second instance) -- healed this "
             "window per round_reports r866 line; sequence honest 865 -> 866 (report+commits on "
             "origin) -> 867. r867 product: W181 sec7/8 settle backfill HEAL (r864 window miss) + "
             "W182 prereg buildgen/freeze/ignition full chain.")
st.update({
    "round": 867,
    "round_no": 868,
    "loop_round": "r867",
    "last_round": "r867",
    "last_round_at": TS,
    "last_round_closed": TS,
    "last_round_ts": TS,
    "updated": TS,
    "last_run": TS,
    "last_seen": TS,
    "clock_read": TS,
    "ts": TS,
    "heartbeat_epoch_utc": EPOCH,
    "last_heartbeat_epoch_utc": prev_epoch if isinstance(prev_epoch, int) else 1791412280,
    "current_task": ("W182 burned by engine (self-ignited r867 tick 07:06 pid=77636, 12 shards queue); "
                     "next: W182 finalize one-pass + sec7/8 same-window backfill (r864 lesson) at burn completion; "
                     "T-177 REGIME-5 validation prereg + bull-supply scan leg2 (<=10-14 12:00)"),
    "now_active": "r867 closing: W182 prereg+freeze+ignition landed; engine burning W182; queue depth 10",
    "did": ("r867: S0-1 orphan probe face=0 post-r866-kill + S0 rebase clean (writer-pause r832 method, "
            "behind-3 bm-c r738 absorbed, flush x2) + S0.5 sweep-1 zero-unack + D-19 MATCH (dec EE659451 unchanged, "
            "consumed r866; ord unchanged per bm-c r737/r738 cross-check) + S1 smoke 49/49 + S3 PRODUCT: "
            "①W181 sec7/sec8 settle backfill HEAL (r864 finalize-window miss; all values machine-read from "
            "n1_w181_results.json: ledger 802,318+2,200=804,518 EXACT, +413 W16 legal increment vs projection "
            "804,105 disclosed; K=396,120 EXACT; mu -0.0928 (4dp roll), w-only -0.0987, sigma 0.245101, se_mu "
            "0.000389, line 1.1854->1.1853 K-lift -0.0001 sign-roll, p95 0.3073; sec5 four-key all PASS; "
            "delayed-window precedent W159/W168/W169/W180 family disclosed; head/tail byte-preserved vs blob "
            "fce370dca) ②W182 prereg buildgen r863-bloodline (50 TOK/BACK AST-carried, S82 map incl NEW "
            "merged-mu 4dp roll entry -0.0927->-0.0928, DRY 50/50 + stale-sweep CLEAN, preprobe receipt 50/50, "
            "banned gate ADMIT 0, prereg frozen push f543c161c) ③W182 FREEZE five-face registry (S82f buildgen "
            "173 pairs dump-verified, --dry PASS then live, pf 9/9 + n1 PASS incl W182 mat leg 172nd wave/98th "
            "bm-a/42nd staircase, push 385dbafd8) ④ignition verified tick 07:06 'ignited:n1w182-1of12 pid=77636 "
            "ledger_flush=1' (r325 product-growth law) + S6 38/38 rc0 (dualrun streak 51; pre-open honest "
            "no-ops cutoff 09-30; REPORT/LIVE-2026-10-08 regen; attrition CLEAN) + quartet green (pin=8 no-op, "
            "watchdog re-registered, claws byte-equal) + idle --worked + state heal r866-loss disclosed"),
    "next": ("r868: W182 burn completes (engine queue 10 shards after 1of12; headroom gate managing) -> "
             "W182 finalize one-pass (r381) + sec7/8 SAME-WINDOW backfill (r864 miss lesson) + ledger/products "
             "push; then T-177 REGIME-5 validation prereg draft (PREREG_TEMPLATE/science_gates, deadline "
             "<=10-14 12:00) + bull-supply scan leg2; 15:30 market-reopen re-arm: zt_pool FIRST REAL accrual "
             "(10-08 bar), REGIME_GUARD v3 enforce, bar-conditioned legs (live.paper + t35_open_fill_verify "
             "+ prospect legs); W183 seat chain after W182 finalize (proj A 417_204..419_203 / B 417_404..417_603 "
             "B-inside-A, re-derive-MANDATORY on post-W182 universe per r865 probe leg4 note)"),
    "verify": ("smoke 49/49 + buildgen DRY 50/50 + preprobe 50/50 + banned gate ADMIT rc0 + freeze --dry PASS + "
               "live rc0 (pf 356,311->359,106 B / n1 2,271,016->2,298,621 B) + pf selftest 9/9 + n1 selftest PASS "
               "(W182 mat leg) + ignition 'ignited:n1w182-1of12 pid=77636' + S6 38/38 rc0 + dualrun streak 51 "
               "ZERO-DRIFT + attrition CLEAN + quartet green + orders unacked=[] both sweeps + D-19 MATCH "
               "EE659451 + orphan face=0 + not-at-origin=0"),
    "notes": (st.get("notes") or "") + " " + notes_add,
    "last_artifact": ("research/PERPETUAL_N1_W182_PREREG.md + scripts/perpetual_faces.py N1_BANDS[182] row "
                      "(W182 freeze 385dbafd8, 2026-10-08T07:0x)"),
    "latest_artifact": ("results/perpetual_faces/n1_w182 shard burn (engine-ignited 07:06) + "
                        "PERPETUAL_N1_W182_PREREG.md @2026-10-08T07:0x+08:00"),
    "last_orders_at": TS,
    "last_decisions_at": TS,
})
json.dump(st, open("state-bm-a.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- heartbeat (fleet/machines/bm-a.json) ----------------------------------
hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
prev_hb_epoch = hb.get("heartbeat_epoch_utc")
hb.update({
    "clock_read": TS,
    "last_seen": TS,
    "ts": TS,
    "last_run": TS,
    "heartbeat_epoch_utc": EPOCH,
    "last_heartbeat_epoch_utc": prev_hb_epoch if isinstance(prev_hb_epoch, int) else 1791412280,
    "round": 867,
    "round_no": 868,
    "loop_round": "r867",
    "last_round": "r867",
    "last_action": ("r867: W181 sec7/8 backfill HEAL + W182 prereg+freeze+ignition full chain "
                    "(preseat probe ADMIT r865 -> buildgen DRY 50/50 -> banned gate 0 -> freeze five-face "
                    "-> selftest pf 9/9 n1 PASS -> ignition 1of12) + S6 38/38"),
    "current": ("W182 frozen+ignited (burn in flight); next: finalize one-pass + sec7/8 same-window backfill; "
                "T-177 REGIME-5 validation prereg <=10-14"),
    "current_task": ("W182 burn (engine) -> finalize; T-2026-10-08-177 REGIME-5 s2 validation prereg + "
                     "bull-supply scan leg2"),
    "now_active": "r867 closing: W182 chain landed; engine burning W182",
    "next_milestone": ("W182 finalize + sec7/8 same-window backfill (burn completion window <=48h); "
                       "REGIME-5 validation prereg <=10-14 12:00; 15:30 today market-reopen re-arm "
                       "(zt_pool first real accrual + REGIME_GUARD v3 enforce)"),
    "latest_artifact": ("PERPETUAL_N1_W182_PREREG.md + W182 registry freeze 385dbafd8 + "
                        "W181 sec7/8 backfill heal b6bbbb3b7 @2026-10-08T07:0x"),
    "verdict": "green (red=false lane healthy; engine ALIVE ignited n1w182 1of12, queue 10; W182 frozen; trial-labor supply standing)",
    "idle_rounds": 0,
    "agenda_starved": False,
    "orphan_faces": 0,
    "orphan_killed": 0,
})
json.dump(hb, open("fleet/machines/bm-a.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# epoch int self-verify (R170/R178 law)
chk = json.load(open("state-bm-a.json", encoding="utf-8"))
hb2 = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "state epoch not int"
assert isinstance(hb2["heartbeat_epoch_utc"], int), "heartbeat epoch not int"
print("state round", chk["round"], "round_no", chk["round_no"], "| hb epoch int", hb2["heartbeat_epoch_utc"], "| ts", TS)
