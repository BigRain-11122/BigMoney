$env:PYTHONIOENCODING = 'utf-8'
$legs = @(
    @('dualrun', 'scripts/pool_dualrun_reconcile.py', 'run'),
    @('audit', 'scripts/compute_audit.py', ''),
    @('wmprobe', 'scripts/py_watermark.py', 'probe'),
    @('daily', 'scripts/update_daily.py', ''),
    @('regime', 'scripts/market_regime.py', ''),
    @('clock', 'scripts/market_clock_call.py', 'run'),
    @('lhb', 'scripts/update_lhb.py', ''),
    @('ztpool', 'scripts/update_zt_pool.py', ''),
    @('heat', 'scripts/update_heat.py', ''),
    @('futures', 'scripts/update_futures.py', ''),
    @('repo', 'scripts/update_repo.py', ''),
    @('options', 'scripts/update_options.py', ''),
    @('moneyflow', 'scripts/update_moneyflow.py', ''),
    @('sinamf', 'scripts/update_sina_mf.py', ''),
    @('astock', 'scripts/update_astock_daily.py', ''),
    @('etfdaily', 'scripts/update_etf_daily.py', ''),
    @('thermo', 'scripts/regime_thermo_build.py', ''),
    @('dualarm', 'scripts/regime_gate_dualarm.py', 'run'),
    @('revosc', 'scripts/rev_osc_signal_export.py', 'run'),
    @('minutefeed', 'scripts/update_minute_feed.py', ''),
    @('ths', 'scripts/update_ths_panel.py', ''),
    @('ahpanel', 'scripts/ah_panel_puller.py', ''),
    @('fundpremium', 'scripts/update_fund_premium.py', 'snapshot'),
    @('fundamental', 'scripts/update_fundamental.py', ''),
    @('blayer', '-m', 'firm.risk.b_layer_filter'),
    @('fundstmt', 'scripts/update_fund_statements.py', ''),
    @('dailyreport', 'scripts/daily_report.py', 'run'),
    @('liveusage', 'scripts/ceo_live_usage.py', ''),
    @('tokenmeter', 'scripts/token_meter.py', '')
)
$report = @()
foreach ($l in $legs) {
    $name = $l[0]; $script = $l[1]; $arg = $l[2]
    if ($script -eq '-m') {
        $out = & python -m firm.risk.b_layer_filter 2>&1
        $rc = $LASTEXITCODE
    } else {
        if ($arg -ne '') { $out = & python $script $arg 2>&1 } else { $out = & python $script 2>&1 }
        $rc = $LASTEXITCODE
    }
    $last = ($out | Select-Object -Last 1)
    if ($null -eq $last) { $last = '(no output)' }
    $line = "$name rc=$rc | $last"
    $report += $line
    Write-Output $line
}
$report | Out-File -FilePath 'results/_r996bmc_s6_light.txt' -Encoding utf8
