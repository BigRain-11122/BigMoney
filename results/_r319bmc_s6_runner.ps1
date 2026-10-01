# r319 bm-c S6 chain -- run all legs, capture rc per leg, log to file.
# Write-Host for progress lines (r318 [void] output-swallow law).
$Project = "K:\Fluxgroup\FluxGroup\quant\bigmoney"
Set-Location $Project
$log = Join-Path $Project "results\_r319bmc_s6.log"
"=== r319 S6 chain start $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Encoding utf8
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
foreach ($leg in $legs) {
  $name = $leg[0]; $script = $leg[1]; $sub = $leg[2]
  $t0 = Get-Date
  if ($sub -ne "") {
    $out = & python $script $sub 2>&1
  } else {
    $out = & python $script 2>&1
  }
  $rc = $LASTEXITCODE
  $el = [int]((Get-Date) - $t0).TotalSeconds
  $tail = ($out | Select-Object -Last 2) -join " | "
  $line = "LEG $name rc=$rc ${el}s :: $tail"
  Write-Host $line
  Add-Content $log $line
  Add-Content $log ($out -join "`n")
}
Write-Host "=== blayer ==="
& python -m firm.risk.b_layer_filter 2>&1 | ForEach-Object { Add-Content $log $_ }
Write-Host "BLAYER rc=$LASTEXITCODE"
Add-Content $log "=== end $(Get-Date -Format 'HH:mm:ss') ==="
