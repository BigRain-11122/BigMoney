# -*- coding: utf-8 -*-
"""r1066 bm-c closeout: state + heartbeat + canonical round-report line + CODELY S4 one-liner + seat MSG sweep.
Single-file read-modify-write per shared-file law (python, json.load->json.dump).
"""
import json, time, io, os, shutil, datetime
if True:
    import sys
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
ROUND = "r1066"
NEXT_ROUND_NO = 1067

# --- watermark red face read (verdict line) ---
try:
    wr = json.load(io.open(r"results\watermark_red.json", encoding="utf-8"))
    red = wr.get("red")
except Exception as e:
    red = None
    print("watermark_red read err:", e)

# ---------- S4: CODELY.md one-line pit entry (absorb-estate stale-receipt law) ----------
CODELY_ENTRY = ("[2026-10-17 13:2x r1066 bm-c] \u5438\u6536\u7a97 estate \u56de\u6267\u65f6\u6ede\u5224\u4f8b\uff08W261 prereg absorb \u5b9e\u5f39\uff09\uff1a\u6b7b\u7a97\u5728\u811a\u672c\u5185 heal\uff08'987,535' floor 2->1\u00b7VMAP FLOOR FAIL \u540e\u4fee\u6b63+\u91cd\u8dd1\uff09\u540e\u624d\u6b7b\u2014\u2014\u5176 floor_audit.txt \u505c\u7559\u5728 heal \u524d\u72b6\u6001\uff08mismatches=1 \u5047\u7ea2\uff09\uff0c\u5438\u6536\u7a97\u9996\u5224\u9669\u4e9b\u8bef\u8bca\u4e3a\u5185\u5bb9\u7f3a\u9677\uff1b\u6b63\u6cd5=\u5224\u8bfb estate \u56de\u6267 mismatch \u524d\u5148\u5bf9\u7167\u811a\u672c\u5185 heal \u62ab\u9732\u6ce8\u8bb0+\u91cd\u8dd1\u8be5\u56de\u6267\u5b9a\u8c2d\uff08\u91cd\u8dd1=231/231 \u96f6 mismatch\uff09\u3002How\uff1a\u5438\u6536\u94fe\u4e00\u5207 verification \u56de\u6267\uff08audit txt/needle counts\uff09\u5fc5\u987b\u4e0e\u811a\u672c\u7ec8\u6001\u540c\u7a97\u91cd\u8dd1\u540e\u624d\u53ef\u5f53\u73b0\u503c\u5224\u8bfb\u3002\r\n")
cp = r"CODELY.md"
old_codely = io.open(cp, encoding="utf-8", errors="replace").read()
assert "r1066 bm-c" not in old_codely, "CODELY r1066 entry already present"
io.open(cp, "a", encoding="utf-8", newline="").write(CODELY_ENTRY)
print("CODELY.md appended one line; new size:", len(io.open(cp, "rb").read()))

# ---------- seat MSG sweep to processed ----------
src_msg = r"fleet\inbox\MSG-20261017-1225-bmc-w261-seat.md"
dst_msg = r"fleet\inbox\processed\MSG-20261017-1225-bmc-w261-seat.md"
if os.path.exists(src_msg) and not os.path.exists(dst_msg):
    shutil.move(src_msg, dst_msg)
    print("seat MSG swept to processed")

# ---------- state ----------
sp = r"state-bm-c.json"
st = json.load(io.open(sp, encoding="utf-8"))
assert st["round_no"] == 1066, f"state round_no {st['round_no']} != 1066 (open face drift)"
st["round_no"] = NEXT_ROUND_NO
st["round_no_label"] = ROUND
st["last_round"] = ROUND
st["last_round_at"] = NOW
st["last_round_closed"] = NOW
st["clock_read"] = NOW
st["ts"] = NOW
st["last_seen"] = NOW
st["now_active"] = NOW
st["activity_now"] = NOW
st["current_task"] = "r1066 closeout (56th-gen absorb continuation: W261 PREREG FREEZE landed 03ab504d7 + ORD 3-row consumed + S6 43/43)"
st["current_task_at"] = NOW
st["last_action"] = "r1066 closeout (56th-gen absorb continuation + W261 prereg freeze landed 03ab504d7; counter 1066->1067)"
st["last_action_at"] = NOW
st["last_round_summary"] = "r1066: 56th-gen absorb continuation (W261 PREREG FREEZE landed 03ab504d7 first-try + dead-window derive estate verified) + ORD 3-row consumed (all BigStream-lane) + S6 43/43 run this window + quad green"
st["last_round_summary_at"] = NOW

