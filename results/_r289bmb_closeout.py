# -*- coding: utf-8 -*-
"""r289 bm-b S7 closeout: state round 289 + heartbeat + round report line.
Byte-face mirror: heartbeat indent=1/ensure_ascii=False/LF/no-tail-nl;
state indent=1; report tail-newline probe before append (r281 law).
All timestamps derived from one now() instance (r271 law)."""
import datetime
import json
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

# --- state.json (indent=1 mirror) ---
sp = "logs/iteration-loop/state.json"
st = json.loads(open(sp, encoding="utf-8-sig").read())
st["round_no"] = 289
st["did"] = ("r289: 主面同步+集团令修复: 滞留r287/r288 rebase收编bm-a r284-286面5停5解(skill配方"
             "CODELY memory-union/ledger-union零丢失/post_review行级union 2229/快照take-new)并push; "
             "集团令O-20260927-0230(CODELY<=10KB)回执: 复活事故自捕+byte-exact整编面恢复1820B+"
             "append迁archive+r289坑律编码resolver")
st["verdict"] = "main-sync + group-order repair round (resurrection E1 self-caught, fixed+pushed)"
st["next"] = ("p1_results落地即harvest(_r287bmb_cntrend_harvest.py)+pool flip+harvest_note r279③"
              "竞速裁定注记; bm-a rival面 void-at-merge per r288裁定")
st["last_round_ts"] = ts
st["last_result"] = "ok"
st["current_task"] = "CN-TREND-ETF-P1 nulls burn in-flight (harvest on landing) + T-87 akshare refresh on_track"
st["last_tick"] = now.strftime("%H:%M")
st["updated_at"] = ts
st["last_seen"] = iso
st["ts"] = ts
st["last_run"] = "R289 " + iso
st["last_round_at"] = ts
st["updated"] = now.strftime("%Y-%m-%d %H:%M:%S")
open(sp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(st, ensure_ascii=False, indent=1))

# --- heartbeat fleet/machines/bm-b.json (indent=1, no tail-nl, LF) ---
hp = "fleet/machines/bm-b.json"
hb = json.loads(open(hp, encoding="utf-8-sig").read())
hb["last_seen"] = iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = iso
hb["round"] = 289
hb["round_no"] = 289
hb["verdict"] = ("main-sync+group-order-repair round ok; CN-TREND nulls in-flight; "
                 "smoke 25/25; S6 22 legs rc=0; orders 90/90")
hb["current_task"] = st["current_task"]
hb["cpu_pct"] = cpu_pct
hb["cpu_util_pct"] = cpu_pct
hb["free_ram_gb"] = free_ram_gb
hb["idle_ram_gb"] = free_ram_gb
ack = hb.get("orders_ack", "")
if isinstance(ack, list):
    ack = " ".join(ack)
new_order = "O-20260927-0230-bm-a.md"
if new_order not in ack.split():
    ack = (ack + " " + new_order).strip()
hb["orders_ack"] = ack
hb["n_orders_ack"] = len(ack.split())
if gpu_vram:
    hb["gpu_free_vram_mb"] = int(gpu_vram)
    hb["gpu_idle_vram_mb"] = int(gpu_vram)
    hb["gpu_free_vram_gb"] = round(int(gpu_vram) / 1024, 1)
    hb["gpu_idle_vram_gb"] = round(int(gpu_vram) / 1024, 1)
open(hp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(hb, ensure_ascii=False, indent=1))

# --- round report line (tail-newline probe per r281) ---
rp = "logs/iteration-loop/round_reports.md"
raw = open(rp, "rb").read()
if raw and not raw.endswith(b"\n"):
    with open(rp, "ab") as f:
        f.write(b"\n")
line = (
    iso + " | r289 bm-b | dept:研究+工程 | WM-VERDICT: 绿 (red=false healthy lane; CN-TREND "
    "nulls 4-worker burn py~30% real work) | S0: targeted tick/rerun commits unblocked "
    "stranded sync -> pull --rebase onto bm-a r284-286 face, 5 commits replayed 5 stops, "
    "UU resolved per skill recipes (CODELY base-anchored union + compute_audit ledger-union "
    "201->206 + regime union + post_review.jsonl line-union 2157+2118->2229 zero-loss + "
    "snapshot take-new-by-ts) push cb9bf08d | S0.5: orders 89/89 zero new at round start; "
    "group order O-20260927-0230 (CODELY.md<=10KB 集团令·bm-a 8a00f514 executed) RECEIPTED "
    "with incident: my rebase union resurrected the 49KB face (len(side)<len(base) suffix-"
    "empty bug·E1 post-push self-caught) -> byte-exact compacted face restored 1820B 判据绿 + "
    "my 1506B appends migrated archive 750->754 lines + r289 kenglu law encoded in resolver "
    "(full-len+full-prefix assert, compact-face take-side) push f7bcda21; decisions.md absent "
    "on bm-b honest no-op | S1 smoke 25/25 | S6 22 legs rc=0 (audit CLEAN flags=[], wm healthy, "
    "update_daily 0 new rows source cutoff 09-24 Friday bar unpublished honest face, weekend "
    "no-ops bm-a/bm-c lanes, astock refresh on_track, scorecard+daily_report+monitor mirrors, "
    "token snapshot) | CN-TREND nulls in-flight ~70min CPU p1_results pending | 下轮指针: "
    "p1_results落地即harvest(_r287bmb_cntrend_harvest.py)+pool flip+harvest_note r279③竞速"
    "裁定注记; bm-a rival product void-at-merge per r288 ruling"
)
with open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write(line + "\n")

# --- self-verification (R170/R178/R262 laws) ---
hb2 = json.loads(open(hp, encoding="utf-8-sig").read())
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in hb2["clock_read"], "clock_read not T-format"
assert hb2["n_orders_ack"] == 90, "orders_ack count=%s" % hb2["n_orders_ack"]
st2 = json.loads(open(sp, encoding="utf-8-sig").read())
assert st2["round_no"] == 289
print("closeout OK: round=289 epoch=%d clock=%s ack=90 cpu=%s%% ram_free=%sGB"
      % (hb2["heartbeat_epoch_utc"], hb2["clock_read"], cpu_pct, free_ram_gb))
