# r1078 task panel audit per O-20261018-0137 2.1 (all schtasks via Invoke-SilentExe, zero-window law)
$repo = "K:\Fluxgroup\FluxGroup\quant\bigmoney"
Set-Location $repo
$raw = & .\Tools\Invoke-SilentExe.ps1 -Exe schtasks -ArgString "/query /fo csv /nh" -StdoutOnly
$names = ($raw -split "`n" | ForEach-Object { $_.Trim('"') -split '","' } | Where-Object { $_ -match '^(Bigmoney-|HQ-|bm-c-|MiniGame|.*Watchdog|.*Sentinel|.*sentinel)' }) | Sort-Object -Unique
# also include known in-service canon names even if missing from filter
$extra = @('Bigmoney-IterationLoop','Bigmoney-LoopWatchdog','HQ-bm-c-Sentinel','HQ-WT-Park','HQ-FleetDispatcher','HQ-FleetIdleWatch')
$targets = ($names + $extra) | Sort-Object -Unique
$out = New-Object System.Collections.Generic.List[string]
foreach ($t in $targets) {
  $v = & .\Tools\Invoke-SilentExe.ps1 -Exe schtasks -ArgString "/query /tn `"$t`" /v /fo list" -StdoutOnly
  if ($LASTEXITCODE -ne 0) { $out.Add("$t | NOT_FOUND(rc=$LASTEXITCODE)"); continue }
  $status = ($v | Select-String '^Status:\s*(.*)$').Matches.Groups[1].Value
  $nextr  = ($v | Select-String '^Next Run Time:\s*(.*)$').Matches.Groups[1].Value
  $sched = ($v | Select-String '^Schedule Type:\s*(.*)$').Matches.Groups[1].Value
  $last  = ($v | Select-String '^Last Run Time:\s*(.*)$').Matches.Groups[1].Value
  $lastr = ($v | Select-String '^Last Result:\s*(.*)$').Matches.Groups[1].Value
  $xml = & .\Tools\Invoke-SilentExe.ps1 -Exe schtasks -ArgString "/query /tn `"$t`" /xml" -StdoutOnly
  $logon = 'n/a'
  if ($xml -match '<LogonType>(\S+)</LogonType>') { $logon = $Matches[1] }
  $out.Add("$t | State=$status | LogonType=$logon | Next=$nextr | Sched=$sched | LastRun=$last | LastResult=$lastr")
}
$out | Out-File results\_r1078bmc_taskaudit.txt -Encoding utf8
Write-Output "AUDITED=$($out.Count)"
