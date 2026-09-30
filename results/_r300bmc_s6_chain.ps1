# r300 S6 chain runner: execute legs in canonical order, print compact leg/rc lines
$legs = @(
  @('dualrun',    'python scripts\pool_dualrun_reconcile.py run'),
  @('cmpaudit',   'python scripts\compute_audit.py'),
  @('pywm',       'python scripts\py_watermark.py probe'),
  @('daily',      'python scripts\update_daily.py'),
  @('regime',     'python scripts\market_regime.py'),
  @('scorecard',  'python scripts\strategy_scorecard.py'),
  @('clockcall',  'python scripts\market_clock_call.py run'),
  @('lhb',        'python scripts\update_lhb.py'),
  @('heat',       'python scripts\update_heat.py'),
  @('futures',    'python scripts\update_futures.py'),
  @('repo',       'python scripts\update_repo.py'),
  @('options',    'python scripts\update_options.py'),
  @('moneyflow',  'python scripts\update_moneyflow.py'),
  @('sinamf',     'python scripts\update_sina_mf.py'),
  @('astock',     'python scripts\update_astock_daily.py'),
  @('etfdaily',   'python scripts\update_etf_daily.py'),
  @('revosc',     'python scripts\rev_osc_signal_export.py run'),
  @('minfeed',    'python scripts\update_minute_feed.py'),
  @('thspanel',   'python scripts\update_ths_panel.py'),
  @('ahpanel',    'python scripts\ah_panel_puller.py'),
  @('fundprem',   'python scripts\update_fund_premium.py snapshot'),
  @('fundament',  'python scripts\update_fundamental.py'),
  @('blayer',     'python -m firm.risk.b_layer_filter'),
  @('aggrpaper',  'python scripts\aggressive_lab.py paper'),
  @('allocpaper', 'python scripts\alloc_paper.py run'),
  @('gridpaper',  'python scripts\grid_paper.py run'),
  @('sysv1paper', 'python scripts\system_v1_paper.py run'),
  @('t35export',  'python scripts\t35_paper_export.py run'),
  @('dailysc',    'python scripts\daily_scorecard.py'),
  @('dailyrep',   'python scripts\daily_report.py run'),
  @('liveusage',  'python scripts\ceo_live_usage.py'),
  @('buildstat',  'python -m monitor.build_status'),
  @('tokenmeter', 'python scripts\token_meter.py')
)
$bad = 0
foreach ($leg in $legs) {
  $name = $leg[0]; $cmd = $leg[1]
  $out = Invoke-Expression $cmd 2>&1 | Out-String
  $rc = $LASTEXITCODE
  $last = ($out.Trim() -split "`r?`n") | Select-Object -Last 1
  if ($null -eq $last) { $last = '' }
  Write-Output ("LEG {0} rc={1} :: {2}" -f $name, $rc, $last.Substring(0, [Math]::Min(110, $last.Length)))
  if ($rc -ne 0) { $bad++ }
}
Write-Output ("S6 SUMMARY: legs={0} nonzero_rc={1}" -f $legs.Count, $bad)
