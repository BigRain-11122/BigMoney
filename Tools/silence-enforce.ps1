# silence-enforce.ps1 - Fleet silence root-cure (CEO order 10-08, U060 escalation)
# Idempotent, silent, machine-agnostic. Re-asserts gates (self-heal vs OS resets),
# audits scheduled tasks for console-flash violations, writes compliance JSON.
# Invoked via wscript //B //nologo chain (Tools/silence-enforce.vbs) or directly.
#
# -DryRun (2026-10-26 r1288): read-only audit - reports what this guard WOULD
# remediate on this host and writes the same JSON, but touches nothing (no
# registry gates, no task rewrite, no lane registration, no disable). Added
# because the auto-enforce leg could only be inspected by running it, and
# running it mutates host state; a disabled lane stays invisible until the next
# round fails to appear.
param([switch]$DryRun)
$ErrorActionPreference = 'SilentlyContinue'
$hostName = $env:COMPUTERNAME
$report = [ordered]@{
    host       = $hostName
    ts         = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
    dry_run    = [bool]$DryRun
    toast_gate = $null
    noc_gate   = $null
    task_violations = @()
    remediations   = @()
    protected_tasks = @()
    guard_cadence  = $null
    quark_updater_killed = $null
}

# Round-ignition tasks are never wrapped or disabled by this guard.
# D-20261026-10 sec.2 (council, 2026-10-26): IterationLoop/LoopWatchdog are the
# ONLY ignition face of a compute lane, so any silent stop is a lane outage.
# D-20261026-15 sec.3 already recorded them going Disabled twice in one day on
# bm-a, 2 minutes apart (12:33/12:37), right after being Ready at 09:07 - the
# exact shape of this foreach: Set-ScheduledTask throws, the fallback disables,
# and there is no name allowlist. A console flash costs one window; a disabled
# round costs the whole lane, so on the protected face the guard fails closed.
$ProtectedPattern = '(?i)^(.*[-_])?(IterationLoop|LoopWatchdog)$'

# 1) Global toast gates (re-assert every run - OS updates may reset them)
# 双闸律（10-06 C 机配方）：①ToastEnabled ②NOC_GLOBAL_SETTING_TOASTS_ENABLED=系统勿扰总闸
# （12:2x 复发实锚：bm-a 曾只设①漏②=弹窗复发根源——两道全无条件写）
$pushKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\PushNotifications'
if (-not $DryRun) {
    if (-not (Test-Path $pushKey)) { New-Item $pushKey -Force | Out-Null }
    New-ItemProperty $pushKey -Name ToastEnabled -Value 0 -PropertyType DWord -Force | Out-Null
    New-ItemProperty $pushKey -Name AllowToasts -Value 0 -PropertyType DWord -Force | Out-Null
}
$pv = Get-ItemProperty $pushKey
$report.toast_gate = [int]$pv.ToastEnabled

$nocKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings'
if (-not $DryRun) {
    if (-not (Test-Path $nocKey)) { New-Item $nocKey -Force | Out-Null }
    New-ItemProperty $nocKey -Name NOC_GLOBAL_SETTING_TOASTS_ENABLED -Value 0 -PropertyType DWord -Force | Out-Null
}
$nv = Get-ItemProperty $nocKey
$report.noc_gate = [int]$nv.NOC_GLOBAL_SETTING_TOASTS_ENABLED

# 2) QuarkUpdater popup source (updater only - main app untouched)
if (-not $DryRun) {
    foreach ($t in (Get-ScheduledTask -TaskPath '\QuarkUpdaterUser\*' -ErrorAction SilentlyContinue)) {
        if ($t.State -ne 'Disabled') { Disable-ScheduledTask -TaskPath $t.TaskPath -TaskName $t.TaskName | Out-Null }
    }
    Remove-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'QuarkUpdaterTaskUser1.0.0.21' -ErrorAction SilentlyContinue
}
$quarkTask = @(Get-ScheduledTask -TaskPath '\QuarkUpdaterUser\*' -ErrorAction SilentlyContinue)
if ($quarkTask.Count -gt 0) {
    $dis = @($quarkTask | Where-Object { $_.State -eq 'Disabled' }).Count
    $report.quark_updater_killed = ($dis -eq $quarkTask.Count).ToString()
} else { $report.quark_updater_killed = 'no-task' }

