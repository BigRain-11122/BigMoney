# r335 bm-b S6 maintenance chain (Sunday evening: no-new-bar family; lane guards per R31)
$ErrorActionPreference = 'Continue'
$log = 'results\_r335bmb_s6.log'
"=== r335 bm-b S6 chain start $(Get-Date -Format s) ===" | Out-File $log -Encoding utf8
$legs = @(
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
  @('scripts\rev_osc_signal_export.py','run'),
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
  @('scripts\daily_scorecard.py'),
  @('scripts\daily_report.py','run'),
  @('-m','monitor.build_status'),
  @('scripts\token_meter.py')
)
$fails = 0
foreach ($leg in $legs) {
  $name = $leg -join ' '
  & python @leg 1>> $log 2>&1
  $rc = $LASTEXITCODE
  Write-Output ("LEG [{0}] rc={1}" -f $name, $rc)
  "LEG [$name] rc=$rc" | Out-File $log -Append -Encoding utf8
  if ($rc -ne 0) { $fails++ }
}
Write-Output ("S6-CHAIN-DONE legs={0} nonzero={1} (log={2})" -f $legs.Count, $fails, $log)
