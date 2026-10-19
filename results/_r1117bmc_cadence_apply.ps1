# _r1117bmc_cadence_apply.ps1 -- cadence-v2 leg-8 (CEO 2026-10-19 11:53 "全面提速令 v2")
# Law: cph4/cadence.md sec.8 v2 table -- B/C machines: Set-ScheduledTask single-field
# re-freq; S4U+VBS chains untouched (Action/Principal untouched, triggers only);
# read-back verify; disabled state untouched (kept as-is); mod-5 stagger kept
# (start boundary unchanged, interval change preserves minute residue).
$ErrorActionPreference = 'Continue'
$report = @()
$intChanges = @(
  @{Name='\Bigmoney-IterationLoop';    Old='PT10M'; New='PT5M'},
  @{Name='\MiniGameEngineTick';        Old='PT10M'; New='PT5M'},
  @{Name='\BmcIdleGuard';              Old='PT10M'; New='PT5M'},
  @{Name='\Bigmoney-PoolWorker';       Old='PT15M'; New='PT5M'},
  @{Name='\FluxGroup-FleetOversight';  Old='PT1H';  New='PT30M'},
  @{Name='\HQ-MemoryBudgetGate';       Old='PT4H';  New='PT2H'}
)
foreach ($c in $intChanges) {
  $tn = $c.Name.TrimStart('\')
  try {
    $task = Get-ScheduledTask -TaskName $tn -ErrorAction Stop
    $stateBefore = "$($task.State)"
    $logon = "$($task.Principal.LogonType)"
    $before = @($task.Triggers | ForEach-Object { "$($_.Repetition.Interval)" })
    $hits = 0
    foreach ($trig in @($task.Triggers)) {
      if ("$($trig.Repetition.Interval)" -eq $c.Old) { $trig.Repetition.Interval = $c.New; $hits++ }
    }
    if ($hits -eq 0) { $report += "SKIP $tn no-trigger@ $($c.Old) (current: $($before -join ','))"; continue }
    $task | Set-ScheduledTask -ErrorAction Stop | Out-Null
    Start-Sleep -Milliseconds 400
    $after = Get-ScheduledTask -TaskName $tn -ErrorAction Stop
    $afterI = @($after.Triggers | ForEach-Object { "$($_.Repetition.Interval)" })
    $ok = ($afterI -contains $c.New) -and (-not ($afterI -contains $c.Old)) -and ("$($after.State)" -eq $stateBefore)
    $report += ("{0}: {1}->{2} x{3} state {4}->{5} logon={6} readback={7} intervals=[{8}]" -f $tn,$c.Old,$c.New,$hits,$stateBefore,"$($after.State)",$logon,$(if($ok){'OK'}else{'FAIL'}),($afterI -join ','))
  } catch { $report += "ERROR $tn :: $($_.Exception.Message)" }
}
foreach ($s in @(@{N='\MiniGameRadarTick';T='21:52'}, @{N='\MiniGameAuditTick';T='05:52'})) {
  $tn = $s.N.TrimStart('\')
  try {
    $task = Get-ScheduledTask -TaskName $tn -ErrorAction Stop
    $stateBefore = "$($task.State)"
    $logon = "$($task.Principal.LogonType)"
    $starts = @($task.Triggers | ForEach-Object { "$($_.StartBoundary)" })
    if ($starts -match [regex]::Escape($s.T)) { $report += "NOOP $tn shift $($s.T) already present"; continue }
    $newT = New-ScheduledTaskTrigger -Daily -At $s.T
    $all = @($task.Triggers) + @($newT)
    Set-ScheduledTask -TaskName $tn -Trigger $all -ErrorAction Stop | Out-Null
    Start-Sleep -Milliseconds 400
    $after = Get-ScheduledTask -TaskName $tn -ErrorAction Stop
    $startsAfter = @($after.Triggers | ForEach-Object { "$($_.StartBoundary)" })
    $ok = ($startsAfter -match [regex]::Escape($s.T)) -and ("$($after.State)" -eq $stateBefore)
    $report += ("{0}: +shift {1} state {2}->{3} logon={4} readback={5} starts=[{6}]" -f $tn,$s.T,$stateBefore,"$($after.State)",$logon,$(if($ok){'OK'}else{'FAIL'}),($startsAfter -join ' | '))
  } catch { $report += "ERROR $tn :: $($_.Exception.Message)" }
}
$report | ForEach-Object { Write-Output $_ }
$report | Out-File -Encoding utf8 results\_r1117bmc_cadence_readback.txt
