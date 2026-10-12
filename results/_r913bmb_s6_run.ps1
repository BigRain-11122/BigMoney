# r913 bm-b S6 chain runner (r911 42-leg pattern verbatim, ASCII comments only)
$ErrorActionPreference = 'Continue'
$log = 'results\_r913bmb_s6_log.txt'
"r913 bm-b S6 chain start $(Get-Date -Format o)" | Set-Content $log -Encoding UTF8
$legs = @(
  @('pool_dualrun_reconcile', 'scripts\pool_dualrun_reconcile.py run'),
  @('compute_audit', 'scripts\compute_audit.py'),
  @('py_watermark', 'scripts\py_watermark.py probe'),
  @('update_daily', 'scripts\update_daily.py'),
  @('market_regime', 'scripts\market_regime.py'),
  @('strategy_scorecard', 'scripts\strategy_scorecard.py'),
  @('market_clock_call', 'scripts\market_clock_call.py run'),
  @('update_lhb', 'scripts\update_lhb.py'),
  @('update_zt_pool', 'scripts\update_zt_pool.py'),
  @('update_heat', 'scripts\update_heat.py'),
  @('update_futures', 'scripts\update_futures.py'),
  @('update_repo', 'scripts\update_repo.py'),
  @('update_options', 'scripts\update_options.py'),
  @('update_moneyflow', 'scripts\update_moneyflow.py'),
  @('update_sina_mf', 'scripts\update_sina_mf.py'),
  @('update_astock_daily', 'scripts\update_astock_daily.py'),
  @('update_etf_daily', 'scripts\update_etf_daily.py'),
  @('regime_thermo_build', 'scripts\regime_thermo_build.py'),
  @('regime_gate_dualarm', 'scripts\regime_gate_dualarm.py run'),
  @('rev_osc_signal_export', 'scripts\rev_osc_signal_export.py run'),
  @('update_minute_feed', 'scripts\update_minute_feed.py'),
  @('update_ths_panel', 'scripts\update_ths_panel.py'),
  @('ah_panel_puller', 'scripts\ah_panel_puller.py'),
  @('update_fund_premium', 'scripts\update_fund_premium.py snapshot'),
  @('update_fundamental', 'scripts\update_fundamental.py'),
  @('b_layer_filter', '-m firm.risk.b_layer_filter'),
  @('update_fund_statements', 'scripts\update_fund_statements.py'),
  @('live_paper', '-m live.paper'),
  @('t35_open_fill_verify', 'scripts\t35_open_fill_verify.py'),
  @('t24_prospect_paper', 'scripts\t24_prospect_paper.py run'),
  @('t24_prospect_promotion', 'scripts\t24_prospect_promotion.py run'),
  @('aggressive_lab', 'scripts\aggressive_lab.py paper'),
  @('alloc_paper', 'scripts\alloc_paper.py run'),
  @('grid_paper', 'scripts\grid_paper.py run'),
  @('system_v1_paper', 'scripts\system_v1_paper.py run'),
  @('t35_paper_export', 'scripts\t35_paper_export.py run'),
  @('daily_scorecard', 'scripts\daily_scorecard.py'),
  @('daily_report', 'scripts\daily_report.py run'),
  @('ceo_live_usage', 'scripts\ceo_live_usage.py'),
  @('build_status', '-m monitor.build_status'),
  @('token_meter', 'scripts\token_meter.py')
)
$bad = 0
foreach ($leg in $legs) {
  $name = $leg[0]; $argline = $leg[1]
  $env:BIGMONEY_REGIME_GUARD = if ($name -eq 'live_paper') { 'enforce' } else { $null }
  $t0 = Get-Date
  $out = & python $argline.Split(' ') 2>&1
  $rc = $LASTEXITCODE
  $dt = ((Get-Date) - $t0).TotalSeconds
  "=== $name rc=$rc $([math]::Round($dt,1))s" | Add-Content $log -Encoding UTF8
  if ($out) { ($out | Select-Object -First 40) | Add-Content $log -Encoding UTF8 }
  if ($rc -ne 0) { $bad++ }
  $env:BIGMONEY_REGIME_GUARD = $null
}
"r913 S6 chain done rc_nonzero=$bad of $($legs.Count)" | Add-Content $log -Encoding UTF8
Write-Output "S6 done: nonzero=$bad of $($legs.Count); log=$log"
