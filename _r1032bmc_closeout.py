# -*- coding: utf-8 -*-
# _r1032bmc_closeout.py -- r1032 closeout: report row + state + heartbeat + watermark advance (absorb window 33rd)
import json, time, datetime, sys

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
ORD_SHA = "4f5727aaea89b9f8a0844a764afe0749bc07e1f7"
DEC_SHA = "ab3f0cc9f4cb9bbb1f23c5e5a98bd5bed540a272b0b111bb481120ea7e0ba8fd"
CPU, RAM, GPU = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])

try:
    it = json.load(open("results/idle_trigger.bm-c.json", encoding="utf-8"))
    IDLE_ROUNDS = int(it.get("idle_rounds", 0))
    AGENDA = bool(it.get("agenda_starved", False))
except Exception:
    IDLE_ROUNDS, AGENDA = 0, False

DID = ("r1032 bm-c (33rd absorb instance): (1) S0-1 anchor bm-c + round-zero probe py_faces=7 orphans=1 zero-kill "
       "+ S0 stash-bridge 6 shared regenerable faces (push rc verified + top-stash identity matched before drop + quoted 'stash@{0}'; "
       "watermark_red.json face = untracked-at-HEAD, merge-created, daemon live-wins) + ff-merge f50979df3 (bm-a r1019 W247 prereg derive 4c403cb16 + bm-b r984 estate); "
       "(2) ABSORB dead r1032-predecessor (17:07-17:45): its S0.5 probe 17:09:44 advanced ORD cafcf953->e522828c tail-face + "
       "S6 43/43 rc0 17:36-17:39 + jayredo precheck script built + jayredo_v4_r1032.py runner ignited 17:34:37 (pid 70040) + "
       "closeout-style heartbeat/idle/orders_ack writes 17:45:02, died pre-commit; estate machine-verified BEFORE landing "
       "(S6 log 43x [rc=0] + precheck run this window VERDICT GO + runner alive progress fresh 17:54:14); S6 absorbed NOT rerun per same-round law; "
       "(3) S0.5 ORD consumed through 4f5727aa (predecessor e522828c tail-face rows re-judged zero-double-count): rows 16:5x O-1655 MV-playbook "
       "+ 17:1x O-1647 Top1-workflow-v2 + 17:2x O-1720 W5/W6 research + 17:2x O-1725 KF-haixuan/precision-ladder + 17:4x O-1745 tonal-fingerprint-law "
       "all bm-a-domain zero bm-c action; 17:1x @bm-c Jay verdict r1026 = P0 ACTIONABLE; 17:41 O-1741 POOL-0015~0019 bm-c cards: "
       "星晴 T1 gated (PROMPT-GATE-星晴 verdict absent, full-tree zero-hit) + 表演三件套 10-16/17/18 nights + 画质链 填隙 = conditions-not-met honest no-claim; "
       "DEC ab3f0cc9 hold; unacked=0; (4) S1 smoke 49/49; (5) P0 POOL-0014 EXECUTED (claim-and-start same-round law): "
       "precheck GO (RESHAKE6 E01c/SIL2/SING1+C01/B01/D01 + I2V11 + lint zero-negatives + frame-map ALL PRESENT) + "
       "runner self-chain absorbed zero double-ignite: Phase A KF reshake 24/24 ok (haixuan v1.1 4 seeds/slot 9600-9623) + "
       "BOARD JAY-REDO-RESHAKE6-BOARD-r1032.jpg 548KB + receipt 17KB landed bmc/ 17:54:16 + phases C/D/E self-chained "
       "(atomic-push + poke bm-a director re-review + 11 i2v INT8 768P 5s skip-if-exists INT3 eyelid-half-lower + D03b eye-light-preserving director prescriptions "
       "+ push + orders receipt + poke bm-a assembly; ~10min/clip ETA ~20:0x); (6) S3: satengine ALIVE + wm red=pool-batch-runnable-idle-low-cpu "
       "WAIVED-named (4 W20 SCREEN shards RAM-gate 2.4pct<4GB park-honest, autofill night-window standing, O-1612 GM waiver) + "
       "W247 bm-a chain in-flight (prereg landed, splice/burn/finalize pending) -> W248 waits-upstream ARMED verify-not-rescan + "
       "jobs 0 + inbox 0 + idle green_idle=false RAM-gate honest; (7) S6 absorbed 43/43 rc0: bars 10-15 sina-lag 4th window "
       "(cutoff 10-14, tencent upstream_has_newer_bar 10-15 fallback event disclosed, papers debt=0 waits-source) + dualrun + compute_audit + "
       "collectors + REPORT-2026-10-15 + LIVE-2026-10-15 (ORANGE cap 50%) + token delta=0; (8) S7 quad green + attrition CLEAN; counter 1032->1033")