# 3) Task audit + AUTO-ENFORCE (10-08 15:5x recurrence: a session registered a bare-cmd
#     task 3h after the 12:40 root-cure; detect-only + daily cadence = hours of popup
#     exposure. Root cure per CEO: the guard itself neutralizes violations.)
#     Skip disabled (cannot run, cannot flash) and Microsoft tasks. Remediate: wrap the
#     action into the group InvisibleRunner hidden chain (work preserved, window killed);
#     fallback = disable. Every remediation is recorded in JSON for patrol.
$vbsPath = Join-Path $PSScriptRoot 'InvisibleRunner.vbs'
foreach ($tk in (Get-ScheduledTask -ErrorAction SilentlyContinue)) {
    if ($tk.TaskPath -like '\Microsoft\*') { continue }
    if ($tk.State -eq 'Disabled') { continue }
    $act = ($tk.Actions | ForEach-Object { ($_.Execute + ' ' + $_.Arguments).Trim() }) -join ' ;; '
    if (-not $act) { continue }
    if ($act -match 'wscript|mshta') { continue }
    if ($act -notmatch 'powershell|cmd|pwsh|cscript|\.ps1|\.bat|\.cmd') { continue }
    $vname = $tk.TaskPath + $tk.TaskName
    $report.task_violations += $vname
    $r = [ordered]@{ task = $vname; action = ''; detail = $act }
    if ($tk.TaskName -match $ProtectedPattern) {
        # report only: a rewritten ignition task is indistinguishable from a healthy
        # one until the next round silently does not start
        $r.action = 'protected_left_intact'
        $report.protected_tasks += $vname
        $report.remediations += $r
        continue
    }
    if ($DryRun) {
        $r.action = 'would-wrap-or-disable'
        $report.remediations += $r
        continue
    }
    try {
        $newAct = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument ('//B //nologo "{0}" {1}' -f $vbsPath, $act)
        Set-ScheduledTask -TaskPath $tk.TaskPath -TaskName $tk.TaskName -Action $newAct | Out-Null
        $r.action = 'wrapped'
    } catch {
        try { Disable-ScheduledTask -TaskPath $tk.TaskPath -TaskName $tk.TaskName | Out-Null; $r.action = 'disabled' }
        catch { $r.action = 'failed'; $r.detail = $_.Exception.Message }
    }
    $report.remediations += $r
}

# 4) Self-configure: ensure the 1-MINUTE self-heal lane exists (mechanism-grade floor:
#    even a violated bare-console task can flash at most ~60s before this guard
#    neutralizes it). Migrates the 10-08 15m lane if present. Original HQ-SilenceGuard
#    (logon + daily 04:07) stays untouched: PS5.1 Set-ScheduledTask on it returns
#    "Access is denied" on this host. Write-then-readback law: green only after verify.
$laneName = 'HQ-SilenceGuard-Lane'
$laneVbs = Join-Path $PSScriptRoot 'silence-enforce.vbs'
try {
    Get-ScheduledTask -TaskName 'HQ-SilenceGuard-15m' -ErrorAction Stop | Out-Null
    if (-not $DryRun) { Unregister-ScheduledTask -TaskName 'HQ-SilenceGuard-15m' -Confirm:$false -ErrorAction SilentlyContinue }
} catch {}
$laneIntOk = $false
try {
    $lane = Get-ScheduledTask -TaskName $laneName -ErrorAction Stop
    if ($lane.Triggers | Where-Object { "$($_.Repetition.Interval)" -match '^PT1M$' }) { $laneIntOk = $true }
} catch {}
if ($DryRun) {
    $report.guard_cadence = if ($laneIntOk) { 'lane-1m-ok' } else { 'lane-missing-dryrun' }
} elseif (-not $laneIntOk) {
    try {
        if (Get-ScheduledTask -TaskName $laneName -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $laneName -Confirm:$false }
        $laneAct = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument ('//B //nologo "{0}"' -f $laneVbs)
        $laneRep = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 1) -RepetitionDuration (New-TimeSpan -Days 3650)
        Register-ScheduledTask -TaskName $laneName -Action $laneAct -Trigger $laneRep -Description 'Fleet silence guard 1-min self-heal lane (U060 mechanism-grade)' | Out-Null
        $report.guard_cadence = 'lane-1m-added'
    } catch { $report.guard_cadence = 'lane-failed: ' + $_.Exception.Message }
} else { $report.guard_cadence = 'lane-1m-ok' }
$lv = Get-ScheduledTask -TaskName $laneName -ErrorAction SilentlyContinue
if (-not $DryRun -and (-not $lv -or -not ($lv.Triggers | Where-Object { "$($_.Repetition.Interval)" -match '^PT1M$' }))) {
    $report.guard_cadence = 'lane-verify-failed'
}

# 5) Write compliance JSON (patrol consumes; fleet status plane)
$outDir = Join-Path $PSScriptRoot '..\.codely-cli\patrol'
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir -Force | Out-Null }
$jsonPath = Join-Path $outDir 'silence-audit.json'
[IO.File]::WriteAllText($jsonPath, ($report | ConvertTo-Json -Compress))

# 6) Dry-run also lands a repo-visible evidence face (r1288): the audit answers
#    "what would this host's silence guard do to its own lanes?" without doing it.
if ($DryRun) {
    $resDir = Join-Path $PSScriptRoot '..\results'
    if (Test-Path $resDir) {
        $mid = 'unknown'
        try { $mid = (Get-Content (Join-Path $PSScriptRoot '..\fleet\machine.json') -Raw | ConvertFrom-Json).machine_id } catch {}
        $evPath = Join-Path $resDir ("silence_guard_audit.{0}.json" -f $mid)
        [IO.File]::WriteAllText($evPath, ($report | ConvertTo-Json -Depth 6))
    }
}
