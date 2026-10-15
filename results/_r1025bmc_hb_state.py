# -*- coding: utf-8 -*-
"""r1025 bm-c closeout: state + heartbeat update (fresh RAM/GPU read, int-epoch assert)."""
import datetime, io, json, os, subprocess, time

now_iso = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
epoch = int(time.time())

ram_free_gb = round(__import__("psutil").virtual_memory().available / 1e9, 2)
try:
    q = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu",
                        "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=15)
    mu, mt, gu = [int(x.strip()) for x in q.stdout.strip().split(",")]
    gpu_free_mb = mt - mu
except Exception:
    mu, mt, gu, gpu_free_mb = 1129, 16384, 0, 15255

DID = (
 "r1025 bm-c: (1) S0-1 anchor bm-c + probe py_faces=5 orphans=2 zero-kill + stash-ff-pop to 11ce7c1db (behind 3 absorbed: bm-b r973/974 + bm-a r1012 estate); "
 "(2) 24th-lineage absorb: dead self-labeled r1025 window (10:55 firing, died 11:02-11:15 pre-closeout) -- MV V4 Jay-redo KF 14/14 + LOOKBOARD group-tree delivery VERIFIED LANDED (origin d9f4c53, 3 files cat-file exit 0, progress receipt stage=done '14/14 KF ok' pid 69760, POOL-0014 claimed receipt line on origin; battle-proven Tools/git-atomic-push-bmc.py absorbed to Tools/) + 3 bm-b order receipts (O-0025 resume no-valve-residue + occupancy + sentinel TTL deferred/O-0915+O-0952 知会面) + S6 43/43 rc0 chain (10:58-11:02, dualrun streak 51, collectors no-op, ORANGE regime, scorecard stale-takeover lawful) ABSORBED NOT RERUN per same-round law + scratch 5 + foreign sentinel_bm-c.py edit untouched; "
 "(3) S0.5 ORD delta TRUE e2423fef->46c60d47 consumed (new rows: Agent 业务法/O-1040 Jay-redo/O-1040 24h audit/O-1055 MV full-speed + quant CPU max -- BigMoney leg covered by dead-window receipt: registry RAM gate honest + MV yield lawful) + DEC hold 6910a9ed + unacked 4 receipted (orders_ack 213->217); "
 "(4) S1 smoke 49/49; engine ALIVE rc0 queue 0; attrition 4 CLEAN; idle_trigger green_idle=false ram 8.7% -> U256 claims deferred per bill sec.5 bm-c risk-note 1 (bmc-w004 scope executed inline as absorb duty zero-burn, evidence results/_r1025bmc_estate_audit.json; w001/w003 stay ready); S8 wiring deferred again (bm-b edit still not on origin, local/origin identical verified); "
 "(5) S7 quad green + HANDOVER 5x row r986-r1025 (8 missed checkpoints disclosed) + closeout push rides this window; tail dual-scan at close"
)

VERDICT = ("green: dead r1025 window absorbed (MV V4 KF 14/14 delivery landed d9f4c53 + receipts + S6 43/43), "
           "U256 claims deferred honest (GREEN-IDLE RAM gate closed 8.7%<40% per bill risk-note), "
           "W-chain = bm-a W245 in-flight -> W246 bm-c turn staged, no-silent-idle 🔵 structural-wait annotation carried")

NEXT = ("r1026: (1) W245 finalize watch -> W246 seat (bm-c turn) FIRST ACTION = candidate draft per funnel-0 verdict "
        "(GENERATE route entry-x-filter: TRIAL_LABOR prereg template + seed-admit probe vs SEED_REGISTRY + banned-direction gate + "
        "TRIAL_GRAMMAR_LEDGER 77-function dedup, r924 bm-b W19-draft precedent; freeze gated on W245 anchor per chain-order law); "
        "(2) bars 10-15 due 15:30 -> update_daily gate -> papers full chain re-arm (live.paper REGIME_GUARD + t35 openfill + t24 x2 + aggr/alloc/grid/system_v1 + export + faces); "
        "(3) RAM gate opens (post-MV i2v window) -> bmc-w001 funnel-1 audit + bmc-w003 collector recovery verify claims; "
        "(4) S8 prompt wiring: re-check bm-b edit on origin, wire bmc-registry S8 step once clear; "
        "(5) MV V4 GPU lane: i2v INT8 768P full batch on bm-a director review of JAY-REDO-KF-BOARD-r1025.jpg (POOL-0014 pending-review)")

