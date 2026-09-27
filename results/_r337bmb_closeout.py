# r337 bm-b closeout: state.json + heartbeat + round report line (formats preserved: 1-space indent, no trailing newline on state)
import json, time, subprocess, datetime

NOW = datetime.datetime.now()
ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
EPOCH = int(time.time())
RND = 337

# --- fresh machine sampling ---
free_ram_gb = None; cpu_pct = None
try:
    import psutil
    vm = psutil.virtual_memory()
    free_ram_gb = round(vm.available / 1024**3, 1)
    cpu_pct = round(psutil.cpu_percent(interval=1), 1)
except Exception:
    pass
gpu_free_gb = None
try:
    o = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=20)
    gpu_free_gb = round(int(o.stdout.strip().splitlines()[0]) / 1024, 2)
except Exception:
    pass
print("sample:", "ram=", free_ram_gb, "cpu=", cpu_pct, "gpu_free_gb=", gpu_free_gb)

# --- state.json (logs/iteration-loop/state.json, 1-space indent lineage) ---
sp = r"logs\iteration-loop\state.json"
st = json.load(open(sp, encoding="utf-8"))
st.update({
    "round_no": RND,
    "did": "S3 dual closure: (A) W2-A census burn health probe = parent 13148 + 4 workers ~94% each, 32.6k CPU-s = 9.1 core-h, zero crash (5x past r330 point), ckpt first block not yet flushed, ETA 18:40-21:40 window per r334 est; (B) Monday 09-28 new-bar full-chain preflight 8/8 selftests PASS (rev_osc/system_v1/t24x2/aggr 32:32/alloc 15:15/grid/astock); S6 29/29 rc=0 Sunday family; S0 tick designed-tail adopted + rebase zero-conflict",
    "verdict": "green",
    "next": "W2-A burn harvest watch (finalize -> r312 done-flip pool face + T-86 bm-a ticket receipt), ETA 18:40-21:40; Mon 09-28: 09:15 T-91 s3 auto-fire (SIG/BARS replay) + 15:30 T-87 astock first increment + new-bar full chain (preflight 8/8 green); R340 5x HANDOVER bm-b side; 10-01 monthly trio + REGIME_GUARD v3 date gate",
    "last_round_ts": ISO,
    "last_result": "ok",
    "current_task": "r337 closed: W2-A burn probe healthy 9.1 core-h + Monday preflight 8/8 + S6 29/29",
    "updated_at": ISO,
    "last_seen": ISO,
    "ts": NOW.strftime("%Y-%m-%d %H:%M:%S"),
})
json.dump(st, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("state.json round_no ->", RND)

# --- heartbeat fleet/machines/bm-b.json ---
hp = r"fleet\machines\bm-b.json"
hb = json.load(open(hp, encoding="utf-8"))
hb.update({
    "last_seen": ISO,
    "heartbeat_epoch_utc": EPOCH,
    "clock_read": ISO,
    "current_task": st["current_task"],
    "free_ram_gb": free_ram_gb if free_ram_gb is not None else hb.get("free_ram_gb"),
    "cpu_util_pct": cpu_pct if cpu_pct is not None else hb.get("cpu_util_pct"),
    "round_no": RND,
    "verdict": "healthy",
})
if free_ram_gb is not None:
    hb["idle_ram_gb"] = free_ram_gb
    hb["idle_ram_mb"] = int(free_ram_gb * 1024)
    hb["free_ram_mb"] = int(free_ram_gb * 1024)
if cpu_pct is not None:
    hb["cpu_pct"] = cpu_pct
if gpu_free_gb is not None:
    hb["gpu_free_vram_gb"] = gpu_free_gb
    hb["gpu_idle_vram_gb"] = gpu_free_gb
    hb["gpu_free_vram_mb"] = int(gpu_free_gb * 1024)
    hb["gpu_idle_vram_mb"] = int(gpu_free_gb * 1024)
hb["loop_round"] = RND
hb["round"] = RND
json.dump(hb, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("heartbeat round ->", RND, "| ack n=", len(hb.get("orders_ack", [])))

# --- self-verify (three-face law) ---
v1 = json.load(open(sp, encoding="utf-8"))
v2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(v2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in v2["clock_read"] and v2["clock_read"][10] == "T", "clock_read must be T-separated"
assert v2["last_seen"] == ISO
print("SELF-VERIFY OK: epoch int =", v2["heartbeat_epoch_utc"], "| clock T-sep | ack =", len(v2["orders_ack"]))

# --- token meter delta line ---
try:
    tu = json.load(open(r"results\token_usage.json", encoding="utf-8"))
    print("token:", json.dumps({k: tu.get(k) for k in ("delta_vs_prev", "total_state_tokens_est", "total_report_tokens_est")}, ensure_ascii=False)[:200])
except Exception as e:
    print("token read err:", e)
