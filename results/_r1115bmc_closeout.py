# -*- coding: utf-8 -*-
# r1115 bm-c closeout: state-bm-c.json + fleet/machines/bm-c.json mirror + round_reports-bm-c.md row.
# Fresh-read-modify-write (multi-writer file law r1106); EOL preserved; epoch int asserted (R170/R178);
# clock_read ISO-T asserted (R262); d19-written watermark faces preserved verbatim (fresh load).
import io, os, json, time, subprocess, datetime, psutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = os.path.join(REPO, "state-bm-c.json")
HB = os.path.join(REPO, "fleet", "machines", "bm-c.json")
RR = os.path.join(REPO, "round_reports-bm-c.md")
GIT = "C:/Program Files/Git/cmd/git.exe"

def load_raw(path):
    b = open(path, "rb").read()
    return b, (b"\r\n" in b)

def dump(path, obj, crlf):
    txt = json.dumps(obj, ensure_ascii=False, indent=1)
    if crlf:
        txt = txt.replace("\n", "\r\n")
    open(path, "wb").write(txt.encode("utf-8"))

now_dt = datetime.datetime.now().astimezone()
NOW = now_dt.isoformat(timespec="seconds")
EPOCH = int(time.time())
head_sha = subprocess.run([GIT, "rev-parse", "HEAD"], capture_output=True, cwd=REPO).stdout.decode().strip()
ram = round(psutil.virtual_memory().available / 1024**3, 1)
gpu = subprocess.run(["nvidia-smi", "--query-gpu=memory.free,memory.used,utilization.gpu", "--format=csv,noheader,nounits"],
                     capture_output=True).stdout.decode().strip().split(", ")
gfree, gused, gutil = int(gpu[0]), int(gpu[1]), float(gpu[2])
codely_n = sum(1 for p in psutil.process_iter(["name"]) if p.info["name"] and "codely" in (p.info["name"] or "").lower())

DID = ("r1115: W278 PREREG PREP LANDED per r1096/r1098/r1103 honest-split window-budget law -- "
 "(1) S0-1 anchor bm-c + round-zero probe py_faces=4 orphans=0 resident=1 zero-kill + S0 fetch 0/0 clean open (HEAD==origin efc4a1c1bb, dirty=1 regenerable daemon face watermark_red) + opening D-19 dual FALSE (ord 57d1f5de / dec 8706acd8 hold, unacked=0, files=105 inside ack-230); "
 "(2) S1 smoke 49/49; (3) S3 satengine ALIVE rc0 via Tools entry (r1102 pit law; queue waits-upstream = W278 prereg not yet frozen) + wm red=false py_low_board_clear legal; "
 "(4) P0 PRODUCT = W278 prereg derive PREP: frozen face results/_w278bmc_w277_frozen_face.txt byte-verified 23,593B sha256_16 45ee1de94c7d36fd @ e0bc4a0ddd PRE-backfill (python subprocess raw bytes r1012 law; freeze blob e5d12b12da03a799a88bd980cf8566b2b1eff5ba; HEAD post-backfill twin 78571eb16e279d7b6f316b04aef0960fac37283f 27,848B disclosed NOT used per r1049/r1052) "
 "+ MEASURED floors results/_w278bmc_prep_facts.json via results/_r1115bmc_prep.py (r1077 measured-counts law: wave rolls W277=44/W276=62/W275=4/W274=4; stamps 07:4x=4/07:2x=2/08:1x=1 positive floors matching the r1113-gen roll chain exactly + 09:5x/10:3x zero-floors; ALL W278 new faces measured 0 zero-floor audit PASS) "
 "+ EXTENDED ANCHOR FACTS block (r1103 facts-gather fold: prereg freeze 09:02:01 / splice 9e53371814 09:57:42 SPLICE_T=09:5x / engine batches 0df07c846b 09:58:29 + 644b4f8459 10:03:34 / finalize estate 0502c722ac 10:35:34 / seat b187aa6214 10:35:34 MSG-20261019-102x-bmc-w278-seat; fivekeys W277 full-precision merged mu -0.09277043683725218 (8dp -0.09277044) / sigma 0.24508693698115214 (8dp 0.24508694) / se_mu@607,320 0.000314 / W277-only -0.0888985 (8dp -0.08889850) / A p95 0.3095 / K-lift +0.0000 / n_eff_held 1,031,535 / line_pre_w277 1.197 / line_merged@607,320 1.197 / key1 gap 0.0039 @4dp / ledger 1,033,735 EXACT / K 607,320; receipt bands verbatim A 626901..628900 / B 628901..629100 + hop chains + W279p A 628_901..630_900 / B 629_101..629_300; projections K 609,520 / ledger 1,035,935 / n_eff_held 1,033,735) for the r1116 builder window zero-transcription "
 "+ builder gen-diff evidence results/_r1115bmc_builder_gen_diff.txt (r1110->r1113 builder 21-chunk diff = the one-gen roll pattern map, committed as authoring evidence); "
 "(5) same-window arithmetic-slip heal disclosed: prep facts first cut carried ledger_projection 1,035,735 (base= n_eff_held 1,031,535 slip) -- caught in-window PRE-consumption, healed to machine-computed fk277.ledger_identity.total+2,200 = 1,035,935 + n_eff_held_projection 1,033,735 face added, prep re-run clean; "
 "(6) S7 tail D-19 re-probe caught MID-ROUND ORD DELTA TRUE = 10:53 CEO jman 年轻档 LoRA 续训令 dispatched @bm-c -> consumed + claimed same-round per CEO-ticket law: judgment receipt results/_r1115bmc_ord_judgment.json + watermark advanced 57d1f5de->0992a4ea via d19 update --advance (two-face r1090 law, read-back full-string equality OK, heartbeat mirrors synced 5, verify structural_ok=true probe_equality equal both) + v1 pipeline spec located cph4/fleet/mv0001-handover/outbound/krea2/jman-lora-training-spec-v1.md (GPU-lane standing P0, night-priority per ticket lane discipline, jman v1 照用零断供, dataset assembly = next GPU-lane window first step); "
 "(7) S6 light 10/10 rc0 (driver _r1115bmc_s6_light.py r1114 canon-clone, log results/_r1115bmc_s6_log.txt); "
 "(8) S7: attrition 4 files CLEAN (healed shrinks as-is) + quad green (IterationLoop present next fire 11:05 + LoopWatchdog present + precommit/prepush claws CR-normalized identical x2) + idle --worked rc0 idle_rounds=0 agenda_starved=false + orphan face=0")

