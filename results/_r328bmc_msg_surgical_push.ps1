# r328 bm-c surgical push: W17xW19 collision kill-advice MSG only (speed lane).
# r512 temp-index law + r523 live-daemon race route. ZERO working-tree/HEAD touch
# (local finalize commit chain preserved for the subsequent integration).
$ErrorActionPreference = "Stop"
$g = "K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\silent-git.ps1"
Set-Location "K:\Fluxgroup\FluxGroup\quant\bigmoney"

& $g -GitArgs "fetch origin" | Out-Null
$parent = (& $g -GitArgs "rev-parse origin/main").Trim()
"BASE=$parent"

$idx = Join-Path $env:TEMP "r328bmc_msg_idx"
if (Test-Path $idx) { Remove-Item $idx -Force }
$env:GIT_INDEX_FILE = $idx
& $g -GitArgs "read-tree origin/main" | Out-Null
& $g -GitArgs "add fleet/inbox/MSG-20261001-184x-bmc-bmb-GM-ALL-w17-w19-double-freeze-collision.md"
$tree = (& $g -GitArgs "write-tree").Trim()
"TREE=$tree"
Remove-Item Env:GIT_INDEX_FILE -ErrorAction SilentlyContinue

$msg = "MSG-184x surgical: N1-W17xW19 double-freeze collision kill-advice + commit-time adjudication (W19 yields: identical bands A 76_001..78_000/B 38_100..38_299, bm-c W17 freeze 7e03101fb on origin ~18:23 EARLIER than bm-b 5f18511ce 18:28:34; W17 12/12 burned+finalized K=35,320 ledger 401,948 landing same window; bm-b truncate W19 burn, no finalize, discard 9 dup shards zero loss, yield=re-band or void) + r513-disease 4th occurrence disclosure (stale surgical swept W17 rows) [via bm-c]"
$new = (& $g -GitArgs ("commit-tree " + $tree + " -p " + $parent + " -m `"" + $msg + "`"")).Trim()
"NEW_COMMIT=$new"

& $g -GitArgs ("push origin " + $new + ":refs/heads/main")
"PUSH_EXIT=$LASTEXITCODE"
if ($LASTEXITCODE -ne 0) {
    "push rejected -- per r512 law: fetch, rebuild, new parent, cheap retry"
    exit 1
}
& $g -GitArgs "fetch origin" | Out-Null
$now = (& $g -GitArgs "rev-parse origin/main").Trim()
"ORIGIN_NOW=$now"
