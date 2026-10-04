$ErrorActionPreference = "Continue"
$legs = @(
    @("dualrun",            "python scripts\pool_dualrun_reconcile.py run"),
    @("compute_audit",      "python scripts\compute_audit.py"),
    @("py_watermark",       "python scripts\py_watermark.py probe"),
    @("update_daily",       "python scripts\update_daily.py"),
    @("market_regime",      "python scripts\market_regime.py"),
    @("scorecard",          "python scripts\strategy_scorecard.py"),
    @("market_clock",       "python scripts\market_clock_call.py run"),
    @("update_lhb",         "python scripts\update_lhb.py"),
    @("update_heat",        "python scripts\update_heat.py"),
    @("update_futures",     "python scripts\update_futures.py"),
    @("update_repo",        "python scripts\update_repo.py"),
    @("update_options",     "python scripts\update_options.py"),
    @("update_moneyflow",    "python scripts\update_moneyflow.py"),
    @("update_sina_mf",     "python scripts\update_sina_mf.py"),
    @("astock_daily",       "python scripts\update_astock_daily.py"),
    @("etf_daily",          "python scripts\update_etf_daily.py"),
    @("rev_osc_export",     "python scripts\rev_osc_signal_export.py run"),
    @("minute_feed",        "python scripts\update_minute_feed.py"),
    @("ths_panel",          "python scripts\update_ths_panel.py"),
    @("ah_panel",           "python scripts\ah_panel_puller.py"),
    @("fund_premium",       "python scripts\update_fund_premium.py snapshot"),
    @("fundamental",        "python scripts\update_fundamental.py"),
    @("b_layer_filter",     "python -m firm.risk.b_layer_filter"),
    @("fund_statements",    "python scripts\update_fund_statements.py"),
    @("aggr_paper",         "python scripts\aggressive_lab.py paper"),
    @("alloc_paper",        "python scripts\alloc_paper.py run"),
    @("grid_paper",         "python scripts\grid_paper.py run"),
    @("system_v1_paper",    "python scripts\system_v1_paper.py run"),
    @("t35_paper_export",   "python scripts\t35_paper_export.py run"),
    @("daily_scorecard",    "python scripts\daily_scorecard.py"),
    @("daily_report",       "python scripts\daily_report.py run"),
    @("ceo_live_usage",     "python scripts\ceo_live_usage.py"),
    @("build_status",       "python -m monitor.build_status"),
    @("token_meter",        "python scripts\token_meter.py")
)
$fail = 0
foreach ($leg in $legs) {
    $name = $leg[0]
    $out = Invoke-Expression $leg[1] 2>&1 | Out-String
    $rc = $LASTEXITCODE
    $tail = ($out.TrimEnd() -split "`r?`n" | Select-Object -Last 1)
    if ($tail -eq $null) { $tail = "(no output)" }
    if ($tail.Length -gt 160) { $tail = $tail.Substring(0, 160) }
    Write-Output ("{0} rc={1} :: {2}" -f $name, $rc, $tail)
    if ($rc -ne 0) { $fail = $fail + 1 }
}
Write-Output ("S6_CHAIN_SUMMARY fail_legs={0}" -f $fail)
