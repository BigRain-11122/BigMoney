import subprocess

r = subprocess.run(['powershell', '-NoProfile', '-Command',
                    "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
                    "Where-Object {$_.CommandLine -match 'trial_labor_w2|fund_divlowvol|fund_value|judge'} | "
                    "Select-Object ProcessId,CreationDate,@{N='C';E={$_.CommandLine.Substring(0,[Math]::Min(130,$_.CommandLine.Length))}} | ConvertTo-Json"],
                   capture_output=True, text=True)
print('RUNNING:', r.stdout.strip()[:1500] or '(none)')
r2 = subprocess.run(['powershell', '-NoProfile', '-Command', 'Get-Date -Format "HH:mm:ss"'],
                    capture_output=True, text=True)
print('NOW:', r2.stdout.strip())
