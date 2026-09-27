"""r317 bm-a wrap: state + heartbeat update (single-writer, JSON int epoch law)."""
import json
import time
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
now_iso = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
epoch = int(time.time())

# --- state-bm-a.json ---
sp = ROOT / "state-bm-a.json"
s = json.loads(sp.read_text(encoding="utf-8"))
s["round_no"] = 317
s["did"] = ("R317: Sunday maintenance -- S6 32/32 legs rc=0 (chain script r317 lineage +2 new legs rev_osc/sysv1 per prompt wiring) "
            "+ MSG-1210 bm-b (c)-parallel position PROCESSED + ack MSG-1145 sent (supply-face contract: terminal three-piece verdict "
            "window at ETA) + repull interim probe 817/5228 pace 22.0/min zero-fail ETA ~15:01 (probe json landed)")
s["verdict"] = ("py_low_with_work_cands legal-occupied (refresh_lock_lanes=[sina_mf] A1 deep repull 817/5228 @11:41 pace 22.0/min "
                "ETA ~15:01; board 0 open; pool ready=0; audit CLEAN)")
s["next"] = ("R318: repull watch-face (terminal verdict window ~15:0x+ = update_sina_mf exit-code law + sina_mf_accept sec-4 gates "
             "coverage>=5000/self-collapse/idempotency + N=250 depth census -> sina_mf_update_status complete+N=250 = bm-b "
             "sina-construct prereg open-gate); Monday 09-28 09:15 T-91 s3 auto-fire full chain; HANDOVER next R320; 10-01 month trio standing")
s["ts"] = now_iso
s["last_round_ts"] = now_iso
s["updated_at"] = now_iso
s["last_run"] = now_iso
s["last_round_at"] = now_iso
s["last_round"] = 316
s["last_seen"] = now_iso
s["current_task"] = "R318 next: repull watch-face (terminal ~15:0x) + Monday T-91 s3 auto-fire 09:15"
s["task"] = "R317 done: S6 32/32 green + MSG-1210 processed + ack sent + probe 817/5228; R318 next: repull watch-face"
sp.write_text(json.dumps(s, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

# --- fleet/machines/bm-a.json (heartbeat, own file only) ---
hp = ROOT / "fleet" / "machines" / "bm-a.json"
h = json.loads(hp.read_text(encoding="utf-8"))
h["last_seen"] = now_iso
h["current_task"] = "R317 done: S6 32/32 green + MSG-1210 (c)-parallel processed + ack MSG-1145 + repull probe 817/5228; R318: repull watch-face ~15:0x terminal verdict"
h["cpu_cores"] = 32
h["cpu_pct"] = 7.5
h["cpu_util_pct"] = 7.5
h["free_ram_gb"] = 54.0
h["free_ram_mb"] = 55296
h["idle_ram_gb"] = 54.0
h["gpu_free_vram_gb"] = 5.55
h["gpu_idle_vram_gb"] = 5.55
h["gpu_idle_vram_mb"] = 5678
h["gpu0_free_vram_gb"] = 5.3
h["verdict"] = "py_low_with_work_cands legal-occupied: sina_mf A1 deep repull in flight (817/5228 @11:41, pace 22.0/min, ETA ~15:01, zero-fail); board 0 open; pool ready=0; audit CLEAN"
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now_iso
h["round_no"] = 317
h["task"] = "R317 done: S6 32/32 green + MSG-1210 processed + ack MSG-1145 sent + probe; R318 next: repull terminal verdict window"
hp.write_text(json.dumps(h, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

# self-assert epoch int (R170/R178 law)
h2 = json.loads(hp.read_text(encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in h2["clock_read"], "clock_read must be ISO-8601 T-separated"
print(f"state 317 + heartbeat OK epoch={epoch} clock={now_iso}")
