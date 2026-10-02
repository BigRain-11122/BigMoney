import json, time, datetime

# --- state-bm-a.json: round 566 -> 568 (skip dead-session 567 per r529 law) ---
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 568
st["round"] = 568
st["loop_round"] = 568
st["last_round"] = 568
st["last_round_at"] = "2026-10-02T10:45:00+08:00"
st["last_round_ts"] = "2026-10-02T10:45:00+08:00"
st["updated"] = "2026-10-02T10:45:00+08:00"
st["current_task"] = ("W64 finalize closeout landed (chain head 505,348; unblocked W65/W66 finalize fleet-wide) "
                      "+ W68 FREEZE delivered+ignited (5/12 shards burning, A arithmetic/B forced-skip past 50_500)")
st["did"] = ("r568: S0 integration surgical (3-reject escalation, fork-point payload law) + W64 finalize one-pass "
             "landed 0e21c860f (S5 4/4 PASS, S7/S8 backfilled, r567 stranded product adopted per r471) + "
             "W68 freeze five-face + seat MSG-1010 + band gate ADMIT + S6 37 legs green + D-19 MATCH")
st["notes"] = ("dead r567 session adopted (finalize generate 09:22:38, died pre-commit; product stranded untracked "
               "one window, closed by r568); orders diff=empty; audit flags pool_starvation+supply_floor = "
               "engine-lane-active (W68 burning outside pool by law sec.1/2) + holiday board-clear, honest note")
st["next"] = ("W68 burn 12/12 -> one-pass finalize (prev=live head derive; chain order: W65 bm-b -> W66 bm-c -> "
              "W67 bm-b -> W68 bm-a FAIL-CLOSED r307); next freeze W69 (projection A 181_004..183_003 / "
              "B 50_701..50_900 both CLEAN)")
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("state r568 written")

# --- heartbeat fleet/machines/bm-a.json ---
import subprocess
cpu = subprocess.check_output(["powershell", "-NoProfile", "-Command",
    "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"],
    text=True).strip() or "0"
import psutil
free_gb = round(psutil.virtual_memory().available / (1024**3), 1)
epoch = int(time.time())
clock = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
hp = "fleet/machines/bm-a.json"
h = json.load(open(hp, encoding="utf-8"))
h["machine_id"] = "bm-a"
h["last_seen"] = "2026-10-02T10:45:00+08:00"
h["round_no"] = 568
h["round"] = 568
h["loop_round"] = 568
h["last_round"] = 568
h["task"] = ("W64 finalize landed + W68 freeze/ignition; W68 burn in flight 5/12")
h["current_task"] = h["task"]
h["cpu_pct"] = float(cpu) if cpu else 0.0
h["cpu_util_pct"] = float(cpu) if cpu else 0.0
h["cores"] = 32
h["cpu_cores"] = 32
h["idle_ram_gb"] = free_gb
h["free_ram_gb"] = free_gb
h["ram_free_gb"] = free_gb
h["total_ram_gb"] = round(psutil.virtual_memory().total / (1024**3), 1)
h["verdict"] = ("loaded_ok: W68 engine burn active (5/12 shards, tick ~1/min); pool_starvation flag = "
                "engine-lane-active + holiday board-clear, legal idle per SATURATION_ENGINE_LAW sec.1/2")
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = clock
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
# self-check: epoch must be JSON int
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
assert "T" in chk["clock_read"], "clock_read must be T-separated ISO (R262 law)"
print("heartbeat r568 written, epoch int:", chk["heartbeat_epoch_utc"], "clock:", chk["clock_read"])
