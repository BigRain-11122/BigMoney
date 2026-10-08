# silence-enforce.ps1 - Fleet silence root-cure (CEO order 10-08, U060 escalation)
# Idempotent, silent, machine-agnostic. Re-asserts gates (self-heal vs OS resets),
# audits scheduled tasks for console-flash violations, writes compliance JSON.
# Invoked via wscript //B //nologo chain (Tools/silence-enforce.vbs) or directly.
$ErrorActionPreference = 'SilentlyContinue'
$hostName = $env:COMPUTERNAME
$report = [ordered]@{
    host       = $hostName
    ts         = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
    toast_gate = $null
    noc_gate   = $null
    task_violations = @()
    remediations   = @()
    guard_cadence  = $null
    quark_updater_killed = $null
}

# 1) Global toast gates (re-assert every run - OS updates may reset them)
# 双闸律（10-06 C 机配方）：①ToastEnabled ②NOC_GLOBAL_SETTING_TOASTS_ENABLED=系统勿扰总闸
# （12:2x 复发实锚：bm-a 曾只设①漏②=弹窗复发根源——两道全无条件写）
$pushKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\PushNotifications'
if (-not (Test-Path $pushKey)) { New-Item $pushKey -Force | Out-Null }
New-ItemProperty $pushKey -Name ToastEnabled -Value 0 -PropertyType DWord -Force | Out-Null
New-ItemProperty $pushKey -Name AllowToasts -Value 0 -PropertyType DWord -Force | Out-Null
$pv = Get-ItemProperty $pushKey
$report.toast_gate = [int]$pv.ToastEnabled

$nocKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings'
if (-not (Test-Path $nocKey)) { New-Item $nocKey -Force | Out-Null }
New-ItemProperty $nocKey -Name NOC_GLOBAL_SETTING_TOASTS_ENABLED -Value 0 -PropertyType DWord -Force | Out-Null
$nv = Get-ItemProperty $nocKey
$report.noc_gate = [int]$nv.NOC_GLOBAL_SETTING_TOASTS_ENABLED

# 2) QuarkUpdater popup source (updater only - main app untouched)
foreach ($t in (Get-ScheduledTask -TaskPath '\QuarkUpdaterUser\*' -ErrorAction SilentlyContinue)) {
    if ($t.State -ne 'Disabled') { Disable-ScheduledTask -TaskPath $t.TaskPath -TaskName $t.TaskName | Out-Null }
}
Remove-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'QuarkUpdaterTaskUser1.0.0.21' -ErrorAction SilentlyContinue
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
    Unregister-ScheduledTask -TaskName 'HQ-SilenceGuard-15m' -Confirm:$false -ErrorAction SilentlyContinue
} catch {}
$laneIntOk = $false
try {
    $lane = Get-ScheduledTask -TaskName $laneName -ErrorAction Stop
    if ($lane.Triggers | Where-Object { "$($_.Repetition.Interval)" -match '^PT1M$' }) { $laneIntOk = $true }
} catch {}
if (-not $laneIntOk) {
    try {
        if (Get-ScheduledTask -TaskName $laneName -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $laneName -Confirm:$false }
        $laneAct = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument ('//B //nologo "{0}"' -f $laneVbs)
        $laneRep = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 1) -RepetitionDuration (New-TimeSpan -Days 3650)
        Register-ScheduledTask -TaskName $laneName -Action $laneAct -Trigger $laneRep -Description 'Fleet silence guard 1-min self-heal lane (U060 mechanism-grade)' | Out-Null
        $report.guard_cadence = 'lane-1m-added'
    } catch { $report.guard_cadence = 'lane-failed: ' + $_.Exception.Message }
} else { $report.guard_cadence = 'lane-1m-ok' }
$lv = Get-ScheduledTask -TaskName $laneName -ErrorAction SilentlyContinue
if (-not $lv -or -not ($lv.Triggers | Where-Object { "$($_.Repetition.Interval)" -match '^PT1M$' })) {
    $report.guard_cadence = 'lane-verify-failed'
}

# 5) Write compliance JSON (patrol consumes; fleet status plane)
$outDir = Join-Path $PSScriptRoot '..\.codely-cli\patrol'
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir -Force | Out-Null }
$jsonPath = Join-Path $outDir 'silence-audit.json'
[IO.File]::WriteAllText($jsonPath, ($report | ConvertTo-Json -Compress))