st["r1066_absorb_note"] = ("r1066 absorb note: dead window (self-labeled r1066, fired ~12:3x after r1065 closeout 12:28:11) executed the FULL W261 prereg derive body on disk: "
 "frozen-face extraction results/_w261bmc_w260_frozen_face.txt (byte-identical 47,643B sha256_16 87a4c206a35e0584 @ freeze-commit 0f33f9abc pre-backfill face per r1052/r1049 law) "
 "+ needle probe results/_w261bmc_needle_probe.py + counts (post-roll T1 forms extracted by probe simulation) "
 "+ derive script results/_w261bmc_prereg_derive.py (635 lines; ALL GATES PASS; vmap+floors 231+post-legs+MUST/MUST_NOT+8 blocks; "
 "5 disclosed same-window needle heals: (1) bare '已落账键' leg canon-redundant no-op kept, (2) NO K-lift POST_LEG 2nd consecutive true-0.0000 wave, "
 "(3) RAM face honest update ~2GB->~11GB + LLM face RETIRED per CEO order O-20261017-0953, (4) consumed-label W254 pre-authored per r1059 canon-embed advice, "
 "(5) '987,535' floor 2->1 live-audit heal [b1-HIST W257-era ledger head appears ONCE in frozen W260 face; W259-template twin carried 2, pattern-assumed floor corrected; zero content impact]) "
 "+ floor audit results/_r1066bmc_floor_audit.py (231 floors post-heal 0 mismatches -- the on-disk txt initially read mismatches=1 = PRE-heal stale-receipt face, "
 "re-run THIS window after reading the script's L59 heal disclosure = 231/231 clean; stale-receipt absorb law appended to CODELY.md) "
 "+ W260 keys machine-read results/_r1066bmc_w260_keys_dump.txt (merged mu -0.09273073 / sigma 0.24503935 / W260-only -0.09156055 / A p95 0.3292 / line_merged 1.195 / se_mu 0.000325 / K-lift 0.0) "
 "+ ORD tail extraction (ord_tail/ord_tail2 scratch) -- died pre-commit (state frozen round_no=1066, zero own commits). "
 "THIS session (per bm-c absorb precedent lineage r894..r1065, 56th instance) machine-verified the estate BEFORE landing: "
 "banned_direction_gate re-run ADMIT rc0 + needle probe re-run rc0 (utf-8 env; first print run died on GBK \\u2212 = known pit-encoding face) "
 "+ frozen face byte-identity vs blob @0f33f9abc (47,643B sha256_16 87a4c206a35e0584) + floor audit re-run 231/231 + probe receipt re-read (committed @ r1065 seat cf23c4553) "
 "+ smoke 49/49, then landed W261 PREREG FREEZE commit 03ab504d7 pushed first-try (d647cd295..03ab504d7); out 49,660B sha256_16 2a2921f1bb741f31; "
 "executed as r1066 per counter, advanced 1066->1067 so next session = r1067; zero double-count: the dead window consumed no ORD/DEC rows (no watermark writes), "
 "the 3 in-range ORD rows consumed THIS window with d19 update --advance read-back full-equality")

st["r1066_closeout_note"] = ("r1066: 56th-gen absorb continuation (dead-window W261 prereg derive estate verified+landed) + W261 PREREG FREEZE origin 03ab504d7 "
 "(bands A 589_501..591_500 TENTH consecutive A-hop / B 591_501..591_700 ELEVENTH consecutive above-own-A per seat probe receipt ADMIT; "
 "frozen tpl byte-identical @0f33f9abc; floor audit 231/231 post-heal; 5 disclosed needle heals; banned ADMIT rc0; smoke 49/49) "
 "+ S0.5 ORD delta consumed (e8f58ff1->85407b18: 3 rows ALL BigStream-lane [12:29 xq-AB 62/62 ZOOMQC receipt via bm-c 生成窗 / "
 "11:44 CEO MV 出片+歌名卡副标令 via bm-a / 13:0x CEO MV 剪辑转场特效升级令 O-20261017-1300 via bm-a], zero BigMoney action; "
 "DEC 1d4741e4 FALSE hold; unacked=0 both scans) + S6 43/43 rc=0 run THIS window (dead-window S6 debt; weekend honest: bars cutoff 10-16 current / "
 "regime ORANGE 6th day / dualrun ZERO-DRIFT streak 26 / fund_premium weekend no-op / papers marks current 10-16 [t35 openfill+prospect 22/22 drift=0+aggr/grid/cta idempotent no-ops] / "
 "token delta=0 / lane no-ops honest) + W261 seat MSG swept processed + S7 quad green (loop pin=5 no-op + watchdog registered [S4U flip = adjudicated default-principal standing face] + claws x2 OK) "
 "+ attrition 4 CLEAN + idle worked rc0 + orphan face=2 zero-kill (same legal resident faces as r1001/r1065 adjudication) | " + NOW)

