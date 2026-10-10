$ErrorActionPreference = 'Continue'
$log = 'results\_r839bmb_s6chain.log'
Remove-Item $log -ErrorAction SilentlyContinue
function Run-Leg($name, $argvList) {
  $outF = "$env:TEMP\s6_out.txt"
  $errF = "$env:TEMP\s6_err.txt"
  $p = Start-Process -FilePath 'python' -ArgumentList $argvList -NoNewWindow -Wait -PassThru -RedirectStandardOutput $outF -RedirectStandardError $errF
  $rc = $p.ExitCode
  $last = ''
  if (Test-Path $outF) { $last = (Get-Content $outF | Select-Object -Last 1) }
  $err = ''
  if (Test-Path $errF) { $err = (Get-Content $errF | Select-Object -Last 1) }
  Add-Content -Path $log -Value "$name rc=$rc last=$last err=$err"
}
Run-Leg 'd19probe' @('results\_r686bmb_d19_check.py')
Run-Leg 'dualrun' @('scripts\pool_dualrun_reconcile.py','run')
Run-Leg 'audit' @('scripts\compute_audit.py')
Run-Leg 'pywm' @('scripts\py_watermark.py','probe')
Run-Leg 'daily' @('scripts\update_daily.py')
Run-Leg 'regime' @('scripts\market_regime.py')
Run-Leg 'scorecard' @('scripts\strategy_scorecard.py')
Run-Leg 'clock' @('scripts\market_clock_call.py','run')
Run-Leg 'lhb' @('scripts\update_lhb.py')
Run-Leg 'ztpool' @('scripts\update_zt_pool.py')
Run-Leg 'heat' @('scripts\update_heat.py')
Run-Leg 'futures' @('scripts\update_futures.py')
Run-Leg 'repo' @('scripts\update_repo.py')
Run-Leg 'options' @('scripts\update_options.py')
Run-Leg 'moneyflow' @('scripts\update_moneyflow.py')
Run-Leg 'sinamf' @('scripts\update_sina_mf.py')
Run-Leg 'astock' @('scripts\update_astock_daily.py')
Run-Leg 'etf' @('scripts\update_etf_daily.py')
Run-Leg 'thermo' @('scripts\regime_thermo_build.py')
Run-Leg 'dualarm' @('scripts\regime_gate_dualarm.py','run')
Run-Leg 'revosc' @('scripts\rev_osc_signal_export.py','run')
Run-Leg 'minute' @('scripts\update_minute_feed.py')
Run-Leg 'ths' @('scripts\update_ths_panel.py')
Run-Leg 'ah' @('scripts\ah_panel_puller.py')
Run-Leg 'fundprem' @('scripts\update_fund_premium.py','snapshot')
Run-Leg 'fundamental' @('scripts\update_fundamental.py')
Run-Leg 'blayer' @('-m','firm.risk.b_layer_filter')
Run-Leg 'fundstmt' @('scripts\update_fund_statements.py')
Run-Leg 'aggr' @('scripts\aggressive_lab.py','paper')
Run-Leg 'alloc' @('scripts\alloc_paper.py','run')
Run-Leg 'grid' @('scripts\grid_paper.py','run')
Run-Leg 't24a' @('scripts\t24_prospect_paper.py','run')
Run-Leg 't24b' @('scripts\t24_prospect_promotion.py','run')
Run-Leg 'dailyrep' @('scripts\daily_report.py','run')
Run-Leg 'liveusage' @('scripts\ceo_live_usage.py')
Run-Leg 'token' @('scripts\token_meter.py')
Run-Leg 'attrition' @('scripts\attrition_ledger_guard.py','scan')
Get-Content $log
Write-Output '===D19PROBE==='
Get-Content 'results\_r686bmb_d19_check.json'
