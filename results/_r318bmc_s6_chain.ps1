# r318 bm-c S6 chain (holiday round: no new bar -> live.paper/t35_open_fill_verify/t24_prospect_paper
# correctly skipped per prompt gate; paper legs self-no-op per own gates) + overdue Oct monthly legs
# + dualrun flip-gate status + pool truth probe. All hidden-window per CEO silence law.
$ErrorActionPreference = 'Continue'
$repo = 'K:\Fluxgroup\FluxGroup\quant\bigmoney'
function Run-Hidden([string]$exe, [string]$argline, [string]$cwd) {
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $exe; $psi.Arguments = $argline
  if ($cwd) { $psi.WorkingDirectory = $cwd }
  $psi.UseShellExecute = $false; $psi.CreateNoWindow = $true
  $psi.RedirectStandardOutput = $true; $psi.RedirectStandardError = $true
  $p = [System.Diagnostics.Process]::Start($psi)
  $oT = $p.StandardOutput.ReadToEndAsync(); $e = $p.StandardError.ReadToEnd()
  $o = $oT.Result; $p.WaitForExit()
  return @{ out = $o; err = $e; rc = $p.ExitCode }
}
function Leg([string]$name, [string]$argline) {
  $r = Run-Hidden 'python' $argline $repo
  $ol = @($r.out -split "`n") | Where-Object { $_.Trim() -ne '' } | Select-Object -Last 2
  $tail = ($ol -join ' | ')
  if ($tail.Length -gt 260) { $tail = $tail.Substring(0, 260) }
  Write-Host ('LEG ' + $name + ' rc=' + $r.rc + ' :: ' + $tail)
  return $r.rc
}
Write-Output ('NOW: ' + (Get-Date -Format 'HH:mm:ss'))
Write-Output '=== S6 core (order per prompt; dualrun MUST precede compute_audit) ==='
[void](Leg 'dualrun_reconcile'      'scripts\pool_dualrun_reconcile.py run')
[void](Leg 'compute_audit'          'scripts\compute_audit.py')
[void](Leg 'py_watermark_probe'    'scripts\py_watermark.py probe')
[void](Leg 'update_daily'           'scripts\update_daily.py')
[void](Leg 'market_regime'          'scripts\market_regime.py')
[void](Leg 'strategy_scorecard'    'scripts\strategy_scorecard.py')
[void](Leg 'market_clock_call'     'scripts\market_clock_call.py run')
[void](Leg 'update_lhb'             'scripts\update_lhb.py')
[void](Leg 'update_heat'            'scripts\update_heat.py')
[void](Leg 'update_futures'         'scripts\update_futures.py')
[void](Leg 'update_repo'            'scripts\update_repo.py')
[void](Leg 'update_options'         'scripts\update_options.py')
[void](Leg 'update_moneyflow'       'scripts\update_moneyflow.py')
[void](Leg 'update_sina_mf'         'scripts\update_sina_mf.py')
[void](Leg 'update_astock_daily'    'scripts\update_astock_daily.py')
[void](Leg 'update_etf_daily'       'scripts\update_etf_daily.py')
[void](Leg 'rev_osc_signal_export' 'scripts\rev_osc_signal_export.py run')
[void](Leg 'update_minute_feed'    'scripts\update_minute_feed.py')
[void](Leg 'update_ths_panel'       'scripts\update_ths_panel.py')
[void](Leg 'ah_panel_puller'        'scripts\ah_panel_puller.py')
[void](Leg 'update_fund_premium'   'scripts\update_fund_premium.py snapshot')
[void](Leg 'update_fundamental'    'scripts\update_fundamental.py')
[void](Leg 'b_layer_filter'         '-m firm.risk.b_layer_filter')
[void](Leg 't24_prospect_promotion' 'scripts\t24_prospect_promotion.py run')
[void](Leg 'aggressive_lab_paper'  'scripts\aggressive_lab.py paper')
[void](Leg 'alloc_paper'            'scripts\alloc_paper.py run')
[void](Leg 'grid_paper'             'scripts\grid_paper.py run')
[void](Leg 'system_v1_paper'        'scripts\system_v1_paper.py run')
[void](Leg 't35_paper_export'      'scripts\t35_paper_export.py run')
[void](Leg 'daily_scorecard'        'scripts\daily_scorecard.py')
[void](Leg 'daily_report'           'scripts\daily_report.py run')
[void](Leg 'ceo_live_usage'         'scripts\ceo_live_usage.py')
[void](Leg 'build_status'           '-m monitor.build_status')
[void](Leg 'token_meter'            'scripts\token_meter.py')
Write-Output '=== S7 guards ==='
[void](Leg 'attrition_guard_scan'   'scripts\attrition_ledger_guard.py scan')
Write-Output '=== MONTHLY legs (Oct overdue: BRIEF-202610 + SELF-REVIEW-202610 missing) ==='
[void](Leg 'science_audit'          'scripts\science_audit.py run')
[void](Leg 'monthly_briefing'      'scripts\monthly_briefing.py run')
[void](Leg 'self_review'           'scripts\self_review.py run')
Write-Output '=== dualrun flip gate (read-only status) ==='
[void](Leg 'dualrun_status'        'scripts\pool_dualrun_reconcile.py status')
Write-Output '=== pool truth probe (r513 stale-view law: origin-side read) ==='
[void](Leg 'pool_truth_probe'      'results\_r318bmc_pool_truth.py')
Write-Output ('NOW: ' + (Get-Date -Format 'HH:mm:ss'))
Write-Output '=== chain done ==='
