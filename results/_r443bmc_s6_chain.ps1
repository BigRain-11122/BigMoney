# r443 bm-c S6 chain runner -- golden-week no-new-bar face (last bar 2026-09-30, Sunday 10-04).
# r418 template; all legs routed through Tools\Invoke-SilentExe.ps1 (zero-window law, defense-in-depth).
# Live/paper new-bar legs skipped: no new bar (golden week). Host-guarded faces omitted per r418 pattern.
$ErrorActionPreference = 'Continue'
Set-Location $PSScriptRoot\..
$legs = @(
    @('dualrun',    'scripts\pool_dualrun_reconcile.py run'),
    @('audit',      'scripts\compute_audit.py'),
    @('wm_probe',   'scripts\py_watermark.py probe'),
    @('daily',      'scripts\update_daily.py'),
    @('regime',     'scripts\market_regime.py'),
    @('scorecard',  'scripts\strategy_scorecard.py'),
    @('clock_call', 'scripts\market_clock_call.py run'),
    @('lhb',        'scripts\update_lhb.py'),
    @('heat',       'scripts\update_heat.py'),
    @('futures',    'scripts\update_futures.py'),
    @('repo',       'scripts\update_repo.py'),
    @('options',    'scripts\update_options.py'),
    @('moneyflow',  'scripts\update_moneyflow.py'),
    @('sina_mf',    'scripts\update_sina_mf.py'),
    @('astock',     'scripts\update_astock_daily.py'),
    @('etf_daily',  'scripts\update_etf_daily.py'),
    @('rev_osc',    'scripts\rev_osc_signal_export.py run'),
    @('minute',     'scripts\update_minute_feed.py'),
    @('ths_panel',  'scripts\update_ths_panel.py'),
    @('ah_panel',   'scripts\ah_panel_puller.py'),
    @('fund_prem',  'scripts\update_fund_premium.py snapshot'),
    @('fundamental','scripts\update_fundamental.py'),
    @('b_layer',    '-m firm.risk.b_layer_filter'),
    @('aggr_paper', 'scripts\aggressive_lab.py paper'),
    @('alloc_paper','scripts\alloc_paper.py run'),
    @('grid_paper', 'scripts\grid_paper.py run'),
    @('daily_rep',  'scripts\daily_report.py run'),
    @('live_usage', 'scripts\ceo_live_usage.py'),
    @('token',      'scripts\token_meter.py')
)
$fails = 0
foreach ($leg in $legs) {
    $name = $leg[0]
    $argstr = $leg[1]
    $lines = & Tools\Invoke-SilentExe.ps1 -Exe python -ArgString $argstr -IncludeStderr
    $rc = $LASTEXITCODE
    $tail = @($lines | Select-Object -Last 2)
    Write-Output "=== $name rc=$rc ==="
    foreach ($t in $tail) { Write-Output ("  " + $t) }
    if ($rc -ne 0) { $fails++ }
}
Write-Output "S6_CHAIN_DONE fails=$fails / total=$($legs.Count)"
