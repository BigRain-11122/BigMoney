# r561 bm-a S6 chain runner (per-leg rc logging; Write-Host diagnostics per r318 law)
$legs = @(
    @('pool_dualrun', 'python', 'scripts\pool_dualrun_reconcile.py', 'run'),
    @('compute_audit', 'python', 'scripts\compute_audit.py'),
    @('watermark', 'python', 'scripts\py_watermark.py', 'probe'),
    @('update_daily', 'python', 'scripts\update_daily.py'),
    @('market_regime', 'python', 'scripts\market_regime.py'),
    @('strategy_scorecard', 'python', 'scripts\strategy_scorecard.py'),
    @('market_clock', 'python', 'scripts\market_clock_call.py', 'run'),
    @('update_lhb', 'python', 'scripts\update_lhb.py'),
    @('update_heat', 'python', 'scripts\update_heat.py'),
    @('update_futures', 'python', 'scripts\update_futures.py'),
    @('update_repo', 'python', 'scripts\update_repo.py'),
    @('update_options', 'python', 'scripts\update_options.py'),
    @('update_moneyflow', 'python', 'scripts\update_moneyflow.py'),
    @('update_sina_mf', 'python', 'scripts\update_sina_mf.py'),
    @('update_ths_panel', 'python', 'scripts\update_ths_panel.py'),
    @('ah_panel', 'python', 'scripts\ah_panel_puller.py'),
    @('update_fundamental', 'python', 'scripts\update_fundamental.py'),
    @('b_layer_filter', 'python', '-m', 'firm.risk.b_layer_filter'),
    @('aggressive_paper', 'python', 'scripts\aggressive_lab.py', 'paper'),
    @('alloc_paper', 'python', 'scripts\alloc_paper.py', 'run'),
    @('grid_paper', 'python', 'scripts\grid_paper.py', 'run'),
    @('system_v1_paper', 'python', 'scripts\system_v1_paper.py', 'run'),
    @('t35_export', 'python', 'scripts\t35_paper_export.py', 'run'),
    @('daily_scorecard', 'python', 'scripts\daily_scorecard.py'),
    @('daily_report', 'python', 'scripts\daily_report.py', 'run'),
    @('ceo_live_usage', 'python', 'scripts\ceo_live_usage.py'),
    @('build_status', 'python', '-m', 'monitor.build_status'),
    @('token_meter', 'python', 'scripts\token_meter.py'),
    @('attrition_guard', 'python', 'scripts\attrition_ledger_guard.py', 'scan')
)
$fail = @()
foreach ($leg in $legs) {
    $name = $leg[0]
    $args2 = $leg[1..($leg.Count-1)]
    Write-Host "LEG $name starting"
    & @args2 2>&1 | Out-Null
    $rc = $LASTEXITCODE
    Write-Host "LEG $name rc=$rc"
    if ($rc -ne 0) { $fail += "$name rc=$rc" }
}
Write-Host "S6_CHAIN_DONE fails=$($fail.Count)"
foreach ($f in $fail) { Write-Host "FAIL: $f" }
