# r314 bm-c S6 chain RERUN with visible per-leg output (idempotent legs)
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
  if ($tail.Length -gt 280) { $tail = $tail.Substring(0, 280) }
  [Console]::WriteLine('LEG ' + $name + ' rc=' + $r.rc + ' :: ' + $tail)
  if ($r.err -and $r.err.Trim() -ne '') {
    $el = @($r.err -split "`n") | Where-Object { $_.Trim() -ne '' } | Select-Object -Last 2
    $et = ($el -join ' | ')
    if ($et.Length -gt 280) { $et = $et.Substring(0, 280) }
    [Console]::WriteLine('   ERR: ' + $et)
  }
}
[Console]::WriteLine('NOW: ' + (Get-Date -Format 'HH:mm:ss'))
Leg 'dualrun_reconcile'      'scripts\pool_dualrun_reconcile.py run'
Leg 'compute_audit'          'scripts\compute_audit.py'
Leg 'py_watermark_probe'     'scripts\py_watermark.py probe'
Leg 'update_daily'           'scripts\update_daily.py'
Leg 'market_regime'          'scripts\market_regime.py'
Leg 'strategy_scorecard'     'scripts\strategy_scorecard.py'
Leg 'market_clock_call'      'scripts\market_clock_call.py run'
Leg 'update_lhb'             'scripts\update_lhb.py'
Leg 'update_heat'            'scripts\update_heat.py'
Leg 'update_futures'         'scripts\update_futures.py'
Leg 'update_repo'            'scripts\update_repo.py'
Leg 'update_options'         'scripts\update_options.py'
Leg 'update_moneyflow'       'scripts\update_moneyflow.py'
Leg 'update_sina_mf'         'scripts\update_sina_mf.py'
Leg 'update_astock_daily'    'scripts\update_astock_daily.py'
Leg 'update_etf_daily'       'scripts\update_etf_daily.py'
Leg 'rev_osc_signal_export'  'scripts\rev_osc_signal_export.py run'
Leg 'update_minute_feed'     'scripts\update_minute_feed.py'
Leg 'update_ths_panel'       'scripts\update_ths_panel.py'
Leg 'ah_panel_puller'        'scripts\ah_panel_puller.py'
Leg 'update_fund_premium'    'scripts\update_fund_premium.py snapshot'
Leg 'update_fundamental'     'scripts\update_fundamental.py'
Leg 'b_layer_filter'         '-m firm.risk.b_layer_filter'
Leg 't24_prospect_promotion' 'scripts\t24_prospect_promotion.py run'
Leg 'aggressive_lab_paper'   'scripts\aggressive_lab.py paper'
Leg 'alloc_paper'            'scripts\alloc_paper.py run'
Leg 'grid_paper'             'scripts\grid_paper.py run'
Leg 'system_v1_paper'        'scripts\system_v1_paper.py run'
Leg 't35_paper_export'       'scripts\t35_paper_export.py run'
Leg 'daily_scorecard'        'scripts\daily_scorecard.py'
Leg 'daily_report'           'scripts\daily_report.py run'
Leg 'ceo_live_usage'         'scripts\ceo_live_usage.py'
Leg 'build_status'           '-m monitor.build_status'
Leg 'token_meter'            'scripts\token_meter.py'
[Console]::WriteLine('=== monthly + guards ===')
Leg 'science_audit'          'scripts\science_audit.py run'
Leg 'monthly_briefing'       'scripts\monthly_briefing.py run'
Leg 'self_review'            'scripts\self_review.py run'
Leg 'attrition_guard_scan'   'scripts\attrition_ledger_guard.py scan'
Leg 'wr_pool_smoke'          'results\_r312bmc_wr_pool_smoke.py'
[Console]::WriteLine('NOW: ' + (Get-Date -Format 'HH:mm:ss'))
[Console]::WriteLine('=== chain rerun done ===')
