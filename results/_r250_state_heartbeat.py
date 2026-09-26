"""r250 bm-b: state.json round bump + heartbeat refresh (epoch=int law R170/R178, BOM-free JSON)."""
import json
import time
import datetime
import psutil

now = "2026-09-26 13:17"
epoch = int(time.time())
clock_read = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

state = {
    "round_no": 250,
    "did": "r250: maintenance round fourth census (zero-claim honest) + 5x HANDOVER recon r246-250 (line3 refreshed r220->r250 + end-window row; ledger 185,798 flat); S6 28 legs all exit 0 (weekend honest no-ops, cutoff 09-24); pool_starvation 5th consecutive -> S8.3 three-face supply check = legal idle (MF-IC-P1 panel-blocked 53/5222 bm-a lane self-heal in flight; bm-a T-73 CN-REV-TILT runner being written, pool submit next; no P1 face); post_review today 257 rows zero-fail",
    "verdict": "GREEN",
    "next": "09-28 Monday new-bar full chain (grid_paper 5 accounts first marks + wired exit_overrides first paper run + bm-c T-16 takeover evaluation 15:30); 10-01 month-first three-pack (science_audit/monthly_briefing/self_review) + corr-watch W3 + REGIME_GUARD v3 date-gate enforce window; 10-31 six-member first review all-HOLD",
    "last_round_ts": now,
    "last_result": "S6 28 legs all exit 0 (weekend no-ops honest, cutoff 09-24; live.paper 6 anchors OK, x2 watch C02 0.0491 + ENGULF 0.0143 probation as recorded); smoke 25/25; watermark py_low_board_clear py 0.6% legal idle; pool_starvation 5th round supply-check legal per S8.3; orders 79/79 both scans zero unacked; bm-c staleness disclosed not seized (T-16 eval window 09-28 15:30)",
    "current_task": "r250 closed: maintenance round + 5x HANDOVER recon; next action face = 09-28 Monday new-bar full chain + T-16 takeover evaluation 15:30",
    "last_tick": "13:17",
    "updated_at": now,
    "last_seen": now,
    "ts": now,
    "last_run": "R250 2026-09-26T13:17:00",
    "last_round_at": "R250 2026-09-26T13:17:00",
    "updated": now,
}
with open("logs/iteration-loop/state.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

hb_path = "fleet/machines/bm-b.json"
hb = json.load(open(hb_path, encoding="utf-8-sig"))
hb["last_seen"] = now
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock_read
hb["current_task"] = state["current_task"]
hb["round_no"] = 250
hb["verdict"] = "GREEN"
hb["free_ram_gb"] = round(psutil.virtual_memory().available / 1e9, 1)
hb["cpu_cores"] = 16
hb["cpu_util_pct"] = psutil.cpu_percent(interval=1)
hb["total_ram_gb"] = round(psutil.virtual_memory().total / 1e9, 1)
hb["idle_ram_gb"] = hb["free_ram_gb"]
hb["idle_ram_mb"] = int(hb["free_ram_gb"] * 1024)
hb["gpu_free_vram_gb"] = 2.2
hb["gpu_free_vram_mb"] = 2235
hb["gpu_idle_vram_mb"] = 2235
with open(hb_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# self-verify: epoch must be JSON int, files parse back
chk = json.load(open(hb_path, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
json.load(open("logs/iteration-loop/state.json", encoding="utf-8"))
print("state round_no=250 OK; heartbeat epoch int OK", chk["heartbeat_epoch_utc"], chk["clock_read"])