REPORT_ROW = (NOW + " | r1032 | bm-c | r1032 (33rd absorb): (1) S0-1 anchor + round-zero probe py_faces=7 orphans=1 zero-kill + "
    "S0 stash-bridge 6 shared regenerable faces (rc-verified + identity-matched drop) + ff-merge f50979df3 (bm-a r1019 W247 prereg + bm-b r984 estate); "
    "(2) ABSORB dead r1032-predecessor (17:07-17:45: S0.5 probe ORD->e522828c + S6 43/43 rc0 + precheck built + runner ignited 17:34 + "
    "closeout-style writes 17:45, died pre-commit) -- estate machine-verified before landing (S6 log 43x rc=0 + precheck GO + runner pid 70040 fresh 17:54:14), "
    "S6 absorbed NOT rerun per same-round law; (3) S0.5 ORD consumed through 4f5727aa: bm-a-domain rows O-1655/O-1647/O-1720/O-1725/O-1745 zero bm-c action + "
    "**17:1x @bm-c Jay verdict r1026 = P0 ACTIONABLE** + 17:41 O-1741 POOL-0015~0019 bm-c cards (星晴 T1 gated PROMPT-GATE verdict absent 全树零命中 / "
    "表演三件套 10-16 nights / 画质链 填隙 = no-claim honest) / DEC ab3f0cc9 hold / unacked=0; (4) S1 smoke 49/49; (5) P0 POOL-0014 EXECUTED same-round: "
    "precheck GO (RESHAKE6+I2V11+lint+frame-map ALL PRESENT) + runner self-chain absorbed zero double-ignite: KF reshake 24/24 ok (海选制 v1.1 4 seeds/slot) + "
    "BOARD JAY-REDO-RESHAKE6-BOARD-r1032.jpg + receipt landed bmc/ 17:54:16 + i2v-11 self-chained (INT8 768P 5s, INT3/D03b director prescriptions, ETA ~20:0x); "
    "(6) S3: satengine ALIVE + wm red=pool-batch-runnable-idle-low-cpu WAIVED-named (W20 4 shards RAM-gate park-honest, autofill night-window, O-1612 GM waiver) + "
    "W247 bm-a in-flight -> W248 waits-upstream ARMED (verify-not-rescan) + jobs 0 + inbox 0; (7) S6 absorbed 43/43 rc0: bars 10-15 sina-lag 4th window "
    "(cutoff 10-14, tencent newer-bar disclosed, papers debt=0 waits-source) + REPORT-2026-10-15 + LIVE-2026-10-15 (ORANGE 50%) + token 0; "
    "(8) S7 quad green + attrition CLEAN + counter 1032->1033 | 证据: ff f50979df3 + stash drop 2740e223 + smoke 49/49 + precheck GO + runner progress 17:54:14 + "
    "S6 log 43x rc=0 + ORD 4f5727aa readback + epoch int readback | 当前活: P0 jayredo i2v-11 runner watch (burning) | "
    "最近实物: JAY-REDO-RESHAKE6-BOARD-r1032.jpg (24 格海选板·548KB) + jayredo_reshake6_r1032_receipt.json（17:54·bmc/·runner 自链上链）| "
    "下个里程碑: jayredo 17 件齐->bm-a 复检/装配（今晚 ~20:0x）+ bars 10-15 sina 落即 papers 全链 | "
    "watermark verdict=red: pool-batch-runnable-idle-low-cpu WAIVED-named (W20 RAM-gate autofill night-window O-1612) | "
    "本地未达 origin commit 数=closeout push 骑本窗（下轮开窗 fetch-verify） | "
    "下轮指针: r1033 = jayredo runner harvest watch (i2v-11 完成包+push/poke 回执核验+拼板) + W247 finalize watch -> W248 prereg derive 首动作 + "
    "bars 10-15 recheck + 星晴 T1 候 PROMPT-GATE verdict 签发 + 表演三件套 10-16 夜窗准备")

