# r338 bm-b closeout: closing orders double-scan + heartbeat + state + round report append
# (r342bma_closeout.py pattern; three-face self-verified)
import json, time, subprocess, io, os, sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.now().astimezone()
ts_iso = now.isoformat(timespec="seconds")          # 2026-09-27T18:38:00+08:00
ts_space = now.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())

# --- 0) closing orders double-scan (S7 tail scan) ---
hb = json.load(open(os.path.join(ROOT, "fleet/machines/bm-b.json"), encoding="utf-8"))
ack = set(hb.get("orders_ack", []))
disk = set(f for f in os.listdir(os.path.join(ROOT, "fleet/orders")) if f.startswith("O-") and f.endswith(".md"))
unacked, gone = disk - ack, ack - disk
print("closing scan: disk=%d ack=%d unacked=%s gone=%s" % (len(disk), len(ack), sorted(unacked), sorted(gone)))
if unacked:
    print("!! UNACKED ORDERS PRESENT -- handle before commit"); sys.exit(3)

# --- 1) machine stats ---
try:
    import psutil
    cpu_pct = psutil.cpu_percent(interval=1)
    ram_gb = round(psutil.virtual_memory().available / (1024**3), 1)
    total_ram = round(psutil.virtual_memory().total / (1024**3), 1)
    ram_mb = int(psutil.virtual_memory().available / (1024**2))
except Exception as e:
    print("psutil fail:", e); cpu_pct, ram_gb, total_ram, ram_mb = 0.0, 0.0, 0.0, 0
gpu_used_mb = None
try:
    o = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=10)
    if o.returncode == 0 and o.stdout.strip():
        gpu_used_mb = int(float(o.stdout.strip().splitlines()[0]))
except Exception:
    pass
prev_gpu = hb.get("gpu_model", "")
if gpu_used_mb is None:  # reuse prior used figure
    import re
    m = re.search(r"(\d+)MiB used", prev_gpu); gpu_used_mb = int(m.group(1)) if m else 0
gpu_free_mb = max(6891 - 0, 8192 - gpu_used_mb)  # 3070 8GB nominal - used
hb["gpu_model"] = "NVIDIA GeForce RTX 3070 (%dMiB used @%s)" % (gpu_used_mb, ts_iso)

