# r921 bm-b closeout: state + heartbeat + report line (continuation of dead r921 S0 incarnation)
import json, time, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
print("closeout start", NOW, flush=True)

REPORT = (
 "| " + NOW + " | r921 bm-b [dept:eng/fleet] | dead-session-takeover closeout + N2U3 leg-3 IGNITION verification round | "
 "watermark: RED lane pool-batch-runnable-idle-low-cpu read 01:05 (pool N2U3-LEG3-TRAIN ready + py 1.8%) -> SELF-HEALED 01:06:19: "
 "L54 claim-strand recheck fired after prior-incarnation S0 push delivery (S0 merge 9 commits 16 UU + S0-b merge bm-c r969 8 UU + claim commit, rev-list 0/0) "
 "-> autofill launch PID 8556 alphagen_rl_p1.py train --episodes 4096 (8-worker ProcessPool BelowNormal per workers_plan; O-20261014-0030 CPU-full law) "
 "-> py CPU 77% -> watchdog cycle re-derives green | "
 "orphan-faces=0 (round-zero probe 01:03: py_faces=21 orphans=0; legal = satengine + astock refresh + backfill_ext_slots + N2U3 burn) | "
 "currently-active: N2U3 leg-3 train BURNING (PID 8556 + 8 workers, 4096 eps ~3.3h ETA ~04:40, resume from leg-2 ckpt) + astock full-universe refresh (PID 6036) + backfill_ext_slots (PID 26800); GPU idle MODE=pause PSU-deferred (i2v 27/53) | "
 "latest-artifact: N2U3-ALPHAGEN-RL-P1-LEG3-TRAIN ignition + burn in-flight + 3 CEO orders acked (0951/0030/0040, executed by interactive sessions, receipts verified) | "
 "did: (1) S0 takeover: prior r921 incarnation died post-S0-push pre-S0.5; this session continued S0.5->closeout. "
 "(2) S0.5: D-19 zero-delta (orders 348eaf34/decisions b137f331 unchanged); fleet/orders diff = 3 unacked -> all bm-b orders already executed (O-0951 power redline / O-0030 CPU-full / O-0040 bili-reply) -> acked 205->208 with receipts. "
 "(3) S1 smoke 49/49. (4) S3: SatEngine alive idle (N1 queue 0, TJ-blocked standing); post_review 51 NO all historical (latest 10-10, zero new this window); board open=0, job_list empty; "
 "unity POC probe#6 bridge = No instances (editor closed; NEW: Cowork app RUNNING since 00:20 = R2 auto-install path live at first editor-open) -> honest carry. "
 "(5) S6 4 legs: dualrun ZERO-DRIFT 446 entries streak 1 (post-r920-flip observation reset), compute_audit CLEAN load_state=burning-healthy (pool_starvation+ignition_sla healed), pywm insufficient_history LEGAL (batch running = the work), token delta 0. "
 "(6) S7: idle_trigger --worked (idle_rounds 0), attrition CLEAN, loop pin=2 no-op, watchdog re-registered, both claws installed, inbox 0 unread. | "
 "evidence: PID 8556+8 workers Get-CimInstance + results/compute_audit.bm-b.json (CLEAN burning-healthy) + smoke 49/49 + results/_r686bmb_d19_check.json + results/_r921bmb_postrev_scan.txt + results/_r921bmb_board.txt + results/_orphan_face_probe.bm-b.json + results/_attrition_guard_scan.json | "
 "unacked_orders=0 (208/208) | registry-zero-hit: no sweep/archive/delete actions this round | "
 "local-unreached-origin-commits: round-start 0 (prior incarnation delivered S0) -> closeout commit+push follows + self-proof | "
 "next-pointer r922: N2U3 burn watch (ETA ~04:40 -> ckpt products -> export-topk K=32 -> judged face per prereg sec.6) > S6 full chain 10-14 15:30 data window > standing: GPU line PSU-swap (MODE=pause holds, i2v 27/53), unity POC first interactive editor window (Cowork running = R2 live), Speech-02 committee/CEO, Music3 post-batch, bili-reply CEO cookie+aid, MF panel source-blocked | [r921 bm-b]"
)

