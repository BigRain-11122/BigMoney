# r448 bm-c S6 chain runner -- golden-week no-new-bar face (last bar 2026-09-30, Sunday 10-04).
# r444 template extended to full 37-leg protocol accounting (r446 caliber): new-bar legs run
# and no-op/veto honestly (no BIGMONEY_REGIME_GUARD set: no new bar this window).
# All legs routed through Tools\Invoke-SilentExe.ps1 (zero-window law, defense-in-depth).
$ErrorActionPreference = 'Continue'
Set-Location $PSScriptRoot\..
$env:PYTHONUTF8 = '1'
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
    @('live_paper', '-m live.paper'),
    @('t35_fill',   'scripts\t35_open_fill_verify.py'),
    @('prosp_paper','scripts\t24_prospect_paper.py run'),
    @('prosp_promo','scripts\t24_prospect_promotion.py run'),
    @('aggr_paper', 'scripts\aggressive_lab.py paper'),
    @('alloc_paper','scripts\alloc_paper.py run'),
    @('grid_paper', 'scripts\grid_paper.py run'),
    @('system_v1', 'scripts\system_v1_paper.py run'),
    @('t35_export', 'scripts\t35_paper_export.py run'),
    @('daily_score','scripts\daily_scorecard.py'),
    @('daily_rep',  'scripts\daily_report.py run'),
    @('live_usage', 'scripts\ceo_live_usage.py'),
    @('build_stat', '-m monitor.build_status'),
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
