# -*- coding: utf-8 -*-
"""r1065 bm-c closeout: state + heartbeat + canonical round-report line.
Single-file read-modify-write per shared-file law (python, json.load->json.dump).
"""
import json, time, io, datetime
if True:
    import sys
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
ROUND = "r1065"
NEXT_ROUND_NO = 1066

# --- watermark red face read (verdict line) ---
try:
    wr = json.load(io.open(r"results\watermark_red.json", encoding="utf-8"))
    red = wr.get("red")
except Exception as e:
    red = None
    print("watermark_red read err:", e)

# ---------- state ----------
sp = r"state-bm-c.json"
st = json.load(io.open(sp, encoding="utf-8"))
assert st["round_no"] == 1065, f"state round_no {st['round_no']} != 1065 (open face drift)"
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
st["current_task"] = "r1065 closeout (55th-gen absorb continuation: W260 cycle complete + W261 seat published cf23c4553)"
st["current_task_at"] = NOW
st["last_action"] = "r1065 closeout (55th-gen absorb continuation + W260 cycle complete + W261 seat published; counter 1065->1066)"
st["last_action_at"] = NOW
st["last_round_summary"] = "r1065: 55th-gen absorb continuation (W260 cycle COMPLETE: fivekeys 6/6 + sec78 backfill + W261 seat) + dual-delta consumed (ORD 1-row V5 receipt byte-verified / DEC 5-row committee zero-action) + quad green"
st["last_round_summary_at"] = NOW

st["r1065_absorb_note"] = ("r1065 absorb note: dead-window chain (three windows, all died pre-closeout, state counter frozen at 1065) executed the W260 chain body: "
 "window A (09:27-10:09) authored frozen-face extract + needle probe/counts + derive script, died pre-run (absorbed by window B per its commit message); "
 "window B landed W260 PREREG FREEZE 0f33f9abc (~10:2x; 1 disclosed gate-heal: line-591 prior-label expect 3->0 W259-lineage mirror; derive ALL GATES PASS vmap 61+floors 221+post-legs 6+MUST 129+MUST_NOT 175+8 blocks; banned ADMIT rc0; out 47,643B sha256_16 87a4c206a35e0584; freeze stamp 2026-10-17 r1065 10:2x) "
 "and ran the S6 43-leg chain 10:37:24-10:41:45 all rc=0 (log results/_r1065bmc_s6_log.txt: dualrun streak 25 / audit FLAG pool_starvation+supply_floor answered-by-chain / py_wm insufficient_history / bars cutoff 10-16 weekend / papers marks current / token delta=-170), died pre-closeout; "
 "window C landed the five-face freeze splice e8a9d5d67 AND pushed (E63 13th-gen 1 disclosed needle heal: editor OUTPUT-GATE w245_a 0!=1 = builder wrongly rolled frozen aging-face token w244_a +1 AGAIN [r1064 healed same defect in W259 editor] -> healed back to w244_a 12 per 5-gen frozen-verbatim canon W255..W259; 2nd freeze_edits invocation correctly r609-aborted; DEBT HEALED: n1_w259_results.json missed by r1064 closeout landed there; dual-sha16 pf bfd877ee61d6b456->31d5dc07baee6620 / n1 57a139af18df580d->f40a82c450f32c5a; bands A 587_301..589_300 / B 589_301..589_500; parity 118 rows split boundary MOVES 241->242; seed_admit FREE x2 + banned ADMIT rc0 re-run at freeze) "
 "+ engine mtime-watch self-burn 12/12 (ledger appends 63ef15c4f 12:00:47 + 9598cf5cb 12:05:29 batched 6+6 self-commit) + sixgate PRE-FINALIZE ALL PASS (22nd consecutive, results/_r1065bmc_w260_sixgate.json: gate-1 n1 TRIPLE identity f40a82c450f32c5a worktree==receipt post==LANDED @ e8a9d5d67 + banned ADMIT + pf/n1 selftests + shards 12/12 + seed_admit FREE verbatim base=587301 span=2000 / base=589301 span=200 + W259 boundary kept + W259 finalize product present) "
 "+ finalize one-pass 994,135+2,200=996,335 / K=567,720+2,200=569,920 EXACT (n1_w260_results.json 12:10:37: merged mu -0.0927307 / sigma 0.2450393 / W260-only mu -0.0915605 / se_mu 0.000325 / K-lift 0.0 / A p95 0.3292), died pre-closeout. "
 "This session (fired 12:15, per bm-c absorb precedent lineage r894..r1064, 55th-gen) machine-verified the estate BEFORE continuing (sixgate json triple identity + finalize ledger identity EXACT + HEAD==origin 0/0 + prereg worktree==committed blob @ 0f33f9abc anchors in splice commit message) and completed the cycle THIS window: fivekeys + sec.7/8 backfill + W261 seat publish + dual-delta consumption + closeout")

