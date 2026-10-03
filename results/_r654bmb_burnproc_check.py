"""r654 bm-b: verify trio FUND NULLS burn processes alive (x3)."""
import subprocess

ps = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
      "Where-Object { $_.CommandLine -match 'fund_' } | "
      "ForEach-Object { \"$($_.ProcessId) :: $($_.CommandLine.Substring(0, [Math]::Min(110, $_.CommandLine.Length)))\" }")
r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                   capture_output=True, text=True, creationflags=0x08000000)
lines = [ln for ln in (r.stdout or "").splitlines() if ln.strip()]
print("burn procs n=%d" % len(lines))
for ln in lines:
    print("BURNPROC:", ln)
