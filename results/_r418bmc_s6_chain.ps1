# r418 bm-c S6 chain runner -- Saturday golden-week no-new-bar face.
# Lane-guarded collectors run on all machines (honest no-op stdout off-lane).
# Live/paper legs skipped: no new bar (last bar 2026-09-30, golden week).
$ErrorActionPreference = 'Continue'
Set-Location $PSScriptRoot\..
$legs = @(
    @('dualrun',    'python', 'scripts\pool_dualrun_reconcile.py run'),
    @('audit',      'python', 'scripts\compute_audit.py'),
    @('wm_probe',   'python', 'scripts\py_watermark.py probe'),
    @('daily',      'python', 'scripts\update_daily.py'),
    @('regime',     'python', 'scripts\market_regime.py'),
    @('scorecard',  'python', 'scripts\strategy_scorecard.py'),
    @('clock_call', 'python', 'scripts\market_clock_call.py run'),
    @('lhb',        'python', 'scripts\update_lhb.py'),
    @('heat',       'python', 'scripts\update_heat.py'),
    @('futures',    'python', 'scripts\update_futures.py'),
    @('repo',       'python', 'scripts\update_repo.py'),
    @('options',    'python', 'scripts\update_options.py'),
    @('moneyflow',  'python', 'scripts\update_moneyflow.py'),
    @('sina_mf',    'python', 'scripts\update_sina_mf.py'),
    @('astock',     'python', 'scripts\update_astock_daily.py'),
    @('etf_daily',  'python', 'scripts\update_etf_daily.py'),
    @('rev_osc',    'python', 'scripts\rev_osc_signal_export.py run'),
    @('minute',     'python', 'scripts\update_minute_feed.py'),
    @('ths_panel',  'python', 'scripts\update_ths_panel.py'),
    @('ah_panel',   'python', 'scripts\ah_panel_puller.py'),
    @('fund_prem',  'python', 'scripts\update_fund_premium.py snapshot'),
    @('fundamental','python', 'scripts\update_fundamental.py'),
    @('b_layer',    'python', '-m firm.risk.b_layer_filter'),
    @('aggr_paper', 'python', 'scripts\aggressive_lab.py paper'),
    @('alloc_paper','python', 'scripts\alloc_paper.py run'),
    @('grid_paper', 'python', 'scripts\grid_paper.py run'),
    @('daily_rep',  'python', 'scripts\daily_report.py run'),
    @('live_usage', 'python', 'scripts\ceo_live_usage.py'),
    @('token',      'python', 'scripts\token_meter.py')
)
$fails = 0
foreach ($leg in $legs) {
    $name = $leg[0]
    Write-Output "=== $name ==="
    $args = $leg[2] -split ' '
    & python $args 2>&1 | Select-Object -Last 2
    $rc = $LASTEXITCODE
    Write-Output "[$name rc=$rc]"
    if ($rc -ne 0) { $fails++ }
}
Write-Output "S6_CHAIN_DONE fails=$fails / total=$($legs.Count)"