PROD_LANES = ("CPU=W20 SCREEN 4 shards claim-ready lane-pinned bm-c (RAM gate 2.4pct<4GB park-honest; autofill burns on night-window RAM free) -> screen-finalize next ; "
    "GPU=MV V4 jayredo P0 BURNING (runner pid 70040: KF reshake 24/24 + board landed bmc/ + 11 i2v INT8 768P in-flight -> bmc/i2v/jayredo/ -> bm-a re-review/assembly) "
    "+ ComfyUI resident + album serve ; N1=W247 bm-a in-flight (prereg 4c403cb16 landed, splice/burn/finalize theirs per seat-first) -> W248 bm-c waits-upstream ARMED ; "
    "U256 w001/w003 = RAM gate deferred ; MEMORY-GATE=HQ-MemoryBudgetGate 4h cycle (bm-c leg closed r1027)")

ARTIFACT = ("r1032: JAY-REDO-RESHAKE6-BOARD-r1032.jpg (24 格海选板 548KB) + jayredo_reshake6_r1032_receipt.json + 24 reshake PNGs kf_r1032/ (runner self-chained, landed bmc/) "
    "+ jayredo_v4_r1032.py runner alive pid 70040 + watermark advance 4f5727aa + precheck GO + S6 absorbed 43/43 (dead-predecessor estate landed this commit)")

NEXT_PTR = ("r1033: (1) jayredo runner harvest watch: 11 i2v INT8 768P 完成包 + board/push/poke 回执核验 + 全 17 件齐拼板; (2) W247 finalize watch (bm-a chain) -> W248 prereg derive = THIS machine first action on finalize landing (waits-upstream law); (3) bars 10-15 recheck (sina 510300 calendar governs; if landed -> papers full chain); (4) 星晴 T1 POOL-0015 候 PROMPT-GATE-星晴 verdict 签发后点火 (Jay P0 完成即升最高); (5) 表演三件套夜试跑 = 10-16/17/18 夜窗 (tomorrow first); (6) 画质链免费档试跑 = 填隙 after P0; (7) W20 SCREEN autofill night-window; (8) U256 w001/w003 RAM gate deferred")

VERDICT = ("green: r1032 absorb window 33rd (dead predecessor estate landed: S6 43/43 + precheck + runner ignition) + ORD consumed through 4f5727aa "
    "(P0 Jay verdict r1026 executed same-round: KF reshake 24/24 + board landed + i2v-11 self-chained burning) + POOL-0015~0017 cards honest no-claim (conditions not met) + "
    "smoke 49/49 + S6 absorbed 43/43 rc0 (bars 10-15 sina-lag 4th window, papers debt=0) + S7 quad green + W248 waits-upstream ARMED + "
    "W20 4 shards RAM-gated park-honest (autofill night-window)")

SELFPROOF = {
    "占用一行": PROD_LANES,
    "当前活": "r1032 closeout (P0 jayredo runner ignited + i2v-11 watch + ORD 7-row consumption + S6 absorbed)",
    "最近实物": "JAY-REDO-RESHAKE6-BOARD-r1032.jpg + jayredo_reshake6_r1032_receipt.json（17:54·bmc/·runner 自链上链）+ 24 reshake PNGs + watermark 4f5727aa（本窗 commit）",
    "下个交付物": "jayredo 11 i2v INT8 768P 完成包（ETA ~20:0x）-> bm-a 装配站 V4 重装；bars 10-15 sina 落即 papers 全链；W248 prereg derive（W247 finalize 落即发）",
    "队列水位": "池 ready=4（全 W20 screen·lane bm-c·RAM 门 park-honest）·N1 W247 bm-a 在飞·W248 waits-upstream·U256 候 RAM 门·P2/P3 空·jobs 0",
}

# ---- 1. round report row (canonical ROOT path per r750 law) ----
with open("round_reports-bm-c.md", "a", encoding="utf-8") as f:
    f.write(REPORT_ROW + "\n")

