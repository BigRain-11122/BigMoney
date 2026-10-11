# r902 bm-c S6 maintenance chain batch (exit-code ledger)
# legs self-guard lane ownership (R31); no new bar tonight (cutoff 10-09, Monday pre-market) => mostly no-ops
# extends r899 chain: + daily_scorecard + build_status + queue_seed_gate scan (r892 38+3-leg precedent)
$legs = @(
    @("dualrun",      "python scripts\pool_dualrun_reconcile.py run"),
    @("compute_audit","python scripts\compute_audit.py"),
    @("py_watermark", "python scripts\py_watermark.py probe"),
    @("update_daily", "python scripts\update_daily.py"),
    @("market_regime","python scripts\market_regime.py"),
    @("scorecard",    "python scripts\strategy_scorecard.py"),
    @("mkt_clock",    "python scripts\market_clock_call.py run"),
    @("lhb",          "python scripts\update_lhb.py"),
    @("zt_pool",      "python scripts\update_zt_pool.py"),
    @("heat",         "python scripts\update_heat.py"),
    @("futures",      "python scripts\update_futures.py"),
    @("repo",         "python scripts\update_repo.py"),
    @("options",      "python scripts\update_options.py"),
    @("moneyflow",    "python scripts\update_moneyflow.py"),
    @("sina_mf",      "python scripts\update_sina_mf.py"),
    @("astock",       "python scripts\update_astock_daily.py"),
    @("etf_daily",    "python scripts\update_etf_daily.py"),
    @("thermo",       "python scripts\regime_thermo_build.py"),
    @("dualarm",      "python scripts\regime_gate_dualarm.py run"),
    @("rev_osc",      "python scripts\rev_osc_signal_export.py run"),
    @("minute_feed",  "python scripts\update_minute_feed.py"),
    @("ths_panel",    "python scripts\update_ths_panel.py"),
    @("ah_panel",     "python scripts\ah_panel_puller.py"),
    @("fund_prem",    "python scripts\update_fund_premium.py snapshot"),
    @("fundamental",  "python scripts\update_fundamental.py"),
    @("b_layer",      "python -m firm.risk.b_layer_filter"),
    @("fund_stmt",    "python scripts\update_fund_statements.py"),
    @("prospect_prom","python scripts\t24_prospect_promotion.py run"),
    @("aggr_paper",   "python scripts\aggressive_lab.py paper"),
    @("alloc_paper",  "python scripts\alloc_paper.py run"),
    @("grid_paper",   "python scripts\grid_paper.py run"),
    @("sysv1_paper",  "python scripts\system_v1_paper.py run"),
    @("t35_export",   "python scripts\t35_paper_export.py run"),
    @("daily_score",  "python scripts\daily_scorecard.py"),
    @("daily_rep",    "python scripts\daily_report.py run"),
    @("ceo_live",     "python scripts\ceo_live_usage.py"),
    @("build_status", "python -m monitor.build_status"),
    @("q_seed_gate",  "python scripts\queue_seed_gate.py scan"),
    @("token_meter",  "python scripts\token_meter.py")
)
$red = @()
foreach ($leg in $legs) {
    $name = $leg[0]; $cmd = $leg[1]
    Invoke-Expression $cmd *> $null
    $rc = $LASTEXITCODE
    Write-Output "$name rc=$rc"
    if ($rc -ne 0) { $red += "$name rc=$rc" }
}
Write-Output "=== RED LEGS: $($red.Count) ==="
if ($red) { $red }
