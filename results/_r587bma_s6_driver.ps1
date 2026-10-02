$legs = @(
  @("dualrun", "python", @("scripts\pool_dualrun_reconcile.py", "run")),
  @("audit", "python", @("scripts\compute_audit.py")),
  @("wm", "python", @("scripts\py_watermark.py", "probe")),
  @("daily", "python", @("scripts\update_daily.py")),
  @("regime", "python", @("scripts\market_regime.py")),
  @("scorecard", "python", @("scripts\strategy_scorecard.py")),
  @("clock", "python", @("scripts\market_clock_call.py", "run")),
  @("lhb", "python", @("scripts\update_lhb.py")),
  @("heat", "python", @("scripts\update_heat.py")),
  @("futures", "python", @("scripts\update_futures.py")),
  @("repo", "python", @("scripts\update_repo.py")),
  @("options", "python", @("scripts\update_options.py")),
  @("moneyflow", "python", @("scripts\update_moneyflow.py")),
  @("sinamf", "python", @("scripts\update_sina_mf.py")),
  @("astock", "python", @("scripts\update_astock_daily.py")),
  @("etf", "python", @("scripts\update_etf_daily.py")),
  @("revosc", "python", @("scripts\rev_osc_signal_export.py", "run")),
  @("minutefeed", "python", @("scripts\update_minute_feed.py")),
  @("ths", "python", @("scripts\update_ths_panel.py")),
  @("ahpanel", "python", @("scripts\ah_panel_puller.py")),
  @("fundprem", "python", @("scripts\update_fund_premium.py", "snapshot")),
  @("fundamental", "python", @("scripts\update_fundamental.py")),
  @("blayer", "python", @("-m", "firm.risk.b_layer_filter")),
  @("t35fill", "python", @("scripts\t35_open_fill_verify.py")),
  @("t24paper", "python", @("scripts\t24_prospect_paper.py", "run")),
  @("t24prom", "python", @("scripts\t24_prospect_promotion.py", "run")),
  @("aggr", "python", @("scripts\aggressive_lab.py", "paper")),
  @("alloc", "python", @("scripts\alloc_paper.py", "run")),
  @("grid", "python", @("scripts\grid_paper.py", "run")),
  @("sysv1", "python", @("scripts\system_v1_paper.py", "run")),
  @("export", "python", @("scripts\t35_paper_export.py", "run")),
  @("dscore", "python", @("scripts\daily_scorecard.py")),
  @("dreport", "python", @("scripts\daily_report.py", "run")),
  @("liveusage", "python", @("scripts\ceo_live_usage.py")),
  @("build", "python", @("-m", "monitor.build_status")),
  @("token", "python", @("scripts\token_meter.py"))
)
$bad = @()
foreach ($leg in $legs) {
  $name = $leg[0]; $exe = $leg[1]; $args = $leg[2]
  $out = & $exe @args 2>&1
  $rc = $LASTEXITCODE
  $tail = ($out | Select-Object -Last 1)
  Write-Host ("LEG {0} rc={1} :: {2}" -f $name, $rc, "$tail")
  if ($rc -ne 0) { $bad += ("{0} rc={1}" -f $name, $rc) }
}
Write-Host ("BATCH DONE bad={0}" -f ($bad -join "; "))
