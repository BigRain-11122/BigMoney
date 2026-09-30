$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$legs = @(
  @('pool_dualrun_reconcile', 'python scripts\pool_dualrun_reconcile.py run'),
  @('compute_audit', 'python scripts\compute_audit.py'),
  @('py_watermark', 'python scripts\py_watermark.py probe'),
  @('update_daily', 'python scripts\update_daily.py'),
  @('market_regime', 'python scripts\market_regime.py'),
  @('strategy_scorecard', 'python scripts\strategy_scorecard.py'),
  @('market_clock_call', 'python scripts\market_clock_call.py run'),
  @('update_lhb', 'python scripts\update_lhb.py'),
  @('update_heat', 'python scripts\update_heat.py'),
  @('update_futures', 'python scripts\update_futures.py'),
  @('update_repo', 'python scripts\update_repo.py'),
  @('update_options', 'python scripts\update_options.py'),
  @('update_moneyflow', 'python scripts\update_moneyflow.py'),
  @('update_sina_mf', 'python scripts\update_sina_mf.py'),
  @('update_astock_daily', 'python scripts\update_astock_daily.py'),
  @('update_etf_daily', 'python scripts\update_etf_daily.py'),
  @('rev_osc_signal_export', 'python scripts\rev_osc_signal_export.py run'),
  @('update_minute_feed', 'python scripts\update_minute_feed.py'),
  @('update_ths_panel', 'python scripts\update_ths_panel.py'),
  @('ah_panel_puller', 'python scripts\ah_panel_puller.py'),
  @('update_fund_premium', 'python scripts\update_fund_premium.py snapshot'),
  @('update_fundamental', 'python scripts\update_fundamental.py'),
  @('b_layer_filter', 'python -m firm.risk.b_layer_filter'),
  @('t24_prospect_promotion', 'python scripts\t24_prospect_promotion.py run'),
  @('aggressive_lab_paper', 'python scripts\aggressive_lab.py paper'),
  @('alloc_paper', 'python scripts\alloc_paper.py run'),
  @('grid_paper', 'python scripts\grid_paper.py run'),
  @('system_v1_paper', 'python scripts\system_v1_paper.py run'),
  @('t35_paper_export', 'python scripts\t35_paper_export.py run'),
  @('daily_scorecard', 'python scripts\daily_scorecard.py'),
  @('daily_report', 'python scripts\daily_report.py run'),
  @('ceo_live_usage', 'python scripts\ceo_live_usage.py'),
  @('build_status', 'python -m monitor.build_status'),
  @('token_meter', 'python scripts\token_meter.py')
)
foreach ($leg in $legs) {
  $t0 = Get-Date -Format 'HH:mm:ss'
  Invoke-Expression $leg[1] 2>&1 | ForEach-Object { "[$($leg[0])] $_" } | Select-Object -Last 3 | Out-Host
  $rc = $LASTEXITCODE
  Add-Content -Path 'results\_r505bma_s6.log' -Value "$t0 $($leg[0]) RC=$rc"
}
Add-Content -Path 'results\_r505bma_s6.log' -Value "$(Get-Date -Format 'HH:mm:ss') S6-CHAIN-DONE"
