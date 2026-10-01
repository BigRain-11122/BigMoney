# S6 chain r528 bm-a -- canonical order, rc capture, host-stream leg lines
$ErrorActionPreference = 'Continue'
$log = 'results\_r528bma_s6_log.txt'
Remove-Item $log -ErrorAction SilentlyContinue
$legs = @(
  @('dualrun',   'python', @('scripts\pool_dualrun_reconcile.py','run')),
  @('audit',     'python', @('scripts\compute_audit.py')),
  @('wmprobe',   'python', @('scripts\py_watermark.py','probe')),
  @('daily',     'python', @('scripts\update_daily.py')),
  @('regime',    'python', @('scripts\market_regime.py')),
  @('scorecard', 'python', @('scripts\strategy_scorecard.py')),
  @('clock',     'python', @('scripts\market_clock_call.py','run')),
  @('lhb',       'python', @('scripts\update_lhb.py')),
  @('heat',      'python', @('scripts\update_heat.py')),
  @('futures',   'python', @('scripts\update_futures.py')),
  @('repo',      'python', @('scripts\update_repo.py')),
  @('options',   'python', @('scripts\update_options.py')),
  @('mf',        'python', @('scripts\update_moneyflow.py')),
  @('sinamf',    'python', @('scripts\update_sina_mf.py')),
  @('astock',    'python', @('scripts\update_astock_daily.py')),
  @('etfdaily',  'python', @('scripts\update_etf_daily.py')),
  @('revosc',    'python', @('scripts\rev_osc_signal_export.py','run')),
  @('minfeed',   'python', @('scripts\update_minute_feed.py')),
  @('ths',       'python', @('scripts\update_ths_panel.py')),
  @('ah',        'python', @('scripts\ah_panel_puller.py')),
  @('fundprem',  'python', @('scripts\update_fund_premium.py','snapshot')),
  @('fundament', 'python', @('scripts\update_fundamental.py')),
  @('blayer',    'python', @('-m','firm.risk.b_layer_filter')),
  @('aggr',      'python', @('scripts\aggressive_lab.py','paper')),
  @('alloc',     'python', @('scripts\alloc_paper.py','run')),
  @('grid',      'python', @('scripts\grid_paper.py','run')),
  @('sysv1',     'python', @('scripts\system_v1_paper.py','run')),
  @('t35exp',    'python', @('scripts\t35_paper_export.py','run')),
  @('dscore',    'python', @('scripts\daily_scorecard.py')),
  @('dreport',   'python', @('scripts\daily_report.py','run')),
  @('ceolive',   'python', @('scripts\ceo_live_usage.py'))
)
$rcs = @()
foreach ($leg in $legs) {
  $name = $leg[0]; $exe = $leg[1]; $argList = [string[]]$leg[2]
  $out = & $exe @argList 2>&1
  $rc = $LASTEXITCODE
  $rcs += "$name=$rc"
  $tail = ($out | Select-Object -Last 2) -join ' | '
  Add-Content -Path $log -Value ("LEG $name rc=$rc :: $tail") -Encoding UTF8
  Write-Host ("LEG {0} rc={1}" -f $name, $rc)
}
# build_status + token_meter last
$null = & python -m monitor.build_status 2>&1
Add-Content -Path $log -Value ("LEG build_status rc={0}" -f $LASTEXITCODE) -Encoding UTF8
Write-Host ("LEG build_status rc={0}" -f $LASTEXITCODE)
$null = & python scripts\token_meter.py 2>&1
Add-Content -Path $log -Value ("LEG token rc={0}" -f $LASTEXITCODE) -Encoding UTF8
Write-Host ("LEG token rc={0}" -f $LASTEXITCODE)
Write-Host ("RC-SUMMARY: " + ($rcs -join ' '))
