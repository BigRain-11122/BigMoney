# -*- coding: utf-8 -*-
# r1047 bm-c closeout: state + heartbeat + round-report row (canon clone pattern
# of _r1046bmc_closeout.py lineage). Clean continuation window: r1046 closeout landed
# clean, state round_no was 1047 at open, executed as r1047 per counter, advanced
# 1047->1048 so next session = r1048; zero absorb owed.
import io
import json
import os
import time
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

ABSORB = ("")  # clean continuation window -- zero absorb owed (r1046 closeout landed clean)

DID = ("r1047 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=5 orphans=2 zero-kill (ComfyUI "
       "standalone 1656min + album-serve pythonw 6442min = legal detached residents, probe default "
       "read-only); (2) S0 fetch 0/0 (HEAD==origin 0a172bd4c at open, daemon live-faces legit dirty, no "
       "rebase owed); (3) S0.5 dual-delta FALSE both scans + unacked=0 (ORD f321f54a / DEC ec6b9164 hold, "
       "opening + S7 tail); (4) S1 smoke 49/49; (5) S3 boards clear (tasks open=0 / P2 T5-T14 done / P3 "
       "E1-E10 done-closed / jobs 0 / satengine ALIVE rc0 / wm red=false / idle green_idle=false RAM 28pct "
       "gate honest); (6) P0 PRODUCT = W251 PREREG FREEZE LANDED 9f5f106d6 first-try push clean (seat-first "
       "FIRST ACTION per r1046 next_pointer): machine-SUB from committed frozen W250 template 4f7a130ff "
       "(frozen face byte-verified == blob 910aa89c, 34,465B) via count-asserted ordered transform "
       "results/_w251bmc_prereg_derive.py -- 52 vmap legs + 75 needle floors + 9 post-legs + 7 block "
       "replaces + 79 MUST + 53 MUST_NOT + count gates + window regex ALL green, bands A 567_501..569_500 "
       "hops=0 (FOURTEENTH consecutive seed-gap, A base==W250 A tail 567_500+1) / B 569_501..569_700 = "
       "13-HOP WALK (naive 545_301..545_500 REFUSED at seed 545_500 + W240..W249 A-ladder + W250-A + "
       "own-A reservation; B lands ABOVE own-A first since W239 staircase era; B base==own-A tail "
       "569_500+1 EXACT), key-anchored to W250 actuals ledger 974,335 / K=547,920 (merged mu -0.09276996 "
       "/ sigma 0.2450351 / se_mu 0.000331 / A p95 0.3235 / K-lift 0.0000 / n_eff_held 972,135), "
       "banned_direction_gate ADMIT rc0, 1 disclosed needle heal (sec8 placeholder projection-label lag "
       "W251+->W252+, disclosed in script header + commit); W252 freezer forward face: naive B "
       "569_701..569_900 lands INSIDE naive W252 A window 569_501..571_500 = staircase re-emergence, live "
       "re-derive governs r587; (7) W251 seat MSG swept to processed (zero-loss inbox move, r1046 addendum "
       "precedent); (8) S6 43/43 rc0 idempotent sweep via canon-clone driver Tools/_r1047bmc_s6.py (bars "
       "10-16 not due till 15:30, papers debt=0, token delta=0); (9) S7 quad green (pin=5 no-op + watchdog "
       "registered S4U access-denied adjudicated face + claws x2 installed) + attrition 4 CLEAN; counter "
       "1047->1048")

NEXT = ("r1048: (1) W251 five-face freeze splice = FIRST ACTION (editor derive canon clone from committed "
        "_w250bmc_freeze_edits.py template, gate0.5 self-check W250 row + W250 finalize present, estate "
        "extraction face = W250 block physical bytes, parity 109 rows W138..W206+W211..W250, dual-sha16 "
        "receipt; engine mtime-watch self-burn 12/12 follows); (2) sixgate PRE-FINALIZE correct-phase (W217-"
        "debt standing law, E70 landed-blob gate-1 anchor face); (3) finalize one-pass ledger 974,335+2,200="
        "976,535 EXACT / merged K=550,120 projection (registry-key derive at runtime) + fivekeys vs W250 "
        "keys + sec.7/8 backfill; (4) W252 seat publish after finalize (post-W251 universe live re-derive, "
        "own-A reservation mandatory); (5) bars 10-16 window 15:30 (papers debt=0); (6) ORD/DEC tail "
        "re-scan")