st["r1065_closeout_note"] = ("r1065: 55th-gen absorb continuation (dead-window W260 chain estate verified) + W260 CYCLE COMPLETE "
 "(sixgate 22nd consecutive PRE-FINALIZE + finalize one-pass 996,335/K=569,920 EXACT landed by dead windows; THIS window: fivekeys 6/6 ALL PASS "
 "[key1 gap 0.001170 tightened / key1b 4.5e-06 / key2 sigma rel +0.00075% / key3 A p95 +0.0058 in-band / key4 K-lift 0.0 held-flat-at-zero / key5 se_mu 0.000325 held-flat] "
 "+ sec.7/8 backfilled placeholders=0) + W261 SEAT published origin cf23c4553 (probe _w261bmc_20261017_probe.py authored+run live THIS window ADMIT: "
 "A 589_501..591_500 TENTH consecutive A-hop [1-hop trace: naive 589_301..591_300 refused at registered W260 B 589_301..589_500] / "
 "B 591_501..591_700 ELEVENTH consecutive above-own-A [own-A reservation 1-hop: naive 589_501..589_700 lands inside own-wave A window]; "
 "seed_admit FREE base=589501 span=2000 / base=591501 span=200; origin vacancy four-check; zero W262/W263 skip-claims) "
 "+ S0.5 dual-delta TRUE consumed (ORD 6aae4d9c->e8f58ff1: 1 row = 12:1x @bm-c V5 4-shot re-burn receipt row [O-20261017-1020 lineage], delivery faces byte-verified on group origin 4/4 [D01 698,288 / C04 1,351,687 / E01c 743,837 / INT5 556,579 B], zero additional action; "
 "DEC 7f12de36->1d4741e4: 5 rows D-20261017-04..07 committee governance [receipt-batch/BigStream PT-01/MiniGame CODELY/bm-b E1], all other-division zero bm-c action; watermarks advanced read-back full-equality) "
 "+ S6 43/43 absorbed (dead-window 10:37:24-10:41:45 rc0 same-round law; bars 10-16 cutoff current weekend honest; regime ORANGE 6th day; dualrun streak 25; audit FLAG answered-by-chain [W261 seat]) "
 "+ smoke 49/49 + satengine ALIVE rc0 + attrition 4 CLEAN + idle worked rc0 (idle_rounds->0) + loop pin=5 no-op + watchdog registered (S4U flip = adjudicated default-principal face) + claws x2 OK + orphan face=2 zero-kill + unacked=0 | " + NOW)

st["next"] = ("r1066: (1) W261 PREREG DERIVE (FIRST ACTION per seat-first law; seat origin cf23c4553 MSG-20261017-1225-bmc-w261-seat.md; "
 "derive script canon-clone from results/_w260bmc_prereg_derive.py @ committed W260 lineage [prereg 0f33f9abc + splice e8a9d5d67 + finalize 996,335/K=569,920 machine-carried anchors]; "
 "needle-probe preflight; bands A 589_501..591_500 / B 591_501..591_700 per probe receipt results/_w261bmc_20261017_probe_receipt.json live-walk ADMIT [never transcribe r587]; "
 "freeze window stamp 2026-10-17; count-asserted gates; sec.5 keys = W260 finalize actuals machine-read [merged mu -0.09273073 / sigma 0.24503935 / W260-only -0.09156055 / A p95 0.3292 / line_merged 1.195 / se_mu 0.000325 / K-lift 0.0]) "
 "-> five-face freeze splice (editor canon-clone from _w260bmc_derive_editor.py; prereg anchor @ freeze commit; dual-sha16 pf 31d5dc07baee6620->next / n1 f40a82c450f32c5a->next; kept/dropped split boundary per W261 prereg sec.3 mandate [W260 boundary 241->242 carried -- W261 must re-derive, E63 w245_a aging-token law: do NOT roll frozen aging-face tokens]) "
 "-> engine self-burn 12/12 (mtime-watch) -> sixgate PRE-FINALIZE (23rd consecutive target; triple identity n1==receipt==LANDED) -> finalize one-pass 996,335+2,200=998,535 / K=569,920+2,200=572,120 EXACT "
 "-> fivekeys vs W260 keys (key1 gap 0.001170 / key4 K-lift 0.0000 / key5 se_mu 0.000325 carried) -> sec.7/8 backfill placeholders=0 -> W262 seat publish "
 "(live re-derive on post-W261 universe; naive W262 A 591_501..593_500 expected REFUSED at registered W261 B 591_501..591_700 = ELEVENTH consecutive A-hop face per probe leg4; W262 freezer MUST re-derive, never transcribe); "
 "(2) Monday 10-19 15:30 bars window: full papers chain fires on the new bar (10-17/18 weekend no bars); (3) GPU lane = llm fill-gap 27b resident (GEN state yields per C-20261016-03 dual-mode law)")