st["next"] = ("r1067: (1) W261 FIVE-FACE FREEZE SPLICE (FIRST ACTION): editor canon-clone from results/_w260bmc_derive_editor.py per age() machine-needle law "
 "(builder canon _r1065bmc_build_editor.py if rebuild needed); prereg anchor @ freeze commit 03ab504d7; "
 "E63 w245_a AGING-TOKEN LAW: do NOT roll frozen aging-face tokens [r1065 healed the same builder defect in the W260 editor -- 2nd instance, do NOT repeat a 3rd]; "
 "kept/dropped split boundary per W261 prereg sec.3 mandate [W260 boundary 241->242 carried -- W261 must re-derive]; "
 "dual-sha16 pf 31d5dc07baee6620->next / n1 f40a82c450f32c5a->next; bands A 589_501..591_500 / B 591_501..591_700; "
 "count-asserted gates; needle preflight; 2nd freeze_edits invocation r609-abort law) "
 "-> splice land+push -> engine mtime-watch self-burn 12/12 -> sixgate PRE-FINALIZE (23rd consecutive target; triple identity n1==receipt==LANDED) "
 "-> finalize one-pass 996,335+2,200=998,535 / K=569,920+2,200=572,120 EXACT -> fivekeys vs W260 keys (key1 gap 0.001170 / key4 K-lift 0.0000 / key5 se_mu 0.000325 carried) "
 "-> sec.7/8 backfill placeholders=0 -> W262 seat publish (live re-derive on post-W261 universe; naive W262 A 591_501..593_500 expected REFUSED at registered W261 B 591_501..591_700 "
 "= ELEVENTH consecutive A-hop face per probe leg4; W262 freezer MUST re-derive, never transcribe r587); "
 "(2) Monday 10-19 15:30 bars window: full papers chain fires on the new bar (10-17/18 weekend no bars); "
 "(3) GPU lane = gen-only (LLM face retired per O-20261017-0953; GPU burns = interactive window lane per O-20261017-0131 sec.3; loop CPU-only)")
st["next_pointer"] = st["next"]
st["next_milestone"] = "W261 splice -> self-burn 12/12 -> sixgate 23rd -> finalize 998,535/K=572,120 EXACT -> W262 seat publish (r1067-r1069, 48h window)"

ART = ("research/PERPETUAL_N1_W261_PREREG.md (FREEZE 03ab504d7, out 49,660B sha256_16 2a2921f1bb741f31, sec.7/8 placeholders intact) "
 "+ results/_w261bmc_prereg_derive.py + results/_r1066bmc_floor_audit.txt (231/231 post-heal) + results/_r1066bmc_s6_log.txt (43/43 rc0)")
st["latest_artifact"] = ART
st["last_artifact"] = ART
st["recent_artifact"] = ART
st["head_sha"] = "W261 prereg FROZEN (03ab504d7); splice = r1067 first action (this window's closeout commit rides this window)"
st["sync"] = {"origin_tip": "03ab504d7 (W261 prereg freeze pushed first-try; closeout commit rides this window)", "ts": NOW}
st["prod_lanes"] = ("CPU=engine W261 prereg FROZEN (splice = r1067 first action) ; GPU=gen-only lane "
 "(LLM face retired per O-20261017-0953; GPU burns = interactive window lane per O-20261017-0131 sec.3; loop CPU-only)")
st["full_load_selfproof"] = {"占用一行": ("CPU=engine lane W261 prereg FROZEN (splice = r1067 first action) ; "
 "GPU=gen-only lane (LLM retired per O-20261017-0953, free VRAM ~1.5GiB; GPU burns = interactive window lane per O-20261017-0131 sec.3; loop CPU-only)")}
