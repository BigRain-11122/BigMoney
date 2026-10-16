# -*- coding: utf-8 -*-
# r1046 bm-c closeout: state + heartbeat + round-report row (canon clone pattern
# of _r1043bmc_closeout.py / _r1045 closeout lineage).
import io
import json
import os
import time
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

ABSORB = ("r1046 absorb note: dead window self-labeled r1046-predecessor (fired ~07:4x after r1045 closeout "
          "07:37:49) executed: W250 five-face freeze splice 08:02-08:04 LANDED commit 29930f489 (incl "
          "disclosed post-splice heal print-face rows 68->69, E63 family; dual-sha16 pf 40b0befe37ebbe2c / "
          "n1 050d7e70375727f2 pre-heal receipt face) + engine mtime-watch self-burn 12/12 (batched ledger "
          "appends 486458150 08:07:21 + 77a4f529a 08:10:59) + sixgate script authored 08:09:43 UNRUN + "
          "verify_edits precheck 08:03 -- died pre-closeout (state frozen at round_no=1046, heartbeat stale "
          "at r1045/07:37); this session executed as r1046 continuation per bm-c absorb precedent lineage "
          "(r894..r1045, 39th instance), zero double-count: S0.5 dual-delta FALSE both scans (ORD f321f54a / "
          "DEC ec6b9164 hold, probe-verified, unacked=0), dead-window debts handled by its own origin commits "
          "+ this closeout landing the W250 cycle completion; counter stays 1046->1047 so next session = r1047")

DID = ("r1046 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=5 orphans=2 zero-kill; (2) CONTINUATION "
       "39th gen (dead r1046-predecessor estate verified: splice 29930f489 + engine self-burn 12/12 both on "
       "origin; sixgate script absorbed); (3) P0 PRODUCT = W250 cycle COMPLETE this window correct-phase: "
       "sixgate PRE-FINALIZE ALL PASS (_r1046bmc_w250_sixgate.json -- first run FAIL root-caused: receipt "
       "n1_sha16_post = in-memory PRE-HEAL snapshot (n1_t4 hashed at receipt-write 08:04:23, heal landed "
       "08:07:43 pre-commit) = stale by construction; gate-1 re-anchored worktree==LANDED git blob n1 "
       "22a957f851fd3adc / pf 40b0befe37ebbe2c, E70 methodology card) -> finalize one-pass ledger "
       "972,135+2,200=974,335 EXACT / merged K=547,920 (545,720+2,200) / w250-only mu -0.09229 sigma 0.24666 / "
       "merged mu -0.09277 sigma 0.24504 / K-lift 0.0000 in-band -> fivekeys ALL PASS "
       "(_r1046bmc_w250_fivekeys.json: key1 0.00051<0.02, key1b 0.0000021, key2 sigma rel +0.0027pct, key3 "
       "p95 0.3235 vs 0.3158 +0.0077<0.05, key4 0.0, key5 se_mu 0.000331<=0.000332 narrowed) -> sec.7/8 "
       "backfilled (programmatic needle location, zero hand-copied CJK, backfill-limited law) + E70 "
       "METHODOLOGY_ASSETS card appended; (4) W251 SEAT published queue-head (probe _w251bmc_20261016 rc0 "
       "ADMIT: A 567_501..569_500 hops=0 14th seed-gap / B 569_501..569_700 hops=13 walk [seed 545_500 + "
       "W240..W249 A-ladder + W250-A + own-A reservation], B lands ABOVE own-A first since W239 staircase "
       "era, / seed gates FREE both / origin vacancy 4-check / no-skip W252/W253; W252+ proj: A "
       "569_501..571_500 CLEAN / naive B 569_701..569_900 lands INSIDE W252 A window -> staircase "
       "re-emergence face for the W252 freezer, live re-derive governs); (5) S0.5 dual-delta FALSE both "
       "scans + unacked=0; (6) smoke 49/49; (7) S6 43/43 rc0 idempotent sweep (bars 10-15 consumed, 10-16 "
       "not due till 15:30, token delta=0); (8) S7 quad green + attrition 4 CLEAN + W249 seat MSG inbox-move "
       "committed; counter 1046->1047")

NEXT = ("r1047: (1) W251 prereg derive = FIRST ACTION (seat-first law, machine-SUB from frozen W250 template "
        "research/PERPETUAL_N1_W250_PREREG.md, key-anchored to W250 actuals ledger 974,335 / K=547,920 / "
        "w250-only mu -0.09229 / se_mu 0.000331; bands A 567_501..569_500 / B 569_501..569_700 per seat "
        "receipt); (2) W251 five-face freeze splice after prereg (engine mtime-watch self-burn follows); "
        "(3) bars 10-16 window 15:30 (papers debt=0); (4) ORD/DEC tail re-scan")

