# r672 bm-a heartbeat write (fleet/machines/bm-a.json; epoch int + T-sep clock, F7 contract)
import json, io, time, datetime, subprocess

HP = r"fleet\machines\bm-a.json"
hb = json.load(io.open(HP, encoding="utf-8"))

now = datetime.datetime.now().astimezone()
hb["last_seen"] = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")

def wmic_free():
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"],
            capture_output=True, timeout=60)
        return float(r.stdout.decode().strip())
    except Exception:
        return None

def gpu_free():
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "$p=Get-Process -Name 'ollama*','python*' -ErrorAction SilentlyContinue; 0"],
            capture_output=True, timeout=60)
        return None  # VRAM probe delegated to keepwarm face; honest None
    except Exception:
        return None

hb["idle_ram_gb"] = wmic_free()
hb["cpu_cores"] = 32
hb["gpu_idle_vram_gb"] = gpu_free()
hb["verdict"] = "alive"
hb["current_task"] = ("r672 wrapped: THEME-JUDGE-P1 judged_negative closeout completed "
                      "(treasure row + idempotent finalize re-verify); fund trio NULLS "
                      "burn-done watch; piece-4 trio-gated ETA 10-05..09")
# preserve orders_ack field untouched

with io.open(HP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
re = json.load(io.open(HP, encoding="utf-8"))
assert isinstance(re["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in re["clock_read"], "clock must be T-separated"
print("HEARTBEAT OK epoch=", re["heartbeat_epoch_utc"], "clock=", re["clock_read"],
      "orders_ack preserved:", len(re.get("orders_ack", [])))
