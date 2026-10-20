# r1080 bm-b: W21 judge-finalize (long: nulls battery) -- runs outside the session tree.
$ErrorActionPreference = 'Continue'
$root = 'C:\Fluxgroup\FluxGroup\quant\bigmoney'
Set-Location $root
$log = Join-Path $root 'results\trial_labor_w21\logs\judge_finalize.log'
New-Item -ItemType Directory -Force -Path (Split-Path $log) | Out-Null
"[$(Get-Date -Format o)] judge-finalize start" | Out-File -FilePath $log -Append -Encoding utf8
& python scripts\trial_labor_w21.py judge-finalize *>> $log
$rc = $LASTEXITCODE
"[$(Get-Date -Format o)] judge-finalize exit rc=$rc" | Out-File -FilePath $log -Append -Encoding utf8