$g='git'
& $g fetch origin *>&1 | Out-Null
$parent = (& $g rev-parse origin/main).Trim()
Write-Host "parent=$parent"
$env:GIT_INDEX_FILE = Join-Path $env:TEMP 'fg-surg-idx'
if(Test-Path $env:GIT_INDEX_FILE){Remove-Item $env:GIT_INDEX_FILE -Force}
& $g read-tree $parent
# add only pure-new product files + MSG (explicit pathspec, no -A, no shared-face overwrite)
& $g add -- results/p2cal_ext/n1_w38/ fleet/inbox/MSG-20261002-012x-bm-b-w37-finalize-chain-priority.md
$tree = (& $g write-tree).Trim()
Write-Host "tree=$tree"
$sha = (& $g commit-tree $tree -p $parent -m 'surgical r530: W38 12/12 shard products to origin (engine wave products delivery, r310) + MSG w37-finalize chain reminder (from bm-b)').Trim()
Write-Host "newcommit=$sha"
# post-write ls-tree audit legs (r531): W38 12 present, W37 12 still present, W36 results still present
$n38 = (& $g ls-tree $sha results/p2cal_ext/n1_w38/ --name-only | Measure-Object -Line).Lines
$n37 = (& $g ls-tree $sha results/p2cal_ext/n1_w37/ --name-only | Measure-Object -Line).Lines
$n36 = (& $g ls-tree $sha results/perpetual_faces/n1_w36_results.json --name-only | Measure-Object).Count
Write-Host "audit: w38=$n38 w37=$n37 w36file=$n36"
if(-not($n38 -eq 12 -and $n37 -eq 12 -and $n36 -eq 1)){ throw "AUDIT FAIL: stale-base deletion risk detected (r531), ABORT push" }
# deletion-set self-audit (r519 law): D-face must be empty
$del = & $g diff --name-only --diff-filter=D $parent $sha
if($del){ throw "DELETION DETECTED: $del -- ABORT (r525 ownership gate)" }
& $g push origin "${sha}:refs/heads/main" 2>&1 | Select-Object -Last 2
Remove-Item Env:GIT_INDEX_FILE -ErrorAction SilentlyContinue
