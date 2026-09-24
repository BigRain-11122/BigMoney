# watchdog_c7_selftest.ps1 -- C7 injection acceptance tests (O-20260924-1626 T-25).
# Acceptance per ticket: injected watermark RED actually escalates; injected
# zombie process actually killed (3-check guard); guard/unknown lanes exempt.
# Mechanism: runs watchdog.ps1 -C7Only with the zombie whitelist NARROWED to
# 'c7_zombie_test' so compressed test thresholds can never touch production
# batch processes. Real processes are launched and really killed in T4.
# Pure ASCII. Exit 0 = all pass, 1 = any fail. Never uses 2>&1 pipes (rc trap).
$ErrorActionPreference = 'Continue'
$Project = Split-Path -Parent $PSScriptRoot
$Wd = Join-Path $Project 'Tools\watchdog.ps1'
$Tmp = Join-Path $Project 'logs\c7_selftest'
New-Item -ItemType Directory -Path $Tmp -Force | Out-Null
$WdLog = Join-Path $Project 'logs\watchdog.log'
$pass = 0; $fail = 0
function Check([string]$name, [bool]$cond) {
    if ($cond) { $script:pass++; Write-Output ('[PASS] ' + $name) }
    else { $script:fail++; Write-Output ('[FAIL] ' + $name) }
}
function Run-C7([string]$wm, [string]$red, [string]$st, [double]$age, [double]$delta) {
    powershell -NoProfile -ExecutionPolicy Bypass -File $Wd -C7Only -WmFile $wm -RedFile $red -PyStateFile $st `
        -ZombieAgeMin $age -ZombieCpuDeltaSec $delta -ZombieLanes @('c7_zombie_test') | Out-Null
    return $LASTEXITCODE
}
function Test-AliveCim([int]$procId) {
    # CIM second opinion (r100 law: Get-Process transient false-negative trap)
    $c = Get-CimInstance Win32_Process -Filter "ProcessId = $procId" -ErrorAction SilentlyContinue
    return ($null -ne $c)
}
function Write-Wm([string]$path, [double]$py, [int]$tickets, [int]$bandit) {
    $now = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $lines = @()
    foreach ($i in @(0,1,2)) {
        $lines += ('{"ts": "' + $now + '", "epoch": 1790241600.0, "machine": "bm-a", "cpu_total_pct": 10.0, "cores": 32, "py_cpu_pct": ' + $py + ', "py_procs": 3, "top_proc_cores": 0.1, "local_batch_running": false, "open_tickets": ' + $tickets + ', "open_ticket_ids": [], "bandit_open": ' + $bandit + ', "bars_present": true, "daily_panel": true}')
    }
    Set-Content -Path $path -Value $lines -Encoding ASCII
}

# ---- T1: injected RED escalates (3 low-py samples + runnable work) ----
$wm1 = Join-Path $Tmp 'wm_red.jsonl'; $red1 = Join-Path $Tmp 'red1.json'; $st1 = Join-Path $Tmp 'st1.json'
Write-Wm $wm1 0.5 2 0
Run-C7 $wm1 $red1 $st1 45 5.0 | Out-Null
$r1 = Get-Content $red1 -Raw | ConvertFrom-Json
Check 'T1 injected RED escalates (red=true + lane + order_ref)' ($r1.red -eq $true -and $r1.lane -like '*escalate*' -and $r1.order_ref -eq 'O-20260924-1626 R1/R2/R3')

# ---- T2: healthy py -> no red ----
$wm2 = Join-Path $Tmp 'wm_green.jsonl'; $red2 = Join-Path $Tmp 'red2.json'; $st2 = Join-Path $Tmp 'st2.json'
Write-Wm $wm2 85.0 2 0
Run-C7 $wm2 $red2 $st2 45 5.0 | Out-Null
$r2 = Get-Content $red2 -Raw | ConvertFrom-Json
Check 'T2 healthy py -> red=false (no false alarm)' ($r2.red -eq $false -and $r2.lane -eq 'healthy')

# ---- T3: low py + EMPTY queue -> honest idle, no red (board-clear clause) ----
$wm3 = Join-Path $Tmp 'wm_clear.jsonl'; $red3 = Join-Path $Tmp 'red3.json'; $st3 = Join-Path $Tmp 'st3.json'
Write-Wm $wm3 0.5 0 0
Run-C7 $wm3 $red3 $st3 45 5.0 | Out-Null
$r3 = Get-Content $red3 -Raw | ConvertFrom-Json
Check 'T3 low py + empty queue -> red=false (legal idle)' ($r3.red -eq $false)

# ---- T4: injected zombie REALLY killed (two-pass CPU-delta, 3-check) ----
$wm4 = Join-Path $Tmp 'wm_kill.jsonl'; $red4 = Join-Path $Tmp 'red4.json'; $st4 = Join-Path $Tmp 'st4.json'
Write-Wm $wm4 0.5 2 0
# NOTE: Start-Process does NOT auto-quote spaced ArgumentList elements -- the
# -c code string MUST be wrapped in literal double quotes or python exits on
# a mangled command line (first run red: all "kill" assertions false-positive).
$zp = Start-Process -FilePath 'python' -ArgumentList '-c', '"import time; time.sleep(120)  # c7_zombie_test"' -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 1
Run-C7 $wm4 $red4 $st4 0.05 0.5 | Out-Null      # pass 1: records CPU snapshot, no prev -> no kill
$aliveAfterP1 = Test-AliveCim $zp.Id
Start-Sleep -Seconds 3
Run-C7 $wm4 $red4 $st4 0.05 0.5 | Out-Null      # pass 2: age passed + CPU delta ~0 -> KILL
$aliveAfterP2 = Test-AliveCim $zp.Id
$logTail = (Get-Content $WdLog -Tail 25) -join ' '
Check 'T4 zombie: pass1 no-kill (state recorded)' ($aliveAfterP1)
Check 'T4 zombie: pass2 real kill executed' (-not $aliveAfterP2)
Check 'T4 zombie: kill logged (3-check passed line)' ($logTail -like '*ZOMBIE KILL*c7_zombie_test*')
Check 'T4 zombie: red-file lists zombie' ((Get-Content $red4 -Raw | ConvertFrom-Json).zombies_killed.Count -ge 1)

# ---- T5: interactive-session guard exempts (codely in cmdline) ----
$wm5 = $wm4; $red5 = Join-Path $Tmp 'red5.json'; $st5 = Join-Path $Tmp 'st5.json'
$ip = Start-Process -FilePath 'python' -ArgumentList '-c', '"import time; time.sleep(60)  # c7_zombie_test codely"' -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 1
Run-C7 $wm5 $red5 $st5 0.001 0.001 | Out-Null
Start-Sleep -Seconds 2
Run-C7 $wm5 $red5 $st5 0.001 0.001 | Out-Null
$guardAlive = Test-AliveCim $ip.Id
Check 'T5 interactive guard (codely) exempt -> alive' ($guardAlive)
Stop-Process -Id $ip.Id -Force -ErrorAction SilentlyContinue

# ---- T6: unknown lane (not whitelisted) exempt -> conservative no-kill ----
$up = Start-Process -FilePath 'python' -ArgumentList '-c', '"import time; time.sleep(60)  # c7_unknown_lane_test"' -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 1
Run-C7 $wm5 (Join-Path $Tmp 'red6.json') (Join-Path $Tmp 'st6.json') 0.001 0.001 | Out-Null
Start-Sleep -Seconds 2
Run-C7 $wm5 (Join-Path $Tmp 'red6.json') (Join-Path $Tmp 'st6.json') 0.001 0.001 | Out-Null
$unknownAlive = Test-AliveCim $up.Id
Check 'T6 unknown lane exempt (whitelist-only kill) -> alive' ($unknownAlive)
Stop-Process -Id $up.Id -Force -ErrorAction SilentlyContinue

# ---- T7: insufficient history (2 samples) -> no red, honest lane ----
$wm7 = Join-Path $Tmp 'wm_short.jsonl'; $red7 = Join-Path $Tmp 'red7.json'; $st7 = Join-Path $Tmp 'st7.json'
$now = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
Set-Content -Path $wm7 -Value @(
    '{"ts": "' + $now + '", "py_cpu_pct": 0.5, "open_tickets": 1, "bandit_open": 0}',
    '{"ts": "' + $now + '", "py_cpu_pct": 0.5, "open_tickets": 1, "bandit_open": 0}'
) -Encoding ASCII
Run-C7 $wm7 $red7 $st7 45 5.0 | Out-Null
$r7 = Get-Content $red7 -Raw | ConvertFrom-Json
Check 'T7 insufficient history -> red=false + honest lane' ($r7.red -eq $false -and $r7.lane -eq 'insufficient_history')

# ---- T8: STALE work only in older samples, freshest clear -> no red ----
# regression fixture for the R107 (T-38) / R110 (T-39) stale false-red class:
# ticket was open during older samples then claimed/closed; tail-union hasWork
# kept the red alive while the current board is clear (legal idle).
$wm8 = Join-Path $Tmp 'wm_stale.jsonl'; $red8 = Join-Path $Tmp 'red8.json'; $st8 = Join-Path $Tmp 'st8.json'
$sBase = '{"ts": "' + $now + '", "epoch": 1790241600.0, "machine": "bm-a", "cpu_total_pct": 10.0, "cores": 32, "py_cpu_pct": 0.5, "py_procs": 3, "top_proc_cores": 0.1, "local_batch_running": false, "open_ticket_ids": [], "bandit_open": 0, "bars_present": true, "daily_panel": true, "open_tickets": '
Set-Content -Path $wm8 -Value @(
    ($sBase + '1}'),     # older sample: ticket still open
    ($sBase + '1}'),     # mid sample: ticket still open
    ($sBase + '0}')      # FRESHEST sample: ticket claimed -> board clear
) -Encoding ASCII
Run-C7 $wm8 $red8 $st8 45 5.0 | Out-Null
$r8 = Get-Content $red8 -Raw | ConvertFrom-Json
Check 'T8 stale-work-only older samples -> red=false (freshest wins)' ($r8.red -eq $false -and $r8.lane -eq 'healthy')
# and the symmetric guard: freshest sample WITH work still escalates (T1 covers
# all-3-work; here only the freshest shows work -> must still be red)
$wm8b = Join-Path $Tmp 'wm_freshwork.jsonl'; $red8b = Join-Path $Tmp 'red8b.json'; $st8b = Join-Path $Tmp 'st8b.json'
Set-Content -Path $wm8b -Value @(
    ($sBase + '0}'),     # older sample: board clear
    ($sBase + '0}'),     # mid sample: board clear
    ($sBase + '2}')      # FRESHEST sample: new ticket open -> work exists NOW
) -Encoding ASCII
Run-C7 $wm8b $red8b $st8b 45 5.0 | Out-Null
$r8b = Get-Content $red8b -Raw | ConvertFrom-Json
Check 'T8b freshest-sample work + low py -> red=true (escalation preserved)' ($r8b.red -eq $true -and $r8b.lane -like '*escalate*')

Write-Output ('selftest: ' + $pass + ' PASS, ' + $fail + ' FAIL')
if ($fail -gt 0) { exit 1 } else { exit 0 }
