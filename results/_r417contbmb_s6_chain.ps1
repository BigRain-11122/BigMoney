$ErrorActionPreference = "Continue"
$log = "results\_r417contbmb_s6_log.txt"
$legs = @(
  @("dualrun", "python scripts\pool_dualrun_reconcile.py run"),
  @("comp_audit", "python scripts\compute_audit.py"),
  @("py_wm", "python scripts\py_watermark.py probe"),
  @("update_daily", "python scripts\update_daily.py"),
  @("regime", "python scripts\market_regime.py"),
  @("scorecard", "python scripts\strategy_scorecard.py"),
  @("clock", "python scripts\market_clock_call.py run"),
  @("lhb", "python scripts\update_lhb.py"),
  @("heat", "python scripts\update_heat.py"),
  @("futures", "python scripts\update_futures.py"),
  @("repo", "python scripts\update_repo.py"),
  @("options", "python scripts\update_options.py"),
  @("moneyflow", "python scripts\update_moneyflow.py"),
  @("sina_mf", "python scripts\update_sina_mf.py"),
  @("astock", "python scripts\update_astock_daily.py"),
  @("etf_daily", "python scripts\update_etf_daily.py"),
  @("rev_osc", "python scripts\rev_osc_signal_export.py run"),
  @("minute_feed", "python scripts\update_minute_feed.py"),
  @("ths", "python scripts\update_ths_panel.py"),
  @("ah_panel", "python scripts\ah_panel_puller.py"),
  @("fund_prem", "python scripts\update_fund_premium.py snapshot"),
  @("fundamental", "python scripts\update_fundamental.py"),
  @("b_layer", "python -m firm.risk.b_layer_filter"),
  @("live_paper", "python -m live.paper"),
  @("t35v", "python scripts\t35_open_fill_verify.py"),
  @("t24a", "python scripts\t24_prospect_paper.py run"),
  @("t24b", "python scripts\t24_prospect_promotion.py run"),
  @("aggr", "python scripts\aggressive_lab.py paper"),
  @("alloc", "python scripts\alloc_paper.py run"),
  @("grid", "python scripts\grid_paper.py run"),
  @("sysv1", "python scripts\system_v1_paper.py run"),
  @("t35e", "python scripts\t35_paper_export.py run"),
  @("daily_score", "python scripts\daily_scorecard.py"),
  @("daily_report", "python scripts\daily_report.py run"),
  @("ceo_live", "python scripts\ceo_live_usage.py"),
  @("build_status", "python -m monitor.build_status"),
  @("token", "python scripts\token_meter.py")
)
foreach ($leg in $legs) {
  $name = $leg[0]; $cmd = $leg[1]
  $out = Invoke-Expression $cmd 2>&1 | Out-String
  $rc = $LASTEXITCODE
  $tail = ($out -split "`n" | Select-Object -Last 2) -join " | "
  Add-Content $log "[$name] rc=$rc :: $tail"
}
Add-Content $log "=== S6 chain done $(Get-Date -Format 'HH:mm:ss') ==="
