# register-fleet-link.ps1 - idempotent registration for the FluxGroup-FleetLink
# listener task (CEO order 2026-10-04). Pattern = non-elevated -User registration
# (OrderSentinel precedent) + VBS silent wrapper (U060) + 5-min keepalive; the
# listener itself is single-instance via port occupancy. No elevation needed:
# inbound tailnet traffic is already allowed by the Tailscale-In firewall rules.
param(
  [string]$Root = "C:\Users\sjs20\Desktop\FluxGroup",
  [string]$NodeId = ""
)
$ErrorActionPreference = 'Stop'
$TaskName = 'FluxGroup-FleetLink'
$script = Join-Path $Root 'Tools\fleet-link.ps1'
$vbs = Join-Path $Root 'Tools\InvisibleRunner.vbs'
if (-not (Test-Path $script)) { throw 'fleet-link.ps1 missing' }
if (-not (Test-Path $vbs)) { throw 'InvisibleRunner.vbs missing' }

$port = 8790
if ($NodeId -eq '') {
  try {
    $cfg = Get-Content -Raw -Encoding UTF8 (Join-Path $Root 'Tools\fleet-nodes.json') | ConvertFrom-Json
    if ($cfg.PSObject.Properties.Name -contains 'port') { $port = [int]$cfg.port }
    foreach ($n in @($cfg.nodes)) {
      if ([string]$n.host -ne '' -and ([string]$n.host -ieq $env:COMPUTERNAME)) { $NodeId = [string]$n.id; break }
    }
  } catch { }
  if ($NodeId -eq '') { $NodeId = $env:COMPUTERNAME }
}

$argLine = '//B //nologo "' + $vbs + '" powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + $script + '" -Root "' + $Root + '" -NodeId ' + $NodeId
$action = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument $argLine
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances Parallel
# PS5.1 quirk: Register-ScheduledTask has no -LogonType direct parameter here;
# go through New-ScheduledTaskPrincipal instead (same interactive-user effect).
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
Write-Output ('REGISTERED ' + $TaskName + ' node=' + $NodeId)
Start-ScheduledTask -TaskName $TaskName

$ok = $false
for ($i = 0; $i -lt 20; $i++) {
  Start-Sleep -Milliseconds 500
  try {
    $h = Invoke-RestMethod -Uri ('http://127.0.0.1:' + $port + '/health') -TimeoutSec 2
    if ($h.ok) { $ok = $true; break }
  } catch { }
}
if ($ok) { Write-Output ('HEALTH OK node=' + $NodeId + ' port=' + $port) }
else { Write-Output 'HEALTH PENDING (listener still starting; re-check in 1 min)' }

$tsrule = Get-NetFirewallRule -DisplayName 'Tailscale-In' -ErrorAction SilentlyContinue
if (-not $tsrule) { Write-Output 'WARN: Tailscale-In firewall rule missing - tailnet peers may be blocked (loopback still works)' }
else { Write-Output 'FW: Tailscale-In present (tailnet inbound allowed)' }
