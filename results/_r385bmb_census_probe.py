"""r385 bm-b: census W2B runner liveness probe (cpu-time delta over ~20s window).

Per r384 next-pointer: census final stretch no-kill; this probe decides
"alive-burning" vs "stalled" without touching the runner (read-only).
"""
import json
import subprocess
import time
import os

PID = 28820
CK = r"results\census_fusion_s2\w2b_checkpoint.jsonl"


def cpu_seconds(pid):
    ps = (
        "Get-CimInstance Win32_Process -Filter \"ProcessId=%d\" | "
        "ForEach-Object { $_.UserModeTime + $_.KernelModeTime }" % pid
    )
    out = subprocess.check_output(
        ["powershell", "-NoProfile", "-Command", ps]
    ).decode().strip()
    return int(out) / 1e7  # 100ns units -> seconds


def ws_mb(pid):
    ps = (
        "(Get-Process -Id %d).WorkingSet64/1MB" % pid
    )
    return round(float(subprocess.check_output(
        ["powershell", "-NoProfile", "-Command", ps]
    ).decode().strip()), 1)


probe = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "pid": PID}
try:
    c0 = cpu_seconds(PID)
    ws = ws_mb(PID)
    time.sleep(20)
    c1 = cpu_seconds(PID)
    probe.update(cpu_s0=round(c0, 1), cpu_s1=round(c1, 1),
                 cpu_delta_20s=round(c1 - c0, 1), ws_mb=ws)
    probe["verdict"] = "alive-burning" if (c1 - c0) > 0.5 else "cpu-idle-suspect"
except Exception as e:
    probe["verdict"] = "process-gone"
    probe["err"] = str(e)

lines = [l for l in open(CK, encoding="utf-8") if l.strip()]
probe["checkpoint_entries"] = len(lines)
last = json.loads(lines[-1])
probe["checkpoint_last_i"] = last.get("i")
probe["checkpoint_mtime"] = time.strftime(
    "%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(CK)))

print(json.dumps(probe, ensure_ascii=False, indent=1))
