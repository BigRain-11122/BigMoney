import json, io, time, datetime, shutil, os

# 1) state.json round_no 670 -> 671
sp = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\state.json"
s = json.load(io.open(sp, encoding="utf-8"))
s["round_no"] = 671
with io.open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
assert json.load(io.open(sp, encoding="utf-8"))["round_no"] == 671
print("state round_no=671 ok")

# 2) heartbeat update
hp = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-b.json"
h = json.load(io.open(hp, encoding="utf-8"))
now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec="seconds")
epoch = int(time.time())
assert isinstance(epoch, int)
h["last_seen"] = iso
h["clock_read"] = iso
h["heartbeat_epoch_utc"] = epoch
h["round_no"] = 671
h["round_no_label"] = "round 671 (bm-b)"
h["current_task"] = "trio NULLS burn care in flight (V38.1%/Q29.6%/D21.9%, ETAs 10-06/10-07/10-08 per results/trio_burn_eta.json) + finalize candidate window watch"
h["verdict"] = "healthy: r671 S6 30/30 rc0 (CEO faces REPORT-2026-10-04+LIVE-2026-10-04 refreshed) + trio burn-rate/ETA probe delivered + orders 153/153 + D-19 double MATCH"
h["ts"] = iso
h["updated"] = iso
# fresh resource readings (light probe)
import subprocess
try:
    cpu = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"],
                         capture_output=True, timeout=30).stdout.decode().strip()
    h["cpu_util_pct"] = float(cpu)
except Exception:
    pass
try:
    ram = subprocess.run(["powershell", "-NoProfile", "-Command",
          "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)"],
         capture_output=True, timeout=30).stdout.decode().strip()
    h["free_ram_gb"] = float(ram)
    h["idle_ram_gb"] = float(ram)
    h["ram_avail_gb"] = float(ram)
except Exception:
    pass
with io.open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-sep"
print("heartbeat ok epoch=%d clock=%s" % (chk["heartbeat_epoch_utc"], chk["clock_read"]))

# 3) inbox msg -> processed
src = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\inbox\MSG-2026-10-04-1245-bma-all.md"
dst = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\inbox\processed\MSG-2026-10-04-1245-bma-all.md"
if os.path.exists(src):
    shutil.move(src, dst)
    print("inbox msg moved to processed")
else:
    print("inbox msg already gone")
print("S7 closeout script done")
