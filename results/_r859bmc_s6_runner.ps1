$ErrorActionPreference = 'Continue'
$py = 'C:\Users\Dasheng\AppData\Local\Programs\Python\Python313\python.exe'
$log = 'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r859bmc_s6_log.txt'
$legs = @(
  @('pool_dualrun_reconcile', 'scripts/pool_dualrun_reconcile.py', 'run'),
  @('compute_audit', 'scripts/compute_audit.py', ''),
  @('py_watermark', 'scripts/py_watermark.py', 'probe'),
  @('update_daily', 'scripts/update_daily.py', ''),
  @('market_regime', 'scripts/market_regime.py', ''),
  @('strategy_scorecard', 'scripts/strategy_scorecard.py', ''),
  @('market_clock_call', 'scripts/market_clock_call.py', 'run'),
  @('update_lhb', 'scripts/update_lhb.py', ''),
  @('update_zt_pool', 'scripts/update_zt_pool.py', ''),
  @('zt_pool_crosscheck', 'scripts/zt_pool_crosscheck.py', ''),
  @('update_heat', 'scripts/update_heat.py', ''),
  @('update_futures', 'scripts/update_futures.py', ''),
  @('update_repo', 'scripts/update_repo.py', ''),
  @('update_options', 'scripts/update_options.py', ''),
  @('update_moneyflow', 'scripts/update_moneyflow.py', ''),
  @('update_sina_mf', 'scripts/update_sina_mf.py', ''),
  @('update_astock_daily', 'scripts/update_astock_daily.py', ''),
  @('update_etf_daily', 'scripts/update_etf_daily.py', ''),
  @('regime_thermo_build', 'scripts/regime_thermo_build.py', ''),
  @('regime_gate_evidence', 'scripts/regime_gate_evidence.py', 'run'),
  @('rev_osc_signal_export', 'scripts/rev_osc_signal_export.py', 'run'),
  @('update_minute_feed', 'scripts/update_minute_feed.py', ''),
  @('update_ths_panel', 'scripts/update_ths_panel.py', ''),
  @('ah_panel_puller', 'scripts/ah_panel_puller.py', ''),
  @('update_fund_premium', 'scripts/update_fund_premium.py', 'snapshot'),
  @('update_fundamental', 'scripts/update_fundamental.py', ''),
  @('b_layer_filter', '-m', 'firm.risk.b_layer_filter'),
  @('update_fund_statements', 'scripts/update_fund_statements.py', ''),
  @('live_paper', '-m', 'live.paper'),
  @('t35_open_fill_verify', 'scripts/t35_open_fill_verify.py', ''),
  @('t24_prospect_paper', 'scripts/t24_prospect_paper.py', 'run'),
  @('t24_prospect_promotion', 'scripts/t24_prospect_promotion.py', 'run'),
  @('aggressive_lab', 'scripts/aggressive_lab.py', 'paper'),
  @('alloc_paper', 'scripts/alloc_paper.py', 'run'),
  @('grid_paper', 'scripts/grid_paper.py', 'run'),
  @('cta_p1_paper', 'scripts/cta_p1_paper.py', 'run'),
  @('system_v1_paper', 'scripts/system_v1_paper.py', 'run'),
  @('t35_paper_export', 'scripts/t35_paper_export.py', 'run'),
  @('daily_scorecard', 'scripts/daily_scorecard.py', ''),
  @('daily_report', 'scripts/daily_report.py', 'run'),
  @('ceo_live_usage', 'scripts/ceo_live_usage.py', ''),
  @('build_status', '-m', 'monitor.build_status'),
  @('token_meter', 'scripts/token_meter.py', '')
)
"r859 bm-c S6 chain run $(Get-Date -Format o) legs=$($legs.Count)" | Out-File $log -Encoding utf8
$bad = 0
foreach ($leg in $legs) {
  $name = $leg[0]; $target = $leg[1]; $arg = $leg[2]
  "`n===== $name =====`n`$ $py $target $arg" | Out-File $log -Append -Encoding utf8
  if ($target -eq '-m') {
    $out = & $py -m $arg 2>&1
  } elseif ($arg -eq '') {
    $out = & $py $target 2>&1
  } else {
    $out = & $py $target $arg 2>&1
  }
  $out | Out-File $log -Append -Encoding utf8
  $rc = $LASTEXITCODE
  "[rc=$rc]" | Out-File $log -Append -Encoding utf8
  if ($rc -ne 0) { $bad++; Write-Host "LEG-FAIL ${name} rc=$rc" }
}
"`nDONE $(Get-Date -Format o) bad=$bad" | Out-File $log -Append -Encoding utf8
Write-Host "S6-DONE bad=$bad legs=$($legs.Count)"
