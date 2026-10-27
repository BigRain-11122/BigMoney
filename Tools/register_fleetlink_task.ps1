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
  [string]$Root = "",
  [string]$NodeId = "bm-b",
  [int]$Port = 8790
)
$ErrorActionPreference = 'Stop'
# D-20261028-04: never default to a literal mirror. Resolve the group tree, then
# require that it is the tree this task actually runs (fleet-link.ps1 present);
# a mirror that resolves but lacks the script throws instead of registering a
# task that can never start. -Root still wins when a caller passes one.
if ([string]::IsNullOrWhiteSpace($Root)) {
  # group-root-sweep: validated-walk - each candidate is only a HINT; it has to
  # carry fleet-link.ps1 AND have the group repo as its git origin, which is the
  # same two-part test Tools/group_root.py applies in Python.
  $cands = @()
  if ($env:FLUXGROUP_ROOT) { $cands += $env:FLUXGROUP_ROOT }
  if ($PSScriptRoot) {
    $cands += (Join-Path (Join-Path (Join-Path $PSScriptRoot '..') '..') '..')
  }
  foreach ($c in $cands) {
    if (-not $c) { continue }
    if (-not (Test-Path (Join-Path $c 'Tools\fleet-link.ps1'))) { continue }
    $origin = ''
    try { $origin = (& git -C $c remote get-url origin 2>$null) } catch { $origin = '' }
    if (-not $origin -or $origin -notmatch 'FluxGroup') { continue }
    $Root = (Resolve-Path $c).Path
    break
  }
  if (-not $Root) { throw 'group root not resolved: pass -Root or set FLUXGROUP_ROOT' }
}
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
