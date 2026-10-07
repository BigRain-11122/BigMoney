"""r702 bm-c W14 judge watch receipt: process liveness + RAM gate + recent
output faces. Zero-window law: CIM query via powershell child carries
CREATE_NO_WINDOW (0x08000000); RAM via ctypes GlobalMemoryStatusEx (no
subprocess). Facts -> results/_r702bmc_w14_watch.json."""
import ctypes
import glob
import json
import os
import subprocess
import time

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
OUT = os.path.join(REPO, "results", "_r702bmc_w14_watch.json")
CREATE_NO_WINDOW = 0x08000000
now = time.time()

facts = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00")}

ps = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe' or "
      "Name='pythonw.exe'\" | Where-Object {$_.CommandLine -match "
      "'trial_labor_w14'} | Select-Object ProcessId,CreationDate,"
      "CommandLine | ConvertTo-Json -Compress")
r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace", creationflags=CREATE_NO_WINDOW)
raw = (r.stdout or "").strip()
facts["cim_raw"] = raw[:600]
procs = []
if raw:
    try:
        j = json.loads(raw)
        for it in (j if isinstance(j, list) else [j]):
            procs.append({"pid": it.get("ProcessId"),
                          "created": it.get("CreationDate"),
                          "cmd": (it.get("CommandLine") or "")[:160]})
    except Exception as e:
        facts["cim_parse_err"] = str(e)[:200]
facts["judge_procs"] = procs

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
m = MEMORYSTATUSEX()
m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
facts["ram_free_gb"] = round(m.ullAvailPhys / (1024 ** 3), 1)
facts["ram_gate_6g_pass"] = facts["ram_free_gb"] >= 6.0

recent = []
for pat in (r"results\trial_labor_w14*", r"results\trial_labor_w14\**",
            r"results\w14*", r"results\trial_labor\**",
            r"results\w14\**", r"results\judge\**"):
    for f in glob.glob(os.path.join(REPO, pat)):
        try:
            st = os.stat(f)
        except OSError:
            continue
        age = (now - st.st_mtime) / 60.0
        if age < 240:
            recent.append({"age_min": round(age, 1), "size": st.st_size,
                           "path": os.path.relpath(f, REPO)})
facts["recent_faces"] = sorted(recent, key=lambda x: x["age_min"])[:25]
facts["burn_alive"] = bool(procs)

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(facts, fh, ensure_ascii=False, indent=1)
print(json.dumps({"burn_alive": facts["burn_alive"], "n_procs": len(procs),
                  "ram_free_gb": facts["ram_free_gb"],
                  "gate_pass": facts["ram_gate_6g_pass"],
                  "recent_n": len(recent)}, ensure_ascii=False))
