# register_fleetlink_task.ps1 - FluxGroup-FleetLink listener task registration
# for bm-b. Local fork of group Tools/register-fleet-link.ps1 (CEO order
# 2026-10-04, O-20260909-2150 onboarding step1) with ONE machine-law override:
# principal LogonType = S4U instead of Interactive. bm-b machine law (judgment
# 2026-09-29 blackout-root): ALL lane scheduled tasks on this machine are S4U
# ("run whether user is logged on or not" = child consoles inherently
# invisible); InteractiveToken is forbidden. The wscript //B VBS hidden chain
# is kept per U060 zero-window law (defense in depth).
# Quoting law (B795 family): the task Arguments string is built INSIDE this
# .ps1 file only - never pass it through an outer shell re-parse (inline shell
# quoting mangled the arguments on first registration attempt r810).
# Pure ASCII. Idempotent via -Force. Path-agnostic via -Root param.
param(
  [string]$Root = "C:\Fluxgroup\FluxGroup",
  [string]$NodeId = "bm-b",
  [int]$Port = 8790
)
$ErrorActionPreference = 'Stop'
$TaskName = 'FluxGroup-FleetLink'
$script = Join-Path $Root 'Tools\fleet-link.ps1'
$vbs = Join-Path $Root 'Tools\InvisibleRunner.vbs'
if (-not (Test-Path $script)) { throw 'fleet-link.ps1 missing' }
if (-not (Test-Path $vbs)) { throw 'InvisibleRunner.vbs missing' }

$argLine = '//B //nologo "' + $vbs + '" powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + $script + '" -Root "' + $Root + '" -NodeId ' + $NodeId
$action = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument $argLine -WorkingDirectory $Root
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances Parallel
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
Write-Output ('REGISTERED ' + $TaskName + ' node=' + $NodeId + ' S4U root=' + $Root)
Start-ScheduledTask -TaskName $TaskName

$ok = $false
for ($i = 0; $i -lt 20; $i++) {
  Start-Sleep -Milliseconds 500
  try {
    $h = Invoke-RestMethod -Uri ('http://127.0.0.1:' + $Port + '/health') -TimeoutSec 2
    if ($h.ok) { $ok = $true; break }
  } catch { }
}
if ($ok) { Write-Output ('HEALTH OK node=' + $NodeId + ' port=' + $Port) }
else { Write-Output 'HEALTH PENDING (listener still starting; re-check in 1 min)' }
$tsrule = Get-NetFirewallRule -DisplayName 'Tailscale-In' -ErrorAction SilentlyContinue
if (-not $tsrule) { Write-Output 'WARN: Tailscale-In firewall rule missing - tailnet peers may be blocked (loopback still works)' }
else { Write-Output 'FW: Tailscale-In present (tailnet inbound allowed)' }
