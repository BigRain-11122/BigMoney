$env:PYTHONIOENCODING = 'utf-8'
$legs = @(
  @('update_ths_panel', 'python scripts\update_ths_panel.py'),
  @('ah_panel_puller', 'python scripts\ah_panel_puller.py'),
  @('update_fund_premium', 'python scripts\update_fund_premium.py snapshot'),
  @('update_fundamental', 'python scripts\update_fundamental.py'),
  @('b_layer_filter', 'python -m firm.risk.b_layer_filter'),
  @('update_fund_statements', 'python scripts\update_fund_statements.py'),
  @('live_paper', 'python -m live.paper'),
  @('t35_open_fill_verify', 'python scripts\t35_open_fill_verify.py'),
  @('t24_prospect_paper', 'python scripts\t24_prospect_paper.py run'),
  @('t24_prospect_promotion', 'python scripts\t24_prospect_promotion.py run'),
  @('aggressive_lab', 'python scripts\aggressive_lab.py paper'),
  @('alloc_paper', 'python scripts\alloc_paper.py run'),
  @('grid_paper', 'python scripts\grid_paper.py run'),
  @('system_v1_paper', 'python scripts\system_v1_paper.py run'),
  @('t35_paper_export', 'python scripts\t35_paper_export.py run'),
  @('daily_scorecard', 'python scripts\daily_scorecard.py'),
  @('daily_report', 'python scripts\daily_report.py run'),
  @('ceo_live_usage', 'python scripts\ceo_live_usage.py'),
  @('monitor_build_status', 'python -m monitor.build_status'),
  @('token_meter', 'python scripts\token_meter.py')
)
foreach ($leg in $legs) {
  $out = Invoke-Expression $leg[1] 2>&1 | Out-String
  $extra = ($out -split "`r?`n" | Where-Object { $_.Trim() } | Select-Object -First 3) -join ' ~ '
  Write-Output ("LEG {0} | exit={1} | {2}" -f $leg[0], $LASTEXITCODE, $extra)
}