VERIFY = ("W278 PREP receipts machine-verified: frozen face disk==blob byte-identity (23,593B, sha256_16 45ee1de94c7d36fd, freeze-commit e0bc4a0ddd blob sha1 e5d12b12da03a799a88bd980cf8566b2b1eff5ba, HEAD twin 78571eb16e279d7b6f316b04aef0960fac37283f 27,848B) + prep facts regenerated post-heal machine-read (k_projection_w278 609,520 / ledger_projection_w278 1,035,935 / n_eff_held_projection_w278 1,033,735 all machine-computed from fk277 json) + D-19 verify structural_ok=true probe_equality equal both faces (ord 0992a4ea / dec 8706acd8) + smoke 49/49 + S6 light 10/10 rc0 (log results/_r1115bmc_s6_log.txt: dualrun ZERO-DRIFT streak 51 [461] / audit FLAG pool_starvation+supply_floor structural answered-by-chain [W278 seat armed + PREP landed, supply legally chained to the r1116 derive+freeze] / py_wm py_low_board_clear legal idle whitelist [board clear, bandit 0, no runnable batch; N1 engine waits-upstream W278 prereg] / update_daily 0 rows cutoff 10-16 pre-15:30 Monday honest papers debt=0 / CALL-2026-10-16 ORANGE_COOL idempotent sleeves=4 activated=0 / b_layer all_pass / REPORT-2026-10-19 faces=5 token=1 / token delta=0 / L2 legs 0 today) + attrition 4 CLEAN + orphan face=0 + quad green (loop+watchdog present, claws x2 identical) + idle --worked rc0 + epoch int + clock_read ISO-T. DISCLOSED: (a) honest split = builder+derive deferred to r1116 FIRST ACTION per r1096 window-budget law with ALL facts pre-frozen (r1103->r1104 precedent pattern); (b) 10:53 CEO jman ticket: consumption+claim+spec-pointer landed this window (同轮认领+开动), dataset/training ignition = next GPU-lane window per ticket lane discipline (夜窗优先不打架白班正片); (c) prep first-cut arithmetic slip caught+healed in-window pre-consumption")