st["next_pointer"] = st["next"]
st["next_milestone"] = "W261 prereg derive -> splice -> self-burn -> sixgate 23rd -> finalize 998,535/K=572,120 EXACT -> W262 seat publish (r1066-r1068, 48h window)"

ART = ("research/PERPETUAL_N1_W260_PREREG.md (sec.7/8 backfilled placeholders=0) + results/perpetual_faces/n1_w260_results.json (finalize 996,335/K=569,920) "
 "+ results/_r1065bmc_w260_fivekeys.json (6/6 ALL PASS) + fleet/inbox/MSG-20261017-1225-bmc-w261-seat.md (W261 seat origin cf23c4553) + results/_w261bmc_20261017_probe_receipt.json")
st["latest_artifact"] = ART
st["last_artifact"] = ART
st["recent_artifact"] = ART
st["head_sha"] = "W260 prereg frozen + spliced + finalized; W261 seat published (this window's closeout commit rides this window)"
st["sync"] = {"origin_tip": "cf23c4553 (W261 seat pushed first-try; closeout commit rides this window)", "ts": NOW}
st["prod_lanes"] = ("CPU=engine W261 seat published (prereg derive = r1066 first action) ; GPU=llm fill-gap mode 27b resident "
 "(C-20261016-03 dual-mode; GPU burns = interactive window lane per O-20261017-0131 sec.3; loop CPU-only)")
st["full_load_selfproof"] = {"占用一行": ("CPU=engine lane W261 seat published (prereg derive = r1066 first action) ; "
 "GPU=llm fill-gap mode 27b resident (C-20261016-03 dual-mode, free ~1.5GiB; GPU burns = interactive window lane per O-20261017-0131 sec.3; loop CPU-only)")}
st["verdict"] = ("green: r1065 = 55th-gen absorb continuation -- W260 CYCLE COMPLETE (dead-window estate verified: prereg 0f33f9abc + splice e8a9d5d67 + "
 "engine self-burn 12/12 appends 63ef15c4f+9598cf5cb + sixgate 22nd consecutive PRE-FINALIZE + finalize one-pass 996,335/K=569,920 EXACT) + "
 "THIS window: fivekeys 6/6 + sec.7/8 backfill placeholders=0 + W261 SEAT published origin cf23c4553 (A 589_501..591_500 TENTH A-hop / B 591_501..591_700 ELEVENTH above-own-A) + "
 "ORD 1-row consumed (V5 4-shot receipt byte-verified 4/4) + DEC 5-row consumed (committee zero-action) + S6 43/43 absorbed + smoke 49/49 + attrition CLEAN + orphan face=2 zero-kill")
st["idle_rounds"] = 0
st["agenda_starved"] = False

