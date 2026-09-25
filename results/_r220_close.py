"""r220 close: state.json round_no++, heartbeat update (epoch int law), verify."""
import io
import json
import subprocess
import time
from datetime import datetime, timezone, timedelta

# ---- machine facts
import psutil
free_ram = round(psutil.virtual_memory().available / 2**30, 1)
cpu_util = round(psutil.cpu_percent(interval=1.0), 1)
gpu_free = None
try:
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=10)
    if out.returncode == 0 and out.stdout.strip():
        gpu_free = round(float(out.stdout.strip().splitlines()[0]) / 1024, 1)
except Exception:
    gpu_free = None
now = datetime.now(timezone(timedelta(hours=8)))
ts = now.strftime("%Y-%m-%d %H:%M")
clock_read = now.isoformat()
epoch = int(time.time())

# ---- state.json (bm-b ledger)
sp = "logs/iteration-loop/state.json"
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 220
st["did"] = ("P-1e runner DELIVERED+POOLED per prereg SS9 step-2: "
             "scripts/p1e_ic_batch.py (reuse p1c loaders/gates_v123/"
             "_chain_head_total + _ic_series_fast + batch-pre real-slice "
             "equiv gate + append_ledger r217 embed) selftest 9-leg/24-check "
             "PASS pre-pooling; runnable_pool +4 entries "
             "(P1E-NULLS-MCLOSE/MCLOSETR/MARC + P1E-CELLS, lane bm-b r188 "
             "lane-pin, one-entry-per-shard house pattern, workers_plan "
             "4-shard note); dry-tick takeable + 03:10 autofill LAUNCHED "
             "P1E-NULLS-MCLOSE pid3096 target_met (execution-face split "
             "closed loop); dual rebase autofill_state conflicts resolved "
             "via v2 canonical resolver (R208/R209 laws applied, v1 "
             "572-line whole-rewrite self-caught pre-push zero-leak)")
st["verdict"] = "green"
st["next"] = ("r221: ①P-1e harvest once 4 shards land (session flips pool "
              "shards->done per r203 pool-flip-is-round-work + finalize "
              "fail-closed + judgement table + factor ledger +157 via "
              "append_ledger embed + prereg §7/§8 backfill + round report "
              "receipt; 0 survivor = honest line-close) ②09-28 Monday "
              "new-bar full chain (update_daily -> live.paper "
              "REGIME_GUARD v3 enforce -> t35_open_fill_verify -> "
              "t24_prospect_paper x2 -> export/scorecard) ③EM push2his "
              "south re-probe daylight window (12:00-13:40 live / night "
              "burnt) ④bm-c noon window 09-28 15:30 (T-16 NAV takeover "
              "eval) ⑤zoo #86 ICU open-to-any deep-read; CODELY.md "
              "48.0KB approaching 50KB hot-cold archival watermark")
io.open(sp, "w", encoding="utf-8", newline="").write(
    json.dumps(st, ensure_ascii=False, indent=1))

# ---- heartbeat (own file only)
hp = "fleet/machines/bm-b.json"
hb = json.load(io.open(hp, encoding="utf-8"))
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = epoch            # MUST be JSON int (R170/R178)
hb["clock_read"] = clock_read
hb["current_task"] = ("P-1e batch in flight via autofill (4 pool entries "
                      "lane bm-b, first shard launched 03:10); r221 = "
                      "harvest + pool flip")
hb["cpu_cores"] = 16
hb["free_ram_gb"] = free_ram
if gpu_free is not None:
    hb["gpu_free_vram_gb"] = gpu_free
hb["cpu_util_pct"] = cpu_util
hb["round_no"] = 220
hb["verdict"] = "green"
# orders_ack: unchanged (74/74 all acked, both scans clean this round)
io.open(hp, "w", encoding="utf-8", newline="").write(
    json.dumps(hb, ensure_ascii=False, indent=1))

# ---- write-time self-verification (smoke F7 law)
rb = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(rb["heartbeat_epoch_utc"], int), "epoch must be int"
assert rb["round_no"] == 220
rs = json.load(io.open(sp, encoding="utf-8"))
assert rs["round_no"] == 220
print(f"state 219->220 OK | heartbeat ts={ts} epoch={epoch} (int "
      f"verified) | ram_free={free_ram}GB cpu={cpu_util}% gpu_free="
      f"{gpu_free}GB")
