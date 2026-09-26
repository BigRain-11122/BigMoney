# r289 bm-b S6 driver (ASCII-only per PS5.1 law). Legs in protocol order.
# Print one line per leg: name + rc; non-zero rc -> last 3 output lines.
$legs = @(
  @("01 compute_audit",      "python scripts\compute_audit.py"),
  @("02 py_watermark probe", "python scripts\py_watermark.py probe"),
  @("03 update_daily",       "python scripts\update_daily.py"),
  @("04 market_regime",      "python scripts\market_regime.py"),
  @("05 strategy_scorecard", "python scripts\strategy_scorecard.py"),
  @("06 market_clock_call",  "python scripts\market_clock_call.py run"),
  @("07 update_lhb",         "python scripts\update_lhb.py"),
  @("08 update_heat",        "python scripts\update_heat.py"),
  @("09 update_futures",     "python scripts\update_futures.py"),
  @("10 update_options",     "python scripts\update_options.py"),
  @("11 update_moneyflow",   "python scripts\update_moneyflow.py"),
  @("12 update_sina_mf",     "python scripts\update_sina_mf.py"),
  @("13 update_astock_daily","python scripts\update_astock_daily.py"),
  @("14 update_ths_panel",   "python scripts\update_ths_panel.py"),
  @("15 ah_panel_puller",   "python scripts\ah_panel_puller.py"),
  @("16 update_fund_premium","python scripts\update_fund_premium.py snapshot"),
  @("17 update_fundamental", "python scripts\update_fundamental.py"),
  @("18 b_layer_filter",    "python -m firm.risk.b_layer_filter"),
  @("19 daily_scorecard",   "python scripts\daily_scorecard.py"),
  @("20 daily_report",      "python scripts\daily_report.py run"),
  @("21 monitor build_status","python -m monitor.build_status"),
  @("22 token_meter",       "python scripts\token_meter.py")
)
foreach ($leg in $legs) {
  $name = $leg[0]; $cmd = $leg[1]
  $out = cmd /c "$cmd 2>&1"
  $rc = $LASTEXITCODE
  $tail3 = ($out | Select-Object -Last 3) -join " | "
  Write-Output ("LEG $name rc=$rc")
  if ($rc -ne 0) { Write-Output ("  TAIL: " + $tail3) }
}
Write-Output "S6_DRIVER_DONE"
