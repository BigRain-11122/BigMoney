$ErrorActionPreference = "Continue"
$log = "results\_s6_r885_run.log"
$cmds = @(
  @("pool_dualrun", @("scripts\pool_dualrun_reconcile.py", "run")),
  @("compute_audit", @("scripts\compute_audit.py")),
  @("py_watermark", @("scripts\py_watermark.py", "probe")),
  @("update_daily", @("scripts\update_daily.py")),
  @("market_regime", @("scripts\market_regime.py")),
  @("scorecard", @("scripts\strategy_scorecard.py")),
  @("market_clock", @("scripts\market_clock_call.py", "run")),
  @("update_lhb", @("scripts\update_lhb.py")),
  @("zt_pool", @("scripts\update_zt_pool.py")),
  @("update_heat", @("scripts\update_heat.py")),
  @("update_futures", @("scripts\update_futures.py")),
  @("update_repo", @("scripts\update_repo.py")),
  @("update_options", @("scripts\update_options.py")),
  @("moneyflow", @("scripts\update_moneyflow.py")),
  @("sina_mf", @("scripts\update_sina_mf.py")),
  @("astock_daily", @("scripts\update_astock_daily.py")),
  @("etf_daily", @("scripts\update_etf_daily.py")),
  @("thermo_build", @("scripts\regime_thermo_build.py")),
  @("gate_dualarm", @("scripts\regime_gate_dualarm.py", "run")),
  @("rev_osc", @("scripts\rev_osc_signal_export.py", "run")),
  @("minute_feed", @("scripts\update_minute_feed.py")),
  @("ths_panel", @("scripts\update_ths_panel.py")),
  @("ah_panel", @("scripts\ah_panel_puller.py")),
  @("fund_premium", @("scripts\update_fund_premium.py", "snapshot")),
  @("update_fundamental", @("scripts\update_fundamental.py")),
  @("b_layer", @("-m", "firm.risk.b_layer_filter")),
  @("fund_statements", @("scripts\update_fund_statements.py")),
  @("aggr_paper", @("scripts\aggressive_lab.py", "paper")),
  @("alloc_paper", @("scripts\alloc_paper.py", "run")),
  @("grid_paper", @("scripts\grid_paper.py", "run")),
  @("system_v1_paper", @("scripts\system_v1_paper.py", "run")),
  @("t35_export", @("scripts\t35_paper_export.py", "run")),
  @("daily_scorecard", @("scripts\daily_scorecard.py")),
  @("daily_report", @("scripts\daily_report.py", "run")),
  @("ceo_live_usage", @("scripts\ceo_live_usage.py")),
  @("build_status", @("-m", "monitor.build_status")),
  @("token_meter", @("scripts\token_meter.py"))
)
$rc_list = @()
foreach ($c in $cmds) {
  $name = $c[0]
  $cargs = $c[1]
  $out = & python @cargs 2>&1
  $rc = $LASTEXITCODE
  $rc_list += "$name=$rc"
  $tail = ($out | Select-Object -Last 3) -join " | "
  Add-Content $log "=== $name rc=$rc :: $tail"
}
$rc_list -join " "
Write-Output "LOG=$log"
