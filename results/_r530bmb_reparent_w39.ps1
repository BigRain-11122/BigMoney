$g='git'
& $g fetch origin *>&1 | Out-Null
$parent = (& $g rev-parse origin/main).Trim()
$mine = "e94a7d523"
$base = (& $g rev-parse "$mine^").Trim()
Write-Host "parent(origin)=$parent base(my-parent)=$mine mine=$mine"

# three-way tree merge: base = my parent (daemon-rebased fork point),
# ours = latest origin, theirs = my W39 freeze commit. Conflicts -> abort.
$idx = Join-Path $env:TEMP 'fg-w39-idx'
if(Test-Path $idx){ Remove-Item $idx -Force }
$env:GIT_INDEX_FILE = $idx
& $g read-tree -m $base $parent $mine 2>&1 | Out-Null
if($LASTEXITCODE -ne 0){ Write-Host "read-tree 3-way FAILED -- ABORT"; Remove-Item Env:GIT_INDEX_FILE; exit 1 }
$unmerged = & $g ls-files -u
if($unmerged){ Write-Host "TREE CONFLICTS: $unmerged -- ABORT"; Remove-Item Env:GIT_INDEX_FILE; exit 1 }
Write-Host "3-way tree merge CLEAN (zero conflicts)"

$tree = (& $g write-tree).Trim()
Write-Host "tree=$tree"
$sha = (& $g commit-tree $tree -p $parent -F "$env:TEMP\w39msg.txt").Trim()
Write-Host "newcommit=$sha"

# post-write audit legs (r531/r519)
$n38 = (& $g ls-tree $sha results/p2cal_ext/n1_w38/ --name-only | Measure-Object -Line).Lines
$n37 = (& $g ls-tree $sha results/p2cal_ext/n1_w37/ --name-only | Measure-Object -Line).Lines
$w37res = (& $g ls-tree $sha results/perpetual_faces/n1_w37_results.json --name-only | Measure-Object).Count
$n36 = (& $g ls-tree $sha results/perpetual_faces/n1_w36_results.json --name-only | Measure-Object).Count
$w39row = (& $g show "${sha}:scripts/perpetual_faces.py" | Select-String -Pattern '39: \{"a": \(121_004, 123_003\)').Count
$lap3 = (& $g ls-tree $sha results/lowamp_p3/ --name-only | Measure-Object -Line).Lines
$claims = (& $g ls-tree $sha results/pool_claims/ --name-only | Measure-Object -Line).Lines
Write-Host "audit: w38=$n38 w37=$n37 w37res=$w37res w36res=$n36 w39row=$w39row lowamp_p3=$lap3 pool_claims=$claims"
if(-not($n38 -eq 12 -and $n37 -eq 12 -and $w37res -eq 1 -and $n36 -eq 1 -and $w39row -ge 1 -and $lap3 -ge 10)){
  Write-Host "AUDIT FAIL (r531) -- ABORT push"; Remove-Item Env:GIT_INDEX_FILE; exit 1
}
$del = & $g diff --name-only --diff-filter=D $parent $sha
if($del){ Write-Host "DELETION DETECTED: $del -- ABORT (r525)"; Remove-Item Env:GIT_INDEX_FILE; exit 1 }
Write-Host "deletion-set self-audit PASS (r519 law)"

& $g push origin "${sha}:refs/heads/main" 2>&1 | Select-Object -Last 2
Write-Host "PUSHED_SHA=$sha"
Remove-Item Env:GIT_INDEX_FILE -ErrorAction SilentlyContinue