VERDICT = ("green r1115 PREP product window (W278 prereg derive PREP landed: frozen face byte-verified + measured floors + extended anchor facts zero-transcription; mid-round 10:53 CEO jman ticket consumed+claimed same-round; smoke 49/49; S6 light 10/10; loop CPU-only, GPU idle)")

NEXTP = ("r1116: (1) FIRST ACTION = W278 PREREG DERIVE one-window per r1104/r1110/r1113 precedent (builder E63 canon-clone _r1113bmc_build_w277_derive.py -> _r1115bmc_build_w278_derive.py one-gen roll + derive -> research/PERPETUAL_N1_W278_PREREG.md + banned_direction_gate ADMIT + content spot-check + CAS surgical freeze-push; ALL anchors machine-frozen results/_w278bmc_prep_facts.json w278_anchor_facts block zero-transcription; stamp rolls 07:4x->10:3x x4 / SPLICE_T 09:5x / seat-stamp 10:3x; r-window rolls OLD=r1113-gen NEW sides, NEW=r1113/r1114/r1115 family, self-window live-read stamp=r1116; sixgate 40th->41st consecutive; CLEAN-AT-BIRTH 9th->10th gen; K projection 609,520 / ledger 1,035,935 / n_eff_held 1,033,735; floors W277=44/W276=62 stamps 07:4x=4/07:2x=2/08:1x=1); (2) W278 five-face splice editor chain = post-freeze FIRST ACTION (canon _w277bmc_derive_editor.py E63 clone); (3) TODAY Monday 2026-10-19 15:30 bars window: full papers chain (live.paper enforce + t35_openfill + t24 x2 + aggr + alloc + grid + system_v1 + t35_export + scorecard, debt=0 cutoff 10-16); (4) GPU-lane standing P0 = jman young-era LoRA v2 (10:53 CEO ticket consumed+claimed r1115; spec cph4/fleet/mv0001-handover/outbound/krea2/jman-lora-training-spec-v1.md; dataset assembly young-era official imagery 2000-2003 first, night-priority, jman v1 照用零断供); (5) BigMoney automation-plan faces deadlines <=10-25/<=10-31; (6) RAM watch standing (loop CPU-only, GPU idle)")

OCCUPY = ("CPU=W278 PREREG PREP LANDED (frozen face + measured floors + anchor facts @ results/_w278bmc_prep_facts.json; builder+derive = r1116 FIRST ACTION); GPU=idle ~%dG free, loop CPU-only; short-video lane DISABLED standing per O-20261017-1741; GPU-lane standing P0 = jman young-era LoRA v2 (10:53 CEO ticket, night-priority)" % round(gfree / 1024.0, 1))
ARTIFACT = ("results/_w278bmc_prep_facts.json (W278 measured floors + extended anchor facts zero-transcription) + results/_w278bmc_w277_frozen_face.txt (23,593B sha16 45ee1de94c7d36fd @ e0bc4a0ddd) + results/_r1115bmc_ord_judgment.json (10:53 CEO ticket judgment) @ %s" % NOW)
MILESTONE = ("W278 prereg derive+freeze (r1116 FIRST ACTION); TODAY Monday 15:30 papers chain; jman v2 dataset assembly (GPU lane, night window); BM automation-plan <=10-25/<=10-31")
CURTASK = ("W278 PREREG PREP LANDED (frozen face + measured floors + anchor facts); builder+derive = r1116 FIRST ACTION; GPU-lane standing P0 = jman young-era LoRA v2 (10:53 CEO ticket consumed+claimed r1115)")
ACK_RCPT = ("r1115: opening scan dual FALSE (ord 57d1f5de / dec 8706acd8 hold, unacked=0, files=105 inside ack-230); S7 tail re-probe caught MID-ROUND ORD DELTA TRUE (10:53 CEO jman 年轻档 LoRA 续训令 dispatched @bm-c) -> consumed + claimed same-round per CEO-ticket law, watermark advanced 57d1f5de->0992a4ea (two-face r1090 law, read-back OK, mirrors synced 5, verify structural_ok=true); dec hold both scans")
ORD_NOTE = ("r1115: S7 tail re-probe caught ORD delta TRUE (mid-round 10:53 CEO jman-young-LoRA row @bm-c) -> consumed+claimed same-round per CEO-ticket law, d19 two-face advance 57d1f5de->0992a4ea read-back OK mirrors synced 5")
DEC_NOTE = "r1115: DEC delta FALSE at open+tail both (raw-blob sha256 8706acd8 hold; zero rows owed)"
CLOSENOTE = ("r1115: (1) clean continuation product window (state round_no=1115 at open per r1114 counter advance, executed r1115, advanced 1115->1116 so next=r1116); zero absorb owed (r1114-continuation closeout efc4a1c1bb landed clean 10:40:39, zero dead window between; census 2 codely = self + resident lane PID 3996); "
 "(2) S0-1 anchor bm-c + probe py_faces=4 orphans=0 zero-kill (resident ComfyUI listener legal) + S0 fetch 0/0 clean open; (3) S0.5 opening dual FALSE + S7 tail caught mid-round ORD 10:53 CEO jman ticket (consumed+claimed, judgment receipt + d19 two-face advance 57d1f5de->0992a4ea) + dec hold; unacked=0; (4) smoke 49/49; satengine ALIVE waits-upstream; "
 "(5) P0 PRODUCT = W278 PREREG PREP per honest-split law (frozen face byte-verified + measured floors + extended anchor facts + builder gen-diff evidence; arithmetic-slip healed in-window pre-consumption); derive builder+derive = r1116 FIRST ACTION; (6) S6 light 10/10 rc0; (7) attrition 4 CLEAN + quad green + idle --worked + orphan face=0; 5x HANDOVER duty discharged by the r1114-continuation catch-up stamp (next 5x = bm-c r1120)")