VERDICT = ("green: r1047 = clean continuation + P0 PRODUCT W251 PREREG FREEZE LANDED 9f5f106d6 first-try "
           "(machine-SUB 52-leg transform ALL gates green, 13-hop B walk above-own-A face first since "
           "staircase era, banned ADMIT rc0, 1 disclosed needle heal) + S6 43/43 + smoke 49/49 + S7 quad "
           "green + attrition 4 CLEAN")

PROD = ("CPU=W20 SCREEN 4/4 shards ALL DONE (pool face closed r1044 chain) + engine queue idle (never-dry "
        "supply = W251 prereg FROZEN, splice next) ; GPU=VRAM 14.5G free ; N1=W250 COMPLETE (ledger "
        "974,335 / K=547,920) + W251 PREREG FROZEN 9f5f106d6 (A 567_501..569_500 / B 569_501..569_700) -> "
        "five-face splice r1048 first action ; SPAWN-GATE=codely cap2 live")

ARTIFACT = ("research/PERPETUAL_N1_W251_PREREG.md (freeze 10-16 09:0x, commit 9f5f106d6, 35,820B, banned "
            "ADMIT rc0, key-anchored to W250 actuals 974,335/547,920) + results/_w251bmc_prereg_derive.py "
            "(52 legs + 9 post-legs + 7 blocks + 79 MUST + 53 MUST_NOT) + results/_w251bmc_w250_frozen_face.txt "
            "(byte-verified == blob 910aa89c)")

CLOSE = ("r1047: clean continuation (zero absorb owed) + W251 PREREG FREEZE LANDED 9f5f106d6 (machine-SUB "
         "from frozen W250 tpl, A hops=0 14th seed-gap / B 13-hop walk lands above own-A first since W239 "
         "staircase era, 1 disclosed needle heal sec8 label) + S6 43/43 + smoke 49/49 + S7 quad green + "
         "attrition 4 CLEAN | " + NOW)

SELFPROOF = {
    "占用一行": PROD,
    "当前活": "r1047 closeout (W251 prereg frozen + S6 sweep)",
    "最近实物": ARTIFACT,
    "下个交付物": "W251 five-face splice + engine self-burn 12/12 + sixgate + finalize (ledger 976,535 / K=550,120 投影) + W252 seat + bars 10-16 15:30 窗",
    "队列水位": "池 ready=0 (W20 closed)·N1 W251 prereg frozen→splice r1048·P2/P3 空·jobs 0",
}

ROW = (NOW + " | r1047 | bm-c | watermark verdict=绿 (satengine ALIVE rc0 / py_watermark loaded_ok lane / "
       "red=false) | clean continuation (state round_no=1047 at open, executed r1047, advanced 1047->1048) "
       "+ P0 PRODUCT = W251 PREREG FREEZE LANDED 9f5f106d6 first-try push clean (seat-first FIRST ACTION: "
       "machine-SUB from committed frozen W250 tpl 4f7a130ff byte-verified == blob 910aa89c via "
       "count-asserted ordered transform -- 52 vmap legs + 75 floors + 9 post-legs + 7 blocks + 79 MUST + "
       "53 MUST_NOT + count gates + window regex ALL green; bands A 567_501..569_500 hops=0 FOURTEENTH "
       "seed-gap / B 569_501..569_700 = 13-HOP WALK landing ABOVE own-A first since W239 staircase era "
       "(seed 545_500 + W240..W249 A-ladder + W250-A + own-A reservation, B base==own-A tail 569_500+1 "
       "EXACT); key-anchored to W250 actuals 974,335 / 547,920 (mu -0.09276996 / sigma 0.2450351 / se_mu "
       "0.000331 / p95 0.3235 / K-lift 0.0000 / n_eff_held 972,135); banned ADMIT rc0; 1 disclosed needle "
       "heal = sec8 placeholder projection-label lag W251+->W252+; W252 freezer forward face = naive B "
       "569_701..569_900 lands INSIDE naive W252 A window = staircase re-emergence, live re-derive governs "
       "r587) + W251 seat MSG swept to processed + S0.5 dual-delta FALSE both scans (opening + tail) + "
       "smoke 49/49 + S6 43/43 rc0 (bars 10-16 not due till 15:30, papers debt=0) + S7 quad green (pin=5 "
       "no-op + watchdog S4U adjudicated face + claws x2) + attrition 4 CLEAN | next: W251 five-face "
       "splice r1048 FIRST ACTION -> engine self-burn -> sixgate PRE-FINALIZE -> finalize 976,535/K=550,120 "
       "-> W252 seat | ledger 974,335 | 本地未达 origin commit 数=0 (push+rev-parse verify in closeout) | "
       "孤儿面=2 (zero-kill legal detached residents)")