did = ("r1065 (55th-gen absorb continuation window): (1) S0-1 anchor bm-c + round-zero probe py_faces=8 orphans=2 (孤儿面=2) zero-kill; S0 estate inspection at open: dead-window chain "
 "(three windows, prereg-freeze window B + splice window C + sixgate/finalize window, state counter frozen 1065) had ALREADY landed the W260 chain body on origin "
 "(prereg 0f33f9abc + S6 43/43 10:37-10:41 + splice e8a9d5d67 + engine self-burn 12/12 appends 63ef15c4f+9598cf5cb + sixgate PRE-FINALIZE ALL PASS 22nd consecutive + "
 "finalize one-pass 996,335/K=569,920 EXACT); THIS window machine-verified the estate (sixgate json triple identity f40a82c450f32c5a + finalize ledger identity EXACT + HEAD==origin 0/0) "
 "and COMPLETED the cycle: fivekeys 6/6 ALL PASS (results/_r1065bmc_w260_fivekeys.py+json THIS window: key1 gap 0.001170 in-band / key1b 4.5e-06 / key2 sigma rel +0.00075% / "
 "key3 A p95 +0.0058 in-band / key4 K-lift 0.0 held-flat-at-zero / key5 se_mu 0.000325 held-flat <= W259 key) + sec.7/8 backfill placeholders=0 (research/PERPETUAL_N1_W260_PREREG.md, W259 r1064 precedent law) "
 "+ W261 SEAT published origin cf23c4553 pushed first-try (probe _w261bmc_20261017_probe.py canon-clone from _w260bmc_20261017_probe.py authored+run live THIS window: ADMIT "
 "A 589_501..591_500 hops=1 [TENTH consecutive A-hop, staircase: naive 589_301..591_300 refused at registered W260 B 589_301..589_500] / B 591_501..591_700 hops=1 "
 "[ELEVENTH consecutive above-own-A, own-A reservation: naive 589_501..589_700 lands inside own-wave A window]; seed_admit FREE base=589501 span=2000 / base=591501 span=200; "
 "origin vacancy four-check [no W261 seat/row/WAVE_CONFIGS/prereg on origin]; zero W262/W263 skip-claims; chain-relation W259->W260 994,135->996,335 / K 567,720->569,920 both +2,200 EXACT; "
 "W262+ projection recorded leg4 [naive A 591_501..593_500 clean pre-W261, refused at registered W261 B once registered = ELEVENTH hop expected]) "
 "+ S0.5 dual-delta TRUE consumed with watermarks advanced read-back (ORD 6aae4d9c->e8f58ff1: 1 row = 12:1x @bm-c V5 4-shot re-burn receipt row, delivery faces byte-verified on group origin 4/4 "
 "[cph4/.../bmc/i2v/v5redo/: D01_carver_words_v5.mp4 698,288B / C04_words_alive_v5.mp4 1,351,687B / E01c_first_line_v5.mp4 743,837B / INT5_head_bow_v5.mp4 556,579B], zero additional bm-c action; "
 "DEC 7f12de36->1d4741e4: 5 rows D-20261017-04/05/06/07 + batch header = committee governance other-division [BigStream PT-01 receipt / MiniGame CODELY E1 / bm-b E1 POOL-0020], "
 "bigmoney mentions = read-only facts [尾读零新行 / bm-b lane], zero bm-c action; unacked=0) "
 "+ S6 43/43 absorbed per same-round law (dead-window 10:37:24-10:41:45 rc0: dualrun ZERO-DRIFT streak 25 / compute_audit FLAG pool_starvation+supply_floor answered-by-chain [W261 seat] / "
 "py_wm insufficient_history fresh / bars cutoff 10-16 weekend honest / regime ORANGE 6th day [hs300<MA200 + crash10d -6.2% + breadth 0.83] / papers marks current 10-16 / token delta=-170) "
 "+ smoke 49/49 + satengine ALIVE rc0 + watermark red face read + attrition 4 CLEAN + idle worked rc0 + quad green (loop pin=5 no-op + watchdog registered [S4U flip = adjudicated default-principal standing face] + claws x2 OK) "
 "+ r1065 d19 row-extraction evidence results/_r1065bmc_d19_rows.md; counter 1065->1066")
st["did"] = did

json.dump(st, io.open(sp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print("state written: round_no", st["round_no"], "epoch-typed watermark faces preserved")

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
hb["note"] = ("r1065: 55th-gen absorb continuation -- W260 CYCLE COMPLETE (fivekeys 6/6 + sec78 + W261 seat cf23c4553 published THIS window; "
 "dead-window chain landed prereg/splice/burn/sixgate/finalize estate verified); splice->W261 prereg derive = r1066 FIRST ACTION")
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
hb["orders_ack_receipt"] = ("r1065: ORD 1-row consumed (12:1x @bm-c V5 4-shot re-burn receipt row, delivery byte-verified 4/4 on group origin, zero action) + "
 "DEC 5-row consumed (D-20261017-04..07 committee governance other-division, zero bm-c action); watermarks ord e8f58ff1 / dec 1d4741e4 advanced read-back full-equality; unacked=0 both scans")
hb["orders_ack_ts"] = NOW
hb["last_orders_read_note"] = ("r1065: ORD 6aae4d9c->e8f58ff1 consumed THIS window (1 row = own-dead-window V5 4-shot receipt row; verified not re-executed -- delivery landed 12:1x by dead window, faces byte-verified)")
hb["last_decisions_read_note"] = "r1065: DEC 7f12de36->1d4741e4 consumed THIS window (5 rows committee 12:00 常务轮 batch, all other-division, zero bm-c action)"
hb["last_orders_read_at"] = NOW
hb["last_decisions_read_at"] = NOW
hb["last_orders_seen"] = NOW
hb["last_decisions_seen"] = NOW

json.dump(hb, io.open(hp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat written; epoch int read-back OK:", chk["heartbeat_epoch_utc"])

# ---------- canonical round report ----------
rp = r"round_reports-bm-c.md"
old = io.open(rp, encoding="utf-8", errors="strict").read()
verdict_line = ("watermark verdict=" + ("红" if red else "绿") +
                " (red=" + str(red) + " healthy / satengine ALIVE rc0 / engine-queue never-dry W261 seat published cf23c4553 / jobs 0 / inbox 0-self-seat)")
row = (NOW + " | " + ROUND + " | bm-c | " + verdict_line + " | " + NOW + " | " + ROUND + " | " + did + " | " + NOW + "\n")
assert row.count("\n") == 1
io.open(rp, "a", encoding="utf-8", newline="").write(row)
lines = io.open(rp, encoding="utf-8", errors="replace").read().splitlines()
print("report appended; canonical lines:", len(lines), "| last row head:", lines[-1][:120])
