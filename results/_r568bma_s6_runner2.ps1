# r568 S6 part-2: paper/live chain legs (ordered, rc evidence)
$env:BIGMONEY_REGIME_GUARD = 'enforce'
$legs = @(
  @{n='live_paper';    c=@('python','-m','live.paper')},
  @{n='open_fill';     c=@('python','scripts\t35_open_fill_verify.py')},
  @{n='prospect';      c=@('python','scripts\t24_prospect_paper.py','run')},
  @{n='promotion';     c=@('python','scripts\t24_prospect_promotion.py','run')},
  @{n='aggr_lab';      c=@('python','scripts\aggressive_lab.py','paper')},
  @{n='alloc_paper';   c=@('python','scripts\alloc_paper.py','run')},
  @{n='grid_paper';    c=@('python','scripts\grid_paper.py','run')},
  @{n='system_v1';     c=@('python','scripts\system_v1_paper.py','run')},
  @{n='paper_export';  c=@('python','scripts\t35_paper_export.py','run')},
  @{n='daily_score';   c=@('python','scripts\daily_scorecard.py')},
  @{n='daily_report';  c=@('python','scripts\daily_report.py','run')},
  @{n='ceo_live';      c=@('python','scripts\ceo_live_usage.py')},
  @{n='build_status';  c=@('python','-m','monitor.build_status')},
  @{n='token_meter';   c=@('python','scripts\token_meter.py')}
)
$fail=@()
foreach ($l in $legs) {
  $out = & $l.c[0] $l.c[1..($l.c.Count-1)] 2>&1
  $rc = $LASTEXITCODE
  $tail = ($out | Select-Object -Last 1)
  Write-Output ("LEG {0} rc={1} :: {2}" -f $l.n, $rc, (($tail -replace '\s+',' ') | Out-String).Trim().Substring(0, [Math]::Min(160, (($tail -replace '\s+',' ') | Out-String).Trim().Length)))
  if ($rc -ne 0) { $fail += ("{0} rc={1}" -f $l.n, $rc) }
}
Write-Output ("S6-PART2 DONE fails=" + ($fail -join ','))
