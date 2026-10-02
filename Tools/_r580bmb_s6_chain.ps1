# r580 bm-b S6 chain runner (holiday no-op faces; rc-per-leg, no *> overwrite per r559)
$legs = @(
    @('dualrun',   'python', @('scripts\pool_dualrun_reconcile.py','run')),
    @('compute_audit', 'python', @('scripts\compute_audit.py')),
    @('py_watermark', 'python', @('scripts\py_watermark.py','probe')),
    @('update_daily', 'python', @('scripts\update_daily.py')),
    @('market_regime', 'python', @('scripts\market_regime.py')),
    @('scorecard', 'python', @('scripts\strategy_scorecard.py')),
    @('clock_call', 'python', @('scripts\market_clock_call.py','run')),
    @('lhb', 'python', @('scripts\update_lhb.py')),
    @('heat', 'python', @('scripts\update_heat.py')),
    @('futures', 'python', @('scripts\update_futures.py')),
    @('repo', 'python', @('scripts\update_repo.py')),
    @('options', 'python', @('scripts\update_options.py')),
    @('moneyflow', 'python', @('scripts\update_moneyflow.py')),
    @('sina_mf', 'python', @('scripts\update_sina_mf.py')),
    @('astock_daily', 'python', @('scripts\update_astock_daily.py')),
    @('etf_daily', 'python', @('scripts\update_etf_daily.py')),
    @('rev_osc', 'python', @('scripts\rev_osc_signal_export.py','run')),
    @('minute_feed', 'python', @('scripts\update_minute_feed.py')),
    @('ths_panel', 'python', @('scripts\update_ths_panel.py')),
    @('ah_panel', 'python', @('scripts\ah_panel_puller.py')),
    @('fund_premium', 'python', @('scripts\update_fund_premium.py','snapshot')),
    @('fundamental', 'python', @('scripts\update_fundamental.py')),
    @('b_layer', 'python', @('-m','firm.risk.b_layer_filter')),
    @('daily_scorecard', 'python', @('scripts\daily_scorecard.py')),
    @('daily_report', 'python', @('scripts\daily_report.py','run')),
    @('ceo_live', 'python', @('scripts\ceo_live_usage.py')),
    @('build_status', 'python', @('-m','monitor.build_status')),
    @('token_meter', 'python', @('scripts\token_meter.py'))
)
foreach ($leg in $legs) {
    $name = $leg[0]
    $out = & $leg[1] $leg[2] 2>&1
    $rc = $LASTEXITCODE
    $tail = ($out | Select-Object -Last 1)
    if ($rc -ne 0) { $tail = ($out | Select-Object -Last 3) -join ' | ' }
    Write-Output ("{0} rc={1} :: {2}" -f $name, $rc, $tail)
}
