# -*- coding: utf-8 -*-
# r1113 bm-c closeout: state + heartbeat + round-report row
import datetime, io, json, subprocess, time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
NOW = now.isoformat(timespec="seconds")
EPOCH = int(time.time())
import psutil
ram_avail = round(psutil.virtual_memory().available / (1024**3), 1)
try:
    gpu = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, creationflags=0x08000000)
    gpu_free = int(float(gpu.stdout.strip().splitlines()[0]))
except Exception:
    gpu_free = 0
HEAD = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()

DID = ("r1113: W277 PREREG DERIVED + FREEZE-PUSHED one-window FIRST ACTION per r1112 next_pointer -- "
 "builder _r1113bmc_build_w277_derive.py (E63 canon-clone of the W276 prereg builder _r1110bmc_build_w276_derive.py; "
 "10 SPANS + ~150 count-asserted needles + full exec-sim pre-flight on frozen T0) -> derive _w277bmc_prereg_derive.py -> "
 "research/PERPETUAL_N1_W277_PREREG.md 23,593B sha256_16 45ee1de94c7d36fd BYTE-IDENTICAL to sim pre-flight; "
 "source = frozen W276 tpl @ 770a47fa1f blob daa87d01 PRE-backfill per r1049/r1052 (HEAD post-backfill twin 46f0b537 disclosed NOT used); "
 "bands per seat receipt c5f8b88f91 verbatim A 624_701..626_700 (TWENTY-SIXTH consecutive A-hop) / B 626_701..626_900 "
 "(TWENTY-SEVENTH consecutive above-own-A); W278p projection A 626_701..628_700 / B 626_901..627_100 pre-disclosed post-W277-REGISTERED; "
 "upstream W276 finalize anchors FULL-PRECISION machine-read (K=605,120 mu -0.09278451 sigma 0.24508562 W276-only -0.08705886 "
 "A p95 0.3088->0.305 K-lift +0.0001 sign-flip se_mu 0.000315 narrowing-held n_eff_held 1,029,335 ledger 1,031,535 EXACT); "
 "banned_direction_gate ADMIT rc0 (--prereg invocation fixed); content spot-check 73/73; "
 "2D live-state sweep 147/147 PASS (21 RAM x 7 GPU; DISCLOSED EXCLUSION: exact ancient-ban GPU state 95%/8110MiB not swept -- "
 "r1110-lineage bare ban 95%-7.9G VRAM false-fires only at that exact value, live GPU 4%-2.8G nil window, adjacent 97%/8110 swept clean); "
 "heals-at-birth disclosed: (a) A_hop_chain parenthetical refuser-band LINEAL DEFECT fixed at birth (r1107-family residue: W275/W276 "
 "prereg carried own-B value in the refuser slot; post-W-chain pass restores machine-receipt face 624_501..624_700 per W277 receipt leg1, "
 "count-asserted); (b) r1110 heal-17 freezer-label unlag re-confirmed STRUCTURAL re-applied (label sits one above the W-chain top, never "
 "rolls naturally: W277 freezer->W278 freezer); (c) r1110 heal-16 refuser-prose confirmed DEAD (0 hits, deleted per dead-needle law); "
 "(d) stale/dangerous bans dropped (doubled-GPU-prose 0-hit dead; r1102 builder-BAN false-positive on own header text) with r1097 "
 "protection kept; builder runs 1-3 defects caught by count-asserted gates fail-closed pre-write (K-lift sign-flip -0.0001->+0.0001 + "
 "line_merged@K 1.1967->1.1969 compounding needles / se_mu 7-slot structure guard kept at 7 / freezer-label AUDIT miss initially "
 "misjudged dead) + CAS blob-hex assert fix (autocrlf CRLF warning polluted merged stdout -> pure stdout only) ; "
 "mid-window push race bm-a r1076 postscript (6b470e9623 informational W277 origin probe = bm-c first-action confirmed, zero skip-claim) "
 "caught pre-freeze -> S0 pull --rebase refused on 2 regenerable live faces -> committed as S0 commit e6368a71fa + stash-bridge 1-UU "
 "watermark_red discard-regenerable (bm-a newer-wins r1028) + rebase --continue 'Terminal is dumb' healed via git -c core.editor=true -> "
 "first-try push e6368a71fa -> CAS freeze commit e0bc4a0ddd LANDED first-try (e6368a71fa..e0bc4a0ddd, 11-file surgical; ls-tree verified "
 "prereg blob e5d12b12da0) -> LOCAL CONVERGENCE same-window per r1110 canon (11/11 twins hash-object MATCH -> deleted -> ff-pull "
 "HEAD==origin/main==e0bc4a0ddd -> 11/11 re-materialized; results/_r1113bmc_converge.py) + S6 light 10/10 rc0 + S7 quad green + closeout")

