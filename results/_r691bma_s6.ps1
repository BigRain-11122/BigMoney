# r691 bm-a S6 chain driver (golden-week expected no-op family)
$log = "results\_r691bma_s6_log.txt"
Remove-Item $log -ErrorAction SilentlyContinue
$cmds = @(
    @("dualrun",      "python scripts\pool_dualrun_reconcile.py run"),
    @("audit",        "python scripts\compute_audit.py"),
    @("watermark",    "python scripts\py_watermark.py probe"),
    @("daily",        "python scripts\update_daily.py"),
    @("regime",       "python scripts\market_regime.py"),
    @("scorecard",    "python scripts\strategy_scorecard.py"),
    @("clock",        "python scripts\market_clock_call.py run"),
    @("lhb",          "python scripts\update_lhb.py"),
    @("heat",         "python scripts\update_heat.py"),
    @("futures",      "python scripts\update_futures.py"),
    @("repo",         "python scripts\update_repo.py"),
    @("options",      "python scripts\update_options.py"),
    @("moneyflow",    "python scripts\update_moneyflow.py"),
    @("sina_mf",      "python scripts\update_sina_mf.py"),
    @("astock",       "python scripts\update_astock_daily.py"),
    @("etf_daily",    "python scripts\update_etf_daily.py"),
    @("rev_osc",      "python scripts\rev_osc_signal_export.py run"),
    @("minute_feed",  "python scripts\update_minute_feed.py"),
    @("ths_panel",    "python scripts\update_ths_panel.py"),
    @("ah_panel",     "python scripts\ah_panel_puller.py"),
    @("fund_premium", "python scripts\update_fund_premium.py snapshot"),
    @("fundamental",  "python scripts\update_fundamental.py"),
    @("b_layer",      "python -m firm.risk.b_layer_filter"),
    @("fund_stmts",   "python scripts\update_fund_statements.py"),
    @("t24_promo",    "python scripts\t24_prospect_promotion.py run"),
    @("aggr_paper",   "python scripts\aggressive_lab.py paper"),
    @("alloc_paper",  "python scripts\alloc_paper.py run"),
    @("grid_paper",   "python scripts\grid_paper.py run"),
    @("sysv1_paper",  "python scripts\system_v1_paper.py run"),
    @("t35_export",   "python scripts\t35_paper_export.py run"),
    @("daily_score",  "python scripts\daily_scorecard.py"),
    @("daily_report", "python scripts\daily_report.py run"),
    @("ceo_live",     "python scripts\ceo_live_usage.py"),
    @("build_status", "python -m monitor.build_status"),
    @("token_meter",  "python scripts\token_meter.py"),
    @("attr_guard",   "python scripts\attrition_ledger_guard.py scan")
)
foreach ($c in $cmds) {
    $t0 = Get-Date -Format "HH:mm:ss"
    Add-Content $log "=== LEG $($c[0]) start $t0"
    Invoke-Expression $c[1] >> $log 2>&1
    Add-Content $log "=== LEG $($c[0]) rc=$LASTEXITCODE"
}
Add-Content $log "=== S6 chain end"
Write-Host "DONE legs=$($cmds.Count)"
