# -*- coding: utf-8 -*-
"""r850 bm-a state + heartbeat writer (fresh read-modify-write per r806 law;
epoch int + T-separator clock per R170/R178/R262 smoke F7 law)."""
import json
import time

now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# --- state-bm-a.json -----------------------------------------------------
P = "state-bm-a.json"
st = json.load(open(P, encoding="utf-8"))
st["round_no"] = 850
st["round"] = 850
st["last_round"] = "r850"
st["last_round_at"] = now_iso
st["last_round_ts"] = now_iso
st["did"] = ("r850: W179 finalize one-pass full chain (burn 12/12 observed at round start -> preflight "
             "three-gate GREEN_FINALIZE_READY half-open r846 bloodline -> finalize ledger 797,505+2,200=799,705 "
             "EXACT + merged K=391,720 EXACT + skill_line 1.1851->1.1850 K-lift -0.0001 + SS5 four pred keys "
             "all PASS + SS7/SS8 machine backfill assert-pool + dual selftest green incl W179 mat leg 169th wave/"
             "95th bm-a owned/39th staircase E36) + S0 storm triple push-race (r849 dead-tail staged adoption r752 "
             "three-gate + 17-UU rebase-stop canon resolve merge_lane_views x6/twins deep-ts x6/CODELY origin+r849 "
             "append/snapshot take-new x4 + r835 three-step false-conflict escape E42 family + cherry-pick leg2 "
             "residue) + S0.5 orders 51/51 double-sweep zero unacked + DEC watermark 771c3a8d->ee659451 consumed "
             "(10-08 00:09 morning batch D-20261008-01~04, zero BigMoney dispatch rows, ORD 2bb2ee75 identical "
             "zero-action) + S1 smoke 48/48 + S6 38 legs rc0 (dualrun ZERO-DRIFT streak 51; pre-market honest "
             "no-op family cutoff 09-30; REPORT/LIVE-2026-10-08 twins produced) + S7 quartet green + attrition "
             "CLEAN + idle_trigger --worked + HANDOVER r850 5x block appended")
st["last_action"] = ("W179 finalize landed on origin (ledger head 799,705 / K 391,720 / prereg sec7-8 backfilled); "
                     "10-08 market-reopen day: data chain re-arms after 15:30 first bar")
st["last_decisions_sha"] = "ee6594516c01856ecd1bd4131e49cafd8f95a61293c131ce5d45c574c20ff6ce"
st["last_decisions_at"] = now_iso
st["last_decisions_ts"] = now_iso
st["last_decisions_src"] = "group origin/main docs/decisions.md (local group tree fallback per D-20261004-02③)"
st["last_decisions_seen"] = ("hash ee659451 changed from 771c3a8d: 10-08 00:09 batch D-20261008-01~04 consumed "
                             "same round (receipt accounting / BigStream restock / MiniGame budget / ledger "
                             "archaeology -- zero BigMoney dispatch rows); orders.md 2bb2ee75 identical zero-action")
st["last_orders_at"] = now_iso
st["last_orders_sha"] = "2bb2ee75edfcd506501608c422f94c7ca8ca3255d3612e38803e14eaf4baf416"
st["heartbeat_epoch_utc"] = epoch
st["last_heartbeat_epoch_utc"] = epoch
st["last_seen"] = now_iso
st["last_run"] = now_iso
st["clock_read"] = now_iso
st["ts"] = now_iso
st["updated"] = now_iso
st["loop_round"] = "r850"
st["latest_artifact"] = "results/perpetual_faces/n1_w179_results.json (finalize landed origin 9eb89503a)"
st["verify"] = ("preflight GREEN_FINALIZE_READY 7-gate; finalize FAIL-CLOSED guards all passed (pit-95 no-relend, "
                "12/12 shards, A 2000/B 200 identity, seed sweeps EXACT 408604..410603 + 410604..410803); "
                "SS5 projections EXACT both keys (799,705 ledger / 391,720 K); SS7/SS8 backfill assert-pool + "
                "r773 residue scan clean; pf 9/9 + n1 selftest PASS; smoke 48/48; S6 38/38 rc0; attrition CLEAN; "
                "orders 51/51 dual-sweep; quartet 4/4; local not-at-origin=0 post-push fetch self-check")
st["now_active"] = ("engine idle (W179 closed, ledger 799,705, K 391,720); 10-08 reopen-day data chain re-arm "
                    "after 15:30 + fund trio NULLS finalize window to 10-09 (bm-b pool lane) + CEO order files "
                    "advance (P-audit 10-12 / R-research + REGIME-5 10-14)")
st["next"] = ("r851: W180 seat chain half-window (probe on post-W179 universe re-derive MANDATORY -> seat MSG -> "
              "gated push; naive A 410_604..412_603 refused by W179 B band = staircase 40th expected; naive B "
              "410_804..411_003 inside naive A = W141 leg2) + 10-08 15:30 market-reopen first-bar data chain "
              "re-arm (all gates fire + REGIME_GUARD v3 enforce activation) + OSS ledger S3/S4/S5 pending-scan by "
              "10-09 + O-1850 VL pull+co-residence test 3 readings + CEO order execution files advance")
json.dump(st, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state round_no ->", st["round_no"], "| epoch int:", st["heartbeat_epoch_utc"],
      "| isinstance int:", isinstance(st["heartbeat_epoch_utc"], int))

# --- fleet/machines/bm-a.json (heartbeat) ---------------------------------
H = "fleet/machines/bm-a.json"
h = json.load(open(H, encoding="utf-8"))
h["last_seen"] = now_iso
h["current_task"] = ("W179 finalize landed (ledger 799,705 / K 391,720); next: W180 seat chain + 10-08 15:30 "
                     "reopen-day data chain re-arm")
h["cpu_cores"] = 32
h["cpu_total_pct"] = 6.0
h["idle_ram_gb"] = 51.6
h["gpu_idle_vram_mb"] = 5852
h["verdict"] = ("worked (W179 finalize one-pass product; engine idle queue0; idle_trigger --worked declared; "
                "not full GREEN-IDLE this sample: VRAM 5.85GB<6GB)")
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now_iso
h["ts"] = now_iso
h["round_no"] = 850
json.dump(h, open(H, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(H, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
print("heartbeat epoch int OK; orders_ack n =", len(h.get("orders_ack", [])))
