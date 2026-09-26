# r276 bm-b S6 chain driver -- run all legs in order, report exit codes only.
$legs = @(
  @('compute_audit',   'python', 'scripts\compute_audit.py'),
  @('watermark',       'python', 'scripts\py_watermark.py', 'probe'),
  @('daily',           'python', 'scripts\update_daily.py'),
  @('regime',          'python', 'scripts\market_regime.py'),
  @('scorecard',       'python', 'scripts\strategy_scorecard.py'),
  @('clock',           'python', 'scripts\market_clock_call.py', 'run'),
  @('lhb',             'python', 'scripts\update_lhb.py'),
  @('heat',            'python', 'scripts\update_heat.py'),
  @('futures',         'python', 'scripts\update_futures.py'),
  @('options',        'python', 'scripts\update_options.py'),
  @('moneyflow',       'python', 'scripts\update_moneyflow.py'),
  @('sina_mf',         'python', 'scripts\update_sina_mf.py'),
  @('ths_panel',       'python', 'scripts\update_ths_panel.py'),
  @('ah_panel',        'python', 'scripts\ah_panel_puller.py'),
  @('fund_premium',    'python', 'scripts\update_fund_premium.py', 'snapshot'),
  @('fundamental',     'python', 'scripts\update_fundamental.py'),
  @('blf',             'python', '-m', 'firm.risk.b_layer_filter'),
  @('aggr_paper',      'python', 'scripts\aggressive_lab.py', 'paper'),
  @('alloc_paper',     'python', 'scripts\alloc_paper.py', 'run'),
  @('grid_paper',      'python', 'scripts\grid_paper.py', 'run'),
  @('t35_export',      'python', 'scripts\t35_paper_export.py', 'run'),
  @('dsc',             'python', 'scripts\daily_scorecard.py'),
  @('daily_report',    'python', 'scripts\daily_report.py', 'run'),
  @('monitor',         'python', '-m', 'monitor.build_status'),
  @('token_meter',     'python', 'scripts\token_meter.py')
)
$fails = @()
foreach ($leg in $legs) {
  $name = $leg[0]
  $out = & $leg[1] $leg[2..($leg.Count-1)] 2>&1
  $rc = $LASTEXITCODE
  $tail = ($out | Select-Object -Last 2) -join ' | '
  Write-Output ("{0} rc={1} :: {2}" -f $name, $rc, $tail)
  if ($rc -ne 0) { $fails += ("{0}:{1}" -f $name, $rc) }
}
Write-Output ("CHAIN_DONE fails=" + ($fails -join ','))
