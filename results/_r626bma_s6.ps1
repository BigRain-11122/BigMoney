$ErrorActionPreference = "Continue"
$log = "results\_r626bma_s6.log"
"=== S6 chain r626 bm-a start $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File $log -Encoding utf8
$legs = @(
  @("dualrun", "python scripts\pool_dualrun_reconcile.py run"),
  @("audit", "python scripts\compute_audit.py"),
  @("wm-probe", "python scripts\py_watermark.py probe"),
  @("daily", "python scripts\update_daily.py"),
  @("regime", "python scripts\market_regime.py"),
  @("scorecard", "python scripts\strategy_scorecard.py"),
  @("clockcall", "python scripts\market_clock_call.py run"),
  @("lhb", "python scripts\update_lhb.py"),
  @("heat", "python scripts\update_heat.py"),
  @("futures", "python scripts\update_futures.py"),
  @("repo", "python scripts\update_repo.py"),
  @("options", "python scripts\update_options.py"),
  @("moneyflow", "python scripts\update_moneyflow.py"),
  @("sinamf", "python scripts\update_sina_mf.py"),
  @("astock", "python scripts\update_astock_daily.py"),
  @("etfdaily", "python scripts\update_etf_daily.py"),
  @("revosc", "python scripts\rev_osc_signal_export.py run"),
  @("minutefeed", "python scripts\update_minute_feed.py"),
  @("thspanel", "python scripts\update_ths_panel.py"),
  @("ahpanel", "python scripts\ah_panel_puller.py"),
  @("fundprem", "python scripts\update_fund_premium.py snapshot"),
  @("fundamental", "python scripts\update_fundamental.py"),
  @("blayer", "python -m firm.risk.b_layer_filter"),
  @("paperexport", "python scripts\t35_paper_export.py run"),
  @("dscore", "python scripts\daily_scorecard.py"),
  @("dreport", "python scripts\daily_report.py run"),
  @("liveusage", "python scripts\ceo_live_usage.py"),
  @("buildstatus", "python -m monitor.build_status"),
  @("token", "python scripts\token_meter.py")
)
$fails = 0
foreach ($leg in $legs) {
  $name = $leg[0]; $cmd = $leg[1]
  $t0 = Get-Date
  Invoke-Expression $cmd 2>&1 | Out-File $log -Append -Encoding utf8
  $rc = $LASTEXITCODE
  $el = [int]((Get-Date) - $t0).TotalSeconds
  $line = "LEG|$name|rc=$rc|${el}s"
  $line | Out-File $log -Append -Encoding utf8
  Write-Output $line
  if ($rc -ne 0) { $fails++ }
}
"=== chain done fails=$fails $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Append -Encoding utf8
Write-Output "FAILS=$fails"
