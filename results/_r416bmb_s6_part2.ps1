$ErrorActionPreference = "Continue"
$log = "results\_r416bmb_s6_log.txt"
$legs = @(
    @{ n = "astock_dly";  c = "python scripts\update_astock_daily.py" },
    @{ n = "etf_dly";     c = "python scripts\update_etf_daily.py" },
    @{ n = "rev_osc";     c = "python scripts\rev_osc_signal_export.py run" },
    @{ n = "minute_feed"; c = "python scripts\update_minute_feed.py" },
    @{ n = "ths_panel";   c = "python scripts\update_ths_panel.py" },
    @{ n = "ah_panel";    c = "python scripts\ah_panel_puller.py" },
    @{ n = "fund_prem";   c = "python scripts\update_fund_premium.py snapshot" },
    @{ n = "fundament";   c = "python scripts\update_fundamental.py" },
    @{ n = "b_layer";     c = "python -m firm.risk.b_layer_filter" },
    @{ n = "t24_promo";   c = "python scripts\t24_prospect_promotion.py run" },
    @{ n = "aggr_paper";  c = "python scripts\aggressive_lab.py paper" },
    @{ n = "alloc_paper"; c = "python scripts\alloc_paper.py run" },
    @{ n = "grid_paper";  c = "python scripts\grid_paper.py run" },
    @{ n = "sys_v1";      c = "python scripts\system_v1_paper.py run" },
    @{ n = "t35_export";  c = "python scripts\t35_paper_export.py run" },
    @{ n = "daily_score"; c = "python scripts\daily_scorecard.py" },
    @{ n = "daily_rpt";   c = "python scripts\daily_report.py run" },
    @{ n = "ceo_usage";   c = "python scripts\ceo_live_usage.py" },
    @{ n = "build_stat";  c = "python -m monitor.build_status" },
    @{ n = "token_mtr";   c = "python scripts\token_meter.py" }
)
foreach ($l in $legs) {
    $start = Get-Date
    $out = Invoke-Expression $l.c 2>&1 | Out-String
    $rc = $LASTEXITCODE
    $tail = ($out -split "`n" | Where-Object { $_ -match '\S' } | Select-Object -Last 2) -join ' | '
    $line = "{0,-12} rc={1} [{2:mm\:ss}] {3}" -f $l.n, $rc, ((Get-Date) - $start), $tail
    Write-Output $line
    Add-Content $log "=== LEG $($l.n) rc=$rc ==="
    Add-Content $log $out
}
