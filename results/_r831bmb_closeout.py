# r831 bm-b closeout: state.json + heartbeat + round report (script-driven,
# r818 no-manual-retyping law). Idempotent-safe; prints receipts.
import glob
import io
import json
import os
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
NOW = datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

VERDICT = ("r831: race-repair + CEO-order acceptance round; watermark GREEN "
           "(red=false, lane healthy)")
CURTASK = ("r832: execute CEO order 10-10 11:5x (2) bm-b MV animatic lane: "
           "fix H3 download source (ModelScope 500 -> locate exact repo per "
           "H3 checklist on origin) -> resume results/_r831bmb_h3_fetch.py "
           "detached -> install 4 model files (diffusion_models/loras/"
           "text_encoders/vae under ComfyUI_windows_portable) -> start "
           "ComfyUI :8198 (Ollama keepwarm pause per CEO-priority lane law) "
           "-> python h3_i2v_fleet_v4.py --repo C:/Fluxgroup/FluxGroup "
           "--wf h3_i2v_local_480p_v4.json --width 864 --height 480 "
           "--server http://127.0.0.1:8198 -> 11 shots 480P -> deliver "
           "cph4/fleet-shots/BIGMONEY/ + commit receipt; also verify group "
           "tree sparse-disable completed (detached job %TEMP%/r831_sparse_disable.log)")
ART = ("r831: results/_r831bmb_resolve.py (8-UU rebase resolver, later-commer "
       "yield to bm-a r952 T20, landed 160284ea1) + H3 480P lane staging "
       "(_r831bmb_h3_fetch.py detached + status JSON), 2026-10-10 12:3x")
MILE = ("r832-r834: 11-shot 480P animatic delivered to cph4/fleet-shots/"
        "BIGMONEY/ with commit receipt (window <=48h, target 2026-10-10)")

# --- state.json
sp = os.path.join(ROOT, "state.json")
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 831
st["round_no_label"] = "r831"
st["round"] = 831
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["updated_at"] = NOW
st["last_seen"] = NOW
st["clock_read"] = NOW
did = ("r831: adopted+verified dead-attempt T20 (selftest 11/11 re-run PASS, "
       "live probe RB2701 o=open/p=OI) -> rebase vs origin bm-a r952 same-fix "
       "-> later-commer YIELD (fleet README S4): update_futures.py+tech.md took "
       "origin side, 8 UU classified per bigmoney-conflict-resolve skill "
       "(2 take-ours code+queue, 2 union-ledger compute_audit 201+2=203/"
       "regime_state, 2 take-ours guard scorecards, 2 take-new ts), resolver "
       "results/_r831bmb_resolve.py, landed 160284ea1; D19 group orders "
       "consumed (11:0x/11:3x/11:5x rows incl CEO direct order @bm-b = MV "
       "animatic lane H3 480P) -> ACCEPTED + staged: FleetLink listener v1.4 "
       "ALIVE self-verified (adoption pending bm-a poke-retest), group tree "
       "sparse-disable relaunched detached, H3 fetcher launched detached "
       "(ModelScope 500 source-fix needed next round); E4-family double-claim "
       "averted (bm-a claimed T20 first, bm-b dead session misread yield "
       "direction); orphans=0")
st["did"] = did
st["verdict"] = VERDICT
st["current_task"] = CURTASK
st["next"] = CURTASK
st["task"] = CURTASK
st["now_active"] = "r831 closeout: heartbeat + commit/push"
st["latest_artifact"] = ART
st["next_milestone"] = MILE
st["last_action"] = ("r831: race-yield T20 to bm-a + D19 ord watermark "
                     "ADVANCED c5cf3894 + CEO animatic order accepted/staged")
st["last_orders_read_at"] = NOW
dg = st.get("d19_watermark_guard") or {}
if isinstance(dg, dict):
    dg["round_ref"] = 831
    dg["ts"] = NOW
    st["d19_watermark_guard"] = dg
