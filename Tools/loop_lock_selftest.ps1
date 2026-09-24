# loop_lock_selftest.ps1 -- D-20260925-03 lock-standard adoption selftest.
# Verifies the pid-liveness lock decision paths of iteration_loop.ps1 and
# watchdog.ps1 via -LockProbeOnly against fabricated lock states. Both scripts
# derive all paths from their own file location, so a throwaway SANDBOX COPY
# isolates everything -- production lock files are never touched. Pure ASCII.
# Matrix per script: no-lock -> TAKE (atomic grab), live-pid -> SKIP at any
# age, dead-pid -> immediate TAKE, legacy fresh -> SKIP, legacy stale -> TAKE.
# Not covered: concurrent CreateNew race (hard to orchestrate deterministically;
# the catch direction is skip = safe). Exit 0 = all PASS, nonzero = fail count.
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$sb = Join-Path $env:TEMP ('bm-lock-selftest-' + $PID + '-' + (Get-Date -Format 'HHmmss'))
$sbTools = Join-Path $sb 'Tools'
$sbLogs = Join-Path $sb 'logs'
New-Item -ItemType Directory -Force $sbTools | Out-Null
New-Item -ItemType Directory -Force (Join-Path $sbLogs 'iteration-loop') | Out-Null
Copy-Item (Join-Path $repo 'Tools\iteration_loop.ps1') $sbTools -Force
Copy-Item (Join-Path $repo 'Tools\watchdog.ps1') $sbTools -Force

$script:fails = 0
function Invoke-Probe([string]$scriptName) {
    # PS 5.1: native stderr + 2>&1 under EAP=Stop throws; relax inside probe call.
    $ErrorActionPreference = 'Continue'
    $raw = & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $sbTools $scriptName) -LockProbeOnly 2>&1
    return ($raw | Where-Object { "$_" -like 'probe:*' } | Select-Object -First 1)
}
function Check([string]$name, [string]$lockPath, [string]$scriptName, [scriptblock]$fabricate, [string]$expect) {
    if (Test-Path $lockPath) { Remove-Item $lockPath -Force }
    & $fabricate
    $got = Invoke-Probe $scriptName
    if ("$got" -like $expect) {
        Write-Output ("PASS {0}: {1}" -f $name, $got)
    } else {
        Write-Output ("FAIL {0}: expect={1} got={2}" -f $name, $expect, $got)
        $script:fails++
    }
}

# sacrificial dead pid: spawn + reap a real process (pid-reuse window is ~ms;
# on a spurious FAIL rerun the selftest)
$sac = Start-Process powershell -ArgumentList '-NoProfile', '-Command', 'exit 0' -PassThru
$sac.WaitForExit()
$deadPid = $sac.Id

foreach ($target in @(
    @{ script = 'iteration_loop.ps1'; lock = (Join-Path $sbLogs 'iteration-loop\round.lock') },
    @{ script = 'watchdog.ps1';       lock = (Join-Path $sbLogs 'watchdog.lock') }
)) {
    $s = $target.script
    $lp = $target.lock
    Check ("{0} no-lock -> TAKE" -f $s) $lp $s {} 'probe: TAKE grabbed*'
    Check ("{0} live-pid -> SKIP" -f $s) $lp $s { Set-Content -Path $lp -Value ("pid=$PID x") -Encoding ASCII } 'probe: SKIP pid=*alive*'
    Check ("{0} dead-pid -> TAKE" -f $s) $lp $s { Set-Content -Path $lp -Value ("pid=$deadPid x") -Encoding ASCII } 'probe: TAKE pid=*dead*'
    Check ("{0} legacy-fresh -> SKIP" -f $s) $lp $s { Set-Content -Path $lp -Value '20260925_020000' -Encoding ASCII } 'probe: SKIP legacy-fresh*'
    Check ("{0} legacy-stale -> TAKE" -f $s) $lp $s {
        Set-Content -Path $lp -Value '20260925_020000' -Encoding ASCII
        (Get-Item $lp).LastWriteTime = (Get-Date).AddMinutes(-45)
    } 'probe: TAKE legacy-stale*'
}

Remove-Item $sb -Recurse -Force -ErrorAction SilentlyContinue
Write-Output ("selftest result: {0} FAIL" -f $script:fails)
exit $script:fails
