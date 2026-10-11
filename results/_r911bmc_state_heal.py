# -*- coding: utf-8 -*-
"""r911 bm-c state heal: absorb r908-r910 dead sessions + this session's product faces."""
import json, time, datetime

SP = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json"
HP = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-c.json"

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
now_epoch = int(time.time())

summary = ("r911 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=5 orphans=1 zero-kill; "
"(2) ABSORB r908-r910 THREE dead sessions (all committed bodies -- r908: W213 seat 4f3b0d6a8 + prereg eeda85145 + "
"five-face freeze a24069f4c; r909: W213 finalize one-pass a9401c82c ledger 892,389 K=466,520 + three-wave "
"sec.7/8 backfill W209/W211/W213 + W214 seat d55a6b58b; r910: W212 five-key+six-gate debt heal 7b215ab56 + "
"W214 prereg b0aa90376 + five-face freeze splice 4664900c8 + engine self-burn 12/12 + S6 chain 36 legs rc0 "
"-- every one died pre-closeout, state frozen at r907/908) -> this session = r911, counter advanced 908->912; "
"(3) S0 fetch clean; S0.5 standing probe: orders_delta=false decisions_delta=false unacked=0 (dec 67403afa / "
"ord 33aee170 hold, zero new rows zero action); (4) S1 smoke 49/49; S2 boards clear (jobs 0, fleet open=0, "
"queues CLEAR); satengine ALIVE rc0 (live daemon PID 38072); (5) PRODUCT = W214 FULL CYCLE completed same-window: "
"engine ledger appends completed 9->12 (96dd84783 3-shard tail batch) -> pre-finalize six-gate probe (banned "
"ADMIT rc0 + pf selftest 9/9 + n1 selftest PASS + shards 12/12 + seed_admit FREE x2 + WAVE_CONFIGS row) RUN "
"BEFORE finalize (W212 debt lesson applied, no post-hoc) -> finalize one-pass LANDED (ledger identity "
"892,389+2,200=894,589 EXACT asserted; merged K=468,720 EXACT vs prereg projection; merged mu=-0.09269118 "
"sigma=0.24512135; w214-only mu=-0.09374873; skill_line_v2 @n_eff=892,389: 1.1905->1.1905 K-lift +0.0000; "
"se_mu 0.000358; voids LOWAMP-P1/P2; FAIL-CLOSED five-gate suite passed) -> five-key probe ALL PASS "
"(key1 0.00106<0.02 / key2 +0.00029%<10% / key3 A p95 0.3086 diff 0.0030<0.05 / key4 +0.0000<=0.02 / key5 "
"sec.8 projection) -> prereg sec.7/8 backfilled machine-read; (6) SECOND PRODUCT = W215 seat published=reserved "
"(pre-seat probe rc0 ADMIT: A 487_804..489_803 staircase SEVENTY-FIFTH E36 hops=1 + B 489_804..490_003 own-A "
"mutual exclusion hops=1; seed_admit FREE x2 487804/2000 + 489804/200; conflicts=0; origin vacancy 4-check "
"held; W216+ projection leg4; seat MSG-20261012-0536 pushed origin 37d7adc0a; r565 seat-first law); "
"(7) S6 absorbed from r910 (36 legs rc0, ~25min fresh at commit 021b4ed6a + token_meter rerun this window); "
"(8) next: W215 per-wave prereg + five-face freeze splice = next action (same-window chain if time holds, "
"else next window FIRST ACTION per r908/r910 precedent); W214 sec.5 five-key debt = NONE (probe ran pre-finalize "
"this window); MV XQ-24 harvest watch continues (receipt into O-2126 when lane completes)")

