import datetime as dt
import json
import os
import shutil
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
STATE = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
HEART = os.path.join(ROOT, "fleet", "machines", "bm-b.json")

# --- system sampling (windows) ---
import psutil
cpu = psutil.cpu_percent(interval=1)
vm = psutil.virtual_memory()
free_ram = round(vm.available / 1024**3, 1)
total_ram = round(vm.total / 1024**3, 1)
gpu_free = 2.2  # conservative carry; no new heavy GPU job this round (nvidia-smi flaky in-loop)
try:
    import subprocess
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        capture_output=True, timeout=10).stdout.decode().strip().splitlines()
    if out and out[0].isdigit():
        gpu_free = round(int(out[0]) / 1024, 1)
except Exception:
    pass

now = time.strftime("%Y-%m-%d %H:%M")
epoch = int(time.time())
clock_read = dt.datetime.now().astimezone().isoformat(timespec="seconds")

# --- state.json ---
s = json.load(open(STATE, encoding="utf-8-sig"))
s["round_no"] = 260
s["did"] = ("r260: T-76 wave-10 face(e) arXiv standing channel FIRST SWEEP (scripts/arxiv_sweep.py "
            "standing weekly tool + results/harvest/arxiv_sweep_20260926.json PM4/STR0 + digest "
            "triage 4 entries: A-lead referee paper / B-lead SPT concentration / C-watch window-agg "
            "/ D-pass IVC-BSDE; funnel 4/0 material-level) + S6 28 legs exit 0 weekend no-ops")
s["verdict"] = "GREEN"
s["next"] = ("R261+: T-82 bcd-basis transfer branch arrival = byte-verify + dD LF-normalize "
             "row-multiset compare; faces (a) jisilu/hibor/guorn + jin-gong = 09-28 open window; "
             "face (c) QuantsPlaybook second-sweep open; referee deep-read optional; "
             "09-28 new-bar chain; 10-01 month trio + REGIME_GUARD v3")
s["last_round_ts"] = epoch
s["last_result"] = "ok"
s["current_task"] = "T-76 wave-10 harvest faces (standing channels date-gated 09-28); pool watch CN-REGIME-POLICY-P1 (bm-a lane)"
with open(STATE, "w", encoding="utf-8", newline="\n") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)

# --- heartbeat ---
h = json.load(open(HEART, encoding="utf-8-sig"))
h["last_seen"] = now
h["heartbeat_epoch_utc"] = epoch  # python int, JSON int (R170/R178 law)
h["clock_read"] = clock_read
h["current_task"] = ("R260 done: T-76 face(e) arXiv standing channel first sweep (4 entries triaged, "
                     "A-lead referee methodology + B-lead SPT-EW prior; funnel 4/0) + MSG-1610 receipted "
                     "(PT-01 adjudication FYI, CEO domain) + MSG-1622 receive-leg pending bm-a branch; "
                     "next=09-28 channels window + transfer branch compare")
h["cpu_cores"] = psutil.cpu_count(logical=True)
h["free_ram_gb"] = free_ram
h["gpu_free_vram_gb"] = gpu_free
h["total_ram_gb"] = total_ram
h["cpu_util_pct"] = cpu
h["round_no"] = 260
h["verdict"] = "GREEN"
with open(HEART, "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)

# self-verify epoch is int in the written file (R170/R178 both-face law)
chk = json.loads(open(HEART, encoding="utf-8-sig").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("heartbeat epoch=%d int-verified, cpu=%.1f%% free_ram=%.1fGB gpu_free=%.1fGB" %
      (chk["heartbeat_epoch_utc"], cpu, free_ram, gpu_free))

# --- MSG-1610 archive (processed) ---
src = os.path.join(ROOT, "fleet", "inbox", "MSG-20260926-1610-bm-a-pt01-adjudication.md")
dst = os.path.join(ROOT, "fleet", "inbox", "processed", "MSG-20260926-1610-bm-a-pt01-adjudication.md")
if os.path.exists(src):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)
    print("MSG-1610 archived to processed")
else:
    print("MSG-1610 already moved")
print("closing done")
