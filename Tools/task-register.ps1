# task-register.ps1 - THE canonical silent task registrar (U060 zero-window law, mechanism-grade)
# CEO order 2026-10-08: "silence by construction, not cleanup after incidents."
# Every task registered through this tool is silent BY STRUCTURE:
#   1. Action is ALWAYS wrapped in the Tools\InvisibleRunner.vbs hidden chain (fleet-proven since 09-20).
#   2. Write-then-readback verification: registration is reported OK only after the
#      hidden chain is confirmed present on the task object.
#   3. There is NO parameter or code path that can produce a visible-console task.
# Sessions must use this tool instead of raw schtasks / Register-ScheduledTask
# (that is a hard law in AI.md item 7 - violations are counted by patrol).
#
# Usage:
#   powershell Tools/task-register.ps1 -Name MyTask -Script C:\path\job.ps1 -Trigger every:10m
#   powershell Tools/task-register.ps1 -Name MyTask -Script C:\path\job.bat -Trigger daily:04:07 -Arg "-x 1"
# Trigger forms:
#   logon | boot | daily:HH:mm | every:Nm | once:yyyy-MM-ddTHH:mm
param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string]$Script,
    [string]$Arg = '',
    [Parameter(Mandatory = $true)][string]$Trigger,
    [string]$Description = 'fleet silent task via Tools/task-register.ps1 (U060 mechanism-grade)'
)
$ErrorActionPreference = 'Stop'

$vbs = Join-Path $PSScriptRoot 'InvisibleRunner.vbs'
if (-not (Test-Path $vbs)) { throw 'InvisibleRunner.vbs missing - cannot guarantee silence' }

$sc = [System.IO.Path]::GetFullPath($Script)
if (-not (Test-Path $sc)) { throw "script/exe not found: $sc" }
$ext = [System.IO.Path]::GetExtension($sc).ToLower()
$tailArg = if ($Arg) { ' ' + $Arg } else { '' }

# inner launcher by file type - all console-capable hosts are wrapped by the outer VBS chain
switch ($ext) {
    '.ps1' { $inner = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{0}"{1}' -f $sc, $tailArg }
    '.bat' { $inner = 'cmd.exe /c "{0}"{1}' -f $sc, $tailArg }
    '.cmd' { $inner = 'cmd.exe /c "{0}"{1}' -f $sc, $tailArg }
    '.py'  { $inner = 'pythonw.exe "{0}"{1}' -f $sc, $tailArg }
    default { $inner = '"{0}"{1}' -f $sc, $tailArg }
}

$action = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument ('//B //nologo "{0}" {1}' -f $vbs, $inner)

switch -Regex ($Trigger) {
    '^logon$'  { $trg = New-ScheduledTaskTrigger -AtLogOn }
    '^boot$'   { $trg = New-ScheduledTaskTrigger -AtBoot }
    '^daily:'  { $trg = New-ScheduledTaskTrigger -Daily -At ($Trigger -replace '^daily:', '') }
    '^once:'   { $trg = New-ScheduledTaskTrigger -Once -At ([datetime]($Trigger -replace '^once:', '')) }
    '^every:'  {
        $mins = [int]($Trigger -replace '^every:', '').TrimEnd('m')
        if ($mins -lt 1) { throw 'every:Nm requires N >= 1' }
        $trg = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes $mins) -RepetitionDuration (New-TimeSpan -Days 3650)
    }
    default { throw "unknown trigger form: $Trigger (use logon|boot|daily:HH:mm|every:Nm|once:ISO)" }
}

if (Get-ScheduledTask -TaskName $Name -ErrorAction SilentlyContinue) {
    throw "task already exists: $Name (unregister it first - no silent overwrite)"
}

Register-ScheduledTask -TaskName $Name -Action $action -Trigger $trg -Description $Description | Out-Null

# write-then-readback law: green only if the hidden chain is confirmed on the live object
$chk = Get-ScheduledTask -TaskName $Name
$chkAct = ($chk.Actions | ForEach-Object { $_.Execute + ' ' + $_.Arguments }) -join ' '
if ($chkAct -notmatch [regex]::Escape('InvisibleRunner.vbs')) {
    Unregister-ScheduledTask -TaskName $Name -Confirm:$false
    throw 'readback failed: hidden chain missing - registration rolled back'
}

Write-Output ('OK silent task registered: ' + $Name)
Write-Output ('  action : ' + $chkAct)
Write-Output ('  trigger: ' + $Trigger)
