"""R217 close-out: state round bump + heartbeat refresh (ephemeral, not committed as tool)."""
import datetime as dt
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

epoch = int(time.time())
clock = dt.datetime.now().astimezone().isoformat(timespec="seconds")
now_s = dt.datetime.now().isoformat(timespec="seconds")

try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1), 1)
    free_ram_gb = round(psutil.virtual_memory().available / 1024 ** 3, 1)
except Exception:
    cpu_pct, free_ram_gb = None, None

# --- state-bm-a.json ---
sp = os.path.join(ROOT, "state-bm-a.json")
with open(sp, "r", encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 217
st["did"] = ("R217: T-72 sina MF collector ticket opened+claimed+prereg FROZEN (commit 5a14ff38) "
             "+ s1 delivered (update_sina_mf.py selftest green 10 sections + live-fire spawn "
             "04:33:37 todo=5228 lock alive + first artifacts schema/law verified 000001.csv "
             "through 09-24) + decision-ack F-20260926-02 (D-07/D-05/D-10 night-window closure) "
             "+ S6 21 legs all green + MSG-0415 bm-b #86 claim acked zero-conflict")
st["verdict"] = "GREEN"
st["next"] = ("T-72 s2 patrol: detached first-pull in flight (~5s/symbol, ETA 7-8h, checkpoint "
              "self-heal; on completion = acceptance derive coverage>=5000/5222 + law-zero-violation "
              "+ idempotency rerun + num ceiling probe freeze + request budget account; s3 = S6 "
              "wiring after s2); 09-28 Monday new-bar full chain relay; mf/AH EM-block self-heal "
              "windows; bm-c rebuild-or-retire 09-26 11:52 GM face; 10-01 monthly trio + "
              "REGIME_GUARD v3 date gate; T-70 midterm 10-09")
st["ts"] = now_s
st["last_round_ts"] = "2026-09-26T04:23:37"
st["updated_at"] = now_s
st["current_task"] = ("r217 done: T-72 s1 collector live (first pull in flight); next: "
                      "s2 acceptance derive on completion / 09-28 new-bar relay")
st["last_run"] = now_s
st["last_round_at"] = now_s
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# --- fleet/machines/bm-a.json heartbeat ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
with open(hp, "r", encoding="utf-8") as f:
    hb = json.load(f)
hb["machine_id"] = "bm-a"
hb["last_seen"] = now_s
hb["current_task"] = st["current_task"]
hb["cpu_cores"] = 32
if cpu_pct is not None:
    hb["cpu_pct"] = cpu_pct
if free_ram_gb is not None:
    hb["free_ram_gb"] = free_ram_gb
    hb["idle_ram_gb"] = free_ram_gb
    hb["free_ram_mb"] = int(free_ram_gb * 1024)
hb["gpu_free_vram_gb"] = 5.3
hb["gpu_idle_vram_gb"] = 5.3
hb["verdict"] = "GREEN"
hb["heartbeat_epoch_utc"] = epoch          # MUST be JSON int (R170/R178 double-violation law)
hb["clock_read"] = clock
hb["task"] = ("T-72 s1 delivered, first-pull refresh in flight; s2 acceptance derive on "
              "completion; 09-28 new-bar relay next")
hb["round_no"] = 217
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# self-verify epoch int (F5/F7 discipline)
with open(hp, "r", encoding="utf-8") as f:
    back = json.load(f)
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int"
print(f"state round_no=217 ok; heartbeat epoch={back['heartbeat_epoch_utc']} int-verified; "
      f"clock={back['clock_read']}; cpu={cpu_pct} free_ram={free_ram_gb}")