st_raw, st_crlf = load_raw(ST)
hb_raw, hb_crlf = load_raw(HB)
st = json.loads(st_raw.decode("utf-8"))
hb = json.loads(hb_raw.decode("utf-8"))

for obj in (st, hb):
    obj["round_no"] = 1116
    obj["round_no_label"] = "r1115 closeout -> counter 1116"
    obj["last_round"] = 1115
    obj["last_round_label"] = "r1115"
    obj["last_round_at"] = NOW
    obj["last_round_closed"] = 1115
    obj["last_round_closed_at"] = NOW
    obj["last_round_summary"] = "r1115: W278 PREREG PREP LANDED (honest split r1096/r1098/r1103 law: frozen face byte-verified 23,593B sha16 45ee1de94c7d36fd @ e0bc4a0ddd + measured floors _w278bmc_prep_facts.json + W278 anchor facts zero-transcription) + mid-round 10:53 CEO jman-young-LoRA ticket consumed+claimed; derive builder = r1116 FIRST ACTION"
    obj["last_round_summary_at"] = NOW
    obj["last_round_ts"] = NOW
    obj["activity_now"] = NOW
    obj["clock_read"] = NOW
    obj["current_task"] = CURTASK
    obj["current_task_at"] = NOW
    obj["current_task_ts"] = EPOCH
    obj["now_active"] = "W278 prereg PREP landed; builder+derive = r1116 first action; GPU lane P0 = jman young v2"
    obj["last_action"] = "W278 prereg derive PREP (frozen face + measured floors + anchor facts) + 10:53 CEO jman ticket consumed/claimed + S6 light 10/10 + closeout"
    obj["last_action_at"] = NOW
    obj["last_artifact"] = ARTIFACT
    obj["latest_artifact"] = ARTIFACT
    obj["recent_artifact"] = ARTIFACT
    obj["last_seen"] = NOW
    obj["last_seen_at"] = NOW
    obj["last_ts"] = NOW
    obj["updated"] = NOW
    obj["updated_at"] = NOW
    obj["ts"] = NOW
    obj["next"] = NEXTP
    obj["next_pointer"] = NEXTP
    obj["next_milestone"] = MILESTONE
    obj["did"] = DID
    obj["verify"] = VERIFY
    obj["verdict"] = VERDICT
    obj["note"] = "CPU=W278 PREREG PREP LANDED (r1116 first action = builder+derive); GPU=idle (loop CPU-only); GPU-lane P0 = jman young-era LoRA v2 (10:53 CEO ticket); short-video lane DISABLED standing per O-20261017-1741"
    obj["prod_lanes"] = "CPU=W278 PREREG PREP (facts machine-frozen; derive = r1116 first action); GPU=idle (loop CPU-only; jman v2 = GPU-lane standing P0 night-priority); short-video lane DISABLED standing per O-20261017-1741"
    obj["ram_critical_face"] = "none (loop CPU-only, GPU idle, %.1fGB free)" % ram
    obj["ram_free_gb"] = ram
    obj["free_ram_gb"] = ram
    obj["idle_ram_gb"] = ram
    obj["full_load_selfproof"] = {"占用一行": OCCUPY, "最近实物": ARTIFACT, "下个里程碑": MILESTONE}
    obj["heartbeat_epoch_utc"] = EPOCH
    obj["heartbeat_epoch_utc_type"] = "int (assert)"
    obj["idle_rounds"] = 0
    obj["agenda_starved"] = False
    obj["orphan_face"] = 0
    obj["orphan_faces"] = 0
    obj["codely_live_count"] = codely_n
    obj["health"] = "ok"
    obj["head_sha"] = head_sha
    obj["last_pulled_at"] = NOW
    obj["last_orders_at"] = "2026-10-19T10:53:00+08:00"
    obj["last_orders_read_at"] = NOW
    obj["last_orders_seen"] = NOW
    obj["last_orders_read_note"] = ORD_NOTE
    obj["last_decisions_read_at"] = NOW
    obj["last_decisions_seen"] = NOW
    obj["last_decisions_read_note"] = DEC_NOTE
    obj["orders_ack_receipt"] = ACK_RCPT
    obj["orders_ack_ts"] = NOW
    obj["sync"] = {"origin_tip": "efc4a1c1bb r1114-continuation closeout (pre-this-window face; r1115 push rides closeout)", "ts": NOW}
    # gpu faces (update only keys already present)
    for k, v in (("gpu_free_mib", gfree), ("gpu_used_mib", gused), ("gpu_mem_used_mib", gused),
                 ("gpu_used_vram_mib", gused), ("gpu_free_vram_mib", gfree), ("gpu_idle_mib", gfree),
                 ("gpu_idle_vram_mib", gfree), ("gpu_free_vram_mb", gfree), ("gpu_free_mb", gfree),
                 ("free_vram_mb", gfree), ("gpu_vram_free_mb", gfree), ("gpu_idle_vram_mb", gfree),
                 ("gpu_idle_mb", gfree), ("gpu_util_pct", gutil)):
        if k in obj:
            obj[k] = v
    if "gpu_free_vram_gb" in obj:
        obj["gpu_free_vram_gb"] = round(gfree / 1024.0, 2)

