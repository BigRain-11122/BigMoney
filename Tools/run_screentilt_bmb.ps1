# r1159 bm-b: one-shot E81 screentilt burn launcher (tilt-era screened twin).
# Why a scheduled task: a session-spawned worker dies with the CLI job object at
# the round boundary (live-fire r1159: the Start-Process child vanished with zero
# log lines), so a multi-minute census burn runs here instead.
# Why cmd /c redirect: PowerShell '>>' writes UTF-16, which turns the log into
# binary garbage on re-read (pit r1012 family). cmd writes raw bytes.
$ErrorActionPreference = 'Continue'
$root = 'C:\Fluxgroup\FluxGroup\quant\bigmoney'
Set-Location $root
$env:PYTHONIOENCODING = 'utf-8'
$logdir = Join-Path $root 'results\e42_tilt_era\logs'
New-Item -ItemType Directory -Force -Path $logdir | Out-Null
$log = Join-Path $logdir 'screentilt.log'
$err = Join-Path $logdir 'screentilt.err'
"[$(Get-Date -Format o)] screentilt start" | Out-File -FilePath $log -Append -Encoding utf8
$cli = 'python -u scripts\e39_panel_census.py screentilt 1>> "' + $log + '" 2>> "' + $err + '"'
& cmd.exe /c $cli
$rc = $LASTEXITCODE
"[$(Get-Date -Format o)] screentilt exit rc=$rc" | Out-File -FilePath $log -Append -Encoding utf8
exit $rc