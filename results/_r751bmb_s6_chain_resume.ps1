# r751 bm-b S6 chain RESUME runner (legs 37-39 only; legs 01-36 rc=0 in _r751bmb_s6_chain.log,
#  original runner tree-killed by tool 5min auto-cancel mid-leg-37 per r737 family)
# Log: results\_r751bmb_s6_chain_resume.log
$ErrorActionPreference = "Continue"
$env:PYTHONIOENCODING = "utf-8"
$rcs = @()

function Leg($name) {
    "== LEG $name RC=$LASTEXITCODE =="
    $script:rcs += "$name=$LASTEXITCODE"
}

"== S6 chain RESUME r751 legs 37-39 bm-b $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') =="
python -m monitor.build_status; Leg "37_build_status"
python scripts\token_meter.py; Leg "38_token_meter"
python scripts\finalize_trio_readiness.py; Leg "39_trio_readiness"

"== S6 SUMMARY RESUME =="
$rcs -join " "
"== S6 chain RESUME end $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') =="
