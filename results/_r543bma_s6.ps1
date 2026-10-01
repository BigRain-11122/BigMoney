# S6 chain runner r543 bm-a (per-leg rc echo; dualrun BEFORE compute_audit per prompt order)
$legs = @(
  @('dualrun',      'python', @('scripts\pool_dualrun_reconcile.py','run')),
  @('compute_audit','python', @('scripts\compute_audit.py')),
  @('watermark',    'python', @('scripts\py_watermark.py','probe')),
  @('update_daily', 'python', @('scripts\update_daily.py')),
  @('regime',       'python', @('scripts\market_regime.py')),
  @('scorecard',    'python', @('scripts\strategy_scorecard.py')),
  @('mktclock',     'python', @('scripts\market_clock_call.py','run')),
  @('lhb',          'python', @('scripts\update_lhb.py')),
  @('heat',         'python', @('scripts\update_heat.py')),
  @('futures',      'python', @('scripts\update_futures.py')),
  @('repo',         'python', @('scripts\update_repo.py')),
  @('options',      'python', @('scripts\update_options.py')),
  @('moneyflow',    'python', @('scripts\update_moneyflow.py')),
  @('sina_mf',      'python', @('scripts\update_sina_mf.py')),
  @('astock_daily', 'python', @('scripts\update_astock_daily.py')),
  @('etf_daily',    'python', @('scripts\update_etf_daily.py')),
  @('rev_osc',      'python', @('scripts\rev_osc_signal_export.py','run')),
  @('minute_feed',  'python', @('scripts\update_minute_feed.py')),
  @('ths_panel',    'python', @('scripts\update_ths_panel.py')),
  @('ah_panel',     'python', @('scripts\ah_panel_puller.py')),
  @('fund_prem',    'python', @('scripts\update_fund_premium.py','snapshot')),
  @('fundamental',  'python', @('scripts\update_fundamental.py')),
  @('b_layer',      'python', @('-m','firm.risk.b_layer_filter')),
  @('live_paper',   'python', @('-m','live.paper')),
  @('t35_fill',     'python', @('scripts\t35_open_fill_verify.py')),
  @('prospect',     'python', @('scripts\t24_prospect_paper.py','run')),
  @('promotion',    'python', @('scripts\t24_prospect_promotion.py','run')),
  @('aggr_paper',   'python', @('scripts\aggressive_lab.py','paper')),
  @('alloc_paper',  'python', @('scripts\alloc_paper.py','run')),
  @('grid_paper',   'python', @('scripts\grid_paper.py','run')),
  @('sys_v1_paper', 'python', @('scripts\system_v1_paper.py','run')),
  @('t35_export',   'python', @('scripts\t35_paper_export.py','run')),
  @('dscore',       'python', @('scripts\daily_scorecard.py')),
  @('daily_report', 'python', @('scripts\daily_report.py','run')),
  @('ceo_usage',    'python', @('scripts\ceo_live_usage.py')),
  @('build_status', 'python', @('-m','monitor.build_status')),
  @('token_meter',  'python', @('scripts\token_meter.py'))
)
$fails = @()
foreach ($leg in $legs) {
  $name = $leg[0]; $exe = $leg[1]; $args = $leg[2]
  $out = & $exe @args 2>&1
  $rc = $LASTEXITCODE
  $last = ($out | Select-Object -Last 1)
  Write-Host ("LEG {0} rc={1} :: {2}" -f $name, $rc, $last)
  if ($rc -ne 0) { $fails += ("{0} rc={1}" -f $name, $rc) }
}
Write-Host ("S6 DONE fails={0}" -f $fails.Count)
if ($fails.Count -gt 0) { $fails | ForEach-Object { Write-Host "FAIL $_" } }
