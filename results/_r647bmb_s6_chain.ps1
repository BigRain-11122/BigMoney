# r647 bm-b S6 chain runner (ASCII-only per PS5.1 ANSI pit law)
# Conditional new-bar trio (live.paper / t35_open_fill_verify / t24_prospect_paper /
# t24_prospect_promotion) skipped this round: Golden Week Sunday, no new bar
# (r636/r637/r646 precedent; last trading day 2026-09-30).
$ev = 'results\_r647bmb_s6_evidence.txt'
Set-Content -Path $ev -Value ("S6 chain r647 bm-b start " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))

function Run-Leg {
  param([string]$name, [string[]]$argv)
  $t0 = Get-Date
  $o = & python @argv 2>&1
  $rc = $LASTEXITCODE
  $last = ''
  foreach ($l in $o) { if ($l -and $l.ToString().Trim()) { $last = $l.ToString().Trim() } }
  if ($last.Length -gt 120) { $last = $last.Substring(0, 120) }
  Add-Content -Path $ev -Value ("{0} {1} rc={2} tail={3}" -f $t0.ToString('HH:mm:ss'), $name, $rc, $last)
  return $rc
}

$fail = @()
$rc = 0

$rc = Run-Leg 'dualrun'        @('scripts\pool_dualrun_reconcile.py','run'); if ($rc -ne 0) { $fail += "dualrun=$rc" }
$rc = Run-Leg 'compute_audit'  @('scripts\compute_audit.py');                if ($rc -ne 0) { $fail += "compute_audit=$rc" }
$rc = Run-Leg 'wm_probe'       @('scripts\py_watermark.py','probe');         if ($rc -ne 0) { $fail += "wm_probe=$rc" }
$rc = Run-Leg 'update_daily'   @('scripts\update_daily.py');                 if ($rc -ne 0 -and $rc -ne 1) { $fail += "update_daily=$rc" }
$rc = Run-Leg 'market_regime'  @('scripts\market_regime.py');                if ($rc -ne 0) { $fail += "market_regime=$rc" }
$rc = Run-Leg 'scorecard'      @('scripts\strategy_scorecard.py');          if ($rc -ne 0) { $fail += "scorecard=$rc" }
$rc = Run-Leg 'clock_call'     @('scripts\market_clock_call.py','run');      if ($rc -ne 0) { $fail += "clock_call=$rc" }
$rc = Run-Leg 'lhb'            @('scripts\update_lhb.py');                   if ($rc -ne 0) { $fail += "lhb=$rc" }
$rc = Run-Leg 'heat'           @('scripts\update_heat.py');                   if ($rc -ne 0) { $fail += "heat=$rc" }
$rc = Run-Leg 'futures'        @('scripts\update_futures.py');               if ($rc -ne 0) { $fail += "futures=$rc" }
$rc = Run-Leg 'repo'           @('scripts\update_repo.py');                   if ($rc -ne 0) { $fail += "repo=$rc" }
$rc = Run-Leg 'options'        @('scripts\update_options.py');               if ($rc -ne 0) { $fail += "options=$rc" }
$rc = Run-Leg 'moneyflow'      @('scripts\update_moneyflow.py');             if ($rc -ne 0) { $fail += "moneyflow=$rc" }
$rc = Run-Leg 'sina_mf'        @('scripts\update_sina_mf.py');               if ($rc -ne 0) { $fail += "sina_mf=$rc" }
$rc = Run-Leg 'astock_daily'   @('scripts\update_astock_daily.py');          if ($rc -ne 0) { $fail += "astock_daily=$rc" }
$rc = Run-Leg 'etf_daily'      @('scripts\update_etf_daily.py');             if ($rc -ne 0) { $fail += "etf_daily=$rc" }
$rc = Run-Leg 'rev_osc'        @('scripts\rev_osc_signal_export.py','run');  if ($rc -ne 0) { $fail += "rev_osc=$rc" }
$rc = Run-Leg 'minute_feed'    @('scripts\update_minute_feed.py');           if ($rc -ne 0) { $fail += "minute_feed=$rc" }
$rc = Run-Leg 'ths_panel'      @('scripts\update_ths_panel.py');             if ($rc -ne 0) { $fail += "ths_panel=$rc" }
$rc = Run-Leg 'ah_panel'       @('scripts\ah_panel_puller.py');              if ($rc -ne 0) { $fail += "ah_panel=$rc" }
$rc = Run-Leg 'fund_premium'   @('scripts\update_fund_premium.py','snapshot'); if ($rc -ne 0) { $fail += "fund_premium=$rc" }
$rc = Run-Leg 'fundamental'    @('scripts\update_fundamental.py');           if ($rc -ne 0) { $fail += "fundamental=$rc" }
$rc = Run-Leg 'b_layer'        @('-m','firm.risk.b_layer_filter');           if ($rc -ne 0) { $fail += "b_layer=$rc" }
$rc = Run-Leg 'aggr_lab'       @('scripts\aggressive_lab.py','paper');       if ($rc -ne 0) { $fail += "aggr_lab=$rc" }
$rc = Run-Leg 'alloc_paper'    @('scripts\alloc_paper.py','run');            if ($rc -ne 0) { $fail += "alloc_paper=$rc" }
$rc = Run-Leg 'grid_paper'     @('scripts\grid_paper.py','run');             if ($rc -ne 0) { $fail += "grid_paper=$rc" }
$rc = Run-Leg 'sys_v1'         @('scripts\system_v1_paper.py','run');       if ($rc -ne 0) { $fail += "sys_v1=$rc" }
$rc = Run-Leg 't35_export'     @('scripts\t35_paper_export.py','run');       if ($rc -ne 0) { $fail += "t35_export=$rc" }
$rc = Run-Leg 'daily_scorecard' @('scripts\daily_scorecard.py');             if ($rc -ne 0) { $fail += "daily_scorecard=$rc" }
$rc = Run-Leg 'daily_report'   @('scripts\daily_report.py','run');           if ($rc -ne 0) { $fail += "daily_report=$rc" }
$rc = Run-Leg 'ceo_live'       @('scripts\ceo_live_usage.py');               if ($rc -ne 0) { $fail += "ceo_live=$rc" }
$rc = Run-Leg 'build_status'   @('-m','monitor.build_status');               if ($rc -ne 0) { $fail += "build_status=$rc" }
$rc = Run-Leg 'token_meter'    @('scripts\token_meter.py');                   if ($rc -ne 0) { $fail += "token_meter=$rc" }

Add-Content -Path $ev -Value ("S6 chain r647 bm-b end " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
if ($fail.Count -eq 0) {
  Write-Output "S6_ALL_GREEN count=33"
  Add-Content -Path $ev -Value "S6_ALL_GREEN count=33"
} else {
  Write-Output ("S6_FAILURES: " + ($fail -join ' | '))
  Add-Content -Path $ev -Value ("S6_FAILURES: " + ($fail -join ' | '))
}