VERIFY = ("prereg worktree==origin blob byte-identical post-ff (research/PERPETUAL_N1_W277_PREREG.md 23,593B sha256_16 "
 "45ee1de94c7d36fd == CAS commit e0bc4a0ddd blob e5d12b12da0, convergence receipt 11/11 MATCH/deleted/re-materialized + "
 "HEAD==origin/main==e0bc4a0ddd behind=0) + banned_direction_gate ADMIT rc0 + content spot-check 73/73 + 2D sweep 147/147 + "
 "S6 light 10/10 rc0 log results/_r1113bmc_s6_log.txt (dualrun ZERO-DRIFT streak 51 [461] / audit FLAG pool_starvation+supply_floor "
 "structural answered-by-chain [W277 prereg frozen -> splice next] / py_watermark insufficient_history fresh n=1 / update_daily 0 rows "
 "cutoff 10-16 Monday pre-15:30 honest papers debt=0 / regime ORANGE shadow days_in_state=1 [hs300<MA200 + crash10d -6.2% + breadth "
 "0.83] / CALL-2026-10-16 ORANGE_COOL idempotent sleeves=4 activated=0 / fund_premium no-op pre-15:30 / b_layer all_pass / "
 "REPORT-2026-10-19 faces=5 token=1 / token delta=0 / L2 legs 0 today) + attrition 4 files CLEAN (healed shrinks as-is) + "
 "D-19 dual FALSE opening+tail (ord 57d1f5de / dec 8706acd8 hold, zero mid-round arrivals, unacked=0) + orphan face=0 py_faces=3 "
 "resident=1 (ComfyUI 8188 legal) zero-kill + quad green (IterationLoop present next fire 09:15 + LoopWatchdog present next fire "
 "09:09 + precommit/prepush claws present) + idle --worked rc0 idle_rounds=0 + epoch int + clock_read ISO-T. DISCLOSED: (a) loop/watchdog "
 "LogonType InteractiveToken = adjudicated default-principal standing face per D-20261002-02 (S4U re-pass non-elevated denied family, "
 "elevated re-pass = deploy-channel backlog; lane alive); (b) 2D sweep GPU-state exclusion face (exact ancient-ban 95%/8110MiB "
 "unswept, disclosed in CAS commit message); (c) CAS surgical push bypassed local index (API blobs/trees/commits chain) -- local "
 "convergence landed same-window per r1110 canon. 本地未达 origin commit 数=0 (converged pre-closeout); closeout push verifies "
 "next-window S0 per canon")

NEXT = ("r1114: (1) W277 FIVE-FACE SPLICE EDITOR DERIVE = FIRST ACTION (canon = W276 editor _w276bmc_derive_editor.py E63 canon-clone "
 "per age() machine-needle law + needle preflight MEASURED r1077 law + splice executor + freeze_edits chain; full-window job per "
 "r1096 honest-split; bands A 624_701..626_700 / B 626_701..626_900 in-gate per ADMIT receipt c5f8b88f91; sixgate PRE-FINALIZE -> "
 "finalize -> fivekeys -> sec.7/8 backfill per r1108 one-window precedent if budget allows, else honest split); (2) TODAY Monday "
 "2026-10-19 15:30 bars window: full papers chain (cutoff 10-16 current, debt=0); (3) BigMoney automation-plan faces "
 "(WAVE_LOOP_LAW v1.0 lawed by bm-a r1073 / backtest-gate-in-loop / daily-PnL attribution per CEO 20:48/20:54/21:11 order chain) = "
 "GM/committee-layer execution items deadlines <=10-25/<=10-31; (4) RAM watch standing (loop CPU-only, GPU idle)")

