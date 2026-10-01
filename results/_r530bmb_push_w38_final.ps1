$g='git'
& $g fetch origin *>&1 | Out-Null
$parent = (& $g rev-parse origin/main).Trim()
Write-Host "parent=$parent"

# safety leg: origin's W38 prereg must still be the placeholder version
$ph = & $g show "${parent}:research/PERPETUAL_N1_W38_PREREG.md" | Select-String -Pattern 's7-T'
if(-not $ph){ Write-Host "SAFETY FAIL: origin W38 prereg shape unexpected -- ABORT"; exit 1 }
Write-Host "safety leg PASS: origin W38 prereg intact"

$msg = @'
round 530: W38 FINALIZE one-pass (prev 443,940 [==W37 finalize head 441,740+2,200, chain-unlocked by bm-c r342 same window] + 2,200 = 446,140; K-lift -0.0001 [1.1575->1.1574 @n_eff 443,940]; S5 4/4 PASS dual-anchor [W36 frozen-anchor + W37 rolled-anchor both disclosed]; merged K=81,520 mu -0.0916 sigma 0.2449; voids LOWAMP-P1/P2 inherited; r310 12/12 ls-tree gate PASS; prereg s7/s8 mechanical backfill; r538 one-pass no-rerun law) + W39 yield to bm-c r342 (same-band double-freeze collision, A 121_004..123_003 / B 43_001..43_200 bit-identical = dual-machine independent derive cross-validation; commit-order yield per r511 law, zero local W39 burns, zero ledger pollution) + bm-b tool receipts (_r530bmb_* band-gate/land/surgical/backfill archive) [bm-b]
'@
$msgFile = "$env:TEMP\w38fin-msg.txt"
[System.IO.File]::WriteAllText($msgFile, $msg, (New-Object System.Text.UTF8Encoding($false)))

$payload = @(
  "results/perpetual_faces/n1_w38_results.json",
  "research/PERPETUAL_N1_W38_PREREG.md",
  "results/_r530bmb_w39_band_gate.py",
  "results/_r530bmb_land_w39.py",
  "results/_r530bmb_land_w39_runner.py",
  "results/_r530bmb_land_w39_law.py",
  "results/_r530bmb_surgical_w38.ps1",
  "results/_r530bmb_reparent_w39.ps1",
  "results/_r530bmb_w38_backfill.py"
)
$idx = Join-Path $env:TEMP 'fg-w38fin-idx'
if(Test-Path $idx){ Remove-Item $idx -Force }
$env:GIT_INDEX_FILE = $idx
& $g read-tree $parent 2>&1 | Out-Null
foreach($f in $payload){
  $blob = (& $g hash-object -w $f).Trim()
  & $g update-index --add --cacheinfo "100644,$blob,$f"
  if($LASTEXITCODE -ne 0){ Write-Host "update-index FAILED $f"; Remove-Item Env:GIT_INDEX_FILE; exit 1 }
}
$tree = (& $g write-tree).Trim()
$sha = (& $g commit-tree $tree -p $parent -F $msgFile).Trim()
Write-Host "newcommit=$sha"

# audit legs (r531/r519)
$w38res = (& $g ls-tree $sha results/perpetual_faces/n1_w38_results.json --name-only | Measure-Object).Count
$w37res = (& $g ls-tree $sha results/perpetual_faces/n1_w37_results.json --name-only | Measure-Object).Count
$w36res = (& $g ls-tree $sha results/perpetual_faces/n1_w36_results.json --name-only | Measure-Object).Count
$n38 = (& $g ls-tree $sha results/p2cal_ext/n1_w38/ --name-only | Measure-Object -Line).Lines
$lap3 = (& $g ls-tree $sha results/lowamp_p3/ --name-only | Measure-Object -Line).Lines
Write-Host "audit: w38res=$w38res w37res=$w37res w36res=$w36res w38shards=$n38 lowamp_p3=$lap3"
if(-not($w38res -eq 1 -and $w37res -eq 1 -and $w36res -eq 1 -and $n38 -eq 12 -and $lap3 -ge 10)){
  Write-Host "AUDIT FAIL (r531) -- ABORT push"; Remove-Item Env:GIT_INDEX_FILE; exit 1
}
$del = & $g diff --name-only --diff-filter=D $parent $sha
if($del){ Write-Host "DELETION DETECTED: $del -- ABORT (r525)"; Remove-Item Env:GIT_INDEX_FILE; exit 1 }
Write-Host "deletion-set self-audit PASS (r519)"

& $g push origin "${sha}:refs/heads/main" 2>&1 | Select-Object -Last 2
if($LASTEXITCODE -eq 0){ & $g update-ref refs/heads/main $sha $parent 2>&1 | Out-Null; Write-Host "local main aligned to $sha" }
Write-Host "PUSHED_SHA=$sha"
Remove-Item Env:GIT_INDEX_FILE -ErrorAction SilentlyContinue
