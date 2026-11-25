# r2089 bm-c: drive scripts/etf_book_atlas_arms_rebuild.py refresh on a 10-minute self-heal tick.
# WHY: 8 of the 11 phase-atlas arm faces are priced on the 2026-11-20 world (digest 2e875bf4)
# while the atlas base face sits on 2026-11-24 (706c06e0). The arms audit can then compare
# only the two rungs that were re-priced, the floor fit needs >=4 points, k comes back None,
# and 7 selftest legs go red -- a face-generation gap, not a code defect. One atlas sweep is
# ~200s, so the whole family cannot be paid for inside a CLI round (and a CLI-started long
# child is killed with the parent). This tick pays what the budget allows, leaves the rest
# named in the receipt, and disables ITSELF once every arm carries the same world digest.
# Pure ASCII on purpose (iteration_loop.ps1 ENCODING RULE family).
$ErrorActionPreference = 'Continue'
$root = 'K:\Fluxgroup\FluxGroup\quant\bigmoney'
$name = 'Bigmoney-AtlasArmsReburn-bm-c'
Set-Location $root
$lock = Join-Path $root 'results\_atlas_arms_reburn.lock'
$log  = Join-Path $root 'logs\atlas_arms_reburn.log'
$rec  = Join-Path $root 'results\etf_book_atlas_arms_rebuild.json'
New-Item -ItemType Directory -Force -Path (Split-Path $log) | Out-Null

function Say($m) {
    $ts = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
    "$ts $m" | Out-File -Append -Encoding utf8 $log
}

# single flight: a dead holder's lock is reclaimed, a live one is skipped
if (Test-Path $lock) {
    $held = Get-Content $lock -Raw -ErrorAction SilentlyContinue
    if ($held -and $held.Trim() -match '^\d+$') {
        if (Get-Process -Id ([int]$held.Trim()) -ErrorAction SilentlyContinue) {
            Say "[skip] pid $($held.Trim()) still running"
            exit 0
        }
        Say "[lock] reclaiming dead pid $($held.Trim())"
    }
}
$PID | Set-Content -Encoding ascii $lock
try {
    $env:PYTHONIOENCODING = 'utf-8'
    Say "[tick] refresh start"
    & python scripts\etf_book_atlas_arms_rebuild.py refresh --budget=2400 2>&1 |
        Out-File -Append -Encoding utf8 $log
    $rc = $LASTEXITCODE
    Say "[tick] rc=$rc"
    if (Test-Path $rec) {
        $j = Get-Content $rec -Raw | ConvertFrom-Json
        $rebuilt = (@($j.rebuilt) -join ',')
        $left    = (@($j.left)    -join ',')
        Say "[tick] status=$($j.status) verdict=$($j.verdict) rebuilt=[$rebuilt] left=[$left] audit_check_rc=$($j.audit_check_rc)"
        if ($j.verdict -eq 'ONE_WORLD') {
            Say "[done] every arm on one world; disabling $name"
            & schtasks.exe /change /tn $name /disable | Out-Null
        }
    } else {
        Say "[tick] no receipt written"
    }
} finally {
    Remove-Item $lock -Force -ErrorAction SilentlyContinue
}