st["r1115_closeout_note"] = CLOSENOTE

dump(ST, st, st_crlf)
dump(HB, hb, hb_crlf)

# --- round report row (fresh-read-append-write, EOL preserved) ---
rr_bytes = open(RR, "rb").read()
rr_crlf = b"\r\n" in rr_bytes
NL = "\r\n" if rr_crlf else "\n"
row = ("| %s | r1115 | %s | %s | %s |" % (NOW, DID, VERIFY, NEXTP))
with open(RR, "ab") as f:
    if not rr_bytes.endswith(b"\n"):
        f.write(NL.encode("utf-8"))
    f.write(row.encode("utf-8") + NL.encode("utf-8"))

# --- assertions ---
chk = json.loads(open(ST, "rb").read().decode("utf-8"))
hbk = json.loads(open(HB, "rb").read().decode("utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read not ISO-T"
assert chk["round_no"] == 1116 and chk["last_round"] == 1115
assert chk["last_orders_sha"] == "0992a4ea9cc6d0e455ec8d004133124db035ecc0", "ord watermark clobbered: %r" % chk["last_orders_sha"]
assert chk["last_decisions_sha"] == "8706acd8a7b65441f23c9813f62a25fdecbd9da0df10994e5915b5742a40a3fd", "dec watermark clobbered"
assert hbk["round_no"] == 1116 and hbk["last_orders_sha"] == chk["last_orders_sha"], "heartbeat mirror divergence"
assert isinstance(hbk["heartbeat_epoch_utc"], int)
print("CLOSEOUT OK: round 1115 -> counter 1116 | epoch=%d int | clock_read=%s | ord wm=0992a4ea preserved | dec wm=8706acd8 preserved | ram=%.1fGB | gpu free=%dMiB util=%s%% | codely=%d | round-report row appended (crlf=%s)" % (
    EPOCH, NOW, ram, gfree, gutil, codely_n, rr_crlf))
