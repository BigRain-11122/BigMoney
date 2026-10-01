# r312(->r314) bm-c liveness + triage batch 3 -- zero-window, in-process cmdlets only (except silent-git)
$ErrorActionPreference = 'Continue'
$repo = 'K:\Fluxgroup\FluxGroup\quant\bigmoney'
$sg   = 'K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\silent-git.ps1'
Write-Output ('NOW: ' + (Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz'))
Write-Output '--- codely/node session processes (exclude self-probe) ---'
$procs = Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'codely|node' -and $_.CommandLine -notmatch 'Get-CimInstance' }
foreach ($p in $procs) {
  $cd = if ($p.CreationDate) { ([System.Management.ManagementDateTimeConverter]::ToDateTime($p.CreationDate)).ToString('MM-dd HH:mm:ss') } else { '?' }
  Write-Output ($p.ProcessId.ToString() + ' | ' + $p.Name + ' | start ' + $cd + ' | ' + (($p.CommandLine -replace '\s+',' ').Substring(0, [Math]::Min(160, $p.CommandLine.Length))))
}
Write-Output '--- python processes (daemon expected; look for fresh session-born ones) ---'
$py = Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python' -and $_.CommandLine -notmatch 'Get-CimInstance' }
foreach ($p in $py) {
  $cd = if ($p.CreationDate) { ([System.Management.ManagementDateTimeConverter]::ToDateTime($p.CreationDate)).ToString('MM-dd HH:mm:ss') } else { '?' }
  Write-Output ($p.ProcessId.ToString() + ' | start ' + $cd + ' | ' + (($p.CommandLine -replace '\s+',' ').Substring(0, [Math]::Min(140, $p.CommandLine.Length))))
}
Write-Output '--- tick lock files age ---'
$lockCandidates = @()
foreach ($root in @('K:\Fluxgroup\FluxGroup\quant\bigmoney\tools','K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools','K:\Fluxgroup\FluxGroup\quant\.codely-cli')) {
  if (Test-Path $root) {
    $lc = Get-ChildItem $root -Recurse -Filter '*lock*' -ErrorAction SilentlyContinue | Select-Object -First 8
    foreach ($f in $lc) { $lockCandidates += ($f.FullName + ' | mtime ' + $f.LastWriteTime.ToString('MM-dd HH:mm:ss')) }
  }
}
if ($lockCandidates.Count -gt 0) { $lockCandidates | ForEach-Object { Write-Output $_ } } else { Write-Output 'no lock files found under scanned roots' }
Write-Output '--- repo files modified in last 6 min (daemon noise excluded paths) ---'
$cut = (Get-Date).AddMinutes(-6)
$recent = Get-ChildItem $repo -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt $cut -and $_.FullName -notmatch 'results\\_r31[24]bmc|\.git\\|__pycache__' } | Sort-Object LastWriteTime -Descending | Select-Object -First 25
foreach ($f in $recent) { Write-Output ($f.LastWriteTime.ToString('HH:mm:ss') + ' | ' + $f.FullName.Replace($repo,'')) }
Write-Output '--- CODELY.md working-tree diff (full) ---'
& $sg -GitArgs 'diff HEAD -- CODELY.md' -Cwd $repo
Write-Output '--- orders ack diff (files on disk not in heartbeat orders_ack) ---'
$hb = Get-Content (Join-Path $repo 'fleet\machines\bm-c.json') -Raw | ConvertFrom-Json
$ack = @($hb.orders_ack)
$files = Get-ChildItem (Join-Path $repo 'fleet\orders') -Filter 'O-*.md'
foreach ($f in $files) { if ($ack -notcontains $f.Name) { Write-Output ('NEW-ORDER: ' + $f.Name + ' | mtime ' + $f.LastWriteTime.ToString('MM-dd HH:mm')) }
}
Write-Output ('ack count: ' + $ack.Count + ' ; dir count: ' + $files.Count)
Write-Output '=== done ==='
