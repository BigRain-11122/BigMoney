# r517 bm-b surgical push (r512 temp-index law; r523 live-daemon race route)
# Payload = my commits vs old base (d2e9894f7) + current dirty engine faces.
# Never re-serializes origin-owned faces: read-tree origin/main first, then add
# only my paths from the working tree.
$ErrorActionPreference = "Stop"
Set-Location "C:\Fluxgroup\FluxGroup\quant\bigmoney"

$base = "d2e9894f7"
git fetch origin 2>&1 | Out-Null

$mine = @(git diff --name-only "$base..HEAD")
$dirty = @()
git status --porcelain | ForEach-Object {
    $p = $_.Substring(3).Trim('"')
    if ($p) { $dirty += $p }
}
$payload = @($mine + $dirty) | Sort-Object -Unique
$plFile = Join-Path $env:TEMP "r517_payload.txt"
$payload | Out-File -FilePath $plFile -Encoding ascii
"PAYLOAD_FILES=" + $payload.Count

$idx = Join-Path $env:TEMP "r517_idx"
if (Test-Path $idx) { Remove-Item $idx -Force }
$env:GIT_INDEX_FILE = $idx
git read-tree origin/main
git add -A --pathspec-from-file="$plFile"
$tree = git write-tree
$parent = git rev-parse origin/main
$new = git commit-tree $tree -p $parent -m "round 517 closeout surgical (temp-index onto moved origin): N1-W19 engine wave frozen (7th engine wave, bm-b 5th own, rotation slot 19=bm-b; A 76_001..78_000 arithmetic clean, B 38_100..38_299 FORCED skip past lfc actual + registry point 30_000; ADMIT receipt + law row + mirrors + prereg + selftest legs + banned gate ADMIT; engine ignited, shards burning) + state/heartbeat r517 + round report + CODELY lesson + S6 37-leg faces + rides [via bm-b]"
$new = $new.Trim()
"NEW_COMMIT=" + $new
Remove-Item Env:GIT_INDEX_FILE -ErrorAction SilentlyContinue

git push origin "$($new):refs/heads/main" 2>&1 | Select-Object -Last 2
"PUSH_EXIT=$LASTEXITCODE"
if ($LASTEXITCODE -ne 0) {
    "push rejected -- per r512 law: fetch, rebuild, new parent, cheap retry"
    exit 1
}
git fetch origin 2>&1 | Out-Null
git reset --mixed origin/main
git checkout -- .
"N_AHEAD=" + @(git log origin/main..HEAD --oneline).Count
git log -1 --format="HEAD=%h %ci %s"
"DIRTY_AFTER=" + @(git status --porcelain).Count
git status --porcelain | Select-Object -First 6
