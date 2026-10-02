$legs = @(
    @('dualrun',    'python', @('scripts\pool_dualrun_reconcile.py', 'run')),
    @('audit',      'python', @('scripts\compute_audit.py')),
    @('wm',         'python', @('scripts\py_watermark.py', 'probe')),
    @('daily',      'python', @('scripts\update_daily.py')),
    @('regime',     'python', @('scripts\market_regime.py')),
    @('scorecard',  'python', @('scripts\strategy_scorecard.py')),
    @('clock',      'python', @('scripts\market_clock_call.py', 'run')),
    @('lhb',        'python', @('scripts\update_lhb.py')),
    @('astock',     'python', @('scripts\update_astock_daily.py')),
    @('etf',        'python', @('scripts\update_etf_daily.py')),
    @('revosc',     'python', @('scripts\rev_osc_signal_export.py', 'run')),
    @('minfeed',    'python', @('scripts\update_minute_feed.py')),
    @('fund',       'python', @('scripts\update_fundamental.py')),
    @('bmask',      'python', @('-m', 'firm.risk.b_layer_filter')),
    @('aggr',       'python', @('scripts\aggressive_lab.py', 'paper')),
    @('alloc',      'python', @('scripts\alloc_paper.py', 'run')),
    @('grid',       'python', @('scripts\grid_paper.py', 'run')),
    @('dreport',    'python', @('scripts\daily_report.py', 'run')),
    @('ceolive',    'python', @('scripts\ceo_live_usage.py')),
    @('token',      'python', @('scripts\token_meter.py'))
)
$fails = @()
foreach ($leg in $legs) {
    $name = $leg[0]; $exe = $leg[1]; $rest = $leg[2]
    & $exe @rest *> "$env:TEMP\s6leg_$name.log"
    $rc = $LASTEXITCODE
    Write-Host ("{0,-10} rc={1}" -f $name, $rc)
    if ($rc -ne 0) { $fails += ("$name rc=$rc") }
}
Write-Host "FAILS: $($fails.Count)"
if ($fails.Count -gt 0) { $fails | ForEach-Object { Write-Host "  $_" } }
