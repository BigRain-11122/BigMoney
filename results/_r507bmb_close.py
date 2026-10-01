import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.now(timezone(timedelta(hours=8)))
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# --- resource sample (fail-soft keeps prior values) ---
cpu_pct, free_ram, gpu_free = 0.0, 0.0, 0.0
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    free_ram = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    pass
try:
    out = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.free",
         "--format=csv,noheader,nounits"], stderr=subprocess.DEVNULL)
    gpu_free = round(float(out.decode().splitlines()[0].strip()) / 1024, 1)
except Exception:
    pass

# --- state.json (bm-b uses state.json) ---
sp = os.path.join(ROOT, "state.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 507
st["note"] = ("r507: pool shared-face settled via S6 compute_audit sync_face "
              "(LOWAMP-P2-NULLS ghost-ready healed -> 18/18 done, bm-a burn "
              "claim provenance) + N1-W9 supply FIRED (12 per-shard entries "
              "PERPETUAL-N1-W9-SHARD-0..11 materialized, never-dry live==0) + "
              "S6 34 legs rc0 + smoke 47/47; daemon W9 claims auto-resume "
              "post-push (r351 yield)")
st["last_round_at"] = ts
st["last_round_ts"] = ts
st["ts"] = ts
st["updated"] = ts
st["updated_at"] = ts
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# --- heartbeat ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts
hb["current_task"] = ("r507: N1-W9 wave LIVE (12 shards materialized, daemon "
                      "auto-claim resumes post-push); LOWAMP-P2 finalize gate "
                      "unblocked (18/18 done shared face settled); "
                      "CODELY >50KB hot-cold reorg in-window")
hb["cpu_cores"] = 16
hb["free_ram_gb"] = free_ram
hb["gpu_free_vram_gb"] = gpu_free
hb["cpu_util_pct"] = cpu_pct
hb["round_no"] = 507
hb["verdict"] = (
    "r507 products: (1) pool shared-face settle (compute_audit sync_face) "
    "healed LOWAMP-P2-NULLS ghost-ready -> 18/18 done (bm-a burn claim "
    "provenance, finalize gate unblocked for bm-a lane); (2) N1-W9 supply "
    "FIRED per O-1332 sec.1.2 chain: 12 per-shard entries materialized "
    "(live==0 starve->ignite, compute_audit FLAG:supply_floor answered "
    "in-round); (3) S6 34 legs rc0 (reconcile DRIFT recorded pre-settle "
    "streak reset, audit settle, watermark insufficient_history n=1, "
    "clock ORANGE_COOL cap50, REPORT/LIVE 2026-10-01 regenerated, "
    "token delta=0); smoke 47/47; attrition CLEAN")
# orders_ack unchanged (no new orders; O-1332 already acked r505)
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# --- self-verify heartbeat epoch is JSON int (R170/R178 law) ---
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int!"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"], "clock fmt!"

# --- inbox: move processed bm-b messages ---
proc = os.path.join(ROOT, "fleet", "inbox", "processed")
os.makedirs(proc, exist_ok=True)
for fn in ["MSG-20261001-1331-bmc-bmb.md",
           "MSG-20261001-1345-bma-bmb-lowamp-p2-nulls.md"]:
    src = os.path.join(ROOT, "fleet", "inbox", fn)
    if os.path.exists(src):
        shutil.move(src, os.path.join(proc, fn))
        print("inbox processed:", fn)

print("CLOSE_OK ts=%s epoch=%d cpu=%s free_ram=%s gpu_free=%s"
      % (ts, epoch, cpu_pct, free_ram, gpu_free))
