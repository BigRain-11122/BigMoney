# -*- coding: utf-8 -*-
# r1049 bm-c closeout: round report row (canonical path r750 law) + state round_no 1049->1050 + heartbeat.
import io, json, datetime, subprocess, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now().astimezone()
TS = now.isoformat(timespec="seconds")          # 2026-10-16T10:4x:xx+08:00
EPOCH = int(now.timestamp())
FREEZE_T = "%02d:%dx" % (now.hour, now.minute // 10)

ROW = (
    "2026-10-16T10:%dx | r1049 | (1) S0-1 anchor bm-c + round-zero probe py_faces=5 orphans=2 zero-kill; "
    "S0 fetch 0/0 (HEAD==origin b1ca46495 at open, no rebase owed); "
    "(2) S0.5 dual-delta FALSE both scans (ORD f321f54a / DEC ec6b9164 hold, opening + S7 tail, unacked=0); "
    "(3) S1 smoke 49/49; "
    "(4) S3 boards: jobs 0 / satengine rc0 alive / wm red=false insufficient_history fresh window / "
    "idle green_idle=false RAM-gate honest (27.5pct free, claimable_pool_lines=1 stays per r354); "
    "(5) P0 PRODUCT = W252 PREREG FREEZE LANDED 472cc8386 pushed first-try (seat-first FIRST ACTION per next_pointer; "
    "machine-SUB from committed frozen W251 tpl 9f5f106d6, blob 60d2b4e9 byte-verified in-script via git hash-object; "
    "STAIRCASE-AFFECTS-A live face: A 569_701..571_700 hops=1 FIRST A-HOP SINCE W239 ERA (naive 569_501..571_500 REFUSED at "
    "registered W251 B band 569_501..569_700; W251 item5 A-CLEAN projection superseded live r587, divergence disclosed) / "
    "B 571_701..571_900 hops=1 own-A reservation past 571_700 (second consecutive above-own-A; B base==own-A tail+1 re-emerges); "
    "key-anchored to W251 actuals ledger 976,535 / K=550,120 (merged mu -0.09274994 / sigma 0.2450362 / se_mu 0.000330 / "
    "W251-only mu -0.08776 / A p95 0.3153 / K-lift +0.0001 in-band first nonzero micro-move / n_eff_held 974,335 / "
    "line_pre_w251 1.194 / line_merged_550120 1.1941); banned_direction_gate ADMIT rc0; "
    "count-asserted 50 legs + 75 floors + 10 POST legs + 8 blocks + MUST 87 + MUST_NOT 61 + W253+ count gate 4/0 "
    "(two POST legs repair wave-roll collateral: se_mu chain tail restore + K-lift value face; zero disclosed needle heals); "
    "W252 seat MSG swept to processed zero-loss; same-window defect caught+fixed pre-freeze: MSG leg split form "
    "-bmc-w251-seat straggler x3 -> full-form leg (r1047 precedent); "
    "(6) S6 43/43 rc0 (bars 10-16 not due till 15:30 papers debt=0; dualrun ZERO-DRIFT streak 7; audit FLAG supply_floor "
    "structural answered-by-chain W252; update_daily cutoff 10-15 fresh); "
    "(7) S7 quad green (pin=5 no-op + watchdog S4U flip access-denied = adjudicated default-principal face + claws x2 installed) "
    "+ attrition 4 CLEAN + tail dual-scan FALSE + idle --worked "
    "| receipts: push b1ca46495..472cc8386 rev-parse verified HEAD==origin + gate ADMIT rc0 x2 (pre+post fix) + "
    "derive stdout all-gates + smoke 49/49 + S6 log 43x rc=0 (_r1049bmc_s6_log.txt) + attrition 4 CLEAN + epoch int readback "
    "| 下轮指针 r1050: (1) five-face splice = FIRST ACTION (editor derive canon clone from _w251bmc_freeze_edits.py via "
    "_w251bmc_derive_editor.py clone -- NEW FACE both bands: A flips clean->1-hop staircase walk + B flips 13-hop->1-hop "
    "own-A reservation, P5e chunks must rewrite BOTH A and B faces; gate0.5 W251 row + W251 finalize present; "
    "parity 110 rows = estate 69 W138..W206 + kept W211..W238 28 + fresh W239..W251 13; dual-sha16 receipt; "
    "needle-count prep evidence results/_w252bmc_ctx2.txt + frozen face _w252bmc_w251_frozen_face.txt committed); "
    "(2) engine mtime-watch self-burn 12/12 follows; (3) sixgate PRE-FINALIZE correct-phase (W217-debt standing law); "
    "(4) finalize one-pass 976,535+2,200=978,735 EXACT / merged K=552,320 projection + fivekeys vs W251 keys + sec.7/8 backfill; "
    "(5) W253 seat publish after finalize (post-W252 live re-derive -- staircase continues: naive W253 A 571_701..573_700 "
    "will be REFUSED at registered W252 B band 571_701..571_900 = A second consecutive hop + B reservation cascade, "
    "live re-derive governs r587); (6) 5x HANDOVER duty: executing round r1050 IS a 5x multiple -- consolidate r1026-r1050 "
    "with OVERDUE stamps r1030/r1035/r1040/r1045 disclosed per r1025 precedent; (7) bars 10-16 window 15:30 "
    "(papers debt=0, if new bar lands fire full papers chain); (8) ORD/DEC tail re-scan" % (now.minute // 10)
)

# ---- round report row (canonical path r750 law) ----
RP = os.path.join(REPO, "round_reports-bm-c.md")  # canonical ROOT face (r750 law; logs/ copy frozen r1007)
rp = io.open(RP, encoding="utf-8", newline="").read()
if not rp.endswith("\n"):
    rp += "\n"
rp += "- " + ROW + "\n"
io.open(RP, "w", encoding="utf-8", newline="").write(rp)

# ---- state ----
ST = os.path.join(REPO, "state-bm-c.json")
st = json.loads(io.open(ST, encoding="utf-8").read())
assert st["round_no"] == 1049, "state round_no=%s expect 1049" % st["round_no"]
st["round_no"] = 1050
st["last_round"] = "r1049"
st["last_round_at"] = TS
st["last_round_ts"] = TS
st["last_round_label"] = "r1049"
st["last_round_closed"] = TS
st["last_action"] = "r1049 closeout (W252 prereg freeze LANDED 472cc8386)"
st["last_action_at"] = TS
st["current_task"] = "r1049 closeout (W252 prereg freeze landed + S6/S7 green)"
st["current_task_at"] = TS
st["current_task_ts"] = EPOCH
st["clock_read"] = TS
st["ts"] = TS
st["updated"] = TS
st["updated_at"] = TS
st["now_active"] = TS
st["activity_now"] = TS
st["heartbeat_epoch_utc"] = EPOCH
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["orphan_face"] = 2
st["orphan_faces"] = 2
st["note"] = ("r1049: W252 PREREG FROZEN 472cc8386 (A 569_701..571_700 hops=1 staircase-affects-A FIRST A-hop since W239 era / "
              "B 571_701..571_900 hops=1 own-A reservation) | five-face splice = r1050 FIRST ACTION | W253 forward face: "
              "staircase continues, live re-derive governs r587 | r1050 = 5x HANDOVER duty (overdue stamps r1030/1035/1040/1045)")
st["did"] = ROW
st["verdict"] = ("green: r1049 = P0 PRODUCT W252 PREREG FREEZE LANDED 472cc8386 first-try (staircase-affects-A live face: "
                 "A 569_701..571_700 hops=1 first A-hop since W239 era with W251 projection supersession disclosed / "
                 "B 571_701..571_900 hops=1 own-A reservation second consecutive above-own-A; key-anchored W251 actuals "
                 "ledger 976,535/K=550,120; banned ADMIT rc0; count-asserted all-gates transform, zero disclosed needle heals) "
                 "+ S0.5 dual-delta FALSE both scans + smoke 49/49 + S6 43/43 rc0 (bars 10-16 not due, papers debt=0) + "
                 "S7 quad green + attrition 4 CLEAN + W252 seat MSG swept to processed")
st["verify"] = ("receipts: push b1ca46495..472cc8386 landed first-try (rev-parse HEAD==origin 472cc8386909b3f81e3d33365f8e73766a9503fd) "
                "+ banned_direction_gate ADMIT rc0 (pre+post MSG-leg fix) + derive stdout (50 legs/75 floors/10 POST/8 blocks/"
                "MUST 87/MUST_NOT 61/W253+ 4/0) + src blob-verified 60d2b4e9 via git hash-object in-script + "
                "smoke 49/49 + S6 log 43x rc=0 (_r1049bmc_s6_log.txt) + attrition 4 CLEAN + epoch int readback + "
                "ORD/DEC dual-delta FALSE both scans (opening + S7 tail)")
st["head_sha"] = "472cc8386 (W252 prereg freeze push landed first-try; closeout commit rides this window)"
st["last_artifact"] = ("research/PERPETUAL_N1_W252_PREREG.md (W252 prereg freeze LANDED 472cc8386 pushed origin 10-16 10:3x, "
                       "banned_direction_gate ADMIT rc0, A 569_701..571_700 staircase-affects-A / B 571_701..571_900 own-A "
                       "reservation, key-anchored to W251 actuals ledger 976,535 / K=550,120) + results/_r1049bmc_s6_log.txt (43 legs rc=0)")
st["latest_artifact"] = st["last_artifact"]
st["recent_artifact"] = st["last_artifact"]
st["sync"] = {"origin_tip": "472cc8386 (W252 prereg freeze push landed first-try clean)", "ts": TS,
              "ahead_behind": "local-ahead-0 (push + rev-parse verified; closeout commit rides this window)"}
st["last_pulled_at"] = TS
st["full_load_selfproof"] = {
    "占用一行": ("CPU=engine queue never-dry (W252 PREREG FROZEN 472cc8386 -> five-face splice = r1050 first action) ; "
                 "GPU=VRAM 14.5G free ; N1=W251 COMPLETE (ledger 976,535 / K=550,120, fivekeys ALL PASS) + "
                 "W252 SEAT CANDIDATE-RESERVED + PREREG FROZEN (A 569_701..571_700 staircase-A hops=1 / "
                 "B 571_701..571_900 hops=1 own-A reservation) ; SPAWN-GATE=codely cap2 live"),
    "当前活": "r1049 closeout (W252 prereg freeze landed)",
    "最近实物": st["last_artifact"],
    "下个交付物": "W252 five-face splice + engine self-burn 12/12 + sixgate + finalize (978,735/K=552,320 投影) + W253 seat (r1050 chain) + 5x HANDOVER r1026-r1050",
    "队列水位": "池 ready=0·N1 W252 prereg frozen·P2/P3 空·jobs 0",
}
st["prod_lanes"] = ("CPU=engine queue never-dry (W252 PREREG FROZEN -> splice r1050 first action) ; GPU=VRAM 14.5G free ; "
                    "N1=W251 COMPLETE (ledger 976,535 / K=550,120 EXACT, fivekeys ALL PASS, K-lift +0.0001 in-band first nonzero) "
                    "+ W252 SEAT published f9441de67 + PREREG FROZEN 472cc8386 (A 569_701..571_700 staircase-A hops=1 / "
                    "B 571_701..571_900 hops=1 above-own-A) ; SPAWN-GATE=codely cap2 live")
st["next_pointer"] = (
    "r1050: (1) five-face splice = FIRST ACTION (editor derive canon clone from _w251bmc_freeze_edits.py via "
    "_w251bmc_derive_editor.py clone -- NEW FACE BOTH BANDS: A flips FIRST-CLEAN->1-HOP staircase walk (first since W239 era: "
    "P5e must rewrite A-face chunks too) + B flips 13-HOP->1-HOP own-A reservation; band asserts "
    "(a_lo,a_hi)==(569701,571700) and (b_lo,b_hi)==(571701,571900); gate0.5 W251 row + W251 finalize present; "
    "parity 110 rows = estate 69 (W138..W206) + kept W211..W238 (28) + fresh W239..W251 (13); dual-sha16 receipt; "
    "prep evidence committed: results/_w252bmc_ctx2.txt needle counts + results/_w252bmc_w251_frozen_face.txt frozen tpl); "
    "(2) engine mtime-watch self-burn 12/12 follows (2-cycle product-growth face r325 law); "
    "(3) sixgate PRE-FINALIZE correct-phase (W217-debt standing law); "
    "(4) finalize one-pass ledger 976,535+2,200=978,735 EXACT / merged K=552,320 projection + fivekeys vs W251 keys "
    "(key1 gap ~W252-only vs merged |<0.02| / key2 sigma drift <10% / key3 A p95 drift <0.05 / key4 K-lift <=0.02 / "
    "key5 se_mu <=0.000330) + sec.7/8 backfill (bm-c r1049 W252 范式 rows); "
    "(5) W253 seat publish after finalize (post-W252 universe live re-derive, staircase continues: naive W253 A "
    "571_701..573_700 will be REFUSED at registered W252 B band 571_701..571_900 -> A second consecutive hop + "
    "B own-A reservation cascade ~573_901..574_100-class landing, live re-derive governs r587, never transcribe); "
    "(6) 5x HANDOVER duty: r1050 IS a 5x multiple -- consolidate r1026-r1050 row with OVERDUE stamps "
    "r1030/r1035/r1040/r1045 disclosed (r1025 precedent, last bm-c 5x row = r1025); "
    "(7) bars 10-16 window 15:30 (papers debt=0, if new bar lands fire full papers chain); (8) ORD/DEC tail re-scan"
)
st["next"] = st["next_pointer"]
st["next_milestone"] = "r1050+: W252 splice -> burn -> sixgate -> finalize (978,735/K=552,320) -> W253 seat + 5x HANDOVER + bars 10-16 15:30 窗"
st["r1049_closeout_note"] = (
    "r1049: (1) S0-1 anchor bm-c + round-zero probe py_faces=5 orphans=2 zero-kill + S0 fetch 0/0 "
    "(HEAD==origin b1ca46495 at open, 37 dirty = daemon live-faces + prior scratch, no rebase owed); "
    "(2) S0.5 dual-delta FALSE both scans (ORD f321f54a / DEC ec6b9164 hold, unacked=0); (3) smoke 49/49; "
    "(4) P0 PRODUCT = W252 PREREG FREEZE LANDED 472cc8386 pushed first-try: derive results/_w252bmc_prereg_derive.py "
    "(machine-SUB from committed frozen W251 tpl 9f5f106d6, src blob 60d2b4e9 byte-verified in-script via git hash-object; "
    "50 vmap legs + 75 floors + 10 POST legs + 8 marker-extracted blocks + MUST 87 + MUST_NOT 61 + W253+ count gate 4/0 + "
    "window well-formed regex; HIST spans machine-extracted from T0 pre-roll bytes zero-transcription for b1 chain + "
    "b6 RAM ledger) -> research/PERPETUAL_N1_W252_PREREG.md 37,501B/64 lines; banned_direction_gate ADMIT rc0; "
    "STAIRCASE-AFFECTS-A live face A 569_701..571_700 hops=1 (naive refused at registered W251 B band; W251 item5 A-CLEAN "
    "superseded live r587 disclosed) / B 571_701..571_900 hops=1 own-A reservation (second consecutive above-own-A); "
    "same-window defect caught+fixed PRE-freeze: MSG seat-leg split form left '-bmc-w251-seat' suffix x3 -> full-form leg "
    "(r1047 needle precedent), re-derive all-gates green + straggler scan clean (lowercase w-tokens all legit); "
    "(5) S6 43/43 rc0 absorbed-not-rerun... NO -- this window RAN the full chain (driver Tools/_r1049bmc_s6.py canon clone of "
    "r1048, log results/_r1049bmc_s6_log.txt): dualrun ZERO-DRIFT streak 7 / audit FLAG supply_floor answered-by-chain "
    "(W252 prereg frozen -> splice next) / wm insufficient_history fresh / update_daily 0 rows cutoff 10-15 fresh "
    "(bars 10-16 not due till 15:30, papers debt=0) / lane no-ops honest; (6) W252 seat MSG swept to processed (zero-loss); "
    "(7) S7 quad green (loop pin=5 no-op + watchdog registered [S4U XML flip access-denied = adjudicated default-principal "
    "standing face] + precommit claw + prepush claw) + attrition 4 CLEAN + idle_trigger green_idle=false RAM-gate honest "
    "(27.5pct free) + --worked same-window; counter 1049->1050 so next session = r1050 (5x multiple: HANDOVER duty due)"
)
st["last_round_summary"] = (
    "r1049: W252 PREREG FREEZE LANDED 472cc8386 (staircase-affects-A A first-hop since W239 era / B own-A reservation "
    "hops=1; W251 actuals key-anchored; banned ADMIT rc0; zero disclosed needle heals) + S6 43/43 + smoke 49/49 + "
    "S7 quad green + attrition 4 CLEAN"
)
st["last_round_summary_at"] = TS
st["loop_round"] = 996
io.open(ST, "w", encoding="utf-8", newline="").write(
    json.dumps(st, ensure_ascii=False, indent=1) + "\n")

# ---- heartbeat ----
HB = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.loads(io.open(HB, encoding="utf-8").read())
for k in ("round_no", "last_round", "last_round_at", "last_round_ts", "last_round_label",
          "last_round_closed", "last_action", "last_action_at", "current_task", "current_task_at",
          "current_task_ts", "clock_read", "ts", "updated", "updated_at", "now_active", "activity_now",
          "heartbeat_epoch_utc", "idle_rounds", "agenda_starved", "note", "did", "verdict", "verify",
          "head_sha", "last_artifact", "latest_artifact", "recent_artifact", "sync", "last_pulled_at",
          "full_load_selfproof", "prod_lanes", "next_pointer", "next", "next_milestone",
          "r1049_closeout_note", "last_round_summary", "last_round_summary_at"):
    hb[k] = st[k]
hb["last_seen"] = TS
hb["last_seen_at"] = TS
hb["last_ts"] = TS
hb["idle_ram_gb"] = 7.0
hb["ram_free_gb"] = 7.0
hb["free_ram_gb"] = 7.0
json.dump_check = None
data = json.dumps(hb, ensure_ascii=False, indent=1)
io.open(HB, "w", encoding="utf-8", newline="").write(data + "\n")

# readback asserts
rb = json.loads(io.open(HB, encoding="utf-8").read())
assert isinstance(rb["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in rb["clock_read"] and "+" in rb["clock_read"], "clock_read malformed"
srb = json.loads(io.open(ST, encoding="utf-8").read())
assert srb["round_no"] == 1050 and srb["last_round"] == "r1049"
print("CLOSEOUT WRITES OK: report row + state 1049->1050 + heartbeat (epoch int readback PASS)")
print("TS=%s EPOCH=%d FREEZE_T=%s" % (TS, EPOCH, FREEZE_T))
