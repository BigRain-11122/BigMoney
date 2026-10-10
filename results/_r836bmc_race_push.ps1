# r836 race-push: absorb -> rebase -> settle -> push, up to 3 rings (r824 law)
Set-ExecutionPolicy -Scope Process Bypass -Force | Out-Null

function Resolve-RebaseConflicts {
    param([int]$MaxIter = 24)
    for ($i = 0; $i -lt $MaxIter; $i++) {
        if (-not (Test-Path ".git\rebase-merge")) { return $true }
        $conf = git status --porcelain=v1 | Where-Object { $_ -match '^(AA|UU|DD|AU|UA|DU|UD) ' }
        if ($conf) {
            foreach ($c in $conf) {
                $f = ($c -replace '^..\s+', '').Trim()
                if ($f -eq 'results/crash_fuse.json') {
                    python results\_r836bmc_fuse_merge.py 2>&1 | Out-Null
                    if ($LASTEXITCODE -ne 0) { Write-Output "FUSE-MERGE-FAIL"; return $false }
                } elseif ($f -eq 'results/runnable_pool.json') {
                    git checkout --ours -- $f 2>&1 | Out-Null
                } else {
                    Write-Output "UNKNOWN-CONFLICT: $f"; return $false
                }
            }
            git add -- results/crash_fuse.json results/runnable_pool.json 2>&1 | Out-Null
        }
        # clean unstaged daemon churn (Y column != space, not untracked)
        git status --porcelain=v1 | ForEach-Object {
            if ($_.Length -ge 4 -and $_[0] -ne '?' -and $_[1] -ne ' ') {
                git checkout -- ($_.Substring(3).Trim()) 2>&1 | Out-Null
            }
        }
        $uu = git ls-files -u
        $staged = git diff --cached --name-only
        if (-not $uu -and -not $staged) {
            git rebase --skip 2>&1 | Out-Null
            continue
        }
        git -c core.editor=true rebase --continue 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0 -and (Test-Path ".git\rebase-merge")) {
            Write-Output "CONTINUE-FAIL iter $i"
        }
    }
    return (Test-Path ".git\rebase-merge") -eq $false
}

$pushed = $false
for ($ring = 1; $ring -le 3; $ring++) {
    git add -A 2>&1 | Out-Null
    git commit -m "r836 churn absorb ring ${ring}: daemon live faces pre-rebase" 2>&1 | Out-Null
    git fetch origin -q
    git rebase origin/main 2>&1 | Select-Object -Last 1
    if (Test-Path ".git\rebase-merge") {
        $ok = Resolve-RebaseConflicts
        if (-not $ok) { Write-Output "RESOLVE-FAILED ring $ring"; break }
    }
    $settle = python -c "import sys; sys.path.insert(0, r'scripts'); import merge_lane_views as m; r=m.sync_face('runnable_pool', machine='bm-c'); print(r['status'], r['wrote_shared'], r['wrote_lane'])"
    Write-Output "settle ring ${ring}: $settle"
    git add -A 2>&1 | Out-Null
    git commit -m "r836: post-rebase pool settle (ring ${ring} race window absorb)" 2>&1 | Out-Null
    git push origin main 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { Write-Output "PUSH-OK ring $ring"; $pushed = $true; break }
    Write-Output "PUSH-REJECTED ring $ring"
}
git fetch origin -q
$behind = git rev-list --count HEAD..origin/main
$ahead = git rev-list --count origin/main..HEAD
Write-Output "FINAL behind/ahead: $behind/$ahead pushed=$pushed"
if (-not $pushed -and $ahead -gt 0) {
    git push origin "HEAD:refs/heads/machine/bm-c-r836" 2>&1 | Select-Object -Last 1
    Write-Output "FALLBACK machine branch pushed"
}