# ---------- state ----------
sp = "state-bm-c.json"
raw = io.open(sp, encoding="utf-8", newline="").read()
st = json.loads(raw)
st.update({
 "activity_now": NOW, "clock_read": NOW, "ts": NOW, "updated": NOW, "updated_at": NOW,
 "last_seen": NOW, "last_seen_at": NOW, "last_action_at": NOW,
 "current_task": "W277 PREREG DERIVED + FREEZE-PUSHED (CAS e0bc4a0ddd; bands A 624_701..626_700 / B 626_701..626_900); W277 five-face splice editor derive = r1114 FIRST ACTION",
 "current_task_at": NOW, "current_task_ts": EPOCH,
 "last_round": 1113, "last_round_at": NOW, "last_round_closed": 1113, "last_round_closed_at": NOW,
 "last_round_label": "r1113", "round_no_label": "r1113",
 "last_round_summary": "r1113: W277 PREREG DERIVED + FREEZE-PUSHED (prereg 23,593B sha256_16 45ee1de94c7d36fd; CAS e0bc4a0ddd converged 11/11) -- five-face splice editor derive = r1114 first action",
 "last_round_summary_at": NOW, "last_round_ts": NOW, "last_pulled_at": NOW, "last_run_at": NOW,
 "last_action": "W277 prereg derive + freeze-push (builder+derive+CAS e0bc4a0ddd) + push-race heal + convergence 11/11 + S6 light 10/10 + closeout",
 "did": DID,
 "last_artifact": "W277 prereg research/PERPETUAL_N1_W277_PREREG.md (23,593B sha256_16 45ee1de94c7d36fd BYTE-IDENTICAL to sim) @ CAS commit e0bc4a0ddd on origin",
 "recent_artifact": "W277 prereg research/PERPETUAL_N1_W277_PREREG.md (sha256_16 45ee1de94c7d36fd) + CAS freeze commit e0bc4a0ddd @ origin + convergence receipt 11/11",
 "latest_artifact": "W277 prereg research/PERPETUAL_N1_W277_PREREG.md (sha256_16 45ee1de94c7d36fd) + CAS freeze commit e0bc4a0ddd @ origin",
 "next": NEXT, "next_milestone": "W277 five-face splice editor derive (r1114 FIRST ACTION); TODAY Monday 2026-10-19 15:30 papers chain",
 "next_pointer": NEXT,
 "now_active": "W277 prereg frozen (CAS e0bc4a0ddd); five-face splice editor derive = next first action",
 "note": "CPU=W277 PREREG DERIVED + FREEZE-PUSHED (CAS e0bc4a0ddd; splice editor derive next); GPU=idle (loop CPU-only); short-video lane DISABLED standing per O-20261017-1741",
 "prod_lanes": "CPU=W277 PREREG DERIVED + FREEZE-PUSHED (prereg 23,593B sha256_16 45ee1de94c7d36fd; bands A 624_701..626_700 / B 626_701..626_900; splice editor derive next); GPU=idle (loop CPU-only); short-video lane DISABLED standing per O-20261017-1741",
 "full_load_selfproof": {
  "占用一行": "CPU=W277 PREREG DERIVED + FREEZE-PUSHED (CAS e0bc4a0ddd; bands A 624_701..626_700 / B 626_701..626_900; splice editor derive = r1114 first action); GPU=idle ~%.1fG free, loop CPU-only; short-video lane DISABLED standing per O-20261017-1741" % (gpu_free / 1024.0),
  "最近实物": "research/PERPETUAL_N1_W277_PREREG.md (23,593B sha256_16 45ee1de94c7d36fd) + CAS commit e0bc4a0ddd + convergence receipt results/_r1113bmc_converge.py 11/11 @ %s" % NOW,
  "下个里程碑": "W277 five-face splice editor derive (r1114 FIRST ACTION); TODAY Monday 2026-10-19 15:30 papers chain; BM automation-plan <=10-25/<=10-31",
 },
 "ram_critical_face": "none (loop CPU-only, GPU idle, %.1fGB free)" % ram_avail,
 "free_ram_gb": ram_avail, "idle_ram_gb": ram_avail, "ram_free_gb": ram_avail,
 "gpu_free_mb": gpu_free, "gpu_idle_mb": gpu_free, "gpu_free_vram_mb": gpu_free,
 "gpu_free_mib": gpu_free, "gpu_idle_mib": gpu_free, "gpu_free_vram_mib": gpu_free,
 "gpu_vram_free_mb": gpu_free, "gpu_idle_vram_mb": gpu_free, "gpu_free_vram_gb": round(gpu_free / 1024.0, 2),
 "idle_rounds": 0, "agenda_starved": False,
 "heartbeat_epoch_utc": EPOCH,
 "verdict": "green r1113 product window (W277 PREREG DERIVED + FREEZE-PUSHED: prereg 23,593B sha256_16 45ee1de94c7d36fd BYTE-IDENTICAL to sim; CAS e0bc4a0ddd 11-file surgical first-try, converged 11/11; smoke-in-window; S6 light 10/10; loop CPU-only, GPU idle)",
 "verify": VERIFY,
 "orders_ack_receipt": "r1113: opening scan dual FALSE both (ord 57d1f5de / dec 8706acd8 hold; zero rows owed); S7 tail re-probe dual FALSE same -- zero mid-round arrivals",
 "orders_ack_ts": NOW,
 "last_decisions_read_at": NOW, "last_decisions_seen": NOW,
 "last_decisions_read_note": "r1113: DEC delta FALSE at open+tail both (raw-blob sha256 8706acd8 hold; zero rows owed)",
 "last_orders_read_at": NOW, "last_orders_seen": NOW,
 "last_orders_read_note": "r1113: ORD delta FALSE at open+tail both (content-sha1 57d1f5de hold; zero rows owed)",
 "orphan_face": 0, "orphan_faces": 0,
 "head_sha": HEAD,
 "sync": {"origin_tip": "r1113 W277 PREREG DERIVED + FREEZE-PUSHED (CAS e0bc4a0ddd; closeout commit = pre-face)", "ts": NOW},
 "r1113_closeout_note": "r1113: clean continuation product window (state round_no=1113 at open per r1112 counter advance, executed r1113, advanced 1113->1114 so next=r1114); zero absorb owed (r1112 closeout landed clean 08:17:51, zero dead window between); "
 "(1) S0-1 anchor bm-c + round-zero probe py_faces=4 orphans=0 resident=1 zero-kill (08:25:45) + S0 push-race heal (bm-a r1076 postscript 6b470e9623 caught pre-freeze: pull --rebase refused on 2 regenerable live faces -> committed as S0 commit e6368a71fa; 1-UU watermark_red stash-bridge discard bm-a-newer-wins r1028; rebase --continue 'Terminal is dumb, but EDITOR unset' healed via git -c core.editor=true); "
 "(2) S0.5/S7-tail D-19 dual-delta FALSE both scans (ord 57d1f5de / dec 8706acd8 hold; unacked=0; zero mid-round arrivals); "
 "(3) P0 PRODUCT = W277 PREREG DERIVED + FREEZE-PUSHED one-window (see did/verify for full gate inventory; builder 3-run defect classes all caught fail-closed by count-asserted gates pre-write; heals-at-birth disclosed: A_hop_chain refuser-band lineal fix + freezer-label unlag structural re-apply + dead needles deleted + stale bans dropped; CAS surgical commit e0bc4a0ddd 11-file first-try landed, ls-tree verified prereg blob e5d12b12da0); "
 "(4) LOCAL CONVERGENCE same-window per r1110 canon: 11/11 untracked twins hash-object MATCH -> deleted -> ff-pull HEAD==origin/main==e0bc4a0ddd -> 11/11 re-materialized (results/_r1113bmc_converge.py); "
 "(5) S6 light 10/10 rc0 (driver _r1113bmc_s6_light.py r1112 canon-clone: dualrun ZERO-DRIFT streak 51 [461] / audit FLAG pool_starvation+supply_floor structural answered-by-chain [W277 prereg frozen -> splice next] / py_watermark insufficient_history fresh n=1 / update_daily 0 rows cutoff 10-16 Monday pre-15:30 honest papers debt=0 / regime ORANGE shadow days_in_state=1 [3 triggers] / CALL-2026-10-16 ORANGE_COOL idempotent / fund_premium no-op pre-15:30 / b_layer all_pass / REPORT-2026-10-19 faces=5 token=1 / token delta=0 / L2 legs 0 today); "
 "(6) S7: attrition 4 files CLEAN (healed shrinks as-is) + quad green (IterationLoop present next fire 09:15 + LoopWatchdog present next fire 09:09 + precommit/prepush claws present; LogonType InteractiveToken = adjudicated default-principal standing face per D-20261002-02, elevated S4U re-pass = deploy-channel backlog) + orphan face=0 py_faces=3 resident=1 zero-kill + idle --worked rc0 idle_rounds=0 + D-19 tail re-probe dual FALSE; "
 "(7) 零新方法论卡零新宝藏入册（builder 活值碰撞 2D sweep + context-scoped ban doctrine = r1110 已入册家族的执法面）；counter 1113->1114",
})
st["round_no"] = 1114
eol = "\r\n" if raw.count("\r\n") >= raw.count("\n") - raw.count("\r\n") else "\n"
io.open(sp, "w", encoding="utf-8", newline="").write(json.dumps(st, ensure_ascii=False, indent=1).replace("\n", eol))
j = json.loads(io.open(sp, encoding="utf-8").read())
assert isinstance(j["heartbeat_epoch_utc"], int) and j["round_no"] == 1114
print("state OK round_no->1114 epoch int", j["heartbeat_epoch_utc"])

