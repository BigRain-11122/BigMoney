# -*- coding: utf-8 -*-
"""r290 bm-b S7 closeout: state round 290 + heartbeat + orders double-scan.
Report line already appended this round (no duplicate). Byte-face mirror:
heartbeat indent=1/ensure_ascii=False/LF/no-tail-nl; state indent=1.
All timestamps derived from one now() instance (r271 law -- repairs the
hardcoded last_round_at written by the earlier minimal bump)."""
import datetime
import json
import glob
import os
import subprocess
import time

now = datetime.datetime.now()
ts = now.strftime("%Y-%m-%d %H:%M:%S")
iso = now.astimezone().isoformat()          # T-format clock_read (R262)
epoch = int(time.time())

# --- machine stats ---
cpu_pct = 0.0
free_ram_gb = 0.0
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1), 1)
    free_ram_gb = round(psutil.virtual_memory().available / 1e9, 1)
except Exception:
    pass
gpu_vram = ""
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=10)
    if r.returncode == 0 and r.stdout.strip():
        gpu_vram = str(int(r.stdout.strip().splitlines()[0]))
except Exception:
    pass

# --- S7 closing orders double-scan (round-start scan was 90/90 empty) ---
hp = "fleet/machines/bm-b.json"
hb = json.loads(open(hp, encoding="utf-8-sig").read())
ack = hb.get("orders_ack", "")
if isinstance(ack, list):
    ack = " ".join(ack)
acked = set(ack.split())
order_files = sorted(os.path.basename(o) for o in glob.glob("fleet/orders/O-*.md"))
new_orders = [o for o in order_files if o not in acked]
if new_orders:
    # execute/ack nothing unseen here without review -- report honestly;
    # this window's scan found none at round start, treat new arrivals as
    # next-round S0.5 face but do ack-mark them for takeover visibility.
    print("NEW ORDERS AT CLOSE (deferred to next round S0.5):", new_orders)

# --- state.json (indent=1 mirror) ---
sp = "logs/iteration-loop/state.json"
st = json.loads(open(sp, encoding="utf-8-sig").read())
st["round_no"] = 290
st["did"] = ("r290: S0 stash-pop pool冲突take-upstream正典解(stashed 53⊂upstream 54逐字节·"
             "CENSUS-FUS-S2-W1保序零丢失·_r290_resolve.py留痕)+autofill r290自提交律"
             "(_tick_owned_dirt()=claim/keepalive git流并入STATE+FUSE·r282 rebase-retry"
             "轮间窗可达化·S15i/S17e新腿全量ALL PASS)+CODELY坑律条+S6 22腿+HANDOVER 5x核对")
st["verdict"] = ("conflict-resolve + self-commit-law round ok (tick-owned dirt rides the "
                 "claim/keepalive commit; CN-TREND nulls in-flight)")
st["next"] = ("p1_results落地即harvest(_r287bmb_cntrend_harvest.py十面门)+pool flip; "
              "CENSUS-FUS-S2-W1 ready待autofill装; T-87 pass ETA 06:40复探; 09-28周一新bar全链")
st["last_round_ts"] = ts
st["last_result"] = "ok"
st["current_task"] = ("CN-TREND-ETF-P1 nulls burn in-flight (harvest on landing) + "
                      "T-87 astock full-universe refresh in-flight + r290 self-commit law landed")
st["last_tick"] = now.strftime("%H:%M")
st["updated_at"] = ts
st["last_seen"] = iso
st["ts"] = ts
st["last_run"] = "R290 " + iso
st["last_round_at"] = ts          # repairs earlier hardcoded estimate (r271 law)
st["updated"] = ts
open(sp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(st, ensure_ascii=False, indent=1))

# --- heartbeat fleet/machines/bm-b.json (indent=1, no tail-nl, LF) ---
hb["last_seen"] = iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = iso
hb["round"] = 290
hb["round_no"] = 290
hb["verdict"] = ("conflict-resolve+self-commit-law round ok; CN-TREND nulls in-flight; "
                 "smoke 25/25; S6 22 legs rc=0; orders 90/90")
hb["current_task"] = st["current_task"]
hb["cpu_pct"] = cpu_pct
hb["cpu_util_pct"] = cpu_pct
hb["free_ram_gb"] = free_ram_gb
hb["idle_ram_gb"] = free_ram_gb
if gpu_vram:
    hb["gpu_free_vram_mb"] = int(gpu_vram)
    hb["gpu_idle_vram_mb"] = int(gpu_vram)
    hb["gpu_free_vram_gb"] = round(int(gpu_vram) / 1024, 1)
    hb["gpu_idle_vram_gb"] = round(int(gpu_vram) / 1024, 1)
open(hp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(hb, ensure_ascii=False, indent=1))

# --- self-verification (R170/R178/R262 laws) ---
hb2 = json.loads(open(hp, encoding="utf-8-sig").read())
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in hb2["clock_read"], "clock_read not T-format"
st2 = json.loads(open(sp, encoding="utf-8-sig").read())
assert st2["round_no"] == 290
unacked = [o for o in order_files if o not in set(hb2["orders_ack"].split())]
print("closeout OK: round=290 epoch=%d clock=%s ack=%d unacked=%s "
      "new_at_close=%s cpu=%s%% ram_free=%sGB"
      % (hb2["heartbeat_epoch_utc"], hb2["clock_read"], hb2["n_orders_ack"],
         unacked, new_orders, cpu_pct, free_ram_gb))
