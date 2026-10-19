# r1079 bm-a S6 maintenance chain (r1078 face clone verbatim, round label updated)
# U060 zero-window: invoke IN-PROCESS via `& _r1079bma_s6chain.ps1`
$log = 'results\_r1079bma_s6chain_rc.log'
"=== r1079 bm-a S6 chain $(Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz') ===" | Out-File $log -Encoding utf8
function Leg($name, $cmd) {
  & $cmd[0] $cmd[1..($cmd.Count - 1)] 2>$null | Out-Null
  $rc = $LASTEXITCODE
  if ($null -eq $rc) { $rc = 0 }
  "$name rc=$rc" | Out-File $log -Append -Encoding utf8
  Write-Host "$name rc=$rc"
  return $rc
}
$bad = 0
$bad += Leg 'dualrun_reconcile' @('python', 'scripts\pool_dualrun_reconcile.py', 'run')
$bad += Leg 'compute_audit' @('python', 'scripts\compute_audit.py')
$bad += Leg 'py_watermark' @('python', 'scripts\py_watermark.py', 'probe')
$bad += Leg 'update_daily' @('python', 'scripts\update_daily.py')
$bad += Leg 'market_regime' @('python', 'scripts\market_regime.py')
$bad += Leg 'strategy_scorecard' @('python', 'scripts\strategy_scorecard.py')
$bad += Leg 'market_clock_call' @('python', 'scripts\market_clock_call.py', 'run')
$bad += Leg 'update_lhb' @('python', 'scripts\update_lhb.py')
$bad += Leg 'update_zt_pool' @('python', 'scripts\update_zt_pool.py')
$bad += Leg 'update_heat' @('python', 'scripts\update_heat.py')
$bad += Leg 'update_futures' @('python', 'scripts\update_futures.py')
$bad += Leg 'update_repo' @('python', 'scripts\update_repo.py')
$bad += Leg 'update_options' @('python', 'scripts\update_options.py')
$bad += Leg 'update_moneyflow' @('python', 'scripts\update_moneyflow.py')
$bad += Leg 'update_sina_mf' @('python', 'scripts\update_sina_mf.py')
$bad += Leg 'update_astock_daily' @('python', 'scripts\update_astock_daily.py')
$bad += Leg 'update_etf_daily' @('python', 'scripts\update_etf_daily.py')
$bad += Leg 'regime_thermo_build' @('python', 'scripts\regime_thermo_build.py')
$bad += Leg 'regime_gate_dualarm' @('python', 'scripts\regime_gate_dualarm.py', 'run')
$bad += Leg 'rev_osc_signal_export' @('python', 'scripts\rev_osc_signal_export.py', 'run')
$bad += Leg 'update_minute_feed' @('python', 'scripts\update_minute_feed.py')
$bad += Leg 'update_ths_panel' @('python', 'scripts\update_ths_panel.py')
$bad += Leg 'ah_panel_puller' @('python', 'scripts\ah_panel_puller.py')
$bad += Leg 'update_fund_premium' @('python', 'scripts\update_fund_premium.py', 'snapshot')
$bad += Leg 'update_fundamental' @('python', 'scripts\update_fundamental.py')
$bad += Leg 'b_layer_filter' @('python', '-m', 'firm.risk.b_layer_filter')
$bad += Leg 'update_fund_statements' @('python', 'scripts\update_fund_statements.py')
$bad += Leg 't35_open_fill_verify' @('python', 'scripts\t35_open_fill_verify.py')
$bad += Leg 't24_prospect_paper' @('python', 'scripts\t24_prospect_paper.py', 'run')
$bad += Leg 't24_prospect_promotion' @('python', 'scripts\t24_prospect_promotion.py', 'run')
$bad += Leg 'aggressive_lab' @('python', 'scripts\aggressive_lab.py', 'paper')
$bad += Leg 'alloc_paper' @('python', 'scripts\alloc_paper.py', 'run')
$bad += Leg 'grid_paper' @('python', 'scripts\grid_paper.py', 'run')
$bad += Leg 'system_v1_paper' @('python', 'scripts\system_v1_paper.py', 'run')
$bad += Leg 't35_paper_export' @('python', 'scripts\t35_paper_export.py', 'run')
$bad += Leg 'daily_scorecard' @('python', 'scripts\daily_scorecard.py')
$bad += Leg 'daily_report' @('python', 'scripts\daily_report.py', 'run')
$bad += Leg 'ceo_live_usage' @('python', 'scripts\ceo_live_usage.py')
$bad += Leg 'build_status' @('python', '-m', 'monitor.build_status')
$bad += Leg 'token_meter' @('python', 'scripts\token_meter.py')
$bad += Leg 'attrition_guard_scan' @('python', 'scripts\attrition_ledger_guard.py', 'scan')
$bad += Leg 'automation_line_audit' @('python', 'scripts\automation_line_audit.py')
$bad += Leg 'a5_acceptance_pack' @('python', 'scripts\a5_acceptance_pack.py')
# live_paper anchor leg (new-bar gate; enforce guard)
$env:BIGMONEY_REGIME_GUARD = 'enforce'
python -m live.paper 2>$null | Out-Null
$rc = $LASTEXITCODE
"live_paper rc=$rc" | Out-File $log -Append -Encoding utf8
if ($rc -ne 0 -and $rc -ne 1) { $bad += 1 }
"=== chain done bad_rc=$bad (nonzero non-one legs) + live_paper appended $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Append -Encoding utf8
Write-Output "S6 chain complete, bad_rc=$bad (log: $log)"