st = json.load(open(SP, encoding="utf-8"))
st.update({
    "round_no": 912,
    "loop_round": 911,
    "round_no_label": "r911",
    "last_round": 911,
    "clock_read": now_iso,
    "ts": now_iso,
    "updated": now_iso, "updated_at": now_iso,
    "last_seen": now_iso, "last_seen_at": now_iso,
    "last_round_at": now_iso, "last_round_ts": now_iso,
    "last_round_closed": now_iso,
    "heartbeat_epoch_utc": now_epoch,
    "current_task": "r911 closeout: W214 full cycle (finalize+backfill+five-key) + W215 seat published; W215 prereg+freeze = next",
    "current_task_at": now_iso, "current_task_ts": now_iso,
    "last_action": "r911 absorb+product closeout (W214 finalize one-pass + sec.7/8 + W215 seat publish)",
    "last_round_summary": summary,
    "did": summary,
    "note": summary,
    "last_action_at": now_iso,
    "activity_now": ("r911: W214 FULL CYCLE complete (finalize one-pass, ledger 894,589, K=468,720, "
                     "skill_line 1.1905, five-key ALL PASS) + W215 seat published (A 487_804..489_803 + "
                     "B 489_804..490_003); W215 prereg+freeze splice = next window FIRST ACTION; "
                     "MV XQ i2v lane in flight (interactive window owns, zero lane-touch)"),
    "now_active": ("r911: W214 FULL CYCLE complete (finalize one-pass, ledger 894,589, K=468,720, "
                   "skill_line 1.1905, five-key ALL PASS) + W215 seat published (A 487_804..489_803 + "
                   "B 489_804..490_003); W215 prereg+freeze splice = next window FIRST ACTION; "
                   "MV XQ i2v lane in flight (interactive window owns, zero lane-touch)"),
    "verdict": ("green: absorb+double-product round -- W214 full cycle complete (engine 12/12 appended "
                "96dd84783 -> six-gate probe PRE-finalize -> finalize one-pass: ledger 894,589 / K=468,720 / "
                "skill_line 1.1905 delta +0.0000 -> five-key ALL PASS -> sec.7/8 backfilled), W215 seat "
                "published (staircase 75th, seed_admit FREE x2, origin vacancy held), smoke 49/49, dual "
                "watermark zero-delta, 3 dead sessions absorbed, GPU/RAM yielded to MV CEO-priority i2v lane"),
    "next_pointer": ("r912: (1) W215 per-wave prereg build + five-face freeze splice FIRST ACTION "
                     "(upstream W214 finalize landed = clean precondition; bands machine-derived in "
                     "results/_w215bmc_20261012_probe_receipt.json: A 487_804..489_803 + B 489_804..490_003; "
                     "seat MSG-20261012-0536 already pushed 37d7adc0a); engine self-burns after splice "
                     "(2) W214 sec.5 five-key debt = NONE (pre-finalize probe ran r911) + W209/W211/W212/W213 "
                     "sec.7/8 all backfilled zero debt; (3) Monday 15:30 first new-bar window: update_daily "
                     "chain + live.paper + t35_open_fill_verify + t24 legs; (4) unity-mcp POC receipt due "
                     "10-13 12:00 (O-2333, post-MV-lane); (5) MV XQ-24 harvest watch when lane completes "
                     "(receipt into O-2126)"),
    "next": ("r912: (1) W215 per-wave prereg build + five-face freeze splice FIRST ACTION "
             "(upstream W214 finalize landed = clean precondition; bands machine-derived in "
             "results/_w215bmc_20261012_probe_receipt.json: A 487_804..489_803 + B 489_804..490_003; "
             "seat MSG-20261012-0536 already pushed 37d7adc0a); engine self-burns after splice "
             "(2) W214 sec.5 five-key debt = NONE (pre-finalize probe ran r911) + W209/W211/W212/W213 "
             "sec.7/8 all backfilled zero debt; (3) Monday 15:30 first new-bar window: update_daily "
             "chain + live.paper + t35_open_fill_verify + t24 legs; (4) unity-mcp POC receipt due "
             "10-13 12:00 (O-2333, post-MV-lane); (5) MV XQ-24 harvest watch when lane completes "
             "(receipt into O-2126)"),
    "next_milestone": ("W215 freeze splice + engine self-burn 12/12 + finalize = next full cycle "
                       "(ETA next 2 windows); Monday 15:30 new-bar chain; unity-mcp POC 10-13 12:00"),
    "latest_artifact": ("results/perpetual_faces/n1_w214_results.json (finalize one-pass 2026-10-12 05:1x, "
                        "ledger 894,589 / K=468,720) + research/PERPETUAL_N1_W214_PREREG.md sec.7/8 backfilled "
                        "+ results/_r911bmc_w214_fivekey_receipt.json + results/_w215bmc_20261012_probe_receipt.json (W215 seat)"),
    "last_artifact": ("results/perpetual_faces/n1_w214_results.json (finalize one-pass 2026-10-12 05:1x, "
                      "ledger 894,589 / K=468,720) + research/PERPETUAL_N1_W214_PREREG.md sec.7/8 backfilled "
                      "+ results/_r911bmc_w214_fivekey_receipt.json + results/_w215bmc_20261012_probe_receipt.json (W215 seat)"),
    "recent_artifact": ("results/perpetual_faces/n1_w214_results.json (finalize one-pass 2026-10-12 05:1x, "
                        "ledger 894,589 / K=468,720) + research/PERPETUAL_N1_W214_PREREG.md sec.7/8 backfilled "
                        "+ results/_r911bmc_w214_fivekey_receipt.json + results/_w215bmc_20261012_probe_receipt.json (W215 seat)"),
    "last_round_summary_at": now_iso,
    "idle_rounds": 0,
    "agenda_starved": False,
    "orphan_face": 1, "orphan_faces": 1,
    "cpu_pct": 11.7, "cpu_util_pct": 11.7, "cpu_idle_pct": 88.3,
    "free_ram_gb": 3.27, "ram_free_gb": 3.27, "idle_ram_gb": 3.27,
    "gpu_free_vram_mib": 1335, "gpu_free_vram_mb": 1335, "gpu_free_mib": 1335, "gpu_free_mb": 1335,
    "gpu_idle_vram_mb": 1335, "gpu_idle_mib": 1335, "gpu_idle_mb": 1335,
    "gpu_vram_free_mb": 1335, "free_vram_mb": 1335, "gpu_free_vram_gb": 1.34,
    "r911_absorb_note": ("r911 absorb: sessions r908/r909/r910 each ran full/partial bodies with "
                         "commits+pushes (W213 seat+prereg+freeze r908; W213 finalize+three-wave backfill+"
                         "W214 seat r909; W212 debt heal+W214 prereg+freeze+engine self-burn+S6 chain r910) "
                         "but ALL died pre-closeout -- state had been frozen at r907/round_no=908 the whole "
                         "time; this session executed as r911 (next after highest committed r910) and advanced "
                         "counter 908->912 so next session = r912; zero double-count: S0.5 dual-delta FALSE "
                         "this window (dec 67403afa / ord 33aee170 both current, zero consumption owed)"),
    "head_sha": "37d7adc0a",
    "verify": ("receipts: smoke 49/49 + pre-finalize six-gate (banned ADMIT/pf 9/9/n1 selftest/12-12 shards/"
               "seed_admit FREE x2) + finalize one-pass ledger identity 892389+2200=894589 EXACT + five-key "
               "ALL PASS + W215 seat probe rc0 ADMIT + push self-proof 021b4ed6a/37d7adc0a both range-pushed"),
})
st["sync"] = {"ahead_behind": "r911 closeout commit rides this push",
              "origin_tip": "pending", "ts": now_iso,
              "note": "r911 closeout: W214 product commit 021b4ed6a + W215 seat 37d7adc0a pushed; state/heartbeat commit+push this round"}
json.dump(st, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
assert isinstance(st["heartbeat_epoch_utc"], int)

hb = json.load(open(HP, encoding="utf-8"))
hb.update({
    "machine_id": "bm-c",
    "last_seen": now_iso, "ts": now_iso, "clock_read": now_iso,
    "heartbeat_epoch_utc": now_epoch,
    "current_task": "r911: W214 full cycle complete (finalize ledger 894,589 K=468,720 five-key PASS) + W215 seat published; W215 prereg+freeze next",
    "cpu_pct": 11.7,
    "free_ram_gb": 3.27, "idle_ram_gb": 3.27,
    "gpu_free_vram_mib": 1335, "gpu_free_mb": 1335,
    "verdict": "green: W214 full cycle + W215 seat published; smoke 49/49; engine alive; next=W215 freeze splice",
    "idle_rounds": 0,
    "agenda_starved": False,
    "last_round": 911,
    "round_no": 912,
    "cores": 32, "cpu_cores": 32,
    "orders_ack": hb.get("orders_ack"),
})
json.dump(hb, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
assert isinstance(hb["heartbeat_epoch_utc"], int)
print("state+heartbeat healed: round_no=912 (this=r911), epoch int verified", now_epoch)
