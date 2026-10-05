# r737 bm-b S6 chain RESUME (legs 32-39; recovery after outer-tool 5-min-silent cancel killed the
#  original driver mid-leg-32; legs 01-31 all RC=0 verified in results\_r737bmb_s6_chain.log)
# Log: results\_r737bmb_s6_chain_resume.log
$ErrorActionPreference = "Continue"
$env:PYTHONIOENCODING = "utf-8"
$rcs = @()

function Leg($name) {
    "== LEG $name RC=$LASTEXITCODE =="
    $script:rcs += "$name=$LASTEXITCODE"
}

"== S6 chain RESUME r737 legs 32-39 bm-b $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') =="
python scripts\system_v1_paper.py run; Leg "32_system_v1"
python scripts\t35_paper_export.py run; Leg "33_t35_export"
python scripts\daily_scorecard.py; Leg "34_daily_scorecard"
python scripts\daily_report.py run; Leg "35_daily_report"
python scripts\ceo_live_usage.py; Leg "36_ceo_live"
python -m monitor.build_status; Leg "37_build_status"
python scripts\token_meter.py; Leg "38_token_meter"
python scripts\finalize_trio_readiness.py; Leg "39_trio_readiness"

"== S6 RESUME SUMMARY (legs 32-39) =="
$rcs -join " "
"== S6 chain resume end $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') =="
