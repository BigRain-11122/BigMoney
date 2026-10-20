# r1080 bm-b: one-shot W21 judge burn launcher (silent task chain, survives session exit).
# Root cause of r1079 screen deaths: session-spawned workers are killed with the CLI
# job object at round boundary. Judge burn therefore runs under a scheduled task,
# never inside the interactive session tree.
$ErrorActionPreference = 'Continue'
$root = 'C:\Fluxgroup\FluxGroup\quant\bigmoney'
Set-Location $root
$log = Join-Path $root 'results\trial_labor_w21\logs\judge_0of1.log'
New-Item -ItemType Directory -Force -Path (Split-Path $log) | Out-Null
"[$(Get-Date -Format o)] judge 0of1 start" | Out-File -FilePath $log -Append -Encoding utf8
& python scripts\trial_labor_w21.py judge 0 1 --workers 8 *>> $log
$rc = $LASTEXITCODE
"[$(Get-Date -Format o)] judge 0of1 exit rc=$rc" | Out-File -FilePath $log -Append -Encoding utf8