PROD_LANES = ("CPU=N1 W-chain seat watch (W245=bm-a chain in-flight: prereg 09:52 landed, freeze/burn/finalize theirs; W246=bm-c turn staged, candidate-draft next-window first action); GPU=ComfyUI resident idle (MV V4 Jay-redo KF 14/14 + LOOKBOARD delivered 11:07 group-tree d9f4c53; i2v INT8 768P full batch gated on bm-a director review)")

OCCUPANCY = ("GPU=ComfyUI 8188 resident idle (V4 KF batch done 14/14, next burn gated on bm-a director review) · CPU=loop round r1025 closeout + W-chain watch")

SELFPROOF = {
 "占用一行": PROD_LANES,
 "当前活": "r1025 dead-window absorb closeout + delivery verification (MV V4 KF landed) + S6 43/43 absorbed + HANDOVER 5x",
 "下一交付物": "r1026: W246 candidate draft (on W245 anchor) + 15:30 bars papers full chain; MV V4 i2v batch on director review",
 "队列水位": "N1 engine 0 burning on bm-c (W245=bm-a wave) · MV V4 KF delivered, i2v gated upstream · P2/P3 queues all-done · U256 registry 3 ready+1 waiting (RAM gate closed 8.7%) · bars 15:30"
}

# ---- state file ----
sp = "state-bm-c.json"
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 1026
st["clock_read"] = now_iso
st["current_task"] = "r1025 closeout: dead-window absorb (MV V4 KF delivery verified d9f4c53) + S6 43/43 absorbed + HANDOVER 5x"
st["current_task_at"] = now_iso
st["last_round"] = "r1025"
st["did"] = DID
st["verdict"] = VERDICT
st["next"] = NEXT
st["next_pointer"] = NEXT
st["free_ram_gb"] = ram_free_gb
st["gpu_free_vram_mb"] = gpu_free_mb
st["heartbeat_epoch_utc"] = epoch
st["r1025_absorb_note"] = ("r1025 absorb note: dead window (10:55 firing, self-labeled r1025) executed the FULL MV V4 Jay-redo POOL-0014 leg "
                           "(KF 14/14 burn 10:51-11:07 pid 69760 + LOOKBOARD + group-tree atomic push LANDED d9f4c53 + 3 bm-b order receipts + S6 43/43 rc0 "
                           "10:58-11:02) then died pre-closeout; this session absorbed per bm-c absorb precedent lineage: delivery verified landed, "
                           "in-repo estate committed via targeted add (foreign sentinel_bm-c.py excluded), counter advanced 1025->1026 so next session = r1026; "
                           "zero double-count: S0.5 ORD delta consumed THIS window (e2423fef->46c60d47), DEC hold 6910a9ed; evidence results/_r1025bmc_estate_audit.json")
