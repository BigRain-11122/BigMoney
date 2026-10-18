# r1089 bm-c: F-20261017-01 fix selftest. Live-fire tree-kill test of the
# Kill-RoundTree function EXTRACTED VERBATIM from Tools/iteration_loop.ps1
# (deep-tree proof: root -> mid -> leaf, all three must die; one-level kill
# would leave the leaf alive = the 2026-10-17 starvation root cause).
# Also runs spawn_gate.ps1 selftest lanes + PS parser checks.
# Pure ASCII. Read-only except the dummy tree it creates and kills.
$ErrorActionPreference = 'Continue'
$root = 'K:\Fluxgroup\FluxGroup\quant\bigmoney'
Set-Location $root

# --- 1. PS parser check on both edited files ---
$errs = 0
foreach ($f in @('Tools\iteration_loop.ps1', 'Tools\spawn_gate.ps1')) {
    $tokens = $null; $parseErrs = $null
    [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path $f), [ref]$tokens, [ref]$parseErrs) | Out-Null
    Write-Output ("parser {0}: {1} errors" -f $f, $parseErrs.Count)
    $errs += $parseErrs.Count
}
if ($errs -gt 0) { Write-Output 'SELFTEST FAIL: parser errors'; exit 1 }

# --- 2. ASCII purity check (iteration_loop ENCODING RULE family) ---
foreach ($f in @('Tools\iteration_loop.ps1', 'Tools\spawn_gate.ps1')) {
    $bytes = [System.IO.File]::ReadAllBytes((Resolve-Path $f))
    $nonAscii = @($bytes | Where-Object { $_ -gt 127 }).Count
    Write-Output ("ascii {0}: non-ascii bytes={1}" -f $f, $nonAscii)
    if ($nonAscii -gt 0) { Write-Output 'SELFTEST FAIL: non-ASCII bytes in ENCODING-RULE file'; exit 1 }
}

# --- 3. spawn_gate selftest lanes ---
$probeOut = & powershell -NoProfile -ExecutionPolicy Bypass -File Tools\spawn_gate.ps1 -ProbeOnly
Write-Output "spawn_gate PROBE: $probeOut"
$goOut = & powershell -NoProfile -ExecutionPolicy Bypass -File Tools\spawn_gate.ps1 -Cap 99 -ProbeOnly
Write-Output "spawn_gate forced-GO lane: $goOut"
$tmpLedger = Join-Path $env:TEMP ("sg_selftest_" + (Get-Date -Format 'yyyyMMdd_HHmmss') + ".jsonl")
& powershell -NoProfile -ExecutionPolicy Bypass -File Tools\spawn_gate.ps1 -Cap 0 -Ledger $tmpLedger
Write-Output ("spawn_gate forced-DEFER rc=" + $LASTEXITCODE)
if ($LASTEXITCODE -ne 3) { Write-Output 'SELFTEST FAIL: forced-DEFER lane rc != 3'; exit 1 }
if (Test-Path $tmpLedger) { Remove-Item $tmpLedger -Force }

# --- 4. live-fire tree-kill test (function extracted verbatim from the file) ---
$src = Get-Content -Raw -Encoding ASCII 'Tools\iteration_loop.ps1'
$s = $src.IndexOf('function Kill-RoundTree')
$e = $src.IndexOf('# ---- single-instance')
if ($s -lt 0 -or $e -lt 0 -or $e -le $s) { Write-Output 'SELFTEST FAIL: function extraction anchors missing'; exit 1 }
$funcs = $src.Substring($s, $e - $s)
function Log([string]$m) { Write-Output ("  [test-Log] $m") }
Invoke-Expression $funcs

$leaf = Join-Path $env:TEMP ('bmc_tree_leaf_' + (Get-Date -Format 'HHmmss') + '.ps1')
$mid = Join-Path $env:TEMP ('bmc_tree_mid_' + (Get-Date -Format 'HHmmss') + '.ps1')
$rootFile = Join-Path $env:TEMP ('bmc_tree_root_' + (Get-Date -Format 'HHmmss') + '.ps1')
Set-Content -Path $leaf -Value 'Start-Sleep -Seconds 120' -Encoding ASCII
$midContent = @"
Start-Process powershell -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File','$leaf') -WindowStyle Hidden | Out-Null
Start-Sleep -Seconds 120
"@
Set-Content -Path $mid -Value $midContent -Encoding ASCII
$rootContent = @"
Start-Process powershell -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File','$mid') -WindowStyle Hidden | Out-Null
Start-Sleep -Seconds 120
"@
Set-Content -Path $rootFile -Value $rootContent -Encoding ASCII
$rootProc = Start-Process powershell -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',$rootFile) -WindowStyle Hidden -PassThru
$leafPid = 0
$midPid = 0
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Milliseconds 500
    $kid = @(Get-CimInstance Win32_Process -Filter "ParentProcessId=$($rootProc.Id)" -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -eq 'powershell.exe' })
    if ($kid.Count -gt 0) {
        $midPid = $kid[0].ProcessId
        $gk = @(Get-CimInstance Win32_Process -Filter "ParentProcessId=$($midPid)" -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -eq 'powershell.exe' })
        if ($gk.Count -gt 0) { $leafPid = $gk[0].ProcessId; break }
    }
}
if ($leafPid -eq 0) { Write-Output 'SELFTEST FAIL: dummy tree never materialized (no grandchild)'; if ($rootProc) { Stop-Process -Id $rootProc.Id -Force -ErrorAction SilentlyContinue }; exit 1 }
Write-Output ("dummy tree: root={0} mid={1} leaf={2}" -f $rootProc.Id, $midPid, $leafPid)
$descendants = Kill-RoundTree $rootProc.Id
Write-Output ("Kill-RoundTree returned descendants={0}: {1}" -f $descendants.Count, ($descendants -join ','))
Start-Sleep -Seconds 2
$rootAlive = [bool](Get-Process -Id $rootProc.Id -ErrorAction SilentlyContinue)
$midAlive = [bool](Get-Process -Id $midPid -ErrorAction SilentlyContinue)
$leafAlive = [bool](Get-Process -Id $leafPid -ErrorAction SilentlyContinue)
Write-Output ("post-kill: root_alive={0} mid_alive={1} leaf_alive={2}" -f $rootAlive, $midAlive, $leafAlive)
if ($rootAlive -or $midAlive -or $leafAlive) {
    Write-Output 'SELFTEST FAIL: deep-tree survivors after Kill-RoundTree (the exact F-20261017-01 defect)'
    if ($midAlive) { Stop-Process -Id $midPid -Force -ErrorAction SilentlyContinue }
    if ($leafAlive) { Stop-Process -Id $leafPid -Force -ErrorAction SilentlyContinue }
    exit 1
}
if ($descendants.Count -lt 2) { Write-Output 'SELFTEST FAIL: descendant collection missed a level'; exit 1 }
Remove-Item $leaf, $mid -Force -ErrorAction SilentlyContinue
Write-Output 'SELFTEST PASS: parser 0 errors + ascii pure + spawn_gate lanes OK + deep-tree kill 3/3 dead + descendant chain collected recursively'
exit 0
