# r264 bm-b: heartbeat update (fleet/machines/bm-b.json).
# epoch MUST be JSON int (R170/R178 double-law: value AND type both fixed).
import json
import subprocess
import time
import datetime as dt

P = "fleet/machines/bm-b.json"
raw = open(P, "rb").read()
bom = raw.startswith(b"\xef\xbb\xbf")
crlf = b"\r\n" in raw
txt = raw.decode("utf-8-sig")
d = json.loads(txt)
print("faces: BOM", bom, "CRLF", crlf, "tail_nl", raw.endswith(b"\n"))

# machine stats via built-ins (no external deps)
try:
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1);"
         "[math]::Round((Get-CimInstance Win32_OperatingSystem).TotalVisibleMemorySize/1MB,1)"],
        capture_output=True, text=True, timeout=30).stdout.split()
    free_ram, total_ram = float(out[0]), float(out[1])
except Exception:
    free_ram = d.get("free_ram_gb", 0)
    total_ram = d.get("total_ram_gb", 0)
try:
    import psutil  # type: ignore
    cpu_util = psutil.cpu_percent(interval=1)
except Exception:
    cpu_util = d.get("cpu_util_pct", 0)

now = dt.datetime.now()
d["last_seen"] = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
d["heartbeat_epoch_utc"] = int(time.time())
d["clock_read"] = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
d["current_task"] = "r264 closeout: post-review debt zeroed + QRS family adjudication delivered; next windows 09-28/10-01"
d["cpu_cores"] = 16
d["free_ram_gb"] = free_ram
d["gpu_free_vram_gb"] = d.get("gpu_free_vram_gb", 2.2)
d["total_ram_gb"] = total_ram
d["cpu_util_pct"] = cpu_util
d["round_no"] = 264
d["verdict"] = "py_low_board_clear legal idle (board closed into 09-28/10-01 windows; pool 1 ready = bm-a batch autofill supply face; research-face round delivered QRS adjudication)"

out_txt = json.dumps(d, ensure_ascii=False, indent=1)
if crlf:
    out_txt = out_txt.replace("\n", "\r\n")
if not raw.endswith(b"\n"):
    out_txt = out_txt  # mirror: no trailing newline
else:
    out_txt += "\n"
open(P, "wb").write(out_txt.encode("utf-8"))

# post-write self-verify (S7 law)
d2 = json.loads(open(P, "rb").read().decode("utf-8-sig"))
assert isinstance(d2["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat written; epoch int-verified:", d2["heartbeat_epoch_utc"],
      "ram free:", free_ram, "cpu%:", cpu_util)
