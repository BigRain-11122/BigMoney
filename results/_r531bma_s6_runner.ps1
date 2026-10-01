# r531 bm-a S6 maintenance chain runner (per-leg rc capture, r318 Write-Host law)
$ErrorActionPreference = "Continue"
Set-Location "C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
$legs = @(
  @("dualrun",    @("python", "scripts\pool_dualrun_reconcile.py", "run")),
  @("compute_audit", @("python", "scripts\compute_audit.py")),
  @("py_watermark", @("python", "scripts\py_watermark.py", "probe")),
  @("update_daily", @("python", "scripts\update_daily.py")),
  @("market_regime", @("python", "scripts\market_regime.py")),
  @("scorecard",   @("python", "scripts\strategy_scorecard.py")),
  @("market_clock", @("python", "scripts\market_clock_call.py", "run")),
  @("update_lhb",  @("python", "scripts\update_lhb.py")),
  @("update_heat", @("python", "scripts\update_heat.py")),
  @("update_futures", @("python", "scripts\update_futures.py")),
  @("update_repo", @("python", "scripts\update_repo.py")),
  @("update_options", @("python", "scripts\update_options.py")),
  @("update_moneyflow", @("python", "scripts\update_moneyflow.py")),
  @("update_sina_mf", @("python", "scripts\update_sina_mf.py")),
  @("update_astock", @("python", "scripts\update_astock_daily.py")),
  @("update_etf_daily", @("python", "scripts\update_etf_daily.py")),
  @("rev_osc_export", @("python", "scripts\rev_osc_signal_export.py", "run")),
  @("minute_feed", @("python", "scripts\update_minute_feed.py")),
  @("ths_panel",  @("python", "scripts\update_ths_panel.py")),
  @("ah_panel",   @("python", "scripts\ah_panel_puller.py")),
  @("fund_premium", @("python", "scripts\update_fund_premium.py", "snapshot")),
  @("fundamental", @("python", "scripts\update_fundamental.py")),
  @("b_layer",    @("python", "-m", "firm.risk.b_layer_filter")),
  @("t35_fill_verify", @("python", "scripts\t35_open_fill_verify.py")),
  @("prospect_paper", @("python", "scripts\t24_prospect_paper.py", "run")),
  @("prospect_promo", @("python", "scripts\t24_prospect_promotion.py", "run")),
  @("aggressive_paper", @("python", "scripts\aggressive_lab.py", "paper")),
  @("alloc_paper", @("python", "scripts\alloc_paper.py", "run")),
  @("grid_paper",  @("python", "scripts\grid_paper.py", "run")),
  @("system_v1_paper", @("python", "scripts\system_v1_paper.py", "run")),
  @("t35_export",  @("python", "scripts\t35_paper_export.py", "run")),
  @("daily_scorecard", @("python", "scripts\daily_scorecard.py")),
  @("daily_report", @("python", "scripts\daily_report.py", "run")),
  @("ceo_live",    @("python", "scripts\ceo_live_usage.py")),
  @("build_status", @("python", "-m", "monitor.build_status")),
  @("token_meter", @("python", "scripts\token_meter.py"))
)
$fails = 0
foreach ($leg in $legs) {
  $name = $leg[0]
  $argv = $leg[1]
  $out = & $argv[0] $argv[1..($argv.Count-1)] 2>&1 | Out-String
  $rc = $LASTEXITCODE
  $tail = ($out.Trim() -split "`n" | Select-Object -Last 1)
  if ($tail -and $tail.Length -gt 110) { $tail = $tail.Substring(0,110) }
  Write-Host ("LEG {0,-18} rc={1}  {2}" -f $name, $rc, $tail)
  if ($rc -ne 0) { $fails++ }
}
Write-Host ("S6 CHAIN DONE fails={0}/{1}" -f $fails, $legs.Count)
