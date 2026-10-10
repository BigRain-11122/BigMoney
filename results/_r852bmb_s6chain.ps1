# r852 bm-b S6 chain runner (ASCII-only per PS5.1 encoding law)
$ErrorActionPreference = 'Continue'
$root = 'C:\Fluxgroup\FluxGroup\quant\bigmoney'
Set-Location $root
if (-not (Test-Path $root)) { throw "root guard failed: $root" }
$log = Join-Path $root 'results\_r852bmb_s6chain.log'
"== r852 S6 chain start $(Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz') ==" | Out-File -FilePath $log -Encoding utf8

function Run-Leg {
  param($name, $cmd)
  $out = Invoke-Expression $cmd 2>&1 | Out-String
  $rc = $LASTEXITCODE
  $tail = ($out -split "`r?`n") | Where-Object { $_ -ne '' } | Select-Object -Last 8
  Add-Content -Path $log -Value "[$name] rc=$rc"
  if ($tail) { Add-Content -Path $log -Value ($tail -join "`n") }
  Write-Host "[$name] rc=$rc"
}

Run-Leg '01_pool_dualrun' 'python scripts\pool_dualrun_reconcile.py run'
Run-Leg '02_compute_audit' 'python scripts\compute_audit.py'
Run-Leg '03_py_watermark' 'python scripts\py_watermark.py probe'
Run-Leg '04_update_daily' 'python scripts\update_daily.py'
Run-Leg '05_market_regime' 'python scripts\market_regime.py'
Run-Leg '06_scorecard' 'python scripts\strategy_scorecard.py'
Run-Leg '07_market_clock' 'python scripts\market_clock_call.py run'
Run-Leg '08_update_lhb' 'python scripts\update_lhb.py'
Run-Leg '09_zt_pool' 'python scripts\update_zt_pool.py'
Run-Leg '10_update_heat' 'python scripts\update_heat.py'
Run-Leg '11_update_futures' 'python scripts\update_futures.py'
Run-Leg '12_update_repo' 'python scripts\update_repo.py'
Run-Leg '13_update_options' 'python scripts\update_options.py'
Run-Leg '14_moneyflow' 'python scripts\update_moneyflow.py'
Run-Leg '15_sina_mf' 'python scripts\update_sina_mf.py'
Run-Leg '16_astock_daily' 'python scripts\update_astock_daily.py'
Run-Leg '17_etf_daily' 'python scripts\update_etf_daily.py'
Run-Leg '18_thermo_build' 'python scripts\regime_thermo_build.py'
Run-Leg '19_dualarm' 'python scripts\regime_gate_dualarm.py run'
Run-Leg '20_rev_osc_export' 'python scripts\rev_osc_signal_export.py run'
Run-Leg '21_minute_feed' 'python scripts\update_minute_feed.py'
Run-Leg '22_ths_panel' 'python scripts\update_ths_panel.py'
Run-Leg '23_ah_panel' 'python scripts\ah_panel_puller.py'
Run-Leg '24_fund_premium' 'python scripts\update_fund_premium.py snapshot'
Run-Leg '25_fundamental' 'python scripts\update_fundamental.py'
Run-Leg '26_b_layer' 'python -m firm.risk.b_layer_filter'
Run-Leg '27_fund_stmt' 'python scripts\update_fund_statements.py'
$env:BIGMONEY_REGIME_GUARD = 'enforce'
Run-Leg '28_live_paper' 'python -m live.paper'
Run-Leg '29_t35_open_fill' 'python scripts\t35_open_fill_verify.py'
Run-Leg '30_t24_prospect' 'python scripts\t24_prospect_paper.py run'
Run-Leg '31_t24_promotion' 'python scripts\t24_prospect_promotion.py run'
Run-Leg '32_aggr_paper' 'python scripts\aggressive_lab.py paper'
Run-Leg '33_alloc_paper' 'python scripts\alloc_paper.py run'
Run-Leg '34_grid_paper' 'python scripts\grid_paper.py run'
Run-Leg '35_system_v1' 'python scripts\system_v1_paper.py run'
Run-Leg '36_t35_export' 'python scripts\t35_paper_export.py run'
Run-Leg '37_daily_scorecard' 'python scripts\daily_scorecard.py'
Run-Leg '38_daily_report' 'python scripts\daily_report.py run'
Run-Leg '39_ceo_live_usage' 'python scripts\ceo_live_usage.py'
Run-Leg '40_build_status' 'python -m monitor.build_status'
Run-Leg '41_token_meter' 'python scripts\token_meter.py'
Add-Content -Path $log -Value "== r852 S6 chain end $(Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz') =="
