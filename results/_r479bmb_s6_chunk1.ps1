# r479 bm-b S6 chain chunk 1 (legs 1-23) - per-leg rc logged to results/_r479bmb_s6_log.txt
$ErrorActionPreference = 'Continue'
$log = 'results\_r479bmb_s6_log.txt'
"=== r479 bm-b S6 chunk1 start $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Encoding utf8
$legs = @(
    @('pool_dualrun_reconcile', 'python', 'scripts\pool_dualrun_reconcile.py run'),
    @('compute_audit', 'python', 'scripts\compute_audit.py'),
    @('py_watermark', 'python', 'scripts\py_watermark.py probe'),
    @('update_daily', 'python', 'scripts\update_daily.py'),
    @('market_regime', 'python', 'scripts\market_regime.py'),
    @('strategy_scorecard', 'python', 'scripts\strategy_scorecard.py'),
    @('market_clock_call', 'python', 'scripts\market_clock_call.py run'),
    @('update_lhb', 'python', 'scripts\update_lhb.py'),
    @('update_heat', 'python', 'scripts\update_heat.py'),
    @('update_futures', 'python', 'scripts\update_futures.py'),
    @('update_repo', 'python', 'scripts\update_repo.py'),
    @('update_options', 'python', 'scripts\update_options.py'),
    @('update_moneyflow', 'python', 'scripts\update_moneyflow.py'),
    @('update_sina_mf', 'python', 'scripts\update_sina_mf.py'),
    @('update_astock_daily', 'python', 'scripts\update_astock_daily.py'),
    @('update_etf_daily', 'python', 'scripts\update_etf_daily.py'),
    @('rev_osc_signal_export', 'python', 'scripts\rev_osc_signal_export.py run'),
    @('update_minute_feed', 'python', 'scripts\update_minute_feed.py'),
    @('update_ths_panel', 'python', 'scripts\update_ths_panel.py'),
    @('ah_panel_puller', 'python', 'scripts\ah_panel_puller.py'),
    @('update_fund_premium', 'python', 'scripts\update_fund_premium.py snapshot'),
    @('update_fundamental', 'python', 'scripts\update_fundamental.py'),
    @('b_layer_filter', 'python', '-m firm.risk.b_layer_filter')
)
foreach ($leg in $legs) {
    $name = $leg[0]
    $t0 = Get-Date
    Invoke-Expression $leg[2] *>&1 | Out-File $log -Append -Encoding utf8
    $rc = $LASTEXITCODE
    $dt = ((Get-Date) - $t0).TotalSeconds
    $line = "LEG $name rc=$rc ${dt}s"
    $line | Out-File $log -Append -Encoding utf8
    Write-Output $line
}
"=== chunk1 end $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Append -Encoding utf8
