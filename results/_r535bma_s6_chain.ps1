# r535 bm-a S6 maintenance chain v2 (holiday 2026-10-01; each leg self-guards)
$ErrorActionPreference = 'Continue'
$legs = @(
  @('pool_dualrun_reconcile', 'run'),
  @('compute_audit', ''),
  @('py_watermark', 'probe'),
  @('update_daily', ''),
  @('market_regime', ''),
  @('strategy_scorecard', ''),
  @('market_clock_call', 'run'),
  @('update_lhb', ''),
  @('update_heat', ''),
  @('update_futures', ''),
  @('update_repo', ''),
  @('update_options', ''),
  @('update_moneyflow', ''),
  @('update_sina_mf', ''),
  @('update_astock_daily', ''),
  @('update_etf_daily', ''),
  @('rev_osc_signal_export', 'run'),
  @('update_minute_feed', ''),
  @('update_ths_panel', ''),
  @('ah_panel_puller', ''),
  @('update_fund_premium', 'snapshot'),
  @('update_fundamental', ''),
  @('t24_prospect_promotion', 'run'),
  @('aggressive_lab', 'paper'),
  @('alloc_paper', 'run'),
  @('grid_paper', 'run'),
  @('system_v1_paper', 'run'),
  @('t35_paper_export', 'run'),
  @('daily_scorecard', ''),
  @('daily_report', 'run'),
  @('ceo_live_usage', '')
)
$fails = @()
foreach ($leg in $legs) {
  $name = $leg[0]; $sub = $leg[1]
  $cmd = "scripts\" + $name + ".py"
  if ($sub -ne '') { $out = & python $cmd $sub 2>&1 } else { $out = & python $cmd 2>&1 }
  $rc = $LASTEXITCODE
  $arr = @($out | Select-Object -Last 1)
  $txt = ''
  if ($arr.Count -gt 0 -and $null -ne $arr[0]) { $txt = ($arr[0].ToString() -replace '\s+', ' ') }
  if ($txt.Length -gt 105) { $txt = $txt.Substring(0, 105) }
  Write-Host ("{0,-26} rc={1}  {2}" -f $name, $rc, $txt)
  if ($rc -ne 0) { $fails += ("$name rc=$rc") }
}
# module-form legs
foreach ($m in @(@('firm.risk.b_layer_filter',''), @('monitor.build_status',''))) {
  if ($m[1] -ne '') { $out = & python -m $m[0] $m[1] 2>&1 } else { $out = & python -m $m[0] 2>&1 }
  Write-Host ("{0,-26} rc={1}" -f $m[0], $LASTEXITCODE)
  if ($LASTEXITCODE -ne 0) { $fails += "$($m[0]) rc=$LASTEXITCODE" }
}
$out = & python scripts\token_meter.py 2>&1
$arr = @($out | Select-Object -Last 1); $txt = if ($arr.Count) { $arr[0].ToString() } else { '' }
Write-Host ("{0,-26} rc={1}  {2}" -f 'token_meter', $LASTEXITCODE, $txt)
if ($LASTEXITCODE -ne 0) { $fails += "token_meter rc=$LASTEXITCODE" }
Write-Host "=== FAILS: $($fails.Count) ==="
if ($fails.Count -gt 0) { $fails | ForEach-Object { Write-Host "  FAIL: $_" } }