st["verdict"] = ("green: r1066 = 56th-gen absorb continuation -- dead-window W261 prereg derive estate machine-verified (frozen tpl byte-identical @0f33f9abc + "
 "floor audit 231/231 post-heal + needle probe rc0 + banned ADMIT + smoke 49/49) and W261 PREREG FREEZE landed origin 03ab504d7 pushed first-try "
 "(A 589_501..591_500 TENTH A-hop / B 591_501..591_700 ELEVENTH above-own-A) + ORD 3-row consumed (all BigStream-lane zero BigMoney action, "
 "watermark advanced read-back full-equality) + S6 43/43 rc0 run this window + attrition 4 CLEAN + orphan face=2 zero-kill")
st["idle_rounds"] = 0
st["agenda_starved"] = False

did = ("r1066 (56th-gen absorb continuation window): (1) S0-1 anchor bm-c + round-zero probe py_faces=7 orphans=2 (孤儿面=2) zero-kill "
 "(same legal resident faces as r1001/r1065 adjudication: resident services/polling-legs, probe false-positive face standing); S0 fetch 0/0 (HEAD==origin d647cd295 at open); "
 "(2) S0.5 dual-delta: ORD e8f58ff1->85407b18 TRUE consumed THIS window (3 rows ALL BigStream-lane: 12:29 xq-AB 正档 62/62+ZOOMQC receipt [via bm-c 生成窗] / "
 "11:44 CEO MV 出片+歌名卡副标令 [via bm-a] / 13:0x CEO MV 剪辑转场特效升级令 O-20261017-1300 [via bm-a] -- zero BigMoney execution owed; "
 "DEC 1d4741e4 FALSE hold; unacked=0; d19 update --advance read-back full-string equality OK); "
 "(3) S1 smoke 49/49; "
 "(4) PRODUCT = W261 PREREG FREEZE landed origin 03ab504d7 pushed first-try: dead-window derive estate (frozen-face extract byte-identical 47,643B sha256_16 87a4c206a35e0584 @ 0f33f9abc + "
 "derive script ALL GATES PASS with 5 disclosed needle heals + needle probe/counts + floor audit + W260 keys machine-read) machine-verified THIS window BEFORE landing "
 "(banned_direction_gate ADMIT rc0 + needle probe rc0 rerun [first run died on GBK \\u2212 print = known pit-encoding face, zero data loss] + floor audit re-run 231/231 post-heal "
 "[the on-disk mismatches=1 txt was the PRE-heal stale-receipt face; stale-receipt absorb law appended to CODELY.md] + probe receipt re-read ADMIT + smoke 49/49); "
 "out 49,660B sha256_16 2a2921f1bb741f31; bands A 589_501..591_500 TENTH consecutive A-hop [naive 589_301..591_300 refused at registered W260 B 589_301..589_500] / "
 "B 591_501..591_700 ELEVENTH consecutive above-own-A [own-A reservation: naive 589_501..589_700 lands inside own-wave A window]; freeze stamp 2026-10-17 r1066; "
 "RAM face honest update ~11GB free + LLM face retired per O-20261017-0953; W262+ projection leg4 in seat receipt [naive A 591_501..593_500 CLEAN pre-W261, refused once registered]; "
 "(5) S6 43-leg chain run THIS window (dead-window S6 debt, driver Tools/_r1066bmc_s6.py canon clone of r1063, log results/_r1066bmc_s6_log.txt): 43/43 rc=0 "
 "(dualrun ZERO-DRIFT streak 26 / compute_audit rc0 / py_wm probe rc0 red=false / update_daily 0 new rows cutoff 10-16 weekend honest / regime ORANGE 6th day / "
 "market_clock CALL-2026-10-16 ORANGE_COOL / fund_premium weekend no-op / papers marks current 10-16 [t35 openfill + prospect 22/22 drift=0 + promotion 0/22 eligible honest + "
 "aggr/grid/cta idempotent no-ops] / ceo_live_usage LIVE-2026-10-17 ORANGE cap 50% / token delta=0 / lane no-ops honest); "
 "(6) W261 seat MSG-20261017-1225-bmc-w261-seat.md swept to processed (seat consumed by this freeze); "
 "(7) S7 quad green (loop pin=5 no-op next 13:25 + watchdog registered [S4U XML flip access-denied = adjudicated default-principal standing face] + precommit claw + prepush claw installed) "
 "+ attrition 4 CLEAN (healed notes as-is) + idle worked rc0 (idle_rounds->0) + orphan face=2; counter 1066->1067")
