# r877 S6 maintenance chain runner (bm-b) - one line per leg, rc captured
$ErrorActionPreference = 'Continue'
$legs = @(
  @('pool_dualrun_reconcile', 'python scripts\pool_dualrun_reconcile.py run'),
  @('compute_audit', 'python scripts\compute_audit.py'),
  @('py_watermark', 'python scripts\py_watermark.py probe'),
  @('update_daily', 'python scripts\update_daily.py'),
  @('market_regime', 'python scripts\market_regime.py'),
  @('strategy_scorecard', 'python scripts\strategy_scorecard.py'),
  @('market_clock_call', 'python scripts\market_clock_call.py run'),
  @('update_lhb', 'python scripts\update_lhb.py'),
  @('update_zt_pool', 'python scripts\update_zt_pool.py'),
  @('update_heat', 'python scripts\update_heat.py'),
  @('update_futures', 'python scripts\update_futures.py'),
  @('update_repo', 'python scripts\update_repo.py'),
  @('update_options', 'python scripts\update_options.py'),
  @('update_moneyflow', 'python scripts\update_moneyflow.py'),
  @('update_sina_mf', 'python scripts\update_sina_mf.py'),
  @('update_astock_daily', 'python scripts\update_astock_daily.py'),
  @('update_etf_daily', 'python scripts\update_etf_daily.py'),
  @('regime_thermo_build', 'python scripts\regime_thermo_build.py'),
  @('regime_gate_dualarm', 'python scripts\regime_gate_dualarm.py run'),
  @('rev_osc_signal_export', 'python scripts\rev_osc_signal_export.py run'),
  @('update_minute_feed', 'python scripts\update_minute_feed.py'),
  @('update_ths_panel', 'python scripts\update_ths_panel.py'),
  @('ah_panel_puller', 'python scripts\ah_panel_puller.py'),
  @('update_fund_premium', 'python scripts\update_fund_premium.py snapshot'),
  @('update_fundamental', 'python scripts\update_fundamental.py'),
  @('b_layer_filter', 'python -m firm.risk.b_layer_filter'),
  @('update_fund_statements', 'python scripts\update_fund_statements.py'),
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
  @('build_status', 'python -m monitor.build_status'),
  @('token_meter', 'python scripts\token_meter.py')
)
$fails = 0
foreach ($leg in $legs) {
  $name = $leg[0]
  Invoke-Expression $leg[1] *> $null
  $rc = $LASTEXITCODE
  if ($null -eq $rc) { $rc = 0 }
  Write-Output ("{0}={1}" -f $name, $rc)
  if ($rc -ne 0) { $fails++ }
}
Write-Output ("S6_FAILS={0}" -f $fails)
