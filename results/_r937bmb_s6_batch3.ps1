# r937 bm-b S6 chain batch 3 (paper legs + panels + token)
$ErrorActionPreference = 'Continue'
$chain = @(
  @{n='aggr_paper';    c='python scripts\aggressive_lab.py paper'},
  @{n='alloc_paper';   c='python scripts\alloc_paper.py run'},
  @{n='grid_paper';    c='python scripts\grid_paper.py run'},
  @{n='system_v1';     c='python scripts\system_v1_paper.py run'},
  @{n='t35_export';    c='python scripts\t35_paper_export.py run'},
  @{n='daily_score';   c='python scripts\daily_scorecard.py'},
  @{n='daily_report';  c='python scripts\daily_report.py run'},
  @{n='ceo_live';      c='python scripts\ceo_live_usage.py'},
  @{n='build_status';  c='python -m monitor.build_status'},
  @{n='token_meter';   c='python scripts\token_meter.py'}
)
foreach ($s in $chain) {
  $out = & cmd /c $s.c 2>&1
  $rc = $LASTEXITCODE
  Write-Output ("### {0} rc={1}" -f $s.n, $rc)
  if ($rc -ne 0) { $out | Select-Object -Last 4 | Write-Output }
}
