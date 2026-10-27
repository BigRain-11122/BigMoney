# r1159 bm-b: one-shot E93 burn launcher (screengapera leg -> SCREENGAPERA json).
# Same reason as run_w21_judge_bmb.ps1: a session-spawned worker dies with the
# CLI job object at the round boundary, so a multi-minute census burn runs under
# a scheduled task instead. Pure ASCII. Log is UTF-8 (PS 5.1 Out-File default is
# UTF-16 = binary garbage on re-read, pit r1012).
$ErrorActionPreference = 'Continue'
$root = 'C:\Fluxgroup\FluxGroup\quant\bigmoney'
Set-Location $root
$logdir = Join-Path $root 'results\e44_midmonth\logs'
New-Item -ItemType Directory -Force -Path $logdir | Out-Null
$log = Join-Path $logdir 'e93_spread.log'
"[$(Get-Date -Format o)] e93 screengapera start" | Out-File -FilePath $log -Append -Encoding utf8
& python scripts\e39_panel_census.py screengapera --gaps 1,5 *>> $log
$rc = $LASTEXITCODE
"[$(Get-Date -Format o)] e93 screengapera exit rc=$rc" | Out-File -FilePath $log -Append -Encoding utf8
exit $rc