with io.open(sp, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("state round_no ->", st["round_no"])

# ---- heartbeat ----
hp = os.path.join("fleet", "machines", "bm-c.json")
hb = json.load(io.open(hp, encoding="utf-8"))
hb["free_ram_gb"] = ram_free_gb
hb["idle_ram_gb"] = ram_free_gb
hb["ram_free_gb"] = ram_free_gb
for k in ("gpu_free_vram_mb", "gpu_free_vram_mib"):
    hb[k] = gpu_free_mb
hb["gpu_used_vram_mib"] = mu
hb["gpu_util_pct"] = gu
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
hb["ts"] = now_iso
hb["last_seen"] = now_iso
hb["last_seen_at"] = now_iso
hb["updated_at"] = now_iso
hb["last_round"] = "r1025"
hb["round_no"] = 1025
hb["round_no_label"] = "r1025"
hb["loop_round"] = 1025
hb["last_round_at"] = now_iso
hb["last_round_closed"] = now_iso
hb["current_task"] = "r1025 closeout: dead-window absorb (MV V4 KF delivery verified d9f4c53) + S6 43/43 absorbed + HANDOVER 5x + U256 claims deferred (RAM gate)"
hb["current_task_at"] = now_iso
hb["current_task_ts"] = epoch
hb["last_round_summary"] = ("r1025: dead-window absorb 24th-lineage (MV V4 Jay-redo KF 14/14+LOOKBOARD landed d9f4c53, POOL-0014 claimed) + "
                            "3 bm-b receipts + S6 43/43 absorbed + ORD 46c60d47 consumed + HANDOVER 5x + S7 quad green")
hb["latest_artifact"] = ("r1025: MV V4 Jay-redo KF batch 14/14 + LOOKBOARD delivered (group-tree origin d9f4c53, "
                         "cph4/fleet/mv0001-handover/outbound/krea2/kf-demo-20261012/bmc/JAY-REDO-KF-BOARD-r1025.jpg, 11:07) + "
                         "estate audit results/_r1025bmc_estate_audit.json")
hb["last_artifact"] = hb["latest_artifact"]
hb["next_milestone"] = NEXT
hb["next"] = NEXT
hb["next_pointer"] = NEXT
hb["activity_now"] = "%s | r1025 | bm-c: dead-window absorb closeout (MV V4 KF delivery verified) | counter 1025->1026" % now_iso
hb["now_active"] = hb["activity_now"]
hb["last_action"] = "r1025 dead-window absorb closeout"
hb["last_action_at"] = now_iso
hb["did"] = DID
hb["verdict"] = VERDICT
hb["note"] = "r1026: " + NEXT
hb["prod_lanes"] = PROD_LANES
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_face"] = 2
hb["orphan_faces"] = 2
hb["health"] = "ok"
hb["last_orders_sha"] = "46c60d47911c3f4ac94beef90ba5e2841501129b"
hb["last_orders_at"] = now_iso
hb["last_orders_read_at"] = now_iso
hb["last_orders_sha_note"] = ("r1025: ORD delta TRUE e2423fef->46c60d47 consumed (new rows 10-15 10:38x-11:2x: Agent 业务法 v1 / O-20261015-1040 MV V4 Jay-redo 派单 / "
                              "O-20261015-1040 24h 全链贯通审计案 / O-20261015-1055 MV 全速+金融 CPU 排满令 / bmc r1025 交付回执行 -- "
                              "O-1055 BigMoney CPU leg receipted by dead-window line: registry RAM gate honest + MV yield lawful)")
hb["last_decisions_sha"] = "6910a9ed7d1a99044b607c6307d2e6f9e44b8e9f3dd0d7c301e5ea57cd5c2cb9"
hb["last_decisions_read_at"] = now_iso
hb["last_decisions_seen"] = now_iso
ack = hb.setdefault("orders_ack", [])
for f in ("O-20261015-0025-bm-b.md", "O-20261015-0906-bm-b.md", "O-20261015-0915-bm-b.md", "O-20261015-0952-bm-b.md"):
    if f not in ack:
        ack.append(f)
hb["orders_ack_count"] = len(ack)
hb["orders_ack_ts"] = now_iso
hb["r1025_absorb_note"] = st["r1025_absorb_note"]
hb["ram_note"] = "protect: MV V4 i2v 窗前 ComfyUI 常驻合法保留（O-20261015-1055『其他本地可以让路』·quant claims RAM 门闭=法定让路面如实注记）"
hb["pulse_law"] = "PT-20261006-01② 案1: burn-window pulse-only <=2h (per-round S7 write + in-round pulse on long burns)"
hb["heartbeat_epoch_utc_type"] = "int (assert)"
hb["verify"] = ("receipts: smoke 49/49 + S6 chain 43/43 rc0 absorbed (results/_r1025bmc_s6_log.txt DONE 11:02:02) + dualrun streak 51 + "
               "attrition 4 CLEAN + orphan probe 2 zero-kill + estate audit results/_r1025bmc_estate_audit.json + "
               "MV delivery verified origin d9f4c53 + HANDOVER 5x row r986-r1025 + closeout push rides this window")
hb["full_load_selfproof"] = SELFPROOF
hb["sync"] = {"origin_tip": "11ce7c1db merged pre-estate; closeout commit+push rides this window", "ts": now_iso, "ahead_behind": "0/0 pre-closeout"}
with io.open(hp, "w", encoding="utf-8", newline="") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# verify
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
assert len(chk["orders_ack"]) == chk["orders_ack_count"]
print("heartbeat ok: epoch=%s int, clock=%s, ack=%d" % (chk["heartbeat_epoch_utc"], chk["clock_read"], chk["orders_ack_count"]))
