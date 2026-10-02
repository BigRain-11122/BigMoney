# r578 bm-b S6 maintenance chain (holiday window; most steps expected no-op).
# Detached runner: plain output (NOT Write-Host) so -RedirectStandardOutput captures it.
# python -u: unbuffered under redirection (r324 block-buffer假死 law).
$steps = @(
  @('scripts\pool_dualrun_reconcile.py','run'),
  @('scripts\compute_audit.py'),
  @('scripts\py_watermark.py','probe'),
  @('scripts\update_daily.py'),
  @('scripts\market_regime.py'),
  @('scripts\strategy_scorecard.py'),
  @('scripts\market_clock_call.py','run'),
  @('scripts\update_lhb.py'),
  @('scripts\update_heat.py'),
  @('scripts\update_futures.py'),
  @('scripts\update_repo.py'),
  @('scripts\update_options.py'),
  @('scripts\update_moneyflow.py'),
  @('scripts\update_sina_mf.py'),
  @('scripts\update_astock_daily.py'),
  @('scripts\update_etf_daily.py'),
  @('scripts\rev_osc_signal_export.py','run'),
  @('scripts\update_minute_feed.py'),
  @('scripts\update_ths_panel.py'),
  @('scripts\ah_panel_puller.py'),
  @('scripts\update_fund_premium.py','snapshot'),
  @('scripts\update_fundamental.py'),
  @('-m','firm.risk.b_layer_filter'),
  @('scripts\aggressive_lab.py','paper'),
  @('scripts\alloc_paper.py','run'),
  @('scripts\grid_paper.py','run'),
  @('scripts\system_v1_paper.py','run'),
  @('scripts\t35_paper_export.py','run'),
  @('scripts\daily_report.py','run'),
  @('scripts\ceo_live_usage.py'),
  @('scripts\token_meter.py'),
  @('scripts\attrition_ledger_guard.py','scan')
)
foreach ($s in $steps) {
  "=== STEP $($s -join ' ') ==="
  & python -u @s
  "rc=$LASTEXITCODE"
}
"=== S6 CHAIN DONE ==="
