# r414 bm-c S6 chain runner (r412 33-leg base verbatim + 4 new-bar-gated legs at protocol
# position; r413 precedent ran all 37 legs, each self-gates rc0 on no-new-bar,
# LAST_BAR=2026-09-30 Golden-Week). Zero-window: every leg via Tools\Invoke-SilentExe.ps1
# (CreateNoWindow). r559: >> per-leg append never >; r318: markers via Write-Host.
$ErrorActionPreference = 'Continue'
$log = 'results\_r414bmc_s6_runner.log'
Set-Content -Path $log -Value "S6 chain r414 bm-c start $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$legs = @(
    @('pool_dualrun_reconcile', 'scripts\pool_dualrun_reconcile.py', 'run'),
    @('compute_audit', 'scripts\compute_audit.py', ''),
    @('py_watermark', 'scripts\py_watermark.py', 'probe'),
    @('update_daily', 'scripts\update_daily.py', ''),
    @('market_regime', 'scripts\market_regime.py', ''),
    @('strategy_scorecard', 'scripts\strategy_scorecard.py', ''),
    @('market_clock_call', 'scripts\market_clock_call.py', 'run'),
    @('update_lhb', 'scripts\update_lhb.py', ''),
    @('update_heat', 'scripts\update_heat.py', ''),
    @('update_futures', 'scripts\update_futures.py', ''),
    @('update_repo', 'scripts\update_repo.py', ''),
    @('update_options', 'scripts\update_options.py', ''),
    @('update_moneyflow', 'scripts\update_moneyflow.py', ''),
    @('update_sina_mf', 'scripts\update_sina_mf.py', ''),
    @('update_astock_daily', 'scripts\update_astock_daily.py', ''),
    @('update_etf_daily', 'scripts\update_etf_daily.py', ''),
    @('rev_osc_signal_export', 'scripts\rev_osc_signal_export.py', 'run'),
    @('update_minute_feed', 'scripts\update_minute_feed.py', ''),
    @('update_ths_panel', 'scripts\update_ths_panel.py', ''),
    @('ah_panel_puller', 'scripts\ah_panel_puller.py', ''),
    @('update_fund_premium', 'scripts\update_fund_premium.py', 'snapshot'),
    @('update_fundamental', 'scripts\update_fundamental.py', ''),
    @('b_layer_filter', '-m', 'firm.risk.b_layer_filter'),
    @('live_paper', '-m', 'live.paper'),
    @('t35_open_fill_verify', 'scripts\t35_open_fill_verify.py', ''),
    @('t24_prospect_paper', 'scripts\t24_prospect_paper.py', 'run'),
    @('t24_prospect_promotion', 'scripts\t24_prospect_promotion.py', 'run'),
    @('aggressive_lab', 'scripts\aggressive_lab.py', 'paper'),
    @('alloc_paper', 'scripts\alloc_paper.py', 'run'),
    @('grid_paper', 'scripts\grid_paper.py', 'run'),
    @('system_v1_paper', 'scripts\system_v1_paper.py', 'run'),
    @('t35_paper_export', 'scripts\t35_paper_export.py', 'run'),
    @('daily_scorecard', 'scripts\daily_scorecard.py', ''),
    @('daily_report', 'scripts\daily_report.py', 'run'),
    @('ceo_live_usage', 'scripts\ceo_live_usage.py', ''),
    @('build_status', '-m', 'monitor.build_status'),
    @('token_meter', 'scripts\token_meter.py', '')
)
$fail = @()
foreach ($leg in $legs) {
    $name = $leg[0]
    if ($name -eq 'live_paper') { $env:BIGMONEY_REGIME_GUARD = 'enforce' }
    Add-Content -Path $log -Value "=== LEG $name ==="
    if ($leg[1] -eq '-m') {
        $out = & Tools\Invoke-SilentExe.ps1 -Exe python.exe -ArgString "-m $($leg[2])"
    } elseif ($leg[2] -eq '') {
        $out = & Tools\Invoke-SilentExe.ps1 -Exe python.exe -ArgString $leg[1]
    } else {
        $out = & Tools\Invoke-SilentExe.ps1 -Exe python.exe -ArgString "$($leg[1]) $($leg[2])"
    }
    if ($name -eq 'live_paper') { Remove-Item Env:BIGMONEY_REGIME_GUARD -ErrorAction SilentlyContinue }
    $rcv = $LASTEXITCODE
    if ($out) { Add-Content -Path $log -Value $out }
    Add-Content -Path $log -Value "LEG $name rc=$rcv"
    if ($rcv -ne 0) { $fail += "$name rc=$rcv" }
    Write-Host "LEG $name rc=$rcv"
}
Write-Host "S6_DONE fails=$($fail.Count)"
if ($fail.Count -gt 0) { Write-Host "FAILED: $($fail -join ', ')" }