st["did"] = did

json.dump(st, io.open(sp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print("state written: round_no", st["round_no"], "; watermark faces preserved:",
      st.get("last_orders_sha"), st.get("last_decisions_sha"))

# ---------- heartbeat ----------
hp = r"fleet\machines\bm-c.json"
hb = json.load(io.open(hp, encoding="utf-8"))
hb["machine_id"] = "bm-c"
hb["clock_read"] = NOW
hb["ts"] = NOW
hb["last_seen"] = NOW
hb["now_active"] = NOW
hb["activity_now"] = NOW
hb["last_round"] = ROUND
hb["last_round_at"] = NOW
hb["last_round_closed"] = NOW
hb["last_round_label"] = ROUND
hb["current_task"] = st["current_task"]
hb["current_task_at"] = NOW
hb["current_task_ts"] = EPOCH
hb["last_action"] = st["last_action"]
hb["last_action_at"] = NOW
hb["last_round_summary"] = st["last_round_summary"]
hb["last_round_summary_at"] = NOW
hb["did"] = did
hb["verdict"] = st["verdict"]
hb["note"] = ("r1066: 56th-gen absorb continuation -- W261 PREREG FREEZE landed 03ab504d7 first-try "
 "(dead-window derive estate machine-verified: frozen tpl byte-identical + floor audit 231/231 + needle probe rc0 + banned ADMIT + smoke 49/49); "
 "W261 five-face splice = r1067 FIRST ACTION (E63 w245_a aging-token law: do NOT roll frozen aging tokens)")
hb["next"] = st["next"]
hb["next_pointer"] = st["next"]
hb["next_milestone"] = st["next_milestone"]
hb["latest_artifact"] = ART
hb["last_artifact"] = ART
hb["recent_artifact"] = ART
hb["prod_lanes"] = st["prod_lanes"]
hb["full_load_selfproof"] = st["full_load_selfproof"]
hb["round_no"] = NEXT_ROUND_NO
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["heartbeat_epoch_utc"] = EPOCH
hb["heartbeat_epoch_utc_type"] = "int (assert)"
hb["sync"] = st["sync"]
hb["head_sha"] = st["head_sha"]
hb["orders_ack_receipt"] = ("r1066: ORD 3-row consumed (12:29 xq-AB 62/62 ZOOMQC receipt + 11:44 CEO MV 出片令 + 13:0x CEO MV 转场特效令 O-20261017-1300, "
 "all BigStream-lane zero BigMoney action); DEC 1d4741e4 hold; watermarks ord e8f58ff1->85407b18 advanced read-back full-equality; unacked=0 both scans")
hb["orders_ack_ts"] = NOW
hb["last_orders_read_note"] = ("r1066: ORD e8f58ff1->85407b18 consumed THIS window (3 rows all BigStream-lane: own 生成窗 xq-AB receipt + two bm-a MV-lane CEO orders; zero BigMoney execution)")
hb["last_decisions_read_note"] = "r1066: DEC delta FALSE hold (raw-blob sha256 1d4741e4 pinned probe, zero rows owed)"
hb["last_orders_read_at"] = NOW
hb["last_decisions_read_at"] = NOW
hb["last_orders_seen"] = NOW
hb["last_decisions_seen"] = NOW

json.dump(hb, io.open(hp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat written; epoch int read-back OK:", chk["heartbeat_epoch_utc"])

# ---------- canonical round report (ROOT per r1007 freeze pointer) ----------
rp = r"round_reports-bm-c.md"
pre_lines = len(io.open(rp, encoding="utf-8", errors="replace").read().splitlines())
verdict_line = ("watermark verdict=" + ("红" if red else "绿") +
                " (red=" + str(red) + " healthy / satengine ALIVE rc0 / engine-queue never-dry W261 prereg FROZEN 03ab504d7 / jobs 0 / seat-inbox swept)")
row = (NOW + " | " + ROUND + " | bm-c | " + verdict_line + " | " + NOW + " | " + ROUND + " | " + did + " | " + NOW + "\n")
assert row.count("\n") == 1
io.open(rp, "a", encoding="utf-8", newline="").write(row)
lines = io.open(rp, encoding="utf-8", errors="replace").read().splitlines()
assert len(lines) == pre_lines + 1, "report line count must be +1"
print("report appended; canonical lines:", len(lines), "| last row head:", lines[-1][:120])