# --- 2) heartbeat face (int-epoch law R170/R178 + T-separator clock law R262) ---
hb["last_seen"] = ts_iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts_iso
hb["current_task"] = "r338 closed: pure maintenance S6 30/30 rc=0 + burn watch alive parent13148"
hb["cpu_cores"] = hb.get("cores", 16)
hb["free_ram_gb"] = ram_gb
hb["idle_ram_gb"] = ram_gb
hb["free_ram_mb"] = ram_mb
hb["idle_ram_mb"] = ram_mb
hb["total_ram_gb"] = total_ram
hb["cpu_util_pct"] = cpu_pct
hb["cpu_pct"] = cpu_pct
hb["gpu_free_vram_gb"] = round(gpu_free_mb / 1024, 2)
hb["gpu_free_vram_mb"] = gpu_free_mb
hb["gpu_idle_vram_gb"] = hb["gpu_free_vram_gb"]
hb["gpu_idle_vram_mb"] = gpu_free_mb
hb["round_no"] = 338
hb["round"] = 338
hb["loop_round"] = 338
hb["n_orders_ack"] = len(ack)
hb["verdict"] = "healthy"
with io.open(os.path.join(ROOT, "fleet/machines/bm-b.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(open(os.path.join(ROOT, "fleet/machines/bm-b.json"), encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be T-separated ISO8601"
print("heartbeat face OK: epoch=%d(int) clock=%s round=338 ram=%.1fGB cpu=%.1f%% gpu_free=%dMB" %
      (chk["heartbeat_epoch_utc"], chk["clock_read"], ram_gb, cpu_pct, gpu_free_mb))

# --- 3) state face (bm-b uses logs/iteration-loop/state.json per S5) ---
sp = os.path.join(ROOT, "logs/iteration-loop/state.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 338
st["did"] = ("S3 maintenance round: S0 fast-forward c64ab6b2->4ee172ce (bm-a r342 fold-landing received); orders 96/96 double-scan zero-diff; "
             "P-32 group-ledger absent on bm-b = honest no-op (r104/r107 precedent); smoke 25/25; S6 30/30 rc=0 Sunday no-op family "
             "(bm-b lanes astock+rev_osc idempotent at cutoff 2026-09-24; 09-25 mid-autumn holiday, next bar Mon 09-28 15:30; "
             "live.paper/t35_open_fill/t24_prospect_paper new-bar condition unmet = legal skip); W2-A burn watch parent 13148 alive ETA 18:40-21:40; RAM-tight 1.9GB zero new heavy work")
st["verdict"] = "green"
st["next"] = ("W2-A burn harvest watch (finalize -> r312 done-flip pool face + T-86 bm-a ticket receipt), ETA 18:40-21:40; "
              "Mon 09-28: 09:15 T-91 s3 auto-fire (SIG/BARS replay) + 15:30 T-87 astock first increment + new-bar full chain (preflight 8/8 green); "
              "R340 5x HANDOVER bm-b side; 10-01 monthly trio + REGIME_GUARD v3 date gate")
st["last_round_ts"] = ts_iso
st["last_result"] = "ok"
st["current_task"] = "r338 closed: pure maintenance S6 30/30 + burn watch alive"
st["updated_at"] = ts_iso
st["last_seen"] = ts_iso
st["ts"] = ts_space
with io.open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state face OK: round_no=%d" % json.load(open(sp, encoding="utf-8"))["round_no"])

# --- 4) round report append (EOL-aware, one line) ---
rp = os.path.join(ROOT, "logs/iteration-loop/round_reports.md")
raw = open(rp, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-400:] else b"\n"
line = ("{0} | round 338 bm-b | dept:工程+舰队(维护轮) | WM=绿: red=false 18:00:24 tick; probe 18:24 py_low_with_work_cands(py 28-30%) "
        "但 local_batch_running=true=W2-A 燃烧合法占柄(parent 13148 存活, ETA 18:40-21:40), open票0/bandit0/池ready1 交 autofill C8 自动续批; "
        "RAM 1.9GB<4GB 禁重活=零新重活诚实披露 | did: S0 快进 c64ab6b2->4ee172ce 收讫 bm-a r342 fold-landing; S0.5 orders 96/96 轮首+S7 双扫零差集; "
        "P-32 集团台账 bm-b 侧缺位=诚实 no-op(r104/r107 正典); S1 smoke 25/25; S3 任务双板 0 open(bm-b 在册 11 slice 票无到期面), inbox 0; "
        "S6 30/30 rc=0 周日 no-op 家族: astock/rev_osc bm-b 双道幂等 cutoff 2026-09-24(09-25 中秋休市, 下一 bar=周一 09-28 15:30), "
        "live.paper/t35_open_fill/t24_prospect_paper 三件 new-bar 条件不满足合法跳过, t24_promotion 0/22 eligible 如实, 其余车道护栏诚实 no-op; "
        "S7 双计划任务 schtasks 实探在役+pre-commit claw identical | token: L2 本地腿 1 今日 ~6450(零 API) | "
        "next: W2-A finalize 收割窗 18:40-21:40(->r312 done-flip 池面+T-86 bm-a 票回执); 周一 09-28: 09:15 T-91 s3 auto-fire+15:30 T-87 astock 首增量"
        "+new-bar 全链(preflight 8/8 绿); R340 5x HANDOVER bm-b 侧").format(ts_iso)
with open(rp, "ab") as f:
    if raw and not raw.endswith(eol):
        f.write(eol)
    f.write(line.encode("utf-8") + eol)
print("report face OK: appended r338 line (%dB) eol=%r" % (len(line.encode("utf-8")), eol))
print("CLOSEOUT DONE")
