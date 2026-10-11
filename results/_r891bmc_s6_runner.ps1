$ErrorActionPreference = 'Continue'
$log = 'results\_r891bmc_s6_log.txt'
Remove-Item $log -ErrorAction SilentlyContinue
$legs = @(
    @('pool_dualrun', 'python scripts\pool_dualrun_reconcile.py run'),
    @('compute_audit', 'python scripts\compute_audit.py'),
    @('py_watermark', 'python scripts\py_watermark.py probe'),
    @('update_daily', 'python scripts\update_daily.py'),
    @('market_regime', 'python scripts\market_regime.py'),
    @('strategy_scorecard', 'python scripts\strategy_scorecard.py'),
    @('market_clock', 'python scripts\market_clock_call.py run'),
    @('update_lhb', 'python scripts\update_lhb.py'),
    @('update_zt_pool', 'python scripts\update_zt_pool.py'),
    @('update_heat', 'python scripts\update_heat.py'),
    @('update_futures', 'python scripts\update_futures.py'),
    @('update_repo', 'python scripts\update_repo.py'),
    @('update_options', 'python scripts\update_options.py'),
    @('update_moneyflow', 'python scripts\update_moneyflow.py'),
    @('update_sina_mf', 'python scripts\update_sina_mf.py'),
    @('update_astock_daily', 'python scripts\update_astock_daily.py'),
    @('update_etf_daily', 'python scripts\update_etf_daily.py'),
    @('regime_thermo_build', 'python scripts\regime_thermo_build.py'),
    @('regime_gate_dualarm', 'python scripts\regime_gate_dualarm.py run'),
    @('rev_osc_signal_export', 'python scripts\rev_osc_signal_export.py run'),
    @('update_minute_feed', 'python scripts\update_minute_feed.py'),
    @('update_ths_panel', 'python scripts\update_ths_panel.py'),
    @('ah_panel_puller', 'python scripts\ah_panel_puller.py'),
    @('update_fund_premium', 'python scripts\update_fund_premium.py snapshot'),
    @('update_fundamental', 'python scripts\update_fundamental.py'),
    @('b_layer_filter', 'python -m firm.risk.b_layer_filter'),
    @('update_fund_statements', 'python scripts\update_fund_statements.py'),
    @('daily_report', 'python scripts\daily_report.py run'),
    @('ceo_live_usage', 'python scripts\ceo_live_usage.py'),
    @('token_meter', 'python scripts\token_meter.py')
)
$red = 0
foreach ($leg in $legs) {
    $name = $leg[0]
    $out = Invoke-Expression $leg[1] 2>&1
    $rc = $LASTEXITCODE
    $tail = ($out | Select-Object -Last 1)
    Add-Content $log ("{0}|rc={1}|{2}" -f $name, $rc, $tail)
    if ($rc -ne 0) { $red++ ; Add-Content $log ("{0}|FULLTAIL|{1}" -f $name, (($out | Select-Object -Last 6) -join ' // ')) }
}
Add-Content $log ("S6-SUMMARY|legs={0}|red={1}" -f $legs.Count, $red)
Get-Content $log
