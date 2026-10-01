import io, json, time, subprocess

NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# ---- state.json (indent=1, LF) ----
p = "state.json"
d = json.load(io.open(p, encoding="utf-8"))
d["round_no"] = 501
d["note"] = ("r501: W6 closeout chain (shard-6 product c9653b39e + 11-entry ghost double-flip "
             "AA-yield to bm-a sweep 2087ece58 + MSG-103x receipt) + N1-W7 wave supply LANDED "
             "(prereg frozen bands A 26100..28099/B 28100..28299 both-tails skip-over, selftest "
             "8/8+3d, gate ADMIT, 12 entries materialized pool ready 0->12, commit 1d97134bf) "
             "+ S6 34 legs rc0 + rebase 3-refusal net-path pit-law to CODELY")
d["last_round_at"] = NOW
d["last_round_ts"] = NOW
d["ts"] = NOW
d["updated"] = NOW
d["updated_at"] = NOW
io.open(p, "w", encoding="utf-8", newline="").write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
print("state.json -> round 501")

# ---- heartbeat fleet/machines/bm-b.json (indent=1, LF) ----
p = "fleet/machines/bm-b.json"
d = json.load(io.open(p, encoding="utf-8"))
print("hb keys:", list(d.keys()))
free = subprocess.run(["powershell", "-NoProfile", "-Command",
    "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB"], capture_output=True, text=True)
free_ram = round(float(free.stdout.strip()), 1)
gpu = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                     capture_output=True, text=True)
gpu_free = int(gpu.stdout.strip().splitlines()[0]) if gpu.returncode == 0 else None
d["last_seen"] = NOW
d["heartbeat_epoch_utc"] = EPOCH
d["clock_read"] = NOW
d["current_task"] = ("r501: N1-W7 wave supply (prereg+bands+12 entries materialized, pool ready 0->12) "
                     "+ W6 closeout chain (shard-6 product, ghost heal yield, finalize landed K-lift +0.0003) "
                     "+ S6 34 legs rc0")
d["cpu_cores"] = 16
if "free_ram_gb" in d:
    d["free_ram_gb"] = free_ram
for k in list(d.keys()):
    if "gpu" in k.lower() and gpu_free is not None and not isinstance(d[k], (dict, list)):
        d[k] = gpu_free
if "verdict" in d:
    d["verdict"] = ("r501 products: W7 supply 12-ready + W6 finalize chain closed (K=13320, "
                    "ledger 377647) + pool truth healed; watermark red face root-fixed (supply restored)")
io.open(p, "w", encoding="utf-8", newline="").write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")

# post-verify: epoch must be JSON int (R170/R178 law)
h = json.load(io.open(p, encoding="utf-8"))
assert isinstance(h["heartbeat_epoch_utc"], int), "epoch not int"
print("heartbeat ->", NOW, "epoch:", h["heartbeat_epoch_utc"], "int OK | free_ram:", free_ram, "gpu_free:", gpu_free)
