import io, json, subprocess, time

p = "fleet/machines/bm-b.json"
h = json.load(io.open(p, encoding="utf-8"))

# repair my over-broad "gpu" substring write (values recovered from HEAD)
h["gpu_model"] = "NVIDIA GeForce RTX 3070"
h["gpu_free_vram_gb"] = 2.1       # 2124 MB probe -> GB face
h["gpu_idle_vram_gb"] = 2.1
h["gpu_idle_vram_mb"] = None       # legacy empty at HEAD, preserved
h["gpu_free_vram_mb"] = 2124       # current probe (nvidia-smi), unit-correct
h["ram_free_gb"] = 6.0
h["idle_ram_gb"] = 6.0
h["free_ram_gb"] = 6.0
h["round_no"] = 501
h["round"] = 501
h["loop_round"] = 501
cpu = subprocess.run(["powershell", "-NoProfile", "-Command",
    "(Get-CimInstance Win32_Processor).LoadPercentage"], capture_output=True, text=True)
try:
    h["cpu_util_pct"] = float(cpu.stdout.strip().splitlines()[0])
except Exception:
    pass

io.open(p, "w", encoding="utf-8", newline="").write(json.dumps(h, ensure_ascii=False, indent=1) + "\n")

# post-verify
v = json.load(io.open(p, encoding="utf-8"))
assert isinstance(v["heartbeat_epoch_utc"], int)
assert v["gpu_model"] == "NVIDIA GeForce RTX 3070"
assert v["gpu_free_vram_gb"] == 2.1 and v["gpu_idle_vram_gb"] == 2.1
assert v["round_no"] == 501 and v["round"] == 501 and v["loop_round"] == 501
print("heartbeat repaired: gpu faces restored, rounds=501, epoch int OK, cpu_pct:", v.get("cpu_util_pct"))
