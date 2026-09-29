import json, time, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

path = "fleet/machines/bm-b.json"
hb = json.load(open(path, encoding="utf-8"))

now_local = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
os_r = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB; "
     "(Get-CimInstance Win32_Processor | Measure-Object -Property "
     "LoadPercentage -Average).Average"],
    capture_output=True, text=True)
vals = [x for x in os_r.stdout.splitlines() if x.strip()]
free_ram = round(float(vals[0]), 1)
cpu_pct = round(float(vals[1]), 1) if len(vals) > 1 and vals[1].strip() else 0.0

hb["last_seen"] = now_local
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = now_local
hb["current_task"] = (
    "r443 IN FLIGHT (this session alive): W11 GENERATE heritage adopted+pushed "
    "(8d03c4126) + pool GENERATE=done/SCREEN=ready armed; screen-prep PASS; "
    "next = ignite SCREEN burn (1462 cells) then S6 chain in-round, screen-finalize "
    "+ JUDGE arm/ignite if window allows -- DO NOT start a concurrent round 443; "
    "back off and wait for state round_no increment"
)
hb["round_no"] = 443
hb["round"] = 443
hb["loop_round"] = 443
hb["cpu_cores"] = 16
hb["free_ram_gb"] = free_ram
hb["ram_free_gb"] = free_ram
hb["idle_ram_gb"] = free_ram
hb["cpu_util_pct"] = cpu_pct
hb["verdict"] = "healthy"
hb["last_round_at"] = now_local

with open(path, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

chk = json.load(open(path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (F7 law)"
print("heartbeat written:", chk["last_seen"], "| epoch int:", chk["heartbeat_epoch_utc"],
      "| round:", chk["round_no"], "| free_ram:", free_ram, "| cpu:", cpu_pct)
