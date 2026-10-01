# r508 bm-b S6 chain part 2 (paper/export/scorecard/report/token legs)
$Project = "C:\Fluxgroup\FluxGroup\quant\bigmoney"
Set-Location $Project
$log = Join-Path $Project "results\_r508bmb_s6_log.txt"

function Leg($name, $cmd) {
    Write-Host "LEG $name ..."
    $out = & cmd /c "$cmd 2>&1"
    $rc = $LASTEXITCODE
    $tail = ($out | Select-Object -Last 3) -join " | "
    Write-Host "LEG $name rc=$rc :: $tail"
    "LEG $name rc=$rc :: $tail" | Out-File $log -Append -Encoding utf8
}

Leg "24 live.paper" "python -m live.paper"
Leg "25 t35_open_fill_verify" "python scripts\t35_open_fill_verify.py"
Leg "26 t24_prospect_paper" "python scripts\t24_prospect_paper.py run"
Leg "27 t24_prospect_promotion" "python scripts\t24_prospect_promotion.py run"
Leg "28 aggressive_lab paper" "python scripts\aggressive_lab.py paper"
Leg "29 alloc_paper run" "python scripts\alloc_paper.py run"
Leg "30 grid_paper run" "python scripts\grid_paper.py run"
Leg "31 system_v1_paper run" "python scripts\system_v1_paper.py run"
Leg "32 t35_paper_export" "python scripts\t35_paper_export.py run"
Leg "33 daily_scorecard" "python scripts\daily_scorecard.py"
Leg "34 daily_report run" "python scripts\daily_report.py run"
Leg "35 ceo_live_usage" "python scripts\ceo_live_usage.py"
Leg "36 build_status" "python -m monitor.build_status"
Leg "37 token_meter" "python scripts\token_meter.py"
"=== r508 S6 chain end $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss') ===" | Out-File $log -Append -Encoding utf8
Write-Host "PART2 DONE"
