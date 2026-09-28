"""r385 bm-b: census worker-tree probe — parent 28820 idle; check children."""
import subprocess
import time

ps = r"""
Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' } |
 ForEach-Object { '{0}|{1}|{2}' -f $_.ProcessId, $_.ParentProcessId,
   ($_.CommandLine -replace '\s+',' ').Substring(0, [Math]::Min(110, $_.CommandLine.Length)) }
"""
out = subprocess.check_output(
    ["powershell", "-NoProfile", "-Command", ps], text=True).strip()
print("--- procs (pid|ppid|cmd) ---")
print(out)


def cpu(pid):
    q = ("Get-CimInstance Win32_Process -Filter \"ProcessId=%d\" | "
         "ForEach-Object { $_.UserModeTime + $_.KernelModeTime }" % pid)
    return int(subprocess.check_output(
        ["powershell", "-NoProfile", "-Command", q], text=True).strip()) / 1e7


pids = []
for ln in out.splitlines():
    if ln.strip():
        pids.append(int(ln.split("|")[0]))
snap0 = {p: cpu(p) for p in pids}
time.sleep(20)
snap1 = {p: cpu(p) for p in pids}
print("--- cpu delta over 20s ---")
for p in pids:
    print(p, round(snap1[p] - snap0[p], 2), "s")