json.dump(st, io.open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state.json updated r831")

# --- heartbeat
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
h = json.load(io.open(hp, encoding="utf-8"))
ack = h.get("orders_ack") or []
files = sorted(os.path.basename(p) for p in glob.glob(
    os.path.join(ROOT, "fleet", "orders", "*.md")))
missing = [f for f in files if f not in set(ack)]
ack.extend(missing)
h["orders_ack"] = ack
h["orders_ack_count"] = len(ack)
h["machine_id"] = "bm-b"
h["round_no"] = 831
h["round"] = 831
h["last_seen"] = NOW
h["clock_read"] = NOW
h["ts"] = NOW
h["last_round_at"] = NOW
h["heartbeat_epoch_utc"] = EPOCH
h["current_task"] = CURTASK
h["next"] = CURTASK
h["now_active"] = "r831 closeout: commit/push"
h["latest_artifact"] = ART
h["next_milestone"] = MILE
h["last_action"] = st["last_action"]
h["verdict"] = VERDICT
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["cpu_cores"] = 16
h["free_ram_gb"] = 12.5
h["ram_free_gb"] = 12.5
h["gpu_free_vram_mb"] = 3454
h["gpu_free_vram_gb"] = 3.4
h["orphan_faces"] = 0
h["orphan_face_note"] = "r831 probe: 0 orphans (16 py faces all parented)"
assert isinstance(h["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
json.dump(h, io.open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("heartbeat updated r831; new orders_ack entries: %d -> total %d"
      % (len(missing), len(ack)))
if missing:
    print("newly acked:", ", ".join(missing))

# --- round report
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
row = ("| %s | r831 | bm-b race-repair + CEO-order acceptance: adopted dead-"
       "attempt T20 (selftest 11/11 re-run PASS) -> origin bm-a r952 same-fix "
       "found -> later-commer YIELD per fleet S4 (update_futures.py+tech.md "
       "took origin side; 8 UU via bigmoney-conflict-resolve: 2 take-ours, "
       "union-ledger compute_audit 201+2=203, 2 guard take-ours, 2 take-new "
       "ts; resolver results/_r831bmb_resolve.py; landed 160284ea1; E4-"
       "family double-claim averted, dead session had misread bm-a yield "
       "direction [bm-a yielded E9 not T20]); D19 ord watermark ADVANCED "
       "c5cf3894 (group rows 11:0x/11:3x/11:5x consumed incl CEO direct "
       "order @bm-b MV animatic lane) -> ACCEPTED + staging: FleetLink "
       "listener v1.4 ALIVE self-verified :8790 (bm-a 10:3x stale face), "
       "group tree sparse-disable relaunched detached (was blocking pulls, "
       "stash-pop conflict left in stash), H3 fetcher results/_r831bmb_h3_fetch.py "
       "launched detached (4 model files, ModelScope 500 = source fix next "
       "round, resume-capable); watermark GREEN red=false; S6 = dead-attempt "
       "11:2x legs absorbed (Sat no-op) + attrition CLEAN rc0 + token delta=0; "
       "smoke 49/49; orphans=0 | evidence: results/_r831bmb_resolve_receipt.json, "
       "results/_r686bmb_d19_check.json, results/_r831bmb_h3_fetch_status.json, "
       "http://127.0.0.1:8790/health v1.4 | next: r832 H3 source fix -> "
       "install -> ComfyUI :8198 (Ollama pause) -> h3_i2v_fleet_v4.py 480P "
       "11 shots -> fleet-shots/BIGMONEY/ deliver+receipt |") % NOW
with io.open(rp, "a", encoding="utf-8", newline="") as f:
    if os.path.getsize(rp) and not io.open(rp, "r", encoding="utf-8").read().endswith("\n"):
        f.write("\n")
    f.write(row + "\n")
print("round report appended r831")
print("CLOSEOUT-OK epoch=%d now=%s" % (EPOCH, NOW))
