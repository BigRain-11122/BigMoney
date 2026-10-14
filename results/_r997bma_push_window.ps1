# r997 bm-a writer-pause window (E42 methodology): pause repo-writer tasks,
# rebase onto origin, push, re-enable tasks. Zero-window per U060.
$ErrorActionPreference = "Continue"
$repo = "C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
$git = "C:\Program Files\Git\cmd\git.exe"
$tasks = @("Bigmoney-ResidentDispatcher","Bigmoney-Autofill","Bigmoney-SatEngine-bm-b","Bigmoney-PoolWorker")

# 1) pause writers
foreach ($t in $tasks) {
  & "C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\Tools\Invoke-SilentExe.ps1" -Exe schtasks -ArgString "/change /tn $t /disable" | Out-Null
}
Write-Output "WRITERS PAUSED"

# 2) commit any residual runtime face (single sweep)
Set-Location $repo
& $git add -A 2>&1 | Out-Null
$st = & $git status --short
if ($st) {
  & $git commit -m "round 997 addendum: runtime faces (writer-pause window)" 2>&1 | Select-Object -Last 1
}

# 3) rebase + push
$rb = & $git pull --rebase 2>&1 | Select-Object -Last 3
Write-Output "REBASE: $rb"
$ps = & $git push origin 2>&1 | Select-Object -Last 3
Write-Output "PUSH: $ps"

# 4) re-enable writers
foreach ($t in $tasks) {
  & "C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\Tools\Invoke-SilentExe.ps1" -Exe schtasks -ArgString "/change /tn $t /enable" | Out-Null
}
Write-Output "WRITERS RE-ENABLED"

# 5) verify
$behind = & $git rev-list --count "HEAD..origin/main"
$tip = & $git rev-parse --short HEAD
$origin = & $git rev-parse --short origin/main
Write-Output "VERIFY tip=$tip origin=$origin behind=$behind"