# --- state face ---
sp = os.path.join(ROOT, "state-bm-c.json")
st = json.load(io.open(sp, encoding="utf-8"))
st["machine_id"] = "bm-c"
st["round_no"] = 1048
st["last_round"] = "r1047"
st["last_round_label"] = "r1047"
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
st["current_task"] = "r1047 closeout (W251 prereg frozen + S6 sweep)"
st["current_task_at"] = NOW
st["current_task_ts"] = EPOCH
st["last_action"] = "r1047 closeout (W251 prereg freeze + S6 sweep)"
st["last_action_at"] = NOW
st["last_round_closed"] = NOW
st["last_round_summary"] = ("r1047: clean continuation + W251 PREREG FREEZE LANDED 9f5f106d6 (machine-SUB "
                            "13-hop B walk above-own-A, banned ADMIT, 1 disclosed needle heal) + S6 43/43 "
                            "+ smoke 49/49 + S7 quad green")
st["last_round_summary_at"] = NOW
st["last_artifact"] = ARTIFACT
st["latest_artifact"] = ARTIFACT
st["recent_artifact"] = ARTIFACT
st["next"] = NEXT
st["next_pointer"] = NEXT
st["next_milestone"] = "r1048+: W251 five-face splice + engine self-burn + sixgate + finalize (976,535/K=550,120) + W252 seat + bars 10-16 15:30 window"
st["verdict"] = VERDICT
st["note"] = ("r1047: W251 PREREG FROZEN 9f5f106d6 (A 567_501..569_500 / B 569_501..569_700 13-hop walk "
              "above-own-A, banned ADMIT rc0) | five-face splice = r1048 first action | W252 forward face: "
              "staircase re-emergence, live re-derive governs")
st["did"] = DID
st["verify"] = ("receipts: derive stdout ALL gates green (52 legs/75 floors/9 post-legs/7 blocks/79 MUST/53 "
                "MUST_NOT) + banned_direction_gate ADMIT rc0 + freeze commit 9f5f106d6 first-try push "
                "origin==HEAD rev-parse verified + smoke 49/49 + S6 log 43x rc=0 "
                "(_r1047bmc_s6_log.txt) + attrition 4 CLEAN + epoch int readback + ORD/DEC dual-delta FALSE "
                "both scans (opening + S7 tail)")
st["prod_lanes"] = PROD
st["full_load_selfproof"] = SELFPROOF
st["ram_free_gb"] = 6.5
st["free_ram_gb"] = 6.5
st["idle_ram_gb"] = 6.5
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
st["loop_round"] = st.get("loop_round", 995) + 1
st["head_sha"] = "closeout commit rides this window (push verify in closeout)"
st["r1047_absorb_note"] = ABSORB
st["r1047_closeout_note"] = CLOSE
io.open(sp, "w", encoding="utf-8", newline="\n").write(json.dumps(st, indent=1, ensure_ascii=False))
back = json.load(io.open(sp, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int"
assert back["round_no"] == 1048
print("state OK: round_no 1047->1048, epoch int verified")

# --- heartbeat face ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(io.open(hp, encoding="utf-8"))
hb["machine_id"] = "bm-c"
hb["last_seen"] = NOW
hb["last_seen_at"] = NOW
hb["ts"] = NOW
hb["clock_read"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["current_task"] = "r1047 closeout (W251 prereg frozen + S6 sweep)"
hb["current_task_at"] = NOW
hb["last_round"] = "r1047"
hb["last_round_at"] = NOW
hb["last_round_summary"] = st["last_round_summary"]
hb["did"] = DID
hb["verdict"] = VERDICT
hb["prod_lanes"] = PROD
hb["latest_artifact"] = ARTIFACT
hb["next_pointer"] = NEXT
hb["free_ram_gb"] = 6.5
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