# ---- 2. state ----
st = json.load(open("state-bm-c.json", encoding="utf-8"))
st["round_no"] = 1033
st["last_round"] = "r1032"
st["last_round_label"] = "r1032"
for k in ("last_round_at", "last_seen", "last_seen_at", "last_ts", "clock_read", "ts", "updated", "updated_at",
          "current_task_at", "last_round_summary_at", "last_round_closed", "last_action_at", "now_active",
          "activity_now", "last_orders_seen", "last_orders_read_at", "last_decisions_read_at", "last_decisions_seen"):
    st[k] = NOW
st["heartbeat_epoch_utc"] = EPOCH
st["current_task"] = "r1032 closeout: P0 jayredo runner watch (i2v-11 burning) + ORD 7-row consumption + S6 absorbed 43/43"
st["last_orders_sha"] = ORD_SHA
st["last_orders_sha_note"] = ("r1032: ORD delta consumed through 4f5727aa (7 rows: O-1655/O-1647/O-1720/O-1725/O-1745 bm-a-domain zero-action + "
    "17:1x @bm-c Jay verdict r1026 P0 executed + 17:41 O-1741 POOL cards honest no-claim; dead-predecessor tail-face e522828c re-judged zero-double-count)")
st["last_decisions_sha"] = DEC_SHA
st["d19_watermark_guard"]["round_ref"] = 1033
st["d19_watermark_guard"]["ts"] = NOW
st["did"] = DID
st["verdict"] = VERDICT
st["note"] = ("r1032: absorb window 33rd (dead predecessor: S6+precheck+runner landed) | ORD 4f5727aa (P0 Jay verdict executed) | "
    "bars 10-15 sina-lag 4th window | W20 4 shards RAM-gated | W248 waits-upstream W247 bm-a in-flight | jayredo i2v-11 burning ETA ~20:0x")
st["last_round_summary"] = "r1032: 33rd absorb (predecessor estate + P0 jayredo KF 24/24+board landed + i2v-11 self-chained) + ORD 7-row consumption + S6 absorbed 43/43 + S7 quad green"
st["last_action"] = "r1032 closeout (P0 jayredo runner ignited+watch + ORD consumption + estate landed)"
st["last_artifact"] = ARTIFACT
st["latest_artifact"] = ARTIFACT
st["recent_artifact"] = ARTIFACT
st["next"] = NEXT_PTR
st["next_pointer"] = NEXT_PTR
st["next_milestone"] = "r1033+: jayredo 17 件齐->bm-a 装配站 V4 重装 (今晚 ~20:0x) + bars 10-15 papers 全链 on sina landing + W248 prereg derive on W247 finalize + 星晴 T1 候 PROMPT-GATE verdict"
st["prod_lanes"] = PROD_LANES
st["full_load_selfproof"] = SELFPROOF
st["idle_rounds"] = IDLE_ROUNDS
st["agenda_starved"] = AGENDA
st["free_ram_gb"] = RAM
st["ram_free_gb"] = RAM
st["idle_ram_gb"] = RAM
st["cpu_pct"] = CPU
st["cpu_util_pct"] = CPU
st["gpu_free_mb"] = GPU
st["gpu_free_vram_mb"] = GPU
st["verify"] = ("receipts: smoke 49/49 + S6 43/43 rc0 absorbed (dead-window faces, log 43x [rc=0]) + precheck GO (RESHAKE6/I2V11/lint/frame-map) + "
    "runner progress 24/24 ok + ORD watermark 4f5727aa readback + DEC ab3f0cc9 hold + epoch int readback + attrition CLEAN + quad green")
st["r1032_absorb_note"] = ("r1032 absorb note: dead r1032-predecessor (17:07-17:45) ran: S0.5 probe 17:09:44 (advanced ORD cafcf953->e522828c, "
    "state watermark write uncommitted at death) + second probe 17:30:26 (facts file, ORD e522828c->347edf39 delta found, died before consumption) + "
    "S6 43-leg chain 17:36-17:39 rc0 (driver Tools/_r1032bmc_s6.py + log, faces on disk) + jayredo precheck script built + "
    "jayredo_v4_r1032.py runner ignited 17:34:37 pid 70040 (KF reshake through 17:54:14) + closeout-style heartbeat/idle/orders_ack/sentinel writes 17:45:02; "
    "died pre-commit with zero own commits. This session (per bm-c absorb precedent lineage r894..r1031, 33rd instance) machine-verified the estate "
    "BEFORE landing (S6 log 43x rc=0 + precheck rerun GO + runner liveness + probe facts), consumed the ORD rows the predecessor left unconsumed "
    "(347edf39->4f5727aa with e522828c tail-face re-judged, zero double-count: P0 execution absent in predecessor), and closed out; executed as r1032 "
    "(per counter), advanced counter 1032->1033 so next session = r1033")
