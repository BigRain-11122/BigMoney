# r775 bm-b S6 chain RESUME runner (legs 22-39; legs 01-21 rc=0 in _r775bmb_s6_chain.out,
#  parent killed by 5-min no-output watchdog mid-leg-22 2026-10-06 14:2x; lineage r774 verbatim)
$ErrorActionPreference = "Continue"
$env:PYTHONIOENCODING = "utf-8"
$rcs = @()

function Leg($name) {
    "== LEG $name RC=$LASTEXITCODE =="
    $script:rcs += "$name=$LASTEXITCODE"
}

"== S6 chain RESUME r775 bm-b legs 22-39 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') =="
python scripts\update_fundamental.py; Leg "22_fundamental"
python -m firm.risk.b_layer_filter; Leg "23_b_layer"
python scripts\update_fund_statements.py; Leg "24_fund_statements"
# legs 25-28 (live.paper/t35_open_fill/t24 pair): golden-week no-new-bar block -> honest skip (cutoff 2026-09-30 unchanged)
python scripts\aggressive_lab.py paper; Leg "29_aggr_paper"
python scripts\alloc_paper.py run; Leg "30_alloc_paper"
python scripts\grid_paper.py run; Leg "31_grid_paper"
python scripts\system_v1_paper.py run; Leg "32_system_v1"
python scripts\t35_paper_export.py run; Leg "33_t35_export"
python scripts\daily_scorecard.py; Leg "34_daily_scorecard"
python scripts\daily_report.py run; Leg "35_daily_report"
python scripts\ceo_live_usage.py; Leg "36_ceo_live"
python -m monitor.build_status; Leg "37_build_status"
python scripts\token_meter.py; Leg "38_token_meter"
python scripts\finalize_trio_readiness.py; Leg "39_trio_readiness"

"== S6 SUMMARY (resume legs 22-39) =="
$rcs -join " "
"== S6 chain RESUME end $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') =="
