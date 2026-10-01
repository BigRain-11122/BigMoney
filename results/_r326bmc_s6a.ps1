# r326 bm-c S6 chain batch A -- data/maintenance legs (23), rc per leg, log to file.
# Write-Host for progress (r318 law); batch A/B split per r324 5min-chop law.
$Project = "K:\Fluxgroup\FluxGroup\quant\bigmoney"
Set-Location $Project
$log = Join-Path $Project "results\_r326bmc_s6.log"
"=== r326 S6 chain batch A start $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Encoding utf8
$legs = @(
  @("dualrun",    "scripts\pool_dualrun_reconcile.py", "run"),
  @("audit",      "scripts\compute_audit.py", ""),
  @("wm",         "scripts\py_watermark.py", "probe"),
  @("daily",      "scripts\update_daily.py", ""),
  @("regime",     "scripts\market_regime.py", ""),
  @("scorecard",  "scripts\strategy_scorecard.py", ""),
  @("mccall",     "scripts\market_clock_call.py", "run"),
  @("lhb",        "scripts\update_lhb.py", ""),
  @("heat",       "scripts\update_heat.py", ""),
  @("futures",    "scripts\update_futures.py", ""),
  @("repo",       "scripts\update_repo.py", ""),
  @("options",    "scripts\update_options.py", ""),
  @("moneyflow",  "scripts\update_moneyflow.py", ""),
  @("sinamf",     "scripts\update_sina_mf.py", ""),
  @("astock",     "scripts\update_astock_daily.py", ""),
  @("etf",        "scripts\update_etf_daily.py", ""),
  @("revosc",     "scripts\rev_osc_signal_export.py", "run"),
  @("minfeed",    "scripts\update_minute_feed.py", ""),
  @("ths",        "scripts\update_ths_panel.py", ""),
  @("ahpanel",    "scripts\ah_panel_puller.py", ""),
  @("fundprem",   "scripts\update_fund_premium.py", "snapshot"),
  @("fundamental","scripts\update_fundamental.py", "")
)
$fail = 0
foreach ($leg in $legs) {
  $name = $leg[0]; $script = $leg[1]; $sub = $leg[2]
  $t0 = Get-Date
  if ($sub -ne "") { $out = & python $script $sub 2>&1 } else { $out = & python $script 2>&1 }
  $rc = $LASTEXITCODE
  $el = [int]((Get-Date) - $t0).TotalSeconds
  if ($rc -ne 0) { $fail++ }
  $tail = ($out | Select-Object -Last 2) -join " | "
  $line = "LEG $name rc=$rc ${el}s :: $tail"
  Write-Host $line
  Add-Content $log $line
  Add-Content $log ($out -join "`n")
}
$t0 = Get-Date
$out = & python -m firm.risk.b_layer_filter 2>&1
$rc = $LASTEXITCODE
$el = [int]((Get-Date) - $t0).TotalSeconds
if ($rc -ne 0) { $fail++ }
$line = "LEG blayer rc=$rc ${el}s :: $(($out | Select-Object -Last 2) -join ' | ')"
Write-Host $line
Add-Content $log $line
Add-Content $log ($out -join "`n")
Write-Host "=== batch A done $(Get-Date -Format 'HH:mm:ss') fail=$fail ==="
Add-Content $log "=== batch A done $(Get-Date -Format 'HH:mm:ss') fail=$fail ==="
exit $fail