st["r1032_closeout_note"] = ("r1032: 33rd absorb window (dead predecessor estate landed + P0 jayredo executed) + ORD 7-row consumption "
    "(P0 ACTIONABLE executed same-round per CEO-ticket law) + S6 absorbed 43/43 (bars sina-lag 4th window) + S7 quad green | " + NOW)
with open("state-bm-c.json", "w", encoding="utf-8") as f:
    json.dump(st, f, indent=1, ensure_ascii=False)

# ---- 3. heartbeat ----
hb = json.load(open("fleet/machines/bm-c.json", encoding="utf-8"))
hb["round_no"] = 1033
hb["round_no_label"] = "r1032"
hb["last_round"] = "r1032"
for k in ("last_seen", "last_seen_at", "clock_read", "ts", "updated", "updated_at", "last_round_at",
          "last_round_ts", "last_round_summary_at", "last_round_closed", "last_action_at", "current_task_at"):
    hb[k] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["cpu_pct"] = CPU
hb["cpu_util_pct"] = CPU
hb["free_ram_gb"] = RAM
hb["ram_free_gb"] = RAM
hb["idle_ram_gb"] = RAM
hb["gpu_free_mb"] = GPU
hb["gpu_free_vram_mb"] = GPU
for k in ("gpu_idle_vram_mb", "gpu_idle_mb", "gpu_vram_free_mb"):
    hb[k] = GPU
hb["current_task"] = st["current_task"]
hb["did"] = DID
hb["verdict"] = VERDICT
hb["note"] = st["note"]
hb["last_round_summary"] = st["last_round_summary"]
hb["last_action"] = st["last_action"]
hb["last_artifact"] = ARTIFACT
hb["latest_artifact"] = ARTIFACT
hb["recent_artifact"] = ARTIFACT
hb["next"] = NEXT_PTR
hb["next_pointer"] = NEXT_PTR
hb["next_milestone"] = st["next_milestone"]
hb["prod_lanes"] = PROD_LANES
hb["full_load_selfproof"] = SELFPROOF
hb["idle_rounds"] = IDLE_ROUNDS
hb["agenda_starved"] = AGENDA
hb["last_orders_sha"] = ORD_SHA
hb["last_orders_at"] = NOW
hb["last_orders_read_at"] = NOW
hb["last_orders_seen"] = NOW
hb["last_decisions_sha"] = DEC_SHA
hb["last_decisions_read_at"] = NOW
hb["last_decisions_at"] = NOW
hb["last_decisions_seen"] = NOW
hb["verify"] = st["verify"]
hb["activity_now"] = "%s | r1032 | bm-c: closeout (P0 jayredo ignited+watch + absorb + consumption) | counter 1032->1033 (r1032 exec)" % NOW
hb["now_active"] = hb["activity_now"]
hb["sync"] = {"origin_tip": "closeout commit+push rides this window", "ts": NOW, "ahead_behind": "0/0 pre-closeout"}
with open("fleet/machines/bm-c.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, indent=1, ensure_ascii=False)

# ---- 4. readback verifications ----
st2 = json.load(open("state-bm-c.json", encoding="utf-8"))
hb2 = json.load(open("fleet/machines/bm-c.json", encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert st2["last_orders_sha"] == ORD_SHA, "ORD watermark readback"
assert st2["last_decisions_sha"] == DEC_SHA, "DEC hold readback"
assert st2["round_no"] == 1033 and st2["last_round"] == "r1032", "counter readback"
rep = open("round_reports-bm-c.md", encoding="utf-8").read()
assert REPORT_ROW[:60] in rep, "report row readback"
assert "r1032" in hb2["did"][:400], "heartbeat did readback"
print("CLOSEOUT-OK %s | epoch=%d(int) | ORD=%s | DEC hold | counter->1033 | report-row landed | idle_rounds=%d agenda_starved=%s"
      % (NOW, hb2["heartbeat_epoch_utc"], ORD_SHA[:8], IDLE_ROUNDS, AGENDA))
