# r510 bm-b S6 chain part 1 (23 legs, reuse r509 skeleton; r318 Write-Host law)
$Project = "C:\Fluxgroup\FluxGroup\quant\bigmoney"
Set-Location $Project
$log = Join-Path $Project "results\_r510bmb_s6_log.txt"
"=== r510 S6 chain start $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss') ===" | Out-File $log -Encoding utf8

function Leg($name, $cmd) {
    Write-Host "LEG $name ..."
    $out = & cmd /c "$cmd 2>&1"
    $rc = $LASTEXITCODE
    $tail = ($out | Select-Object -Last 3) -join " | "
    Write-Host "LEG $name rc=$rc :: $tail"
    "LEG $name rc=$rc :: $tail" | Out-File $log -Append -Encoding utf8
}

Leg "01 pool_dualrun_reconcile" "python scripts\pool_dualrun_reconcile.py run"
Leg "02 compute_audit" "python scripts\compute_audit.py"
Leg "03 py_watermark probe" "python scripts\py_watermark.py probe"
Leg "04 update_daily" "python scripts\update_daily.py"
Leg "05 market_regime" "python scripts\market_regime.py"
Leg "06 strategy_scorecard" "python scripts\strategy_scorecard.py"
Leg "07 market_clock_call" "python scripts\market_clock_call.py run"
Leg "08 update_lhb" "python scripts\update_lhb.py"
Leg "09 update_heat" "python scripts\update_heat.py"
Leg "10 update_futures" "python scripts\update_futures.py"
Leg "11 update_repo" "python scripts\update_repo.py"
Leg "12 update_options" "python scripts\update_options.py"
Leg "13 update_moneyflow" "python scripts\update_moneyflow.py"
Leg "14 update_sina_mf" "python scripts\update_sina_mf.py"
Leg "15 update_astock_daily" "python scripts\update_astock_daily.py"
Leg "16 update_etf_daily" "python scripts\update_etf_daily.py"
Leg "17 rev_osc_signal_export" "python scripts\rev_osc_signal_export.py run"
Leg "18 update_minute_feed" "python scripts\update_minute_feed.py"
Leg "19 update_ths_panel" "python scripts\update_ths_panel.py"
Leg "20 ah_panel_puller" "python scripts\ah_panel_puller.py"
Leg "21 update_fund_premium" "python scripts\update_fund_premium.py snapshot"
Leg "22 update_fundamental" "python scripts\update_fundamental.py"
Leg "23 b_layer_filter" "python -m firm.risk.b_layer_filter"
"=== r510 S6 part 1 done $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Append -Encoding utf8
Write-Host "PART1 DONE"