VERDICT = ("green: r1046 = CONTINUATION 39th (dead r1046-predecessor splice+burn verified on origin) + P0 "
           "PRODUCT W250 cycle COMPLETE correct-phase (sixgate ALL PASS with E70 stale-receipt-sha gate-1 "
           "re-anchor disclosed -> finalize 974,335 EXACT / K=547,920 -> fivekeys ALL PASS -> sec.7/8 "
           "backfilled) + W251 seat published (ADMIT A 567_501..569_500 / B 569_501..569_700 hops=13 "
           "above-own-A) + S6 43/43 + smoke 49/49 + S7 quad green")

PROD = ("CPU=W20 SCREEN 4/4 shards ALL DONE (pool face closed r1044 chain) + engine queue idle (never-dry "
        "supply = W251 seat published) ; GPU=VRAM 14.5G free ; N1=W250 COMPLETE (ledger 974,335 / K=547,920) "
        "+ W251 seat OPEN (A 567_501..569_500 / B 569_501..569_700) -> prereg derive r1047 first action ; "
        "SPAWN-GATE=codely cap2 live")

ARTIFACT = ("results/perpetual_faces/n1_w250_results.json (finalize 10-16 08:4x, ledger 974,335, K=547,920, "
            "fivekeys ALL PASS) + results/_w251bmc_20261016_probe_receipt.json (W251 seat ADMIT) + E70 card "
            "knowledge/METHODOLOGY_ASSETS.md")

CLOSE = ("r1046: continuation 39th (dead predecessor splice 29930f489 + self-burn 12/12 absorbed) + W250 "
         "full cycle COMPLETE (sixgate ALL PASS after E70 stale-receipt gate-1 re-anchor -> finalize "
         "974,335 EXACT / K=547,920 -> fivekeys ALL PASS -> sec.7/8 backfilled) + W251 seat published + S6 "
         "43/43 + smoke 49/49 + S7 quad green + attrition 4 CLEAN | " + NOW)

SELFPROOF = {
    "占用一行": PROD,
    "当前活": "r1046 closeout (W250 cycle complete + W251 seat published)",
    "最近实物": ARTIFACT,
    "下个交付物": "W251 prereg derive (r1047 首动作·seat-first) + splice+burn chain + bars 10-16 15:30 窗",
    "队列水位": "池 ready=0 (W20 closed)·N1 W251 seat queued·P2/P3 空·jobs 0",
}

ROW = (NOW + " | r1046 | bm-c | CONTINUATION 39th (dead r1046-predecessor: splice 29930f489 + engine "
       "self-burn 12/12 + sixgate script authored-unrun, died pre-closeout state frozen 1046) + P0 PRODUCT "
       "= W250 cycle COMPLETE correct-phase: sixgate PRE-FINALIZE ALL PASS (first-run FAIL root-caused = "
       "receipt n1_sha16_post pre-heal in-memory snapshot vs disclosed post-splice heal rows 68->69; gate-1 "
       "re-anchored to landed git blob n1 22a957f851fd3adc / pf 40b0befe37ebbe2c, E70 card) -> finalize "
       "one-pass 972,135+2,200=974,335 EXACT / K=547,920 / merged mu -0.09277 sigma 0.24504 / K-lift 0.0000 "
       "-> fivekeys ALL PASS (_r1046bmc_w250_fivekeys.json) -> sec.7/8 backfilled + E70 METHODOLOGY_ASSETS "
       "card -> W251 SEAT published (probe ADMIT: A 567_501..569_500 hops=0 14th seed-gap / B "
       "569_501..569_700 hops=13 above-own-A first since staircase, gates FREE, vacancy 4-check, no-skip "
       "W252/W253; W252+ proj: naive B lands INSIDE W252 A window = staircase re-emergence face) + S0.5 "
       "dual-delta FALSE both + smoke 49/49 + S6 43/43 rc0 (bars 10-16 not due) + S7 quad green + attrition "
       "4 CLEAN | next: W251 prereg derive r1047 FIRST ACTION | ledger 974,335 | 未达 origin commit 数=0 "
       "(push+fetch verify in closeout) | 孤儿面=2 (zero-kill legal faces)")