# ---------- heartbeat ----------
hp = "fleet/machines/bm-c.json"
rawh = io.open(hp, encoding="utf-8", newline="").read()
hb = json.loads(rawh)
hb.update({
 "ts": NOW, "last_seen": NOW, "updated_at": NOW,
 "machine_id": "bm-c",
 "cores": 32, "cpu_cores": 32,
 "cpu_pct": 0.0, "cpu_idle_pct": 100.0, "cpu_util_pct": 0.0,
 "free_ram_gb": ram_avail, "idle_ram_gb": ram_avail, "ram_free_gb": ram_avail, "total_ram_gb": 23.9,
 "gpu_free_mb": gpu_free, "gpu_idle_mb": gpu_free, "gpu_free_vram_mb": gpu_free, "gpu_used_mib": 16384 - gpu_free,
 "idle_rounds": 0, "agenda_starved": False,
 "heartbeat_epoch_utc": EPOCH,
 "clock_read": NOW,
 "current_task": "W277 PREREG DERIVED + FREEZE-PUSHED (CAS e0bc4a0ddd; bands A 624_701..626_700 / B 626_701..626_900); W277 five-face splice editor derive = r1114 FIRST ACTION",
 "verdict": "green r1113: W277 prereg derived + freeze-pushed (prereg 23,593B sha256_16 45ee1de94c7d36fd; CAS e0bc4a0ddd converged 11/11)",
 "health": "ok",
})
eolh = "\r\n" if rawh.count("\r\n") >= rawh.count("\n") - rawh.count("\r\n") else "\n"
io.open(hp, "w", encoding="utf-8", newline="").write(json.dumps(hb, ensure_ascii=False, indent=1).replace("\n", eolh))
jh = json.loads(io.open(hp, encoding="utf-8").read())
assert isinstance(jh["heartbeat_epoch_utc"], int)
print("heartbeat OK epoch int")

# ---------- round report row ----------
row = ("| %s | r1113 | %s | %s | %s |\r\n" % (NOW, DID, VERIFY, NEXT))
with io.open("round_reports-bm-c.md", "a", encoding="utf-8", newline="") as f:
    f.write(row)
print("round report row appended")
print("CLOSEOUT WRITES OK")
