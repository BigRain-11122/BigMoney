# r1035 bm-b S6 chain driver (r1033 template, 43 legs + conditional papers family)
$ErrorActionPreference = 'Continue'
Set-Location C:\Fluxgroup\FluxGroup\quant\bigmoney
$log = "results\_r1035bmb_s6_log.txt"
$t0 = Get-Date
"" | Out-File $log -Encoding utf8
function Leg([string]$name, [string[]]$cmd) {
  $out = & $cmd[0] @($cmd[1..($cmd.Length-1)]) 2>&1 | Out-String
  $rc = if ($null -ne $LASTEXITCODE) { $LASTEXITCODE } else { 0 }
  $clean = ($out -replace "`r","").TrimEnd()
  "rc=$rc $name :: $clean" | Out-File $log -Append -Encoding utf8
  return $rc
}
"chain start $($t0.ToString('HH:mm:ss')) (r1035)" | Out-File $log -Encoding utf8

$r = @()
$r += Leg 'sat_engine_status' @('python','scripts\saturation_engine.py','status')
$r += Leg 'pool_dualrun' @('python','scripts\pool_dualrun_reconcile.py','run')
$r += Leg 'compute_audit' @('python','scripts\compute_audit.py')
$r += Leg 'py_watermark' @('python','scripts\py_watermark.py','probe')
$r += Leg 'd19_probe' @('python','results\_r686bmb_d19_check.py')
$r += Leg 'd19_advance' @('python','scripts\d19_watermark.py','update','--advance')
$r += Leg 'update_daily' @('python','scripts\update_daily.py')

# bar probe: 10-19 close bar landed? (papers family gate; evening window ~20:4x-21:xx)
$tail = (Get-Content data\daily\sh510300.csv -Tail 1) -join ''
$barLanded = $tail -match '^2026-10-19,'
if ($barLanded) {
  "rc=0 papers_gate :: FIRE (10-19 bar landed, tail=$tail) -> live.paper family runs at protocol position" | Out-File $log -Append -Encoding utf8
} else {
  "rc=0 papers_gate :: SKIP live.paper family (r1035 $($t0.ToString('HH:mm')): 10-19 bar not landed, tail=$tail, evening window retry r1036)" | Out-File $log -Append -Encoding utf8
}

$r += Leg 'market_regime' @('python','scripts\market_regime.py')
$r += Leg 'strategy_scorecard' @('python','scripts\strategy_scorecard.py')
$r += Leg 'market_clock_call' @('python','scripts\market_clock_call.py','run')
$r += Leg 'update_lhb' @('python','scripts\update_lhb.py')
$r += Leg 'update_zt_pool' @('python','scripts\update_zt_pool.py')
$r += Leg 'update_heat' @('python','scripts\update_heat.py')
$r += Leg 'update_futures' @('python','scripts\update_futures.py')
$r += Leg 'update_repo_panel' @('python','scripts\update_repo.py')
$r += Leg 'update_options' @('python','scripts\update_options.py')
$r += Leg 'update_moneyflow' @('python','scripts\update_moneyflow.py')
$r += Leg 'update_sina_mf' @('python','scripts\update_sina_mf.py')
$r += Leg 'update_astock_daily' @('python','scripts\update_astock_daily.py')
$r += Leg 'update_etf_daily' @('python','scripts\update_etf_daily.py')
$r += Leg 'regime_thermo' @('python','scripts\regime_thermo_build.py')
$r += Leg 'regime_gate_dualarm' @('python','scripts\regime_gate_dualarm.py','run')
$r += Leg 'rev_osc_signal' @('python','scripts\rev_osc_signal_export.py','run')
$r += Leg 'update_minute_feed' @('python','scripts\update_minute_feed.py')
$r += Leg 'update_ths_panel' @('python','scripts\update_ths_panel.py')
$r += Leg 'ah_panel_puller' @('python','scripts\ah_panel_puller.py')
$r += Leg 'update_fund_premium' @('python','scripts\update_fund_premium.py','snapshot')
$r += Leg 'update_fundamental' @('python','scripts\update_fundamental.py')
$r += Leg 'b_layer_filter' @('python','-m','firm.risk.b_layer_filter')
$r += Leg 'update_fund_statements' @('python','scripts\update_fund_statements.py')

if ($barLanded) {
  $env:BIGMONEY_REGIME_GUARD = 'enforce'
  $r += Leg 'live_paper' @('python','-m','live.paper')
  $r += Leg 't35_open_fill_verify' @('python','scripts\t35_open_fill_verify.py')
  $r += Leg 't24_prospect_paper' @('python','scripts\t24_prospect_paper.py','run')
  $r += Leg 't24_prospect_promotion' @('python','scripts\t24_prospect_promotion.py','run')
  Remove-Item Env:BIGMONEY_REGIME_GUARD -ErrorAction SilentlyContinue
} else {
  "rc=0 papers_family :: honest SKIP x4 (live.paper + t35_open_fill_verify + t24_prospect_paper + t24_prospect_promotion; bar gate closed)" | Out-File $log -Append -Encoding utf8
}

$r += Leg 'aggressive_lab' @('python','scripts\aggressive_lab.py','paper')
$r += Leg 'alloc_paper' @('python','scripts\alloc_paper.py','run')
$r += Leg 'grid_paper' @('python','scripts\grid_paper.py','run')
$r += Leg 'system_v1_paper' @('python','scripts\system_v1_paper.py','run')
$r += Leg 't35_paper_export' @('python','scripts\t35_paper_export.py','run')
$r += Leg 'daily_scorecard' @('python','scripts\daily_scorecard.py')
$r += Leg 'daily_report' @('python','scripts\daily_report.py','run')
$r += Leg 'ceo_live_usage' @('python','scripts\ceo_live_usage.py')
$r += Leg 'build_status' @('python','-m','monitor.build_status')
$r += Leg 'token_meter' @('python','scripts\token_meter.py')
$r += Leg 'attrition_scan' @('python','scripts\attrition_ledger_guard.py','scan')
$r += Leg 'idle_probe_no_worked' @('python','Tools\idle_trigger.py')

$t1 = Get-Date
$elapsed = [math]::Round(($t1 - $t0).TotalMinutes, 1)
$bad = ($r | Where-Object { $_ -ne 0 }).Count
"chain end $($t1.ToString('HH:mm:ss')) elapsed=$elapsed min legs=$($r.Count) nonzero_rc=$bad rc_list=$($r -join ',')" | Out-File $log -Append -Encoding utf8
Write-Output "CHAIN_DONE elapsed=$elapsed min legs=$($r.Count) nonzero_rc=$bad"