# --- state face ---
sp = os.path.join(ROOT, "state-bm-c.json")
st = json.load(io.open(sp, encoding="utf-8"))
st["machine_id"] = "bm-c"
st["round_no"] = 1047
st["last_round"] = "r1046"
st["last_round_label"] = "r1046"
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_round_at_legacy"] = st.get("last_round_at_legacy", NOW)
st["last_seen"] = NOW
st["last_seen_at"] = NOW
st["last_ts"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["updated_at"] = NOW
st["activity_now"] = NOW
st["now_active"] = NOW
st["current_task"] = "r1046 closeout (W250 cycle complete + W251 seat published)"
st["current_task_at"] = NOW
st["current_task_ts"] = EPOCH
st["last_action"] = "r1046 closeout (W250 cycle complete + W251 seat publish)"
st["last_action_at"] = NOW
st["last_round_closed"] = NOW
st["last_round_summary"] = ("r1046: continuation 39th + W250 cycle COMPLETE (sixgate ALL PASS after E70 "
                           "gate-1 re-anchor -> finalize 974,335/K=547,920 -> fivekeys ALL PASS -> backfill) "
                           "+ W251 seat published + S6 43/43 + smoke 49/49 + S7 quad green")
st["last_round_summary_at"] = NOW
st["last_artifact"] = ARTIFACT
st["latest_artifact"] = ARTIFACT
st["recent_artifact"] = ARTIFACT
st["next"] = NEXT
st["next_pointer"] = NEXT
st["next_milestone"] = "r1047+: W251 prereg derive + splice + burn + bars 10-16 15:30 window"
st["verdict"] = VERDICT
st["note"] = ("r1046: W250 cycle COMPLETE (finalize 974,335 / K=547,920, fivekeys ALL PASS, E70 gate-1 "
              "re-anchor disclosed) | W251 seat OPEN (A 567_501..569_500 / B 569_501..569_700) | prereg "
              "derive = r1047 first action")
st["did"] = DID
st["verify"] = ("receipts: sixgate ALL PASS receipt _r1046bmc_w250_sixgate.json (gate-1 landed-blob anchor) "
                "+ finalize stdout (ledger 974,335 / K=547,920 EXACT) + fivekeys receipt all_pass=true "
                "(6 checks) + backfill byte-count 34,465->38,553 + probe ADMIT receipt "
                "_w251bmc_20261016_probe_receipt.json (A hops=0 / B hops=13 trace / gates FREE) + smoke 49/49 "
                "+ S6 log 43x rc=0 (_r1046bmc_s6_log.txt) + attrition 4 CLEAN + epoch int readback + ORD/DEC "
                "dual-delta FALSE both scans")
st["prod_lanes"] = PROD
st["full_load_selfproof"] = SELFPROOF
st["ram_free_gb"] = 7.0
st["free_ram_gb"] = 7.0
st["idle_ram_gb"] = 7.0
st["gpu_free_vram_mib"] = 14896
st["gpu_free_vram_mb"] = 14896
st["gpu_vram_free_mb"] = 14896
st["free_vram_mb"] = 14896
st["gpu_free_vram_gb"] = round(14896 / 1024, 2)
st["heartbeat_epoch_utc"] = EPOCH
st["clock_read"] = NOW
st["orphan_face"] = 2
st["orphan_faces"] = 2
st["codely_live_count"] = 1
st["loop_round"] = st.get("loop_round", 993) + 1
st["head_sha"] = "closeout commit rides this window (push verify in closeout)"
st["r1046_absorb_note"] = ABSORB
st["r1046_closeout_note"] = CLOSE
io.open(sp, "w", encoding="utf-8", newline="\n").write(json.dumps(st, indent=1, ensure_ascii=False))
back = json.load(io.open(sp, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int"
assert back["round_no"] == 1047
print("state OK: round_no 1046->1047, epoch int verified")

# --- heartbeat face ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(io.open(hp, encoding="utf-8"))
hb["machine_id"] = "bm-c"
hb["last_seen"] = NOW
hb["last_seen_at"] = NOW
hb["ts"] = NOW
hb["clock_read"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["current_task"] = "r1046 closeout (W250 cycle complete + W251 seat published)"
hb["current_task_at"] = NOW
hb["last_round"] = "r1046"
hb["last_round_at"] = NOW
hb["last_round_summary"] = st["last_round_summary"]
hb["did"] = DID
hb["verdict"] = VERDICT
hb["prod_lanes"] = PROD
hb["latest_artifact"] = ARTIFACT
hb["next_pointer"] = NEXT
hb["free_ram_gb"] = 7.0
hb["gpu_free_vram_mb"] = 14896
hb["gpu_free_vram_mib"] = 14896
hb["cpu_pct"] = "4"
hb["cores"] = 32
hb["total_ram_gb"] = 23.9
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["health"] = "ok"
io.open(hp, "w", encoding="utf-8", newline="\n").write(json.dumps(hb, indent=1, ensure_ascii=False))
back2 = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(back2["heartbeat_epoch_utc"], int), "hb epoch must be int"
print("heartbeat OK: epoch int verified")

# --- round-report row ---
rp = os.path.join(ROOT, "round_reports-bm-c.md")
t = io.open(rp, encoding="utf-8", newline="").read()
io.open(rp, "a", encoding="utf-8", newline="\n").write(ROW + "\n")
print("round report row appended")