# --- state.json ---
sp = ROOT / "state.json"
st = json.loads(sp.read_text(encoding="utf-8"))
st.update({
 "round": 921, "round_no": 922, "round_no_label": "r921",
 "ts": NOW, "updated": NOW, "updated_at": NOW, "last_round_at": NOW, "last_seen": NOW, "last_round_ts": NOW,
 "last_action": "r921: N2U3 leg-3 IGNITION verified (L54 self-heal: claim delivered -> autofill launch PID 8556, 8 workers, 4096 eps) + 3 CEO orders acked (0951/0030/0040) + S6 core green (audit CLEAN burning-healthy)",
 "last_action_at": NOW,
 "did": "r921: (1) S0 takeover of dead incarnation (S0+S0-b merges already delivered 0/0, this session S0.5->closeout). (2) D-19 zero-delta. (3) orders diff: 3 unacked (0951/0030/0040) all executed by interactive sessions -> acked. (4) watermark RED lane pool-batch-runnable-idle-low-cpu self-healed: L54 recheck fired post-delivery -> autofill launch 01:06:19 PID 8556 train --episodes 4096, 8-worker ProcessPool; py 77%; audit CLEAN. (5) smoke 49/49; SatEngine alive idle; post_review 51 NO all historical; unity POC probe#6 no-instance honest carry (Cowork app now RUNNING = R2 path live). (6) S6: dualrun ZERO-DRIFT streak 1, audit CLEAN, pywm insufficient_history legal, token 0. (7) S7 all green, idle --worked.",
 "note": "r921: takeover+ignition round; product = N2U3 leg-3 burn in-flight (4096 eps, ~3.3h); red lane resolved by L54 daemon self-heal",
 "task": "r922: N2U3 burn watch (ETA ~04:40) -> export-topk K=32 -> judged; S6 full chain 10-14 15:30; standing: PSU-swap GPU hold, unity POC editor-window, Speech-02/Music3 gates, bili-reply CEO physical items",
 "current_task": "r922: N2U3 burn watch + judged chain post-burn + S6 full chain 10-14 15:30 + unity POC waits first interactive editor window",
 "next": "r922: (a) N2U3 burn watch to 53/53... to 4096 eps done (ETA ~04:40) -> export-topk K=32 -> judged face; (b) S6 full chain at 10-14 15:30 data window; (c) standing: GPU PSU-swap (MODE=pause, i2v 27/53), unity POC (Cowork running, editor window pending), Speech-02 adjudication, Music3 install post-batch, bili-reply cookie+aid CEO items, MF panel source-blocked",
 "next_milestone": "N2U3 leg-3 burn done ~04:40 -> export-topk + judged face (first judged N2U3 evidence); S6 data window 10-14 15:30; GPU line = PSU swap or CEO re-order",
 "now_active": "N2U3 leg-3 burn PID 8556 (8 workers, py CPU 77%); astock refresh + backfill_ext_slots in-flight; GPU idle MODE=pause PSU-deferred; SatEngine ticking; Cowork hub+app running (no editor)",
 "orphan_face": 0, "orphan_faces": 0,
 "orphan_face_note": "r921 probe 01:03: py_faces=21 orphans=0 killed=[] (satengine + astock refresh + backfill_ext_slots + N2U3 burn = legal lanes)",
 "verdict": "GREEN: N2U3 leg-3 burn ignited + running (main chain face); red watermark lane self-healed by L54; flags = GPU PSU-deferred (MODE=pause) + unity POC editor-window-gated + Speech-02/Music3 standing gates",
 "d19_watermark_guard": {**st.get("d19_watermark_guard", {}), "round_ref": 921, "ts": NOW},
})
sp.write_text(json.dumps(st, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("state.json written", flush=True)

# --- heartbeat ---
hp = ROOT / "fleet" / "machines" / "bm-b.json"
hb = json.loads(hp.read_text(encoding="utf-8"))
for f in ("O-20261013-0951-bm-b.md", "O-20261014-0030-bm-b.md", "O-20261014-0040-bm-b.md"):
    if f not in hb["orders_ack"]:
        hb["orders_ack"].append(f)
hb["orders_ack_count"] = len(hb["orders_ack"])
notes = hb.setdefault("orders_ack_notes", {})
notes["O-20261013-0951-bm-b.md"] = ("r921 bm-b receipt: queue-serial discipline standing + power redline honored -- GPU heavy = one-at-a-time queue (i2v 27/53 held PSU-deferred, zero GPU co-fire this round; CPU light lanes parallel per law); landed origin 9e7dca5a2 + errata 78394ec14")
notes["O-20261014-0030-bm-b.md"] = ("r921 bm-b receipt: CPU cap lifted live proof = N2U3-LEG3-TRAIN burn 8-worker ProcessPool full-grid (PID 8556, no -2 cap) + astock refresh + backfill_ext_slots + SatEngine concurrent; power redline narrowed to GPU salvos (no GPU batch running); landed 9b7b8a8da")
notes["O-20261014-0040-bm-b.md"] = ("r921 bm-b receipt: deployment verified on origin (commit ad58d51af, delivery rev-list 0/0); CPU-only bili-reply legal under O-0951+O-0030 (100% CPU, ~3.7GB RAM, zero VRAM); standing gap = CEO physical items (SESSDATA+bili_jct cookie + target video aid) -> config.json then production")
try:
    import psutil
    ram_gb = round(psutil.virtual_memory().available / 1024**3, 1)
    ram_pct = round(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total, 1)
except Exception:
    ram_gb, ram_pct = hb.get("free_ram_gb", 0), hb.get("ram_free_pct", 0)
gpu_u, gpu_w, vram_free = hb.get("gpu", {}).get("util_pct", 1.0), hb.get("gpu", {}).get("power_w", 14.0), hb.get("gpu_free_vram_gb", 3.4)
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,power.draw,memory.total,memory.used", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=20).stdout.strip().split(",")
    gpu_u, gpu_w = float(out[0]), float(out[1])
    vram_free = round((float(out[2]) - float(out[3])) / 1024, 1)
except Exception as ex:
    print("gpu query fail", ex, flush=True)
hb.update({
 "round": 921, "round_no": 922, "round_no_label": "r921",
 "ts": NOW, "updated": NOW, "updated_at": NOW, "last_seen": NOW, "last_round_at": NOW,
 "last_action": "r921: N2U3 leg-3 IGNITION verified (L54 self-heal -> autofill launch PID 8556, 8 workers, 4096 eps in-flight) + 3 CEO orders acked (0951/0030/0040 receipts) + S6 core green (audit CLEAN burning-healthy, dualrun ZERO-DRIFT)",
 "last_action_at": NOW,
 "latest_artifact": "N2U3-ALPHAGEN-RL-P1-LEG3-TRAIN burn in-flight (PID 8556 launched 01:06:19, 4096 eps ETA ~04:40; ignition = first pool-batch launch under O-0951/O-0030 power-law regime)",
 "did": st["did"],
 "task": st["task"], "current_task": st["current_task"], "next": st["next"], "next_milestone": st["next_milestone"],
 "note": st["note"], "now_active": st["now_active"],
 "orphan_face": 0, "orphan_faces": 0, "orphan_face_note": st["orphan_face_note"],
 "verdict": st["verdict"],
 "heartbeat_epoch_utc": EPOCH,
 "clock_read": NOW,
 "idle_rounds": 0, "agenda_starved": False, "green_idle": False,
 "free_ram_gb": ram_gb, "ram_free_gb": ram_gb, "idle_ram_gb": ram_gb,
 "ram_free_pct": ram_pct, "idle_ram_pct": ram_pct,
 "gpu_free_vram_gb": vram_free, "gpu_idle_vram_gb": vram_free,
 "gpu": {"util_pct": gpu_u, "power_w": gpu_w, "face": "GPU idle (MODE=pause PSU-deferred, i2v 27/53 held for PSU swap/CEO re-order); N2U3 burn = pure CPU face"},
 "sync": {"last_push_ts": NOW, "note": "r921: closeout commit+push follows this write; delivery self-proof via fetch+rev-list"},
})
hp.write_text(json.dumps(hb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("heartbeat written, acks:", hb["orders_ack_count"], "epoch int:", isinstance(hb["heartbeat_epoch_utc"], int), flush=True)

# --- report line ---
rp = ROOT / "logs" / "iteration-loop" / "round_reports.md"
with rp.open("a", encoding="utf-8", newline="\r\n") as fh:
    fh.write(REPORT + "\r\n")
print("report line appended", flush=True)
print("closeout writes DONE", flush=True)
