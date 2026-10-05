# _r539bmc_close1.ps1 -- S7 close phase 1: bookkeeping -> close-scan -> add/commit/push (gated).
$root = 'K:\Fluxgroup\FluxGroup\quant\bigmoney'
$env:PYTHONIOENCODING = 'utf-8'
$wrap = Join-Path $root 'Tools\Invoke-SilentExe.ps1'

"=== BOOKKEEPING ==="
$bk = & $wrap -Exe python.exe -ArgString "Tools\_r539bmc_bookkeeping.py" -Cwd $root
"BOOK_RC=$LASTEXITCODE"
$bk

if ($LASTEXITCODE -ne 0) { Write-Output 'ABORT: bookkeeping failed -- no add/commit'; exit 1 }

"=== ORDERS CLOSE SCAN (second face) ==="
$scan = & $wrap -Exe python.exe -ArgString "Tools\_r539bmc_orders_probe.py" -Cwd $root
$scan
$unacked = @($scan | Where-Object { $_ -match '^UNACKED:' }).Count
"UNACKED_COUNT=$unacked"
if ($unacked -gt 0) { Write-Output 'ABORT: unacked orders at close -- handle before commit'; exit 1 }

"=== STATUS / ADD / COMMIT / PUSH ==="
$w = & $wrap -Exe git.exe -ArgString 'status --porcelain' -Cwd $root -StdoutOnly
$wl = if ($w) { $w -split "`n" } else { @() }
"DIRTY_FACES=$($wl.Count)"
$wl | Select-Object -First 40

& $wrap -Exe git.exe -ArgString 'add -A' -Cwd $root | Out-Null
"ADD_RC=$LASTEXITCODE"

Set-Content -Path "$env:TEMP\msg_r539b.txt" -Value 'round 539: golden-week standby -- QA pack r539 (12th consecutive determinism evidence) + S6 38/38 first-pass zero-heal + orders/D-19/group-orders triple MATCH' -Encoding ascii
$c = & $wrap -Exe git.exe -ArgString "commit -F `"$env:TEMP\msg_r539b.txt`"" -Cwd $root
"COMMIT_RC=$LASTEXITCODE"
if ($c) { ($c -split "`n") | Select-Object -First 3 }

$head = & $wrap -Exe git.exe -ArgString 'rev-parse HEAD' -Cwd $root -StdoutOnly
"HEAD=$head"

$p = & $wrap -Exe git.exe -ArgString 'push origin main' -Cwd $root
"PUSH_RC=$LASTEXITCODE"
if ($p) { ($p -split "`n") | Select-Object -Last 4 }
