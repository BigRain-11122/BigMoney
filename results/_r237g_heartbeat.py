# r237 (bm-a): heartbeat update -- fleet/machines/bm-a.json (own file only,
# r191 identity-first law; epoch must be JSON int per R170/R178 law)
import json
import time
import datetime as dt
import subprocess

m = json.load(open("fleet/machines/bm-a.json", encoding="utf-8-sig"))
epoch = int(time.time())
clock = dt.datetime.now().astimezone().isoformat(timespec="seconds")

cpu = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; "
     "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1); "
     "(Get-CimInstance Win32_VideoController | Where-Object {$_.Name -match 'NVIDIA|AMD|GPU'} | Measure-Object -Property AdapterRAM -Sum).Sum"],
    capture_output=True, timeout=60)
vals = cpu.stdout.decode("utf-8", "replace").strip().splitlines()
cpu_pct = float(vals[0]) if vals and vals[0].strip() else None
free_ram = float(vals[1]) if len(vals) > 1 and vals[1].strip() else None

m["last_seen"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
m["current_task"] = "R237 done: T-39 moneyflow R236 amendment family port (selftest 21/21, zero behavior change on in-flight first-pull); idle monitor"
m["cpu_cores"] = 32
m["cpu_pct"] = cpu_pct
m["free_ram_gb"] = free_ram
m["verdict"] = "py_low_board_clear legal idle (0 open/0 bandit/pool ready 0); smoke 25/25"
m["heartbeat_epoch_utc"] = epoch
m["clock_read"] = clock

raw = json.dumps(m, ensure_ascii=False, indent=1)
open("fleet/machines/bm-a.json", "wb").write(raw.replace("\n", "\r\n").encode("utf-8"))

back = json.load(open("fleet/machines/bm-a.json", encoding="utf-8-sig"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
print("heartbeat OK: epoch=%d (int) clock=%s cpu=%s free_ram=%s" % (
    back["heartbeat_epoch_utc"], back["clock_read"], cpu_pct, free_ram))
