# r945 bm-b S6 batch driver -- runs each leg, prints name + rc + 1 tail line (ASCII-safe summary)
$ErrorActionPreference = "Continue"
$legs = @(
    @("market_regime", "python", @("scripts\market_regime.py")),
    @("strategy_scorecard", "python", @("scripts\strategy_scorecard.py")),
    @("market_clock_call", "python", @("scripts\market_clock_call.py", "run")),
    @("update_lhb", "python", @("scripts\update_lhb.py")),
    @("update_zt_pool", "python", @("scripts\update_zt_pool.py")),
    @("update_heat", "python", @("scripts\update_heat.py")),
    @("update_futures", "python", @("scripts\update_futures.py")),
    @("update_repo", "python", @("scripts\update_repo.py")),
    @("update_options", "python", @("scripts\update_options.py")),
    @("update_moneyflow", "python", @("scripts\update_moneyflow.py")),
    @("update_sina_mf", "python", @("scripts\update_sina_mf.py")),
    @("update_ths_panel", "python", @("scripts\update_ths_panel.py")),
    @("ah_panel_puller", "python", @("scripts\ah_panel_puller.py")),
    @("update_fund_premium", "python", @("scripts\update_fund_premium.py", "snapshot")),
    @("update_fundamental", "python", @("scripts\update_fundamental.py")),
    @("b_layer_filter", "python", @("-m", "firm.risk.b_layer_filter")),
    @("update_fund_statements", "python", @("scripts\update_fund_statements.py")),
    @("update_astock_daily", "python", @("scripts\update_astock_daily.py")),
    @("update_etf_daily", "python", @("scripts\update_etf_daily.py")),
    @("regime_thermo_build", "python", @("scripts\regime_thermo_build.py")),
    @("regime_gate_dualarm", "python", @("scripts\regime_gate_dualarm.py", "run")),
    @("rev_osc_signal_export", "python", @("scripts\rev_osc_signal_export.py", "run")),
    @("update_minute_feed", "python", @("scripts\update_minute_feed.py")),
    @("aggressive_lab", "python", @("scripts\aggressive_lab.py", "paper")),
    @("alloc_paper", "python", @("scripts\alloc_paper.py", "run")),
    @("grid_paper", "python", @("scripts\grid_paper.py", "run")),
    @("system_v1_paper", "python", @("scripts\system_v1_paper.py", "run")),
    @("t35_paper_export", "python", @("scripts\t35_paper_export.py", "run")),
    @("daily_scorecard", "python", @("scripts\daily_scorecard.py")),
    @("daily_report", "python", @("scripts\daily_report.py", "run")),
    @("ceo_live_usage", "python", @("scripts\ceo_live_usage.py")),
    @("build_status", "python", @("-m", "monitor.build_status")),
    @("token_meter", "python", @("scripts\token_meter.py")),
    @("py_watermark_probe", "python", @("scripts\py_watermark.py", "probe"))
)
foreach ($leg in $legs) {
    $name = $leg[0]
    $out = & $leg[1] $leg[2] 2>&1
    $rc = $LASTEXITCODE
    $tail = ""
    if ($out) { $last = @($out)[-1]; if ($last -ne $null) { $tail = ($last.ToString() -replace "\s+", " "); if ($tail.Length -gt 110) { $tail = $tail.Substring(0, 110) } } }
    Write-Output ("LEG {0} rc={1} :: {2}" -f $name, $rc, $tail)
}
