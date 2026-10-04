# r677 bm-a S6 chain driver (leg runner; logs rc per leg) -- adapted from r674 driver per r461 law
Set-StrictMode -Off
$log = 'results\_r677bma_s6_log.txt'
"=== r677 bm-a S6 chain start $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss+08:00') ===" | Out-File $log -Encoding utf8
$legs = @(
  @('pool_dualrun', 'python scripts\pool_dualrun_reconcile.py run'),
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
  @('rev_osc_export', 'python scripts\rev_osc_signal_export.py run'),
  @('update_minute_feed', 'python scripts\update_minute_feed.py'),
  @('update_ths_panel', 'python scripts\update_ths_panel.py'),
  @('ah_panel_puller', 'python scripts\ah_panel_puller.py'),
  @('update_fund_premium', 'python scripts\update_fund_premium.py snapshot'),
  @('update_fundamental', 'python scripts\update_fundamental.py'),
  @('b_layer_filter', 'python -m firm.risk.b_layer_filter'),
  @('update_fund_statements', 'python scripts\update_fund_statements.py'),
  @('t24_prospect_paper', 'python scripts\t24_prospect_paper.py run'),
  @('t24_promotion', 'python scripts\t24_prospect_promotion.py run'),
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
$bad = 0
foreach ($leg in $legs) {
  $name = $leg[0]; $cmd = $leg[1]
  $out = cmd /c "$cmd 2>&1"
  $rc = $LASTEXITCODE
  $tail = ($out | Select-Object -Last 2) -join ' | '
  "[$name] rc=$rc :: $tail" | Out-File $log -Append -Encoding utf8
  if ($rc -ne 0) { $bad++; Write-Host "NONZERO $name rc=$rc" }
}
"=== chain done bad=$bad legs=$($legs.Count) $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Append -Encoding utf8
Write-Host "S6 chain complete: bad=$bad / legs=$($legs.Count)"

